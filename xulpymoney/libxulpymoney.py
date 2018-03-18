from PyQt5.QtCore import QObject,  pyqtSignal,  QTimer,  Qt,  QSettings, QCoreApplication, QTranslator
from PyQt5.QtGui import QIcon,  QColor,  QPixmap,  QFont
from PyQt5.QtWidgets import QTableWidgetItem,  QWidget,  QMessageBox, QApplication, QCheckBox, QHBoxLayout,  qApp,  QProgressDialog
from libodfgenerator import ODT
from odf.text import P
import datetime
import time
import logging
import platform
import io
from os import path,  makedirs
import pytz
import psycopg2
import psycopg2.extras
import sys
import codecs
import inspect
import argparse
import getpass
from decimal import Decimal, getcontext
from enum import IntEnum
from libxulpymoneyversion import version
from PyQt5.QtChart import QChart
getcontext().prec=20


def dirs_create():
    """
        Returns xulpymoney_tmp_dir, ...
    """
    dir_tmp=path.expanduser("~/.xulpymoney/tmp/")
    try:
        makedirs(dir_tmp)
    except:
        pass
    return dir_tmp

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


class AccountOperationOfInvestmentOperation:
    """Clase parar trabajar con las opercuentas generadas automaticamente por los movimientos de las inversiones"""
    def __init__(self, mem):
        self.mem=mem    
        self.id=None #Coincide con id_opercuentas de la tabla opercuentas.
        self.datetime=None
        self.concepto=None
        self.tipooperacion=None
        self.importe=None
        self.comentario=None #Documented in comment
        self.account=None
        self.operinversion=None
        self.investment=None
        
    def init__create(self, datetime,  concepto, tipooperacion, importe, comentario, cuenta, operinversion, inversion, id=None):
        self.datetime=datetime
        self.concepto=concepto
        self.tipooperacion=tipooperacion
        self.importe=importe
        self.comentario=comentario
        self.account=cuenta
        self.operinversion=operinversion
        self.investment=inversion
        return self
        


    def save(self):
        cur=self.mem.con.cursor()
        if self.id==None:
            cur.execute("insert into opercuentasdeoperinversiones (datetime, id_conceptos, id_tiposoperaciones, importe, comentario,id_cuentas, id_operinversiones,id_inversiones) values ( %s,%s,%s,%s,%s,%s,%s,%s) returning id_opercuentas", (self.datetime, self.concepto.id, self.tipooperacion.id, self.importe, self.comentario, self.account.id, self.operinversion.id, self.investment.id))
            self.id=cur.fetchone()[0]
        else:
            cur.execute("UPDATE FALTA  set datetime=%s, id_conceptos=%s, id_tiposoperaciones=%s, importe=%s, comentario=%s, id_cuentas=%s where id_opercuentas=%s", (self.datetime, self.concepto.id, self.tipooperacion.id,  self.importe,  self.comentario,  self.account.id,  self.id))
        cur.close()


class SetCommonsGeneric:
    """Base class to group items without a name neither an id, only objects, only arr, not dic_arr"""
    def __init__(self):
        self.arr=[]
        self.selected=None#Used to select a item in the set. Usefull in tables. Its a item

    def append(self,  obj):
        self.arr.append(obj)

    def remove(self, obj):
        self.arr.remove(obj)

    def length(self):
        return len(self.arr)

    def clean(self):
        """Deletes all items"""
        self.arr=[]
        
class SetCommons(SetCommonsGeneric):
    """Base clase to create Sets, it needs id and name attributes, as index. It has a list arr and a dics dic_arr to access objects of the set"""
    def __init__(self):
        SetCommonsGeneric.__init__(self)
        self.dic_arr={}
        self.id=None
        self.name=None
    
    def arr_position(self, id):
        """Returns arr position of the id, useful to select items with unittests"""
        for i, a in enumerate(self.arr):
            if a.id==id:
                return i
        return None
            
    def append(self,  obj):
        self.arr.append(obj)
        self.dic_arr[str(obj.id)]=obj
        
    def remove(self, obj):
        self.arr.remove(obj)
        del self.dic_arr[str(obj.id)]
        
        
    def find(self, o,  log=False):
        """o is and object with id parameter"""
        try:
            return self.dic_arr[str(o.id)]    
        except:
            if log:
                print ("SetCommons ({}) fails finding {}".format(self.__class__.__name__, o.id))
            return None        
    def find_by_id(self, id,  log=False):
        """Finds by id"""
        try:
            return self.dic_arr[str(id)]    
        except:
            if log:
                print ("SetCommons ({}) fails finding {}".format(self.__class__.__name__, id))
            return None
            
    def find_by_arr(self, id,  log=False):
        """log permite localizar errores en find. Ojo hay veces que hay find fallidos buscados como en UNION
                inicio=datetime.datetime.now()
        self.mem.data.products.find_by_id(80230)
        print (datetime.datetime.now()-inicio)
        self.mem.agrupations.find_by_arr(80230)
        print (datetime.datetime.now()-inicio)
        Always fister find_by_dict
        0:00:00.000473
        0:00:00.000530

        """
        for a in self.arr:
            if a.id==id:
                return a
        if log:
            print ("SetCommons ({}) fails finding  by arr {}".format(self.__class__.__name__, id))
        return None
                
    def order_by_id(self):
        """Orders the Set using self.arr"""
        try:
            self.arr=sorted(self.arr, key=lambda c: c.id,  reverse=False)     
            return True
        except:
            return False
        
    def order_by_name(self):
        """Orders the Set using self.arr"""
        try:
            self.arr=sorted(self.arr, key=lambda c: c.name,  reverse=False)       
            return True
        except:
            return False        
    def order_by_upper_name(self):
        """Orders the Set using self.arr"""
        try:
            self.arr=sorted(self.arr, key=lambda c: c.name.upper(),  reverse=False)       
            return True
        except:
            return False

    def qcombobox(self, combo,  selected=None):
        """Load set items in a comobo using id and name
        Selected is and object
        It sorts by name the arr""" 
        self.order_by_name()
        combo.clear()
        for a in self.arr:
            combo.addItem(a.name, a.id)

        if selected!=None:
            combo.setCurrentIndex(combo.findData(selected.id))
            
                
    def clean(self):
        """Deletes all items"""
        self.arr=[]
        self.dic_arr={}
                
    def clone(self,  *initparams):
        """Returns other Set object, with items referenced, ojo con las formas de las instancias
        initparams son los parametros de iniciación de la clase"""
        result=self.__class__(*initparams)#Para que coja la clase del objeto que lo invoca
        for a in self.arr:
            result.append(a)
        return result
        
    def setSelected(self, sel):
        """
            Searches the objects id in the array and mak selected. ReturnsTrue if the o.id exists in the arr and False if don't
        """
        for i, o in enumerate(self.arr):
            if o.id==sel.id:
                self.selected=o
                return True
        self.selected=None
        return False        
    def setSelectedList(self, lista):
        """
            Searches the objects id in the array and mak selected. ReturnsTrue if the o.id exists in the arr and False if don't
        """
        assert type(lista) is list, "id is not a list {}".format(lista)
        self.arr=[]
        for i, o in enumerate(self.arr):
            for l in lista:
                if o.id==l.id:
                    self.append(o)
        self.selected=None
        return False
        
    def union(self,  set,  *initparams):
        """Returns a new set, with the union comparing id
        initparams son los parametros de iniciación de la clse"""        
        resultado=self.__class__(*initparams)#Para que coja la clase del objeto que lo invoca SetProduct(self.mem), luego será self.mem
        for p in self.arr:
            resultado.append(p)
        for p in set.arr:
            if resultado.find_by_id(p.id, False)==None:
                resultado.append(p)
        return resultado

class SetSimulationTypes(SetCommons):
    def __init__(self, mem):
        SetCommons.__init__(self)
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


#class SetInvestmentsGeneric(SetCommonsGeneric):
#    """
#        Generic class. Investments doesn't hava an id, neither an account
#        
#        Used in DisReinvest , merging investments ....
#    """
#    def __init__(self, mem):
#        SetCommonsGeneric.__init__(self)
#        self.mem=mem
#
#    def order_by_balance(self, fecha=None,  type=3):
#        """Orders the Set using self.arr"""
##        try:
#        self.arr=sorted(self.arr, key=lambda inv: inv.balance(fecha,  type),  reverse=True) 
##            return True
##        except:
##            logging.error("SetInvestmentsGeneric can't order by balance")
##            return False
            
class SetInvestments(SetCommons):
    def __init__(self, mem, cuentas, products, benchmark):
        SetCommons.__init__(self)
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
                    table.item(i, 7).setBackground(QColor(255, 148, 148))
                if (tpc_venta.value_100()<=Decimal(5) and tpc_venta.isGTZero()) or tpc_venta.isLTZero():
                    table.item(i, 8).setBackground(QColor(148, 255, 148))

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
                table.setItem(i, 2, qright(inv.op_actual.last().acciones))
                table.setItem(i, 3, qright(inv.op_actual.acciones()))
                table.setItem(i, 4,  inv.balance(None, type).qtablewidgetitem())
                table.setItem(i, 5, inv.op_actual.pendiente(inv.product.result.basic.last, type).qtablewidgetitem())
                lasttpc=inv.op_actual.last().tpc_total(inv.product.result.basic.last, type=3)
                table.setItem(i, 6, lasttpc.qtablewidgetitem())
                table.setItem(i, 7, inv.op_actual.tpc_total(inv.product.result.basic.last, type=3).qtablewidgetitem())
                table.setItem(i, 8, inv.percentage_to_selling_point().qtablewidgetitem())
                if lasttpc<Percentage(percentage, 1):   
                    table.item(i, 6).setBackground(QColor(255, 148, 148))
            except:
                logging.error("I couldn't show last of {}".format(inv.name))

    def myqtablewidget_sellingpoints(self, table):
        """Crea un set y luego construye la tabla"""
        
        set=SetInvestments(self.mem,  self.accounts, self.products, self.benchmark)
        for inv in self.arr:
            if inv.selling_expiration!=None and inv.acciones()>0:
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
                    table.item(i, 1).setBackground( QColor(255, 182, 182))       
                table.setItem(i, 2, qleft(inv.name))
                table.setItem(i, 3, qleft(inv.account.name))   
                table.setItem(i, 4, qright(inv.acciones()))
                table.setItem(i, 5, inv.product.currency.qtablewidgetitem(inv.venta))
                table.setItem(i, 6, inv.percentage_to_selling_point().qtablewidgetitem())


    def average_age(self):
        """Average age of the investments in this set in days"""
        #Extracts all currentinvestmentoperations
        set=SetInvestmentOperationsCurrentHeterogeneus(self.mem)
        for inv in self.arr:
            for o in inv.op_actual.arr:
                set.arr.append(o)
        average=set.average_age()
        if average==None:
            return None
        return round(average, 2)
            
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

    def products_distinct(self):
        """Returns a SetProduct with all distinct products of the Set investments items"""
        s=set([])
        for i in self.arr:
            s.add(i.product)
            
        r=SetProducts(self.mem)
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
        account=Account(self.mem).init__create("Merging account",  bank, True, "", self.mem.localcurrency, -1)
        r=Investment(self.mem).init__create(name, None, account, product, None, True, -1)
        r.merge=2
        r.op=SetInvestmentOperationsHomogeneus(self.mem, r)
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
        account=Account(self.mem).init__create("Merging account",  bank, True, "", self.mem.localcurrency, -1)
        r=Investment(self.mem).init__create(name, None, account, product, None, True, -1)
        set=SetDividendsHomogeneus(self.mem, r)
        for inv in self.arr:
            if inv.product.id==product.id:
                for d in inv.setDividends_from_operations().arr:
                    set.append(d)
        set.sort()
        return set

    def investment_merging_current_operations_with_same_product(self, product):
        """
            Funci´on que convierte el set actual de inversiones, sacando las del producto pasado como parámetro
            Crea una inversi´on nueva cogiendo las  operaciones actuales, juntándolas , convirtiendolas en operaciones normales 
            
            se usa para hacer reinversiones, en las que no se ha tenido cuenta el metodo fifo, para que use las acciones actuales.
        """
        name=QApplication.translate("Core", "Virtual investment merging current operations of {}".format(product.name))
        bank=Bank(self.mem).init__create("Merging bank", True, -1)
        account=Account(self.mem).init__create("Merging account",  bank, True, "", self.mem.localcurrency, -1)
        r=Investment(self.mem).init__create(name, None, account, product, None, True, -1)    
        r.merge=1
        r.op=SetInvestmentOperationsHomogeneus(self.mem, r)
        for inv in self.arr: #Recorre las inversion del array
            if inv.product.id==product.id:
                for o in inv.op_actual.arr:
                    r.op.append(InvestmentOperation(self.mem).init__create(o.tipooperacion, o.datetime, r, o.acciones, o.impuestos, o.comision,  o.valor_accion,  o.comision,  o.show_in_ranges,  o.currency_conversion,  o.id))
        r.op.order_by_datetime()
        (r.op_actual,  r.op_historica)=r.op.calcular()             
        return r
        

    def setDividends_merging_current_operation_dividends(self, product):
        name=QApplication.translate("Core", "Virtual investment merging current operations of {}".format(product.name))
        bank=Bank(self.mem).init__create("Merging bank", True, -1)
        account=Account(self.mem).init__create("Merging account",  bank, True, "", self.mem.localcurrency, -1)
        r=Investment(self.mem).init__create(name, None, account, product, None, True, -1)    
        set=SetDividendsHomogeneus(self.mem, r)
        for inv in self.arr:
            if inv.product.id==product.id:
                for d in inv.setDividends_from_current_operations().arr:
                    set.append(d)
        set.sort()
        return set

    def setinvestments_filter_by_type(self,  type_id):
        """
            Returns a new setinvestments filtering original by type_id
            For example to get all funds in the original setinvesmet
        """
        r=SetInvestments(self.mem, self.mem.data.accounts, self.mem.data.products, self.mem.data.benchmark )
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
        invs=SetInvestments(self.mem, None, self.mem.data.products, self.mem.data.benchmark)
        for product in self.products_distinct().arr:
            i=self.investment_merging_operations_with_same_product(product)
            invs.append(i) 
        return invs

                
    def setInvestments_merging_investments_with_same_product_merging_current_operations(self):
        """
            Genera un set Investment nuevo , creando invesments aglutinadoras de todas las inversiones con el mismo producto
            
            Account no es necesaria pero para mostrar algunas tablas con los calculos (currency) se necesita por lo que se puede pasar como parametro. Por ejemplo
            en frmReportInvestment, se pasar´ia la< cuenta asociada ala inversi´on del informe.
            
        """
        invs=SetInvestments(self.mem, None, self.mem.data.products, self.mem.data.benchmark)
        for product in self.products_distinct().arr:
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
            op_cuenta=AccountOperation(self.mem).init__create(now.date(), self.mem.conceptos.find_by_id(38), self.mem.tiposoperaciones.find_by_id(1), -comision, "Traspaso de valores", origen.account)
            op_cuenta.save()           
            comentario="{0}|{1}".format(destino.id, op_cuenta.id)
        else:
            comentario="{0}|{1}".format(destino.id, "None")
        
        op_origen=InvestmentOperation(self.mem).init__create( self.mem.tiposoperaciones.find_by_id(9), now, origen,  -numacciones, 0,0, comision, 0, comentario, True, currency_conversion)
        op_origen.save( False)      

        #NO ES OPTIMO YA QUE POR CADA SAVE SE CALCULA TODO
        comentario="{0}".format(op_origen.id)
        for o in origen.op_actual.arr:
            op_destino=InvestmentOperation(self.mem).init__create( self.mem.tiposoperaciones.find_by_id(10), now, destino,  o.acciones, o.importe, o.impuestos, o.comision, o.valor_accion, comentario,  o.show_in_ranges, currency_conversion)
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
            logging.error("SetInvestments can't order by balance")
            return False
        
        
class SetProducts(SetCommons):
    def __init__(self, mem):
        SetCommons.__init__(self)
        self.mem=mem
        

#    def find_by_googleticker(self, ticker):
#        if ticker==None:
#            logging.info("I coudn't find a None google ticker")
#            return ""
#        for p in self.arr:
#            googleticker=p.googleticker()
#            if googleticker=="":
#                continue
#            if googleticker.upper()==ticker.upper():
#                return p
#        logging.info("I coudn't find this google ticker: {}".format(ticker))
#        return None        

#    def find_by_ticker(self, ticker):
#        if ticker==None:
#            return None
#        for p in self.arr:
#            if p.ticker==None:
#                continue
#            if p.ticker.upper()==ticker.upper():
#                return p
#        return None        
        

    def find_by_isin(self, isin):
        if isin==None:
            return None
        for p in self.arr:
            if p.isin==None:
                continue
            if p.isin.upper()==isin.upper():
                return p
        return None                
        
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


#    def googletickers_string(self):
#        s=""
#        for p in self.arr:
#            if p.ticker==None:
#                continue
#            if p.ticker=="":
#                continue
#            ticker=p.googleticker()
#            if ticker==None:
#                logging.debug("googleticker {} failed".format(p.ticker))
#                continue
#            s=s+ticker+","
#        return s[:-1]
        

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
            inv.estimations_dps.load_from_db()
            inv.result.basic.load_from_db()
            self.append(inv)
        cur.close()

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
            
    def qcombobox_not_obsolete(self, combo,  selected=None):
        """Load set items in a comobo using id and name
        Selected is and object
        It sorts by name the arr""" 
        self.order_by_name()
        combo.clear()
        for a in self.arr:
            if a.obsolete==False:
                combo.addItem(a.name, a.id)

        if selected!=None:
            combo.setCurrentIndex(combo.findData(selected.id))
    def subset_with_same_type(self, type):
        """Returns a SetProduct with all products with the type passed as parameter.
        Type is an object"""
        result=SetProducts(self.mem)
        for a in self.arr:
            if a.type.id==type.id:
                result.append(a)
        return result
        
    def list_ISIN_XULPYMONEY(self):
        """Returns a list with all products with 3 appends --ISIN_XULPYMONEY ISIN, ID"""
        suf=[]
        for p in self.arr:
            if len(p.isin)>5:
                suf.append("--ISIN_XULPYMONEY")
                suf.append(p.isin)
                suf.append(str(p.id))
        return suf
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
                table.item(i, 7).setBackground( QColor(255, 182, 182))          
            else:
                table.setItem(i, 7, p.estimations_dps.currentYear().percentage().qtablewidgetitem())
                
            if p.has_autoupdate()==True:#Active
                table.item(i, 4).setIcon(transfer)
            if p.obsolete==True:#Obsolete
                for c in range(table.columnCount()):
                    table.item(i, c).setFont(tachado)



class SetProductsModes(SetCommons):
    """Agrupa los mode"""
    def __init__(self, mem):
        SetCommons.__init__(self)
        self.mem=mem     
    
    def load_all(self):
        self.append(ProductMode(self.mem).init__create("p",QApplication.translate("Core","Put")))
        self.append(ProductMode(self.mem).init__create("c",QApplication.translate("Core","Call")))
        self.append(ProductMode(self.mem).init__create("i",QApplication.translate("Core","Inline")))

class SetSimulations(SetCommons):
    def __init__(self, mem):
        SetCommons.__init__(self)
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


class SetStockMarkets(SetCommons):
    def __init__(self, mem):
        SetCommons.__init__(self)
        self.mem=mem     
    
    def load_all_from_db(self):
        cur=self.mem.con.cursor()
        cur.execute("select * from stockmarkets")
        for row in cur:
            self.append(StockMarket(self.mem).init__db_row(row, self.mem.countries.find_by_id(row['country'])))
        cur.close()

