from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import datetime
import time
import io
import pytz
import psycopg2
import psycopg2.extras
import sys,  codecs,   inspect,  threading, argparse, getpass

from decimal import *

version="0.1"
version_date=datetime.date(2015,3,1)
class Connection:
    """Futuro conection object"""
    def __init__(self):
        self.user=None
        self.password=None
        self.server=None
        self.port=None
        self.db=None
        self._con=None
        self.active=False
        
        self.init=None
        
    def init__create(self, user, password, server, port, db):
        self.user=user
        self.password=password
        self.server=server
        self.port=port
        self.db=db
        return self
        
    def cursor(self):
        return self._con.cursor()
        
    
    def mogrify(self, sql, arr):
        """Mogrify text"""
        cur=self._con.cursor()
        s=cur.mogrify(sql, arr)
        cur.close()
        return  s
        
    def cursor_one_row(self, sql, arr=[]):
        """Returns only one row"""
        cur=self._con.cursor()
        cur.execute(sql, arr)
        row=cur.fetchone()
        cur.close()
        return row        
        
    def cursor_one_column(self, sql, arr=[]):
        """Returns un array with the results of the column"""
        cur=self._con.cursor()
        cur.execute(sql, arr)
        for row in cur:
            arr.append(row[0])
        cur.close()
        return arr
        
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
#            self._con(None, QApplication.translate("Core","Error conecting to Xulpymoney"))
        self.active=True
        self.init=datetime.datetime.now()
        
    def disconnect(self):
        self._con.close()
        
    def is_active(self):
        return self.active
        
        
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
#        
#        
#    def connect(self,  db,  port, user, host, pasw):        
#        self.strcon="dbname='{}' port='{}' user='{}' host='{}' password='{}'".format(db, port, user, host, pasw)
#        try:
#            con=psycopg2.extras.DictConnection(self.strcon)
#        except psycopg2.Error as e:
#            print (e.pgcode, e.pgerror)
#            return (None, QApplication.translate("Core","Error conecting to Xulpymoney"))
#        return (con, QApplication.translate("Core", "Connection done"))
    

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
        self.inversion=None
        
    def init__create(self, datetime,  concepto, tipooperacion, importe, comentario, cuenta, operinversion, inversion, id=None):
        self.datetime=datetime
        self.concepto=concepto
        self.tipooperacion=tipooperacion
        self.importe=importe
        self.comentario=comentario
        self.account=cuenta
        self.operinversion=operinversion
        self.inversion=inversion
        return self
        


    def save(self):
        cur=self.mem.con.cursor()
        if self.id==None:
            cur.execute("insert into opercuentasdeoperinversiones (datetime, id_conceptos, id_tiposoperaciones, importe, comentario,id_cuentas, id_operinversiones,id_inversiones) values ( %s,%s,%s,%s,%s,%s,%s,%s) returning id_opercuentas", (self.datetime, self.concepto.id, self.tipooperacion.id, self.importe, self.comentario, self.account.id, self.operinversion.id, self.inversion.id))
            self.id=cur.fetchone()[0]
        else:
            cur.execute("UPDATE FALTA  set datetime=%s, id_conceptos=%s, id_tiposoperaciones=%s, importe=%s, comentario=%s, id_cuentas=%s where id_opercuentas=%s", (self.datetime, self.concepto.id, self.tipooperacion.id,  self.importe,  self.comentario,  self.account.id,  self.id))
        cur.close()


