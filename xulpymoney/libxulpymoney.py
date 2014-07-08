from PyQt4.QtCore import *
from PyQt4.QtGui import *
import datetime,  time,  pytz,   psycopg2,  psycopg2.extras,  sys,  codecs,  urllib.request,    os,  configparser,  inspect,  threading

from decimal import *

version="20140517"

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
        self.cuenta=None
        self.operinversion=None
        self.inversion=None
        
    def init__create(self, datetime,  concepto, tipooperacion, importe, comentario, cuenta, operinversion, inversion, id=None):
        self.datetime=datetime
        self.concepto=concepto
        self.tipooperacion=tipooperacion
        self.importe=importe
        self.comentario=comentario
        self.cuenta=cuenta
        self.operinversion=operinversion
        self.inversion=inversion
        return self

    def save(self):
        cur=self.mem.con.cursor()
        if self.id==None:
            cur.execute("insert into opercuentasdeoperinversiones (datetime, id_conceptos, id_tiposoperaciones, importe, comentario,id_cuentas, id_operinversiones,id_inversiones) values ( %s,%s,%s,%s,%s,%s,%s,%s) returning id_opercuentas", (self.datetime, self.concepto.id, self.tipooperacion.id, self.importe, self.comentario, self.cuenta.id, self.operinversion.id, self.inversion.id))
            self.id=cur.fetchone()[0]
        else:
            cur.execute("UPDATE FALTA  set datetime=%s, id_conceptos=%s, id_tiposoperaciones=%s, importe=%s, comentario=%s, id_cuentas=%s where id_opercuentas=%s", (self.datetime, self.concepto.id, self.tipooperacion.id,  self.importe,  self.comentario,  self.cuenta.id,  self.id))
        cur.close()
        self.cuenta.saldo_from_db()

class SetInvestments:
    def __init__(self, mem, cuentas, products, benchmark):
        self.arr=[]
        self.mem=mem
        self.cuentas=cuentas
        self.products=products
        self.benchmark=benchmark  ##Objeto product
            
    def load_from_db(self, sql,  progress=False):
        cur=self.mem.con.cursor()
        cur.execute(sql)#"Select * from inversiones"
        if progress==True:
            pd= QProgressDialog(QApplication.translate("Core","Loading {0} products from database".format(cur.rowcount)),None, 0,cur.rowcount)
            pd.setModal(True)
            pd.setWindowTitle(QApplication.translate("Core","Loading products..."))
            pd.forceShow()
        for row in cur:
            if progress==True:
                pd.setValue(cur.rownumber)
                pd.update()
                QApplication.processEvents()
            inv=Investment(self.mem).init__db_row(row,  self.cuentas.find(row['id_cuentas']), self.products.find(row['mystocksid']))
            inv.get_operinversiones()
            inv.op_actual.get_valor_benchmark(self.benchmark)
            self.arr.append(inv)
#            stri="{0}: {1}/{2}          ".format(function_name(self), cur.rownumber, cur.rowcount)
#            sys.stdout.write("\b"*1000+stri)
#            sys.stdout.flush()
        cur.close()  
        
    def list_distinct_mystocksid(self):
        """Función que devuelve una lista con los distintos mystocksid """
        resultado=set([])
        for inv in self.arr:
            resultado.add(inv.product.id)
        return list(resultado)
            
            
                
        ##Conviert cur a lista separada comas
        lista=""
        for row in cur:
            lista=lista+ str(row['mystocksid']) + ", "
        lista=lista[:-2]
    
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
        
    def find(self, id):
        for i in self.arr:
            if i.id==id:
                return i
        print ("No se ha encontrado la inversión {0} en SetInvestments.inversion".format(id))
        return None
        
    
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
    
    def union(self, list2):
        """Devuelve un SetBanks con la union del set1 y del set2"""
        resultado=SetInvestments(self.mem, self.cuentas, self.products, self.benchmark)
        resultado.arr=self.arr+list2.arr
        return resultado


    def qcombobox_same_investmentmq(self, combo,  investmentmq):
        """Muestra las inversiones activas que tienen el mq pasado como parametro"""
        arr=[]
        for i in self.arr:
            print (i.product, investmentmq)
            if i.activa==True and i.product==investmentmq:
                arr.append(("{0} - {1}".format(i.cuenta.eb.name, i.name), i.id))
                        
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
                if i.activa==False:
                    continue
            elif activas==False:
                if i.activa==True:
                    continue
            if tipo==0:
                arr.append((i.name, i.id))            
            elif tipo==1:
                arr.append(("{0} - {1}".format(i.cuenta.eb.name, i.name), i.id))
                
        
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
            op_cuenta=AccountOperation(self.mem).init__create(now.date(), self.mem.conceptos.find(38), self.mem.tiposoperaciones.find(1), -comision, "Traspaso de valores", origen.cuenta)
            op_cuenta.save()       
            origen.cuenta.saldo_from_db()        
            comentario="{0}|{1}".format(destino.id, op_cuenta.id)
        else:
            comentario="{0}|{1}".format(destino.id, "None")
        
        op_origen=InvestmentOperation(self.mem).init__create( self.mem.tiposoperaciones.find(9), now, origen,  -numacciones, 0,0, comision, 0, comentario)
        op_origen.save( False)      

        #NO ES OPTIMO YA QUE POR CADA SAVE SE CALCULA TODO
        comentario="{0}".format(op_origen.id)
        for o in origen.op_actual.arr:
            op_destino=InvestmentOperation(self.mem).init__create( self.mem.tiposoperaciones.find(10), now, destino,  o.acciones, o.importe, o.impuestos, o.comision, o.valor_accion, comentario)
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
        destino=self.find(int(id_inversiondestino))
        cur=self.mem.con.cursor()
#        print (cur.mogrify("delete from operinversiones where id_tiposoperaciones=10 and id_inversiones=%s and comentario=%s", (id_inversiondestino, str(operinversionorigen.id))))

        cur.execute("delete from operinversiones where id_tiposoperaciones=10 and id_inversiones=%s and comentario=%s", (destino.id, str(operinversionorigen.id)))
        cur.execute("delete from operinversiones where id_operinversiones=%s", (operinversionorigen.id, ))
        if id_opercuentacomision!="None":
            cur.execute("delete from opercuentas where id_opercuentas=%s", (int(id_opercuentacomision), ))
            origen.cuenta.saldo_from_db()
            
        self.mem.con.commit()
        origen.get_operinversiones()
        destino.get_operinversiones()
        cur.close()
        return True
        
    def sort_by_percentage(self):
        try:
            self.arr=sorted(self.arr, key=lambda inv: inv.product.estimations_dps.currentYear().percentage(),  reverse=True) 
        except:
            print ("No se ha podido ordenar por haber estimaciones de dividend nulas")
        
        
class SetProducts:
    def __init__(self, mem):
        self.arr=[]
        self.mem=mem
    def load_from_inversiones_query(self, sql):
        """sql es una query sobre la tabla inversiones"""
        cur=self.mem.con.cursor()
        cur.execute(sql)#"Select distinct(mystocksid) from inversiones"
        ##Conviert cur a lista separada comas
        lista=""
        for row in cur:
            lista=lista+ str(row['mystocksid']) + ", "
        lista=lista[:-2]
        cur.close()
        
        ##Carga los products
        if len(lista)>0:
            self.load_from_db("select * from products where id in ("+lista+")", progress=True )
        
    def load_from_db(self, sql,  progress=False):
        """sql es una query sobre la tabla inversiones
        Carga estimations_dbs, y basic
        """
        curms=self.mem.conms.cursor()
        curms.execute(sql)#"select * from products where id in ("+lista+")" 
        if progress==True:
            pd= QProgressDialog(QApplication.translate("Core","Loading {0} MyStocks products from database".format(curms.rowcount)),None, 0,curms.rowcount)
            pd.setModal(True)
            pd.setWindowTitle(QApplication.translate("Core","Loading MyStocks products..."))
            pd.forceShow()
        for rowms in curms:
            if progress==True:
                pd.setValue(curms.rownumber)
                pd.update()
                QApplication.processEvents()
                
            inv=Product(self.mem).init__db_row(rowms)
            inv.estimations_dps.load_from_db()
            inv.result.basic.load_from_db()
            self.arr.append(inv)
        curms.close()
#            stri="{0}: {1}/{2}          ".format(function_name(self), curms.rownumber, curms.rowcount)
#            sys.stdout.write("\b"*1000+stri)
#            sys.stdout.flush()
#        print("")
                           
    def find(self, id):
        """Devuelve el objeto product con id pasado como parámetro y None si no lo encuentra"""
        for a in self.arr:
            if a.id==id:
                return a
        return None
                
    def union(self, list2):
        """Devuelve un SetBanks con la union del set1 y del set2"""
        resultado=SetProducts(self.mem)
        resultado.arr=self.arr+list2.arr
        return resultado

    def qcombobox(self, combo, selected=None):
        """Show products in a combo with a flag and the code as data
        Selected is a product id."""
        self.sort_by_name()
        for p in self.arr:
            combo.addItem(p.name, p.id)
        if selected!=None:
                combo.setCurrentIndex(combo.findData(selected))
    def sort_by_name(self):
        self.arr=sorted(self.arr, key=lambda c: c.name,  reverse=False)      
class SetProductsModes:
    """Agrupa los mode"""
    def __init__(self, mem):
        self.dic_arr={}
        self.mem=mem     
    
    def load_all(self):
        self.dic_arr['p']=ProductMode(self.mem).init__create("p",QApplication.translate("Core","Put"))
        self.dic_arr['c']=ProductMode(self.mem).init__create("c",QApplication.translate("Core","Call"))
        self.dic_arr['i']=ProductMode(self.mem).init__create("i",QApplication.translate("Core","Inline"))
        
    def qcombobox(self, combo):
        """Carga conceptos operaciones 1,2,3"""
        for c in self.list():
            combo.addItem(c.name, c.id)

    def find(self, id):
        return self.dic_arr[str(id)]
        
    def list(self):
        """Lista ordenada por nombre"""
        lista=dic2list(self.dic_arr)
        lista=sorted(lista, key=lambda c: c.name  ,  reverse=False)    
        return lista
        
        
class SetStockExchanges:
    def __init__(self, mem):
        self.dic_arr={}
        self.mem=mem     
    
    def load_all_from_db(self):
        curms=self.mem.conms.cursor()
        curms.execute("Select * from bolsas")
        for row in curms:
            self.dic_arr[str(row['id_bolsas'])]=StockExchange(self.mem).init__db_row(row, self.mem.countries.find(row['country']))
        curms.close()
            
    def qcombobox(self, combo):
        for c in self.list():
            combo.addItem(c.country.qicon(), c.name, c.id)
            
    def find(self, id):
        return self.dic_arr[str(id)]
        
    def list(self):
        return dic2list(self.dic_arr)

        
        
class SetConcepts:      
    def __init__(self, mem):
        self.dic_arr={}
        self.mem=mem 
                 
    def append(self, concepto):
        self.dic_arr[str(concepto.id)]=concepto
        
    def load_from_db(self):
        cur=self.mem.con.cursor()
        cur.execute("Select * from conceptos")
        for row in cur:
            self.dic_arr[str(row['id_conceptos'])]=Concept(self.mem).init__db_row(row, self.mem.tiposoperaciones.find(row['id_tiposoperaciones']))
        cur.close()
                        
    def load_opercuentas_qcombobox(self, combo):
        """Carga conceptos operaciones 1,2,3, menos dividends y renta fija, no pueden ser editados, luego no se necesitan"""
        for c in self.list():
            if c.tipooperacion.id in (1, 2, 3):
                if c.id not in (39, 50, 62, 63, 65, 66):
                    combo.addItem("{0} -- {1}".format(  c.name,  c.tipooperacion.name),  c.id  )

    def load_dividend_qcombobox(self, combo,  select=None):
        """Select es un class Concept"""
        for n in (39, 50,  62):
            c=self.find(n)
            combo.addItem("{0} -- {1}".format(  c.name,  c.tipooperacion.name),  c.id   )
        if select!=None:
            combo.setCurrentIndex(combo.findData(select.id))
    def load_bonds_qcombobox(self, combo,  select=None):
        """Carga conceptos operaciones 1,2,3"""
        for n in (50, 63, 65, 66):
            c=self.find(n)
            combo.addItem("{0} -- {1}".format(  c.name,  c.tipooperacion.name),  c.id )
        if select!=None:
            combo.setCurrentIndex(combo.findData(select.id))
            
    def considered_dividends_in_totals(self):
        """El 63 es pago de cupon corrido y no es considerado dividend  a efectos de totales, sino gasto."""
        return[39, 50, 62, 65, 66]

    def find(self, id):
        return self.dic_arr[str(id)]
        
    def list(self):
        """Lista ordenada por nombre"""
        lista=dic2list(self.dic_arr)
        lista=sorted(lista, key=lambda c: c.name  ,  reverse=False)    
        return lista

    def clone_x_tipooperacion(self, id_tiposoperaciones):
        resultado=SetConcepts(self.mem)
        for k, v in self.dic_arr.items():
            if v.tipooperacion.id==id_tiposoperaciones:
                resultado.dic_arr[k]=v
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
        for k, v in self.dic_arr.items():
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
            
    def remove(self, concepto):
        #However, this mutates the existing dictionary so the contents of the dictionary changes for anybody else who has a reference to the same instance. To return a new dictionary, make a copy of the dictionary:
        new = dict(self.dic_arr)
        del new[str(concepto.id)]
        self.dic_arr=new


class SetCountries:
    def __init__(self, mem):
        self.dic_arr={}
        self.mem=mem   
        
    def load_all(self):
        self.dic_arr['es']=Country().init__create("es",QApplication.translate("Core","Spain"))
        self.dic_arr['be']=Country().init__create("be",QApplication.translate("Core","Belgium"))
        self.dic_arr['cn']=Country().init__create("cn",QApplication.translate("Core","China"))
        self.dic_arr['de']=Country().init__create("de",QApplication.translate("Core","Germany"))
        self.dic_arr['en']=Country().init__create("en",QApplication.translate("Core","United Kingdom"))
        self.dic_arr['eu']=Country().init__create("eu",QApplication.translate("Core","Europe"))
        self.dic_arr['fi']=Country().init__create("fi",QApplication.translate("Core","Finland"))
        self.dic_arr['fr']=Country().init__create("fr",QApplication.translate("Core","France"))
        self.dic_arr['ie']=Country().init__create("ie",QApplication.translate("Core","Ireland"))
        self.dic_arr['it']=Country().init__create("it",QApplication.translate("Core","Italy"))
        self.dic_arr['jp']=Country().init__create("jp",QApplication.translate("Core","Japan"))
        self.dic_arr['nl']=Country().init__create("nl",QApplication.translate("Core","Netherlands"))
        self.dic_arr['pt']=Country().init__create("pt",QApplication.translate("Core","Portugal"))
        self.dic_arr['us']=Country().init__create("us",QApplication.translate("Core","United States of America"))
        self.dic_arr['ro']=Country().init__create("ro",QApplication.translate("Core","Romanian"))
        self.dic_arr['ru']=Country().init__create("ru",QApplication.translate("Core","Rusia"))
                

    def list(self):
        """Devuelve una lista ordenada por name"""
        currencies=dic2list(self.dic_arr)
        currencies=sorted(currencies, key=lambda c: c.name,  reverse=False)         
        return currencies
        
    def find(self, id):
        return self.dic_arr[str(id)]
    def qcombobox(self, combo,  country=None):
        """Función que carga en un combo pasado como parámetro y con un SetAccounts pasado como parametro
        Se ordena por nombre y se se pasa el tercer parametro que es un objeto Account lo selecciona""" 
        self.sort()
        for cu in self.list():
            self.addItem(cu.qicon(), cu.name, cu.id)

        if country!=None:
                combo.setCurrentIndex(combo.findData(country.id))
class SetAccounts:     
    def __init__(self, mem,  setebs):
        self.arr=[]
        self.mem=mem   
        self.ebs=setebs

    def load_from_db(self, sql):
        cur=self.mem.con.cursor()
        cur2=self.mem.con.cursor()
        cur.execute(sql)#"Select * from cuentas"
        for row in cur:
            c=Account(self.mem).init__db_row(row, self.ebs.find(row['id_entidadesbancarias']))
            c.saldo_from_db()
            self.arr.append(c)
        cur.close()
        cur2.close()
                               
    def qcombobox(self, combo,  cuenta=None):
        """Función que carga en un combo pasado como parámetro y con un SetAccounts pasado como parametro
        Se ordena por nombre y se se pasa el tercer parametro que es un objeto Account lo selecciona""" 
        self.sort()
        for cu in self.arr:
            combo.addItem(cu.name, cu.id)
        if cuenta!=None:
                combo.setCurrentIndex(combo.findData(cuenta.id))
        
    def find(self, id):
        for a in self.arr:
            if a.id==id:
                return a
                
    def sort(self):
        self.arr=sorted(self.arr, key=lambda c: c.name,  reverse=False)         
    
            
    def union(self,  list2):
        """Devuelve un SetBanks con la union del set1 y del set2"""
        resultado=SetAccounts(self.mem, self.ebs)
        resultado.arr=self.arr+list2.arr
        return resultado

class SetAccountOperations:
    """Clase es un array ordenado de objetos newInvestmentOperation"""
    def __init__(self, mem):
        self.mem=mem
        self.arr=[]
        
    def append(self, objeto):
        self.arr.append(objeto)

        
    def load_from_db(self, sql):
        cur=self.mem.con.cursor()
        cur.execute(sql)#"Select * from opercuentas"
        for row in cur:        
            co=AccountOperation(self.mem).init__create(row['datetime'], self.mem.conceptos.find(row['id_conceptos']), self.mem.tiposoperaciones.find(row['id_tiposoperaciones']), row['importe'], row['comentario'],  self.mem.data.cuentas_all().find(row['id_cuentas']))
            self.arr.append(co)
        cur.close()
    
    def load_from_db_with_creditcard(self, sql):
        """Usado en unionall opercuentas y opertarjetas y se crea un campo id_tarjetas con el id de la tarjeta y -1 sino tiene es decir opercuentas"""
        cur=self.mem.con.cursor()
        cur.execute(sql)#"Select * from opercuentas"
        for row in cur:        
            if row['id_tarjetas']==-1:
                comentario=row['comentario']
            else:
                comentario=QApplication.translate("Core","Paid with {0}. {1}".format(self.mem.data.tarjetas_all().find(row['id_tarjetas']).name, row['comentario'] ), None, QApplication.UnicodeUTF8)
            
            co=AccountOperation(self.mem).init__create(row['datetime'], self.mem.conceptos.find(row['id_conceptos']), self.mem.tiposoperaciones.find(row['id_tiposoperaciones']), row['importe'], comentario,  self.mem.data.cuentas_all().find(row['id_cuentas']))
            self.arr.append(co)
        cur.close()
    def sort(self):       
        self.arr=sorted(self.arr, key=lambda e: e.datetime,  reverse=False) 
        
    def myqtablewidget(self, tabla, section, show_account=False):
        """Section es donde guardar en el config file, coincide con el nombre del formulario en el que está la tabla
        show_account muestra la cuenta cuando las opercuentas son de diversos cuentas (Estudios totales)"""
        ##HEADERS
        diff=0
        if show_account==True:
            tabla.setColumnCount(6)
            diff=1
        else:
            tabla.setColumnCount(5)
        tabla.setHorizontalHeaderItem(0, QTableWidgetItem(QApplication.translate(section, "Date", None, QApplication.UnicodeUTF8)))
        if show_account==True:
            tabla.setHorizontalHeaderItem(diff, QTableWidgetItem(QApplication.translate(section, "Account", None, QApplication.UnicodeUTF8)))
        tabla.setHorizontalHeaderItem(1+diff, QTableWidgetItem(QApplication.translate(section, "Concept", None, QApplication.UnicodeUTF8)))
        tabla.setHorizontalHeaderItem(2+diff,  QTableWidgetItem(QApplication.translate(section, "Amount", None, QApplication.UnicodeUTF8)))
        tabla.setHorizontalHeaderItem(3+diff, QTableWidgetItem(QApplication.translate(section, "Balance", None, QApplication.UnicodeUTF8)))
        tabla.setHorizontalHeaderItem(4+diff, QTableWidgetItem(QApplication.translate(section, "Comment", None, QApplication.UnicodeUTF8)))
        ##DATA 
        tabla.clearContents()
        tabla.settings(section,  self.mem)       
        tabla.setRowCount(len(self.arr))
        balance=0
        for rownumber, a in enumerate(self.arr):
            balance=balance+a.importe
            tabla.setItem(rownumber, 0, qdatetime(a.datetime, self.mem.localzone))
            if show_account==True:
                tabla.setItem(rownumber, diff, QTableWidgetItem(a.cuenta.name))
            tabla.setItem(rownumber, 1+diff, qleft(a.concepto.name))
            tabla.setItem(rownumber, 2+diff, self.mem.localcurrency.qtablewidgetitem(a.importe))
            tabla.setItem(rownumber, 3+diff, self.mem.localcurrency.qtablewidgetitem(balance))
            tabla.setItem(rownumber, 4+diff, qleft(a.comentario))

