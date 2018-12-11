import datetime
from decimal import Decimal
from xulpymoney.libxulpymoney import Percentage, qmessagebox, qdate, qleft, qempty
from xulpymoney.libmanagers import ObjectManager_With_IdDate
from xulpymoney.libxulpymoneytypes import eQColor
from PyQt5.QtWidgets import QTableWidgetItem,   QApplication

## Class that register a purchase opportunity
class Opportunity:
    ## Constructor with the following attributes combination
    ## 1. Opportunity(mem). Crete a Opportunity object with all attributes set to None
    ## 1. Opportunity(mem, row). Create an Opportunity from a db row, generated in a database query
    ## 2. Opportunity(mem, date, removed, executed, entry, products_id, id). Create a Opportunity passing all attributes
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
            init__create(row['date'], row['removed'], row['executed'], row['entry'], row['products_id'], row['id'])
        def init__create(date, removed, executed, entry, products_id, id):
            self.date=date
            self.removed=removed
            self.executed=executed
            self.entry=entry
            if products_id!=None:
                self.product=self.mem.data.products.find_by_id(products_id)
                self.product.needStatus(1)
            else:
                self.product=None
            self.id=id
        self.mem=args[0]
        if len(args)==1:
            init__create(None, None, None, None, None, None)
        if len(args)==2:
            init__db_row(args[1])
        if len(args)==7:
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
            cur.execute("insert into opportunities(date, removed, executed, entry, products_id) values (%s, %s, %s, %s, %s) returning id", 
            (self.date,  self.removed, self.executed, self.entry, self.product.id))
            self.id=cur.fetchone()[0]
        else:
            cur.execute("update opportunities set date=%s, removed=%s, executed=%s, entry=%s, products_id=%s where id=%s", (self.date,  self.removed, self.executed, self.entry, self.product.id, self.id))
        if autocommit==True:
            self.mem.con.commit()
        cur.close()
        
    def remove(self):
        cur=self.mem.con.cursor()
        cur.execute("delete from opportunities where id=%s", (self.id, ))
        cur.close()
        
    ##Calculates percentage from current price to order entry
    def percentage_from_current_price(self):
        return Percentage(self.entry-self.product.result.basic.last.quote, self.product.result.basic.last.quote)


## Manage Opportunities
class OpportunityManager(ObjectManager_With_IdDate):
    def __init__(self, mem):
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
            qmessagebox(QApplication.translate("Core", "I couldn't order data due to they have null values"))

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

    def myqtablewidget(self, table):
        table.setColumnCount(7)
        table.setHorizontalHeaderItem(0, QTableWidgetItem(QApplication.translate("Core","Date")))
        table.setHorizontalHeaderItem(1, QTableWidgetItem(QApplication.translate("Core","Removed")))
        table.setHorizontalHeaderItem(2, QTableWidgetItem(QApplication.translate("Core","Product")))
        table.setHorizontalHeaderItem(3, QTableWidgetItem(QApplication.translate("Core","Current price")))
        table.setHorizontalHeaderItem(4, QTableWidgetItem(QApplication.translate("Core","Opportunity entry")))
        table.setHorizontalHeaderItem(5, QTableWidgetItem(QApplication.translate("Core","% from current")))
        table.setHorizontalHeaderItem(6, QTableWidgetItem(QApplication.translate("Core","Executed")))
        table.applySettings()
        table.clearContents()
        table.setRowCount(self.length())
        for i, p in enumerate(self.arr):
            table.setItem(i, 0, qdate(p.date))
            table.setItem(i, 1, qdate(p.removed))      
            table.setItem(i, 2, qleft(p.product.name))
            table.setItem(i, 3, p.product.result.basic.last.money().qtablewidgetitem())
            table.setItem(i, 4, p.product.currency.qtablewidgetitem(p.entry))
            if p.is_in_force():
                table.setItem(i, 5, p.percentage_from_current_price().qtablewidgetitem())
            else:
                table.setItem(i, 5, qempty())
            if p.is_executed():
                table.setItem(i, 6, qdate(p.executed))
            else:
                table.setItem(i, 6, qempty())
                
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