class SetCommons:
    """Base clase to create Sets, it needs id and name attributes, as index. It has a list arr and a dics dic_arr to access objects of the set"""
    def __init__(self):
        self.dic_arr={}
        self.arr=[]
        self.id=None
        self.name=None
        self.selected=None#Used to select a item in the set. Usefull in tables. Its a item
    
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
        
    def length(self):
        return len(self.arr)
        
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
        self.mem.data.products_all().find_by_id(80230)
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
        initparams son los parametros de iniciaci´on de la clase"""
        result=self.__class__(*initparams)#Para que coja la clase del objeto que lo invoca
        for a in self.arr:
            result.append(a)
        return result
        
    def union(self,  set,  *initparams):
        """Returns a new set, with the union comparing id
        initparams son los parametros de iniciaci´on de la clse"""        
        resultado=self.__class__(*initparams)#Para que coja la clase del objeto que lo invoca SetProduct(self.mem), luego ser´a self.mem
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
        
    def list_distinct_products_id(self):
        """Función que devuelve una lista con los distintos products_id """
        resultado=set([])
        for inv in self.arr:
            resultado.add(inv.product.id)
        return list(resultado)
            
    def myqtablewidget(self, table):
        table.setRowCount(len(self.arr))
        table.clearContents()
        d={"sumpendiente":Decimal(0), "sumdiario":Decimal(0), "suminvertido":Decimal(0), "sumpositivos":Decimal(0), "sumnegativos":Decimal(0)} 
        for i, inv in enumerate(self.arr):
            table.setItem(i, 0, QTableWidgetItem("{0} ({1})".format(inv.name, inv.account.name)))            
            table.setItem(i, 1, qdatetime(inv.product.result.basic.last.datetime, inv.product.stockexchange.zone))
            table.setItem(i, 2, inv.product.currency.qtablewidgetitem(inv.product.result.basic.last.quote,  6))#Se debería recibir el parametro currency
            
            diario=inv.diferencia_saldo_diario()
            try:
                d["sumdiario"]=d["sumdiario"]+diario
            except:
                pass
            table.setItem(i, 3, inv.product.currency.qtablewidgetitem(diario))
            table.setItem(i, 4, qtpc(inv.product.result.basic.tpc_diario()))
            table.setItem(i, 5, inv.product.currency.qtablewidgetitem(inv.balance()))
            d["suminvertido"]=d["suminvertido"]+inv.invertido()
            pendiente=inv.pendiente()
            if pendiente>0:
                d["sumpositivos"]=d["sumpositivos"]+pendiente
            else:
                d["sumnegativos"]=d["sumnegativos"]+pendiente
            d["sumpendiente"]=d["sumpendiente"]+pendiente
            table.setItem(i, 6, inv.product.currency.qtablewidgetitem(pendiente))
            tpc_invertido=inv.tpc_invertido()
            table.setItem(i, 7, qtpc(tpc_invertido))
            if self.mem.gainsyear==True and inv.op_actual.less_than_a_year()==True:
                table.item(i, 7).setIcon(QIcon(":/xulpymoney/new.png"))
            tpc_venta=inv.tpc_venta()
            table.setItem(i, 8, qtpc(tpc_venta))
            if inv.selling_expiration!=None:
                if inv.selling_expiration<datetime.date.today():
                    table.item(i, 8).setIcon(QIcon(":/xulpymoney/alarm_clock.png"))
            if tpc_invertido!=None and tpc_venta!=None:
                if tpc_invertido<=-50:   
                    table.item(i, 7).setBackground(QColor(255, 148, 148))
                if (tpc_venta<=5 and tpc_venta>0) or tpc_venta<0:
                    table.item(i, 8).setBackground(QColor(148, 255, 148))
        return d
    def myqtablewidget_lastCurrent(self, table,  percentage):
        """
            Percentage is the colored percentage to show
        """
        table.setRowCount(len(self.arr))
        table.clearContents()
        for i, inv in enumerate(self.arr):
            table.setItem(i, 0, QTableWidgetItem("{0} ({1})".format(inv.name, inv.account.name)))
            table.setItem(i, 1, qdatetime(inv.op_actual.arr[inv.op_actual.length()-1].datetime, self.mem.localzone))
            table.setItem(i, 2, qright(inv.op_actual.arr[inv.op_actual.length()-1].acciones))
            table.setItem(i, 3, qright(inv.op_actual.acciones()))
            table.setItem(i, 4,  inv.product.currency.qtablewidgetitem(inv.balance()))
            table.setItem(i, 5, inv.product.currency.qtablewidgetitem(inv.pendiente()))
            lasttpc=inv.op_actual.arr[inv.op_actual.length()-1].tpc_total(inv.product.result.basic.last.quote)
            table.setItem(i, 6, qtpc(lasttpc))
            table.setItem(i, 7, qtpc(inv.tpc_invertido()))
            table.setItem(i, 8, qtpc(inv.tpc_venta()))
            if lasttpc<=percentage:   
                table.item(i, 6).setBackground(QColor(255, 148, 148))

    def average_age(self):
        """Average age of the investments in this set in days"""
        #Extracts all currentinvestmentoperations
        set=SetInvestmentOperationsCurrent(self.mem)
        for inv in self.arr:
            for o in inv.op_actual.arr:
                set.arr.append(o)
        average=set.average_age()
        if average==None:
            return None
        return round(average, 2)
            
    def saldo_misma_investment(self, product):
        """Devuelve el balance de todas las inversiones que tienen el mismo product.bolsa
        product es un objeto Product"""
        resultado=Decimal(0)
        for i in self.arr:
            if i.product==product:
                resultado=resultado+i.balance()
        return resultado
        
    def invertido_misma_investment(self, product):
        """Devuelve el balance de todas las inversiones que tienen el mismo product.bolsa
        product es un objeto Product"""
        resultado=Decimal(0)
        for i in self.arr:
            if i.product==product:
                resultado=resultado+i.invertido()
        return resultado



    def qcombobox_same_investmentmq(self, combo,  investmentmq):
        """Muestra las inversiones activas que tienen el mq pasado como parametro"""
        arr=[]
        for i in self.arr:
            if i.active==True and i.product==investmentmq:
                arr.append(("{0} - {1}".format(i.account.eb.name, i.name), i.id))
                        
        arr=sorted(arr, key=lambda a: a[0]  ,  reverse=False)  
        for a in arr:
            combo.addItem(a[0], a[1])

    def qcombobox(self, combo, tipo, activas=None):
        """Activas puede tomar None. Muestra Todas, True. Muestra activas y False Muestra inactivas
        tipo es una variable que controla la forma de visualizar
        0: inversion
        1: eb - inversion"""
        arr=[]
        for i in self.arr:
            if activas==True:
                if i.active==False:
                    continue
            elif activas==False:
                if i.active==True:
                    continue
            if tipo==0:
                arr.append((i.name, i.id))            
            elif tipo==1:
                arr.append(("{0} - {1}".format(i.account.eb.name, i.name), i.id))
                
        
        arr=sorted(arr, key=lambda a: a[0]  ,  reverse=False)  
        for a in arr:
            combo.addItem(a[0], a[1])
            
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

        if comision!=0:
            op_cuenta=AccountOperation(self.mem).init__create(now.date(), self.mem.conceptos.find_by_id(38), self.mem.tiposoperaciones.find_by_id(1), -comision, "Traspaso de valores", origen.account)
            op_cuenta.save()           
            comentario="{0}|{1}".format(destino.id, op_cuenta.id)
        else:
            comentario="{0}|{1}".format(destino.id, "None")
        
        op_origen=InvestmentOperation(self.mem).init__create( self.mem.tiposoperaciones.find_by_id(9), now, origen,  -numacciones, 0,0, comision, 0, comentario, True)
        op_origen.save( False)      

        #NO ES OPTIMO YA QUE POR CADA SAVE SE CALCULA TODO
        comentario="{0}".format(op_origen.id)
        for o in origen.op_actual.arr:
            op_destino=InvestmentOperation(self.mem).init__create( self.mem.tiposoperaciones.find_by_id(10), now, destino,  o.acciones, o.importe, o.impuestos, o.comision, o.valor_accion, comentario,  o.show_in_ranges)
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
        origen=operinversionorigen.inversion
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


    def order_by_percentage_last_operation(self):
        """Orders the Set using self.arr"""
        try:
            self.arr=sorted(self.arr, key=lambda inv: inv.op_actual.arr[inv.op_actual.length()-1].tpc_total(inv.product.result.basic.last.quote),  reverse=True) 
            return True
        except:
            return False
            
    def order_by_datetime_last_operation(self):
        """Orders the Set using self.arr"""
        try:
            self.arr=sorted(self.arr, key=lambda inv: inv.op_actual.arr[inv.op_actual.length()-1].datetime,  reverse=False) 
            return True
        except:
            return False


    def order_by_percentage_sellingpoint(self):
        """Orders the Set using self.arr"""
        try:
            self.arr=sorted(self.arr, key=lambda inv: ( inv.tpc_venta(), -inv.tpc_invertido()),  reverse=False) #Ordenado por dos criterios
            return True
        except:
            return False
            
    def order_by_percentage_invested(self):
        """Orders the Set using self.arr"""
        try:
            self.arr=sorted(self.arr, key=lambda inv: inv.tpc_invertido(),  reverse=True) 
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
        
        
class SetProducts(SetCommons):
    def __init__(self, mem):
        SetCommons.__init__(self)
        self.mem=mem
        

    def find_by_ticker(self, ticker):
        if ticker==None:
            return None
        for p in self.arr:
            if p.ticker==None:
                continue
            if p.ticker.upper()==ticker.upper():
                return p
        return None        
        

    def find_by_isin(self, isin):
        if isin==None:
            return None
        for p in self.arr:
            if p.isin==None:
                continue
            if p.isin.upper()==isin.upper():
                return p
        return None                
        
    def load_from_inversiones_query(self, sql):
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
            self.load_from_db("select * from products where id in ("+lista+")", progress=True )
        
    def load_from_db(self, sql,  progress=False):
        """sql es una query sobre la tabla inversiones
        Carga estimations_dbs, y basic
        """
        self.clean()
        cur=self.mem.con.cursor()
        cur.execute(sql)#"select * from products where id in ("+lista+")" 
        if progress==True:
            pd= QProgressDialog(QApplication.translate("Core","Loading {0} products from database").format(cur.rowcount),None, 0,cur.rowcount)
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
   
        table.clearSelection()    
        table.setFocus()
        table.horizontalHeader().setStretchLastSection(False)   
        table.clearContents()
        table.setRowCount(self.length())
        for i, p in enumerate(self.arr):
            table.setItem(i, 0, QTableWidgetItem(str(p.id)))
            table.setItem(i, 1, QTableWidgetItem(p.name.upper()))
            table.item(i, 1).setIcon(p.stockexchange.country.qicon())
            table.setItem(i, 2, QTableWidgetItem(p.isin))   
            table.setItem(i, 3, qdatetime(p.result.basic.last.datetime, p.stockexchange.zone))#, self.mem.localzone.name)))
            table.setItem(i, 4, p.currency.qtablewidgetitem(p.result.basic.last.quote, 6 ))  

            table.setItem(i, 5, qtpc(p.result.basic.tpc_diario()))
            table.setItem(i, 6, qtpc(p.result.basic.tpc_anual()))           
            if p.estimations_dps.currentYear()==None:
                table.setItem(i, 7, qtpc(None))
                table.item(i, 7).setBackground( QColor(255, 182, 182))          
            else:
                table.setItem(i, 7, qtpc(p.estimations_dps.currentYear().percentage()))  
                
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
        table.setRowCount(self.length())
        for i, a in enumerate(self.arr):
            table.setItem(i, 0, qdatetime(a.creation, self.mem.localzone))
            table.setItem(i, 1, qleft(a.type.name))
            table.item(i, 1).setIcon(a.type.qicon())
            table.setItem(i, 2, qleft(a.simulated_db()))
            table.setItem(i, 3, qdatetime(a.starting, self.mem.localzone))
            table.setItem(i, 4, qdatetime(a.ending, self.mem.localzone))


class SetStockExchanges(SetCommons):
    def __init__(self, mem):
        SetCommons.__init__(self)
        self.mem=mem     
    
    def load_all_from_db(self):
        cur=self.mem.con.cursor()
        cur.execute("Select * from bolsas")
        for row in cur:
            self.append(StockExchange(self.mem).init__db_row(row, self.mem.countries.find_by_id(row['country'])))
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
        resultado=SetConcepts(self.mem)
        for c in self.arr:
            if c.tipooperacion.id==id_tiposoperaciones:
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
        
        arr=sorted(arr, key=lambda o:o[0].name)
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
        """Función que carga en un combo pasado como parámetro con los pa´ises que tienen traducci´on""" 
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
        res=Decimal(0)
        for ac in self.arr:
            res=res+ac.balance(date)
        return res


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
            co=AccountOperation(self.mem).init__create(row['datetime'], self.mem.conceptos.find_by_id(row['id_conceptos']), self.mem.tiposoperaciones.find_by_id(row['id_tiposoperaciones']), row['importe'], row['comentario'],  self.mem.data.accounts_all().find_by_id(row['id_cuentas']), row['id_opercuentas'])
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
                comentario=QApplication.translate("Core","Paid with {0}. {1}").format(self.mem.data.creditcards_all().find_by_id(row['id_tarjetas']).name, row['comentario'] )
            
            co=AccountOperation(self.mem).init__create(row['datetime'], self.mem.conceptos.find_by_id(row['id_conceptos']), self.mem.tiposoperaciones.find_by_id(row['id_tiposoperaciones']), row['importe'], comentario,  self.mem.data.accounts_all().find_by_id(row['id_cuentas']))
            self.append(co)
        cur.close()

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
        tabla.settings(   self.mem, parentname)       
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
            tabla.setItem(rownumber, 4+diff, qleft(a.comentario))
            
    def myqtablewidget_lastmonthbalance(self, table,    account, lastmonthbalance):
        table.clearContents()
        table.setRowCount(self.length()+1)        
        table.setItem(0, 1, QTableWidgetItem(QApplication.translate("Core", "Starting month balance")))
        table.setItem(0, 3, account.currency.qtablewidgetitem(lastmonthbalance))
        for i, o in enumerate(self.arr):
            lastmonthbalance=lastmonthbalance+o.importe
            table.setItem(i+1, 0, qdatetime(o.datetime, self.mem.localzone))
            table.setItem(i+1, 1, QTableWidgetItem(o.concepto.name))
            table.setItem(i+1, 2, account.currency.qtablewidgetitem(o.importe))
            table.setItem(i+1, 3, account.currency.qtablewidgetitem(lastmonthbalance))
            table.setItem(i+1, 4, QTableWidgetItem(o.comment()))                   

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


    def qcombobox(self, combo, selectedcurrency=None):
        """Función que carga en un combo pasado como parámetro las currencies"""
        for c in self.arr:
            combo.addItem("{0} - {1} ({2})".format(c.id, c.name, c.symbol), c.id)
        if selectedcurrency!=None:
                combo.setCurrentIndex(combo.findData(selectedcurrency.id))

class SetDividends:
    """Class that  groups dividends from a Xulpymoney Product"""
    def __init__(self, mem):
        self.mem=mem
        self.arr=[]
        
    def load_from_db(self, sql):    
        del self.arr
        self.arr=[]
        cur=self.mem.con.cursor()
        cur.execute( sql)#"select * from dividends where id_inversiones=%s order by fecha", (self.inversion.id, )
        for row in cur:
            inversion=self.mem.data.investments_all().find_by_id(row['id_inversiones'])
            oc=AccountOperation(self.mem).init__db_query(row['id_opercuentas'])
            print(oc)
            self.arr.append(Dividend(self.mem).init__db_row(row, inversion, oc, self.mem.conceptos.find_by_id(row['id_conceptos']) ))
        cur.close()      
        
    def sort(self):       
        self.arr=sorted(self.arr, key=lambda e: e.fecha,  reverse=False) 
        
    def myqtablewidget(self, table,   show_investment=False,  parentname=None ):
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
            table.setItem(i, 0, QTableWidgetItem(str(d.fecha)))
            if show_investment==True:
                table.setItem(i, diff, qleft(d.inversion.name))
            table.setItem(i, diff+1, QTableWidgetItem(str(d.opercuenta.concepto.name)))
            table.setItem(i, diff+2, self.mem.localcurrency.qtablewidgetitem(d.bruto))
            table.setItem(i, diff+3, self.mem.localcurrency.qtablewidgetitem(d.retencion))
            table.setItem(i, diff+4, self.mem.localcurrency.qtablewidgetitem(d.comision))
            table.setItem(i, diff+5, self.mem.localcurrency.qtablewidgetitem(d.neto))
            table.setItem(i, diff+6, self.mem.localcurrency.qtablewidgetitem(d.dpa))
        table.setItem(len(self.arr), diff+1, QTableWidgetItem("TOTAL"))
        table.setItem(len(self.arr), diff+2, self.mem.localcurrency.qtablewidgetitem(sumbruto))
        table.setItem(len(self.arr), diff+3, self.mem.localcurrency.qtablewidgetitem(sumretencion))
        table.setItem(len(self.arr), diff+4, self.mem.localcurrency.qtablewidgetitem(sumcomision))
        table.setItem(len(self.arr), diff+5, self.mem.localcurrency.qtablewidgetitem(sumneto))
        return (sumneto, sumbruto, sumretencion, sumcomision)
            
    def clean(self):
        """Deletes all items"""
        del self.arr 
        self.arr=[]
    
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
        table.clearContents()
        table.setRowCount(len(self.arr))
        for i, e in enumerate(self.arr):
            table.setItem(i, 0, qcenter(str(e.year)))
            table.setItem(i, 1, self.product.currency.qtablewidgetitem(e.estimation, 6))       
            table.setItem(i, 2, qtpc(e.percentage()))
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
        table.clearContents()
        table.setRowCount(len(self.arr))
        for i, e in enumerate(self.arr):
            table.setItem(i, 0, qcenter(str(e.year)))
            table.setItem(i, 1, self.product.currency.qtablewidgetitem(e.estimation, 6))       
            table.setItem(i, 2, qright(e.PER(Quote(self.mem).init__from_query(self.product, day_end_from_date(datetime.date(e.year, 12, 31), self.product.stockexchange.zone))), 2))
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
            if a.datetime.date()>=date:
                resultado.append(a)
        return resultado
        
    def append(self, objeto):
        self.arr.append(objeto)
        
    def remove(self, objeto):
        """Remove from array"""
        self.arr.remove(objeto)
                
    def clone(self):
        """Links all items in self. arr to a new set. Linked points the same object"""
        result=self.__class__(self.mem)
        for a in self.arr:
            result.append(a)
        return result
                
    def clone_from_datetime(self, dt):
        """Función que devuelve otro SetInvestmentOperations con las oper que tienen datetime mayor o igual a la pasada como parametro."""
        result=self.__class__(self.mem)#Para que coja la clase del objeto que lo invoca
        if dt==None:
            return self.clone()
        for a in self.arr:
            if a.datetime>=dt:
                result.append(a)
        return result
                
                
    def copy(self):
        """Copy all items in self. arr. Copy is generate a copy in a diferent memoriy direction"""
        result=self.__class__(self.mem)
        for a in self.arr:
            result.append(a.clone())
        return result
                
    def copy_from_datetime(self, dt):
        """Función que devuelve otro SetInvestmentOperations con las oper que tienen datetime mayor o igual a la pasada como parametro."""
        result=self.__class__(self.mem)#Para que coja la clase del objeto que lo invoca
        if dt==None:
            return self.copy()
        for a in self.arr:
            if a.datetime>=dt:
                result.append(a.copy())
        return result
        
    def length(self):
        return len(self.arr)

    def order_by_datetime(self):
        """Ordena por datetime"""
        self.arr=sorted(self.arr, key=lambda o:o.datetime)

class SetInvestmentOperations(SetIO):       
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
        
        super(SetInvestmentOperations, self).remove(io)
        
        (io.inversion.op_actual,  io.inversion.op_historica)=io.inversion.op.calcular()
        io.inversion.actualizar_cuentasoperaciones_asociadas()#Regenera toda la inversi´on.
        
    def calcular(self):
        """Realiza los cálculos y devuelve dos arrays"""
        sioh=SetInvestmentOperationsHistorical(self.mem)
        sioa=SetInvestmentOperationsCurrent(self.mem)       
        for o in self.arr:      
#            print ("Despues ",  sioa.acciones(), o)              
            if o.acciones>=0:#Compra
                sioa.arr.append(InvestmentOperationCurrent(self.mem).init__create(o, o.tipooperacion, o.datetime, o.inversion, o.acciones, o.importe, o.impuestos, o.comision, o.valor_accion,  o.show_in_ranges,  o.id))
            else:#Venta
                if abs(o.acciones)>sioa.acciones():
                    print (o.acciones, sioa.acciones(),  o)
                    print("No puedo vender más acciones que las que tengo. EEEEEEEEEERRRRRRRRRRRROOOOORRRRR")
                    sys.exit(0)
                sioa.historizar(o, sioh)
        sioa.get_valor_benchmark(self.mem.data.benchmark)
        return (sioa, sioh)
#        
#    def calcular(self ):
#        """Realiza los calculos y devuelve dos arrys."""
#        def comisiones_impuestos(dif, p, n):
#            """Función que calcula lo simpuestos y las comisiones según el momento de actualizar
#            en el que se encuentre"""
#            (impuestos, comisiones)=(0, 0)
#            if dif==0: #Coincide la compra con la venta 
#                impuestos=n.impuestos+p.impuestos
#                comisiones=n.comision+p.comision
#                n.impuestos=0
#                n.comision=0
#                return (impuestos, comisiones)
#            elif dif<0:
#                """La venta no se ha acabado
#                    Las comision de compra se meten, pero no las de venta"""
#                impuestos=p.impuestos
#                comisiones=p.comision
#                p.impuestos=0
#                p.comision=0#Aunque se borra pero se quita por que se ha cobrado
#                return (impuestos, comisiones)
#            elif(dif>0):
#                """La venta se ha acabado y queda un nuevo p sin impuestos ni comision
#                    Los impuestos y las comision se meten
#                """
#                impuestos=n.impuestos+p.impuestos
#                comisiones=n.comision+p.comision
#                n.impuestos=0
#                n.comision=0
#                p.impuestos=0
#                p.comision=0
#                return (impuestos, comisiones)
#
#            
#        ##########################################
#        operinversioneshistorica=SetInvestmentOperationsHistorical(self.mem)
#        #Crea un array copia de self.arr, porque eran vinculos 
#        self.order_by_datetime()
#        arr=[]
#        for a in self.arr:   
#            arr.append(a.copy())
#        arr=sorted(arr, key=lambda a:a.id) 
#
#
#        while (True):#Bucle recursivo.            
#            pos=[]
#            for p in arr:
#                if p.acciones>0:
#                    pos.append(p)
#            #Mira si hay negativos y sino sale
#            n=None
#            for neg in arr:
#                if neg.acciones<0:
#                    n=neg
#                    break
#            if n==None:
#                break
#            elif len(pos)==0:#Se qudaba pillado
#                break
#            
#            #Solo impuestos y comisiones la primera vez
#            for p in pos:
#                dif=p.acciones+n.acciones
#                (impuestos, comisiones)=comisiones_impuestos(dif, p, n)
#                if dif==0: #Si es 0 se inserta el historico que coincide con la venta y se borra el registro negativ
#                    operinversioneshistorica.append(InvestmentOperationHistorical(self.mem).init__create(n, n.inversion, p.datetime.date(), -n.acciones*n.valor_accion,n.tipooperacion, n.acciones, comisiones, impuestos, n.datetime.date(), p.valor_accion, n.valor_accion))
#                    arr.remove(n)
#                    arr.remove(p)
#                    break
#                elif dif<0:#   //Si es <0 es decir hay más acciones negativas que positivas. Se debe introducir en el historico la tmpoperinversion y borrarlo y volver a recorrer el bucle. Restando a n.acciones las acciones ya apuntadas en el historico
#                    operinversioneshistorica.append(InvestmentOperationHistorical(self.mem).init__create(p, p.inversion, p.datetime.date(), p.acciones*n.valor_accion,n.tipooperacion, -p.acciones, comisiones, impuestos, n.datetime.date(), p.valor_accion, n.valor_accion))
#                    arr.remove(p)
#                    n.acciones=n.acciones+p.acciones#ya que n.acciones es negativo
#
#                elif(dif>0):
#                    """Cuando es >0 es decir hay mas acciones positivos se añade el registro en el historico 
#                    con los datos de la operacion negativa en su totalidad. Se borra el registro de negativos y 
#                    de positivos en operinversionesactual y se inserta uno con los datos positivos menos lo 
#                    quitado por el registro negativo. Y se sale del bucle. 
#                    //Aqui no se inserta la comision porque solo cuando se acaba las acciones positivos   """
#                    operinversioneshistorica.append(InvestmentOperationHistorical(self.mem).init__create(p, n.inversion, p.datetime.date(), -n.acciones*n.valor_accion,n.tipooperacion, n.acciones, comisiones, impuestos, n.datetime.date(), p.valor_accion, n.valor_accion))
#                    arr.remove(p)
#                    arr.remove(n)
#                    arr.append(InvestmentOperation(self.mem).init__create( p.tipooperacion, p.datetime, p.inversion,  p.acciones-(-n.acciones), (p.acciones-(-n.acciones))*n.valor_accion,  0, 0, p.valor_accion, "",  p.id))
#                    arr=sorted(arr, key=lambda a:a.id)              
#                    break;
#        #Crea array operinversionesactual, ya que arr es operinversiones
#        operinversionesactual=SetInvestmentOperationsCurrent(self.mem)
#        for a in arr:
#            operinversionesactual.append(InvestmentOperationCurrent(self.mem).init__create(a.id, a.tipooperacion, a.datetime, a.inversion,  a.acciones, a.importe,  a.impuestos, a.comision, a.valor_accion))
#        return (operinversionesactual, operinversioneshistorica)
#            

        
    def myqtablewidget(self, tabla):
        """Section es donde guardar en el config file, coincide con el nombre del formulario en el que está la tabla"""
        self.order_by_datetime()
        diff=0
        homogeneous=self.isHomogeneous()
        if homogeneous==False:
            diff=2
        tabla.setColumnCount(8+diff)
        tabla.setHorizontalHeaderItem(0, QTableWidgetItem(QApplication.translate("Core", "Date" )))
        if homogeneous==False:
            tabla.setHorizontalHeaderItem(diff-1, QTableWidgetItem(QApplication.translate("Core", "Product" )))
            tabla.setHorizontalHeaderItem(diff, QTableWidgetItem(QApplication.translate("Core", "Account" )))
        tabla.setHorizontalHeaderItem(diff+1, QTableWidgetItem(QApplication.translate("Core", "Operation type" )))
        tabla.setHorizontalHeaderItem(diff+2, QTableWidgetItem(QApplication.translate("Core", "Shares" )))
        tabla.setHorizontalHeaderItem(diff+3, QTableWidgetItem(QApplication.translate("Core", "Price" )))
        tabla.setHorizontalHeaderItem(diff+4, QTableWidgetItem(QApplication.translate("Core", "Amount" )))
        tabla.setHorizontalHeaderItem(diff+5, QTableWidgetItem(QApplication.translate("Core", "Comission" )))
        tabla.setHorizontalHeaderItem(diff+6, QTableWidgetItem(QApplication.translate("Core", "Taxes" )))
        tabla.setHorizontalHeaderItem(diff+7, QTableWidgetItem(QApplication.translate("Core", "Total" )))
        #DATA 
        tabla.clearContents()  
        tabla.setRowCount(len(self.arr))
        for rownumber, a in enumerate(self.arr):
            tabla.setItem(rownumber, 0, qdatetime(a.datetime, a.inversion.product.stockexchange.zone))
            if self.mem.gainsyear==True and a.less_than_a_year()==True:
                tabla.item(rownumber, 0).setIcon(QIcon(":/xulpymoney/new.png"))
            if homogeneous==False:
                tabla.setItem(rownumber, diff-1, qleft(a.inversion.name))
                tabla.setItem(rownumber, diff, qleft(a.inversion.account.name))
                
            tabla.setItem(rownumber, diff+1, QTableWidgetItem(a.tipooperacion.name))
            if a.show_in_ranges==True:
                tabla.item(rownumber, diff+1).setIcon(QIcon(":/xulpymoney/eye.png"))
            else:
                tabla.item(rownumber, diff+1).setIcon(QIcon(":/xulpymoney/eye_red.png"))
            
            tabla.setItem(rownumber, diff+2, qright(a.acciones))
            tabla.setItem(rownumber, diff+3, self.mem.localcurrency.qtablewidgetitem(a.valor_accion))
            tabla.setItem(rownumber, diff+4, self.mem.localcurrency.qtablewidgetitem(a.importe))
            tabla.setItem(rownumber, diff+5, self.mem.localcurrency.qtablewidgetitem(a.comision))
            tabla.setItem(rownumber, diff+6, self.mem.localcurrency.qtablewidgetitem(a.impuestos))
            if a.acciones>=0:
                tabla.setItem(rownumber, diff+7, self.mem.localcurrency.qtablewidgetitem(a.importe+a.comision+a.impuestos))
            else:
                tabla.setItem(rownumber, diff+7, self.mem.localcurrency.qtablewidgetitem(a.importe-a.comision-a.impuestos))

    def find(self,  investmentoperation_id):
        """Returns an investmenoperation with the id equals to the parameter"""
        for o in self.arr:
            if o.id==investmentoperation_id:
                return o
        return None

    def isHomogeneous(self):
        """Devuelve true si todas las inversiones son de la misma inversion"""
        if len(self.arr)==0:
            return True
        inversion=self.arr[0].inversion
        for i in range(1, len(self.arr)):
            if self.arr[i].inversion!=inversion:
                return False
        return True


