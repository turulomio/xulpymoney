from PyQt5.QtCore import QObject
from PyQt5.QtGui import QIcon
from xulpymoney.libmanagers import ObjectManager_With_IdName_Selectable
from xulpymoney.ui.myqwidgets import qmessagebox
from xulpymoney.objects.money import Money

class Bank(QObject):
    """Clase que encapsula todas las funciones que se pueden realizar con una Entidad bancaria o banco"""
    def __init__(self, mem):
        """Constructor que inicializa los atributos a None"""
        QObject.__init__(self)
        self.mem=mem
        self.id=None
        self.name=None
        self.active=None
        
    def init__create(self, name,  activa=True, id=None):
        self.id=id
        self.active=activa
        self.name=name
        return self
        
    def __repr__(self):
        return ("Bank: {0} ({1})".format( self.name, self.id))

    def qicon(self):
        return QIcon(":/xulpymoney/bank.png")

    def init__db_row(self, row):
        self.id=row['id_entidadesbancarias']
        self.name=self.tr(row['entidadbancaria'])
        self.active=row['active']
        return self
        
    def qmessagebox_inactive(self):
        if self.active==False:
            qmessagebox(self.tr("The associated bank is not active. You must activate it first"))
            return True
        return False
    def save(self):
        """Función que inserta si self.id es nulo y actualiza si no es nulo"""
        cur=self.mem.con.cursor()
        if self.id==None:
            cur.execute("insert into entidadesbancarias (entidadbancaria, active) values (%s,%s) returning id_entidadesbancarias", (self.name, self.active))
            self.id=cur.fetchone()[0]
        else:
            cur.execute("update entidadesbancarias set entidadbancaria=%s, active=%s where id_entidadesbancarias=%s", (self.name, self.active, self.id))
        cur.close()
        
    def balance(self):
        resultado=Money(self, 0, self.mem.localcurrency)
        #Recorre balance cuentas
        for c in self.mem.data.accounts_active().arr:
            if c.bank.id==self.id:
                resultado=resultado+c.balance().local()
        
        #Recorre balance inversiones
        for i in self.mem.data.investments_active().arr:
            if i.account.bank.id==self.id:
                resultado=resultado+i.balance().local()
        return resultado
        
    def is_deletable(self):
        """Función que devuelve un booleano si una cuenta es borrable, es decir, que no tenga registros dependientes."""
        #Recorre balance cuentas
        for c  in self.mem.data.accounts.arr:
            if c.bank.id==self.id:
                if c.is_deletable()==self.id:
                    return False
        return True
        
    def delete(self):
        """Función que borra. You must use is_deletable before"""
        cur=self.mem.con.cursor()
        cur.execute("delete from entidadesbancarias where id_entidadesbancarias=%s", (self.id, ))  
        cur.close()
        
class BankManager(ObjectManager_With_IdName_Selectable, QObject):
    def __init__(self, mem):
        ObjectManager_With_IdName_Selectable.__init__(self)
        QObject.__init__(self )
        self.mem=mem   

    def load_from_db(self, sql):
        cur=self.mem.con.cursor()
        cur.execute(sql)#"select * from entidadesbancarias"
        for row in cur:
            self.append(Bank(self.mem).init__db_row(row))
        cur.close()            
        
    def delete(self, bank):
        """Deletes from db and removes object from array.
        bank is an object"""
        bank.delete()
        self.remove(bank)
        
    def balance(self):
        r=Money(self, 0, self.mem.localcurrency)
        for o in self.arr:
            r=r+o.balance()
        return r

    def mqtw(self, wdg):
        data=[]
        for i, o in enumerate(self.arr):
            data.append([
                o.name, 
                o.active, 
                o.balance(), 
                o#Data with objects
            ])
        wdg.setDataWithObjects(
            [self.tr("Bank"), self.tr("Active"), self.tr("Balance")],
            None, 
            data,
            additional=self.mqtw_additional
        )   
        
    def mqtw_additional(self, wdg):
        wdg.table.setRowCount(self.length()+1)
        wdg.addRow(self.length(), [self.tr("Total"), "#crossedout", self.balance()])
        for row, o in enumerate(wdg.objects()):
            wdg.table.item(row, 0).setIcon(o.qicon())
