import datetime
from decimal import Decimal
from xulpymoney.objects.money import Money
from xulpymoney.objects.percentage import Percentage
from xulpymoney.libxulpymoneyfunctions import relation_gains_risk
from xulpymoney.ui.myqwidgets import qmessagebox
from xulpymoney.libmanagers import ObjectManager_With_IdDate
from xulpymoney.libxulpymoneytypes import eQColor, eInvestmentTypePosition
from PyQt5.QtCore import QObject

## Class that register a purchase opportunity
class Opportunity:
    ## Constructor with the following attributes combination
    ## 1. Opportunity(mem). Crete a Opportunity object with all attributes set to None
    ## 1. Opportunity(mem, row). Create an Opportunity from a db row, generated in a database query
    ## 2. Opportunity(mem, date, removed, executed, entry, target, stoploss, products_id, id). Create a Opportunity passing all attributes
    ## @param mem MemXulpymoney object
    ## @param row Dictionary of a database query cursor
    ## @param date datetime.date object with the date of the Opportunity
    ## @param removed datetime.date object when the Opportunity was removed
    ## @param executed datetime.date object when the Opportunity was executed
    ## @param entry decimal.Decimal object with the Opportunity entry
    ## @param products_id Integer with the product id, after the constructur this integer is converted to self.product using mem
    ## @param id Integer that sets the id of an Opportunity. If id=None it's not in the database. id is set in the save method
    def __init__(self, *args):
        def init__db_row( row):
            init__create(row['date'], row['removed'], row['executed'], row['entry'], row['target'], row['stoploss'], row['products_id'], row['short'], row['id'])
        def init__create(date, removed, executed, entry, target, stoploss, products_id, short, id):
            self.date=date
            self.removed=removed
            self.executed=executed
            self.entry=entry
            self.stoploss=stoploss
            self.target=target
            if products_id!=None:
                self.product=self.mem.data.products.find_by_id(products_id)
                self.product.needStatus(1)
            else:
                self.product=None
            self.short=short
            self.id=id
        self.mem=args[0]
        if len(args)==1:
            init__create(None, None, None, Decimal('0'), Decimal('0'), Decimal('0'), None, None, None)
        if len(args)==2:
            init__db_row(args[1])
        if len(args)==9:
            init__create(*args[1:])

    ## In Spanish is said "Está vigente"
    def is_in_force(self):
        if self.is_removed()==False and self.is_executed()==False:
            return True
        return False

    def is_removed(self):
        if self.removed!=None:
            return True
        return False
        
    def is_executed(self):
        if self.executed!=None:
            return True
        return False

    def save(self, autocommit=False):
        cur=self.mem.con.cursor()
        if self.id==None:#insertar
            cur.execute("insert into opportunities(date, removed, executed, entry, target, stoploss, short, products_id) values (%s, %s, %s, %s, %s, %s, %s, %s) returning id", 
            (self.date,  self.removed, self.executed, self.entry, self.target, self.stoploss, self.short, self.product.id))
            self.id=cur.fetchone()[0]
        else:
            cur.execute("update opportunities set date=%s, removed=%s, executed=%s, entry=%s, target=%s, stoploss=%s, products_id=%s, short=%s where id=%s", (self.date,  self.removed, self.executed, self.entry, self.target, self.stoploss, self.product.id, self.short, self.id))
        if autocommit==True:
            self.mem.con.commit()
        cur.close()
        
    def relation_gains_risk(self):
        return relation_gains_risk(self.target, self.entry, self.stoploss)
        
    def remove(self):
        cur=self.mem.con.cursor()
        cur.execute("delete from opportunities where id=%s", (self.id, ))
        cur.close()
        
    ##Calculates percentage from current price to order entry
    def percentage_from_current_price(self):
        return Percentage(self.entry-self.product.result.basic.last.quote, self.product.result.basic.last.quote)
        
    ## @param dInvested Decimal with the invested amount in product currency
    ## @return Money with the gains in opportunity product currrency
    def m_target_gains(self, dInvested):
        try:
            shares=dInvested/self.entry
            value= (self.target-self.entry)*shares
            value=-value if self.short==True else value
        except:
            value= Decimal(0)
        return Money(self.mem, value, self.product.currency)

    ## @param dInvested Decimal with the invested amount in product currency
    ## @return Money with the gains in opportunity product currrency
    def m_stop_loss_losses(self, dInvested):
        try:
            shares=dInvested/self.entry
            value= (self.stoploss-self.entry)*shares
            value=-value if self.short==True else value
        except:
            value= Decimal(0)
        return Money(self.mem, value, self.product.currency)