class SetInvestmentOperationsCurrent(SetIO):    
    """Clase es un array ordenado de objetos newInvestmentOperation"""
    def __init__(self, mem):
        SetIO.__init__(self, mem)
    def __repr__(self):
        try:
            inversion=self.arr[0].inversion.id
        except:
            inversion= "Desconocido"
        return ("SetIOA Inv: {0}. N.Registros: {1}. N.Acciones: {2}. Invertido: {3}. Valor medio:{4}".format(inversion,  len(self.arr), self.acciones(),  self.invertido(),  self.valor_medio_compra()))
                        
    def average_age(self):
        """Average age of the current investment operations in days"""
        (sumbalance, sumbalanceage)=(Decimal(0), Decimal(0))
        for o in self.arr:
            balance=o.balance(o.inversion.product.result.basic.last)
            sumbalance=sumbalance+balance
            sumbalanceage=sumbalanceage+balance*o.age()
        if sumbalance!=Decimal(0):
            return round(sumbalanceage/sumbalance, 2)
        else:
            return 0
            
    def datetime_first_operation(self):
        if len(self.arr)==0:
            return None
        return self.arr[0].datetime
        
    def acciones(self):
        """Devuelve el número de acciones de la inversión actual"""
        resultado=Decimal(0)
        for o in self.arr:
            resultado=resultado+o.acciones
        return resultado
            
    
    def invertido(self):
        resultado=0
        for o in self.arr:
            resultado=resultado+o.invertido()
        return resultado
        
    def isHomogeneous(self):
        """Devuelve true si todas las inversiones son de la misma inversion"""
        if len(self.arr)==0:
            return True
        inversion=self.arr[0].inversion
        for i in range(1, len(self.arr)):
            if self.arr[i].inversion!=inversion:
                return False
        return True
    
    def less_than_a_year(self):
        for o in self.arr:
            if o.less_than_a_year()==True:
                return True
        return False
        
    def myqtablewidget_heterogeneus(self,  tabla, show_accounts=False):
        """Función que rellena una tabla pasada como parámetro con datos procedentes de un array de objetos
        InvestmentOperationCurrent y dos valores de mystocks para rellenar los tpc correspodientes
        
        Se dibujan las columnas pero las propiedad alternate color... deben ser en designer
        
        Parámetros
            - tabla myQTableWidget en la que rellenar los datos
        """
        #UI
        diff=0
        if show_accounts==True:
            diff=2
        tabla.setColumnCount(10+diff)
        tabla.setHorizontalHeaderItem(0, QTableWidgetItem(QApplication.translate("Core", "Date" )))
        if show_accounts==True:
            tabla.setHorizontalHeaderItem(diff-1, QTableWidgetItem(QApplication.translate("Core", "Product" )))
            tabla.setHorizontalHeaderItem(diff, QTableWidgetItem(QApplication.translate("Core", "Account" )))
        tabla.setHorizontalHeaderItem(diff+1, QTableWidgetItem(QApplication.translate("Core", "Shares" )))
        tabla.setHorizontalHeaderItem(diff+2, QTableWidgetItem(QApplication.translate("Core", "Price" )))
        tabla.setHorizontalHeaderItem(diff+3, QTableWidgetItem(QApplication.translate("Core", "Invested" )))
        tabla.setHorizontalHeaderItem(diff+4, QTableWidgetItem(QApplication.translate("Core", "Current balance" )))
        tabla.setHorizontalHeaderItem(diff+5, QTableWidgetItem(QApplication.translate("Core", "Pending" )))
        tabla.setHorizontalHeaderItem(diff+6, QTableWidgetItem(QApplication.translate("Core", "% annual" )))
        tabla.setHorizontalHeaderItem(diff+7, QTableWidgetItem(QApplication.translate("Core", "% APR" )))
        tabla.setHorizontalHeaderItem(diff+8, QTableWidgetItem(QApplication.translate("Core", "% Total" )))
        tabla.setHorizontalHeaderItem(diff+9, QTableWidgetItem(QApplication.translate("Core", "Benchmark" )))
        #DATA
        if self.length()==0:
            tabla.setRowCount(0)
            return
            
        sumsaldo=Decimal('0')
        sumpendiente=Decimal('0')
        suminvertido=Decimal('0')
        tabla.clearContents()
        tabla.setRowCount(len(self.arr)+1)
        rownumber=0
        for rownumber, a in enumerate(self.arr):
            balance=a.balance(a.inversion.product.result.basic.last)
            pendiente=a.pendiente(a.inversion.product.result.basic.last)
            invertido=a.invertido()
    
            sumsaldo=sumsaldo+balance
            sumpendiente=sumpendiente+pendiente
            suminvertido=suminvertido+invertido
    
            tabla.setItem(rownumber, 0, qdatetime(a.datetime, self.mem.localzone))
            if self.mem.gainsyear==True and a.less_than_a_year()==True:
                tabla.item(rownumber, 0).setIcon(QIcon(":/xulpymoney/new.png"))
            if show_accounts==True:
                tabla.setItem(rownumber, diff-1, qleft(a.inversion.name))
                tabla.setItem(rownumber, diff, qleft(a.inversion.account.name))
            tabla.setItem(rownumber, diff+1, qright("{0:.6f}".format(a.acciones)))
            tabla.setItem(rownumber, diff+2, a.inversion.product.currency.qtablewidgetitem(a.valor_accion, 6))
            tabla.setItem(rownumber, diff+3, a.inversion.product.currency.qtablewidgetitem(invertido))
            tabla.setItem(rownumber, diff+4, a.inversion.product.currency.qtablewidgetitem(balance))
            tabla.setItem(rownumber, diff+5, a.inversion.product.currency.qtablewidgetitem(pendiente))
            tabla.setItem(rownumber, diff+6, qtpc(a.tpc_anual(a.inversion.product.result.basic.last.quote, a.inversion.product.result.basic.endlastyear.quote)))
            tabla.setItem(rownumber, diff+7, qtpc(a.tpc_tae(a.inversion.product.result.basic.last.quote)))
            tabla.setItem(rownumber, diff+8, qtpc(a.tpc_total(a.inversion.product.result.basic.last.quote)))
            if a.referenciaindice==None:
                tabla.setItem(rownumber, diff+9, a.inversion.product.currency.qtablewidgetitem(None))
            else:
                tabla.setItem(rownumber, diff+9, a.inversion.product.currency.qtablewidgetitem(a.referenciaindice.quote))

        tabla.setItem(self.length(), 0, qleft(days_to_year_month(self.average_age())))
        tabla.setItem(self.length(), diff+0, QTableWidgetItem(("TOTAL")))
        tabla.setItem(self.length(), diff+3, a.inversion.product.currency.qtablewidgetitem(suminvertido))
        tabla.setItem(self.length(), diff+4, a.inversion.product.currency.qtablewidgetitem(sumsaldo))
        tabla.setItem(self.length(), diff+5, a.inversion.product.currency.qtablewidgetitem(sumpendiente))
        tabla.setItem(self.length(), diff+7, qtpc(self.tpc_tae()))
        tabla.setItem(self.length(), diff+8, qtpc(self.tpc_total(sumpendiente, suminvertido)))
        
    def myqtablewidget_homogeneus(self,  tabla,  show_accounts=False, quote=None):
        """Función que rellena una tabla pasada como parámetro con datos procedentes de un array de objetos
        InvestmentOperationCurrent y dos valores de mystocks para rellenar los tpc correspodientes
        
        Se dibujan las columnas pero las propiedad alternate color... deben ser en designer
        
        Parámetros
            - tabla myQTableWidget en la que rellenar los datos
            - quote, si queremos cargar las operinversiones con un valor determinado se pasar´a la quote correspondiente
        """
        if show_accounts==True:
            diff=2
        else:
            diff=0
            
        tabla.setColumnCount(10+diff)
        tabla.setHorizontalHeaderItem(0, QTableWidgetItem(QApplication.translate("Core", "Date" )))
        if show_accounts==True:
            tabla.setHorizontalHeaderItem(diff-1, QTableWidgetItem(QApplication.translate("Core", "Product" )))
            tabla.setHorizontalHeaderItem(diff, QTableWidgetItem(QApplication.translate("Core", "Account" )))
        tabla.setHorizontalHeaderItem(diff+1, QTableWidgetItem(QApplication.translate("Core", "Shares" )))
        tabla.setHorizontalHeaderItem(diff+2, QTableWidgetItem(QApplication.translate("Core", "Price" )))
        tabla.setHorizontalHeaderItem(diff+3, QTableWidgetItem(QApplication.translate("Core", "Invested" )))
        tabla.setHorizontalHeaderItem(diff+4, QTableWidgetItem(QApplication.translate("Core", "Current balance" )))
        tabla.setHorizontalHeaderItem(diff+5, QTableWidgetItem(QApplication.translate("Core", "Pending" )))
        tabla.setHorizontalHeaderItem(diff+6, QTableWidgetItem(QApplication.translate("Core", "% annual" )))
        tabla.setHorizontalHeaderItem(diff+7, QTableWidgetItem(QApplication.translate("Core", "% APR" )))
        tabla.setHorizontalHeaderItem(diff+8, QTableWidgetItem(QApplication.translate("Core", "% Total" )))
        tabla.setHorizontalHeaderItem(diff+9, QTableWidgetItem(QApplication.translate("Core", "Benchmark" )))
        #DATA
        if self.length()==0:
            tabla.setRowCount(0)
            return
            

        if quote==None:
            quote=self.arr[0].inversion.product.result.basic.last
        
        sumacciones=Decimal('0')
        sum_accionesXvalor=Decimal('0')
        sumsaldo=Decimal('0')
        sumpendiente=Decimal('0')
        suminvertido=Decimal('0')
        tabla.clearContents()
        tabla.setRowCount(self.length()+1)
        for rownumber, a in enumerate(self.arr):
            sumacciones=sumacciones+a.acciones
            balance=a.balance(quote)
            pendiente=a.pendiente(quote)
            invertido=a.invertido()
    
            sumsaldo=sumsaldo+balance
            sumpendiente=sumpendiente+pendiente
            suminvertido=suminvertido+invertido
            sum_accionesXvalor=sum_accionesXvalor+a.acciones*a.valor_accion
    
            tabla.setItem(rownumber, 0, qdatetime(a.datetime, self.mem.localzone))
            if self.mem.gainsyear==True and a.less_than_a_year()==True:
                tabla.item(rownumber, 0).setIcon(QIcon(":/xulpymoney/new.png"))
            if show_accounts==True:
                tabla.setItem(rownumber, diff-1, qleft(a.inversion.name))
                tabla.setItem(rownumber, diff, qleft(a.inversion.account.name))
            tabla.setItem(rownumber, diff+1, qright("{0:.6f}".format(a.acciones)))
            tabla.setItem(rownumber, diff+2, a.inversion.product.currency.qtablewidgetitem(a.valor_accion, 6))
            tabla.setItem(rownumber, diff+3, a.inversion.product.currency.qtablewidgetitem(invertido))
            tabla.setItem(rownumber, diff+4, a.inversion.product.currency.qtablewidgetitem(balance))
            tabla.setItem(rownumber, diff+5, a.inversion.product.currency.qtablewidgetitem(pendiente))
            tabla.setItem(rownumber, diff+6, qtpc(a.tpc_anual(quote.quote, a.inversion.product.result.basic.endlastyear.quote)))
            tabla.setItem(rownumber, diff+7, qtpc(a.tpc_tae(quote.quote)))
            tabla.setItem(rownumber, diff+8, qtpc(a.tpc_total(quote.quote)))
            if a.referenciaindice==None:
                tabla.setItem(rownumber, diff+9, a.inversion.product.currency.qtablewidgetitem(None))
            else:
                tabla.setItem(rownumber, diff+9, a.inversion.product.currency.qtablewidgetitem(a.referenciaindice.quote))
                
        tabla.setItem(self.length(), diff+0, QTableWidgetItem(("TOTAL")))
        tabla.setItem(self.length(), diff+1, qright(str(sumacciones)))
        if sumacciones==0:
            tabla.setItem(self.length(), diff+2, a.inversion.product.currency.qtablewidgetitem(0))
        else:
            tabla.setItem(self.length(), diff+2, a.inversion.product.currency.qtablewidgetitem(sum_accionesXvalor/sumacciones, 6))
        tabla.setItem(self.length(), diff+3, a.inversion.product.currency.qtablewidgetitem(suminvertido))
        tabla.setItem(self.length(), diff+4, a.inversion.product.currency.qtablewidgetitem(sumsaldo))
        tabla.setItem(self.length(), diff+5, a.inversion.product.currency.qtablewidgetitem(sumpendiente))
        tabla.setItem(self.length(), diff+7, qtpc(self.tpc_tae()))
        tabla.setItem(self.length(), diff+8, qtpc(self.tpc_total(sumpendiente, suminvertido)))
        return (sumacciones, suminvertido, sumpendiente)

    def pendiente(self, lastquote):
        resultado=0
        for o in self.arr:
            resultado=resultado+o.pendiente(lastquote)
        return resultado
                
    def tpc_tae(self):
        suminvertido=0
        invertidoxtae=0
        for o in self.arr:
            suminvertido=suminvertido+o.invertido()
            invertidoxtae=invertidoxtae+o.invertido()*o.tpc_tae(o.inversion.product.result.basic.last.quote)
        if suminvertido==0:
            return None
        return invertidoxtae/suminvertido
    
    def tpc_total(self, sumpendiente=None, suminvertido=None):
        """Si se pasan por parametros se optimizan los calculos"""
        if sumpendiente==None:
            sumpendiente=self.pendiente()
        if suminvertido==None:
            suminvertido=self.invertido()
        if suminvertido==0:
            return None
        return sumpendiente*100/suminvertido
    
    def get_valor_benchmark(self, indice):
        cur=self.mem.con.cursor()
        for o in self.arr:
            o.get_referencia_indice(indice)
        cur.close()
    
    def valor_medio_compra(self):
        """Devuelve el valor medio de compra de todas las operaciones de inversión actual"""
        numacciones=Decimal(0)
        numaccionesxvalor=Decimal(0)
        for o in self.arr:
            numacciones=numacciones+o.acciones
            numaccionesxvalor=numaccionesxvalor+o.acciones*o.valor_accion
        if numacciones==Decimal(0):
            return Dedimal(0)
        return numaccionesxvalor/numacciones
 
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
                    sioh.arr.append(InvestmentOperationHistorical(self.mem).init__create(ioa, io.inversion, ioa.datetime.date(), -accionesventa*io.valor_accion, io.tipooperacion, -accionesventa, comisiones, impuestos, io.datetime.date(), ioa.valor_accion, io.valor_accion))
                    self.arr.insert(0, InvestmentOperationCurrent(self.mem).init__create(ioa, ioa.tipooperacion, ioa.datetime, ioa.inversion,  ioa.acciones-abs(accionesventa), (ioa.acciones-abs(accionesventa))*ioa.valor_accion,  0, 0, ioa.valor_accion, ioa.show_in_ranges,  ioa.id))
                    self.arr.remove(ioa)
                    accionesventa=Decimal('0')#Sale bucle
                    break
                elif ioa.acciones-accionesventa<Decimal('0'):#<0 Se historiza todo y se restan acciones venta
                    comisiones=comisiones+ioa.comision
                    impuestos=impuestos+ioa.impuestos
                    sioh.arr.append(InvestmentOperationHistorical(self.mem).init__create(ioa, io.inversion, ioa.datetime.date(), -ioa.acciones*io.valor_accion, io.tipooperacion, -ioa.acciones, Decimal('0'), Decimal('0'), io.datetime.date(), ioa.valor_accion, io.valor_accion))
                    accionesventa=accionesventa-ioa.acciones                    
                    self.arr.remove(ioa)
                elif ioa.acciones-accionesventa==Decimal('0'):#Se historiza todo y se restan acciones venta y se sale
                    comisiones=comisiones+io.comision+ioa.comision
                    impuestos=impuestos+io.impuestos+ioa.impuestos
                    sioh.arr.append(InvestmentOperationHistorical(self.mem).init__create(ioa, io.inversion, ioa.datetime.date(), ioa.acciones*io.valor_accion, io.tipooperacion, -ioa.acciones, comisiones, impuestos, io.datetime.date(), ioa.valor_accion, io.valor_accion))
                    self.arr.remove(ioa)                    
                    accionesventa=Decimal('0')#Sale bucle                    
                    break
        if inicio-self.acciones()-abs(io.acciones)!=Decimal('0'):
            print ("Error en historizar. diff ", inicio-self.acciones()-abs(io.acciones),  "inicio",  inicio,  "fin", self.acciones(), io)
                
        
    def print_list(self):
        self.order_by_datetime()
        print ("\n Imprimiendo SIOA",  self)
        for oia in self.arr:
            print ("  - ", oia)
        
        
 
