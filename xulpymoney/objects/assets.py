from datetime import datetime, timedelta, date
from xulpymoney.objects.money import Money
from xulpymoney.casts import none2decimal0
from xulpymoney.objects.currency import MostCommonCurrencyTypes
from xulpymoney.libxulpymoneytypes import eProductType, eConcept
from xulpymoney.datetime_functions import dtaware_day_end_from_date

class Assets:
    def __init__(self, mem):
        self.mem=mem        
    
    def first_database_datetime(self):        
        cur=self.mem.con.cursor()
        sql='select datetime from accountsoperations UNION all select datetime from investmentsoperations UNION all select datetime from creditcardsoperations order by datetime limit 1;'
        cur.execute(sql)
        if cur.rowcount==0:
            cur.close()
            return datetime.now()
        else:
            resultado=cur.fetchone()[0]
            cur.close()
            return resultado

    def first_datetime_allowed_estimated(self):
        return self.first_database_datetime()-timedelta(days=365*5)

    def last_database_datetime(self):        
        cur=self.mem.con.cursor()
        sql='select datetime from accountsoperations UNION all select datetime from investmentsoperations UNION all select datetime from creditcardsoperations order by datetime desc limit 1;'
        cur.execute(sql)
        if cur.rowcount==0:
            cur.close()
            return datetime.now()
        else:
            resultado=cur.fetchone()[0]
            cur.close()
            return resultado

    def last_datetime_allowed_estimated(self):
        return self.last_database_datetime()+timedelta(days=365*5)

    def saldo_todas_accounts(self,  fecha):
        dt=dtaware_day_end_from_date(fecha, self.mem.localzone_name)
        r=self.mem.con.cursor_one_field("select accounts_balance(%s,%s)", (dt, self.mem.localcurrency))
        return Money(self.mem, r, self.mem.localcurrency)

        
    def saldo_total(self, setinversiones,  fe):
        """Versión que se calcula en cliente muy optimizada"""
        return self.saldo_todas_accounts(fe)+self.saldo_todas_inversiones(fe)

    ## This method gets all investments balance. High-Low investments are not sumarized, due to they have daily account adjustments
    ##
    ## Esta función se calcula en cliente
    def saldo_todas_inversiones(self, fecha):
