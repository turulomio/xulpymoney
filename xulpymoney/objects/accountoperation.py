from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QTableWidgetItem, QApplication
from xulpymoney.libmanagers import ManagerSelectionMode, ObjectManager_With_IdDatetime_Selectable

from xulpymoney.objects.comment import Comment
from xulpymoney.libxulpymoneytypes import eConcept, eComment
from xulpymoney.ui.myqtablewidget import qdatetime, qleft
## Class to manage everything relationed with bank accounts operations
class AccountOperation(QObject):
    ## Constructor with the following attributes combination
    ## 1. AccountOperation(mem). Create an account operation with all attributes to None
    ## 2. AccountOperation(mem, id). Create an account operation searching data in the database for an id.
    ## 3. AccountOperation(mem, row, concepto, tipooperacion, account). Create an account operation from a db row, generated in a database query
    ## 4. AccountOperation(mem, datetime, concepto, tipooperacion, importe,  comentario, account, id):. Create account operation passing all attributes
    ## @param mem MemXulpymoney object
    ## @param row Dictionary of a database query cursor
    ## @param concepto Concept object
    ## @param tipooperacion OperationType object
    ## @param account Account object
    ## @param datetime Datetime of the account operation
    ## @param importe Decimal with the amount of the operation
    ## @param comentario Account operation comment
    ## @param id Integer that sets the id of an accoun operation. If id=None it's not in the database. id is set in the save method
    def __init__(self, *args):
        def init__create(dt, concepto, tipooperacion, importe,  comentario, cuenta, id):
            self.id=id
            self.datetime=dt
            self.concepto=concepto
            self.tipooperacion=tipooperacion
            self.importe=importe
            self.comentario=comentario
            self.account=cuenta
            
        def init__db_row(row, concepto,  tipooperacion, cuenta):
            init__create(row['datetime'],  concepto,  tipooperacion,  row['importe'],  row['comentario'],  cuenta,  row['id_opercuentas'])

        def init__db_query(id_opercuentas):
            """Creates a AccountOperation querying database for an id_opercuentas"""
            cur=self.mem.con.cursor()
            cur.execute("select * from opercuentas where id_opercuentas=%s", (id_opercuentas, ))
            for row in cur:
                concepto=self.mem.conceptos.find_by_id(row['id_conceptos'])
                init__db_row(row, concepto, concepto.tipooperacion, self.mem.data.accounts.find_by_id(row['id_cuentas']))
            cur.close()

        QObject.__init__(self)
        self.mem=args[0]
        if  len(args)==1:
            init__create(None, None, None, None, None, None, None)
        if len(args)==2:
            init__db_query(args[1])
        if len(args)==5:
            init__db_row(args[1], args[2], args[3], args[4])
        if len(args)==8:
            init__create(args[1], args[2], args[3], args[4], args[5], args[6], args[7])

    def __repr__(self):
        return "AccountOperation: {}".format(self.id)

    def borrar(self):
        cur=self.mem.con.cursor()
        cur.execute("delete from opercuentas where id_opercuentas=%s", (self.id, ))
        cur.close()

    def es_editable(self):
        if self.concepto==None:
            return False
        if self.concepto.id in (eConcept.BuyShares, eConcept.SellShares, 
            eConcept.Dividends, eConcept.CreditCardBilling, eConcept.AssistancePremium,
            eConcept.DividendsSaleRights, eConcept.BondsCouponRunPayment, eConcept.BondsCouponRunIncome, 
            eConcept.BondsCoupon):
            return False
        if Comment(self.mem).getCode(self.comentario) in (eComment.AccountTransferOrigin, eComment.AccountTransferDestiny, eComment.AccountTransferOriginCommission):
            return False        
        return True
        
    def save(self):
        cur=self.mem.con.cursor()
        if self.id==None:
            cur.execute("insert into opercuentas (datetime, id_conceptos, id_tiposoperaciones, importe, comentario, id_cuentas) values ( %s,%s,%s,%s,%s,%s) returning id_opercuentas",(self.datetime, self.concepto.id, self.tipooperacion.id, self.importe, self.comentario, self.account.id))
            self.id=cur.fetchone()[0]
        else:
            cur.execute("update opercuentas set datetime=%s, id_conceptos=%s, id_tiposoperaciones=%s, importe=%s, comentario=%s, id_cuentas=%s where id_opercuentas=%s", (self.datetime, self.concepto.id, self.tipooperacion.id,  self.importe,  self.comentario,  self.account.id,  self.id))
        cur.close()