class SetInvestmentOperationsHistorical(SetIO):       
    """Clase es un array ordenado de objetos newInvestmentOperation"""
    def __init__(self, mem):
        SetIO.__init__(self, mem)

        
    def consolidado_bruto(self,  year=None,  month=None):
        resultado=0
        for o in self.arr:        
            if year==None:#calculo historico
                resultado=resultado+o.consolidado_neto()
            else:                
                if month==None:#Calculo anual
                    if o.fecha_venta.year==year:
                        resultado=resultado+o.consolidado_bruto()
                else:#Calculo mensual
                    if o.fecha_venta.year==year and o.fecha_venta.month==month:
                        resultado=resultado+o.consolidado_bruto()
        return resultado        
        
    def consolidado_neto(self,  year=None,  month=None):
        resultado=0
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
        resultado=0
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
    def myqtablewidget(self, tabla, parentname=None):
        """Rellena datos de un array de objetos de InvestmentOperationHistorical, devuelve totales ver código"""
        self.order_by_fechaventa()
        tabla.setColumnCount(13)
        tabla.setHorizontalHeaderItem(0, QTableWidgetItem(QApplication.translate("Core", "Date" )))
        tabla.setHorizontalHeaderItem(1, QTableWidgetItem(QApplication.translate("Core", "Years" )))
        tabla.setHorizontalHeaderItem(2, QTableWidgetItem(QApplication.translate("Core", "Product" )))
        tabla.setHorizontalHeaderItem(3, QTableWidgetItem(QApplication.translate("Core", "Operation type" )))
        tabla.setHorizontalHeaderItem(4, QTableWidgetItem(QApplication.translate("Core", "Shares" )))
        tabla.setHorizontalHeaderItem(5, QTableWidgetItem(QApplication.translate("Core", "Initial balance" )))
        tabla.setHorizontalHeaderItem(6, QTableWidgetItem(QApplication.translate("Core", "Final balance" )))
        tabla.setHorizontalHeaderItem(7, QTableWidgetItem(QApplication.translate("Core", "Gross selling operations" )))
        tabla.setHorizontalHeaderItem(8, QTableWidgetItem(QApplication.translate("Core", "Comissions" )))
        tabla.setHorizontalHeaderItem(9, QTableWidgetItem(QApplication.translate("Core", "Taxes" )))
        tabla.setHorizontalHeaderItem(10, QTableWidgetItem(QApplication.translate("Core", "Net selling operations" )))
        tabla.setHorizontalHeaderItem(11, QTableWidgetItem(QApplication.translate("Core", "% Net APR" )))
        tabla.setHorizontalHeaderItem(12, QTableWidgetItem(QApplication.translate("Core", "% Net Total" )))
        #DATA       
        
        (sumbruto, sumneto)=(0, 0);
        sumsaldosinicio=0;
        sumsaldosfinal=0;
    
        sumoperacionespositivas=0;
        sumoperacionesnegativas=0;
        sumimpuestos=0;
        sumcomision=0;        
        tabla.clearContents()
        tabla.setRowCount(len(self.arr)+1)
        for rownumber, a in enumerate(self.arr):
            saldoinicio=a.bruto_compra()
            saldofinal=a.bruto_venta()
            bruto=a.consolidado_bruto()
            sumimpuestos=sumimpuestos+Decimal(str(a.impuestos))
            sumcomision=sumcomision+Decimal(str(a.comision))
            neto=a.consolidado_neto()
            
    
            sumbruto=sumbruto+bruto;
            sumneto=sumneto+neto
            sumsaldosinicio=sumsaldosinicio+saldoinicio;
            sumsaldosfinal=sumsaldosfinal+saldofinal;
    
            #Calculo de operaciones positivas y negativas
            if bruto>0:
                sumoperacionespositivas=sumoperacionespositivas+bruto 
            else:
                sumoperacionesnegativas=sumoperacionesnegativas+bruto
    
            tabla.setItem(rownumber, 0,QTableWidgetItem(str(a.fecha_venta)))    
            tabla.setItem(rownumber, 1,QTableWidgetItem(str(round(a.years(), 2))))    
            tabla.setItem(rownumber, 2,QTableWidgetItem(a.inversion.name))
            tabla.setItem(rownumber, 3,QTableWidgetItem(a.tipooperacion.name))
            tabla.setItem(rownumber, 4,qright(a.acciones))
            tabla.setItem(rownumber, 5,self.mem.localcurrency.qtablewidgetitem(saldoinicio))
            tabla.setItem(rownumber, 6,self.mem.localcurrency.qtablewidgetitem(saldofinal))
            tabla.setItem(rownumber, 7,self.mem.localcurrency.qtablewidgetitem(bruto))
            tabla.setItem(rownumber, 8,self.mem.localcurrency.qtablewidgetitem(a.comision))
            tabla.setItem(rownumber, 9,self.mem.localcurrency.qtablewidgetitem(a.impuestos))
            tabla.setItem(rownumber, 10,self.mem.localcurrency.qtablewidgetitem(neto))
            tabla.setItem(rownumber, 11,qtpc(a.tpc_tae_neto()))
            tabla.setItem(rownumber, 12,qtpc(a.tpc_total_neto()))
            rownumber=rownumber+1
        if len(self.arr)>0:
            tabla.setItem(len(self.arr), 2,QTableWidgetItem("TOTAL"))    
            currency=self.arr[0].inversion.product.currency
            tabla.setItem(len(self.arr), 5,currency.qtablewidgetitem(sumsaldosinicio))    
            tabla.setItem(len(self.arr), 6,currency.qtablewidgetitem(sumsaldosfinal))    
            tabla.setItem(len(self.arr), 7,currency.qtablewidgetitem(sumbruto))    
            tabla.setItem(len(self.arr), 8,currency.qtablewidgetitem(sumcomision))    
            tabla.setItem(len(self.arr), 9,currency.qtablewidgetitem(sumimpuestos))    
            tabla.setItem(len(self.arr), 10,currency.qtablewidgetitem(sumneto))    
            tabla.setCurrentCell(len(self.arr), 4)       
        return (sumbruto, sumcomision, sumimpuestos, sumneto)
    

    def order_by_fechaventa(self):
        """Sort by selling date"""
        self.arr=sorted(self.arr, key=lambda o: o.fecha_venta,  reverse=False)      
        
class InvestmentOperationHistorical:
    def __init__(self, mem):
        self.mem=mem 
        self.id=None
        self.operinversion=None
        self.inversion=None
        self.fecha_inicio=None
#        self.importe=None
        self.tipooperacion=None
        self.acciones=None#Es negativo
        self.comision=None
        self.impuestos=None
        self.fecha_venta=None
        self.valor_accion_compra=None
        self.valor_accion_venta=None     
        
    def init__create(self, operinversion, inversion, fecha_inicio, importe, tipooperacion, acciones,comision,impuestos,fecha_venta,valor_accion_compra,valor_accion_venta, id=None):
        """GEnera un objeto con los parametros. id_operinversioneshistoricas es puesto a new"""
        self.id=id
        self.operinversion=operinversion
        self.inversion=inversion
        self.fecha_inicio=fecha_inicio
#        self.importe=importe
        self.tipooperacion=tipooperacion
        self.acciones=acciones
        self.comision=comision
        self.impuestos=impuestos
        self.fecha_venta=fecha_venta
        self.valor_accion_compra=valor_accion_compra
        self.valor_accion_venta=valor_accion_venta
        return self
        
    def less_than_a_year(self):
        """Returns True, when datetime of the operation is <= a year"""
        if self.fecha_venta-self.fecha_inicio<=datetime.timedelta(days=365):
            return True
        return False
        
    def consolidado_bruto(self):
        """Solo acciones"""
        if self.tipooperacion.id in (9, 10):
            return 0
        return self.bruto_venta()-self.bruto_compra()
        
    def consolidado_neto(self):
        if self.tipooperacion.id in (9, 10):
            return 0
        return self.consolidado_bruto() -self.comision -self.impuestos
        
    def consolidado_neto_antes_impuestos(self):
        if self.tipooperacion.id in (9, 10):
            return 0
        return self.consolidado_bruto() -self.comision 
        
    def bruto_compra(self):
        if self.tipooperacion.id in (9, 10):
            return 0
        return -self.acciones*self.valor_accion_compra
        
    def bruto_venta(self):
        if self.tipooperacion.id in (9, 10):
            return 0
        return -self.acciones*self.valor_accion_venta
        
    def days(self):
        return (self.fecha_venta-self.fecha_inicio).days
        
    def years(self):
        dias=self.days()
        if dias==0:#Operación intradía
            return Decimal(1/365.0)
        else:
                return dias/Decimal(365)
    def tpc_total_neto(self):
        bruto=self.bruto_compra()
        if bruto!=0:
            return 100*self.consolidado_neto()/bruto
        return 0
        
    def tpc_total_bruto(self):
        bruto=self.bruto_compra()
        if bruto!=0:
            return 100*self.consolidado_bruto()/bruto
        return 0 #Debería ponerse con valor el día de agregación
        
    def tpc_tae_neto(self):
        dias=(self.fecha_venta-self.fecha_inicio).days +1 #Account el primer día
        if dias==0:
            dias=1
        return Decimal(365*self.tpc_total_neto()/dias)
        
                
class InvestmentOperationCurrent:
    def __init__(self, mem):
        self.mem=mem 
        self.id=None
        self.operinversion=None
        self.tipooperacion=None
        self.datetime=None# con tz
        self.inversion=None
        self.acciones=None
        self.importe=None
        self.impuestos=None
        self.comision=None
        self.valor_accion=None
        self.referenciaindice=None##Debera cargarse desde fuera. No se carga con row.. Almacena un Quote, para comprobar si es el indice correcto ver self.referenciaindice.id
        self.show_in_ranges=True
        
    def __repr__(self):
        return ("IOA {0}. {1} {2}. Acciones: {3}. Valor:{4}".format(self.inversion.name,  self.datetime, self.tipooperacion.name,  self.acciones,  self.valor_accion))
        
    def init__create(self, operinversion, tipooperacion, datetime, inversion, acciones, importe, impuestos, comision, valor_accion, show_in_ranges,  id=None):
        """Investment es un objeto Investment"""
        self.id=id
        self.operinversion=operinversion
        self.tipooperacion=tipooperacion
        self.datetime=datetime
        self.inversion=inversion
        self.acciones=acciones
        self.importe=importe
        self.impuestos=impuestos
        self.comision=comision
        self.valor_accion=valor_accion
        self.show_in_ranges=show_in_ranges
        return self
                                
    def init__db_row(self,  row,  inversion,  operinversion, tipooperacion):
        self.id=row['id_operinversionesactual']
        self.operinversion=operinversion
        self.tipooperacion=tipooperacion
        self.datetime=row['datetime']
        self.inversion=inversion
        self.acciones=row['acciones']
        self.importe=row['importe']
        self.impuestos=row['impuestos']
        self.comision=row['comision']
        self.valor_accion=row['valor_accion']
        self.show_in_ranges=row['show_in_ranges']
        return self
        
    def copy(self):
        return self.init__create(self.operinversion, self.tipooperacion, self.datetime, self.inversion, self.acciones, self.importe, self.impuestos, self.comision, self.valor_accion, self.show_in_ranges,  self.id)
                
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
        
    def invertido(self):
        """Función que devuelve el importe invertido teniendo en cuenta las acciones actuales de la operinversión y el valor de compra
        Si se usa  el importe no fuNCIONA PASO CON EL PUNTOI DE VENTA.
        """
        return self.acciones*self.valor_accion
        
    def balance(self,  lastquote):
        """Función que calcula el balance actual de la operinversion actual
                - lastquote: objeto Quote"""
        if self.acciones==0 or lastquote.quote==None:#Empty xulpy
            return 0
        return self.acciones*lastquote.quote

        
    def less_than_a_year(self):
        """Returns True, when datetime of the operation is <= a year"""
        if datetime.date.today()-self.datetime.date()<=datetime.timedelta(days=365):
            return True
        return False
        
    def pendiente(self, lastquote,  invertido=None):
        """Función que calcula el balance  pendiente de la operacion de inversion actual
                Necesita haber cargado mq getbasic y operinversionesactual
                lasquote es un objeto Quote
                """
        if invertido==None:
            invertido=self.invertido()
        return self.balance(lastquote)-invertido
        
    def tpc_anual(self,  last,  endlastyear):
        if last==None:#initiating xulpymoney
            return 0
        if self.datetime.year==datetime.date.today().year:
            endlastyear=self.valor_accion                
        if endlastyear==0:
            return 0
        return 100*(last-endlastyear)/endlastyear
    
    def tpc_total(self,  last):
        if last==None:#initiating xulpymoney
            return 0        
        if self.valor_accion==0:
            return 0
        return 100*(last-self.valor_accion)/self.valor_accion
        
    def tpc_tae(self, last):
        dias=(datetime.date.today()-self.datetime.date()).days +1 #Account el primer día
        if dias==0:
            dias=1
        return Decimal(365*self.tpc_total(last)/dias)
        
        

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
        cur=self.mem.con.cursor()
        cur.execute("select count(*) from opercuentas where id_conceptos=%s", (self.id, ))
        opercuentas=cur.fetchone()[0]
        cur.execute("select count(*) from opertarjetas where id_conceptos=%s", (self.id, ))
        opertarjetas=cur.fetchone()[0]
        cur.close()
        if opercuentas+opertarjetas!=0:
            return False
        return True
        
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
        
    def __repr__(self):
        return "AccountOperation {0}. datetime: {1}. Importe:{2}. Concept:{3}".format(self.id, self.datetime, self.importe, self.concepto)
        
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
            resultado=self.init__db_row(row, concepto, concepto.tipooperacion, self.mem.data.accounts_all().find_by_id(row['id_cuentas']))
        cur.close()
        return resultado

    def borrar(self):
        cur=self.mem.con.cursor()
        cur.execute("delete from opercuentas where id_opercuentas=%s", (self.id, ))
        cur.close()
        
    def comment(self):
        """Función que genera un comentario parseado según el tipo de operación o concepto
        
        Transferencias 4 origen :
            El comentario en transferencias: other_account|other_operaccount|comission_operaccount|commision
                - other_account: id_accounts of the other account
                - other_operaccount: id_opercuentas in order to remove them.
                - comission_operaccount: comission. Si es 0 es que no hay comision porque tambi´en es 0
        Transferencias 5 destino:
            El comentario en transferencias destino no tiene comission: other_account|other_operaccount
                - other_account: id_accounts of the other account
                - other_operaccount: id_opercuentas in order to remove them.     
                
        Comision de Transferencias
            - Transfer
            - Amount
            - Origin account
        """
        c=self.comentario.split("|")
        if self.concepto.id in (62, 39, 50, 63, 65) and len(c)==4:#"{0}|{1}|{2}|{3}".format(self.inversion.name, self.bruto, self.retencion, self.comision)
            return QApplication.translate("Core","{0[0]}. Gross: {0[1]} {1}. Witholding tax: {0[2]} {1}. Comission: {0[3]} {1}").format(c, self.account.currency.symbol)
        elif self.concepto.id in (29, 35) and len(c)==5:#{0}|{1}|{2}|{3}".format(row['inversion'], importe, comision, impuestos)
            return QApplication.translate("Core","{0[1]}: {0[0]} shares. Amount: {0[2]} {1}. Comission: {0[3]} {1}. Taxes: {0[4]} {1}").format(c, self.account.currency.symbol)
        elif self.concepto.id==40 and len(c)==2:#"{0}|{1}".format(self.selCreditCard.name, len(self.setSelOperCreditCards))
            return QApplication.translate("Core","CreditCard: {0[0]}. Made {0[1]} payments").format(c)
        elif self.concepto.id==4 and len(c)==3:#Transfer from origin
            return QApplication.translate("Core", "Transfer to {0}").format(self.mem.data.accounts_all().find_by_id(int(c[0])).name)
        elif self.concepto.id==5 and len(c)==2:#Transfer received in destiny
            return QApplication.translate("Core", "Transfer received from {0}").format(self.mem.data.accounts_all().find_by_id(int(c[0])).name)
        elif self.concepto.id==38 and c[0]=="Transfer":#Comision bancaria por transferencia
            return QApplication.translate("Core", "Due to account transfer of {0} from {1}").format(self.mem.localcurrency.string(float(c[1])), self.mem.data.accounts_all().find_by_id(int(c[2])).name)
        else:
            return self.comentario 
        
        
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
        c=self.comentario.split("|")
        if self.concepto.id == 38 and c[0]=="Transfer" and len(c)==3:#Comision bancaria por transferencia
            return False
        if self.concepto.id==4 and len(c)==3:#Transferencia origen
            return False
        if self.concepto.id==5 and len(c)==2:#Transferencia destino
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

    def create_db(self, database):
        """It has database parameter, due to I connect to template to create database"""
        if self.con.is_superuser():
            new=Connection().init__create(self.con.user, self.con.password, self.con.server, self.con.port, "template1")
            new.connect()
            new._con.set_isolation_level(0)#Si no no me dejaba
            print (database)
