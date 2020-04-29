from PyQt5.QtCore import QObject
from decimal import Decimal
from xulpymoney.libmanagers import ObjectManager_With_IdDatetime_Selectable
from xulpymoney.objects.accountoperation import AccountOperation
from xulpymoney.objects.comment import Comment

class CreditCardOperation:
    def __init__(self, mem):
        """CreditCard es un objeto CreditCardOperation. pagado, fechapago y opercuenta solo se rellena cuando se paga"""
        self.mem=mem
        self.id=None
        self.datetime=None
        self.concepto=None
        self.tipooperacion=None
        self.importe=None
        self.comentario=None
        self.tarjeta=None
        self.pagado=None
        self.fechapago=None
        self.opercuenta=None
        
    def __repr__(self):
        return "CreditCardOperation: {}".format(self.id)

    def init__create(self, dt,  concepto, tipooperacion, importe, comentario, tarjeta, pagado=None, fechapago=None, opercuenta=None, id_opertarjetas=None):
        """pagado, fechapago y opercuenta solo se rellena cuando se paga"""
        self.id=id_opertarjetas
        self.datetime=dt
        self.concepto=concepto
        self.tipooperacion=tipooperacion
        self.importe=importe
        self.comentario=comentario
        self.tarjeta=tarjeta
        self.pagado=pagado
        self.fechapago=fechapago
        self.opercuenta=opercuenta
        return self
            
            
    def init__db_query(self, id):
        """Creates a CreditCardOperation querying database for an id_opertarjetas"""
        if id==None:
            return None
        cur=self.mem.con.cursor()
        cur.execute("select * from opertarjetas where id_opertarjetas=%s", (id, ))
        for row in cur:
            concepto=self.mem.conceptos.find_by_id(row['id_conceptos'])
            self.init__db_row(row, concepto, concepto.tipooperacion, self.mem.data.accounts.find_creditcard_by_id(row['id_tarjetas']))
        cur.close()
        return self

    def init__db_row(self, row, concepto, tipooperacion, tarjeta, opercuenta=None):
        return self.init__create(row['datetime'],  concepto, tipooperacion, row['importe'], row['comentario'], tarjeta, row['pagado'], row['fechapago'], opercuenta, row['id_opertarjetas'])
        
    def borrar(self):
        cur=self.mem.con.cursor()
        sql="delete from opertarjetas where id_opertarjetas="+ str(self.id)
        cur.execute(sql)
        cur.close()
        
    def save(self):
        cur=self.mem.con.cursor()
        if self.id==None:#insertar
            sql="insert into opertarjetas (datetime, id_conceptos, id_tiposoperaciones, importe, comentario, id_tarjetas, pagado) values ('" + str(self.datetime) + "'," + str(self.concepto.id)+","+ str(self.tipooperacion.id) +","+str(self.importe)+", '"+self.comentario+"', "+str(self.tarjeta.id)+", "+str(self.pagado)+") returning id_opertarjetas"
            cur.execute(sql);
            self.id=cur.fetchone()[0]
        else:
            if self.tarjeta.pagodiferido==True and self.pagado==False:#No hay opercuenta porque es en diferido y no se ha pagado
                cur.execute("update opertarjetas set datetime=%s, id_conceptos=%s, id_tiposoperaciones=%s, importe=%s, comentario=%s, id_tarjetas=%s, pagado=%s, fechapago=%s, id_opercuentas=%s where id_opertarjetas=%s", (self.datetime, self.concepto.id, self.tipooperacion.id,  self.importe,  self.comentario, self.tarjeta.id, self.pagado, self.fechapago, None, self.id))
            else:
                cur.execute("update opertarjetas set datetime=%s, id_conceptos=%s, id_tiposoperaciones=%s, importe=%s, comentario=%s, id_tarjetas=%s, pagado=%s, fechapago=%s, id_opercuentas=%s where id_opertarjetas=%s", (self.datetime, self.concepto.id, self.tipooperacion.id,  self.importe,  self.comentario, self.tarjeta.id, self.pagado, self.fechapago, self.opercuenta.id, self.id))
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
            result=result+o.importe
        return result
        
    def load_from_db(self, sql):
        del self.arr
        self.arr=[]
        cur=self.mem.con.cursor()
        cur.execute(sql)#"Select * from opercuentas"
        for row in cur:        
            co=CreditCardOperation(self.mem).init__db_row(row, self.mem.conceptos.find_by_id(row['id_conceptos']), self.mem.tiposoperaciones.find_by_id(row['id_tiposoperaciones']), self.mem.data.accounts.find_creditcard_by_id(row['id_tarjetas']), AccountOperation(self.mem,  row['id_opercuentas']))
            self.append(co)
        cur.close()
        
    def myqtablewidget(self, wdg):
        hh=[self.tr("Date" ), self.tr("Concept" ), self.tr("Amount" ), self.tr("Balance" ), self.tr("Comment" )]
        data=[]
        balance=0
        for rownumber, o in enumerate(self.arr):
            balance=balance+o.importe
            data.append([
                o.datetime, 
                o.concepto.name, 
                o.tarjeta.account.money(o.importe), 
                o.tarjeta.account.money(balance), 
                Comment(self.mem).decode(o.comentario), 
                o, 
            ])
            wdg.setDataWithObjects(hh, None, data, zonename=self.mem.localzone_name)