## I THINK WE MUST USE HOMOGENEUS ETEROGENEUS SYSTEM
class AccountOperationManager(ObjectManager_With_IdDatetime_Selectable, QObject):
    def __init__(self, mem):
        ObjectManager_With_IdDatetime_Selectable.__init__(self)
        QObject.__init__(self)
        self.setSelectionMode(ManagerSelectionMode.Manager)
        self.mem=mem

    def load_from_db(self, sql):
        cur=self.mem.con.cursor()
        cur.execute(sql)#"Select * from opercuentas"
        for row in cur:        
            co=AccountOperation(self.mem,  row['datetime'], self.mem.conceptos.find_by_id(row['id_conceptos']), self.mem.tiposoperaciones.find_by_id(row['id_tiposoperaciones']), row['importe'], row['comentario'],  self.mem.data.accounts.find_by_id(row['id_cuentas']), row['id_opercuentas'])
            self.append(co)
        cur.close()

    def load_from_db_with_creditcard(self, sql):
        """Usado en unionall opercuentas y opertarjetas y se crea un campo id_tarjetas con el id de la tarjeta y -1 sino tiene es decir opercuentas"""
        cur=self.mem.con.cursor()
        cur.execute(sql)#"Select * from opercuentas"
        fakeid=-999999999#AccountOperationManager is a DictObjectManager needs and id. tarjetasoperation is None, that's what i make a fake id
        for row in cur:
            if row['id_tarjetas']==-1:
                comentario=row['comentario']
            else:
                comentario=QApplication.translate("Mem","Paid with {0}. {1}").format(self.mem.data.accounts.find_creditcard_by_id(row['id_tarjetas']).name, row['comentario'] )
            co=AccountOperation(self.mem, row['datetime'], self.mem.conceptos.find_by_id(row['id_conceptos']), self.mem.tiposoperaciones.find_by_id(row['id_tiposoperaciones']), row['importe'], comentario,  self.mem.data.accounts.find_by_id(row['id_cuentas']), fakeid)
            self.append(co)
            fakeid=fakeid+1
        cur.close()

    ## Section es donde guardar en el config file, coincide con el nombre del formulario en el que está la tabla
    ## show_accounts muestra la cuenta cuando las opercuentas son de diversos cuentas (Estudios totales)
    def myqtablewidget(self, tabla, show_accounts=False):
        ##HEADERS
        diff=0
        if show_accounts==True:
            tabla.setColumnCount(7)
            diff=1
        else:
            tabla.setColumnCount(6)
        tabla.setHorizontalHeaderItem(0, QTableWidgetItem(QApplication.translate("Mem","Date" )))
        if show_accounts==True:
            tabla.setHorizontalHeaderItem(diff, QTableWidgetItem(QApplication.translate("Mem","Account" )))
        tabla.setHorizontalHeaderItem(1+diff, QTableWidgetItem(QApplication.translate("Mem","Concept" )))
        tabla.setHorizontalHeaderItem(2+diff,  QTableWidgetItem(QApplication.translate("Mem","Amount" )))
        tabla.setHorizontalHeaderItem(3+diff, QTableWidgetItem(QApplication.translate("Mem","Balance" )))
        tabla.setHorizontalHeaderItem(4+diff, QTableWidgetItem(QApplication.translate("Mem","Comment" )))
        tabla.setHorizontalHeaderItem(5+diff, QTableWidgetItem("Id"))
        ##DATA 
        tabla.clearContents()
        tabla.applySettings()
        tabla.setRowCount(self.length())
        tabla.setColumnHidden(5+diff, True)
        balance=0
        for rownumber, a in enumerate(self.values_order_by_datetime()):
            balance=balance+a.importe
            tabla.setItem(rownumber, 0, qdatetime(a.datetime, self.mem.localzone_name))
            if show_accounts==True:
                tabla.setItem(rownumber, diff, QTableWidgetItem(a.account.name))
            tabla.setItem(rownumber, 1+diff, qleft(a.concepto.name))
            tabla.setItem(rownumber, 2+diff, self.mem.localcurrency.qtablewidgetitem(a.importe))
            tabla.setItem(rownumber, 3+diff, self.mem.localcurrency.qtablewidgetitem(balance))
            tabla.setItem(rownumber, 4+diff, qleft(Comment(self.mem).decode(a.comentario)))
            tabla.setItem(rownumber, 5+diff, qleft(a.id))
            if self.selected.length()>0:
                if a.id==self.selected.only().id:
                    tabla.selectRow(rownumber+1)

    def myqtablewidget_lastmonthbalance(self, wdg,    account, lastmonthbalance):
        
        from xulpymoney.libxulpymoney import Money
        wdg.table.setColumnCount(6)
        wdg.table.setHorizontalHeaderItem(0, QTableWidgetItem(self.tr("Date" )))
        wdg.table.setHorizontalHeaderItem(1, QTableWidgetItem(self.tr("Concept" )))
        wdg.table.setHorizontalHeaderItem(2, QTableWidgetItem(self.tr("Amount" )))
        wdg.table.setHorizontalHeaderItem(3,  QTableWidgetItem(self.tr("Balance" )))
        wdg.table.setHorizontalHeaderItem(4, QTableWidgetItem(self.tr("Comment" )))
        wdg.table.setHorizontalHeaderItem(5, QTableWidgetItem(self.tr("Id" )))
        wdg.applySettings()
        wdg.table.clearContents()
        wdg.table.setRowCount(self.length()+1)
        wdg.table.setItem(0, 1, QTableWidgetItem(self.tr( "Starting month balance")))
        wdg.table.setItem(0, 3, lastmonthbalance.qtablewidgetitem())
        wdg.table.setColumnHidden(5, True)
        self.order_by_datetime()
        for i, o in enumerate(self.arr):
            importe=Money(self.mem, o.importe, account.currency)
            lastmonthbalance=lastmonthbalance+importe
            wdg.table.setItem(i+1, 0, qdatetime(o.datetime, self.mem.localzone_name))
            wdg.table.setItem(i+1, 1, QTableWidgetItem(o.concepto.name))
            wdg.table.setItem(i+1, 2, importe.qtablewidgetitem())
            wdg.table.setItem(i+1, 3, lastmonthbalance.qtablewidgetitem())
            wdg.table.setItem(i+1, 4, QTableWidgetItem(Comment(self.mem).decode(o.comentario)))       
            wdg.table.setItem(i+1, 5, qleft(o.id))
