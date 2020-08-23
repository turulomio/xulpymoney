from PyQt5.QtCore import QObject
from decimal import Decimal
from xulpymoney.libmanagers import ObjectManager_With_IdName_Selectable
from xulpymoney.ui.myqwidgets import qmessagebox



class CreditCard(QObject):
    def __init__(self, mem):
        QObject.__init__(self)
        self.mem=mem
        self.id=None
        self.name=None
        self.account=None
        self.deferred=None
        self.maximumbalance=None
        self.active=None
        self.number=None
           
    def init__create(self, name, cuenta, deferred, maximumbalance, activa, number, id=None):
        """El parámetro cuenta es un objeto cuenta, si no se tuviera en tiempo de creación se asigna None"""
        self.id=id
        self.name=name
        self.account=cuenta
        self.deferred=deferred
        self.maximumbalance=maximumbalance
        self.active=activa
        self.number=number
        return self
        
    def init__db_row(self, row, cuenta):
        """El parámetro cuenta es un objeto cuenta, si no se tuviera en tiempo de creación se asigna None"""
        self.init__create(row['name'], cuenta, row['deferred'], row['maximumbalance'], row['active'], row['number'], row['id'])
        return self
                    
    def __repr__(self):
        return "CreditCard: {}".format(self.id)

    def delete(self):
        self.mem.con.execute("delete from creditcards where id=%s", (self.id, ))
        
    ## Devuelve False si no puede borrarse por haber dependientes.
    def is_deletable(self):
        res=self.mem.con.cursor_one_field("select count(*) from creditcardsoperations where creditcards_id=%s", (self.id, ))
        if res==0:
            return True
        else:
            return False
        
    def qmessagebox_inactive(self):
        if self.active==False:
            qmessagebox(self.tr("The associated credit card is not active. You must activate it first"))
            return True
        return False
        
    def save(self):
        if self.id==None:
            self.id=self.mem.con.cursor_one_field("insert into creditcards (name,accounts_id,deferred,maximumbalance,active,number) values (%s, %s, %s,%s,%s,%s) returning id", (self.name, self.account.id,  self.deferred ,  self.maximumbalance, self.active, self.number))
        else:
            self.mem.con.execute("update creditcards set name=%s, accounts_id=%s, deferred=%s, maximumbalance=%s, active=%s, number=%s where id=%s", (self.name, self.account.id,  self.deferred ,  self.maximumbalance, self.active, self.number, self.id))

    def saldo_pendiente(self):
        """Es el balance solo de operaciones difreidas sin pagar"""
        cur=self.mem.con.cursor()
        cur.execute("select sum(amount) from creditcardsoperations where creditcards_id=%s and paid=false;", [self.id])
        result=cur.fetchone()[0]
        cur.close()
        if result==None:
            result=Decimal(0)
        return result

class CreditCardManager(QObject, ObjectManager_With_IdName_Selectable):
    def __init__(self, mem):
        QObject.__init__(self)
        ObjectManager_With_IdName_Selectable.__init__(self)
        self.mem=mem   
            
    def CreditCardManager_active(self):        
        r=CreditCardManager(self.mem, self.accounts)
        for b in self.arr:
            if b.active==True:
                r.append(b)
        return r       

    def CreditCardManager_inactive(self):        
        r=CreditCardManager(self.mem, self.accounts)
        for b in self.arr:
            if b.active==False:
                r.append(b)
        return r        

    def load_from_db(self, sql):
        cur=self.mem.con.cursor()
        cur.execute(sql)#"Select * from creditcards")
        for row in cur:
            t=CreditCard(self.mem).init__db_row(row, self.mem.data.accounts.find_by_id(row['accounts_id']))
            self.append(t)
        cur.close()
        
    ## @param table myQTableWidget
    ## @param active Boolean to show active or inactive rows
    def myqtablewidget(self, wdg, active):
        data=[]
        for i, o in enumerate(self.arr):
            data.append([
                o.name, 
                o.number, 
                o.active, 
                o.deferred, 
                o.maximumbalance, 
                o.saldo_pendiente(), 
                o, 
            ])
        wdg.auxiliar=active## Adds this auxiliar value to allow additional filter active / no active
        wdg.setDataWithObjects(
            [self.tr("Credit card"), self.tr("Number"), self.tr("Active"), self.tr("Delayed payment"), self.tr("Maximum balance"), self.tr("Balance")], 
            None, 
            data, 
            decimals=2, 
            zonename=self.mem.localzone_name, 
            additional=self.myqtablewidget_additional
        )

    def myqtablewidget_additional(self, wdg):
        for i, t in enumerate(wdg.objects()):            
            if t.active!=wdg.auxiliar: #Hides active or inactive when necesary
                wdg.table.hideRow(i)
            else:
                wdg.table.showRow(i)

    def qcombobox(self, combo,  selected=None):
        """Load set items in a comobo using id and name
        Selected is and object
        It sorts by name the arr""" 
        self.order_by_name()
        combo.clear()
        for a in self.arr:
            combo.addItem("{} ({})".format(a.name, a.number), a.id)

        if selected!=None:
            combo.setCurrentIndex(combo.findData(selected.id))