class SetConcepts(SetCommons):
    def __init__(self, mem):
        SetCommons.__init__(self)
        self.mem=mem 
                 
        
    def load_from_db(self):
        cur=self.mem.con.cursor()
        cur.execute("Select * from conceptos")
        for row in cur:
            self.append(Concept(self.mem).init__db_row(row, self.mem.tiposoperaciones.find_by_id(row['id_tiposoperaciones'])))
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
        resultado=SetConcepts(self.mem)
        for c in self.arr:
            if c.tipooperacion.id==id_tiposoperaciones:
                resultado.append(c)
        return resultado
        
    def clone_editables(self):
        """SSe usa clone y no init ya que ya están cargados en MEM"""
        resultado=SetConcepts(self.mem)
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



class SetCountries(SetCommons):
    def __init__(self, mem):
        SetCommons.__init__(self)
        self.mem=mem   
        
    def load_all(self):
        self.append(Country().init__create("es",QApplication.translate("Core","Spain")))
        self.append(Country().init__create("be",QApplication.translate("Core","Belgium")))
        self.append(Country().init__create("cn",QApplication.translate("Core","China")))
        self.append(Country().init__create("de",QApplication.translate("Core","Germany")))
        self.append(Country().init__create("earth",QApplication.translate("Core","Earth")))
        self.append(Country().init__create("en",QApplication.translate("Core","United Kingdom")))
        self.append(Country().init__create("eu",QApplication.translate("Core","Europe")))
        self.append(Country().init__create("fi",QApplication.translate("Core","Finland")))
        self.append(Country().init__create("fr",QApplication.translate("Core","France")))
        self.append(Country().init__create("ie",QApplication.translate("Core","Ireland")))
        self.append(Country().init__create("it",QApplication.translate("Core","Italy")))
        self.append(Country().init__create("jp",QApplication.translate("Core","Japan")))
        self.append(Country().init__create("nl",QApplication.translate("Core","Netherlands")))
        self.append(Country().init__create("pt",QApplication.translate("Core","Portugal")))
        self.append(Country().init__create("us",QApplication.translate("Core","United States of America")))
        self.append(Country().init__create("ro",QApplication.translate("Core","Romanian")))
        self.append(Country().init__create("ru",QApplication.translate("Core","Rusia")))
        self.order_by_name()

    def qcombobox(self, combo,  country=None):
        """Función que carga en un combo pasado como parámetro y con un SetAccounts pasado como parametro
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

class SetAccounts(SetCommons):   
    def __init__(self, mem,  setebs):
        SetCommons.__init__(self)
        self.mem=mem   
        self.ebs=setebs

    def load_from_db(self, sql):
        cur=self.mem.con.cursor()
        cur.execute(sql)#"Select * from cuentas"
        for row in cur:
            c=Account(self.mem).init__db_row(row, self.ebs.find_by_id(row['id_entidadesbancarias']))
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
        ibex.result.get_basic_and_ohcls()
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
            account=Account(self.mem).init__create("Reinvest model account",  bank, True, "", self.mem.localcurrency, -1)
            r=Investment(self.mem).init__create(QApplication.translate("Core", "Reinvest model of {}".format(self.product.name)), None, account, self.product, None, True, -1)    
            r.merge=1
            r.op=SetInvestmentOperationsHomogeneus(self.mem, r)
            lastprice=self.product.result.basic.last.quote
            for amount in self.amounts[0:i+1]: #Recorre las amounts del array        
#    def init__create(self, tipooperacion, datetime, inversion, acciones,  impuestos, comision, valor_accion, comentario, show_in_ranges, currency_conversion,    id=None):
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
            



class SetAccountOperations:
    """Clase es un array ordenado de objetos newInvestmentOperation"""
    def __init__(self, mem):
        self.mem=mem
        self.arr=[]
        self.selected=None
        
    def append(self, objeto):
        self.arr.append(objeto)

    def length(self):
        return len (self.arr)
        
    def load_from_db(self, sql):
        cur=self.mem.con.cursor()
        cur.execute(sql)#"Select * from opercuentas"
        for row in cur:        
            co=AccountOperation(self.mem).init__create(row['datetime'], self.mem.conceptos.find_by_id(row['id_conceptos']), self.mem.tiposoperaciones.find_by_id(row['id_tiposoperaciones']), row['importe'], row['comentario'],  self.mem.data.accounts.find_by_id(row['id_cuentas']), row['id_opercuentas'])
            self.append(co)
        cur.close()
    
    def load_from_db_with_creditcard(self, sql):
        """Usado en unionall opercuentas y opertarjetas y se crea un campo id_tarjetas con el id de la tarjeta y -1 sino tiene es decir opercuentas"""
        cur=self.mem.con.cursor()
        cur.execute(sql)#"Select * from opercuentas"
        for row in cur:        
            if row['id_tarjetas']==-1:
                comentario=row['comentario']
            else:
                comentario=QApplication.translate("Core","Paid with {0}. {1}").format(self.mem.data.creditcards.find_by_id(row['id_tarjetas']).name, row['comentario'] )
            
            co=AccountOperation(self.mem).init__create(row['datetime'], self.mem.conceptos.find_by_id(row['id_conceptos']), self.mem.tiposoperaciones.find_by_id(row['id_tiposoperaciones']), row['importe'], comentario,  self.mem.data.accounts.find_by_id(row['id_cuentas']))
            self.append(co)
        cur.close()

    def setSelected(self, sel):
        """
            Searches the objects id in the array and mak selected. ReturnsTrue if the o.id exists in the arr and False if don't
        """
        for i, o in enumerate(self.arr):
            if o.id==sel.id:
                self.selected=o
                return True
        self.selected=None
        return False
    def sort(self):       
        self.arr=sorted(self.arr, key=lambda e: e.datetime,  reverse=False) 
        
    def myqtablewidget(self, tabla,   show_accounts=False,  parentname=None):
        """Section es donde guardar en el config file, coincide con el nombre del formulario en el que está la tabla
        show_accounts muestra la cuenta cuando las opercuentas son de diversos cuentas (Estudios totales)"""
        ##HEADERS
        diff=0
        if show_accounts==True:
            tabla.setColumnCount(6)
            diff=1
        else:
            tabla.setColumnCount(5)
        tabla.setHorizontalHeaderItem(0, QTableWidgetItem(QApplication.translate("Core","Date" )))
        if show_accounts==True:
            tabla.setHorizontalHeaderItem(diff, QTableWidgetItem(QApplication.translate("Core","Account" )))
        tabla.setHorizontalHeaderItem(1+diff, QTableWidgetItem(QApplication.translate("Core","Concept" )))
        tabla.setHorizontalHeaderItem(2+diff,  QTableWidgetItem(QApplication.translate("Core","Amount" )))
        tabla.setHorizontalHeaderItem(3+diff, QTableWidgetItem(QApplication.translate("Core","Balance" )))
        tabla.setHorizontalHeaderItem(4+diff, QTableWidgetItem(QApplication.translate("Core","Comment" )))
        ##DATA 
        tabla.clearContents()
        tabla.applySettings()  
        tabla.setRowCount(len(self.arr))
        balance=0
        for rownumber, a in enumerate(self.arr):
            balance=balance+a.importe
            tabla.setItem(rownumber, 0, qdatetime(a.datetime, self.mem.localzone))
            if show_accounts==True:
                tabla.setItem(rownumber, diff, QTableWidgetItem(a.account.name))
            tabla.setItem(rownumber, 1+diff, qleft(a.concepto.name))
            tabla.setItem(rownumber, 2+diff, self.mem.localcurrency.qtablewidgetitem(a.importe))
            tabla.setItem(rownumber, 3+diff, self.mem.localcurrency.qtablewidgetitem(balance))
            tabla.setItem(rownumber, 4+diff, qleft(Comment(self.mem).setFancy(a.comentario)))
            if self.selected!=None:
                if a.id==self.selected.id:
                    tabla.selectRow(rownumber+1)
            
    def myqtablewidget_lastmonthbalance(self, table,    account, lastmonthbalance):
        table.applySettings()
        table.clearContents()
        table.setRowCount(self.length()+1)        
        table.setItem(0, 1, QTableWidgetItem(QApplication.translate("Core", "Starting month balance")))
        table.setItem(0, 3, lastmonthbalance.qtablewidgetitem())
        for i, o in enumerate(self.arr):
            importe=Money(self.mem, o.importe, account.currency)
            lastmonthbalance=lastmonthbalance+importe
            table.setItem(i+1, 0, qdatetime(o.datetime, self.mem.localzone))
            table.setItem(i+1, 1, QTableWidgetItem(o.concepto.name))
            table.setItem(i+1, 2, importe.qtablewidgetitem())
            table.setItem(i+1, 3, lastmonthbalance.qtablewidgetitem())
            table.setItem(i+1, 4, QTableWidgetItem(Comment(self.mem).setFancy(o.comentario)))               
            if self.selected!=None:
                if o.id==self.selected.id:
                    table.selectRow(i+1)

class SetCurrencies(SetCommons):
    def __init__(self, mem):
        SetCommons.__init__(self)
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
        logging.error("SetCurrencies fails finding {}".format(symbol))
        return None
#        try:
#            return self.dic_arr[str(id)]    
#        except:
#            if log:
#                print ("SetCommons ({}) fails finding {}".format(self.__class__.__name__, id))
#            return None

    def qcombobox(self, combo, selectedcurrency=None):
        """Función que carga en un combo pasado como parámetro las currencies"""
        for c in self.arr:
            combo.addItem("{0} - {1} ({2})".format(c.id, c.name, c.symbol), c.id)
        if selectedcurrency!=None:
                combo.setCurrentIndex(combo.findData(selectedcurrency.id))

class SetDividendsHeterogeneus:
    """Class that  groups dividends from a Xulpymoney Product"""
    def __init__(self, mem):
        self.mem=mem
        self.arr=[]
            
    def gross(self):
        """gross amount in self.mem.localcurrency"""
        r=Money(self.mem, 0, self.mem.localcurrency)
        for d in self.arr:
            r=r+d.gross().local()
        return r

    def length(self):
        return len(self.arr)

    def load_from_db(self, sql):    
        del self.arr
        self.arr=[]
        cur=self.mem.con.cursor()
        cur.execute( sql)#"select * from dividends where id_inversiones=%s order by fecha", (self.investment.id, )
        for row in cur:
            inversion=self.mem.data.investments.find_by_id(row['id_inversiones'])
            oc=AccountOperation(self.mem).init__db_query(row['id_opercuentas'])
            self.arr.append(Dividend(self.mem).init__db_row(row, inversion, oc, self.mem.conceptos.find_by_id(row['id_conceptos']) ))
        cur.close()      
        
    def sort(self):       
        self.arr=sorted(self.arr, key=lambda e: e.fecha,  reverse=False) 
        
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
            table.setItem(i, 0, qdatetime(d.fecha, self.mem.localzone))
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
            
    def clean(self):
        """Deletes all items"""
        del self.arr 
        self.arr=[]

    def append(self, o):
        self.arr.append(o)

        
class SetDividendsHomogeneus(SetDividendsHeterogeneus):
    def __init__(self, mem, investment):
        SetDividendsHeterogeneus.__init__(self, mem)
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
            table.setItem(i, 0, qdatetime(d.fecha, self.mem.localzone))
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
        
class SetEstimationsDPS:
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

class SetEstimationsEPS:
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
        for k, v in self.dic_arr.items():
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

        
class SetBanks(SetCommons):
    def __init__(self, mem):
        SetCommons.__init__(self)
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

class SetIO:
    def __init__(self, mem):
        self.mem=mem
        self.arr=[]
        self.selected=None

    def arr_from_date(self, date):
        """Función que saca del arr las que tienen fecha mayor o igual a la pasada como parametro."""
        resultado=[]
        if date==None:
            return resultado
        for a in self.arr:
            if a.date()>=date:
                resultado.append(a)
        return resultado
        
    def append(self, objeto):
        self.arr.append(objeto)
        
    def remove(self, objeto):
        """Remove from array"""
        self.arr.remove(objeto)
        
                
#    def clone(self):
#        """Links all items in self. arr to a new set. Linked points the same object"""
#        if self.__class__==SetInvestmentOperationsCurrentHeterogeneus:
#            result=self.__class__(self.mem)
#        else:
#            result=self.__class__(self.mem, self.investment)
#        for a in self.arr:
#            result.append(a)
#        return result
#                
#    def clone_from_datetime(self, dt):
#        """Función que devuelve otro SetInvestmentOperations con las oper que tienen datetime mayor o igual a la pasada como parametro."""
#        if self.__class__==SetInvestmentOperationsCurrentHeterogeneus:
#            result=self.__class__(self.mem)
#        else:
#            result=self.__class__(self.mem, self.investment)
#        if dt==None:
#            return self.clone()
#        for a in self.arr:
#            if a.datetime>=dt:
#                result.append(a)
#        return result
                
                
#    def copy(self):
#        """Copy all items in self. arr. Copy is generate a copy in a diferent memoriy direction"""
#        if self.__class__==SetInvestmentOperationsCurrentHeterogeneus:
#            result=self.__class__(self.mem)
#        else:
#            result=self.__class__(self.mem, self.investment)
#        for a in self.arr:
#            result.append(a.copy())
#        return result


    def subSet_from_datetime(self, dt=None):
        """Función que devuelve otro SetInvestmentOperations con las oper que tienen datetime mayor o igual a la pasada como parametro. Las operaciones del array son vinculos a objetos no copiadas como se hace con copy_from"""
        if self.__class__==SetInvestmentOperationsCurrentHeterogeneus:
            result=self.__class__(self.mem)
        else:
            result=self.__class__(self.mem, self.investment)
        if dt==None:
            dt=self.mem.localzone.now()
        for a in self.arr:
            if a.datetime>=dt:
                result.append(a)
        return result
        
    def copy_from_datetime(self, dt=None):
        """Función que devuelve otro SetInvestmentOperations con las oper que tienen datetime mayor o igual a la pasada como parametro tambien copiadas."""
        if self.__class__==SetInvestmentOperationsCurrentHeterogeneus:
            result=self.__class__(self.mem)
        else:
            result=self.__class__(self.mem, self.investment)
        if dt==None:
            dt=self.mem.localzone.now()
        for a in self.arr:
            if a.datetime>=dt:
                result.append(a.copy())
        return result
        
    def copy_until_datetime(self, dt=None):
        """Función que devuelve otro SetInvestmentOperations con las oper que tienen datetime menor que la pasada como parametro."""
        if self.__class__==SetInvestmentOperationsCurrentHeterogeneus:
            result=self.__class__(self.mem)
        else:
            result=self.__class__(self.mem, self.investment)
        if dt==None:
            dt=self.mem.localzone.now()
        for a in self.arr:
            if a.datetime<=dt:
                result.append(a.copy())
        return result
        
    def first(self):
        if self.length()>0:
            return self.arr[0]
        return None
        
    def last(self):
        """REturn last ohcl"""
        if self.length()>0:
            return self.arr[self.length()-1]
        return None
        
    def length(self):
        return len(self.arr)

    def order_by_datetime(self):
        """Ordena por datetime"""
        self.arr=sorted(self.arr, key=lambda o:o.datetime)
        
    def setDistinctProducts(self):
        """Extracts distinct products in IO"""
        s=set([])
        for o in self.arr:
            s.add(o.investment.product)
        result=SetProducts(self.mem)
        result.arr=list(s)
        return result


class SetInvestmentOperationsHeterogeneus(SetIO):       
    """Clase es un array ordenado de objetos newInvestmentOperation"""
    def __init__(self, mem):
        SetIO.__init__(self, mem)
        
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
        
        super(SetInvestmentOperationsHeterogeneus, self).remove(io)
        
        (io.investment.op_actual,  io.investment.op_historica)=io.investment.op.calcular()
        io.investment.actualizar_cuentasoperaciones_asociadas()#Regenera toda la inversión.

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
            
            tabla.setItem(rownumber, 4, qright(a.acciones))
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



class SetInvestmentOperationsHomogeneus(SetInvestmentOperationsHeterogeneus):
    def __init__(self, mem, investment):
        SetInvestmentOperationsHeterogeneus.__init__(self, mem)
        self.investment=investment


    def calcular(self):
        """Realiza los cálculos y devuelve dos arrays"""
        sioh=SetInvestmentOperationsHistoricalHomogeneus(self.mem, self.investment)
        sioa=SetInvestmentOperationsCurrentHomogeneus(self.mem, self.investment)       
        for o in self.arr:                
            if o.acciones>=0:#Compra
                sioa.arr.append(InvestmentOperationCurrent(self.mem).init__create(o, o.tipooperacion, o.datetime, o.investment, o.acciones, o.impuestos, o.comision, o.valor_accion,  o.show_in_ranges, o.currency_conversion,  o.id))
            else:#Venta
                if abs(o.acciones)>sioa.acciones():
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
            
            tabla.setItem(rownumber, 2, qright(a.acciones))
            tabla.setItem(rownumber, 3, a.price(type).qtablewidgetitem())
            tabla.setItem(rownumber, 4, a.gross(type).qtablewidgetitem())            
            tabla.setItem(rownumber, 5, a.comission(type).qtablewidgetitem())
            tabla.setItem(rownumber, 6, a.taxes(type).qtablewidgetitem())
            tabla.setItem(rownumber, 7, a.net(type).qtablewidgetitem())
            if self.investment.hasSameAccountCurrency()==False:
                tabla.setItem(rownumber, 8, qright(a.currency_conversion))

class SetInvestmentOperationsCurrentHeterogeneus(SetIO):    
    """Clase es un array ordenado de objetos newInvestmentOperation"""
    def __init__(self, mem):
        SetIO.__init__(self, mem)
    def __repr__(self):
        try:
            inversion=self.arr[0].investment.id
        except:
            inversion= "Desconocido"
        return ("SetIOA Inv: {0}. N.Registros: {1}. N.Acciones: {2}. Invertido: {3}. Valor medio:{4}".format(inversion,  len(self.arr), self.acciones(),  self.invertido(),  self.average_price()))
                        
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
            shares=shares+Money(self.mem, o.acciones)
            sharesxprice=sharesxprice+Money(self.mem, o.acciones*o.valor_accion)

        if shares.isZero():
            return Money(self.mem)
        return sharesxprice/shares

    def balance(self):
        """Al ser homegeneo da el resultado en Money del producto"""
        resultado=Money(self.mem, 0, self.mem.localcurrency)
        for o in self.arr:
            resultado=resultado+o.balance(o.investment.product.result.basic.last, type=3)
        return resultado        
        
#    def datetime_first_operation(self):
#        if len(self.arr)==0:
#            return None
#        return self.arr[0].datetime
#        
    def acciones(self):
        """Devuelve el número de acciones de la inversión actual"""
        resultado=Decimal(0)
        for o in self.arr:
            resultado=resultado+o.acciones
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
            tabla.setItem(rownumber, 3, qright("{0:.6f}".format(a.acciones)))
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

        tabla.setItem(self.length(), 0, qleft(days_to_year_month(self.average_age())))
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
    
    def order_by_datetime(self):       
        self.arr=sorted(self.arr, key=lambda e: e.datetime,  reverse=False) 

    def tpc_tae(self):
        dias=self.average_age()
        if dias==0:
            dias=1
#        return Decimal(365*self.tpc_total()/dias)
#        return self.tpc_total()*365/dias
        return Percentage(self.tpc_total()*365, dias)

    def tpc_total(self):
        """Como es heterogenous el resultado sera en local"""
#        suminvertido=self.invertido()
#        if suminvertido.isZero():
#            return None
#        return self.pendiente().amount*100/suminvertido.amount
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
        
        inicio=self.acciones()
        
        accionesventa=abs(io.acciones)
        comisiones=Decimal('0')
        impuestos=Decimal('0')
        while accionesventa!=Decimal('0'):
            while True:###nO SE RECORRE EL ARRAY SE RECORRE Con I PORQUE HAY INSERCIONES Y BORRADOS daba problemas de no repetir al insertar
                ioa=self.arr[0]
                if ioa.acciones-accionesventa>Decimal('0'):#>0Se vende todo y se crea un ioa de resto, y se historiza lo restado
                    comisiones=comisiones+io.comision+ioa.comision
                    impuestos=impuestos+io.impuestos+ioa.impuestos
                    sioh.arr.append(InvestmentOperationHistorical(self.mem).init__create(ioa, io.investment, ioa.datetime.date(), io.tipooperacion, -accionesventa, comisiones, impuestos, io.datetime.date(), ioa.valor_accion, io.valor_accion, ioa.currency_conversion, io.currency_conversion))
                    self.arr.insert(0, InvestmentOperationCurrent(self.mem).init__create(ioa, ioa.tipooperacion, ioa.datetime, ioa.investment,  ioa.acciones-abs(accionesventa), 0, 0, ioa.valor_accion, ioa.show_in_ranges,  ioa.currency_conversion, ioa.id))
                    self.arr.remove(ioa)
                    accionesventa=Decimal('0')#Sale bucle
                    break
                elif ioa.acciones-accionesventa<Decimal('0'):#<0 Se historiza todo y se restan acciones venta
                    comisiones=comisiones+ioa.comision
                    impuestos=impuestos+ioa.impuestos
                    sioh.arr.append(InvestmentOperationHistorical(self.mem).init__create(ioa, io.investment, ioa.datetime.date(), io.tipooperacion, -ioa.acciones, Decimal('0'), Decimal('0'), io.datetime.date(), ioa.valor_accion, io.valor_accion, ioa.currency_conversion, io.currency_conversion))
                    accionesventa=accionesventa-ioa.acciones                    
                    self.arr.remove(ioa)
                elif ioa.acciones-accionesventa==Decimal('0'):#Se historiza todo y se restan acciones venta y se sale
                    comisiones=comisiones+io.comision+ioa.comision
                    impuestos=impuestos+io.impuestos+ioa.impuestos
                    sioh.arr.append(InvestmentOperationHistorical(self.mem).init__create(ioa, io.investment, ioa.datetime.date(),  io.tipooperacion, -ioa.acciones, comisiones, impuestos, io.datetime.date(), ioa.valor_accion, io.valor_accion, ioa.currency_conversion, io.currency_conversion))
                    self.arr.remove(ioa)                    
                    accionesventa=Decimal('0')#Sale bucle                    
                    break
        if inicio-self.acciones()-abs(io.acciones)!=Decimal('0'):
            logging.critical ("Error en historizar. diff {}. Inicio {}. Fin {}. {}".format(inicio-self.acciones()-abs(io.acciones),  inicio,   self.acciones(), io))
                
        
    def print_list(self):
        self.order_by_datetime()
        print ("\n Imprimiendo SIOA",  self)
        for oia in self.arr:
            print ("  - ", oia)
        
        
class SetInvestmentOperationsCurrentHomogeneus(SetInvestmentOperationsCurrentHeterogeneus):
    def __init__(self, mem, investment):
        SetInvestmentOperationsCurrentHeterogeneus.__init__(self, mem)
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
        
        shares=self.acciones()
        currency=self.investment.resultsCurrency(type)
        sharesxprice=Decimal(0)
        for o in self.arr:
            sharesxprice=sharesxprice+o.acciones*o.price(type).amount
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
#        try:
        return self.balance(self.investment.product.result.basic.last, type)-self.penultimate(type)
#        except:
#            logging.error("{} no tenia suficientes quotes en {}".format(function_name(self), self.investment.name))
#            return Money(self.mem,  0,  self.investment.product.currency)

    def gains_in_selling_point(self, type=1):
        """Gains in investment defined selling point"""
        if self.investment.venta!=None:
            return self.investment.selling_price(type)*self.investment.acciones()-self.investment.invertido(None, type)
        return Money(self.mem,  0, self.investment.resultsCurrency(type) )
        

    def gains_from_percentage(self, percentage,  type=1):
        """
            Gains a percentage from average_price
            percentage is a Percentage object
        """        
        return self.average_price(type)*percentage.value*self.acciones()

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
#        return self.tpc_total(last,  type)/dias*365
#        print (Percentage(self.tpc_total(last, type)))
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
#        invertido=self.invertido(type)
#        if invertido.isZero():
#            return 0
#        return self.pendiente(last, type).amount*100/invertido.amount
    
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
            
            tabla.setItem(rownumber, 1, qright("{0:.6f}".format(a.acciones)))
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
        tabla.setItem(self.length(), 1, qright(self.acciones()))
        tabla.setItem(self.length(), 2, self.average_price(type).qtablewidgetitem())
        tabla.setItem(self.length(), 3, self.invertido(type).qtablewidgetitem())
        tabla.setItem(self.length(), 4, self.balance(quote, type).qtablewidgetitem())
        tabla.setItem(self.length(), 5, self.pendiente(quote, type).qtablewidgetitem())
        tabla.setItem(self.length(), 7, self.tpc_tae(quote, type).qtablewidgetitem())
        tabla.setItem(self.length(), 8, self.tpc_total(quote, type).qtablewidgetitem())

class SetInvestmentOperationsHistoricalHeterogeneus(SetIO):       
    """Clase es un array ordenado de objetos newInvestmentOperation"""
    def __init__(self, mem):
        SetIO.__init__(self, mem)

        
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
            tabla.setItem(rownumber, 5,qright(a.acciones))
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

        

        
class SetInvestmentOperationsHistoricalHomogeneus(SetInvestmentOperationsHistoricalHeterogeneus):
    def __init__(self, mem, investment):
        SetInvestmentOperationsHistoricalHeterogeneus.__init__(self, mem)
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
            
            tabla.setItem(rownumber, 3+diff,qright(a.acciones))
            
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
        self.acciones=None#Es negativo
        self.comision=None
        self.impuestos=None
        self.fecha_venta=None
        self.valor_accion_compra=None
        self.valor_accion_venta=None     
        self.currency_conversion_compra=None
        self.currency_conversion_venta=None
            
    def __repr__(self):
        return ("IOH {0}. {1} {2}. Acciones: {3}. Valor:{4}. Currency conversion: {5} y {6}".format(self.investment.name,  self.fecha_venta, self.tipooperacion.name,  self.acciones,  self.valor_accion_venta, self.currency_conversion_compra,  self.currency_conversion_venta))
        
    def init__create(self, operinversion, inversion, fecha_inicio, tipooperacion, acciones,comision,impuestos,fecha_venta,valor_accion_compra,valor_accion_venta, currency_conversion_compra, currency_conversion_venta,  id=None):
        """Genera un objeto con los parametros. id_operinversioneshistoricas es puesto a new"""
        self.id=id
        self.operinversion=operinversion
        self.investment=inversion
        self.fecha_inicio=fecha_inicio
        self.tipooperacion=tipooperacion
        self.acciones=acciones
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
            return Money(self.mem, -self.acciones*self.valor_accion_compra, self.investment.product.currency)
        else:
            return Money(self.mem, -self.acciones*self.valor_accion_compra, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion_compra)
        
    def bruto_venta(self, type=1):
        currency=self.investment.resultsCurrency(type)
        if self.tipooperacion.id in (9, 10):
            return Money(self.mem, 0, currency)
        if type==1:
            return Money(self.mem, -self.acciones*self.valor_accion_venta, self.investment.product.currency)
        else:
            return Money(self.mem, -self.acciones*self.valor_accion_venta, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion_venta)
        
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
#        bruto=self.bruto_compra()
#        if bruto.isZero():
#            return 0
#        return 100*(self.consolidado_bruto()/bruto).amount
        
    def tpc_tae_neto(self):
        dias=(self.fecha_venta-self.fecha_inicio).days +1 #Account el primer día
        if dias==0:
            dias=1
#        return self.tpc_total_neto()*365/dias
        return Percentage(self.tpc_total_neto()*365, dias)

class InvestmentOperationCurrent:
    def __init__(self, mem):
        self.mem=mem 
        self.id=None
        self.operinversion=None
        self.tipooperacion=None
        self.datetime=None# con tz
        self.investment=None
        self.acciones=None
#        self.importe=None
        self.impuestos=None
        self.comision=None
        self.valor_accion=None
        self.referenciaindice=None##Debera cargarse desde fuera. No se carga con row.. Almacena un Quote, para comprobar si es el indice correcto ver self.referenciaindice.id
        self.show_in_ranges=True
        self.currency_conversion=None
        
    def __repr__(self):
        return ("IOA {0}. {1} {2}. Acciones: {3}. Valor:{4}. Currency conversion: {5}".format(self.investment.name,  self.datetime, self.tipooperacion.name,  self.acciones,  self.valor_accion, self.currency_conversion))
        
    def init__create(self, operinversion, tipooperacion, datetime, inversion, acciones,  impuestos, comision, valor_accion, show_in_ranges,  currency_conversion, id=None):
        """Investment es un objeto Investment"""
        self.id=id
        self.operinversion=operinversion
        self.tipooperacion=tipooperacion
        self.datetime=datetime
        self.investment=inversion
        self.acciones=acciones
#        self.importe=importe
        self.impuestos=impuestos
        self.comision=comision
        self.valor_accion=valor_accion
        self.show_in_ranges=show_in_ranges
        self.currency_conversion=currency_conversion
        return self
#                                
#    def init__db_row(self,  row,  inversion,  operinversion, tipooperacion):
#        self.id=row['id_operinversionesactual']
#        self.operinversion=operinversion
#        self.tipooperacion=tipooperacion
#        self.datetime=row['datetime']
#        self.investment=inversion
#        self.acciones=row['acciones']
#        self.importe=row['importe']
#        self.impuestos=row['impuestos']
#        self.comision=row['comision']
#        self.valor_accion=row['valor_accion']
#        self.show_in_ranges=row['show_in_ranges']
#        logging.error("NO SE SI DEBERIA HABER ROW PARA INVESTMENTOPERATIONCURRENT")
#        return self
        
    def copy(self):
        return self.init__create(self.operinversion, self.tipooperacion, self.datetime, self.investment, self.acciones, self.impuestos, self.comision, self.valor_accion, self.show_in_ranges, self.currency_conversion,   self.id)
                
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
            return Money(self.mem, abs(self.acciones*self.valor_accion), self.investment.product.currency)
        elif type==2:
            return Money(self.mem, abs(self.acciones*self.valor_accion), self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion)#Usa el factor del dia de la operacicón
        elif type==3:
            return Money(self.mem, abs(self.acciones*self.valor_accion), self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion).local(self.datetime)#Usa el factor del dia de la operacicón
    
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
        money=Money(self.mem, (last-first)*self.acciones, self.investment.product.currency)
        print("{} {} {} accciones. {}-{}. {}-{}={} ({})".format(self.investment.name, self.datetime, self.acciones, dt_last, dt_first, last, first, last-first,  money))
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
        money=Money(self.mem, (last-first)*self.acciones, self.investment.product.currency)
        print("ANNUAL:{} {} {} accciones. {}-{}. {}-{}={} ({})".format(self.investment.name, self.datetime, self.acciones, dt_last, dt_first, last, first, last-first,  money))
        if type==1:
            return money
        elif type==2:
            return money.convert(self.investment.account.currency, dt_last)
        elif type==3:
            return money.convert(self.investment.account.currency, dt_last).local(dt_last)
            
            
    def gross(self, type=1):
        if type==1:
            return Money(self.mem, self.acciones*self.valor_accion, self.investment.product.currency)
        elif type==2:
            return Money(self.mem, self.acciones*self.valor_accion, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion)
            
    def net(self, type=1):
        if self.acciones>=Decimal(0):
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
        if self.acciones==0 or lastquote.quote==None:#Empty xulpy
            return Money(self.mem, 0, currency)

        if type==1:
            return Money(self.mem, abs(self.acciones*lastquote.quote), self.investment.product.currency)
        elif type==2:
            return Money(self.mem, abs(self.acciones*lastquote.quote), self.investment.product.currency).convert(self.investment.account.currency, lastquote.datetime)
        elif type==3:
            return Money(self.mem, abs(self.acciones*lastquote.quote), self.investment.product.currency).convert(self.investment.account.currency, lastquote.datetime).local(lastquote.datetime)

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
        if self.acciones==0 or penultimate.quote==None:#Empty xulpy
            logging.error("{} no tenia suficientes quotes en {}".format(function_name(self), self.investment.name))
            return Money(self.mem, 0, currency)

        if type==1:
            return Money(self.mem, abs(self.acciones*penultimate.quote), self.investment.product.currency)
        elif type==2:
            return Money(self.mem, abs(self.acciones*penultimate.quote), self.investment.product.currency).convert(self.investment.account.currency, penultimate.datetime)#Al ser balance actual usa el datetime actual
        elif type==3:
            return Money(self.mem, abs(self.acciones*penultimate.quote), self.investment.product.currency).convert(self.investment.account.currency, penultimate.datetime).local(penultimate.datetime)
            
    def tpc_anual(self,  last,  lastyear, type=1):        
        """
            last is a Money object with investment.product currency
            type puede ser:
                1 Da el tanto por  ciento en la currency de la inversi´on
                2 Da el tanto por  ciento en la currency de la cuenta, por lo que se debe convertir teniendo en cuenta la temporalidad
                3 Da el tanto por ciento en la currency local, partiendo  de la conversi´on a la currency de la cuenta
        """
#        if last==None:#initiating xulpymoney
#            return 0
            
        mlast=self.investment.quote2money(last, type)
        
        if self.datetime.year==datetime.date.today().year:#Si la operaci´on fue en el año, cuenta desde el dia de la operaci´on, luego su preicio
            mlastyear=self.price(type)
        else:
            mlastyear=self.investment.quote2money(lastyear, type)
            
#        if mlastyear.isZero():
#            return 0
#            
#        return 100*(mlast-mlastyear).amount/mlastyear.amount
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
#        invertido=self.invertido(type)
#        if invertido.isZero():
#            return 0
#        return 100*(self.pendiente(last, type).amount/invertido.amount)
        return Percentage(self.pendiente(last, type), self.invertido(type))
            
        
    def tpc_tae(self, last, type=1):
        dias=self.age()
        if self.age()==0:
            dias=1
#        return Decimal(365*self.tpc_total(last, type)/dias)
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
        accountoperation=AccountOperation(self.mem).init__db_query(id)
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
                return QApplication.translate("Core","{}: {} shares. Amount: {}. Comission: {}. Taxes: {}").format(io.investment.name, io.acciones, io.gross(1), io.comission(1), io.taxes(1))
            else:
                return QApplication.translate("Core","{}: {} shares. Amount: {} ({}). Comission: {} ({}). Taxes: {} ({})").format(io.investment.name, io.acciones, io.gross(1), io.gross(2),  io.comission(1), io.comission(2),  io.taxes(1), io.taxes(2))
                
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
            return QApplication.translate("Core"," Refund of {} payment of which had an amount of {}").format(datetime_string(cco.datetime,  self.mem.localzone), money)
        
        
        #OPERINVESTMENTS
                        
#    def comment(self):
#        """Función que genera un comentario parseado según el tipo de operación o concepto"""
#        if self.tipooperacion.id==9:#"Traspaso de valores. Origen"#"{0}|{1}|{2}|{3}".format(self.investment.name, self.bruto, self.retencion, self.comision)
#            return QApplication.translate("Core","Traspaso de valores realizado a {0}".format(self.comentario.split("|"), self.account.currency.symbol))



class Concept:
    def __init__(self, mem):
        self.mem=mem
        self.id=None
        self.name=None
        self.tipooperacion=None
        self.editable=None

    def __repr__(self):
        return ("Instancia de Concept: {0} -- {1} ({2})".format( self.name, self.tipooperacion.name,  self.id))


    def init__create(self, name, tipooperacion, editable,  id=None):
        self.id=id
        self.name=name
        self.tipooperacion=tipooperacion
        self.editable=editable
        return self
                
    def init__db_row(self, row, tipooperacion):
        """El parámetro tipooperacion es un objeto tipooperacion, si no se tuviera en tiempo de creación se asigna None"""
        return self.init__create(row['concepto'], tipooperacion, row['editable'], row['id_conceptos'])

        
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

class AccountOperation:
    def __init__(self, mem):
        self.mem=mem
        self.id=None
        self.datetime=None
        self.concepto=None
        self.tipooperacion=None
        self.importe=None
        self.comentario=None #Documented in comment
        self.account=None
        
#    def __repr__(self):
#        return "AccountOperation {0}. datetime: {1}. Importe:{2}. Concept:{3}".format(self.id, self.datetime, self.importe, self.concepto)
    def __repr__(self):
        return "AccountOperation: {}".format(self.id)
        
    def init__create(self, dt, concepto, tipooperacion, importe,  comentario, cuenta, id=None):
        self.id=id
        self.datetime=dt
        self.concepto=concepto
        self.tipooperacion=tipooperacion
        self.importe=importe
        self.comentario=comentario
        self.account=cuenta
        return self
        
    def init__db_row(self, row, concepto,  tipooperacion, cuenta):
        return self.init__create(row['datetime'],  concepto,  tipooperacion,  row['importe'],  row['comentario'],  cuenta,  row['id_opercuentas'])


    def init__db_query(self, id_opercuentas):
        """Creates a AccountOperation querying database for an id_opercuentas"""
        if id_opercuentas==None:
            return None
        resultado=None
        cur=self.mem.con.cursor()
        cur.execute("select * from opercuentas where id_opercuentas=%s", (id_opercuentas, ))
        for row in cur:
            concepto=self.mem.conceptos.find_by_id(row['id_conceptos'])
            resultado=self.init__db_row(row, concepto, concepto.tipooperacion, self.mem.data.accounts.find_by_id(row['id_cuentas']))
        cur.close()
        return resultado

    def borrar(self):
        cur=self.mem.con.cursor()
        cur.execute("delete from opercuentas where id_opercuentas=%s", (self.id, ))
        cur.close()
        
#    def comment(self):
#        """Función que genera un comentario parseado según el tipo de operación o concepto
#        
#        Transferencias 4 origen :
#            El comentario en transferencias: other_account|other_operaccount|comission_operaccount|commision
#                - other_account: id_accounts of the other account
#                - other_operaccount: id_opercuentas in order to remove them.
#                - comission_operaccount: comission. Si es 0 es que no hay comision porque también es 0
#        Transferencias 5 destino:
#            El comentario en transferencias destino no tiene comission: other_account|other_operaccount
#                - other_account: id_accounts of the other account
#                - other_operaccount: id_opercuentas in order to remove them.     
#                
#        Comision de Transferencias
#            - Transfer
#            - Amount
#            - Origin account
#        """
##        c=self.comentario.split("|")
##        if self.concepto.id in (62, 39, 50, 63, 65) and len(c)==4:#"{0}|{1}|{2}|{3}".format(self.investment.name, self.bruto, self.retencion, self.comision)
##            return QApplication.translate("Core","{0[0]}. Gross: {0[1]} {1}. Witholding tax: {0[2]} {1}. Comission: {0[3]} {1}").format(c, self.account.currency.symbol)
##        elif self.concepto.id in (29, 35) and len(c)==5:#{0}|{1}|{2}|{3}".format(row['inversion'], importe, comision, impuestos)
##            return QApplication.translate("Core","{0[1]}: {0[0]} shares. Amount: {0[2]} {1}. Comission: {0[3]} {1}. Taxes: {0[4]} {1}").format(c, self.account.currency.symbol)
##        elif self.concepto.id==40 and len(c)==2:#"{0}|{1}".format(self.selCreditCard.name, len(self.setSelOperCreditCards))
##            return QApplication.translate("Core","CreditCard: {0[0]}. Made {0[1]} payments").format(c)
##        elif self.concepto.id==4 and len(c)==3:#Transfer from origin
##            return QApplication.translate("Core", "Transfer to {0}").format(self.mem.data.accounts.find_by_id(int(c[0])).name)
##        elif self.concepto.id==5 and len(c)==2:#Transfer received in destiny
##            return QApplication.translate("Core", "Transfer received from {0}").format(self.mem.data.accounts.find_by_id(int(c[0])).name)
##        elif self.concepto.id==38 and c[0]=="Transfer":#Comision bancaria por transferencia
##            return QApplication.translate("Core", "Due to account transfer of {0} from {1}").format(self.mem.localcurrency.string(float(c[1])), self.mem.data.accounts.find_by_id(int(c[2])).name)
##        else:
#        logging.info("Obsolete comment")
#        return self.comentario 
        
        
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
#            try:
            cur=cont.cursor()
            cur.execute("create database {0};".format(database))
