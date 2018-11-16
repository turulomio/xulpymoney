## @package libxulpymoney
## @brief Package with all xulpymoney core classes .

from PyQt5.QtCore import QObject,  pyqtSignal,  QTimer,  Qt,  QSettings, QCoreApplication, QTranslator
from PyQt5.QtGui import QIcon,  QColor,  QPixmap,  QFont
from PyQt5.QtWidgets import QTableWidgetItem,   QMessageBox, QApplication,   qApp,  QProgressDialog
from officegenerator import ODT_Standard, ODS_Write, Coord,  OpenPyXL
from odf.text import P
import datetime
import time
import logging
import platform
import io
import pytz
import pkg_resources
import psycopg2
import psycopg2.extras
import sys
import argparse
import getpass
import os
from decimal import Decimal, getcontext
from xulpymoney.version import __version__
from xulpymoney.libxulpymoneyfunctions import makedirs, qdatetime, dtaware, qright, qleft, qcenter, qdate, qbool, day_end_from_date, day_start_from_date, days2string, month_end, month_start, year_end, year_start, str2bool, function_name, string2date, string2datetime, string2list, qmessagebox, qtime, dtaware2string, day_end, list2string, dirs_create, qempty,  l10nDecimal, deprecated
from xulpymoney.libxulpymoneytypes import eProductType, eTickerPosition,  eHistoricalChartAdjusts,  eOHCLDuration, eOperationType,  eLeverageType,  eQColor
from xulpymoney.libmanagers import Object_With_IdName, ObjectManager_With_Id_Selectable, ObjectManager_With_IdName_Selectable, ObjectManager_With_IdDatetime_Selectable,  ObjectManager, ObjectManager_With_IdDate,  DictObjectManager_With_IdDatetime_Selectable,  DictObjectManager_With_IdName_Selectable, ManagerSelectionMode
from PyQt5.QtChart import QChart
getcontext().prec=20

class Connection(QObject):
    inactivity_timeout=pyqtSignal()
    def __init__(self):
        QObject.__init__(self)
        
        self.user=None
        self.password=None
        self.server=None
        self.port=None
        self.db=None
        self._con=None
        self._active=False
        
        self.restart_timeout()
        self.inactivity_timeout_minutes=30
        self.init=None
        
    def init__create(self, user, password, server, port, db):
        self.user=user
        self.password=password
        self.server=server
        self.port=port
        self.db=db
        return self
        
    def _check_inactivity(self):
        if datetime.datetime.now()-self._lastuse>datetime.timedelta(minutes=self.inactivity_timeout_minutes):
            self.disconnect()
            self._timerlastuse.stop()
            self.inactivity_timeout.emit()
        print ("Remaining time {}".format(self._lastuse+datetime.timedelta(minutes=self.inactivity_timeout_minutes)-datetime.datetime.now()))

    def cursor(self):
        self.restart_timeout()#Datetime who saves the las use of connection
        return self._con.cursor()
        
    def restart_timeout(self):
        """Resets timeout, usefull in long process without database connections"""
        self._lastuse=datetime.datetime.now()
        
    
    def mogrify(self, sql, arr):
        """Mogrify text"""
        cur=self._con.cursor()
        s=cur.mogrify(sql, arr)
        cur.close()
        return  s
        
    def cursor_one_row(self, sql, arr=[]):
        """Returns only one row"""
        self.restart_timeout()
        cur=self._con.cursor()
        cur.execute(sql, arr)
        row=cur.fetchone()
        cur.close()
        return row        
        
    def cursor_one_column(self, sql, arr=[]):
        """Returns un array with the results of the column"""
        self.restart_timeout()
        cur=self._con.cursor()
        cur.execute(sql, arr)
        for row in cur:
            arr.append(row[0])
        cur.close()
        return arr
        
    def cursor_one_field(self, sql, arr=[]):
        """Returns only one field"""
        self.restart_timeout()
        cur=self._con.cursor()
        cur.execute(sql, arr)
        row=cur.fetchone()[0]
        cur.close()
        return row      
        
    def commit(self):
        self._con.commit()
        
    def rollback(self):
        self._con.rollback()
        
        
    def connection_string(self):
        return "dbname='{}' port='{}' user='{}' host='{}' password='{}'".format(self.db, self.port, self.user, self.server, self.password)
        
    def connect(self, connection_string=None):
        """Used in code to connect using last self.strcon"""
        if connection_string==None:
            s=self.connection_string()
        else:
            s=connection_string        
        try:
            self._con=psycopg2.extras.DictConnection(s)
        except psycopg2.Error as e:
            print (e.pgcode, e.pgerror)
            return
        self._active=True
        self.init=datetime.datetime.now()
        self.restart_timeout()
        self._timerlastuse = QTimer()
        self._timerlastuse.timeout.connect(self._check_inactivity)
        self._timerlastuse.start(300000)
        
    def disconnect(self):
        self._active=False
        if self._timerlastuse.isActive()==True:
            self._timerlastuse.stop()
        self._con.close()
        
    def is_active(self):
        return self._active
        
        
    def is_superuser(self):
        """Checks if the user has superuser role"""
        res=False
        cur=self.cursor()
        cur.execute("SELECT rolsuper FROM pg_roles where rolname=%s;", (self.user, ))
        if cur.rowcount==1:
            if cur.fetchone()[0]==True:
                res=True
        cur.close()
        return res
class Percentage:
    def __init__(self, numerator=None, denominator=None):
        self.value=None
        self.setValue(self.toDecimal(numerator),self.toDecimal(denominator))
        
        
    def toDecimal(self, o):
        if o==None:
            return o
        if o.__class__==Money:
            return o.amount
        elif o.__class__==Decimal:
            return o
        elif o.__class__ in ( int, float):
            return Decimal(o)
        elif o.__class__==Percentage:
            return o.value
        else:
            print (o.__class__)
            return None
        
    def __repr__(self):
        return self.string()
            
    def __neg__(self):
        """Devuelve otro money con el amount con signo cambiado"""
        if self.value==None:
            return self
        return Percentage(-self.value, 1)
        
    def __lt__(self, other):
        if self.value==None:
            value1=Decimal('-Infinity')
        else:
            value1=self.value
        if other.value==None:
            value2=Decimal('-Infinity')
        else:
            value2=other.value
        if value1<value2:
            return True
        return False
        
    def __mul__(self, value):
        if self.value==None or value==None:
            r=None
        else:
            r=self.value*self.toDecimal(value)
        return Percentage(r, 1)

    def __truediv__(self, value):
        try:
            r=self.value/self.toDecimal(value)
        except:
            r=None
        return Percentage(r, 1)
        
    def setValue(self, numerator,  denominator):
        try:
            self.value=Decimal(numerator/denominator)
        except:
            self.value=None
        
        
    def value_100(self):
        if self.value==None:
            return None
        else:
            return self.value*Decimal(100)
        
    def string(self, rnd=2):
        if self.value==None:
            return "None %"
        return "{} %".format(round(self.value_100(), rnd))
        
    def qtablewidgetitem(self, rnd=2):
        a=QTableWidgetItem(self.string(rnd))
        a.setTextAlignment(Qt.AlignVCenter|Qt.AlignRight)
        if self.value==None:
            a.setForeground(QColor(0, 0, 255))
        elif self.value<0:
            a.setForeground(QColor(255, 0, 0))
        return a
        
    def isValid(self):
        if self.value!=None:
            return True
        return False
        
    def isGETZero(self):
        if self.value>=0:
            return True
        return False
    def isGTZero(self):
        if self.value>0:
            return True
        return False
    def isLTZero(self):
        if self.value<0:
            return True
        return False

## Clase parar trabajar con las opercuentas generadas automaticamente por los movimientos de las inversiones
class AccountOperationOfInvestmentOperation:
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

class SimulationTypeManager(ObjectManager_With_IdName_Selectable):
    def __init__(self, mem):
        ObjectManager_With_IdName_Selectable.__init__(self)
        self.mem=mem

    def load_all(self):
        self.append(SimulationType().init__create(1,QApplication.translate("Core","Xulpymoney between dates")))
        self.append(SimulationType().init__create(2,QApplication.translate("Core","Xulpymvoney only investments between dates")))
        self.append(SimulationType().init__create(3,QApplication.translate("Core","Simulating current benchmark between dates")))
        
    def qcombobox(self, combo,  selected=None):
        """selected is a SimulationType object""" 
        ###########################
        combo.clear()
        for a in self.arr:
            combo.addItem(a.qicon(), a.name, a.id)

        if selected!=None:
                combo.setCurrentIndex(combo.findData(selected.id))

class InvestmentManager(ObjectManager_With_IdName_Selectable):
    def __init__(self, mem, cuentas, products, benchmark):
        ObjectManager_With_IdName_Selectable.__init__(self)
        self.mem=mem
        self.accounts=cuentas
        self.products=products
        self.benchmark=benchmark  ##Objeto product
            
    def load_from_db(self, sql,  progress=False):
        cur=self.mem.con.cursor()
        cur.execute(sql)#"Select * from inversiones"
        if progress==True:
            pd= QProgressDialog(QApplication.translate("Core","Loading {0} investments from database").format(cur.rowcount),None, 0,cur.rowcount)
            pd.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
            pd.setModal(True)
            pd.setWindowTitle(QApplication.translate("Core","Loading investments..."))
            pd.forceShow()
        for row in cur:
            if progress==True:
                pd.setValue(cur.rownumber)
                pd.update()
                QApplication.processEvents()
            inv=Investment(self.mem).init__db_row(row,  self.accounts.find_by_id(row['id_cuentas']), self.products.find_by_id(row['products_id']))
            inv.get_operinversiones()
            self.append(inv)
        cur.close()  
            
    def myqtablewidget(self, table):
        """Esta tabla muestra los money con la moneda local"""
        table.setRowCount(self.length())
        table.applySettings()
        table.clearContents()
        type=3
        for i, inv in enumerate(self.arr):
            table.setItem(i, 0, QTableWidgetItem("{0} ({1})".format(inv.name, inv.account.name)))            
            table.setItem(i, 1, qdatetime(inv.product.result.basic.last.datetime, self.mem.localzone))
            table.setItem(i, 2, inv.product.currency.qtablewidgetitem(inv.product.result.basic.last.quote,  6))#Se debería recibir el parametro currency
            table.setItem(i, 3, inv.op_actual.gains_last_day(type).qtablewidgetitem())
            table.setItem(i, 4, inv.product.result.basic.tpc_diario().qtablewidgetitem())
            table.setItem(i, 5, inv.balance(None,  type).qtablewidgetitem())
            table.setItem(i, 6, inv.op_actual.pendiente(inv.product.result.basic.last, type).qtablewidgetitem())
            
            tpc_invertido=inv.op_actual.tpc_total(inv.product.result.basic.last, type)
            table.setItem(i, 7, tpc_invertido.qtablewidgetitem())
            if self.mem.gainsyear==True and inv.op_actual.less_than_a_year()==True:
                table.item(i, 7).setIcon(QIcon(":/xulpymoney/new.png"))
            
            tpc_venta=inv.percentage_to_selling_point()
            table.setItem(i, 8, tpc_venta.qtablewidgetitem())
            if inv.selling_expiration!=None:
                if inv.selling_expiration<datetime.date.today():
                    table.item(i, 8).setIcon(QIcon(":/xulpymoney/alarm_clock.png"))
            if tpc_invertido.isValid() and tpc_venta.isValid():
                if tpc_invertido.value_100()<=-Decimal(50):   
                    table.item(i, 7).setBackground(eQColor.Red)
                if (tpc_venta.value_100()<=Decimal(5) and tpc_venta.isGTZero()) or tpc_venta.isLTZero():
                    table.item(i, 8).setBackground(eQColor.Green)

    def myqtablewidget_lastCurrent(self, table,  percentage):
        """
            Percentage is the colored percentage to show
        """
        table.setRowCount(len(self.arr))
        table.applySettings()
        table.clearContents()
        type=3
        for i, inv in enumerate(self.arr):
            try:
                table.setItem(i, 0, QTableWidgetItem("{0} ({1})".format(inv.name, inv.account.name)))
                table.setItem(i, 1, qdatetime(inv.op_actual.last().datetime, self.mem.localzone))
                table.setItem(i, 2, qright(inv.op_actual.last().shares))
                table.setItem(i, 3, qright(inv.op_actual.shares()))
                table.setItem(i, 4,  inv.balance(None, type).qtablewidgetitem())
                table.setItem(i, 5, inv.op_actual.pendiente(inv.product.result.basic.last, type).qtablewidgetitem())
                lasttpc=inv.op_actual.last().tpc_total(inv.product.result.basic.last, type=3)
                table.setItem(i, 6, lasttpc.qtablewidgetitem())
                table.setItem(i, 7, inv.op_actual.tpc_total(inv.product.result.basic.last, type=3).qtablewidgetitem())
                table.setItem(i, 8, inv.percentage_to_selling_point().qtablewidgetitem())
                if lasttpc<Percentage(percentage, 1):   
                    table.item(i, 6).setBackground(eQColor.Red)
            except:
                logging.error("I couldn't show last of {}".format(inv.name))

    def myqtablewidget_sellingpoints(self, table):
        """Crea un set y luego construye la tabla"""
        
        set=InvestmentManager(self.mem,  self.accounts, self.products, self.benchmark)
        for inv in self.arr:
            if inv.selling_expiration!=None and inv.shares()>0:
                set.append(inv)
        set.order_by_percentage_sellingpoint()
        
        table.setColumnCount(7)
        table.setHorizontalHeaderItem(0, QTableWidgetItem(QApplication.translate("Core","Date")))
        table.setHorizontalHeaderItem(1, QTableWidgetItem(QApplication.translate("Core","Expiration")))
        table.setHorizontalHeaderItem(2, QTableWidgetItem(QApplication.translate("Core","Investment")))
        table.setHorizontalHeaderItem(3, QTableWidgetItem(QApplication.translate("Core","Account")))
        table.setHorizontalHeaderItem(4, QTableWidgetItem(QApplication.translate("Core","Shares")))
        table.setHorizontalHeaderItem(5, QTableWidgetItem(QApplication.translate("Core","Price")))
        table.setHorizontalHeaderItem(6, QTableWidgetItem(QApplication.translate("Core","% selling point")))
   
        table.applySettings()
        table.clearContents()
        table.setRowCount(set.length())
        for i, inv in enumerate(set.arr):
            if inv.selling_expiration!=None:
                table.setItem(i, 0, qdate(inv.op_actual.last().datetime.date()))
                table.setItem(i, 1, qdate(inv.selling_expiration))    
                if inv.selling_expiration<datetime.date.today():
                    table.item(i, 1).setBackground(eQColor.Red)       
                table.setItem(i, 2, qleft(inv.name))
                table.setItem(i, 3, qleft(inv.account.name))   
                table.setItem(i, 4, qright(inv.shares()))
                table.setItem(i, 5, inv.product.currency.qtablewidgetitem(inv.venta))
                table.setItem(i, 6, inv.percentage_to_selling_point().qtablewidgetitem())


    def average_age(self):
        """Average age of the investments in this set in days"""
        #Extracts all currentinvestmentoperations
        set=InvestmentOperationCurrentHeterogeneusManager(self.mem)
        for inv in self.arr:
            for o in inv.op_actual.arr:
                set.arr.append(o)
        average=set.average_age()
        if average==None:
            return None
        return round(average, 2)
            
    ## Returns and InvestmentManager object with all investmentes with the same product passed as parameter
    ## @param product Product to search in this InvestmentManager
    ## @return InvestmentManager
    def InvestmentManager_with_investments_with_the_same_product(self, product):
        result=InvestmentManager(self.mem, self.accounts, self.products, self.benchmark)
        for inv in self.arr:
            if inv.product.id==product.id:
                result.append(inv)
        return result

    ## Change investments with a product_id to another product_id
    ## @param product_from. 
    ## @param product_to
    def change_product_id(self,  product_from,  product_to):
        for inv in self.InvestmentManager_with_investments_with_the_same_product(product_from).arr:
            inv.product=product_to
            inv.save()

    def findInvestmentOperation(self, id):
        """Busca la IO en el set o dveuleve None"""
        for inv in self.arr:
            for o in inv.op.arr:
                if o.id==id:
                    return o
        return None
            
            
    def revaluation_monthly(self, type_id,  year, month):
        """
            Used to get investments type_id revauation montyly
            if type==2 I get current investment funds revaluation_annual
            I must use current investment, because inactive has been contabilized in gains
        """
        r=Money(self.mem, 0, self.mem.localcurrency)
        for inv in self.setinvestments_filter_by_type(type_id).arr:
            for o in inv.op_actual.arr:
                r=r+o.revaluation_monthly(year, month, type=3)
        return r
                    
    def revaluation_annual(self, type_id, year):
        """
            Used to get investments type_id revauation annual
            if type==2 I get current investment funds revaluation_annual
            I must use current investment, because inactive has been contabilized in gains
        """
        r=Money(self.mem, 0, self.mem.localcurrency)
        for inv in self.setinvestments_filter_by_type(type_id).arr:
            for o in inv.op_actual.arr:
                r=r+o.revaluation_annual(year, type=3)
        return r
            
    def gains_last_day(self):
        """Da el resultado en self.mem.localcurrency"""
        r=Money(self.mem, 0, self.mem.localcurrency)
        for inv in self.arr:
            r=r+inv.op_actual.gains_last_day(type=3)
        return r 

    def invested(self):
        """Da el resultado en self.mem.localcurrency"""
        r=Money(self.mem, 0, self.mem.localcurrency)
        for inv in self.arr:
            r=r+inv.invertido(type=3)
        return r            
    
    def numberWithSameProduct(self, product):
        """
            Returns the number of investments with the same product in the array
        """
        r=0
        for inv in self.arr:
            if inv.product.id==product.id:
                r=r+1
        return r
        
    def pendiente(self):
        """Da el resultado en self.mem.localcurrency"""
        r=Money(self.mem, 0, self.mem.localcurrency)
        for inv in self.arr:
            r=r+inv.op_actual.pendiente(inv.product.result.basic.last, 3)
        return r
    def pendiente_positivo(self):
        """Da el resultado en self.mem.localcurrency"""
        r=Money(self.mem, 0, self.mem.localcurrency)
        for inv in self.arr:
            pendiente=inv.op_actual.pendiente(inv.product.result.basic.last, 3)
            if pendiente.isGETZero():
                r=r+pendiente
        return r
    def pendiente_negativo(self):
        """Da el resultado en self.mem.localcurrency"""
        r=Money(self.mem, 0, self.mem.localcurrency)
        for inv in self.arr:
            pendiente=inv.op_actual.pendiente(inv.product.result.basic.last, 3)
            if pendiente.isLETZero():
                r=r+pendiente
        return r

    def ProductManager_with_investments_distinct_products(self):
        """Returns a SetProduct with all distinct products of the Set investments items"""
        s=set([])
        for i in self.arr:
            s.add(i.product)
            
        r=ProductManager(self.mem)
        for p in s:
            r.append(p)        
        return r
        

    def investment_merging_operations_with_same_product(self,  product):
        """
            Returns and investment object, with all operations of the invesments with the same product. The merged investments are in the set
            The investment and the operations are copied objects.
            
            Tiene cuenta como None, Active=False y Id=None
            
            Account no es necesaria pero para mostrar algunas tablas con los calculos (currency) se necesita por lo que se puede pasar como parametro. Por ejemplo
            en frmReportInvestment, se pasar´ia la< cuenta asociada ala inversi´on del informe.
            
            Realmente es aplicar el m´etodo FIFO  a todas las inversiones.
            
        """
        name=QApplication.translate("Core", "Virtual investment merging all operations of {}".format(product.name))
        bank=Bank(self.mem).init__create("Merging bank", True, -1)
        account=Account(self.mem, "Merging account",  bank, True, "", self.mem.localcurrency, -1)
        r=Investment(self.mem).init__create(name, None, account, product, None, True, -1)
        r.merge=2
        r.op=InvestmentOperationHomogeneusManager(self.mem, r)
        for inv in self.arr: #Recorre las inversion del array
            if inv.product.id==product.id:
                for o in inv.op.arr:
                    #En operations quito los traspasos, ya que fallaban calculos dobles pasadas y en realidad no hace falta porque son transpasos entre mismos productos
                    #En operations actual no hace falta porque se eliminan los transpasos origen de las operaciones actuales
                    if o.tipooperacion.id not in (9, 10):
                        io=o.copy(investment=r)
                        r.op.append(io)
                    
        r.op.order_by_datetime()
        (r.op_actual,  r.op_historica)=r.op.calcular() 
        return r


    def setDividends_merging_operation_dividends(self, product):
        name=QApplication.translate("Core", "Virtual investment merging all operations of {}".format(product.name))
        bank=Bank(self.mem).init__create("Merging bank", True, -1)
        account=Account(self.mem, "Merging account",  bank, True, "", self.mem.localcurrency, -1)
        r=Investment(self.mem).init__create(name, None, account, product, None, True, -1)
        set=DividendHomogeneusManager(self.mem, r)
        for inv in self.arr:
            if inv.product.id==product.id:
                for d in inv.setDividends_from_operations().arr:
                    set.append(d)
        set.order_by_datetime()
        return set

    def investment_merging_current_operations_with_same_product(self, product):
        """
            Funci´on que convierte el set actual de inversiones, sacando las del producto pasado como parámetro
            Crea una inversi´on nueva cogiendo las  operaciones actuales, juntándolas , convirtiendolas en operaciones normales 
            
            se usa para hacer reinversiones, en las que no se ha tenido cuenta el metodo fifo, para que use las acciones actuales.
        """
        name=QApplication.translate("Core", "Virtual investment merging current operations of {}".format(product.name))
        bank=Bank(self.mem).init__create("Merging bank", True, -1)
        account=Account(self.mem, "Merging account",  bank, True, "", self.mem.localcurrency, -1)
        r=Investment(self.mem).init__create(name, None, account, product, None, True, -1)    
        r.merge=1
        r.op=InvestmentOperationHomogeneusManager(self.mem, r)
        for inv in self.arr: #Recorre las inversion del array
            if inv.product.id==product.id:
                for o in inv.op_actual.arr:
                    r.op.append(InvestmentOperation(self.mem).init__create(o.tipooperacion, o.datetime, r, o.shares, o.impuestos, o.comision,  o.valor_accion,  o.comision,  o.show_in_ranges,  o.currency_conversion,  o.id))
        r.op.order_by_datetime()
        (r.op_actual,  r.op_historica)=r.op.calcular()             
        return r
        

    def setDividends_merging_current_operation_dividends(self, product):
        name=QApplication.translate("Core", "Virtual investment merging current operations of {}".format(product.name))
        bank=Bank(self.mem).init__create("Merging bank", True, -1)
        account=Account(self.mem, "Merging account",  bank, True, "", self.mem.localcurrency, -1)
        r=Investment(self.mem).init__create(name, None, account, product, None, True, -1)    
        set=DividendHomogeneusManager(self.mem, r)
        for inv in self.arr:
            if inv.product.id==product.id:
                for d in inv.setDividends_from_current_operations().arr:
                    set.append(d)
        set.order_by_datetime()
        return set

    def setinvestments_filter_by_type(self,  type_id):
        """
            Returns a new setinvestments filtering original by type_id
            For example to get all funds in the original setinvesmet
        """
        r=InvestmentManager(self.mem, self.mem.data.accounts, self.mem.data.products, self.mem.data.benchmark )
        for inv in self.arr:
            if inv.product.type.id==type_id:
                r.append(inv)
        return r

    def setInvestments_merging_investments_with_same_product_merging_operations(self):
        """
            Genera un set Investment nuevo , creando invesments aglutinadoras de todas las inversiones con el mismo producto
            
            Account no es necesaria pero para mostrar algunas tablas con los calculos (currency) se necesita por lo que se puede pasar como parametro. Por ejemplo
            en frmReportInvestment, se pasar´ia la< cuenta asociada ala inversi´on del informe.
            
        """
        invs=InvestmentManager(self.mem, None, self.mem.data.products, self.mem.data.benchmark)
        for product in self.ProductManager_with_investments_distinct_products().arr:
            i=self.investment_merging_operations_with_same_product(product)
            invs.append(i) 
        return invs

                
    def setInvestments_merging_investments_with_same_product_merging_current_operations(self):
        """
            Genera un set Investment nuevo , creando invesments aglutinadoras de todas las inversiones con el mismo producto
            
            Account no es necesaria pero para mostrar algunas tablas con los calculos (currency) se necesita por lo que se puede pasar como parametro. Por ejemplo
            en frmReportInvestment, se pasar´ia la< cuenta asociada ala inversi´on del informe.
            
        """
        invs=InvestmentManager(self.mem, None, self.mem.data.products, self.mem.data.benchmark)
        for product in self.ProductManager_with_investments_distinct_products().arr:
            i=self.investment_merging_current_operations_with_same_product(product)
            invs.append(i) 
        return invs






    def qcombobox_same_investmentmq(self, combo,  investmentmq):
        """Muestra las inversiones activas que tienen el mq pasado como parametro"""
        arr=[]
        for i in self.arr:
            if i.active==True and i.product==investmentmq:
                arr.append(("{0} - {1}".format(i.account.eb.name, i.name), i.id))
                        
        arr=sorted(arr, key=lambda a: a[0]  ,  reverse=False)  
        for a in arr:
            combo.addItem(a[0], a[1])

    def qcombobox(self, combo, tipo, selected=None, obsolete_product=False, investments_active=True,  accounts_active=True):
        """
        Investments_active puede tomar None. Muestra Todas, True. Muestra activas y False Muestra inactivas
        Accounts_active puede tomar None. Muestra Todas, True. Muestra activas y False Muestra inactivas
        Obsolete_product puede tomar True: Muestra tambien obsoletos y False, no muestra los obsoletos
        tipo es una variable que controla la forma de visualizar
        0: inversion
        1: eb - inversion
        2: inversion (cuenta)
        3: Cuenta - inversion
        
        selected is an Investment object"""
        combo.clear()
        arr=[]
        for i in self.arr:
            if accounts_active==True:
                if i.account.active==False:
                    continue
            elif accounts_active==False:
                if i.account.active==True:
                    continue
                    
            if investments_active==True:
                if i.active==False:
                    continue
            elif investments_active==False:
                if i.active==True:
                    continue
                    
            if obsolete_product==False:
                if i.product.obsolete==True:
                    continue


            if tipo==0:
                arr.append((i.name, i.id))            
            elif tipo==1:
                arr.append(("{} - {}".format(i.account.eb.name, i.name), i.id))
            elif tipo==2:
                arr.append(("{} ({})".format(i.name, i.account.name), i.id))
            elif tipo==3:
                arr.append(("{} - {}".format(i.account.name, i.name), i.id))
                
        
        arr=sorted(arr, key=lambda a: a[0]  ,  reverse=False)  
        for a in arr:
            combo.addItem(a[0], a[1])
        if selected==None:
            combo.setCurrentIndex(-1)
        else:
            combo.setCurrentIndex(combo.findData(selected.id))
            
    def traspaso_valores(self, origen, destino, numacciones, comision):
        """Función que realiza un traspaso de valores desde una inversion origen a destino
        
        En origen:
            - Debe comprobar que origen y destino es el mismo
            - Se añade una operinversion con traspaso de valores origen que tendrá un balance de acciones negativo
            - Se añadirá un comentario con id_inversiondestino
            
        En destino:
            - Se añaden tantas operaciones como operinversionesactual con misma datetime 
            - Tendrán balance positivo y el tipo operacion es traspaso de valores. destino 
            - Se añadirá un comentario con id_operinversion origen
            
        Devuelve False si ha habido algún problema
        
        ACTUALMENTE SOLO HACE UN TRASLADO TOTAL
        """
        #Comprueba que el subyacente de origen y destino sea el mismo
        if origen.product!=destino.product:
            return False
        now=self.mem.localzone.now()
        currency_conversion=1
        if comision!=0:
            op_cuenta=AccountOperation(self.mem, now.date(), self.mem.conceptos.find_by_id(38), self.mem.tiposoperaciones.find_by_id(1), -comision, "Traspaso de valores", origen.account, None)
            op_cuenta.save()           
            comentario="{0}|{1}".format(destino.id, op_cuenta.id)
        else:
            comentario="{0}|{1}".format(destino.id, "None")
        
        op_origen=InvestmentOperation(self.mem).init__create( self.mem.tiposoperaciones.find_by_id(9), now, origen,  -numacciones, 0,0, comision, 0, comentario, True, currency_conversion)
        op_origen.save( False)      

        #NO ES OPTIMO YA QUE POR CADA SAVE SE CALCULA TODO
        comentario="{0}".format(op_origen.id)
        for o in origen.op_actual.arr:
            op_destino=InvestmentOperation(self.mem).init__create( self.mem.tiposoperaciones.find_by_id(10), now, destino,  o.shares, o.importe, o.impuestos, o.comision, o.valor_accion, comentario,  o.show_in_ranges, currency_conversion)
            op_destino.save( False)
            
        #Vuelvo a introducir el comentario de la opercuenta
        self.mem.con.commit()
        (origen.op_actual,  origen.op_historica)=origen.op.calcular()   
        (destino.op_actual,  destino.op_historica)=destino.op.calcular()   
        return True
        
    def traspaso_valores_deshacer(self, operinversionorigen):
        """Da marcha atrás a un traspaso de valores realizado por equivocación
        Solo se podrá hacer desde el listado de operinversiones
        Elimina todos los operinversion cuyo id_tipooperacion=10 (destino) cuyo comentario tengo "idorigen|"
        Se comprobará antes de eliminar que el id_inversiondestino del comentario coincide con los que quiero eliminar
        Elimina el id_operinversionorigen"""        
#        try:
        (id_inversiondestino, id_opercuentacomision)=operinversionorigen.comentario.split("|")
        origen=operinversionorigen.investment
        destino=self.find_by_id(int(id_inversiondestino))
        cur=self.mem.con.cursor()
#        print (cur.mogrify("delete from operinversiones where id_tiposoperaciones=10 and id_inversiones=%s and comentario=%s", (id_inversiondestino, str(operinversionorigen.id))))

        cur.execute("delete from operinversiones where id_tiposoperaciones=10 and id_inversiones=%s and comentario=%s", (destino.id, str(operinversionorigen.id)))
        cur.execute("delete from operinversiones where id_operinversiones=%s", (operinversionorigen.id, ))
        if id_opercuentacomision!="None":
            cur.execute("delete from opercuentas where id_opercuentas=%s", (int(id_opercuentacomision), ))
            
        self.mem.con.commit()
        origen.get_operinversiones()
        destino.get_operinversiones()
        cur.close()
        return True

    def order_by_percentage_daily(self):
        """Orders the Set using self.arr"""
        try:
            self.arr=sorted(self.arr, key=lambda inv: inv.product.result.basic.tpc_diario(),  reverse=True) 
            return True
        except:
            return False
    def order_by_selling_expiration(self):
        """Orders the Set using self.arr"""
        try:
            self.arr=sorted(self.arr, key=lambda inv: inv.selling_expiration,  reverse=False) 
            return True
        except:
            return False


    def order_by_percentage_last_operation(self):
        """Orders the Set using self.arr"""
        try:
            self.arr=sorted(self.arr, key=lambda inv: inv.op_actual.last().tpc_total(inv.product.result.basic.last, type=3),  reverse=True)
            return True
        except:
            return False
            
    def order_by_datetime_last_operation(self):
        """Orders the Set using self.arr"""
        try:
            self.arr=sorted(self.arr, key=lambda inv: inv.op_actual.last().datetime,  reverse=False) 
            return True
        except:
            return False


    def order_by_percentage_sellingpoint(self):
        """Orders the Set using self.arr"""
        try:
            self.arr=sorted(self.arr, key=lambda inv: inv.percentage_to_selling_point(),  reverse=False)##, -inv.op_actual.tpc_total(inv.product.result.basic.last, type=3)),  reverse=False) #Ordenado por dos criterios
            return True
        except:
            return False
            
    def order_by_percentage_invested(self):
        """Orders the Set using self.arr"""
            
        try:
            self.arr=sorted(self.arr, key=lambda inv: inv.op_actual.tpc_total(inv.product.result.basic.last, type=3),  reverse=True) 
            return True
        except:
            return False
            
    def order_by_datetime(self):
        """Orders the Set using self.arr"""
        try:
            self.arr=sorted(self.arr, key=lambda c: c.product.result.basic.last.datetime,  reverse=False)  
            return True
        except:
            return False
            
    def order_by_dividend(self):
        """Orders the Set using self.arr"""
        try:
            self.arr=sorted(self.arr, key=lambda inv: inv.product.estimations_dps.currentYear().percentage(),  reverse=True) 
            return True
        except:
            return False
            
    def order_by_balance(self, fecha=None,  type=3):
        """Orders the Set using self.arr"""
        try:
            self.arr=sorted(self.arr, key=lambda inv: inv.balance(fecha, type),  reverse=True) 
            return True
        except:
            logging.error("InvestmentManager can't order by balance")
            return False
        
## Class to manage products
class ProductManager(ObjectManager_With_IdName_Selectable):
    def __init__(self, mem):
        ObjectManager_With_IdName_Selectable.__init__(self)
        self.setSelectionMode(ManagerSelectionMode.List)
        self.mem=mem

    def find_by_isin(self, isin):
        if isin==None:
            return None
        for p in self.arr:
            if p.isin==None:
                continue
            if p.isin.upper()==isin.upper():
                return p
        return None                
        
    @deprecated
    def load_from_inversiones_query(self, sql, progress=True):
        """sql es una query sobre la tabla inversiones"""
        cur=self.mem.con.cursor()
        cur.execute(sql)#"Select distinct(products_id) from inversiones"
        ##Conviert cur a lista separada comas
        lista=""
        for row in cur:
            lista=lista+ str(row['products_id']) + ", "
        lista=lista[:-2]
        cur.close()
        
        ##Carga los products
        if len(lista)>0:
            self.load_from_db("select * from products where id in ("+lista+")", progress )

    def load_from_db(self, sql,  progress=False):
        """sql es una query sobre la tabla inversiones
        Carga estimations_dbs, y basic
        """
        self.clean()
        cur=self.mem.con.cursor()
        cur.execute(sql)#"select * from products where id in ("+lista+")" 
        if progress==True:
            pd= QProgressDialog(QApplication.translate("Core","Loading {0} products from database").format(cur.rowcount),None, 0,cur.rowcount)
            pd.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
            pd.setModal(True)
            pd.setWindowTitle(QApplication.translate("Core","Loading products..."))
            pd.forceShow()
        for rowms in cur:
            if progress==True:
                pd.setValue(cur.rownumber)
                pd.update()
                QApplication.processEvents()
                
            inv=Product(self.mem).init__db_row(rowms)
            self.append(inv)
        cur.close()
        

    ## Passes product.needStatus method to all products in arr
    ## @param needstatus Status needed
    ## @param progress Boolean. If true shows a progress bar
    def needStatus(self, needstatus,  progress=False):
        if progress==True:
            pd= QProgressDialog(QApplication.translate("Core","Loading additional data to {0} products from database").format(self.length()),None, 0,self.length())
            pd.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
            pd.setModal(True)
            pd.setWindowTitle(QApplication.translate("Core","Loading products..."))
            pd.forceShow()
        for i, product in enumerate(self.arr):
            if progress==True:
                pd.setValue(i)
                pd.update()
                QApplication.processEvents()
            product.needStatus(needstatus)

    def order_by_datetime(self):
        """Orders the Set using self.arr"""
        try:
            self.arr=sorted(self.arr, key=lambda c: c.result.basic.last.datetime,  reverse=False)  
            return True
        except:
            return False
        
    def order_by_dividend(self):
        """Return a boolean if the sort can be done"""
        try:
            self.arr=sorted(self.arr, key=lambda p: p.estimations_dps.currentYear().percentage(),  reverse=True) 
            return True
        except:
            return False
        
    def order_by_daily_tpc(self):
        """Return a boolean if the sort can be done"""
        try:
            self.arr=sorted(self.arr, key=lambda p: p.result.basic.tpc_diario(),  reverse=True) 
            return True
        except:
            return False
                
    def order_by_annual_tpc(self):
        """Return a boolean if the sort can be done"""
        try:
            self.arr=sorted(self.arr, key=lambda p: p.result.basic.tpc_anual(),  reverse=True) 
            return True
        except:
            return False
            
    ## Fills a qcombobox with product nume in upper case
    ## @param combo QComboBox to fill
    ## @param selected Product object to select in the QComboBox
    def qcombobox_not_obsolete(self, combo,  selected=None):
        self.order_by_name()
        combo.clear()
        for a in self.arr:
            if a.obsolete==False:
                combo.addItem(a.name.upper(), a.id)

        if selected!=None:
            combo.setCurrentIndex(combo.findData(selected.id))

    ## Returns a ProductManager with all products with the type passed as parameter.
    ## @param type ProductType object
    ## @return ProductManager
    def ProductManager_with_same_type(self, type):
        result=ProductManager(self.mem)
        for a in self.arr:
            if a.type.id==type.id:
                result.append(a)
        return result

    ## Generate a new ProductManager object finding ids of parameter array in self.arr
    ## @param arrInt Array of integers to seach in self.arr
    ## @return ProductManager with the products matchind ids in arrInt.
    def ProductManager_with_id_in_list(self, arrInt):
        result=ProductManager(self.mem)
        for i, id in enumerate(arrInt):
            selected=self.mem.data.products.find_by_id(id)
            if selected!=None:
                result.append(selected)
        return result
        

    ## Generate a new ProductManager object with products that contains parameter string
    ## @param s String to seach
    ## @return ProductManager that is a subset of this class
    def ProductManager_contains_string(self, s):
        def find_attribute(att, s):
            if att==None:
                return False
            if att.upper().find(s)!=-1:
                return True
            return False
        # #############################################
        s=s.upper()
        result=ProductManager(self.mem)
        for o in self.arr:
            if find_attribute(o.name, s) or find_attribute(o.isin, s) or any(find_attribute(ticker, s) for ticker in o.tickers) or find_attribute(o.comment, s):
                result.append(o)
        return result
        
    ## Removes a product and return a boolean. NO HACE COMMIT
    def remove(self, o):
        if o.remove():
            ObjectManager_With_Id_Selectable.remove(self, o)
            return True
        return False
        
    ## Function that store products in a libreoffice ods file
    def save_to_ods(self, filename):
        products=ProductManager(self.mem)
        products.load_from_db("select * from products order by id")
        ods=ODS_Write(filename)
        s1=ods.createSheet("Products")
        s1.add("A1", [['ID','NAME',  'ISIN',  'STOCKMARKET',  'CURRENCY',  'TYPE	',  'AGRUPATIONS',  'WEB', 'ADDRESS', 'PHONE', 'MAIL', 'PERCENTAGE', 'PCI', 'LEVERAGED', 'COMMENT', 'OBSOLETE', 'TYAHOO', 'TMORNINGSTAR', 'TGOOGLE', 'TQUEFONDOS']], "OrangeCenter")
        for row, p in enumerate(products.arr):
            print(p.name)
            s1.add(Coord("A2").addRow(row), [[p.id, p.name, p.isin, p.stockmarket.name, p.currency.id, p.type.name, p.agrupations.dbstring(), p.web, p.address, p.phone, p.mail, p.percentage, p.mode.id, p.leveraged.name, p.comment, str(p.obsolete), p.tickers[0], p.tickers[1], p.tickers[2], p.tickers[3] ]])
        ods.save()

    ## Function that downloads products.xlsx from github repository and compares sheet data with database products.arr
    ## If detects modifications or new products updates database.
    def update_from_internet(self):
        def product_xlsx(row):
            try:
                p=Product(self.mem)
                tickers=[None]*4
                for cell in row:
                    if cell.column=="A":
                        p.id=cell.value
                    elif cell.column=="B":
                        p.name=cell.value
                    elif cell.column=="C":
                        p.isin=cell.value
                    elif cell.column=="D":
                        p.stockmarket=self.mem.stockmarkets.find_by_name(cell.value)
                        if p.stockmarket==None:
                            raise
                    elif cell.column=="E":
                        p.currency=self.mem.currencies.find_by_id(cell.value)
                        if p.currency==None:
                            raise
                    elif cell.column=="F":
                        p.type=self.mem.types.find_by_name(cell.value)
                        if p.type==None:
                            raise
                    elif cell.column=="G":
                        p.agrupations=self.mem.agrupations.clone_from_dbstring(cell.value)
                        if p.agrupations==None:
                            raise
                    elif cell.column=="H":
                        p.web=cell.value
                    elif cell.column=="I":
                        p.address=cell.value
                    elif cell.column=="J":
                        p.phone=cell.value
                    elif cell.column=="K":
                        p.mail=cell.value
                    elif cell.column=="L":
                        p.percentage=cell.value
                    elif cell.column=="M":
                        p.mode=self.mem.investmentsmodes.find_by_id(cell.value)
                        if p.mode==None:
                            raise
                    elif cell.column=="N":
                        p.leveraged=self.mem.leverages.find_by_name(cell.value)
                        if p.leveraged==None:
                            raise
                    elif cell.column=="O":
                        p.comment=cell.value
                    elif cell.column=="P":
                        p.obsolete=str2bool(cell.value)
                    elif cell.column=="Q":
                        tickers[0]=cell.value
                    elif cell.column=="R":
                        tickers[1]=cell.value
                    elif cell.column=="S":
                        tickers[2]=cell.value
                    elif cell.column=="T":
                        tickers[3]=cell.value
                    p.tickers=tickers
                return p
            except:
                print("Error creando ProductODS con Id: {}".format(p.id))
                return None
        #Download file 
        from urllib.request import urlretrieve
        urlretrieve ("https://github.com/Turulomio/xulpymoney/blob/master/products.xlsx?raw=true", "product.xlsx")
        
        oldlanguage=self.mem.language.id
        self.mem.languages.cambiar("es")
        
        #Load database products
        products=ProductManager(self.mem)
        products.load_from_db("select * from products order by id")
        
        #Iterate ods and load in product object
        xlsx=OpenPyXL("product.xlsx","product.xlsx")  
        xlsx.setCurrentSheet(0)
        # for each row
        changed=[]
        added=[]
        for row in xlsx.ws_current.iter_rows():
            p_xlsx=product_xlsx(row)
            if p_xlsx==None:
                continue

            p_db=products.find_by_id(p_xlsx.id)       
       
            if p_db==None:
                added.append(p_xlsx)
            elif (  
                        p_db.id!=p_xlsx.id or
                        p_db.name!=p_xlsx.name or
                        p_db.isin!=p_xlsx.isin or
                        p_db.stockmarket.id!=p_xlsx.stockmarket.id or
                        p_db.currency.id!=p_xlsx.currency.id or
                        p_db.type.id!=p_xlsx.type.id or
                        p_db.agrupations.dbstring()!=p_xlsx.agrupations.dbstring() or 
                        p_db.web!=p_xlsx.web or
                        p_db.address!=p_xlsx.address or
                        p_db.phone!=p_xlsx.phone or
                        p_db.mail!=p_xlsx.mail or
                        p_db.percentage!=p_xlsx.percentage or
                        p_db.mode.id!=p_xlsx.mode.id or
                        p_db.leveraged.id!=p_xlsx.leveraged.id or
                        p_db.comment!=p_xlsx.comment or 
                        p_db.obsolete!=p_xlsx.obsolete or
                        p_db.tickers[0]!=p_xlsx.tickers[0] or
                        p_db.tickers[1]!=p_xlsx.tickers[1] or
                        p_db.tickers[2]!=p_xlsx.tickers[2] or
                        p_db.tickers[3]!=p_xlsx.tickers[3]
                    ):
                changed.append(p_xlsx)

        #Sumary
        print("{} Products changed".format(len(changed)))
        for p in changed:
            print("  +", p,  p.currency.id ,  p.type.name, p.isin, p.agrupations.dbstring(), p.percentage, p.mode.name, p.leveraged.name,  p.obsolete, p.tickers)
            p.save()
        print("{} Products added".format(len(added)))
        for p in added:
            print("  +", p,  p.currency.id ,  p.type.name, p.isin, p.agrupations.dbstring(), p.percentage, p.mode.name, p.leveraged.name,  p.obsolete, p.tickers)
            ##Como tiene p.id del xlsx,save haría un update, hago un insert mínimo y luego vuelvo a grabar para que haga update
            cur=self.mem.con.cursor()
            cur.execute("insert into products (id,stockmarkets_id) values (%s,%s)",  (p.id, 1))
            cur.close()
            p.save()
        self.mem.con.commit()
        self.mem.languages.cambiar(oldlanguage)
        os.remove("product.xlsx")
        self.mem.data.load()

    def list_ISIN_XULPYMONEY(self):
        """Returns a list with all products with 3 appends --ISIN_XULPYMONEY ISIN, ID"""
        suf=[]
        for p in self.arr:
            if len(p.isin)>5:
                suf.append("--ISIN_XULPYMONEY")
                suf.append(p.isin)
                suf.append(str(p.id))
        return suf

    ## Move data from product_from to product_to, changing data with the id to the new product id
    ## It will not remove origin product but it will be empty after this move, so if it's a user product could be removed manually.
    ## @param product_from. Must be a user product (id<0). 
    ## @param product_to
    def move_data_between_products(self,  product_from,  product_to):
        cur=self.mem.con.cursor()
        cur.execute("update quotes set id=%s where id=%s",(product_to.id,product_from.id))
        cur.execute("update dps set id=%s where id=%s",(product_to.id,product_from.id))        
        cur.execute("update estimations_dps set id=%s where id=%s",(product_to.id,product_from.id))        
        cur.execute("update estimations_eps set id=%s where id=%s",(product_to.id,product_from.id))      
        cur.execute("update splits set products_id=%s where products_id=%s",(product_to.id,product_from.id))
        cur.execute("update opportunities set products_id=%s where products_id=%s",(product_to.id,product_from.id))
        cur.execute("update inversiones set products_id=%s where products_id=%s",(product_to.id,product_from.id))
        cur.close()

    def myqtablewidget(self, table):
        tachado = QFont()
        tachado.setStrikeOut(True)        #Fuente tachada
        transfer=QIcon(":/xulpymoney/transfer.png")
        table.setColumnCount(8)
        table.setHorizontalHeaderItem(0, QTableWidgetItem(QApplication.translate("Core","Id")))
        table.setHorizontalHeaderItem(1, QTableWidgetItem(QApplication.translate("Core","Product")))
        table.setHorizontalHeaderItem(2, QTableWidgetItem(QApplication.translate("Core","ISIN")))
        table.setHorizontalHeaderItem(3, QTableWidgetItem(QApplication.translate("Core","Last update")))
        table.setHorizontalHeaderItem(4, QTableWidgetItem(QApplication.translate("Core","Price")))
        table.setHorizontalHeaderItem(5, QTableWidgetItem(QApplication.translate("Core","% Daily")))
        table.setHorizontalHeaderItem(6, QTableWidgetItem(QApplication.translate("Core","% Year to date")))
        table.setHorizontalHeaderItem(7, QTableWidgetItem(QApplication.translate("Core","% Dividend")))
   
        table.applySettings()
        table.clearSelection()    
        table.setFocus()
        table.horizontalHeader().setStretchLastSection(False)   
        table.clearContents()
        table.setRowCount(self.length())
        for i, p in enumerate(self.arr):
            table.setItem(i, 0, QTableWidgetItem(str(p.id)))
            table.setItem(i, 1, QTableWidgetItem(p.name.upper()))
            table.item(i, 1).setIcon(p.stockmarket.country.qicon())
            table.setItem(i, 2, QTableWidgetItem(p.isin))   
            table.setItem(i, 3, qdatetime(p.result.basic.last.datetime, self.mem.localzone))
            table.setItem(i, 4, p.currency.qtablewidgetitem(p.result.basic.last.quote, 6 ))  

            table.setItem(i, 5, p.result.basic.tpc_diario().qtablewidgetitem())
            table.setItem(i, 6, p.result.basic.tpc_anual().qtablewidgetitem())     
            if p.estimations_dps.currentYear()==None:
                table.setItem(i, 7, Percentage().qtablewidgetitem())
                table.item(i, 7).setBackground( eQColor.Red)          
            else:
                table.setItem(i, 7, p.estimations_dps.currentYear().percentage().qtablewidgetitem())
                
            if p.has_autoupdate()==True:#Active
                table.item(i, 4).setIcon(transfer)
            if p.obsolete==True:#Obsolete
                for c in range(table.columnCount()):
                    table.item(i, c).setFont(tachado)



class ProductModesManager(ObjectManager_With_IdName_Selectable):
    """Agrupa los mode"""
    def __init__(self, mem):
        ObjectManager_With_IdName_Selectable.__init__(self)
        self.mem=mem     
    
    def load_all(self):
        self.append(ProductMode(self.mem).init__create("p",QApplication.translate("Core","Put")))
        self.append(ProductMode(self.mem).init__create("c",QApplication.translate("Core","Call")))
        self.append(ProductMode(self.mem).init__create("i",QApplication.translate("Core","Inline")))

class SimulationManager(ObjectManager_With_IdName_Selectable):
    def __init__(self, mem):
        ObjectManager_With_IdName_Selectable.__init__(self)
        self.mem=mem
            
    def delete(self, simulation):
        """Deletes from db and removes object from array.
        simulation is an object"""
        simulation.delete()
        self.remove(simulation)

    def load_from_db(self, sql,  original_db):
        cur=self.mem.con.cursor()
        cur.execute(sql)
        for row in cur:
            s=Simulation(self.mem, original_db).init__db_row(row)
            self.append(s)
        cur.close()  
        
    def myqtablewidget(self, table):
        table.setColumnCount(5)
        table.setHorizontalHeaderItem(0, QTableWidgetItem(QApplication.translate("Core", "Creation" )))
        table.setHorizontalHeaderItem(1, QTableWidgetItem(QApplication.translate("Core", "Type" )))
        table.setHorizontalHeaderItem(2, QTableWidgetItem(QApplication.translate("Core", "Database" )))
        table.setHorizontalHeaderItem(3, QTableWidgetItem(QApplication.translate("Core", "Starting" )))
        table.setHorizontalHeaderItem(4, QTableWidgetItem(QApplication.translate("Core", "Ending" )))
        table.clearContents()
        table.applySettings()
        table.setRowCount(self.length())
        for i, a in enumerate(self.arr):
            table.setItem(i, 0, qdatetime(a.creation, self.mem.localzone))
            table.setItem(i, 1, qleft(a.type.name))
            table.item(i, 1).setIcon(a.type.qicon())
            table.setItem(i, 2, qleft(a.simulated_db()))
            table.setItem(i, 3, qdatetime(a.starting, self.mem.localzone))
            table.setItem(i, 4, qdatetime(a.ending, self.mem.localzone))


class StockMarketManager(ObjectManager_With_IdName_Selectable):
    def __init__(self, mem):
        ObjectManager_With_IdName_Selectable.__init__(self)
        self.mem=mem

    ## Load in the Manager all Stockmarket objects. Originally StockMarkets was a db table with this values.
    ## @code
    ##         id | country |  starts  |              name               |  closes  |       zone       
    ##----+---------+----------+---------------------------------+----------+------------------
    ## 11 | be      | 07:00:00 | Bolsa de Bélgica                | 17:38:00 | Europe/Madrid
    ## 12 | nl      | 07:00:00 | Bolsa de Amsterdam              | 17:38:00 | Europe/Madrid
    ## 13 | ie      | 07:00:00 | Bolsa de Dublín                 | 17:38:00 | Europe/Madrid
    ## 14 | fi      | 07:00:00 | Bolsa de Helsinki               | 17:38:00 | Europe/Madrid
    ##  6 | it      | 07:00:00 | Bolsa de Milán                  | 17:38:00 | Europe/Rome
    ##  7 | jp      | 09:00:00 | Bolsa de Tokio                  | 20:00:00 | Asia/Tokyo
    ##  5 | de      | 09:00:00 | Bosa de Frankfurt               | 17:38:00 | Europe/Berlin
    ##  2 | us      | 09:30:00 | Bolsa de New York               | 16:38:00 | America/New_York
    ## 10 | eu      | 07:00:00 | Bolsa Europea                   | 17:38:00 | Europe/Madrid
    ##  9 | pt      | 07:00:00 | Bolsa de Lisboa                 | 17:38:00 | Europe/Lisbon
    ##  4 | en      | 07:00:00 | Bolsa de Londres                | 17:38:00 | Europe/London
    ##  8 | cn      | 00:00:00 | Bolsa de Hong Kong              | 20:00:00 | Asia/Hong_Kong
    ##  1 | es      | 09:00:00 | Bolsa de Madrid                 | 17:38:00 | Europe/Madrid
    ##  3 | fr      | 09:00:00 | Bolsa de París                  | 17:38:00 | Europe/Paris
    ## 15 | earth   | 09:00:00 | No cotiza en mercados oficiales | 17:38:00 | Europe/Madrid
    ## @endcode
    def load_all(self):
        self.append(StockMarket(self.mem).init__create( 1, "Bolsa de Madrid", "es", datetime.time(9, 0), datetime.time(17, 38), "Europe/Madrid"))
        self.append(StockMarket(self.mem).init__create( 11, "Bolsa de Bélgica", "be", datetime.time(9, 0), datetime.time(17, 38), "Europe/Brussels"))
        self.append(StockMarket(self.mem).init__create( 12, "Bolsa de Amsterdam", "nl", datetime.time(9, 0), datetime.time(17, 38), "Europe/Amsterdam"))
        self.append(StockMarket(self.mem).init__create( 13, "Bolsa de Dublín", "ie", datetime.time(8, 0), datetime.time(16, 38), "Europe/Dublin"))
        self.append(StockMarket(self.mem).init__create( 14, "Bolsa de Helsinki", "fi", datetime.time(9, 0), datetime.time(18, 38), "Europe/Helsinki"))
        self.append(StockMarket(self.mem).init__create( 6, "Bolsa de Milán", "it", datetime.time(9, 0), datetime.time(17, 38), "Europe/Rome"))
        self.append(StockMarket(self.mem).init__create( 7, "Bolsa de Tokio", "jp", datetime.time(9, 0), datetime.time(15, 8), "Asia/Tokyo"))
        self.append(StockMarket(self.mem).init__create( 5, "Bolsa de Frankfurt", "de", datetime.time(9, 0), datetime.time(17, 38), "Europe/Berlin"))
        self.append(StockMarket(self.mem).init__create( 2, "NYSE Stock Exchange", "us", datetime.time(9, 30), datetime.time(16, 38), "America/New_York"))
        self.append(StockMarket(self.mem).init__create( 10, "Bolsa Europea", "eu", datetime.time(9, 0), datetime.time(17, 38), "Europe/Brussels"))
        self.append(StockMarket(self.mem).init__create( 9, "Bolsa de Lisboa", "pt", datetime.time(9, 0), datetime.time(17, 38), "Europe/Lisbon"))
        self.append(StockMarket(self.mem).init__create( 4, "Bolsa de Londres", "en", datetime.time(8, 0), datetime.time(16, 38), "Europe/London"))
        self.append(StockMarket(self.mem).init__create( 8, "Bolsa de Hong Kong", "cn", datetime.time(9, 30), datetime.time(16, 8), "Asia/Hong_Kong"))
        self.append(StockMarket(self.mem).init__create( 3, "Bolsa de Paris", "fr", datetime.time(9, 0), datetime.time(17, 38), "Europe/Paris"))
        self.append(StockMarket(self.mem).init__create( 15, "No cotiza en mercados oficiales", "earth", datetime.time(9, 0), datetime.time(17, 38), "Europe/Madrid"))
        self.append(StockMarket(self.mem).init__create( 16, "AMEX Stock Exchange", "us", datetime.time(9, 30), datetime.time(16, 38), "America/New_York"))
        self.append(StockMarket(self.mem).init__create( 17, "Nasdaq Stock Exchange", "us", datetime.time(9, 30), datetime.time(16, 38), "America/New_York"))

class ConceptManager(ObjectManager_With_IdName_Selectable):
    def __init__(self, mem):
        ObjectManager_With_IdName_Selectable.__init__(self)
        self.mem=mem 
                 
        
    def load_from_db(self):
        cur=self.mem.con.cursor()
        cur.execute("Select * from conceptos")
        for row in cur:
            self.append(Concept(self.mem, row, self.mem.tiposoperaciones.find_by_id(row['id_tiposoperaciones'])))
        cur.close()
        self.order_by_name()
                        
    def load_opercuentas_qcombobox(self, combo):
        """Carga conceptos operaciones 1,2,3, menos dividends y renta fija, no pueden ser editados, luego no se necesitan"""
        for c in self.arr:
            if c.tipooperacion.id in (1, 2, 3):
                if c.id not in (39, 50, 62, 63, 65, 66):
                    combo.addItem("{0} -- {1}".format(  c.name,  c.tipooperacion.name),  c.id  )

    def load_dividend_qcombobox(self, combo,  select=None):
        """Select es un class Concept"""
        for n in (39, 50,  62):
            c=self.find_by_id(n)
            combo.addItem("{0} -- {1}".format(  c.name,  c.tipooperacion.name),  c.id   )
        if select!=None:
            combo.setCurrentIndex(combo.findData(select.id))

    def load_bonds_qcombobox(self, combo,  select=None):
        """Carga conceptos operaciones 1,2,3"""
        for n in (50, 63, 65, 66):
            c=self.find_by_id(n)
            combo.addItem("{0} -- {1}".format(  c.name,  c.tipooperacion.name),  c.id )
        if select!=None:
            combo.setCurrentIndex(combo.findData(select.id))

    def considered_dividends_in_totals(self):
        """El 63 es pago de cupon corrido y no es considerado dividend  a efectos de totales, sino gasto."""
        return[39, 50, 62, 65, 66]


    def clone_x_tipooperacion(self, id_tiposoperaciones):
        """SSe usa clone y no init ya que ya están cargados en MEM"""
        resultado=ConceptManager(self.mem)
        for c in self.arr:
            if c.tipooperacion.id==id_tiposoperaciones:
                resultado.append(c)
        return resultado
        
    def clone_editables(self):
        """SSe usa clone y no init ya que ya están cargados en MEM"""
        resultado=ConceptManager(self.mem)
        for c in self.arr:
            if c.editable==True:
                resultado.append(c)
        return resultado
        
    def percentage_monthly(self, year, month):
        """ Generates an arr with:
        1) Concept:
        2) Monthly expense
        3) Percentage expenses of all conceptos this month
        4) Monthly average from first operation
        
        Returns three fields:
        1) dictionary arr, whith above values, sort by concepto.name
        2) total expenses of all concepts
        3) total average expenses of all conceptos
        """
        ##Fills column 0 and 1, 3 and gets totalexpenses
        arr=[]
        totalexpenses=Decimal(0)
        totalmedia_mensual=Decimal(0)
        for v in self.arr:
            thismonth=v.mensual(year, month)
            if thismonth==Decimal(0):
                continue
            totalexpenses=totalexpenses+thismonth
            media_mensual=v.media_mensual()
            totalmedia_mensual=totalmedia_mensual+media_mensual
            arr.append([v, thismonth, None,  media_mensual])
        
        ##Fills column 2 and calculates percentage
        for  v in arr:
            if totalexpenses==Decimal(0):
                v[2]=Decimal(0)
            else:
                v[2]=Decimal(100)*v[1]/totalexpenses
        
        arr=sorted(arr, key=lambda o:o[1])
        return (arr, totalexpenses,  totalmedia_mensual)



class CountryManager(ObjectManager_With_IdName_Selectable):
    def __init__(self, mem):
        ObjectManager_With_IdName_Selectable.__init__(self)
        self.mem=mem   
        
    def load_all(self):
        self.append(Country("es",QApplication.translate("Core","Spain")))
        self.append(Country("be",QApplication.translate("Core","Belgium")))
        self.append(Country("cn",QApplication.translate("Core","China")))
        self.append(Country("de",QApplication.translate("Core","Germany")))
        self.append(Country("earth",QApplication.translate("Core","Earth")))
        self.append(Country("en",QApplication.translate("Core","United Kingdom")))
        self.append(Country("eu",QApplication.translate("Core","Europe")))
        self.append(Country("fi",QApplication.translate("Core","Finland")))
        self.append(Country("fr",QApplication.translate("Core","France")))
        self.append(Country("ie",QApplication.translate("Core","Ireland")))
        self.append(Country("it",QApplication.translate("Core","Italy")))
        self.append(Country("jp",QApplication.translate("Core","Japan")))
        self.append(Country("nl",QApplication.translate("Core","Netherlands")))
        self.append(Country("pt",QApplication.translate("Core","Portugal")))
        self.append(Country("us",QApplication.translate("Core","United States of America")))
        self.append(Country("ro",QApplication.translate("Core","Romanian")))
        self.append(Country("ru",QApplication.translate("Core","Rusia")))
        self.order_by_name()

    def qcombobox(self, combo,  country=None):
        """Función que carga en un combo pasado como parámetro y con un AccountManager pasado como parametro
        Se ordena por nombre y se se pasa el tercer parametro que es un objeto Account lo selecciona""" 
        for cu in self.arr:
            combo.addItem(cu.qicon(), cu.name, cu.id)

        if country!=None:
                combo.setCurrentIndex(combo.findData(country.id))

    def qcombobox_translation(self, combo,  country=None):
        """Función que carga en un combo pasado como parámetro con los pa´ises que tienen traducción""" 
        for cu in [self.find_by_id("es"),self.find_by_id("fr"),self.find_by_id("ro"),self.find_by_id("ru"),self.find_by_id("en") ]:
            combo.addItem(cu.qicon(), cu.name, cu.id)

        if country!=None:
                combo.setCurrentIndex(combo.findData(country.id))

class AccountManager(ObjectManager_With_IdName_Selectable):   
    def __init__(self, mem,  setebs):
        ObjectManager_With_IdName_Selectable.__init__(self)
        self.mem=mem   
        self.ebs=setebs

    def load_from_db(self, sql):
        cur=self.mem.con.cursor()
        cur.execute(sql)#"Select * from cuentas"
        for row in cur:
            c=Account(self.mem, row, self.ebs.find_by_id(row['id_entidadesbancarias']))
            c.balance()
            self.append(c)
        cur.close()
        
    def balance(self, date=None):
        """Give the sum of all accounts balances in self.arr"""
        res=Money(self.mem, 0, self.mem.localcurrency)
        for ac in self.arr:
            res=res+ac.balance(date,  type=3)
        return res


class Report:
    """Class to make studiies and reports"""
    def __init__(self, mem):
        self.mem=mem
        
    def ibex35_tpc_down_and_up(self, tpc):
        id_product=79329
        ibex=Product(self.mem).init__db(id_product)
        ibex.result=QuotesResult(self.mem, ibex)
        ibex.needStatus(2)
        bajan=0
        subenfinal=0
        for ohcl in ibex.result.ohclDaily.arr:
            if ohcl.low<=ohcl.open*Decimal(1-tpc/100):
                bajan=bajan+1
                if ohcl.close>=ohcl.open:
                    subenfinal=subenfinal+1
        print("""
IBEX (Informe de d´ias que baja un {}% y luego sube
    Numero registros: {}
    N´umero bajan: {}
    N´umero bajan y suben al final: {}
    % Exito= {}
""".format(tpc, ibex.result.ohclDaily.length(), bajan, subenfinal, subenfinal/bajan*100))
        

class ReinvestModel:
    def __init__(self,  mem, amounts,  product, pricepercentage,  gainspercentage):
        """
            amounts is an array with all the amounts to invest
            both percentages are Percentage objetcs
        """
        self.mem=mem
        self.amounts=amounts
        self.product=product
        self.pricepercentage=pricepercentage
        self.gainspercentage=gainspercentage
        
        self.investments=[]
        for i in range(self.length()):
            bank=Bank(self.mem).init__create("Reinvest model bank", True, -1)
            account=Account(self.mem, "Reinvest model account",  bank, True, "", self.mem.localcurrency, -1)
            r=Investment(self.mem).init__create(QApplication.translate("Core", "Reinvest model of {}".format(self.product.name)), None, account, self.product, None, True, -1)    
            r.merge=1
            r.op=InvestmentOperationHomogeneusManager(self.mem, r)
            lastprice=self.product.result.basic.last.quote
            for amount in self.amounts[0:i+1]: #Recorre las amounts del array        
                r.op.append(InvestmentOperation(self.mem).init__create(self.mem.tiposoperaciones.find_by_id(4), self.mem.localzone.now(), r,  int(amount/lastprice), Decimal(0), Decimal(0),  lastprice,  None, False, 1, -1))
                lastprice=lastprice*(1-pricepercentage.value)
            r.op.order_by_datetime()
            (r.op_actual,  r.op_historica)=r.op.calcular()           
            self.investments.append(r)
        
    
    def length(self):
        return len(self.amounts)
        
    def print(self):
        """
            Prints a console report
        """
        result=[]
        for i, inv in enumerate(self.investments):
            print("Reinvestment {} of {}".format(i, inv.name))
            print("  + Invested amount: {}".format(inv.op_actual.invertido(type=1)))
            print("  + Purchase price average  amount: {}".format(inv.op_actual.average_price(type=1)))
            print("  + Current operations:")
            for o in inv.op_actual.arr:
                print("    - {}".format(o))
            print("  + Selling price: {}".format(inv.op_actual.average_price(type=1)*(1+self.gainspercentage.value)))
            result.append(1-Percentage(self.product.result.basic.last.quote-inv.op_actual.average_price(type=1).amount, self.product.result.basic.last.quote).value)
        print("*** Purchase percentage: {} ***".format(result))
            



class AccountOperationManager(DictObjectManager_With_IdDatetime_Selectable):
    def __init__(self, mem):
        DictObjectManager_With_IdDatetime_Selectable.__init__(self)
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
                comentario=QApplication.translate("Core","Paid with {0}. {1}").format(self.mem.data.creditcards.find_by_id(row['id_tarjetas']).name, row['comentario'] )
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
        tabla.setHorizontalHeaderItem(0, QTableWidgetItem(QApplication.translate("Core","Date" )))
        if show_accounts==True:
            tabla.setHorizontalHeaderItem(diff, QTableWidgetItem(QApplication.translate("Core","Account" )))
        tabla.setHorizontalHeaderItem(1+diff, QTableWidgetItem(QApplication.translate("Core","Concept" )))
        tabla.setHorizontalHeaderItem(2+diff,  QTableWidgetItem(QApplication.translate("Core","Amount" )))
        tabla.setHorizontalHeaderItem(3+diff, QTableWidgetItem(QApplication.translate("Core","Balance" )))
        tabla.setHorizontalHeaderItem(4+diff, QTableWidgetItem(QApplication.translate("Core","Comment" )))
        tabla.setHorizontalHeaderItem(5+diff, QTableWidgetItem("Id"))
        ##DATA 
        tabla.clearContents()
        tabla.applySettings()
        tabla.setRowCount(self.length())
        tabla.setColumnHidden(5+diff, True)
        balance=0
        for rownumber, a in enumerate(self.values_order_by_datetime()):
            balance=balance+a.importe
            tabla.setItem(rownumber, 0, qdatetime(a.datetime, self.mem.localzone))
            if show_accounts==True:
                tabla.setItem(rownumber, diff, QTableWidgetItem(a.account.name))
            tabla.setItem(rownumber, 1+diff, qleft(a.concepto.name))
            tabla.setItem(rownumber, 2+diff, self.mem.localcurrency.qtablewidgetitem(a.importe))
            tabla.setItem(rownumber, 3+diff, self.mem.localcurrency.qtablewidgetitem(balance))
            tabla.setItem(rownumber, 4+diff, qleft(Comment(self.mem).setFancy(a.comentario)))
            tabla.setItem(rownumber, 5+diff, qleft(a.id))
            if self.selected.length()>0:
                if a.id==self.selected.only().id:
                    tabla.selectRow(rownumber+1)

    def myqtablewidget_lastmonthbalance(self, table,    account, lastmonthbalance):
        table.applySettings()
        table.clearContents()
        table.setRowCount(self.length()+1)
        table.setItem(0, 1, QTableWidgetItem(QApplication.translate("Core", "Starting month balance")))
        table.setItem(0, 3, lastmonthbalance.qtablewidgetitem())
        table.setColumnHidden(5, True)
        for i, o in enumerate(self.values_order_by_datetime()):
            importe=Money(self.mem, o.importe, account.currency)
            lastmonthbalance=lastmonthbalance+importe
            table.setItem(i+1, 0, qdatetime(o.datetime, self.mem.localzone))
            table.setItem(i+1, 1, QTableWidgetItem(o.concepto.name))
            table.setItem(i+1, 2, importe.qtablewidgetitem())
            print (o.importe,  l10nDecimal(o.importe))
            table.setItem(i+1, 3, lastmonthbalance.qtablewidgetitem())
            table.setItem(i+1, 4, QTableWidgetItem(Comment(self.mem).setFancy(o.comentario)))       
            table.setItem(i+1, 5, qleft(o.id))
            if self.selected.length()>0:
                if o.id==self.selected.only().id:
                    table.selectRow(i+1)

class CurrencyManager(ObjectManager_With_IdName_Selectable):
    def __init__(self, mem):
        ObjectManager_With_IdName_Selectable.__init__(self)
        self.mem=mem   
    
    def load_all(self):
        self.append(Currency().init__create(QApplication.translate("Core","Chinese Yoan"), "¥", 'CNY'))
        self.append(Currency().init__create(QApplication.translate("Core","Euro"), "€", "EUR"))
        self.append(Currency().init__create(QApplication.translate("Core","Pound"),"£", 'GBP'))
        self.append(Currency().init__create(QApplication.translate("Core","Japones Yen"), '¥', "JPY"))
        self.append(Currency().init__create(QApplication.translate("Core","American Dolar"), '$', 'USD'))
        self.append(Currency().init__create(QApplication.translate("Core","Units"), 'u', 'u'))

    def find_by_symbol(self, symbol,  log=False):
        """Finds by id"""
        for c in self.arr:
            if c.symbol==symbol:
                return c
        logging.error("CurrencyManager fails finding {}".format(symbol))
        return None

    def qcombobox(self, combo, selectedcurrency=None):
        """Función que carga en un combo pasado como parámetro las currencies"""
        for c in self.arr:
            combo.addItem("{0} - {1} ({2})".format(c.id, c.name, c.symbol), c.id)
        if selectedcurrency!=None:
                combo.setCurrentIndex(combo.findData(selectedcurrency.id))

class DividendHeterogeneusManager(ObjectManager_With_IdDatetime_Selectable):
    """Class that  groups dividends from a Xulpymoney Product"""
    def __init__(self, mem):
        ObjectManager_With_IdDatetime_Selectable.__init__(self)
        self.mem=mem
            
    def gross(self):
        """gross amount in self.mem.localcurrency"""
        r=Money(self.mem, 0, self.mem.localcurrency)
        for d in self.arr:
            r=r+d.gross().local()
        return r

    def load_from_db(self, sql):    
        del self.arr
        self.arr=[]
        cur=self.mem.con.cursor()
        cur.execute( sql)#"select * from dividends where id_inversiones=%s order by fecha", (self.investment.id, )
        for row in cur:
            inversion=self.mem.data.investments.find_by_id(row['id_inversiones'])
            oc=AccountOperation(self.mem, row['id_opercuentas'])
            self.arr.append(Dividend(self.mem).init__db_row(row, inversion, oc, self.mem.conceptos.find_by_id(row['id_conceptos']) ))
        cur.close()      
                
    def myqtablewidget(self, table,   show_investment=False):
        """Section es donde guardar en el config file, coincide con el nombre del formulario en el que está la table
        Devuelve sumatorios"""
        diff=0
        if show_investment==True:
            diff=1
        table.setColumnCount(7+diff)
        table.setHorizontalHeaderItem(0, QTableWidgetItem(QApplication.translate("Core", "Date" )))
        table.setHorizontalHeaderItem(diff, QTableWidgetItem(QApplication.translate("Core", "Product" )))
        table.setHorizontalHeaderItem(diff+1, QTableWidgetItem(QApplication.translate("Core", "Concept" )))
        table.setHorizontalHeaderItem(diff+2, QTableWidgetItem(QApplication.translate("Core", "Gross" )))
        table.setHorizontalHeaderItem(diff+3, QTableWidgetItem(QApplication.translate("Core", "Withholding" )))
        table.setHorizontalHeaderItem(diff+4, QTableWidgetItem(QApplication.translate("Core", "Comission" )))
        table.setHorizontalHeaderItem(diff+5, QTableWidgetItem(QApplication.translate("Core", "Net" )))
        table.setHorizontalHeaderItem(diff+6, QTableWidgetItem(QApplication.translate("Core", "DPS" )))
        #DATA  
        table.applySettings()
        table.clearContents()


        table.setRowCount(len(self.arr)+1)
        sumneto=0
        sumbruto=0
        sumretencion=0
        sumcomision=0
        for i, d in enumerate(self.arr):
            sumneto=sumneto+d.neto
            sumbruto=sumbruto+d.bruto
            sumretencion=sumretencion+d.retencion
            sumcomision=sumcomision+d.comision
            table.setItem(i, 0, qdatetime(d.datetime, self.mem.localzone))
            if show_investment==True:
                table.setItem(i, diff, qleft(d.investment.name))
            table.setItem(i, diff+1, qleft(d.opercuenta.concepto.name))
            table.setItem(i, diff+2, self.mem.localcurrency.qtablewidgetitem(d.bruto))
            table.setItem(i, diff+3, self.mem.localcurrency.qtablewidgetitem(d.retencion))
            table.setItem(i, diff+4, self.mem.localcurrency.qtablewidgetitem(d.comision))
            table.setItem(i, diff+5, self.mem.localcurrency.qtablewidgetitem(d.neto))
            table.setItem(i, diff+6, self.mem.localcurrency.qtablewidgetitem(d.dpa))
        table.setItem(len(self.arr), diff+1, qleft(QApplication.translate("core","TOTAL")))
        table.setItem(len(self.arr), diff+2, self.mem.localcurrency.qtablewidgetitem(sumbruto))
        table.setItem(len(self.arr), diff+3, self.mem.localcurrency.qtablewidgetitem(sumretencion))
        table.setItem(len(self.arr), diff+4, self.mem.localcurrency.qtablewidgetitem(sumcomision))
        table.setItem(len(self.arr), diff+5, self.mem.localcurrency.qtablewidgetitem(sumneto))
        return (sumneto, sumbruto, sumretencion, sumcomision)

class DividendHomogeneusManager(DividendHeterogeneusManager):
    def __init__(self, mem, investment):
        DividendHeterogeneusManager.__init__(self, mem)
        self.investment=investment
        
    def gross(self, type=1):
        """gross amount"""
        r=Money(self.mem, 0, self.investment.resultsCurrency(type))
        for d in self.arr:
            r=r+d.gross(type)
        return r
    def net(self, type=1):
        r=Money(self.mem, 0, self.investment.resultsCurrency(type))
        for d in self.arr:
            r=r+d.net(type)
        return r
        
    def percentage_from_invested(self, type=1):
        return Percentage(self.gross(type), self.investment.invertido(None, type))
        
    def percentage_tae_from_invested(self, type=1):
        try:
            dias=(datetime.date.today()-self.investment.op_actual.first().datetime.date()).days+1
            return Percentage(self.percentage_from_invested(type)*365, dias )
        except:#No first
            return Percentage()
        
    def myqtablewidget(self, table, type=1):
        """Section es donde guardar en el config file, coincide con el nombre del formulario en el que está la table
        Devuelve sumatorios"""

        table.setColumnCount(7)
        table.setHorizontalHeaderItem(0, QTableWidgetItem(QApplication.translate("Core", "Date" )))
        table.setHorizontalHeaderItem(1, QTableWidgetItem(QApplication.translate("Core", "Concept" )))
        table.setHorizontalHeaderItem(2, QTableWidgetItem(QApplication.translate("Core", "Gross" )))
        table.setHorizontalHeaderItem(3, QTableWidgetItem(QApplication.translate("Core", "Withholding" )))
        table.setHorizontalHeaderItem(4, QTableWidgetItem(QApplication.translate("Core", "Comission" )))
        table.setHorizontalHeaderItem(5, QTableWidgetItem(QApplication.translate("Core", "Net" )))
        table.setHorizontalHeaderItem(6, QTableWidgetItem(QApplication.translate("Core", "DPS" )))
        #DATA  
        table.applySettings()
        table.clearContents()
        
        currency=self.investment.resultsCurrency(type)

        table.setRowCount(self.length()+1)
        sumneto=Money(self.mem, 0, currency)
        sumbruto=Money(self.mem, 0, currency)
        sumretencion=Money(self.mem, 0, currency)
        sumcomision=Money(self.mem, 0, currency)
        for i, d in enumerate(self.arr):
            sumneto=sumneto+d.net(type)
            sumbruto=sumbruto+d.gross(type)
            sumretencion=sumretencion+d.retention(type)
            sumcomision=sumcomision+d.comission(type)
            table.setItem(i, 0, qdatetime(d.datetime, self.mem.localzone))
            table.setItem(i, 1, qleft(d.opercuenta.concepto.name))
            table.setItem(i, 2, d.gross(type).qtablewidgetitem())
            table.setItem(i, 3, d.retention(type).qtablewidgetitem())
            table.setItem(i, 4, d.comission(type).qtablewidgetitem())
            table.setItem(i, 5, d.net(type).qtablewidgetitem())
            table.setItem(i, 6, d.dps(type).qtablewidgetitem())
        table.setItem(self.length(), 1, qleft(QApplication.translate("core","TOTAL")))
        table.setItem(self.length(), 2, sumbruto.qtablewidgetitem())
        table.setItem(self.length(), 3, sumretencion.qtablewidgetitem())
        table.setItem(self.length(), 4, sumcomision.qtablewidgetitem())
        table.setItem(self.length(), 5, sumneto.qtablewidgetitem())
        return (sumneto, sumbruto, sumretencion, sumcomision)
        
class EstimationDPSManager:
    def __init__(self, mem,  product):
        self.arr=[]
        self.mem=mem   
        self.product=product
    
    def estimacionNula(self, year):
        return EstimationDPS(self.mem).init__create(self.product, year, datetime.date.today(), "None Estimation", None, None)
    
    def load_from_db(self):
        del self.arr
        self.arr=[]
        cur=self.mem.con.cursor()
        cur.execute( "select * from estimations_dps where id=%s order by year", (self.product.id, ))
        for row in cur:
            self.arr.append(EstimationDPS(self.mem).init__from_db(self.product, row['year']))
        cur.close()            
        
    def find(self, year):
        """Como puede no haber todos los años se usa find que devuelve una estimacion nula sino existe"""
        for e in self.arr:
            if e.year==year:
                return e
        return self.estimacionNula(year)
            
    def currentYear(self):
        return self.find(datetime.date.today().year)

    def dias_sin_actualizar(self):
        """Si no hay datos devuelve 1000"""
        self.sort()
        try:
            ultima=self.arr[len(self.arr)-1].date_estimation
            return (datetime.date.today()-ultima).days
        except:
            return 1000

    def sort(self):
        self.arr=sorted(self.arr, key=lambda c: c.year,  reverse=False)         
        
    def myqtablewidget(self, table):
        """settings, must be thrown before, not in each reload"""
        self.sort()  
        table.applySettings()
        table.clearContents()
        table.setRowCount(len(self.arr))
        for i, e in enumerate(self.arr):
            table.setItem(i, 0, qcenter(str(e.year)))
            table.setItem(i, 1, self.product.currency.qtablewidgetitem(e.estimation, 6))       
            table.setItem(i, 2, e.percentage().qtablewidgetitem())
            table.setItem(i, 3, qdate(e.date_estimation))
            table.setItem(i, 4, qleft(e.source))
            table.setItem(i, 5, qbool(e.manual))

        table.setCurrentCell(len(self.arr)-1, 0)
        table.setFocus()

class EstimationEPSManager:
    def __init__(self, mem,  product):
        self.arr=[]
        self.mem=mem   
        self.product=product
    
    def estimacionNula(self, year):
        return EstimationEPS(self.mem).init__create(self.product, year, datetime.date.today(), "None Estimation", None, None)
    
    def load_from_db(self):
        del self.arr
        self.arr=[]
        cur=self.mem.con.cursor()
        cur.execute( "select * from estimations_eps where id=%s order by year", (self.product.id, ))
        for row in cur:
            self.arr.append(EstimationEPS(self.mem).init__from_db(self.product, row['year']))
        cur.close()            
        
    def find(self, year):
        """Como puede no haber todos los años se usa find que devuelve una estimacion nula sino existe"""
        for e in self.arr:
            if e.year==year:
                return e
        return self.estimacionNula(year)
            
    def currentYear(self):
        return self.find(datetime.date.today().year)

    def dias_sin_actualizar(self):
        ultima=datetime.date(1990, 1, 1)
        for k, v in self.dic.items():
            if v.date_estimation>ultima:
                ultima=v.date_estimation
        return (datetime.date.today()-ultima).days
        
        
    def sort(self):
        self.arr=sorted(self.arr, key=lambda c: c.year,  reverse=False)         
        
    def myqtablewidget(self, table):
        self.sort()     
        table.applySettings()
        table.clearContents()
        table.setRowCount(len(self.arr))
        for i, e in enumerate(self.arr):
            table.setItem(i, 0, qcenter(str(e.year)))
            table.setItem(i, 1, self.product.currency.qtablewidgetitem(e.estimation, 6))       
            table.setItem(i, 2, qright(e.PER(Quote(self.mem).init__from_query(self.product, day_end_from_date(datetime.date(e.year, 12, 31), self.product.stockmarket.zone))), 2))
            table.setItem(i, 3, qdate(e.date_estimation))
            table.setItem(i, 4, QTableWidgetItem(e.source))
            table.setItem(i, 5, qbool(e.manual)) 
        table.setCurrentCell(len(self.arr)-1, 0)
        table.setFocus()

        
class BankManager(ObjectManager_With_IdName_Selectable):
    def __init__(self, mem):
        ObjectManager_With_IdName_Selectable.__init__(self)
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


class InvestmentOperationHeterogeneusManager(ObjectManager_With_IdDatetime_Selectable):       
    """Clase es un array ordenado de objetos newInvestmentOperation"""
    def __init__(self, mem):
        ObjectManager_With_IdDatetime_Selectable.__init__(self)
        self.mem=mem
        
    def get_highest_io_id(self):
        """Get the highest IO.Id of the arr"""
        max=0
        for i in self.arr:
            if i.id>max:
                max=i.id
        return max
        
    def remove(self,  io):      
        """io is an InvestmentOPeration object
        Deletes from db and removes from array, and recalculate things"""  
        cur=self.mem.con.cursor()
        cur.execute("delete from operinversiones where id_operinversiones=%s",(io.id, ))
        cur.close()
        
        super(InvestmentOperationHeterogeneusManager, self).remove(io)
        
        (io.investment.op_actual,  io.investment.op_historica)=io.investment.op.calcular()
        io.investment.actualizar_cuentasoperaciones_asociadas()#Regenera toda la inversión.

        
    def setDistinctProducts(self):
        """Extracts distinct products in IO"""
        s=set([])
        for o in self.arr:
            s.add(o.investment.product)
        result=ProductManager(self.mem)
        result.arr=list(s)
        return result
        
    def print_list(self):
        print ("\n Imprimiendo SIO Heterogéneo",  self)
        for oia in self.arr:
            print ("  - ", oia)

    def order_by_datetime(self):       
        self.arr=sorted(self.arr, key=lambda e: e.datetime,  reverse=False) 

    def myqtablewidget(self, tabla):
        """Muestra los resultados en self.mem.localcurrency al ser heterogeneo().local()"""
        self.order_by_datetime()
        tabla.setColumnCount(10)
        tabla.setHorizontalHeaderItem(0, QTableWidgetItem(QApplication.translate("Core", "Date" )))
        tabla.setHorizontalHeaderItem(1, QTableWidgetItem(QApplication.translate("Core", "Product" )))
        tabla.setHorizontalHeaderItem(2, QTableWidgetItem(QApplication.translate("Core", "Account" )))
        tabla.setHorizontalHeaderItem(3, QTableWidgetItem(QApplication.translate("Core", "Operation type" )))
        tabla.setHorizontalHeaderItem(4, QTableWidgetItem(QApplication.translate("Core", "Shares" )))
        tabla.setHorizontalHeaderItem(5, QTableWidgetItem(QApplication.translate("Core", "Price" )))
        tabla.setHorizontalHeaderItem(6, QTableWidgetItem(QApplication.translate("Core", "Amount" )))
        tabla.setHorizontalHeaderItem(7, QTableWidgetItem(QApplication.translate("Core", "Comission" )))
        tabla.setHorizontalHeaderItem(8, QTableWidgetItem(QApplication.translate("Core", "Taxes" )))
        tabla.setHorizontalHeaderItem(9, QTableWidgetItem(QApplication.translate("Core", "Total" )))
        #DATA 
        tabla.applySettings()
        tabla.clearContents()  
        tabla.setRowCount(self.length())
        for rownumber, a in enumerate(self.arr):
            tabla.setItem(rownumber, 0, qdatetime(a.datetime, self.mem.localzone))
            if self.mem.gainsyear==True and a.less_than_a_year()==True:
                tabla.item(rownumber, 0).setIcon(QIcon(":/xulpymoney/new.png"))
        
            tabla.setItem(rownumber, 1, qleft(a.investment.name))
            tabla.setItem(rownumber, 2, qleft(a.investment.account.name))
            
            tabla.setItem(rownumber, 3, qleft(a.tipooperacion.name))
            if a.show_in_ranges==True:
                tabla.item(rownumber, 3).setIcon(QIcon(":/xulpymoney/eye.png"))
            else:
                tabla.item(rownumber, 3).setIcon(QIcon(":/xulpymoney/eye_red.png"))
            
            tabla.setItem(rownumber, 4, qright(a.shares))
            tabla.setItem(rownumber, 5, a.price().local().qtablewidgetitem())
            tabla.setItem(rownumber, 6, a.gross().local().qtablewidgetitem())
            tabla.setItem(rownumber, 7, a.comission().local().qtablewidgetitem())
            tabla.setItem(rownumber, 8, a.taxes().local().qtablewidgetitem())
            tabla.setItem(rownumber, 9, a.net().local().qtablewidgetitem())

    def find(self,  investmentoperation_id):
        """Returns an investmenoperation with the id equals to the parameter"""
        for o in self.arr:
            if o.id==investmentoperation_id:
                return o
        return None



class InvestmentOperationHomogeneusManager(InvestmentOperationHeterogeneusManager):
    def __init__(self, mem, investment):
        InvestmentOperationHeterogeneusManager.__init__(self, mem)
        self.investment=investment


    def calcular(self):
        """Realiza los cálculos y devuelve dos arrays"""
        sioh=InvestmentOperationHistoricalHomogeneusManager(self.mem, self.investment)
        sioa=InvestmentOperationCurrentHomogeneusManager(self.mem, self.investment)       
        for o in self.arr:                
            if o.shares>=0:#Compra
                sioa.arr.append(InvestmentOperationCurrent(self.mem).init__create(o, o.tipooperacion, o.datetime, o.investment, o.shares, o.impuestos, o.comision, o.valor_accion,  o.show_in_ranges, o.currency_conversion,  o.id))
            else:#Venta
                if abs(o.shares)>sioa.shares():
                    logging.critical("No puedo vender más acciones que las que tengo. EEEEEEEEEERRRRRRRRRRRROOOOORRRRR")
                    sys.exit(0)
                sioa.historizar(o, sioh)
        sioa.get_valor_benchmark(self.mem.data.benchmark)
        return (sioa, sioh)

    def print_list(self):
        print ("\n Imprimiendo SIO de",  self.investment.name)
        for oia in self.arr:
            print ("  - ", oia)
            
        
    def myqtablewidget(self, tabla, type=1):
        """Section es donde guardar en el config file, coincide con el nombre del formulario en el que está la tabla
        show_accounts, muestra el producto y la cuenta
        type muestra los money en la currency de la cuenta
        """
        
        self.order_by_datetime()
        if self.investment.hasSameAccountCurrency()==True:
            tabla.setColumnCount(8)
        else:
            tabla.setColumnCount(9)
        tabla.setHorizontalHeaderItem(0, QTableWidgetItem(QApplication.translate("Core", "Date" )))
        tabla.setHorizontalHeaderItem(1, QTableWidgetItem(QApplication.translate("Core", "Operation type" )))
        tabla.setHorizontalHeaderItem(2, QTableWidgetItem(QApplication.translate("Core", "Shares" )))
        tabla.setHorizontalHeaderItem(3, QTableWidgetItem(QApplication.translate("Core", "Price" )))
        tabla.setHorizontalHeaderItem(4, QTableWidgetItem(QApplication.translate("Core", "Gross" )))
        tabla.setHorizontalHeaderItem(5, QTableWidgetItem(QApplication.translate("Core", "Comission" )))
        tabla.setHorizontalHeaderItem(6, QTableWidgetItem(QApplication.translate("Core", "Taxes" )))
        tabla.setHorizontalHeaderItem(7, QTableWidgetItem(QApplication.translate("Core", "Total" )))
        if self.investment.hasSameAccountCurrency()==False:
            tabla.setHorizontalHeaderItem(8, QTableWidgetItem(QApplication.translate("Core", "Currency conversion" )))
        
        #DATA 
        tabla.applySettings()
        tabla.clearContents()  
        tabla.setRowCount(len(self.arr))
        
        for rownumber, a in enumerate(self.arr):
            tabla.setItem(rownumber, 0, qdatetime(a.datetime, self.mem.localzone))
            if self.mem.gainsyear==True and a.less_than_a_year()==True:
                tabla.item(rownumber, 0).setIcon(QIcon(":/xulpymoney/new.png"))
                
            tabla.setItem(rownumber, 1, QTableWidgetItem(a.tipooperacion.name))
            if a.show_in_ranges==True:
                tabla.item(rownumber, 1).setIcon(QIcon(":/xulpymoney/eye.png"))
            else:
                tabla.item(rownumber, 1).setIcon(QIcon(":/xulpymoney/eye_red.png"))
            
            tabla.setItem(rownumber, 2, qright(a.shares))
            tabla.setItem(rownumber, 3, a.price(type).qtablewidgetitem())
            tabla.setItem(rownumber, 4, a.gross(type).qtablewidgetitem())            
            tabla.setItem(rownumber, 5, a.comission(type).qtablewidgetitem())
            tabla.setItem(rownumber, 6, a.taxes(type).qtablewidgetitem())
            tabla.setItem(rownumber, 7, a.net(type).qtablewidgetitem())
            if self.investment.hasSameAccountCurrency()==False:
                tabla.setItem(rownumber, 8, qright(a.currency_conversion))

class InvestmentOperationCurrentHeterogeneusManager(ObjectManager_With_IdDatetime_Selectable):    
    """Clase es un array ordenado de objetos newInvestmentOperation"""
    def __init__(self, mem):
        ObjectManager_With_IdDatetime_Selectable.__init__(self)
        self.mem=mem
    def __repr__(self):
        try:
            inversion=self.arr[0].investment.id
        except:
            inversion= "Desconocido"
        return ("SetIOA Inv: {0}. N.Registros: {1}. N.shares: {2}. Invertido: {3}. Valor medio:{4}".format(inversion,  len(self.arr), self.shares(),  self.invertido(),  self.average_price()))
                        
    def average_age(self):
        """Average age of the current investment operations in days"""
        (sumbalance, sumbalanceage)=(Decimal(0), Decimal(0))
        for o in self.arr:
            balance=o.balance(o.investment.product.result.basic.last).convert_from_factor(o.investment.account.currency, o.currency_conversion).local()
            sumbalance=sumbalance+balance.amount
            sumbalanceage=sumbalanceage+balance.amount*o.age()
        if sumbalance!=Decimal(0):
            return round(sumbalanceage/sumbalance, 2)
        else:
            return Decimal(0)
            
    def average_price(self):
        """Calcula el precio medio de compra"""
        
        shares=Money(self.mem)
        sharesxprice=Money(self.mem)
        for o in self.arr:
            shares=shares+Money(self.mem, o.shares)
            sharesxprice=sharesxprice+Money(self.mem, o.shares*o.valor_accion)

        if shares.isZero():
            return Money(self.mem)
        return sharesxprice/shares

    def balance(self):
        """Al ser homegeneo da el resultado en Money del producto"""
        resultado=Money(self.mem, 0, self.mem.localcurrency)
        for o in self.arr:
            resultado=resultado+o.balance(o.investment.product.result.basic.last, type=3)
        return resultado        

    def shares(self):
        """Devuelve el número de acciones de la inversión actual"""
        resultado=Decimal(0)
        for o in self.arr:
            resultado=resultado+o.shares
        return resultado
            
    
    def invertido(self):
        """Al ser heterogeneo da el resultado en Money local"""
        resultado=Money(self.mem, 0, self.mem.localcurrency)
        for o in self.arr:
            resultado=resultado+o.invertido(type=3)
        return resultado
        
    def last(self):
        """Returns last current operation with valor_accion greater than 0"""
        for o in reversed(self.arr):
            if o.valor_accion==Decimal(0):#Añadidos
                continue
            return o
        return None 
    
    def less_than_a_year(self):
        for o in self.arr:
            if o.less_than_a_year()==True:
                return True
        return False
        
    def myqtablewidget(self,  tabla):
        """Parámetros
            - tabla myQTableWidget en la que rellenar los datos
            
            Al ser heterogeneo se calcula con self.mem.localcurrency
        """
        tabla.setColumnCount(12)
        tabla.setHorizontalHeaderItem(0, QTableWidgetItem(QApplication.translate("Core", "Date" )))
        tabla.setHorizontalHeaderItem(1, QTableWidgetItem(QApplication.translate("Core", "Product" )))
        tabla.setHorizontalHeaderItem(2, QTableWidgetItem(QApplication.translate("Core", "Account" )))
        tabla.setHorizontalHeaderItem(3, QTableWidgetItem(QApplication.translate("Core", "Shares" )))
        tabla.setHorizontalHeaderItem(4, QTableWidgetItem(QApplication.translate("Core", "Price" )))
        tabla.setHorizontalHeaderItem(5, QTableWidgetItem(QApplication.translate("Core", "Invested" )))
        tabla.setHorizontalHeaderItem(6, QTableWidgetItem(QApplication.translate("Core", "Current balance" )))
        tabla.setHorizontalHeaderItem(7, QTableWidgetItem(QApplication.translate("Core", "Pending" )))
        tabla.setHorizontalHeaderItem(8, QTableWidgetItem(QApplication.translate("Core", "% annual" )))
        tabla.setHorizontalHeaderItem(9, QTableWidgetItem(QApplication.translate("Core", "% APR" )))
        tabla.setHorizontalHeaderItem(10, QTableWidgetItem(QApplication.translate("Core", "% Total" )))
        tabla.setHorizontalHeaderItem(11, QTableWidgetItem(QApplication.translate("Core", "Benchmark" )))
        #DATA
        if self.length()==0:
            tabla.setRowCount(0)
            return
        type=3
            
        tabla.applySettings()
        tabla.clearContents()
        tabla.setRowCount(self.length()+1)
        for rownumber, a in enumerate(self.arr):        
            tabla.setItem(rownumber, 0, qdatetime(a.datetime, self.mem.localzone))
            if self.mem.gainsyear==True and a.less_than_a_year()==True:
                tabla.item(rownumber, 0).setIcon(QIcon(":/xulpymoney/new.png"))
            tabla.setItem(rownumber, 1, qleft(a.investment.name))
            tabla.setItem(rownumber, 2, qleft(a.investment.account.name))
            tabla.setItem(rownumber, 3, qright("{0:.6f}".format(a.shares)))
            tabla.setItem(rownumber, 4, a.price().local().qtablewidgetitem())
            tabla.setItem(rownumber, 5, a.invertido(type).qtablewidgetitem())
            tabla.setItem(rownumber, 6, a.balance(a.investment.product.result.basic.last, type).qtablewidgetitem())
            tabla.setItem(rownumber, 7, a.pendiente(a.investment.product.result.basic.last, type).qtablewidgetitem())
            tabla.setItem(rownumber, 8, a.tpc_anual(a.investment.product.result.basic.last, a.investment.product.result.basic.lastyear, type=2).qtablewidgetitem())
            tabla.setItem(rownumber, 9, a.tpc_tae(a.investment.product.result.basic.last, type=2).qtablewidgetitem())
            tabla.setItem(rownumber, 10, a.tpc_total(a.investment.product.result.basic.last, type=2).qtablewidgetitem())
            if a.referenciaindice==None:
                tabla.setItem(rownumber, 11, self.mem.data.benchmark.currency.qtablewidgetitem(None))
            else:
                tabla.setItem(rownumber, 11, self.mem.data.benchmark.currency.qtablewidgetitem(a.referenciaindice.quote))

        tabla.setItem(self.length(), 0, qleft(days2string(self.average_age())))
        tabla.setItem(self.length(), 0, QTableWidgetItem(("TOTAL")))
        tabla.setItem(self.length(), 5, self.invertido().qtablewidgetitem())
        tabla.setItem(self.length(), 6, self.balance().qtablewidgetitem())
        tabla.setItem(self.length(), 7, self.pendiente().qtablewidgetitem())
        tabla.setItem(self.length(), 8, self.tpc_tae().qtablewidgetitem())
        tabla.setItem(self.length(), 9, self.tpc_total().qtablewidgetitem())


    def pendiente(self):
        """Calcula el resultado de pendientes utilizando lastquote como el ultimo de cada operaci´on"""
        resultado=Money(self.mem, 0, self.mem.localcurrency)
        for o in self.arr:
            resultado=resultado+o.pendiente(o.investment.product.result.basic.last, type=3)
        return resultado
    

    def tpc_tae(self):
        dias=self.average_age()
        if dias==0:
            dias=1
        return Percentage(self.tpc_total()*365, dias)

    def tpc_total(self):
        """Como es heterogenous el resultado sera en local"""
        return Percentage(self.pendiente(), self.invertido())
        
    
    def get_valor_benchmark(self, indice):
        cur=self.mem.con.cursor()
        for o in self.arr:
            o.get_referencia_indice(indice)
        cur.close()

    def historizar(self, io,  sioh):
        """
        io es una Investmentoperacion de venta
        1 Pasa al set de inversion operacion historica tantas inversionoperacionesactual como acciones tenga
       la inversion operacion de venta
      2 Si no ha sido un número exacto y se ha partido la ioactual, añade la difrencia al setIOA y lo quitado a SIOH
      
        Las comisiones se cobran se evaluan (ya estan en io) para ioh cuando sale con Decimal('0'), esdecir
        cuando acaba la venta
        
        """
        self.order_by_datetime()
        
        inicio=self.shares()
        
        accionesventa=abs(io.shares)
        comisiones=Decimal('0')
        impuestos=Decimal('0')
        while accionesventa!=Decimal('0'):
            while True:###nO SE RECORRE EL ARRAY SE RECORRE Con I PORQUE HAY INSERCIONES Y BORRADOS daba problemas de no repetir al insertar
                ioa=self.arr[0]
                if ioa.shares-accionesventa>Decimal('0'):#>0Se vende todo y se crea un ioa de resto, y se historiza lo restado
                    comisiones=comisiones+io.comision+ioa.comision
                    impuestos=impuestos+io.impuestos+ioa.impuestos
                    sioh.arr.append(InvestmentOperationHistorical(self.mem).init__create(ioa, io.investment, ioa.datetime.date(), io.tipooperacion, -accionesventa, comisiones, impuestos, io.datetime.date(), ioa.valor_accion, io.valor_accion, ioa.currency_conversion, io.currency_conversion))
                    self.arr.insert(0, InvestmentOperationCurrent(self.mem).init__create(ioa, ioa.tipooperacion, ioa.datetime, ioa.investment,  ioa.shares-abs(accionesventa), 0, 0, ioa.valor_accion, ioa.show_in_ranges,  ioa.currency_conversion, ioa.id))
                    self.arr.remove(ioa)
                    accionesventa=Decimal('0')#Sale bucle
                    break
                elif ioa.shares-accionesventa<Decimal('0'):#<0 Se historiza todo y se restan acciones venta
                    comisiones=comisiones+ioa.comision
                    impuestos=impuestos+ioa.impuestos
                    sioh.arr.append(InvestmentOperationHistorical(self.mem).init__create(ioa, io.investment, ioa.datetime.date(), io.tipooperacion, -ioa.shares, Decimal('0'), Decimal('0'), io.datetime.date(), ioa.valor_accion, io.valor_accion, ioa.currency_conversion, io.currency_conversion))
                    accionesventa=accionesventa-ioa.shares                    
                    self.arr.remove(ioa)
                elif ioa.shares-accionesventa==Decimal('0'):#Se historiza todo y se restan acciones venta y se sale
                    comisiones=comisiones+io.comision+ioa.comision
                    impuestos=impuestos+io.impuestos+ioa.impuestos
                    sioh.arr.append(InvestmentOperationHistorical(self.mem).init__create(ioa, io.investment, ioa.datetime.date(),  io.tipooperacion, -ioa.shares, comisiones, impuestos, io.datetime.date(), ioa.valor_accion, io.valor_accion, ioa.currency_conversion, io.currency_conversion))
                    self.arr.remove(ioa)                    
                    accionesventa=Decimal('0')#Sale bucle                    
                    break
        if inicio-self.shares()-abs(io.shares)!=Decimal('0'):
            logging.critical ("Error en historizar. diff {}. Inicio {}. Fin {}. {}".format(inicio-self.shares()-abs(io.shares),  inicio,   self.shares(), io))
                
        
    def print_list(self):
        self.order_by_datetime()
        print ("\n Imprimiendo SIOA",  self)
        for oia in self.arr:
            print ("  - ", oia)
        
        
class InvestmentOperationCurrentHomogeneusManager(InvestmentOperationCurrentHeterogeneusManager):
    def __init__(self, mem, investment):
        InvestmentOperationCurrentHeterogeneusManager.__init__(self, mem)
        self.investment=investment
    
    def average_age(self, type=1):
        """Average age of the current investment operations in days"""
        (sumbalance, sumbalanceage)=(Decimal(0), Decimal(0))
        for o in self.arr:
            balance=o.balance(o.investment.product.result.basic.last, type)
            sumbalance=sumbalance+balance.amount
            sumbalanceage=sumbalanceage+balance.amount*o.age()
        if sumbalance!=Decimal(0):
            return sumbalanceage/sumbalance
        else:
            return Decimal(0)

    def average_price(self, type=1):
        """Calcula el precio medio de compra"""
        
        shares=self.shares()
        currency=self.investment.resultsCurrency(type)
        sharesxprice=Decimal(0)
        for o in self.arr:
            sharesxprice=sharesxprice+o.shares*o.price(type).amount
        return Money(self.mem, 0, currency) if shares==Decimal(0) else Money(self.mem, sharesxprice/shares,  currency)
        
        
    def average_price_after_a_gains_percentage(self, percentage,  type=1):
        """
            percentage is a Percentage object
            Returns a Money object after add a percentage to the average_price
        """
        return self.average_price(type)*(1+percentage.value)
        
    def invertido(self, type=1):
        """Al ser homegeneo da el resultado en Money del producto"""
        currency=self.investment.resultsCurrency(type)
        resultado=Money(self.mem, 0, currency)
        for o in self.arr:
            resultado=resultado+o.invertido(type)
        return resultado
        
    def balance(self, quote, type=1):
        """Al ser homegeneo da el resultado en Money del producto"""
        currency=self.investment.resultsCurrency(type)
        resultado=Money(self.mem, 0, currency)
        for o in self.arr:
            resultado=resultado+o.balance(quote, type)
        return resultado        

    def penultimate(self, type=1):
        """Al ser homegeneo da el resultado en Money del producto"""
        currency=self.investment.resultsCurrency(type)
        resultado=Money(self.mem, 0, currency)
        for o in self.arr:
            resultado=resultado+o.penultimate( type)
        return resultado
        
        
    def gains_last_day(self, type=1):
        """Función que calcula la diferencia de balance entre last y penultimate
        Necesita haber cargado mq getbasic y operinversionesactual"""
        return self.balance(self.investment.product.result.basic.last, type)-self.penultimate(type)

    def gains_in_selling_point(self, type=1):
        """Gains in investment defined selling point"""
        if self.investment.venta!=None:
            return self.investment.selling_price(type)*self.investment.shares()-self.investment.invertido(None, type)
        return Money(self.mem,  0, self.investment.resultsCurrency(type) )
        

    def gains_from_percentage(self, percentage,  type=1):
        """
            Gains a percentage from average_price
            percentage is a Percentage object
        """        
        return self.average_price(type)*percentage.value*self.shares()

    def pendiente(self, lastquote, type=1):
        currency=self.investment.resultsCurrency(type)
        resultado=Money(self.mem, 0, currency)
        for o in self.arr:
            resultado=resultado+o.pendiente(lastquote, type)
        return resultado
        
    def pendiente_positivo(self, lastquote, type=1):
        currency=self.investment.resultsCurrency(type)
        resultado=Money(self.mem, 0, currency)
        for o in self.arr:
            pendiente=o.pendiente(lastquote, type)
            if pendiente.isGETZero():
                resultado=resultado+pendiente
        return resultado
        
    def pendiente_negativo(self, lastquote, type=1):
        currency=self.investment.resultsCurrency(type)
        resultado=Money(self.mem, 0, currency)
        for o in self.arr:
            pendiente=o.pendiente(lastquote, type)
            if pendiente.isLETZero():
                resultado=resultado+pendiente
        return resultado

    def tpc_tae(self, last,  type=1):
        dias=self.average_age()
        if dias==0:
            dias=1
        return Percentage(self.tpc_total(last, type)*365, dias)

    def tpc_total(self, last, type=1):
        """
            last is a Money object with investment.product currency
            type puede ser:
                1 Da el tanto por  ciento en la currency de la inversi´on
                2 Da el tanto por  ciento en la currency de la cuenta, por lo que se debe convertir teniendo en cuenta la temporalidad
                3 Da el tanto por ciento en la currency local, partiendo  de la conversi´on a la currency de la cuenta
        """
        return Percentage(self.pendiente(last, type), self.invertido(type))
    
    def myqtablewidget(self,  tabla,  quote=None, type=1):
        """Función que rellena una tabla pasada como parámetro con datos procedentes de un array de objetos
        InvestmentOperationCurrent y dos valores de mystocks para rellenar los tpc correspodientes
        
        Se dibujan las columnas pero las propiedad alternate color... deben ser en designer
        
        Parámetros
            - tabla myQTableWidget en la que rellenar los datos
            - quote, si queremos cargar las operinversiones con un valor determinado se pasará la quote correspondiente. Es un Objeto quote
            - type. Si es Falsa muestra la moneda de la inversión si es verdadera con la currency de la cuentaº
        """
            
        tabla.setColumnCount(10)
        tabla.setHorizontalHeaderItem(0, QTableWidgetItem(QApplication.translate("Core", "Date" )))
        tabla.setHorizontalHeaderItem(1, QTableWidgetItem(QApplication.translate("Core", "Shares" )))
        tabla.setHorizontalHeaderItem(2, QTableWidgetItem(QApplication.translate("Core", "Price" )))
        tabla.setHorizontalHeaderItem(3, QTableWidgetItem(QApplication.translate("Core", "Invested" )))
        tabla.setHorizontalHeaderItem(4, QTableWidgetItem(QApplication.translate("Core", "Current balance" )))
        tabla.setHorizontalHeaderItem(5, QTableWidgetItem(QApplication.translate("Core", "Pending" )))
        tabla.setHorizontalHeaderItem(6, QTableWidgetItem(QApplication.translate("Core", "% annual" )))
        tabla.setHorizontalHeaderItem(7, QTableWidgetItem(QApplication.translate("Core", "% APR" )))
        tabla.setHorizontalHeaderItem(8, QTableWidgetItem(QApplication.translate("Core", "% Total" )))
        tabla.setHorizontalHeaderItem(9, QTableWidgetItem(QApplication.translate("Core", "Benchmark" )))
        #DATA
        if self.length()==0:
            tabla.setRowCount(0)
            return

        if quote==None:
            quote=self.investment.product.result.basic.last
        quote_lastyear=self.investment.product.result.basic.lastyear

        tabla.applySettings()
        tabla.clearContents()
        tabla.setRowCount(self.length()+1)
        for rownumber, a in enumerate(self.arr):
            tabla.setItem(rownumber, 0, qdatetime(a.datetime, self.mem.localzone))
            if self.mem.gainsyear==True and a.less_than_a_year()==True:
                tabla.item(rownumber, 0).setIcon(QIcon(":/xulpymoney/new.png"))
            
            tabla.setItem(rownumber, 1, qright("{0:.6f}".format(a.shares)))
            tabla.setItem(rownumber, 2, a.price(type).qtablewidgetitem())            
            tabla.setItem(rownumber, 3, a.invertido(type).qtablewidgetitem())
            tabla.setItem(rownumber, 4, a.balance(quote, type).qtablewidgetitem())
            tabla.setItem(rownumber, 5, a.pendiente(quote, type).qtablewidgetitem())
            tabla.setItem(rownumber, 6, a.tpc_anual(quote, quote_lastyear, type).qtablewidgetitem())
            tabla.setItem(rownumber, 7, a.tpc_tae(quote, type).qtablewidgetitem())
            tabla.setItem(rownumber, 8, a.tpc_total(quote, type).qtablewidgetitem())
            if a.referenciaindice==None:
                tabla.setItem(rownumber, 9, self.mem.data.benchmark.currency.qtablewidgetitem(None))
            else:
                tabla.setItem(rownumber, 9, self.mem.data.benchmark.currency.qtablewidgetitem(a.referenciaindice.quote))
                
        tabla.setItem(self.length(), 0, QTableWidgetItem(("TOTAL")))
        tabla.setItem(self.length(), 1, qright(self.shares()))
        tabla.setItem(self.length(), 2, self.average_price(type).qtablewidgetitem())
        tabla.setItem(self.length(), 3, self.invertido(type).qtablewidgetitem())
        tabla.setItem(self.length(), 4, self.balance(quote, type).qtablewidgetitem())
        tabla.setItem(self.length(), 5, self.pendiente(quote, type).qtablewidgetitem())
        tabla.setItem(self.length(), 7, self.tpc_tae(quote, type).qtablewidgetitem())
        tabla.setItem(self.length(), 8, self.tpc_total(quote, type).qtablewidgetitem())

class InvestmentOperationHistoricalHeterogeneusManager(ObjectManager_With_Id_Selectable):       
    """Clase es un array ordenado de objetos newInvestmentOperation"""
    def __init__(self, mem):
        ObjectManager_With_Id_Selectable.__init__(self)
        self.mem=mem

        
    def consolidado_bruto(self,  year=None,  month=None):
        type=3
        resultado=Money(self.mem, 0, self.mem.localcurrency)
        for o in self.arr:        
            if year==None:#calculo historico
                resultado=resultado+o.consolidado_bruto(type)
            else:                
                if month==None:#Calculo anual
                    if o.fecha_venta.year==year:
                        resultado=resultado+o.consolidado_bruto(type)
                else:#Calculo mensual
                    if o.fecha_venta.year==year and o.fecha_venta.month==month:
                        resultado=resultado+o.consolidado_bruto(type)
        return resultado        
        
    def consolidado_neto(self,  year=None,  month=None):
        type=3
        resultado=Money(self.mem, 0, self.mem.localcurrency)
        for o in self.arr:        
            if year==None:#calculo historico
                resultado=resultado+o.consolidado_neto(type)
            else:                
                if month==None:#Calculo anual
                    if o.fecha_venta.year==year:
                        resultado=resultado+o.consolidado_neto(type)
                else:#Calculo mensual
                    if o.fecha_venta.year==year and o.fecha_venta.month==month:
                        resultado=resultado+o.consolidado_neto(type)
        return resultado
        
    def consolidado_neto_antes_impuestos(self,  year=None,  month=None):
        resultado=Money(self.mem, 0, self.mem.localcurrency)
        type=3
        for o in self.arr:        
            if year==None:#calculo historico
                resultado=resultado+o.consolidado_neto_antes_impuestos(type)
            else:                
                if month==None:#Calculo anual
                    if o.fecha_venta.year==year:
                        resultado=resultado+o.consolidado_neto_antes_impuestos(type)
                else:#Calculo mensual
                    if o.fecha_venta.year==year and o.fecha_venta.month==month:
                        resultado=resultado+o.consolidado_neto_antes_impuestos(type)
        return resultado

    def gross_purchases(self):
        """Bruto de todas las compras de la historicas"""
        r=Money(self.mem, 0, self.mem.localcurrency)
        for a in self.arr:
            r=r+a.bruto_compra(3)
        return r

    def gross_sales(self):
        """Bruto de todas las compras de la historicas"""
        r=Money(self.mem, 0,  self.mem.localcurrency)
        for a in self.arr:
            r=r+a.bruto_venta(3)
        return r
        
    def taxes(self):
        r=Money(self.mem,  0,  self.mem.localcurrency)
        for a in self.arr:
            r=r+a.taxes(3)
        return r
        
    def tpc_total_neto(self):
        return Percentage(self.consolidado_neto(), self.gross_purchases())
        
    def comissions(self):
        r=Money(self.mem, 0,  self.mem.localcurrency)
        for a in self.arr:
            r=r+a.comission(3)
        return r

    def gross_positive_operations(self):
        """Resultado en self.mem.localcurrency"""
        r=Money(self.mem, 0, self.mem.localcurrency)
        for a in self.arr:
            if a.bruto().local().isGETZero():
                r=r+a.bruto(3)
        return r
    
    def gross_negative_operations(self):
        """Resultado en self.mem.localcurrency"""
        r=Money(self.mem, 0, self.mem.localcurrency)
        for a in self.arr:
            if a.bruto().local().isLTZero():
                r=r+a.bruto(3)
        return r
        
        
    def myqtablewidget(self, tabla):
        """Usa self.mem.localcurrency como moneda"""
            
        tabla.setColumnCount(13)
        tabla.setHorizontalHeaderItem(0, QTableWidgetItem(QApplication.translate("Core", "Date" )))
        tabla.setHorizontalHeaderItem(1, QTableWidgetItem(QApplication.translate("Core", "Years" )))
        tabla.setHorizontalHeaderItem(2, QTableWidgetItem(QApplication.translate("Core", "Product" )))
        tabla.setHorizontalHeaderItem(3, QTableWidgetItem(QApplication.translate("Core", "Account" )))
        tabla.setHorizontalHeaderItem(4, QTableWidgetItem(QApplication.translate("Core", "Operation type" )))
        tabla.setHorizontalHeaderItem(5, QTableWidgetItem(QApplication.translate("Core", "Shares" )))
        tabla.setHorizontalHeaderItem(6, QTableWidgetItem(QApplication.translate("Core", "Initial balance" )))
        tabla.setHorizontalHeaderItem(7, QTableWidgetItem(QApplication.translate("Core", "Final balance" )))
        tabla.setHorizontalHeaderItem(8, QTableWidgetItem(QApplication.translate("Core", "Gross selling operations" )))
        tabla.setHorizontalHeaderItem(9, QTableWidgetItem(QApplication.translate("Core", "Comissions" )))
        tabla.setHorizontalHeaderItem(10, QTableWidgetItem(QApplication.translate("Core", "Taxes" )))
        tabla.setHorizontalHeaderItem(11, QTableWidgetItem(QApplication.translate("Core", "Net selling operations" )))
        tabla.setHorizontalHeaderItem(12, QTableWidgetItem(QApplication.translate("Core", "% Net APR" )))
        tabla.setHorizontalHeaderItem(13, QTableWidgetItem(QApplication.translate("Core", "% Net Total" )))


        type=3
        tabla.applySettings()
        tabla.clearContents()
        tabla.setRowCount(self.length()+1)
        for rownumber, a in enumerate(self.arr):    
            tabla.setItem(rownumber, 0,QTableWidgetItem(str(a.fecha_venta)))    
            tabla.setItem(rownumber, 1,QTableWidgetItem(str(round(a.years(), 2))))    
            tabla.setItem(rownumber, 2,QTableWidgetItem(a.investment.name))
            tabla.setItem(rownumber, 3,QTableWidgetItem(a.investment.account.name))
            tabla.setItem(rownumber, 4,QTableWidgetItem(a.tipooperacion.name))
            tabla.setItem(rownumber, 5,qright(a.shares))
            tabla.setItem(rownumber, 6,a.bruto_compra(type).qtablewidgetitem())
            tabla.setItem(rownumber, 7,a.bruto_venta(type).qtablewidgetitem())
            tabla.setItem(rownumber, 8,a.consolidado_bruto(type).qtablewidgetitem())
            tabla.setItem(rownumber, 9,a.comission(type).qtablewidgetitem())
            tabla.setItem(rownumber, 10,a.taxes(type).qtablewidgetitem())
            tabla.setItem(rownumber, 11,a.consolidado_neto(type).qtablewidgetitem())
            tabla.setItem(rownumber, 12,a.tpc_tae_neto().qtablewidgetitem())
            tabla.setItem(rownumber, 13,a.tpc_total_neto().qtablewidgetitem())

        
        tabla.setItem(self.length(), 2,QTableWidgetItem("TOTAL"))
        tabla.setItem(self.length(), 6,self.gross_purchases().qtablewidgetitem())    
        tabla.setItem(self.length(), 7,self.gross_sales().qtablewidgetitem())    
        tabla.setItem(self.length(), 8,self.consolidado_bruto().qtablewidgetitem())    
        tabla.setItem(self.length(), 9,self.comissions().qtablewidgetitem())    
        tabla.setItem(self.length(), 10,self.taxes().qtablewidgetitem())    
        tabla.setItem(self.length(), 11,self.consolidado_neto().qtablewidgetitem())
        tabla.setItem(self.length(), 13,self.tpc_total_neto().qtablewidgetitem())
        tabla.setCurrentCell(self.length(), 5)       
    

    def order_by_fechaventa(self):
        """Sort by selling date"""
        self.arr=sorted(self.arr, key=lambda o: o.fecha_venta,  reverse=False)      

        

        
class InvestmentOperationHistoricalHomogeneusManager(InvestmentOperationHistoricalHeterogeneusManager):
    def __init__(self, mem, investment):
        InvestmentOperationHistoricalHeterogeneusManager.__init__(self, mem)
        self.investment=investment
                
    def consolidado_bruto(self,  year=None,  month=None, type=1):
        resultado=Money(self.mem, 0, self.investment.resultsCurrency(type))
        for o in self.arr:        
            if year==None:#calculo historico
                resultado=resultado+o.consolidado_bruto(type)
            else:                
                if month==None:#Calculo anual
                    if o.fecha_venta.year==year:
                        resultado=resultado+o.consolidado_bruto(type)
                else:#Calculo mensual
                    if o.fecha_venta.year==year and o.fecha_venta.month==month:
                        resultado=resultado+o.consolidado_bruto(type)
        return resultado
        
    def consolidado_neto(self,  year=None,  month=None):
        resultado=Money(self.mem, 0, self.investment.product.currency)
        for o in self.arr:        
            if year==None:#calculo historico
                resultado=resultado+o.consolidado_neto()
            else:                
                if month==None:#Calculo anual
                    if o.fecha_venta.year==year:
                        resultado=resultado+o.consolidado_neto()
                else:#Calculo mensual
                    if o.fecha_venta.year==year and o.fecha_venta.month==month:
                        resultado=resultado+o.consolidado_neto()
        return resultado
        
    def consolidado_neto_antes_impuestos(self,  year=None,  month=None):
        resultado=Money(self.mem, 0, self.investment.product.currency)
        for o in self.arr:        
            if year==None:#calculo historico
                resultado=resultado+o.consolidado_neto_antes_impuestos()
            else:                
                if month==None:#Calculo anual
                    if o.fecha_venta.year==year:
                        resultado=resultado+o.consolidado_neto_antes_impuestos()
                else:#Calculo mensual
                    if o.fecha_venta.year==year and o.fecha_venta.month==month:
                        resultado=resultado+o.consolidado_neto_antes_impuestos()
        return resultado
        
    def bruto_compra(self):
        resultado=Money(self.mem, 0, self.investment.product.currency)
        for o in self.arr:
            resultado=resultado+o.bruto_compra()
        return resultado
    def tpc_total_neto(self):
        return Percentage(self.consolidado_neto(), self.bruto_compra())

    def myqtablewidget(self, tabla, show_accounts=False, type=1):
        """Rellena datos de un array de objetos de InvestmentOperationHistorical, devuelve totales ver código"""
        diff=0
        if show_accounts==True:
            diff=2
            
        tabla.setColumnCount(12+diff)
        tabla.setHorizontalHeaderItem(0, QTableWidgetItem(QApplication.translate("Core", "Date" )))
        tabla.setHorizontalHeaderItem(1, QTableWidgetItem(QApplication.translate("Core", "Years" )))
        if show_accounts==True:
            tabla.setHorizontalHeaderItem(2, QTableWidgetItem(QApplication.translate("Core", "Product" )))
            tabla.setHorizontalHeaderItem(3, QTableWidgetItem(QApplication.translate("Core", "Account" )))
        tabla.setHorizontalHeaderItem(2+diff, QTableWidgetItem(QApplication.translate("Core", "Operation type" )))
        tabla.setHorizontalHeaderItem(3+diff, QTableWidgetItem(QApplication.translate("Core", "Shares" )))
        tabla.setHorizontalHeaderItem(4+diff, QTableWidgetItem(QApplication.translate("Core", "Initial balance" )))
        tabla.setHorizontalHeaderItem(5+diff, QTableWidgetItem(QApplication.translate("Core", "Final balance" )))
        tabla.setHorizontalHeaderItem(6+diff, QTableWidgetItem(QApplication.translate("Core", "Gross selling operations" )))
        tabla.setHorizontalHeaderItem(7+diff, QTableWidgetItem(QApplication.translate("Core", "Comissions" )))
        tabla.setHorizontalHeaderItem(8+diff, QTableWidgetItem(QApplication.translate("Core", "Taxes" )))
        tabla.setHorizontalHeaderItem(9+diff, QTableWidgetItem(QApplication.translate("Core", "Net selling operations" )))
        tabla.setHorizontalHeaderItem(10+diff, QTableWidgetItem(QApplication.translate("Core", "% Net APR" )))
        tabla.setHorizontalHeaderItem(11+diff, QTableWidgetItem(QApplication.translate("Core", "% Net Total" )))
        #DATA    
                
                
        currency=self.investment.resultsCurrency(type)
        
        
        (sumbruto, sumneto)=(Money(self.mem, 0, currency), Money(self.mem, 0, currency))
        sumsaldosinicio=Money(self.mem, 0, currency)
        sumsaldosfinal=Money(self.mem, 0, currency)
        
        sumoperacionespositivas=Money(self.mem, 0, currency)
        sumoperacionesnegativas=Money(self.mem, 0, currency)
        sumimpuestos=Money(self.mem, 0, currency)
        sumcomision=Money(self.mem, 0, currency)
 
 
        tabla.applySettings()
        tabla.clearContents()
        tabla.setRowCount(self.length()+1)
        for rownumber, a in enumerate(self.arr):
            saldoinicio=a.bruto_compra(type)
            saldofinal=a.bruto_venta(type)
            bruto=a.consolidado_bruto(type)
            neto=a.consolidado_neto(type)
            
            sumbruto=sumbruto+bruto
            sumneto=sumneto+neto
            sumsaldosinicio=sumsaldosinicio+saldoinicio
            sumsaldosfinal=sumsaldosfinal+saldofinal
    
            #Calculo de operaciones positivas y negativas
            if bruto.isGETZero():
                sumoperacionespositivas=sumoperacionespositivas+bruto 
            else:
                sumoperacionesnegativas=sumoperacionesnegativas+bruto
    
            tabla.setItem(rownumber, 0,qdate(a.fecha_venta))
            
            tabla.setItem(rownumber, 1,QTableWidgetItem(str(round(a.years(), 2))))    
            
            
            if show_accounts==True:
                tabla.setItem(rownumber, 2,QTableWidgetItem(a.investment.name))
                tabla.setItem(rownumber, 3,QTableWidgetItem(a.investment.account.name))
                
            tabla.setItem(rownumber, 2+diff,QTableWidgetItem(a.tipooperacion.name))
            
            tabla.setItem(rownumber, 3+diff,qright(a.shares))
            
            tabla.setItem(rownumber, 4+diff,saldoinicio.qtablewidgetitem())
            
            tabla.setItem(rownumber, 5+diff,saldofinal.qtablewidgetitem())
            
            tabla.setItem(rownumber, 6+diff,bruto.qtablewidgetitem())
            
            sumimpuestos=sumimpuestos+a.taxes(type)
            sumcomision=sumcomision+a.comission(type)
            tabla.setItem(rownumber, 7+diff,a.comission(type).qtablewidgetitem())
            tabla.setItem(rownumber, 8+diff,a.taxes(type).qtablewidgetitem())
            
            tabla.setItem(rownumber, 9+diff,neto.qtablewidgetitem())
            
            tabla.setItem(rownumber, 10+diff, a.tpc_tae_neto().qtablewidgetitem())
            
            tabla.setItem(rownumber, 11+diff, a.tpc_total_neto().qtablewidgetitem())
        if self.length()>0:
            tabla.setItem(self.length(), 2,QTableWidgetItem("TOTAL"))
            tabla.setItem(self.length(), 4+diff,sumsaldosinicio.qtablewidgetitem())
            tabla.setItem(self.length(), 5+diff,sumsaldosfinal.qtablewidgetitem())
            tabla.setItem(self.length(), 6+diff,sumbruto.qtablewidgetitem())  
            tabla.setItem(self.length(), 7+diff,sumcomision.qtablewidgetitem())    
            tabla.setItem(self.length(), 8+diff,sumimpuestos.qtablewidgetitem())    
            tabla.setItem(self.length(), 9+diff,sumneto.qtablewidgetitem())
            tabla.setItem(self.length(), 11+diff,self.tpc_total_neto().qtablewidgetitem())
            tabla.setCurrentCell(self.length(), 4+diff)       
        return (sumbruto, sumcomision, sumimpuestos, sumneto)
    
class InvestmentOperationHistorical:
    def __init__(self, mem):
        self.mem=mem 
        self.id=None
        self.operinversion=None
        self.investment=None
        self.fecha_inicio=None
        self.tipooperacion=None
        self.shares=None#Es negativo
        self.comision=None
        self.impuestos=None
        self.fecha_venta=None
        self.valor_accion_compra=None
        self.valor_accion_venta=None     
        self.currency_conversion_compra=None
        self.currency_conversion_venta=None
            
    def __repr__(self):
        return ("IOH {0}. {1} {2}. Acciones: {3}. Valor:{4}. Currency conversion: {5} y {6}".format(self.investment.name,  self.fecha_venta, self.tipooperacion.name,  self.shares,  self.valor_accion_venta, self.currency_conversion_compra,  self.currency_conversion_venta))
        
    def init__create(self, operinversion, inversion, fecha_inicio, tipooperacion, acciones,comision,impuestos,fecha_venta,valor_accion_compra,valor_accion_venta, currency_conversion_compra, currency_conversion_venta,  id=None):
        """Genera un objeto con los parametros. id_operinversioneshistoricas es puesto a new"""
        self.id=id
        self.operinversion=operinversion
        self.investment=inversion
        self.fecha_inicio=fecha_inicio
        self.tipooperacion=tipooperacion
        self.shares=acciones
        self.comision=comision
        self.impuestos=impuestos
        self.fecha_venta=fecha_venta
        self.valor_accion_compra=valor_accion_compra
        self.valor_accion_venta=valor_accion_venta
        self.currency_conversion_compra=currency_conversion_compra
        self.currency_conversion_venta=currency_conversion_venta
        return self
        
    def less_than_a_year(self):
        """Returns True, when datetime of the operation is <= a year"""
        if self.fecha_venta-self.fecha_inicio<=datetime.timedelta(days=365):
            return True
        return False
        
    def consolidado_bruto(self, type=1):
        """Solo acciones"""
        currency=self.investment.resultsCurrency(type)
        if self.tipooperacion.id in (9, 10):
            return Money(self.mem, 0, currency)
        return self.bruto_venta(type)-self.bruto_compra(type)
        
    def consolidado_neto(self, type=1):
        currency=self.investment.resultsCurrency(type)
        if self.tipooperacion.id in (9, 10):
            return Money(self.mem, 0, currency)
        return self.consolidado_bruto(type)-self.comission(type)-self.taxes(type)

    def consolidado_neto_antes_impuestos(self, type=1):
        currency=self.investment.resultsCurrency(type)
        if self.tipooperacion.id in (9, 10):
            return Money(self.mem, 0, currency)
        return self.consolidado_bruto(type)-self.comission(type)

    def bruto_compra(self, type=1):
        currency=self.investment.resultsCurrency(type)
        if self.tipooperacion.id in (9, 10):
            return Money(self.mem, 0, currency)
        if type==1:
            return Money(self.mem, -self.shares*self.valor_accion_compra, self.investment.product.currency)
        else:
            return Money(self.mem, -self.shares*self.valor_accion_compra, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion_compra)
        
    def bruto_venta(self, type=1):
        currency=self.investment.resultsCurrency(type)
        if self.tipooperacion.id in (9, 10):
            return Money(self.mem, 0, currency)
        if type==1:
            return Money(self.mem, -self.shares*self.valor_accion_venta, self.investment.product.currency)
        else:
            return Money(self.mem, -self.shares*self.valor_accion_venta, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion_venta)
        
    def taxes(self, type=1):
        if type==1:
            return Money(self.mem, self.impuestos, self.investment.account.currency).convert_from_factor(self.investment.product.currency, 1/self.currency_conversion_venta)
        else:
            return Money(self.mem, self.impuestos, self.investment.account.currency)        
    
    def comission(self, type=1):
        if type==1:
            return Money(self.mem, self.comision, self.investment.account.currency).convert_from_factor(self.investment.product.currency, 1/self.currency_conversion_venta)
        else:
            return Money(self.mem, self.comision, self.investment.account.currency)
        
        
    def days(self):
        return (self.fecha_venta-self.fecha_inicio).days
        
    def years(self):
        dias=self.days()
        if dias==0:#Operación intradía
            return Decimal(1/365.0)
        else:
                return dias/Decimal(365)

    def tpc_total_neto(self):
        return Percentage(self.consolidado_neto(), self.bruto_compra())
        
    def tpc_total_bruto(self):
        return Percentage(self.consolidado_bruto(), self.bruto_compra())
        
    def tpc_tae_neto(self):
        dias=(self.fecha_venta-self.fecha_inicio).days +1 #Account el primer día
        if dias==0:
            dias=1
        return Percentage(self.tpc_total_neto()*365, dias)

class InvestmentOperationCurrent:
    def __init__(self, mem):
        self.mem=mem 
        self.id=None
        self.operinversion=None
        self.tipooperacion=None
        self.datetime=None# con tz
        self.investment=None
        self.shares=None
        self.impuestos=None
        self.comision=None
        self.valor_accion=None
        self.referenciaindice=None##Debera cargarse desde fuera. No se carga con row.. Almacena un Quote, para comprobar si es el indice correcto ver self.referenciaindice.id
        self.show_in_ranges=True
        self.currency_conversion=None
        
    def __repr__(self):
        return ("IOA {0}. {1} {2}. Acciones: {3}. Valor:{4}. Currency conversion: {5}".format(self.investment.name,  self.datetime, self.tipooperacion.name,  self.shares,  self.valor_accion, self.currency_conversion))
        
    def init__create(self, operinversion, tipooperacion, datetime, inversion, acciones,  impuestos, comision, valor_accion, show_in_ranges,  currency_conversion, id=None):
        """Investment es un objeto Investment"""
        self.id=id
        self.operinversion=operinversion
        self.tipooperacion=tipooperacion
        self.datetime=datetime
        self.investment=inversion
        self.shares=acciones
        self.impuestos=impuestos
        self.comision=comision
        self.valor_accion=valor_accion
        self.show_in_ranges=show_in_ranges
        self.currency_conversion=currency_conversion
        return self
        
    def copy(self):
        return self.init__create(self.operinversion, self.tipooperacion, self.datetime, self.investment, self.shares, self.impuestos, self.comision, self.valor_accion, self.show_in_ranges, self.currency_conversion,   self.id)
                
    def age(self):
        """Average age of the current investment operations in days"""
        return (datetime.date.today()-self.datetime.date()).days
                
    def get_referencia_indice(self, indice):
        """Función que devuelve un Quote con la referencia del indice.
        Si no existe devuelve un Quote con quote 0"""
        quote=Quote(self.mem).init__from_query( indice, self.datetime)
        if quote==None:
            self.referenciaindice= Quote(self.mem).init__create(indice, self.datetime, 0)
        else:
            self.referenciaindice=quote
        return self.referenciaindice
        
    def invertido(self, type=1):
        """Función que devuelve el importe invertido teniendo en cuenta las acciones actuales de la operinversión y el valor de compra
        Si se usa  el importe no fuNCIONA PASO CON EL PUNTOI DE VENTA.
        """
        if type==1:
            return Money(self.mem, abs(self.shares*self.valor_accion), self.investment.product.currency)
        elif type==2:
            return Money(self.mem, abs(self.shares*self.valor_accion), self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion)#Usa el factor del dia de la operacicón
        elif type==3:
            return Money(self.mem, abs(self.shares*self.valor_accion), self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion).local(self.datetime)#Usa el factor del dia de la operacicón
    
    def price(self, type=1):
        if type==1:
            return Money(self.mem, self.valor_accion, self.investment.product.currency)
        elif type==2:
            return Money(self.mem, self.valor_accion, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion)
        elif type==3:
            return Money(self.mem, self.valor_accion, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion).local(self.datetime)
            
            
    def revaluation_monthly(self, year, month, type=1):
        """
            Returns a money object with monthly reevaluation
        """
        dt_last= month_end(year, month, self.mem.localzone)
        dt_first=month_start(year, month, self.mem.localzone)
        if self.datetime>dt_first and self.datetime<dt_last:
            dt_first=self.datetime
        elif self.datetime>dt_last:
            return Money(self.mem, 0, self.investment.product.currency)
        first=Quote(self.mem).init__from_query( self.investment.product, dt_first).quote
        last=Quote(self.mem).init__from_query( self.investment.product, dt_last).quote
        money=Money(self.mem, (last-first)*self.shares, self.investment.product.currency)
        print("{} {} {} accciones. {}-{}. {}-{}={} ({})".format(self.investment.name, self.datetime, self.shares, dt_last, dt_first, last, first, last-first,  money))
        if type==1:
            return money
        elif type==2:
            return money.convert(self.investment.account.currency, dt_last)
        elif type==3:
            return money.convert(self.investment.account.currency, dt_last).local(dt_last)
            
            
    def revaluation_annual(self, year, type=1):
        """
            Returns a money object with monthly reevaluation
        """
        dt_last= year_end(year, self.mem.localzone)
        dt_first=year_start(year, self.mem.localzone)
        if self.datetime>dt_first:
            dt_first=self.datetime
        first=Quote(self.mem).init__from_query( self.investment.product, dt_first).quote
        last=Quote(self.mem).init__from_query( self.investment.product, dt_last).quote
        money=Money(self.mem, (last-first)*self.shares, self.investment.product.currency)
        print("ANNUAL:{} {} {} accciones. {}-{}. {}-{}={} ({})".format(self.investment.name, self.datetime, self.shares, dt_last, dt_first, last, first, last-first,  money))
        if type==1:
            return money
        elif type==2:
            return money.convert(self.investment.account.currency, dt_last)
        elif type==3:
            return money.convert(self.investment.account.currency, dt_last).local(dt_last)
            
            
    def gross(self, type=1):
        if type==1:
            return Money(self.mem, self.shares*self.valor_accion, self.investment.product.currency)
        elif type==2:
            return Money(self.mem, self.shares*self.valor_accion, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion)
            
    def net(self, type=1):
        if self.shares>=Decimal(0):
            return self.gross(type)+self.comission(type)+self.taxes(type)
        elif type==2:
            return self.gross(type)-self.comission(type)-self.taxes(type)
            
    def taxes(self, type=1):
        if type==1:
            return Money(self.mem, self.impuestos, self.investment.product.currency)
        elif type==2:
            return Money(self.mem, self.impuestos, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion)
            
    def comission(self, type=1):
        if type==1:
            return Money(self.mem, self.comision, self.investment.product.currency)
        elif type==2:
            return Money(self.mem, self.comision, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion)
            
    def balance(self,  lastquote, type=1):
        """Función que calcula el balance actual de la operinversion actual
                - lastquote: objeto Quote
                type si da el resultado en la currency del account o en el de la inversion"""
        currency=self.investment.resultsCurrency(type)
        if self.shares==0 or lastquote.quote==None:#Empty xulpy
            return Money(self.mem, 0, currency)

        if type==1:
            return Money(self.mem, abs(self.shares*lastquote.quote), self.investment.product.currency)
        elif type==2:
            return Money(self.mem, abs(self.shares*lastquote.quote), self.investment.product.currency).convert(self.investment.account.currency, lastquote.datetime)
        elif type==3:
            return Money(self.mem, abs(self.shares*lastquote.quote), self.investment.product.currency).convert(self.investment.account.currency, lastquote.datetime).local(lastquote.datetime)

    def less_than_a_year(self):
        """Returns True, when datetime of the operation is <= a year"""
        if datetime.date.today()-self.datetime.date()<=datetime.timedelta(days=365):
            return True
        return False
        
    def pendiente(self, lastquote,  type=1):
        """Función que calcula el balance  pendiente de la operacion de inversion actual
                Necesita haber cargado mq getbasic y operinversionesactual
                lasquote es un objeto Quote
                """
        return self.balance(lastquote, type)-self.invertido(type)

    def penultimate(self, type=1):
        """
            Función que calcula elbalance en el penultimate ida
        """
        
        currency=self.investment.resultsCurrency(type)
        penultimate=self.investment.product.result.basic.penultimate
        if self.shares==0 or penultimate.quote==None:#Empty xulpy
            logging.error("{} no tenia suficientes quotes en {}".format(function_name(self), self.investment.name))
            return Money(self.mem, 0, currency)

        if type==1:
            return Money(self.mem, abs(self.shares*penultimate.quote), self.investment.product.currency)
        elif type==2:
            return Money(self.mem, abs(self.shares*penultimate.quote), self.investment.product.currency).convert(self.investment.account.currency, penultimate.datetime)#Al ser balance actual usa el datetime actual
        elif type==3:
            return Money(self.mem, abs(self.shares*penultimate.quote), self.investment.product.currency).convert(self.investment.account.currency, penultimate.datetime).local(penultimate.datetime)
            
    def tpc_anual(self,  last,  lastyear, type=1):        
        """
            last is a Money object with investment.product currency
            type puede ser:
                1 Da el tanto por  ciento en la currency de la inversi´on
                2 Da el tanto por  ciento en la currency de la cuenta, por lo que se debe convertir teniendo en cuenta la temporalidad
                3 Da el tanto por ciento en la currency local, partiendo  de la conversi´on a la currency de la cuenta
        """
        mlast=self.investment.quote2money(last, type)
        
        if self.datetime.year==datetime.date.today().year:#Si la operaci´on fue en el año, cuenta desde el dia de la operaci´on, luego su preicio
            mlastyear=self.price(type)
        else:
            mlastyear=self.investment.quote2money(lastyear, type)
            
        return Percentage(mlast-mlastyear, mlastyear)
    
    def tpc_total(self,  last,  type=1):
        """
            last is a Quote object 
            type puede ser:
                1 Da el tanto por  ciento en la currency de la inversi´on
                2 Da el tanto por  ciento en la currency de la cuenta, por lo que se debe convertir teniendo en cuenta la temporalidad
                3 Da el tanto por ciento en la currency local, partiendo  de la conversi´on a la currency de la cuenta
        """
        if last==None:#initiating xulpymoney
            return Percentage()
        return Percentage(self.pendiente(last, type), self.invertido(type))
            
        
    def tpc_tae(self, last, type=1):
        dias=self.age()
        if self.age()==0:
            dias=1
        return Percentage(self.tpc_total(last, type)*365,  dias)
        
        

class Comment:
    """Class who controls all comments from opercuentas, operinversiones ..."""
    def __init__(self, mem):
        self.mem=mem

    def getCode(self, string):
        """
            Obtiene el codigo de un comentario
        """
        (code, args)=self.get(string)
        return code        

    def getArgs(self, string):
        """
            Obtiene los argumentos enteros de un comentario
        """
        (code, args)=self.get(string)
        return args

    def get(self, string):
        """Returns (code,args)"""
        string=string
        try:
            number=string2list(string)
            if len(number)==1:
                code=number[0]
                args=[]
            else:
                code=number[0]
                args=number[1:]
            return(code, args)
        except:
            return(None, None)
        
    def validateLength(self, number, code, args):
        if number!=len(args):
            logging("Comment {} has not enough parameters".format(code))
            return False
        return True
        
    def getDividend(self, id, code):
        dividend=Dividend(self.mem).init__db_query(id)
        if dividend==None:
            logging.error("I coudn't find dividend {} for comment {}".format(id, code))
        return dividend
        
    def getInvestmentOperation(self, id, code):
        operinversion=self.mem.data.investments.findInvestmentOperation(id)
        if operinversion==None:
            logging.error("I coudn't find operinversion {} for comment {}".format(id, code))
        return operinversion
        
    def getAccountOperation(self, id, code):
        accountoperation=AccountOperation(self.mem,  id)
        if accountoperation==None:
            logging.error("I couldn't find accountoperation {} for comment {}".format(id, code))
        return accountoperation
        
    def getCreditCard(self, id, code):
        creditcard=self.mem.data.creditcards.find_by_id(id)
        if creditcard==None:
            logging.error("I couldn't find creditcard {} for comment {}".format(id, code))
        return creditcard        
    def getCreditCardOperation(self, id, code):
        cco=CreditCardOperation(self.mem).init__db_query(id)
        if cco==None:
            logging.error("I couldn't find creditcard operation {} for comment {}".format(id, code))
        return cco
        
    def setEncoded10000(self, operinvestment):
        """
            10000;investmentoperation.idSets the coded comment to save in db
        """
        return "10000,{}".format(operinvestment.id)
        
    def setEncoded10001(self, operaccountorigin, operaccountdestiny, operaccountorigincomission):
        """
            Usado en una transferencia entre cuentas, es la opercuenta de origen
        """
        if operaccountorigincomission==None:
            operaccountorigincomission_id=-1
        else:
            operaccountorigincomission_id=operaccountorigincomission.id
        return "10001,{},{},{}".format(operaccountorigin.id, operaccountdestiny.id, operaccountorigincomission_id)        
        
    def setEncoded10002(self, operaccountorigin, operaccountdestiny, operaccountorigincomission):
        """
            Usado en una transferencia entre cuentas, es la opercuenta de destino
        """
        if operaccountorigincomission==None:
            operaccountorigincomission_id=-1
        else:
            operaccountorigincomission_id=operaccountorigincomission.id
        return "10002,{},{},{}".format(operaccountorigin.id, operaccountdestiny.id, operaccountorigincomission_id)        
        
    def setEncoded10003(self, operaccountorigin, operaccountdestiny, operaccountorigincomission):
        """
            Usado en una transferencia entre cuentas, es la opercuenta de la comisi´on en origen
        """
        if operaccountorigincomission==None:
            operaccountorigincomission_id=-1
        else:
            operaccountorigincomission_id=operaccountorigincomission.id
        return "10003,{},{},{}".format(operaccountorigin.id, operaccountdestiny.id, operaccountorigincomission_id)        
                
    def setEncoded10004(self, dividend):
        """
            Usado en un dividendo para poner comentario a la cuenta asociada
        """
        return "10004,{}".format(dividend.id)        
                        
    def setEncoded10005(self, creditcard,  operaccount):
        """
            Usado en en comentario que muestra la opercuenta cuando se ha realizado un pago de facturaci´on de tarjeta
            
            De la opercuenta se puede sacar el n´umero de pagos incluidos.
        """
        return "10005,{},{}".format(creditcard.id, operaccount.id)        
    def setEncoded10006(self, opercreditcardtorefund):
        """
            Usado en comentario que muestra la opertarjeta que quiero devolver.
        """
        return "10006,{}".format(opercreditcardtorefund.id)        
        
    def setFancy(self, string):
        """Sets the comment to show in app"""
        (code, args)=self.get(string)
        if code==None:
            return string
        if code==10000:#Operinversion comment
            self.validateLength(1, code, args)
            io=self.getInvestmentOperation(args[0], code)
            if io.investment.hasSameAccountCurrency():
                return QApplication.translate("Core","{}: {} shares. Amount: {}. Comission: {}. Taxes: {}").format(io.investment.name, io.shares, io.gross(1), io.comission(1), io.taxes(1))
            else:
                return QApplication.translate("Core","{}: {} shares. Amount: {} ({}). Comission: {} ({}). Taxes: {} ({})").format(io.investment.name, io.shares, io.gross(1), io.gross(2),  io.comission(1), io.comission(2),  io.taxes(1), io.taxes(2))
                
        elif code==10001:#Operaccount transfer origin
            self.validateLength(3, code, args)
            aod=self.getAccountOperation(args[1], code)
            return QApplication.translate("Core","Transfer to {}").format(aod.account.name)
        elif code==10002:#Operaccount transfer destiny
            self.validateLength(3, code, args)
            aoo=self.getAccountOperation(args[0], code)
            return QApplication.translate("Core","Transfer received from {}").format(aoo.account.name)
        elif code==10003:#Operaccount transfer origin comision
            self.validateLength(3, code, args)
            aoo=self.getAccountOperation(args[0], code)
            aod=self.getAccountOperation(args[1], code)
            return QApplication.translate("Core","Comission transfering {} from {} to {}").format(aoo.account.currency.string(aoo.importe), aoo.account.name, aod.account.name)
        elif code==10004:#Comentario de cuenta asociada al dividendo
            self.validateLength(1, code, args)
            dividend=self.getDividend(args[0], code)
            print(dividend)
            investment=self.mem.data.investments.find_by_id(dividend.investment.id)
            if investment.hasSameAccountCurrency():
                return QApplication.translate("Core", "From {}. Gross {}. Net {}.").format(investment.name, dividend.gross(1), dividend.net(1))
            else:
                return QApplication.translate("Core", "From {}. Gross {} ({}). Net {} ({}).").format(investment.name, dividend.gross(1), dividend.gross(2), dividend.net(1), dividend.net(2))
        elif code==10005:#Facturaci´on de tarjeta diferida
            self.validateLength(2, code, args)
            creditcard=self.getCreditCard(args[0], code)
            number=self.mem.con.cursor_one_field("select count(*) from opertarjetas where id_opercuentas=%s", (args[1], ))
            return QApplication.translate("Core"," Billing {} movements of {}").format(number, creditcard.name)
        elif code==10006:#Devoluci´on de tarjeta
            self.validateLength(1, code, args)
            cco=self.getCreditCardOperation(args[0], code)
            money=Money(self.mem, cco.importe, cco.tarjeta.account.currency)
            return QApplication.translate("Core"," Refund of {} payment of which had an amount of {}").format(dtaware2string(cco.datetime,  self.mem.localzone.name), money)
## Class to manage operation concepts for expenses, incomes... For example: Restuarant, Supermarket
class Concept:
    ## Constructor with the following attributes combination
    ## 1. Concept(mem). Create a Concept with all attributes to None
    ## 2. Concept(mem, row, tipooperacion). Create a Concept from a db row, generated in a database query
    ## 3. Concept(mem, name, tipooperacion,editable, id). Create a Concept passing all attributes
    ## @param mem MemXulpymoney object
    ## @param row Dictionary of a database query cursor
    ## @param tipooperacion OperationType Bank object
    ## @param name Concept name
    ## @param editable Boolean that sets if a Concept is editable by the user
    ## @param id Integer that sets the id of an Concept. You must set id=None if the Concept is not in the database. id is set in the save method
    def __init__(self, *args):
        def init__create(name, tipooperacion, editable,  id):
            self.id=id
            self.name=name
            self.tipooperacion=tipooperacion
            self.editable=editable

        def init__db_row(row, tipooperacion):
            return init__create(row['concepto'], tipooperacion, row['editable'], row['id_conceptos'])

        self.mem=args[0]
        if len(args)==1:
            init__create(None, None, None, None)
        elif len(args)==3:
            init__db_row(*args[1:])
        elif len(args)==5:
            init__create(*args[1:])

    def __repr__(self):
        return ("Instancia de Concept: {0} -- {1} ({2})".format( self.name, self.tipooperacion.name,  self.id))

        
    def save(self):
        cur=self.mem.con.cursor()
        if self.id==None:
            cur.execute("insert into conceptos (concepto, id_tiposoperaciones, editable) values (%s, %s, %s) returning id_conceptos", (self.name, self.tipooperacion.id, self.editable))
            self.id=cur.fetchone()[0]
        else:
            cur.execute("update conceptos set concepto=%s, id_tiposoperaciones=%s, editable=%s where id_conceptos=%s", (self.name, self.tipooperacion.id, self.editable, self.id))
        cur.close()
                            
    def es_borrable(self):
        """Función que devuelve un booleano si una cuenta es borrable, es decir, que no tenga registros dependientes."""
        if self.uses()>0 and self.editable==True:
            return False
        return True
        
    def uses(self):
        """Returns the number of uses in opercuenta and opertarjetas"""
        cur=self.mem.con.cursor()
        cur.execute("select count(*) from opercuentas where id_conceptos=%s", (self.id, ))
        opercuentas=cur.fetchone()[0]
        cur.execute("select count(*) from opertarjetas where id_conceptos=%s", (self.id, ))
        opertarjetas=cur.fetchone()[0]
        cur.close()
        return opercuentas+opertarjetas

    def borrar(self):
        if self.es_borrable():
            cur=self.mem.con.cursor()        
            cur.execute("delete from conceptos where id_conceptos=%s", (self.id, ))
            cur.close()
            return True
        return False

    def media_mensual(self):
        cur=self.mem.con.cursor()
        cur.execute("select datetime from opercuentas where id_conceptos=%s union all select datetime from opertarjetas where id_conceptos=%s order by datetime limit 1", (self.id, self.id))
        res=cur.fetchone()
        if res==None:
            primerafecha=datetime.date.today()-datetime.timedelta(days=1)
        else:
            primerafecha=res['datetime'].date()
        cur.execute("select sum(importe) as suma from opercuentas where id_conceptos=%s union all select sum(importe) as suma from opertarjetas where id_conceptos=%s", (self.id, self.id))
        suma=Decimal(0)
        for i in cur:
            if i['suma']==None:
                continue
            suma=suma+i['suma']
        cur.close()
        return Decimal(30)*suma/((datetime.date.today()-primerafecha).days+1)
        
    def mensual(self,   year,  month):  
        """Saca el gasto mensual de este concepto"""
        cur=self.mem.con.cursor()
        cur.execute("select sum(importe) as suma from opercuentas where id_conceptos=%s and date_part('month',datetime)=%s and date_part('year', datetime)=%s union all select sum(importe) as suma from opertarjetas where id_conceptos=%s  and date_part('month',datetime)=%s and date_part('year', datetime)=%s", (self.id,  month, year,  self.id,  month, year  ))
        suma=0
        for i in cur:
            if i['suma']==None:
                continue
            suma=suma+i['suma']
        cur.close()
        return suma

## Class to manage everything relationed with bank accounts operations
class AccountOperation:
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
        """opercuenta es un diccionario con el contenido de una opercuetna
        7 facturación de tarjeta
        29 y 35 compraventa productos de inversión
        39 dividends
        40 facturación de tarjeta
        50 prima de asistencia
        62 Vemta derechos de dividends
        63 y 65,66 renta fija cuponcorrido"""
        if self.concepto==None:
            return False
        if self.concepto.id in (29, 35, 39, 40, 50,  62, 63, 65, 66):#div, factur tarj:
            return False
        if Comment(self.mem).getCode(self.comentario) in (10001, 10002, 10003):
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
        
class DBAdmin:
    def __init__(self, connection):
        """connection is an object Connection to a database"""
        self.con=connection
        
    def connection_template1(self):
        cont=Connection().init__create(self.con.user, self.con.password, self.con.server, self.con.port, "template1")
        cont.connect()
        return cont


    def check_connection(self):
        """It has database parameter, due to I connect to template to create database"""
        try:
            cont=self.connection_template1()
            cont._con.set_isolation_level(0)#Si no no me dejaba
            cont.disconnect()
            return True
        except:
            print ("Conection to template1 failed")
            return False

    def create_db(self, database):
        """It has database parameter, due to I connect to template to create database"""
        cont=self.connection_template1()
        cont._con.set_isolation_level(0)#Si no no me dejaba
        if cont.is_superuser():
            cur=cont.cursor()
            cur.execute("create database {0};".format(database))
        else:
            print ("You need to be superuser to create database")
            return False
        
        
    def db_exists(self, database):
        """Hace conexi´on automatica a template usando la con """
        new=Connection().init__create(self.con.user, self.con.password, self.con.server, self.con.port, "template1")
        new.connect()
        new._con.set_isolation_level(0)#Si no no me dejaba            
        cur=new.cursor()
        cur.execute("SELECT 1 AS result FROM pg_database WHERE datname=%s", (database, ))
        
        if cur.rowcount==1:
            cur.close()
            new.disconnect
            return True
        cur.close()
        new.disconnect()
        return False

    def drop_db(self, database):
        """It has database parameter, due to I connect to template to drop database"""
        
        if self.db_exists(database)==False:
            print("Database doesn't exist")
            return True
        
        if self.con.is_superuser():
            new=Connection().init__create(self.con.user, self.con.password, self.con.server, self.con.port, "template1")
            new.connect()
            new._con.set_isolation_level(0)#Si no no me dejaba            
            try:
                cur=new.cursor()
                cur.execute("drop database {0};".format(database))
            except:
                print ("Error in drop()")
            finally:
                cur.close()
                new.disconnect()
                return False
            print("Database droped")
            return True
        else:
            print ("You need to be superuser to drop a database")
            return False
        

    def load_script(self, file):
        cur= self.con.cursor()
        procedures  = open(file,'r').read() 
        cur.execute(procedures)
        
        self.con.commit()
        cur.close()       
        
        
    def copy(self, con_origin, sql,  table_destiny ):
        """Used to copy between tables, and sql to table_destiny, table origin and destiny must have the same structure"""
        if sql.__class__==bytes:
            sql=sql.decode('UTF-8')
        f=io.StringIO()
        cur_origin=con_origin.cursor()
        cur_origin.copy_expert("copy ({}) to stdout".format(sql), f)
        cur_origin.close()
        f.seek(0)
        cur_destiny=self.con.cursor()
        cur_destiny.copy_from(f, table_destiny)
        cur_destiny.close()
        f.seek(0)
        print (f.read())
        f.close()
        
    def xulpymoney_basic_schema(self):
#        try:
            if platform.system()=="Windows":
                self.load_script("sql/xulpymoney.sql")
            else:
                self.load_script("/usr/share/xulpymoney/sql/xulpymoney.sql")
            cur= self.con.cursor()
            cur.execute("insert into entidadesbancarias values(3,'{0}', true)".format(QApplication.translate("Core","Personal Management")))
            cur.execute("insert into cuentas values(4,'{0}',3,true,NULL,'EUR')".format(QApplication.translate("Core","Cash")))
            cur.execute("insert into conceptos values(1,'{0}',2,false)".format(QApplication.translate("Core","Initiating bank account")))
            cur.execute("insert into conceptos values(2,'{0}',2,true)".format(QApplication.translate("Core","Paysheet")))
            cur.execute("insert into conceptos values(3,'{0}',1,true)".format(QApplication.translate("Core","Supermarket")))
            cur.execute("insert into conceptos values(4,'{0}',3,false)".format(QApplication.translate("Core","Transfer. Origin")))
            cur.execute("insert into conceptos values(5,'{0}',3,false)".format(QApplication.translate("Core","Transfer. Destination")))
            cur.execute("insert into conceptos values(6,'{0}',2,false)".format(QApplication.translate("Core","Taxes. Returned")))
            cur.execute("insert into conceptos values(7,'{0}',1,true)".format(QApplication.translate("Core","Gas")))
            cur.execute("insert into conceptos values(8,'{0}',1,true)".format(QApplication.translate("Core","Restaurant")))  
            cur.execute("insert into conceptos values(29,'{0}',4,false)".format(QApplication.translate("Core","Purchase investment product")))
            cur.execute("insert into conceptos values(35,'{0}',5,false)".format(QApplication.translate("Core","Sale investment product")))
            cur.execute("insert into conceptos values(37,'{0}',1,false)".format(QApplication.translate("Core","Taxes. Paid")))
            cur.execute("insert into conceptos values(38,'{0}',1,false)".format(QApplication.translate("Core","Bank commissions")))
            cur.execute("insert into conceptos values(39,'{0}',2,false)".format(QApplication.translate("Core","Dividends")))
            cur.execute("insert into conceptos values(40,'{0}',7,false)".format(QApplication.translate("Core","Credit card billing")))
            cur.execute("insert into conceptos values(43,'{0}',6,false)".format(QApplication.translate("Core","Added shares")))
            cur.execute("insert into conceptos values(50,'{0}',2,false)".format(QApplication.translate("Core","Attendance bonus")))
            cur.execute("insert into conceptos values(59,'{0}',1,false)".format(QApplication.translate("Core","Custody commission")))
            cur.execute("insert into conceptos values(62,'{0}',2,false)".format(QApplication.translate("Core","Dividends. Sale of rights")))
            cur.execute("insert into conceptos values(63,'{0}',1,false)".format(QApplication.translate("Core","Bonds. Running coupon payment")))
            cur.execute("insert into conceptos values(65,'{0}',2,false)".format(QApplication.translate("Core","Bonds. Running coupon collection")))
            cur.execute("insert into conceptos values(66,'{0}',2,false)".format(QApplication.translate("Core","Bonds. Coupon collection")))
            cur.execute("insert into conceptos values(67,'{0}',2,false)".format(QApplication.translate("Core","Credit card refund")))          
            cur.close()
#            return True
#        except:
#            print ("Error creating xulpymoney basic schema")
#            return False

        
class DBData:
    def __init__(self, mem):
        self.mem=mem

    def load(self, progress=True):
        """
            This method will subsitute load_actives and load_inactives
        """
        inicio=datetime.datetime.now()
        
        start=datetime.datetime.now()
        self.products=ProductManager(self.mem)
        self.products.load_from_db("select * from products", progress)
        print("DBData > Products took {}".format(datetime.datetime.now()-start))
        
        self.benchmark=self.products.find_by_id(int(self.mem.settingsdb.value("mem/benchmark", "79329" )))
        self.benchmark.needStatus(2)
        
        #Loading currencies
        start=datetime.datetime.now()
        self.currencies=ProductManager(self.mem)
        for p in self.products.arr:
            if p.type.id==6:
                p.needStatus(3)
                self.currencies.append(p)
        print("DBData > Currencies took {}".format(datetime.datetime.now()-start))
        
        self.banks=BankManager(self.mem)
        self.banks.load_from_db("select * from entidadesbancarias")

        self.accounts=AccountManager(self.mem, self.banks)
        self.accounts.load_from_db("select * from cuentas")

        self.creditcards=CreditCardManager(self.mem, self.accounts)
        self.creditcards.load_from_db("select * from tarjetas")

        self.investments=InvestmentManager(self.mem, self.accounts, self.products, self.benchmark)
        self.investments.load_from_db("select * from inversiones", progress)
        #change status to 1 to self.investments products
        pros=self.investments.ProductManager_with_investments_distinct_products()
        pros.needStatus(1, progress=True)
        
        logging.info("DBData loaded: {}".format(datetime.datetime.now()-inicio))

    def accounts_active(self):        
        r=AccountManager(self.mem, self.banks)
        for b in self.accounts.arr:
            if b.active==True:
                r.append(b)
        return r 

    def accounts_inactive(self):        
        r=AccountManager(self.mem, self.banks)
        for b in self.accounts.arr:
            if b.active==False:
                r.append(b)
        return r
        
    def banks_active(self):        
        r=BankManager(self.mem)
        for b in self.banks.arr:
            if b.active==True:
                r.append(b)
        return r        
        
    def banks_inactive(self):        
        r=BankManager(self.mem)
        for b in self.banks.arr:
            if b.active==False:
                r.append(b)
        return r        
        
    def creditcards_active(self):        
        r=CreditCardManager(self.mem, self.accounts)
        for b in self.creditcards.arr:
            if b.active==True:
                r.append(b)
        return r        
        
    def creditcards_inactive(self):        
        r=CreditCardManager(self.mem, self.accounts)
        for b in self.creditcards.arr:
            if b.active==False:
                r.append(b)
        return r
            
    def investments_active(self):        
        r=InvestmentManager(self.mem, self.accounts, self.products, self.benchmark)
        for b in self.investments.arr:
            if b.active==True:
                r.append(b)
        return r        
        
    def investments_inactive(self):        
        r=InvestmentManager(self.mem, self.accounts, self.products, self.benchmark)
        for b in self.investments.arr:
            if b.active==False:
                r.append(b)
        return r        

    def banks_set(self, active):
        """Function to point to list if is active or not"""
        if active==True:
            return self.banks_active()
        else:
            return self.banks_inactive()
            
    def accounts_set(self, active):
        """Function to point to list if is active or not"""
        if active==True:
            return self.accounts_active()
        else:
            return self.accounts_inactive()
    
    def investments_set(self, active):
        """Function to point to list if is active or not"""
        if active==True:
            return self.investments_active()
        else:
            return self.investments_inactive()

    def creditcards_set(self, active):
        """Function to point to list if is active or not"""
        if active==True:
            return self.creditcards_active()
        else:
            return self.creditcards_inactive()

        
class Dividend:
    def __init__(self, mem):
        self.mem=mem
        self.id=None
        self.investment=None
        self.bruto=None
        self.retencion=None
        self.neto=None
        self.dpa=None
        self.datetime=None
        self.opercuenta=None
        self.comision=None
        self.concepto=None#Puedeser 39 o 62 para derechos venta
        self.currency_conversion=None

    def __repr__(self):
        return ("Instancia de Dividend: {0} ({1})".format( self.neto, self.id))
        
    def init__create(self,  inversion,  bruto,  retencion, neto,  dpa,  fecha,  comision,  concepto, currency_conversion,  opercuenta=None,  id=None):
        """Opercuenta puede no aparecer porque se asigna al hacer un save que es cuando se crea. Si id=None,opercuenta debe ser None"""
        self.id=id
        self.investment=inversion
        self.bruto=bruto
        self.retencion=retencion
        self.neto=neto
        self.dpa=dpa
        self.datetime=fecha
        self.opercuenta=opercuenta
        self.comision=comision
        self.concepto=concepto
        self.currency_conversion=currency_conversion
        return self
        
    def init__db_row(self, row, inversion,  opercuenta,  concepto):
        return self.init__create(inversion,  row['bruto'],  row['retencion'], row['neto'],  row['valorxaccion'],  row['fecha'],   row['comision'],  concepto, row['currency_conversion'], opercuenta, row['id_dividends'])
        
    def init__db_query(self, id):
        """
            Searches in db dividend, investment from memory, operaccount from db
        """
        row=self.mem.con.cursor_one_row("select * from dividends where id_dividends=%s", (id, ))
        accountoperation=AccountOperation(self.mem,  row['id_opercuentas'])
        return self.init__db_row(row, self.mem.data.investments.find_by_id(row['id_inversiones']), accountoperation, self.mem.conceptos.find_by_id(row['id_conceptos']))
        
    def borrar(self):
        """Borra un dividend, para ello borra el registro de la tabla dividends 
            y el asociado en la tabla opercuentas
            
            También actualiza el balance de la cuenta."""
        cur=self.mem.con.cursor()
        self.opercuenta.borrar()
        cur.execute("delete from dividends where id_dividends=%s", (self.id, ))
        cur.close()
        
    def gross(self, type=1):
        if type==1:
            return Money(self.mem, self.bruto, self.investment.product.currency)
        elif type==2:
            return Money(self.mem, self.bruto, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion)
        elif type==3:
            return Money(self.mem, self.bruto, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion).local(self.datetime)
    def net(self, type=1):
        if type==1:
            return Money(self.mem, self.neto, self.investment.product.currency)
        elif type==2:
            return Money(self.mem, self.neto, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion)
        elif type==3:
            return Money(self.mem, self.neto, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion).local(self.datetime)
    def retention(self, type=1):
        if type==1:
            return Money(self.mem, self.retencion, self.investment.product.currency)
        elif type==2:
            return Money(self.mem, self.retencion, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion)
        elif type==3:
            return Money(self.mem, self.retencion, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion).local(self.datetime)
    def dps(self, type=1):
        "Dividend per share"
        if type==1:
            return Money(self.mem, self.dpa, self.investment.product.currency)
        elif type==2:
            return Money(self.mem, self.dpa, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion)
        elif type==3:
            return Money(self.mem, self.dpa, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion).local(self.datetime)
    def comission(self, type=1):
        if type==1:
            return Money(self.mem, self.comision, self.investment.product.currency)
        elif type==2:
            return Money(self.mem, self.comision, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion)
        elif type==3:
            return Money(self.mem, self.comision, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion).local(self.datetime)
            
        
    def neto_antes_impuestos(self):
        return self.bruto-self.comision
    
    def save(self):
        """Insertar un dividend y una opercuenta vinculada a la tabla dividends en el campo id_opercuentas
        
        En caso de que sea actualizar un dividend hay que actualizar los datos de opercuenta y se graba desde aquí. No desde el objeto opercuenta
        
        Actualiza la cuenta 
        """
        cur=self.mem.con.cursor()
        if self.id==None:#Insertar
            self.opercuenta=AccountOperation(self.mem,  self.datetime,self.concepto, self.concepto.tipooperacion, self.neto, "Transaction not finished", self.investment.account, None)
            self.opercuenta.save()
            cur.execute("insert into dividends (fecha, valorxaccion, bruto, retencion, neto, id_inversiones,id_opercuentas, comision, id_conceptos,currency_conversion) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) returning id_dividends", (self.datetime, self.dpa, self.bruto, self.retencion, self.neto, self.investment.id, self.opercuenta.id, self.comision, self.concepto.id, self.currency_conversion))
            self.id=cur.fetchone()[0]
            self.opercuenta.comentario=Comment(self.mem).setEncoded10004(self)
            self.opercuenta.save()
        else:
            self.opercuenta.datetime=self.datetime
            self.opercuenta.importe=self.neto
            self.opercuenta.comentario=Comment(self.mem).setEncoded10004(self)
            self.opercuenta.concepto=self.concepto
            self.opercuenta.tipooperacion=self.concepto.tipooperacion
            self.opercuenta.save()
            cur.execute("update dividends set fecha=%s, valorxaccion=%s, bruto=%s, retencion=%s, neto=%s, id_inversiones=%s, id_opercuentas=%s, comision=%s, id_conceptos=%s, currency_conversion=%s where id_dividends=%s", (self.datetime, self.dpa, self.bruto, self.retencion, self.neto, self.investment.id, self.opercuenta.id, self.comision, self.concepto.id, self.currency_conversion, self.id))
        cur.close()

class InvestmentOperation:
    def __init__(self, mem):
        self.mem=mem
        self.id=None
        self.tipooperacion=None
        self.investment=None
        self.shares=None
        self.impuestos=None
        self.comision=None
        self.valor_accion=None
        self.datetime=None
        self.comentario=None
        self.archivada=None
        self.currency_conversion=None
        self.show_in_ranges=True
        
    def __repr__(self):
        return ("IO {0} ({1}). {2} {3}. Acciones: {4}. Valor:{5}. IdObject: {6}. Currency conversion {7}".format(self.investment.name, self.investment.id,  self.datetime, self.tipooperacion.name,  self.shares,  self.valor_accion, id(self), self.currency_conversion))
        
        
    def init__db_row(self,  row, inversion,  tipooperacion):
        self.id=row['id_operinversiones']
        self.tipooperacion=tipooperacion
        self.investment=inversion
        self.shares=row['acciones']
        self.impuestos=row['impuestos']
        self.comision=row['comision']
        self.valor_accion=row['valor_accion']
        self.datetime=row['datetime']
        self.comentario=row['comentario']
        self.show_in_ranges=row['show_in_ranges']
        self.currency_conversion=row['currency_conversion']
        return self
        
    def init__create(self, tipooperacion, datetime, inversion, acciones,  impuestos, comision, valor_accion, comentario, show_in_ranges, currency_conversion,    id=None):
        self.id=id
        self.tipooperacion=tipooperacion
        self.datetime=datetime
        self.investment=inversion
        self.shares=acciones
        self.impuestos=impuestos
        self.comision=comision
        self.valor_accion=valor_accion
        self.comentario=comentario
        self.show_in_ranges=show_in_ranges
        self.currency_conversion=currency_conversion
        return self
        
    def init__from_accountoperation(self, accountoperation):
        """AccountOperation is a object, and must have id_conceptos share of sale or purchase. 
        IO returned is an object already created in investments_all()"""
        cur=self.mem.con.cursor()
        cur.execute("select id_inversiones,id_operinversiones from opercuentasdeoperinversiones where id_opercuentas=%s", (accountoperation.id, ))
        if cur.rowcount==0:
            cur.close()
            return None
        row=cur.fetchone()
        cur.close()
        investment=self.mem.data.investments.find_by_id(row['id_inversiones'])
        return investment.op.find(row['id_operinversiones'])
        
    def price(self, type=1):
        if type==1:
            return Money(self.mem, self.valor_accion, self.investment.product.currency)
        else:
            return Money(self.mem, self.valor_accion, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion)
            
    def gross(self, type=1):
        if type==1:
            return Money(self.mem, abs(self.shares*self.valor_accion), self.investment.product.currency)
        else:
            return Money(self.mem, abs(self.shares*self.valor_accion), self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion)
            
    def net(self, type=1):
        if self.shares>=Decimal(0):
            return self.gross(type)+self.comission(type)+self.taxes(type)
        else:
            return self.gross(type)-self.comission(type)-self.taxes(type)
            
    def taxes(self, type=1):
        if type==1:
            return Money(self.mem, self.impuestos, self.investment.product.currency)
        else:
            return Money(self.mem, self.impuestos, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion)
            
    def comission(self, type=1):
        if type==1:
            return Money(self.mem, self.comision, self.investment.product.currency)
        else:
            return Money(self.mem, self.comision, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion)

    def find_by_mem(self, investment, id):
        """
            Searchs in mem (needed investments_all())
            invesment is an Investment object
            id is the invesmentoperation to find
        """
        for i in self.mem.data.investments:
            if investment.id==i.id:
                found=i.op.find(id)
                if found!=None:
                    return found
        print ("Investment operation {} hasn't been found in mem".format(id))
        return None

    def actualizar_cuentaoperacion_asociada(self):
        """Esta función actualiza la tabla opercuentasdeoperinversiones que es una tabla donde 
        se almacenan las opercuentas automaticas por las operaciones con inversiones. Es una tabla 
        que se puede actualizar en cualquier momento con esta función"""
        self.comentario=Comment(self.mem).setEncoded10000(self)
        #/Borra de la tabla opercuentasdeoperinversiones los de la operinversión pasada como parámetro
        cur=self.mem.con.cursor()
        cur.execute("delete from opercuentasdeoperinversiones where id_operinversiones=%s",(self.id, )) 
        cur.close()
        if self.tipooperacion.id==4:#Compra Acciones
            #Se pone un registro de compra de acciones que resta el balance de la opercuenta
            importe=-self.gross(type=2)-self.comission(type=2)
            c=AccountOperationOfInvestmentOperation(self.mem, self.datetime, self.mem.conceptos.find_by_id(29), self.tipooperacion, importe.amount, self.comentario, self.investment.account, self,self.investment, None)
            c.save()
        elif self.tipooperacion.id==5:#// Venta Acciones
            #//Se pone un registro de compra de acciones que resta el balance de la opercuenta
            importe=self.gross(type=2)-self.comission(type=2)-self.taxes(type=2)
            c=AccountOperationOfInvestmentOperation(self.mem, self.datetime, self.mem.conceptos.find_by_id(35), self.tipooperacion, importe.amount, self.comentario, self.investment.account, self,self.investment, None)
            c.save()
        elif self.tipooperacion.id==6:
            #//Si hubiera comisión se añade la comisión.
            if(self.comision!=0):
                importe=-self.comission(type=2)-self.taxes(type=2)
                c=AccountOperationOfInvestmentOperation(self.mem, self.datetime, self.mem.conceptos.find_by_id(38), self.mem.tiposoperaciones.find_by_id(1), importe.amount, self.comentario, self.investment.account, self,self.investment, None)
                c.save()
    
    def copy(self, investment=None):
        """
            Crea una inversion operacion desde otra inversionoepracion. NO es un enlace es un objeto clone
            Si el parametro investment es pasado usa el objeto investment  en vez de una referencia a self.investmen
        """
        inv=self.investment if investment==None else investment
        return InvestmentOperation(self.mem).init__create(self.tipooperacion, self.datetime, inv , self.shares, self.impuestos, self.comision, self.valor_accion, self.comentario,  self.show_in_ranges, self.currency_conversion, self.id)

    def less_than_a_year(self):
        if datetime.date.today()-self.datetime.date()<=datetime.timedelta(days=365):
                return True
        return False
        
    def save(self, recalculate=True,  autocommit=True):
        cur=self.mem.con.cursor()
        if self.id==None:#insertar
            cur.execute("insert into operinversiones(datetime, id_tiposoperaciones,  acciones,  impuestos,  comision,  valor_accion, comentario, show_in_ranges, id_inversiones, currency_conversion) values (%s, %s, %s, %s, %s, %s, %s, %s,%s,%s) returning id_operinversiones", (self.datetime, self.tipooperacion.id, self.shares, self.impuestos, self.comision, self.valor_accion, self.comentario, self.show_in_ranges,  self.investment.id,  self.currency_conversion))
            self.id=cur.fetchone()[0]
            self.investment.op.append(self)
        else:
            cur.execute("update operinversiones set datetime=%s, id_tiposoperaciones=%s, acciones=%s, impuestos=%s, comision=%s, valor_accion=%s, comentario=%s, id_inversiones=%s, show_in_ranges=%s, currency_conversion=%s where id_operinversiones=%s", (self.datetime, self.tipooperacion.id, self.shares, self.impuestos, self.comision, self.valor_accion, self.comentario, self.investment.id, self.show_in_ranges,  self.currency_conversion,  self.id))
        if recalculate==True:
            (self.investment.op_actual,  self.investment.op_historica)=self.investment.op.calcular()   
            self.actualizar_cuentaoperacion_asociada()
        if autocommit==True:
            self.mem.con.commit()
        cur.close()
   
class Bank:
    """Clase que encapsula todas las funciones que se pueden realizar con una Entidad bancaria o banco"""
    def __init__(self, mem):
        """Constructor que inicializa los atributos a None"""
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
        return ("Instancia de Bank: {0} ({1})".format( self.name, self.id))

    def init__db_row(self, row):
        self.id=row['id_entidadesbancarias']
        self.name=row['entidadbancaria']
        self.active=row['active']
        return self
        
    def qmessagebox_inactive(self):
        if self.active==False:
            m=QMessageBox()
            m.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
            m.setIcon(QMessageBox.Information)
            m.setText(QApplication.translate("Core", "The associated bank is not active. You must activate it first"))
            m.exec_()    
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
        
    def balance(self, setcuentas,  setinversiones):
        resultado=Money(self, 0, self.mem.localcurrency)
        #Recorre balance cuentas
        for c in setcuentas.arr:
            if c.eb.id==self.id:
                resultado=resultado+c.balance().local()
        
        #Recorre balance inversiones
        for i in setinversiones.arr:
            if i.account.eb.id==self.id:
                resultado=resultado+i.balance().local()
        return resultado
        
    def es_borrable(self):
        """Función que devuelve un booleano si una cuenta es borrable, es decir, que no tenga registros dependientes."""
        #Recorre balance cuentas
        for c  in self.mem.data.accounts.arr:
            if c.eb.id==self.id:
                if c.es_borrable()==self.id:
                    return False
        return True
        
    def delete(self):
        """Función que borra. You must use es_borrable before"""
        cur=self.mem.con.cursor()
        cur.execute("delete from entidadesbancarias where id_entidadesbancarias=%s", (self.id, ))  
        cur.close()


## Class to manage everything relationed with bank accounts
class Account:
    ## Constructor with the following attributes combination
    ## 1. Account(mem, row, bank). Create an Account from a db row, generated in a database query
    ## 2. Account(mem, name, bank, active, numero, currency, id). Create account passing all attributes
    ## @param mem MemXulpymoney object
    ## @param row Dictionary of a database query cursor
    ## @param bank Bank object
    ## @param name Account name
    ## @param active Boolean that sets if the Account is active
    ## @param numero String with the account number
    ## @param currency Currency object that sets the currency of the Account
    ## @param id Integer that sets the id of an account. If id=None it's not in the database. id is set in the save method
    def __init__(self, *args):
        self.mem=args[0]
        if len(args)==3:
            self.id=args[1]['id_cuentas']
            self.name=args[1]['cuenta']
            self.eb=args[2]
            self.active=args[1]['active']
            self.numero=args[1]['numerocuenta']
            self.currency=self.mem.currencies.find_by_id(args[1]['currency'])            
        if len(args)==7:
            self.name=args[1]
            self.eb=args[2]
            self.active=args[3]
            self.numero=args[4]
            self.currency=args[5]
            self.id=args[6]

        
    def __repr__(self):
        return ("Instancia de Account: {0} ({1})".format( self.name, self.id))

    def balance(self,fecha=None, type=3):
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
            fecha=datetime.date.today()
        cur.execute('select sum(importe) from opercuentas where id_cuentas='+ str(self.id) +" and datetime::date<='"+str(fecha)+"';") 
        res=cur.fetchone()[0]
        cur.close()
        if res==None:
            return Money(self.mem, 0, self.resultsCurrency(type))
        if type==2:
            return Money(self.mem, res, self.currency)
        elif type==3:
            if fecha==None:
                dt=self.mem.localzone.now()
            else:
                dt=day_end_from_date(fecha, self.mem.localzone)
            return Money(self.mem, res, self.currency).convert(self.mem.localcurrency, dt)

    def save(self):
        cur=self.mem.con.cursor()
        if self.id==None:
            cur.execute("insert into cuentas (id_entidadesbancarias, cuenta, numerocuenta, active,currency) values (%s,%s,%s,%s,%s) returning id_cuentas", (self.eb.id, self.name, self.numero, self.active, self.currency.id))
            self.id=cur.fetchone()[0]
        else:
            cur.execute("update cuentas set cuenta=%s, id_entidadesbancarias=%s, numerocuenta=%s, active=%s, currency=%s where id_cuentas=%s", (self.name, self.eb.id, self.numero, self.active, self.currency.id, self.id))
        cur.close()

    def es_borrable(self):
        """Función que devuelve un booleano si una cuenta es borrable, es decir, que no tenga registros dependientes."""
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
        
    def borrar(self, cur):
        if self.es_borrable()==True:
            cur.execute("delete from cuentas where id_cuentas=%s", (self.id, ))

    def transferencia(self, datetime, cuentaorigen, cuentadestino, importe, comision):
        """Si el oc_comision_id es 0 es que no hay comision porque también es 0"""
        #Ojo los comentarios están dependientes.
        oc_comision=None
        notfinished="Tranfer not fully finished"
        if comision>0:
            oc_comision=AccountOperation(self.mem, datetime, self.mem.conceptos.find_by_id(38), self.mem.tiposoperaciones.find_by_id(1), -comision, notfinished, cuentaorigen, None)
            oc_comision.save()
        oc_origen=AccountOperation(self.mem, datetime, self.mem.conceptos.find_by_id(4), self.mem.tiposoperaciones.find_by_id(3), -importe, notfinished, cuentaorigen, None)
        oc_origen.save()
        oc_destino=AccountOperation(self.mem, datetime, self.mem.conceptos.find_by_id(5), self.mem.tiposoperaciones.find_by_id(3), importe, notfinished, cuentadestino, None)
        oc_destino.save()
        
        oc_origen.comentario=Comment(self.mem).setEncoded10001(oc_origen, oc_destino, oc_comision)
        oc_origen.save()
        oc_destino.comentario=Comment(self.mem).setEncoded10002(oc_origen, oc_destino, oc_comision)
        oc_destino.save()
        if oc_comision!=None:
            oc_comision.comentario=Comment(self.mem).setEncoded10003(oc_origen, oc_destino, oc_comision)
            oc_comision.save()

    def qmessagebox_inactive(self):
        if self.active==False:
            m=QMessageBox()
            m.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
            m.setIcon(QMessageBox.Information)
            m.setText(QApplication.translate("Core", "The associated account is not active. You must activate it first"))
            m.exec_()    
            return True
        return False

    def resultsCurrency(self, type ):
        if type==2:
            return self.currency
        elif type==3:
            return self.mem.localcurrency
        logging.critical("Rare account result currency: {}".format(type))

class Investment:
    """Clase que encapsula todas las funciones que se pueden realizar con una Inversión
    
    Las entradas al objeto pueden ser por:
        - init__db_row
        - init__db_extended_row
        - create. Solo contenedor hasta realizar un save y guardar en id, el id apropiado. mientras id=None
        
    """
    def __init__(self, mem):
        """Constructor que inicializa los atributos a None"""
        self.mem=mem
        self.id=None
        self.name=None
        self.venta=None
        self.product=None#Puntero a objeto MQInvestment
        self.account=None#Vincula a un objeto  Account
        self.active=None
        self.op=None#Es un objeto SetInvestmentOperations
        self.op_actual=None#Es un objeto Setoperinversionesactual
        self.op_historica=None#setoperinversioneshistorica
        self.selling_expiration=None
        self.merge=0#Used for mergin investments. 0 normal investment, 1 merging current operations, 2 merging operations

    def init__create(self, name, venta, cuenta, inversionmq, selling_expiration, active, id=None):
        self.name=name
        self.venta=venta
        self.account=cuenta
        self.product=inversionmq
        self.active=active
        self.selling_expiration=selling_expiration
        self.id=id
        return self

    def copy(self ):
        return Investment(self.mem).init__create(self.name, self.venta, self.account, self.product, self.selling_expiration, self.active, self.id)
    
    def save(self):
        """Inserta o actualiza la inversión dependiendo de si id=None o no"""
        cur=self.mem.con.cursor()
        if self.id==None:
            cur.execute("insert into inversiones (inversion, venta, id_cuentas, active, selling_expiration,products_id) values (%s, %s,%s,%s,%s,%s) returning id_inversiones", (self.name, self.venta, self.account.id, self.active, self.selling_expiration,  self.product.id))    
            self.id=cur.fetchone()[0]                
        else:
            cur.execute("update inversiones set inversion=%s, venta=%s, id_cuentas=%s, active=%s, selling_expiration=%s, products_id=%s where id_inversiones=%s", (self.name, self.venta, self.account.id, self.active, self.selling_expiration,  self.product.id, self.id))
        cur.close()

    def selling_price(self, type=1):
        if type==1:
            return Money(self.mem, self.venta, self.product.currency)

    def setDividends_from_current_operations(self):
        """
            Returns a setDividens from the datetime of the first currnt operation
        """
        first=self.op_actual.first()
        set=DividendHomogeneusManager(self.mem, self)
        if first!=None:
            set.load_from_db("select * from dividends where id_inversiones={0} and fecha >='{1}'  order by fecha".format(self.id, first.datetime))
        return set

    def setDividends_from_operations(self):
        """
            Returns a setDividens with all the dividends
        """
        set=DividendHomogeneusManager(self.mem, self)
        set.load_from_db("select * from dividends where id_inversiones={0} order by fecha".format(self.id ))  
        return set

    def __repr__(self):
        return ("Instancia de Investment: {0} ({1})".format( self.name, self.id))
        
    def init__db_row(self, row, cuenta, mqinvestment):
        self.id=row['id_inversiones']
        self.name=row['inversion']
        self.venta=row['venta']
        self.account=cuenta
        self.product=mqinvestment
        self.active=row['active']
        self.selling_expiration=row['selling_expiration']
        return self


    def es_borrable(self):
        """Función que devuelve un booleano si una cuenta es borrable, es decir, que no tenga registros dependientes."""
        if self.op.length()>0:
            return False
        if self.setDividends_from_operations().length()>0:
            return False
        return True
        

    def actualizar_cuentasoperaciones_asociadas(self):
        #Borra las opercuentasdeoperinversiones de la inversión actual
        cur=self.mem.con.cursor()
        cur.execute("delete from opercuentasdeoperinversiones where id_inversiones=%s", (self.id, ));
        cur.close()
        for o in self.op.arr:
            o.actualizar_cuentaoperacion_asociada()
            
    def borrar(self):
        cur=self.mem.con.cursor()
        cur.execute("delete from inversiones where id_inversiones=%s", (self.id, ))
        cur.close()

    def resultsCurrency(self, type=1 ):
        if type==1:
            return self.product.currency
        elif type==2:
            return self.account.currency
        elif type==3:
            return self.mem.localcurrency
        logging.critical("Rare investment result currency: {}".format(type))

    def quote2money(self, quote,  type=1):
        """
            Converts a quote object to a money. Then shows money with the currency type
        """        
        if quote==None:
            return None
            
        if quote.product.currency.id!=self.product.currency.id:
            logging.error("I can't convert a quote to money, if quote product is diferent to investment product")
            return None
            
        if type==1:
            return Money(self.mem, quote.quote, self.product.currency)
        elif type==2:
            return Money(self.mem, quote.quote, self.product.currency).convert(self.account.currency, quote.datetime)
        elif type==3:
            return  Money(self.mem, quote.quote, self.product.currency).convert(self.account.currency, quote.datetime).local(quote.datetime)
    
    def get_operinversiones(self, date=None):
        """Funci`on que carga un array con objetos inversion operacion y con ellos calcula el set de actual e historicas
        date is used to get invested balance in a particular date"""
        cur=self.mem.con.cursor()
        self.op=InvestmentOperationHomogeneusManager(self.mem, self)
        if date==None:
            cur.execute("select * from operinversiones where id_inversiones=%s order by datetime", (self.id, ))
        else:
            cur.execute("select * from operinversiones where id_inversiones=%s and datetime::date<=%s order by datetime", (self.id, date))
        for row in cur:
            self.op.append(InvestmentOperation(self.mem).init__db_row(row, self, self.mem.tiposoperaciones.find_by_id(row['id_tiposoperaciones'])))
        (self.op_actual,  self.op_historica)=self.op.calcular()
        
        cur.close()
        

    
    def dividend_bruto_estimado(self, year=None):
        """
            Si el year es None es el año actual
            Calcula el dividend estimado de la inversion se ha tenido que cargar:
                - El inversiones mq
                - La estimacion de dividends mq"""
        if year==None:
            year=datetime.date.today().year
        try:
            return Money(self.mem, self.shares()*self.product.estimations_dps.find(year).estimation, self.product.currency)
        except:
            return Money(self.mem, 0, self.product.currency)


    def shares(self, fecha=None):
        """Función que saca el número de acciones de las self.op_actual"""
        if fecha==None:
            dat=self.mem.localzone.now()
        else:
            dat=day_end_from_date(fecha, self.mem.localzone)
        resultado=Decimal('0')

        for o in self.op.arr:
            if o.datetime<=dat:
                resultado=resultado+o.shares
        return resultado
        
    def hasSameAccountCurrency(self):
        """
            Returns a boolean
            Check if investment currency is the same that account currency
        """
        if self.product.currency.id==self.account.currency.id:
            return True
        return False
        
    def qmessagebox_inactive(self):
        if self.active==False:
            m=QMessageBox()
            m.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
            m.setIcon(QMessageBox.Information)
            m.setText(QApplication.translate("Core", "The associated product is not active. You must activate it first"))
            m.exec_()    
            return True
        return False

    def questionbox_inactive(self):
        """It makes a database commit"""
        if self.active==False:
            reply = QMessageBox.question(None, QApplication.translate("Core", 'Investment activation question'), QApplication.translate("Core", "Investment {} ({}) is inactive.\nDo you want to activate it?").format(self.name, self.account.name), QMessageBox.Yes, QMessageBox.No)          
            if reply==QMessageBox.Yes:
                self.active=True
                self.save()
                self.mem.con.commit()
                return QMessageBox.Yes
            return QMessageBox.No
        return QMessageBox.Yes
        
    def balance(self, fecha=None, type=1):
        """Función que calcula el balance de la inversión
            Si el cur es None se calcula el actual 
                Necesita haber cargado mq getbasic y operinversionesactual"""     
        acciones=self.shares(fecha)
        currency=self.resultsCurrency(type)
        if acciones==0 or self.product.result.basic.last.quote==None:#Empty xulpy
            return Money(self.mem, 0, currency)
                
        if fecha==None:
            return self.op_actual.balance(self.product.result.basic.last, type)
        else:
            quote=Quote(self.mem).init__from_query(self.product, day_end_from_date(fecha, self.mem.localzone))
            if quote.datetime==None:
                print ("Investment balance: {0} ({1}) en {2} no tiene valor".format(self.name, self.product.id, fecha))
                return Money(self.mem, 0, self.product.currency)
            return Money(self.mem, acciones*self.quote2money(quote, type).amount, currency)
        
    def invertido(self, date=None, type=1):
        """Función que calcula el balance invertido partiendo de las acciones y el precio de compra
        Necesita haber cargado mq getbasic y operinversionesactual"""
        if date==None or date==datetime.date.today():#Current
            return self.op_actual.invertido(type)
        else:
            # Creo una vinversion fake para reutilizar codigo, cargando operinversiones hasta date
            invfake=Investment(self.mem).copy()
            invfake.op=self.op.copy_until_datetime(day_end_from_date(date, self.mem.localzone), self.mem, invfake)
            (invfake.op_actual,  invfake.op_historica)=invfake.op.calcular()
            return invfake.op_actual.invertido(type)
                
    def percentage_to_selling_point(self):       
        """Función que calcula el tpc venta partiendo de las el last y el valor_venta
        Necesita haber cargado mq getbasic y operinversionesactual"""
        if self.venta==0 or self.venta==None:
            return Percentage()
        return Percentage(self.venta-self.product.result.basic.last.quote, self.product.result.basic.last.quote)


class CreditCard:    
    def __init__(self, mem):
        self.mem=mem
        self.id=None
        self.name=None
        self.account=None
        self.pagodiferido=None
        self.saldomaximo=None
        self.active=None
        self.numero=None
           
    def init__create(self, name, cuenta, pagodiferido, saldomaximo, activa, numero, id=None):
        """El parámetro cuenta es un objeto cuenta, si no se tuviera en tiempo de creación se asigna None"""
        self.id=id
        self.name=name
        self.account=cuenta
        self.pagodiferido=pagodiferido
        self.saldomaximo=saldomaximo
        self.active=activa
        self.numero=numero
        return self
        
    def init__db_row(self, row, cuenta):
        """El parámetro cuenta es un objeto cuenta, si no se tuviera en tiempo de creación se asigna None"""
        self.init__create(row['tarjeta'], cuenta, row['pagodiferido'], row['saldomaximo'], row['active'], row['numero'], row['id_tarjetas'])
        return self
                    
    def __repr__(self):
        return "CreditCard: {}".format(self.id)
    def delete(self):
        cur=self.mem.con.cursor()
        cur.execute("delete from tarjetas where id_tarjetas=%s", (self.id, ))
        cur.close()
        
    def is_deletable(self):
        """
            Devuelve False si no puede borrarse por haber dependientes.
        """
        res=0
        cur=self.mem.con.cursor()
        cur.execute("select count(*) from opertarjetas where id_tarjetas=%s", (self.id, ))
        res=cur.fetchone()[0]
        cur.close()
        if res==0:
            return True
        else:
            return False
        
    def qmessagebox_inactive(self):
        if self.active==False:
            m=QMessageBox()
            m.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
            m.setIcon(QMessageBox.Information)
            m.setText(QApplication.translate("Core", "The associated credit card is not active. You must activate it first"))
            m.exec_()    
            return True
        return False
        
    def save(self):
        cur=self.mem.con.cursor()
        if self.id==None:
            cur.execute("insert into tarjetas (tarjeta,id_cuentas,pagodiferido,saldomaximo,active,numero) values (%s, %s, %s,%s,%s,%s) returning id_tarjetas", (self.name, self.account.id,  self.pagodiferido ,  self.saldomaximo, self.active, self.numero))
            self.id=cur.fetchone()[0]
        else:
            cur.execute("update tarjetas set tarjeta=%s, id_cuentas=%s, pagodiferido=%s, saldomaximo=%s, active=%s, numero=%s where id_tarjetas=%s", (self.name, self.account.id,  self.pagodiferido ,  self.saldomaximo, self.active, self.numero, self.id))

        cur.close()
        
    def saldo_pendiente(self):
        """Es el balance solo de operaciones difreidas sin pagar"""
        cur=self.mem.con.cursor()
        cur.execute("select sum(importe) from opertarjetas where id_tarjetas=%s and pagado=false;", [self.id])
        result=cur.fetchone()[0]
        cur.close()
        if result==None:
            result=Decimal(0)
        return result

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
            self.init__db_row(row, concepto, concepto.tipooperacion, self.mem.data.creditcards.find_by_id(row['id_tarjetas']))
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

## Class that register a purchase opportunity
class Opportunity:
    ## Constructor with the following attributes combination
    ## 1. Opportunity(mem). Crete a Opportunity object with all attributes set to None
    ## 1. Opportunity(mem, row). Create an Opportunity from a db row, generated in a database query
    ## 2. Opportunity(mem, date, removed, executed, price, products_id, id). Create a Opportunity passing all attributes
    ## @param mem MemXulpymoney object
    ## @param row Dictionary of a database query cursor
    ## @param date datetime.date object with the date of the Opportunity
    ## @param removed datetime.date object when the Opportunity was removed
    ## @param executed datetime.date object when the Opportunity was executed
    ## @param price decimal.Decimal object with the Opportunity price
    ## @param products_id Integer with the product id, after the constructur this integer is converted to self.product using mem
    ## @param id Integer that sets the id of an Opportunity. If id=None it's not in the database. id is set in the save method
    def __init__(self, *args):
        def init__db_row( row):
            init__create(row['date'], row['removed'], row['executed'], row['price'], row['products_id'], row['id'])
        def init__create(date, removed, executed, price, products_id, id):
            self.date=date
            self.removed=removed
            self.executed=executed
            self.price=price
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
            cur.execute("insert into opportunities(date, removed, executed, price, products_id) values (%s, %s, %s, %s, %s) returning id", 
            (self.date,  self.removed, self.executed, self.price, self.product.id))
            self.id=cur.fetchone()[0]
        else:
            cur.execute("update opportunities set date=%s, removed=%s, executed=%s, price=%s, products_id=%s where id=%s", (self.date,  self.removed, self.executed, self.price, self.product.id, self.id))
        if autocommit==True:
            self.mem.con.commit()
        cur.close()
        
    def remove(self):
        cur=self.mem.con.cursor()
        cur.execute("delete from opportunities where id=%s", (self.id, ))
        cur.close()
        
    ##Calculates percentage from current price to order price
    def percentage_from_current_price(self):
        return Percentage(self.price-self.product.result.basic.last.quote, self.product.result.basic.last.quote)


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
        table.setHorizontalHeaderItem(4, QTableWidgetItem(QApplication.translate("Core","Opportunity price")))
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
            table.setItem(i, 4, p.product.currency.qtablewidgetitem(p.price))
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


class Order:
    def __init__(self, mem):
        self.mem=mem
        self.id=None
        self.date=None
        self.expiration=None
        self.amount=None
        self.price=None
        self.shares=None
        self.investment=None
        self.executed=None
        
    def init__db_row(self, row):
        self.id=row['id']
        self.date=row['date']
        self.expiration=row['expiration']
        self.amount=row['amount']
        self.price=row['price']
        self.shares=row['shares']
        self.investment=self.mem.data.investments.find_by_id(row['investments_id'])
        self.executed=row['executed']
        return self
        
    def is_in_force(self):
        "Está vigente"
        if self.is_expired()==False and self.is_executed()==False:
            return True
        return False

    def is_expired(self):
        if self.expiration<datetime.date.today():
            return True
        return False
        
    def is_executed(self):
        if self.executed!=None:
            return True
        return False

    def save(self, autocommit=False):
        cur=self.mem.con.cursor()
        if self.id==None:#insertar
            cur.execute("insert into orders(date, expiration, amount, shares, price,investments_id, executed) values (%s, %s, %s, %s, %s, %s, %s) returning id", (self.date,  self.expiration, self.amount, self.shares, self.price, self.investment.id, self.executed))
            self.id=cur.fetchone()[0]
        else:
            cur.execute("update orders set date=%s, expiration=%s, amount=%s, shares=%s, price=%s, investments_id=%s, executed=%s where id=%s", (self.date,  self.expiration, self.amount, self.shares, self.price, self.investment.id, self.executed, self.id))
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
        m=QMessageBox()
        m.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
        m.setIcon(QMessageBox.Information)
        m.setText(QApplication.translate("Core","Don't forget to tell your bank to add and order for:\n{} ({})\n{} {} shares to {}".format(self.investment.name, self.investment.account.name, type, abs(self.shares), self.investment.product.currency.string(self.price, 6))))
        m.exec_()   
        
    def percentage_from_current_price(self):
        """Calculates percentage from current price to order price"""
        return Percentage(self.price-self.investment.product.result.basic.last.quote, self.investment.product.result.basic.last.quote)
        
class OperationType:
    def __init__(self):
        self.id=None
        self.name=None
        
    def init__create(self, name,  id=None):
        self.id=id
        self.name=name
        return self

class AnnualTarget:
    def __init__(self, mem):
        self.mem=mem
        self.year=None
        self.percentage=None
        self.lastyear_assests=None
        self.saved_in_db=False #Controls if AnnualTarget is saved in the table annualtargets
    
    ## Fills the object with data from db.
    ## If lastyear_assests=None it gets the assests from db
    def init__from_db(self, year, lastyear_assests=None):
        cur=self.mem.con.cursor()
        
        if lastyear_assests==None:
            self.lastyear_assests=Assets(self.mem).saldo_total(self.mem.data.investments,  datetime.date(year-1, 12, 31))
        else:
            self.lastyear_assests=lastyear_assests
        
        cur.execute("select * from annualtargets where year=%s", (year, ))
        if cur.rowcount==0:
            self.year=year
            self.percentage=0
        else:
            row=cur.fetchone()
            self.year=year
            self.percentage=row['percentage']
            self.saved_in_db=True
        cur.close()
        return self
        
    def save(self):
        cur=self.mem.con.cursor()
        if self.saved_in_db==False:
            cur.execute("insert into annualtargets (year, percentage) values (%s,%s)", (self.year, self.percentage))
            self.saved_in_db=True
        else:
            cur.execute("update annualtargets set percentage=%s where year=%s", (self.percentage, self.year))
        cur.close()
        
    ## Returns the amount of tthe annual target
    def annual_balance(self):
        return self.lastyear_assests.amount*self.percentage/100
        
    ## Returns the amount of the monthly target (annual/12)
    def monthly_balance(self):
        return self.annual_balance()/12

class Assets:
    def __init__(self, mem):
        self.mem=mem        
    
    ## Devuelve la datetime actual si no hay datos. Base de datos vacía
    def first_datetime_with_user_data(self):        
        cur=self.mem.con.cursor()
        sql='select datetime from opercuentas UNION all select datetime from operinversiones UNION all select datetime from opertarjetas order by datetime limit 1;'
        cur.execute(sql)
        if cur.rowcount==0:
            return datetime.datetime.now()
        resultado=cur.fetchone()[0]
        cur.close()
        return resultado

    def saldo_todas_cuentas(self,  datetime=None):
        """Si cur es none y datetime calcula el balance actual."""
        cur=self.mem.con.cursor()
        cur.execute("select cuentas_saldo('"+str(datetime)+"') as balance")
        resultado=cur.fetchone()[0] 
        cur.close()
        return Money(self.mem, resultado, self.mem.localcurrency)

        
    def saldo_total(self, setinversiones,  datetime):
        """Versión que se calcula en cliente muy optimizada"""
        return self.saldo_todas_cuentas(datetime)+self.saldo_todas_inversiones(setinversiones, datetime)

        
    def saldo_todas_inversiones(self, setinversiones,   fecha):
        """Versión que se calcula en cliente muy optimizada"""
        resultado=Money(self.mem, 0, self.mem.localcurrency)
        for i in setinversiones.arr:
            resultado=resultado+i.balance(fecha, type=3)
        return resultado

        
    def saldo_todas_inversiones_riesgo_cero(self, setinversiones, fecha=None):
        """Versión que se calcula en cliente muy optimizada
        Fecha None calcula  el balance actual
        """
        resultado=Money(self.mem, 0, self.mem.localcurrency)
        #        inicio=datetime.datetime.now()
        for inv in setinversiones.arr:
            if inv.product.percentage==0:        
                resultado=resultado+inv.balance( fecha, type=3)
        #        print ("core > Total > saldo_todas_inversiones_riego_cero: {0}".format(datetime.datetime.now()-inicio))
        return resultado
            
    def dividends_neto(self, ano,  mes=None):
        """Dividend cobrado en un año y mes pasado como parámetro, independientemente de si la inversión esta activa o no.
        El 63 es un gasto aunque también este registrado en dividends."""
        r=Money(self.mem, 0, self.mem.localcurrency)
        for inv in self.mem.data.investments.arr:
            setdiv=DividendHomogeneusManager(self.mem, inv)
            if mes==None:#Calcula en el año
                setdiv.load_from_db("select * from dividends where id_conceptos not in (63) and  date_part('year',fecha)={} and id_inversiones={}".format(ano, inv.id))
            else:
                setdiv.load_from_db("select * from dividends where id_conceptos not in (63) and  date_part('year',fecha) ={} and date_part('month',fecha)={} and id_inversiones={}".format(ano, mes, inv.id))
            r=r+setdiv.net(type=3)
        return r

    def dividends_bruto(self,  ano,  mes=None):
        """Dividend cobrado en un año y mes pasado como parámetro, independientemente de si la inversión esta activa o no"""
        r=Money(self.mem, 0, self.mem.localcurrency)
        for inv in self.mem.data.investments.arr:
            setdiv=DividendHomogeneusManager(self.mem, inv)
            if mes==None:#Calcula en el año
                setdiv.load_from_db("select * from dividends where id_conceptos not in (63) and  date_part('year',fecha)={} and id_inversiones={}".format(ano, inv.id))
            else:
                setdiv.load_from_db("select * from dividends where id_conceptos not in (63) and  date_part('year',fecha) ={} and date_part('month',fecha)={} and id_inversiones={}".format(ano, mes, inv.id))
            r=r+setdiv.gross(type=3)
        return r
        
        
    def invested(self, date=None):
        """Devuelve el patrimonio invertido en una determinada fecha"""
        if date==None or date==datetime.date.today():
            array=self.mem.data.investments_active().arr #Current and active
        else:
            array=self.mem.data.investments.arr#All, because i don't know witch one was active.
        
        r=Money(self.mem, 0, self.mem.localcurrency)
        for inv in array:
            r=r+inv.invertido(date, type=3)
        return r
        
    def saldo_todas_inversiones_bonds(self, fecha=None):        
        """Versión que se calcula en cliente muy optimizada
        Fecha None calcula  el balance actual
        """
        resultado=Money(self.mem, 0, self.mem.localcurrency)
        #        inicio=datetime.datetime.now()
        for inv in self.mem.data.investments.arr:
            print (inv,  inv.product)
            if inv.product.type.id in (eProductType.PublicBond, eProductType.PrivateBond):#public and private bonds        
                if fecha==None:
                    resultado=resultado+inv.balance().local()
                else:
                    resultado=resultado+inv.balance( fecha).local()
        #        print ("core > Assets > saldo_todas_inversiones_bonds: {0}".format(datetime.datetime.now()-inicio))
        return resultado

    def patrimonio_riesgo_cero(self, setinversiones, fecha):
        """CAlcula el patrimonio de riego cero"""
        return self.saldo_todas_cuentas(fecha)+self.saldo_todas_inversiones_riesgo_cero(setinversiones, fecha)

    def saldo_anual_por_tipo_operacion(self,  year,  id_tiposoperaciones):   
        """Opercuentas y opertarjetas"""
        resultado=Money(self.mem, 0, self.mem.localcurrency)
        for currency in self.mem.currencies.arr:
            cur=self.mem.con.cursor()
            sql="""
                select sum(Importe) as importe 
                from 
                    opercuentas,
                    cuentas
                where 
                    id_tiposoperaciones={0} and 
                    date_part('year',datetime)={1} and
                    cuentas.currency='{2}' and
                    cuentas.id_cuentas=opercuentas.id_cuentas   
            union all 
                select sum(Importe) as importe 
                from 
                    opertarjetas ,
                    tarjetas,
                    cuentas
                where 
                    id_tiposoperaciones={0} and 
                    date_part('year',datetime)={1} and
                    cuentas.currency='{2}' and
                    cuentas.id_cuentas=tarjetas.id_cuentas and
                    tarjetas.id_tarjetas=opertarjetas.id_tarjetas""".format(id_tiposoperaciones, year,  currency.id)
            cur.execute(sql)        
            for i in cur:
                if i['importe']==None:
                    continue
                resultado=resultado+Money(self.mem, i['importe'], currency).local()
            cur.close()
        return resultado

    def saldo_por_tipo_operacion(self,  year,  month,  id_tiposoperaciones):   
        """Opercuentas y opertarjetas"""
        resultado=Money(self.mem, 0, self.mem.localcurrency)
        for currency in self.mem.currencies.arr:
            cur=self.mem.con.cursor()
            sql="""
                select sum(Importe) as importe 
                from 
                    opercuentas,
                    cuentas
                where 
                    id_tiposoperaciones={0} and 
                    date_part('year',datetime)={1} and
                    date_part('month',datetime)={2} and
                    cuentas.currency='{3}' and
                    cuentas.id_cuentas=opercuentas.id_cuentas   
            union all 
                select sum(Importe) as importe 
                from 
                    opertarjetas ,
                    tarjetas,
                    cuentas
                where 
                    id_tiposoperaciones={0} and 
                    date_part('year',datetime)={1} and
                    date_part('month',datetime)={2} and
                    cuentas.currency='{3}' and
                    cuentas.id_cuentas=tarjetas.id_cuentas and
                    tarjetas.id_tarjetas=opertarjetas.id_tarjetas""".format(id_tiposoperaciones, year, month,  currency.id)
            cur.execute(sql)        
            for i in cur:
                if i['importe']==None:
                    continue
                resultado=resultado+Money(self.mem, i['importe'], currency).local()
            cur.close()
        return resultado
        
    def consolidado_bruto(self, setinversiones,  year=None, month=None):
        """Si year es none calcula el historicca  si month es nonve calcula el anual sino el mensual"""
        resultado=Money(self.mem, 0, self.mem.localcurrency)
        for i in setinversiones.arr:        
            resultado=resultado+i.op_historica.consolidado_bruto(year, month)
        return resultado
    def consolidado_neto_antes_impuestos(self, setinversiones, year=None, month=None):
        """Si year es none calcula el historicca  si month es nonve calcula el anual sino el mensual"""
        resultado=Money(self.mem, 0, self.mem.localcurrency)
        for i in setinversiones.arr:        
            resultado=resultado+i.op_historica.consolidado_neto_antes_impuestos(year, month)
        return resultado
        
                
    def consolidado_neto(self, setinversiones, year=None, month=None):
        """Si year es none calcula el historicca  si month es nonve calcula el anual sino el mensual"""
        resultado=Money(self.mem, 0, self.mem.localcurrency)
        for i in setinversiones.arr:        
            resultado=resultado+i.op_historica.consolidado_neto(year, month).local()
        return resultado        


class CreditCardManager(ObjectManager_With_IdName_Selectable):
    def __init__(self, mem, cuentas):
        ObjectManager_With_IdName_Selectable.__init__(self)
        self.mem=mem   
        self.accounts=cuentas

            
    def delete(self, creditcard):
        """Deletes from db and removes object from array.
        creditcard is an object"""
        creditcard.delete()
        self.remove(creditcard)


    def load_from_db(self, sql):
        cur=self.mem.con.cursor()
        cur.execute(sql)#"Select * from tarjetas")
        for row in cur:
            t=CreditCard(self.mem).init__db_row(row, self.accounts.find_by_id(row['id_cuentas']))
            self.append(t)
        cur.close()
        
    def myqtablewidget(self, table):
        table.applySettings()
        table.setRowCount(self.length())        
        for i, t in enumerate(self.arr):
            table.setItem(i, 0, QTableWidgetItem(t.name))
            table.setItem(i, 1, QTableWidgetItem(str(t.numero)))
            table.setItem(i, 2, qbool(t.active))
            table.setItem(i, 3, qbool(t.pagodiferido))
            table.setItem(i, 4, t.account.currency.qtablewidgetitem(t.saldomaximo ))
            table.setItem(i, 5, t.account.currency.qtablewidgetitem(t.saldo_pendiente()))
            if self.selected!=None:
                if t.id==self.selected.id:
                    table.selectRow(i)
            
    def clone_of_account(self, cuenta):
        """Devuelve un CreditCardManager con las tarjetas de una determinada cuenta"""
        s=CreditCardManager(self.mem, self.accounts)
        for t in self.arr:
            if t.account==cuenta:
                s.arr.append(t)
        return s

    def qcombobox(self, combo,  selected=None):
        """Load set items in a comobo using id and name
        Selected is and object
        It sorts by name the arr""" 
        self.order_by_name()
        combo.clear()
        for a in self.arr:
            combo.addItem("{} ({})".format(a.name, a.numero), a.id)

        if selected!=None:
            combo.setCurrentIndex(combo.findData(selected.id))

class CreditCardOperationManager(ObjectManager_With_IdDatetime_Selectable):
    def __init__(self, mem):
        ObjectManager_With_IdDatetime_Selectable.__init__(self)
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
            co=CreditCardOperation(self.mem).init__db_row(row, self.mem.conceptos.find_by_id(row['id_conceptos']), self.mem.tiposoperaciones.find_by_id(row['id_tiposoperaciones']), self.mem.data.creditcards.find_by_id(row['id_tarjetas']), AccountOperation(self.mem,  row['id_opercuentas']))
            self.append(co)
        cur.close()
        
    def myqtablewidget(self, tabla):
        """Section es donde guardar en el config file, coincide con el nombre del formulario en el que está la tabla
        show_accounts muestra la cuenta cuando las opercuentas son de diversos cuentas (Estudios totales)"""
        ##HEADERS
        tabla.setColumnCount(5)
        tabla.setHorizontalHeaderItem(0, QTableWidgetItem(QApplication.translate("Core","Date" )))
        tabla.setHorizontalHeaderItem(1, QTableWidgetItem(QApplication.translate("Core","Concept" )))
        tabla.setHorizontalHeaderItem(2,  QTableWidgetItem(QApplication.translate("Core","Amount" )))
        tabla.setHorizontalHeaderItem(3, QTableWidgetItem(QApplication.translate("Core","Balance" )))
        tabla.setHorizontalHeaderItem(4, QTableWidgetItem(QApplication.translate("Core","Comment" )))
        ##DATA 
        tabla.applySettings()
        tabla.clearContents()   
        tabla.setRowCount(self.length())
        balance=Decimal(0)
        self.order_by_datetime()
        for rownumber, a in enumerate(self.arr):
            balance=balance+a.importe
            tabla.setItem(rownumber, 0, qdatetime(a.datetime, self.mem.localzone))
            tabla.setItem(rownumber, 1, qleft(a.concepto.name))
            tabla.setItem(rownumber, 2, self.mem.localcurrency.qtablewidgetitem(a.importe))
            tabla.setItem(rownumber, 3, self.mem.localcurrency.qtablewidgetitem(balance))
            tabla.setItem(rownumber, 4, qleft(Comment(self.mem).setFancy(a.comentario)))
            if self.selected: #If selected is not necesary is None by default
                if self.selected.length()>0:
                    for sel in self.selected.arr:
                        if a.id==sel.id:
                            tabla.selectRow(rownumber)

class OperationTypeManager(DictObjectManager_With_IdName_Selectable):
    def __init__(self, mem):
        DictObjectManager_With_IdName_Selectable.__init__(self)
        self.mem=mem     

    def load(self):
        self.append(OperationType().init__create( QApplication.translate("Core","Expense"),  eOperationType.Expense))
        self.append(OperationType().init__create( QApplication.translate("Core","Income"), eOperationType.Income))
        self.append(OperationType().init__create( QApplication.translate("Core","Transfer"), eOperationType.Transfer))
        self.append(OperationType().init__create( QApplication.translate("Core","Purchase of shares"), eOperationType.SharesPurchase))
        self.append(OperationType().init__create( QApplication.translate("Core","Sale of shares"), eOperationType.SharesSale))
        self.append(OperationType().init__create( QApplication.translate("Core","Added of shares"), eOperationType.SharesAdd))
        self.append(OperationType().init__create( QApplication.translate("Core","Credit card billing"), eOperationType.CreditCardBilling))
        self.append(OperationType().init__create( QApplication.translate("Core","Transfer of funds"), eOperationType.TransferFunds)) #Se contabilizan como ganancia
        self.append(OperationType().init__create( QApplication.translate("Core","Transfer of shares. Origin"), eOperationType.TransferSharesOrigin)) #No se contabiliza
        self.append(OperationType().init__create( QApplication.translate("Core","Transfer of shares. Destiny"), eOperationType.TransferSharesDestiny)) #No se contabiliza     


    def qcombobox_basic(self, combo,  selected=None):
        """Load lust some items
        Selected is and object
        It sorts by name the arr""" 
        combo.clear()
        for n in (eOperationType.Expense, eOperationType.Income):
            a=self.find_by_id(str(n))
            combo.addItem(a.name, a.id)

        if selected!=None:
            combo.setCurrentIndex(combo.findData(selected.id))
            
            
    def qcombobox_investments_operations(self, combo,  selected=None):
        """Load lust some items
        Selected is and object
        It sorts by name the arr""" 
        combo.clear()
        for n in (eOperationType.SharesPurchase, eOperationType.SharesSale, eOperationType.SharesAdd, eOperationType.TransferFunds):
            a=self.find_by_id(str(n))
            combo.addItem(a.name, a.id)

        if selected!=None:
            combo.setCurrentIndex(combo.findData(selected.id))

class AgrupationManager(ObjectManager_With_IdName_Selectable):
    """Se usa para meter en mem las agrupaciones, pero también para crear agrupaciones en las inversiones"""
    def __init__(self, mem):
        """Usa la variable mem.Agrupations"""
        ObjectManager_With_IdName_Selectable.__init__(self)
        self.mem=mem

    def load_all(self):
        self.append(Agrupation(self.mem,  "IBEX","Ibex 35", self.mem.types.find_by_id(3), self.mem.stockmarkets.find_by_id(1) ))
        self.append(Agrupation(self.mem,  "MERCADOCONTINUO","Mercado continuo español", self.mem.types.find_by_id(3), self.mem.stockmarkets.find_by_id(1) ))
        self.append(Agrupation(self.mem, "CAC",  "CAC 40 de París", self.mem.types.find_by_id(3),self.mem.stockmarkets.find_by_id(3) ))
        self.append(Agrupation(self.mem,  "EUROSTOXX","Eurostoxx 50", self.mem.types.find_by_id(3),self.mem.stockmarkets.find_by_id(10)  ))
        self.append(Agrupation(self.mem,  "DAX","DAX", self.mem.types.find_by_id(3), self.mem.stockmarkets.find_by_id(5)  ))
        self.append(Agrupation(self.mem, "SP500",  "Standard & Poors 500", self.mem.types.find_by_id(3), self.mem.stockmarkets.find_by_id(2)  ))
        self.append(Agrupation(self.mem,  "NASDAQ100","Nasdaq 100", self.mem.types.find_by_id(3), self.mem.stockmarkets.find_by_id(2)  ))
        self.append(Agrupation(self.mem,  "EURONEXT",  "EURONEXT", self.mem.types.find_by_id(3), self.mem.stockmarkets.find_by_id(10)  ))
        self.append(Agrupation(self.mem,  "DEUTSCHEBOERSE",  "DEUTSCHEBOERSE", self.mem.types.find_by_id(3), self.mem.stockmarkets.find_by_id(5)  ))
        self.append(Agrupation(self.mem,  "LATIBEX",  "LATIBEX", self.mem.types.find_by_id(3), self.mem.stockmarkets.find_by_id(1)  ))

        self.append(Agrupation(self.mem,  "e_fr_LYXOR","LYXOR", self.mem.types.find_by_id(4),self.mem.stockmarkets.find_by_id(3)  ))
        self.append(Agrupation(self.mem,  "e_de_DBXTRACKERS","Deutsche Bank X-Trackers", self.mem.types.find_by_id(4),self.mem.stockmarkets.find_by_id(5)  ))
        
        self.append(Agrupation(self.mem,  "f_es_BMF","Fondos de la bolsa de Madrid", self.mem.types.find_by_id(2), self.mem.stockmarkets.find_by_id(1) ))
        self.append(Agrupation(self.mem,  "f_fr_CARMIGNAC","Gestora CARMIGNAC", self.mem.types.find_by_id(2), self.mem.stockmarkets.find_by_id(3) ))
        self.append(Agrupation(self.mem, "f_cat_money","Funds category: Money", self.mem.types.find_by_id(2),self.mem.stockmarkets.find_by_id(10)))

        self.append(Agrupation(self.mem,  "w_fr_SG","Warrants Societe Generale", self.mem.types.find_by_id(5),self.mem.stockmarkets.find_by_id(3) ))
        self.append(Agrupation(self.mem, "w_es_BNP","Warrants BNP Paribas", self.mem.types.find_by_id(5),self.mem.stockmarkets.find_by_id(1)))
        
        
  
    def clone_by_type(self,  type):
        """Muestra las agrupaciónes de un tipo pasado como parámetro. El parámetro type es un objeto Type"""
        resultado=AgrupationManager(self.mem)
        for a in self.arr:
            if a.type==type:
                resultado.append(a)
        return resultado

    def clone_etfs(self):
        """Función que filtra el diccionario a según el país y el fondo """
        return self.clone_by_type(self.mem.types.find_by_id(4))
        
    def clone_warrants(self):
        """Función que filtra el diccionario a según el país y el fondo """
        return self.clone_by_type(self.mem.types.find_by_id(5))
        
    def clone_fondos(self):
        """Función que filtra el diccionario a según el país y el fondo """
        return self.clone_by_type(self.mem.types.find_by_id(2))
        
    def clone_acciones(self):
        """Función que filtra el diccionario a según el país y el fondo """
        return self.clone_by_type(self.mem.types.find_by_id(3))
        
        
    def clone_from_dbstring(self, dbstr):
        """Convierte la cadena de la base datos en un array de objetos agrupation"""
        resultado=AgrupationManager(self.mem)
        if dbstr==None or dbstr=="":
            pass
        else:
            for item in dbstr[1:-1].split("|"):
                resultado.append(self.mem.agrupations.find_by_id(item))
        return resultado
            
    def dbstring(self):
        resultado="|"
        for a in self.arr:
            resultado=resultado+a.id+"|"
        if resultado=="|":
            return ""
        return resultado
        
        
    def clone_from_combo(self, cmb):
        """Función que convierte un combo de agrupations a un array de agrupations"""
        resultado=AgrupationManager(self.mem)
        for i in range (cmb.count()):
            resultado.append(self.mem.agrupations.find_by_id(cmb.itemData(i)))
        return resultado

class LeverageManager(ObjectManager_With_IdName_Selectable):
    def __init__(self, mem):
        """Usa la variable mem.Agrupations"""
        ObjectManager_With_IdName_Selectable.__init__(self)
        self.mem=mem

    def load_all(self):
        self.append(Leverage(self.mem).init__create(-1,QApplication.translate("Core","Variable leverage (Warrants)"), eLeverageType.Variable))
        self.append(Leverage(self.mem).init__create(1 ,QApplication.translate("Core","Not leveraged"), eLeverageType.NotLeveraged))
        self.append(Leverage(self.mem).init__create( 2,QApplication.translate("Core","Leverage x2"), eLeverageType.X2))
        self.append(Leverage(self.mem).init__create( 3,QApplication.translate("Core","Leverage x3"), eLeverageType.X3))
        self.append(Leverage(self.mem).init__create( 4,QApplication.translate("Core","Leverage x4"), eLeverageType.X4))
        self.append(Leverage(self.mem).init__create( 5,QApplication.translate("Core","Leverage x5"), eLeverageType.X5))
        self.append(Leverage(self.mem).init__create( 6,QApplication.translate("Core","Leverage x10"), eLeverageType.X10))

class OrderManager(ObjectManager_With_Id_Selectable):
    def __init__(self, mem):
        ObjectManager_With_Id_Selectable.__init__(self)
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
        
        
        
    def order_by_percentage_from_current_price(self):
        try:
            self.arr=sorted(self.arr, key=lambda o:o.percentage_from_current_price(), reverse=True)
        except:            
            qmessagebox(QApplication.translate("Core", "I couldn't order data due to they have null values"))
        
    def date_first_db_order(self):
        """First order date. It searches in database not in array"""
        cur=self.mem.con.cursor()
        cur.execute("select date from orders order by date limit 1")
        r=cur.fetchone()
        cur.close()
        if r==None:#To avoid crashed returns today if null
            return datetime.date.today()
        else:
            return r[0]
        
    def myqtablewidget(self, table):
        table.setColumnCount(9)
        table.setHorizontalHeaderItem(0, QTableWidgetItem(QApplication.translate("Core","Date")))
        table.setHorizontalHeaderItem(1, QTableWidgetItem(QApplication.translate("Core","Expiration")))
        table.setHorizontalHeaderItem(2, QTableWidgetItem(QApplication.translate("Core","Investment")))
        table.setHorizontalHeaderItem(3, QTableWidgetItem(QApplication.translate("Core","Account")))
        table.setHorizontalHeaderItem(4, QTableWidgetItem(QApplication.translate("Core","Shares")))
        table.setHorizontalHeaderItem(5, QTableWidgetItem(QApplication.translate("Core","Price")))
        table.setHorizontalHeaderItem(6, QTableWidgetItem(QApplication.translate("Core","Amount")))
        table.setHorizontalHeaderItem(7, QTableWidgetItem(QApplication.translate("Core","% from current")))
        table.setHorizontalHeaderItem(8, QTableWidgetItem(QApplication.translate("Core","Executed")))
        table.applySettings()
        table.clearContents()
        table.setRowCount(self.length())
        for i, p in enumerate(self.arr):
            table.setItem(i, 0, qdate(p.date))
            table.setItem(i, 1, qdate(p.expiration))      
            table.setItem(i, 2, qleft(p.investment.name))
            table.setItem(i, 3, qleft(p.investment.account.name))   
            table.setItem(i, 4, qright(p.shares))
            table.setItem(i, 5, p.investment.product.currency.qtablewidgetitem(p.price))
            table.setItem(i, 6, self.mem.localcurrency.qtablewidgetitem(p.amount))   
            if p.is_in_force():
                table.setItem(i, 7, p.percentage_from_current_price().qtablewidgetitem())
            else:
                table.setItem(i, 7, qempty())
            if p.is_executed():
                table.setItem(i, 8, qdatetime(p.executed, self.mem.localzone))
            else:
                table.setItem(i, 8, qempty())
                
            #Color
            if p.is_executed():
                for column in range (table.columnCount()):
                    table.item(i, column).setBackground(eQColor.Green)                     
            elif p.is_expired():
                for column in range (table.columnCount()):
                    table.item(i, column).setBackground(eQColor.Red)     

## Class that represents stock market object. It gives several utils to manage it.
class StockMarket:
    def __init__(self, mem):
        self.mem=mem
        self.id=None
        self.name=None
        self.country=None
        self.starts=None
        self.closes=None
        self.zone=None
        
    def __repr__(self):
        return self.name
        
    def init__db_row(self, row,  country):
        self.id=row['id']
        self.name=row['name']
        self.country=country
        self.starts=row['starts']
        self.closes=row['closes']
        self.zone=self.mem.zones.find_by_name(row['zone'])
        return self
        
    def init__create(self, id, name,  country_id, starts, closes, zone_name):
        self.id=id
        self.name=name
        self.country=self.mem.countries.find_by_id(country_id)
        self.starts=starts
        self.closes=closes
        self.zone=self.mem.zones.find_by_name(zone_name)
        return self
        

    ## Returns the close time of a given date
    def date_closes(self, date):
        return dtaware(date, self.closes, self.zone.name)
    
    ## Returns a datetime with timezone with the todays stockmarket closes
    def today_closes(self):
        return self.date_closes(datetime.date.today())

    ## Returns a datetime with timezone with the todays stockmarket closes
    def today_starts(self):
        return dtaware(datetime.date.today(), self.starts, self.zone.name)
        
    ## When we don't know the datetime of a quote because the webpage we are scrapping doesn't gives us, we can use this functions
    ## - If it's saturday or sunday it returns last friday at close time
    ## - If it's not weekend and it's after close time it returns todays close time
    ## - If it's not weekend and it's before open time it returns yesterday close time. If it's monday it returns last friday at close time
    ## - If it's not weekend and it's after opent time and before close time it returns aware current datetime
    ## @param delay Boolean that if it's True (default) now  datetime is minus 15 minutes. If False uses now datetime
    ## @return Datetime aware, always. It can't be None
    def estimated_datetime_for_intraday_quote(self, delay=True):
        if delay==True:
            now=self.zone.now()-datetime.timedelta(minutes=15)
        else:
            now=self.zone.now()
        if now.weekday()<5:#Weekday
            if now>self.today_closes():
                return self.today_closes()
            elif now<self.today_starts():
                if now.weekday()>0:#Tuesday to Friday
                    return dtaware(datetime.date.today()-datetime.timedelta(days=1), self.closes, self.zone.name)
                else: #Monday
                    return dtaware(datetime.date.today()-datetime.timedelta(days=3), self.closes, self.zone.name)
            else:
                return now
        elif now.weekday()==5:#Saturday
            return dtaware(datetime.date.today()-datetime.timedelta(days=1), self.closes, self.zone.name)
        elif now.weekday()==6:#Sunday
            return dtaware(datetime.date.today()-datetime.timedelta(days=2), self.closes, self.zone.name)

    ## When we don't know the date pf a quote of a one quote by day product. For example funds... we'll use this function
    ## - If it's saturday or sunday it returns last thursday at close time
    ## - If it's not weekend and returns yesterday close time except if it's monday that returns last friday at close time
    ## @return Datetime aware, always. It can't be None
    def estimated_datetime_for_daily_quote(self):
        now=self.zone.now()
        if now.weekday()<5:#Weekday
            if now.weekday()>0:#Tuesday to Friday
                return dtaware(datetime.date.today()-datetime.timedelta(days=1), self.closes, self.zone.name)
            else: #Monday
                return dtaware(datetime.date.today()-datetime.timedelta(days=3), self.closes, self.zone.name)
        elif now.weekday()==5:#Saturday
            return dtaware(datetime.date.today()-datetime.timedelta(days=2), self.closes, self.zone.name)
        elif now.weekday()==6:#Sunday
            return dtaware(datetime.date.today()-datetime.timedelta(days=3), self.closes, self.zone.name)

class Currency:
    """Clase que almacena el concepto divisa"""
    def __init__(self ):
        self.name=None
        self.symbol=None
        self.id=None

    def __repr__(self):
        return ("Currency: {} ({})".format( self.id, self.symbol))
        
    def init__create(self, name, symbol,  id=None):
        self.name=name
        self.symbol=symbol
        self.id=id
        return self

    def string(self, number,  digits=2):
        if number==None:
            return "None " + self.symbol
        else:
            return "{} {}".format(round(number, digits), self.symbol)

    def qtablewidgetitem(self, n, digits=2):
        """Devuelve un QTableWidgetItem mostrando un currency
        curren es un objeto Curryency"""
        text= self.string(n,  digits)
        a=QTableWidgetItem(text)
        a.setTextAlignment(Qt.AlignVCenter|Qt.AlignRight)
        if n==None:
            a.setForeground(QColor(0, 0, 255))
        elif n<0:
            a.setForeground(QColor(255, 0, 0))
        return a

    ## returns a qtablewidgetitem colored in red is amount is smaller than target or green if greater
    def qtablewidgetitem_with_target(self, amount, target, digits=2):
        item=self.qtablewidgetitem(amount, digits)
        if amount<target:   
            item.setBackground(eQColor.Red)
        else:
            item.setBackground(eQColor.Green)
        return item
        
## Class that compares two products, removes ohclDaily that aren't in both products
class ProductComparation:
    def __init__(self, mem, product1, product2):
        self.mem=mem
        
        self.__fromDate=None#None all array.
        self.product1=product1
        self.product2=product2     
        self.set1=OHCLDailyManager(self.mem, self.product1)#Set with common data. Needed in order to not broke self.product1 data
        self.set2=OHCLDailyManager(self.mem, self.product2)
        self.product1.needStatus(2)
        self.product2.needStatus(2)
        self.__commonDates=None 
        self.__removeNotCommon()
        
    def setFromDate(self, date):
        """Only affect to functions returning data, not to constructor"""
        self.__fromDate=date            
            
    def canBeMade(self):
        """Returns a boolean if comparation can be made"""        
        if len(self.__commonDates)==0:
            return False
        return True
            
    def __removeNotCommon(self):
        self.__commonDates=list(set(self.product1.result.ohclDaily.dates()) & set(self.product2.result.ohclDaily.dates()))
        self.__commonDates=sorted(self.__commonDates, key=lambda c: c,  reverse=False)     
        for ohcl in self.product1.result.ohclDaily.arr:
            if ohcl.date in self.__commonDates:
                self.set1.append(ohcl)
        for ohcl in self.product2.result.ohclDaily.arr:
            if ohcl.date in self.__commonDates:
                self.set2.append(ohcl)

    def myqtablewidget(self, tabla):
        arr=[]#date, product1, product2
        for i, date in enumerate(self.__commonDates):
            arr.append((date, self.set1.arr[i].close, self.set2.arr[i].close))
            
        tabla.setColumnCount(3)
        tabla.setHorizontalHeaderItem(0, QTableWidgetItem(QApplication.translate("Core","Date" )))
        tabla.setHorizontalHeaderItem(1, QTableWidgetItem(self.product1.name))
        tabla.setHorizontalHeaderItem(2,  QTableWidgetItem(self.product2.name))
        ##DATA 
        tabla.clearContents()
        tabla.applySettings()  
        tabla.setRowCount(len(self.__commonDates))
        
        for i, a in enumerate(arr):
            tabla.setItem(i, 0, qdate(a[0]))
            tabla.setItem(i, 1, self.product1.currency.qtablewidgetitem(a[1]))
            tabla.setItem(i, 2, self.product1.currency.qtablewidgetitem(a[2]))
        tabla.setSortingEnabled(True)
        
    def index(self, date):
        """Returns date index in array"""
        if date==None:
            return 0
        for i, d in enumerate(self.__commonDates):
            if date<=d:
                return i
        return 0

    def dates(self):
        """Returns a list with common dates"""
        return self.__commonDates[self.index(self.__fromDate):len(self.__commonDates)]
        
    def product1Closes(self):
        r=[]
        for ohcl in self.set1.arr:
            r.append(ohcl.close)
        return r[self.index(self.__fromDate):len(self.__commonDates)]

    def product2Closes(self):
        r=[]
        for ohcl in self.set2.arr:
            r.append(ohcl.close)
        return r[self.index(self.__fromDate):len(self.__commonDates)]
    
    def product1ClosesDividingFirst(self):
        """Divides set1 by a factor to get the same price in the first ohcl"""
        idx=self.index(self.__fromDate)
        factor=self.set1.arr[idx].close/self.set2.arr[idx].close
        r=[]
        for ohcl in self.set1.arr:
            r.append(ohcl.close/factor)
        return r[idx:len(self.__commonDates)]

    def product1ClosesDividingFirstLeveragedReduced(self):
        """Divides set1 by a factor to get the same price in the first ohcl
        It controls leverage too"""
        idx=self.index(self.__fromDate)
        factor=self.set1.arr[idx].close/self.set2.arr[idx].close*self.product1.leveraged.multiplier
        r=[]
        for ohcl in self.set1.arr:
            r.append(ohcl.close/factor)
        return r[idx:len(self.__commonDates)]
        
    def product1PercentageFromFirstProduct2Price(self):
        """Usa el primer valor de set 2 y la va sumando los porcentajes de set1. """
        idx=self.index(self.__fromDate)
        r=[]
        last=self.set2.arr[idx].close
        r.append(last)
        for index in range(idx+1, self.set1.length()):
            last=last*(1+ self.set1.arr[index-1].percentage(self.set1.arr[index]).value)
            r.append(last)
        return r 
        
    def product1PercentageFromFirstProduct2PriceLeveragedReduced(self):
        """Usa el primer valor de set 2 y la va sumando los porcentajes de set1. Contrala leverages"""
        idx=self.index(self.__fromDate)
        r=[]
        last=self.set2.arr[idx].close
        r.append(last)
        for index in range(idx+1, self.set1.length()):
            last=last*(1+ self.set1.arr[index-1].percentage(self.set1.arr[index]).value/self.product1.leveraged.multiplier)
            r.append(last)
        return r
        
    def product1PercentageFromFirstProduct2InversePrice(self):
        """Usa el primer valor de set 2 y la va sumando los porcentajes de set1. """
        idx=self.index(self.__fromDate)
        r=[]
        last=self.set2.arr[idx].close
        r.append(last)
        for index in range(idx+1, self.set1.length()):
            last=last*(1- self.set1.arr[index-1].percentage(self.set1.arr[index]).value)
            r.append(last)
        return r 
        
    def product1PercentageFromFirstProduct2InversePriceLeveragedReduced(self):
        """Usa el primer valor de set 2 y la va sumando los porcentajes de set1. Contrala leverages"""
        idx=self.index(self.__fromDate)
        r=[]
        last=self.set2.arr[idx].close
        r.append(last)
        for index in range(idx+1, self.set1.length()):
            last=last*(1- self.set1.arr[index-1].percentage(self.set1.arr[index]).value/self.product1.leveraged.multiplier)
            r.append(last)
        return r
            

class ProductMode:
    def __init__(self, mem):
        self.mem=mem
        self.id=None
        self.name=None
        
    def init__create(self, id, name):
        self.id=id
        self.name=name
        return self
        
        
class Money:
    "Permite operar con dinero y divisas teniendo en cuenta la fecha de la operación mirando la divisa en mystocks"
    def __init__(self, mem,  amount=None,  currency=None) :
        self.mem=mem
        if amount==None:
            self.amount=Decimal(0)
        else:
            self.amount=Decimal(str(amount))
        if currency==None:
            self.currency=self.mem.localcurrency
        else:
            self.currency=currency


    def __add__(self, money):
        """Si las divisas son distintas, queda el resultado con la divisa del primero"""
        if self.currency==money.currency:
            return Money(self.mem, self.amount+money.amount, self.currency)
        else:
            print (self.currency, money.currency )
            logging.error("Before adding, please convert to the same currency")
            raise "MoneyOperationException"
            
        
    def __sub__(self, money):
        """Si las divisas son distintas, queda el resultado con la divisa del primero"""
        if self.currency==money.currency:
            return Money(self.mem, self.amount-money.amount, self.currency)
        else:
            logging.error("Before substracting, please convert to the same currency")
            raise "MoneyOperationException"
        
    def __lt__(self, money):
        if self.currency==money.currency:
            if self.amount < money.amount:
                return True
            return False
        else:
            logging.error("Before lt ordering, please convert to the same currency")
            sys.exit(1)
        
    def __mul__(self, money):
        """Si las divisas son distintas, queda el resultado con la divisa del primero
        En caso de querer multiplicar por un numero debe ser despues
        money*4
        """
        if money.__class__ in (int,  float, Decimal):
            return Money(self.mem, self.amount*money, self.currency)
        if self.currency==money.currency:
            return Money(self.mem, self.amount*money.amount, self.currency)
        else:
            logging.error("Before multiplying, please convert to the same currency")
            sys.exit(1)
    
    def __truediv__(self, money):
        """Si las divisas son distintas, queda el resultado con la divisa del primero"""
        if self.currency==money.currency:
            return Money(self.mem, self.amount/money.amount, self.currency)
        else:
            logging.error("Before true dividing, please convert to the same currency")
            sys.exit(1)
        
    def __repr__(self):
        return self.string(2)
        
    def string(self,   digits=2):
        return self.currency.string(self.amount, digits)
        
    def isZero(self):
        if self.amount==Decimal(0):
            return True
        else:
            return False
            
    def isGETZero(self):
        if self.amount>=Decimal(0):
            return True
        else:
            return False            
    def isGTZero(self):
        if self.amount>Decimal(0):
            return True
        else:
            return False

    def isLTZero(self):
        if self.amount<Decimal(0):
            return True
        else:
            return False

    def isLETZero(self):
        if self.amount<=Decimal(0):
            return True
        else:
            return False
            
    def __neg__(self):
        """Devuelve otro money con el amount con signo cambiado"""
        return Money(self.mem, -self.amount, self.currency)
        
    def local(self, dt=None):
        """Converts a Money to local currency
        Date==None means today"""
        return self.convert(self.mem.localcurrency, dt)
        
    def convert(self, currency, dt=None):
        """Converts self money to currency"""
        if self.currency==currency:
            return self
        if self.amount==Decimal(0):
            return Money(self.mem, 0, currency)
            
        init=datetime.datetime.now()
        if dt==None:
            dt=self.mem.localzone.now()
        factor=self.conversionFactor(currency, dt)
        result=Money(self.mem, self.amount*factor, currency)
        logging.debug("Money conversion. {} to {} at {} took {}".format(self.string(6), result.string(6), dt, datetime.datetime.now()-init))
        return result
        
    def conversionFactor(self, currency, dt):
        """Factor to convert from self currency to parameter currency, using datetime from result. allsetquotesintraday, uses mem"""
        if self.currency==currency:
            return Decimal(1)
        
        if self.currency.id=="EUR":
            if currency.id=="USD":
                return self.mem.data.currencies.find_by_id(74747).result.all.find(dt).quote
        elif self.currency.id=="USD":
            if currency.id=="EUR":
                return 1/self.mem.data.currencies.find_by_id(74747).result.all.find(dt).quote
        logging.critical("No existe factor de conversión")
        return None  

    def conversionFactorString(self, currency, dt):
        """Factor to convert from self currency to parameter currency, using datetime from result. allsetquotesintraday, uses mem"""
        factor=self.conversionFactor(currency, dt)
        
        if self.currency==currency:
            return "No currency conversion factor"
            
        return "1 {} = {} {}".format(self.currency.id, factor, currency.id)
   
    def conversionDatetime(self, currency, dt):
        """
            Returns conversion datetime
        """       
        if self.currency==currency:
            return dt
        
        if self.currency.id=="EUR":
            if currency.id=="USD":
                return self.mem.data.currencies.find_by_id(74747).result.all.find(dt).datetime
        elif self.currency.id=="USD":
            if currency.id=="EUR":
                return 1/self.mem.data.currencies.find_by_id(74747).result.all.find(dt).datetime
        logging.critical("No existe factor de conversión, por lo que tampoco su datetime")
        return None
        
        
    def convert_from_factor(self, currency, factor):
        """Converts self money to currency, multiplicando el amount del self con el factor y obteniendo la nueva currency pasada como parametro"""
        if self.currency==currency:
            return self
        
        return Money(self.mem, self.amount*factor, currency)

    def qtablewidgetitem(self, digits=2):
        """Devuelve un QTableWidgetItem mostrando un currency
        curren es un objeto Curryency"""
        text=self.string(digits)
        a=QTableWidgetItem(text)
        a.setTextAlignment(Qt.AlignVCenter|Qt.AlignRight)
        if self.amount==None:
            a.setForeground(QColor(0, 0, 255))
        elif self.amount<Decimal(0):
            a.setForeground(QColor(255, 0, 0))
        return a

    def round(self, digits=2):
        return round(self.amount, digits)

class DPSManager(ObjectManager_With_IdDate):
    def __init__(self, mem,  product):
        ObjectManager_With_IdDate.__init__(self)
        self.mem=mem   
        self.product=product
    
    def load_from_db(self):
        del self.arr
        self.arr=[]
        cur=self.mem.con.cursor()
        cur.execute( "select * from dps where id=%s order by date", (self.product.id, ))
        for row in cur:
            self.arr.append(DPS(self.mem, self.product).init__from_db_row(row))
        cur.close()            
    
    def save(self):
        """
            Saves DPS Without commit
        """            
        for o in self.arr:
            o.save()
        
    def myqtablewidget(self, table):
        table.setColumnCount(2)
        table.setHorizontalHeaderItem(0, QTableWidgetItem(QApplication.translate("Core", "Date" )))
        table.setHorizontalHeaderItem(1, QTableWidgetItem(QApplication.translate("Core", "Gross" )))
        self.order_by_date()   
        table.applySettings()
        table.clearContents()
        table.setRowCount(len(self.arr))
        for i, e in enumerate(self.arr):
            table.setItem(i, 0, qcenter(str(e.date)))
            table.setItem(i, 1, self.product.currency.qtablewidgetitem(e.gross, 6))       
        table.setCurrentCell(len(self.arr)-1, 0)
    
    def adjustPrice(self, datetime, price):
        """
            Returns a new price adjusting
        """
        r=price
        for dps in self.arr:
            if datetime>day_end_from_date(dps.date, self.mem.localzone):
                r=r+dps.gross
        return r
        
    def adjustOHCLDaily(self, ohcl ):
        r=OHCLDaily(self.mem)
        r.product=ohcl.product
        r.date=ohcl.date
        r.close=self.adjustPrice(ohcl.datetime(), ohcl.close)
        r.open=self.adjustPrice(ohcl.datetime(), ohcl.open)
        r.high=self.adjustPrice(ohcl.datetime(), ohcl.high)
        r.low=self.adjustPrice(ohcl.datetime(), ohcl.low)
        return r

    def adjustOHCLDailyManager(self, set):
        r=OHCLDailyManager(self.mem, self.product)
        for ohcl in set.arr:
            r.append(self.adjustOHCLDaily(ohcl))
        return r


class DPS:
    """Dividend por acción pagados. Se usa para pintar gráficos sin dividends"""
    def __init__(self, mem,  product):
        self.mem=mem
        self.product=product
        self.id=None#id_dps
        self.date=None#pk
        self.gross=None#bruto
        
    def __repr__(self):
        return "DPS. Id: {0}. Gross: {1}".format(self.id, self.gross)
        
    def init__create(self, date, gross, id=None):
        self.date=date
        self.gross=gross
        self.id=id
        return self

    def init__from_db_row(self,  row):
        """Saca el registro  o uno en blanco si no lo encuentra, que fueron pasados como parámetro"""
        return self.init__create(row['date'], row['gross'], row['id_dps'])
        
    def borrar(self):
        cur=self.mem.con.cursor()
        cur.execute("delete from dps where id_dps=%s", (self.id,))
        cur.close()
            
    def save(self):
        """Función que comprueba si existe el registro para insertar o modificarlo según proceda"""
        cur=self.mem.con.cursor()
        if self.id==None:
            cur.execute("insert into dps(date, gross,id) values (%s,%s,%s) returning id_dps", (self.date, self.gross, self.product.id))
            self.id=cur.fetchone()[0]
        else:         
            cur.execute("update dps set date=%s, gross=%s, id=%s where id_dps=%s", (self.date,  self.gross, self.product.id, self.id))
        cur.close()
        

        
        
class EstimationEPS:
    """Beneficio por acción. Earnings per share Beneficio por acción. Para los calculos usaremos
    esto, aunque sean estimaciones."""

    def __init__(self, mem):
        self.mem=mem
        self.product=None#pk
        self.year=None#pk
        self.date_estimation=None
        self.source=None
        self.estimation=None
        self.manual=None
        
    def init__create(self, product, year, date_estimation, source, manual, estimation):
        self.product=product
        self.year=year
        self.date_estimation=date_estimation
        self.source=source
        self.manual=manual
        self.estimation=estimation
        return self

    def init__from_db(self, product,  currentyear):
        """Saca el registro  o uno en blanco si no lo encuentra, que fueron pasados como parámetro"""
        cur=self.mem.con.cursor()
        cur.execute("select estimation, date_estimation ,source,manual from estimations_eps where id=%s and year=%s", (product.id, currentyear))
        if cur.rowcount==1:
            row=cur.fetchone()
            self.init__create(product, currentyear, row['date_estimation'], row['source'], row['manual'], row['estimation'])
            cur.close()
        else:
            self.init__create(product, currentyear, None, None, None, None)
        return self
            
            
    def borrar(self):
        cur=self.mem.con.cursor()
        cur.execute("delete from estimations_eps where id=%s and year=%s", (self.product.id, self.year))
        cur.close()
            
    def save(self):
        """Función que comprueba si existe el registro para insertar o modificarlo según proceda"""
        cur=self.mem.con.cursor()
        cur.execute("select count(*) from estimations_eps where id=%s and year=%s", (self.product.id, self.year))
        if cur.fetchone()[0]==0:
            cur.execute("insert into estimations_eps(id, year, estimation, date_estimation, source, manual) values (%s,%s,%s,%s,%s,%s)", (self.product.id, self.year, self.estimation, self.date_estimation, self.source, self.manual))
        elif self.estimation!=None:            
            cur.execute("update estimations_eps set estimation=%s, date_estimation=%s, source=%s, manual=%s where id=%s and year=%s", (self.estimation, self.date_estimation, self.source, self.manual, self.product.id, self.year))
        cur.close()
        
        
    def PER(self, last_year_quote_of_estimation):
        """Price to Earnings Ratio"""
        try:
            return last_year_quote_of_estimation.quote/self.estimation
        except:
            return None

class EstimationDPS:
    """Dividends por acción"""
    def __init__(self, mem):
        self.mem=mem
        self.product=None#pk
        self.year=None#pk
        self.date_estimation=None
        self.source=None
        self.estimation=None
        self.manual=None
        
    def __repr__(self):
        return "EstimationDPS: Product {0}. Year {1}. Estimation {2}".format(self.product.id, self.year, self.estimation)
        
    def init__create(self, product, year, date_estimation, source, manual, estimation):
        self.product=product
        self.year=year
        self.date_estimation=date_estimation
        self.source=source
        self.manual=manual
        self.estimation=estimation
        return self

    def init__from_db(self, product,  currentyear):
        """Saca el registro  o uno en blanco si no lo encuentra, que fueron pasados como parámetro"""
        cur=self.mem.con.cursor()
        cur.execute("select estimation, date_estimation ,source,manual from estimations_dps where id=%s and year=%s", (product.id, currentyear))
        if cur.rowcount==1:
            row=cur.fetchone()
            self.init__create(product, currentyear, row['date_estimation'], row['source'], row['manual'], row['estimation'])
            cur.close()
        else:
            self.init__create(product, currentyear, None, None, None, None)
        return self
            
            
    def borrar(self):
        cur=self.mem.con.cursor()
        cur.execute("delete from estimations_dps where id=%s and year=%s", (self.product.id, self.year))
        cur.close()
            
    def save(self):
        """Función que comprueba si existe el registro para insertar o modificarlo según proceda"""
        cur=self.mem.con.cursor()
        cur.execute("select count(*) from estimations_dps where id=%s and year=%s", (self.product.id, self.year))
        if cur.fetchone()[0]==0:
            cur.execute("insert into estimations_dps(id, year, estimation, date_estimation, source, manual) values (%s,%s,%s,%s,%s,%s)", (self.product.id, self.year, self.estimation, self.date_estimation, self.source, self.manual))
        elif self.estimation!=None:            
            cur.execute("update estimations_dps set estimation=%s, date_estimation=%s, source=%s, manual=%s where id=%s and year=%s", (self.estimation, self.date_estimation, self.source, self.manual, self.product.id, self.year))
        cur.close()
        
    def percentage(self):
        """Hay que tener presente que lastyear (Objeto Quote) es el lastyear del año actual
        Necesita tener cargado en id el lastyear """
        return Percentage(self.estimation, self.product.result.basic.last.quote)


class Product:
    def __init__(self, mem):
        self.mem=mem
        self.name=None
        self.isin=None
        self.currency=None #Apunta a un objeto currency
        self.type=None
        self.agrupations=None #Es un objeto AgrupationManager
        self.id=None
        self.web=None
        self.address=None
        self.phone=None
        self.mail=None
        self.percentage=None
        self.mode=None#Anterior mode investmentmode
        self.leveraged=None
        self.stockmarket=None
        self.tickers=[None]*eTickerPosition.length()#Its a list of strings, eTickerPosition is the 
        self.comment=None
        self.obsolete=None
        
        ## Variable with the current product status
        ## 0 No data
        ## 1 Loaded splits and triplete and estimations_dps
        ## 2 Load estimations_eps, dps, eps, ohcls and dividends
        ## 3 Load all quotes
        self.status=0
        
        self.result=None#Variable en la que se almacena QuotesResult
        self.estimations_dps=None#Es un diccionario que guarda objetos estimations_dps con clave el año
        self.estimations_eps=None
        self.dps=None #It's created when loading quotes in quotes result
        self.splits=None #It's created when loading quotes in quotes result
        
#    ## Compares this product with other products
#    ## Logs differences
#    def __eq__(self, other):
#        if (self.id!=other.id or
#            self.name!=other.name or
#            self.isin!=other.isin or
#            self.stockmarket.id!=other.stockmarket.id or
#            self.currency.id!=other.currency.id or
#            self.type.id!=other.type.id or
#            self.agrupations.dbstring()!=other.agrupations.dbstring() or 
#            self.web!=other.web or
#            self.address!=other.address or
#            self.phone!=other.phone or
#            self.mail!=other.mail or
#            self.percentage!=other.percentage or
#            self.mode.id!=other.mode.id or
#            self.leveraged.id!=other.leveraged.id or
#            self.comment!=other.comment or 
#            self.obsolete!=other.obsolete or
#            self.tickers[0]!=other.tickers[0] or
#            self.tickers[1]!=other.tickers[1] or
#            self.tickers[2]!=other.tickers[2] or
#            self.tickers[3]!=other.tickers[3]):
#            return False
#        return True
#        
#    def __ne__(self, other):
#        return not self.__eq__(other)
    def __repr__(self):
        return "{0} ({1}) de la {2}".format(self.name , self.id, self.stockmarket.name)
                
    def init__db_row(self, row):
        """row es una fila de un pgcursro de investmentes"""
        self.name=row['name'].upper()
        self.isin=row['isin']
        self.currency=self.mem.currencies.find_by_id(row['currency'])
        self.type=self.mem.types.find_by_id(row['type'])
        self.agrupations=self.mem.agrupations.clone_from_dbstring(row['agrupations'])
        self.id=row['id']
        self.web=row['web']
        self.address=row['address']
        self.phone=row['phone']
        self.mail=row['mail']
        self.percentage=row['percentage']
        self.mode=self.mem.investmentsmodes.find_by_id(row['pci'])
        self.leveraged=self.mem.leverages.find_by_id(row['leveraged'])
        self.stockmarket=self.mem.stockmarkets.find_by_id(row['stockmarkets_id'])
        self.tickers=row['tickers']
        self.comment=row['comment']
        self.obsolete=row['obsolete']
        
        return self


    def init__create(self, name,  isin, currency, type, agrupations, active, web, address, phone, mail, percentage, mode, leveraged, stockmarket, tickers, comment, obsolete, id=None):
        self.name=name
        self.isin=isin
        self.currency=currency
        self.type=type
        self.agrupations=agrupations
        self.active=active
        self.id=id
        self.web=web
        self.address=address
        self.phone=phone
        self.mail=mail
        self.percentage=percentage
        self.mode=mode
        self.leveraged=leveraged        
        self.stockmarket=stockmarket
        self.tickers=tickers
        self.comment=comment
        self.obsolete=obsolete
        return self        

    def init__db(self, id):
        """Se pasa id porque se debe usar cuando todavía no se ha generado."""
        cur=self.mem.con.cursor()
        cur.execute("select * from products where id=%s", (id, ))
        row=cur.fetchone()
        cur.close()
        return self.init__db_row(row)

    def save(self):
        """
            Esta función inserta una inversión manua
            Los arrays deberan pasarse como parametros ARRAY[1,2,,3,] o None
        """
        
        cur=self.mem.con.cursor()
        if self.id==None:
            cur.execute("select min(id)-1 from products")
            id=cur.fetchone()[0]
            if id>=0:
                id=-1
            cur.execute("insert into products (id, name,  isin,  currency,  type,  agrupations,   web, address,  phone, mail, percentage, pci,  leveraged, stockmarkets_id, tickers, comment,  obsolete) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",  (id, self.name,  self.isin,  self.currency.id,  self.type.id,  self.agrupations.dbstring(), self.web, self.address,  self.phone, self.mail, self.percentage, self.mode.id,  self.leveraged.id, self.stockmarket.id, self.tickers, self.comment, self.obsolete))
            self.id=id
        else:
            cur.execute("update products set name=%s, isin=%s,currency=%s,type=%s, agrupations=%s, web=%s, address=%s, phone=%s, mail=%s, percentage=%s, pci=%s, leveraged=%s, stockmarkets_id=%s, tickers=%s, comment=%s, obsolete=%s where id=%s", ( self.name,  self.isin,  self.currency.id,  self.type.id,  self.agrupations.dbstring(),  self.web, self.address,  self.phone, self.mail, self.percentage, self.mode.id,  self.leveraged.id, self.stockmarket.id, self.tickers, self.comment, self.obsolete,  self.id))
        cur.close()
    
    ## Return if the product has autoupdate in some source
    def has_autoupdate(self):
        if self.obsolete==True:
            return False
        if self.id in self.mem.autoupdate:
            return True
        return False
        
    ## La forma para ver si un objeto no se han cargado valores es que sea None y para borrarlos es ponerlos a None
    ## Variable with the current product status
    ## 0 No data. Tendra los siguientes valores
    ## 1 Loaded splits and triplete and estimations_dps,splits
    ## 2 Load estimations_eps, dps, , dividends, ohcls 
    ## 3 Load all quotes
    
    ## ESTA FUNCION VA AUMENTANDO STATUS SIN MOLESTAR LOS ANTERIORES, SOLO CARGA CUANDO stsatus_to es mayor que self.status
    ## @param statusneeded  Integer with the status needed 
    ## @param downgrade_to Integer with the status to downgrade before checking needed status. If None it does nothing
    def needStatus(self, statusneeded, downgrade_to=None):
        if downgrade_to!=None:
            self.status=downgrade_to
        
        
        if self.status==statusneeded:
            return
        #0
        if self.status==0 and statusneeded==1: #MAIN
            start=datetime.datetime.now()
            self.estimations_dps=EstimationDPSManager(self.mem, self)
            self.estimations_dps.load_from_db()
            self.splits=SplitManager(self.mem, self)
            self.splits.init__from_db("select * from splits where products_id={} order by datetime".format(self.id))
            self.result=QuotesResult(self.mem, self)
            self.result.get_basic()
            
            logging.debug("Product {} took {} to pass from status {} to {}".format(self.name, datetime.datetime.now()-start, self.status, statusneeded))
            self.status=1
        elif self.status==0 and statusneeded==2:
            self.needStatus(1)
            self.needStatus(2)
        elif self.status==0 and statusneeded==3:
            self.needStatus(1)
            self.needStatus(2)
            self.needStatus(3)
        elif self.status==1 and statusneeded==2: #MAIN
            start=datetime.datetime.now()
            self.estimations_eps=EstimationEPSManager(self.mem, self)
            self.estimations_eps.load_from_db()
            self.dps=DPSManager(self.mem, self)
            self.dps.load_from_db()           
            self.result.get_ohcls()
            logging.debug("Product {} took {} to pass from status {} to {}".format(self.name, datetime.datetime.now()-start, self.status, statusneeded))
            self.status=2
        elif self.status==1 and statusneeded==3:
            self.needStatus(2)
            self.needStatus(3)
        elif self.status==2 and statusneeded==3:#MAIN
            start=datetime.datetime.now()
            self.result.get_all()
            logging.debug("Product {} took {} to pass from status {} to {}".format(self.name, datetime.datetime.now()-start, self.status, statusneeded))
            self.status=3
        
    def setinvestments(self):
        """Returns a InvestmentManager object with all the investments of the product. Investments can be active or inactive"""
        set=InvestmentManager(self.mem, self.mem.data.accounts, self.mem.data.products, self.mem.data.benchmark)
        sql="""
            SELECT * 
            FROM 
                inversiones 
            WHERE
                products_id={}
            ORDER BY
                inversion
        """.format(self.id)
        set.load_from_db(sql,  progress=False)
        return set

    def hasSameLocalCurrency(self):
        """
            Returns a boolean
            Check if product currency is the same that local currency
        """
        if self.currency.id==self.mem.localcurrency.id:
            return True
        return False

    def has_basic_data(self):
        """Returns (True,True,True,True) if product has last and penultimate quotes (last, penultimate, lastyear, thisyearestimation_dps)"""
#        result=QuotesResult(self.mem, self)
#        result.get_basic_and_ohcls()
#        dps=EstimationDPS(self.mem).init__from_db(self, datetime.date.today().year)
#        print (dps.estimation, dps)
        self.needStatus(1)
        (last, penultimate, lastyear, estimation)=(False, False, False, False)
        if self.result.basic.last: 
            if self.result.basic.last.quote:
                last=True
        if self.result.basic.penultimate: 
            if self.result.basic.penultimate.quote:
                penultimate=True
        if self.result.basic.lastyear: 
            if self.result.basic.lastyear.quote:
                lastyear=True
        if self.dps:
           if self.dps.estimation!=None:
                estimation=True
        return (last, penultimate, lastyear, estimation)
        
        
    def is_deletable(self):
        if self.is_system():
            return False
            
        #Search in all investments
        for i in self.mem.data.investments.arr:
            if i.product.id==self.id:
                return False
        
        #Search in benchmark
        if self.mem.data.benchmark.id==self.id:
            return False
        
        return True       

    def is_system(self):
        """Returns if the product is a system product or a user product"""
        if self.id>=0:
            return True
        return False

    ## @return boolen if could be done
    ## NO HACE COMMIT
    def remove(self):     
        if self.is_deletable()==True and self.is_system()==False:
            cur=self.mem.con.cursor()
            cur.execute("delete from quotes where id=%s", (self.id, ))
            cur.execute("delete from estimations_dps where id=%s", (self.id, ))
            cur.execute("delete from estimations_eps where id=%s", (self.id, ))
            cur.execute("delete from dps where id=%s", (self.id, ))
            cur.execute("delete from splits where products_id=%s", (self.id, ))
            cur.execute("delete from opportunities where products_id=%s", (self.id, ))
            cur.execute("delete from products where id=%s", (self.id, ))
            cur.close()
            self.needStatus(0, downgrade_to=0)
            return True
        return False

    def fecha_ultima_actualizacion_historica(self):
        """
            Si es acciones, etf, indexes, warrants, currencies, publicbond, private bond buscará el microsegundo 4
            Si es fondo, plan de pensiones buscará la última cotización
        """
        cur=self.mem.con.cursor()
        if self.type.id in [eProductType.Share, eProductType.ETF, eProductType.Index, eProductType.Warrant, eProductType.Currency, eProductType.PublicBond, eProductType.PrivateBond]:
            cur.execute("select max(datetime)::date as date from quotes where date_part('microsecond',datetime)=4 and id=%s", (self.id, ))
        else:
            cur.execute("select max(datetime)::date as date from quotes where id=%s", (self.id, ))
        dat=cur.fetchone()[0]
        if dat==None:
            resultado=datetime.date(self.mem.fillfromyear, 1, 1)
        else:
            resultado=dat
        cur.close()
        return resultado


    ## Search in Internet for last quote information
    ## @return QuoteManager QuoteManager object with the quotes found in Internet
    def update(self):
        r=QuoteManager(self.mem)
        r.print()

class QuoteManager(ObjectManager):
    """Clase que agrupa quotes un una lista arr. Util para operar con ellas como por ejemplo insertar, puede haber varios productos"""
    def __init__(self, mem):
        ObjectManager.__init__(self)
        self.mem=mem
    
    def save(self):
        """Recibe con code,  date,  time, value, zone
            Para poner el dato en close, el valor de time debe ser None
            Devuelve una tripleta (insertado,buscados,modificados)
        """
        insertados=QuoteManager(self.mem)
        ignored=QuoteManager(self.mem)
        modificados=QuoteManager(self.mem)    
        malos=QuoteManager(self.mem)
            
        for q in self.arr:
            if q.can_be_saved():#Debe hacerse en automaticos
                ibm=q.save()
                if ibm==1:
                    insertados.append(q)
                elif ibm==2:
                    modificados.append(q)
                elif ibm==3:
                    ignored.append(q)
            else:
                malos.append(q)
                
        print ("{} SetMyquotes.save".format(len(self.arr)), insertados.length(), ignored.length(), modificados.length(), malos.length())
        return (insertados, ignored, modificados, malos)

    def addTo(self, settoadd):
        """Añade los quotes en array a un nuevo set paasado por parametro"""
        for q in self.arr:
            settoadd.append(q)
        
    def myqtablewidget(self, tabla):
        tabla.setColumnCount(3)
        tabla.setHorizontalHeaderItem(0, QTableWidgetItem(QApplication.translate("Core","Date and time" )))
        tabla.setHorizontalHeaderItem(1, QTableWidgetItem(QApplication.translate("Core","Product" )))
        tabla.setHorizontalHeaderItem(2, QTableWidgetItem(QApplication.translate("Core","Price" )))        
        tabla.applySettings()
        tabla.clearContents() 
        tabla.setRowCount(len(self.arr))
        for rownumber, a in enumerate(self.arr):
            tabla.setItem(rownumber, 0, qdatetime(a.datetime, self.mem.localzone))
            tabla.setItem(rownumber, 1, qleft(a.product.name))
            tabla.item(rownumber, 1).setIcon(a.product.stockmarket.country.qicon())
            tabla.setItem(rownumber, 2, a.product.currency.qtablewidgetitem(a.quote))
                
                
class QuoteAllIntradayManager(ObjectManager):
    """Class that groups all quotes of the database. It's an array of QuoteIntradayManager"""
    def __init__(self, mem):
        ObjectManager.__init__(self)
        self.mem=mem
        self.product=None
 
    def load_from_db(self,  product):
        """Función que mete en setquotesintradia ordenado de objetos Quote, no es el ultimo día es un día"""
        del self.arr
        self.arr=[]
        self.product=product
        cur=self.mem.con.cursor()
        cur.execute("select * from quotes where id=%s order by datetime", (self.product.id,  ))
        
        intradayarr=[]
        dt_end=None
        for row in cur:
            if dt_end==None:#Loads the first datetime
                dt_end=day_end(row['datetime'], self.product.stockmarket.zone)
            if row['datetime']>dt_end:#Cambio de QuoteIntradayManager
                self.arr.append(QuoteIntradayManager(self.mem).init__create(self.product, dt_end.date(), intradayarr))
                dt_end=day_end(row['datetime'], self.product.stockmarket.zone)
                #crea otro intradayarr
                del intradayarr
                intradayarr=[]
                intradayarr.append(Quote(self.mem).init__db_row(row, self.product))
            else:
                intradayarr.append(Quote(self.mem).init__db_row(row, self.product))
        #No entraba si hay dos días en el primer día
        if len(intradayarr)!=0:
            self.arr.append(QuoteIntradayManager(self.mem).init__create(self.product, dt_end.date(), intradayarr))
            
        cur.close()

        
    def find(self, dattime):
        """Recorro de mayor a menor"""
        for i,  sqi in enumerate(reversed(self.arr)):
            if sqi.date<=dattime.date():
                found=sqi.find(dattime)
                if found==None:#Si no lo encuntra por que hay un quote de la misma fecha, pero es mayor que el que busco. Daba errores
                    continue
                else:
                    return found                    
        logging.critical("Quote not found in QuoteAllIntradayManager of {} at {}".format(self.product, dattime))
        return None
            
            
    def purge(self, progress=False):
        """Purga todas las quotes de la inversión. Si progress es true muestra un QProgressDialog. 
        Devuelve el numero de quotes purgadas
        Si devuelve None, es que ha sido cancelado por el usuario, y no debería hacerse un comiti en el UI
        Sólo purga fichas menores a hoy()-30"""
        if progress==True:
            pd= QProgressDialog(QApplication.translate("Core","Purging innecesary data"), QApplication.translate("Core","Cancel"), 0,len(self.arr))
            pd.setModal(True)
            pd.setWindowTitle(QApplication.translate("Core","Purging quotes"))
            pd.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
            pd.setMinimumDuration(0)          
        counter=0
        for i, sqi in enumerate(self.arr):
            if progress==True:
                pd.setValue(i)
                pd.setLabelText(QApplication.translate("Core","Purged {0} quotes from {1}").format(counter, self.product.name))
                pd.update()
                QApplication.processEvents()
                if pd.wasCanceled():
                    return None
                QApplication.processEvents()
            if sqi.date<datetime.date.today()-datetime.timedelta(days=30):
                counter=counter+sqi.purge()
        return counter
        
class QuoteBasicManager:
    """Clase que agrupa quotes basic, last penultimate, lastyear """
    def __init__(self, mem, product):
        self.mem=mem
        self.lastyear=None
        self.last=None
        self.penultimate=None
        self.product=product       
        
    def init__create(self, last,  penultimate, lastyear):
        self.last=last
        self.penultimate=penultimate
        self.lastyear=lastyear
        return self
       
    
    def load_from_db(self):
        """
            Función que carga last, penultimate y lastdate 
            To see if there is a good value, You must search for datetime!= None or quote!=None
        """
        cur=self.mem.con.cursor()
        cur.execute("select * from last_penultimate_lastyear(%s)", (self.product.id, ))
        row=cur.fetchone()
        self.last=Quote(self.mem).init__create(self.product, row['last_datetime'], row['last'])
        self.penultimate=Quote(self.mem).init__create(self.product, row['penultimate_datetime'], row['penultimate'])
        self.lastyear=Quote(self.mem).init__create(self.product, row['lastyear_datetime'], row['lastyear'])

    def tpc_diario(self):
        if self.last.quote==None or self.penultimate.quote==None:
            return Percentage()
        else:
            return Percentage(self.last.quote-self.penultimate.quote, self.penultimate.quote)

    def tpc_anual(self):
        if self.lastyear.quote==None or self.lastyear.quote==0 or self.last.quote==None:
            return Percentage()
        else:
            return Percentage(self.last.quote-self.lastyear.quote, self.lastyear.quote)

class QuoteIntradayManager(QuoteManager):
    """Clase que agrupa quotes un una lista arr de una misma inversión y de un mismo día. """
    def __init__(self, mem):
        QuoteManager.__init__(self, mem)
        self.product=None
        self.date=None
        
    def load_from_db(self,  date, product):
        """Función que mete en setquotesintradia ordenado de objetos Quote, no es el ultimo día es un día"""
        del self.arr
        self.arr=[]
        self.product=product
        self.date=date
        cur=self.mem.con.cursor()
        iniciodia=day_start_from_date(date, self.product.stockmarket.zone)
        siguientedia=iniciodia+datetime.timedelta(days=1)
        cur.execute("select * from quotes where id=%s and datetime>=%s and datetime<%s order by datetime", (self.product.id,  iniciodia, siguientedia))
        for row in cur:
            self.append(Quote(self.mem).init__db_row(row,  self.product))
        cur.close()
        
    def init__create(self, product, date, arrquotes):
        self.product=product
        self.date=date
        for q in arrquotes:
            self.arr.append(q)
        return self
        
    def open(self):
        """Devuelve el quote cuyo datetime es menor"""
        if len(self.arr)>0:
            return self.arr[0]
        return None
            
    def close(self):
        """Devuelve el quote cuyo datetime es mayor"""
        if len(self.arr)>0:
            return self.arr[len(self.arr)-1]
        return None
            
    def high(self):
        """Devuelve el quote cuyo quote es mayor"""
        if len(self.arr)==0:
            return None
        high=self.arr[0]
        for q in self.arr:
            if q.quote>high.quote:
                high=q
        return high
        
    def low(self):
        """Devuelve el quote cuyo quote es menor"""
        if len(self.arr)==0:
            return None
        low=self.arr[0]
        for q in self.arr:
            if q.quote<low.quote:
                low=q
        return low
        
    def find(self, dt):
        for q in reversed(self.arr):
            if q.datetime<=dt:
                return q
        logging.info("Quote not found in QuoteIntradayManager ({}) of {} at {}. En el set hay {}".format(self.date,  self.product, dt, self.arr))
        return None

    def datetimes(self):
        """Returns a list with datetimes"""
        r=[]
        for quote in self.arr:
            r.append(quote.datetime)
        return r
        
    def quotes(self):
        """Show product quotes of the day"""
        r=[]
        for quote in self.arr:
            r.append(quote.quote)
        return r



    def purge(self):
        """Función que purga una inversión en un día dado, dejando ohlc y microsecond=5, que son los no borrables.
        Devuelve el número que se han quitado
        Esta función no hace un commit.
        """
        todelete=[]
        protected=[self.open(), self.close(), self.high(), self.low()]
        for q in self.arr:
            if q not in protected:
                if q.datetime.microsecond!=5:
                    todelete.append(q)

        if len(todelete)>0:
            for q in todelete:
                self.arr.remove(q)
                q.delete()
                
            ##Reescribe microseconds si ya el close tenía un 4
            if self.close().datetime.microsecond==4 : #SOLO SI TODELETE >0
                self.rewrite_microseconds()
                
        return len(todelete)
        
    def rewrite_microseconds(self):
        """Reescribe los microseconds de close,...
        Los escribe en orden de importancia"""
        c=self.close()
        if c!=None:
            c.delete()
            c.datetime=c.datetime.replace(microsecond=4)
            c.save()
            
    def variance(self):
        """Gives difference between highest and lowest prices"""
        return self.high().quote - self.low().quote
        
    def variance_percentage(self):
        """Gives variance percentage, using the lowest quote to calculate it to see daily volatility only. It's always a positive number"""
        h=self.high().quote
        l=self.low().quote
        return Percentage(h-l, l)

    def myqtablewidget(self, table): 
        
        if self.product.hasSameLocalCurrency():
            table.setColumnCount(3)
        else:
            table.setColumnCount(5)
            table.setHorizontalHeaderItem(3, QTableWidgetItem(QApplication.translate("Core","Price")))
            table.setHorizontalHeaderItem(4, QTableWidgetItem(QApplication.translate("Core","% Daily")))
        table.setHorizontalHeaderItem(0, QTableWidgetItem(QApplication.translate("Core","Time")))
        table.setHorizontalHeaderItem(1, QTableWidgetItem(QApplication.translate("Core","Price")))
        table.setHorizontalHeaderItem(2, QTableWidgetItem(QApplication.translate("Core","% Daily")))
        table.applySettings()
        table.clearContents()
        table.setRowCount(self.length())
        QuoteDayBefore=Quote(self.mem).init__from_query(self.product, day_start_from_date(self.date, self.mem.localzone))#day before as selected

        ##Construye tabla
        for i , q in enumerate(self.arr):
            table.setItem(i, 0, qtime(q.datetime))
            table.setItem(i, 1, self.product.currency.qtablewidgetitem(q.quote,6))
            tpcq=Percentage(q.quote-QuoteDayBefore.quote, QuoteDayBefore.quote)
            table.setItem(i, 2, tpcq.qtablewidgetitem())
            if self.product.hasSameLocalCurrency()==False:
                moneybefore=QuoteDayBefore.money().convert(self.mem.localcurrency, q.datetime)
                money=q.money().convert(self.mem.localcurrency, q.datetime)
                table.setItem(i, 3, money.qtablewidgetitem(6))
                tpcq=Percentage(money-moneybefore, moneybefore)
                table.setItem(i, 4, tpcq.qtablewidgetitem())
                
            if q==self.high():
                table.item(i, 1).setBackground(eQColor.Green)
            elif q==self.product.result.intradia.low():
                table.item(i, 1).setBackground(eQColor.Red)             
        table.setCurrentCell(self.length()-1, 0)
        table.clearSelection()

## Class to manage source xulpymoney_run_client and other scripts
## Update works creating a file in ____ and theen executing xulpymoney_run_client
class ProductUpdate:
    ## @param mem Memory Singleton
    def __init__(self, mem):
        self.mem=mem
        self.commands=[]
    
    ## Adds a command that will be inserted in  "{}/clients.txt".format(dir_tmp)
    ## Example: self.appendCommand(["xulpymoney_morningstar_client","--TICKER_XULPYMONEY",  p.tickers[eTickerPosition.Morningstar], str(p.id)])       
    def appendCommand(self, command):
        self.commands.append(command)

     ## Generates "{}/clients.txt".format(dir_tmp)
    def __generateCommandsFile(self):
        filename="{}/clients.txt".format(self.mem.dir_tmp)
        f=open(filename, "w")
        for a in self.commands:
            f.write(" ".join(a) + "\n")
        f.close()
        logging.debug("Added {} comandos to {}".format(len(self.commands), filename))

    ## Reads ("{}/clients_result.txt".format(self.mem.dir_tmp), an return a strubg
    def readResults(self):
        f=open("{}/clients_result.txt".format(self.mem.dir_tmp), "r")
        r=f.read()
        f.close()
        return r


    ## Returns a set with all ids of products that are searched in ProductUpdate.setGlobalCommands.
    ##
    ## Developer must change this querys after changeing setGlobalCommands querys.
    ## @param mem. Xulpymoney mem
    ## @return set. Set with integers (products_id)
    @staticmethod
    def generateAutoupdateSet(mem):
        r=set()
        used=""
        ##### BOLSAMADRID #####
        cur=mem.con.cursor()
        sqls=[
            "select * from products where type in (1,4) and obsolete=false and stockmarkets_id=1 and isin is not null and isin<>'' {} order by name".format(used), 
            "select * from products where type in ({}) and obsolete=false and stockmarkets_id=1 and isin is not null {} order by name".format(eProductType.PublicBond, used), 
            "select * from products where type in ({},{}) and obsolete=false and tickers[{}] is not null {} order by name".format(eProductType.ETF, eProductType.Share, eTickerPosition.postgresql(eTickerPosition.Google), used), 
            "select * from products where type in ({}) and obsolete=false and tickers[{}] is not null order by name".format(eProductType.Index,  eTickerPosition.postgresql(eTickerPosition.Google)), 
            "select * from products where type in ({}) and tickers[{}] is not null and obsolete=false is not null order by name".format(eProductType.Currency,  eTickerPosition.postgresql(eTickerPosition.Yahoo)), 
            "select * from products where type={} and stockmarkets_id=1 and obsolete=false and tickers[{}] is not null {} order by name".format(eProductType.PensionPlan.value, eTickerPosition.postgresql(eTickerPosition.QueFondos), used), 
            "select * from products where tickers[{}] is not null and obsolete=false {} order by name".format(eTickerPosition.postgresql(eTickerPosition.Morningstar),  used)
        ]
        for sql in sqls:
            cur.execute(sql)
            for row in cur:
                r.add(row['id'])
        cur.close()
        return r





    ## Function that executes xulpymoney_run_client and generate a QuoteManager 
    ## Source commands must be created before in file "{}/clients.txt".format(dir_tmp)
    ## Output of the xulpymoney_run_client command is generated in ("{}/clients_result.txt".format(self.mem.dir_tmp),
    ## After run, clears self.command array
    ## @return QuoteManager
    def run(self):        
        self.__generateCommandsFile()
        quotes=QuoteManager(self.mem)
        os.system("xulpymoney_run_client")
        cr=open("{}/clients_result.txt".format(self.mem.dir_tmp), "r")
        for line in cr.readlines():
            if line.find("OHCL")!=-1:
                ohcl=OHCLDaily(self.mem).init__from_client_string(line[:-1])
                if ohcl!=None:
                    for quote in ohcl.generate_4_quotes():
                        if quote!=None:
                            quotes.append(quote)
            if line.find("PRICE")!=-1:
                quote=Quote(self.mem).init__from_client_string(line[:-1])
                if quote!=None:
                    quotes.append(quote)
        cr.close()
        self.commands=[]
        return quotes

    ## Sets commands for a product update
    def setCommands(self,  product):
        if product.tickers[eTickerPosition.Yahoo]!=None:
            self.appendCommand(["xulpymoney_yahoo_client","--TICKER_XULPYMONEY",  product.tickers[eTickerPosition.Yahoo], str(product.id)])
            
    ## Sets commands for all products
    ## @param all if this boolean it's True, tries to get all products updates. If it's False it tries to get used product in investment, indexes and currencies
    def setGlobalCommands(self, all):
        oneday=datetime.timedelta(days=1)
        if all==True:
            used=""
        else:
            used=" and id in (select products_id from inversiones) "
        ##### BOLSAMADRID #####
        sql="select * from products where type in (1,4) and obsolete=false and stockmarkets_id=1 and isin is not null and isin<>'' {} order by name".format(used)
        products=ProductManager(self.mem)
        products.load_from_db(sql)    
        for p in products.arr:
            ultima=p.fecha_ultima_actualizacion_historica()
            if datetime.date.today()>ultima+oneday:#Historical data is always refreshed the next day, so dont work again
                if p.type.id==eProductType.ETF:
                    self.appendCommand(["xulpymoney_bolsamadrid_client","--ISIN_XULPYMONEY",  p.isin, str(p.id),  "--etf","--fromdate", str( p.fecha_ultima_actualizacion_historica()+oneday)])
                elif p.type.id==eProductType.Share:
                    self.appendCommand(["xulpymoney_bolsamadrid_client","--ISIN_XULPYMONEY",  p.isin, str(p.id),"--share","--fromdate", str( p.fecha_ultima_actualizacion_historica()+oneday)])
                    
        self.appendCommand(["xulpymoney_bolsamadrid_client","--share"]+products.ProductManager_with_same_type(self.mem.types.find_by_id(eProductType.Share.value)).list_ISIN_XULPYMONEY()) # SHARES INTRADAY

        self.appendCommand(["xulpymoney_bolsamadrid_client","--etf"]+products.ProductManager_with_same_type(self.mem.types.find_by_id(eProductType.ETF.value)).list_ISIN_XULPYMONEY()) # SHARES INTRADAY

        sql="select * from products where type in ({}) and obsolete=false and stockmarkets_id=1 and isin is not null {} order by name".format(eProductType.PublicBond, used)        
        bm_publicbonds=ProductManager(self.mem)
        bm_publicbonds.load_from_db(sql)    
        self.appendCommand(["xulpymoney_bolsamadrid_client","--publicbond"]+bm_publicbonds.list_ISIN_XULPYMONEY())#MUST BE INTRADAY
        
        ibex=Product(self.mem).init__db(79329)
        self.appendCommand(["xulpymoney_bolsamadrid_client","--ISIN_XULPYMONEY",  ibex.isin, str(ibex.id),"--index","--fromdate", str(ibex.fecha_ultima_actualizacion_historica()+oneday)])

        ##### GOOGLE #####
        sql="select * from products where type in ({},{}) and obsolete=false and tickers[{}] is not null {} order by name".format(eProductType.ETF, eProductType.Share, eTickerPosition.postgresql(eTickerPosition.Google), used)
        print(sql)
        products=ProductManager(self.mem)
        products.load_from_db(sql)    
        for p in products.arr:
            self.appendCommand(["xulpymoney_google_client","--TICKER_XULPYMONEY",  p.tickers[eTickerPosition.Google], str(p.id), "--STOCKMARKET", str(p.stockmarket.id)])

        ##### GOOGLE INDICES  #####
        sql="select * from products where type in ({}) and obsolete=false and tickers[{}] is not null order by name".format(eProductType.Index,  eTickerPosition.postgresql(eTickerPosition.Google))
        print(sql)
        products=ProductManager(self.mem)
        products.load_from_db(sql)    
        for p in products.arr:
            self.appendCommand(["xulpymoney_google_client","--TICKER_XULPYMONEY",  p.tickers[eTickerPosition.Google], str(p.id), "--STOCKMARKET", str(p.stockmarket.id)])

        ##### INFOBOLSA CURRENCIES  #####
        sql="select * from products where type in ({}) and tickers[{}] is not null and obsolete=false is not null order by name".format(eProductType.Currency,  eTickerPosition.postgresql(eTickerPosition.Yahoo))
        print(sql)
        products=ProductManager(self.mem)
        products.load_from_db(sql)    
        for p in products.arr:
            self.appendCommand(["xulpymoney_infobolsa_client","--TICKER_XULPYMONEY",  p.tickers[eTickerPosition.Yahoo], str(p.id), "--STOCKMARKET", str(p.stockmarket.id)])

        ##### QUE FONDOS ####
        sql="select * from products where type={} and stockmarkets_id=1 and obsolete=false and tickers[{}] is not null {} order by name".format(eProductType.PensionPlan.value, eTickerPosition.postgresql(eTickerPosition.QueFondos), used)
        products_quefondos=ProductManager(self.mem)#Total of products_quefondos of an Agrupation
        products_quefondos.load_from_db(sql)    
        for p in products_quefondos.arr:
            ultima=p.fecha_ultima_actualizacion_historica()
            if datetime.date.today()>ultima+oneday:#Historical data is always refreshed the next day, so dont work agan
                self.appendCommand(["xulpymoney_quefondos_client","--TICKER_XULPYMONEY",  p.tickers[eTickerPosition.QueFondos], str(p.id),  "--STOCKMARKET", str(p.stockmarket.id)])    
                
        ##### MORNINGSTAR FONDOS #####
        sql="select * from products where type={} and tickers[{}] is not null and obsolete=false {} order by name".format(eProductType.Fund, eTickerPosition.postgresql(eTickerPosition.Morningstar),  used)
        products_morningstar=ProductManager(self.mem)#Total of products_morningstar of an Agrupation
        products_morningstar.load_from_db(sql)    
        for p in products_morningstar.arr:
            ultima=p.fecha_ultima_actualizacion_historica()
            if datetime.date.today()>ultima+oneday:#Historical data is always refreshed the next day, so dont work again
                self.appendCommand(["xulpymoney_morningstar_client", "--fund", "--TICKER_XULPYMONEY",  p.tickers[eTickerPosition.Morningstar], str(p.id), "--STOCKMARKET", str(p.stockmarket.id)])         
                
        ##### MORNINGSTAR ETF #####
        sql="select * from products where type={} and tickers[{}] is not null and obsolete=false {} order by name".format(eProductType.ETF, eTickerPosition.postgresql(eTickerPosition.Morningstar),  used)
        products_morningstar=ProductManager(self.mem)#Total of products_morningstar of an Agrupation
        products_morningstar.load_from_db(sql)    
        for p in products_morningstar.arr:
            self.appendCommand(["xulpymoney_morningstar_client", "--etf", "--TICKER_XULPYMONEY",  p.tickers[eTickerPosition.Yahoo], str(p.id), "--STOCKMARKET", str(p.stockmarket.id)])

## Class that represents a Quote
## A quote can be a datetime duplicated
class Quote:
    """Un quote no puede estar duplicado en un datetime solo puede haber uno"""
    def __init__(self, mem):
        self.mem=mem
        self.product=None
        self.quote=None
        self.datetime=None
        
    def __repr__(self):
        return "Quote de {} ({}) de fecha {} vale {}".format(self.product.name, self.product.id,  self.datetime, self.quote)
        
    def init__create(self,  product,  datetime,  quote):
        """Función que crea un Quote nuevo, con la finalidad de insertarlo
        quote must be a Decimal object."""
        self.product=product
        self.datetime=datetime
        self.quote=quote
        return self
        
    def exists(self):
        """Función que comprueba si existe en la base de datos y devuelve el valor de quote en caso positivo en una dupla""" 
        (status, reg)=(False, None)
        cur=self.mem.con.cursor()
        cur.execute("select quote from quotes where id=%s and  datetime=%s;", (self.product.id, self.datetime))
        if cur.rowcount!=0:
            reg=cur.fetchone()[0]
            status=True
        cur.close()
        return (status, reg)
        
        
    def can_be_saved(self):
        """Returns a boolean True if can be saved, debe usurse en los autokkmaticos. Puede haber algun manual que quiera ser 0"""
        r=True
        if self.quote==Decimal(0):
            r=False
        return r
        
    def money(self):
        """
            Returns a MOney Object
        """
        return Money(self.mem, self.quote, self.product.currency)
    
    def none(self, product):
        return self.init__create(product, None, None)
        
    def save(self):
        """Función que graba el quotes si coincide todo lo ignora. Si no coincide lo inserta o actualiza.
        No hace commit a la conexión
        Devuelve un número 1 si insert, 2 update, 3 ya  exisitia
        """
        r=None
        cur=self.mem.con.cursor()
        exists=self.exists()
        if exists[0]==False:
            cur.execute('insert into quotes (id, datetime, quote) values (%s,%s,%s)', ( self.product.id, self.datetime, self.quote))
            r=1
        else:
            if exists[1]!=self.quote:
                cur.execute("update quotes set quote=%s where id=%s and datetime=%s", (self.quote, self.product.id, self.datetime))
                r=2
            else: #ignored
                r=3
        cur.close()
        return r
                
    def delete(self):
        cur=self.mem.con.cursor()
        cur.execute("delete from quotes where id=%s and datetime=%s", (self.product.id, self.datetime))
        cur.close()

    def init__db_row(self, row, product):
        if row==None:
            return self.init__create(product, None, None)
        return self.init__create(product, row['datetime'], row['quote'])

    def init__from_query(self, product, dt): 
        """Función que busca el quote de un id y datetime con timezone"""
        cur=self.mem.con.cursor()
        cur.execute("select * from quote (%s,%s)", (product.id,  dt))
        row=cur.fetchone()
        cur.close()
        return self.init__db_row(row, product)
                
    def init__from_query_penultima(self,product,  lastdate=None):
        cur=self.mem.con.cursor()
        if lastdate==None:
            lastdate=datetime.date.today()
        cur.execute("select * from penultimate(%s,%s)", (product.id, lastdate ))
        row=cur.fetchone()
        cur.close()
        return self.init__db_row(row, product)        
    def init__from_client_string(self, s):
        """
            Creates a Quote object from client scrapper line
            PRICE | XULPYMONEY | 78139 | 2017-11-20 23:00:00+00:00 | 12.66
        """
        try:
            a=s.split(" | ")
            self.product=Product(self.mem).init__db(int(a[2]))
            if a[3].find(".")!=-1:#With microseconds
                self.datetime=string2datetime(a[3], type=5)
            else:#Without microsecond
                self.datetime=string2datetime(a[3], type=1)
            self.quote=Decimal(a[4])
        except:
            return None
        return self
        
## Class to manage Open High Close Low Values in a period of time of a productº
class OHCL:
    def __init__(self,  mem):
        self.mem=mem
        self.product=None
        self.open=None
        self.close=None
        self.high=None
        self.low=None
        
    
    ## Calcula el intervalo entre dos ohcl. El posteror es el que se pasa como parámetro
    def get_interval(self, ohclposterior):
        return ohclposterior.datetime-self.datetime

    def percentage(self, ohcl):
        """CAlcula el incremento en % en el cierre del ohcl actual y el pasado como parametro. Siendo el pasado como parametro posterior en el tiempo"""
        if ohcl:
            return Percentage(ohcl.close-self.close, self.close)            
        else:
            return Percentage()

        
class OHCLDaily(OHCL):
    def __init__(self, mem):
        OHCL.__init__(self, mem)
        self.date=None
        
    def init__from_client_string(self, s):
        """
            Generates a OHCL object from string from scrapper clients
            OHCL | XULPYMONEY | 81093 | 2017-11-21 | 0.0330 | 0.0330 | 0.0320 | 0.0310
        """
        a=s.split(" | ")
        try:
            self.product=Product(self.mem).init__db(int(a[2]))
            self.date=string2date(a[3])
            self.open=Decimal(a[4])
            self.high=Decimal(a[5])
            self.close=Decimal(a[6])
            self.low=Decimal(a[7])
        except:
            return None
        return self

    def generate_4_quotes(self):
        quotes=[]
        datestart=dtaware(self.date,self.product.stockmarket.starts,self.product.stockmarket.zone.name)
        dateends=dtaware(self.date,self.product.stockmarket.closes,self.product.stockmarket.zone.name)
        datetimefirst=datestart-datetime.timedelta(seconds=1)
        datetimelow=(datestart+(dateends-datestart)*1/3)
        datetimehigh=(datestart+(dateends-datestart)*2/3)
        datetimelast=dateends+datetime.timedelta(microseconds=4)

        quotes.append(Quote(self.mem).init__create(self.product,datetimelast, Decimal(self.close)))#closes
        quotes.append(Quote(self.mem).init__create(self.product,datetimelow, Decimal(self.low)))#low
        quotes.append(Quote(self.mem).init__create(self.product,datetimehigh, Decimal(self.high)))#high
        quotes.append(Quote(self.mem).init__create(self.product, datetimefirst, Decimal(self.open)))#open        
        return quotes
        
    def init__from_dbrow(self, row, product):
        self.product=product
        self.date=row['date']
        self.open=row['first']
        self.close=row['last']
        self.high=row['high']
        self.low=row['low']
        return self
        
    def datetime(self):
        """Devuelve un datetime usado para dibujar en gráficos"""
        return day_end_from_date(self.date, self.product.stockmarket.zone)
        
    def print_time(self):
        return "{0}".format(self.date)
        
    def clone(self):
        o=OHCLDaily(self.mem)
        o.product=self.product
        o.date=self.date
        o.open=self.open
        o.close=self.close
        o.high=self.high
        o.low=self.low
        return o
        
    ## Removes all quotes of the selected day
    def delete(self):
        cur=self.mem.con.cursor()
        cur.execute("delete from quotes where id=%s and datetime::date=%s", (self.product.id, self.date))
        cur.close()
        
class OHCLMonthly(OHCL):
    def __init__(self, mem):
        OHCL.__init__(self, mem)
        self.year=None
        self.month=None
        
    def init__from_dbrow(self, row, product):
        self.product=product
        self.year=int(row['year'])
        self.month=int(row['month'])
        self.open=row['first']
        self.close=row['last']
        self.high=row['high']
        self.low=row['low']
        return self
    def print_time(self):
        return "{0}-{1}".format(int(self.year), int(self.month))
        
                
    def clone(self):
        o=OHCLMonthly(self.mem)
        o.product=self.product
        o.year=self.year
        o.month=self.month
        o.open=self.open
        o.close=self.close
        o.high=self.high
        o.low=self.low
        return o
    def datetime(self):
        """Devuelve un datetime usado para dibujar en gráficos, pongo el día 28 para no calcular el último"""
        return day_end_from_date(datetime.date(self.year, self.month, 28), self.product.stockmarket.zone)
        
        
    ## Removes all quotes of the selected month and year
    def delete(self):
        cur=self.mem.con.cursor()
        cur.execute("delete from quotes where id=%s and date_part('month',datetime)=%s and date_part('year',datetime)=%s", (self.product.id, self.month, self.year))
        cur.close()        
                
class OHCLWeekly(OHCL):
    def __init__(self, mem):
        OHCL.__init__(self, mem)
        self.year=None
        self.week=None
        
    def init__from_dbrow(self, row, product):
        self.product=product
        self.year=int(row['year'])
        self.week=int(row['week'])
        self.open=row['first']
        self.close=row['last']
        self.high=row['high']
        self.low=row['low']
        return self
                        
    def clone(self):
        o=OHCLWeekly(self.mem)
        o.product=self.product
        o.year=self.year
        o.week=self.week
        o.open=self.open
        o.close=self.close
        o.high=self.high
        o.low=self.low
        return o
        
    def datetime(self):
        """Devuelve un datetime usado para dibujar en gráficos, con el último día de la semana"""
        d = datetime.date(self.year,1,1)
        d = d - datetime.timedelta(d.weekday())
        dlt = datetime.timedelta(days = (self.week-1)*7)
        lastday= d + dlt + datetime.timedelta(days=6)
        return day_end_from_date(lastday, self.product.stockmarket.zone)
        
    def print_time(self):
        return "{0}-{1}".format(self.year, self.week)

class OHCLYearly(OHCL):
    def __init__(self, mem):
        OHCL.__init__(self, mem)
        self.year=None
        
    def __repr__(self):
        return ("OHCLYearly ({}) of product {}".format( self.year, self.product.id))
        
    def init__from_dbrow(self, row, product):
        self.product=product
        self.year=int(row['year'])
        self.open=row['first']
        self.close=row['last']
        self.high=row['high']
        self.low=row['low']
        return self
                        
    def clone(self):
        o=OHCLDaily(self.mem)
        o.product=self.product
        o.year=self.year
        o.open=self.open
        o.close=self.close
        o.high=self.high
        o.low=self.low
        return o
    def datetime(self):
        """Devuelve un datetime usado para dibujar en gráficos"""
        return day_end_from_date(datetime.date(self.year, 12, 31), self.product.stockmarket.zone)
    def print_time(self):
        return "{0}".format(int(self.year))
    
    ## Removes all quotes of the selected year
    def delete(self):
        cur=self.mem.con.cursor()
        cur.execute("delete from quotes where id=%s and date_part('year',datetime)=%s", (self.product.id, self.year))
        cur.close()     

class OHCLManager(ObjectManager):
    def __init__(self, mem, product):
        ObjectManager.__init__(self)
        self.mem=mem
        self.product=product
    
    def load_from_db(self, sql):
        """El sql debe estar ordenado por date"""
        
        del self.arr
        self.arr=[]
        cur=self.mem.con.cursor()
        cur.execute(sql)#select * from ohclyearly where id=79329 order by date
        for row in cur:
            self.append(self.itemclass(self.mem).init__from_dbrow(row, self.product))
        cur.close()

    ## Returns a list with all the close of the array
    def closes(self, from_dt=None):
        closes=[]
        if from_dt==None:
            for ohcl in self.arr:
                closes.append(ohcl.close)
        else:
            for ohcl in self.arr:
                if ohcl.datetime()>=from_dt:
                    closes.append(ohcl.close)
        return closes


    def sma(self, number):
        """
        simple movil average
            Return a sma array of tuples (datetime,sma_n)
            Normal numbers are 50 and 200
            
        Calculamos segun
        a=[1,2,3,4]
        sum([0:2])=3
        """
        def average(inicio, final):
            suma=Decimal(0)
            for ohcl in self.arr[inicio:final]:
                suma=suma+ohcl.close
            return suma/(final-inicio)
        ######################
        if self.length()<=number:
            return None
            
        sma=[]
        for i, ohcl in enumerate(self.arr):
            if i>=number:
                sma.append((ohcl.datetime(), average(i-number, i)))
        return sma
        
    ## Calculates the median value of all OHCL.close values
    ## This function is in OHCLManager and can be used in all derivated classes
    ## @param from_dt Date from data is calculated. If it's None (default) if calculated the median value from all OHCL data in the array.
    def closes_median_value(self, from_dt=None):
        r=self.closes()
        r.sort()
        if self.length() % 2==0:#Par
            return r[self.length() // 2 -1]#n/2. But like I begin with 0 is -1
        else:
            return r[self.length() // 2]#If it's 5, median will be 3, but like I begin with 0 is integer division
        

    def opens(self, from_dt=None):
        """Returns a list with all the open of the array"""
        opens=[]
        if from_dt==None:
            for ohcl in self.arr:
                opens.append(ohcl.open)
        else:
            for ohcl in self.arr:
                if ohcl.datetime()>=from_dt:
                    opens.append(ohcl.open)
        return opens

    def highs(self, from_dt=None):
        """Returns a list with all the high of the array"""
        highs=[]
        if from_dt==None:
            for ohcl in self.arr:
                highs.append(ohcl.high)
        else:
            for ohcl in self.arr:
                if ohcl.datetime()>=from_dt:
                    highs.append(ohcl.high)
        return highs

    def lows(self, from_dt=None):
        """Returns a list with all the low of the array"""
        lows=[]
        if from_dt==None:
            for ohcl in self.arr:
                lows.append(ohcl.low)
        else:
            for ohcl in self.arr:
                if ohcl.datetime()>=from_dt:
                    lows.append(ohcl.low)
        return lows

    def datetimes(self, from_dt=None):
        """Returns a list with all the datetimes of the array"""
        datetimes=[]
        if from_dt==None:
            for ohcl in self.arr:
                datetimes.append(ohcl.datetime())
        else:
            for ohcl in self.arr:
                if ohcl.datetime()>=from_dt:
                    datetimes.append(ohcl.datetime())
        return datetimes

    def highest(self):
        if self.length()==0:
            return None
        r=self.arr[0]
        for ohcl in self.arr:
            if ohcl.close>=r.close:
                r=ohcl
        return r
        
    def lowest(self):
        if self.length()==0:
            return None
        r=self.arr[0]
        for ohcl in self.arr:
            if ohcl.close<=r.close:
                r=ohcl
        return r

class OHCLDailyManager(OHCLManager):
    def __init__(self, mem, product):
        OHCLManager.__init__(self, mem, product)
        self.itemclass=OHCLDaily

    def find(self, date):
        """Fucnción que busca un ohcldaily con fecha igual o menor de la pasada como parametro"""
        for ohcl in reversed(self.arr):
            if ohcl.date<=date:
                return ohcl
        return None



    ## Returns a QuoteBasicManager con los datos del setohcldairy
    def setquotesbasic(self):
        last=None
        penultimate=None
        lastyear=None
        if self.length()==0:
            return QuoteBasicManager(self.mem, self.product).init__create(Quote(self.mem).none(self.product), Quote(self.mem).none(self.product),  Quote(self.mem).none(self.product))
        ohcl=self.arr[self.length()-1]#last
        last=Quote(self.mem).init__create(self.product, dtaware(ohcl.date, self.product.stockmarket.closes,  self.product.stockmarket.zone.name), ohcl.close)
        ohcl=self.find(ohcl.date-datetime.timedelta(days=1))#penultimate
        if ohcl!=None:
            penultimate=Quote(self.mem).init__create(self.product, dtaware(ohcl.date, self.product.stockmarket.closes,  self.product.stockmarket.zone.name), ohcl.close)
        ohcl=self.find(datetime.date(datetime.date.today().year-1, 12, 31))#lastyear
        if ohcl!=None:
            lastyear=Quote(self.mem).init__create(self.product, dtaware(ohcl.date, self.product.stockmarket.closes,  self.product.stockmarket.zone.name), ohcl.close)        
        return QuoteBasicManager(self.mem, self.product).init__create(last, penultimate, lastyear)

    ## Returns a list with all the dates of the array
    def dates(self):
        r=[]
        for ohcl in self.arr:
            r.append(ohcl.date)
        return r
        

class OHCLWeeklyManager(OHCLManager):
    def __init__(self, mem, product):
        OHCLManager.__init__(self, mem, product)
        self.itemclass=OHCLWeekly
        
class OHCLYearlyManager(OHCLManager):
    def __init__(self, mem, product):
        OHCLManager.__init__(self, mem, product)
        self.itemclass=OHCLYearly
        

        
    ## Returns a OHCLYearly
    def find(self, year):
        for ohcl in self.arr:
            if ohcl.year==year:
                return ohcl
        return None
        
    def percentage_by_year(self, year):
        """
            Calcula el porcentaje del mes partiendo del punto de cierre del mes anterior
        """
        ohcl=self.find(year)
        lastohcl=self.find(year-1)
        if lastohcl:
            return lastohcl.percentage(ohcl)
        if ohcl:
            return Percentage((ohcl.close-ohcl.open), ohcl.open)
        else:
            return Percentage()
        
class OHCLMonthlyManager(OHCLManager):
    def __init__(self, mem, product):
        OHCLManager.__init__(self, mem, product)
        self.itemclass=OHCLMonthly
        
    def find(self, year,  month):
        for ohcl in self.arr:
            if ohcl.year==year and ohcl.month==month:
                return ohcl
        return None
        
        
    def percentage_by_year_month(self, year, month):
        """
            Calcula el porcentaje del mes partiendo del punto de cierre del mes anterior
        """
        dat=datetime.date(year, month, 1)
        last=dat-datetime.timedelta(days=1)
        ohcl=self.find(year, month)
        lastohcl=self.find(last.year, last.month)
        if lastohcl:
            return lastohcl.percentage(ohcl)
        else:
            return Percentage()
        
    
## Manages languages
class LanguageManager(ObjectManager_With_IdName_Selectable):
    def __init__(self, mem):
        ObjectManager_With_IdName_Selectable.__init__(self)
        self.mem=mem
        
    def load_all(self):
        self.append(Language(self.mem, "en","English" ))
        self.append(Language(self.mem, "es","Español" ))
        self.append(Language(self.mem, "fr","Français" ))
        self.append(Language(self.mem, "ro","Rom\xe2n" ))
        self.append(Language(self.mem, "ru",'\u0420\u0443\u0441\u0441\u043a\u0438\u0439' ))

    def qcombobox(self, combo, selected=None):
        """Selected is the object"""
        self.order_by_name()
        for l in self.arr:
            combo.addItem(self.mem.countries.find_by_id(l.id).qicon(), l.name, l.id)
        if selected!=None:
                combo.setCurrentIndex(combo.findData(selected.id))

    def cambiar(self, id):  
        """language es un string"""
        filename=pkg_resources.resource_filename("xulpymoney","i18n/xulpymoney_{}.qm".format(id))
        logging.debug(filename)
        self.mem.qtranslator.load(filename)
        logging.info("Language changed to {}".format(id))
        qApp.installTranslator(self.mem.qtranslator)
 
## Class that stores all kind of quotes asociated to a product
class QuotesResult:
    def __init__(self,mem,  product):
        self.mem=mem
        self.product=product

    def get_basic(self):
        self.basic=QuoteBasicManager(self.mem, self.product)
        self.basic.load_from_db()

#    ## Only once. If it's already in memory. It ignore it
#    ## @param force Boolean that if it'sTrue load from database again even if dps is not null
#    def load_dps_and_splits(self, force=False):
#        if self.product.dps==None or force==True:
#            self.product.dps=DPSManager(self.mem, self.product)
#            self.product.dps.load_from_db()     
#        if self.product.splits==None or force==True:
#            self.product.splits=SplitManager(self.mem, self.product)
#            self.product.splits.init__from_db("select * from splits where products_id={} order by datetime".format(self.product.id))
#        

    def get_intraday(self, date):
        self.intradia=QuoteIntradayManager(self.mem)
        self.intradia.load_from_db(date,  self.product)

    ## Function that generate all results and computes splits and dividends
    def get_ohcls(self):
        """Tambien sirve para recargar"""
        inicioall=datetime.datetime.now()  
                       
        # These are without splits nor dividends
        self.ohclDailyBeforeSplits=OHCLDailyManager(self.mem, self.product)
        self.ohclMonthlyBeforeSplits=OHCLMonthlyManager(self.mem, self.product)
        self.ohclYearlyBeforeSplits=OHCLYearlyManager(self.mem, self.product)
        self.ohclWeeklyBeforeSplit=OHCLWeeklyManager(self.mem, self.product)
        
        # These are with splits and without dividends
        self.ohclDaily=OHCLDailyManager(self.mem, self.product)
        self.ohclMonthly=OHCLMonthlyManager(self.mem, self.product)
        self.ohclYearly=OHCLYearlyManager(self.mem, self.product)
        self.ohclWeekly=OHCLWeeklyManager(self.mem, self.product)

        # These are with splits and dividends
        self.ohclDailyAfterDividends=OHCLDailyManager(self.mem, self.product)
        self.ohclMonthlyAfterDividends=OHCLMonthlyManager(self.mem, self.product)
        self.ohclYearlyAfterDividends=OHCLYearlyManager(self.mem, self.product)
        self.ohclWeeklyAfterDividends=OHCLWeeklyManager(self.mem, self.product)
        
        self.ohclDailyBeforeSplits.load_from_db("""
            select 
                id, 
                datetime::date as date, 
                (array_agg(quote order by datetime))[1] as first, 
                min(quote) as low, 
                max(quote) as high, 
                (array_agg(quote order by datetime desc))[1] as last 
            from quotes 
            where id={} 
            group by id, datetime::date 
            order by datetime::date 
            """.format(self.product.id))#necesario para usar luego ohcl_otros
            
        if self.product.splits.length()>0:
            self.ohclDaily=self.ohclDailyBeforeSplits.clone(self.mem, self.product)
            self.ohclDaily=self.product.splits.adjustOHCLDailyManager(self.ohclDaily)
        else:
            self.ohclDaily=self.ohclDailyBeforeSplits
            
        if self.product.dps.length()>0:
            self.ohclDailyAfterDividends=self.ohclDaily.clone(self.mem, self.product)
            self.ohclDailyAfterDividends=self.product.dps.adjustOHCLDailyManager(self.ohclDailyAfterDividends)
        else:
            self.ohclDailyAfterDividends=self.ohclDaily
            
        self.ohclMonthly.load_from_db("""
            select 
                id, 
                date_part('year',datetime) as year, 
                date_part('month', datetime) as month, 
                (array_agg(quote order by datetime))[1] as first, 
                min(quote) as low, 
                max(quote) as high, 
                (array_agg(quote order by datetime desc))[1] as last 
            from quotes 
            where id={} 
            group by id, year, month 
            order by year, month
        """.format(self.product.id))
        
        self.ohclWeekly.load_from_db("""
            select 
                id, 
                date_part('year',datetime) as year, 
                date_part('week', datetime) as week, 
                (array_agg(quote order by datetime))[1] as first, 
                min(quote) as low, 
                max(quote) as high, 
                (array_agg(quote order by datetime desc))[1] as last 
            from quotes 
            where id={} 
            group by id, year, week 
            order by year, week 
        """.format(self.product.id))
        
        self.ohclYearly.load_from_db("""
            select 
                id, 
                date_part('year',datetime) as year, 
                (array_agg(quote order by datetime))[1] as first, 
                min(quote) as low, max(quote) as high, 
                (array_agg(quote order by datetime desc))[1] as last 
            from quotes 
            where id={} 
            group by id, year 
            order by year 
        """.format(self.product.id))
        
        print ("QuotesResult.get_ohcls of '{}' took {} with {} splits and {} dividends".format(self.product.name, datetime.datetime.now()-inicioall, self.product.splits.length(), self.product.dps.length()))
        

    def get_all(self):
        """Gets all in a set intradays form"""
        self.all=QuoteAllIntradayManager(self.mem)
        self.all.load_from_db(self.product)

    ## Returns the OHCLManager corresponding to it's duration and if has splits and dividends adjust
    def ohcl(self,  ohclduration, historicalchartadjust=eHistoricalChartAdjusts.NoAdjusts):
        if ohclduration==eOHCLDuration.Day:
            if historicalchartadjust==eHistoricalChartAdjusts.Splits:
                return self.ohclDaily
            elif historicalchartadjust==eHistoricalChartAdjusts.NoAdjusts:
                return self.ohclDailyBeforeSplits
            elif historicalchartadjust==eHistoricalChartAdjusts.SplitsAndDividends:
                return self.ohclDailyAfterDividends
        if ohclduration==eOHCLDuration.Week:
            return self.ohclWeekly
        if ohclduration==eOHCLDuration.Month:
            return self.ohclMonthly
        if ohclduration==eOHCLDuration.Year:
            return self.ohclYearly

class Leverage:
    def __init__(self, mem):
        self.id=None
        self.name=None
        self.multiplier=None#Valor por el que multiplicar
    def init__create(self, id, name, multiplier):
        self.id=id
        self.name=name
        self.multiplier=multiplier
        return self
        
    
class Simulation:
    def __init__(self,mem, original_db):
        """Types are defined in combo ui wdgSimulationsADd
        database is the database which data is going to be simulated"""
        self.mem=mem
        self.database=original_db
        self.id=None
        self.name=None#self.simulated_db, used to reuse ObjectManager_With_IdName_Selectable
        self.creation=None
        self.type=None
        self.starting=None
        self.ending=None
        
    def init__create(self, type_id, starting, ending):
        """Used only to create a new one"""
        self.type=self.mem.simulationtypes.find_by_id(type_id)
        self.starting=starting
        self.ending=ending
        self.creation=self.mem.localzone.now()
        return self
        
    def simulated_db(self):
        """Returns"""
        return "{}_{}".format(self.database, self.id)    

    def init__db_row(self, row):
        self.id=row['id']
        self.database=row['database']
        self.creation=row['creation']
        self.type=self.mem.simulationtypes.find_by_id(row['type'])
        self.starting=row['starting']
        self.ending=row['ending']
        return self
        
    def save(self):
        cur=self.mem.con.cursor()
        print (self.type)
        if self.id==None:
            cur.execute("insert into simulations (database, type, starting, ending, creation) values (%s,%s,%s,%s,%s) returning id", (self.database, self.type.id, self.starting, self.ending, self.creation))
            self.id=cur.fetchone()[0]
            self.name=self.simulated_db()
        else:
            cur.execute("update simulations set database=%s, type=%s, starting=%s, ending=%s, creation=%s where id=%s", (self.database, self.type.id, self.starting, self.ending, self.creation, self.id))
        cur.close()

    def delete(self):
        cur=self.mem.con.cursor()
        cur.execute("delete from simulations where id=%s", (self.id, ))
        cur.close()

class SimulationType:
    def __init__(self):
        self.id=None
        self.name=None
    def init__create(self, id, name):
        self.id=id
        self.name=name
        return self
        

    def qicon(self):
        if self.id in (1, 2):
            return QIcon(":/xulpymoney/database.png")
        else:
            return QIcon(":/xulpymoney/replication.png")    

class Split:
    def __init__(self, mem):
        self.mem=mem
        self.id=None
        self.product=None
        self.datetime=None
        self.after=None
        self.before=None
        self.comment=None
                
    def __repr__(self):
        return ("Instancia de SplitNew: {0} ({1})".format( self.id, self.id))
        
    def init__create(self, product, datetime, before, after, comment, id=None):
        self.id=id
        self.product=product
        self.datetime=datetime
        self.after=after
        self.before=before
        self.comment=comment
        return self
        
    def init__db_row(self, row, product):
        return self.init__create(product,  row['datetime'],  row['before'], row['after'],   row['comment'],  row['id'])

    def save(self):
        cur=self.mem.con.cursor()
        if self.id==None:#Insertar
            cur.execute("insert into splits(products_id,datetime,after,before,comment) values (%s,%s,%s,%s,%s) returning id", (self.product.id, self.datetime, self.after, self.before, self.comment))
            self.id=cur.fetchone()[0]
        else:
            cur.execute("update splits set products_id=%s, datetime=%s, after=%s, before=%s, comment=%s where id=%s", (self.product.id, self.datetime, self.after, self.before, self.comment, self.id))
        cur.close()


    def convertShares(self, shares):
        """Function to calculate new shares just pass the number you need to convert"""
        return shares*self.after/self.before
        
    def convertPrices(self, price):
        return price*self.before/self.after
                
    def delete(self):
        cur=self.mem.con.cursor()
        cur.execute("delete from splits where id=%s", (self.id,))
        cur.close()
            
        
    def type(self):
        """Función que devuelve si es un Split o contrasplit"""
        if self.before>self.after:
            return "Contrasplit"
        else:
            return "Split"

class SplitManager(ObjectManager_With_IdName_Selectable):
    def __init__(self, mem, product):
        ObjectManager_With_IdName_Selectable.__init__(self)
        self.product=product
        self.mem=mem
        
    def init__from_db(self, sql):
        cur=self.mem.con.cursor()
        cur.execute(sql)
        for row in cur:
            self.append(Split(self.mem).init__db_row(row, self.product))
        cur.close()
        return self
            
    def order_by_datetime(self):
        """Orders the Set using self.arr"""
        try:
            self.arr=sorted(self.arr, key=lambda c: c.product.result.basic.last.datetime,  reverse=False)  
            return True
        except:
            return False
    def myqtablewidget(self, table):
        """Section es donde guardar en el config file, coincide con el nombre del formulario en el que está la table
        Devuelve sumatorios"""

        table.setColumnCount(4)
        table.setHorizontalHeaderItem(0, QTableWidgetItem(QApplication.translate("Core", "Date" )))
        table.setHorizontalHeaderItem(1, QTableWidgetItem(QApplication.translate("Core", "Before" )))
        table.setHorizontalHeaderItem(2, QTableWidgetItem(QApplication.translate("Core", "After" )))
        table.setHorizontalHeaderItem(3, QTableWidgetItem(QApplication.translate("Core", "Comment" )))
        #DATA  
        table.applySettings()
        table.clearContents()

        table.setRowCount(len(self.arr))
        for i, o in enumerate(self.arr):
            table.setItem(i, 0, qdatetime(o.datetime, self.mem.localzone))
            table.setItem(i, 1, qright(o.before))
            table.setItem(i, 2, qright(o.after))
            table.setItem(i, 3, qleft(o.comment))
                
    def delete(self, o):
        o.delete()    #Delete from database
        self.remove(o)    #Removes from array
        
    def adjustPrice(self, datetime, price):
        """
            Returns a new price adjusting
        """
        r=price
        for split in reversed(self.arr):
            if datetime<split.datetime:
                r=split.convertPrices(r)
        return r
        
    def adjustOHCLDaily(self, ohcl ):
        r=OHCLDaily(self.mem)
        r.product=ohcl.product
        r.date=ohcl.date
        r.close=self.adjustPrice(ohcl.datetime(), ohcl.close)
        r.open=self.adjustPrice(ohcl.datetime(), ohcl.open)
        r.high=self.adjustPrice(ohcl.datetime(), ohcl.high)
        r.low=self.adjustPrice(ohcl.datetime(), ohcl.low)
        return r

    def adjustOHCLDailyManager(self, set):
        r=OHCLDailyManager(self.mem, self.product)
        for ohcl in set.arr:
            r.append(self.adjustOHCLDaily(ohcl))
        return r

class SplitManual:
    """Class to make calculations with splits or contrasplits, between two datetimes"""
    def __init__(self, mem, product, sharesinitial,  sharesfinal,  dtinitial, dtfinal):
        self.mem=mem
        self.initial=sharesinitial
        self.final=sharesfinal
        self.dtinitial=dtinitial
        self.dtfinal=dtfinal
        self.product=product

    def convertShares(self, actions):
        """Function to calculate new shares just pass the number you need to convert"""
        return actions*self.final/self.initial
        
    def convertPrices(self, price):
        return price*self.initial/self.final
    
    def updateQuotes(self):
        """Transforms de price of the quotes of the array"""
        self.quotes=QuoteAllIntradayManager(self.mem)
        self.quotes.load_from_db(self.product)
        for setquoteintraday in self.quotes.arr:
            for q in setquoteintraday.arr:
                if self.dtinitial<=q.datetime and self.dtfinal>=q.datetime:
                    q.quote=self.convertPrices(q.quote)
                    q.save()
                    
    def updateDPS(self):
        set=DPSManager(self.mem, self.product)
        set.load_from_db()
        for d in set.arr:
            if self.dtinitial.date()<=d.date and self.dtfinal.date()>=d.date:
                d.gross=self.convertPrices(d.gross)
                d.save()
        
    def updateEPS(self):
        pass
        
    def updateEstimationsDPS(self):
        set=EstimationDPSManager(self.mem, self.product)
        set.load_from_db()
        for d in set.arr:
            if self.dtinitial.year<=d.year and self.dtfinal.year>=d.year:
                d.estimation=self.convertPrices(d.estimation)
                d.save()
        
    def updateEstimationsEPS(self):
        set=EstimationEPSManager(self.mem, self.product)
        set.load_from_db()
        for d in set.arr:
            if self.dtinitial.year<=d.year and self.dtfinal.year>=d.year:
                d.estimation=self.convertPrices(d.estimation)
                d.save()
        
        
    def updateOperInvestments(self):
        """Transforms de number of shares and its price of the array of InvestmentOperation"""
        for inv in self.mem.data.investments.arr:
            if inv.product.id==self.product.id:
                for oi in inv.op.arr:
                    if self.dtinitial<=oi.datetime and self.dtfinal>=oi.datetime:
                        oi.shares=self.convertShares(oi.shares)
                        oi.valor_accion=self.convertPrices(oi.valor_accion)
                        oi.save(autocommit=False)

        
    def updateDividends(self):
        """Transforms de dpa of an array of dividends"""
        for inv in self.mem.data.investments.arr:
            if inv.product.id==self.product.id:
                dividends=DividendHomogeneusManager(self.mem, inv)
                dividends.load_from_db("select * from dividends where id_inversiones={0} order by fecha".format(inv.id ))  
                for d in dividends.arr:
                    if self.dtinitial<=d.datetime and self.dtfinal>=d.datetime:
                        d.dpa=self.convertPrices(d.dpa)
                    d.save()
        
    def type(self):
        """Función que devuelve si es un Split o contrasplit"""
        if self.initial>self.final:
            return "Contrasplit"
        else:
            return "Split"
            
    def makeSplit(self):
        """All calculates to make the split"""        
        self.updateDPS()
        self.updateEstimationsDPS()
        self.updateEstimationsEPS()
        self.updateOperInvestments()
        self.updateDividends()
        self.updateQuotes()
        self.mem.con.commit()



## Una inversión pertenece a una lista de agrupaciones ibex, indices europeos
## fondo europeo, fondo barclays. Hat tantas agrupaciones como clasificaciones . grupos en kaddressbook similar
class Agrupation:
    ## Constructor with the following attributes combination
    ## 1. Agrupation(mem). Create an aggrupation with all attributes to None
    ## 2. Agrupation(mem, id,  name, type, bolsa). Create an agrupation settings all attributes.
    ## @param mem MemXulpymoney object
    ## @param name String with the name of the agrupation
    ## @param type
    ## @param stockmarket StockMarket object
    ## @param id Integer that sets the id of the agrupation
    def __init__(self,  *args):        
        def init__create( id,  name, type, bolsa):
            self.id=id
            self.name=name
            self.type=type
            self.stockmarket=bolsa

        self.mem=args[0]
        if len(args)==1:
            init__create(None, None, None, None)
        if len(args)==5:
            init__create(args[1], args[2], args[3], args[4])

## Product type class
class ProductType(Object_With_IdName):
    def __init__(self, *args):
        Object_With_IdName.__init__(self, *args)

## Set of product types
class ProductTypesManager(ObjectManager_With_IdName_Selectable):
    def __init__(self, mem):
        ObjectManager_With_IdName_Selectable.__init__(self)
        self.mem=mem

    def load_all(self):
        self.append(ProductType(eProductType.Share.value,QApplication.translate("Core","Shares")))
        self.append(ProductType(eProductType.Fund.value,QApplication.translate("Core","Funds")))
        self.append(ProductType(eProductType.Index.value,QApplication.translate("Core","Indexes")))
        self.append(ProductType(eProductType.ETF.value,QApplication.translate("Core","ETF")))
        self.append(ProductType(eProductType.Warrant.value,QApplication.translate("Core","Warrants")))
        self.append(ProductType(eProductType.Currency.value,QApplication.translate("Core","Currencies")))
        self.append(ProductType(eProductType.PublicBond.value,QApplication.translate("Core","Public Bond")))
        self.append(ProductType(eProductType.PensionPlan.value,QApplication.translate("Core","Pension plans")))
        self.append(ProductType(eProductType.PrivateBond.value,QApplication.translate("Core","Private Bond")))
        self.append(ProductType(eProductType.Deposit.value,QApplication.translate("Core","Deposit")))
        self.append(ProductType(eProductType.Account.value,QApplication.translate("Core","Accounts")))

    def investment_types(self):
        """Returns a ProductTypesManager without Indexes and Accounts"""
        r=ProductTypesManager(self.mem)
        for t in self.arr:
            if t.id not in (eProductType.Index, eProductType.Account):
                r.append(t)
        return r

    def with_operation_comissions_types(self):
        """Returns a ProductTypesManager with types which product operations  has comissions"""
        r=ProductTypesManager(self.mem)
        for t in self.arr:
            if t.id not in (eProductType.Fund, eProductType.Index, eProductType.PensionPlan, eProductType.Deposit, eProductType.Account):
                r.append(t)
        return r

class Language:
    def __init__(self, mem, id, name):
        self.id=id
        self.name=name
    
            
class Maintenance:
    """Funciones de mantenimiento y ayuda a la programación y depuración"""
    def __init__(self, mem):
        self.mem=mem
        
    def regenera_todas_opercuentasdeoperinversiones(self):
         
        for inv in self.mem.data.investments.arr:
            print (inv)
            inv.actualizar_cuentasoperaciones_asociadas()
        self.mem.con.commit()        
        
        
    def show_investments_status(self, date):
        """Shows investments status in a date"""
        datet=dtaware(date, time(22, 00), self.mem.localzone.name)
        sumbalance=0
        print ("{0:<40s} {1:>15s} {2:>15s} {3:>15s}".format("Investments at {0}".format(date), "Shares", "Price", "Balance"))
        for inv in self.mem.data.investments.arr:
            balance=inv.balance(date)
            sumbalance=sumbalance+balance
            acciones=inv.shares(date)
            price=Quote(self.mem).init__from_query(inv.product, datet)
            if acciones!=0:
                print ("{0:<40s} {1:>15f} {2:>15s} {3:>15s}".format(inv.name, acciones, self.mem.localcurrency.string(price.quote),  self.mem.localcurrency.string(balance)))
        print ("{0:>40s} {1:>15s} {2:>15s} {3:>15s}".format("Total balance at {0}".format(date), "","", self.mem.localcurrency.string(sumbalance)))


class SettingsDB:
    def __init__(self, mem):
        self.mem=mem
    
    def in_db(self, name):
        """Returns true if globals is saved in database"""
        cur=self.mem.con.cursor()
        cur.execute("select value from globals where id_globals=%s", (self.id(name), ))
        num=cur.rowcount
        cur.close()
        if num==0:
            return False
        else:
            return True
  
    def value(self, name, default):
        """Search in database if not use default"""            
        cur=self.mem.con.cursor()
        cur.execute("select value from globals where id_globals=%s", (self.id(name), ))
        if cur.rowcount==0:
            return default
        else:
            value=cur.fetchone()[0]
            cur.close()
            return value
        
    def setValue(self, name, value):
        """Set the global value.
        It doesn't makes a commit, you must do it manually
        value can't be None
        """
        cur=self.mem.con.cursor()
        if self.in_db(name)==False:
            cur.execute("insert into globals (id_globals, global,value) values(%s,%s,%s)", (self.id(name),  name, value))     
        else:
            cur.execute("update globals set global=%s, value=%s where id_globals=%s", (name, value, self.id(name)))
        cur.close()
        self.mem.con.commit()
        
    def id(self,  name):
        """Converts section and name to id of table globals"""
        if name=="wdgIndexRange/spin":
            return 7
        elif name=="wdgIndexRange/invertir":
            return 8
        elif name=="wdgIndexRange/minimo":
            return 9
        elif name=="wdgLastCurrent/spin":
            return 10
        elif name=="mem/localcurrency":
            return 11
        elif name=="mem/localzone":
            return 12
        elif name=="mem/benchmarkid":
            return 13
        elif name=="mem/dividendwithholding":
            return 14
        elif name=="mem/taxcapitalappreciation":
            return 15
        elif name=="mem/taxcapitalappreciationbelow":
            return 16
        elif name=="mem/gainsyear":
            return 17
        elif name=="mem/favorites":
            return 18
        elif name=="mem/fillfromyear":
            return 19
        elif name=="frmSellingPoint/lastgainpercentage":
            return 20
        elif name=="wdgAPR/cmbYear":
            return 21
        elif name=="wdgLastCurrent/viewode":
            return 22
        return None

class MemSources:
    def __init__(self):
        self.data=DBData(self)
        
        self.countries=CountryManager(self)
        self.countries.load_all()
        
        self.zones=ZoneManager(self)
        self.zones.load_all()
        #self.localzone=self.zones.find_by_name(self.settingsdb.value("mem/localzone", "Europe/Madrid"))
        
        self.stockmarkets=StockMarketManager(self)
        self.stockmarkets.load_all()
        
        
class MemXulpymoney:
    def __init__(self):                
        self.dir_tmp=dirs_create()
        
        self.qtranslator=None#Residirá el qtranslator
        self.settings=QSettings()
        self.settingsdb=SettingsDB(self)
        
        self.inittime=datetime.datetime.now()#Tiempo arranca el config
        self.dbinitdate=None#Fecha de inicio bd.
        self.con=None#Conexión        
        
        #Loading data in code
        self.countries=CountryManager(self)
        self.countries.load_all()
        self.languages=LanguageManager(self)
        self.languages.load_all()
        
        #Mem variables not in database
        self.language=self.languages.find_by_id(self.settings.value("mem/language", "en"))
        
        self.frmMain=None #Pointer to mainwidget
        self.closing=False#Used to close threads

    def init__script(self, title, tickers=False, sql=False):
        """
            Script arguments and autoconnect in mem.con, load_db_data
            
            type==1 #tickers
        """
        app = QCoreApplication(sys.argv)
        app.setOrganizationName("Mariano Muñoz ©")
        app.setOrganizationDomain("turulomio.users.sourceforge.net")
        app.setApplicationName("Xulpymoney")

        self.setQTranslator(QTranslator(app))
        self.languages.cambiar(self.language.id)

        parser=argparse.ArgumentParser(title)
        parser.add_argument('--user', help='Postgresql user', default='postgres')
        parser.add_argument('--port', help='Postgresql server port', default=5432)
        parser.add_argument('--host', help='Postgresql server address', default='127.0.0.1')
        parser.add_argument('--db', help='Postgresql database', default='xulpymoney')
        if tickers:
            parser.add_argument('--tickers', help='Generate tickers', default=False, action='store_true')
        if sql:
            parser.add_argument('--sql', help='Generate update sql', default=False, action='store_true')

        args=parser.parse_args()
        password=getpass.getpass()
        self.con=Connection().init__create(args.user,  password,  args.host, args.port, args.db)
        self.con.connect()
        if not self.con.is_active():
            print (QCoreApplication.translate("Core", "Error connecting to database"))
            sys.exit(255)        
        self.load_db_data(progress=False, load_data=False)
        return args


    def __del__(self):
        if self.con:#Cierre por reject en frmAccess
            self.con.disconnect()
            
    def setQTranslator(self, qtranslator):
        self.qtranslator=qtranslator

    def set_admin_mode(self, pasw):
        cur=self.con.cursor()
        cur.execute("update globals set value=md5(%s) where id_globals=6;", (pasw, ))
        cur.close()
        
    def check_admin_mode(self, pasw):
        """Returns: 
                - None: No admin password yet
                - True: parameter pasw is ok
                - False: parameter pasw is wrong"""
        cur=self.con.cursor()
        cur.execute("select value from globals where id_globals=6")
        val=cur.fetchone()[0]
        if val==None or val=="":
            resultado=None
        else:
            cur.execute("select value=md5(%s) from globals where id_globals=6;", (pasw, ))
            resultado=cur.fetchone()[0]
        cur.close()
        print (resultado,  "check_admin_mode")
        return resultado
        

    def load_db_data(self, progress=True, load_data=True):
        """Esto debe ejecutarse una vez establecida la conexión"""
        inicio=datetime.datetime.now()
        
        self.autoupdate=ProductUpdate.generateAutoupdateSet(self) #Set with a list of products with autoupdate
        logging.info("There are {} products with autoupdate".format(len(self.autoupdate)))
        
        self.currencies=CurrencyManager(self)
        self.currencies.load_all()
        self.localcurrency=self.currencies.find_by_id(self.settingsdb.value("mem/localcurrency", "EUR"))
        
        self.investmentsmodes=ProductModesManager(self)
        self.investmentsmodes.load_all()
        
        self.simulationtypes=SimulationTypeManager(self)
        self.simulationtypes.load_all()
        
        self.zones=ZoneManager(self)
        self.zones.load_all()
        self.localzone=self.zones.find_by_name(self.settingsdb.value("mem/localzone", "Europe/Madrid"))
        
        self.tiposoperaciones=OperationTypeManager(self)
        self.tiposoperaciones.load()
        
        self.conceptos=ConceptManager(self)
        self.conceptos.load_from_db()

        self.types=ProductTypesManager(self)
        self.types.load_all()
        
        self.stockmarkets=StockMarketManager(self)
        self.stockmarkets.load_all()
        
        self.agrupations=AgrupationManager(self)
        self.agrupations.load_all()

        self.leverages=LeverageManager(self)
        self.leverages.load_all()

        if load_data:
            self.data=DBData(self)
            self.data.load(progress)
        
        #mem Variables con base de datos
        self.dividendwithholding=Decimal(self.settingsdb.value("mem/dividendwithholding", "0.19"))
        self.taxcapitalappreciation=Decimal(self.settingsdb.value("mem/taxcapitalappreciation", "0.19"))
        self.taxcapitalappreciationbelow=Decimal(self.settingsdb.value("mem/taxcapitalappreciationbelow", "0.5"))
        self.gainsyear=str2bool(self.settingsdb.value("mem/gainsyear", "False"))
        self.favorites=string2list(self.settingsdb.value("mem/favorites", ""))
        self.fillfromyear=int(self.settingsdb.value("mem/fillfromyear", "2005"))
        
        logging.info("Loading db data took {}".format(datetime.datetime.now()-inicio))
        
    def save_MemSettingsDB(self):
        self.settingsdb.setValue("mem/localcurrency", self.localcurrency.id)
        self.settingsdb.setValue("mem/localzone", self.localzone.name)
        self.settingsdb.setValue("mem/dividendwithholding", Decimal(self.dividendwithholding))
        self.settingsdb.setValue("mem/taxcapitalappreciation", Decimal(self.taxcapitalappreciation))
        self.settingsdb.setValue("mem/taxcapitalappreciationbelow", Decimal(self.taxcapitalappreciationbelow))
        self.settingsdb.setValue("mem/gainsyear", self.gainsyear)
        self.settingsdb.setValue("mem/favorites", list2string(self.favorites))
        self.settingsdb.setValue("mem/benchmarkid", self.data.benchmark.id)
        self.settingsdb.setValue("mem/fillfromyear", self.fillfromyear)
        logging.info ("Saved Database settings")
        
        
    def qicon_admin(self):
        icon = QIcon()
        icon.addPixmap(QPixmap(":/xulpymoney/admin.png"), QIcon.Normal, QIcon.Off)
        return icon

class Country(Object_With_IdName):
    def __init__(self, *args):
        Object_With_IdName.__init__(self, *args)
            
    def qicon(self):
        icon=QIcon()
        icon.addPixmap(self.qpixmap(), QIcon.Normal, QIcon.Off)    
        return icon 
        
    def qpixmap(self):
        if self.id=="be":
            return QPixmap(":/countries/belgium.gif")
        elif self.id=="cn":
            return QPixmap(":/countries/china.gif")
        elif self.id=="fr":
            return QPixmap(":/countries/france.gif")
        elif self.id=="ie":
            return QPixmap(":/countries/ireland.gif")
        elif self.id=="it":
            return QPixmap(":/countries/italy.gif")
        elif self.id=="earth":
            return QPixmap(":/countries/earth.png")
        elif self.id=="es":
            return QPixmap(":/countries/spain.gif")
        elif self.id=="eu":
            return QPixmap(":/countries/eu.gif")
        elif self.id=="de":
            return QPixmap(":/countries/germany.gif")
        elif self.id=="fi":
            return QPixmap(":/countries/finland.gif")
        elif self.id=="nl":
            return QPixmap(":/countries/nethland.gif")
        elif self.id=="en":
            return QPixmap(":/countries/uk.gif")
        elif self.id=="jp":
            return QPixmap(":/countries/japan.gif")
        elif self.id=="pt":
            return QPixmap(":/countries/portugal.gif")
        elif self.id=="us":
            return QPixmap(":/countries/usa.gif")
        elif self.id=="ro":
            return QPixmap(":/countries/rumania.png")
        elif self.id=="ru":
            return QPixmap(":/countries/rusia.png")
        else:
            return QPixmap(":/xulpymoney/star.gif")
            
## Class to manage datetime timezone and its methods
class Zone:
    ## Constructor with the following attributes combination
    ## 1. Zone(mem). Create a Zone with all attributes set to None, except mem
    ## 2. Zone(mem, id, name, country). Create account passing all attributes
    ## @param mem MemXulpymoney object
    ## @param id Integer that represents the Zone Id
    ## @param name Zone Name
    ## @param country Country object asociated to the timezone
    def __init__(self, *args):
        def init__create(id, name, country):
            self.id=id
            self.name=name
            self.country=country
            return self
        self.mem=args[0]
        if len(args)==1:
            init__create(None, None, None)
        if len(args)==4:
            init__create(args[1], args[2], args[3])

    ## Returns a pytz.timezone
    def timezone(self):
        return pytz.timezone(self.name)
        
    ## Datetime aware with the pyttz.timezone
    def now(self):
        return datetime.datetime.now(pytz.timezone(self.name))
        
    ## Internal __repr__ function
    def __repr__(self):
        return "Zone ({}): {}".format(str(self.id), str(self.name))            

    ## Not all zones names are in pytz zone names. Sometimes we need a conversión
    ##
    ## It's a static method you can invoke with Zone.zone_name_conversion(name)
    ## @param name String with zone not in pytz
    ## @return String with zone name already converted if needed
    @staticmethod
    def zone_name_conversion(name):
        if name=="CEST":
            return "Europe/Berlin"
        if name.find("GMT")!=-1:
            return "Etc/{}".format(name)
        return name

class ZoneManager(ObjectManager_With_IdName_Selectable):
    def __init__(self, mem):
        ObjectManager_With_IdName_Selectable.__init__(self)
        self.mem=mem
        
    def load_all(self):
        self.append(Zone(self.mem,1,'Europe/Madrid', self.mem.countries.find_by_id("es")))
        self.append(Zone(self.mem,2,'Europe/Lisbon', self.mem.countries.find_by_id("pt")))
        self.append(Zone(self.mem,3,'Europe/Rome', self.mem.countries.find_by_id("it")))
        self.append(Zone(self.mem,4,'Europe/London', self.mem.countries.find_by_id("en")))
        self.append(Zone(self.mem,5,'Asia/Tokyo', self.mem.countries.find_by_id("jp")))
        self.append(Zone(self.mem,6,'Europe/Berlin', self.mem.countries.find_by_id("de")))
        self.append(Zone(self.mem,7,'America/New_York', self.mem.countries.find_by_id("us")))
        self.append(Zone(self.mem,8,'Europe/Paris', self.mem.countries.find_by_id("fr")))
        self.append(Zone(self.mem,9,'Asia/Hong_Kong', self.mem.countries.find_by_id("cn")))
        self.append(Zone(self.mem,10,'Europe/Brussels', self.mem.countries.find_by_id("be")))
        self.append(Zone(self.mem,11,'Europe/Amsterdam', self.mem.countries.find_by_id("nl")))
        self.append(Zone(self.mem,12,'Europe/Dublin', self.mem.countries.find_by_id("ie")))
        self.append(Zone(self.mem,13,'Europe/Helsinki', self.mem.countries.find_by_id("fi")))
        self.append(Zone(self.mem,14,'Europe/Lisbon', self.mem.countries.find_by_id("pt")))
        
    def qcombobox(self, combo, zone=None):
        """Carga entidades bancarias en combo"""
        combo.clear()
        for a in self.arr:
            combo.addItem(a.country.qicon(), a.name, a.id)

        if zone!=None:
            combo.setCurrentIndex(combo.findText(zone.name))

class AssetsReport(ODT_Standard, QObject):
    def __init__(self, mem, filename):
        ODT_Standard.__init__(self, filename)
        QObject.__init__(self)
        self.mem=mem
        self.dir=None#Directory in tmp
        
        
    def generate(self):
        self.dir='/tmp/AssetsReport-{}'.format(datetime.datetime.now())
        makedirs(self.dir)
        self.setMetadata( self.tr("Assets report"),  self.tr("This is an automatic generated report from Xulpymoney"), "Xulpymoney-{}".format(__version__))
        self.variables()
        self.cover()
        self.body()
        self.doc.save(self.filename)   
        
    def variables(self):
        self.vTotalLastYear=Assets(self.mem).saldo_total(self.mem.data.investments,  datetime.date(datetime.date.today().year-1, 12, 31))
        self.vTotal=Assets(self.mem).saldo_total(self.mem.data.investments,  datetime.date.today())


    def cover(self):
        self.emptyParagraph(number=10)
        self.simpleParagraph(self.tr("Assets Report"), "Title")
        self.simpleParagraph(self.tr("Generated by Xulpymoney-{}".format(__version__)), "Subtitle")
        self.emptyParagraph(number=8)
        self.simpleParagraph("{}".format(datetime.datetime.now()), "Quotations")        
        self.pageBreak()
        
    def body(self):
        c=self.mem.localcurrency.string
        ## About
        self.header(self.tr("About Xulpymoney"), 1)
        self.header(self.tr("About this report"), 2)
        self.pageBreak()
        
        ## Assets
        self.header(self.tr("Assets"), 1)
        self.simpleParagraph(self.tr("The total assets of the user is {}.").format(self.vTotal))
        if self.vTotalLastYear.isZero()==False:
            moreorless="more"
            if (self.vTotal-self.vTotalLastYear).isLTZero():
                moreorless="less"
            self.simpleParagraph(self.tr("It's a {} {} of the total assets at the end of the last year.").format(Percentage(self.vTotal-self.vTotalLastYear, self.vTotalLastYear), moreorless))
        
        ### Assets by bank
        self.header(self.tr("Assets by bank"), 2)
        data=[]
        self.mem.data.banks_active().order_by_name()
        sumbalances=Money(self.mem, 0, self.mem.localcurrency)
        for bank in self.mem.data.banks_active().arr:
            balance=bank.balance(self.mem.data.accounts_active(), self.mem.data.investments_active())
            sumbalances=sumbalances+balance
            data.append((bank.name, balance))
        self.table( [self.tr("Bank"), self.tr("Balance")], data, [4, 3], 9)       
        self.simpleParagraph(self.tr("Sum of all bank balances is {}").format(sumbalances))
        
        self.pageBreak(True)
        ### Assests current year
        self.header(self.tr("Assets current year evolution"), 2)
        
        from xulpymoney.ui.wdgTotal import TotalYear
        setData=TotalYear(self.mem, datetime.date.today().year)
        columns=[]
        columns.append([self.tr("Incomes"), self.tr("Gains"), self.tr("Dividends"), self.tr("Expenses"), self.tr("I+G+D-E"), "",  self.tr("Accounts"), self.tr("Investments"), self.tr("Total"),"",  self.tr("Monthly difference"), "",  self.tr("% current year")])
        self.simpleParagraph(self.tr("Assets Balance at {0}-12-31 is {1}".format(setData.year-1, setData.total_last_year)))
        for i, m in enumerate(setData.arr):
            if m.year<datetime.date.today().year or (m.year==datetime.date.today().year and m.month<=datetime.date.today().month):
                columns.append([m.incomes(), m.gains(), m.dividends(), m.expenses(), m.i_d_g_e(), "", m.total_accounts(), m.total_investments(), m.total(),"", setData.difference_with_previous_month(m),"",  setData.assets_percentage_in_month(m.month)])
            else:
                columns.append(["","","","","","","","","", "", "", "", ""])
        columns.append([setData.incomes(), setData.gains(), setData.dividends(), setData.expenses(), setData.i_d_g_e(), "", "", "", "", "", setData.difference_with_previous_year(), "", setData.assets_percentage_in_month(12)]) 
        data=zip(*columns)
        
        self.table(   [self.tr("Concept"), self.tr("January"),  self.tr("February"), self.tr("March"), self.tr("April"), self.tr("May"), self.tr("June"), self.tr("July"), self.tr("August"), self.tr("September"), self.tr("October"), self.tr("November"), self.tr("December"), self.tr("Total")], 
                            data, [2.5]+[1.8]*13, 6)
                
        ## Target
        target=AnnualTarget(self.mem).init__from_db(datetime.date.today().year)
        self.simpleParagraph(self.tr("The investment system has established a {} year target.").format(target.percentage)+" " +
                self.tr("With this target you will gain {} at the end of the year.").format(c(target.annual_balance())) +" " +
                self.tr("Up to date you have got  {} (gains + dividends) what represents a {} of the target.").format(setData.dividends()+setData.gains(), Percentage(setData.gains()+setData.dividends(), target.annual_balance())))
        self.pageBreak(True)
        
        ### Assets evolution graphic
        self.header(self.tr("Assets graphical evolution"), 2)
        
        self.mem.frmMain.on_actionTotalReport_triggered()
        self.mem.frmMain.w.load_graphic(animations=False)
        self.mem.frmMain.w.tab.setCurrentIndex(1)
        savefile="{}/wdgTotal.png".format(self.dir)
        self.mem.frmMain.w.view.save(savefile)
        self.addImage(savefile)
        p = P(stylename="Standard")
        p.addElement(self.image(savefile, 25, 13))
        self.doc.text.addElement(p)
        self.pageBreak()
        
        
        ## Accounts
        self.header(self.tr("Current Accounts"), 1)
        data=[]
        self.mem.data.accounts_active().order_by_name()
        for account in self.mem.data.accounts_active().arr:
            data.append((account.name, account.eb.name, account.balance()))
        self.table( [self.tr("Account"), self.tr("Bank"),  self.tr("Balance")], data, [6, 6, 3], 9)       
        
        self.simpleParagraph(self.tr("Sum of all account balances is {}").format(self.mem.data.accounts_active().balance()))

        
        self.pageBreak(True)
        
        ## Investments
        self.header(self.tr("Current investments"), 1)
        
        self.header(self.tr("Investments list"), 2)
        self.simpleParagraph(self.tr("Next list is sorted by the distance in percent to the selling point."))
        data=[]
        self.mem.data.investments_active().order_by_percentage_sellingpoint()
        for inv in self.mem.data.investments_active().arr: 
            pendiente=inv.op_actual.pendiente(inv.product.result.basic.last, type=3)
            arr=("{0} ({1})".format(inv.name, inv.account.name), inv.balance(), pendiente, inv.op_actual.tpc_total(inv.product.result.basic.last), inv.percentage_to_selling_point())
            data.append(arr)

        self.table( [self.tr("Investment"), self.tr("Balance"), self.tr("Gains"), self.tr("% Invested"), self.tr("% Selling point")], data, [13,  3, 3, 3, 3], 8)       
        
        suminvertido=self.mem.data.investments_active().invested()
        sumpendiente=self.mem.data.investments_active().pendiente()
        if suminvertido.isZero()==False:
            self.simpleParagraph(self.tr("Sum of all invested assets is {}.").format(suminvertido))
            self.simpleParagraph(self.tr("Investment gains (positive minus negative results): {} - {} are {}, what represents a {} of total assets.").format(self.mem.data.investments_active().pendiente_positivo(), self.mem.data.investments_active().pendiente_negativo(), sumpendiente, Percentage(sumpendiente, suminvertido)))
            self.simpleParagraph(self.tr(" Assets average age: {}").format(  days2string(self.mem.data.investments_active().average_age())))
        else:
            self.simpleParagraph(self.tr("There aren't invested assets"))
        self.pageBreak()
        
        
        
        ### Graphics wdgInvestments clases
        self.mem.frmMain.setGeometry(10, 10, 800, 800)
        self.mem.frmMain.w.close()
        from xulpymoney.ui.wdgInvestmentClasses import wdgInvestmentClasses
        self.mem.frmMain.w=wdgInvestmentClasses(self.mem, self.mem.frmMain)
        self.mem.frmMain.layout.addWidget(self.mem.frmMain.w)
        self.mem.frmMain.w.show()
        self.mem.frmMain.w.tab.setCurrentIndex(0)
        self.mem.frmMain.w.viewTPC.chart.setAnimationOptions(QChart.NoAnimation)
        self.mem.frmMain.w.update(animations=False)
        
        self.header(self.tr("Investments group by variable percentage"), 2)
        savefile="{}/wdgInvestmentsClasses_canvasTPC_legend.png".format(self.dir)
        self.mem.frmMain.w.viewTPC.save(savefile)
        self.addImage(savefile)
        p = P(stylename="Standard")
        p.addElement(self.image(savefile, 15, 10))
        self.doc.text.addElement(p)
        self.simpleParagraph("")
        self.pageBreak()
        
        self.header(self.tr("Investments group by investment type"), 2)
        savefile="{}/wdgInvestmentsClasses_canvasTipo_legend.png".format(self.dir)
        self.mem.frmMain.w.viewTipo.save(savefile)
        self.addImage(savefile)
        p = P(stylename="Standard")
        p.addElement(self.image(savefile, 15, 10))
        self.doc.text.addElement(p)
        self.simpleParagraph("") 
        self.pageBreak()
        
        self.header(self.tr("Investments group by leverage"), 2)        
        savefile="{}/wdgInvestmentsClasses_canvasApalancado_legend.png".format(self.dir)
        self.mem.frmMain.w.viewApalancado.save(savefile)
        self.addImage(savefile)
        p = P(stylename="Standard")
        p.addElement(self.image(savefile, 15, 10))
        self.doc.text.addElement(p)
        self.simpleParagraph("")       
        self.pageBreak()
        
        self.header(self.tr("Investments group by investment product"), 2)
        savefile="{}/wdgInvestmentsClasses_canvasProduct_legend.png".format(self.dir)
        self.mem.frmMain.w.viewProduct.save(savefile)
        self.addImage(savefile)
        p = P(stylename="Standard")
        p.addElement(self.image(savefile, 15, 10))
        self.doc.text.addElement(p)
        self.simpleParagraph("")       
        self.pageBreak()
        
        self.header(self.tr("Investments group by country"), 2)
        savefile="{}/wdgInvestmentsClasses_canvasCountry_legend.png".format(self.dir)
        self.mem.frmMain.w.viewCountry.save(savefile)
        self.addImage(savefile)
        p = P(stylename="Standard")
        p.addElement(self.image(savefile, 15, 10))
        self.doc.text.addElement(p)
        self.simpleParagraph("")       
        self.pageBreak()
        
        self.header(self.tr("Investments group by Call/Put/Inline"), 2)
        savefile="{}/wdgInvestmentsClasses_canvasPCI_legend.png".format(self.dir)
        self.mem.frmMain.w.viewPCI.save(savefile)
        self.addImage(savefile)
        p = P(stylename="Standard")
        p.addElement(self.image(savefile, 15, 10))
        self.doc.text.addElement(p)
        self.simpleParagraph("")
        
        self.mem.frmMain.w.close()
        self.mem.frmMain.showMaximized()