#        resultado=Money(self.mem, 0, self.mem.localcurrency)
#        for i in self.mem.data.investments.arr:
#            if i.daily_adjustment is False:#Due to there is a daily adjustments in accouts 
#                resultado=resultado+i.balance(fecha, type=3)
#        return resultado
        dt=dtaware_day_end_from_date(fecha, self.mem.localzone_name)
        r=self.mem.con.cursor_one_row("select * from total_balance(%s,%s)", (dt, self.mem.localcurrency))
        print(r, fecha)
        return Money(self.mem, r[1], self.mem.localcurrency)

    ## This method gets all investments balance. High-Low investments are not sumarized, due to they have daily account adjustments
    ##
    ## Esta función se calcula en cliente
    def saldo_todas_inversiones_real(self, fecha):
        resultado=Money(self.mem, 0, self.mem.localcurrency)
        dt=dtaware_day_end_from_date(fecha, self.mem.localzone_name)
        for i in self.mem.data.investments.arr:
            if i.daily_adjustment is False:#Due to there is a daily adjustments in accouts 
                resultado=resultado+i.balance_real(dt, type=3)
        return resultado

    ## This method gets all High-Low investments balance
    ##
    ## Esta función se calcula en cliente
    def saldo_todas_inversiones_with_daily_adjustment(self, fecha):
        resultado=Money(self.mem, 0, self.mem.localcurrency)
        for i in self.mem.data.investments.arr:
            if i.daily_adjustment is True:
                resultado=resultado+i.balance(fecha, type=3)
        return resultado

    def saldo_todas_inversiones_riesgo_cero(self, fecha=None):
        """Versión que se calcula en cliente muy optimizada
        Fecha None calcula  el balance actual
        """
        resultado=Money(self.mem, 0, self.mem.localcurrency)
        for inv in self.mem.data.investments.arr:
            if inv.product.percentage==0:        
                resultado=resultado+inv.balance( fecha, type=3)
        return resultado
            
    def dividends_neto(self, ano,  mes=None):
        """Dividend cobrado en un año y mes pasado como parámetro, independientemente de si la inversión esta activa o no.
        El 63 es un gasto aunque también este registrado en dividends."""
        r=Money(self.mem, 0, self.mem.localcurrency)
        for inv in self.mem.data.investments.arr:
            inv.needStatus(3)
            for dividend in inv.dividends.arr:
                if mes==None:
                    if dividend.datetime.year==ano:
                        r=r+dividend.net(type=3)
                else:# WIth mounth
                    if dividend.datetime.year==ano and dividend.datetime.month==mes:
                        r=r+dividend.net(type=3)
        return r

    def dividends_bruto(self,  ano,  mes=None):
        """Dividend cobrado en un año y mes pasado como parámetro, independientemente de si la inversión esta activa o no"""
        r=Money(self.mem, 0, self.mem.localcurrency)
        for inv in self.mem.data.investments.arr:
            inv.needStatus(3)
            for dividend in inv.dividends.arr:
                if mes==None:
                    if dividend.datetime.year==ano:
                        r=r+dividend.gross(type=3)
                else:# WIth mounth
                    if dividend.datetime.year==ano and dividend.datetime.month==mes:
                        r=r+dividend.net(type=3)
        return r

    ## @return Money Returns the balance of dividend estimated of the current year.
    def dividends_estimated(self):
        sumdiv=Money(self.mem, 0, self.mem.localcurrency)
        for i, inv in enumerate(self.mem.data.investments_active().arr):
            if inv.product.estimations_dps.find(date.today().year) is not None:
                sumdiv=sumdiv+inv.dividend_bruto_estimado().local()
        return sumdiv

    def invested(self, date=None):
        """Devuelve el patrimonio invertido en una determinada fecha"""
        if date==None or date==date.today():
            array=self.mem.data.investments_active().arr #Current and active
        else:
            array=self.mem.data.investments.arr#All, because i don't know witch one was active.
        
        r=Money(self.mem, 0, self.mem.localcurrency)
        for inv in array:
            r=r+inv.invertido(date, type=3)
        return r
    def invested_real(self, date=None):
        """Devuelve el patrimonio invertido en una determinada fecha"""
        if date==None or date==date.today():
            array=self.mem.data.investments_active().arr #Current and active
        else:
            array=self.mem.data.investments.arr#All, because i don't know witch one was active.
        
        r=Money(self.mem, 0, self.mem.localcurrency)
        for inv in array:
            r=r+inv.invested_real(date, type=3)
        return r
        
    def saldo_todas_inversiones_bonds(self, fecha=None):        
        """Versión que se calcula en cliente muy optimizada
        Fecha None calcula  el balance actual
        """
        resultado=Money(self.mem, 0, self.mem.localcurrency)
        for inv in self.mem.data.investments.arr:
            if inv.product.type.id in (eProductType.PublicBond, eProductType.PrivateBond):#public and private bonds        
                if fecha==None:
                    resultado=resultado+inv.balance().local()
                else:
                    resultado=resultado+inv.balance( fecha).local()
        return resultado

    def patrimonio_riesgo_cero(self, fecha):
        """CAlcula el patrimonio de riego cero"""
        return self.saldo_todas_accounts(fecha)+self.saldo_todas_inversiones_riesgo_cero(fecha)

    def saldo_anual_por_tipo_operacion(self,  year,  operationstypes_id):   
        """accountsoperations y creditcardsoperations"""
        resultado=Money(self.mem, 0, self.mem.localcurrency)
        for currency in MostCommonCurrencyTypes():
            cur=self.mem.con.cursor()
            sql="""
                select sum(amount) as amount 
                from 
                    accountsoperations,
                    accounts
                where 
                    operationstypes_id={0} and 
                    date_part('year',datetime)={1} and
                    accounts.currency='{2}' and
                    accounts.id=accountsoperations.accounts_id   
            union all 
                select sum(amount) as amount 
                from 
                    creditcardsoperations ,
                    creditcards,
                    accounts
                where 
                    operationstypes_id={0} and 
                    date_part('year',datetime)={1} and
                    accounts.currency='{2}' and
                    accounts.id=creditcards.accounts_id and
                    creditcards.id=creditcardsoperations.creditcards_id""".format(operationstypes_id, year,  currency)
            cur.execute(sql)        
            for i in cur:
                if i['amount']==None:
                    continue
                resultado=resultado+Money(self.mem, i['amount'], currency).local()
            cur.close()
        return resultado

    def saldo_por_tipo_operacion(self,  year,  month,  operationstypes_id):   
        """accountsoperations y creditcardsoperations"""
        resultado=Money(self.mem, 0, self.mem.localcurrency)
        for currency in MostCommonCurrencyTypes():
            cur=self.mem.con.cursor()
            sql="""
                select sum(amount) as amount 
                from 
                    accountsoperations,
                    accounts
                where 
                    operationstypes_id={0} and 
                    date_part('year',datetime)={1} and
                    date_part('month',datetime)={2} and
                    accounts.currency='{3}' and
                    accounts.id=accountsoperations.accounts_id   
            union all 
                select sum(amount) as amount 
                from 
                    creditcardsoperations ,
                    creditcards,
                    accounts
                where 
                    operationstypes_id={0} and 
                    date_part('year',datetime)={1} and
                    date_part('month',datetime)={2} and
                    accounts.currency='{3}' and
                    accounts.id=creditcards.accounts_id and
                    creditcards.id=creditcardsoperations.creditcards_id""".format(operationstypes_id, year, month,  currency)
            cur.execute(sql)        
            for i in cur:
                if i['amount']==None:
                    continue
                resultado=resultado+Money(self.mem, i['amount'], currency).local()
            cur.close()
        return resultado
        
    def consolidado_bruto(self, setinversiones,  year=None, month=None):
        """Si year es none calcula el historicca  si month es nonve calcula el anual sino el mensual"""
        resultado=Money(self.mem, 0, self.mem.localcurrency)
        for i in setinversiones.arr:        
            resultado=resultado+i.op_historica.consolidado_bruto(year, month)
        return resultado

    def consolidado_neto_antes_impuestos(self, setinversiones, year=None, month=None):
        """Si year es none calcula el historicca  si month es nonve calcula el anual sino el mensual"""
        resultado=Money(self.mem, 0, self.mem.localcurrency)
        for i in setinversiones.arr:        
            resultado=resultado+i.op_historica.consolidado_neto_antes_impuestos(year, month)
        return resultado

    def consolidado_neto(self, setinversiones, year=None, month=None):
        """Si year es none calcula el historicca  si month es nonve calcula el anual sino el mensual"""
        resultado=Money(self.mem, 0, self.mem.localcurrency)
        for i in setinversiones.arr:        
            resultado=resultado+i.op_historica.consolidado_neto(year, month).local()
        return resultado        

    ## Returns custody commissions from all accounts active and inactive between to datetimes
    def custody_commissions(self, dt_start, dt_end):
        #TODO IT SHOULD CONVERT AMOUNTS FROM ACCOUNTS WITH DIFFERENT CURRENCIES
        sql="""
select 
    sum(amount) 
from 
    accountsoperations 
where 
    concepts_id = %s and 
    datetime>%s and datetime<= %s
"""
        sql_params=(eConcept.CommissionCustody, dt_start, dt_end)
        amount= none2decimal0(self.mem.con.cursor_one_field(sql, sql_params))
        return Money(self.mem, amount, self.mem.localcurrency)
        
        
    ## Returns taxes balance from paid taxes and returned taxes between to datetimes
    def taxes(self, dt_start, dt_end):
        #TODO IT SHOULD CONVERT AMOUNTS FROM ACCOUNTS WITH DIFFERENT CURRENCIES
        sql="""
select 
    sum(amount) 
from 
    accountsoperations 
where 
    concepts_id in (%s, %s) and 
    datetime>%s and datetime<= %s
"""
        sql_params=(eConcept.TaxesReturn, eConcept.TaxesPayment, dt_start, dt_end)
        amount= none2decimal0(self.mem.con.cursor_one_field(sql, sql_params))
        return Money(self.mem, amount, self.mem.localcurrency)

    ## Returns investment commissions balance between to datetimes. Custody commisions are not included
    def investments_commissions(self, dt_start, dt_end):
        #TODO IT SHOULD CONVERT AMOUNTS FROM ACCOUNTS WITH DIFFERENT CURRENCIES
        sql="""
            select 
                -sum(commission) as suma 
            from 
                investmentsoperations 
            where  
                datetime>%s and datetime<= %s
"""
        sql_params=(dt_start, dt_end)
        amount= none2decimal0(self.mem.con.cursor_one_field(sql, sql_params))
        return Money(self.mem, amount, self.mem.localcurrency)