#            except:
#                print ("Error in create_db()")
#                return False
#            finally:
#                cur.close()
#                cont.disconnect()
#            return True
        else:
            print ("You need to be superuser to create database")
            return False
        
        
    def db_exists(self, database):
        """Hace conexi´on automatica a template usando la con """
        new=Connection().init__create(self.con.user, self.con.password, self.con.server, self.con.port, "template1")
        new.connect()
        new._con.set_isolation_level(0)#Si no no me dejaba            
#            try:
        cur=new.cursor()
        cur.execute("SELECT 1 AS result FROM pg_database WHERE datname=%s", (database, ))
        
        if cur.rowcount==1:
            cur.close()
            new.disconnect
            return True
        cur.close()
        new.disconnect()
        return False
#            except:
        
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
        try:
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
            return True
        except:
            print ("Error creating xulpymoney basic schema")
            return False

        
class DBData:
    def __init__(self, mem):
        self.mem=mem

    def load(self, progress=True):
        """
            This method will subsitute load_actives and load_inactives
        """
        inicio=datetime.datetime.now()
        self.benchmark=Product(self.mem).init__db(self.mem.settingsdb.value("mem/benchmark", "79329" ))
        self.benchmark.result.basic.load_from_db()
        
        self.currencies=SetProducts(self.mem)
        self.currencies.load_from_db("select * from products where type=6")
        for p in self.currencies.arr:
            p.result.get_all()
        
        self.banks=SetBanks(self.mem)
        self.banks.load_from_db("select * from entidadesbancarias")

        self.accounts=SetAccounts(self.mem, self.banks)
        self.accounts.load_from_db("select * from cuentas")

        self.creditcards=SetCreditCards(self.mem, self.accounts)
        self.creditcards.load_from_db("select * from tarjetas")

        self.products=SetProducts(self.mem)
        self.products.load_from_inversiones_query("select distinct(products_id) from inversiones", progress)
        
        self.investments=SetInvestments(self.mem, self.accounts, self.products, self.benchmark)
        self.investments.load_from_db("select * from inversiones", progress)
        
        logging.info("DBData loaded: {}".format(datetime.datetime.now()-inicio))
        
        
    def accounts_active(self):        
        r=SetAccounts(self.mem, self.banks)
        for b in self.accounts.arr:
            if b.active==True:
                r.append(b)
        return r 

    def accounts_inactive(self):        
        r=SetAccounts(self.mem, self.banks)
        for b in self.accounts.arr:
            if b.active==False:
                r.append(b)
        return r
        
    def banks_active(self):        
        r=SetBanks(self.mem)
        for b in self.banks.arr:
            if b.active==True:
                r.append(b)
        return r        
        
    def banks_inactive(self):        
        r=SetBanks(self.mem)
        for b in self.banks.arr:
            if b.active==False:
                r.append(b)
        return r        
        
    def creditcards_active(self):        
        r=SetCreditCards(self.mem, self.accounts)
        for b in self.creditcards.arr:
            if b.active==True:
                r.append(b)
        return r        
        
    def creditcards_inactive(self):        
        r=SetCreditCards(self.mem, self.accounts)
        for b in self.creditcards.arr:
            if b.active==False:
                r.append(b)
        return r
            
    def investments_active(self):        
        r=SetInvestments(self.mem, self.accounts, self.products, self.benchmark)
        for b in self.investments.arr:
            if b.active==True:
                r.append(b)
        return r        
        
    def investments_inactive(self):        
        r=SetInvestments(self.mem, self.accounts, self.products, self.benchmark)
        for b in self.investments.arr:
            if b.active==False:
                r.append(b)
        return r        