class SetCurrencies:
    def __init__(self, mem):
        self.dic_arr={}
        self.mem=mem   
    
    def load_all(self):
        self.dic_arr["CNY"]=Currency().init__create(QApplication.translate("Core","Chinese Yoan"), "¥", 'CNY')
        self.dic_arr['EUR']=Currency().init__create(QApplication.translate("Core","Euro"), "€", "EUR")
        self.dic_arr['GBP']=Currency().init__create(QApplication.translate("Core","Pound"),"£", 'GBP')
        self.dic_arr['JPY']=Currency().init__create(QApplication.translate("Core","Japones Yen"), '¥', "JPY")
        self.dic_arr['USD']=Currency().init__create(QApplication.translate("Core","American Dolar"), '$', 'USD')
        self.dic_arr['u']=Currency().init__create(QApplication.translate("Core","Units"), 'u', 'u')

    def list(self):
        """Devuelve una lista ordenada por id"""
        currencies=dic2list(self.dic_arr)
        currencies=sorted(currencies, key=lambda c: c.id,  reverse=False)         
        return currencies

    def find(self, id):
        return self.dic_arr[str(id)]

    def qcombobox(self, combo, selectedcurrency=None):
        """Función que carga en un combo pasado como parámetro las currencies"""
        for c in self.list():
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
            inversion=self.mem.data.inversiones_all().find(row['id_inversiones'])
            oc=AccountOperation(self.mem).init__db_query(row['id_opercuentas'])
            self.arr.append(Dividend(self.mem).init__db_row(row, inversion, oc, self.mem.conceptos.find(row['id_conceptos']) ))
        cur.close()      
        
    def sort(self):       
        self.arr=sorted(self.arr, key=lambda e: e.fecha,  reverse=False) 
        
    def myqtablewidget(self, table, section, show_investment=False):
        """Section es donde guardar en el config file, coincide con el nombre del formulario en el que está la table
        Devuelve sumatorios"""
        diff=0
        if show_investment==True:
            diff=1
        table.setColumnCount(7+diff)
        table.setHorizontalHeaderItem(0, QTableWidgetItem(QApplication.translate("Core", "Date", None, QApplication.UnicodeUTF8)))
        table.setHorizontalHeaderItem(diff, QTableWidgetItem(QApplication.translate("Core", "Product", None, QApplication.UnicodeUTF8)))
        table.setHorizontalHeaderItem(diff+1, QTableWidgetItem(QApplication.translate("Core", "Concept", None, QApplication.UnicodeUTF8)))
        table.setHorizontalHeaderItem(diff+2, QTableWidgetItem(QApplication.translate("Core", "Gross", None, QApplication.UnicodeUTF8)))
        table.setHorizontalHeaderItem(diff+3, QTableWidgetItem(QApplication.translate("Core", "Withholding", None, QApplication.UnicodeUTF8)))
        table.setHorizontalHeaderItem(diff+4, QTableWidgetItem(QApplication.translate("Core", "Comission", None, QApplication.UnicodeUTF8)))
        table.setHorizontalHeaderItem(diff+5, QTableWidgetItem(QApplication.translate("Core", "Net", None, QApplication.UnicodeUTF8)))
        table.setHorizontalHeaderItem(diff+6, QTableWidgetItem(QApplication.translate("Core", "DPS", None, QApplication.UnicodeUTF8)))
        #DATA
        table.settings(section,  self.mem)        
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
        cur=self.mem.conms.cursor()
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
        cur=self.mem.conms.cursor()
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

        
class SetBanks:     
    def __init__(self, mem):
        self.arr=[]
        self.mem=mem   
    def load_from_db(self, sql):
        cur=self.mem.con.cursor()
        cur.execute(sql)#"select * from entidadesbancarias"
        for row in cur:
            self.arr.append(Bank(self.mem).init__db_row(row))
        cur.close()            
        
    def find(self, id):
        for a in self.arr:
            if a.id==id:
                return a
                   
    def qcombobox(self, combo):
        """Carga entidades bancarias en combo. Es un SetBanks"""
        self.sort()
        for e in self.arr:
            combo.addItem(e.name, e.id)   
            
    def sort(self):       
        self.arr=sorted(self.arr, key=lambda e: e.name,  reverse=False) 
        
    def union(self,  list2):
        """Devuelve un SetBanks con la union del set1 y del set2"""
        resultado=SetBanks(self.mem)
        resultado.arr=self.arr+list2.arr
        return resultado

class SetInvestmentOperations:       
    """Clase es un array ordenado de objetos newInvestmentOperation"""
    def __init__(self, mem):
        self.mem=mem
        self.arr=[]
        
    def append(self, objeto):
        self.arr.append(objeto)
        
    def clone_from_datetime(self, dt):
        """Función que devuelve otro SetInvestmentOperations con las oper que tienen datetime mayor o igual a la pasada como parametro."""
        resultado=SetInvestmentOperations(self.mem)
        if dt==None:
            return self.clone()
        for a in self.arr:
            if a.datetime>=dt:
                resultado.append(a)
        return resultado
        
    def calcular_new(self):
        """Realiza los cálculos y devuelve dos arrays"""
        sioh=SetInvestmentOperationsHistorical(self.mem)
        sioa=SetInvestmentOperationsCurrent(self.mem)       
        for o in self.arr:      
#            print ("Despues ",  sioa.acciones(), o)              
            if o.acciones>=0:#Compra
                sioa.arr.append(InvestmentOperationCurrent(self.mem).init__create(o, o.tipooperacion, o.datetime, o.inversion, o.acciones, o.importe, o.impuestos, o.comision, o.valor_accion,  o.id))
            else:#Venta
                if abs(o.acciones)>sioa.acciones():
                    print (o.acciones, sioa.acciones(),  o)
                    print("No puedo vender más acciones que las que tengo. EEEEEEEEEERRRRRRRRRRRROOOOORRRRR")
                    sys.exit(0)
                sioa.historizar(o, sioh)
        return (sioa, sioh)
        
    def calcular(self ):
        """Realiza los calculos y devuelve dos arrys."""
        def comisiones_impuestos(dif, p, n):
            """Función que calcula lo simpuestos y las comisiones según el momento de actualizar
            en el que se encuentre"""
            (impuestos, comisiones)=(0, 0)
            if dif==0: #Coincide la compra con la venta 
                impuestos=n.impuestos+p.impuestos
                comisiones=n.comision+p.comision
                n.impuestos=0
                n.comision=0
                return (impuestos, comisiones)
            elif dif<0:
                """La venta no se ha acabado
                    Las comision de compra se meten, pero no las de venta"""
                impuestos=p.impuestos
                comisiones=p.comision
                p.impuestos=0
                p.comision=0#Aunque se borra pero se quita por que se ha cobrado
                return (impuestos, comisiones)
            elif(dif>0):
                """La venta se ha acabado y queda un nuevo p sin impuestos ni comision
                    Los impuestos y las comision se meten
                """
                impuestos=n.impuestos+p.impuestos
                comisiones=n.comision+p.comision
                n.impuestos=0
                n.comision=0
                p.impuestos=0
                p.comision=0
                return (impuestos, comisiones)

            
        ##########################################
        operinversioneshistorica=SetInvestmentOperationsHistorical(self.mem)
        #Crea un array copia de self.arr, porque eran vinculos 
        arr=[]
        for a in self.arr:   
            arr.append(a.clone())
        arr=sorted(arr, key=lambda a:a.id) 


        while (True):#Bucle recursivo.            
            pos=[]
            for p in arr:
                if p.acciones>0:
                    pos.append(p)
            #Mira si hay negativos y sino sale
            n=None
            for neg in arr:
                if neg.acciones<0:
                    n=neg
                    break
            if n==None:
                break
            elif len(pos)==0:#Se qudaba pillado
                break
            
            #Solo impuestos y comisiones la primera vez
            for p in pos:
                dif=p.acciones+n.acciones
                (impuestos, comisiones)=comisiones_impuestos(dif, p, n)
                if dif==0: #Si es 0 se inserta el historico que coincide con la venta y se borra el registro negativ
                    operinversioneshistorica.append(InvestmentOperationHistorical(self.mem).init__create(n, n.inversion, p.datetime.date(), -n.acciones*n.valor_accion,n.tipooperacion, n.acciones, comisiones, impuestos, n.datetime.date(), p.valor_accion, n.valor_accion))
                    arr.remove(n)
                    arr.remove(p)
                    break
                elif dif<0:#   //Si es <0 es decir hay más acciones negativas que positivas. Se debe introducir en el historico la tmpoperinversion y borrarlo y volver a recorrer el bucle. Restando a n.acciones las acciones ya apuntadas en el historico
                    operinversioneshistorica.append(InvestmentOperationHistorical(self.mem).init__create(p, p.inversion, p.datetime.date(), p.acciones*n.valor_accion,n.tipooperacion, -p.acciones, comisiones, impuestos, n.datetime.date(), p.valor_accion, n.valor_accion))
                    arr.remove(p)
                    n.acciones=n.acciones+p.acciones#ya que n.acciones es negativo

                elif(dif>0):
                    """Cuando es >0 es decir hay mas acciones positivos se añade el registro en el historico 
                    con los datos de la operacion negativa en su totalidad. Se borra el registro de negativos y 
                    de positivos en operinversionesactual y se inserta uno con los datos positivos menos lo 
                    quitado por el registro negativo. Y se sale del bucle. 
                    //Aqui no se inserta la comision porque solo cuando se acaba las acciones positivos   """
                    operinversioneshistorica.append(InvestmentOperationHistorical(self.mem).init__create(p, n.inversion, p.datetime.date(), -n.acciones*n.valor_accion,n.tipooperacion, n.acciones, comisiones, impuestos, n.datetime.date(), p.valor_accion, n.valor_accion))
                    arr.remove(p)
                    arr.remove(n)
                    arr.append(InvestmentOperation(self.mem).init__create( p.tipooperacion, p.datetime, p.inversion,  p.acciones-(-n.acciones), (p.acciones-(-n.acciones))*n.valor_accion,  0, 0, p.valor_accion, "",  p.id))
                    arr=sorted(arr, key=lambda a:a.id)              
                    break;
        #Crea array operinversionesactual, ya que arr es operinversiones
        operinversionesactual=SetInvestmentOperationsCurrent(self.mem)
        for a in arr:
            operinversionesactual.append(InvestmentOperationCurrent(self.mem).init__create(a.id, a.tipooperacion, a.datetime, a.inversion,  a.acciones, a.importe,  a.impuestos, a.comision, a.valor_accion))
        return (operinversionesactual, operinversioneshistorica)
            
    def clone(self):
        """Funcion que devuelve un SetInvestmentOperations, con todas sus InvestmentOperation clonadas. Se usa para
        hacer estimaciones"""
        resultado=SetInvestmentOperations(self.mem)
        for io in self.arr:
            resultado.arr.append(io.clone())
        return resultado
        
    def myqtablewidget(self, tabla, section):
        """Section es donde guardar en el config file, coincide con el nombre del formulario en el que está la tabla"""
        diff=0
        homogeneous=self.isHomogeneous()
        if homogeneous==False:
            diff=2
        tabla.setColumnCount(8+diff)
        tabla.setHorizontalHeaderItem(0, QTableWidgetItem(QApplication.translate("Core", "Date", None, QApplication.UnicodeUTF8)))
        if homogeneous==False:
            tabla.setHorizontalHeaderItem(diff-1, QTableWidgetItem(QApplication.translate("Core", "Product", None, QApplication.UnicodeUTF8)))
            tabla.setHorizontalHeaderItem(diff, QTableWidgetItem(QApplication.translate("Core", "Account", None, QApplication.UnicodeUTF8)))
        tabla.setHorizontalHeaderItem(diff+1, QTableWidgetItem(QApplication.translate("Core", "Operation type", None, QApplication.UnicodeUTF8)))
        tabla.setHorizontalHeaderItem(diff+2, QTableWidgetItem(QApplication.translate("Core", "Shares", None, QApplication.UnicodeUTF8)))
        tabla.setHorizontalHeaderItem(diff+3, QTableWidgetItem(QApplication.translate("Core", "Valor acción", None, QApplication.UnicodeUTF8)))
        tabla.setHorizontalHeaderItem(diff+4, QTableWidgetItem(QApplication.translate("Core", "Importe", None, QApplication.UnicodeUTF8)))
        tabla.setHorizontalHeaderItem(diff+5, QTableWidgetItem(QApplication.translate("Core", "Comission", None, QApplication.UnicodeUTF8)))
        tabla.setHorizontalHeaderItem(diff+6, QTableWidgetItem(QApplication.translate("Core", "Taxes", None, QApplication.UnicodeUTF8)))
        tabla.setHorizontalHeaderItem(diff+7, QTableWidgetItem(QApplication.translate("Core", "Total", None, QApplication.UnicodeUTF8)))
        #DATA 
        tabla.clearContents()
        tabla.settings(section,  self.mem)       
        tabla.setRowCount(len(self.arr))
        gainsyear=str2bool(self.mem.config.get_value("settings", "gainsyear"))
        for rownumber, a in enumerate(self.arr):
            tabla.setItem(rownumber, 0, qdatetime(a.datetime, a.inversion.product.stockexchange.zone))
            if gainsyear==True and a.less_than_a_year()==True:
                tabla.item(rownumber, 0).setIcon(QIcon(":/xulpymoney/new.png"))
            if homogeneous==False:
                tabla.setItem(rownumber, diff-1, qleft(a.inversion.name))
                tabla.setItem(rownumber, diff, qleft(a.inversion.cuenta.name))
            tabla.setItem(rownumber, diff+1, QTableWidgetItem(a.tipooperacion.name))
            tabla.setItem(rownumber, diff+2, qright(a.acciones))
            tabla.setItem(rownumber, diff+3, self.mem.localcurrency.qtablewidgetitem(a.valor_accion))
            tabla.setItem(rownumber, diff+4, self.mem.localcurrency.qtablewidgetitem(a.importe))
            tabla.setItem(rownumber, diff+5, self.mem.localcurrency.qtablewidgetitem(a.comision))
            tabla.setItem(rownumber, diff+6, self.mem.localcurrency.qtablewidgetitem(a.impuestos))
            if a.acciones>=0:
                tabla.setItem(rownumber, diff+7, self.mem.localcurrency.qtablewidgetitem(a.importe+a.comision+a.impuestos))
            else:
                tabla.setItem(rownumber, diff+7, self.mem.localcurrency.qtablewidgetitem(a.importe-a.comision-a.impuestos))

    def isHomogeneous(self):
        """Devuelve true si todas las inversiones son de la misma inversion"""
        if len(self.arr)==0:
            return True
        inversion=self.arr[0].inversion
        for i in range(1, len(self.arr)):
            if self.arr[i].inversion!=inversion:
                return False
        return True


class SetInvestmentOperationsCurrent:    
    """Clase es un array ordenado de objetos newInvestmentOperation"""
    def __init__(self, mem):
        self.mem=mem
        self.arr=[]
    def append(self, objeto):
        self.arr.append(objeto)
    def arr_from_fecha(self, date):
        """Función que saca del arr las que tienen fecha mayor o igual a la pasada como parametro."""
        resultado=[]
        if date==None:
            return resultado
        for a in self.arr:
            if a.datetime.date()>=date:
                resultado.append(a)
        return resultado
    def __repr__(self):
        try:
            inversion=self.arr[0].inversion.id
        except:
            inversion="Desconocido"
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
            
    def datetime_primera_operacion(self):
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
        
    def myqtablewidget(self,  tabla,  section ):
        """Función que rellena una tabla pasada como parámetro con datos procedentes de un array de objetos
        InvestmentOperationCurrent y dos valores de mystocks para rellenar los tpc correspodientes
        
        Se dibujan las columnas pero las propiedad alternate color... deben ser en designer
        
        Parámetros
            - tabla myQTableWidget en la que rellenar los datos
            - setoperinversion. Vincula a una inversión que  Debe tener cargado mq con get_basic y las operaciones de inversión calculadas
        last es el último quote de la inversión"""
        #UI
        diff=0
        homogeneous=self.isHomogeneous()
        if homogeneous==False:
            diff=2
        tabla.setColumnCount(10+diff)
        tabla.setHorizontalHeaderItem(0, QTableWidgetItem(QApplication.translate("Core", "Date", None, QApplication.UnicodeUTF8)))
        if homogeneous==False:
            tabla.setHorizontalHeaderItem(diff-1, QTableWidgetItem(QApplication.translate("Core", "Product", None, QApplication.UnicodeUTF8)))
            tabla.setHorizontalHeaderItem(diff, QTableWidgetItem(QApplication.translate("Core", "Account", None, QApplication.UnicodeUTF8)))
        tabla.setHorizontalHeaderItem(diff+1, QTableWidgetItem(QApplication.translate("Core", "Shares", None, QApplication.UnicodeUTF8)))
        tabla.setHorizontalHeaderItem(diff+2, QTableWidgetItem(QApplication.translate("Core", "Price", None, QApplication.UnicodeUTF8)))
        tabla.setHorizontalHeaderItem(diff+3, QTableWidgetItem(QApplication.translate("Core", "Invested", None, QApplication.UnicodeUTF8)))
        tabla.setHorizontalHeaderItem(diff+4, QTableWidgetItem(QApplication.translate("Core", "Current balance", None, QApplication.UnicodeUTF8)))
        tabla.setHorizontalHeaderItem(diff+5, QTableWidgetItem(QApplication.translate("Core", "Pending", None, QApplication.UnicodeUTF8)))
        tabla.setHorizontalHeaderItem(diff+6, QTableWidgetItem(QApplication.translate("Core", "% annual", None, QApplication.UnicodeUTF8)))
        tabla.setHorizontalHeaderItem(diff+7, QTableWidgetItem(QApplication.translate("Core", "% APR", None, QApplication.UnicodeUTF8)))
        tabla.setHorizontalHeaderItem(diff+8, QTableWidgetItem(QApplication.translate("Core", "% Total", None, QApplication.UnicodeUTF8)))
        tabla.setHorizontalHeaderItem(diff+9, QTableWidgetItem(QApplication.translate("Core", "Benchmark", None, QApplication.UnicodeUTF8)))
        #DATA
        tabla.settings(section,  self.mem)
        if len(self.arr)==0:
            tabla.setRowCount(0)
            return
#        inversion=self.arr[0].inversion
#        numdigitos=inversion.product.result.decimalesSignificativos()
        sumacciones=Decimal('0')
        sum_accionesXvalor=Decimal('0')
        sumsaldo=Decimal('0')
        sumpendiente=Decimal('0')
        suminvertido=Decimal('0')
        tabla.clearContents()
        tabla.setRowCount(len(self.arr)+1)
        rownumber=0
        gainsyear=str2bool(self.mem.config.get_value("settings", "gainsyear"))
        for rownumber, a in enumerate(self.arr):
            sumacciones=Decimal(sumacciones)+Decimal(str(a.acciones))
            balance=a.balance(a.inversion.product.result.basic.last)
            pendiente=a.pendiente(a.inversion.product.result.basic.last)
            invertido=a.invertido()
    
            sumsaldo=sumsaldo+balance
            sumpendiente=sumpendiente+pendiente
            suminvertido=suminvertido+invertido
            sum_accionesXvalor=sum_accionesXvalor+a.acciones*a.valor_accion
    
            tabla.setItem(rownumber, 0, qdatetime(a.datetime, self.mem.localzone))
            if gainsyear==True and a.less_than_a_year()==True:
                tabla.item(rownumber, 0).setIcon(QIcon(":/xulpymoney/new.png"))
            if homogeneous==False:
                tabla.setItem(rownumber, diff-1, qleft(a.inversion.name))
                tabla.setItem(rownumber, diff, qleft(a.inversion.cuenta.name))
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
            rownumber=rownumber+1
        tabla.setItem(rownumber, diff+0, QTableWidgetItem(("TOTAL")))
        tabla.setItem(rownumber, diff+1, qright(str(sumacciones)))
        if sumacciones==0:
            tabla.setItem(rownumber, diff+2, a.inversion.product.currency.qtablewidgetitem(0))
        else:
            tabla.setItem(rownumber, diff+2, a.inversion.product.currency.qtablewidgetitem(sum_accionesXvalor/sumacciones, 6))
        tabla.setItem(rownumber, diff+3, a.inversion.product.currency.qtablewidgetitem(suminvertido))
        tabla.setItem(rownumber, diff+4, a.inversion.product.currency.qtablewidgetitem(sumsaldo))
        tabla.setItem(rownumber, diff+5, a.inversion.product.currency.qtablewidgetitem(sumpendiente))
        tabla.setItem(rownumber, diff+7, qtpc(self.tpc_tae(a.inversion.product.result.basic.last.quote)))
        tabla.setItem(rownumber, diff+8, qtpc(self.tpc_total(sumpendiente, suminvertido)))
            

    def pendiente(self, lastquote):
        resultado=0
        for o in self.arr:
            resultado=resultado+o.pendiente(lastquote)
        return resultado
                
    def tpc_tae(self, last):
        sumacciones=0
        axtae=0
        for o in self.arr:
            sumacciones=sumacciones+o.acciones
            axtae=axtae+o.acciones*o.tpc_tae(last)
        if sumacciones==0:
            return None
        return axtae/sumacciones
            
        dias=(datetime.date.today()-self.datetime.date()).days +1 #Account el primer día
        if dias==0:
            dias=1
        return Decimal(365*self.tpc_total(last)/dias)
        
        
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
        curms=self.mem.conms.cursor()
        for o in self.arr:
            o.get_referencia_indice(indice)
        curms.close()
    
    def valor_medio_compra(self):
        """Devuelve el valor medio de compra de todas las operaciones de inversión actual"""
        numacciones=0
        numaccionesxvalor=0
        for o in self.arr:
            numacciones=numacciones+o.acciones
            numaccionesxvalor=numaccionesxvalor+o.acciones*o.valor_accion
        if numacciones==0:
            return 0
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
        self.sort()
        
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
                    self.arr.insert(0, InvestmentOperationCurrent(self.mem).init__create(ioa, ioa.tipooperacion, ioa.datetime, ioa.inversion,  ioa.acciones-abs(accionesventa), (ioa.acciones-abs(accionesventa))*ioa.valor_accion,  0, 0, ioa.valor_accion, ioa.id))
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
        self.sort()
        print ("\n Imprimiendo SIOA",  self)
        for oia in self.arr:
            print ("  - ", oia)
        
        
    def sort(self):
        """Ordena por datetime"""
        self.arr=sorted(self.arr, key=lambda o:o.datetime)
 
