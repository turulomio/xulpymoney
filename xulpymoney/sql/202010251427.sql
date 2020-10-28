drop function public.total_balance;
drop function public.investment_operations;
drop function public.investment_operations_totals;
drop function public.investment_operations_alltotals;
drop function public.money_convert;
drop function public.currency_factor;

-- FUNCTION: public.total_balance(timestamp with time zone, text)

-- DROP FUNCTION public.total_balance(timestamp with time zone, text);

CREATE OR REPLACE FUNCTION public.total_balance(
    p_at_datetime timestamp with time zone,
    user_currency text)
    RETURNS TABLE(accounts_user numeric, investments_user numeric, total_user numeric, investments_invested_user numeric) 
    LANGUAGE 'plpython3u'

    COST 100
    VOLATILE 
    ROWS 1000
    
AS $BODY$
## Esta función debe usarse cuando no nos interesan los datos sino los saldos de todas las inversiones
from decimal import Decimal
plan_accounts=plpy.prepare('SELECT * from  accounts_balance($1,$2)',["timestamp with time zone","text"])
accounts=plpy.execute(plan_accounts, (p_at_datetime,user_currency))
plan_investments=plpy.prepare('SELECT * from investment_operations_alltotals($1,$2,false)',["timestamp with time zone","text"])
investments=plpy.execute(plan_investments, (p_at_datetime,user_currency))

accounts_user=accounts[0]['accounts_balance']
investments=eval(investments[0]['io_current'])
investments_user=investments['balance_user']
    
return [{ 
    "accounts_user": accounts_user, 
    "investments_user": investments_user,
    "total_user": accounts_user+investments_user,
    "investments_invested_user": investments['invested_user'],
},]
$BODY$;

ALTER FUNCTION public.total_balance(timestamp with time zone, text)
    OWNER TO postgres;


-- FUNCTION: public.investment_operations(integer, timestamp with time zone, text)

-- DROP FUNCTION public.investment_operations(integer, timestamp with time zone, text);

CREATE OR REPLACE FUNCTION public.investment_operations(
    p_investment_id integer,
    p_at_datetime timestamp with time zone,
    user_currency text)
    RETURNS TABLE(io text, io_current text, io_historical text) 
    LANGUAGE 'plpython3u'

    COST 100
    VOLATILE 
    ROWS 1000
    
AS $BODY$
## Esta función crea dos listas de diccionarios para current y para historica, las convierte a textos y las devuelve
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
    c['invested_investment']=c['shares']*c['price_investment']*c['real_leverages']
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

## -------------------- COPIAR HASTA AQUI ------------------------
$BODY$;

ALTER FUNCTION public.investment_operations(integer, timestamp with time zone, text)
    OWNER TO postgres;


-- FUNCTION: public.investment_operations_totals(integer, timestamp with time zone, text)

-- DROP FUNCTION public.investment_operations_totals(integer, timestamp with time zone, text);

CREATE OR REPLACE FUNCTION public.investment_operations_totals(
    p_investment_id integer,
    p_at_datetime timestamp with time zone,
    user_currency text)
    RETURNS TABLE(io text, io_current text, io_historical text) 
    LANGUAGE 'plpython3u'

    COST 100
    VOLATILE 
    ROWS 1000
    
AS $BODY$
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
    "gains_gross_user":sumador(io_current, 'gains_gross_user'),
    "shares":sumador(io_current, 'shares'),
    "price_investment":sumador(io_current, 'price_investment'),
    "invested_user":sumador(io_current, 'invested_user'),
}

d_io_historical={
    "commissions_account":sumador(io_historical, 'commissions_account'),
    "gains_net_user":sumador(io_historical, 'gains_net_user'),
}

return [{ "io": str(d_io), "io_current": str(d_io_current),"io_historical":str(d_io_historical)}]
$BODY$;

ALTER FUNCTION public.investment_operations_totals(integer, timestamp with time zone, text)
    OWNER TO postgres;