#    def banks_all(self):
#        return self.banks_active().union(self.banks_inactive(), self.mem)
#        
#    def accounts_all(self):
#        return self.accounts_active().union(self.accounts_inactive(), self.mem, self.banks)
        
#    def creditcards_all(self):
#        return self.creditcards_active().union(self.creditcards_inactive(), self.mem,  self.accounts)
#        
#    def investments_all(self):
#        return self.investments_active().union(self.investments_inactive(), self.mem, self.accounts, self.products, self.benchmark)
    
    
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
            return self.investments_active()()
        else:
            return self.investments_inactive()()

    def creditcards_set(self, active):
        """Function to point to list if is active or not"""
        if active==True:
            return self.creditcards_active()()
        else:
            return self.creditcards_inactive()()

        
class Dividend:
    def __init__(self, mem):
        self.mem=mem
        self.id=None
        self.investment=None
        self.bruto=None
        self.retencion=None
        self.neto=None
        self.dpa=None
        self.fecha=None
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
        self.fecha=fecha
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
        accountoperation=AccountOperation(self.mem).init__db_query(row['id_opercuentas'])
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
            return Money(self.mem, self.bruto, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion).local(self.fecha)
    def net(self, type=1):
        if type==1:
            return Money(self.mem, self.neto, self.investment.product.currency)
        elif type==2:
            return Money(self.mem, self.neto, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion)
        elif type==3:
            return Money(self.mem, self.neto, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion).local(self.fecha)
    def retention(self, type=1):
        if type==1:
            return Money(self.mem, self.retencion, self.investment.product.currency)
        elif type==2:
            return Money(self.mem, self.retencion, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion)
        elif type==3:
            return Money(self.mem, self.retencion, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion).local(self.fecha)
    def dps(self, type=1):
        "Dividend per share"
        if type==1:
            return Money(self.mem, self.dpa, self.investment.product.currency)
        elif type==2:
            return Money(self.mem, self.dpa, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion)
        elif type==3:
            return Money(self.mem, self.dpa, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion).local(self.fecha)
    def comission(self, type=1):
        if type==1:
            return Money(self.mem, self.comision, self.investment.product.currency)
        elif type==2:
            return Money(self.mem, self.comision, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion)
        elif type==3:
            return Money(self.mem, self.comision, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion).local(self.fecha)
            
        
    def neto_antes_impuestos(self):
        return self.bruto-self.comision
    
    def save(self):
        """Insertar un dividend y una opercuenta vinculada a la tabla dividends en el campo id_opercuentas
        
        En caso de que sea actualizar un dividend hay que actualizar los datos de opercuenta y se graba desde aquí. No desde el objeto opercuenta
        
        Actualiza la cuenta 
        """
        cur=self.mem.con.cursor()
        if self.id==None:#Insertar
            self.opercuenta=AccountOperation(self.mem).init__create( self.fecha,self.concepto, self.concepto.tipooperacion, self.neto, "Transaction not finished", self.investment.account)
            self.opercuenta.save()
            cur.execute("insert into dividends (fecha, valorxaccion, bruto, retencion, neto, id_inversiones,id_opercuentas, comision, id_conceptos,currency_conversion) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) returning id_dividends", (self.fecha, self.dpa, self.bruto, self.retencion, self.neto, self.investment.id, self.opercuenta.id, self.comision, self.concepto.id, self.currency_conversion))
            self.id=cur.fetchone()[0]
            self.opercuenta.comentario=Comment(self.mem).setEncoded10004(self)
            self.opercuenta.save()
        else:
            self.opercuenta.datetime=self.fecha
            self.opercuenta.importe=self.neto
            self.opercuenta.comentario=Comment(self.mem).setEncoded10004(self)
            self.opercuenta.concepto=self.concepto
            self.opercuenta.tipooperacion=self.concepto.tipooperacion
            self.opercuenta.save()
            cur.execute("update dividends set fecha=%s, valorxaccion=%s, bruto=%s, retencion=%s, neto=%s, id_inversiones=%s, id_opercuentas=%s, comision=%s, id_conceptos=%s, currency_conversion=%s where id_dividends=%s", (self.fecha, self.dpa, self.bruto, self.retencion, self.neto, self.investment.id, self.opercuenta.id, self.comision, self.concepto.id, self.currency_conversion, self.id))
        cur.close()

class InvestmentOperation:
    def __init__(self, mem):
        self.mem=mem
        self.id=None
        self.tipooperacion=None
        self.investment=None
        self.acciones=None
#        self.importe=None
        self.impuestos=None
        self.comision=None
        self.valor_accion=None
        self.datetime=None
        self.comentario=None
        self.archivada=None
        self.currency_conversion=None
        self.show_in_ranges=True
        
    def __repr__(self):
        return ("IO {0} ({1}). {2} {3}. Acciones: {4}. Valor:{5}. IdObject: {6}. Currency conversion {7}".format(self.investment.name, self.investment.id,  self.datetime, self.tipooperacion.name,  self.acciones,  self.valor_accion, id(self), self.currency_conversion))
        
        
    def init__db_row(self,  row, inversion,  tipooperacion):
        self.id=row['id_operinversiones']
        self.tipooperacion=tipooperacion
        self.investment=inversion
        self.acciones=row['acciones']
#        self.importe=row['importe']
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
        self.acciones=acciones
#        self.importe=importe
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
            return Money(self.mem, abs(self.acciones*self.valor_accion), self.investment.product.currency)
        else:
            return Money(self.mem, abs(self.acciones*self.valor_accion), self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion)
            
    def net(self, type=1):
        if self.acciones>=Decimal(0):
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
            c=AccountOperationOfInvestmentOperation(self.mem).init__create(self.datetime, self.mem.conceptos.find_by_id(29), self.tipooperacion, importe.amount, self.comentario, self.investment.account, self,self.investment)
            c.save()
        elif self.tipooperacion.id==5:#// Venta Acciones
            #//Se pone un registro de compra de acciones que resta el balance de la opercuenta
            importe=self.gross(type=2)-self.comission(type=2)-self.taxes(type=2)
            c=AccountOperationOfInvestmentOperation(self.mem).init__create(self.datetime, self.mem.conceptos.find_by_id(35), self.tipooperacion, importe.amount, self.comentario, self.investment.account, self,self.investment)
            c.save()
        elif self.tipooperacion.id==6:
            #//Si hubiera comisión se añade la comisión.
            if(self.comision!=0):
                importe=-self.comission(type=2)-self.taxes(type=2)
                c=AccountOperationOfInvestmentOperation(self.mem).init__create(self.datetime, self.mem.conceptos.find_by_id(38), self.mem.tiposoperaciones.find_by_id(1), importe.amount, self.comentario, self.investment.account, self,self.investment)
                c.save()
    
    def copy(self, investment=None):
        """
            Crea una inversion operacion desde otra inversionoepracion. NO es un enlace es un objeto clone
            Si el parametro investment es pasado usa el objeto investment  en vez de una referencia a self.investmen
        """
        inv=self.investment if investment==None else investment
        return InvestmentOperation(self.mem).init__create(self.tipooperacion, self.datetime, inv , self.acciones, self.impuestos, self.comision, self.valor_accion, self.comentario,  self.show_in_ranges, self.currency_conversion, self.id)

    def less_than_a_year(self):
        if datetime.date.today()-self.datetime.date()<=datetime.timedelta(days=365):
                return True
        return False
        
    def save(self, recalculate=True,  autocommit=True):
        cur=self.mem.con.cursor()
        if self.id==None:#insertar
            cur.execute("insert into operinversiones(datetime, id_tiposoperaciones,  acciones,  impuestos,  comision,  valor_accion, comentario, show_in_ranges, id_inversiones, currency_conversion) values (%s, %s, %s, %s, %s, %s, %s, %s,%s,%s) returning id_operinversiones", (self.datetime, self.tipooperacion.id, self.acciones, self.impuestos, self.comision, self.valor_accion, self.comentario, self.show_in_ranges,  self.investment.id,  self.currency_conversion))
            self.id=cur.fetchone()[0]
            self.investment.op.append(self)
        else:
            cur.execute("update operinversiones set datetime=%s, id_tiposoperaciones=%s, acciones=%s, impuestos=%s, comision=%s, valor_accion=%s, comentario=%s, id_inversiones=%s, show_in_ranges=%s, currency_conversion=%s where id_operinversiones=%s", (self.datetime, self.tipooperacion.id, self.acciones, self.impuestos, self.comision, self.valor_accion, self.comentario, self.investment.id, self.show_in_ranges,  self.currency_conversion,  self.id))
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
            
class Account:
    def __init__(self, mem):
        self.mem=mem
        self.id=None
        self.name=None
        self.eb=None
        self.active=None
        self.numero=None
        self.currency=None
        self.eb=None #Enlace a objeto

    def __repr__(self):
        return ("Instancia de Account: {0} ({1})".format( self.name, self.id))
        
    def init__db_row(self, row, eb):
        self.id=row['id_cuentas']
        self.name=row['cuenta']
        self.eb=eb
        self.active=row['active']
        self.numero=row['numerocuenta']
        self.currency=self.mem.currencies.find_by_id(row['currency'])
        return self
    
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
            
    def init__create(self, name,  eb, activa, numero, currency, id=None):
        self.id=id
        self.name=name
        self.eb=eb
        self.active=activa
        self.numero=numero
        self.currency=currency
        return self
        
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
            oc_comision=AccountOperation(self.mem).init__create(datetime, self.mem.conceptos.find_by_id(38), self.mem.tiposoperaciones.find_by_id(1), -comision, notfinished, cuentaorigen )
            oc_comision.save()
        oc_origen=AccountOperation(self.mem).init__create(datetime, self.mem.conceptos.find_by_id(4), self.mem.tiposoperaciones.find_by_id(3), -importe, notfinished, cuentaorigen )
        oc_origen.save()
        oc_destino=AccountOperation(self.mem).init__create(datetime, self.mem.conceptos.find_by_id(5), self.mem.tiposoperaciones.find_by_id(3), importe, notfinished, cuentadestino )
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
#        self.id_cuentas=None
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
#        elif type==2:
#            return Money(self.mem, self.venta, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion)
#        elif type==3:
#            return Money(self.mem, self.venta, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion).local(self.datetime)
            
    def setDividends_from_current_operations(self):
        """
            Returns a setDividens from the datetime of the first currnt operation
        """
        first=self.op_actual.first()
        set=SetDividendsHomogeneus(self.mem, self)
        if first!=None:
            set.load_from_db("select * from dividends where id_inversiones={0} and fecha >='{1}'  order by fecha".format(self.id, first.datetime))
        return set

    def setDividends_from_operations(self):
        """
            Returns a setDividens with all the dividends
        """
        set=SetDividendsHomogeneus(self.mem, self)
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
        self.op=SetInvestmentOperationsHomogeneus(self.mem, self)
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
            return Money(self.mem, self.acciones()*self.product.estimations_dps.find(year).estimation, self.product.currency)
        except:
            return Money(self.mem, 0, self.product.currency)


    def acciones(self, fecha=None):
        """Función que saca el número de acciones de las self.op_actual"""
        if fecha==None:
            dat=self.mem.localzone.now()
        else:
            dat=day_end_from_date(fecha, self.mem.localzone)
        resultado=Decimal('0')

        for o in self.op.arr:
            if o.datetime<=dat:
                resultado=resultado+o.acciones
        return resultado
        
    def hasSameAccountCurrency(self):
        """
            Returns a boolean
            Check if investment currency is the same that account currency
        """
        if self.product.currency.id==self.account.currency.id:
            return True
        return False
#        
#    def pendiente(self):
#        """Función que calcula el balance  pendiente de la inversión
#                Necesita haber cargado mq getbasic y operinversionesactual"""
#        return self.balance()-self.invertido()
        
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
        acciones=self.acciones(fecha)
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
            ### 0 Creo una vinversion fake para reutilizar codigo, cargando operinversiones hasta date
            invfake=Investment(self.mem).copy()
            invfake.op=self.op.copy_until_datetime(day_end_from_date(date, self.mem.localzone))
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
        
#        self.op_diferido=SetCreditCardOperations(self.mem)#array que almacena objetos CreditCard operacion que son en diferido, los carga
        
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
        
#    def comment(self):
#        """Función que genera un comentario parseado según el tipo de operación o concepto
#        Opertarjetas refund:
#            El comentario es : "Refund|id_opertarjetas|lastcomment"
#        """
##        c=self.comentario.split("|")
##        if self.concepto.id==67 and c[0]=="Refund":#CreditCardOperation refund
##            opertarjeta=CreditCardOperation(self.mem).init__db_query(int(c[1]))        
##            return QApplication.translate("Core", "Refund of {} credit card payment which had an amount of {}. {}").format(str(opertarjeta.datetime)[0:19], opertarjeta.tarjeta.account.currency.string(opertarjeta.importe), c[2])
##        else:
#        logging.info("obsolete comment")
#        return self.comentario 

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
    
    def init__from_db(self, year, lastyear_assests=None):
        """Fills the object with data from db.
        If lastyear_assests=None it gets the assests from db"""
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
        
    def annual_balance(self):
        """Returns the percentage of the last year assests"""
        return self.lastyear_assests.amount*self.percentage/100
        
    def monthly_balance(self):
        """Returns the monthly balance (annual/12)"""
        return self.annual_balance()/12
        
    def qtablewidgetitem_monthly(self, amount):
        """returns a qtablewidgetitem colored"""
        item=self.mem.localcurrency.qtablewidgetitem(amount)
        if amount<self.monthly_balance():   
            item.setBackground(QColor(255, 148, 148))
        else:
            item.setBackground(QColor(148, 255, 148))
        return item
        
    def qtablewidgetitem_annual(self, amount):
        item=self.mem.localcurrency.qtablewidgetitem(amount)
        if amount<self.annual_balance():   
            item.setBackground(QColor(255, 148, 148))
        else:
            item.setBackground(QColor(148, 255, 148))
        return item
    def qtablewidgetitem_accumulated(self, amount, month):
        """month: january=1"""
        item=self.mem.localcurrency.qtablewidgetitem(amount)
        if amount<self.monthly_balance()*month:   
            item.setBackground(QColor(255, 148, 148))
        else:
            item.setBackground(QColor(148, 255, 148))
        return item
        

class Assets:
    def __init__(self, mem):
        self.mem=mem        
    
    def first_datetime_with_user_data(self):        
        """Devuelve la datetime actual si no hay datos. Base de datos vacía"""
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
#        
#    def saldo_todas_inversiones_no_losses(self, setinversiones,   fecha):
#        """
#            Calcula el valor de las inversiones sin perdidas es decir solo lo invertido
#        """
#        resultado=Money(self.mem, 0, self.mem.localcurrency)
#        for i in setinversiones.arr:
#            resultado=resultado+i.invertido(fecha, type=3)
#        return resultado
        
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
            setdiv=SetDividendsHomogeneus(self.mem, inv)
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
            setdiv=SetDividendsHomogeneus(self.mem, inv)
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


class SetCreditCards(SetCommons):
    def __init__(self, mem, cuentas):
        SetCommons.__init__(self)
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
        """Devuelve un SetCreditCards con las tarjetas de una determinada cuenta"""
        s=SetCreditCards(self.mem, self.accounts)
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
class SetCreditCardOperations:
    def __init__(self, mem):
        self.mem=mem
        self.arr=[]
        self.selected=None#Used to work with selected items is a SetCreditCardOperations created when necesarie
        
    def clear(self):
        del self.arr
        self.arr=[]

    def first(self):
        if self.length()>0:
            return self.arr[0]
        else:
            return None

    def balance(self):
        """Returns the balance of all credit card operations"""
        result=Decimal(0)
        for o in self.arr:
            result=result+o.importe
        return result
        
    def append(self, objeto):
        self.arr.append(objeto)

    def length(self):
        return len(self.arr)
        
        
    def load_from_db(self, sql):
        del self.arr
        self.arr=[]
        cur=self.mem.con.cursor()
        cur.execute(sql)#"Select * from opercuentas"
        for row in cur:        
            co=CreditCardOperation(self.mem).init__db_row(row, self.mem.conceptos.find_by_id(row['id_conceptos']), self.mem.tiposoperaciones.find_by_id(row['id_tiposoperaciones']), self.mem.data.creditcards.find_by_id(row['id_tarjetas']), AccountOperation(self.mem).init__db_query(row['id_opercuentas']))
            self.append(co)
        cur.close()
    