#            if self.selected.length()>0:
#                if o.id==self.selected.only().id:
#                    wdg.table.selectRow(i+1)

class AccountOperationManagerHeterogeneus(ObjectManager_With_IdDatetime_Selectable, QObject):
    def __init__(self, mem):
        ObjectManager_With_IdDatetime_Selectable.__init__(self)
        QObject.__init__(self)
        self.setSelectionMode(ManagerSelectionMode.Manager)
        self.mem=mem
    
    ## Función que calcula el balance de todas las AccountOperation in eMoneyCurrency.User
    def balance(self):
        from xulpymoney.libxulpymoney import Money
        r=Money(self.mem, 0, self.mem.localcurrency)
        for o in self.arr:
            if o.account.currency==self.mem.localcurrency:
                r=r+Money(self.mem, o.importe, o.account.currency)
            else:
                r=r+Money(self.mem, o.importe, o.account.currency).convert(self.mem.localcurrency, o.datetime)
        return r

    def load_from_db(self, sql):
        cur=self.mem.con.cursor()
        cur.execute(sql)#"Select * from opercuentas"
        for row in cur:        
            co=AccountOperation(self.mem,  row['datetime'], self.mem.conceptos.find_by_id(row['id_conceptos']), self.mem.tiposoperaciones.find_by_id(row['id_tiposoperaciones']), row['importe'], row['comentario'],  self.mem.data.accounts.find_by_id(row['id_cuentas']), row['id_opercuentas'])
            self.append(co)
        cur.close()

    def load_from_db_with_creditcard(self, sql):
        """Usado en unionall opercuentas y opertarjetas y se crea un campo id_tarjetas con el id de la tarjeta y -1 sino tiene es decir opercuentas"""
        cur=self.mem.con.cursor()
        cur.execute(sql)#"Select * from opercuentas"
        fakeid=-999999999#AccountOperationManager is a DictObjectManager needs and id. tarjetasoperation is None, that's what i make a fake id
        for row in cur:
            if row['id_tarjetas']==-1:
                comentario=row['comentario']
            else:
                comentario=self.tr("Paid with {0}. {1}").format(self.mem.data.accounts.find_creditcard_by_id(row['id_tarjetas']).name, row['comentario'] )
            co=AccountOperation(self.mem, row['datetime'], self.mem.conceptos.find_by_id(row['id_conceptos']), self.mem.tiposoperaciones.find_by_id(row['id_tiposoperaciones']), row['importe'], comentario,  self.mem.data.accounts.find_by_id(row['id_cuentas']), fakeid)
            self.append(co)
            fakeid=fakeid+1
        cur.close()

    ## Section es donde guardar en el config file, coincide con el nombre del formulario en el que está la tabla
    ## show_accounts muestra la cuenta cuando las opercuentas son de diversos cuentas (Estudios totales)
    def myqtablewidget(self, tabla, show_accounts=False):
        ##HEADERS
        diff=0
        if show_accounts==True:
            tabla.setColumnCount(7)
            diff=1
        else:
            tabla.setColumnCount(6)
        tabla.setHorizontalHeaderItem(0, QTableWidgetItem(self.tr("Date" )))
        if show_accounts==True:
            tabla.setHorizontalHeaderItem(diff, QTableWidgetItem(self.tr("Account" )))
        tabla.setHorizontalHeaderItem(1+diff, QTableWidgetItem(self.tr("Concept" )))
        tabla.setHorizontalHeaderItem(2+diff,  QTableWidgetItem(self.tr("Amount" )))
        tabla.setHorizontalHeaderItem(3+diff, QTableWidgetItem(self.tr("Balance" )))
        tabla.setHorizontalHeaderItem(4+diff, QTableWidgetItem(self.tr("Comment" )))
        tabla.setHorizontalHeaderItem(5+diff, QTableWidgetItem("Id"))
        ##DATA 
        tabla.clearContents()
        tabla.applySettings()
        tabla.setRowCount(self.length())
        tabla.setColumnHidden(5+diff, True)
        balance=0
        for rownumber, a in enumerate(self.values_order_by_datetime()):
            balance=balance+a.importe
            tabla.setItem(rownumber, 0, qdatetime(a.datetime, self.mem.localzone_name))
            if show_accounts==True:
                tabla.setItem(rownumber, diff, QTableWidgetItem(a.account.name))
            tabla.setItem(rownumber, 1+diff, qleft(a.concepto.name))
            tabla.setItem(rownumber, 2+diff, self.mem.localcurrency.qtablewidgetitem(a.importe))
            tabla.setItem(rownumber, 3+diff, self.mem.localcurrency.qtablewidgetitem(balance))
            tabla.setItem(rownumber, 4+diff, qleft(Comment(self.mem).decode(a.comentario)))
            tabla.setItem(rownumber, 5+diff, qleft(a.id))
            if self.selected.length()>0:
                if a.id==self.selected.only().id:
                    tabla.selectRow(rownumber+1)