class SetInvestmentOperationsHistorical:       
    """Clase es un array ordenado de objetos newInvestmentOperation"""
    def __init__(self, mem):
        self.mem=mem
        self.arr=[]
    def append(self, objeto):
        self.arr.append(objeto)
    def arr_from_fecha(self, date):
        """Función que saca del arr las que tienen fecha mayor o igual a la pasada como parametro."""
        resultado=[]
        if date==None:
            return resultado
        for a in self.arr:
            if a.datetime.date()>=date:
                resultado.append(a)
        return resultado
        
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
    def myqtablewidget(self, tabla, section):
        """Rellena datos de un array de objetos de InvestmentOperationHistorical, devuelve totales ver código"""
        tabla.setColumnCount(13)
        tabla.setHorizontalHeaderItem(0, QTableWidgetItem(QApplication.translate("Core", "Date", None, QApplication.UnicodeUTF8)))
        tabla.setHorizontalHeaderItem(1, QTableWidgetItem(QApplication.translate("Core", "Years", None, QApplication.UnicodeUTF8)))
        tabla.setHorizontalHeaderItem(2, QTableWidgetItem(QApplication.translate("Core", "Product", None, QApplication.UnicodeUTF8)))
        tabla.setHorizontalHeaderItem(3, QTableWidgetItem(QApplication.translate("Core", "Operation type", None, QApplication.UnicodeUTF8)))
        tabla.setHorizontalHeaderItem(4, QTableWidgetItem(QApplication.translate("Core", "Shares", None, QApplication.UnicodeUTF8)))
        tabla.setHorizontalHeaderItem(5, QTableWidgetItem(QApplication.translate("Core", "Initial balance", None, QApplication.UnicodeUTF8)))
        tabla.setHorizontalHeaderItem(6, QTableWidgetItem(QApplication.translate("Core", "Final balance", None, QApplication.UnicodeUTF8)))
        tabla.setHorizontalHeaderItem(7, QTableWidgetItem(QApplication.translate("Core", "Gross selling operations", None, QApplication.UnicodeUTF8)))
        tabla.setHorizontalHeaderItem(8, QTableWidgetItem(QApplication.translate("Core", "Comissions", None, QApplication.UnicodeUTF8)))
        tabla.setHorizontalHeaderItem(9, QTableWidgetItem(QApplication.translate("Core", "Taxes", None, QApplication.UnicodeUTF8)))
        tabla.setHorizontalHeaderItem(10, QTableWidgetItem(QApplication.translate("Core", "Net selling operations", None, QApplication.UnicodeUTF8)))
        tabla.setHorizontalHeaderItem(11, QTableWidgetItem(QApplication.translate("Core", "% Net APR", None, QApplication.UnicodeUTF8)))
        tabla.setHorizontalHeaderItem(12, QTableWidgetItem(QApplication.translate("Core", "% Net Total", None, QApplication.UnicodeUTF8)))
        #DATA
        tabla.settings(section,  self.mem)        
        
        
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
    

    def sort(self):
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
        
    def __repr__(self):
        return ("IOA {0}. {1} {2}. Acciones: {3}. Valor:{4}".format(self.inversion.name,  self.datetime, self.tipooperacion.name,  self.acciones,  self.valor_accion))
        
    def init__create(self, operinversion, tipooperacion, datetime, inversion, acciones, importe, impuestos, comision, valor_accion, id=None):
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
        return self
                
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

#    def strct(self):
#        """Junta en una string el concepto y el tipo separado por coma"""
#        return "{0};{1}".format(self.id, self.tipooperacion.id)
        

    def init__create(self, name, tipooperacion, editable,  id=None):
        self.id=id
        self.name=name
        self.tipooperacion=tipooperacion
        self.editable=editable
        return self
                
    def init__db_row(self, row, tipooperacion):
        """El parámetro tipooperacion es un objeto tipooperacion, si no se tuviera en tiempo de creación se asigna None"""
        return self.init__create(row['concepto'], tipooperacion, row['editable'], row['id_conceptos'])
#            
#    def balance(self, cur, year,  month):
#        sql="select sum(importe) as importe from opercuentastarjetas where id_conceptos="+str(self.id)+" and date_part('year',datetime)='"+str(year)+"' and date_part('month',datetime)='"+str(month)+"'"
#        saldoopercuentastarjetas=con.Execute(sql).GetRowAssoc(0)["importe"]
#        if saldoopercuentastarjetas==None:
#            saldoopercuentastarjetas=0
#        return saldoopercuentastarjetas
        
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
        self.cuenta=None
        
    def __repr__(self):
        return "AccountOperation {0}. datetime: {1}. Importe:{2}. Concept:{3}".format(self.id, self.datetime, self.importe, self.concepto)
        
    def init__create(self, dt, concepto, tipooperacion, importe,  comentario, cuenta, id=None):
        self.id=id
        self.datetime=dt
        self.concepto=concepto
        self.tipooperacion=tipooperacion
        self.importe=importe
        self.comentario=comentario
        self.cuenta=cuenta
        return self
        
    def init__db_row(self, row, concepto,  tipooperacion, cuenta):
        return self.init__create(row['datetime'],  concepto,  tipooperacion,  row['importe'],  row['comentario'],  cuenta,  row['id_opercuentas'])


    def init__db_query(self, id_opercuentas):
        """Creates a AccountOperation querying database for an id_opercuentas"""
        resultado=None
        cur=self.mem.con.cursor()
        cur.execute("select * from opercuentas where id_opercuentas=%s", (id_opercuentas, ))
        for row in cur:
            concepto=self.mem.conceptos.find(row['id_conceptos'])
            resultado=self.init__db_row(row, concepto, concepto.tipooperacion, self.mem.data.cuentas_all().find(row['id_cuentas']))
        cur.close()
        return resultado

    def borrar(self):
        cur=self.mem.con.cursor()
        cur.execute("delete from opercuentas where id_opercuentas=%s", (self.id, ))
        self.cuenta.saldo_from_db()
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
            return QApplication.translate("Core","{0[0]}. Gross: {0[1]} {1}. Witholding tax: {0[2]} {1}. Comission: {0[3]} {1}".format(c, self.cuenta.currency.symbol))
        elif self.concepto.id in (29, 35) and len(c)==5:#{0}|{1}|{2}|{3}".format(row['inversion'], importe, comision, impuestos)
            return QApplication.translate("Core","{0[1]}: {0[0]} shares. Amount: {0[2]} {1}. Comission: {0[3]} {1}. Taxes: {0[4]} {1}".format(c, self.cuenta.currency.symbol))        
        elif self.concepto.id==40 and len(c)==2:#"{0}|{1}".format(self.selCreditCard.name, len(self.setSelOperCreditCards))
            return QApplication.translate("Core","CreditCard: {0[0]}. Se han ejecutado {0[1]} pagos con tarjeta".format(c))        
        elif self.concepto.id==4 and len(c)==3:#Transfer from origin
            return QApplication.translate("Core", "Transfer to {0}".format(self.mem.data.cuentas_all().find(int(c[0])).name))
        elif self.concepto.id==5 and len(c)==2:#Transfer received in destiny
            return QApplication.translate("Core", "Transfer received from {0}".format(self.mem.data.cuentas_all().find(int(c[0])).name))
        elif self.concepto.id==38 and c[0]=="Transfer":#Comision bancaria por transferencia
            print (c[2])
            return QApplication.translate("Core", "Due to account transfer of {0} from {1}".format(self.mem.localcurrency.string(float(c[1])), self.mem.data.cuentas_all().find(int(c[2])).name))
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
        if self.concepto.id in (29, 35, 39, 40, 50,  62, 63, 65):#div, factur tarj:
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
            cur.execute("insert into opercuentas (datetime, id_conceptos, id_tiposoperaciones, importe, comentario, id_cuentas) values ( %s,%s,%s,%s,%s,%s) returning id_opercuentas",(self.datetime, self.concepto.id, self.tipooperacion.id, self.importe, self.comentario, self.cuenta.id))
            self.id=cur.fetchone()[0]
        else:
            cur.execute("update opercuentas set datetime=%s, id_conceptos=%s, id_tiposoperaciones=%s, importe=%s, comentario=%s, id_cuentas=%s where id_opercuentas=%s", (self.datetime, self.concepto.id, self.tipooperacion.id,  self.importe,  self.comentario,  self.cuenta.id,  self.id))
        cur.close()
        self.cuenta.saldo_from_db()
        
class DBData:
    def __init__(self, mem):
        self.mem=mem
        self.loaded_inactive=False
        self.tupdatedata=TUpdateData(self.mem)
        
    def __del__(self):
        if self.tupdatedata.isAlive():
            self.tupdatedata.join()
            print ("TUpdateData closed")

    def load_actives(self):
        inicio=datetime.datetime.now()
        self.benchmark=Product(self.mem).init__db(self.mem.config.get_value("settings", "benchmark" ))
        self.benchmark.result.basic.load_from_db()
        self.ebs_active=SetBanks(self.mem)
        self.ebs_active.load_from_db("select * from entidadesbancarias where eb_activa=true")
        self.cuentas_active=SetAccounts(self.mem, self.ebs_active)
        self.cuentas_active.load_from_db("select * from cuentas where cu_activa=true")
        self.tarjetas_active=SetCreditCards(self.mem, self.mem.data.cuentas_active)
        self.tarjetas_active.load_from_db("select * from tarjetas where tj_activa=true")
        self.investments_active=SetProducts(self.mem)
        self.investments_active.load_from_inversiones_query("select distinct(mystocksid) from inversiones where in_activa=true")
        self.inversiones_active=SetInvestments(self.mem, self.cuentas_active, self.investments_active, self.benchmark)
        self.inversiones_active.load_from_db("select * from inversiones where in_activa=true", True)
        if not self.tupdatedata.isAlive():#Necesary because, can be thrown from actionUpdateMemory
            self.tupdatedata.start()        
        print("Cargando actives",  datetime.datetime.now()-inicio)
        
    def load_inactives(self, force=False):
        def load():
            inicio=datetime.datetime.now()
            
            self.ebs_inactive=SetBanks(self.mem)
            self.ebs_inactive.load_from_db("select * from entidadesbancarias where eb_activa=false")
            
            self.cuentas_inactive=SetAccounts(self.mem, self.ebs_all())
            self.cuentas_inactive.load_from_db("select * from cuentas where cu_activa=false")
            
            self.tarjetas_inactive=SetCreditCards(self.mem, self.cuentas_all())
            self.tarjetas_inactive.load_from_db("select * from tarjetas where tj_activa=false")
            
            self.investments_inactive=SetProducts(self.mem)
            self.investments_inactive.load_from_inversiones_query("select distinct(mystocksid) from inversiones where in_activa=false")

            self.inversiones_inactive=SetInvestments(self.mem, self.cuentas_all(), self.investments_all(), self.benchmark)
            self.inversiones_inactive.load_from_db("select * from inversiones where in_activa=false",  True)
            
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
        
    def reload(self):
        self.load_actives()
        self.load_inactives()
        
    def ebs_all(self):
        return self.ebs_active.union(self.ebs_inactive)
    def cuentas_all(self):
        return self.cuentas_active.union(self.cuentas_inactive)
    def tarjetas_all(self):
        return self.tarjetas_active.union(self.tarjetas_inactive,  self.cuentas_all())
    def inversiones_all(self):
        return self.inversiones_active.union(self.inversiones_inactive)
    def investments_all(self):
        return self.investments_active.union(self.investments_inactive)

        
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
        self.inversion.cuenta.saldo_from_db()
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
            oc=AccountOperation(self.mem).init__create( self.datetime,self.concepto, self.concepto.tipooperacion, self.neto, comentario, self.inversion.cuenta)
            oc.save()
            self.opercuenta=oc
            #Añade el dividend
            sql="insert into dividends (fecha, valorxaccion, bruto, retencion, neto, id_inversiones,id_opercuentas, comision, id_conceptos) values ('"+str(self.fecha)+"', "+str(self.dpa)+", "+str(self.bruto)+", "+str(self.retencion)+", "+str(self.neto)+", "+str(self.inversion.id)+", "+str(self.opercuenta.id)+", "+str(self.comision)+", "+str(self.concepto.id)+")"
            cur.execute(sql)
        else:
            self.opercuenta.fecha=self.fecha
            self.opercuenta.importe=self.neto
            self.opercuenta.comentario=comentario
            self.opercuenta.concepto=self.concepto
            self.opercuenta.tipooperacion=self.concepto.tipooperacion
            self.opercuenta.save()
            cur.execute("update dividends set fecha=%s, valorxaccion=%s, bruto=%s, retencion=%s, neto=%s, id_inversiones=%s, id_opercuentas=%s, comision=%s, id_conceptos=%s where id_dividends=%s", (self.fecha, self.dpa, self.bruto, self.retencion, self.neto, self.inversion.id, self.opercuenta.id, self.comision, self.concepto.id, self.id))
        self.inversion.cuenta.saldo_from_db()
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
        
    def __repr__(self):
        return ("IO {0} ({1}). {2} {3}. Acciones: {4}. Valor:{5}".format(self.inversion.name, self.inversion.id,  self.datetime, self.tipooperacion.name,  self.acciones,  self.valor_accion))
        
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
        return self
        
    def init__create(self, tipooperacion, datetime, inversion, acciones, importe, impuestos, comision, valor_accion, comentario,  id=None):
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
        return self

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
            c=AccountOperationOfInvestmentOperation(self.mem).init__create(self.datetime.date(), self.mem.conceptos.find(29), self.tipooperacion, -self.importe-self.comision, self.comentario, self.inversion.cuenta, self,self.inversion)
            c.save()
        elif self.tipooperacion.id==5:#// Venta Acciones
            #//Se pone un registro de compra de acciones que resta el balance de la opercuenta
            c=AccountOperationOfInvestmentOperation(self.mem).init__create(self.datetime.date(), self.mem.conceptos.find(35), self.tipooperacion, self.importe-self.comision-self.impuestos, self.comentario, self.inversion.cuenta, self,self.inversion)
            c.save()
        elif self.tipooperacion.id==6:
            #//Si hubiera comisión se añade la comisión.
            if(self.comision!=0):
                c=AccountOperationOfInvestmentOperation(self.mem).init__create(self.datetime.date(), self.mem.conceptos.find(38), self.mem.tiposoperaciones.find(1), -self.comision-self.impuestos, self.comentario, self.inversion.cuenta, self,self.inversion)
                c.save()
    
    def clone(self):
        """Crea una inversion operacion desde otra inversionoepracion. NO es un enlace es un objeto clone"""
        resultado=InvestmentOperation(self.mem)
        resultado.init__create(self.tipooperacion, self.datetime, self.inversion, self.acciones, self.importe, self.impuestos, self.comision, self.valor_accion, self.comentario, self.id)
        return resultado
                
    def comment(self):
        """Función que genera un comentario parseado según el tipo de operación o concepto"""
        if self.tipooperacion.id==9:#"Traspaso de valores. Origen"#"{0}|{1}|{2}|{3}".format(self.inversion.name, self.bruto, self.retencion, self.comision)
            return QApplication.translate("Core","Traspaso de valores realizado a {0}".format(self.comentario.split("|"), self.cuenta.currency.symbol))
        else:
            return self.comentario

    def less_than_a_year(self):
        if datetime.date.today()-self.datetime.date()<=datetime.timedelta(days=365):
                return True
        return False
        
    def save(self, recalculate=True):
        cur=self.mem.con.cursor()
        if self.id==None:#insertar
            cur.execute("insert into operinversiones(datetime, id_tiposoperaciones,  importe, acciones,  impuestos,  comision,  valor_accion, comentario, id_inversiones) values (%s, %s, %s, %s, %s, %s, %s, %s,%s) returning id_operinversiones", (self.datetime, self.tipooperacion.id, self.importe, self.acciones, self.impuestos, self.comision, self.valor_accion, self.comentario, self.inversion.id))
            self.id=cur.fetchone()[0]
            self.inversion.op.append(self)
        else:
            cur.execute("update operinversiones set datetime=%s, id_tiposoperaciones=%s, importe=%s, acciones=%s, impuestos=%s, comision=%s, valor_accion=%s, comentario=%s, id_inversiones=%s where id_operinversiones=%s", (self.datetime, self.tipooperacion.id, self.importe, self.acciones, self.impuestos, self.comision, self.valor_accion, self.comentario, self.inversion.id, self.id))
        if recalculate==True:
            (self.inversion.op_actual,  self.inversion.op_historica)=self.inversion.op.calcular()   
            self.actualizar_cuentaoperacion_asociada()
            self.inversion.cuenta.saldo_from_db()
        self.mem.con.commit()
        cur.close()
        
    def borrar(self):        
        cur=self.mem.con.cursor()
        cur.execute("delete from operinversiones where id_operinversiones=%s",(self.id, ))
        self.inversion.op.arr.remove(self)
        (self.inversion.op_actual,  self.inversion.op_historica)=self.inversion.op.calcular()
        self.inversion.cuenta.saldo_from_db()
        self.inversion.actualizar_cuentasoperaciones_asociadas()#Regenera toda la inversi´on.
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
        self.activa=None
        
    def init__create(self, name,  activa=True, id=None):
        self.id=id
        self.activa=activa
        self.name=name
        return self
        
    def __repr__(self):
        return ("Instancia de Bank: {0} ({1})".format( self.name, self.id))

    

    def init__db_row(self, row):
        self.id=row['id_entidadesbancarias']
        self.name=row['entidadbancaria']
        self.activa=row['eb_activa']
        return self
        
    def qmessagebox_inactive(self):
        if self.activa==False:
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
            cur.execute("insert into entidadesbancarias (entidadbancaria, eb_activa) values (%s,%s) returning id_entidadesbancarias", (self.name, self.activa))
            self.id=cur.fetchone()[0]
        else:
            cur.execute("update entidadesbancarias set entidadbancaria=%s, eb_activa=%s where id_entidadesbancarias=%s", (self.name, self.activa, self.id))
        cur.close()
        
    def balance(self, setcuentas,  setinversiones):
        resultado=0
        #Recorre balance cuentas
        for v in setcuentas.arr:
            if v.eb.id==self.id:
                resultado=resultado+v.balance
        
        #Recorre balance inversiones
        for i in setinversiones.arr:
            if i.cuenta.eb.id==self.id:
                resultado=resultado+i.balance()
        return resultado
        
    def es_borrable(self, dic_cuentas):
        """Función que devuelve un booleano si una cuenta es borrable, es decir, que no tenga registros dependientes."""
        #Recorre balance cuentas
        for k, v in dic_cuentas.items():
            if v.eb.id==self.id:
                return False
        return True
        
    def borrar(self,cur, dic_cuentas):
        """Función que borra una vez comprobado que es variable
        dic_cuentas es el diccionario de todas las cuentas de la applicación"""
        if self.es_borrable(dic_cuentas)==True:
            cur.execute("delete from entidadesbancarias where id_entidadesbancarias=%s", (self.id, ))  
            