#    def setSelected(self, sel):
#        """
#            Searches the objects id in the array and mak selected. ReturnsTrue if the o.id exists in the arr and False if don't
#        """
#        for i, o in enumerate(self.arr):
#            if o.id==sel.id:
#                self.selected=o
#                return True
#        self.selected=None
#        return False
    def sort(self):       
        self.arr=sorted(self.arr, key=lambda e: e.datetime,  reverse=False) 
        
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
        self.sort()
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

class SetOperationTypes(SetCommons):
    def __init__(self, mem):
        SetCommons.__init__(self)
        self.mem=mem     
        
    def load(self):
        self.append(OperationType().init__create( QApplication.translate("Core","Expense"), 1))
        self.append(OperationType().init__create( QApplication.translate("Core","Income"), 2))
        self.append(OperationType().init__create( QApplication.translate("Core","Transfer"), 3))
        self.append(OperationType().init__create( QApplication.translate("Core","Purchase of shares"), 4))
        self.append(OperationType().init__create( QApplication.translate("Core","Sale of shares"), 5))
        self.append(OperationType().init__create( QApplication.translate("Core","Added of shares"), 6))
        self.append(OperationType().init__create( QApplication.translate("Core","Credit card billing"), 7))
        self.append(OperationType().init__create( QApplication.translate("Core","Transfer of funds"), 8)) #Se contabilizan como ganancia
        self.append(OperationType().init__create( QApplication.translate("Core","Transfer of shares. Origin"), 9)) #No se contabiliza
        self.append(OperationType().init__create( QApplication.translate("Core","Transfer of shares. Destiny"), 10)) #No se contabiliza     


    def qcombobox_basic(self, combo,  selected=None):
        """Load lust some items
        Selected is and object
        It sorts by name the arr""" 
        self.order_by_name()
        combo.clear()
        for n in (1, 2):
            a=self.dic_arr[str(n)]
            combo.addItem(a.name, a.id)

        if selected!=None:
            combo.setCurrentIndex(combo.findData(selected.id))
            
            
    def qcombobox_investments_operations(self, combo,  selected=None):
        """Load lust some items
        Selected is and object
        It sorts by name the arr""" 
        self.order_by_name()
        combo.clear()
        for n in (4, 5, 6, 8):
            a=self.dic_arr[str(n)]
            combo.addItem(a.name, a.id)

        if selected!=None:
            combo.setCurrentIndex(combo.findData(selected.id))


def mylog(text):
    f=open("/tmp/xulpymoney.log","a")
    f.write(str(datetime.datetime.now()) + "|" + text + "\n")
    f.close()
    
def decimal_check(dec):
    print ("Decimal check", dec, dec.__class__,  dec.__repr__(),  "prec:",  getcontext().prec)

class SetAgrupations(SetCommons):
    """Se usa para meter en mem las agrupaciones, pero también para crear agrupaciones en las inversiones"""
    def __init__(self, mem):
        """Usa la variable mem.Agrupations"""
        SetCommons.__init__(self)
        self.mem=mem

    def load_all(self):
        self.append(Agrupation(self.mem).init__create( "IBEX","Ibex 35", self.mem.types.find_by_id(3), self.mem.stockmarkets.find_by_id(1) ))
        self.append(Agrupation(self.mem).init__create( "MERCADOCONTINUO","Mercado continuo español", self.mem.types.find_by_id(3), self.mem.stockmarkets.find_by_id(1) ))
        self.append(Agrupation(self.mem).init__create("CAC",  "CAC 40 de París", self.mem.types.find_by_id(3),self.mem.stockmarkets.find_by_id(3) ))
        self.append(Agrupation(self.mem).init__create( "EUROSTOXX","Eurostoxx 50", self.mem.types.find_by_id(3),self.mem.stockmarkets.find_by_id(10)  ))
        self.append(Agrupation(self.mem).init__create( "DAX","DAX", self.mem.types.find_by_id(3), self.mem.stockmarkets.find_by_id(5)  ))
        self.append(Agrupation(self.mem).init__create("SP500",  "Standard & Poors 500", self.mem.types.find_by_id(3), self.mem.stockmarkets.find_by_id(2)  ))
        self.append(Agrupation(self.mem).init__create( "NASDAQ100","Nasdaq 100", self.mem.types.find_by_id(3), self.mem.stockmarkets.find_by_id(2)  ))
        self.append(Agrupation(self.mem).init__create( "EURONEXT",  "EURONEXT", self.mem.types.find_by_id(3), self.mem.stockmarkets.find_by_id(10)  ))
        self.append(Agrupation(self.mem).init__create( "DEUTSCHEBOERSE",  "DEUTSCHEBOERSE", self.mem.types.find_by_id(3), self.mem.stockmarkets.find_by_id(5)  ))
        self.append(Agrupation(self.mem).init__create( "LATIBEX",  "LATIBEX", self.mem.types.find_by_id(3), self.mem.stockmarkets.find_by_id(1)  ))

        self.append(Agrupation(self.mem).init__create( "e_fr_LYXOR","LYXOR", self.mem.types.find_by_id(4),self.mem.stockmarkets.find_by_id(3)  ))
        self.append(Agrupation(self.mem).init__create( "e_de_DBXTRACKERS","Deutsche Bank X-Trackers", self.mem.types.find_by_id(4),self.mem.stockmarkets.find_by_id(5)  ))
        
        self.append(Agrupation(self.mem).init__create( "f_es_BMF","Fondos de la bolsa de Madrid", self.mem.types.find_by_id(2), self.mem.stockmarkets.find_by_id(1) ))
        self.append(Agrupation(self.mem).init__create( "f_fr_CARMIGNAC","Gestora CARMIGNAC", self.mem.types.find_by_id(2), self.mem.stockmarkets.find_by_id(3) ))
        self.append(Agrupation(self.mem).init__create("f_cat_money","Funds category: Money", self.mem.types.find_by_id(2),self.mem.stockmarkets.find_by_id(10)))

        self.append(Agrupation(self.mem).init__create( "w_fr_SG","Warrants Societe Generale", self.mem.types.find_by_id(5),self.mem.stockmarkets.find_by_id(3) ))
        self.append(Agrupation(self.mem).init__create("w_es_BNP","Warrants BNP Paribas", self.mem.types.find_by_id(5),self.mem.stockmarkets.find_by_id(1)))
        
        
  
    def clone_by_type(self,  type):
        """Muestra las agrupaciónes de un tipo pasado como parámetro. El parámetro type es un objeto Type"""
        resultado=SetAgrupations(self.mem)
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
        resultado=SetAgrupations(self.mem)
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
        resultado=SetAgrupations(self.mem)
        for i in range (cmb.count()):
            resultado.append(self.mem.agrupations.find_by_id(cmb.itemData(i)))
        return resultado

class SetLeverages(SetCommons):
    def __init__(self, mem):
        """Usa la variable mem.Agrupations"""
        SetCommons.__init__(self)
        self.mem=mem

    def load_all(self):
        self.append(Leverage(self.mem).init__create(0 ,QApplication.translate("Core","Not leveraged"), 1))
        self.append(Leverage(self.mem).init__create( 1,QApplication.translate("Core","Variable leverage (Warrants)"), 10))
        self.append(Leverage(self.mem).init__create( 2,QApplication.translate("Core","Leverage x2"), 2))
        self.append(Leverage(self.mem).init__create( 3,QApplication.translate("Core","Leverage x3"), 3))
        self.append(Leverage(self.mem).init__create( 4,QApplication.translate("Core","Leverage x4"), 4))


class SetOrders:
    def __init__(self, mem):
        self.mem=mem
        self.arr=[]
        self.selected=None
        
    def init__from_db(self, sql):
        cur=self.mem.con.cursor()
        cur.execute(sql)
        for row in cur:
            self.append(Order(self.mem).init__db_row(row))
        cur.close()
        return self
        
    def append(self, objeto):
        self.arr.append(objeto)
        
    def remove(self, order):
        """Remove from array"""
        self.arr.remove(order)#Remove from array
        order.remove()#Database

    def length(self):
        return len(self.arr)

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
                table.setItem(i, 7, QTableWidgetItem(""))
            if p.is_executed():
                table.setItem(i, 8, qdatetime(p.executed, self.mem.localzone))
            else:
                table.setItem(i, 8, QTableWidgetItem(""))
                
            #Color
            if p.is_executed():
                for column in range (table.columnCount()):
                    table.item(i, column).setBackground( QColor(182, 255, 182))                     
            elif p.is_expired():
                for column in range (table.columnCount()):
                    table.item(i, column).setBackground( QColor(255, 182, 182))     

class SetPriorities(SetCommons):
    def __init__(self, mem):
        """Usa la variable mem.Agrupations. Debe ser una lista no un diccionario porque importa el orden"""
        SetCommons.__init__(self)
        self.mem=mem
                
    def load_all(self):
        self.append(Priority().init__create(1,"Yahoo Financials. 200 pc."))
        self.append(Priority().init__create(5,"Productos cotizados bonus. 20 pc."))
        self.append(Priority().init__create(6,"Societe Generale Warrants. Todos pc."))
        self.append(Priority().init__create(7,"Bond alemán desde http://jcbcarc.dyndns.org. 3 pc."))#SANTGES ERA 3, para que no se repitan
        self.append(Priority().init__create(9,"Mercado continuo from Bolsa de Madrid"))
        
    def init__create_from_db(self, arr):
        """Convierte el array de enteros de la base datos en un array de objetos priority"""
        resultado=SetPriorities(self.mem)
        if arr==None or len(arr)==0:
            resultado.arr=[]
        else:
            for a in arr:
                resultado.append(self.mem.priorities.find_by_id(a))
        return resultado
        
    def array_of_id(self):
        """Used to psycopg.execute automatical pare"""
        resultado=[]
        for p in self.arr:
            resultado.append(p.id)
        return resultado

        
    def init__create_from_combo(self, cmb):
        """Función que convierte un combo de agrupations a un array de agrupations"""
        for i in range (cmb.count()):
            self.append(self.mem.priorities.find_by_id(cmb.itemData(i)))
        return self
                
class SetPrioritiesHistorical(SetCommons):
    def __init__(self, mem):
        """Usa la variable mem.Agrupations"""
        SetCommons.__init__(self)
        self.mem=mem

    def load_all(self):
        self.append(PriorityHistorical().init__create(3,QApplication.translate("Core","Individual. Yahoo historicals")))
        self.append(PriorityHistorical().init__create(8,QApplication.translate("Core","Individual. Morningstar funds")))
            
    def init__create_from_db(self, arr):
        """Convierte el array de enteros de la base datos en un array de objetos priority"""
        resultado=SetPrioritiesHistorical(self.mem)
        if arr==None or len(arr)==0:
            resultado.arr=[]
        else:
            for a in arr:
                resultado.append(self.mem.prioritieshistorical.find_by_id(a))
        return resultado

    def array_of_id(self):
        """Used to psycopg.execute automatical pare"""
        resultado=[]
        for p in self.arr:
            resultado.append(p.id)
        return resultado

    def init__create_from_combo(self, cmb):
        """Función que convierte un combo de agrupations a un array de agrupations"""
        for i in range (cmb.count()):
            self.append(self.mem.prioritieshistorical.find_by_id(cmb.itemData(i)))
        return self

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
        
    def today_closes(self):
        """
            Returns a datetime with timezone with the todays stockmarket closes
        """
        return dt(datetime.date.today(), self.closes, self.zone)

    def today_starts(self):
        """
            Returns a datetime with timezone with the todays stockmarket closes
        """
        return dt(datetime.date.today(), self.starts, self.zone)

class Color:
    esc_seq = "\x1b["
    codes={}
    codes["reset"]     = esc_seq + "39;49;00m"
    codes["bold"]      = esc_seq + "01m"
    codes["faint"]     = esc_seq + "02m"
    codes["standout"]  = esc_seq + "03m"
    codes["underline"] = esc_seq + "04m"
    codes["blink"]     = esc_seq + "05m"
    codes["overline"]  = esc_seq + "06m"  # Who made this up? Seriously.
    codes["teal"]      = esc_seq + "36m"
    codes["turquoise"] = esc_seq + "36;01m"
    codes["fuchsia"]   = esc_seq + "35;01m"
    codes["purple"]    = esc_seq + "35m"
    codes["blue"]      = esc_seq + "34;01m"
    codes["darkblue"]  = esc_seq + "34m"
    codes["green"]     = esc_seq + "32;01m"
    codes["darkgreen"] = esc_seq + "32m"
    codes["yellow"]    = esc_seq + "33;01m"
    codes["brown"]     = esc_seq + "33m"
    codes["red"]       = esc_seq + "31;01m"
    codes["darkred"]   = esc_seq + "31m"
    
    def resetColor(self, ):
        return self.codes["reset"]
    def ctext(self, color,text):
        return self.codes[text]+text+self.codes["reset"]
    def bold(self, text):
        return self.codes["bold"]+text+self.codes["reset"]
    def white(self, text):
        return self.bold(text)
    def teal(self, text):
        return self.codes["teal"]+text+self.codes["reset"]
    def turquoise(self, text):
        return self.codes["turquoise"]+text+self.codes["reset"]
    def darkteal(self, text):
        return self.turquoise(text)
    def fuchsia(self, text):
        return self.codes["fuchsia"]+text+self.codes["reset"]
    def purple(self, text):
        return self.codes["purple"]+text+self.codes["reset"]
    def blue(self, text):
        return self.codes["blue"]+text+self.codes["reset"]
    def darkblue(self, text):
        return self.codes["darkblue"]+text+self.codes["reset"]
    def green(self, text):
        return self.codes["green"]+text+self.codes["reset"]
    def darkgreen(self, text):
        return self.codes["darkgreen"]+text+self.codes["reset"]
    def yellow(self, text):
        return self.codes["yellow"]+text+self.codes["reset"]
    def brown(self, text):
        return self.codes["brown"]+text+self.codes["reset"]
    def darkyellow(self, text):
        return self.brown(text)
    def red(self, text):
        return self.codes["red"]+text+self.codes["reset"]
    def darkred(self, text):
        return self.codes["darkred"]+text+self.codes["reset"]

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
            return "{0} {1}".format(round(number, digits),self.symbol)
            
    def currencies_exchange(self, cur,  quote, origen, destino):
        cambio=Quote.valor2(cur, origen+"2"+destino, quote['fecha'],  quote['hora'])
        exchange={"code":quote['code'],"quote":quote['quote']*cambio['quote'],  "date":cambio['date'], "time":cambio['time'],  "zone":cambio['zone'],  "currency":destino}
        return exchange

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

class ProductComparation:
    """Compares two products, removes ohclDaily that aren't in both products"""
    def __init__(self, mem, product1, product2):
        self.mem=mem
        
        self.__fromDate=None#None all array.
        self.product1=product1
        self.product2=product2     
        self.set1=SetOHCLDaily(self.mem, self.product1)#Set with common data. Needed in order to not broke self.product1 data
        self.set2=SetOHCLDaily(self.mem, self.product2)
        self.__commonDates=None

        #Load data if necesary
        for p in [self.product1, self.product2]:
            if p.result.ohclDaily.length()==0:
                p.result.get_basic_and_ohcls()  
  
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
#            raise MoneyOperationException("MoneyOperationException")
            raise "MoneyOperationException"
#            b=money.convert(self.currency)
#            return Money(self.mem, self.amount+b.amount, self.currency)
            
        
    def __sub__(self, money):
        """Si las divisas son distintas, queda el resultado con la divisa del primero"""
        if self.currency==money.currency:
            return Money(self.mem, self.amount-money.amount, self.currency)
        else:
            logging.error("Before substracting, please convert to the same currency")
            raise "MoneyOperationException"
#            b=money.convert(self.currency)
#            return Money(self.mem, self.amount-b.amount, self.currency)
        
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
#            b=money.convert(self.currency)
#            return Money(self.mem, self.amount*b.amount, self.currency)
    
    def __truediv__(self, money):
        """Si las divisas son distintas, queda el resultado con la divisa del primero"""
        if self.currency==money.currency:
            return Money(self.mem, self.amount/money.amount, self.currency)
        else:
            logging.error("Before true dividing, please convert to the same currency")
            sys.exit(1)
#            b=money.convert(self.currency)
#            return Money(self.mem, self.amount/b.amount, self.currency)
        
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

class SetDPS:
    def __init__(self, mem,  product):
        self.arr=[]
        self.mem=mem   
        self.product=product
        
    def append(self, o):
        self.arr.append(o)
    
    def length(self):
        return len(self.arr)
    
    def load_from_db(self):
        del self.arr
        self.arr=[]
        cur=self.mem.con.cursor()
        cur.execute( "select * from dps where id=%s order by date", (self.product.id, ))
        for row in cur:
            self.arr.append(DPS(self.mem, self.product).init__from_db_row(row))
        cur.close()            
        
    def find(self, id):
        """Como puede no haber todos los años se usa find que devuelve una estimacion nula sino existe"""
        for e in self.arr:
            if e.id==id:
                return e
        return None
    
    
    
    def save(self):
        """
            Saves DPS Without commit
        """            
        for o in self.arr:
            o.save()

    def sort(self):
        self.arr=sorted(self.arr, key=lambda c: c.date,  reverse=False)         
        
    def myqtablewidget(self, table):
        table.setColumnCount(2)
        table.setHorizontalHeaderItem(0, QTableWidgetItem(QApplication.translate("Core", "Date" )))
        table.setHorizontalHeaderItem(1, QTableWidgetItem(QApplication.translate("Core", "Gross" )))
        self.sort()   
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

    def adjustSetOHCLDaily(self, set):
        r=SetOHCLDaily(self.mem, self.product)
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

#            print (cur.mogrify("insert into estimations_eps (id, year, estimation, date_estimation, source, manual) values (%s,%s,%s,%s,%s,%s)", (self.product.id, self.year, self.estimation, self.date_estimation, self.source, self.manual)))
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
#            print (cur.mogrify("insert into estimations_dps (id, year, estimation, date_estimation, source, manual) values (%s,%s,%s,%s,%s,%s)", (self.product.id, self.year, self.estimation, self.date_estimation, self.source, self.manual)))
        elif self.estimation!=None:            
            cur.execute("update estimations_dps set estimation=%s, date_estimation=%s, source=%s, manual=%s where id=%s and year=%s", (self.estimation, self.date_estimation, self.source, self.manual, self.product.id, self.year))
        cur.close()
        
    def percentage(self):
        """Hay que tener presente que lastyear (Objeto Quote) es el lastyear del año actual
        Necesita tener cargado en id el lastyear """
        
#        try:
#            return self.estimation*100/self.product.result.basic.last.quote
#        except:
#            return None
        return Percentage(self.estimation, self.product.result.basic.last.quote)