## Manage Opportunities
class OpportunityManager(ObjectManager_With_IdDate, QObject):
    def __init__(self, mem):
        QObject.__init__(self)
        ObjectManager_With_IdDate.__init__(self)
        self.mem=mem

    def init__from_db(self, sql):
        cur=self.mem.con.cursor()
        cur.execute(sql)
        for row in cur:
            self.append(Opportunity(self.mem, row))
        cur.close()
        return self

    ## Removes from array and from database. It doesn't make a database commit
    def remove(self, order):
        """Remove from array"""
        ObjectManager_With_IdDate.remove(self, order)#Remove from array
        order.remove()#Database

    def order_by_removed(self):
        self.arr=sorted(self.arr, key=lambda o:o.removed)

    def order_by_executed(self):
        self.arr=sorted(self.arr, key=lambda o:o.executed)

    def order_by_percentage_from_current_price(self):
        try:
            self.arr=sorted(self.arr, key=lambda o:o.percentage_from_current_price(), reverse=True)
        except:            
            qmessagebox(self.tr("I couldn't order data due to they have null values"))

    ## Returns a datetime.date object with the date of the first opportunity in the database
    def date_of_the_first_database_oppportunity(self):
        cur=self.mem.con.cursor()
        cur.execute("select date from orders order by date limit 1")
        r=cur.fetchone()
        cur.close()
        if r==None:#To avoid crashed returns today if null
            return datetime.date.today()
        else:
            return r[0]

    ## @param table
    ## @invested Decimal with the amount to invest in product currency
    def mqtw(self, wdg, dInvested):
        hh=[self.tr("Date"), self.tr("Removed"), self.tr("Product"), self.tr("Current price"), self.tr("Entry"), 
        self.tr("Target"), self.tr("Stop loss"), self.tr("Gains/Risk"), self.tr("% from current"), self.tr("Executed"), 
        self.tr("Target gains"), self.tr("Stop loss losses")]
        data=[]
        for i, o in enumerate(self.arr):
            percentage_from_current_price=o.percentage_from_current_price() if o.is_in_force() else None
            executed=o.executed if o.is_executed() else None
            data.append([
                o.date, 
                o.removed, 
                o.product.name, 
                o.product.result.basic.last.money(), 
                o.product.money(o.entry), 
                o.product.money(o.target), 
                o.product.money(o.stoploss), 
                o.relation_gains_risk(), 
                percentage_from_current_price, 
                executed, 
                o.m_target_gains(dInvested), 
                o.m_stop_loss_losses(dInvested), 
                o, 
            ])
        wdg.setDataWithObjects(hh, None, data, additional=self.mqtw_additional)

    def mqtw_additional(self, wdg):
        for i, o in enumerate(wdg.objects()):
            #Color
            wdg.table.item(i, 0).setIcon(eInvestmentTypePosition.qicon_boolean(o.short))
            if o.is_executed():
                for column in range (wdg.table.columnCount()):
                    wdg.table.item(i, column).setBackground(eQColor.Green)                     
            elif o.is_removed():
                for column in range (wdg.table.columnCount()):
                    wdg.table.item(i, column).setBackground(eQColor.Red)     
                    
            if o.is_executed()==False and o.is_removed()==False:#Color if current oportunity
                if o.percentage_from_current_price().value_100()>Decimal(0):
                    wdg.table.item(i, 3).setBackground(eQColor.Green)