class Account:
    def __init__(self, mem):
        self.mem=mem
        self.id=None
        self.name=None
        self.eb=None
        self.activa=None
        self.numero=None
        self.currency=None
        self.eb=None #Enlace a objeto
        self.balance=0#Se calcula al crear el objeto y cuando haya opercuentas se calcula dinamicamente

    def __repr__(self):
        return ("Instancia de Account: {0} ({1})".format( self.name, self.id))
        
    def init__db_row(self, row, eb):
        self.id=row['id_cuentas']
        self.name=row['cuenta']
        self.eb=eb
        self.activa=row['cu_activa']
        self.numero=row['numerocuenta']
        self.currency=self.mem.currencies.find(row['currency'])
        return self
    
    def saldo_from_db(self,fecha=None):
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
        balance=cur.fetchone()[0]
        if balance==None:
            cur.close()
            return 0        
        if fecha==datetime.date.today():
            self.balance=balance
        cur.close()
        return balance
            
    def init__create(self, name,  eb, activa, numero, currency, id=None):
        self.id=id
        self.name=name
        self.eb=eb
        self.activa=activa
        self.numero=numero
        self.currency=currency
        return self
        
    def save(self):
        cur=self.mem.con.cursor()
        if self.id==None:
            cur.execute("insert into cuentas (id_entidadesbancarias, cuenta, numerocuenta, cu_activa,currency) values (%s,%s,%s,%s,%s) returning id_cuentas", (self.eb.id, self.name, self.numero, self.activa, self.currency.id))
            self.id=cur.fetchone()[0]
        else:
            cur.execute("update cuentas set cuenta=%s, id_entidadesbancarias=%s, numerocuenta=%s, cu_activa=%s, currency=%s where id_cuentas=%s", (self.name, self.eb.id, self.numero, self.activa, self.currency.id, self.id))
        cur.close()

    def es_borrable(self, cur):
        """Función que devuelve un booleano si una cuenta es borrable, es decir, que no tenga registros dependientes."""
        cur.execute("select count(*) from tarjetas where id_cuentas=%s", (self.id, ))
        if cur.fetchone()[0]!=0:
            return False
        cur.execute("select count(*) from inversiones where id_cuentas=%s", (self.id, ))
        if cur.fetchone()[0]!=0:
            return False
        cur.execute("select count(*) from opercuentas where id_cuentas=%s", (self.id, ))
        if cur.fetchone()[0]!=0:
            return False
        return True
        
    def borrar(self, cur):
        if self.es_borrable(cur)==True:
            cur.execute("delete from cuentas where id_cuentas=%s", (self.id, ))

    def transferencia(self, datetime, cuentaorigen, cuentadestino, importe, comision):
        """Si el oc_comision_id es 0 es que no hay comision porque tambi´en es 0"""
        #Ojo los comentarios est´an dependientes.
        if comision>0:
            commentcomission="Transfer|{0}|{1}".format(importe, cuentaorigen.id)
            oc_comision=AccountOperation(self.mem).init__create(datetime, self.mem.conceptos.find(38), self.mem.tiposoperaciones.find(1), -comision, commentcomission, cuentaorigen )
            oc_comision.save()          
            oc_comision_id=oc_comision.id  
        else:
            oc_comision_id=0
        oc_origen=AccountOperation(self.mem).init__create(datetime, self.mem.conceptos.find(4), self.mem.tiposoperaciones.find(3), -importe, "", cuentaorigen )
        oc_origen.save()
        commentdestino="{0}|{1}".format(cuentaorigen.id, oc_origen.id)
        oc_destino=AccountOperation(self.mem).init__create(datetime, self.mem.conceptos.find(5), self.mem.tiposoperaciones.find(3), importe, commentdestino, cuentadestino )
        oc_destino.save()
        oc_origen.comentario="{0}|{1}|{2}".format(cuentadestino.id, oc_destino.id, oc_comision_id)
        oc_origen.save()

    def qmessagebox_inactive(self):
        if self.activa==False:
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
        self.cuenta=None#Vincula a un objeto  Account
        self.activa=None
        self.op=None#Es un objeto SetInvestmentOperations
        self.op_actual=None#Es un objeto Setoperinversionesactual
        self.op_historica=None#setoperinversioneshistorica
        
        
    def create(self, name, venta, cuenta, inversionmq):
        self.name=name
        self.venta=venta
        self.cuenta=cuenta
        self.product=inversionmq
        self.activa=True
        return self
    
    
    def save(self):
        """Inserta o actualiza la inversión dependiendo de si id=None o no"""
        cur=self.mem.con.cursor()
        if self.id==None:
            cur.execute("insert into inversiones (inversion, venta, id_cuentas, in_activa, mystocksid) values (%s, %s,%s,%s,%s) returning id_inversiones", (self.name, self.venta, self.cuenta.id, self.activa, self.product.id))    
            self.id=cur.fetchone()[0]
        else:
            cur.execute("update inversiones set inversion=%s, venta=%s, id_cuentas=%s, in_activa=%s, mystocksid=%s where id_inversiones=%s", (self.name, self.venta, self.cuenta.id, self.activa, self.product.id, self.id))
        cur.close()

    def __repr__(self):
        return ("Instancia de Investment: {0} ({1})".format( self.name, self.id))
        
    def init__db_row(self, row, cuenta, mqinvestment):
        self.id=row['id_inversiones']
        self.name=row['inversion']
        self.venta=row['venta']
        self.cuenta=cuenta
        self.product=mqinvestment
        self.activa=row['in_activa']
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

        
    def get_operinversiones(self):
        """Funci`on que carga un array con objetos inversion operacion y con ellos calcula el set de actual e historicas"""
        cur=self.mem.con.cursor()
        self.op=SetInvestmentOperations(self.mem)
        cur.execute("SELECT * from operinversiones where id_inversiones=%s order by datetime", (self.id, ))
        for row in cur:
            self.op.append(InvestmentOperation(self.mem).init__db_row(row, self, self.mem.tiposoperaciones.find(row['id_tiposoperaciones'])))
        (self.op_actual,  self.op_historica)=self.op.calcular_new()
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
            return self.acciones()*self.product.estimations_dps.find(year).estimation
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
        if self.activa==False:
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(QApplication.translate("Core", "The associated product is not active. You must activate it first"))
            m.exec_()    
            return True
        return False
    def balance(self, fecha=None):
        """Función que calcula el balance de la inversión
            Si el curms es None se calcula el actual 
                Necesita haber cargado mq getbasic y operinversionesactual"""     
        acciones=self.acciones(fecha)
        if acciones==0 or self.product.result.basic.last.quote==None:#Empty xulpy
            return 0
                
        if fecha==None:
            return acciones*self.product.result.basic.last.quote
        else:
            if acciones==0:
                return Decimal('0')
            quote=Quote(self.mem).init__from_query(self.product, day_end_from_date(fecha, self.mem.localzone))
            if quote.datetime==None:
                print ("Investment balance: {0} ({1}) en {2} no tiene valor".format(self.name, self.product.id, fecha))
                return Decimal('0')
            return acciones*quote.quote
        
    def invertido(self):       
        """Función que calcula el balance invertido partiendo de las acciones y el precio de compra
        Necesita haber cargado mq getbasic y operinversionesactual"""
        resultado=Decimal('0')
        for o in self.op_actual.arr:
            resultado=resultado+(o.acciones*o.valor_accion)
        return resultado
                
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
        self.cuenta=None
        self.pagodiferido=None
        self.saldomaximo=None
        self.activa=None
        self.numero=None
        
        self.op_diferido=[]#array que almacena objetos CreditCard operacion que son en diferido
        
    def init__create(self, name, cuenta, pagodiferido, saldomaximo, activa, numero, id=None):
        """El parámetro cuenta es un objeto cuenta, si no se tuviera en tiempo de creación se asigna None"""
        self.id=id
        self.name=name
        self.cuenta=cuenta
        self.pagodiferido=pagodiferido
        self.saldomaximo=saldomaximo
        self.activa=activa
        self.numero=numero
        return self
        
    def init__db_row(self, row, cuenta):
        """El parámetro cuenta es un objeto cuenta, si no se tuviera en tiempo de creación se asigna None"""
        self.init__create(row['tarjeta'], cuenta, row['pagodiferido'], row['saldomaximo'], row['tj_activa'], row['numero'], row['id_tarjetas'])
        return self
                    
    def borrar(self):
        """
            Devuelve False si no ha podido borrarse por haber dependientes.
        """
        cur=self.mem.con.cursor()
        cur.execute("select count(*) from opertarjetas where id_tarjetas=%s", (self.id, ))
        if cur.fetchone()['count']>0: # tiene dependientes
            cur.close()
            return False
        else:
            sql="delete from tarjetas where id_tarjetas="+ str(self.id);
            cur.execute(sql)
            cur.close()
            return True
        
    def get_opertarjetas_diferidas_pendientes(self):
        """Funci`on que carga un array con objetos inversion operacion y con ellos calcula el set de actual e historicas"""
        cur=self.mem.con.cursor()
        self.op_diferido=[]
        cur.execute("SELECT * from opertarjetas where id_tarjetas=%s and pagado=false", (self.id, ))
        for row in cur:
            self.op_diferido.append(CreditCardOperation(self.mem).init__db_row(row, self.mem.conceptos.find(row['id_conceptos']), self.mem.tiposoperaciones.find(row['id_tiposoperaciones']), self))
        cur.close()
        
    def qmessagebox_inactive(self):
        if self.activa==False:
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(QApplication.translate("Core", "The associated credit card is not active. You must activate it first"))
            m.exec_()    
            return True
        return False
        
    def save(self):
        cur=self.mem.con.cursor()
        if self.id==None:
            cur.execute("insert into tarjetas (tarjeta,id_cuentas,pagodiferido,saldomaximo,tj_activa,numero) values (%s, %s, %s,%s,%s,%s) returning id_tarjetas", (self.name, self.cuenta.id,  self.pagodiferido ,  self.saldomaximo, self.activa, self.numero))
            self.id=cur.fetchone()[0]
        else:
            cur.execute("update tarjetas set tarjeta=%s, id_cuentas=%s, pagodiferido=%s, saldomaximo=%s, tj_activa=%s, numero=%s where id_tarjetas=%s", (self.name, self.cuenta.id,  self.pagodiferido ,  self.saldomaximo, self.activa, self.numero, self.id))

        cur.close()
        
    def saldo_pendiente(self):
        """Es el balance solo de operaciones difreidas sin pagar"""
        resultado=0
        for o in self.op_diferido:
            resultado=resultado+ o.importe
        return resultado

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


class Assets:
    def __init__(self, mem):
        self.mem=mem        
    
    def primera_datetime_con_datos_usuario(self):        
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

    def saldo_todas_inversiones_bonds(self, fecha):        
        """Versión que se calcula en cliente muy optimizada
        Fecha None calcula  el balance actual
        """
        resultado=0
#        inicio=datetime.datetime.now()
        for inv in self.mem.data.inversiones_all().arr:
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


class SetCreditCards:
    def __init__(self, mem, cuentas):
        self.arr=[]
#        self.dic_arr={} ##Prueba de duplicación
        self.mem=mem   
        self.cuentas=cuentas

    def load_from_db(self, sql):
        cur=self.mem.con.cursor()
        cur.execute(sql)#"Select * from tarjetas")
        for row in cur:
            t=CreditCard(self.mem).init__db_row(row, self.cuentas.find(row['id_cuentas']))
            if t.pagodiferido==True:
                t.get_opertarjetas_diferidas_pendientes()
#            self.dic_arr[str(t.id)]=t
            self.arr.append(t)
        cur.close()
            
    def clone_of_account(self, cuenta):
        """Devuelve un SetCreditCards con las tarjetas de una determinada cuenta"""
        s=SetCreditCards(self.mem, self.cuentas)
        for t in self.arr:
            if t.cuenta==cuenta:
                s.arr.append(t)
        return s

    def find(self, id):
        for t in self.arr:
            if t.id==id:
                return t
#        return self.dic_arr[str(id)]
        
#    def tarjetas(self, id=None):
#        if id==None:
#            return dic2list(self.dic_tarjetas)
#        else:
#            return self.dic_tarjetas[str(id)]
#                        
#    def tarjetas_activas(self, activa=True):
#        resultado=[]
#        for i in self.tarjetas():
#            if i.activa==activa:
#                resultado.append(i)
#        return resultado
                    
    def union(self,  list2, cuentasunion):
        """Devuelve un SetBanks con la union del set1 y del set2"""
        resultado=SetCreditCards(self.mem, cuentasunion)
        resultado.arr=self.arr+list2.arr
        return resultado
        
        
class SetOperationTypes:      
    def __init__(self, mem):
        self.dic_arr={}
        self.mem=mem     
        
    def load(self):
        self.dic_arr['1']=OperationType().init__create( "Gasto", 1)
        self.dic_arr['2']=OperationType().init__create( "Ingreso", 2)
        self.dic_arr['3']=OperationType().init__create( "Trasferencia", 3)
        self.dic_arr['4']=OperationType().init__create( "Compra de acciones", 4)
        self.dic_arr['5']=OperationType().init__create( "Venta de acciones", 5)
        self.dic_arr['6']=OperationType().init__create( "Añadido de acciones", 6)
        self.dic_arr['7']=OperationType().init__create( "Facturacion CreditCard", 7)
        self.dic_arr['8']=OperationType().init__create( "Traspaso fondo inversión", 8) #Se contabilizan como ganancia
        self.dic_arr['9']=OperationType().init__create( "Traspaso de valores. Origen", 9) #No se contabiliza
        self.dic_arr['10']=OperationType().init__create( "Traspaso de valores. Destino", 10) #No se contabiliza     
        


    def qcombobox(self, combo):
        for t in self.clone_only_operinversiones().list():
            combo.addItem(t.name,  t.id)
    def qcombobox_basic(self, combo, selected=None):
        """Selected is a Operation Type id"""
        combo.clear()
        combo.addItem(self.dic_arr['1'].name,  self.dic_arr['1'].id)
        combo.addItem(self.dic_arr['2'].name,  self.dic_arr['2'].id)
        if selected!=None:
            combo.setCurrentIndex(combo.findData(selected.id))
        

    def find(self, id):
        return self.dic_arr[str(id)]
        
    def list(self):
        """Lista ordenada por nombre"""
        lista=dic2list(self.dic_arr)
        lista=sorted(lista, key=lambda t:t.name, reverse=False)
        return lista
        
    def clone_only_operinversiones(self):
        """Devuelve los tipos de operación específicos de operinversiones. en un arr de la forma"""
        resultado=SetOperationTypes(self.mem)
        for key,  t in self.dic_arr.items():
            if key in ('4', '5', '6', '8'):
                resultado.dic_arr[str(key)]=t
        return resultado


def mylog(text):
    f=open("/tmp/xulpymoney.log","a")
    f.write(str(datetime.datetime.now()) + "|" + text + "\n")
    f.close()
    
def decimal_check(dec):
    print ("Decimal check", dec, dec.__class__,  dec.__repr__(),  "prec:",  getcontext().prec)
    

    
#def decimalesSignificativos(arraynum):
#    """ESta función busca en quotes_basic para calcular los bits significativos de los quotes, para poder mostrarlos mejor"""
#    return 6
#    
#    ##DEBE CAMBIARSE A ARRAY DE NUMEROS
#    resultado=2
#    if self.last==None or self.penultimate==None or self.endlastyear==None:
##            print ("mal",  resultado)
#        return resultado
#    
#    for num in [self.last.quote, self.penultimate.quote, self.endlastyear.quote]:
#        decimales=str(num).split(".")
#        if len(decimales)==2:
#            cadena=decimales[1]
#            while len(cadena)>=2:
#                if cadena[len(cadena)-1]=="0":
#                    cadena=cadena[:-1]
#                else:
#                    resultado=len(cadena)
#                    break
##        print ("significativos",  self.last.quote,  self.penultimate.quote,  self.endlastyear.quote,  resultado)
#    return resultado

class SetAgrupations:
    """Se usa para meter en mem las agrupaciones, pero también para crear agrupaciones en las inversiones"""
    def __init__(self, mem):
        """Usa la variable mem.Agrupations"""
        self.mem=mem
        self.dic_arr={}
        
        
    def load_all(self):
        self.dic_arr["ERROR"]=Agrupation(self.mem).init__create( "ERROR","Agrupación errónea", self.mem.types.find(3), self.mem.stockexchanges.find(1) )
        self.dic_arr["IBEX"]=Agrupation(self.mem).init__create( "IBEX","Ibex 35", self.mem.types.find(3), self.mem.stockexchanges.find(1) )
        self.dic_arr["MERCADOCONTINUO" ]=Agrupation(self.mem).init__create( "MERCADOCONTINUO","Mercado continuo español", self.mem.types.find(3), self.mem.stockexchanges.find(1) )
        self.dic_arr[ "CAC"]=Agrupation(self.mem).init__create("CAC",  "CAC 40 de París", self.mem.types.find(3),self.mem.stockexchanges.find(3) )
        self.dic_arr["EUROSTOXX"]=Agrupation(self.mem).init__create( "EUROSTOXX","Eurostoxx 50", self.mem.types.find(3),self.mem.stockexchanges.find(10)  )
        self.dic_arr["DAX"]=Agrupation(self.mem).init__create( "DAX","DAX", self.mem.types.find(3), self.mem.stockexchanges.find(5)  )
        self.dic_arr["SP500"]=Agrupation(self.mem).init__create("SP500",  "Standard & Poors 500", self.mem.types.find(3), self.mem.stockexchanges.find(2)  )
        self.dic_arr["NASDAQ100"]=Agrupation(self.mem).init__create( "NASDAQ100","Nasdaq 100", self.mem.types.find(3), self.mem.stockexchanges.find(2)  )
        self.dic_arr["EURONEXT"]=Agrupation(self.mem).init__create( "EURONEXT",  "EURONEXT", self.mem.types.find(3), self.mem.stockexchanges.find(10)  )
        self.dic_arr["DEUTSCHEBOERSE"]=Agrupation(self.mem).init__create( "DEUTSCHEBOERSE",  "DEUTSCHEBOERSE", self.mem.types.find(3), self.mem.stockexchanges.find(5)  )
        self.dic_arr["LATIBEX"]=Agrupation(self.mem).init__create( "LATIBEX",  "LATIBEX", self.mem.types.find(3), self.mem.stockexchanges.find(1)  )


        self.dic_arr["e_fr_LYXOR"]=Agrupation(self.mem).init__create( "e_fr_LYXOR","LYXOR", self.mem.types.find(4),self.mem.stockexchanges.find(3)  )
        self.dic_arr["e_de_DBXTRACKERS"]=Agrupation(self.mem).init__create( "e_de_DBXTRACKERS","Deutsche Bank X-Trackers", self.mem.types.find(4),self.mem.stockexchanges.find(5)  )
        
        self.dic_arr["f_es_0014"]=Agrupation(self.mem).init__create("f_es_0014",  "Gestora BBVA", self.mem.types.find(2), self.mem.stockexchanges.find(1) )
        self.dic_arr["f_es_0043"]=Agrupation(self.mem).init__create( "f_es_0043","Gestora Renta 4", self.mem.types.find(2), self.mem.stockexchanges.find(1))
        self.dic_arr["f_es_0055"]=Agrupation(self.mem).init__create("f_es_0055","Gestora Bankinter", self.mem.types.find(2),self.mem.stockexchanges.find(1) )
        self.dic_arr["f_es_BMF"]=Agrupation(self.mem).init__create( "f_es_BMF","Fondos de la bolsa de Madrid", self.mem.types.find(2), self.mem.stockexchanges.find(1) )

        self.dic_arr["w_fr_SG"]=Agrupation(self.mem).init__create( "w_fr_SG","Warrants Societe Generale", self.mem.types.find(5),self.mem.stockexchanges.find(3) )
        self.dic_arr["w_es_BNP"]=Agrupation(self.mem).init__create("w_es_BNP","Warrants BNP Paribas", self.mem.types.find(5),self.mem.stockexchanges.find(1))

    def find(self, id):
        try:
            return self.dic_arr[str(id)]        
        except:
            return self.dic_arr["ERROR"]
                
    def list_sortby_id(self):
        """Devuelve una lista ordenada por id """
        resultado=dic2list(self.dic_arr)
        resultado=sorted(resultado, key=lambda c: c.id,  reverse=False)     
        return resultado
        
    def list(self):
        """Devuelve una lista ordenada por name"""
        resultado=dic2list(self.dic_arr)
        resultado=sorted(resultado, key=lambda c: c.name,  reverse=False)     
        return resultado
    
    def clone(self):
        resultado=SetAgrupations(self.mem)
        for k, a in self.dic_arr.items():
            resultado.dic_arr[k]=a
        return resultado
    
    def clone_by_type(self,  type):
        """Muestra las agrupaciónes de un tipo pasado como parámetro. El parámetro type es un objeto Type"""
        resultado=SetAgrupations(self.mem)
        for k, a in self.dic_arr.items():
            if a.type==type:
                resultado.dic_arr[k]=a
        return resultado

        
    def clone_etfs(self):
        """Función que filtra el diccionario a según el país y el fondo """
        return self.clone_by_type(self.mem.types.find(4))
        
