## @brief Module to help calculate month totals
from datetime import date
from logging import debug
from xulpymoney.datetime_functions import date_last_of_the_month, months
from xulpymoney.libmanagers import ObjectManager
from xulpymoney.objects.assets import Assets
from xulpymoney.objects.money import Money
from xulpymoney.objects.percentage import Percentage

class TotalMonth:
    """All values are calculated in last day of the month"""
    def __init__(self, mem, year, month):
        self.mem=mem
        self.year=year
        self.month=month
        self.expenses_value=None
        self.no_loses_value=None
        self.dividends_value=None
        self.incomes_value=None
        self.funds_revaluation_value=None
        self.gains_value=None
        self.total_accounts_value=None
        self.total_investments_value=None
        self.total_investments_high_low_value=None
        self.total_zerorisk_value=None
        self.total_bonds_value=None
        
    def __eq__(self, other):
        if self.year==other.year and self.month==other.month:
            return True
        return False

    def i_d_g_e(self):
        return self.incomes()+self.dividends()+self.gains()+self.expenses()

    def d_g(self):
        """Dividends+gains"""
        return self.gains()+self.dividends()

    def expenses(self):
        if self.expenses_value==None:
            self.expenses_value=Assets(self.mem).saldo_por_tipo_operacion( self.year,self.month, 1)#La facturación de tarjeta dentro esta por el union
        return self.expenses_value

    def dividends(self):
        if self.dividends_value==None:
            self.dividends_value=Assets(self.mem).dividends_neto(  self.year, self.month)
        return self.dividends_value

    def incomes(self):
        if self.incomes_value==None:
            self.incomes_value=Assets(self.mem).saldo_por_tipo_operacion(  self.year,self.month,2)-self.dividends()
        return self.incomes_value

    def gains(self):
        if self.gains_value==None:
            self.gains_value=Assets(self.mem).consolidado_neto(self.mem.data.investments, self.year, self.month)
        return self.gains_value

    def funds_revaluation(self):
        if self.funds_revaluation_value==None:
            self.funds_revaluation_value=self.mem.data.investments_active().revaluation_monthly(2, self.year, self.month)#2 if type funds
        return self.funds_revaluation_value

    def name(self):
        return "{}-{}".format(self.year, self.month)

    def last_day(self):
        return date_last_of_the_month(self.year, self.month)

    def first_day(self):
        return date(self.year, self.month, self.day)

    def total(self):
        """Total assests in the month"""
        return self.total_accounts()+self.total_investments()

    ## Calculates total() difference of this TotalMonth and the one passed as parameter
    def total_difference(self, totalmonth):
        return self.total()-totalmonth.total()

    ## Calculates  difference percentage between totalmonth and the total with previous month
    def total_difference_percentage(self, totalmonth):
        return Percentage(self.total()-totalmonth.total(), totalmonth.total())

    def total_accounts(self):
        if self.total_accounts_value==None:
            self.total_accounts_value=Assets(self.mem).saldo_todas_cuentas( self.last_day())
        return self.total_accounts_value

    def total_investments(self):
        if self.total_investments_value==None:
            self.total_investments_value=Assets(self.mem).saldo_todas_inversiones(self.last_day())
        return self.total_investments_value

    def total_investments_high_low(self):
        if self.total_investments_high_low_value==None:
            self.total_investments_high_low_value=Assets(self.mem).saldo_todas_inversiones_high_low(self.last_day())
        return self.total_investments_high_low_value


    def total_zerorisk(self): 
        if self.total_zerorisk_value==None:
            self.total_zerorisk_value=Assets(self.mem).patrimonio_riesgo_cero(self.last_day())
        return self.total_zerorisk_value

    def total_bonds(self):
        if self.total_bonds_value==None:
            self.total_bonds_value=Assets(self.mem).saldo_todas_inversiones_bonds(self.last_day())
        return self.total_bonds_value

    def total_no_losses(self):
        if self.no_loses_value==None:
            self.no_loses_value=Assets(self.mem).invested(self.last_day())+self.total_accounts()
        return self.no_loses_value


## TotalMonth Manager
class TotalMonthManager(ObjectManager):
    def __init__(self, mem):
        ObjectManager.__init__(self)
        self.mem=mem

    def find(self, year, month):
        for m in self.arr:
            if m.year==year and m.month==month:
                return m
        return None

    ## Returns the TotalMonth object precedent in total
    ## @param totalmonth
    def find_previous(self, totalmonth):
        index=self.index(totalmonth)
        if index==0:
            debug ("Previous coudn't be found")
            return None
        else:
            return self.arr[index-1]
            
    ## @param totalmonth
    def find_previous_december(self, totalmonth):
        r=self.find(totalmonth.year-1, 12)
        if r is None:
            debug ("Previous december coudn't be found")
            return None
        else:
            return r

    def expenses(self):
        result=Money(self.mem, 0, self.mem.localcurrency)
        for m in self.arr:
            result=result+m.expenses()
        return result

    def i_d_g_e(self):
        return self.incomes()+self.dividends()+self.gains()+self.expenses()

    def funds_revaluation(self):
        return self.mem.data.investments_active().revaluation_annual(2, self.year)#2 if type funds

    def incomes(self):
        result=Money(self.mem, 0, self.mem.localcurrency)
        for m in self.arr:
            result=result+m.incomes()
        return result

    def gains(self):
        result=Money(self.mem, 0, self.mem.localcurrency)
        for m in self.arr:
            result=result+m.gains()
        return result        

    def dividends(self):
        result=Money(self.mem, 0, self.mem.localcurrency)
        for m in self.arr:
            result=result+m.dividends()
        return result

    def d_g(self):
        """Dividends+gains"""
        return self.gains()+self.dividends()


## Generate a TotalMonthManager from a month to current month. Useful to create wdgTotal graphics
def TotalMonthManager_from_month(mem, from_year, from_month, to_year, to_month):
    r=TotalMonthManager(mem)
    for year, month in months(from_year, from_month, to_year, to_month):
        r.append(TotalMonth(mem, year, month))
    return r

## Generate a TotalMonthManager extracting all TotalMonth from a a year from another manager
def TotalMonthManager_from_manager_extracting_year(manager, year):
    r=TotalMonthManager(manager.mem)
    for tm in manager.arr:
        if tm.year==year:
            r.append(tm)
    return r
    
## Generate a TotalMonthManager extracting all TotalMonth from a a year from another manager
def TotalMonthManager_from_manager_extracting_from_month(manager, from_year, from_month, to_year, to_month):
    r=TotalMonthManager(manager.mem)
    from_=date_last_of_the_month(from_year, from_month)
    to_=date_last_of_the_month(to_year, to_month)
    for tm in manager.arr:
        if date_last_of_the_month(tm.year, tm.month)>=from_ and date_last_of_the_month(tm.year, tm.month)<=to_:
            r.append(tm)
    return r
    
