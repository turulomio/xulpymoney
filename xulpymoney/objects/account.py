from PyQt5.QtCore import QObject
from PyQt5.QtGui import QIcon
from datetime import date
from logging import critical
from xulpymoney.datetime_functions import  dtaware_day_end_from_date
from xulpymoney.libmanagers import ObjectManager_With_IdName_Selectable
from xulpymoney.ui.myqwidgets import qmessagebox
from xulpymoney.libxulpymoneytypes import eComment, eConcept, eMoneyCurrency, eOperationType
from xulpymoney.objects.accountoperation import AccountOperation
from xulpymoney.objects.comment import Comment
from xulpymoney.objects.creditcard import CreditCardManager
from xulpymoney.objects.money import Money

## Class to manage everything relationed with bank accounts
class Account(QObject):
    ## @param mem MemXulpymoney object
    ## @param row Dictionary of a database query cursor
    ## @param bank Bank object
    ## @param name Account name
    ## @param active Boolean that sets if the Account is active
    ## @param numero String with the account number
    ## @param currency Currency object that sets the currency of the Account
    ## @param id Integer that sets the id of an account. If id=None it's not in the database. id is set in the save method
    def __init__(self, mem=None,name=None,  bank=None, active=None, number=None, currency=None, id=None):
        QObject.__init__(self)
        self.mem=mem
        self.name=name
        self.bank=bank
        self.active=active
        self.number=number
        self.currency=currency
        self.id=id
        self.status=0

        
    def __repr__(self):
        return ("Account '{0}' ({1})".format( self.name, self.id))

    def balance(self,fecha=None, type=eMoneyCurrency.User):
        """Función que calcula el balance de una cuenta
        Solo asigna balance al atributo balance si la fecha es actual, es decir la actual
        Parámetros:
            - pg_cursor cur Cursor de base de datos
            - date fecha Fecha en la que calcular el balance
        Devuelve:
            - Decimal balance Valor del balance
        type=2, account currency
        type=3 localcurrency
        """
        cur=self.mem.con.cursor()
        if fecha==None:
            fecha=date.today()
        cur.execute('select sum(importe) from opercuentas where id_cuentas='+ str(self.id) +" and datetime::date<='"+str(fecha)+"';") 
        res=cur.fetchone()[0]
        cur.close()
        if res==None:
            return Money(self.mem, 0, self.resultsCurrency(type))
        if type==eMoneyCurrency.Account:
            return Money(self.mem, res, self.currency)
        elif type==eMoneyCurrency.User:
            if fecha==None:
                dt=self.mem.localzone.now()
            else:
                dt=dtaware_day_end_from_date(fecha, self.mem.localzone_name)
            return Money(self.mem, res, self.currency).convert(self.mem.localcurrency, dt)

    def save(self):
        if self.id==None:
            self.id=self.mem.con.cursor_one_field("insert into cuentas (id_entidadesbancarias, cuenta, numerocuenta, active,currency) values (%s,%s,%s,%s,%s) returning id_cuentas", (self.bank.id, self.name, self.number, self.active, self.currency))
        else:
            self.mem.con.execute("update cuentas set cuenta=%s, id_entidadesbancarias=%s, numerocuenta=%s, active=%s, currency=%s where id_cuentas=%s", (self.name, self.bank.id, self.number, self.active, self.currency, self.id))

    def is_deletable(self):
        """Función que devuelve un booleano si una cuenta es borrable, es decir, que no tenga registros dependientes."""
        if self.id==4:#Cash
            return False
        cur=self.mem.con.cursor()
        cur.execute("select count(*) from tarjetas where id_cuentas=%s", (self.id, ))
        if cur.fetchone()[0]!=0:
            cur.close()
            return False
        cur.execute("select count(*) from inversiones where id_cuentas=%s", (self.id, ))
        if cur.fetchone()[0]!=0:
            cur.close()
            return False
        cur.execute("select count(*) from opercuentas where id_cuentas=%s", (self.id, ))
        if cur.fetchone()[0]!=0:
            cur.close()
            return False
        cur.close()
        return True
        
    def borrar(self):
        if self.is_deletable()==True:
            self.mem.con.execute("delete from cuentas where id_cuentas=%s", (self.id, ))

    def transferencia(self, datetime, cuentaorigen, cuentadestino, importe, comision):
        """Si el oc_comision_id es 0 es que no hay comision porque también es 0"""
        #Ojo los comentarios están dependientes.
        oc_comision=None
        notfinished="Tranfer not fully finished"
        if comision>0:
            oc_comision=AccountOperation(self.mem, datetime, self.mem.conceptos.find_by_id(eConcept.BankCommissions), self.mem.tiposoperaciones.find_by_id(eOperationType.Expense), -comision, notfinished, cuentaorigen, None)
            oc_comision.save()
        oc_origen=AccountOperation(self.mem, datetime, self.mem.conceptos.find_by_id(eConcept.TransferOrigin), self.mem.tiposoperaciones.find_by_id(eOperationType.Transfer), -importe, notfinished, cuentaorigen, None)
        oc_origen.save()
        oc_destino=AccountOperation(self.mem, datetime, self.mem.conceptos.find_by_id(eConcept.TransferDestiny), self.mem.tiposoperaciones.find_by_id(eOperationType.Transfer), importe, notfinished, cuentadestino, None)
        oc_destino.save()
        
        oc_origen.comentario=Comment(self.mem).encode(eComment.AccountTransferOrigin, oc_origen, oc_destino, oc_comision)
        oc_origen.save()
        oc_destino.comentario=Comment(self.mem).encode(eComment.AccountTransferDestiny, oc_origen, oc_destino, oc_comision)
        oc_destino.save()
        if oc_comision!=None:
            oc_comision.comentario=Comment(self.mem).encode(eComment.AccountTransferOriginCommission, oc_origen, oc_destino, oc_comision)
            oc_comision.save()
            
    ## REturn a money object with the amount and account currency
    def money(self, amount):
        return Money(self.mem, amount, self.currency)

    ## ESTA FUNCION VA AUMENTANDO STATUS SIN MOLESTAR LOS ANTERIORES, SOLO CARGA CUANDO stsatus_to es mayor que self.status
    ## @param statusneeded  Integer with the status needed 
    ## @param downgrade_to Integer with the status to downgrade before checking needed status. If None it does nothing
    ##
    ## 0 Account
    ## 1 Credit Cards
    def needStatus(self, statusneeded, downgrade_to=None):
        if downgrade_to!=None:
            self.status=downgrade_to
        
        if self.status==statusneeded:
            return

        if self.status==0 and statusneeded==1: #MAIN
            self.creditcards=CreditCardManager(self.mem)
            self.creditcards.load_from_db(self.mem.con.mogrify("select * from tarjetas where id_cuentas=%s", (self.id, )))
            self.status=1

    def qicon(self):
        return QIcon(":/xulpymoney/coins.png")

    def qmessagebox_inactive(self):
        if self.active==False:
            qmessagebox(self.tr("The associated account is not active. You must activate it first"))
            return True
        return False

    def resultsCurrency(self, type ):
        if type==2:
            return self.currency
        elif type==3:
            return self.mem.localcurrency
        critical("Rare account result currency: {}".format(type))