#        return {k:v for k,v in self.mem.Agrupations.items() if k[0]=='e' and  k[2]==country[0] and k[3]==country[1]}
    def clone_warrants(self):
        """Función que filtra el diccionario a según el país y el fondo """
        return self.clone_by_type(self.mem.types.find(5))
        
    def clone_fondos(self):
        """Función que filtra el diccionario a según el país y el fondo """
        return self.clone_by_type(self.mem.types.find(2))
        
    def clone_acciones(self):
        """Función que filtra el diccionario a según el país y el fondo """
        return self.clone_by_type(self.mem.types.find(3))
        
        
    def clone_from_dbstring(self, dbstr):
        """Convierte la cadena de la base datos en un array de objetos agrupation"""
        resultado=SetAgrupations(self.mem)
        if dbstr==None or dbstr=="":
            pass
        else:
            for item in dbstr[1:-1].split("|"):
                resultado.dic_arr[item]=self.mem.agrupations.find(item)
        return resultado
        
    def qcombobox(self, combo):
        combo.clear()
        for a in self.list():
            combo.addItem(a.name, a.id)
            
    def dbstring(self):
        resultado="|"
        for a in self.list():
            resultado=resultado+a.id+"|"
        if resultado=="|":
            return ""
        return resultado
        
        
    def clone_from_combo(self, cmb):
        """Función que convierte un combo de agrupations a un array de agrupations"""
        resultado=SetAgrupations(self.mem)
        for i in range (cmb.count()):
            resultado.dic_arr[str(cmb.itemData(i))]=self.mem.agrupations.find(cmb.itemData(i))
        return resultado

class SetLeverages:
    def __init__(self, mem):
        """Usa la variable mem.Agrupations"""
        self.mem=mem
        self.dic_arr={}
                
        
    def load_all(self):
        self.dic_arr["0"]=Apalancamiento(self.mem).init__create(0 ,QApplication.translate("Core","Not leveraged"), 1)
        self.dic_arr["1"]=Apalancamiento(self.mem).init__create( 1,QApplication.translate("Core","Variable leverage (Warrants)"), 10)
        self.dic_arr["2"]=Apalancamiento(self.mem).init__create( 2,QApplication.translate("Core","Leverage x2"), 2)
        self.dic_arr["3"]=Apalancamiento(self.mem).init__create( 3,QApplication.translate("Core","Leverage x3"), 3)
        self.dic_arr["4"]=Apalancamiento(self.mem).init__create( 4,QApplication.translate("Core","Leverage x4"), 4)
               

    def qcombobox(self, combo):
        """Carga entidades bancarias en combo"""
        for a in self.list():
            combo.addItem(a.name, a.id)      
        
    def list(self):
        """Devuelve una lista ordenada por nombre """
        arr=dic2list(self.dic_arr)
        arr=sorted(arr, key=lambda a: a.name,  reverse=False)         
        return arr
        
    def find(self, id):
        return self.dic_arr[str(id)]

class SetPriorities:
    def __init__(self, mem):
        """Usa la variable mem.Agrupations. Debe ser una lista no un diccionario porque importa el orden"""
        self.mem=mem
        self.arr=[]
                
    def load_all(self):
        self.arr.append(Priority().init__create(1,"Yahoo Financials. 200 pc."))
        self.arr.append(Priority().init__create(2,"Fondos de la bolsa de Madrid. Todos pc."))
        self.arr.append(Priority().init__create(3,"Borrar"))#SANTGES ERA 3, para que no se repitan
        self.arr.append(Priority().init__create(7,"Bond alemán desde http://jcbcarc.dyndns.org. 3 pc."))#SANTGES ERA 3, para que no se repitan
        self.arr.append(Priority().init__create(4,"Infobolsa. índices internacionales. 20 pc."))
        self.arr.append(Priority().init__create(5,"Productos cotizados bonus. 20 pc."))
        self.arr.append(Priority().init__create(6,"Societe Generale Warrants. Todos pc."))

    def qcombobox(self, combo):
        combo.clear()
        for a in self.arr:
            combo.addItem(a.name, a.id)
            
    def find(self, id):
        for a in self.arr:
            if a.id==id:
                return a
        return None
        
    def init__create_from_db(self, arr):
        """Convierte el array de enteros de la base datos en un array de objetos priority"""
        resultado=SetPriorities(self.mem)
        if arr==None or len(arr)==0:
            resultado.arr=[]
        else:
            for a in arr:
                resultado.arr.append(self.mem.priorities.find(a))
        return resultado
        
    def clone(self):
        """Devuelve los tipos de operación específicos de operinversiones. en un arr de la forma"""
        resultado=SetPriorities(self.mem)
        for a in self.arr:
            resultado.arr.append(a)
        return resultado


    def array_of_id(self):
        """Used to psycopg.execute automatical pare"""
        resultado=[]
        for p in self.arr:
            resultado.append(p.id)
        return resultado
            

#    def dbstring(self):
#        if len(self.arr)==0:
#            return "NULL"
#        else:
#            resultado=[]
#            for a in self.arr:
#                resultado.append(a.id)
#            return "ARRAY"+str(resultado)
        
    def init__create_from_combo(self, cmb):
        """Función que convierte un combo de agrupations a un array de agrupations"""
        for i in range (cmb.count()):
            self.arr.append(self.mem.priorities.find(cmb.itemData(i)))
        return self
                
class SetPrioritiesHistorical:
    def __init__(self, mem):
        """Usa la variable mem.Agrupations"""
        self.mem=mem
        self.arr=[]
        
            
    def load_all(self):
        self.arr.append(PriorityHistorical().init__create(3,"Individual. Yahoo historicals"))
        
        

    def qcombobox(self, combo):
        combo.clear()
        for a in self.arr:
            combo.addItem(a.name, a.id)
                    
    def clone(self):
        """Devuelve los tipos de operación específicos de operinversiones. en un arr de la forma"""
        resultado=SetPrioritiesHistorical(self.mem)
        for a in self.arr:
            resultado.arr.append(a)
        return resultado

        
    def find(self, id):
        for a in self.arr:
            if a.id==id:
                return a
        return None
            
    def init__create_from_db(self, arr):
        """Convierte el array de enteros de la base datos en un array de objetos priority"""
        resultado=SetPrioritiesHistorical(self.mem)
        if arr==None or len(arr)==0:
            resultado.arr=[]
        else:
            for a in arr:
                resultado.arr.append(self.mem.prioritieshistorical.find(a))
        return resultado

    def array_of_id(self):
        """Used to psycopg.execute automatical pare"""
        resultado=[]
        for p in self.arr:
            resultado.append(p.id)
        return resultado
        
#    def dbstring(self):
#        if len(self.arr)==0:
#            return "NULL"
#        else:
#            resultado=[]
#            for a in self.arr:
#                resultado.append(a.id)
#            return "ARRAY"+str(resultado)
        
    def init__create_from_combo(self, cmb):
        """Función que convierte un combo de agrupations a un array de agrupations"""
        for i in range (cmb.count()):
            self.arr.append(self.mem.prioritieshistorical.find(cmb.itemData(i)))
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
        self.zone=self.mem.zones.find(row['zone'])#Intente hacer objeto pero era absurdo.
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


#
#def softwareversion():
#    return "20110409"

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
            
    def currencies_exchange(self, curms,  quote, origen, destino):
        cambio=Quote.valor2(curms, origen+"2"+destino, quote['fecha'],  quote['hora'])
        exchange={"code":quote['code'],"quote":quote['quote']*cambio['quote'],  "date":cambio['date'], "time":cambio['time'],  "zone":cambio['zone'],  "currency":destino}
        return exchange

    def qtablewidgetitem(self, n, digits=2):
        """Devuelve un QTableWidgetItem mostrando un currency
        curren es un objeto Curryency"""
        text= (self.string(n,  digits))
        a=QTableWidgetItem(text)
        a.setTextAlignment(Qt.AlignVCenter|Qt.AlignRight)
        if n==None:
            a.setTextColor(QColor(0, 0, 255))
        elif n<0:
            a.setTextColor(QColor(255, 0, 0))
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

    def currencies_exchange(self, curms,  quote, origen, destino):
        cambio=Quote.valor2(curms, origen+"2"+destino, quote['fecha'],  quote['hora'])
        exchange={"code":quote['code'],"quote":quote['quote']*cambio['quote'],  "date":cambio['date'], "time":cambio['time'],  "zone":cambio['zone'],  "currency":destino}
        return exchange

    def qtablewidgetitem(self, digits=2):
        """Devuelve un QTableWidgetItem mostrando un currency
        curren es un objeto Curryency"""
        text= (self.string(  digits))
        a=QTableWidgetItem(text)
        a.setTextAlignment(Qt.AlignVCenter|Qt.AlignRight)
        if n==None:
            a.setTextColor(QColor(0, 0, 255))
        elif n<0:
            a.setTextColor(QColor(255, 0, 0))
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
        cur=self.mem.conms.cursor()
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
        table.setHorizontalHeaderItem(0, QTableWidgetItem(QApplication.translate("Core", "Date", None, QApplication.UnicodeUTF8)))
        table.setHorizontalHeaderItem(1, QTableWidgetItem(QApplication.translate("Core", "Gross", None, QApplication.UnicodeUTF8)))
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
        cur=self.mem.conms.cursor()
        cur.execute("delete from dps where id_dps=%s", (self.id,))
        cur.close()
            
    def save(self):
        """Función que comprueba si existe el registro para insertar o modificarlo según proceda"""
        curms=self.mem.conms.cursor()
        if self.id==None:
            curms.execute("insert into dps(date, gross,id) values (%s,%s,%s) returning id_dps", (self.date, self.gross, self.product.id))
            self.id=curms.fetchone()[0]
        else:         
            curms.execute("update dps set date=%s, gross=%s, id=%s where id_dps=%s", (self.date,  self.gross, self.product.id, self.id))
        curms.close()
        

        
        
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
        cur=self.mem.conms.cursor()
        cur.execute("select estimation, date_estimation ,source,manual from estimations_eps where id=%s and year=%s", (product.id, currentyear))
        if cur.rowcount==1:
            row=cur.fetchone()
            self.init__create(product, currentyear, row['date_estimation'], row['source'], row['manual'], row['estimation'])
            cur.close()
        else:
            self.init__create(product, currentyear, None, None, None, None)
        return self
            
            
    def borrar(self):
        cur=self.mem.conms.cursor()
        cur.execute("delete from estimations_eps where id=%s and year=%s", (self.product.id, self.year))
        cur.close()
            
    def save(self):
        """Función que comprueba si existe el registro para insertar o modificarlo según proceda"""
        curms=self.mem.conms.cursor()
        curms.execute("select count(*) from estimations_eps where id=%s and year=%s", (self.product.id, self.year))
        if curms.fetchone()[0]==0:
            curms.execute("insert into estimations_eps(id, year, estimation, date_estimation, source, manual) values (%s,%s,%s,%s,%s,%s)", (self.product.id, self.year, self.estimation, self.date_estimation, self.source, self.manual))

            print (curms.mogrify("insert into estimations_eps (id, year, estimation, date_estimation, source, manual) values (%s,%s,%s,%s,%s,%s)", (self.product.id, self.year, self.estimation, self.date_estimation, self.source, self.manual)))
        elif self.estimation!=None:            
            curms.execute("update estimations_eps set estimation=%s, date_estimation=%s, source=%s, manual=%s where id=%s and year=%s", (self.estimation, self.date_estimation, self.source, self.manual, self.product.id, self.year))
        curms.close()
        
        
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
        cur=self.mem.conms.cursor()
        cur.execute("select estimation, date_estimation ,source,manual from estimations_dps where id=%s and year=%s", (product.id, currentyear))
        if cur.rowcount==1:
            row=cur.fetchone()
            self.init__create(product, currentyear, row['date_estimation'], row['source'], row['manual'], row['estimation'])
            cur.close()
        else:
            self.init__create(product, currentyear, None, None, None, None)
        return self
            
            
    def borrar(self):
        cur=self.mem.conms.cursor()
        cur.execute("delete from estimations_dps where id=%s and year=%s", (self.product.id, self.year))
        cur.close()
            
    def save(self):
        """Función que comprueba si existe el registro para insertar o modificarlo según proceda"""
        curms=self.mem.conms.cursor()
        curms.execute("select count(*) from estimations_dps where id=%s and year=%s", (self.product.id, self.year))
        if curms.fetchone()[0]==0:
            curms.execute("insert into estimations_dps(id, year, estimation, date_estimation, source, manual) values (%s,%s,%s,%s,%s,%s)", (self.product.id, self.year, self.estimation, self.date_estimation, self.source, self.manual))
#            print (curms.mogrify("insert into estimations_dps (id, year, estimation, date_estimation, source, manual) values (%s,%s,%s,%s,%s,%s)", (self.product.id, self.year, self.estimation, self.date_estimation, self.source, self.manual)))
        elif self.estimation!=None:            
            curms.execute("update estimations_dps set estimation=%s, date_estimation=%s, source=%s, manual=%s where id=%s and year=%s", (self.estimation, self.date_estimation, self.source, self.manual, self.product.id, self.year))
        curms.close()
        
    def percentage(self):
        """Hay que tener presente que endlastyear (Objeto Quote) es el endlastyear del año actual
        Necesita tener cargado en id el endlastyear """
        try:
            return self.estimation*100/self.product.result.basic.last.quote
        except:
            return None

        
class SourceNew:
    """Clase nueva para todas las sources
    Debera:
    - Cargar al incio un sql con las products del source"""
    def __init__(self, mem, sql):
        self.products=[]
        self.load_investments(sql)
    def load_investments(self,  sql):
        return
        
    def investments_to_search(self):
        """Función que devuelve un array con las products a buscar después de hacer filtros
        Estos filtros son:
        - Filtro por horarios, aunque busque tarde debe meter la hora bien con .0001234, debe permitir primero"""
        
class SourceIntraday(SourceNew):
    def __init__(self, mem, sql):
        SourceNew.__init__(self, mem, sql)
        
        
class SourceDailyUnique(SourceNew):
    def __init__(self, mem, sql):
        SourceNew.__init__(self, mem, sql)
    
class SourceDailyGroup(SourceNew):
    def __init__(self, mem, sql):
        SourceNew.__init__(self, mem, sql)

    
    
class Source:
    """Solo se debe cambiar la función arr_*, independiente de si se usa static o statics
    Al crear uno nuevo se debe crear un start, que  no es heredada ni virtual en la que se cojan los distintos updates con process
    Luego crear las funciones virtuales.
    """
    def __init__(self,  mem):

        self.mem=mem
        self.debugmode=False#Si fuera true en vez de insertar  hace un listado#       
        self.internetquerys=0#Número de consultas a Internet
        self.downloadalways=False#Booleano que a true permite download los fines de semana
#        self.downloadrange=(datetime.time(0, 0), datetime.time(23, 59)) #Estas horas deben estar en utc
        
    def print_parsed(self,  parsed):
        for p in parsed:
            print ("{0:>6} {2} {1:>10} ".format(p['id'], p['quote'], p['datetime']))
        
    def parse_errors(self, cur, errors):
        er=0
        for e in errors:
            if e==None:
                er=er+1
            else:
                self.mem.activas[str(e)].priority_change(cur)
        if er>0:
            print ("{0} errores no se han podido parsear".format(er))
            
        
    def arr_quote(self, code):
        return []
#        
#    def arr_quotes(self):
#        return []
#        
#    def arr_historical(self, code,  isin=''):
#        """isin se usa cuando se ha obtenido el code por isin2yahoocode para poner el nombre en code con yahoo_historical"""
#        return []
#        
#    def arr_static(self, code):
#        return []
#        
#    def arr_statics(self):
#        return []
#        
#    def arr_dividends(self):
#        return []
#        
#    def arr_dividend(self, code):
#        return []
        
    def filtrar_ids_primerregistro_ge_iniciodb(self,  ids):
        """Filtra aquellos ids cuyo primer registro es mayor que el inicio de la base de datos. Es decir que no se han buscado historicos"""
        con=self.mem.connect_mystocksd()
        cur = con.cursor()     
        resultado=[]
        for id in ids:
            cur.execute(" select id, count(*) from quotes where id in (select id from products where active=false and priority[1]=1) group by id;=%s and datetime::date<%s", (id, self.mem.dbinitdate))
            if cur.fetchone()[0]==0:
                resultado.append(id)
        cur.close()                
        self.mem.disconnect_mystocksd(con)
        return resultado
                
    def filtrar_ids_inactivos_no_actualizados(self, cur,  idpriority, dias,  priorityhistorical=False):
        """Filtra aquellos ids consultando a la base dpe datos, que tengan activa un id_prioridad
        o un id_prioridadhistorical si priorityhistorical=True y que no hayan sido actualizados desde now()-dias
        y que esten inactivo"""
        resultado=[]
        if priorityhistorical==False:
            cur.execute("select * from products where (select count(*) from quotes where id=products.id and datetime>now()::date-%s)=0 and active=false and priority[1]=%s;", (dias,  idpriority))   
        else:
            cur.execute("select * from products where (select count(*) from quotes where id=products.id and datetime>now()::date-%s)=0 and active=false and priorityhistorical[1]=%s;", (dias,  idpriority))   
        for row in cur:
            resultado.append(Product(self.mem).init__db_row(self.mem, row))
        return resultado
        
    def find_ids(self):
        """Devuelve un array con los objetos de Product que cumplen"""
        print ("find_ids es obsoleto hacer con query")
        self.ids=[]
        for inv in self.mem.activas():
            if inv.active==True: #Debe ser activa
                if len(inv.priority.arr)>0:
                    if inv.priority.arr[0].id==self.id_source: #Seleccion generica
                        #particularidades
                        if self.id_source==1 : #Caso de yahoo
                            if inv.ticker!=None or inv.ticker!='':#Comprueba que tiene ticker
                                self.ids.append(inv)
                        else:
                                self.ids.append(inv)
#        print (len(self.ids))
        return self.ids        
        
    def find_ids_historical(self):
        """Función que busca todos los ids de las inversiones con priorityhistorical=id_source y que estén activas"""
        self.ids=[]
        for inv in self.mem.activas():
            if inv.active==True: #Debe ser activa
                if len(inv.priorityhistorical.arr)>0:
                    if inv.priorityhistorical.arr[0].id==self.id_source: #Seleccion generica
                        #particularidades
                        if  self.id_source==3: #Caso de yahoo
                            if inv.ticker!=None or inv.ticker!='':#Comprueba que tiene yahoo
                                self.ids.append(inv)
                        else:
                                self.ids.append(inv)
        return self.ids

#        
#    def filtrar_ids(self, ids):
#        ids=self.filtrar_horario_bolsa(ids)
#        return ids
        
        
    def isin2id(self, isin,  id_stockexchanges):
        for i in self.mem.activas:
            if isin==self.mem.activas[i].isin and id_stockexchanges==self.mem.activas[i].id_stockexchanges:
                return int(i)
        return None
        

    def download(self, url,  function,  controltime=True):
        """Función que devuelve la salida del comando urllib, normalmente es el parametro web o None si ha salido mal la descarga
        """
        download=True
        message=""
        
        if message!="" and download==True:
            log(self.name, "DOWNLOAD",  message)
        
        if download==True:     
            try:                 
                web=urllib.request.urlopen(url)
            except:            
#                cur=con.cursor()
#                status_update(cur, self.name, "Update quotes", status='Downloading error',  statuschange=datetime.datetime.now())
#                con.commit()
#                cur.close()
#                self.mem.disconnect_mystocksd(con)    
#                time.sleep(60)
                return None
        else:
            return None
#        con=self.mem.connect_mystocksd()
#        cur=con.cursor()
#        self.internetquerys=self.internetquerys+1
#        status_update(cur, self.name, "Update quotes", internets=self.internetquerys)
#        con.commit()
#        cur.close()
#        self.mem.disconnect_mystocksd(con)    
        return web

    def update_step_quotes(self, sql):
        """Hace un bucle con los distintos codes del sql."""
        con=self.mem.connect_mystocksd()
        cur=con.cursor()
        status_insert(cur, self.name, "Update stepcode quotes")
        con.commit()
        cur.close()
        mem.disconnect_mystocksd(con)   
        while True:
            time.sleep(self.time_before_quotes)
            con=self.mem.connect_mystocksd()
            cur=con.cursor()
            cur2=con.cursor()
            status_update(cur, self.name, "Update step quotes", status='Working',  statuschange=datetime.datetime.now())
            con.commit()
            cur.execute(sql)
            for row in cur:
                if self.debugmode==True:
                    for i in self.arr_quote(row['code']):
                        print (i)
    #                log("S_SOCIETEGENERALEWARRANTS_STATICS", QApplication.translate("Core",("%d de %d" %(cur.rownumber, cur.rowcount)))
                else:
                    Quote(self.mem).insert_cdtv(self.arr_quote(row['code']), self.name)
                status_update(cur2, self.name, "Update step quotes", status='Waiting step',  statuschange=datetime.datetime.now())
                con.commit()
                time.sleep(self.time_step_static)
            
            status_update(cur2, self.name, "Update step quotes", status='Waiting after',  statuschange=datetime.datetime.now())
            con.commit()
            cur.close()
            cur2.close()
            mem.disconnect_mystocksd(con)    
            time.sleep( self.time_after_statics)
        
