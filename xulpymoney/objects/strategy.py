from PyQt5.QtCore import QObject
from datetime import timedelta
from xulpymoney.casts import list2string, string2list_of_integers
from xulpymoney.libmanagers import ObjectManager_With_IdName_Selectable
from xulpymoney.objects.dividend import DividendHeterogeneusManager
from xulpymoney.objects.investment import InvestmentManager_from_list_of_ids
from xulpymoney.objects.investmentoperation import InvestmentOperationCurrentHeterogeneusManager, InvestmentOperationHistoricalHeterogeneusManager

class Strategy(QObject):
    def __init__(self, mem=None,name=None,  investments=None, dt_from=None, dt_to=None, id=None):
        QObject.__init__(self)
        self.mem=mem
        self.name=name
        self.investments=investments
        self.dt_from=dt_from
        self.dt_to=dt_to
        self.id=id

    def __repr__(self):
        return ("Strategy '{0}' ({1})".format( self.name, self.id))

    def save(self):
        if self.investments is None:
            investments=""
        else:
            investments=list2string(self.investments.array_of_ids())
        if self.id==None:
            self.id=self.mem.con.cursor_one_field("insert into strategies (name, investments, dt_from, dt_to) values (%s,%s,%s,%s) returning id", 
                (self.name, investments,  self.dt_from, self.dt_to))
        else:
            self.mem.con.execute("update strategies set name=%s, investments=%s, dt_from=%s, dt_to=%s where id=%s", 
                (self.name, investments,  self.dt_from,  self.dt_to, self.id))

    def delete(self):
        self.mem.con.execute("delete from strategies where id=%s", (self.id, ))
        
    ## @return boolean True if it's dt_end is None or greater than current time
    def is_active(self):
        if self.dt_from<=self.mem.localzone_now() and self.mem.localzone_now()<=self.dt_to_for_comparations():
            return True
        return False
        
    ## Replaces None for dt_to and sets a very big datetine
    def dt_to_for_comparations(self):
        if self.dt_to is None:
            return self.mem.localzone_now()+timedelta(days=365*100)
        return self.dt_to

    ## Returns strategy current operations
    def dividends(self):
        r=DividendHeterogeneusManager(self.mem)
        for inv in self.investments:
            inv.needStatus(3)
            for o in inv.dividends:
                if self.dt_from<=o.datetime and o.datetime<=self.dt_to_for_comparations():
                    r.append(o)
        r.order_by_datetime()
        return r          

    ## Returns strategy current operations
    def currentOperations(self):
        r=InvestmentOperationCurrentHeterogeneusManager(self.mem)
        for inv in self.investments:
            for o in inv.op_actual:
                if self.dt_from<=o.datetime and o.datetime<=self.dt_to_for_comparations():
                    r.append(o)
        r.order_by_datetime()
        return r        
        
    ## Returns strategy current operations
    def historicalOperations(self):
        r=InvestmentOperationHistoricalHeterogeneusManager(self.mem)
        for inv in self.investments:
            for o in inv.op_historica:
                if self.dt_from<=o.dt_end and o.dt_end<=self.dt_to_for_comparations():
                    r.append(o)
        r.order_by_fechaventa()
        return r

class StrategyManager(QObject, ObjectManager_With_IdName_Selectable):   
    def __init__(self, mem):
        QObject.__init__(self)
        ObjectManager_With_IdName_Selectable.__init__(self)
        self.mem=mem

    ## @param active_strategies Boolean. True uses active strategies. False uses inactive strategies
    def current_gains(self, active_strategies=True):
        r=self.mem.localmoney_zero()
        for o in self:
            if o.is_active()==active_strategies:
                r=r+o.currentOperations().pendiente()
        return r     

    ## @param active_strategies Boolean. True uses active strategies. False uses inactive strategies
    def historical_gains_net(self, active_strategies=True):
        r=self.mem.localmoney_zero()
        for o in self:
            if o.is_active()==active_strategies:
                r=r+o.historicalOperations().consolidado_neto()
        return r

    ## @param active_strategies Boolean. True uses active strategies. False uses inactive strategies
    def dividends_net(self, active_strategies=True):
        r=self.mem.localmoney_zero()
        for o in self:
            if o.is_active()==active_strategies:
                r=r+o.dividends().net()
        return r
    
    ## @param table myQTableWidget
    ## @param active Boolean to show active or inactive rows
    def myqtablewidget(self, wdg, finished):
        data=[]
        for i, o in enumerate(self.arr):
            current=o.currentOperations().pendiente()
            historical=o.historicalOperations().consolidado_neto()
            dividends=o.dividends().net()
            data.append([
                o.name, 
                o.dt_from, 
                o.dt_to, 
                current, 
                historical, 
                dividends, 
                current+historical+dividends, 
                o, 
            ])
        wdg.auxiliar=finished## Adds this auxiliar value to allow additional filter active / no active
        wdg.setDataWithObjects(
            [self.tr("Name"), self.tr("Date from"), self.tr("Date to"), self.tr("Gains"), self.tr("Net historical gains"), self.tr("Net dividends"), self.tr("Total gains")], 
            None, 
            data, 
            decimals=2, 
            zonename=self.mem.localzone_name, 
            additional=self.myqtablewidget_additional
        )

    def myqtablewidget_additional(self, wdg):
        wdg.table.setRowCount(wdg.length()+1)
        for i, o in enumerate(wdg.objects()):            
            if wdg.auxiliar is True:#Only finished
                if o.dt_to is not None:
                    wdg.table.showRow(i)
                else:
                    wdg.table.hideRow(i)
            else:# Current strategies
                if o.dt_to is None:
                    wdg.table.showRow(i)
                else:
                    wdg.table.hideRow(i)
        current=self.current_gains(not wdg.auxiliar)
        historical=self.historical_gains_net(not wdg.auxiliar)
        dividends=self.dividends_net(not wdg.auxiliar)
        wdg.addRow(wdg.length(), [self.tr("Total"), "#crossedout", "#crossedout", current,historical,dividends,current+historical+dividends])

def Strategy_from_dict(mem, row):
    r=Strategy(mem)
    r.id=row['id']
    r.name=row['name']
    r.investments=InvestmentManager_from_list_of_ids(mem, string2list_of_integers(row['investments']))
    r.dt_from=row['dt_from']
    r.dt_to=row['dt_to']
    return r

def StrategyManager_from_sql(mem, sql):
    r=StrategyManager(mem)
    for row in mem.con.cursor_rows(sql):
        r.append(Strategy_from_dict(mem, row))
    return r
    
def StrategyManager_all(mem):
    return StrategyManager_from_sql(mem, "select * from strategies order by name")