#            try:
            cur=new.cursor()
            cur.execute("create database {0};".format(database))
#            except:
#                print ("Error in create_db()")
#            finally:
            cur.close()
            new.disconnect()
            return False
            return True
        else:
            print ("You need to be superuser to create database")
            return False
        
    def drop_db(self, database):
        """It has database parameter, due to I connect to template to drop database"""
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
            cur.close()
            return True
        except:
            print ("Error creating xulpymoney basic schema")
            return False

        
class DBData:
    def __init__(self, mem):
        self.mem=mem
        self.loaded_inactive=False


    def load_actives(self):
        inicio=datetime.datetime.now()
        self.benchmark=Product(self.mem).init__db(self.mem.settingsdb.value("mem/benchmark", "79329" ))
        self.benchmark.result.basic.load_from_db()
        self.banks_active=SetBanks(self.mem)
        self.banks_active.load_from_db("select * from entidadesbancarias where active=true")
        self.accounts_active=SetAccounts(self.mem, self.banks_active)
        self.accounts_active.load_from_db("select * from cuentas where active=true")
        self.creditcards_active=SetCreditCards(self.mem, self.mem.data.accounts_active)
        self.creditcards_active.load_from_db("select * from tarjetas where active=true")
        self.products_active=SetProducts(self.mem)
        self.products_active.load_from_inversiones_query("select distinct(products_id) from inversiones where active=true")
        self.investments_active=SetInvestments(self.mem, self.accounts_active, self.products_active, self.benchmark)
        self.investments_active.load_from_db("select * from inversiones where active=true", True)
        print("Cargando actives",  datetime.datetime.now()-inicio)
        
    def load_inactives(self, force=False):
        def load():
            inicio=datetime.datetime.now()
            
            self.banks_inactive=SetBanks(self.mem)
            self.banks_inactive.load_from_db("select * from entidadesbancarias where active=false")

            self.accounts_inactive=SetAccounts(self.mem, self.banks_all())
            self.accounts_inactive.load_from_db("select * from cuentas where active=false")
        
            self.creditcards_inactive=SetCreditCards(self.mem, self.accounts_all())
            self.creditcards_inactive.load_from_db("select * from tarjetas where active=false")
            
            self.products_inactive=SetProducts(self.mem)
            self.products_inactive.load_from_inversiones_query("select distinct(products_id) from inversiones where active=false")

            self.investments_inactive=SetInvestments(self.mem, self.accounts_all(), self.products_all(), self.benchmark)
            self.investments_inactive.load_from_db("select * from inversiones where active=false",  True)
            
            print("\n","Cargando inactives",  datetime.datetime.now()-inicio)
            self.loaded_inactive=True
        #######################
        if force==False:
            if self.loaded_inactive==True:
                print ("Ya está cargada las inactives")
                return
            else:
                load()
        else:#No están cargadas
            load()
        
    def reload(self, force=True):
        self.load_actives()
        self.load_inactives(force)
        
        
    def reload_prices(self):
        ##Selecting products to update
        if self.loaded_inactive==False:
            products=self.products_active
        else:
            products=self.products_all()
        
        pd= QProgressDialog(QApplication.translate("Core","Reloading {0} product prices from database").format(len(products.arr)),None, 0,products.length())
        pd.setModal(True)
        pd.setWindowTitle(QApplication.translate("Core","Reloading prices..."))
        pd.forceShow()
        for i, p in enumerate(products.arr):
            pd.setValue(i)
            pd.update()
            QApplication.processEvents()
            p.result.basic.load_from_db()
        self.mem.data.benchmark.result.basic.load_from_db()        
        
    def banks_all(self):
        return self.banks_active.union(self.banks_inactive, self.mem)
        
    def accounts_all(self):
        return self.accounts_active.union(self.accounts_inactive, self.mem, self.banks_all())
        
    def creditcards_all(self):
        return self.creditcards_active.union(self.creditcards_inactive, self.mem,  self.accounts_all())
        
    def investments_all(self):
        return self.investments_active.union(self.investments_inactive, self.mem, self.accounts_all(), self.products_all(), self.benchmark)
        
    def products_all(self):
        return self.products_active.union(self.products_inactive, self.mem)
    
    
    def banks_set(self, active):
        """Function to point to list if is active or not"""
        if active==True:
            return self.banks_active
        else:
            self.load_inactives()
            return self.banks_inactive    
            
    def accounts_set(self, active):
        """Function to point to list if is active or not"""
        if active==True:
            return self.accounts_active
        else:
            return self.accounts_inactive    
    
    def investments_set(self, active):
        """Function to point to list if is active or not"""
        if active==True:
            return self.investments_active
        else:
            return self.investments_inactive
            
    def products_set(self, active):
        """Function to point to list if is active or not"""
        if active==True:
            return self.products_active
        else:
            return self.products_inactive            
            
    def creditcards_set(self, active):
        """Function to point to list if is active or not"""
        if active==True:
            return self.creditcards_active
        else:
            return self.creditcards_inactive

        
class Dividend:
    def __init__(self, mem):
        self.mem=mem
        self.id=None
        self.inversion=None
        self.bruto=None
        self.retencion=None
        self.neto=None
        self.dpa=None
        self.fecha=None
        self.opercuenta=None
        self.comision=None
        self.concepto=None#Puedeser 39 o 62 para derechos venta

    def __repr__(self):
        return ("Instancia de Dividend: {0} ({1})".format( self.neto, self.id))
        
    def init__create(self,  inversion,  bruto,  retencion, neto,  dpa,  fecha,  comision,  concepto, opercuenta=None,  id=None):
        """Opercuenta puede no aparecer porque se asigna al hacer un save que es cuando se crea. Si id=None,opercuenta debe ser None"""
        self.id=id
        self.inversion=inversion
        self.bruto=bruto
        self.retencion=retencion
        self.neto=neto
        self.dpa=dpa
        self.fecha=fecha
        self.opercuenta=opercuenta
        self.comision=comision
        self.concepto=concepto
        return self
        
    def init__db_row(self, row, inversion,  opercuenta,  concepto):
        return self.init__create(inversion,  row['bruto'],  row['retencion'], row['neto'],  row['valorxaccion'],  row['fecha'],   row['comision'],  concepto, opercuenta, row['id_dividends'])
        
    def borrar(self):
        """Borra un dividend, para ello borra el registro de la tabla dividends 
            y el asociado en la tabla opercuentas
            
            También actualiza el balance de la cuenta."""
        cur=self.mem.con.cursor()
        self.opercuenta.borrar()
        cur.execute("delete from dividends where id_dividends=%s", (self.id, ))
        cur.close()
        
    def neto_antes_impuestos(self):
        return self.bruto-self.comision
    
    def save(self):
        """Insertar un dividend y una opercuenta vinculada a la tabla dividends en el campo id_opercuentas
        Cuando se inserta el campo comentario de opercuenta tiene la forma (nombreinversion|bruto\retencion|comision)
        
        En caso de que sea actualizar un dividend hay que actualizar los datos de opercuenta y se graba desde aquí. No desde el objeto opercuenta
        
        Actualiza la cuenta 
        """
        cur=self.mem.con.cursor()
        comentario="{0}|{1}|{2}|{3}".format(self.inversion.name, self.bruto, self.retencion, self.comision)
        if self.id==None:#Insertar
            oc=AccountOperation(self.mem).init__create( self.fecha,self.concepto, self.concepto.tipooperacion, self.neto, comentario, self.inversion.account)
            oc.save()
            self.opercuenta=oc
            #Añade el dividend
            sql="insert into dividends (fecha, valorxaccion, bruto, retencion, neto, id_inversiones,id_opercuentas, comision, id_conceptos) values ('"+str(self.fecha)+"', "+str(self.dpa)+", "+str(self.bruto)+", "+str(self.retencion)+", "+str(self.neto)+", "+str(self.inversion.id)+", "+str(self.opercuenta.id)+", "+str(self.comision)+", "+str(self.concepto.id)+")"
            cur.execute(sql)
        else:
            self.opercuenta.datetime=self.fecha
            self.opercuenta.importe=self.neto
            self.opercuenta.comentario=comentario
            self.opercuenta.concepto=self.concepto
            self.opercuenta.tipooperacion=self.concepto.tipooperacion
            self.opercuenta.save()
            cur.execute("update dividends set fecha=%s, valorxaccion=%s, bruto=%s, retencion=%s, neto=%s, id_inversiones=%s, id_opercuentas=%s, comision=%s, id_conceptos=%s where id_dividends=%s", (self.fecha, self.dpa, self.bruto, self.retencion, self.neto, self.inversion.id, self.opercuenta.id, self.comision, self.concepto.id, self.id))
        cur.close()

