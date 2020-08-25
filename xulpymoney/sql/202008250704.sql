
--
-- Name: account_balance(integer, timestamp with time zone, text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.account_balance(INOUT account_id integer, INOUT at_datetime timestamp with time zone, OUT balance_account_currency numeric, OUT balance_user_currency numeric, INOUT user_currency text) RETURNS record
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

CREATE FUNCTION public.accounts_balance(at_datetime timestamp with time zone, user_currency text) RETURNS numeric
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

CREATE FUNCTION public.create_role_if_not_exists(rolename name) RETURNS text
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
-- Name: investment_operations_current(integer, timestamp with time zone); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.investment_operations_current(p_investment_id integer, p_at_datetime timestamp with time zone) RETURNS TABLE(id integer, investments_id integer, datetime timestamp with time zone, shares numeric, price numeric, operationstypes_id integer, taxes numeric, commission numeric, currency_conversion numeric)
    LANGUAGE plpython3u
    AS $_$
from datetime import datetime

have_same_sign = lambda a, b: True if (a>=0 and b>=0) or (a<0 and b<0) else False
set_sign_of_other_number = lambda number, number_to_change: abs(number_to_change) if number>=0 else -abs(number_to_change)

ioh_id=0
cur=[]
hist=[]
plan=plpy.prepare('SELECT * from investmentsoperations where investments_id=$1 and datetime <=$2  order by datetime', ["integer","timestamp with time zone"])
for row in plan.cursor( [p_investment_id, p_at_datetime]):
	operationstypes_id=4 if row["shares"]>=0 else 5
	if len(cur)==0 or have_same_sign(cur[0]["shares"], row["shares"]) is True:
		cur.append(row)
	elif have_same_sign(cur[0]["shares"], row["shares"]) is False:
		rest=row["shares"]
		ciclos=0
		while rest!=0:
			ciclos=ciclos+1
			commissions=0
			taxes=0
			if ciclos==1:
				commissions=row["commission"]+cur[0]["commission"]
				taxes=row["taxes"]+cur[0]["taxes"]
		
			if len(cur)>0:
				if abs(cur[0]["shares"])>=abs(rest):
					ioh_id=ioh_id+1
					hist.append({"shares":set_sign_of_other_number(row["shares"],rest),"id":ioh_id, "investments_id": p_investment_id, "dt_start":cur[0]["datetime"], "dt_end":row["datetime"], "operationstypes_id":operationstypes_id, "commission":commissions, "taxes":taxes, "buyprice":cur[0]["price"], "sellprice":row["price"],"buycc":cur[0]["currency_conversion"], "sellcc":row["currency_conversion"]    })
					if rest+cur[0]["shares"]!=0:
						cur.insert(0, {"id":row["id"], "investments_id":row["investments_id"], "datetime":cur[0]["datetime"] , "shares": rest+cur[0]["shares"], "price": row["price"], "operationstypes_id": operationstypes_id, "taxes":row["taxes"], "commission": row["commission"], "currency_conversion": row["currency_conversion"]}) 
						cur.pop(1)
					else:
						cur.pop(0)
					rest=0
					break
				else:
					ioh_id=ioh_id+1
					hist.append({"shares":set_sign_of_other_number(row["shares"],cur[0]["shares"]),"id":ioh_id, "investments_id": p_investment_id, "dt_start":cur[0]["datetime"], "dt_end":row["datetime"], "operationstypes_id":operationstypes_id, "commission":commissions, "taxes":taxes, "buyprice":cur[0]["price"], "sellprice":row["price"],"buycc":cur[0]["currency_conversion"], "sellcc":row["currency_conversion"]    })

					rest=rest+cur[0]["shares"]
					rest=set_sign_of_other_number(row["shares"],rest)
					cur.pop(0)
			else:
				cur.insert(0, {"id":row["id"], "investments_id":row["investments_id"], "datetime":row["datetime"] , "shares": rest, "price": row["price"], "operationstypes_id": operationstypes_id, "taxes":row["taxes"], "commission": row["commission"], "currency_conversion": row["currency_conversion"]}) 
				break
					
return cur

$_$;


ALTER FUNCTION public.investment_operations_current(p_investment_id integer, p_at_datetime timestamp with time zone) OWNER TO postgres;

--
-- Name: investment_operations_historical(integer, timestamp with time zone); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.investment_operations_historical(p_investment_id integer, p_at_datetime timestamp with time zone) RETURNS TABLE(id integer, investments_id integer, dt_start timestamp with time zone, dt_end timestamp with time zone, shares numeric, buyprice numeric, sellprice numeric, operationstypes_id integer, taxes numeric, commission numeric, buycc numeric, sellcc numeric)
    LANGUAGE plpython3u
    AS $_$
from datetime import datetime

have_same_sign = lambda a, b: True if (a>=0 and b>=0) or (a<0 and b<0) else False
set_sign_of_other_number = lambda number, number_to_change: abs(number_to_change) if number>=0 else -abs(number_to_change)

ioh_id=0
cur=[]
hist=[]
plan=plpy.prepare('SELECT * from investmentsoperations where investments_id=$1 and datetime <=$2  order by datetime', ["integer","timestamp with time zone"])
for row in plan.cursor( [p_investment_id, p_at_datetime]):
	operationstypes_id=4 if row["shares"]>=0 else 5
	if len(cur)==0 or have_same_sign(cur[0]["shares"], row["shares"]) is True:
		cur.append(row)
	elif have_same_sign(cur[0]["shares"], row["shares"]) is False:
		rest=row["shares"]
		ciclos=0
		while rest!=0:
			ciclos=ciclos+1
			commissions=0
			taxes=0
			if ciclos==1:
				commissions=row["commission"]+cur[0]["commission"]
				taxes=row["taxes"]+cur[0]["taxes"]
		
			if len(cur)>0:
				if abs(cur[0]["shares"])>=abs(rest):
					ioh_id=ioh_id+1
					hist.append({"shares":set_sign_of_other_number(row["shares"],rest),"id":ioh_id, "investments_id": p_investment_id, "dt_start":cur[0]["datetime"], "dt_end":row["datetime"], "operationstypes_id":operationstypes_id, "commission":commissions, "taxes":taxes, "buyprice":cur[0]["price"], "sellprice":row["price"],"buycc":cur[0]["currency_conversion"], "sellcc":row["currency_conversion"]    })
					if rest+cur[0]["shares"]!=0:
						cur.insert(0, {"id":row["id"], "investments_id":row["investments_id"], "datetime":cur[0]["datetime"] , "shares": rest+cur[0]["shares"], "price": row["price"], "operationstypes_id": operationstypes_id, "taxes":row["taxes"], "commission": row["commission"], "currency_conversion": row["currency_conversion"]}) 
						cur.pop(1)
					else:
						cur.pop(0)
					rest=0
					break
				else:
					ioh_id=ioh_id+1
					hist.append({"shares":set_sign_of_other_number(row["shares"],cur[0]["shares"]),"id":ioh_id, "investments_id": p_investment_id, "dt_start":cur[0]["datetime"], "dt_end":row["datetime"], "operationstypes_id":operationstypes_id, "commission":commissions, "taxes":taxes, "buyprice":cur[0]["price"], "sellprice":row["price"],"buycc":cur[0]["currency_conversion"], "sellcc":row["currency_conversion"]    })

					rest=rest+cur[0]["shares"]
					rest=set_sign_of_other_number(row["shares"],rest)
					cur.pop(0)
			else:
				cur.insert(0, {"id":row["id"], "investments_id":row["investments_id"], "datetime":row["datetime"] , "shares": rest, "price": row["price"], "operationstypes_id": operationstypes_id, "taxes":row["taxes"], "commission": row["commission"], "currency_conversion": row["currency_conversion"]}) 
				break
					
return hist

$_$;


ALTER FUNCTION public.investment_operations_historical(p_investment_id integer, p_at_datetime timestamp with time zone) OWNER TO postgres;

--
-- Name: is_price_variation_in_time(integer, double precision, timestamp with time zone); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.is_price_variation_in_time(p_id_products integer, p_percentage double precision, p_datetime timestamp with time zone) RETURNS boolean
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

CREATE FUNCTION public.last_penultimate_lastyear(INOUT id integer, at_datetime timestamp with time zone, OUT last_datetime timestamp with time zone, OUT last numeric, OUT penultimate_datetime timestamp with time zone, OUT penultimate numeric, OUT lastyear_datetime timestamp with time zone, OUT lastyear numeric) RETURNS record
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

CREATE FUNCTION public.money_convert(at_datetime timestamp with time zone, amount_from numeric, currency_from text, currency_to text) RETURNS numeric
    LANGUAGE plpgsql
    AS $$
DECLARE
	factor NUMERIC;
BEGIN
	IF amount_from IS NULL THEN return NULL; END IF;
	IF currency_from = currency_to THEN
		factor:=1;
	ELSIF currency_from = 'EUR' AND currency_to = 'USD' THEN
		select quote INTO factor from quote(74747, at_datetime);
	ELSIF currency_from = 'USD' AND currency_to = 'EUR' THEN
		select quote INTO factor from quote(74747, at_datetime);
		factor:=1/factor;
	END IF;
	
	IF factor IS NULL THEN return NULL; ELSE return amount_from *factor; END IF;
END;
$$;


ALTER FUNCTION public.money_convert(at_datetime timestamp with time zone, amount_from numeric, currency_from text, currency_to text) OWNER TO postgres;

--
-- Name: ohcldailybeforesplits(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.ohcldailybeforesplits(product_id integer) RETURNS TABLE(date date, open numeric, high numeric, low numeric, close numeric)
    LANGUAGE plpgsql
    AS $$
DECLARE 
    o record;
BEGIN
    FOR o IN (            select 
                id, 
                datetime::date as date, 
                (array_agg(quote order by datetime))[1] as open, 
                min(quote) as low, 
                max(quote) as high, 
                (array_agg(quote order by datetime desc))[1] as close 
            from quotes 
            where products_id=product_id
            group by products_id, datetime::date 
            order by datetime::date )  
    LOOP
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

CREATE FUNCTION public.ohclmonthlybeforesplits(product_id integer) RETURNS TABLE(year integer, month integer, open numeric, high numeric, low numeric, close numeric)
    LANGUAGE plpgsql
    AS $$
DECLARE 
    o record;
BEGIN
    FOR o IN (                   select 
                date_part('year',date) as year, 
                date_part('month', date) as month, 
                (array_agg(t.open order by date))[1] as open, 
                min(t.low) as low, 
                max(t.high) as high, 
                (array_agg(t.close order by date desc))[1] as close 
            from ohclDailyBeforeSplits(product_id) as t
            group by  year, month 
            order by year, month)
    LOOP
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

CREATE FUNCTION public.penultimate(INOUT id integer, date date, OUT quote numeric, OUT datetime timestamp with time zone, OUT searched timestamp with time zone) RETURNS record
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
-- Name: quote(integer, timestamp with time zone); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.quote(INOUT id integer, INOUT datetime timestamp with time zone, OUT quote numeric, OUT searched timestamp with time zone) RETURNS record
    LANGUAGE plpgsql
    AS $$
BEGIN
    searched := quote.datetime;
    SELECT quotes.quote, quotes.datetime  INTO quote.quote, quote.datetime FROM quotes where quotes.products_Id= quote.id and quotes.datetime <= quote.datetime order by quotes.datetime desc limit 1;
END;
$$;


ALTER FUNCTION public.quote(INOUT id integer, INOUT datetime timestamp with time zone, OUT quote numeric, OUT searched timestamp with time zone) OWNER TO postgres;

--
-- Name: same_sign(numeric, numeric); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.same_sign(a numeric, b numeric) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
DECLARE
	factor NUMERIC;
BEGIN
	IF (a >= 0 and b>=0) OR (a<0 and b<0) THEN
	    return TRUE;
	ELSE 
		return FALSE;
	END IF;
	
END;
$$;


ALTER FUNCTION public.same_sign(a numeric, b numeric) OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

