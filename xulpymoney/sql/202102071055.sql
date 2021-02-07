DROP FUNCTION public.investment_operations_alltotals;
DROP FUNCTION public.same_sign;

CREATE OR REPLACE FUNCTION public._final_median(numeric[]) RETURNS numeric
    LANGUAGE sql IMMUTABLE
    AS $_$
   SELECT AVG(val)
   FROM (
     SELECT val
     FROM unnest($1) val
     ORDER BY 1
     LIMIT  2 - MOD(array_upper($1, 1), 2)
     OFFSET CEIL(array_upper($1, 1) / 2.0) - 1
   ) sub;
$_$;


ALTER FUNCTION public._final_median(numeric[]) OWNER TO postgres;

--
-- Name: account_balance(integer, timestamp with time zone, text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE OR REPLACE FUNCTION public.account_balance(INOUT account_id integer, INOUT at_datetime timestamp with time zone, OUT balance_account_currency numeric, OUT balance_user_currency numeric, INOUT user_currency text) RETURNS record
    LANGUAGE plpgsql
    AS $$
DECLARE
	account_currency TEXT;
	recCuentas RECORD;
	factor NUMERIC;
BEGIN
	SELECT sum(amount) INTO account_balance.balance_account_currency FROM accountsoperations where accounts_id=account_id and datetime <= at_datetime;
	SELECT currency into account_currency FROM accounts WHERE id=account_id;
	account_balance.balance_user_currency := money_convert(at_datetime,balance_account_currency,account_currency,user_currency);

	
	IF account_balance.balance_account_currency IS NULL THEN account_balance.balance_account_currency:=0; END IF;
	IF account_balance.balance_user_currency IS NULL THEN account_balance.balance_user_currency:=0; END IF;
END;
$$;


ALTER FUNCTION public.account_balance(INOUT account_id integer, INOUT at_datetime timestamp with time zone, OUT balance_account_currency numeric, OUT balance_user_currency numeric, INOUT user_currency text) OWNER TO postgres;

--
-- Name: accounts_balance(timestamp with time zone, text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE OR REPLACE FUNCTION public.accounts_balance(at_datetime timestamp with time zone, user_currency text) RETURNS numeric
    LANGUAGE plpgsql
    AS $$
DECLARE
	recCuentas RECORD;
	resultado NUMERIC;
BEGIN

    resultado := 0;
    FOR recCuentas IN SELECT id FROM accounts  LOOP
		resultado := resultado + (account_balance(recCuentas.id, at_datetime, user_currency)).balance_user_currency;
    END LOOP;
    RETURN resultado;

END;
$$;


ALTER FUNCTION public.accounts_balance(at_datetime timestamp with time zone, user_currency text) OWNER TO postgres;

--
-- Name: create_role_if_not_exists(name); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE OR REPLACE FUNCTION public.create_role_if_not_exists(rolename name) RETURNS text
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NOT EXISTS (SELECT * FROM pg_roles WHERE rolname = rolename) THEN
        EXECUTE format('CREATE ROLE %I', rolename);
        RETURN 'CREATE ROLE';
    ELSE
        RETURN format('ROLE ''%I'' ALREADY EXISTS', rolename);
    END IF;
END;
$$;


ALTER FUNCTION public.create_role_if_not_exists(rolename name) OWNER TO postgres;

--
-- Name: currency_factor(timestamp with time zone, text, text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE OR REPLACE FUNCTION public.currency_factor(at_datetime timestamp with time zone, currency_from text, currency_to text) RETURNS numeric
    LANGUAGE plpgsql
    AS $$
DECLARE
    factor NUMERIC;
BEGIN
    IF currency_from = currency_to THEN
        factor:=1;
    ELSIF currency_from = 'EUR' AND currency_to = 'USD' THEN
        select quote INTO factor from quote(74747, at_datetime);
    ELSIF currency_from = 'USD' AND currency_to = 'EUR' THEN
        select quote INTO factor from quote(74747, at_datetime);
        IF factor = 0 THEN
            factor:=NULL;
        ELSE
            factor:=1/factor;
        END IF;
    END IF;
    IF factor IS NULL THEN return NULL; ELSE return factor; END IF;
END;
$$;


ALTER FUNCTION public.currency_factor(at_datetime timestamp with time zone, currency_from text, currency_to text) OWNER TO postgres;

--
-- Name: investment_operations(integer, timestamp with time zone, text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE OR REPLACE FUNCTION public.investment_operations(p_investment_id integer, p_at_datetime timestamp with time zone, user_currency text) RETURNS TABLE(io text, io_current text, io_historical text)
    LANGUAGE plpython3u
    AS $_$

## Esta función crea tres listas de diccionarios para io, current y para historica, las convierte a textos y las devuelve
## Para accedar a los datos usar eval()
## Esta función debe usarse para utilizar los datos y no los totales de una inversión

from datetime import datetime

realmultiplier=lambda data: data['multiplier'] if data['productstypes_id'] in (12,13) else 1
cf_plan=plpy.prepare('SELECT * FROM currency_factor($1,$2,$3)',["timestamp with time zone","text","text"])

data_plan=plpy.prepare('SELECT products.id as products_id, multiplier, accounts.currency as accounts_currency, products.currency as products_currency, productstypes_id from accounts, investments, products, leverages where accounts.id=investments.accounts_id and investments.products_id=products.id and leverages.id=products.leverages_id and investments.id=$1', ["integer"])
data=plpy.execute(data_plan, (p_investment_id,))[0]

quote_plan=plpy.prepare("select quote from quote($1, $2)",("integer","timestamp with time zone"))
quote_at_datetime=plpy.execute(quote_plan,(data['products_id'], p_at_datetime))[0]['quote']
# Should be None but to avoid errors I set to 0
if quote_at_datetime is None:
    quote_at_datetime=0
investment2account_at_datetime=plpy.execute(cf_plan, (p_at_datetime, data['products_currency'], data['accounts_currency']))[0]['currency_factor']
account2user_at_datetime=plpy.execute(cf_plan, (p_at_datetime, data['accounts_currency'], user_currency))[0]['currency_factor']

have_same_sign = lambda a, b: True if (a>=0 and b>=0) or (a<0 and b<0) else False
set_sign_of_other_number = lambda number, number_to_change: abs(number_to_change) if number>=0 else -abs(number_to_change)
operationstypes= lambda shares: 4 if shares>=0 else 5

ioh_id=0
io=[]
cur=[]
hist=[]
plan=plpy.prepare('SELECT * from investmentsoperations where investments_id=$1 and datetime <=$2  order by datetime', ["integer","timestamp with time zone"])
for row in plan.cursor( [p_investment_id, p_at_datetime]):
    io.append(row)
    if len(cur)==0 or have_same_sign(cur[0]["shares"], row["shares"]) is True:
        cur.append({"id":row["id"], "investments_id":row["investments_id"], "datetime":row["datetime"] , "shares": row["shares"], "price_investment": row["price"], "operationstypes_id": operationstypes(row['shares']), "taxes_account":row["taxes"], "commissions_account": row["commission"], "investment2account": row["currency_conversion"]}) 
    elif have_same_sign(cur[0]["shares"], row["shares"]) is False:
        rest=row["shares"]
        ciclos=0
        while rest!=0:
            ciclos=ciclos+1
            commissions=0
            taxes=0
            if ciclos==1:
                commissions=row["commission"]+cur[0]["commissions_account"]
                taxes=row["taxes"]+cur[0]["taxes_account"]
        
            if len(cur)>0:
                if abs(cur[0]["shares"])>=abs(rest):
                    ioh_id=ioh_id+1
                    hist.append({"shares":set_sign_of_other_number(row["shares"],rest),"id":ioh_id, "investments_id": p_investment_id, "dt_start":cur[0]["datetime"], "dt_end":row["datetime"], "operationstypes_id": operationstypes(cur[0]['shares']), "commissions_account":commissions, "taxes_account":taxes, "price_start_investment":cur[0]["price_investment"], "price_end_investment":row["price"],"investment2account_start":cur[0]["investment2account"], "investment2account_end":row["currency_conversion"]    })
                    if rest+cur[0]["shares"]!=0:
                        cur.insert(0, {"id":cur[0]["id"], "investments_id":cur[0]["investments_id"], "datetime":cur[0]["datetime"] , "shares": rest+cur[0]["shares"], "price_investment": cur[0]["price_investment"], "operationstypes_id": operationstypes(cur[0]['shares']), "taxes_account":cur[0]["taxes_account"], "commissions_account": cur[0]["commissions_account"], "investment2account": cur[0]["investment2account"]}) 
                        cur.pop(1)
                    else:
                        cur.pop(0)
                    rest=0
                    break
                else:
                    ioh_id=ioh_id+1
                    hist.append({"shares":set_sign_of_other_number(row["shares"],cur[0]["shares"]),"id":ioh_id, "investments_id": p_investment_id, "dt_start":cur[0]["datetime"], "dt_end":row["datetime"], "operationstypes_id": operationstypes(row['shares']), "commissions_account":commissions, "taxes_account":taxes, "price_start_investment":cur[0]["price_investment"], "price_end_investment":row["price"],"investment2account_start":cur[0]["investment2account"], "investment2account_end":row["currency_conversion"]    })

                    rest=rest+cur[0]["shares"]
                    rest=set_sign_of_other_number(row["shares"],rest)
                    cur.pop(0)
            else:
                cur.insert(0, {"id":row["id"], "investments_id":row["investments_id"], "datetime":row["datetime"] , "shares": rest, "price_investment": row["price"], "operationstypes_id": operationstypes(row['shares']),"taxes_account":row["taxes"], "commissions_account": row["commission"], "investment2account": row["currency_conversion"]}) 
                break

for o in io:
    o['commission_account']=o['commission']
    o['taxes_account']=o['taxes']
    o['gross_account']=abs(o['shares']*o['price']*o['currency_conversion'])
    if o['shares']>=0:
        o['net_account']=o['gross_account']+o['commission_account']+o['taxes_account']
    else:
        o['net_account']=o['gross_account']-o['commission_account']-o['taxes_account']

for c in cur:
    c['real_leverages']= realmultiplier(data)
    c['investment2account_at_datetime']=investment2account_at_datetime
    c['account2user_at_datetime']=account2user_at_datetime 
    c['currency_investment']=data["products_currency"]        
    c['currency_account']=data['accounts_currency']
    c['currency_user']=user_currency
    c['account2user']=plpy.execute(cf_plan, (c['datetime'], c['currency_account'],c['currency_user']))[0]['currency_factor']
    c['price_account']=c['price_investment']*c['investment2account']
    c['price_user']=c['price_account']*c['account2user']
    c['taxes_investment']=c['taxes_account']/c['investment2account']#taxes and commissions are in account currency buy we can guess them
    c['taxes_user']=c['taxes_account']*c['account2user']
    c['commissions_investment']=c['commissions_account']/c['investment2account']
    c['commissions_user']=c['commissions_account']*c['account2user']
    #Si son cfds o futuros el saldo es 0, ya que es un contrato y el saldo todavía está en la cuenta. Sin embargo cuento las perdidas
    c['balance_investment']=0 if data['productstypes_id'] in (12,13) else abs(c['shares'])*quote_at_datetime*c['real_leverages']
    c['balance_account']=c['balance_investment']*investment2account_at_datetime
    c['balance_user']=c['balance_account']*account2user_at_datetime
    #Aquí calculo con saldo y futuros y cfd
    if c['shares']>0:
        c['balance_futures_investment']=c['shares']*quote_at_datetime*c['real_leverages']
    else:
        diff=(quote_at_datetime-c['price_investment'])*abs(c['shares'])*c['real_leverages']
        init_balance=c['price_investment']*abs(c['shares'])*c['real_leverages']
        c['balance_futures_investment']=init_balance-diff
    c['balance_futures_account']=c['balance_futures_investment']*investment2account_at_datetime
    c['balance_futures_user']=c['balance_futures_account']*account2user_at_datetime
    c['invested_investment']=abs(c['shares']*c['price_investment']*c['real_leverages'])
    c['invested_account']=c['invested_investment']*c['investment2account']
    c['invested_user']=c['invested_account']*c['account2user']
    c['gains_gross_investment']=(quote_at_datetime - c['price_investment'])*c['shares']*c['real_leverages']
    c['gains_gross_account']=(quote_at_datetime*c['investment2account_at_datetime'] - c['price_investment']*c['investment2account'])*c['shares']*c['real_leverages']
    c['gains_gross_user']=(quote_at_datetime*c['investment2account_at_datetime']*c['account2user_at_datetime'] - c['price_investment']*c['investment2account']*c['account2user'])*c['shares']*c['real_leverages']
    c['gains_net_investment']=c['gains_gross_investment'] -c['taxes_investment'] -c['commissions_investment']
    c['gains_net_account']=c['gains_gross_account']-c['taxes_account']-c['commissions_account'] 
    c['gains_net_user']=c['gains_gross_user']-c['taxes_user']-c['commissions_user']
    
for h in hist:
    h['currency_investment']=data['products_currency']        
    h['currency_account']=data['accounts_currency']
    h['currency_user']=user_currency
    h['account2user_start']=plpy.execute(cf_plan, (h['dt_start'], h['currency_account'],h['currency_user']))[0]['currency_factor']
    h['account2user_end']=plpy.execute(cf_plan, (h['dt_end'], h['currency_account'],h['currency_user']))[0]['currency_factor']
    h['real_leverages']= realmultiplier(data)
    h['gross_start_investment']=0 if h['operationstypes_id'] in (9,10) else abs(h['shares']*h['price_start_investment']*h['real_leverages'])#Transfer shares 9, 10
    if h['operationstypes_id'] in (9,10):
        h['gross_end_investment']=0
    elif h['shares']<0:#Sell after bought
        h['gross_end_investment']=abs(h['shares'])*h['price_end_investment']*h['real_leverages']
    else:
        diff=(h['price_end_investment']-h['price_start_investment'])*abs(h['shares'])*h['real_leverages']
        init_balance=h['price_start_investment']*abs(h['shares'])*h['real_leverages']
        h['gross_end_investment']=init_balance-diff
    h['gains_gross_investment']=h['gross_end_investment']-h['gross_start_investment']
    h['gains_gross_account']=h['gains_gross_investment']*h['investment2account_end']
    h['gains_gross_user']=h['gains_gross_account']*h['account2user_end']
    h['gross_start_account']=h['gross_start_investment']*h['investment2account_start']
    h['gross_start_user']=h['gross_start_account']*h['account2user_start']
    h['gross_end_account']=h['gross_end_investment']*h['investment2account_end']
    h['gross_end_user']=h['gross_end_account']*h['account2user_end']
    h['taxes_investment']=h['taxes_account']/h['investment2account_end']#taxes and commissions are in account currency buy we can guess them
    h['taxes_user']=h['taxes_account']*h['account2user_end']
    h['commissions_investment']=h['commissions_account']/h['investment2account_end']
    h['commissions_user']=h['commissions_account']*h['account2user_end']
    h['gains_net_investment']=h['gains_gross_investment']-h['taxes_investment']-h['commissions_investment']
    h['gains_net_account']=h['gains_net_investment']*h['investment2account_end']
    h['gains_net_user']=h['gains_net_account']*h['account2user_end']

return [{ "io": str(io), "io_current": str(cur),"io_historical":str(hist)}]

## -------------------- COPIAR HASTA AQUI ----------------------a-
$_$;


ALTER FUNCTION public.investment_operations(p_investment_id integer, p_at_datetime timestamp with time zone, user_currency text) OWNER TO postgres;

--
-- Name: investment_operations_totals(integer, timestamp with time zone, text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE OR REPLACE FUNCTION public.investment_operations_totals(p_investment_id integer, p_at_datetime timestamp with time zone, user_currency text) RETURNS TABLE(io text, io_current text, io_historical text)
    LANGUAGE plpython3u
    AS $_$
from decimal import Decimal
plan=plpy.prepare('SELECT * FROM investment_operations($1,$2,$3)',["integer", "timestamp with time zone","text"])
data=plpy.execute(plan, (p_investment_id,p_at_datetime,user_currency))[0]
io=eval(data['io'])
io_current=eval(data['io_current'])
io_historical=eval(data['io_historical'])
#plpy.warning(str(io_current))

sumador= lambda l, key: sum(d[key] if d[key] is not None else 0 for d  in l)

d_io={
    "price":sumador(io, 'price'),
}

d_io_current={
    "balance_user":sumador(io_current, 'balance_user'),
    "balance_futures_user":sumador(io_current, 'balance_futures_user'),
    "gains_gross_user":sumador(io_current, 'gains_gross_user'),
    "gains_net_user":sumador(io_current, 'gains_gross_user'),
    "shares":sumador(io_current, 'shares'),
    "price_investment":sumador(io_current, 'price_investment'),
    "invested_user":sumador(io_current, 'invested_user'),
}

d_io_historical={
    "commissions_account":sumador(io_historical, 'commissions_account'),
    "gains_net_user":sumador(io_historical, 'gains_net_user'),
}

return [{ "io": str(d_io), "io_current": str(d_io_current),"io_historical":str(d_io_historical)}]
$_$;


ALTER FUNCTION public.investment_operations_totals(p_investment_id integer, p_at_datetime timestamp with time zone, user_currency text) OWNER TO postgres;

--
-- Name: is_price_variation_in_time(integer, double precision, timestamp with time zone); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE OR REPLACE FUNCTION public.is_price_variation_in_time(p_id_products integer, p_percentage double precision, p_datetime timestamp with time zone) RETURNS boolean
    LANGUAGE plpgsql
    AS $$DECLARE
    result boolean;
    initial numeric(18,6);
    final numeric(18,6);
        variation numeric(18,6);
BEGIN
    result := False;
    SELECT quotes.quote  INTO final FROM quotes where quotes.id= p_id_products and quotes.datetime <= now() order by quotes.datetime desc limit 1;
    SELECT quotes.quote  INTO initial FROM quotes where quotes.id= p_id_products and quotes.datetime <= p_datetime order by quotes.datetime desc limit 1;
    IF initial=0 THEN
            return False;
        END IF;
        
        variation:=100*(final-initial)/initial;
        --Raise Notice 'hello world % %: % (%)', initial, final, variation, p_percentage;
    -- PERCENTAGE POSITIVE
    IF p_percentage>0 AND variation > p_percentage THEN
        return True;
    END IF;
    -- PERCENTAGE NEGATIVE
    IF p_percentage<0 AND variation < p_percentage THEN
        return True;
    END IF;
    RETURN result;
END;
$$;


ALTER FUNCTION public.is_price_variation_in_time(p_id_products integer, p_percentage double precision, p_datetime timestamp with time zone) OWNER TO postgres;

--
-- Name: FUNCTION is_price_variation_in_time(p_id_products integer, p_percentage double precision, p_datetime timestamp with time zone); Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON FUNCTION public.is_price_variation_in_time(p_id_products integer, p_percentage double precision, p_datetime timestamp with time zone) IS 'Returns True, if percentage is negative and variation between timestamp price and current product price is less than percentage
Returns True, if percentage is positive and variation between timestamp price and current product price is bigger than percentage
Return False, in other cases';


--
-- Name: last_penultimate_lastyear(integer, timestamp with time zone); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE OR REPLACE FUNCTION public.last_penultimate_lastyear(INOUT id integer, at_datetime timestamp with time zone, OUT last_datetime timestamp with time zone, OUT last numeric, OUT penultimate_datetime timestamp with time zone, OUT penultimate numeric, OUT lastyear_datetime timestamp with time zone, OUT lastyear numeric) RETURNS record
    LANGUAGE plpgsql
    AS $$
DECLARE
    ly timestamptz;
BEGIN
    SELECT quotes.quote, quotes.datetime  INTO last_penultimate_lastyear.last, last_penultimate_lastyear.last_datetime FROM quote(id, at_datetime) quotes;
    SELECT quotes.quote, quotes.datetime  INTO last_penultimate_lastyear.penultimate, last_penultimate_lastyear.penultimate_datetime FROM penultimate(id, at_datetime::date) quotes;
    ly:=make_timestamptz((EXTRACT(YEAR FROM  at_datetime)-1)::integer, 12, 31, 23, 59, 59.999999::double precision) ;
    SELECT quotes.quote, quotes.datetime  INTO last_penultimate_lastyear.lastyear, last_penultimate_lastyear.lastyear_datetime FROM quote(id,ly) quotes;
END;
$$;


ALTER FUNCTION public.last_penultimate_lastyear(INOUT id integer, at_datetime timestamp with time zone, OUT last_datetime timestamp with time zone, OUT last numeric, OUT penultimate_datetime timestamp with time zone, OUT penultimate numeric, OUT lastyear_datetime timestamp with time zone, OUT lastyear numeric) OWNER TO postgres;

--
-- Name: money_convert(timestamp with time zone, numeric, text, text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE OR REPLACE FUNCTION public.money_convert(at_datetime timestamp with time zone, amount_from numeric, currency_from text, currency_to text) RETURNS numeric
    LANGUAGE plpgsql
    AS $$
DECLARE
    factor NUMERIC;
BEGIN
    select currency_factor INTO factor from currency_factor(at_datetime,currency_from,currency_to);
    -- Should return None but I return amount_from to avoid errors
    IF factor IS NULL THEN return amount_from; ELSE return amount_from *factor; END IF;
END;
$$;


ALTER FUNCTION public.money_convert(at_datetime timestamp with time zone, amount_from numeric, currency_from text, currency_to text) OWNER TO postgres;

--
-- Name: ohcldailybeforesplits(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE OR REPLACE FUNCTION public.ohcldailybeforesplits(product_id integer) RETURNS TABLE(products_id integer, date date, open numeric, high numeric, low numeric, close numeric)
    LANGUAGE plpgsql
    AS $$
DECLARE 
    o record;
BEGIN
    FOR o IN (select 
                quotes.products_id, 
                datetime::date as date, 
                (array_agg(quote order by datetime))[1] as open, 
                min(quote) as low, 
                max(quote) as high, 
                (array_agg(quote order by datetime desc))[1] as close 
            from quotes 
            where quotes.products_id=product_id
            group by quotes.products_id, datetime::date 
            order by datetime::date )  
    LOOP
	    products_id=o.products_id;
        date:= o.date;
        open:=o.open;
        high:=o.high;
        low:=o.low;
        close:=o.close;
        RETURN NEXT;
    END LOOP;
END;
$$;


ALTER FUNCTION public.ohcldailybeforesplits(product_id integer) OWNER TO postgres;

--
-- Name: ohclmonthlybeforesplits(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE OR REPLACE FUNCTION public.ohclmonthlybeforesplits(product_id integer) RETURNS TABLE(products_id integer, year integer, month integer, open numeric, high numeric, low numeric, close numeric)
    LANGUAGE plpgsql
    AS $$
DECLARE 
    o record;
BEGIN
    FOR o IN (                   select 
			    t.products_id,
                date_part('year',date) as year, 
                date_part('month', date) as month, 
                (array_agg(t.open order by date))[1] as open, 
                min(t.low) as low, 
                max(t.high) as high, 
                (array_agg(t.close order by date desc))[1] as close 
            from ohclDailyBeforeSplits(product_id) as t
            group by t.products_id,  year, month 
            order by year, month)
    LOOP
	    products_id=product_id;
        year:= o.year;
			  month:= o.month;
        open:=o.open;
        high:=o.high;
        low:=o.low;
        close:=o.close;
        RETURN NEXT;
    END LOOP;
END;
$$;


ALTER FUNCTION public.ohclmonthlybeforesplits(product_id integer) OWNER TO postgres;

--
-- Name: penultimate(integer, date); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE OR REPLACE FUNCTION public.penultimate(INOUT id integer, date date, OUT quote numeric, OUT datetime timestamp with time zone, OUT searched timestamp with time zone) RETURNS record
    LANGUAGE plpgsql
    AS $$
DECLARE
    last_datetime timestamptz;
    minus date;
BEGIN
    searched:=make_timestamptz(EXTRACT(YEAR FROM penultimate.date)::integer,EXTRACT(MONTH FROM penultimate.date)::integer, EXTRACT(DAY FROM penultimate.date)::integer, 23, 59, 59.999999::double precision) ;
    select quotes.datetime INTO last_datetime from quote(penultimate.id, searched) quotes;
    minus:=last_datetime::date - integer '1';
    searched:=make_timestamptz(EXTRACT(YEAR FROM minus)::integer,EXTRACT(MONTH FROM minus)::integer, EXTRACT(DAY FROM minus)::integer, 23, 59, 59.999999::double precision) ;
    SELECT quotes.quote, quotes.datetime  INTO penultimate.quote, penultimate.datetime FROM quotes where quotes.products_id= penultimate.id and quotes.datetime <= searched order by quotes.datetime desc limit 1;
END;
$$;


ALTER FUNCTION public.penultimate(INOUT id integer, date date, OUT quote numeric, OUT datetime timestamp with time zone, OUT searched timestamp with time zone) OWNER TO postgres;

--
-- Name: percentage(numeric, numeric, boolean); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE OR REPLACE FUNCTION public.percentage(from_ numeric, to_ numeric, by_100 boolean DEFAULT true) RETURNS numeric
    LANGUAGE plpgsql
    AS $$
BEGIN
	if from_ = 0::numeric then 
		return Null;
	end if;
	if by_100 = true then
		return(to_-from_)/from_*100;
	else
		return(to_-from_)/from_;
	end if;
END;
$$;


ALTER FUNCTION public.percentage(from_ numeric, to_ numeric, by_100 boolean) OWNER TO postgres;

--
-- Name: quote(integer, timestamp with time zone); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE OR REPLACE FUNCTION public.quote(INOUT id integer, INOUT datetime timestamp with time zone, OUT quote numeric, OUT searched timestamp with time zone) RETURNS record
    LANGUAGE plpgsql
    AS $$
BEGIN
    searched := quote.datetime;
    SELECT quotes.quote, quotes.datetime  INTO quote.quote, quote.datetime FROM quotes where quotes.products_Id= quote.id and quotes.datetime <= quote.datetime order by quotes.datetime desc limit 1;
END;
$$;


ALTER FUNCTION public.quote(INOUT id integer, INOUT datetime timestamp with time zone, OUT quote numeric, OUT searched timestamp with time zone) OWNER TO postgres;

--
-- Name: total_balance(timestamp with time zone, text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE OR REPLACE FUNCTION public.total_balance(p_at_datetime timestamp with time zone, user_currency text) RETURNS TABLE(accounts_user numeric, investments_user numeric, total_user numeric, investments_invested_user numeric)
    LANGUAGE plpython3u
    AS $_$
## Esta función debe usarse cuando no nos interesan los datos sino los saldos de todas las inversiones en una fecha
from decimal import Decimal
plan_accounts=plpy.prepare('SELECT * from  accounts_balance($1,$2)',["timestamp with time zone","text"])
accounts=plpy.execute(plan_accounts, (p_at_datetime,user_currency))
plan_investments=plpy.prepare('select investment_operations_totals.* from investments, investment_operations_totals(investments.id,$1,$2 ) as investment_operations_totals',["timestamp with time zone","text"])
investments=plpy.execute(plan_investments, (p_at_datetime,user_currency))


sumador= lambda l, key: sum(d[key] if d[key] is not None else 0 for d  in l)

ld_current=[]
for d in investments:
    ld_current.append(eval(d['io_current']))

accounts_user=accounts[0]['accounts_balance']
investments_user=sumador(ld_current, 'balance_user')

return [{ 
    "accounts_user": accounts_user, 
    "investments_user": investments_user,
    "total_user": accounts_user+investments_user,
    "investments_invested_user": sumador(ld_current, 'invested_user'),
},]
$_$;


ALTER FUNCTION public.total_balance(p_at_datetime timestamp with time zone, user_currency text) OWNER TO postgres;

--
-- Name: tt_investment_operations(integer, timestamp with time zone, text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE OR REPLACE FUNCTION public.tt_investment_operations(p_investment_id integer, p_at_datetime timestamp with time zone, user_currency text) RETURNS text
    LANGUAGE plpython3u
    AS $_$
## Esta función crea tres tablas temporales con nombres io_datestring, ioc_datestring , ioh_datestring
## Devuelve el datestring
from datetime import datetime

realmultiplier=lambda data: data['multiplier'] if data['productstypes_id'] in (12,13) else 1
cf_plan=plpy.prepare('SELECT * FROM currency_factor($1,$2,$3)',["timestamp with time zone","text","text"])

data_plan=plpy.prepare('SELECT products.id as products_id, multiplier, accounts.currency as accounts_currency, products.currency as products_currency, productstypes_id from accounts, investments, products, leverages where accounts.id=investments.accounts_id and investments.products_id=products.id and leverages.id=products.leverages_id and investments.id=$1', ["integer"])
data=plpy.execute(data_plan, (p_investment_id,))[0]

quote_plan=plpy.prepare("select quote from quote($1, $2)",("integer","timestamp with time zone"))
quote_at_datetime=plpy.execute(quote_plan,(data['products_id'], p_at_datetime))[0]['quote']
# Should be None but to avoid errors I set to 0
if quote_at_datetime is None:
    quote_at_datetime=0
investment2account_at_datetime=plpy.execute(cf_plan, (p_at_datetime, data['products_currency'], data['accounts_currency']))[0]['currency_factor']
account2user_at_datetime=plpy.execute(cf_plan, (p_at_datetime, data['accounts_currency'], user_currency))[0]['currency_factor']

have_same_sign = lambda a, b: True if (a>=0 and b>=0) or (a<0 and b<0) else False
set_sign_of_other_number = lambda number, number_to_change: abs(number_to_change) if number>=0 else -abs(number_to_change)
operationstypes= lambda shares: 4 if shares>=0 else 5

ioh_id=0
io=[]
cur=[]
hist=[]
plan=plpy.prepare('SELECT * from investmentsoperations where investments_id=$1 and datetime <=$2  order by datetime', ["integer","timestamp with time zone"])
for row in plan.cursor( [p_investment_id, p_at_datetime]):
    io.append(row)
    if len(cur)==0 or have_same_sign(cur[0]["shares"], row["shares"]) is True:
        cur.append({"id":row["id"], "investments_id":row["investments_id"], "datetime":row["datetime"] , "shares": row["shares"], "price_investment": row["price"], "operationstypes_id": operationstypes(row['shares']), "taxes_account":row["taxes"], "commissions_account": row["commission"], "investment2account": row["currency_conversion"]}) 
    elif have_same_sign(cur[0]["shares"], row["shares"]) is False:
        rest=row["shares"]
        ciclos=0
        while rest!=0:
            ciclos=ciclos+1
            commissions=0
            taxes=0
            if ciclos==1:
                commissions=row["commission"]+cur[0]["commissions_account"]
                taxes=row["taxes"]+cur[0]["taxes_account"]
        
            if len(cur)>0:
                if abs(cur[0]["shares"])>=abs(rest):
                    ioh_id=ioh_id+1
                    hist.append({"shares":set_sign_of_other_number(row["shares"],rest),"id":ioh_id, "investments_id": p_investment_id, "dt_start":cur[0]["datetime"], "dt_end":row["datetime"], "operationstypes_id": operationstypes(cur[0]['shares']), "commissions_account":commissions, "taxes_account":taxes, "price_start_investment":cur[0]["price_investment"], "price_end_investment":row["price"],"investment2account_start":cur[0]["investment2account"], "investment2account_end":row["currency_conversion"]    })
                    if rest+cur[0]["shares"]!=0:
                        cur.insert(0, {"id":cur[0]["id"], "investments_id":cur[0]["investments_id"], "datetime":cur[0]["datetime"] , "shares": rest+cur[0]["shares"], "price_investment": cur[0]["price_investment"], "operationstypes_id": operationstypes(cur[0]['shares']), "taxes_account":cur[0]["taxes_account"], "commissions_account": cur[0]["commissions_account"], "investment2account": cur[0]["investment2account"]}) 
                        cur.pop(1)
                    else:
                        cur.pop(0)
                    rest=0
                    break
                else:
                    ioh_id=ioh_id+1
                    hist.append({"shares":set_sign_of_other_number(row["shares"],cur[0]["shares"]),"id":ioh_id, "investments_id": p_investment_id, "dt_start":cur[0]["datetime"], "dt_end":row["datetime"], "operationstypes_id": operationstypes(row['shares']), "commissions_account":commissions, "taxes_account":taxes, "price_start_investment":cur[0]["price_investment"], "price_end_investment":row["price"],"investment2account_start":cur[0]["investment2account"], "investment2account_end":row["currency_conversion"]    })

                    rest=rest+cur[0]["shares"]
                    rest=set_sign_of_other_number(row["shares"],rest)
                    cur.pop(0)
            else:
                cur.insert(0, {"id":row["id"], "investments_id":row["investments_id"], "datetime":row["datetime"] , "shares": rest, "price_investment": row["price"], "operationstypes_id": operationstypes(row['shares']),"taxes_account":row["taxes"], "commissions_account": row["commission"], "investment2account": row["currency_conversion"]}) 
                break

for o in io:
	o['commission_account']=o['commission']
	o['taxes_account']=o['taxes']
	o['gross_account']=abs(o['shares']*o['price']*o['currency_conversion'])
	o['net_account']=o['gross_account']-o['commission_account']-o['taxes_account']

for c in cur:
    c['real_leverages']= realmultiplier(data)
    c['investment2account_at_datetime']=investment2account_at_datetime
    c['account2user_at_datetime']=account2user_at_datetime 
    c['currency_investment']=data["products_currency"]        
    c['currency_account']=data['accounts_currency']
    c['currency_user']=user_currency
    c['account2user']=plpy.execute(cf_plan, (c['datetime'], c['currency_account'],c['currency_user']))[0]['currency_factor']
    c['price_account']=c['price_investment']*c['investment2account']
    c['price_user']=c['price_account']*c['account2user']
    c['taxes_investment']=c['taxes_account']/c['investment2account']#taxes and commissions are in account currency buy we can guess them
    c['taxes_user']=c['taxes_account']*c['account2user']
    c['commissions_investment']=c['commissions_account']/c['investment2account']
    c['commissions_user']=c['commissions_account']*c['account2user']
    #Si son cfds o futuros el saldo es 0, ya que es un contrato y el saldo todavía está en la cuenta. Sin embargo cuento las perdidas
    c['balance_investment']=0 if data['productstypes_id'] in (12,13) else abs(c['shares'])*quote_at_datetime*c['real_leverages']
    c['balance_account']=c['balance_investment']*investment2account_at_datetime
    c['balance_user']=c['balance_account']*account2user_at_datetime
    c['invested_investment']=abs(c['shares']*c['price_investment']*c['real_leverages'])
    c['invested_account']=c['invested_investment']*c['investment2account']
    c['invested_user']=c['invested_account']*c['account2user']
    c['gains_gross_investment']=(quote_at_datetime - c['price_investment'])*c['shares']*c['real_leverages']
    c['gains_gross_account']=(quote_at_datetime*c['investment2account_at_datetime'] - c['price_investment']*c['investment2account'])*c['shares']*c['real_leverages']
    c['gains_gross_user']=(quote_at_datetime*c['investment2account_at_datetime']*c['account2user_at_datetime'] - c['price_investment']*c['investment2account']*c['account2user'])*c['shares']*c['real_leverages']
    c['gains_net_investment']=c['gains_gross_investment'] -c['taxes_investment'] -c['commissions_investment']
    c['gains_net_account']=c['gains_gross_account']-c['taxes_account']-c['commissions_account'] 
    c['gains_net_user']=c['gains_gross_user']-c['taxes_user']-c['commissions_user']
    
for h in hist:
    h['currency_investment']=data['products_currency']        
    h['currency_account']=data['accounts_currency']
    h['currency_user']=user_currency
    h['account2user_start']=plpy.execute(cf_plan, (h['dt_start'], h['currency_account'],h['currency_user']))[0]['currency_factor']
    h['account2user_end']=plpy.execute(cf_plan, (h['dt_end'], h['currency_account'],h['currency_user']))[0]['currency_factor']
    h['real_leverages']= realmultiplier(data)
    h['gross_start_investment']=0 if h['operationstypes_id'] in (9,10) else abs(h['shares']*h['price_start_investment']*h['real_leverages'])#Transfer shares 9, 10
    if h['operationstypes_id'] in (9,10):
        h['gross_end_investment']=0
    elif h['shares']<0:#Sell after bought
        h['gross_end_investment']=abs(h['shares'])*h['price_end_investment']*h['real_leverages']
    else:
        diff=(h['price_end_investment']-h['price_start_investment'])*abs(h['shares'])*h['real_leverages']
        init_balance=h['price_start_investment']*abs(h['shares'])*h['real_leverages']
        h['gross_end_investment']=init_balance-diff
    h['gains_gross_investment']=h['gross_end_investment']-h['gross_start_investment']
    h['gains_gross_account']=h['gains_gross_investment']*h['investment2account_end']
    h['gains_gross_user']=h['gains_gross_account']*h['account2user_end']
    h['gross_start_account']=h['gross_start_investment']*h['investment2account_start']
    h['gross_start_user']=h['gross_start_account']*h['account2user_start']
    h['gross_end_account']=h['gross_end_investment']*h['investment2account_end']
    h['gross_end_user']=h['gross_end_account']*h['account2user_end']
    h['taxes_investment']=h['taxes_account']/h['investment2account_end']#taxes and commissions are in account currency buy we can guess them
    h['taxes_user']=h['taxes_account']*h['account2user_end']
    h['commissions_investment']=h['commissions_account']/h['investment2account_end']
    h['commissions_user']=h['commissions_account']*h['account2user_end']
    h['gains_net_investment']=h['gains_gross_investment']-h['taxes_investment']-h['commissions_investment']
    h['gains_net_account']=h['gains_net_investment']*h['investment2account_end']
    h['gains_net_user']=h['gains_net_account']*h['account2user_end']

plpy.warning(str(io[0]))
#return str([{ "io": str(io), "io_current": str(cur),"io_historical":str(hist)}])

## CREATING IO TABLE
table_datetime= str(p_at_datetime).replace("-","").replace(":","").replace(" ","_").replace(".","_")[:-3]
table_io=f'io_{table_datetime}'
table_ioc=f'ioc_{table_datetime}'
table_ioh=f'ioh_{table_datetime}'
table_prueba=f'prueba_{table_datetime}'

plpy.execute(f'CREATE TEMPORARY TABLE {table_io} (id serial , operationstypes_id integer, investments_id integer, shares numeric(12,6), taxes numeric(12,6), commission numeric(12,6), price numeric(12,6), datetime timestamp with time zone, comment text, show_in_ranges boolean, currency_conversion numeric(12,10), commission_account numeric (12,6), taxes_account numeric(12,6), gross_account numeric(12,6), net_account numeric(12,6))')
#{'id': 575, 'operationstypes_id': 4, 'investments_id': 81, 'shares': Decimal('1989.000000'), 'taxes': Decimal('0.00'), 'commission': Decimal('16.45'), 'price': Decimal('15.080000'), 'datetime': '1808-05-15 00:00:00+02', 'comment': None, 'show_in_ranges': True, 'currency_conversion': Decimal('1.0000000000'), 'commission_account': Decimal('16.45'), 'taxes_account': Decimal('0.00'), 'gross_account': Decimal('29994.1180000000000000000000'), 'net_account': Decimal('29977.6700000000000000000000')}

for o in io:
	plpy.execute(f'''insert into {table_io} (operationstypes_id, investments_id, shares, taxes, commission, price, datetime, comment, show_in_ranges, currency_conversion, commission_account, taxes_account, gross_account, net_account)
				 values( {o['operationstypes_id']}, {o['investments_id']}, {o['shares']},{o['taxes']},{o['commission']},{o['price']}, '{o['datetime']}', '{o['comment']}', {o['show_in_ranges']}, {o['currency_conversion']}, {o['commission_account']}, {o['taxes_account']},{o['gross_account']}, {o['net_account']} )''')

plpy.execute(f'CREATE TEMPORARY TABLE {table_ioc} (id serial , investments_id integer, datetime timestamp with time zone, shares numeric(12,6), price numeric(12,6))')
plpy.execute(f'CREATE TEMPORARY TABLE {table_ioh} (id serial , investments_id integer, datetime timestamp with time zone, shares numeric(12,6), price numeric(12,6))')

return f'{table_io}#{table_ioc}#{table_ioh}'

## -------------------- COPIAR HASTA AQUI ------------------------
$_$;


ALTER FUNCTION public.tt_investment_operations(p_investment_id integer, p_at_datetime timestamp with time zone, user_currency text) OWNER TO postgres;