class InvestmentOperation:
    def __init__(self, mem):
        self.mem=mem
        self.id=None
        self.tipooperacion=None
        self.inversion=None
        self.acciones=None
        self.importe=None
        self.impuestos=None
        self.comision=None
        self.valor_accion=None
        self.datetime=None
        self.comentario=None
        self.archivada=None
        self.show_in_ranges=True
        
    def __repr__(self):
        return ("IO {0} ({1}). {2} {3}. Acciones: {4}. Valor:{5}. IdObject: {6}".format(self.inversion.name, self.inversion.id,  self.datetime, self.tipooperacion.name,  self.acciones,  self.valor_accion, id(self)))
        
    def init__db_row(self,  row, inversion,  tipooperacion):
        self.id=row['id_operinversiones']
        self.tipooperacion=tipooperacion
        self.inversion=inversion
        self.acciones=row['acciones']
        self.importe=row['importe']
        self.impuestos=row['impuestos']
        self.comision=row['comision']
        self.valor_accion=row['valor_accion']
        self.datetime=row['datetime']
        self.comentario=row['comentario']
        self.show_in_ranges=row['show_in_ranges']
        return self
        
    def init__create(self, tipooperacion, datetime, inversion, acciones, importe, impuestos, comision, valor_accion, comentario, show_in_ranges,   id=None):
        print (show_in_ranges, id)
        self.id=id
        self.tipooperacion=tipooperacion
        self.datetime=datetime
        self.inversion=inversion
        self.acciones=acciones
        self.importe=importe
        self.impuestos=impuestos
        self.comision=comision
        self.valor_accion=valor_accion
        self.comentario=comentario
        self.show_in_ranges=show_in_ranges
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
        investment=self.mem.data.investments_all().find_by_id(row['id_inversiones'])
        return investment.op.find_by_id(row['id_operinversiones'])

    def actualizar_cuentaoperacion_asociada(self):
        """Esta función actualiza la tabla opercuentasdeoperinversiones que es una tabla donde 
        se almacenan las opercuentas automaticas por las operaciones con inversiones. Es una tabla 
        que se puede actualizar en cualquier momento con esta función"""
        self.comentario="{0}|{1}|{2}|{3}|{4}".format(self.acciones, self.inversion.name, self.importe, self.comision, self.impuestos)
        #/Borra de la tabla opercuentasdeoperinversiones los de la operinversi´on pasada como par´ametro
        cur=self.mem.con.cursor()
        cur.execute("delete from opercuentasdeoperinversiones where id_operinversiones=%s",(self.id, )) 
        cur.close()
        if self.tipooperacion.id==4:#Compra Acciones
            #Se pone un registro de compra de acciones que resta el balance de la opercuenta
            c=AccountOperationOfInvestmentOperation(self.mem).init__create(self.datetime, self.mem.conceptos.find_by_id(29), self.tipooperacion, -self.importe-self.comision, self.comentario, self.inversion.account, self,self.inversion)
            c.save()
        elif self.tipooperacion.id==5:#// Venta Acciones
            #//Se pone un registro de compra de acciones que resta el balance de la opercuenta
            c=AccountOperationOfInvestmentOperation(self.mem).init__create(self.datetime, self.mem.conceptos.find_by_id(35), self.tipooperacion, self.importe-self.comision-self.impuestos, self.comentario, self.inversion.account, self,self.inversion)
            c.save()
        elif self.tipooperacion.id==6:
            #//Si hubiera comisión se añade la comisión.
            if(self.comision!=0):
                c=AccountOperationOfInvestmentOperation(self.mem).init__create(self.datetime, self.mem.conceptos.find_by_id(38), self.mem.tiposoperaciones.find_by_id(1), -self.comision-self.impuestos, self.comentario, self.inversion.account, self,self.inversion)
                c.save()
    
    def copy(self):
        """Crea una inversion operacion desde otra inversionoepracion. NO es un enlace es un objeto clone"""
        resultado=InvestmentOperation(self.mem)
        resultado.init__create(self.tipooperacion, self.datetime, self.inversion, self.acciones, self.importe, self.impuestos, self.comision, self.valor_accion, self.comentario,  self.show_in_ranges, self.id)
        return resultado
                
    def comment(self):
        """Función que genera un comentario parseado según el tipo de operación o concepto"""
        if self.tipooperacion.id==9:#"Traspaso de valores. Origen"#"{0}|{1}|{2}|{3}".format(self.inversion.name, self.bruto, self.retencion, self.comision)
            return QApplication.translate("Core","Traspaso de valores realizado a {0}".format(self.comentario.split("|"), self.account.currency.symbol))
        else:
            return self.comentario

    def less_than_a_year(self):
        if datetime.date.today()-self.datetime.date()<=datetime.timedelta(days=365):
                return True
        return False
        
    def save(self, recalculate=True,  autocommit=True):
        cur=self.mem.con.cursor()
        if self.id==None:#insertar
            cur.execute("insert into operinversiones(datetime, id_tiposoperaciones,  importe, acciones,  impuestos,  comision,  valor_accion, comentario, show_in_ranges, id_inversiones) values (%s, %s, %s, %s, %s, %s, %s, %s,%s,%s) returning id_operinversiones", (self.datetime, self.tipooperacion.id, self.importe, self.acciones, self.impuestos, self.comision, self.valor_accion, self.comentario, self.show_in_ranges,  self.inversion.id))
            self.id=cur.fetchone()[0]
            self.inversion.op.append(self)
        else:
            cur.execute("update operinversiones set datetime=%s, id_tiposoperaciones=%s, importe=%s, acciones=%s, impuestos=%s, comision=%s, valor_accion=%s, comentario=%s, id_inversiones=%s, show_in_ranges=%s where id_operinversiones=%s", (self.datetime, self.tipooperacion.id, self.importe, self.acciones, self.impuestos, self.comision, self.valor_accion, self.comentario, self.inversion.id, self.show_in_ranges,  self.id))
        if recalculate==True:
            (self.inversion.op_actual,  self.inversion.op_historica)=self.inversion.op.calcular()   
            self.actualizar_cuentaoperacion_asociada()
        if autocommit==True:
            self.mem.con.commit()
        cur.close()

        
    def tpc_anual(self,  last,  endlastyear):
        return
    
    def tpc_total(self,  last):
        return
   
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
        resultado=0
        #Recorre balance cuentas
        for v in setcuentas.arr:
            if v.eb.id==self.id:
                resultado=resultado+v.balance()
        
        #Recorre balance inversiones
        for i in setinversiones.arr:
            if i.account.eb.id==self.id:
                resultado=resultado+i.balance()
        return resultado
        
    def es_borrable(self):
        """Función que devuelve un booleano si una cuenta es borrable, es decir, que no tenga registros dependientes."""
        #Recorre balance cuentas
        for c  in self.mem.data.accounts_all().arr:
            if c.eb.id==self.id:
                if c.es_borrable()==self.id:
                    return False
        return True
        
    def borrar(self):
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
    
    def balance(self,fecha=None):
        """Función que calcula el balance de una cuenta
        Solo asigna balance al atributo balance si la fecha es actual, es decir la actual
        Parámetros:
            - pg_cursor cur Cursor de base de datos
            - datetime.date fecha Fecha en la que calcular el balance
        Devuelve:
            - Decimal balance Valor del balance
        """
        cur=self.mem.con.cursor()
        if fecha==None:
            fecha=datetime.date.today()
        cur.execute('select sum(importe) from opercuentas where id_cuentas='+ str(self.id) +" and datetime::date<='"+str(fecha)+"';") 
        res=cur.fetchone()[0]
        cur.close()
        if res==None:
            return 0        
        return res
            
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
        """Si el oc_comision_id es 0 es que no hay comision porque tambi´en es 0"""
        #Ojo los comentarios est´an dependientes.
        if comision>0:
            commentcomission="Transfer|{0}|{1}".format(importe, cuentaorigen.id)
            oc_comision=AccountOperation(self.mem).init__create(datetime, self.mem.conceptos.find_by_id(38), self.mem.tiposoperaciones.find_by_id(1), -comision, commentcomission, cuentaorigen )
            oc_comision.save()          
            oc_comision_id=oc_comision.id  
        else:
            oc_comision_id=0
        oc_origen=AccountOperation(self.mem).init__create(datetime, self.mem.conceptos.find_by_id(4), self.mem.tiposoperaciones.find_by_id(3), -importe, "", cuentaorigen )
        oc_origen.save()
        commentdestino="{0}|{1}".format(cuentaorigen.id, oc_origen.id)
        oc_destino=AccountOperation(self.mem).init__create(datetime, self.mem.conceptos.find_by_id(5), self.mem.tiposoperaciones.find_by_id(3), importe, commentdestino, cuentadestino )
        oc_destino.save()
        oc_origen.comentario="{0}|{1}|{2}".format(cuentadestino.id, oc_destino.id, oc_comision_id)
        oc_origen.save()

    def qmessagebox_inactive(self):
        if self.active==False:
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(QApplication.translate("Core", "The associated account is not active. You must activate it first"))
            m.exec_()    
            return True
        return False
            
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
        
        
    def init__create(self, name, venta, cuenta, inversionmq, selling_expiration, active, id=None):
        self.name=name
        self.venta=venta
        self.account=cuenta
        self.product=inversionmq
        self.active=active
        self.selling_expiration=selling_expiration
        self.id=id
        return self
    
    
    def save(self):
        """Inserta o actualiza la inversión dependiendo de si id=None o no"""
        cur=self.mem.con.cursor()
        if self.id==None:
            cur.execute("insert into inversiones (inversion, venta, id_cuentas, active, selling_expiration,products_id) values (%s, %s,%s,%s,%s,%s) returning id_inversiones", (self.name, self.venta, self.account.id, self.active, self.selling_expiration,  self.product.id))    
            self.id=cur.fetchone()[0]
        else:
            cur.execute("update inversiones set inversion=%s, venta=%s, id_cuentas=%s, active=%s, selling_expiration=%s, products_id=%s where id_inversiones=%s", (self.name, self.venta, self.account.id, self.active, self.selling_expiration,  self.product.id, self.id))
        cur.close()

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
        if self.op==None: #No se ha cargado con get_operinversiones
            return False
        if len(self.op.arr)>0:
            return False
        return True
        

    def actualizar_cuentasoperaciones_asociadas(self):
        #Borra las opercuentasdeoperinversiones de la inversi´on actual
        cur=self.mem.con.cursor()
        cur.execute("delete from opercuentasdeoperinversiones where id_inversiones=%s", (self.id, ));
        cur.close()
        for o in self.op.arr:
            o.actualizar_cuentaoperacion_asociada()
            
    def borrar(self, cur):
        if self.es_borrable()==True:
            cur.execute("delete from inversiones where id_inversiones=%s", (self.id, ))

        
    def get_operinversiones(self, date=None):
        """Funci`on que carga un array con objetos inversion operacion y con ellos calcula el set de actual e historicas
        date is used to get invested balance in a particular date"""
        cur=self.mem.con.cursor()
        self.op=SetInvestmentOperations(self.mem)
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
            return self.acciones()*self.product.estimations_dps.find_by_id(year).estimation
        except:
            return 0
        
        
    def diferencia_saldo_diario(self):
        """Función que calcula la diferencia de balance entre last y penultimate
        Necesita haber cargado mq getbasic y operinversionesactual"""
        try:
            return self.acciones()*(self.product.result.basic.last.quote-self.product.result.basic.penultimate.quote)
        except:
            return None
            
    def dividends_neto(self, ano,  mes=None):
        """Dividend cobrado en un año y mes pasado como parámetro, independientemente de si la inversión esta activa o no.
        El 63 es un gasto aunque también este registrado en dividends."""
        cur=self.mem.con.cursor()
        if mes==None:#Calcula en el año
            cur.execute("select sum(neto) as neto from dividends where id_conceptos not in (63) and date_part('year',fecha) = "+str(ano))
            resultado=cur.fetchone()[0]
        else:
            cur.execute("select sum(neto) as neto from dividends where id_conceptos not in (63) and date_part('year',fecha) = "+str(ano)+" and date_part('month',fecha)= " + str(mes))
            resultado=cur.fetchone()[0]   
        if resultado==None:
            resultado=0
        cur.close()
        return resultado;                   
    def dividends_bruto(self,  ano,  mes=None):
        """Dividend cobrado en un año y mes pasado como parámetro, independientemente de si la inversión esta activa o no"""
        
        cur=self.mem.con.cursor()
        if mes==None:#Calcula en el año
            cur.execute("select sum(bruto) as bruto from dividends where id_conceptos not in (63) and  date_part('year',fecha) = "+str(ano))
            resultado=cur.fetchone()[0]
        else:
            cur.execute("select sum(bruto) as bruto from dividends where id_conceptos not in (63) and  date_part('year',fecha) = "+str(ano)+" and date_part('month',fecha)= " + str(mes))
            resultado=cur.fetchone()[0]   
        if resultado==None:
            resultado=0
        cur.close()
        return resultado;                
    
        
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
        
    def pendiente(self):
        """Función que calcula el balance  pendiente de la inversión
                Necesita haber cargado mq getbasic y operinversionesactual"""
        return self.balance()-self.invertido()
        
    def qmessagebox_inactive(self):
        if self.active==False:
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(QApplication.translate("Core", "The associated product is not active. You must activate it first"))
            m.exec_()    
            return True
        return False
    def balance(self, fecha=None):
        """Función que calcula el balance de la inversión
            Si el cur es None se calcula el actual 
                Necesita haber cargado mq getbasic y operinversionesactual"""     
        acciones=self.acciones(fecha)
        if acciones==0 or self.product.result.basic.last.quote==None:#Empty xulpy
            return Decimal(0)
                
        if fecha==None:
            return acciones*self.product.result.basic.last.quote
        else:
            quote=Quote(self.mem).init__from_query(self.product, day_end_from_date(fecha, self.mem.localzone))
            if quote.datetime==None:
                print ("Investment balance: {0} ({1}) en {2} no tiene valor".format(self.name, self.product.id, fecha))
                return Decimal('0')
            return acciones*quote.quote
        
    def invertido(self, date=None):       
        """Función que calcula el balance invertido partiendo de las acciones y el precio de compra
        Necesita haber cargado mq getbasic y operinversionesactual"""
        if date==None or date==datetime.date.today():#Current
            return self.op_actual.invertido()
        else:
            ### 0 Creo una vinversion fake para reutilizar codigo, cargando operinversiones hasta date
            invfake=Investment(self.mem).init__create(self.name, self.venta, self.account, self.product, self.selling_expiration, self.active, self.id)
            invfake.active=self.active
            invfake.get_operinversiones(date)
            return invfake.op_actual.invertido()
                
    def tpc_invertido(self):       
        """Función que calcula el tpc invertido partiendo de las balance actual y el invertido
        Necesita haber cargado mq getbasic y operinversionesactual"""
        invertido=self.invertido()
        if invertido==0:
            return 0
        return (self.balance()-invertido)*100/invertido
    def tpc_venta(self):       
        """Función que calcula el tpc venta partiendo de las el last y el valor_venta
        Necesita haber cargado mq getbasic y operinversionesactual"""
        if self.venta==0 or self.venta==None or self.product.result.basic.last.quote==None or self.product.result.basic.last.quote==0:
            return 0
        return (self.venta-self.product.result.basic.last.quote)*100/self.product.result.basic.last.quote

        



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
        
        
#    def __repr__(self):
#        return """CreditCardOperation ({})
#    - Datetime: {}
#    - Concepto: {}
#    - Tipo de operaci´on: {}
#    - Importe: {}
#    - Comentario: {}
#    - Tarjeta: {} ({})
#    - Pagado: {}
#    - Fecha de pago: {}
#    - Operaci´on de cuenta: {}
#        """.format(self.id, self.datetime, self.concepto.name, self.tipooperacion.name, self.importe, self.comentario, self.tarjeta.name,  self.tarjeta.id, self.pagado, self.fechapago, self.opercuenta.id)
#        
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
            self.lastyear_assests=Assets(self.mem).saldo_total(self.mem.data.investments_all(),  datetime.date(year-1, 12, 31))
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
        return self.lastyear_assests*self.percentage/100
        
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
        resultado=0
        sql="select cuentas_saldo('"+str(datetime)+"') as balance;";
        cur.execute(sql)
        resultado=cur.fetchone()[0] 
        cur.close()
        return resultado;

        
    def saldo_total(self, setinversiones,  datetime):
        """Versión que se calcula en cliente muy optimizada"""
        return self.saldo_todas_cuentas(datetime)+self.saldo_todas_inversiones(setinversiones, datetime)

        
    def saldo_todas_inversiones(self, setinversiones,   fecha):
        """Versión que se calcula en cliente muy optimizada"""
        resultado=0
        for i in setinversiones.arr:
            resultado=resultado+i.balance(fecha)                 
        return resultado
        
    def saldo_todas_inversiones_riesgo_cero(self, setinversiones, fecha=None):
        """Versión que se calcula en cliente muy optimizada
        Fecha None calcula  el balance actual
        """
        resultado=0
#        inicio=datetime.datetime.now()
        for inv in setinversiones.arr:
            if inv.product.tpc==0:        
                if fecha==None:
                    resultado=resultado+inv.balance()
                else:
                    resultado=resultado+inv.balance( fecha)
#        print ("core > Total > saldo_todas_inversiones_riego_cero: {0}".format(datetime.datetime.now()-inicio))
        return resultado

        
    def invested(self, date=None):
        """Devuelve el patrimonio invertido en una determinada fecha"""
        if date==None or date==datetime.date.today():
            array=self.mem.data.investments_active.arr #Current and active
        else:
            array=self.mem.data.investments_all().arr#All, because i don't know witch one was active.
        
        r=Decimal(0)
        for inv in array:
            invert=inv.invertido(date)
#            print ("Invertido", inv.name, date,  invert,  inv.balance(date))
            r=r+invert
        return r
        
    def saldo_todas_inversiones_bonds(self, fecha):        
        """Versión que se calcula en cliente muy optimizada
        Fecha None calcula  el balance actual
        """
        resultado=0
#        inicio=datetime.datetime.now()
        for inv in self.mem.data.investments_all().arr:
            if inv.product.type.id in (7, 9):#public and private bonds        
                if fecha==None:
                    resultado=resultado+inv.balance()
                else:
                    resultado=resultado+inv.balance( fecha)
#        print ("core > Assets > saldo_todas_inversiones_bonds: {0}".format(datetime.datetime.now()-inicio))
        return resultado

    def patrimonio_riesgo_cero(self, setinversiones, fecha):
        """CAlcula el patrimonio de riego cero"""
        return self.saldo_todas_cuentas(fecha)+self.saldo_todas_inversiones_riesgo_cero(setinversiones, fecha)

    def saldo_anual_por_tipo_operacion(self,  ano,  id_tiposoperaciones):   
        """Opercuentas y opertarjetas"""
        cur=self.mem.con.cursor()
        sql="select sum(Importe) as importe from opercuentas where id_tiposoperaciones="+str(id_tiposoperaciones)+" and date_part('year',datetime) = "+str(ano)  + " union all select sum(Importe) as importe from opertarjetas where id_tiposoperaciones="+str(id_tiposoperaciones)+" and date_part('year',datetime) = "+str(ano)
        cur.execute(sql)        
        resultado=0
        for i in cur:
            if i['importe']==None:
                continue
            resultado=resultado+i['importe']
        cur.close()
        return resultado

    def saldo_por_tipo_operacion(self,  ano,  mes,  id_tiposoperaciones):   
        """Opercuentas y opertarjetas"""
        cur=self.mem.con.cursor()
        sql="select sum(Importe) as importe from opercuentas where id_tiposoperaciones="+str(id_tiposoperaciones)+" and date_part('year',datetime) = "+str(ano)+" and date_part('month',datetime)= " + str(mes) + " union all select sum(Importe) as importe from opertarjetas where id_tiposoperaciones="+str(id_tiposoperaciones)+" and date_part('year',datetime) = "+str(ano)+" and date_part('month',datetime)= " + str(mes)
        cur.execute(sql)        
        
        resultado=0
        for i in cur:
            if i['importe']==None:
                continue
            resultado=resultado+i['importe']
        cur.close()
        return resultado
        
    def consolidado_bruto(self, setinversiones,  year=None, month=None):
        """Si year es none calcula el historicca  si month es nonve calcula el anual sino el mensual"""
        resultado=0
        for i in setinversiones.arr:        
            resultado=resultado+i.op_historica.consolidado_bruto(year, month)
        return resultado
    def consolidado_neto_antes_impuestos(self, setinversiones, year=None, month=None):
        """Si year es none calcula el historicca  si month es nonve calcula el anual sino el mensual"""
        resultado=0
        for i in setinversiones.arr:        
            resultado=resultado+i.op_historica.consolidado_neto_antes_impuestos(year, month)
        return resultado
        
                
    def consolidado_neto(self, setinversiones, year=None, month=None):
        """Si year es none calcula el historicca  si month es nonve calcula el anual sino el mensual"""
        resultado=0
        for i in setinversiones.arr:        
            resultado=resultado+i.op_historica.consolidado_neto(year, month)
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
        table.setRowCount(self.length())        
        for i, t in enumerate(self.arr):
            table.setItem(i, 0, QTableWidgetItem(t.name))
            table.setItem(i, 1, QTableWidgetItem(str(t.numero)))
            table.setItem(i, 2, qbool(t.active))
            table.setItem(i, 3, qbool(t.pagodiferido))
            table.setItem(i, 4, t.account.currency.qtablewidgetitem(t.saldomaximo ))
            table.setItem(i, 5, t.account.currency.qtablewidgetitem(t.saldo_pendiente()))
            
    def clone_of_account(self, cuenta):
        """Devuelve un SetCreditCards con las tarjetas de una determinada cuenta"""
        s=SetCreditCards(self.mem, self.accounts)
        for t in self.arr:
            if t.account==cuenta:
                s.arr.append(t)
        return s