class Product:
    def __init__(self, mem):
        self.mem=mem
        self.name=None
        self.isin=None
        self.currency=None #Apunta a un objeto currency
        self.type=None
        self.agrupations=None #Es un objeto SetAgrupations
        self.id=None
        self.web=None
        self.address=None
        self.phone=None
        self.mail=None
        self.percentage=None
        self.mode=None#Anterior mode investmentmode
        self.leveraged=None
        self.stockmarket=None
        self.tickers=None#Its a list of strings, eTickerPosition is the 
        self.priority=None
        self.priorityhistorical=None
        self.comment=None
        self.obsolete=None
        
        self.result=None#Variable en la que se almacena QuotesResult
        self.estimations_dps=SetEstimationsDPS(self.mem, self)#Es un diccionario que guarda objetos estimations_dps con clave el año
        self.estimations_eps=SetEstimationsEPS(self.mem, self)
        self.result=QuotesResult(self.mem,self)

        self.dps=None #It's created when loading quotes in quotes result
        self.splits=None #It's created when loading quotes in quotes result
    def __repr__(self):
        return "{0} ({1}) de la {2}".format(self.name , self.id, self.stockmarket.name)
                
    def init__db_row(self, row):
        """row es una fila de un pgcursro de investmentes"""
        self.name=row['name']
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
        self.priority=SetPriorities(self.mem).init__create_from_db(row['priority'])
        self.priorityhistorical=SetPrioritiesHistorical(self.mem).init__create_from_db(row['priorityhistorical'])
        self.comment=row['comment']
        self.obsolete=row['obsolete']
        
        return self


    def init__create(self, name,  isin, currency, type, agrupations, active, web, address, phone, mail, percentage, mode, leveraged, stockmarket, tickers,  priority, priorityhistorical, comment, obsolete, id=None):
        """agrupations es un setagrupation, priority un SetPriorities y priorityhistorical un SetPrioritieshistorical"""
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
        self.priority=priority
        self.priorityhistorical=priorityhistorical
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
            cur.execute("insert into products (id, name,  isin,  currency,  type,  agrupations,   web, address,  phone, mail, percentage, pci,  leveraged, stockmarkets_id, tickers, priority, priorityhistorical , comment,  obsolete) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",  (id, self.name,  self.isin,  self.currency.id,  self.type.id,  self.agrupations.dbstring(), self.web, self.address,  self.phone, self.mail, self.percentage, self.mode.id,  self.leveraged.id, self.stockmarket.id, self.tickers, self.priority.array_of_id(), self.priorityhistorical.array_of_id() , self.comment, self.obsolete))
            self.id=id
        else:
            cur.execute("update products set name=%s, isin=%s,currency=%s,type=%s, agrupations=%s, web=%s, address=%s, phone=%s, mail=%s, percentage=%s, pci=%s, leveraged=%s, stockmarkets_id=%s, tickers=%s, priority=%s, priorityhistorical=%s, comment=%s, obsolete=%s where id=%s", ( self.name,  self.isin,  self.currency.id,  self.type.id,  self.agrupations.dbstring(),  self.web, self.address,  self.phone, self.mail, self.percentage, self.mode.id,  self.leveraged.id, self.stockmarket.id, self.tickers, self.priority.array_of_id(), self.priorityhistorical.array_of_id() , self.comment, self.obsolete,  self.id))
        cur.close()
    

    def has_autoupdate(self):
        """Return if the product has autoupdate in some source
        REMEMBER TO CHANGE on_actionProductsAutoUpdate_triggered en frmMain"""
        if self.obsolete==True:
            return False
#        #With isin
#        if self.priority.find_by_id(9)!=None or self.priorityhistorical.find_by_id(8)!=None:
#            if self.isin==None or self.isin=="":
#                return False
#            return True
#            
#        #With ticker
#        if self.priority.find_by_id(1)!=None or self.priorityhistorical.find_by_id(3)!=None:
#            if self.ticker==None or self.ticker=="":
#                return False
#            return True
        if self.isin!=None or self.tickers!=[None, None, None, None]:
            return True
            
        return False
        
    def setinvestments(self):
        """Returns a SetInvestments object with all the investments of the product. Investments can be active or inactive"""
        set=SetInvestments(self.mem, self.mem.data.accounts, self.mem.data.products, self.mem.data.benchmark)
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
        
#    def googleticker(self):
#        """
#            Uses ticker property. It's needed to search for a googleticker
#            Returns "" if doesn't exist in order to visualizate it better
#        """
#        if self.ticker[0]==None:
#            logging.debug("googleticker {} not found".format(self.ticker))
#            return None
#            
#        if len(self.ticker)<3:
#            logging.debug("googleticker {} not found".format(self.ticker))
#            return None
#        if self.type.id in (eProductType.Share, eProductType.ETF):#Acciones, etf
#            if  self.ticker[-3:]==".MC":
#                return "BME:{}".format(self.ticker[:-3])
#            if  self.ticker[-3:]==".DE":
#                return "FRA:{}".format(self.ticker[:-3])
#            if  self.ticker[-3:]==".PA":
#                return "EPA:{}".format(self.ticker[:-3])
#            if  self.ticker[-3:]==".MI":
#                return "BIT:{}".format(self.ticker[:-3])
#            if self.ticker in("AH.AS"):
#                return None
#            if len(self.ticker.split("."))==1:##Americanas
#                if self.agrupations.dbstring()=="|NASDAQ100|":
#                    return "NASDAQ:{}".format(self.ticker)
#                if self.agrupations.dbstring()=="|SP500|":
#                    return "NYSE:{}".format(self.ticker)
#        elif self.type.id==eProductType.Index:#Indices   
#            if self.ticker=="^IBEX":
#                return "INDEXBME:IB"
#            if self.ticker=="^GSPC":
#                return "INDEXSP:.INX"
#            if self.ticker=="^VIX":
#                return "INDEXCBOE:VIX"
#            if self.ticker=="PSI20.LS":
#                return "INDEXEURO:PSI20"
#            if self.ticker=="^STOXX50E":
#                return "INDEXSTOXX:SX5E"
#            if self.ticker=="^N225":
#                return "INDEXNIKKEI:NI225"
#            if self.ticker=="^NDX":
#                return "INDEXNASDAQ:NDX"
#            if self.ticker=="^IXIC":
#                return "INDEXNASDAQ:.IXIC"
#            if self.ticker=="^HSI":
#                return "INDEXHANGSENG:HSI"
#            if self.ticker=="FTSEMIB.MI":
#                return "INDEXFTSE:FTSEMIB"
#            if self.ticker=="^FTSE":
#                return "INDEXFTSE:UKX"
#            if self.ticker=="^DJI":
#                return "INDEXDJX:.DJI"
#            if self.ticker=="^FCHI":
#                return "INDEXEURO:PX1"
#            if self.ticker=="^GDAXI":
#                return "INDEXDB:DAX"
#        elif self.type.id==eProductType.Currency:#Currencies
#            if self.ticker=="EURUSD=X":
#                return "EURUSD"
#        logging.debug("googleticker {} not found".format(self.ticker))
#        return None
        

#    def googleticker2ticker(self, ticker):
#        """
#            Should not be used. I should use the product.find_by_ticker
#        """
#        logging.info("Should not be used. I should use the product.find_by_ticker")
#        a=ticker.split(":")
#        if  a[0]=="BME":
#            return "{}.MC".format(a[1])
#        if  a[0]=="FRA":
#            return "{}.DE".format(a[1])
#        if  a[0]=="EPA":
#            return "{}.PA".format(a[1])
#        if  a[0]=="BIT":
#            return "{}.MI".format(a[1])
#        if ticker=="INDEXBME:IB":
#            return "^IBEX"
#        if a[0] in ("NASDAQ",  "NYSEARCA", "NYSE"):
#            return "{}".format(a[1])
#        logging.debug("googleticker2ticker {} not found".format(ticker))
    
#    def googleticker2pytz(self, ticker):
#        a=ticker.split(":")
#        if a[0] in ("BME",  "INDEXBME"):
#            return "Europe/Madrid"
#        if a[0] in ("FRA", ):
#            return "Europe/Berlin"
#        if a[0] in ("EPA", ):
#            return "Europe/Paris"
#        if a[0] in ("BIT", ):
#            return "Europe/Rome"
#        if a[0] in ("NASDAQ",  "NYSEARCA", "NYSE"):
#            return "America/New_York"
#        return None
        
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
        result=QuotesResult(self.mem, self)
        result.get_basic_and_ohcls()
        dps=EstimationDPS(self.mem).init__from_db(self, datetime.date.today().year)
        print (dps.estimation, dps)
        (last, penultimate, lastyear, estimation)=(False, False, False, False)
        if result.basic.last: 
            if result.basic.last.quote:
                last=True
        if result.basic.penultimate: 
            if result.basic.penultimate.quote:
                penultimate=True
        if result.basic.lastyear: 
            if result.basic.lastyear.quote:
                lastyear=True
        if dps:
           if dps.estimation!=None:
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
        
    def priority_change(self, cur):
        """Cambia la primera prioridad y la pone en último lugar, necesita un commit()"""
        idtochange=self.priority[0]
        self.priority.remove(idtochange)
        self.priority.append(idtochange)
        cur.execute("update products set priority=%s", (str(self.priority)))
        
    def priorityhistorical_change(self, cur):
        """Cambia la primera prioridad y la pone en último lugar"""
        idtochange=self.priorityhistorical[0]
        self.priorityhistorical.remove(idtochange)
        self.priorityhistorical.append(idtochange)
        cur.execute("update products set priorityhistorical=%s", (str(self.priorityhistorical)))

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

    def convert_to_system_product(self):
        """It converts a product id<0 in a product >0"""
        cur=self.mem.con.cursor()
        cur.execute("select max(id)+1 from products;")#last id>0
        newid=cur.fetchone()[0]

        cur.execute("update inversiones set products_id=%s where products_id=%s",(newid,self.id))
        cur.execute("update quotes set id=%s where id=%s",(newid,self.id))
        cur.execute("update products set id=%s where id=%s",(newid,self.id))
        cur.execute("update dps set id=%s where id=%s",(newid,self.id))        
        cur.execute("update estimations_dps set id=%s where id=%s",(newid,self.id))        
        cur.execute("update estimations_eps set id=%s where id=%s",(newid,self.id))        
        cur.close()
        self.id=newid
        return self

        
    def convert_to_user_product(self):
        """It converts a product id>0 in a product <0"""
        cur=self.mem.con.cursor()
        cur.execute("select min(id)-1 from products;")#last id>0
        newid=cur.fetchone()[0]

        cur.execute("update inversiones set products_id=%s where products_id=%s",(newid,self.id))
        cur.execute("update quotes set id=%s where id=%s",(newid,self.id))
        cur.execute("update products set id=%s where id=%s",(newid,self.id))
        cur.execute("update dps set id=%s where id=%s",(newid,self.id))        
        cur.execute("update estimations_dps set id=%s where id=%s",(newid,self.id))        
        cur.execute("update estimations_eps set id=%s where id=%s",(newid,self.id))        
        cur.close()
        self.id=newid
        return self

class SetQuotes:
    """Clase que agrupa quotes un una lista arr. Util para operar con ellas como por ejemplo insertar, puede haber varios productos"""
    def __init__(self, mem):
        self.mem=mem
        self.arr=[]
    
    def print(self):
        for q in self.arr:
            print(" * {}".format(q))
    
    
    
    
    def save(self):
        """Recibe con code,  date,  time, value, zone
            Para poner el dato en close, el valor de time debe ser None
            Devuelve una tripleta (insertado,buscados,modificados)
        """
        insertados=SetQuotes(self.mem)
        ignored=SetQuotes(self.mem)
        modificados=SetQuotes(self.mem)    
        malos=SetQuotes(self.mem)
            
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

    def append(self, quote):
        self.arr.append(quote)        
        
    def length(self):
        return len(self.arr)
        
    def clear(self):
        del self.arr
        self.arr=[]
        
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
                
                
class SetQuotesAllIntradays:
    """Class that groups all quotes of the database. It's an array of SetQuotesIntraday"""
    def __init__(self, mem):
        self.mem=mem
        self.arr=[]
        self.product=None
        
    def first_quote(self):
        """Returns the first quote order by time"""
        if len(self.arr)!=0:
            return self.arr[0].open()
        return None
        
                
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
            if row['datetime']>dt_end:#Cambio de SetQuotesIntraday
                self.arr.append(SetQuotesIntraday(self.mem).init__create(self.product, dt_end.date(), intradayarr))
                dt_end=day_end(row['datetime'], self.product.stockmarket.zone)
                #crea otro intradayarr
                del intradayarr
                intradayarr=[]
                intradayarr.append(Quote(self.mem).init__db_row(row, self.product))
            else:
                intradayarr.append(Quote(self.mem).init__db_row(row, self.product))
        #No entraba si hay dos días en el primer día
        if len(intradayarr)!=0:
            self.arr.append(SetQuotesIntraday(self.mem).init__create(self.product, dt_end.date(), intradayarr))
            
#        print ("SetQuotesIntraday created: {0}".format(len(self.arr)))
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
        logging.critical("Quote not found in SetQuotesAllIntradays of {} at {}".format(self.product, dattime))
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
        
class SetQuotesBasic:
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

class SetQuotesIntraday(SetQuotes):
    """Clase que agrupa quotes un una lista arr de una misma inversión y de un mismo día. """
    def __init__(self, mem):
        SetQuotes.__init__(self, mem)
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
        logging.info("Quote not found in SetQuotesIntraday ({}) of {} at {}. En el set hay {}".format(self.date,  self.product, dt, self.arr))
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
#                print ("Purged", q)
                
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
                table.item(i, 1).setBackground(QColor(148, 255, 148))
            elif q==self.product.result.intradia.low():
                table.item(i, 1).setBackground( QColor(255, 148, 148))             
        table.setCurrentCell(self.length()-1, 0)
        table.clearSelection()

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
            self.datetime=string2datetime(a[3], 1)
            self.quote=Decimal(a[4])
        except:
            return None
        return self
        
class OHCL:
    def __init__(self,  mem):
        self.mem=mem
        self.product=None
        self.open=None
        self.close=None
        self.high=None
        self.low=None
        
    def get_interval(self, ohclposterior):
        """Calcula el intervalo entre dos ohcl. El posteror es el que se pasa como parámetro"""
        return ohclposterior.datetime-self.datetime

    def percentage(self, ohcl):
        """CAlcula el incremento en % en el cierre del ohcl actual y el pasado como parametro. Siendo el pasado como parametro posterior en el tiempo"""
        if ohcl:
            return Percentage(ohcl.close-self.close, self.close)            
        else:
            return Percentage()
        
class OHCLDuration:
    Day=1
    Week=2
    Month=3
    Year=4

    @classmethod
    def qcombobox(self, combo, selected_ohclduration):
        combo.addItem(QApplication.translate("Core", "Day"), 1)
        combo.addItem(QApplication.translate("Core", "Week"), 2)
        combo.addItem(QApplication.translate("Core", "Month"), 3)
        combo.addItem(QApplication.translate("Core", "Year"), 4)
        
        combo.setCurrentIndex(combo.findData(selected_ohclduration))
        
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
        datestart=dt(self.date,self.product.stockmarket.starts,self.product.stockmarket.zone)
        dateends=dt(self.date,self.product.stockmarket.closes,self.product.stockmarket.zone)
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
        
    def delete(self):
        """Removes all quotes of the selected day"""
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
        
        
    def delete(self):
        """Removes all quotes of the selected month and year"""
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
#        return d + dlt,  d + dlt + datetime.timedelta(days=6) ## first day, end day
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
    
    def delete(self):
        """Removes all quotes of the selected year"""
        cur=self.mem.con.cursor()
        cur.execute("delete from quotes where id=%s and date_part('year',datetime)=%s", (self.product.id, self.year))
        cur.close()     
                
class SetOHCL:
    def __init__(self, mem, product):
        self.mem=mem
        self.product=product
        self.arr=[]
        self.selected=None
    
    def load_from_db(self, sql):
        """El sql debe estar ordenado por date"""
        
        del self.arr
        self.arr=[]
        cur=self.mem.con.cursor()
        cur.execute(sql)#select * from ohclyearly where id=79329 order by date
        for row in cur:
            self.append(self.itemclass(self.mem).init__from_dbrow(row, self.product))
        cur.close()
        
#        
#    def percentage(self, index):
#        """CAlcula el incremento en % del index del array partiendo de index -1"""
#        try:
#            return Decimal(100)*(self.arr[index].close-self.arr[index-1].close)/self.arr[index-1].close
#        except:
#            return None
        
    def first(self):
        """Return first ohcl"""
        if self.length()>0:
            return self.arr[0]
        else:
            print ("There is no first item in SetOHCL")
            return None
        
    def last(self):
        """REturn last ohcl"""
        return self.arr[self.length()-1]
        
    def length(self):
        return len (self.arr)


    def append(self, o):
        self.arr.append(o)

    def closes(self, from_dt=None):
        """Returns a list with all the close of the array"""
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

class SetOHCLDaily(SetOHCL):
    def __init__(self, mem, product):
        SetOHCL.__init__(self, mem, product)
        self.itemclass=OHCLDaily

    def find(self, date):
        """Fucnción que busca un ohcldaily con fecha igual o menor de la pasada como parametro"""
        for ohcl in reversed(self.arr):
            if ohcl.date<=date:
                return ohcl
        return None



    def setquotesbasic(self):
        """Returns a SetQuotesBasic con los datos del setohcldairy"""
        last=None
        penultimate=None
        lastyear=None
        if self.length()==0:
            return SetQuotesBasic(self.mem, self.product).init__create(Quote(self.mem).none(self.product), Quote(self.mem).none(self.product),  Quote(self.mem).none(self.product))
        ohcl=self.arr[self.length()-1]#last
        last=Quote(self.mem).init__create(self.product, dt(ohcl.date, self.product.stockmarket.closes,  self.product.stockmarket.zone), ohcl.close)
        ohcl=self.find(ohcl.date-datetime.timedelta(days=1))#penultimate
        if ohcl!=None:
            penultimate=Quote(self.mem).init__create(self.product, dt(ohcl.date, self.product.stockmarket.closes,  self.product.stockmarket.zone), ohcl.close)
        ohcl=self.find(datetime.date(datetime.date.today().year-1, 12, 31))#lastyear
        if ohcl!=None:
            lastyear=Quote(self.mem).init__create(self.product, dt(ohcl.date, self.product.stockmarket.closes,  self.product.stockmarket.zone), ohcl.close)        
        return SetQuotesBasic(self.mem, self.product).init__create(last, penultimate, lastyear)

    def dates(self):
        """Returns a list with all the dates of the array"""
        r=[]
        for ohcl in self.arr:
            r.append(ohcl.date)
        return r
        

class SetOHCLWeekly(SetOHCL):
    def __init__(self, mem, product):
        SetOHCL.__init__(self, mem, product)
        self.itemclass=OHCLWeekly
        
class SetOHCLYearly(SetOHCL):
    def __init__(self, mem, product):
        SetOHCL.__init__(self, mem, product)
        self.itemclass=OHCLYearly
        

        
    def find(self, year):
        """Returns a OHCLYearly"""
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
        
class SetOHCLMonthly(SetOHCL):
    def __init__(self, mem, product):
        SetOHCL.__init__(self, mem, product)
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
        
    

class SetLanguages(SetCommons):
    def __init__(self, mem):
        SetCommons.__init__(self)
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
        if platform.system()=="Windows":
            self.mem.qtranslator.load("i18n/xulpymoney_{0}.qm".format(id))
        else:
            self.mem.qtranslator.load("/usr/lib/xulpymoney/xulpymoney_{0}.qm".format(id))
        logging.info("Language changed to {}".format(id))
        qApp.installTranslator(self.mem.qtranslator)
 
class HistoricalChartAdjusts:
    NoAdjusts=0
    Splits=1
    Dividends=2#Dividends with splits.
        