#        
#    def update_quotes(self):
#        con=self.mem.connect_mystocksd()
#        cur=con.cursor()
#        status_insert(cur, self.name, "Update quotes")
#        status_update(cur, self.name, "Update quotes", status='Waiting before',  statuschange=datetime.datetime.now())
#        con.commit()
#        cur.close()
#        self.mem.disconnect_mystocksd(con)   
#        time.sleep(self.time_before_quotes)      
#        while True:      
#            con=self.mem.connect_mystocksd()
#            cur=con.cursor()
#            status_update(cur, self.name, "Update quotes", status='Working',  statuschange=datetime.datetime.now())
#            con.commit()
#            cur.close()
#            self.mem.disconnect_mystocksd(con)    
#            if self.debugmode==True:
#                for i in self.arr_quotes():
#                    print (i)
#            else:
#                Quote(self.mem).insert_cdtv(self.arr_quotes(), self.name)
#            con=self.mem.connect_mystocksd()
#            cur=con.cursor()
#            status_update(cur, self.name, "Update quotes", status='Waiting after',  statuschange=datetime.datetime.now())
#            con.commit()
#            cur.close()
#            self.mem.disconnect_mystocksd(con)               
#            time.sleep(self.time_after_quotes)


#    def update_statics(self):
#        con=self.mem.connect_mystocksd()
#        cur=con.cursor()
#        status_insert(cur, self.name, "Update statics")
#        status_update(cur, self.name, "Update statics", status='Waiting before',  statuschange=datetime.datetime.now())
#        con.commit()
#        cur.close()
#        self.mem.disconnect_mystocksd(con)   
#        time.sleep(self.time_before_statics)
#        while True:            
#            con=self.mem.connect_mystocksd()
#            cur=con.cursor()
#            status_update(cur, self.name, "Update statics", status='Working',  statuschange=datetime.datetime.now())
#            con.commit()
#            cur.close()
#            self.mem.disconnect_mystocksd(con)    
#            if self.debugmode==True:
#                for i in self.arr_statics():
#                    print (i)
#            else:
#                Product(self.mem).update_static(self.arr_statics(), self.name)
#            con=self.mem.connect_mystocksd()
#            cur=con.cursor()
#            status_update(cur, self.name, "Update statics", status='Waiting after',  statuschange=datetime.datetime.now())
#            con.commit()
#            cur.close()
#            self.mem.disconnect_mystocksd(con)                     
#            time.sleep(self.time_after_statics)
            
#    def update_step_statics(self, sql):
#        """Hace un bucle con los distintos codes del sql."""
#        con=self.mem.connect_mystocksd()
#        cur=con.cursor()
#        status_insert(cur, self.name, "Update step statics")
#        status_update(cur, self.name, "Update step statics", status='Waiting before',  statuschange=datetime.datetime.now())
#        con.commit()
#        cur.close()
#        self.mem.disconnect_mystocksd(con)    
#        time.sleep(self.time_before_statics)
#        while True:
#            con=self.mem.connect_mystocksd()
#            cur=con.cursor()
#            cur2=con.cursor()
#            status_update(cur, self.name, "Update statics", status='Working',  statuschange=datetime.datetime.now())
#            con.commit()
#            cur.execute(sql)
#            for row in cur:
#                if self.debugmode==True:
#                    for i in self.arr_static(row['code']):
#                        print (i)
#    #                log("S_SOCIETEGENERALEWARRANTS_STATICS", QApplication.translate("Core",("%d de %d" %(cur.rownumber, cur.rowcount)))
#                else:
#                    Product(self.mem).update_static(self.arr_static(row['code']), self.name)
#
#                status_update(cur2, self.name, "Update step statics", status='Waiting step',  statuschange=datetime.datetime.now())    
#                con.commit()
#                time.sleep(self.time_step_static)
#
#            status_update(cur2, self.name, "Update step statics", status='Waiting after',  statuschange=datetime.datetime.now())                    
#            con.commit()
#            cur.close()
#            cur2.close()
#            self.mem.disconnect_mystocksd(con)    
#            time.sleep( self.time_after_statics)
#            
#    def update_stepcode_statics(self, listcode):
#        """Hace un bucle con los distintos codes del listcode."""        
##        con=self.mem.connect_mystocksd()
##        cur=con.cursor()
##        status_insert(cur, self.name, "Update stepcode statics")
##        status_update(cur, self.name, "Update stepcode statics", status='Waiting before',  statuschange=datetime.datetime.now())
##        con.commit()
##        cur.close()
##        self.mem.disconnect_mystocksd(con)   
#        time.sleep(self.time_before_statics)
#        while True:
#            for code in listcode:
#                if self.debugmode==True:
#                    for i in self.arr_static(code):
#                        print (i)
#                else:
#                    Product(self.mem).update_static(self.arr_static(code), self.name)
#                time.sleep(self.time_step_static)
#            time.sleep( self.time_after_statics)
#
#    def update_step_historicals(self, listcodes):
#        con=self.mem.connect_mystocksd()
#        cur=con.cursor()
#        status_insert(cur, self.name, "Update step historicals")
#        status_update(cur, self.name, "Update step historicals", status='Waiting before',  statuschange=datetime.datetime.now())
#        con.commit()
#        cur.close()
#        self.mem.disconnect_mystocksd(con)   
#        time.sleep(self.time_before_historicals)
#        while True:
#            con=self.mem.connect_mystocksd()
#            cur=con.cursor()
#            status_update(cur, self.name, "Update step historicals", status='Working',  statuschange=datetime.datetime.now())
#            con.commit()
#            cur.close()
#            self.mem.disconnect_mystocksd(con)                
#            for code in listcodes:
##                print code,  listcodes
#                if self.debugmode==True:
#                    for i in self.arr_historical(code):
#                        print (i)
#                else:                
##                    print "Ha llegado"
#                    Quote(self.mem).insert_cdtohclv(self.arr_historical(code, ''),  self.name)
#                con=self.mem.connect_mystocksd()
#                cur=con.cursor()
#                status_update(cur, self.name, "Update step historicals", status='Waiting step',  statuschange=datetime.datetime.now())
#                con.commit()
#                cur.close()
#                self.mem.disconnect_mystocksd(con)       
#                time.sleep(self.time_step_historical)
#
#            con=self.mem.connect_mystocksd()
#            cur=con.cursor()
#            status_update(cur, self.name, "Update step historicals", status='Waiting after',  statuschange=datetime.datetime.now())
#            con.commit()
#            cur.close()
#            self.mem.disconnect_mystocksd(con)                       
#            time.sleep(self.time_after_historicals)
#
#    def update_step_historicals_by_isin(self, sql):
#        """Sql debe devolver isin solamente"""
#        con=self.mem.connect_mystocksd()
#        cur=con.cursor()
#        status_insert(cur, self.name, "Update step historicals by isin")
#        status_update(cur, self.name, "Update step historicals by isin", status='Waiting before',  statuschange=datetime.datetime.now())
#        con.commit()
#        cur.close()
#        self.mem.disconnect_mystocksd(con)   
#        time.sleep(self.time_before_historicals)
#        while True:
#            con=self.mem.connect_mystocksd()
#            cur=con.cursor()
#            status_update(cur, self.name, "Update step historicals", status='Working',  statuschange=datetime.datetime.now())
#            con.commit()            
#            cur.execute(sql)            
#            lista=[]
#            for i in cur:
#                lista.append(i['isin'])
#            cur.close()
#            self.mem.disconnect_mystocksd(con)         
#            
#            for isin in lista:
#                yahoocode=self.isin2yahoocode(isin)
#                if yahoocode==None:
#                    time.sleep(self.time_step_historical)
#                else:
#    #                print code,  listcodes
#                    if self.debugmode==True:
#                        for i in self.arr_historical(yahoocode):
#                            print (i)
#                    else:                
#    #                    print "Ha llegado"
#                        Quote(self.mem).insert_cdtohclv(self.arr_historical(yahoocode, isin),  self.name)                
#                    con=self.mem.connect_mystocksd()
#                    cur=con.cursor()
#                    status_update(cur, self.name, "Update step historicals", status='Waiting step',  statuschange=datetime.datetime.now())
#                    con.commit()
#                    cur.close()
#                    self.mem.disconnect_mystocksd(con)       
#                    time.sleep(self.time_step_historical)
#
#            con=self.mem.connect_mystocksd()
#            cur=con.cursor()
#            status_update(cur, self.name, "Update step historicals", status='Waiting after',  statuschange=datetime.datetime.now())
#            con.commit()
#            cur.close()
#            self.mem.disconnect_mystocksd(con)                          
#            time.sleep(self.time_after_historicals)

#    def update_step_dividends(self, sql):
##        con=self.mem.connect_mystocksd()
##        cur=con.cursor()
##        status_insert(cur, self.name, "Update step dividends")
##        con.commit()
##        cur.close()
##        self.mem.disconnect_mystocksd(con)   
#        return
#        
#    def update_dividends(self):   
#        con=self.mem.connect_mystocksd()
#        cur=con.cursor()
#        status_insert(cur, self.name, "Update dividends")
#        status_update(cur, self.name, "Update dividends", status='Waiting before',  statuschange=datetime.datetime.now())
#        con.commit()
#        cur.close()
#        self.mem.disconnect_mystocksd(con)    
#        time.sleep(self.time_before_dividends)        
#        while True:                   
#            con=self.mem.connect_mystocksd()
#            cur=con.cursor()
#            status_update(cur, self.name, "Update dividends", status='Working',  statuschange=datetime.datetime.now())
#            con.commit()
#            cur.close()
#            self.mem.disconnect_mystocksd(con)                     
#            Product(self.mem).update_dividends( self.arr_dividends(),  self.name)
#            con=self.mem.connect_mystocksd()
#            cur=con.cursor()
#            status_update(cur, self.name, "Update dividends", status='Waiting after',  statuschange=datetime.datetime.now())
#            con.commit()
#            cur.close()
#            self.mem.disconnect_mystocksd(con)                     
#            time.sleep(self.time_after_dividends)
#           
#           

    def filtrar_horario_bolsa(self, products):
        if (datetime.datetime.now()-self.mem.inittime).total_seconds()<120:#120: # Si acaba de arrancar
            return products
            
        if datetime.datetime.now().weekday()>=5:         
            return []
#        now=datetime.time(datetime.datetime.utcnow().hour, datetime.datetime.utcnow().minute) 
        resultado=[]
        margen=datetime.timedelta(hours=1 )
        for inv in products:
#            inv=self.mem.activas(i)
#            bolsa=self.mem.stockexchanges[str(self.mem.activas[str(i)].id_stockexchanges)]
            now=datetime.datetime.now(pytz.timezone(inv.stockexchange.zone))
            starts=now.replace(hour=inv.stockexchange.starts.hour, minute=inv.stockexchange.starts.minute, second=inv.stockexchange.starts.second)
            stops=now.replace(hour=inv.stockexchange.ends.hour, minute=inv.stockexchange.ends.minute)+margen
#            print (starts, now, stops)
            if starts<now and stops>now:
                print ("metido")
                resultado.append(inv)
        return resultado
                


    def agrupations(self, isin, agrbase=[]):
        """agrbase es la agrupación base que se importa desde statics, por ejemplo EURONEXT o BMF"""
        agr=[]
        agr=agr+agrbase
        if isin in self.mem.cac40:
            agr.append('CAC40')            
        if isin in self.mem.eurostoxx:
            agr.append('EUROSTOXX')
        if isin in self.mem.ibex:
            agr.append('IBEX35')
        if isin in self.mem.nyse:
            agr.append('NYSE')
        if isin in self.mem.dax:
            agr.append('DAX')
            
        if len(agr)==0:
            return '||'
        else:
            agr.sort()
            resultado='|'
            for i in agr:
                resultado=resultado + i + '|'
            return resultado
#
#    def set_cac40_isin(self):
#        """Función que devuelve un set"""      
#        while True:
#            web=self.download('http://www.euronext.com/trader/indicescomposition/composition-4411-EN-FR0003500008.html?selectedMep=1', 'SET_CAC40_ISIN',  False)
#            if web==None:
#                time.sleep(60)
#                continue
#                
#            resultado=set([])
#            for line in web.readlines():
##                try:
#                    if line.find(b'<td class="tableValueName">40&nbsp;Stocks</td>')!=-1:
#                        arr=line.split(b'="/trader/summarizedmarket/summarizedmarketRoot.jsp?isinCode=">')
#                        for i in range(1, len(arr)):
#                            isin=b2s(arr[i].split(b'&amp;lan=EN&amp;selectedMep=1">')[0])
#                            resultado.add(isin)
#
#            if len(resultado)==-1:
#                texto=QApplication.translate("Core",("No están todos los del cac40, reintentando")
#                log(self.name,"SET_CAC40_ISIN", texto)
#                time.sleep(60)
#            else:
#                break
#        return resultado
#                
#    def set_dax_isin(self):
#        while True:
#            resultado=set([])
#            web=self.download('http://deutsche-boerse.com/bf4dbag/EN/export/export.aspx?module=IndexConstituents&isin=DE0008469008&title=Constituent+Equities&perpage=50&navpath=http://deutsche-boerse.com/dbag/dispatch/en/isg/gdb_navigation/lc', 'SET_DAX_ISIN',  False)
#            if web==None:
#                time.sleep(60)
#                continue  
#    
#            line=web.readline().decode()
#            while line.find('</html>')==-1:
#                try:
#                    if line.find('<td class="column-name first" rowspan="2">')!=-1:
#                        isin=line.split('<br />')[1].split('</td>')[0]
#                        resultado.add(isin)
#                except:
#                    line=web.readline().decode()
#                    continue    
#                line=web.readline().decode()
#            if len(resultado)==-1:#<10:
#                log(self.name,"SET_DAX_ISIN", QApplication.translate("Core",("No están todos, reintentando"))
#                time.sleep(60)
#            else:
#                break
#        return resultado
#        
#    def set_ibex_isin(self):
#        while True:
#            resultado=set([])
#            web=self.download('http://www.bolsamadrid.es/esp/mercados/acciones/accind1_1.htm', 'SET_IBEX_ISIN',  False)
#            if web==None:
#                time.sleep(60)
#                continue         
#            for line in web.readlines():
#                try:
#                    if line.find('/comun/fichaemp/fichavalor.asp?isin=')!=-1:
#                        isin=line.split('?isin=')[1].split('"><IMG SRC="')[0]
#                        resultado.add(isin)
#                except:
#                    continue    
#            if len(resultado)<10:
#                log(self.name,"SET_IBEX", QApplication.translate("Core",("No están todos los del ibex, reintentando"))
#                time.sleep(60)
#            else:
#                break
#        return resultado
#        
#    def set_eurostoxx_isin(self):
#        while True:
#            resultado=set([])
#            web=self.download('http://www.boerse-frankfurt.de/EN/index.aspx?pageID=85&ISIN=EU0009658145', 'SET_EUROSTOXX_ISIN',  False)
#            if web==None:
#                time.sleep(60)
#                continue       
#            line=web.readline().decode()
#            while line.find('</html>')==-1:
#                try:
#                    if line.find('<td class="column-name"')!=-1:
#                        isin=line.split('<br />')[1].split('</td>')[0]
#        #                print isin
#                        resultado.add(isin)
#                except:
#                    line=web.readline().decode()
#                    continue    
#                line=web.readline().decode()
#            if len(resultado)==-1:#<10:
#                log(self.name,"SET_EUROSTOXX_ISIN",QApplication.translate("Core",("No están todos, reintentando"))
#                time.sleep(60)
#            else:
#                break
#        return resultado
#        
#    def set_nyse(self):
#        while True:
#            resultado=set([])
#            web=self.download('http://www.nyse.com/indexes/nyaindex.csv', 'SET_NYSE', False)
#            if web==None:
#                time.sleep(60)
#                continue
#    
#            for line in web.readlines():
#                arr=line.replace('"', '').split(',')
#                if len (arr[1])>0:
#                    resultado.add(arr[1])
#            if len(resultado)<10:
#                log(self.name,"SET_NYSE",QApplication.translate("Core",("No están todos, reintentando"))
#                time.sleep(60)
#            else:
#                break
#                
#        return resultado

#    def utctime(self, time, zone):
#        salida=utc2(datetime.date.today(), time, zone)        
#        if salida[0]!=datetime.date.today():
#            print ("Ha habido un cambio de día para calcular el datetime",  time,  zone)
#        return salida[1]
        
    def ticker2investment(self, ticker, products):
        for inv in products:
            if inv.ticker==ticker:
                return inv
        return None
#
#    def yahoo_historical(self, code,  dbcode=''):
#        """If othercode se pone como code othercode, util cuando se busca por code de yahoo pero en la base de datos en deutchbore#de00000000"""
#        def fecha_ultimo_registro(code):
#            mem=MemMyStock()
#            con=mem.connect_mystocksd()
#            cur = con.cursor()     
#            resultado=None
#            cur.execute("select max(date) as fecha from quotes where code=%s and last='close'", (code, ))
#            for i in cur:
#                resultado=i['fecha']
#            con.commit()    
#            cur.close()                
#            self.mem.disconnect_mystocksd(con)
#            if resultado==None:
#                resultado=datetime.date(config.fillfromyear, 1, 1)
#            return resultado    
#        #########################
#        resultado=[]       
#        inicio=fecha_ultimo_registro(code)#Se deja uno más para que no falle +datetime.timedelta(days=14)
#    
#        web=self.download('http://ichart.finance.yahoo.com/table.csv?s='+code+'&a='+str(inicio.month-1)+'&b='+str(inicio.day)+'&c='+str(inicio.year)+'&d='+str(datetime.date.today().month-1)+'&e='+str(datetime.date.today().day)+'&f='+str(datetime.date.today().year)+'&g=d&ignore=.csv', 'YAHOO_HISTORICAL')
#        if web==None:
#            return resultado   
#    
#        web.readline()
#        error=0
#        for i in web.readlines(): 
#    #                print i
#            try:  
#                i=b2s(i)
#                d= {}     
#                datos=i.split(",")
#                fecha=datos[0].split("-")
#                if dbcode==None or dbcode=='':
#                    d['code']=code
#                else:
#                    d['code']=dbcode
#                    
##                print d['code']
#                d['date']=datetime.date(int(fecha[0]), int(fecha[1]),  int(fecha[2]))
#                d['open']=float(datos[1])
#                d['high']=float(datos[2])
#                d['low']=float(datos[3])
#                d['close']=float(datos[4])
#                d['volumen']=float(datos[5])
#                d['zone']='UTC'
#            except:
#                error=error+1
#                continue
#            if d['date']>inicio: #Para no insertar el que se puso para que no fallara por vacio
#                resultado.append(d)
#        if error>0:
#            log("YAHOO_HISTORICAL", "",  QApplication.translate("Core",("Error al parsear %(code)s desde %(name)s") % {"code":code.replace("\n", ""),  "name":self.name})       
#        return resultado
#        
#    def yahoo_quotes(self,  quotes,  precode=''):
#        "precode añade NYSE# a la base de datos"
#        resultado=[]
#    
#        web=self.download('http://download.finance.yahoo.com/d/quotes.csv?s=' + strnames(quotes) + '&f=sl1d1t1&e=.csv', 'YAHOO_QUOTES')
#        if web==None:
#            return (resultado, 0)   
#    
#    
#        error=0
#        for i in web.readlines():
#            try:
#                dic= {'code': None, 'date': None, 'time':None,'quote': None }
#                i=b2s(i)
#                datos=i[:-2].split(",")#Se quita dos creo que por caracter final linea windeos.
#
#                dic['code']=precode+datos[0][1:-1]
#                dic['quote']=datos[1]
#                d=int(datos[2][1:-1].split("/")[1])
#                M=int(datos[2][1:-1].split("/")[0])
#                Y=int(datos[2][1:-1].split("/")[2])
#                H=int(datos[3][1:-1].split(":")[0])
#                m=int(datos[3][1:-1].split(":")[1][:-2])
#                pm=datos[3][1:-1].split(":")[1][2:]
#                
#                #Conversion
#                H=ampm_to_24(H, pm)
#                dic['date']=datetime.date(Y, M, d)
#                dic['time']=datetime.time(H, m)
#                dic['zone']='US/Eastern'
#                (dic['date'], dic['time'], dic['zone'])=utc2(dic['date'], dic['time'], dic['zone'])   
##                print (dic)
#                resultado.append(dic)
#            except:
#                error=error +1
#                continue
##    if error>0:
##        log("YAHOO_QUOTES", QApplication.translate("Core",("Han habido %(errores)d errores en el parseo de s_yahoo() desde la url %(url)s" %{ "errores":error, "url":comand}))
#        return (resultado,  error)