class AccountOperationManagerHomogeneus(AccountOperationManagerHeterogeneus):
    def __init__(self, mem, account):
        AccountOperationManagerHeterogeneus.__init__(self, mem)
        self.account=account


    def myqtablewidget_lastmonthbalance(self, table,    lastmonthbalance):
        
        from xulpymoney.libxulpymoney import Money
        table.applySettings()
        table.clearContents()
        table.setRowCount(self.length()+1)
        table.setItem(0, 1, QTableWidgetItem(self.tr( "Starting month balance")))
        table.setItem(0, 3, lastmonthbalance.qtablewidgetitem())
        table.setColumnHidden(5, True)
        for i, o in enumerate(self.values_order_by_datetime()):
            importe=Money(self.mem, o.importe, self.account.currency)
            lastmonthbalance=lastmonthbalance+importe
            table.setItem(i+1, 0, qdatetime(o.datetime, self.mem.localzone_name))
            table.setItem(i+1, 1, QTableWidgetItem(o.concepto.name))
            table.setItem(i+1, 2, importe.qtablewidgetitem())
            table.setItem(i+1, 3, lastmonthbalance.qtablewidgetitem())
            table.setItem(i+1, 4, QTableWidgetItem(Comment(self.mem).decode(o.comentario)))       
            table.setItem(i+1, 5, qleft(o.id))
            if self.selected.length()>0:
                if o.id==self.selected.only().id:
                    table.selectRow(i+1)
                    
                    
