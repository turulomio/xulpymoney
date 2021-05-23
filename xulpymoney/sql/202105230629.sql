

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

have_same_sign = lambda a, b: True if (a>=0 and b>=0) or (a<0 and b<0) else False
set_sign_of_other_number = lambda number, number_to_change: abs(number_to_change) if number>=0 else -abs(number_to_change)
operationstypes= lambda shares: 4 if shares>=0 else 5



ioh_id=0
io=[]
cur=[]
hist=[]
plan=plpy.prepare('SELECT * from investmentsoperations where investments_id=$1 and datetime <=$2  order by datetime', ["integer","timestamp with time zone"])

# Dictionary account2user datetime objects as keys
a2u={}
a2u[p_at_datetime]=plpy.execute(cf_plan, (p_at_datetime, data['accounts_currency'], user_currency))[0]['currency_factor']

for row in plan.cursor( [p_investment_id, p_at_datetime]):
    a2u[row["datetime"]]=plpy.execute(cf_plan, (row['datetime'], data['accounts_currency'], user_currency ))[0]['currency_factor']

    io.append(row)
    if len(cur)==0 or have_same_sign(cur[0]["shares"], row["shares"]) is True:
        cur.append({"id":row["id"], "investments_id":row["investments_id"], "datetime":row["datetime"] , "shares": row["shares"], "price_investment": row["price"], "operationstypes_id": row['operationstypes_id'], "taxes_account":row["taxes"], "commissions_account": row["commission"], "investment2account": row["currency_conversion"]}) 
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
                    hist.append({"shares":set_sign_of_other_number(row["shares"],rest),"id":ioh_id, "investments_id": p_investment_id, "dt_start":cur[0]["datetime"], "dt_end":row["datetime"], "operationstypes_id": operationstypes(rest), "commissions_account":commissions, "taxes_account":taxes, "price_start_investment":cur[0]["price_investment"], "price_end_investment":row["price"],"investment2account_start":cur[0]["investment2account"], "investment2account_end":row["currency_conversion"]    })
                    if rest+cur[0]["shares"]!=0:
                        cur.insert(0, {"id":cur[0]["id"], "investments_id":cur[0]["investments_id"], "datetime":cur[0]["datetime"] , "shares": rest+cur[0]["shares"], "price_investment": cur[0]["price_investment"], "operationstypes_id": cur[0]['operationstypes_id'], "taxes_account":cur[0]["taxes_account"], "commissions_account": cur[0]["commissions_account"], "investment2account": cur[0]["investment2account"]}) 
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
                cur.insert(0, {"id":row["id"], "investments_id":row["investments_id"], "datetime":row["datetime"] , "shares": rest, "price_investment": row["price"], "operationstypes_id": row['operationstypes_id'],"taxes_account":row["taxes"], "commissions_account": row["commission"], "investment2account": row["currency_conversion"]}) 
                break

for o in io:
    o['real_leverages']= realmultiplier(data)       
    o['currency_investment']=data['products_currency']     
    o['currency_account']=data['accounts_currency']
    o['currency_user']=user_currency
    o['commission_account']=o['commission']
    o['taxes_account']=o['taxes']
    o['gross_investment']=abs(o['shares']*o['price']*o['real_leverages'])
    o['gross_account']=o['gross_investment']*o['currency_conversion']
    o['gross_user']=o['gross_account']*a2u[o['datetime']]
    o['account2user']=a2u[o['datetime']]
    o['gross_user']=o['gross_account']*o['account2user']
    if o['shares']>=0:
        o['net_account']=o['gross_account']+o['commission_account']+o['taxes_account']
    else:
        o['net_account']=o['gross_account']-o['commission_account']-o['taxes_account']
    o['net_user']=o['net_account']*a2u[o['datetime']]
    o['net_investment']=o['net_account']/o['currency_conversion']

for c in cur:
    c['real_leverages']= realmultiplier(data)
    c['investment2account_at_datetime']=investment2account_at_datetime
    c['account2user_at_datetime']=a2u[p_at_datetime] 
    c['currency_investment']=data['products_currency']        
    c['currency_account']=data['accounts_currency']
    c['currency_user']=user_currency
    c['account2user']=a2u[c['datetime']]
    c['price_account']=c['price_investment']*c['investment2account']
    c['price_user']=c['price_account']*c['account2user']
    c['taxes_investment']=c['taxes_account']/c['investment2account']#taxes and commissions are in account currency buy we can guess them
    c['taxes_user']=c['taxes_account']*c['account2user']
    c['commissions_investment']=c['commissions_account']/c['investment2account']
    c['commissions_user']=c['commissions_account']*c['account2user']
    #Si son cfds o futuros el saldo es 0, ya que es un contrato y el saldo todavía está en la cuenta. Sin embargo cuento las perdidas
    c['balance_investment']=0 if data['productstypes_id'] in (12,13) else abs(c['shares'])*quote_at_datetime*c['real_leverages']
    c['balance_account']=c['balance_investment']*investment2account_at_datetime
    c['balance_user']=c['balance_account']*a2u[p_at_datetime]
    #Aquí calculo con saldo y futuros y cfd
    if c['shares']>0:
        c['balance_futures_investment']=c['shares']*quote_at_datetime*c['real_leverages']
    else:
        diff=(quote_at_datetime-c['price_investment'])*abs(c['shares'])*c['real_leverages']
        init_balance=c['price_investment']*abs(c['shares'])*c['real_leverages']
        c['balance_futures_investment']=init_balance-diff
    c['balance_futures_account']=c['balance_futures_investment']*investment2account_at_datetime
    c['balance_futures_user']=c['balance_futures_account']*a2u[p_at_datetime]
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
    h['account2user_start']=a2u[h['dt_start']]
    h['account2user_end']=a2u[h['dt_end']]
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
    h['gross_start_account']=h['gross_start_investment']*h['investment2account_start']
    h['gross_start_user']=h['gross_start_account']*h['account2user_start']
    h['gross_end_account']=h['gross_end_investment']*h['investment2account_end']
    h['gross_end_user']=h['gross_end_account']*h['account2user_end']
    h['gains_gross_account']=h['gross_end_account']-h['gross_start_account']
    h['gains_gross_user']=h['gross_end_user']-h['gross_start_user']

    h['taxes_investment']=h['taxes_account']/h['investment2account_end']#taxes and commissions are in account currency buy we can guess them
    h['taxes_user']=h['taxes_account']*h['account2user_end']
    h['commissions_investment']=h['commissions_account']/h['investment2account_end']
    h['commissions_user']=h['commissions_account']*h['account2user_end']
    h['gains_net_investment']=h['gains_gross_investment']-h['taxes_investment']-h['commissions_investment']
    h['gains_net_account']=h['gains_gross_account']-h['taxes_account']-h['commissions_account']
    h['gains_net_user']=h['gains_gross_user']-h['taxes_user']-h['commissions_user']

return [{ "io": str(io), "io_current": str(cur),"io_historical":str(hist)}]
$_$;


ALTER FUNCTION public.investment_operations(p_investment_id integer, p_at_datetime timestamp with time zone, user_currency text) OWNER TO postgres;