class SetCreditCardOperations:
    def __init__(self, mem):
        self.mem=mem
        self.arr=[]
        self.selected=None#Used to work with selected items in arr
        
    def clear(self):
        del self.arr
        self.arr=[]

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
            co=CreditCardOperation(self.mem).init__db_row(row, self.mem.conceptos.find_by_id(row['id_conceptos']), self.mem.tiposoperaciones.find_by_id(row['id_tiposoperaciones']), self.mem.data.creditcards_all().find_by_id(row['id_tarjetas']), AccountOperation(self.mem).init__db_query(row['id_opercuentas']))
            self.append(co)
        cur.close()
    
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
            tabla.setItem(rownumber, 4, qleft(a.comentario))
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
        
    def find_by_id(self, id):
        r=super(SetAgrupations, self).find_by_id(id)
        if r==None:
            return self.dic_arr["ERROR"]
        else:
            return r
        
    def load_all(self):
        self.append(Agrupation(self.mem).init__create( "ERROR","Agrupación errónea", self.mem.types.find_by_id(3), self.mem.stockexchanges.find_by_id(1) ))
        self.append(Agrupation(self.mem).init__create( "IBEX","Ibex 35", self.mem.types.find_by_id(3), self.mem.stockexchanges.find_by_id(1) ))
        self.append(Agrupation(self.mem).init__create( "MERCADOCONTINUO","Mercado continuo español", self.mem.types.find_by_id(3), self.mem.stockexchanges.find_by_id(1) ))
        self.append(Agrupation(self.mem).init__create("CAC",  "CAC 40 de París", self.mem.types.find_by_id(3),self.mem.stockexchanges.find_by_id(3) ))
        self.append(Agrupation(self.mem).init__create( "EUROSTOXX","Eurostoxx 50", self.mem.types.find_by_id(3),self.mem.stockexchanges.find_by_id(10)  ))
        self.append(Agrupation(self.mem).init__create( "DAX","DAX", self.mem.types.find_by_id(3), self.mem.stockexchanges.find_by_id(5)  ))
        self.append(Agrupation(self.mem).init__create("SP500",  "Standard & Poors 500", self.mem.types.find_by_id(3), self.mem.stockexchanges.find_by_id(2)  ))
        self.append(Agrupation(self.mem).init__create( "NASDAQ100","Nasdaq 100", self.mem.types.find_by_id(3), self.mem.stockexchanges.find_by_id(2)  ))
        self.append(Agrupation(self.mem).init__create( "EURONEXT",  "EURONEXT", self.mem.types.find_by_id(3), self.mem.stockexchanges.find_by_id(10)  ))
        self.append(Agrupation(self.mem).init__create( "DEUTSCHEBOERSE",  "DEUTSCHEBOERSE", self.mem.types.find_by_id(3), self.mem.stockexchanges.find_by_id(5)  ))
        self.append(Agrupation(self.mem).init__create( "LATIBEX",  "LATIBEX", self.mem.types.find_by_id(3), self.mem.stockexchanges.find_by_id(1)  ))

        self.append(Agrupation(self.mem).init__create( "e_fr_LYXOR","LYXOR", self.mem.types.find_by_id(4),self.mem.stockexchanges.find_by_id(3)  ))
        self.append(Agrupation(self.mem).init__create( "e_de_DBXTRACKERS","Deutsche Bank X-Trackers", self.mem.types.find_by_id(4),self.mem.stockexchanges.find_by_id(5)  ))
        
        self.append(Agrupation(self.mem).init__create("f_es_0014",  "Gestora BBVA", self.mem.types.find_by_id(2), self.mem.stockexchanges.find_by_id(1) ))
        self.append(Agrupation(self.mem).init__create( "f_es_0043","Gestora Renta 4", self.mem.types.find_by_id(2), self.mem.stockexchanges.find_by_id(1)))
        self.append(Agrupation(self.mem).init__create("f_es_0055","Gestora Bankinter", self.mem.types.find_by_id(2),self.mem.stockexchanges.find_by_id(1) ))
        self.append(Agrupation(self.mem).init__create( "f_es_BMF","Fondos de la bolsa de Madrid", self.mem.types.find_by_id(2), self.mem.stockexchanges.find_by_id(1) ))

        self.append(Agrupation(self.mem).init__create( "w_fr_SG","Warrants Societe Generale", self.mem.types.find_by_id(5),self.mem.stockexchanges.find_by_id(3) ))
        self.append(Agrupation(self.mem).init__create("w_es_BNP","Warrants BNP Paribas", self.mem.types.find_by_id(5),self.mem.stockexchanges.find_by_id(1)))
  
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

class StockExchange:
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
        self.id=row['id_bolsas']
        self.name=row['name']
        self.country=country
        self.starts=row['starts']
        self.closes=row['closes']
        self.zone=self.mem.zones.find_by_name(row['zone'])
        return self

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
        return self.codes[ctext]+text+self.codes["reset"]
    def bold(self, text):
        return self.codes["bold"]+text+self.codes["reset"]
    def white(self, text):
        return bold(text)
    def teal(self, text):
        return self.codes["teal"]+text+self.codes["reset"]
    def turquoise(self, text):
        return self.codes["turquoise"]+text+self.codes["reset"]
    def darkteal(self, text):
        return turquoise(text)
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
        return brown(text)
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
        text= (self.string(n,  digits))
        a=QTableWidgetItem(text)
        a.setTextAlignment(Qt.AlignVCenter|Qt.AlignRight)
        if n==None:
            a.setForeground(QColor(0, 0, 255))
        elif n<0:
            a.setForeground(QColor(255, 0, 0))
        return a

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
    def __init__(self):
        self.number=None
        self.currency=None

    def init__create(self,number,currency):
        self.number=number
        self.currency=currency

    def string(self,   digits=2):
        if self.number==None:
            return "None " + self.currency.symbol
        else:
            return "{0} {1}".format(round(self.number, digits),self.currency.symbol)

    def currencies_exchange(self, cur,  quote, origen, destino):
        cambio=Quote.valor2(cur, origen+"2"+destino, quote['fecha'],  quote['hora'])
        exchange={"code":quote['code'],"quote":quote['quote']*cambio['quote'],  "date":cambio['date'], "time":cambio['time'],  "zone":cambio['zone'],  "currency":destino}
        return exchange

    def qtablewidgetitem(self, digits=2):
        """Devuelve un QTableWidgetItem mostrando un currency
        curren es un objeto Curryency"""
        text= (self.string(  digits))
        a=QTableWidgetItem(text)
        a.setTextAlignment(Qt.AlignVCenter|Qt.AlignRight)
        if n==None:
            a.setForeground(QColor(0, 0, 255))
        elif n<0:
            a.setForeground(QColor(255, 0, 0))
        return a

    def suma_d(self,cur, money, dattime):
        """Suma al money actual el pasado como parametro y consultando el valor de la divisa en date"""
        return


    def suma(self,money, quote):
        return


class SetDPS:
    def __init__(self, mem,  product):
        self.arr=[]
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
        
    def find(self, id):
        """Como puede no haber todos los años se usa find que devuelve una estimacion nula sino existe"""
        for e in self.arr:
            if e.id==id:
                return e
        return None
            
        
    def sort(self):
        self.arr=sorted(self.arr, key=lambda c: c.date,  reverse=False)         
        
    def myqtablewidget(self, table):
        table.setColumnCount(2)
        table.setHorizontalHeaderItem(0, QTableWidgetItem(QApplication.translate("Core", "Date" )))
        table.setHorizontalHeaderItem(1, QTableWidgetItem(QApplication.translate("Core", "Gross" )))
        self.sort()   
        table.clearContents()
        table.setRowCount(len(self.arr))
        for i, e in enumerate(self.arr):
            table.setItem(i, 0, qcenter(str(e.date)))
            table.setItem(i, 1, self.product.currency.qtablewidgetitem(e.gross, 6))       
        table.setCurrentCell(len(self.arr)-1, 0)
        
    def sum(self, date):
        """Devuelve la suma de los dividends desde hoy hasta la fecha.
        Se deben restar a la cotización  del dia date, para tener la cotización sin descontar dividends"""
        self.sort()
        sum=0
        for dps in reversed(self.arr):
            if dps.date>=date:
                sum=sum+dps.gross
            else:
                break
        return sum
        

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
        """Hay que tener presente que endlastyear (Objeto Quote) es el endlastyear del año actual
        Necesita tener cargado en id el endlastyear """
        try:
            return self.estimation*100/self.product.result.basic.last.quote
        except:
            return None



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
        self.tpc=None
        self.mode=None#Anterior mode investmentmode
        self.apalancado=None
        self.stockexchange=None
        self.ticker=None
        self.priority=None
        self.priorityhistorical=None
        self.comentario=None
        self.obsolete=None
        
        self.result=None#Variable en la que se almacena QuotesResult
        self.estimations_dps=SetEstimationsDPS(self.mem, self)#Es un diccionario que guarda objetos estimations_dps con clave el año
        self.estimations_eps=SetEstimationsEPS(self.mem, self)
        self.dps=SetDPS(self.mem, self)

    def __repr__(self):
        return "{0} ({1}) de la {2}".format(self.name , self.id, self.stockexchange.name)
                
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
        self.tpc=row['tpc']
        self.mode=self.mem.investmentsmodes.find_by_id(row['pci'])
        self.apalancado=self.mem.leverages.find_by_id(row['apalancado'])
        self.stockexchange=self.mem.stockexchanges.find_by_id(row['id_bolsas'])
        self.ticker=row['ticker']
        self.priority=SetPriorities(self.mem).init__create_from_db(row['priority'])
        self.priorityhistorical=SetPrioritiesHistorical(self.mem).init__create_from_db(row['priorityhistorical'])
        self.comentario=row['comentario']
        self.obsolete=row['obsolete']
        
        self.result=QuotesResult(self.mem,self)
        return self

    def init__create(self, name,  isin, currency, type, agrupations, active, web, address, phone, mail, tpc, mode, apalancado, bolsa, ticker, priority, priorityhistorical, comentario, obsolete, id=None):
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
        self.tpc=tpc
        self.mode=mode
        self.apalancado=apalancado        
        self.stockexchange=id_stockexchanges
        self.ticker=ticker
        self.priority=priority
        self.priorityhistorical=priorityhistorical
        self.comentario=comentario
        self.obsolete=obsolete
        
        self.result=QuotesResult(self.mem,self)
        return self        

    def init__db(self, id):
        """Se pasa id porque se debe usar cuando todavía no se ha generado."""
        cur=self.mem.con.cursor()
        cur.execute("select * from products where id=%s", (id, ))
        row=cur.fetchone()
        cur.close()
        return self.init__db_row(row)

    def save(self):
        """Esta función inserta una inversión manual"""
        """Los arrays deberan pasarse como parametros ARRAY[1,2,,3,] o None"""
        
        cur=self.mem.con.cursor()
        if self.id==None:
            cur.execute(" select min(id)-1 from products;")
            id=cur.fetchone()[0]
            cur.execute("insert into products (id, name,  isin,  currency,  type,  agrupations,   web, address,  phone, mail, tpc, pci,  apalancado, id_bolsas, ticker, priority, priorityhistorical , comentario,  obsolete) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",  (id, self.name,  self.isin,  self.currency.id,  self.type.id,  self.agrupations.dbstring(), self.web, self.address,  self.phone, self.mail, self.tpc, self.mode.id,  self.apalancado.id, self.stockexchange.id, self.ticker, self.priority.array_of_id(), self.priorityhistorical.array_of_id() , self.comentario, self.obsolete))
            self.id=id
        else:
            cur.execute("update products set name=%s, isin=%s,currency=%s,type=%s, agrupations=%s, web=%s, address=%s, phone=%s, mail=%s, tpc=%s, pci=%s, apalancado=%s, id_bolsas=%s, ticker=%s, priority=%s, priorityhistorical=%s, comentario=%s, obsolete=%s where id=%s", ( self.name,  self.isin,  self.currency.id,  self.type.id,  self.agrupations.dbstring(),  self.web, self.address,  self.phone, self.mail, self.tpc, self.mode.id,  self.apalancado.id, self.stockexchange.id, self.ticker, self.priority.array_of_id(), self.priorityhistorical.array_of_id() , self.comentario, self.obsolete,  self.id))
        cur.close()
    

    def has_autoupdate(self):
        """Return if the product has autoupdate in some source
        REMEMBER TO CHANGE on_actionProductsAutoUpdate_triggered en frmMain"""
        if self.obsolete==True:
            return False
        #With isin
        if self.priority.find_by_id(9)!=None or self.priorityhistorical.find_by_id(8)!=None:
            if self.isin==None or self.isin=="":
                return False
            return True
            
        #With ticker
        if self.priority.find_by_id(1)!=None or self.priorityhistorical.find_by_id(3)!=None:
            if self.ticker==None or self.ticker=="":
                return False
            return True
            
        return False
        
        
        
    def is_deletable(self):
        if self.is_system():
            return False
            
        #Search in all investments
        for i in self.mem.data.investments_all().arr:
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
        
    def priorityhistorical_change(self):
        """Cambia la primera prioridad y la pone en último lugar"""
        idtochange=self.priorityhistorical[0]
        self.priorityhistorical.remove(idtochange)
        self.priorityhistorical.append(idtochange)
        cur.execute("update products set priorityhistorical=%s", (str(self.priorityhistorical)))

    def fecha_ultima_actualizacion_historica(self):
        resultado=datetime.date(self.mem.fillfromyear, 1, 1)
        cur=self.mem.con.cursor()
        cur.execute("select max(datetime)::date as date from quotes where date_part('microsecond',datetime)=4 and id=%s order by date", (self.id, ))
        if cur.rowcount==1:
            dat=cur.fetchone()[0]
            if dat!=None:
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
        tabla.clearContents() 
        tabla.setRowCount(len(self.arr))
        for rownumber, a in enumerate(self.arr):
            tabla.setItem(rownumber, 0, qdatetime(a.datetime, self.mem.localzone))
            tabla.setItem(rownumber, 1, qleft(a.product.name))
            tabla.item(rownumber, 1).setIcon(a.product.stockexchange.country.qicon())
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
                dt_end=day_end(row['datetime'], self.product.stockexchange.zone)
            if row['datetime']>dt_end:#Cambio de SetQuotesIntraday
                self.arr.append(SetQuotesIntraday(self.mem).init__create(self.product, dt_end.date(), intradayarr))
                dt_end=day_end(row['datetime'], self.product.stockexchange.zone)
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
                return sql.find_by_id(dattime)
        print (function_name(self), "Quote not found")
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
        self.endlastyear=None
        self.last=None
        self.penultimate=None
        self.product=product       
        
    def init__create(self, last,  penultimate, endlastyear):
        self.last=last
        self.penultimate=penultimate
        self.endlastyear=endlastyear
        return self
       
    
    def load_from_db(self):
        """Función que calcula last, penultimate y lastdate """
        triplete=Quote(self.mem).init__from_query_triplete(self.product)
        if triplete!=None:
            self.endlastyear=triplete[0]
            self.penultimate=triplete[1]
            self.last=triplete[2]
#            print ("Por triplete {0}".format(str(datetime.datetime.now()-inicio)))
        else:
            self.last=Quote(self.mem).init__from_query(self.product,  self.mem.localzone.now())
            if self.last.datetime!=None: #Solo si hay last puede haber penultimate
                self.penultimate=Quote(self.mem).init__from_query_penultima(self.product, dt_changes_tz(self.last.datetime, self.mem.localzone).date())
            else:
                self.penultimate=Quote(self.mem).init__create(self.product, None, None)
            self.endlastyear=Quote(self.mem).init__from_query(self.product,  datetime.datetime(datetime.date.today().year-1, 12, 31, 23, 59, 59, tzinfo=pytz.timezone('UTC')))

    def tpc_diario(self):
        if self.penultimate==None or self.last==None:
            return None
        if self.penultimate.quote==0 or self.penultimate.quote==None or self.last.quote==None:
            return None
        return round((self.last.quote-self.penultimate.quote)*100/self.penultimate.quote, 2)

    def tpc_anual(self):
        if self.endlastyear.quote==None or self.endlastyear.quote==0 or self.last.quote==None:
            return None
        else:
            return round((self.last.quote-self.endlastyear.quote)*100/self.endlastyear.quote, 2)       

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
        iniciodia=day_start_from_date(date, self.product.stockexchange.zone)
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
        print (function_name(self), "Quote not found")
        return None

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
        return Decimal(100*(h-l)/l)
        
        