class Product:
    def __init__(self, mem):
        self.mem=mem
        self.name=None
        self.isin=None
        self.currency=None #Apunta a un objeto currency
        self.type=None
        self.agrupations=None #Es un objeto SetAgrupations
        self.active=None
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
        self.deletable=None
        self.system=None
        
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
        self.currency=self.mem.currencies.find(row['currency'])
        self.type=self.mem.types.find(row['type'])
        self.agrupations=self.mem.agrupations.clone_from_dbstring(row['agrupations'])
        self.active=row['active']
        self.id=row['id']
        self.web=row['web']
        self.address=row['address']
        self.phone=row['phone']
        self.mail=row['mail']
        self.tpc=row['tpc']
        self.mode=self.mem.investmentsmodes.find(row['pci'])
        self.apalancado=self.mem.apalancamientos.find(row['apalancado'])
        self.stockexchange=self.mem.stockexchanges.find(row['id_bolsas'])
        self.ticker=row['ticker']
        self.priority=SetPriorities(self.mem).init__create_from_db(row['priority'])
        self.priorityhistorical=SetPrioritiesHistorical(self.mem).init__create_from_db(row['priorityhistorical'])
        self.comentario=row['comentario']
        self.obsolete=row['obsolete']
        self.deletable=row['deletable']
        self.system=row['system']
        
        self.result=QuotesResult(self.mem,self)
        return self
        
                
    def init__create(self, name,  isin, currency, type, agrupations, active, web, address, phone, mail, tpc, mode, apalancado, bolsa, ticker, priority, priorityhistorical, comentario, obsolete, deletable, system, id=None):
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
        self.deletable=deletable
        self.system=system
        
        self.result=QuotesResult(self.mem,self)
        return self        

    def init__db(self, id):
        """Se pasa id porque se debe usar cuando todavía no se ha generado."""
        curms=self.mem.conms.cursor()
        curms.execute("select * from products where id=%s", (id, ))
        row=curms.fetchone()
        curms.close()
        return self.init__db_row(row)
        
#    def load_estimacion(self, year=None):
#        """Si year es none carga todas las estimations_dps de la inversionmq"""
#        curms=self.mem.conms.cursor()
#        if year==None:
#            year=datetime.date.today().year
#        curms.execute("select * from estimations_dps where year=%s and id=%s", (year, self.id))
#        if curms.rowcount==0:        
#            e=EstimationEPS(self.mem).init__create(self, year, datetime.date.today(),  "Vacio por código", False, 0)
##            e=EstimationEPS(self.mem).init__create(year, 0, datetime.date(2012, 7, 3), "Vacio por código", False, 0, self)
#        else:
#            e=EstimationEPS(self.mem). init__from_db( product,  currentyear):
#        self.estimations_dps[str(e.year)]=e
#        curms.close()
        
    def save(self):
        """Esta función inserta una inversión manual"""
        """Los arrays deberan pasarse como parametros ARRAY[1,2,,3,] o None"""
        
        cur=self.mem.conms.cursor()
        if self.id==None:
            cur.execute(" select min(id)-1 from products;")
            id=cur.fetchone()[0]
            cur.execute("insert into products (id, name,  isin,  currency,  type,  agrupations,  active,  web, address,  phone, mail, tpc, pci,  apalancado, id_bolsas, ticker, priority, priorityhistorical , comentario,  obsolete, system) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",  (id, self.name,  self.isin,  self.currency.id,  self.type.id,  self.agrupations.dbstring(),  self.active,  self.web, self.address,  self.phone, self.mail, self.tpc, self.mode.id,  self.apalancado.id, self.stockexchange.id, self.ticker, self.priority.array_of_id(), self.priorityhistorical.array_of_id() , self.comentario, self.obsolete, False))
            self.id=id
        else:
            cur.execute("update products set name=%s, isin=%s,currency=%s,type=%s, agrupations=%s, active=%s, web=%s, address=%s, phone=%s, mail=%s, tpc=%s, pci=%s, apalancado=%s, id_bolsas=%s, ticker=%s, priority=%s, priorityhistorical=%s, comentario=%s, obsolete=%s where id=%s", ( self.name,  self.isin,  self.currency.id,  self.type.id,  self.agrupations.dbstring(),  self.active,  self.web, self.address,  self.phone, self.mail, self.tpc, self.mode.id,  self.apalancado.id, self.stockexchange.id, self.ticker, self.priority.array_of_id(), self.priorityhistorical.array_of_id() , self.comentario, self.obsolete,  self.id))
        cur.close()
    
    def changeDeletable(self, ids,  deletable):
        """Modifica a deletable"""
        curms=self.mem.conms.cursor()
        sql="update products set deletable={0} where id in ({1})".format( deletable,  str(ids)[1:-1])
        curms.execute(sql)
        curms.close()
        
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
        year=int(self.mem.config.get_value("settings_mystocks", "fillfromyear"))
        resultado=datetime.date(year, 1, 1)
        cur=self.mem.conms.cursor()
        cur.execute("select max(datetime)::date as date from quotes where date_part('microsecond',datetime)=4 and id=%s order by date", (self.id, ))
        if cur.rowcount==1:
            dat=cur.fetchone()[0]
            if dat!=None:
                resultado=dat
        cur.close()
        return resultado


        
class SetQuotes:
    """Clase que agrupa quotes un una lista arr. Util para operar con ellas como por ejemplo insertar"""
    def __init__(self, mem):
        self.mem=mem
        self.arr=[]
    
    def save(self,  source):
        """Recibe con code,  date,  time, value, zone
            Para poner el dato en close, el valor de time debe ser None
            Devuelve una tripleta (insertado,buscados,modificados)
        """
        (insertados, buscados, modificados)=(0, 0, 0)
        if len(self.arr)==0:
            return  (insertados, buscados, modificados)
            
            
        for p in self.arr:
            ibm=p.save()
            if ibm==0:
                buscados=buscados+1
            elif ibm==1:
                insertados=insertados+1
            elif ibm==2:
                modificados=modificados+1

        if insertados>0 or modificados>0:
             return (insertados, buscados, modificados)
#            log("QUOTES" , source,  QApplication.translate("Core","Se han buscado %(b)d, modificado %(m)d e insertado %(i)d registros de %(c)s") %{"b":buscados, "m": modificados,   "i":insertados,  "c":source})
        
    def append(self, quote):
        self.arr.append(quote)
                
                
class SetQuotesAll:
    """Class that groups all quotes of the database. It's an array of SetQuotesIntraday"""
    def __init__(self, mem):
        self.mem=mem
        self.product=None
                
    def load_from_db(self,  product):
        """Función que mete en setquotesintradia ordenado de objetos Quote, no es el ultimo día es un día"""
        self.arr=[]
        self.product=product
        curms=self.mem.conms.cursor()
        curms.execute("select * from quotes where id=%s order by datetime", (self.product.id,  ))
        
        intradayarr=[]
        dt_end=None
        for row in curms:
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
        curms.close()

        
    def find(self, dattime):
        """Recorro de mayor a menor"""
        for i,  sqi in enumerate(reversed(self.arr)):
            if sqi.date<=dattime.date():
                return sql.find(dattime)
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
                pd.setLabelText(QApplication.translate("Core","Purged {0} quotes from {1}".format(counter, self.product.name)))
                pd.update()
                QApplication.processEvents()
                if pd.wasCanceled():
                    return None
                QApplication.processEvents()
            if sqi.date<datetime.date.today()-datetime.timedelta(days=30):
                counter=counter+sqi.purge()
        return counter

#        
#    def get_all_obsolet_incremental(self, curms):
#        """Función que devuelve un array ordenado de objetos Quote
#        actualiza o carga todo según haya registros
#        Actualiza get_basic_in_all
#        """
#        inicio=datetime.datetime.now()
#        if len(self.all.arr)==0:
#            curms.execute("select * from quotes where id=%s order by datetime;", (self.product.id, ))
#        else:
#            curms.execute("select * from quotes where id=%s and datetime>%s order by datetime;", (self.product.id, self.all[len(self.all)-1].datetime))
#        for row in curms:
#            self.all.arr.append(Quote(self.mem).init__db_row(row,  self.product))
#        print ("Descarga de {0} datos: {1}".format(curms.rowcount,   datetime.datetime.now()-inicio))
#        self.get_basic_in_all()
        
            
#    def get_basic_OBSOLET(self):
#        """Función que calcula last, penultimate y lastdate """
#        if len(self.all.arr)==0:
#            print ("No hay quotes para la inversión",  self.product)
#            return
#        self.last=self.all.arr[len(self.all.arr)-1]
#        #penultimate es el ultimo del penultimo dia localizado
#        dtpenultimate=day_end(self.last.datetime-datetime.timedelta(days=1), self.product.stockexchange.zone)
#        self.penultimate=self.find_quote_in_all(dtpenultimate)
#        dtendlastyear=dt(datetime.date(self.last.datetime.year-1, 12, 31),  datetime.time(23, 59, 59), self.product.stockexchange.zone)
#        self.endlastyear=self.find_quote_in_all(dtendlastyear)

        
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


     
class SetQuotesIntraday:
    """Clase que agrupa quotes un una lista arr de una misma inversión y de un mismo día. """
    def __init__(self, mem):
        self.mem=mem
        self.arr=[]
        self.product=None
        self.date=None
        
    def load_from_db(self,  date, product):
        """Función que mete en setquotesintradia ordenado de objetos Quote, no es el ultimo día es un día"""
        self.arr=[]
        self.product=product
        self.date=date
        curms=self.mem.conms.cursor()
        iniciodia=day_start_from_date(date, self.product.stockexchange.zone)
        siguientedia=iniciodia+datetime.timedelta(days=1)
        curms.execute("select * from quotes where id=%s and datetime>=%s and datetime<%s order by datetime", (self.product.id,  iniciodia, siguientedia))
        for row in curms:
            self.arr.append(Quote(self.mem).init__db_row(row,  self.product))
        curms.close()
        
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
        high=Quote(self.mem).init__create(self.product, day_start_from_date(self.date, self.product.stockexchange.zone), Decimal('0'))
        for q in self.arr:
            if q.quote>high.quote:
                high=q
        return high
        
    def low(self):
        """Devuelve el quote cuyo quote es menor"""
        if len(self.arr)==0:
            return None
        low=Quote(self.mem).init__create(self.product, day_start_from_date(self.date, self.product.stockexchange.zone), Decimal('1000000'))
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
        """Función que crea un Quote nuevo, con la finalidad de insertarlo"""
        self.product=product
        self.datetime=datetime
        self.quote=quote
        return self
        
    def exists(self, curms):
        """Función que comprueba si existe en la base de datos y devuelve el valor de quote en caso positivo en una dupla"""     
        curms.execute("select quote from quotes where id=%s and  datetime=%s;", (self.product.id, self.datetime))
        if curms.rowcount==0: #No Existe el registro
            return (False,  None)
        return (True,  curms.fetchone()['quote'])
        
    def save(self):
        """Función que graba el quotes si coincide todo lo ignora. Si no coincide lo inserta o actualiza.
        No hace commit a la conexión
        Devuelve un número 1 si insert 2, update, 0  exisitia
        """
        curms=self.mem.conms.cursor()
        exists=self.exists(curms)
        if exists[0]==False:
            curms.execute('insert into quotes (id, datetime, quote) values (%s,%s,%s)', ( self.product.id, self.datetime, self.quote))
            curms.close()
            return 1
        else:
            if exists[1]!=self.quote:
                curms.execute("update quotes set quote=%swhere id=%s and datetime=%s", (self.quote, self.product.id, self.datetime))
                curms.close()
                return 2
            else:
                curms.close()
                return 3
                
    def delete(self):
        curms=self.mem.conms.cursor()
        curms.execute("delete from quotes where id=%s and datetime=%s", (self.product.id, self.datetime))
        curms.close()

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
        curms=self.mem.conms.cursor()
        sql="select * from quote(%s, '%s'::timestamptz)" %(product.id,  dt)
        curms.execute(sql)
        row=curms.fetchone()
        curms.close()
        return self.init__db_row(row, dt)
                
    def init__from_query_penultima(self,product,  lastdate=None):
        curms=self.mem.conms.cursor()
        if lastdate==None:
            curms.execute("select * from penultimate(%s)", (product.id, ))
        else:
            curms.execute("select * from penultimate(%s,%s)", (product.id, lastdate ))
        row=curms.fetchone()
        curms.close()
        return self.init__db_row(row, None)        
        
    def init__from_query_triplete(self, product): 
        """Función que busca el last, penultimate y endlastyear de golpe
       Devuelve un array de Quote en el que arr[0] es endlastyear, [1] es penultimate y [2] es last
      Si no devuelve tres Quotes devuelve None y deberaá calcularse de otra forma"""
        curms=self.mem.conms.cursor()
        endlastyear=dt(datetime.date(datetime.date.today().year -1, 12, 31), datetime.time(23, 59, 59), self.mem.localzone)
        curms.execute("select * from quote (%s, now()) union all select * from penultimate(%s) union all select * from quote(%s,%s) order by datetime", (product.id, product.id, product.id,  endlastyear))
        if curms.rowcount!=3:
            curms.close()
            return None
        resultado=[]
        for row in  curms:
            if row['datetime']==None: #Pierde el orden y no se sabe cual es cual
                curms.close()
                return None
            resultado.append(Quote(self.mem).init__db_row(row, product))
        curms.close()
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
class SetOHCLWeekly:
    def __init__(self, mem, product):
        self.mem=mem
        self.product=product
        self.arr=[]
    def load_from_db(self, sql):
        """El sql debe estar ordenado por fecha"""
        del self.arr
        self.arr=[]
        cur=self.mem.conms.cursor()
        cur.execute(sql)#select * from ohclyearly where id=79329 order by year
        for row in cur:
            self.arr.append(OHCLWeekly(self.mem).init__from_dbrow(row, self.product))
        cur.close()  
        
class SetOHCLYearly:
    def __init__(self, mem, product):
        self.mem=mem
        self.product=product
        self.arr=[]
    def load_from_db(self, sql):
        """El sql debe estar ordenado por fecha"""
        del self.arr
        self.arr=[]
        cur=self.mem.conms.cursor()
        cur.execute(sql)#select * from ohclyearly where id=79329 order by year
        for row in cur:
            self.arr.append(OHCLYearly(self.mem).init__from_dbrow(row, self.product))
        cur.close()
        
class SetOHCLMonthly:
    def __init__(self, mem, product):
        self.mem=mem
        self.product=product
        self.arr=[]
    def load_from_db(self, sql):
        """El sql debe estar ordenado por year, month"""
        del self.arr
        self.arr=[]
        cur=self.mem.conms.cursor()
        cur.execute(sql)#select * from ohclyearly where id=79329 order by year,mont
        for row in cur:
            self.arr.append(OHCLMonthly(self.mem).init__from_dbrow(row, self.product))
        cur.close()

class SetLanguages:
    def __init__(self, mem):
        self.mem=mem
        self.arr=[]
        
    def find(self, id):
        for a in self.arr:
            if a.id==id:
                return a
    
    def load_all(self):
        self.arr.append(Language(self.mem, "en","English" ))
        self.arr.append(Language(self.mem, "es","Español" ))
        self.arr.append(Language(self.mem, "fr","Français" ))
        self.arr.append(Language(self.mem, "ro","Rom\xe2n" ))
        self.arr.append(Language(self.mem, "ru",'\u0420\u0443\u0441\u0441\u043a\u0438\u0439' ))

                
    def sort(self):
        self.arr=sorted(self.arr, key=lambda c: c.name,  reverse=False)      
        
    def qcombobox(self, combo, selected=None):
        """Selected is the id"""

        self.sort()
        for l in self.arr:
            combo.addItem(self.mem.countries.find(l.id).qicon(), l.name, l.id)
        if selected!=None:
                combo.setCurrentIndex(combo.findData(selected))

    def cambiar(self, id):  
        """language es un string"""
        self.mem.qtranslator.load("/usr/lib/xulpymoney/xulpymoney_" + id + ".qm")
        qApp.installTranslator(self.mem.qtranslator);
        
class SetOHCLDaily:
    def __init__(self, mem, product):
        self.mem=mem
        self.product=product
        self.arr=[]
        
           
    def load_from_db(self, sql):
        """El sql debe estar ordenado por date"""
        
        del self.arr
        self.arr=[]
        cur=self.mem.conms.cursor()
        cur.execute(sql)#select * from ohclyearly where id=79329 order by date
        for row in cur:
            self.arr.append(OHCLDaily(self.mem).init__from_dbrow(row, self.product))
        cur.close()
#                
#    def __find_ohclDiary_since_date(self, date):
#        resultado=[]
#        date=datetime.datetime(date.year, date.month, date.day)
#        for d in self.ohclDaily:
#            if d[0]>=date:
#                resultado.append(d)
#        return resultado
        
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
        ohcl=self.find(ohcl.date-datetime.timedelta(days=1))#penultimate
        if ohcl!=None:
            penultimate=Quote(self.mem).init__create(self.product, dt(ohcl.date, self.product.stockexchange.closes,  self.product.stockexchange.zone), ohcl.close)
        ohcl=self.find(datetime.date(datetime.date.today().year-1, 12, 31))#endlastyear
        if ohcl!=None:
            endlastyear=Quote(self.mem).init__create(self.product, dt(ohcl.date, self.product.stockexchange.closes,  self.product.stockexchange.zone), ohcl.close)        
        return SetQuotesBasic(self.mem, self.product).init__create(last, penultimate, endlastyear)
        
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
        self.all=SetQuotesAll(self.mem)
        self.basic=SetQuotesBasic(self.mem, self.product)
        self.ohclDaily=SetOHCLDaily(self.mem, self.product)
        self.ohclMonthly=SetOHCLMonthly(self.mem, self.product)
        self.ohclYearly=SetOHCLYearly(self.mem, self.product)
        self.ohclWeekly=SetOHCLWeekly(self.mem, self.product)
        
    def get_basic_ohcls(self):
        """Tambien sirve para recargar"""
        inicio=datetime.datetime.now()
        self.ohclDaily.load_from_db("select * from ohlcdaily where id={0} order by date".format(self.product.id))#necesario para usar luego ohcl_otros
        self.ohclMonthly.load_from_db("select * from ohlcMonthly where id={0} order by year,month".format(self.product.id))
        self.ohclWeekly.load_from_db("select * from ohlcWeekly where id={0} order by year,week".format(self.product.id))
        self.ohclYearly.load_from_db("select * from ohlcYearly where id={0} order by year".format(self.product.id))
        self.basic=self.ohclDaily.setquotesbasic()
        print ("Datos db cargados:",  datetime.datetime.now()-inicio)


class Apalancamiento:
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
        
        
class Split:
    """Class to make calculations with splits or contrasplits"""
    def __init__(self, mem, sharesinitial,  sharesfinal):
        self.mem=mem
        self.initial=sharesinitial
        self.final=sharesfinal
    
    def convertShares(self, actions):
        """Function to calculate new shares just pass the number you need to convert"""
        return actions*self.final/self.initial
        
    def convertPrices(self, price):
        return price*self.initial/self.final
        
    def convertDPA(self, dpa):
        """Converts the dividend por share"""
        return self.convertPrices(dpa)
    
    def updateQuotes(self, arr):
        """Transforms de price of the quotes of the array"""
        for q in arr:
            q.quote=self.convertPrices(q.quote)
            q.save()
        
        
    def updateOperInvestments(self, arr):
        """Transforms de number of shares and its price of the array of InvestmentOperation"""
        for oi in arr:
            oi.acciones=self.convertShares(oi.acciones)
            oi.valor_accion=self.convertPrices(oi.valor_accion)
            oi.save()
        
    def updateDividends(self, arr):
        """Transforms de dpa of an array of dividends"""
        for d in arr:
            d.estimation=self.convertDPA(d.estimation)
            d.save()
        
    def type(self):
        """Función que devuelve si es un Split o contrasplit"""
        if self.initial>self.final:
            return "Contrasplit"
        else:
            return "Split"
        
        
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
                products=self.mem.data.investments_active
            else:
                products=self.mem.data.investments_all()
                
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
        
class SetTypes:
    def __init__(self, mem):
        self.mem=mem
        self.dic_arr={}
        
            
    def load_all(self):
        self.dic_arr["1"]=Type().init__create(1,QApplication.translate("Core","Shares"))
        self.dic_arr["2"]=Type().init__create(2,QApplication.translate("Core","Funds"))
        self.dic_arr["3"]=Type().init__create(3,QApplication.translate("Core","Indexes"))
        self.dic_arr["4"]=Type().init__create(4,QApplication.translate("Core","ETF"))
        self.dic_arr["5"]=Type().init__create(5,QApplication.translate("Core","Warrants"))
        self.dic_arr["6"]=Type().init__create(6,QApplication.translate("Core","Currencies"))
        self.dic_arr["7"]=Type().init__create(7,QApplication.translate("Core","Public Bond"))
        self.dic_arr["8"]=Type().init__create(8,QApplication.translate("Core","Planes de pensiones"))
        self.dic_arr["9"]=Type().init__create(9,QApplication.translate("Core","Private Bond"))
        self.dic_arr["10"]=Type().init__create(10,QApplication.translate("Core","Depósitos"))
        self.dic_arr["11"]=Type().init__create(11,QApplication.translate("Core","Accounts"))

    def qcombobox(self, combo):
        """Carga entidades bancarias en combo"""
        for a in self.list():
            combo.addItem(a.name, a.id)        
            
    def list(self):
        resultado=dic2list(self.dic_arr)
        resultado=sorted(resultado, key=lambda c: c.name  ,  reverse=False)    
        return resultado

    def find(self, id):
        return self.dic_arr[str(id)]        
        
    def products(self):
        return {k:v for k,v in self.dic_arr.items() if k in ("1", "2", "4", "5", "7","8")}


