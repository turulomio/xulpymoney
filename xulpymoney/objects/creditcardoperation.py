from PyQt5.QtCore import QObject
from decimal import Decimal
from xulpymoney.libmanagers import ObjectManager_With_IdDatetime_Selectable
from xulpymoney.objects.accountoperation import AccountOperation
from xulpymoney.objects.comment import Comment

class CreditCardOperation:
    def __init__(self, mem):
        """CreditCard es un objeto CreditCardOperation. paid, paid_datetime y opercuenta solo se rellena cuando se paga"""
        self.mem=mem
        self.id=None
        self.datetime=None
        self.concept=None
        self.tipooperacion=None
        self.amount=None
        self.comment=None
        self.tarjeta=None
        self.paid=None
        self.paid_datetime=None
        self.opercuenta=None
        
    def __repr__(self):
        return "CreditCardOperation: {}".format(self.id)

    def init__create(self, dt,  concept, tipooperacion, amount, comment, tarjeta, paid=None, paid_datetime=None, opercuenta=None, id_creditcardsoperations=None):
        """paid, paid_datetime y opercuenta solo se rellena cuando se paga"""
        self.id=id_creditcardsoperations
        self.datetime=dt
        self.concept=concept
        self.tipooperacion=tipooperacion
        self.amount=amount
        self.comment=comment
        self.tarjeta=tarjeta
        self.paid=paid
        self.paid_datetime=paid_datetime
        self.opercuenta=opercuenta
        return self
            
            
    def init__db_query(self, id):
        """Creates a CreditCardOperation querying database for an id_creditcardsoperations"""
        if id==None:
            return None
        cur=self.mem.con.cursor()
        cur.execute("select * from creditcardsoperations where id=%s", (id, ))
        for row in cur:
            concept=self.mem.concepts.find_by_id(row['concepts_id'])
            self.init__db_row(row, concept, concept.tipooperacion, self.mem.data.accounts.find_creditcard_by_id(row['creditcards_id']))
        cur.close()
        return self

    def init__db_row(self, row, concept, tipooperacion, tarjeta, opercuenta=None):
        return self.init__create(row['datetime'],  concept, tipooperacion, row['amount'], row['comment'], tarjeta, row['paid'], row['paid_datetime'], opercuenta, row['id'])
        
    def borrar(self):
        cur=self.mem.con.cursor()
        sql="delete from creditcardsoperations where id="+ str(self.id)
        cur.execute(sql)
        cur.close()
        
    def save(self):
        cur=self.mem.con.cursor()
        if self.id==None:#insertar
            sql="insert into creditcardsoperations (datetime, concepts_id, operationstypes_id, amount, comment, creditcards_id, paid) values ('" + str(self.datetime) + "'," + str(self.concept.id)+","+ str(self.tipooperacion.id) +","+str(self.amount)+", '"+self.comment+"', "+str(self.tarjeta.id)+", "+str(self.paid)+") returning id"
            cur.execute(sql);
            self.id=cur.fetchone()[0]
        else:
            if self.tarjeta.deferred==True and self.paid==False:#No hay opercuenta porque es en diferido y no se ha paid
                cur.execute("update creditcardsoperations set datetime=%s, concepts_id=%s, operationstypes_id=%s, amount=%s, comment=%s, creditcards_id=%s, paid=%s, paid_datetime=%s, accountsoperations_id=%s where id=%s", (self.datetime, self.concept.id, self.tipooperacion.id,  self.amount,  self.comment, self.tarjeta.id, self.paid, self.paid_datetime, None, self.id))
            else:
                cur.execute("update creditcardsoperations set datetime=%s, concepts_id=%s, operationstypes_id=%s, amount=%s, comment=%s, creditcards_id=%s, paid=%s, paid_datetime=%s, accountsoperations_id=%s where id=%s", (self.datetime, self.concept.id, self.tipooperacion.id,  self.amount,  self.comment, self.tarjeta.id, self.paid, self.paid_datetime, self.opercuenta.id, self.id))
        cur.close()


class CreditCardOperationManager(ObjectManager_With_IdDatetime_Selectable, QObject):
    def __init__(self, mem):
        ObjectManager_With_IdDatetime_Selectable.__init__(self)
        QObject.__init__(self)
        self.setConstructorParameters(mem)
        self.mem=mem

    def balance(self):
        """Returns the balance of all credit card operations"""
        result=Decimal(0)
        for o in self.arr:
            result=result+o.amount
        return result
        
    def load_from_db(self, sql):
        del self.arr
        self.arr=[]
        cur=self.mem.con.cursor()
        cur.execute(sql)#"Select * from accountsoperations"
        for row in cur:        
            co=CreditCardOperation(self.mem).init__db_row(row, self.mem.concepts.find_by_id(row['concepts_id']), self.mem.tiposoperaciones.find_by_id(row['operationstypes_id']), self.mem.data.accounts.find_creditcard_by_id(row['creditcards_id']), AccountOperation(self.mem,  row['accountsoperations_id']))
            self.append(co)
        cur.close()
        
    def myqtablewidget(self, wdg):
        hh=[self.tr("Date" ), self.tr("Concept" ), self.tr("Amount" ), self.tr("Balance" ), self.tr("Comment" )]
        data=[]
        balance=0
        for rownumber, o in enumerate(self.arr):
            balance=balance+o.amount
            data.append([
                o.datetime, 
                o.concept.name, 
                o.tarjeta.account.money(o.amount), 
                o.tarjeta.account.money(balance), 
                Comment(self.mem).decode(o.comment), 
                o, 
            ])
            wdg.setDataWithObjects(hh, None, data, zonename=self.mem.localzone_name)