-- FUNCTION: public.investment_operations_alltotals(timestamp with time zone, text, boolean)

-- DROP FUNCTION public.investment_operations_alltotals(timestamp with time zone, text, boolean);

CREATE OR REPLACE FUNCTION public.investment_operations_alltotals(
    p_at_datetime timestamp with time zone,
    user_currency text,
    onlyactive boolean)
    RETURNS TABLE(io text, io_current text, io_historical text) 
    LANGUAGE 'plpython3u'

    COST 100
    VOLATILE 
    ROWS 1000
    
AS $BODY$
## Esta función debe usarse cuando no nos interesan los datos sino los saldos de todas las inversiones
from decimal import Decimal
if onlyactive is True:
    plan=plpy.prepare('SELECT id, (investment_operations_totals(id ,$1,$2)).io, (investment_operations_totals(id ,$1,$2)).io_current, (investment_operations_totals(id ,$1,$2)).io_historical from investments where active is true',["timestamp with time zone","text"])
else:
    plan=plpy.prepare('SELECT id, (investment_operations_totals(id ,$1,$2)).io, (investment_operations_totals(id ,$1,$2)).io_current, (investment_operations_totals(id ,$1,$2)).io_historical from investments',["timestamp with time zone","text"])

data=plpy.execute(plan, (p_at_datetime,user_currency))

io=[]
io_current=[]
io_historical=[]
for row in data:#Convierte los campos io, io_current e io_historical a sus valores y los mete en unas listas
    io.append(eval(row['io']))
    io_current.append(eval(row['io_current']))
    io_historical.append(eval(row['io_historical']))

    
#plpy.warning(io)
sumador= lambda l, key: sum(d[key] if d[key] is not None else 0 for d  in l)

d_io={
    "price":sumador(io, 'price'),
}

d_io_current={
    "balance_user":sumador(io_current, 'balance_user'),
    "gains_gross_user":sumador(io_current, 'gains_gross_user'),
    "shares":sumador(io_current, 'shares'),
    "price_investment":sumador(io_current, 'price_investment'),
    "invested_user":sumador(io_current, 'invested_user'),
}

d_io_historical={
    "commissions_account":sumador(io_historical, 'commissions_account'),
}

return [{ "io": str(d_io), "io_current": str(d_io_current),"io_historical":str(d_io_historical)}]
$BODY$;

ALTER FUNCTION public.investment_operations_alltotals(timestamp with time zone, text, boolean)
    OWNER TO postgres;


-- FUNCTION: public.currency_factor(timestamp with time zone, text, text)

-- DROP FUNCTION public.currency_factor(timestamp with time zone, text, text);

CREATE OR REPLACE FUNCTION public.currency_factor(
    at_datetime timestamp with time zone,
    currency_from text,
    currency_to text)
    RETURNS numeric
    LANGUAGE 'plpgsql'

    COST 100
    VOLATILE 
    
AS $BODY$
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
$BODY$;

ALTER FUNCTION public.currency_factor(timestamp with time zone, text, text)
    OWNER TO postgres;




-- FUNCTION: public.money_convert(timestamp with time zone, numeric, text, text)

-- DROP FUNCTION public.money_convert(timestamp with time zone, numeric, text, text);

CREATE OR REPLACE FUNCTION public.money_convert(
    at_datetime timestamp with time zone,
    amount_from numeric,
    currency_from text,
    currency_to text)
    RETURNS numeric
    LANGUAGE 'plpgsql'

    COST 100
    VOLATILE 
    
AS $BODY$
DECLARE
    factor NUMERIC;
BEGIN
    select currency_factor INTO factor from currency_factor(at_datetime,currency_from,currency_to);
    -- Should return None but I return amount_from to avoid errors
    IF factor IS NULL THEN return amount_from; ELSE return amount_from *factor; END IF;
END;
$BODY$;

ALTER FUNCTION public.money_convert(timestamp with time zone, numeric, text, text)
    OWNER TO postgres;