## Clase parar trabajar con las opercuentas generadas automaticamente por los movimientos de las inversiones
class AccountOperationOfInvestmentOperation(QObject):
    ## Constructor with the following attributes combination
    ## 1. AccountOperationOfInvestmentOperation(mem). Create an account operation of an investment operation with all attributes to None
    ## 2. AccountOperationOfInvestmentOperation(mem,  datetime,  concepto, tipooperacion, importe, comentario, cuenta, operinversion, inversion, id). Create an account operation of an investment operation settings all attributes.1
    ## @param mem MemXulpymoney object
    ## @param datetime Datetime of the account operation
    ## @param concepto Concept object
    ## @param tipooperacion OperationType object
    ## @param importe Decimal with the amount of the operation
    ## @param comentario Account operation comment
    ## @param account Account object
    ## @param operinversion InvestmentOperation object that generates this account operation
    ## @param id Integer that sets the id of an accoun operation. If id=None it's not in the database. id is set in the save method
    def __init__(self, *args):
        def init__create(datetime,  concepto, tipooperacion, importe, comentario, account, operinversion, inversion, id):
            self.datetime=datetime
            self.concepto=concepto
            self.tipooperacion=tipooperacion
            self.importe=importe
            self.comentario=comentario
            self.account=account
            self.operinversion=operinversion
            self.investment=inversion
            self.id=id
        QObject.__init__(self)
        self.mem=args[0]
        if len(args)==1:
            init__create(None, None, None, None, None, None, None, None, None)
        if len(args)==10:
            init__create(args[1], args[2], args[3], args[4], args[5], args[6], args[7], args[8], args[9])

    def save(self):
        cur=self.mem.con.cursor()
        if self.id==None:
            cur.execute("insert into opercuentasdeoperinversiones (datetime, id_conceptos, id_tiposoperaciones, importe, comentario,id_cuentas, id_operinversiones,id_inversiones) values ( %s,%s,%s,%s,%s,%s,%s,%s) returning id_opercuentas", (self.datetime, self.concepto.id, self.tipooperacion.id, self.importe, self.comentario, self.account.id, self.operinversion.id, self.investment.id))
            self.id=cur.fetchone()[0]
        else:
            cur.execute("UPDATE FALTA  set datetime=%s, id_conceptos=%s, id_tiposoperaciones=%s, importe=%s, comentario=%s, id_cuentas=%s where id_opercuentas=%s", (self.datetime, self.concepto.id, self.tipooperacion.id,  self.importe,  self.comentario,  self.account.id,  self.id))
        cur.close()
        