class AccountManager(QObject, ObjectManager_With_IdName_Selectable):   
    def __init__(self, mem):
        QObject.__init__(self)
        ObjectManager_With_IdName_Selectable.__init__(self)
        self.mem=mem

    def balance(self, date=None):
        """Give the sum of all accounts balances in self.arr"""
        res=Money(self.mem, 0, self.mem.localcurrency)
        for ac in self.arr:
            res=res+ac.balance(date,  type=3)
        return res
        
    ## Used to find a credit card in accounts
    def find_creditcard_by_id(self, id):
        for o in self.arr:
            o.needStatus(1)#Loads all account credit cards
            for cc in o.creditcards.arr:
                if cc.id==id:
                    return cc
        return None
        
    ## Returns a CreditCardManager with all active credit cards 
    def CreditCardManager_active(self):
        r=CreditCardManager(self.mem)
        for o in self.arr:
            o.needStatus(1)#Loads all account credit cards
            for cc in o.creditcards.arr:
                if cc.active==True:
                    r.append(cc)
        return r

    ## @param wdg
    def mqtw(self, wdg):      
        data=[]
        for i, o in enumerate(self.arr):
            data.append([
                o.name,
                o.bank.name, 
                o.active, 
                o.number, 
                o.balance(), 
                o, 
            ])
        wdg.setDataWithObjects(
            [self.tr("Account"), self.tr("Bank"), self.tr("Active"),  self.tr("Account number"), self.tr("Balance")], 
            None, 
            data, 
            decimals=2, 
            zonename=self.mem.localzone_name, 
            additional=self.mqtw_additional
        )

    def mqtw_additional(self, wdg):
        for i, o in enumerate(wdg.objects()):
            if o.name==self.mem.trHS("Cash"):
                wdg.table.item(i, 0).setIcon(QIcon(":/xulpymoney/Money.png"))
            else:
                wdg.table.item(i, 0).setIcon(o.qicon())

    def mqtw_active(self, wdg):       
        data=[]
        for i, o in enumerate(self.arr):
            data.append([
                o.name,
                o.active, 
                o.balance(), 
                o
            ])
        wdg.setDataWithObjects(
            [self.tr("Account"), self.tr("Active"), self.tr("Balance")], 
            None, 
            data, 
            additional=self.mqtw_active_additional
        )

    def mqtw_active_additional(self, wdg):
        wdg.table.setRowCount(wdg.length()+1)
        for i, o in enumerate(wdg.objects()):
            if o.name==self.mem.trHS("Cash"):
                wdg.table.item(i, 0).setIcon(QIcon(":/xulpymoney/Money.png"))
            else:
                wdg.table.item(i, 0).setIcon(o.qicon())
        wdg.addRow(wdg.length(), [self.tr("Total"), "#crossedout", self.balance()])

def Account_from_dict(mem, row):
    r=Account(mem)
    r.id=row['id_cuentas']
    r.name=mem.trHS(row['cuenta'])
    r.bank=mem.data.banks.find_by_id(row['id_entidadesbancarias'])
    r.active=row['active']
    r.number=row['numerocuenta']
    r.currency=row['currency']
    return r

def AccountManager_from_sql(mem, sql):
    r=AccountManager(mem)
    for row in mem.con.cursor_rows(sql):
        r.append(Account_from_dict(mem, row))
    return r