class ConfigFile:
    """Clase que maneja todo lo necesario para un configparser.ConfigParser
    En la aplicación hay dos config y config_ui"""
    def __init__(self, file, defaults):
        self.file=file
        self.config=configparser.ConfigParser()
        self.defaults=defaults
        self.load()
            
    def set_default_value(self, section, name):
        """Devuelve el default value, y lo establece"""
        try:
            if name.find("columns_width")!=-1:
                print ("Reseting",  section,  name)
                return []
            resultado=self.defaults["{0}#{1}".format(section,name)]
            print ("Using default value",  section,  name,  resultado)
            self.set_value(section, name, resultado)
            self.save()
            return resultado
        except:
            print(section, name,  "Default not found en config")
            
        
    def print_all(self):
        """Prints all keys in config"""
        for key in self.config:
            for item in self.config[key]:
                print (key,  item)    

    def load( self):
        try:
            self.config.read(self.file)    
        except:#Valores por defecto
            print ("Error reading config")
            
            
    
    def save(self):
        f=open(self.file, "w")
        self.config.write(f)
        f.close()
        
        
    def get_list(self,  section,  name):
        """Carga una section name parseada con strings y separadas por | y devuelve un arr"""
        try:
            cadena=self.config.get(section, name )
            if cadena=="":
                return []
            return cadena.split("|")
        except:
            return self.set_default_value(section, name)
    
    def set_list(self, section,  name,  list):
        """Establece, no ggraba, una cadena en formato str|str para luego ser parseado en lista"""
        if self.config.has_section(section)==False:
            self.config.add_section(section)
        cadena=""
        for item in list:
            cadena=cadena+str(item)+'|'
        self.config.set(section,  name,  cadena[:-1])
            
    def set_value(self, section, name, value):
        if self.config.has_section(section)==False:
            self.config.add_section(section)
        self.config.set(section,  name,  str(value))
        
    def get_value(self, section, name):
        try:
            resultado=self.config.get(section,  name)
            if resultado==None:
                print ("Resultado None: {0} {1} get and set default value".format(section, name))
                return self.set_default_value(section, name)
            return resultado
        except:
            print ("Except: {0} {1} get and set default value".format(section, name))
            return self.set_default_value(section, name)
            
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
        for inv in self.mem.data.inversiones_all().arr:
            print (inv)
            inv.actualizar_cuentasoperaciones_asociadas()
        self.mem.con.commit()        
        
        
    def show_investments_status(self, date):
        """Shows investments status in a date"""
        datet=dt(date, datetime.time(22, 00), self.mem.localzone)
        sumbalance=0
        print ("{0:<40s} {1:>15s} {2:>15s} {3:>15s}".format("Investments at {0}".format(date), "Shares", "Price", "Balance"))
        for inv in self.mem.data.inversiones_all().arr:
            balance=inv.balance(date)
            sumbalance=sumbalance+balance
            acciones=inv.acciones(date)
            price=Quote(self.mem).init__from_query(inv.product, datet)
            if acciones!=0:
                print ("{0:<40s} {1:>15f} {2:>15s} {3:>15s}".format(inv.name, acciones, self.mem.localcurrency.string(price.quote),  self.mem.localcurrency.string(balance)))
        print ("{0:>40s} {1:>15s} {2:>15s} {3:>15s}".format("Total balance at {0}".format(date), "","", self.mem.localcurrency.string(sumbalance)))

class MemMyStock:
    def __init__(self):
        self.password=""
        self.password2=""
        
        self.consqlite=None#Update internetquery fro Process
        
        
        self.cac40=set([])
        self.dax=set([])
        self.eurostoxx=set([])
        self.ibex=set([])
        self.nyse=set([])
        
        self.debugmode=False # from argv
        self.adminmode=False # from argv
        
        self.qtranslator=None#Residir´a el qtranslator

        self.config=ConfigFile(os.environ['HOME']+ "/.xulpymoney/xulpymoney.cfg", self.default_values())
        self.config_ui=ConfigFile(os.environ['HOME']+ "/.xulpymoney/xulpymoney_ui.cfg", self.default_ui_values())
        
        
        self.inittime=datetime.datetime.now()#Tiempo arranca el config
        self.dbinitdate=None#Fecha de inicio bd.
        
        self.dic_activas={}#Diccionario cuyo indice es el id de la inversión id['1'] corresponde a la IvestmenActive(1) #se usa en mystocksd
        
        self.conms=None#Conexión a mystocks
        
        #Needed for translations and are data
        self.countries=SetCountries(self)
        self.countries.load_all()
        self.languages=SetLanguages(self)
        self.languages.load_all()
        
        
        self.stockexchanges=SetStockExchanges(self)
        self.currencies=SetCurrencies(self)
        self.types=SetTypes(self)
        self.agrupations=SetAgrupations(self)
        self.apalancamientos=SetLeverages(self)
        self.priorities=SetPriorities(self)
        self.prioritieshistorical=SetPrioritiesHistorical(self)
        self.zones=SetZones(self)
        self.investmentsmodes=SetProductsModes(self)
        
    def default_values(self):
        d={}
        d['frmAccess#db'] = 'xulpymoney'
        d['frmAccess#port']='5432'
        d['frmAccess#user']= 'postgres'
        d['frmAccess#server']='127.0.0.1'
        d['frmAccessMS#db'] = 'mystocks'
        d['frmAccessMS#port']='5432'
        d['frmAccessMS#user']= 'postgres'
        d['frmAccessMS#server']='127.0.0.1'
        d['settings#dividendwithholding']='0.21'
        d['settings#taxcapitalappreciation']='0.21'
        d['settings#localcurrency']='EUR'
        d['settings#localzone']='Europe/Madrid'
        d['settings#benchmark']='79329'
        d['settings#gainsyear']='True'
        d['settings#language']='en'
        d['wdgProducts#favoritos']=""
        d['settings_mystocks#fillfromyear']='2005'
        d['wdgIndexRange#spin']='2'
        d['wdgIndexRange#txtInvertir']='4000'
        d['wdgIndexRange#txtMinimo']='1000'

        return d
            
            
    def default_ui_values(self):
        d={}
        d['canvasIntraday#sma50']='True'
        d['canvasIntraday#type']='0'
        d['canvasIntraday#sma200']='True'
        d['canvasHistorical#sma50']='True'
        d['canvasHistorical#type']='1'
        d['canvasHistorical#sma200']='True'
        d['canvasHistorical#interval']='1'
        return d
        

    def __del__(self):
        if self.conms:#Cierre por reject en frmAccess
            self.disconnect_mystocks(self.conms)
    
    def setQTranslator(self, qtranslator):
        self.qtranslator=qtranslator

                
    def actualizar_memoria(self):
        ###Esto debe ejecutarse una vez establecida la conexión
        print ("Cargando MemMyStock")
        self.currencies.load_all()
        self.investmentsmodes.load_all()
        self.zones.load_all()
        
        self.localzone=self.zones.find(self.config.get_value("settings", "localzone"))
        self.dividendwithholding=Decimal(self.config.get_value("settings", "dividendwithholding"))
        self.taxcapitalappreciation=Decimal(self.config.get_value("settings", "taxcapitalappreciation"))
        
        self.priorities.load_all()
        self.prioritieshistorical.load_all()
        self.types.load_all()
        self.stockexchanges.load_all_from_db()
        self.agrupations.load_all()
        self.apalancamientos.load_all()



    def connect_mystocksd(self, pw):        
        """usa también la variables self.conms"""              
        strmq="dbname='%s' port='%s' user='%s' host='%s' password='%s'" % (self.config.get_value("frmAccessMS", "db"),  self.config.get_value("frmAccessMS", "port"), self.config.get_value("frmAccessMS", "user"), self.config.get_value("frmAccessMS", "server"),  pw)
        while True:
            try:
                self.conms=psycopg2.extras.DictConnection(strmq)
                return self.conms
            except psycopg2.Error:
                print (QApplication.translate("Core","Error conecting to MyStocksd, waiting 10 seconds"))
                time.sleep(10)

    def disconnect_mystocksd(self):
        self.conms.close()

    def connect_mystocks(self):             
        strmq="dbname='%s' port='%s' user='%s' host='%s' password='%s'" % (self.config.get_value("frmAccessMS", "db"),  self.config.get_value("frmAccessMS", "port"), self.config.get_value("frmAccessMS", "user"), self.config.get_value("frmAccessMS", "server"),  self.password)
        try:
            mq=psycopg2.extras.DictConnection(strmq)
            return mq
        except psycopg2.Error:
            m=QMessageBox()
            m.setText(QApplication.translate("Core","Error conecting to MyStocks"))
            m.setIcon(QMessageBox.Information)
            m.exec_()
            sys.exit()

    def disconnect_mystocks(self,  mq):
        mq.close()
    
#    def carga_ia(self, cur,  where=""):
#        """La variable where sera del tipo:
#        where="where priority=5"""
#        cur.execute("select * from products {0}".format(where))
#        for row in cur:
#            self.dic_activas[str(row['id'])]=Product(self.mem).init__db_row(self, row)
#            
#
#    def activas(self, id=None):
#        if id==None:
#            return dic2list(self.dic_activas)
#        else:
#            return self.dic_activas[str(id)]
#                        

            
class MemXulpymoney(MemMyStock):
    def __init__(self):
        MemMyStock.__init__(self)
        self.con=None#Conexión a xulpymoney
        self.data=DBData(self)
        self.closing=False#Used to close threads
        
    def __del__(self):
        self.closing=True
        self.data.__del__()
        
        if self.conms:#Cierre por reject en frmAccess
            self.disconnect_mystocks(self.conms)
        if self.con:
            self.disconnect_xulpymoney(self.con)
        

    def actualizar_memoria(self):
        """Solo se cargan datos  de mystocks y operinversiones en las activas
        Pero se general el InvestmentMQ de las inactivas
        Se vinculan todas"""
        super(MemXulpymoney, self).actualizar_memoria()
        inicio=datetime.datetime.now()
        print ("Loading static data")
        self.tiposoperaciones=SetOperationTypes(self)
        self.tiposoperaciones.load()
        self.conceptos=SetConcepts(self)
        self.conceptos.load_from_db()
        self.localcurrency=self.currencies.find(self.config.get_value("settings", "localcurrency")) #Currency definido en config
        self.data.load_actives()
        print(datetime.datetime.now()-inicio)
        

        
    def connect_xulpymoney(self):        
        strcon="dbname='%s' port='%s' user='%s' host='%s' password='%s'" % (self.config.get_value("frmAccess", "db"),  self.config.get_value("frmAccess", "port"), self.config.get_value("frmAccess", "user"), self.config.get_value("frmAccess", "server"),  self.password)
        try:
            con=psycopg2.extras.DictConnection(strcon)
        except psycopg2.Error:
            m=QMessageBox()
            m.setText(QApplication.translate("Core","Error conecting to Xulpymoney"))
            m.setIcon(QMessageBox.Information)
            m.exec_()        
            sys.exit()
        return con
        
    def disconnect_xulpymoney(self, con):
        con.close()
 

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
        elif self.id=="es":
            return QPixmap(":/countries/spain.gif")
        elif self.id=="eu":
            return QPixmap(":/countries/eu.gif")
        elif self.id=="de":
            return QPixmap(":/countries/germany.gif")
        elif self.id=="fi":
            return QPixmap(":/countries/fi.jpg")
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
            
class Global:
    def __init__(self, mem):
        self.mem=mem
    def get_database_version(self):
        cur=self.mem.conms.cursor()
        cur.execute("select value from globals where id_globals=1;")
        resultado=cur.fetchone()['value']
        cur.close()
        return resultado

    def get_database_init_date(self):
        cur=self.mem.conms.cursor()
        cur.execute("select value from globals where id_globals=5;")
        resultado=cur.fetchone()['value']
        cur.close()
        return resultado

    def get_session_counter(self):
        cur=self.mem.conms.cursor()
        cur.execute("select value from globals where id_globals=3;")
        resultado=cur.fetchone()['value']
        cur.close()
        return resultado

    def get_system_counter(self):
        cur=self.mem.conms.cursor()
        cur.execute("select value from globals where id_globals=2;")
        resultado=cur.fetchone()['value']
        cur.close()
        return resultado

    def set_database_init_date(self, valor):
        cur=self.mem.conms.cursor()
        cur.execute("update globals set value=%s where id_globals=5;", (valor, ))
        cur.close()

    def set_database_version(self, valor):
        cur=self.mem.conms.cursor()
        cur.execute("update globals set value=%s where id_globals=1;", (valor, ))
        cur.close()

    def set_session_counter(self, valor):
        cur=self.mem.conms.cursor()
        cur.execute("update globals set value=%s where id_globals=3;", (valor, ))
        cur.close()

    def set_system_counter(self, valor):
        cur=self.mem.conms.cursor()
        cur.execute("update globals set value=%s where id_globals=2;", (valor, ))
        cur.close()
    
    def set_sourceforge_version(self):
        cur=self.mem.conms.cursor()
        try:
            serverversion=""
            comand='http://mystocks.svn.sourceforge.net/viewvc/mystocks/libxulpymoney.py'
            web=urllib.request.urlopen(comand)
            for line in web:
                if line.decode().find('return "20')!=-1:
                    if len(line.decode().split('"')[1])==8:
                        serverversion=line.decode().split('"')[1]        
                        cur.execute("update globals set value=%s where id_globals=4;", (serverversion, ))
                        log("VERSION-SOURCEFORGE", "", QApplication.translate("Core","Sourceforge version detected: %s") % serverversion)
        except:
            log("VERSION-SOURCEFORGE", "", QApplication.translate("Core","Error buscando la versión actual de Sourceforge"))                    
        cur.close()
    def get_sourceforge_version(self):
        cur=self.mem.conms.cursor()
        cur.execute("select value from globals where id_globals=4;")
        resultado=cur.fetchone()['value']
        cur.close()
        return resultado


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
        
class SetZones:
    def __init__(self, mem):
        self.mem=mem
        self.dic_arr={}
        
    def load_all(self):
        self.dic_arr["Europe/Madrid"]=Zone(self.mem).init__create(1,'Europe/Madrid', self.mem.countries.find("es"))#ALGUN DIA HABRá QUE CAMBIAR LAS ZONES POR ID_ZONESº
        self.dic_arr["Europe/Lisbon"]=Zone(self.mem).init__create(2,'Europe/Lisbon', self.mem.countries.find("pt"))
        self.dic_arr["Europe/Rome"]=Zone(self.mem).init__create(3,'Europe/Rome', self.mem.countries.find("it"))
        self.dic_arr["Europe/London"]=Zone(self.mem).init__create(4,'Europe/London', self.mem.countries.find("en"))
        self.dic_arr['Asia/Tokyo']=Zone(self.mem).init__create(5,'Asia/Tokyo', self.mem.countries.find("jp"))
        self.dic_arr["Europe/Berlin"]=Zone(self.mem).init__create(6,'Europe/Berlin', self.mem.countries.find("de"))
        self.dic_arr["America/New_York"]=Zone(self.mem).init__create(7,'America/New_York', self.mem.countries.find("us"))
        self.dic_arr["Europe/Paris"]=Zone(self.mem).init__create(8,'Europe/Paris', self.mem.countries.find("fr"))
        self.dic_arr["Asia/Hong_Kong"]=Zone(self.mem).init__create(9,'Asia/Hong_Kong', self.mem.countries.find("cn"))

    def qcombobox(self, combo, zone=None):
        """Carga entidades bancarias en combo"""
        for a in self.list():
            combo.addItem(a.country.qicon(), a.name, a.name)

        if zone!=None:
            combo.setCurrentIndex(combo.findText(zone.name))
        
    def find(self, id):
        return self.dic_arr[str(id)]        
        
    def list(self):
        """Devuelve una lista ordenada por nombre """
        arr=dic2list(self.dic_arr)
        arr=sorted(arr, key=lambda a: a.name,  reverse=False)         
        return arr        
        

def arr_split(arr, wanted_parts=1):
    length = len(arr)
    return [ arr[i*length // wanted_parts: (i+1)*length // wanted_parts] 
             for i in range(wanted_parts) ]

def arr2stralmohadilla(arr):
    resultado=""
    for a in arr:
        resultado=resultado + str(a) + "#"
    return resultado[:-1]
        
def stralmohadilla2arr(string, type="s"):
    """SE utiliza para matplotlib dsde consola"""
    arr=string.split("#")
    resultado=[]
    for a in arr:
            if type=="s":
                    resultado.append(a.decode('UTF-8'))
            elif type=="f":
                    resultado.append(float(a))
#                       return numpy.array(resultado)
            elif type=="t":
                    dat=a.split(":")
                    resultado.append(datetime.time(int(dat[0]),int(dat[1])))
            elif type=="dt":
                    resultado.append(datetime.datetime.strptime(a, "%Y/%m/%d %H:%M"))
            elif type=="d":
                    resultado.append(datetime.datetime.strptime(a, "%Y-%m-%d").toordinal())
    return resultado

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
#    try:
        cur.execute('insert into status (source, process) values (%s,%s);', (source,  process))
#    except:
#        print("Posible llave duplicada")

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
        a.setTextColor(QColor(0, 0, 255))
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
    return b.decode(code)
    
def s2b(s, code='UTF8'):
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
    """QCheckstate to python bool"""
    if booleano==True:
        return Qt.Checked
    else:
        return Qt.Unchecked     
def comaporpunto(cadena):
    cadena=cadena.replace(b'.',b'')#Quita puntos
    cadena=cadena.replace(b',',b'.')#Cambia coma por punto
    return cadena



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
    rest=int(days -years*365 -months*30)
    return QApplication.translate("Core", "{0} years, {1} months and {2} days".format(years, months, rest))

def dic2list(dic):
    """Función que convierte un diccionario pasado como parametro a una lista de objetos"""
    resultado=[]
    for k,  v in dic.items():
        resultado.append(v)
    return resultado

def dt(date, hour, zone):
    """Función que devuleve un datetime con zone info"""    
    z=pytz.timezone(zone.name)
    a=datetime.datetime(date.year,  date.month,  date.day,  hour.hour,  hour.minute,  hour.second, hour.microsecond)
    a=z.localize(a)
    return a

        
def s2pd(s):
    """python string isodate 2 python datetime.date"""
    a=str(s).split(" ")[0]#por si viene un 2222-22-22 12:12
    a=str(s).split("-")
    return datetime.date(int(a[0]), int(a[1]),  int(a[2]))
    
def str2bool(s):
    """Converts strings True or False to boolean"""
    if s=="True":
        return True
    return False
    

def cur2dict(cur):
    """Función que convierte un cursor a una lista de diccionarioº"""
    resultado=[]
    for row in cur:
            d={}
            for key,col in enumerate(cur.description):
                    d[col[0]]=row[col[0]]
            resultado.append(d)
    return resultado

def cur2dictdict(cur, indexcolumn):
    """Función que convierte un cursor a un diccionario de diccionarioº"""
    resultado={}
    for row in cur:
        d={}
        for key,col in enumerate(cur.description):
                d[col[0]]=row[col[0]]
        resultado[str(row[indexcolumn])]=d
    return resultado


def qbool(bool):
    a=QTableWidgetItem(str(bool))
    a.setTextAlignment(Qt.AlignVCenter|Qt.AlignCenter)
    return a

def qcenter(string, digits=None):
    a=QTableWidgetItem(str(string))
    a.setTextAlignment(Qt.AlignVCenter|Qt.AlignCenter)
    return a
    
def qleft(string):
    a=QTableWidgetItem(str(string))
    a.setTextAlignment(Qt.AlignVCenter|Qt.AlignLeft)
    return a

def qmessagebox_developing():
    m=QMessageBox()
    m.setIcon(QMessageBox.Information)
    m.setText(QApplication.translate("Core", "This option is being developed"))
    m.exec_()    
    
def qright(string, digits=None):
    """When digits, limits the number to """
    if string!=None and digits!=None:
        string=round(string, digits)
    a=QTableWidgetItem(str(string))
    a.setTextAlignment(Qt.AlignVCenter|Qt.AlignRight)
    try:#If is a number corized it
        if string==None:
            a.setTextColor(QColor(0, 0, 255))
        elif string<0:
            a.setTextColor(QColor(255, 0, 0))
    except:
        pass
    return a





def qtpc(n):
    text= (tpc(n))
    a=QTableWidgetItem(text)
    a.setTextAlignment(Qt.AlignVCenter|Qt.AlignRight)
    if n==None:
        a.setTextColor(QColor(0, 0, 255))
    elif n<0:
        a.setTextColor(QColor(255, 0, 0))
    return a
      
def strnames(filter):
    s=""
    for i in filter:
        s=s+i+"+"
    return s[:-1]

def tpc(n):
    if n==None:
        return "None %"
    return str(round(n, 2))+ " %"

        
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