class QuotesResult:
    """Función que consigue resultados de mystocks de un id pasado en el constructor"""
    def __init__(self,mem,  product):
        self.mem=mem
        self.product=product
               
        self.intradiaBeforeSplits=SetQuotesIntraday(self.mem) #Despues del desarrollo deberán ser llamados BeforeSplits, ya que siempre se deberán usar BeforeSplits
        self.allBeforeSplits=SetQuotesAllIntradays(self.mem)
        self.basicBeforeSplits=SetQuotesBasic(self.mem, self.product)
        self.ohclDailyBeforeSplits=SetOHCLDaily(self.mem, self.product)
        self.ohclMonthlyBeforeSplits=SetOHCLMonthly(self.mem, self.product)
        self.ohclYearlyBeforeSplits=SetOHCLYearly(self.mem, self.product)
        self.ohclWeeklyBeforeSplit=SetOHCLWeekly(self.mem, self.product)
        
        
        self.intradia=SetQuotesIntraday(self.mem)
        self.all=SetQuotesAllIntradays(self.mem)
        self.basic=SetQuotesBasic(self.mem, self.product)
        self.ohclDaily=SetOHCLDaily(self.mem, self.product)
        self.ohclMonthly=SetOHCLMonthly(self.mem, self.product)
        self.ohclYearly=SetOHCLYearly(self.mem, self.product)
        self.ohclWeekly=SetOHCLWeekly(self.mem, self.product)

        
        self.intradiaAfterDividends=SetQuotesIntraday(self.mem) 
        self.allAfterDividends=SetQuotesAllIntradays(self.mem)
        self.basicAfterDividends=SetQuotesBasic(self.mem, self.product)
        self.ohclDailyAfterDividends=SetOHCLDaily(self.mem, self.product)
        self.ohclMonthlyAfterDividends=SetOHCLMonthly(self.mem, self.product)
        self.ohclYearlyAfterDividends=SetOHCLYearly(self.mem, self.product)
        self.ohclWeeklyAfterDividends=SetOHCLWeekly(self.mem, self.product)
        
        
        
    def load_dps_and_splits(self, force=False):
        """
            Only once. If it's already in memory. It ignore it
            force=True load from database again even if dps is not null
        """
        if self.product.dps==None or force==True:
            self.product.dps=SetDPS(self.mem, self.product)
            self.product.dps.load_from_db()     
        if self.product.splits==None or force==True:
            self.product.splits=SetSplits(self.mem, self.product)
            self.product.splits.init__from_db("select * from splits where products_id={} order by datetime".format(self.product.id))
        
    def get_basic_and_ohcls(self):
        """Tambien sirve para recargar"""
        inicioall=datetime.datetime.now()  
        self.load_dps_and_splits()
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
            self.ohclDaily=self.product.splits.adjustSetOHCLDaily(self.ohclDailyBeforeSplits)
        else:
            self.ohclDaily=self.ohclDailyBeforeSplits
        if self.product.dps.length()>0:
            self.ohclDailyAfterDividends=self.product.dps.adjustSetOHCLDaily(self.ohclDaily)
        else:
            self.ohclDailyAfterDividends=self.ohclDailyBeforeSplits
            
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
        
        self.basic=self.ohclDaily.setquotesbasic()
        print ("OHCL data of '{}' loaded: {}".format(self.product.name, datetime.datetime.now()-inicioall))
        

    def get_all(self):
        """Gets all in a set intradays form"""
        self.load_dps_and_splits()
        self.all.load_from_db(self.product)

    def ohcl(self,  ohclduration, historicalchartadjust=HistoricalChartAdjusts.NoAdjusts):
        """
            Returns the SetOHCL corresponding to it's duration
        """
        if ohclduration==OHCLDuration.Day:
            if historicalchartadjust==HistoricalChartAdjusts.Splits:
                return self.ohclDaily
            elif historicalchartadjust==HistoricalChartAdjusts.NoAdjusts:
                return self.ohclDailyBeforeSplits
            elif historicalchartadjust==HistoricalChartAdjusts.Dividends:
                return self.ohclDailyAfterDividends
        if ohclduration==OHCLDuration.Week:
            return self.ohclWeekly
        if ohclduration==OHCLDuration.Month:
            return self.ohclMonthly
        if ohclduration==OHCLDuration.Year:
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
        
        

class Priority:
    def __init__(self):
        self.id=None
        self.name=None
    def init__create(self, id, name):
        self.id=id
        self.name=name
        return self
        

class PriorityHistorical:
    def __init__(self):
        self.id=None
        self.name=None
    def init__create(self, id, name):
        self.id=id
        self.name=name
        return self

    
class Simulation:
    def __init__(self,mem, original_db):
        """Types are defined in combo ui wdgSimulationsADd
        database is the database which data is going to be simulated"""
        self.mem=mem
        self.database=original_db
        self.id=None
        self.name=None#self.simulated_db, used to reuse SetCommons
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

#class SimulationTools:
#    def __init__(self, mem, con_sim):
#        self.mem=mem
#        self.con_mem=self.mem.con
#        self.con_sim=con_sim
#        
#    def accounts_insert(self, sql):
#        cur_mem=self.con_mem.cursor()
#        cur_mem.execute(sql)
#        for row in cur_mem:
#            
        
    

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

class SetSplits(SetCommons):
    def __init__(self, mem, product):
        SetCommons.__init__(self)
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

    def adjustSetOHCLDaily(self, set):
        r=SetOHCLDaily(self.mem, self.product)
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
        self.quotes=SetQuotesAllIntradays(self.mem)
        self.quotes.load_from_db(self.product)
        for setquoteintraday in self.quotes.arr:
            for q in setquoteintraday.arr:
                if self.dtinitial<=q.datetime and self.dtfinal>=q.datetime:
                    q.quote=self.convertPrices(q.quote)
                    q.save()
                    
    def updateDPS(self):
        set=SetDPS(self.mem, self.product)
        set.load_from_db()
        for d in set.arr:
            if self.dtinitial.date()<=d.date and self.dtfinal.date()>=d.date:
                d.gross=self.convertPrices(d.gross)
                d.save()
        
    def updateEPS(self):
        pass
        
    def updateEstimationsDPS(self):
        set=SetEstimationsDPS(self.mem, self.product)
        set.load_from_db()
        for d in set.arr:
            if self.dtinitial.year<=d.year and self.dtfinal.year>=d.year:
                d.estimation=self.convertPrices(d.estimation)
                d.save()
        
    def updateEstimationsEPS(self):
        set=SetEstimationsEPS(self.mem, self.product)
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
                        oi.acciones=self.convertShares(oi.acciones)
                        oi.valor_accion=self.convertPrices(oi.valor_accion)
                        oi.save(autocommit=False)

        
    def updateDividends(self):
        """Transforms de dpa of an array of dividends"""
        for inv in self.mem.data.investments.arr:
            if inv.product.id==self.product.id:
                dividends=SetDividendsHomogeneus(self.mem, inv)
                dividends.load_from_db("select * from dividends where id_inversiones={0} order by fecha".format(inv.id ))  
                for d in dividends.arr:
                    if self.dtinitial<=d.fecha and self.dtfinal>=d.fecha:
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
#        self.updateEPS() #NOT YET
        self.updateEstimationsDPS()
        self.updateEstimationsEPS()
        self.updateOperInvestments()
        self.updateDividends()
        self.updateQuotes()
        self.mem.con.commit()
        
#class TUpdateData(threading.Thread):
#    """Hilo que actualiza las products, solo el getBasic, cualquier cambio no de last, deberá ser desarrollado por código"""
#    def __init__(self, mem):
#        threading.Thread.__init__(self)
#        self.mem=mem
#        
#    def run(self):
#        print ("TUpdateData started")
#        while True:
#            inicio=datetime.datetime.now()
#                            
#            self.mem.data.benchmark.result.basic.load_from_db()
#            
#            ##Update loop
#            for inv in self.mem.data.products.arr:
#                if self.mem.closing==True:
#                    return
#                inv.result.basic.load_from_db()
#            print("TUpdateData loop took", datetime.datetime.now()-inicio)
#            
#            ##Wait loop
#            for i in range(60):
#                if self.mem.closing==True:
#                    return
#                time.sleep(1)

class ProductType:
    def __init__(self):
        self.id=None
        self.name=None
    def init__create(self, id, name):
        self.id=id
        self.name=name
        return self

class Agrupation:
    """Una inversión pertenece a una lista de agrupaciones ibex, indices europeos
    fondo europeo, fondo barclays. Hat tantas agrupaciones como clasificaciones . grupos en kaddressbook similar"""
    def __init__(self,  mem):
        self.mem=mem
        self.id=None
        self.name=None
        self.type=None
        self.stockmarket=None

        
    def init__create(self, id,  name, type, bolsa):
        self.id=id
        self.name=name
        self.type=type
        self.stockmarket=bolsa
        return self
        
        
class eProductType(IntEnum):
    """
        IntEnum permite comparar 1 to eProductType.Share
    """
    Share=1
    Fund=2
    Index=3
    ETF=4
    Warrant=5
    Currency=6
    PublicBond=7
    PensionPlan=8
    PrivateBond=9
    Deposit=10
    Account=11
    
class eTickerPosition(IntEnum):
    """It's the number to access to a python list,  not to postgresql. In postgres it will be +1"""
    Yahoo=0
    Morningstar=1
    Google=2
    QueFondos=3
    
    def postgresql(etickerposition):
        return etickerposition.value+1
    
class SetTypes(SetCommons):
    def __init__(self, mem):
        SetCommons.__init__(self)
        self.mem=mem

    def load_all(self):
        self.append(ProductType().init__create(eProductType.Share.value,QApplication.translate("Core","Shares")))
        self.append(ProductType().init__create(eProductType.Fund.value,QApplication.translate("Core","Funds")))
        self.append(ProductType().init__create(eProductType.Index.value,QApplication.translate("Core","Indexes")))
        self.append(ProductType().init__create(eProductType.ETF.value,QApplication.translate("Core","ETF")))
        self.append(ProductType().init__create(eProductType.Warrant.value,QApplication.translate("Core","Warrants")))
        self.append(ProductType().init__create(eProductType.Currency.value,QApplication.translate("Core","Currencies")))
        self.append(ProductType().init__create(eProductType.PublicBond.value,QApplication.translate("Core","Public Bond")))
        self.append(ProductType().init__create(eProductType.PensionPlan.value,QApplication.translate("Core","Pension plans")))
        self.append(ProductType().init__create(eProductType.PrivateBond.value,QApplication.translate("Core","Private Bond")))
        self.append(ProductType().init__create(eProductType.Deposit.value,QApplication.translate("Core","Deposit")))
        self.append(ProductType().init__create(eProductType.Account.value,QApplication.translate("Core","Accounts")))

    def investment_types(self):
        """Returns a SetTypes without Indexes and Accounts"""
        r=SetTypes(self.mem)
        for t in self.arr:
            if t.id not in (eProductType.Index, eProductType.Account):
                r.append(t)
        return r

    def with_operation_comissions_types(self):
        """Returns a SetTypes with types which product operations  has comissions"""
        r=SetTypes(self.mem)
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
        datet=dt(date, time(22, 00), self.mem.localzone)
        sumbalance=0
        print ("{0:<40s} {1:>15s} {2:>15s} {3:>15s}".format("Investments at {0}".format(date), "Shares", "Price", "Balance"))
        for inv in self.mem.data.investments.arr:
            balance=inv.balance(date)
            sumbalance=sumbalance+balance
            acciones=inv.acciones(date)
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
        self.countries=SetCountries(self)
        self.countries.load_all()
        self.languages=SetLanguages(self)
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
        
        self.currencies=SetCurrencies(self)
        self.currencies.load_all()
        self.localcurrency=self.currencies.find_by_id(self.settingsdb.value("mem/localcurrency", "EUR"))
        
        self.investmentsmodes=SetProductsModes(self)
        self.investmentsmodes.load_all()
        
        self.simulationtypes=SetSimulationTypes(self)
        self.simulationtypes.load_all()
        
        self.zones=SetZones(self)
        self.zones.load_all()
        self.localzone=self.zones.find_by_name(self.settingsdb.value("mem/localzone", "Europe/Madrid"))
        
        self.tiposoperaciones=SetOperationTypes(self)
        self.tiposoperaciones.load()
        
        self.conceptos=SetConcepts(self)
        self.conceptos.load_from_db()
                
        self.priorities=SetPriorities(self)
        self.priorities.load_all()
        
        self.prioritieshistorical=SetPrioritiesHistorical(self)
        self.prioritieshistorical.load_all()

        self.types=SetTypes(self)
        self.types.load_all()
        
        self.stockmarkets=SetStockMarkets(self)
        self.stockmarkets.load_all_from_db()
        
        self.agrupations=SetAgrupations(self)
        self.agrupations.load_all()

        self.leverages=SetLeverages(self)
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

class Country:
    def __init__(self):
        self.id=None
        self.name=None
        
    def init__create(self, id, name):
        self.id=id
        self.name=name
        return self
            
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
            

class Zone:
    def __init__(self, mem):
        self.mem=mem
        self.id=None
        self.name=None
        self.country=None
        
    def init__create(self, id, name, country):
        self.id=id
        self.name=name
        self.country=country
        return self
        
    def timezone(self):
        return pytz.timezone(self.name)
        
    def now(self):
        return datetime.datetime.now(pytz.timezone(self.name))
        
    def __repr__(self):
        return "Zone ({}): {}".format(str(self.id), str(self.name))
        
class SetZones(SetCommons):
    def __init__(self, mem):
        SetCommons.__init__(self)
        self.mem=mem
        
    def load_all(self):
        self.append(Zone(self.mem).init__create(1,'Europe/Madrid', self.mem.countries.find_by_id("es")))#ALGUN DIA HABRá QUE CAMBIAR LAS ZONES POR ID_ZONESº
        self.append(Zone(self.mem).init__create(2,'Europe/Lisbon', self.mem.countries.find_by_id("pt")))
        self.append(Zone(self.mem).init__create(3,'Europe/Rome', self.mem.countries.find_by_id("it")))
        self.append(Zone(self.mem).init__create(4,'Europe/London', self.mem.countries.find_by_id("en")))
        self.append(Zone(self.mem).init__create(5,'Asia/Tokyo', self.mem.countries.find_by_id("jp")))
        self.append(Zone(self.mem).init__create(6,'Europe/Berlin', self.mem.countries.find_by_id("de")))
        self.append(Zone(self.mem).init__create(7,'America/New_York', self.mem.countries.find_by_id("us")))
        self.append(Zone(self.mem).init__create(8,'Europe/Paris', self.mem.countries.find_by_id("fr")))
        self.append(Zone(self.mem).init__create(9,'Asia/Hong_Kong', self.mem.countries.find_by_id("cn")))
        self.append(Zone(self.mem).init__create(10,'UTC', self.mem.countries.find_by_id("es")))

    def qcombobox(self, combo, zone=None):
        """Carga entidades bancarias en combo"""
        combo.clear()
        for a in self.arr:
            combo.addItem(a.country.qicon(), a.name, a.id)

        if zone!=None:
            combo.setCurrentIndex(combo.findText(zone.name))

            
    def find_by_name(self, name,  log=False):
        """self.find_by_id() search by id (number).
        This function replaces  it and searches by name (Europe/Madrid)"""
        for a in self.arr:
            if a.name==name:
                return a
        if log:
            print ("SetCommons ({}) fails finding {}".format(self.__class__.__name__, name))
        return None

class AssetsReport(ODT):
    def __init__(self, mem, filename, template):
        ODT.__init__(self, filename, template)
        self.mem=mem
        self.dir=None#Directory in tmp
        
    def tr (self, s):
        return QApplication.translate("Core", s)
        
    def generate(self):
        self.dir='/tmp/AssetsReport-{}'.format(datetime.datetime.now())
        makedirs(self.dir)
        self.setMetadata( self.tr("Assets report"),  self.tr("This is an automatic generated report from Xulpymoney"), "Xulpymoney-{}".format(version))
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
        self.simpleParagraph(self.tr("Generated by Xulpymoney-{}".format(version)), "Subtitle")
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
        self.table( [self.tr("Bank"), self.tr("Balance")], ["<", ">"], data, [3, 2], 12)       
        self.simpleParagraph(self.tr("Sum of all bank balances is {}").format(sumbalances))
        
        self.pageBreak(True)
        ### Assests current year
        self.header(self.tr("Assets current year evolution"), 2)
        
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
                            ["<", ">", ">", ">", ">", ">", ">", ">", ">", ">", ">", ">", ">", ">"], data, [3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2], 7)       
                
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
        self.table( [self.tr("Account"), self.tr("Bank"),  self.tr("Balance")], ["<","<",  ">"], data, [5,5, 2], 11)       
        
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

        self.table( [self.tr("Investment"), self.tr("Balance"), self.tr("Gains"), self.tr("% Invested"), self.tr("% Selling point")], ["<", ">", ">", ">", ">"], data, [3, 1, 1, 1,1], 9)       
        
        suminvertido=self.mem.data.investments_active().invested()
        sumpendiente=self.mem.data.investments_active().pendiente()
        if suminvertido.isZero()==False:
            self.simpleParagraph(self.tr("Sum of all invested assets is {}.").format(suminvertido))
            self.simpleParagraph(self.tr("Investment gains (positive minus negative results): {} - {} are {}, what represents a {} of total assets.").format(self.mem.data.investments_active().pendiente_positivo(), self.mem.data.investments_active().pendiente_negativo(), sumpendiente, Percentage(sumpendiente, suminvertido)))
            self.simpleParagraph(self.tr(" Assets average age: {}").format(  days_to_year_month(self.mem.data.investments_active().average_age())))
        else:
            self.simpleParagraph(self.tr("There aren't invested assets"))
        self.pageBreak()
        
        
        
        ### Graphics wdgInvestments clases
        self.mem.frmMain.setGeometry(10, 10, 800, 800)
        self.mem.frmMain.w.close()
        self.mem.frmMain.w=wdgInvestmentClasses(self.mem, self.mem.frmMain)
        self.mem.frmMain.layout.addWidget(self.mem.frmMain.w)
        self.mem.frmMain.w.show()
        self.mem.frmMain.w.tab.setCurrentIndex(0)
        self.mem.frmMain.w.viewTPC.chart.setAnimationOptions(QChart.NoAnimation)
        self.mem.frmMain.w.update(animations=False)
        
#        wit=15
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
        
        


## FUNCTIONS #############################################
        
def ampm2stringtime(s, type):
    """
        s is a string for time with AMPM and returns a 24 hours time string with zfill
        type is the diferent formats id
    """
    s=s.upper()
    if type==1:#5:35PM > 17:35   ó 5:35AM > 05:35
        s=s.replace("AM", "")
        if s.find("PM"):
            s=s.replace("PM", "")
            points=s.split(":")
            s=str(int(points[0])+12).zfill(2)+":"+points[1]
        else:#AM
            points=s.split(":")
            s=str(int(points[0])).zfill(2)+":"+points[1]
        return s
        
def dt_changes_tz(dt,  tztarjet):
    """Cambia el zoneinfo del dt a tztarjet. El dt del parametre tiene un zoneinfo"""
    if dt==None:
        return None
    tzt=pytz.timezone(tztarjet.name)
    tarjet=tzt.normalize(dt.astimezone(tzt))
    return tarjet

        
def dt_changes_tz_with_pytz(dt,  tzname):
    """Cambia el zoneinfo del dt a tztarjet. El dt del parametre tiene un zoneinfo"""
    if dt==None:
        return None
    tzt=pytz.timezone(tzname)
    tarjet=tzt.normalize(dt.astimezone(tzt))
    return tarjet



def status_insert(cur,  source,  process):
        cur.execute('insert into status (source, process) values (%s,%s);', (source,  process))

def status_update(cur, source,  process, status=None,  statuschange=None,  internets=None ):
    updates=''
    d={ 'status'            : status, 
            'statuschange': statuschange,
            'internets'      : internets}
    for arg in d:
        if arg in ['status', 'statuschange'] and d[arg]!=None:
            updates=updates+' '+arg+ "='"+str(d[arg])+"', "
        elif arg in ['internets'] and d[arg]!=None:
            updates=updates+' '+arg+ "="+str(d[arg])+", "
    if updates=='':
        print ('status_update: parámetros vacios')
        return
    sql="update status set "+updates[:-2]+" where process='"+process+"' and source='"+source+"'"
    cur.execute(sql)