class Quote:
    """"Un quote no puede estar duplicado en un datetime solo puede haber uno"""
    def __init__(self, mem):
        self.mem=mem
        self.product=None
        self.quote=None
        self.datetime=None
        self.datetimeasked=None
        
    def __repr__(self):
        return "Quote de {0} de fecha {1} vale {2}".format(self.product.name, self.datetime, self.quote)

        
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

    def init__db_row(self, row, product,   datetimeasked=None):
        """si datetimeasked es none se pone la misma fecha"""
        self.product=product
        self.quote=row['quote']
        self.datetime=row['datetime']
        if datetimeasked==None:
            self.datetimeasked=row['datetime']
        return self
        
        
    def init__from_query(self, product, dt): 
        """Función que busca el quote de un id y datetime con timezone"""
        cur=self.mem.con.cursor()
        sql="select * from quote(%s, '%s'::timestamptz)" %(product.id,  dt)
        cur.execute(sql)
        row=cur.fetchone()
        cur.close()
        return self.init__db_row(row, product,  dt)
                
    def init__from_query_penultima(self,product,  lastdate=None):
        cur=self.mem.con.cursor()
        if lastdate==None:
            cur.execute("select * from penultimate(%s)", (product.id, ))
        else:
            cur.execute("select * from penultimate(%s,%s)", (product.id, lastdate ))
        row=cur.fetchone()
        cur.close()
        return self.init__db_row(row, product)        
        
    def init__from_query_triplete(self, product): 
        """Función que busca el last, penultimate y endlastyear de golpe
       Devuelve un array de Quote en el que arr[0] es endlastyear, [1] es penultimate y [2] es last
      Si no devuelve tres Quotes devuelve None y deberaá calcularse de otra forma"""
        cur=self.mem.con.cursor()
        endlastyear=dt(datetime.date(datetime.date.today().year -1, 12, 31), datetime.time(23, 59, 59), self.mem.localzone)
        cur.execute("select * from quote (%s, now()) union all select * from penultimate(%s) union all select * from quote(%s,%s) order by datetime", (product.id, product.id, product.id,  endlastyear))
        if cur.rowcount!=3:
            cur.close()
            return None
        resultado=[]
        for row in  cur:
            if row['datetime']==None: #Pierde el orden y no se sabe cual es cual
                cur.close()
                return None
            resultado.append(Quote(self.mem).init__db_row(row, product))
        cur.close()
        return resultado

class OHCLDaily:
    def __init__(self, mem):
        self.mem=mem
        self.product=None
        self.date=None
        self.open=None
        self.close=None
        self.high=None
        self.low=None
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
        return day_end_from_date(self.date, self.product.stockexchange.zone)
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
        
        
class OHCLMonthly:
    def __init__(self, mem):
        self.mem=mem
        self.product=None
        self.year=None
        self.month=None
        self.open=None
        self.close=None
        self.high=None
        self.low=None
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
        return day_end_from_date(datetime.date(self.year, self.month, 28), self.product.stockexchange.zone)
        
        
    def delete(self):
        """Removes all quotes of the selected month and year"""
        cur=self.mem.con.cursor()
        cur.execute("delete from quotes where id=%s and date_part('month',datetime)=%s and date_part('year',datetime)=%s", (self.product.id, self.month, self.year))
        cur.close()        
                
class OHCLWeekly:
    def __init__(self, mem):
        self.mem=mem
        self.product=None
        self.year=None
        self.week=None
        self.open=None
        self.close=None
        self.high=None
        self.low=None
        
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
#        return d + dlt,  d + dlt + timedelta(days=6) ## first day, end day
        lastday= d + dlt + datetime.timedelta(days=6)
        return day_end_from_date(lastday, self.product.stockexchange.zone)
        
    def print_time(self):
        return "{0}-{1}".format(self.year, self.week)
class OHCLYearly:
    def __init__(self, mem):
        self.mem=mem
        self.product=None
        self.year=None
        self.open=None
        self.close=None
        self.high=None
        self.low=None
        
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
        return day_end_from_date(datetime.date(self.year, 12, 31), self.product.stockexchange.zone)
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
        
        
    def length(self):
        return len (self.arr)


    def append(self, o):
        self.arr.append(o)
        
        
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
        endlastyear=None
        if len(self.arr)==0:
            return SetQuotesBasic(self.mem, self.product).init__create(None, None,  None)
        ohcl=self.arr[len(self.arr)-1]#last
        last=Quote(self.mem).init__create(self.product, dt(ohcl.date, self.product.stockexchange.closes,  self.product.stockexchange.zone), ohcl.close)
        ohcl=self.find_by_id(ohcl.date-datetime.timedelta(days=1))#penultimate
        if ohcl!=None:
            penultimate=Quote(self.mem).init__create(self.product, dt(ohcl.date, self.product.stockexchange.closes,  self.product.stockexchange.zone), ohcl.close)
        ohcl=self.find_by_id(datetime.date(datetime.date.today().year-1, 12, 31))#endlastyear
        if ohcl!=None:
            endlastyear=Quote(self.mem).init__create(self.product, dt(ohcl.date, self.product.stockexchange.closes,  self.product.stockexchange.zone), ohcl.close)        
        return SetQuotesBasic(self.mem, self.product).init__create(last, penultimate, endlastyear)
               
class SetOHCLWeekly(SetOHCL):
    def __init__(self, mem, product):
        SetOHCL.__init__(self, mem, product)
        self.itemclass=OHCLWeekly
        
class SetOHCLYearly(SetOHCL):
    def __init__(self, mem, product):
        SetOHCL.__init__(self, mem, product)
        self.itemclass=OHCLYearly
        
class SetOHCLMonthly(SetOHCL):
    def __init__(self, mem, product):
        SetOHCL.__init__(self, mem, product)
        self.itemclass=OHCLMonthly

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
        self.mem.qtranslator.load("/usr/lib/xulpymoney/xulpymoney_" + id + ".qm")
        qApp.installTranslator(self.mem.qtranslator);

 
class OHCL:
    def __init__(self, product, datetime, open, close, high, low ):
        self.product=product
        self.datetime=datetime
        self.open=open
        self.close=close
        self.high=high
        self.low=low
        
    def get_interval(self, ohclposterior):
        """Calcula el intervalo entre dos ohcl. El posteror es el que se pasa como parámetro"""
        return ohclposterior.datetime-self.datetime

        
class QuotesResult:
    """Función que consigue resultados de mystocks de un id pasado en el constructor"""
    def __init__(self,mem,  product):
        self.mem=mem
        self.product=product
        
        self.intradia=SetQuotesIntraday(self.mem)
        self.all=SetQuotesAllIntradays(self.mem)
        self.basic=SetQuotesBasic(self.mem, self.product)
        self.ohclDaily=SetOHCLDaily(self.mem, self.product)
        self.ohclMonthly=SetOHCLMonthly(self.mem, self.product)
        self.ohclYearly=SetOHCLYearly(self.mem, self.product)
        self.ohclWeekly=SetOHCLWeekly(self.mem, self.product)
        
    def get_basic_and_ohcls(self):
        """Tambien sirve para recargar"""
        inicio=datetime.datetime.now()
        self.ohclDaily.load_from_db("select * from ohlcdaily where id={0} order by date".format(self.product.id))#necesario para usar luego ohcl_otros
        self.ohclMonthly.load_from_db("select * from ohlcMonthly where id={0} order by year,month".format(self.product.id))
        self.ohclWeekly.load_from_db("select * from ohlcWeekly where id={0} order by year,week".format(self.product.id))
        self.ohclYearly.load_from_db("select * from ohlcYearly where id={0} order by year".format(self.product.id))
        self.basic=self.ohclDaily.setquotesbasic()
        print ("Datos db cargados:",  datetime.datetime.now()-inicio)


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
        for inv in self.mem.data.investments_all().arr:
            if inv.product.id==self.product.id:
                for oi in inv.op.arr:
                    if self.dtinitial<=oi.datetime and self.dtfinal>=oi.datetime:
                        oi.acciones=self.convertShares(oi.acciones)
                        oi.valor_accion=self.convertPrices(oi.valor_accion)
                        oi.save(autocommit=False)

        
    def updateDividends(self):
        """Transforms de dpa of an array of dividends"""
        for inv in self.mem.data.investments_all().arr:
            if inv.product.id==self.product.id:
                dividends=SetDividends(self.mem)
                dividends.load_from_db("select * from dividends where id_inversiones={0} order by fecha".format(inv.id ))  
                for d in dividends.arr:
                    if self.dtinitial.date()<=d.fecha and self.dtfinal.date()>=d.fecha:
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
        
class TUpdateData(threading.Thread):
    """Hilo que actualiza las products, solo el getBasic, cualquier cambio no de last, deberá ser desarrollado por código"""
    def __init__(self, mem):
        threading.Thread.__init__(self)
        self.mem=mem
        
    def run(self):
        print ("TUpdateData started")
        while True:
            inicio=datetime.datetime.now()
            
            ##Selecting products to update
            if self.mem.data.loaded_inactive==False:
                products=self.mem.data.products_active
            else:
                products=self.mem.data.products_all()
                
            self.mem.data.benchmark.result.basic.load_from_db()
            
            ##Update loop
            for inv in products.arr:
                if self.mem.closing==True:
                    return
                inv.result.basic.load_from_db()
            print("TUpdateData loop took", datetime.datetime.now()-inicio)
            
            ##Wait loop
            for i in range(60):
                if self.mem.closing==True:
                    return
                time.sleep(1)

class Type:
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
        self.stockexchange=None

        
    def init__create(self, id,  name, type, bolsa):
        self.id=id
        self.name=name
        self.type=type
        self.stockexchange=bolsa
        return self
        
class SetTypes(SetCommons):
    def __init__(self, mem):
        SetCommons.__init__(self)
        self.mem=mem
        
            
    def load_all(self):
        self.append(Type().init__create(1,QApplication.translate("Core","Shares")))
        self.append(Type().init__create(2,QApplication.translate("Core","Funds")))
        self.append(Type().init__create(3,QApplication.translate("Core","Indexes")))
        self.append(Type().init__create(4,QApplication.translate("Core","ETF")))
        self.append(Type().init__create(5,QApplication.translate("Core","Warrants")))
        self.append(Type().init__create(6,QApplication.translate("Core","Currencies")))
        self.append(Type().init__create(7,QApplication.translate("Core","Public Bond")))
        self.append(Type().init__create(8,QApplication.translate("Core","Pension plans")))
        self.append(Type().init__create(9,QApplication.translate("Core","Private Bond")))
        self.append(Type().init__create(10,QApplication.translate("Core","Deposit")))
        self.append(Type().init__create(11,QApplication.translate("Core","Accounts")))

    def products(self):
        return {k:v for k,v in self.dic_arr.items() if k in ("1", "2", "4", "5", "7","8")}

class Language:
    def __init__(self, mem, id, name):
        self.id=id
        self.name=name
    
            
class Maintenance:
    """Funciones de mantenimiento y ayuda a la programaci´on y depuraci´on"""
    def __init__(self, mem):
        self.mem=mem
        
    def regenera_todas_opercuentasdeoperinversiones(self):
        self.mem.data.load_inactives()
        for inv in self.mem.data.investments_all().arr:
            print (inv)
            inv.actualizar_cuentasoperaciones_asociadas()
        self.mem.con.commit()        
        
        
    def show_investments_status(self, date):
        """Shows investments status in a date"""
        datet=dt(date, datetime.time(22, 00), self.mem.localzone)
        sumbalance=0
        print ("{0:<40s} {1:>15s} {2:>15s} {3:>15s}".format("Investments at {0}".format(date), "Shares", "Price", "Balance"))
        for inv in self.mem.data.investments_all().arr:
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
        return None

class MemXulpymoney:
    def __init__(self):        
        self.adminmode=False # from argv
        
        self.qtranslator=None#Residir´a el qtranslator
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
        
    def init__script(self, title):
        """Script arguments and autoconnect in mem.con, load_db_data"""
        parser=argparse.ArgumentParser(title)
        parser.add_argument('-U', '--user', help='Postgresql user', default='postgres')
        parser.add_argument('-p', '--port', help='Postgresql server port', default=5432)
        parser.add_argument('-H', '--host', help='Postgresql server address', default='127.0.0.1')
        parser.add_argument('-d', '--db', help='Postgresql database', default='xulpymoney')
        args=parser.parse_args()
        password=getpass.getpass()
        
        (self.con, err)=self.connect(args.db, args.port, args.user, args.host, password)
        if self.con==None:
            print (err)
            sys.exit(255)        
        
        self.load_db_data()


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
        

    def load_db_data(self):
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
        
        self.stockexchanges=SetStockExchanges(self)
        self.stockexchanges.load_all_from_db()
        
        self.agrupations=SetAgrupations(self)
        self.agrupations.load_all()

        self.leverages=SetLeverages(self)
        self.leverages.load_all()

        self.data=DBData(self)
        self.data.load_actives()
        
        #mem Variables con base de datos
        self.dividendwithholding=Decimal(self.settingsdb.value("mem/dividendwithholding", "0.19"))
        self.taxcapitalappreciation=Decimal(self.settingsdb.value("mem/taxcapitalappreciation", "0.19"))
        self.taxcapitalappreciationbelow=Decimal(self.settingsdb.value("mem/taxcapitalappreciationbelow", "0.5"))
        self.gainsyear=str2bool(self.settingsdb.value("mem/gainsyear", "False"))
        self.favorites=string2list(self.settingsdb.value("mem/favorites", ""))
        self.fillfromyear=int(self.settingsdb.value("mem/fillfromyear", "2005"))
        
        print ("Loading db data took {}".format(datetime.datetime.now()-inicio))
        
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
        print ("Saved Database settings")
        
        
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

## FUNCTIONS #############################################

def ampm_to_24(hora, pmam):
    #    Conversión de AM/PM a 24 horas
    #  	  	 
    #  	Para la primera hora del día (de medianoche a 12:59 AM), resta 12 horas
    #  	  	Ejemplos: 12 de medianoche = 0:00, 12:35 AM = 0:35
    #  	  	 
    #  	De 1:00 AM a 12:59 PM, no hay cambios
    #  	  	Ejemplos: 11:20 AM = 11:20, 12:30 PM = 12:30
    #  	  	 
    #  	De 1:00 PM a 11:59 PM, suma 12 horas
    #  	  	Ejemplos: 4:45 PM = 16:45, 11:50 PM = 23:50
    if pmam=="am" and hora==12:
        return 12-12
    elif pmam=="pm" and hora >=1 and hora<= 11:
        return hora+12
    else:
        return hora

        
def dt_changes_tz(dt,  tztarjet):
    """Cambia el zoneinfo del dt a tztarjet. El dt del parametre tiene un zoneinfo"""
    if dt==None:
        return None
    tzt=pytz.timezone(tztarjet.name)
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


def qdatetime(dt, zone,  pixmap=True):
    """dt es un datetime con timezone
    dt, tiene timezone, 
    Convierte un datetime a string, teniendo en cuenta los microsehgundos, para ello se convierte a datetime local
    SE PUEDE OPTIMIZAR
    No hace falta cambiar antes a dt con local.config, ya que lo hace la función
    """
    if dt==None:
        resultado="None"
    else:    
        dt=dt_changes_tz(dt,  zone)#sE CONVIERTE A LOCAL DE dt_changes_tz 2012-07-11 08:52:31.311368-04:00 2012-07-11 14:52:31.311368+02:00
        if dt.microsecond==4 :
            resultado=str(dt.date())
        else:
            resultado=str(dt.date())+" "+str(dt.hour).zfill(2)+":"+str(dt.minute).zfill(2)+":"+str(dt.second).zfill(2)
#        else:
#            resultado=str(dt.date())+" "+str(dt.hour).zfill(2)+":"+str(dt.minute).zfill(2)   
    a=QTableWidgetItem(resultado)
    if dt==None:
        a.setForeground(QColor(0, 0, 255))
    a.setTextAlignment(Qt.AlignVCenter|Qt.AlignRight)
    return a

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

def qtpc(n, rnd=2):
    text= tpc(n, rnd)
    a=QTableWidgetItem(text)
    a.setTextAlignment(Qt.AlignVCenter|Qt.AlignRight)
    if n==None:
        a.setForeground(QColor(0, 0, 255))
    elif n<0:
        a.setForeground(QColor(255, 0, 0))
    return a
#      
#def QApplication.translate("Core",s):
#    return QApplication.translate("Core",  s)
#    


def tpc(n, rnd=2):
    if n==None:
        return "None %"
    return str(round(n, rnd))+ " %"

        
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
