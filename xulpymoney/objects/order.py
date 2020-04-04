from PyQt5.QtCore import QObject
from PyQt5.QtGui import QIcon
from datetime import date
from xulpymoney.libmanagers import ObjectManager_With_Id_Selectable
from xulpymoney.ui.myqwidgets import qmessagebox
from xulpymoney.libxulpymoneytypes import eQColor
from xulpymoney.objects.money import Money
from xulpymoney.objects.percentage import Percentage
class Order(QObject):
    def __init__(self, mem):
        QObject.__init__(self)
        self.mem=mem
        self.id=None
        self.date=None
        self.expiration=None
        self.price=None
        self.shares=None
        self.investment=None
        self.executed=None
        
    def init__db_row(self, row):
        self.id=row['id']
        self.date=row['date']
        self.expiration=row['expiration']
        self.price=row['price']
        self.shares=row['shares']
        self.investment=self.mem.data.investments.find_by_id(row['investments_id'])
        self.executed=row['executed']
        return self
        
    def qicon(self):
        return QIcon(":/xulpymoney/order.png")

    def is_in_force(self):
        "Está vigente"
        if self.is_expired()==False and self.is_executed()==False:
            return True
        return False

    def is_expired(self):
        if self.expiration<date.today():
            return True
        return False
        
    def is_executed(self):
        if self.executed!=None:
            return True
        return False
        
    def amount(self):
        return Money(self.mem, self.shares*self.price, self.investment.product.currency)

    def save(self, autocommit=False):
        cur=self.mem.con.cursor()
        if self.id==None:#insertar
            cur.execute("insert into orders(date, expiration, shares, price,investments_id, executed) values (%s, %s, %s, %s, %s, %s) returning id", (self.date,  self.expiration, self.shares, self.price, self.investment.id, self.executed))
            self.id=cur.fetchone()[0]
        else:
            cur.execute("update orders set date=%s, expiration=%s, shares=%s, price=%s, investments_id=%s, executed=%s where id=%s", (self.date,  self.expiration, self.shares, self.price, self.investment.id, self.executed, self.id))
        if autocommit==True:
            self.mem.con.commit()
        cur.close()
        
    def remove(self):
        cur=self.mem.con.cursor()
        cur.execute("delete from orders where id=%s", (self.id, ))
        cur.close()

    def qmessagebox_reminder(self):
        if self.shares<0:
            type="Sell"
        else:
            type="Buy"
        qmessagebox(self.tr("Don't forget to tell your bank to add and order for:\n{} ({})\n{} {} shares to {}".format(self.investment.name, self.investment.account.name, type, abs(self.shares), self.investment.money(self.price).string(6))))
        
    def percentage_from_current_price(self):
        """Calculates percentage from current price to order price"""
        return Percentage(self.price-self.investment.product.result.basic.last.quote, self.investment.product.result.basic.last.quote)
        
class OrderManager(ObjectManager_With_Id_Selectable, QObject):
    def __init__(self, mem):
        ObjectManager_With_Id_Selectable.__init__(self)
        QObject.__init__(self)
        self.mem=mem
        
    def init__from_db(self, sql):
        cur=self.mem.con.cursor()
        cur.execute(sql)
        for row in cur:
            self.append(Order(self.mem).init__db_row(row))
        cur.close()
        return self
                
    def remove(self, order):
        """Remove from array"""
        self.arr.remove(order)#Remove from array
        order.remove()#Database

    def order_by_date(self):
        self.arr=sorted(self.arr, key=lambda o:o.date)
    def order_by_expiration(self):
        self.arr=sorted(self.arr, key=lambda o:o.expiration)
    def order_by_execution(self):
        self.arr=sorted(self.arr, key=lambda o:o.executed)

    ## Returns the number of order of the investment parameter
    ## This function is used, for example, to determinate if an investment can be delete
    ## @param investment Investment Object
    ## @return int Number of orders of an investment
    def number_of_investment_orders(self, investment):
        return self.mem.con.cursor_one_field("select count(*) from orders where investments_id=%s", (investment.id, ))
        
    def order_by_percentage_from_current_price(self):
        try:
            self.arr=sorted(self.arr, key=lambda o:o.percentage_from_current_price(), reverse=True)
        except:            
            qmessagebox(self.tr("I couldn't order data due to they have null values"))

    ## Returns a string with investments separated with \n for range indexes
    def string_with_names(self):
            resultado=""
            for o in self.arr:
                    resultado=resultado+ self.tr("{}. Amount: {}\n").format(o.investment.fullName(), o.amount())
            return resultado[:-1]

    ## Sum of all order amounts in manager. It's showed in user currency
    def amount(self):
        r=Money(self.mem, 0, self.mem.localcurrency)
        for o in self.arr:
            r=r+abs(o.amount()) #abs due to can be negative amounts.
        return r
        
    def date_first_db_order(self):
        """First order date. It searches in database not in array"""
        cur=self.mem.con.cursor()
        cur.execute("select date from orders order by date limit 1")
        r=cur.fetchone()
        cur.close()
        if r==None:#To avoid crashed returns today if null
            return date.today()
        else:
            return r[0]

    def mqtw(self, wdg):
        data=[]
        for i, o in enumerate(self.arr):
            data.append([
                o.date, 
                o.expiration, 
                o.investment.fullName(), 
                o.shares, 
                o.investment.money(o.price), 
                o.amount(), 
                o.percentage_from_current_price(), 
                o.executed, 
                o#Data with objects
            ])
        wdg.setDataWithObjects(
            [self.tr("Date"), self.tr("Expiration"), self.tr("Investment"), self.tr("Shares"), self.tr("Price"), self.tr("Amount"), self.tr("% from current"), self.tr("Executed")
            ], 
            None, 
            data,
            zonename=self.mem.localzone_name, 
            additional=self.mqtw_additional
        )   
        
    def mqtw_additional(self, wdg):
        for i, o in enumerate(self.arr):
            wdg.table.item(i, 2).setIcon(o.qicon())
            if o.is_executed():
                for column in range (wdg.table.columnCount()):
                    wdg.table.item(i, column).setBackground(eQColor.Green)                     
            elif o.is_expired():
                for column in range (wdg.table.columnCount()):
                    wdg.table.item(i, column).setBackground(eQColor.Red)     