def qdate(date):
    """Return a QTableWidgetItem with the date"""
    return qcenter(str(date))


def qmessagebox(text):
    m=QMessageBox()
    m.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
    m.setIcon(QMessageBox.Information)
    m.setText(text)
    m.exec_()   
    
def dtaware2utc(dtaware):
    """
date -u -R
Tue, 14 Feb 2017 20:11:04 +0000
 date  -R
Tue, 14 Feb 2017 21:11:08 +0100
"""
    pass


def sync_data(con_source, con_target, progress=None):
    """con is con_target, 
    progress is a pointer to progressbar
    returns a tuple (numberofproductssynced, numberofquotessynced)"""
    #Checks if database has same version
    cur_target=con_target.cursor()
    cur2_target=con_target.cursor()
    cur_source=con_source.cursor()
    
    
    #Checks if database has same version
    cur_source.execute("select value from globals where id_globals=1")
    cur_target.execute("select value from globals where id_globals=1")
    
    if cur_source.fetchone()[0]!=cur_target.fetchone()[0]:
        logging.critical ("Databases has diferent versions, please update them")
        sys.exit(0)
    
    quotes=0#Number of quotes synced
    estimation_dps=0#Number of estimation_dps synced
    estimation_eps=0#Number of estimation_eps synced
    dps=0
    products=0#Number of products synced
    
    #Iterate all products
    cur_target.execute("select id,name from products where id>0 order by name;")
    logging.info ("Syncing {} products".format (cur_target.rowcount))
    for row in cur_target:
        output="{}: ".format(row['name'])
        ## QUOTES #####################################################################
        #Search last datetime
        cur2_target.execute("select max(datetime) as max from quotes where id=%s", (row['id'], ))
        max=cur2_target.fetchone()[0]
        #Ask for quotes in source with last datetime
        if max==None:#No hay ningun registro y selecciona todos
            cur_source.execute("select * from quotes where id=%s", (row['id'], ))
        else:#Hay registro y selecciona los posteriores a el
            cur_source.execute("select * from quotes where id=%s and datetime>%s", (row['id'], max))
        if cur_source.rowcount!=0:
            print("  - Syncing {} since {} ".format(row['name'], max),end="")
            for  row_source in cur_source: #Inserts them 
                cur2_target.execute("insert into quotes (id, datetime, quote) values (%s,%s,%s)", ( row_source['id'], row_source['datetime'], row_source['quote']))
                quotes=quotes+1
                output=output+"."
                
        ## DPS ################################################################################
        #Search last datetime
        cur2_target.execute("select max(date) as max from dps where id=%s", (row['id'], ))
        max=cur2_target.fetchone()[0]
        #Ask for quotes in source with last datetime
        if max==None:#No hay ningun registro y selecciona todos
            cur_source.execute("select * from dps where id=%s", (row['id'], ))
        else:#Hay registro y selecciona los posteriores a el
            cur_source.execute("select * from dps where id=%s and date>%s", (row['id'], max))
        if cur_source.rowcount!=0:
            for  row_source in cur_source: #Inserts them 
                cur2_target.execute("insert into dps (date, gross, id) values (%s,%s,%s)", ( row_source['date'], row_source['gross'], row_source['id']))
                dps=dps+1
                output=output+"-"

        ## DPS ESTIMATIONS #####################################################################
        #Search last datetime
        cur2_target.execute("select max(year) as max from estimations_dps where id=%s", (row['id'], ))
        max=cur2_target.fetchone()[0]
        #Ask for quotes in source with last datetime
        if max==None:#No hay ningun registro y selecciona todos
            cur_source.execute("select * from estimations_dps where id=%s", (row['id'], ))
        else:#Hay registro y selecciona los posteriores a el
            cur_source.execute("select * from estimations_dps where id=%s and year>%s", (row['id'], max))
        if cur_source.rowcount!=0:
            for  row_source in cur_source: #Inserts them 
                cur2_target.execute("insert into estimations_dps (year, estimation, date_estimation, source, manual, id) values (%s,%s,%s,%s,%s,%s)", ( row_source['year'], row_source['estimation'], row_source['date_estimation'], row_source['source'], row_source['manual'],  row_source['id']))
                estimation_dps=estimation_dps+1
                output=output+"+"
                
        ## EPS ESTIMATIONS #####################################################################
        #Search last datetime
        cur2_target.execute("select max(year) as max from estimations_eps where id=%s", (row['id'], ))
        max=cur2_target.fetchone()[0]
        #Ask for quotes in source with last datetime
        if max==None:#No hay ningun registro y selecciona todos
            cur_source.execute("select * from estimations_eps where id=%s", (row['id'], ))
        else:#Hay registro y selecciona los posteriores a el
            cur_source.execute("select * from estimations_eps where id=%s and year>%s", (row['id'], max))
        if cur_source.rowcount!=0:
            for  row_source in cur_source: #Inserts them 
                cur2_target.execute("insert into estimations_eps (year, estimation, date_estimation, source, manual, id) values (%s,%s,%s,%s,%s,%s)", ( row_source['year'], row_source['estimation'], row_source['date_estimation'], row_source['source'], row_source['manual'],  row_source['id']))
                estimation_eps=estimation_eps+1
                output=output+"*"
                
        if output!="{}: ".format(row['name']):
            products=products+1
            logging.info(output)
            
        if progress!=None:#If there's a progress bar
            progress.setValue(cur_target.rownumber)
            progress.setMaximum(cur_target.rowcount)
            QCoreApplication.processEvents()
    con_target.commit()
    print("")
    
    if progress!=None:
        s=QCoreApplication.translate("Core", """From {} desynchronized products added:
    - {} quotes
    - {} dividends per share
    - {} dividend per share estimations
    - {} earnings per share estimations""").format(  products,  quotes, dps, estimation_dps,  estimation_eps)
            
        qmessagebox(s)  


def utc2dtaware(dt, utfoffset):
    pass
    
def aware2epochms(d):
    """
        Puede ser dateime o date
        Si viene con zona datetime zone aware, se convierte a UTC y se da el valor en UTC
        return datetime.datetime.now(pytz.timezone(self.name))
    """
#    if d.__class__==datetime.date:
#        return (datetime.datetime(d.year, d.month, d.day, 23, 59, 59, 999999)-datetime.datetime(1970, 1, 1, 0, 0)).total_seconds()*1000
    if d.__class__==datetime.datetime:
        if d.tzname()==None:#unaware datetine
#            return (d-datetime.datetime(1970, 1, 1, 0, 0)).total_seconds()*1000
            logging.critical("Must be aware")
        else:#aware dateime changed to unawar
#            return (dt_changes_tz(d, Zone(10, "UTC", "es")).replace(tzinfo=None)-datetime.datetime(1970, 1, 1, 0, 0)).total_seconds()*1000
            utc=dt_changes_tz_with_pytz(d, 'UTC')
            return utc.timestamp()*1000
    logging.critical("{} can't be converted to epochms".format(d.__class__))
    
def epochms2aware(n):
    """Return a UTC date"""
    utc_unaware=datetime.datetime.utcfromtimestamp(n/1000)
    utc_aware=utc_unaware.replace(tzinfo=pytz.timezone('UTC'))
    return utc_aware

    
    
def datetime_string(dt, zone):
    if dt==None:
        resultado="None"
    else:    
        
        #print (dt,  dt.__class__,  dt.tzinfo, dt.tzname())
        if dt.tzname()==None:
            logging.critical("Datetime should have tzname")
            sys.exit(178)   
        dt=dt_changes_tz(dt,  zone)
        if dt.microsecond==4 :
            resultado="{}-{}-{}".format(dt.year, str(dt.month).zfill(2), str(dt.day).zfill(2))
        else:
            resultado="{}-{}-{} {}:{}:{}".format(dt.year, str(dt.month).zfill(2), str(dt.day).zfill(2), str(dt.hour).zfill(2), str(dt.minute).zfill(2),  str(dt.second).zfill(2))
    return resultado
    
def qdatetime(dt, zone):
    """
        dt es un datetime con timezone, que se mostrara con la zone pasado como parametro
        Convierte un datetime a string, teniendo en cuenta los microsehgundos, para ello se convierte a datetime local
    """
    a=QTableWidgetItem(datetime_string(dt, zone))
    if dt==None:
        a.setForeground(QColor(0, 0, 255))
    a.setTextAlignment(Qt.AlignVCenter|Qt.AlignRight)
    return a

def qtime(dt):
    """
        Shows the time of a datetime
    """
    if dt.microsecond==5:
        item=qleft(str(dt)[11:-13])
        item.setBackground(QColor(255, 255, 148))
    elif dt.microsecond==4:
        item=qleft(str(dt)[11:-13])
        item.setBackground(QColor(148, 148, 148))
    else:
        item=qleft(str(dt)[11:-6])
    return item
    
def list2string(lista):
        """Covierte lista a string"""
        if  len(lista)==0:
            return ""
        if str(lista[0].__class__) in ["<class 'int'>", "<class 'float'>"]:
            resultado=""
            for l in lista:
                resultado=resultado+ str(l) + ", "
            return resultado[:-2]
        elif str(lista[0].__class__) in ["<class 'str'>",]:
            resultado=""
            for l in lista:
                resultado=resultado+ "'" + str(l) + "', "
            return resultado[:-2]
            
def string2list(s):
    """Convers a string of integer separated by comma, into a list of integer"""
    arr=[]
    if s!="":
        arrs=s.split(",")
        for a in arrs:
            arr.append(int(a))
    return arr
    
def string2date(iso, type=1):
    """
        date string to date, with type formats
    """
    if type==1: #YYYY-MM-DD
        d=iso.split("-")
        return datetime.date(int(d[0]), int(d[1]),  int(d[2]))
    if type==2: #DD/MM/YYYY
        d=iso.split("/")
        return datetime.date(int(d[2]), int(d[1]),  int(d[0]))

        
def string2datetime(s, type, zone="Europe/Madrid"):
    """
        s is a string for datetime
        type is the diferent formats id
    """
    if type==1:#2017-11-20 23:00:00+00:00  ==> Aware
        s=s[:-3]+s[-2:]
        dat=datetime.datetime.strptime( s, "%Y-%m-%d %H:%M:%S%z" )
        return dat
    if type==2:#20/11/2017 23:00 ==> Naive
        dat=datetime.datetime.strptime( s, "%d/%m/%Y %H:%M" )
        return dat
    if type==3:#20/11/2017 23:00 ==> Aware, using zone parameter
        dat=datetime.datetime.strptime( s, "%d/%m/%Y %H:%M" )
        z=pytz.timezone(zone)
        return z.localize(dat)
    if type==4:#27 1 16:54 2017==> Aware, using zone parameter . 1 es el mes convertido con month2int
        dat=datetime.datetime.strptime( s, "%d %m %H:%M %Y")
        z=pytz.timezone(zone)
        return z.localize(dat)
def log(tipo, funcion,  mensaje):
    """Tipo es una letra mayuscula S sistema H historico D diario"""
    if funcion!="":
        funcion= funcion + " "
    f=codecs.open("/tmp/mystocks.log",  "a", "utf-8-sig")
    message=str(datetime.datetime.now())[:-7]+" "+ tipo +" " + funcion + mensaje + "\n"
    printmessage=str(datetime.datetime.now())[:-7]+" "+ Color().green(tipo) + " "+ funcion +  mensaje + "\n"
    f.write(message)
    print (printmessage[:-1])
    f.close()

def b2s(b, code='UTF-8'):
    """Bytes 2 string"""
    return b.decode(code)
    
def s2b(s, code='UTF8'):
    """String 2 bytes"""
    if s==None:
        return "".encode(code)
    else:
        return s.encode(code)



def c2b(state):
    """QCheckstate to python bool"""
    if state==Qt.Checked:
        return True
    else:
        return False

def b2c(booleano):
    """Bool to QCheckstate"""
    if booleano==True:
        return Qt.Checked
    else:
        return Qt.Unchecked     

def day_end(dattime, zone):
    """Saca cuando acaba el dia de un dattime en una zona concreta"""
    return dt_changes_tz(dattime, zone).replace(hour=23, minute=59, second=59)
    
def day_start(dattime, zone):
    return dt_changes_tz(dattime, zone).replace(hour=0, minute=0, second=0)
    
def day_end_from_date(date, zone):
    """Saca cuando acaba el dia de un dattime en una zona concreta"""
    return dt(date, datetime.time(23, 59, 59), zone)
    
def day_start_from_date(date, zone):
    return dt(date, datetime.time(0, 0, 0), zone)
    
def month_start(year, month, zone):
    """datetime primero de un mes
    """
    return day_start_from_date(datetime.date(year, month, 1), zone)
    
def month2int(s):
    """
        Converts a month string to a int
    """
    if s in ["Jan", "Ene", "Enero", "January", "enero", "january"]:
        return 1
    if s in ["Feb", "Febrero", "February", "febrero", "february"]:
        return 2
    if s in ["Mar", "Marzo", "March", "marzo", "march"]:
        return 3
    if s in ["Apr", "Abr", "April", "Abril", "abril", "april"]:
        return 4
    if s in ["May", "Mayo", "mayo", "may"]:
        return 5
    if s in ["Jun", "June", "Junio", "junio", "june"]:
        return 6
    if s in ["Jul", "July", "Julio", "julio", "july"]:
        return 7
    if s in ["Aug", "Ago", "August", "Agosto", "agosto", "august"]:
        return 8
    if s in ["Sep", "Septiembre", "September", "septiembre", "september"]:
        return 9
    if s in ["Oct", "October", "Octubre", "octubre", "october"]:
        return 10
    if s in ["Nov", "Noviembre", "November", "noviembre", "november"]:
        return 11
    if s in ["Dic", "Dec", "Diciembre", "December", "diciembre", "december"]:
        return 12

def month_end(year, month, zone):
    """datetime último de un mes
    """
    return day_end_from_date(month_last_date(year, month), zone)
    
def month_last_date(year, month):
    """
        Returns a date with the last day of a month
    """
    if month == 12:
        return datetime.date(year, month, 31)
    return datetime.date(year, month+1, 1) - datetime.timedelta(days=1)
    
    

def year_start(year, zone):
    """
        returns an aware datetime with the start of year
    """
    return day_start_from_date(datetime.date(year, 1, 1), zone)
    

def year_end(year, zone):
    """
        returns an aware datetime with the last of year
    """
    return day_end_from_date(datetime.date(year, 12, 31), zone)
    

    
def days_to_year_month(days):
    years=days//365
    months=(days-years*365)//30
    days=int(days -years*365 -months*30)
    if years==1:
        stryears=QApplication.translate("Core", "year")
    else:
        stryears=QApplication.translate("Core", "years")
    if months==1:
        strmonths=QApplication.translate("Core", "month")
    else:
        strmonths=QApplication.translate("Core", "months")
    if days==1:
        strdays=QApplication.translate("Core", "day")
    else:
        strdays=QApplication.translate("Core", "days")
    return QApplication.translate("Core", "{} {}, {} {} and {} {}").format(years, stryears,  months,  strmonths, days,  strdays)


def dt(date, hour, zone):
    """Función que devuleve un datetime con zone info.
    Zone is an object."""
    z=pytz.timezone(zone.name)
    a=datetime.datetime(date.year,  date.month,  date.day,  hour.hour,  hour.minute,  hour.second, hour.microsecond)
    a=z.localize(a)
    return a
def dt_with_pytz(date, hour, zonename):
    """Función que devuleve un datetime con zone info.
    Zone is an object."""
    z=pytz.timezone(zonename)
    a=datetime.datetime(date.year,  date.month,  date.day,  hour.hour,  hour.minute,  hour.second, hour.microsecond)
    a=z.localize(a)
#    logging.debug("{} {} {} => {}".format(date, hour, zonename, a))
    return a
    
def str2bool(s):
    """Converts strings True or False to boolean"""
    if s=="True":
        return True
    return False
    
def none2decimal0(s):
    if s==None:
        return Decimal('0')
    return s
    


def qbool(bool):
    """Prints bool and check. Is read only and enabled"""
    a=QTableWidgetItem()
    a.setFlags( Qt.ItemIsSelectable |  Qt.ItemIsEnabled )#Set no editable
    if bool:
        a.setCheckState(Qt.Checked);
        a.setText(QApplication.translate("Core","True"))
    else:
        a.setCheckState(Qt.Unchecked);
        a.setText(QApplication.translate("Core","False"))
    a.setTextAlignment(Qt.AlignVCenter|Qt.AlignCenter)
    return a
    
def wdgBool(bool):
    """Center checkbox
    Yo must use with table.setCellWidget(0,0,wdgBool)
    Is disabled to be readonly"""
    pWidget = QWidget()
    pCheckBox = QCheckBox();
    if bool:
        pCheckBox.setCheckState(Qt.Checked);
    else:
        pCheckBox.setCheckState(Qt.Unchecked);
    pLayout = QHBoxLayout(pWidget);
    pLayout.addWidget(pCheckBox);
    pLayout.setAlignment(Qt.AlignCenter);
    pLayout.setContentsMargins(0,0,0,0);
    pWidget.setLayout(pLayout);
    pCheckBox.setEnabled(False)
    return pWidget
    

def qcenter(string, digits=None):
    a=QTableWidgetItem(str(string))
    a.setTextAlignment(Qt.AlignVCenter|Qt.AlignCenter)
    return a
    
def qleft(string):
    a=QTableWidgetItem(str(string))
    a.setTextAlignment(Qt.AlignVCenter|Qt.AlignLeft)
    return a

    
def qright(string, digits=None):
    """When digits, limits the number to """
    if string!=None and digits!=None:
        string=round(string, digits)
    a=QTableWidgetItem(str(string))
    a.setTextAlignment(Qt.AlignVCenter|Qt.AlignRight)
    try:#If is a number corized it
        if string==None:
            a.setForeground(QColor(0, 0, 255))
        elif string<0:
            a.setForeground(QColor(255, 0, 0))
    except:
        pass
    return a

#def qtpc(n, rnd=2):
#    print("qtpc deprecated")
#    text= tpc(n, rnd)
#    a=QTableWidgetItem(text)
#    a.setTextAlignment(Qt.AlignVCenter|Qt.AlignRight)
#    if n==None:
#        a.setForeground(QColor(0, 0, 255))
#    elif n<0:
#        a.setForeground(QColor(255, 0, 0))
#    return a
#      
#def QApplication.translate("Core",s):
#    return QApplication.translate("Core",  s)
#    

#
#def tpc(n, rnd=2):
#    print("tpc deprecated")
#    if n==None:
#        return "None %"
#    return str(round(n, rnd))+ " %"

        
def web2utf8(cadena):
    cadena=cadena.replace('&#209;','Ñ')
    cadena=cadena.replace('&#241;','ñ')
    cadena=cadena.replace('&#252;','ü')
    cadena=cadena.replace('&#246;','ö')
    cadena=cadena.replace('&#233;','é')
    cadena=cadena.replace('&#228;','ä')
    cadena=cadena.replace('&#214;','Ö')
    cadena=cadena.replace('&amp;','&')
    cadena=cadena.replace('&AMP;','&')
    cadena=cadena.replace('&Ntilde;','Ñ')
    
    return cadena
    
def function_name(clas):
#    print (inspect.stack()[0][0].f_code.co_name)
#    print (inspect.stack()[0][3],  inspect.stack())
#    print (inspect.stack()[1][3],  inspect.stack())
#    print (clas.__class__.__name__)
#    print (clas.__module__)
    return "{0}.{1}".format(clas.__class__.__name__,inspect.stack()[1][3])

from wdgTotal import TotalYear
from wdgInvestmentClasses import wdgInvestmentClasses
