import datetime
from decimal import Decimal
from xulpymoney.libxulpymoney import Percentage, qmessagebox, qdate, qleft, qempty, qright,  Money
from xulpymoney.libxulpymoneyfunctions import relation_gains_risk
from xulpymoney.libmanagers import ObjectManager_With_IdDate
from xulpymoney.libxulpymoneytypes import eQColor, eInvestmentTypePosition
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QTableWidgetItem

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
            init__create(None, None, None, Decimal('0'), Decimal('0'), Decimal('0'), None, None)
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
    def myqtablewidget(self, table, dInvested):
        table.setColumnCount(12)
        table.setHorizontalHeaderItem(0, QTableWidgetItem(self.tr("Date")))
        table.setHorizontalHeaderItem(1, QTableWidgetItem(self.tr("Removed")))
        table.setHorizontalHeaderItem(2, QTableWidgetItem(self.tr("Product")))
        table.setHorizontalHeaderItem(3, QTableWidgetItem(self.tr("Current price")))
        table.setHorizontalHeaderItem(4, QTableWidgetItem(self.tr("Entry")))
        table.setHorizontalHeaderItem(5, QTableWidgetItem(self.tr("Target")))
        table.setHorizontalHeaderItem(6, QTableWidgetItem(self.tr("Stop loss")))
        table.setHorizontalHeaderItem(7, QTableWidgetItem(self.tr("Gains/Risk")))
        table.setHorizontalHeaderItem(8, QTableWidgetItem(self.tr("% from current")))
        table.setHorizontalHeaderItem(9, QTableWidgetItem(self.tr("Executed")))
        table.setHorizontalHeaderItem(10, QTableWidgetItem(self.tr("Target gains")))
        table.setHorizontalHeaderItem(11, QTableWidgetItem(self.tr("Stop loss losses")))
        table.applySettings()
        table.clearContents()
        table.setRowCount(self.length())
        for i, p in enumerate(self.arr):
            table.setItem(i, 0, qdate(p.date))
            table.item(i, 0).setIcon(eInvestmentTypePosition.qicon_boolean(p.short))
            table.setItem(i, 1, qdate(p.removed))      
            table.setItem(i, 2, qleft(p.product.name))
            table.setItem(i, 3, p.product.result.basic.last.money().qtablewidgetitem())
            table.setItem(i, 4, p.product.currency.qtablewidgetitem(p.entry))
            table.setItem(i, 5, p.product.currency.qtablewidgetitem(p.target))
            table.setItem(i, 6, p.product.currency.qtablewidgetitem(p.stoploss))
            table.setItem(i, 7, qright(p.relation_gains_risk()))
            if p.is_in_force():
                table.setItem(i, 8, p.percentage_from_current_price().qtablewidgetitem())
            else:
                table.setItem(i, 8, qempty())
            if p.is_executed():
                table.setItem(i, 9, qdate(p.executed))
            else:
                table.setItem(i, 9, qempty())
                
            table.setItem(i, 10, p.m_target_gains(dInvested).qtablewidgetitem())
            table.setItem(i, 11, p.m_stop_loss_losses(dInvested).qtablewidgetitem())
                
            #Color
            if p.is_executed():
                for column in range (table.columnCount()):
                    table.item(i, column).setBackground(eQColor.Green)                     
            elif p.is_removed():
                for column in range (table.columnCount()):
                    table.item(i, column).setBackground(eQColor.Red)     
                    
            if p.is_executed()==False and p.is_removed()==False:#Color if current oportunity
                if p.percentage_from_current_price().value_100()>Decimal(0):
                    table.item(i, 3).setBackground(eQColor.Green)

