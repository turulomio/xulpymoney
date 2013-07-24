from PyQt4.QtCore import *
from PyQt4.QtGui import *
import datetime,  time,  pytz,   psycopg2,  psycopg2.extras,  sys,  codecs,  urllib.request,    os,  configparser,  threading

sys.path.append("/etc/xulpymoney")
import config
  
#gettext.bindtextdomain('myquotes','/usr/share/locale/')
#gettext.textdomain('myquotes')

pathGraphIntraday=os.environ['HOME']+"/.myquotes/graphIntraday.png"
pathGraphHistorical=os.environ['HOME']+"/.myquotes/graphHistorical.png"
pathGraphPieTPC=os.environ['HOME']+"/.myquotes/graphPieTPC.png"

from decimal import *
version="20130724"
#sys.path.append(config.myquoteslib)
#from libxulpymoney import *
#class Priority:
#    p={}
#    p["1"]="Yahoo Financials. 200 pc."
#    p["2"]="Fondos de la bolsa de Madrid. Todos pc."
#    p["3"]="Bond alemán desde http://jcbcarc.dyndns.org. 3 pc."
#    p["4"]="Infobolsa. índices internacionales. 20 pc."
#    p["5"]="Productos cotizados bonus. 20 pc."
#
#
#class PriorityHistorical:
#    p={}
#    p["3"]="Yahoo Financials de 1 pc."



class CuentaOperacionHeredadaInversion:
    """Clase parar trabajar con las opercuentas generadas automaticamente por los movimientos de las inversiones"""
    

    def __init__(self, cfg):
        self.cfg=cfg    
    def insertar(self,  fecha, id_conceptos, id_tiposoperaciones, importe, comentario,id_cuentas,id_operinversiones,id_inversiones):
        cur=self.cfg.con.cursor()
        sql="insert into tmpinversionesheredada (fecha, id_conceptos, id_tiposoperaciones, importe, comentario,id_cuentas, id_operinversiones,id_inversiones) values ('"+str(fecha)+"', "+str(id_conceptos)+", "+str(id_tiposoperaciones)+", "+str(importe)+", '"+str(comentario)+"' ,"+str(id_cuentas)+", "+str(id_operinversiones)+", "+str(id_inversiones)+")"
        cur.execute(sql);
        cur.close()


    def actualizar_una_operacion(self,cur, id_operinversiones):
        """Esta función actualiza la tabla tmpinversionesheredada que es una tabla temporal donde 
        se almacenan las opercuentas automaticas por las operaciones con inversiones. Es una tabla 
        que se puede actualizar en cualquier momento con esta función"""

#    //Borra la tabla tmpinversionesheredada
        sqldel="delete from tmpinversionesheredada where id_operinversiones="+str(id_operinversiones)
        cur.execute(sqldel);
        cur.execute('select datetime, inversiones.id_cuentas as id_cuentas, inversion, fecha, importe, inversiones.id_inversiones as id_inversiones, comision, impuestos, id_tiposoperaciones from operinversiones,inversiones where inversiones.id_inversiones=operinversiones.id_inversiones and id_operinversiones='+str(id_operinversiones))
        row=cur.fetchone()
        fecha=row['datetime'].date();
        importe=row['importe'];
        id_inversiones=row['id_inversiones'];
        id_cuentas=row['id_cuentas']
        comision=row['comision'];
        impuestos=row['impuestos'];
        comentario="{0}|{1}|{2}|{3}".format(row['inversion'], importe, comision, impuestos)
      
        if row['id_tiposoperaciones']==4:#Compra Acciones
#row['inversion']+'. '+str('Importe')+': ' + str(importe)+". "+str('Comisión')+": " + str(comision)+ ". "+str('Impuestos')+": " + str(impuestos)
#row['inversion']+". "+str('Importe')+": " + str(importe)+". "+str('Comisión')+": " + str(comision)+ ". "+str('Impuestos')+": " + str(impuestos)            
#row['inversion']+". "+str('Importe')+": " + str(importe)+". "+str('Comisión')+": " + str(comision)+ ". "+str('Impuestos')+": " + str(impuestos), 
            #Se pone un registro de compra de acciones que resta el saldo de la opercuenta
            CuentaOperacionHeredadaInversion(self.cfg).insertar(fecha, 29, 4, -importe-comision, comentario,id_cuentas,id_operinversiones,id_inversiones);
        elif row['id_tiposoperaciones']==5:#// Venta Acciones
            #//Se pone un registro de compra de acciones que resta el saldo de la opercuenta
            CuentaOperacionHeredadaInversion(self.cfg).insertar(fecha, 35, 5, importe-comision-impuestos,comentario,id_cuentas,id_operinversiones,id_inversiones);
        elif row['id_tiposoperaciones']==6:# // Añadido de Acciones
            #//Si hubiera comisión se añade la comisión.
            if(comision!=0):
                CuentaOperacionHeredadaInversion(self.cfg).insertar(fecha, 38, 1, -comision-impuestos, comentario,  id_cuentas,id_operinversiones,id_inversiones);


    def actualizar_una_inversion(self,cur, cur2, id_inversiones):
#    //Borra la tabla tmpinversionesheredada
        sqldel="delete from tmpinversionesheredada where id_inversiones="+str(id_inversiones)
        cur.execute(sqldel);

#    //Se cogen todas las operaciones de inversiones de la base de datos
        sql="SELECT * from operinversiones where id_inversiones="+str(id_inversiones)
        cur.execute(sql);
        for row in cur:
            CuentaOperacionHeredadaInversion(self.cfg).actualizar_una_operacion(cur2, row['id_operinversiones']);


      
class SetInversiones:
    def __init__(self, cfg, cuentas, investments):
        self.arr=[]
        self.cfg=cfg
        self.cuentas=cuentas
        self.investments=investments
            
    def load_from_db(self, sql):
        cur=self.cfg.con.cursor()
        cur.execute(sql)#"Select * from inversiones"
        for row in cur:
            inv=Inversion(self.cfg).init__db_row(row,  self.cuentas.find(row['id_cuentas']), self.investments.find(row['myquotesid']))
            inv.get_operinversiones()
            inv.op_actual.get_valor_indicereferencia()
            self.arr.append(inv)
            sys.stdout.write("\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\bInversi´on {0}/{1}: ".format(cur.rownumber, cur.rowcount) )
            sys.stdout.flush()
        cur.close()  
            
    def find(self, id):
        for i in self.arr:
            if i.id==id:
                return i
        print ("No se ha encontrado la inversión {0} en SetInversiones.inversion".format(id))
        return None
        
                

    def qcombobox_same_investmentmq(self, combo,  investmentmq):
        """Muestra las inversiones activas que tienen el mq pasado como parametro"""
        arr=[]
        for i in self.arr:
            print (i.mq, investmentmq)
            if i.activa==True and i.mq==investmentmq:
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
            - Se añade una operinversion con traspaso de valores origen que tendrá un saldo de acciones negativo
            - Se añadirá un comentario con id_inversiondestino
            
        En destino:
            - Se añaden tantas operaciones como operinversionesactual con misma fecha 
            - Tendrán saldo positivo y el tipo operacion es traspaso de valores. destino 
            - Se añadirá un comentario con id_operinversion origen
            
        Devuelve False si ha habido algún problema
        
        ACTUALMENTE SOLO HACE UN TRASLADO TOTAL
        """
        #Comprueba que el subyacente de origen y destino sea el mismo
        if origen.mq!=destino.mq:
            return False
        cur=self.cfg.con.cursor()
        cur2=self.cfg.con.cursor()
        now=datetime.datetime.now(pytz.timezone(config.localzone))
#            def init__create(self, fecha, concepto, tipooperacion, importe,  comentario, cuenta, id=None):

        if comision!=0:
            op_cuenta=CuentaOperacion().init__create(now.date(), self.cfg.conceptos.find(38), self.cfg.tiposoperaciones(1), -comision, "Traspaso de valores", origen.cuenta)
            op_cuenta.save(cur)       
            origen.cuenta.saldo_from_db(cur2)        
            comentario="{0}|{1}".format(destino.id, op_cuenta.id)
        else:
            comentario="{0}|{1}".format(destino.id, "None")
        
        op_origen=InversionOperacion(self.cfg).init__create( self.cfg.tiposoperaciones(9), now, origen,  -numacciones, 0,0, comision, 0, comentario)
        op_origen.save(cur, cur2, False)      

        #NO ES OPTIMO YA QUE POR CADA SAVE SE CALCULA TODO
        comentario="{0}".format(op_origen.id)
        for o in origen.op_actual.arr:
            op_destino=InversionOperacion(self.cfg).init__create( self.cfg.tiposoperaciones(10), now, destino,  o.acciones, o.importe, o.impuestos, o.comision, o.valor_accion, comentario)
            op_destino.save(cur, cur2, False)
            
            
        #Vuelvo a introducir el comentario de la opercuenta
        

        self.cfg.con.commit()
        (origen.op_actual,  origen.op_historica)=origen.op.calcular()   
        (destino.op_actual,  destino.op_historica)=destino.op.calcular()   
#        CuentaOperacionHeredadaInversion(self.cfg).actualizar_una_inversion(cur, cur2,  self.inversion.id)  
        cur.close()
        cur2.close()
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
        destino=self.cfg.inversiones.inversion(int(id_inversiondestino))
        cur=self.cfg.con.cursor()
#        print (cur.mogrify("delete from operinversiones where id_tiposoperaciones=10 and id_inversiones=%s and comentario=%s", (id_inversiondestino, str(operinversionorigen.id))))

        cur.execute("delete from operinversiones where id_tiposoperaciones=10 and id_inversiones=%s and comentario=%s", (destino.id, str(operinversionorigen.id)))
        cur.execute("delete from operinversiones where id_operinversiones=%s", (operinversionorigen.id, ))
        if id_opercuentacomision!="None":
            cur.execute("delete from opercuentas where id_opercuentas=%s", (int(id_opercuentacomision), ))
            origen.cuenta.saldo_from_db(cur)
            
        self.cfg.con.commit()
        origen.get_operinversiones(cur, self.cfg)
        destino.get_operinversiones(cur, self.cfg)
        cur.close()
        return True
#        except:
#            return False
        
class SetMQInvestments:
    def __init__(self, cfg):
        self.arr=[]
        self.cfg=cfg
    def load_from_db(self, sql):
        """sql es una query sobre la tabla inversiones"""
        cur=self.cfg.con.cursor()
        curmq=self.cfg.conmq.cursor()
        cur.execute(sql)#"Select distinct(myquotesid) from inversiones"
        
        ##Conviert cur a lista separada comas
        lista=""
        for row in cur:
            lista=lista+ str(row['myquotesid']) + ", "
        lista=lista[:-2]
        
        ##Carga los investments
        curmq.execute("select * from investments where id in ("+lista+")" )
        for rowmq in curmq:
            inv=Investment(self.cfg).init__db_row(rowmq)
            inv.load_estimacion()
            inv.quotes.get_basic()
            self.arr.append(inv)
            sys.stdout.write("\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\bInvestment {0}/{1}: ".format(curmq.rownumber, curmq.rowcount) )
            sys.stdout.flush()
        cur.close()
        curmq.close()
                           
    def find(self, id):
        """Devuelve el objeto investment con id pasado como par´ametro y None si no lo encuentra"""
        for a in self.arr:
            if a.id==id:
                return a
        return None
        
class SetBolsas:
    def __init__(self, cfg):
        self.dic_arr={}
        self.cfg=cfg     
    
    def load_all_from_db(self):
        curmq=self.cfg.conmq.cursor()
        curmq.execute("Select * from bolsas")
        for row in curmq:
            self.dic_arr[str(row['id_bolsas'])]=Bolsa(self.cfg).init__db_row(row, self.cfg.countries.find(row['country']))
        curmq.close()
            
    def find(self, id):
        return self.dic_arr[str(id)]
        
    def list(self):
        return dic2list(self.dic_arr)
        
class SetCommon:
    def __init__(self):
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
        
        
        
        
class SetConceptos:      
    def __init__(self, cfg, tiposoperaciones):
        self.dic_arr={}
        self.cfg=cfg     
        self.tiposoperaciones=tiposoperaciones
        
                 
    def load_from_db(self):
        cur=self.cfg.con.cursor()
        cur.execute("Select * from conceptos")
        for row in cur:
            self.dic_arr[str(row['id_conceptos'])]=Concepto(self.cfg).init__db_row(row, self.tiposoperaciones.find(row['id_tiposoperaciones']))
        cur.close()
            
    def find(self, id):
        return self.dic_arr[str(id)]
        
    def list(self):
        lista=dic2list(self.dic_arr)
        lista=sorted(lista, key=lambda c: c.name  ,  reverse=False)    
        return lista

    def list_x_tipooperacion(self, id_tiposoperaciones):
        resultado=[]
        for k, v in self.dic_arr.items():
            if v.tipooperacion.id==id_tiposoperaciones:
                resultado.append(v)
        resultado=sorted(resultado, key=lambda c: c.name  ,  reverse=False)  
        return resultado


class SetCountries:
    def __init__(self, cfg):
        self.dic_arr={}
        self.cfg=cfg   
        
    def load_all(self):
        self.dic_arr['es']=Country().init__create("es",QApplication.translate("Core","España"))
        self.dic_arr['be']=Country().init__create("be",QApplication.translate("Core","Bélgica"))
        self.dic_arr['cn']=Country().init__create("cn",QApplication.translate("Core","China"))
        self.dic_arr['de']=Country().init__create("de",QApplication.translate("Core","Alemania"))
        self.dic_arr['en']=Country().init__create("en",QApplication.translate("Core","Reino Unido"))
        self.dic_arr['eu']=Country().init__create("eu",QApplication.translate("Core","Europa"))
        self.dic_arr['fi']=Country().init__create("fi",QApplication.translate("Core","Finlandia"))
        self.dic_arr['fr']=Country().init__create("fr",QApplication.translate("Core","Francia"))
        self.dic_arr['ie']=Country().init__create("ie",QApplication.translate("Core","Irlanda"))
        self.dic_arr['it']=Country().init__create("it",QApplication.translate("Core","Italia"))
        self.dic_arr['jp']=Country().init__create("jp",QApplication.translate("Core","Japón"))
        self.dic_arr['nl']=Country().init__create("nl",QApplication.translate("Core","Países Bajos"))
        self.dic_arr['pt']=Country().init__create("pt",QApplication.translate("Core","Portugal"))
        self.dic_arr['us']=Country().init__create("us",QApplication.translate("Core","Estados Unidos"))
                

    def list(self):
        return dic2list(self.dic_arr)
    def find(self, id):
        return self.dic_arr[str(id)]

class SetCuentas:     
    def __init__(self, cfg,  setebs):
        self.arr=[]
        self.cfg=cfg   
        self.ebs=setebs

    def load_from_db(self, sql):
        cur=self.cfg.con.cursor()
        cur2=self.cfg.con.cursor()
        cur.execute(sql)#"Select * from cuentas"
        for row in cur:
            c=Cuenta(self.cfg).init__db_row(row, self.ebs.find(row['id_entidadesbancarias']))
            c.saldo_from_db()
            self.arr.append(c)
        cur.close()
        cur2.close()
                               
    def find(self, id):
        for a in self.arr:
            if a.id==id:
                return a
                
    def sort(self):
        self.arr=sorted(self.arr, key=lambda c: c.name,  reverse=False)         
    
    
class SetCurrencies:
    def __init__(self, cfg):
        self.dic_arr={}
        self.cfg=cfg   
    
    def load_all(self):
        self.dic_arr["CNY"]=Currency().init__create(QApplication.translate("Core","Yoanes chino"), "¥", 'CNY')
        self.dic_arr['EUR']=Currency().init__create(QApplication.translate("Core","Euro"), "€", "EUR")
        self.dic_arr['GBP']=Currency().init__create(QApplication.translate("Core","Libra esterlina"),"£", 'GBP')
        self.dic_arr['JPY']=Currency().init__create(QApplication.translate("Core","Yen Japonés"), '¥', "JPY")
        self.dic_arr['USD']=Currency().init__create(QApplication.translate("Core","Dólar americano"), '$', 'USD')
        self.dic_arr['u']=Currency().init__create(QApplication.translate("Core","Unidades"), 'u', 'u')

    def list_orderby_id(self):
        """Devuelve una lista ordenada por id"""
        currencies=dic2list(self.dic_arr)
        currencies=sorted(currencies, key=lambda c: c.id,  reverse=False)         
        return currencies

    def find(self, id):
        return self.dic_arr[str(id)]
        


    def load_qcombobox(combo, selectedcurrency=None):
        """Función que carga en un combo pasado como parámetro las currencies"""
        for c in self.list_orderby_id():
            combo.addItem("{0} - {1} ({2})".format(c.id, c.name, c.symbol), c.id)
        #NO SE PUEDE PONER C COMO VARIANT YA QUE LUEGO EL FIND NO ENCUENTRA EL OBJETO.

class SetEBs:     
    def __init__(self, cfg):
        self.arr=[]
        self.cfg=cfg   
    def load_from_db(self, sql):
        cur=self.cfg.con.cursor()
        cur.execute(sql)#"select * from entidadesbancarias"
        for row in cur:
            self.arr.append(EntidadBancaria().init__db_row(row))
        cur.close()                                    
    def find(self, id):
        for a in self.arr:
            if a.id==id:
                return a
            
    def ebs_activas(self, activa=True):
        """Función que devuelve una lista con objetos EntidadBancaria activos o no según el parametro"""
        resultado=[]
        for e in self.ebs():
            if e.activa==activa:
                resultado.append(e)
        return resultado
        
    def sort(self):       
        self.arr=sorted(self.arr, key=lambda e: e.name,  reverse=False) 

class SetInversionOperacion(SetCommon):       
    """Clase es un array ordenado de objetos newInversionOperacion"""
    def __init__(self, cfg):
        SetCommon.__init__(self)
        self.cfg=cfg
        
    def calcular_new(self):
        """Realiza los c´alculos y devuelve dos arrays"""
        sioh=SetInversionOperacionHistorica(self.cfg)
        sioa=SetInversionOperacionActual(self.cfg)       
        for o in self.arr:      
#            print ("Despues ",  sioa.acciones(), o)              
            if o.acciones>=0:#Compra
                sioa.arr.append(InversionOperacionActual(self.cfg).init__create(o, o.tipooperacion, o.datetime, o.inversion, o.acciones, o.importe, o.impuestos, o.comision, o.valor_accion,  o.id))
            else:#Venta
                if abs(o.acciones)>sioa.acciones():
                    print (o.acciones, sioa.acciones(),  o)
                    print("No puedo vender m´as acciones que las que tengo. EEEEEEEEEERRRRRRRRRRRROOOOORRRRR")
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
        operinversioneshistorica=SetInversionOperacionHistorica(self.cfg)
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
                    operinversioneshistorica.append(InversionOperacionHistorica(self.cfg).init__create(n, n.inversion, p.datetime.date(), -n.acciones*n.valor_accion,n.tipooperacion, n.acciones, comisiones, impuestos, n.datetime.date(), p.valor_accion, n.valor_accion))
                    arr.remove(n)
                    arr.remove(p)
                    break
                elif dif<0:#   //Si es <0 es decir hay más acciones negativas que positivas. Se debe introducir en el historico la tmpoperinversion y borrarlo y volver a recorrer el bucle. Restando a n.acciones las acciones ya apuntadas en el historico
                    operinversioneshistorica.append(InversionOperacionHistorica(self.cfg).init__create(p, p.inversion, p.datetime.date(), p.acciones*n.valor_accion,n.tipooperacion, -p.acciones, comisiones, impuestos, n.datetime.date(), p.valor_accion, n.valor_accion))
                    arr.remove(p)
                    n.acciones=n.acciones+p.acciones#ya que n.acciones es negativo

                elif(dif>0):
                    """Cuando es >0 es decir hay mas acciones positivos se añade el registro en el historico 
                    con los datos de la operacion negativa en su totalidad. Se borra el registro de negativos y 
                    de positivos en operinversionesactual y se inserta uno con los datos positivos menos lo 
                    quitado por el registro negativo. Y se sale del bucle. 
                    //Aqui no se inserta la comision porque solo cuando se acaba las acciones positivos   """
                    operinversioneshistorica.append(InversionOperacionHistorica(self.cfg).init__create(p, n.inversion, p.datetime.date(), -n.acciones*n.valor_accion,n.tipooperacion, n.acciones, comisiones, impuestos, n.datetime.date(), p.valor_accion, n.valor_accion))
                    arr.remove(p)
                    arr.remove(n)
                    arr.append(InversionOperacion(self.cfg).init__create( p.tipooperacion, p.datetime, p.inversion,  p.acciones-(-n.acciones), (p.acciones-(-n.acciones))*n.valor_accion,  0, 0, p.valor_accion, "",  p.id))
                    arr=sorted(arr, key=lambda a:a.id)              
                    break;
        #Crea array operinversionesactual, ya que arr es operinversiones
        operinversionesactual=SetInversionOperacionActual(self.cfg)
        for a in arr:
            operinversionesactual.append(InversionOperacionActual(self.cfg).init__create(a.id, a.tipooperacion, a.datetime, a.inversion,  a.acciones, a.importe,  a.impuestos, a.comision, a.valor_accion))
        return (operinversionesactual, operinversioneshistorica)
            
    def clone(self):
        """Funcion que devuelve un SetInversionOperacion, con todas sus InversionOperacion clonadas. Se usa para
        hacer estimaciones"""
        resultado=SetInversionOperacion(self.cfg)
        for io in self.arr:
            resultado.arr.append(io.clone())
        return resultado
        
#    def hayNegativas(self):
#        """Funci´on que devuelve si hay operaciones negativos en el array"""
#        for io in self.arr:
#            if io.acciones<0:
#                return True
#        return False
#    def saldoNegativo(self):
#        """Funci´on que devuelve el n´umero de acciones de venta. 
#        Devuelve un n´umero positivo.
#        Deber´a ignorar las archivadas"""
#        resultado=Decimal('0')
#        for io in self.arr:
#            if io.acciones<0:
#                resultado=resultado-(io.acciones)
#        return resultado

class SetInversionOperacionActual(SetCommon):       
    """Clase es un array ordenado de objetos newInversionOperacion"""
    def __init__(self, cfg):
        SetCommon.__init__(self)
        self.cfg=cfg
    def __repr__(self):
        try:
            inversion=self.arr[0].inversion.id
        except:
            inversion="Desconocido"
        return ("SetIOA Inv: {0}. N.Registros: {1}. N.Acciones: {2}. Invertido: {3}. Valor medio:{4}".format(inversion,  len(self.arr), self.acciones(),  self.invertido(),  self.valor_medio_compra()))
        
    def fecha_primera_operacion(self):
        if len(self.arr)==0:
            return None
        return self.arr[0].datetime.date()
        
    def acciones(self):
        """Devuelve el n´umero de acciones de la inversi´on actual"""
        resultado=Decimal(0)
        for o in self.arr:
            resultado=resultado+o.acciones
        return resultado
            
    
    def invertido(self):
        resultado=0
        for o in self.arr:
            resultado=resultado+o.invertido()
        return resultado
        
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
            
        dias=(datetime.date.today()-self.datetime.date()).days +1 #Cuenta el primer día
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
    
    def get_valor_indicereferencia(self):
        curmq=self.cfg.conmq.cursor()
        for o in self.arr:
            o.get_referencia_indice()
        curmq.close()
    
    def valor_medio_compra(self):
        """Devuelve el valor medio de compra de todas las operaciones de inversi´on actual"""
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
        io es una Inversionoperacion de venta
        1 Pasa al set de inversion operacion historica tantas inversionoperacionesactual como acciones tenga
       la inversion operacion de venta
      2 Si no ha sido un n´umero exacto y se ha partido la ioactual, añade la difrencia al setIOA y lo quitado a SIOH
      
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
                    sioh.arr.append(InversionOperacionHistorica(self.cfg).init__create(ioa, io.inversion, ioa.datetime.date(), io.acciones*io.valor_accion, io.tipooperacion, io.acciones, comisiones, impuestos, io.datetime.date(), ioa.valor_accion, io.valor_accion))
                    self.arr.insert(0, InversionOperacionActual(self.cfg).init__create(ioa, ioa.tipooperacion, ioa.datetime, ioa.inversion,  ioa.acciones-abs(accionesventa), (ioa.acciones-abs(accionesventa))*ioa.valor_accion,  0, 0, ioa.valor_accion, ioa.id))
                    self.arr.remove(ioa)
                    accionesventa=Decimal('0')#Sale bucle
                    break
                elif ioa.acciones-accionesventa<Decimal('0'):#<0 Se historiza todo y se restan acciones venta
                    comisiones=comisiones+ioa.comision
                    impuestos=impuestos+ioa.impuestos
                    sioh.arr.append(InversionOperacionHistorica(self.cfg).init__create(ioa, io.inversion, ioa.datetime.date(), -ioa.acciones*io.valor_accion, io.tipooperacion, -ioa.acciones, Decimal('0'), Decimal('0'), io.datetime.date(), ioa.valor_accion, io.valor_accion))
                    accionesventa=accionesventa-ioa.acciones                    
                    self.arr.remove(ioa)
                    
                elif ioa.acciones-accionesventa==Decimal('0'):#Se historiza todo y se restan acciones venta y se sale
                    comisiones=comisiones+io.comision+ioa.comision
                    impuestos=impuestos+io.impuestos+ioa.impuestos
                    sioh.arr.append(InversionOperacionHistorica(self.cfg).init__create(ioa, io.inversion, ioa.datetime.date(), ioa.acciones*io.valor_accion, io.tipooperacion, -ioa.acciones, comisiones, impuestos, io.datetime.date(), ioa.valor_accion, io.valor_accion))
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
 
class SetInversionOperacionHistorica(SetCommon):       
    """Clase es un array ordenado de objetos newInversionOperacion"""
    def __init__(self, cfg):
        SetCommon.__init__(self)
        self.cfg=cfg
        
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

        
class InversionOperacionHistorica:
    def __init__(self, cfg):
        self.cfg=cfg 
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
        dias=(self.fecha_venta-self.fecha_inicio).days +1 #Cuenta el primer día
        if dias==0:
            dias=1
        return Decimal(365*self.tpc_total_neto()/dias)
        
                
class InversionOperacionActual:
    def __init__(self, cfg):
        self.cfg=cfg 
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
        """Inversion es un objeto Inversion"""
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
                
    def get_referencia_indice(self):
        """Función que devuelve un Quote con la referencia del indice.
        Si no existe devuelve un Quote con quote 0"""
        curmq=self.cfg.conmq.cursor()
        quote=Quote(self.cfg).init__from_query(curmq, self.cfg.indicereferencia, self.datetime)
        if quote==None:
            self.referenciaindice= Quote(self.cfg).init__create(self.cfg.indicereferencia, self.datetime, 0)
        else:
            self.referenciaindice=quote
        curmq.close()
        return self.referenciaindice
        
    def invertido(self):
        """Función que devuelve el importe invertido teniendo en cuenta las acciones actuales de la operinversión y el valor de compra
        Si se usa  el importe no fuNCIONA PASO CON EL PUNTOI DE VENTA.
        """
        return self.acciones*self.valor_accion
        
    def saldo(self,  lastquote):
        """Función que calcula el saldo actual de la operinversion actual
                - lastquote: objeto Quote"""
        return self.acciones*lastquote.quote
        
    def pendiente(self, lastquote,  invertido=None):
        """Función que calcula el saldo  pendiente de la operacion de inversion actual
                Necesita haber cargado mq getbasic y operinversionesactual
                lasquote es un objeto Quote
                """
        if invertido==None:
            invertido=self.invertido()
        return self.saldo(lastquote)-invertido
        
    def tpc_anual(self,  last,  endlastyear):
        if self.datetime.year==datetime.date.today().year:
            endlastyear=self.valor_accion                
        if endlastyear==0:
            return 0
        return 100*(last-endlastyear)/endlastyear
    
    def tpc_total(self,  last):
        if self.valor_accion==0:
            return 0
        return 100*(last-self.valor_accion)/self.valor_accion
        
    def tpc_tae(self, last):
        dias=(datetime.date.today()-self.datetime.date()).days +1 #Cuenta el primer día
        if dias==0:
            dias=1
        return Decimal(365*self.tpc_total(last)/dias)
        
class Concepto:
    def __init__(self, cfg):
        self.cfg=cfg
        self.id=None
        self.name=None
        self.tipooperacion=None
        self.editable=None

    def __repr__(self):
        return ("Instancia de Concepto: {0} ({1})".format( self.name, self.id))

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
#    def saldo(self, cur, year,  month):
#        sql="select sum(importe) as importe from opercuentastarjetas where id_conceptos="+str(self.id)+" and date_part('year',fecha)='"+str(year)+"' and date_part('month',fecha)='"+str(month)+"'"
#        saldoopercuentastarjetas=con.Execute(sql).GetRowAssoc(0)["importe"]
#        if saldoopercuentastarjetas==None:
#            saldoopercuentastarjetas=0
#        return saldoopercuentastarjetas
        
    def save(self,  cur):
        if self.id==None:
            con.Execute("insert into conceptos (concepto, id_tiposoperaciones, editable) values (%s, %s, %s)", (self.name, self.tipooperacion.id, self.editable))
        else:
            con.Execute("update conceptos set concepto=%s, id_tiposoperaciones=%s, editable=%s where id_conceptos=%s", (self.name, self.tipooperacion.id, self.editable, self.id))
                            
    def es_borrable(self, cur):
        """Función que devuelve un booleano si una cuenta es borrable, es decir, que no tenga registros dependientes."""
        cur.execute("select count(*) from opercuentas where id_conceptos=%s", (self.id, ))
        if cur.fetchone()[0]!=0:
            return False
        cur.execute("select count(*) from opertarjetas where id_conceptos=%s", (self.id, ))
        if cur.fetchone()[0]!=0:
            return False
        return True

    def media_mensual(self):
        cur=self.cfg.con.cursor()
        cur.execute("select fecha from opercuentas where id_conceptos=%s union select fecha from opertarjetas where id_conceptos=%s order by fecha limit 1", (self.id, self.id))
        res=cur.fetchone()
        if res==None:
            primerafecha=datetime.date.today()-datetime.timedelta(days=1)
        else:
            primerafecha=res['fecha']
        cur.execute("select sum(importe) as suma from opercuentas where id_conceptos=%s union select sum(importe) as suma from opertarjetas where id_conceptos=%s", (self.id, self.id))
        suma=0
        for i in cur:
            if i['suma']==None:
                continue
            suma=suma+i['suma']
        cur.close()
        return 30*suma/((datetime.date.today()-primerafecha).days+1)
        
    def mensual(self,   year,  month):            
        cur=self.cfg.con.cursor()
        cur.execute("select sum(importe) as suma from opercuentas where id_conceptos=%s and date_part('month',fecha)=%s and date_part('year', fecha)=%s union select sum(importe) as suma from opertarjetas where id_conceptos=%s  and date_part('month',fecha)=%s and date_part('year', fecha)=%s", (self.id,  month, year,  self.id,  month, year  ))
        suma=0
        for i in cur:
            if i['suma']==None:
                continue
            suma=suma+i['suma']
        cur.close()
        return suma

class CuentaOperacion:
    def __init__(self):
        self.id=None
        self.fecha=None
        self.concepto=None
        self.tipooperacion=None
        self.importe=None
        self.comentario=None
        self.cuenta=None
        
    def init__create(self, fecha, concepto, tipooperacion, importe,  comentario, cuenta, id=None):
        self.id=id
        self.fecha=fecha
        self.concepto=concepto
        self.tipooperacion=tipooperacion
        self.importe=importe
        self.comentario=comentario
        self.cuenta=cuenta
        return self
        
    def init__db_row(self, row, concepto,  tipooperacion, cuenta):
        return self.init__create(row['fecha'],  concepto,  tipooperacion,  row['importe'],  row['comentario'],  cuenta,  row['id_opercuentas'])

    def borrar(self, cur):
        
        print ("cuenta borrar before",  self.cuenta.saldo)
        cur.execute("delete from opercuentas where id_opercuentas=%s", (self.id, ))
        self.cuenta.saldo_from_db(cur)
        print ("cuenta borrar after",  self.cuenta.saldo)
        
    def comentariobonito(self):
        """Función que genera un comentario parseado según el tipo de operación o concepto"""
        if self.concepto.id in (62, 39) and len(self.comentario.split("|"))==4:#"{0}|{1}|{2}|{3}".format(self.inversion.name, self.bruto, self.retencion, self.comision)
            return QApplication.translate("Core","Dividendo de {0[0]}. Bruto: {0[1]} {1}. Retención: {0[2]} {1}. Comisión: {0[3]} {1}".format(self.comentario.split("|"), self.cuenta.currency.symbol))
        elif self.concepto.id in (29, 35, 38) and len(self.comentario.split("|"))==4:#{0}|{1}|{2}|{3}".format(row['inversion'], importe, comision, impuestos)
            return QApplication.translate("Core","Operación de {0[0]}. Importe: {0[1]} {1}. Comisión: {0[2]} {1}. Impuestos: {0[3]} {1}".format(self.comentario.split("|"), self.cuenta.currency.symbol))        
        elif self.concepto.id==40 and len(self.comentario.split("|"))==2:#"{0}|{1}".format(self.selTarjeta.name, len(self.setSelOperTarjetas))
            return QApplication.translate("Core","Tarjeta: {0[0]}. Se han ejecutado {0[1]} pagos con tarjeta".format(self.comentario.split("|")))        
        else:
            return self.comentario

        
        
    def es_editable(self):
        """opercuenta es un diccionario con el contenido de una opercuetna
        7 facturación de tarjeta
        29 y 35 compraventa productos de inversión
        39 dividendos
        40 facturación de tarjeta"""
        if self.concepto==None:
            return False
        if self.concepto.id in (7, 29, 35, 39, 40, 62):#div, factur tarj:
            return False
        return True
        
    def save(self, cur):
        if self.id==None:
            cur.execute("insert into opercuentas (fecha, id_conceptos, id_tiposoperaciones, importe, comentario, id_cuentas) values ( %s,%s,%s,%s,%s,%s) returning id_opercuentas",(self.fecha, self.concepto.id, self.tipooperacion.id, self.importe, self.comentario, self.cuenta.id))
            self.id=cur.fetchone()[0]
        else:
            cur.execute("update opercuentas set fecha=%s, id_conceptos=%s, id_tiposoperaciones=%s, importe=%s, comentario=%s, id_cuentas=%s where id_opercuentas=%s", (self.fecha, self.concepto.id, self.tipooperacion.id,  self.importe,  self.comentario,  self.cuenta.id,  self.id))
        self.cuenta.saldo_from_db(cur)
        
class Dividendo:
    def __init__(self, cfg):
        self.cfg=cfg
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
        return ("Instancia de Dividendo: {0} ({1})".format( self.neto, self.id))
        
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
        return self.init__create(inversion,  row['bruto'],  row['retencion'], row['neto'],  row['valorxaccion'],  row['fecha'],   row['comision'],  concepto, opercuenta, row['id_dividendos'])
        
    def borrar(self, cur):
        """Borra un dividendo, para ello borra el registro de la tabla dividendos 
            y el asociado en la tabla opercuentas
            
            También actualiza el saldo de la cuenta."""
        self.opercuenta.borrar(cur)
        cur.execute("delete from dividendos where id_dividendos=%s", (self.id, ))
        self.inversion.cuenta.saldo_from_db(cur)
        
    def neto_antes_impuestos(self):
        return self.bruto-self.comision
    
    def save(self,cur):
        """Insertar un dividendo y una opercuenta vinculada a la tabla dividendos en el campo id_opercuentas
        Cuando se inserta el campo comentario de opercuenta tiene la forma (nombreinversion|bruto\retencion|comision)
        
        En caso de que sea actualizar un dividendo hay que actualizar los datos de opercuenta y se graba desde aquí. No desde el objeto opercuenta
        
        Actualiza la cuenta 
        """
        comentario="{0}|{1}|{2}|{3}".format(self.inversion.name, self.bruto, self.retencion, self.comision)
        if self.id==None:#Insertar
            oc=CuentaOperacion().init__create( self.fecha,self.concepto, self.concepto.tipooperacion, self.neto, comentario, self.inversion.cuenta)
            oc.save(cur)
            self.opercuenta=oc
            #Añade el dividendo
            sql="insert into dividendos (fecha, valorxaccion, bruto, retencion, neto, id_inversiones,id_opercuentas, comision, id_conceptos) values ('"+str(self.fecha)+"', "+str(self.dpa)+", "+str(self.bruto)+", "+str(self.retencion)+", "+str(self.neto)+", "+str(self.inversion.id)+", "+str(self.opercuenta.id)+", "+str(self.comision)+", "+str(self.concepto.id)+")"
            cur.execute(sql)
        else:
            self.opercuenta.fecha=self.fecha
            self.opercuenta.importe=self.neto
            self.opercuenta.comentario=comentario
            self.opercuenta.concepto=self.concepto
            self.opercuenta.tipooperacion=self.concepto.tipooperacion
            self.opercuenta.save(cur)
            cur.execute("update dividendos set fecha=%s, valorxaccion=%s, bruto=%s, retencion=%s, neto=%s, id_inversiones=%s, id_opercuentas=%s, comision=%s, id_conceptos=%s where id_dividendos=%s", (self.fecha, self.dpa, self.bruto, self.retencion, self.neto, self.inversion.id, self.opercuenta.id, self.comision, self.concepto.id, self.id))
        self.inversion.cuenta.saldo_from_db(cur)

class InversionOperacion:
    def __init__(self, cfg):
        self.cfg=cfg
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
    
    def clone(self):
        """Crea una inversion operacion desde otra inversionoepracion. NO es un enlace es un objeto clone"""
        resultado=InversionOperacion(self.cfg)
        resultado.init__create(self.tipooperacion, self.datetime, self.inversion, self.acciones, self.importe, self.impuestos, self.comision, self.valor_accion, self.comentario, self.id)
        return resultado
                
    def comentariobonito(self):
        """Función que genera un comentario parseado según el tipo de operación o concepto"""
        if self.tipooperacion.id==9:#"Traspaso de valores. Origen"#"{0}|{1}|{2}|{3}".format(self.inversion.name, self.bruto, self.retencion, self.comision)
            return QApplication.translate("Core","Traspaso de valores realizado a {0}".format(self.comentario.split("|"), self.cuenta.currency.symbol))
        else:
            return self.comentario

    def save(self, recalculate=True):
        cur=self.cfg.con.cursor()
        cur2=self.cfg.con.cursor()
        if self.id==None:#insertar
            cur.execute("insert into operinversiones(datetime, id_tiposoperaciones,  importe, acciones,  impuestos,  comision,  valor_accion, comentario, id_inversiones) values (%s, %s, %s, %s, %s, %s, %s, %s,%s) returning id_operinversiones", (self.datetime, self.tipooperacion.id, self.importe, self.acciones, self.impuestos, self.comision, self.valor_accion, self.comentario, self.inversion.id))
            self.id=cur.fetchone()[0]
            self.inversion.op.append(self)
        else:
            cur.execute("update operinversiones set datetime=%s, id_tiposoperaciones=%s, importe=%s, acciones=%s, impuestos=%s, comision=%s, valor_accion=%s, comentario=%s, id_inversiones=%s where id_operinversiones=%s", (self.datetime, self.tipooperacion.id, self.importe, self.acciones, self.impuestos, self.comision, self.valor_accion, self.comentario, self.inversion.id, self.id))
        if recalculate==True:
            (self.inversion.op_actual,  self.inversion.op_historica)=self.inversion.op.calcular()   
            CuentaOperacionHeredadaInversion(self.cfg).actualizar_una_inversion(cur, cur2,  self.inversion.id)  
            self.inversion.cuenta.saldo_from_db(cur2)
        self.cfg.con.commit()
        cur.close()
        cur2.close()
        
    def borrar(self):
        cur=self.cfg.con.cursor()
        cur2=self.cfg.con.cursor()
        cur.execute("delete from operinversiones where id_operinversiones=%s",(self.id, ))
        self.inversion.op.arr.remove(self)
        (self.inversion.op_actual,  self.inversion.op_historica)=self.inversion.op.calcular()
        CuentaOperacionHeredadaInversion(self.cfg).actualizar_una_inversion(cur, cur2,  self.inversion.id)#Es una inversion ya que la id_operinversion ya no existe. Se ha borrado
        self.inversion.cuenta.saldo_from_db(cur2)
        cur.close()
        cur2.close()
        
    def tpc_anual(self,  last,  endlastyear):
        return
    
    def tpc_total(self,  last):
        return
   
class EntidadBancaria:
    """Clase que encapsula todas las funciones que se pueden realizar con una Entidad bancaria o banco"""
    def __init__(self):
        """Constructor que inicializa los atributos a None"""
        self.id=None
        self.name=None
        self.activa=None
        
    def init__create(self, name,  activa=True, id=None):
        self.id=id
        self.activa=activa
        self.name=name
        return self
        
    def __repr__(self):
        return ("Instancia de EntidadBancaria: {0} ({1})".format( self.name, self.id))

    

    def init__db_row(self, row):
        self.id=row['id_entidadesbancarias']
        self.name=row['entidadbancaria']
        self.activa=row['eb_activa']
        return self
        
    def save(self, cur):
        """Función que inserta si self.id es nulo y actualiza si no es nulo"""
        if self.id==None:
            cur.execute("insert into entidadesbancarias (entidadbancaria, eb_activa) values (%s,%s) returning id_entidadesbancarias", (self.name, self.activa))
            self.id=cur.fetchone()[0]
        else:
            cur.execute("update entidadesbancarias set entidadbancaria=%s, eb_activa=%s where id_entidadesbancarias=%s", (self.name, self.activa, self.id))
        
    def saldo(self, setcuentas,  setinversiones):
        resultado=0
        #Recorre saldo cuentas
        for v in setcuentas.arr:
            if v.eb.id==self.id:
                resultado=resultado+v.saldo
        
        #Recorre saldo inversiones
        for i in setinversiones.arr:
            if i.cuenta.eb.id==self.id:
                resultado=resultado+i.saldo()
        return resultado
        
    def es_borrable(self, dic_cuentas):
        """Función que devuelve un booleano si una cuenta es borrable, es decir, que no tenga registros dependientes."""
        #Recorre saldo cuentas
        for k, v in dic_cuentas.items():
            if v.eb.id==self.id:
                return False
        return True
        
    def borrar(self,cur, dic_cuentas):
        """Función que borra una vez comprobado que es variable
        dic_cuentas es el diccionario de todas las cuentas de la applicación"""
        if self.es_borrable(dic_cuentas)==True:
            cur.execute("delete from entidadesbancarias where id_entidadesbancarias=%s", (self.id, ))  
            
class Cuenta:
    def __init__(self, cfg):
        self.cfg=cfg
        self.id=None
        self.name=None
        self.eb=None
        self.activa=None
        self.numero=None
        self.currency=None
        self.eb=None #Enlace a objeto
        self.saldo=0#Se calcula al crear el objeto y cuando haya opercuentas se calcula dinamicamente

    def __repr__(self):
        return ("Instancia de Cuenta: {0} ({1})".format( self.name, self.id))
        
    def init__db_row(self, row, eb):
        self.id=row['id_cuentas']
        self.name=row['cuenta']
        self.eb=eb
        self.activa=row['cu_activa']
        self.numero=row['numerocuenta']
        self.currency=self.cfg.currencies.find(row['currency'])
        return self
    
    def saldo_from_db(self,fecha=None):
        """Función que calcula el saldo de una cuenta
        Solo asigna saldo al atributo saldo si la fecha es actual, es decir la actual
        Parámetros:
            - pg_cursor cur Cursor de base de datos
            - datetime.date fecha Fecha en la que calcular el saldo
        Devuelve:
            - Decimal saldo Valor del saldo
        """
        cur=self.cfg.con.cursor()
        if fecha==None:
            fecha=datetime.date.today()
        cur.execute('select sum(importe)  from opercuentas where id_cuentas='+ str(self.id) +" and fecha<='"+str(fecha)+"';") 
        saldo=cur.fetchone()[0]
        if saldo==None:
            cur.close()
            return 0        
        if fecha==datetime.date.today():
            self.saldo=saldo
        cur.close()
        return saldo
            
    def init__create(self, name,  eb, activa, numero, currency, id=None):
        self.id=id
        self.name=name
        self.eb=eb
        self.activa=activa
        self.numero=numero
        self.currency=currency
        return self
    
#    def init__db_extended_row(self, row):
#        """Carga de un row que tiene eb, cuentas inversiones"""
#        self.init__db_row(row)
#        self.eb=EntidadBancaria().init__db_row(row)
#        return self
        
    def save(self, cur):
        if self.id==None:
            cur.execute("insert into cuentas (id_entidadesbancarias, cuenta, numerocuenta, cu_activa,currency) values (%s,%s,%s,%s,%s) returning id_cuentas", (self.eb.id, self.name, self.numero, self.activa, self.currency.id))
            self.id=cur.fetchone()[0]
        else:
            cur.execute("update cuentas set cuenta=%s, id_entidadesbancarias=%s, numerocuenta=%s, cu_activa=%s, currency=%s where id_cuentas=%s", (self.name, self.eb.id, self.numero, self.activa, self.currency.id, self.id))


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

    def transferencia(self, fecha,  cuentaorigen,  cuentadestino, importe, comision ):
        """Cuenta origen y cuenta destino son objetos cuenta"""
        cur=self.cfg.con.cursor()
        sql="select transferencia('"+str(fecha)+"', "+ str(cuentaorigen.id) +', ' + str(cuentadestino.id)+', '+str(importe) +', '+str(comision)+');'
        cur.execute(sql)
        cuentaorigen.saldo_from_db(cur)
        cuentadestino.saldo_from_db(cur)
        cur.close()
        
class Inversion:
    """Clase que encapsula todas las funciones que se pueden realizar con una Inversión
    
    Las entradas al objeto pueden ser por:
        - init__db_row
        - init__db_extended_row
        - create. Solo contenedor hasta realizar un save y guardar en id, el id apropiado. mientras id=None
        
    """
    def __init__(self, cfg):
        """Constructor que inicializa los atributos a None"""
        self.cfg=cfg
        self.id=None
        self.name=None
        self.venta=None
#        self.id_cuentas=None
        self.mq=None#Puntero a objeto MQInversion
        self.cuenta=None#Vincula a un objeto  Cuenta
        self.activa=None
        self.op=None#Es un objeto SetInversionOperacion
        self.op_actual=None#Es un objeto newSetoperinversionesactual
        self.op_historica=None#newoperinversioneshistorica
        
        
    def create(self, name, venta, cuenta, inversionmq):
        self.name=name
        self.venta=venta
        self.cuenta=cuenta
        self.mq=inversionmq
        self.activa=True
        return self
    
    
    def save(self, cur):
        """Inserta o actualiza la inversión dependiendo de si id=None o no"""
        if self.id==None:
            cur.execute("insert into inversiones (inversion, venta, id_cuentas, in_activa, myquotesid) values (%s, %s,%s,%s,%s) returning id_inversiones", (self.name, self.venta, self.cuenta.id, self.activa, self.mq.id))    
            self.id=cur.fetchone()[0]
        else:
            cur.execute("update inversiones set inversion=%s, venta=%s, id_cuentas=%s, in_activa=%s, myquotesid=%s where id_inversiones=%s", (self.name, self.venta, self.cuenta.id, self.activa, self.mq.id, self.id))

    def __repr__(self):
        return ("Instancia de Inversion: {0} ({1})".format( self.name, self.id))
        
    def init__db_row(self, row, cuenta, mqinvestment):
        self.id=row['id_inversiones']
        self.name=row['inversion']
        self.venta=row['venta']
        self.cuenta=cuenta
        self.mq=mqinvestment
        self.activa=row['in_activa']
        return self


    def es_borrable(self):
        """Función que devuelve un booleano si una cuenta es borrable, es decir, que no tenga registros dependientes."""
        if self.op==None: #No se ha cargado con get_operinversiones
            return False
        if len(self.op.arr)>0:
            return False
        return True
        
    def borrar(self, cur):
        if self.es_borrable()==True:
            cur.execute("delete from inversiones where id_inversiones=%s", (self.id, ))

        
    def get_operinversiones(self):
        """Funci`on que carga un array con objetos inversion operacion y con ellos calcula el set de actual e historicas"""
        cur=self.cfg.con.cursor()
        self.op=SetInversionOperacion(self.cfg)
        cur.execute("SELECT * from operinversiones where id_inversiones=%s order by datetime", (self.id, ))
        for row in cur:
            self.op.append(InversionOperacion(self.cfg).init__db_row(row, self, self.cfg.tiposoperaciones.find(row['id_tiposoperaciones'])))
#        print ("\n")
#        print ("acciones antes",  self.acciones(datetime.datetime(2011, 9, 22)),  self.acciones(datetime.datetime(2011, 9, 24)))
#        inicio=datetime.datetime.now()
#        (self.op_actual, self.op_historica)=self.op.calcular()
#        print (datetime.datetime.now()-inicio, self.op_actual)
#        inicio=datetime.datetime.now()        
#        (self.op_actual_new,  self.op_historica_new)=self.op.calcular_new()
#        print (datetime.datetime.now()-inicio, self.op_actual_new)
        
#        
#        
#        
        #AL FINAL ME QUEDO CON PARA PRUEBAS :
        (self.op_actual,  self.op_historica)=self.op.calcular_new()
        
#        if (self.id==80):
#            print (self.op_actual.print_list())
#            print (self.op_actual_new.print_list())
        
        
        
        
        
        
        cur.close()
        

    
    def dividendo_bruto_estimado(self, year=None):
        """
            Si el year es None es el año actual
            Calcula el dividendo estimado de la inversion se ha tenido que cargar:
                - El inversiones mq
                - La estimacion de dividendos mq"""
        if year==None:
            year=datetime.date.today().year
        return self.acciones()*self.mq.estimaciones[str(year)].dpa
        
        
    def diferencia_saldo_diario(self):
        """Función que calcula la diferencia de saldo entre last y penultimate
        Necesita haber cargado mq getbasic y operinversionesactual"""
        try:
            return self.acciones()*(self.mq.quotes.last.quote-self.mq.quotes.penultimate.quote)
        except:
            return None
            
    def dividendos_neto(self, ano,  mes=None):
        """Dividendo cobrado en un año y mes pasado como parámetro, independientemente de si la inversión esta activa o no"""
        cur=self.cfg.con.cursor()
        if mes==None:#Calcula en el año
            cur.execute("select sum(neto) as neto from dividendos where date_part('year',fecha) = "+str(ano))
            resultado=cur.fetchone()[0]
        else:
            cur.execute("select sum(neto) as neto from dividendos where date_part('year',fecha) = "+str(ano)+" and date_part('month',fecha)= " + str(mes))
            resultado=cur.fetchone()[0]   
        if resultado==None:
            resultado=0
        cur.close()
        return resultado;                   
    def dividendos_bruto(self,  ano,  mes=None):
        """Dividendo cobrado en un año y mes pasado como parámetro, independientemente de si la inversión esta activa o no"""
        
        cur=self.cfg.con.cursor()
        if mes==None:#Calcula en el año
            cur.execute("select sum(bruto) as bruto from dividendos where date_part('year',fecha) = "+str(ano))
            resultado=cur.fetchone()[0]
        else:
            cur.execute("select sum(bruto) as bruto from dividendos where date_part('year',fecha) = "+str(ano)+" and date_part('month',fecha)= " + str(mes))
            resultado=cur.fetchone()[0]   
        if resultado==None:
            resultado=0
        cur.close()
        return resultado;                
    
        
    def acciones(self, fecha=None):
        """Función que saca el número de acciones de las self.op_actual"""
        if fecha==None:
            dat=datetime.datetime.now(pytz.timezone(config.localzone))
        else:
            dat=day_end_from_date(fecha, config.localzone)
        resultado=Decimal('0')

        for o in self.op.arr:
            if o.datetime<=dat:
                resultado=resultado+o.acciones
                    
#        print ("Inversion >  Acciones de {0} el {1}: {2}".format(self.name, fecha,  resultado))

        return resultado
        
    def pendiente(self):
        """Función que calcula el saldo  pendiente de la inversión
                Necesita haber cargado mq getbasic y operinversionesactual"""
        return self.saldo()-self.invertido()
        
    def saldo(self, fecha=None):
        """Función que calcula el saldo de la inversión
            Si el curmq es None se calcula el actual 
                Necesita haber cargado mq getbasic y operinversionesactual"""     
#        print (self.name)
#        print (self.mq.quotes.endlastyear,  self.mq.quotes.penultimate, self.mq.quotes.last)       
        curmq=self.cfg.conmq.cursor()
        if fecha==None:
            curmq.close()
            return self.acciones()*self.mq.quotes.last.quote
        else:
            acciones=self.acciones(fecha)
            if acciones==0:
                curmq.close()
                return Decimal('0')
            quote=Quote(self.cfg).init__from_query(curmq, self.mq, day_end_from_date(fecha, config.localzone))
            if quote.datetime==None:
                print ("Inversion saldo: {0} ({1}) en {2} no tiene valor".format(self.name, self.mq.id, fecha))
                curmq.close()
                return Decimal('0')
            curmq.close()
            return acciones*quote.quote
        
    def invertido(self):       
        """Función que calcula el saldo invertido partiendo de las acciones y el precio de compra
        Necesita haber cargado mq getbasic y operinversionesactual"""
        resultado=Decimal('0')
        for o in self.op_actual.arr:
            resultado=resultado+(o.acciones*o.valor_accion)
        return resultado
                
    def tpc_invertido(self):       
        """Función que calcula el tpc invertido partiendo de las saldo actual y el invertido
        Necesita haber cargado mq getbasic y operinversionesactual"""
        invertido=self.invertido()
        if invertido==0:
            return 0
        return (self.saldo()-invertido)*100/invertido
    def tpc_venta(self):       
        """Función que calcula el tpc venta partiendo de las el last y el valor_venta
        Necesita haber cargado mq getbasic y operinversionesactual"""
        if self.venta==0 or self.venta==None or self.mq.quotes.last.quote==None or self.mq.quotes.last.quote==0:
            return 0
        return (self.venta-self.mq.quotes.last.quote)*100/self.mq.quotes.last.quote

        



class Tarjeta:    
    def __init__(self):
        self.id=None
        self.name=None
        self.id_cuentas=None
        self.cuenta=None
        self.pagodiferido=None
        self.saldomaximo=None
        self.activa=None
        self.numero=None
        
        self.op_diferido=[]#array que almacena objetos Tarjeta operacion que son en diferido
        
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
                    
    def borrar(self,  cur):
        """
            Devuelve False si no ha podido borrarse por haber dependientes.
        """
        cur.execute("select count(*) from opertarjetas where id_tarjetas=%s", (self.id, ))
        if cur.fetchone()['count']>0: # tiene dependientes
            return False
        else:
            sql="delete from tarjetas where id_tarjetas="+ str(self.id);
            cur.execute(sql)
            return True
        
    def get_opertarjetas_diferidas_pendientes(self, cur, cfg):
        """Funci`on que carga un array con objetos inversion operacion y con ellos calcula el set de actual e historicas"""
        self.op_diferido=[]
        cur.execute("SELECT * from opertarjetas where id_tarjetas=%s and pagado=false", (self.id, ))
        for row in cur:
            self.op_diferido.append(TarjetaOperacion().init__db_row(row, cfg.conceptos.find(row['id_conceptos']), cfg.tiposoperaciones.find(row['id_tiposoperaciones']), self))
        
    def saldo_pendiente(self):
        """Es el saldo solo de operaciones difreidas sin pagar"""
        resultado=0
        for o in self.op_diferido:
            resultado=resultado+ o.importe
        return resultado


class TarjetaOperacion:
    def __init__(self):
        """Tarjeta es un objeto TarjetaOperacion. pagado, fechapago y opercuenta solo se rellena cuando se paga"""
        self.id=None
        self.fecha=None
        self.concepto=None
        self.tipooperacion=None
        self.importe=None
        self.comentario=None
        self.tarjeta=None
        self.pagado=None
        self.fechapago=None
        self.opercuenta=None
        
    def init__create(self, fecha,  concepto, tipooperacion, importe, comentario, tarjeta, pagado=None, fechapago=None, opercuenta=None, id_opertarjetas=None):
        """pagado, fechapago y opercuenta solo se rellena cuando se paga"""
        self.id=id_opertarjetas
        self.fecha=fecha
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
        return self.init__create(row['fecha'],  concepto, tipooperacion, row['importe'], row['comentario'], tarjeta, row['pagado'], row['fechapago'], opercuenta, row['id_opertarjetas'])
        
    def borrar(self,  cur):
        sql="delete from opertarjetas where id_opertarjetas="+ str(self.id)
        cur.execute(sql)
        
    def save(self, cur):
        if self.id==None:#insertar
            sql="insert into opertarjetas (fecha, id_conceptos, id_tiposoperaciones, importe, comentario, id_tarjetas, pagado) values ('" + str(self.fecha) + "'," + str(self.concepto.id)+","+ str(self.tipooperacion.id) +","+str(self.importe)+", '"+self.comentario+"', "+str(self.tarjeta.id)+", "+str(self.pagado)+") returning id_opertarjetas"
            cur.execute(sql);
            self.id=cur.fetchone()[0]
        else:
            if self.tarjeta.pagodiferido==True and self.pagado==False:#No hay opercuenta porque es en diferido y no se ha pagado
                cur.execute("update opertarjetas set fecha=%s, id_conceptos=%s, id_tiposoperaciones=%s, importe=%s, comentario=%s, id_tarjetas=%s, pagado=%s, fechapago=%s, id_opercuentas=%s where id_opertarjetas=%s", (self.fecha, self.concepto.id, self.tipooperacion.id,  self.importe,  self.comentario, self.tarjeta.id, self.pagado, self.fechapago, None, self.id))
            else:
                cur.execute("update opertarjetas set fecha=%s, id_conceptos=%s, id_tiposoperaciones=%s, importe=%s, comentario=%s, id_tarjetas=%s, pagado=%s, fechapago=%s, id_opercuentas=%s where id_opertarjetas=%s", (self.fecha, self.concepto.id, self.tipooperacion.id,  self.importe,  self.comentario, self.tarjeta.id, self.pagado, self.fechapago, self.opercuenta.id, self.id))

        
class TipoOperacion:
    def __init__(self):
        self.id=None
        self.name=None
        
    def init__create(self, name,  id=None):
        self.id=id
        self.name=name
        return self


class Patrimonio:
    def __init__(self, cfg):
        self.cfg=cfg        
    
    def primera_fecha_con_datos_usuario(self):        
        """Devuelve la fecha actual si no hay datos. Base de datos vacía"""
        cur=self.cfg.con.cursor()
        sql='select fecha from opercuentas UNION select datetime::date from operinversiones UNION select fecha from opertarjetas order by fecha limit 1;'
        cur.execute(sql)
        if cur.rowcount==0:
            return datetime.date.today()
        resultado=cur.fetchone()[0]
        cur.close()
        return resultado

    def saldo_todas_cuentas(self,  fecha=None):
        """Si cur es none y fecha calcula el saldo actual."""
        cur=self.cfg.con.cursor()
        resultado=0
        sql="select cuentas_saldo('"+str(fecha)+"') as saldo;";
        cur.execute(sql)
        resultado=cur.fetchone()[0] 
        cur.close()
        return resultado;

        
    def saldo_total(self, setinversiones,  fecha):
        """Versión que se calcula en cliente muy optimizada"""
        return self.saldo_todas_cuentas(fecha)+self.saldo_todas_inversiones(setinversiones, fecha)

        
    def saldo_todas_inversiones(self, setinversiones,   fecha):
        """Versión que se calcula en cliente muy optimizada"""
        resultado=0
        for i in setinversiones.arr:
            resultado=resultado+i.saldo(fecha)                 
        return resultado
        
    def saldo_todas_inversiones_riesgo_cero(self, setinversiones, fecha=None):
        """Versión que se calcula en cliente muy optimizada
        Fecha None calcula  el saldo actual
        """
        resultado=0
        inicio=datetime.datetime.now()
        for inv in setinversiones.arr:
            if inv.mq.tpc==0:        
                if fecha==None:
                    resultado=resultado+inv.saldo()
                else:
                    resultado=resultado+inv.saldo( fecha)
        print ("core > Total > saldo_todas_inversiones_riego_cero: {0}".format(datetime.datetime.now()-inicio))
        return resultado


    def patrimonio_riesgo_cero(self, setinversiones, fecha):
        """CAlcula el patrimonio de riego cero"""
        return self.saldo_todas_cuentas(fecha)+self.saldo_todas_inversiones_riesgo_cero(setinversiones, fecha)

    def saldo_anual_por_tipo_operacion(self,  ano,  id_tiposoperaciones):   
        """Opercuentas y opertarjetas"""
        cur=self.cfg.con.cursor()
        sql="select sum(Importe) as importe from opercuentas where id_tiposoperaciones="+str(id_tiposoperaciones)+" and date_part('year',fecha) = "+str(ano)  + " union select sum(Importe) as importe from opertarjetas where id_tiposoperaciones="+str(id_tiposoperaciones)+" and date_part('year',fecha) = "+str(ano)
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
        cur=self.cfg.con.cursor()
        sql="select sum(Importe) as importe from opercuentas where id_tiposoperaciones="+str(id_tiposoperaciones)+" and date_part('year',fecha) = "+str(ano)+" and date_part('month',fecha)= " + str(mes) + " union select sum(Importe) as importe from opertarjetas where id_tiposoperaciones="+str(id_tiposoperaciones)+" and date_part('year',fecha) = "+str(ano)+" and date_part('month',fecha)= " + str(mes)
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


class SetTarjetas:
    def __init__(self, cfg, cuentas):
        self.arr=[]
        self.dic_arr={} ##Prueba de duplicaci´on
        self.cfg=cfg   
        self.cuentas=cuentas

    def load_from_db(self, sql):
        cur=self.cfg.con.cursor()
        cur2=self.cfg.con.cursor()
        cur.execute(sql)#"Select * from tarjetas")
        for row in cur:
            t=Tarjeta().init__db_row(row, self.cuentas.find(row['id_cuentas']))
            if t.pagodiferido==True:
                t.get_opertarjetas_diferidas_pendientes(cur2, self.cfg)
            self.dic_arr[str(t.id)]=t
            self.arr.append(t)
        cur.close()
        cur2.close()
            


    def find(self, id):
        return self.dic_arr[str(id)]
        
    def tarjetas(self, id=None):
        if id==None:
            return dic2list(self.dic_tarjetas)
        else:
            return self.dic_tarjetas[str(id)]
                        
    def tarjetas_activas(self, activa=True):
        resultado=[]
        for i in self.tarjetas():
            if i.activa==activa:
                resultado.append(i)
        return resultado
        
        
        
class SetTiposOperaciones:      
    def __init__(self, cfg):
        self.dic_arr={}
        self.cfg=cfg     
        
    def load(self):
        self.dic_arr['1']=TipoOperacion().init__create( "Gasto", 1)
        self.dic_arr['2']=TipoOperacion().init__create( "Ingreso", 2)
        self.dic_arr['3']=TipoOperacion().init__create( "Trasferencia", 3)
        self.dic_arr['4']=TipoOperacion().init__create( "Compra de acciones", 4)
        self.dic_arr['5']=TipoOperacion().init__create( "Venta de acciones", 5)
        self.dic_arr['6']=TipoOperacion().init__create( "Añadido de acciones", 6)
        self.dic_arr['7']=TipoOperacion().init__create( "Facturacion Tarjeta", 7)
        self.dic_arr['8']=TipoOperacion().init__create( "Traspaso fondo inversión", 8) #Se contabilizan como ganancia
        self.dic_arr['9']=TipoOperacion().init__create( "Traspaso de valores. Origen", 9) #No se contabiliza
        self.dic_arr['10']=TipoOperacion().init__create( "Traspaso de valores. Destino", 10) #No se contabiliza     
        
    def find(self, id):
        return self.dic_arr[str(id)]
        
    def list(self):
        lista=dic2list(self.dic_arr)
        lista=sorted(lista, key=lambda t:t.name, reverse=False)
        return lista
        
    def clone_only_operinversiones(self):
        """Devuelve los tipos de operación específicos de operinversiones. en un arr de la forma"""
        resultado=SetTiposOperaciones(self.cfg)
        for key,  t in self.dic_arr.items():
            if key in ('4', '5', '6', '8'):
                resultado.dic_arr[str(key)]=t
        return resultado
            
class TUpdateData(threading.Thread):
    def __init__(self, cfg):
        threading.Thread.__init__(self)
        self.cfg=cfg
    
    def run(self):    
        inicio=datetime.datetime.now()
        self.cfg.indicereferencia.quotes.get_basic()
#        for k, v in self.cfg.dic_mqinversiones.items():
#            v.quotes.get_basic(curmq)
        print("Update quotes took",  datetime.datetime.now()-inicio) 


def mylog(text):
    f=open("/tmp/xulpymoney.log","a")
    f.write(str(datetime.datetime.now()) + "|" + text + "\n")
    f.close()
    
def decimal_check(dec):
    print ("Decimal check", dec, dec.__class__,  dec.__repr__(),  "prec:",  getcontext().prec)
    
def myqtablewidget_loads_SetInversionOperacionActual( tabla,  setinversionoperacionactual,  settingsname, cfg):
    """Función que rellena una tabla pasada como parámetro con datos procedentes de un array de objetos
    InversionOperacionActual y dos valores de myquotes para rellenar los tpc correspodientes
    
    Se dibujan las columnas pero las propiedad alternate color... deben ser en designer
    
    Parámetros
        - tabla myQTableWidget en la que rellenar los datos
        - setoperinversion. Vincula a una inversión que  Debe tener cargado mq con get_basic y las operaciones de inversión calculadas
    last es el último quote de la inversión"""
    #UI
    tabla.setColumnCount(10)
    tabla.setHorizontalHeaderItem(0, QTableWidgetItem(QApplication.translate(settingsname, "Día", None, QApplication.UnicodeUTF8)))
    tabla.setHorizontalHeaderItem(1, QTableWidgetItem(QApplication.translate(settingsname, "Acciones", None, QApplication.UnicodeUTF8)))
    tabla.setHorizontalHeaderItem(2, QTableWidgetItem(QApplication.translate(settingsname, "Valor compra", None, QApplication.UnicodeUTF8)))
    tabla.setHorizontalHeaderItem(3, QTableWidgetItem(QApplication.translate(settingsname, "Invertido", None, QApplication.UnicodeUTF8)))
    tabla.setHorizontalHeaderItem(4, QTableWidgetItem(QApplication.translate(settingsname, "Saldo actual", None, QApplication.UnicodeUTF8)))
    tabla.setHorizontalHeaderItem(5, QTableWidgetItem(QApplication.translate(settingsname, "Pendiente", None, QApplication.UnicodeUTF8)))
    tabla.setHorizontalHeaderItem(6, QTableWidgetItem(QApplication.translate(settingsname, "% anual", None, QApplication.UnicodeUTF8)))
    tabla.setHorizontalHeaderItem(7, QTableWidgetItem(QApplication.translate(settingsname, "% TAE", None, QApplication.UnicodeUTF8)))
    tabla.setHorizontalHeaderItem(8, QTableWidgetItem(QApplication.translate(settingsname, "% Total", None, QApplication.UnicodeUTF8)))
    tabla.setHorizontalHeaderItem(9, QTableWidgetItem(QApplication.translate(settingsname, "Índice de referencia", None, QApplication.UnicodeUTF8)))
    #DATA
    tabla.settings(settingsname,  cfg.inifile)
    if len(setinversionoperacionactual.arr)==0:
        tabla.setRowCount(0)
        return
    inversion=setinversionoperacionactual.arr[0].inversion
    numdigitos=inversion.mq.quotes.decimalesSignificativos()
    sumacciones=Decimal('0')
    sum_accionesXvalor=Decimal('0')
#        sum_accionesXtae=0
    sumsaldo=Decimal('0')
    sumpendiente=Decimal('0')
    suminvertido=Decimal('0')
    tabla.clearContents()
    tabla.setRowCount(len(setinversionoperacionactual.arr)+1)
    rownumber=0
    for a in setinversionoperacionactual.arr:
        sumacciones=Decimal(sumacciones)+Decimal(str(a.acciones))
        saldo=a.saldo(inversion.mq.quotes.last)
        pendiente=a.pendiente(inversion.mq.quotes.last)
        invertido=a.invertido()

        sumsaldo=sumsaldo+saldo
        sumpendiente=sumpendiente+pendiente
        suminvertido=suminvertido+invertido
        sum_accionesXvalor=sum_accionesXvalor+a.acciones*a.valor_accion

        tabla.setItem(rownumber, 0, qdatetime(a.datetime))
        tabla.setItem(rownumber, 1, qright("{0:.6f}".format(a.acciones)))
        tabla.setItem(rownumber, 2, inversion.mq.currency.qtablewidgetitem(a.valor_accion, numdigitos))
        tabla.setItem(rownumber, 3, inversion.mq.currency.qtablewidgetitem(invertido))
        tabla.setItem(rownumber, 4, inversion.mq.currency.qtablewidgetitem(saldo))
        tabla.setItem(rownumber, 5, inversion.mq.currency.qtablewidgetitem(pendiente))
        tabla.setItem(rownumber, 6, qtpc(a.tpc_anual(inversion.mq.quotes.last.quote, inversion.mq.quotes.endlastyear.quote)))
        tabla.setItem(rownumber, 7, qtpc(a.tpc_tae(inversion.mq.quotes.last.quote)))
        tabla.setItem(rownumber, 8, qtpc(a.tpc_total(inversion.mq.quotes.last.quote)))
        if a.referenciaindice==None:
            tabla.setItem(rownumber, 9, inversion.mq.currency.qtablewidgetitem(None))
        else:
            tabla.setItem(rownumber, 9, inversion.mq.currency.qtablewidgetitem(a.referenciaindice.quote))
        rownumber=rownumber+1
    tabla.setItem(rownumber, 0, QTableWidgetItem(("TOTAL")))
    tabla.setItem(rownumber, 1, qright(str(sumacciones)))
    if sumacciones==0:
        tabla.setItem(rownumber, 2, inversion.mq.currency.qtablewidgetitem(0))
    else:
        tabla.setItem(rownumber, 2, inversion.mq.currency.qtablewidgetitem(sum_accionesXvalor/sumacciones, numdigitos))
    tabla.setItem(rownumber, 3, inversion.mq.currency.qtablewidgetitem(suminvertido))
    tabla.setItem(rownumber, 4, inversion.mq.currency.qtablewidgetitem(sumsaldo))
    tabla.setItem(rownumber, 5, inversion.mq.currency.qtablewidgetitem(sumpendiente))
    tabla.setItem(rownumber, 7, qtpc(setinversionoperacionactual.tpc_tae(inversion.mq.quotes.last.quote)))
    tabla.setItem(rownumber, 8, qtpc(setinversionoperacionactual.tpc_total(sumpendiente, suminvertido)))
        
def myqtablewidget_loads_SetInversionOperacion(tabla,  arr):
    tabla.clearContents()
    tabla.setRowCount(len(arr))
    rownumber=0
    for a in arr:
        tabla.setItem(rownumber, 0, QTableWidgetItem(str(a.id)))
        tabla.setItem(rownumber, 1, qdatetime(a.datetime))
        tabla.setItem(rownumber, 2, QTableWidgetItem(a.tipooperacion.name))
        tabla.setItem(rownumber, 3, qright(str(a.acciones)))
        tabla.setItem(rownumber, 4, a.inversion.mq.currency.qtablewidgetitem(a.valor_accion))
        tabla.setItem(rownumber, 5, a.inversion.mq.currency.qtablewidgetitem(a.importe))
        tabla.setItem(rownumber, 6, a.inversion.mq.currency.qtablewidgetitem(a.comision))
        tabla.setItem(rownumber, 7, a.inversion.mq.currency.qtablewidgetitem(a.impuestos))
        rownumber=rownumber+1


        
    
def myqtablewidget_loads_SetInversionOperacionHistorica(tabla, arr):
    """Rellena datos de un array de objetos de InversionOperacionHistorica, devuelve totales ver código"""
    (sumbruto, sumneto)=(0, 0);
    sumsaldosinicio=0;
    sumsaldosfinal=0;

    sumoperacionespositivas=0;
    sumoperacionesnegativas=0;
    sumimpuestos=0;
    sumcomision=0;        
    tabla.clearContents()
    tabla.setRowCount(len(arr)+1)
    rownumber=0
    for a in arr:
        saldoinicio=a.bruto_compra()
        saldofinal=a.bruto_venta()
        bruto=a.consolidado_bruto()
        sumimpuestos=sumimpuestos-Decimal(str(a.impuestos))
        sumcomision=sumcomision-Decimal(str(a.comision))
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
        tabla.setItem(rownumber, 4,a.inversion.mq.currency.qtablewidgetitem(saldoinicio))
        tabla.setItem(rownumber, 5,a.inversion.mq.currency.qtablewidgetitem(saldofinal))
        tabla.setItem(rownumber, 6,a.inversion.mq.currency.qtablewidgetitem(bruto))
        tabla.setItem(rownumber, 7,a.inversion.mq.currency.qtablewidgetitem(a.comision))
        tabla.setItem(rownumber, 8,a.inversion.mq.currency.qtablewidgetitem(a.impuestos))
        tabla.setItem(rownumber, 9,a.inversion.mq.currency.qtablewidgetitem(neto))
        tabla.setItem(rownumber, 10,qtpc(a.tpc_tae_neto()))
        tabla.setItem(rownumber, 11,qtpc(a.tpc_total_neto()))
        rownumber=rownumber+1
    tabla.setItem(rownumber, 2,QTableWidgetItem("TOTAL"))    
    if len(arr)>0:
        currency=arr[0].inversion.mq.currency
        tabla.setItem(rownumber, 4,currency.qtablewidgetitem(sumsaldosinicio))    
        tabla.setItem(rownumber, 5,currency.qtablewidgetitem(sumsaldosfinal))    
        tabla.setItem(rownumber, 6,currency.qtablewidgetitem(sumbruto))    
        tabla.setItem(rownumber, 7,currency.qtablewidgetitem(sumcomision))    
        tabla.setItem(rownumber, 8,currency.qtablewidgetitem(sumimpuestos))    
        tabla.setItem(rownumber, 9,currency.qtablewidgetitem(sumneto))    
        tabla.setCurrentCell(rownumber, 4)       
    return (sumbruto, sumcomision, sumimpuestos, sumneto)

def qcombobox_loadcuentas(combo, cuentas,  cuenta=None):
    """Función que carga en un combo pasado como parámetro y con un SetCuentas pasado como parametro
        Se ordena por nombre y se se pasa el tercer parametro que es un objeto Cuenta lo selecciona""" 
    cuentas.sort()
    for cu in cuentas.arr:
        combo.addItem(cu.name, cu.id)
    if cuenta!=None:
            combo.setCurrentIndex(combo.findData(cuenta.id))
        

def qcombobox_loadebs(combo, ebs):
    """Carga entidades bancarias en combo. Es un SetEbs"""
    ebs.sort()
    for e in ebs.arr:
        combo.addItem(e.name, e.id)        

def qcombobox_loadconceptos(combo, conceptos):
    """conceptos es un array de objetos concepto"""
    for c in conceptos.list():
        if c.tipooperacion.id in (1, 2, 3):
            combo.addItem("{0} -- {1}".format(  c.name,  c.tipooperacion.name),  "{0};{1}".format(c.id, c.tipooperacion.id)   )#id_conceptos;id_tiposopeera ciones

def qcombobox_loadtiposoperaciones(combo, tipos):
    for t in tipos.list():
        combo.addItem(t.name,  t.id)

class SetAgrupations:
    """Se usa para meter en cfg las agrupaciones, pero tambi´en para crear agrupaciones en las inversiones"""
    def __init__(self, cfg):
        """Usa la variable cfg.Agrupations"""
        self.cfg=cfg
        self.dic_arr={}
        
        
    def load_all(self):
        self.dic_arr["ERROR"]=Agrupation(self.cfg).init__create( "ERROR","Agrupación errónea", self.cfg.types.find(3), self.cfg.bolsas.find(1) )
        self.dic_arr["IBEX"]=Agrupation(self.cfg).init__create( "IBEX","Ibex 35", self.cfg.types.find(3), self.cfg.bolsas.find(1) )
        self.dic_arr["MERCADOCONTINUO" ]=Agrupation(self.cfg).init__create( "MERCADOCONTINUO","Mercado continuo español", self.cfg.types.find(3), self.cfg.bolsas.find(1) )
        self.dic_arr[ "CAC"]=Agrupation(self.cfg).init__create("CAC",  "CAC 40 de Par´is", self.cfg.types.find(3),self.cfg.bolsas.find(3) )
        self.dic_arr["EUROSTOXX"]=Agrupation(self.cfg).init__create( "EUROSTOXX","Eurostoxx 50", self.cfg.types.find(3),self.cfg.bolsas.find(10)  )
        self.dic_arr["DAX"]=Agrupation(self.cfg).init__create( "DAX","DAX", self.cfg.types.find(3), self.cfg.bolsas.find(5)  )
        self.dic_arr["SP500"]=Agrupation(self.cfg).init__create("SP500",  "Standard & Poors 500", self.cfg.types.find(3), self.cfg.bolsas.find(2)  )
        self.dic_arr["NASDAQ100"]=Agrupation(self.cfg).init__create( "NASDAQ100","Nasdaq 100", self.cfg.types.find(3), self.cfg.bolsas.find(2)  )
        self.dic_arr["EURONEXT"]=Agrupation(self.cfg).init__create( "EURONEXT",  "EURONEXT", self.cfg.types.find(3), self.cfg.bolsas.find(10)  )
        self.dic_arr["DEUTSCHEBOERSE"]=Agrupation(self.cfg).init__create( "DEUTSCHEBOERSE",  "DEUTSCHEBOERSE", self.cfg.types.find(3), self.cfg.bolsas.find(5)  )


        self.dic_arr["e_fr_LYXOR"]=Agrupation(self.cfg).init__create( "e_fr_LYXOR","LYXOR", self.cfg.types.find(4),self.cfg.bolsas.find(3)  )
        self.dic_arr["e_de_DBXTRACKERS"]=Agrupation(self.cfg).init__create( "e_de_DBXTRACKERS","Deutsche Bank X-Trackers", self.cfg.types.find(4),self.cfg.bolsas.find(5)  )
        
        self.dic_arr["f_es_0014"]=Agrupation(self.cfg).init__create("f_es_0014",  "Gestora BBVA", self.cfg.types.find(2), self.cfg.bolsas.find(1) )
        self.dic_arr["f_es_0043"]=Agrupation(self.cfg).init__create( "f_es_0043","Gestora Renta 4", self.cfg.types.find(2), self.cfg.bolsas.find(1))
        self.dic_arr["f_es_0055"]=Agrupation(self.cfg).init__create("f_es_0055","Gestora Bankinter", self.cfg.types.find(2),self.cfg.bolsas.find(1) )
        self.dic_arr["f_es_BMF"]=Agrupation(self.cfg).init__create( "f_es_BMF","Fondos de la bolsa de Madrid", self.cfg.types.find(2), self.cfg.bolsas.find(1) )

        self.dic_arr["w_fr_SG"]=Agrupation(self.cfg).init__create( "w_fr_SG","Warrants Societe Generale", self.cfg.types.find(5),self.cfg.bolsas.find(3) )
        self.dic_arr["w_es_BNP"]=Agrupation(self.cfg).init__create("w_es_BNP","Warrants BNP Paribas", self.cfg.types.find(5),self.cfg.bolsas.find(1))

    def find(self, id):
        try:
            return self.dic_arr[str(id)]        
        except:
            return self.dic_arr["ERROR"]
                
    def list (self, id=None):
        return dic2list(self.dic_arr)
    
    def agrupations_por_tipo(self,  type):
        """Muestra las agrupaciónes de un tipo pasado como par´ametro. El par´ametro type es un objeto Type"""
        resultado=[]
        for a in self.agrupations():
            if a.type==type:
                resultado.append(a)
        return resultado
        
    def init__all(self):
        self.arr=self.cfg.agrupations()
        return self
        
    def init__etfs(self):
        """Función que filtra el diccionario a según el país y el fondo """
        self.arr=self.cfg.agrupations_por_tipo(self.cfg.types.find(4))
        return self
        
#        return {k:v for k,v in self.cfg.Agrupations.items() if k[0]=='e' and  k[2]==country[0] and k[3]==country[1]}
    def init__warrants(self):
        """Función que filtra el diccionario a según el país y el fondo """
        self.arr=self.cfg.agrupations_por_tipo(self.cfg.types.find(5))
        return self
        
    def init__fondos(self):
        """Función que filtra el diccionario a según el país y el fondo """
        self.arr=self.cfg.agrupations_por_tipo(self.cfg.types.find(2))
        return self
        
    def init__acciones(self):
        """Función que filtra el diccionario a según el país y el fondo """
        self.arr=self.cfg.agrupations_por_tipo(self.cfg.types.find(1))
        return self
        
        
    def init__create_from_dbstring(self, dbstr):
        """Convierte la cadena de la base datos en un array de objetos agrupation"""
        resultado=SetAgrupations(self.cfg)
        if dbstr==None or dbstr=="":
            pass
        else:
            for item in dbstr[1:-1].split("|"):
                resultado.dic_arr[item]=self.cfg.agrupations.find(item)
        return self
        
    def combo(self, combo):
        combo.clear()
        for a in self.arr:
            combo.addItem(a.name, a.id)
            
    def dbstring(self):
        resultado="|"
        for a in self.arr:
            resultado=resultado+a.id+"|"
        if resultado=="|":
            return ""
        return resultado
        
        
    def init__create_from_combo(self, cmb):
        """Funci´on que convierte un combo de agrupations a un array de agrupations"""
        for i in range (cmb.count()):
            self.arr.append(self.cfg.agrupations(cmb.itemData(i)))
        return self

class SetApalancamientos:
    def __init__(self, cfg):
        """Usa la variable cfg.Agrupations"""
        self.cfg=cfg
        self.dic_arr={}
                
        
    def load_all(self):
        self.dic_arr["0"]=Apalancamiento(self.cfg).init__create(0 ,QApplication.translate("Core","No apalancado"))
        self.dic_arr["1"]=Apalancamiento(self.cfg).init__create( 1,QApplication.translate("Core","Apalancamiento variable (Warrants)"))
        self.dic_arr["2"]=Apalancamiento(self.cfg).init__create( 2,QApplication.translate("Core","Apalancamiento x2"))
        self.dic_arr["3"]=Apalancamiento(self.cfg).init__create( 3,QApplication.translate("Core","Apalancamiento x3"))
        self.dic_arr["4"]=Apalancamiento(self.cfg).init__create( 4,QApplication.translate("Core","Apalancamiento x4"))
               

    def list(self):
        return dic2list(self.dic_arr)
    def find(self, id):
        return self.dic_arr[str(id)]

class SetPriorities:
    def __init__(self, cfg):
        """Usa la variable cfg.Agrupations"""
        self.cfg=cfg
        self.dic_arr={}
                
    def load_all(self):
        self.dic_arr["1"]=Priority().init__create(1,"Yahoo Financials. 200 pc.")
        self.dic_arr["2"]=Priority().init__create(2,"Fondos de la bolsa de Madrid. Todos pc.")
        self.dic_arr["3"]=Priority().init__create(3,"Borrar")#SANTGES ERA 3, para que no se repitan
        self.dic_arr["7"]=Priority().init__create(7,"Bond alemán desde http://jcbcarc.dyndns.org. 3 pc.")#SANTGES ERA 3, para que no se repitan
        self.dic_arr["4"]=Priority().init__create(4,"Infobolsa. índices internacionales. 20 pc.")
        self.dic_arr["5"]=Priority().init__create(5,"Productos cotizados bonus. 20 pc.")
        self.dic_arr["6"]=Priority().init__create(6,"Societe Generale Warrants. Todos pc.")
                        
    
    def list(self):
        return dic2list(self.dic_arr)
    def find(self, id):
        return self.dic_arr[str(id)]
        
    def init__create_from_db(self, arr):
        """Convierte el array de enteros de la base datos en un array de objetos priority"""
        resultado=SetPriorities(self.cfg)
        if arr==None or len(arr)==0:
            resultado.dic_arr={}
        else:
            for a in arr:
                resultado.dic_arr[str(a)]=self.cfg.priorities.find(a)
        return resultado
    
    def dbstring(self):
        if len(self.arr)==0:
            return "NULL"
        else:
            resultado=[]
            for a in self.arr:
                resultado.append(a.id)
            return "ARRAY"+str(resultado)
        
    def init__create_from_combo(self, cmb):
        """Funci´on que convierte un combo de agrupations a un array de agrupations"""
        for i in range (cmb.count()):
            self.arr.append(self.cfg.priorities(cmb.itemData(i)))
        return self
                
    def init__all(self):
        self.arr=self.cfg.priorities()
        return self
class SetPrioritiesHistorical:
    def __init__(self, cfg):
        """Usa la variable cfg.Agrupations"""
        self.cfg=cfg
        self.dic_arr={}
        
            
    def load_all(self):
        self.dic_arr["3"]=PriorityHistorical().init__create(3,"Individual. Yahoo historicals")
    
    def list(self):
        return dic2list(self.dic_arr)
        
    def find(self, id):
        return self.dic_arr[str(id)]
            
    def init__create_from_db(self, arr):
        """Convierte el array de enteros de la base datos en un array de objetos priority"""
        resultado=SetPrioritiesHistorical(self.cfg)
        if arr==None or len(arr)==0:
            resultado.dic_arr={}
        else:
            for a in arr:
                resultado.dic_arr[str(a)]=self.cfg.prioritieshistorical.find(a)
        return resultado
            
#    def init__all(self):
#        self.arr=self.cfg.prioritieshistorical()
#        return self
        
    def dbstring(self):
        if len(self.arr)==0:
            return "NULL"
        else:
            resultado=[]
            for a in self.arr:
                resultado.append(a.id)
            return "ARRAY"+str(resultado)
        
    def init__create_from_combo(self, cmb):
        """Funci´on que convierte un combo de agrupations a un array de agrupations"""
        for i in range (cmb.count()):
            self.arr.append(self.cfg.prioritieshistorical(cmb.itemData(i)))
        return self

class Bolsa:
    def __init__(self, cfg):
        self.cfg=cfg
        self.id=None
        self.name=None
        self.country=None
        self.starts=None
        self.ends=None
        self.close=None
        self.zone=None
        
    def __repr__(self):
        return self.name
        
    def init__db_row(self, row,  country):
        self.id=row['id_bolsas']
        self.name=row['name']
        self.country=country
        self.starts=row['starts']
        self.ends=row['ends']
        self.close=row['close']
        self.zone=row['zone']#Intente hacer objeto pero era absurdo.
        return self


#configfile_myquotesuser=os.environ['HOME']+"/.myquotes/myquotes.cfg"
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
            
    def currencies_exchange(self, curmq,  quote, origen, destino):
        cambio=Quote.valor2(curmq, origen+"2"+destino, quote['fecha'],  quote['hora'])
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

class Money:
    "Permite operar con dinero y divisas teniendo en cuenta la fecha de la operación mirando la divisa en myquotes"
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

    def currencies_exchange(self, curmq,  quote, origen, destino):
        cambio=Quote.valor2(curmq, origen+"2"+destino, quote['fecha'],  quote['hora'])
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


class Estimacion:
    def __init__(self):
        self.year=None
        self.dpa=None
        self.fechaestimacion=None
        self.fuente=None
        self.manual=None
        self.investment=None# Objeto inversion mq
        self.bpa=None
        
    def init__db_row(self, row, inversionmq):
        self.year=row['year']
        self.dpa=row['dpa']
        self.fechaestimacion=row['fechaestimacion']
        self.fuente=row['fuente']
        self.manual=row['manual']
        self.bpa=row['bpa']
        self.investment=inversionmq #Permite acceder a todo el objeto desde la estimación
        return self
        
    def init__create(self, year, dpa, fechaestimacion, fuente, manual, bpa, inversionmq):
        self.year=year
        self.dpa=dpa
        self.fechaestimacion=fechaestimacion
        self.fuente=fuente
        self.manual=manual
        self.bpa=bpa
        self.investment=inversionmq #Permite acceder a todo el objeto desde la estimación
        return self
        
    def tpc_dpa(self):
        """Hay que tener presente que endlastyear (Objeto Quote) es el endlastyear del año actual
        Necesita tener cargado en id el endlastyear """
        if self.investment.quotes.endlastyear.quote==0 or self.investment.quotes.endlastyear.quote==None:
            return 0
        else:
            return self.dpa/self.investment.quotes.endlastyear.quote*100
    

class DividendoEstimacion:
    def __init__(self, cfg):
        self.cfg=cfg
    def dpa(cur, investment,  currentyear):
        cur.execute("select dpa from estimaciones where id=%s and year=%s", (investment.id, currentyear))
        if cur.rowcount==1:
            return cur.fetchone()[0]
        else:
            return None
    def registro(cur, investment,  currentyear):
        """Saca el registro sin code ni year, que fueron pasados como parámetro"""
        cur.execute("select dpa,fechaestimacion,fuente,manual from estimaciones where id=%s and year=%s", (investment.id, currentyear))
        if cur.rowcount==1:
            return cur.fetchone()
        else:
            return None
            
    def insertar(id,  year, dpa, fechaestimacion=datetime.date.today(), fuente='Internet',  manual=True):
        """Función que comprueba si existe el registro para insertar o modificarlo según proceda"""
        curmq=self.cfg.conmq.cursor()
        curmq.execute("select count(*) from estimaciones where id=%s and year=%s", (id, year))
        if curmq.fetchone()[0]==0:
            curmq.execute("insert into estimaciones (id, year, dpa, fechaestimacion, fuente, manual) values (%s,%s,%s,%s,%s,%s)", (id, year, dpa, fechaestimacion, fuente, manual))
        else:
            curmq.execute("update estimaciones set dpa=%s, fechaestimacion=%s, fuente=%s, manual=%s where id=%s and year=%s", (dpa, fechaestimacion, fuente, manual, id, year))
        curmq.close()
        
#class Gen:#Solo cuando hay que hacer arrays para una operacion como yahoo
#    yahoo1=1
#    yahoo2=2
#
#    
    
class SourceNew:
    """Clase nueva para todas las sources
    Debera:
    - Cargar al incio un sql con las investments del source"""
    def __init__(self, cfg, sql):
        self.investments=[]
        self.load_investments(sql)
    def load_investments(self,  sql):
        return
        
    def investments_to_search(self):
        """Funci´on que devuelve un array con las investments a buscar despu´es de hacer filtros
        Estos filtros son:
        - Filtro por horarios, aunque busque tarde debe meter la hora bien con .0001234, debe permitir primero"""
        
class SourceIntraday(SourceNew):
    def __init__(self, cfg, sql):
        SourceNew.__init__(self, cfg, sql)
        
        
class SourceDailyUnique(SourceNew):
    def __init__(self, cfg, sql):
        SourceNew.__init__(self, cfg, sql)
    
class SourceDailyGroup(SourceNew):
    def __init__(self, cfg, sql):
        SourceNew.__init__(self, cfg, sql)

    
    
class Source:
    """Solo se debe cambiar la función arr_*, independiente de si se usa static o statics
    Al crear uno nuevo se debe crear un start, que  no es heredada ni virtual en la que se cojan los distintos updates con process
    Luego crear las funciones virtuales.
    """
    def __init__(self,  cfg):
#        self.time_after_quotes=None#60#60
#        self.time_after_statics=None#86400 #60*60*24
#        self.time_after_historicals=None#86400 #60*60*24
#        self.time_after_dividends=None#86400 #60*60*24
#        self.time_step_quote=None#0
#        self.time_step_static=None#300#5*60
#        self.time_step_historical=None#300#30*60
#        self.time_step_dividend=None#600
#        self.time_before_statics=None#60
#        self.time_before_quotes=None#0
#        self.time_before_historicals=None#0
#        self.time_before_dividends=None#0
#        self.utctime_start=None#datetime.time de inicio de downloads
#        self.utctime_stop=None#datetime.time de final de downloads
        self.cfg=cfg
        self.debug=False#Si fuera true en vez de insertar  hace un listado#       
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
                self.cfg.activas[str(e)].priority_change(cur)
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
        con=self.cfg.connect_myquotesd()
        cur = con.cursor()     
        resultado=[]
        for id in ids:
            cur.execute(" select id, count(*) from quotes where id in (select id from investments where active=false and priority[1]=1) group by id;=%s and datetime::date<%s", (id, self.cfg.dbinitdate))
            if cur.fetchone()[0]==0:
                resultado.append(id)
        cur.close()                
        self.cfg.disconnect_myquotesd(con)
        return resultado
                
    def filtrar_ids_inactivos_no_actualizados(self, cur,  idpriority, dias,  priorityhistorical=False):
        """Filtra aquellos ids consultando a la base de datos, que tengan activa un id_prioridad
        o un id_prioridadhistorical si priorityhistorical=True y que no hayan sido actualizados desde now()-dias
        y que esten inactivo"""
        resultado=[]
        if priorityhistorical==False:
            cur.execute("select * from investments where (select count(*) from quotes where id=investments.id and datetime>now()::date-%s)=0 and active=false and priority[1]=%s;", (dias,  idpriority))   
        else:
            cur.execute("select * from investments where (select count(*) from quotes where id=investments.id and datetime>now()::date-%s)=0 and active=false and priorityhistorical[1]=%s;", (dias,  idpriority))   
        for row in cur:
            resultado.append(Investment(self.cfg).init__db_row(self.cfg, row))
        return resultado
        
    def find_ids(self):
        """Devuelve un array con los objetos de Investment que cumplen"""
        self.ids=[]
        for inv in self.cfg.activas():
            if inv.active==True: #Debe ser activa
                if len(inv.priority.arr)>0:
                    if inv.priority.arr[0].id==self.id_source: #Seleccion generica
                        #particularidades
                        if self.id_source==1 : #Caso de yahoo
                            if inv.yahoo!=None or inv.yahoo!='':#Comprueba que tiene yahoo
                                self.ids.append(inv)
                        else:
                                self.ids.append(inv)
#        print (len(self.ids))
        return self.ids        
        
    def find_ids_historical(self):
        """Función que busca todos los ids de las inversiones con priorityhistorical=id_source y que estén activas"""
        self.ids=[]
        for inv in self.cfg.activas():
            if inv.active==True: #Debe ser activa
                if len(inv.priorityhistorical.arr)>0:
                    if inv.priorityhistorical.arr[0].id==self.id_source: #Seleccion generica
                        #particularidades
                        if  self.id_source==3: #Caso de yahoo
                            if inv.yahoo!=None or inv.yahoo!='':#Comprueba que tiene yahoo
                                self.ids.append(inv)
                        else:
                                self.ids.append(inv)
        return self.ids

#        
#    def filtrar_ids(self, ids):
#        ids=self.filtrar_horario_bolsa(ids)
#        return ids
        
        
    def isin2id(self, isin,  id_bolsas):
        for i in self.cfg.activas:
            if isin==self.cfg.activas[i].isin and id_bolsas==self.cfg.activas[i].id_bolsas:
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
                con=self.cfg.connect_myquotesd()
                cur=con.cursor()
                status_update(cur, self.name, "Update quotes", status='Downloading error',  statuschange=datetime.datetime.now())
                con.commit()
                cur.close()
                self.cfg.disconnect_myquotesd(con)    
                time.sleep(60)
                return None
        else:
            return None
        con=self.cfg.connect_myquotesd()
        cur=con.cursor()
        self.internetquerys=self.internetquerys+1
        status_update(cur, self.name, "Update quotes", internets=self.internetquerys)
        con.commit()
        cur.close()
        self.cfg.disconnect_myquotesd(con)    
        return web

    def update_step_quotes(self, sql):
        """Hace un bucle con los distintos codes del sql."""
        con=self.cfg.connect_myquotesd()
        cur=con.cursor()
        status_insert(cur, self.name, "Update stepcode quotes")
        con.commit()
        cur.close()
        cfg.disconnect_myquotesd(con)   
        while True:
            time.sleep(self.time_before_quotes)
            con=self.cfg.connect_myquotesd()
            cur=con.cursor()
            cur2=con.cursor()
            status_update(cur, self.name, "Update step quotes", status='Working',  statuschange=datetime.datetime.now())
            con.commit()
            cur.execute(sql)
            for row in cur:
                if self.debug==True:
                    for i in self.arr_quote(row['code']):
                        print (i)
    #                log("S_SOCIETEGENERALEWARRANTS_STATICS", QApplication.translate("Core",("%d de %d" %(cur.rownumber, cur.rowcount)))
                else:
                    Quote(self.cfg).insert_cdtv(self.arr_quote(row['code']), self.name)
                status_update(cur2, self.name, "Update step quotes", status='Waiting step',  statuschange=datetime.datetime.now())
                con.commit()
                time.sleep(self.time_step_static)
            
            status_update(cur2, self.name, "Update step quotes", status='Waiting after',  statuschange=datetime.datetime.now())
            con.commit()
            cur.close()
            cur2.close()
            cfg.disconnect_myquotesd(con)    
            time.sleep( self.time_after_statics)
        
#        
#    def update_quotes(self):
#        con=self.cfg.connect_myquotesd()
#        cur=con.cursor()
#        status_insert(cur, self.name, "Update quotes")
#        status_update(cur, self.name, "Update quotes", status='Waiting before',  statuschange=datetime.datetime.now())
#        con.commit()
#        cur.close()
#        self.cfg.disconnect_myquotesd(con)   
#        time.sleep(self.time_before_quotes)      
#        while True:      
#            con=self.cfg.connect_myquotesd()
#            cur=con.cursor()
#            status_update(cur, self.name, "Update quotes", status='Working',  statuschange=datetime.datetime.now())
#            con.commit()
#            cur.close()
#            self.cfg.disconnect_myquotesd(con)    
#            if self.debug==True:
#                for i in self.arr_quotes():
#                    print (i)
#            else:
#                Quote(self.cfg).insert_cdtv(self.arr_quotes(), self.name)
#            con=self.cfg.connect_myquotesd()
#            cur=con.cursor()
#            status_update(cur, self.name, "Update quotes", status='Waiting after',  statuschange=datetime.datetime.now())
#            con.commit()
#            cur.close()
#            self.cfg.disconnect_myquotesd(con)               
#            time.sleep(self.time_after_quotes)


#    def update_statics(self):
#        con=self.cfg.connect_myquotesd()
#        cur=con.cursor()
#        status_insert(cur, self.name, "Update statics")
#        status_update(cur, self.name, "Update statics", status='Waiting before',  statuschange=datetime.datetime.now())
#        con.commit()
#        cur.close()
#        self.cfg.disconnect_myquotesd(con)   
#        time.sleep(self.time_before_statics)
#        while True:            
#            con=self.cfg.connect_myquotesd()
#            cur=con.cursor()
#            status_update(cur, self.name, "Update statics", status='Working',  statuschange=datetime.datetime.now())
#            con.commit()
#            cur.close()
#            self.cfg.disconnect_myquotesd(con)    
#            if self.debug==True:
#                for i in self.arr_statics():
#                    print (i)
#            else:
#                Investment(self.cfg).update_static(self.arr_statics(), self.name)
#            con=self.cfg.connect_myquotesd()
#            cur=con.cursor()
#            status_update(cur, self.name, "Update statics", status='Waiting after',  statuschange=datetime.datetime.now())
#            con.commit()
#            cur.close()
#            self.cfg.disconnect_myquotesd(con)                     
#            time.sleep(self.time_after_statics)
            
#    def update_step_statics(self, sql):
#        """Hace un bucle con los distintos codes del sql."""
#        con=self.cfg.connect_myquotesd()
#        cur=con.cursor()
#        status_insert(cur, self.name, "Update step statics")
#        status_update(cur, self.name, "Update step statics", status='Waiting before',  statuschange=datetime.datetime.now())
#        con.commit()
#        cur.close()
#        self.cfg.disconnect_myquotesd(con)    
#        time.sleep(self.time_before_statics)
#        while True:
#            con=self.cfg.connect_myquotesd()
#            cur=con.cursor()
#            cur2=con.cursor()
#            status_update(cur, self.name, "Update statics", status='Working',  statuschange=datetime.datetime.now())
#            con.commit()
#            cur.execute(sql)
#            for row in cur:
#                if self.debug==True:
#                    for i in self.arr_static(row['code']):
#                        print (i)
#    #                log("S_SOCIETEGENERALEWARRANTS_STATICS", QApplication.translate("Core",("%d de %d" %(cur.rownumber, cur.rowcount)))
#                else:
#                    Investment(self.cfg).update_static(self.arr_static(row['code']), self.name)
#
#                status_update(cur2, self.name, "Update step statics", status='Waiting step',  statuschange=datetime.datetime.now())    
#                con.commit()
#                time.sleep(self.time_step_static)
#
#            status_update(cur2, self.name, "Update step statics", status='Waiting after',  statuschange=datetime.datetime.now())                    
#            con.commit()
#            cur.close()
#            cur2.close()
#            self.cfg.disconnect_myquotesd(con)    
#            time.sleep( self.time_after_statics)
#            
#    def update_stepcode_statics(self, listcode):
#        """Hace un bucle con los distintos codes del listcode."""        
##        con=self.cfg.connect_myquotesd()
##        cur=con.cursor()
##        status_insert(cur, self.name, "Update stepcode statics")
##        status_update(cur, self.name, "Update stepcode statics", status='Waiting before',  statuschange=datetime.datetime.now())
##        con.commit()
##        cur.close()
##        self.cfg.disconnect_myquotesd(con)   
#        time.sleep(self.time_before_statics)
#        while True:
#            for code in listcode:
#                if self.debug==True:
#                    for i in self.arr_static(code):
#                        print (i)
#                else:
#                    Investment(self.cfg).update_static(self.arr_static(code), self.name)
#                time.sleep(self.time_step_static)
#            time.sleep( self.time_after_statics)
#
#    def update_step_historicals(self, listcodes):
#        con=self.cfg.connect_myquotesd()
#        cur=con.cursor()
#        status_insert(cur, self.name, "Update step historicals")
#        status_update(cur, self.name, "Update step historicals", status='Waiting before',  statuschange=datetime.datetime.now())
#        con.commit()
#        cur.close()
#        self.cfg.disconnect_myquotesd(con)   
#        time.sleep(self.time_before_historicals)
#        while True:
#            con=self.cfg.connect_myquotesd()
#            cur=con.cursor()
#            status_update(cur, self.name, "Update step historicals", status='Working',  statuschange=datetime.datetime.now())
#            con.commit()
#            cur.close()
#            self.cfg.disconnect_myquotesd(con)                
#            for code in listcodes:
##                print code,  listcodes
#                if self.debug==True:
#                    for i in self.arr_historical(code):
#                        print (i)
#                else:                
##                    print "Ha llegado"
#                    Quote(self.cfg).insert_cdtochlv(self.arr_historical(code, ''),  self.name)
#                con=self.cfg.connect_myquotesd()
#                cur=con.cursor()
#                status_update(cur, self.name, "Update step historicals", status='Waiting step',  statuschange=datetime.datetime.now())
#                con.commit()
#                cur.close()
#                self.cfg.disconnect_myquotesd(con)       
#                time.sleep(self.time_step_historical)
#
#            con=self.cfg.connect_myquotesd()
#            cur=con.cursor()
#            status_update(cur, self.name, "Update step historicals", status='Waiting after',  statuschange=datetime.datetime.now())
#            con.commit()
#            cur.close()
#            self.cfg.disconnect_myquotesd(con)                       
#            time.sleep(self.time_after_historicals)
#
#    def update_step_historicals_by_isin(self, sql):
#        """Sql debe devolver isin solamente"""
#        con=self.cfg.connect_myquotesd()
#        cur=con.cursor()
#        status_insert(cur, self.name, "Update step historicals by isin")
#        status_update(cur, self.name, "Update step historicals by isin", status='Waiting before',  statuschange=datetime.datetime.now())
#        con.commit()
#        cur.close()
#        self.cfg.disconnect_myquotesd(con)   
#        time.sleep(self.time_before_historicals)
#        while True:
#            con=self.cfg.connect_myquotesd()
#            cur=con.cursor()
#            status_update(cur, self.name, "Update step historicals", status='Working',  statuschange=datetime.datetime.now())
#            con.commit()            
#            cur.execute(sql)            
#            lista=[]
#            for i in cur:
#                lista.append(i['isin'])
#            cur.close()
#            self.cfg.disconnect_myquotesd(con)         
#            
#            for isin in lista:
#                yahoocode=self.isin2yahoocode(isin)
#                if yahoocode==None:
#                    time.sleep(self.time_step_historical)
#                else:
#    #                print code,  listcodes
#                    if self.debug==True:
#                        for i in self.arr_historical(yahoocode):
#                            print (i)
#                    else:                
#    #                    print "Ha llegado"
#                        Quote(self.cfg).insert_cdtochlv(self.arr_historical(yahoocode, isin),  self.name)                
#                    con=self.cfg.connect_myquotesd()
#                    cur=con.cursor()
#                    status_update(cur, self.name, "Update step historicals", status='Waiting step',  statuschange=datetime.datetime.now())
#                    con.commit()
#                    cur.close()
#                    self.cfg.disconnect_myquotesd(con)       
#                    time.sleep(self.time_step_historical)
#
#            con=self.cfg.connect_myquotesd()
#            cur=con.cursor()
#            status_update(cur, self.name, "Update step historicals", status='Waiting after',  statuschange=datetime.datetime.now())
#            con.commit()
#            cur.close()
#            self.cfg.disconnect_myquotesd(con)                          
#            time.sleep(self.time_after_historicals)

#    def update_step_dividends(self, sql):
##        con=self.cfg.connect_myquotesd()
##        cur=con.cursor()
##        status_insert(cur, self.name, "Update step dividends")
##        con.commit()
##        cur.close()
##        self.cfg.disconnect_myquotesd(con)   
#        return
#        
#    def update_dividends(self):   
#        con=self.cfg.connect_myquotesd()
#        cur=con.cursor()
#        status_insert(cur, self.name, "Update dividends")
#        status_update(cur, self.name, "Update dividends", status='Waiting before',  statuschange=datetime.datetime.now())
#        con.commit()
#        cur.close()
#        self.cfg.disconnect_myquotesd(con)    
#        time.sleep(self.time_before_dividends)        
#        while True:                   
#            con=self.cfg.connect_myquotesd()
#            cur=con.cursor()
#            status_update(cur, self.name, "Update dividends", status='Working',  statuschange=datetime.datetime.now())
#            con.commit()
#            cur.close()
#            self.cfg.disconnect_myquotesd(con)                     
#            Investment(self.cfg).update_dividends( self.arr_dividends(),  self.name)
#            con=self.cfg.connect_myquotesd()
#            cur=con.cursor()
#            status_update(cur, self.name, "Update dividends", status='Waiting after',  statuschange=datetime.datetime.now())
#            con.commit()
#            cur.close()
#            self.cfg.disconnect_myquotesd(con)                     
#            time.sleep(self.time_after_dividends)
#           
#           

    def filtrar_horario_bolsa(self, investments):
        if (datetime.datetime.now()-self.cfg.inittime).total_seconds()<120:#120: # Si acaba de arrancar
            return investments
            
        if datetime.datetime.now().weekday()>=5:         
            return []
#        now=datetime.time(datetime.datetime.utcnow().hour, datetime.datetime.utcnow().minute) 
        resultado=[]
        margen=datetime.timedelta(hours=1 )
        for inv in investments:
#            inv=self.cfg.activas(i)
#            bolsa=self.cfg.bolsas[str(self.cfg.activas[str(i)].id_bolsas)]
            now=datetime.datetime.now(pytz.timezone(inv.bolsa.zone))
            starts=now.replace(hour=inv.bolsa.starts.hour, minute=inv.bolsa.starts.minute, second=inv.bolsa.starts.second)
            stops=now.replace(hour=inv.bolsa.ends.hour, minute=inv.bolsa.ends.minute)+margen
#            print (starts, now, stops)
            if starts<now and stops>now:
                print ("metido")
                resultado.append(inv)
        return resultado
                


    def agrupations(self, isin, agrbase=[]):
        """agrbase es la agrupación base que se importa desde statics, por ejemplo EURONEXT o BMF"""
        agr=[]
        agr=agr+agrbase
        if isin in self.cfg.cac40:
            agr.append('CAC40')            
        if isin in self.cfg.eurostoxx:
            agr.append('EUROSTOXX')
        if isin in self.cfg.ibex:
            agr.append('IBEX35')
        if isin in self.cfg.nyse:
            agr.append('NYSE')
        if isin in self.cfg.dax:
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
        
    def yahoo2investment(self, yahoo, investments):
        for inv in investments:
            if inv.yahoo==yahoo:
                return inv
        return None
#
#    def yahoo_historical(self, code,  dbcode=''):
#        """If othercode se pone como code othercode, util cuando se busca por code de yahoo pero en la base de datos en deutchbore#de00000000"""
#        def fecha_ultimo_registro(code):
#            cfg=ConfigMQ()
#            con=cfg.connect_myquotesd()
#            cur = con.cursor()     
#            resultado=None
#            cur.execute("select max(date) as fecha from quotes where code=%s and last='close'", (code, ))
#            for i in cur:
#                resultado=i['fecha']
#            con.commit()    
#            cur.close()                
#            self.cfg.disconnect_myquotesd(con)
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

class Investment:
    def __init__(self, cfg):
        self.cfg=cfg
        self.name=None
        self.isin=None
        self.currency=None #Apunta a un objeto currency
        self.type=None
        self.agrupations=None #Es un objeto SetAgrupation
        self.active=None
        self.id=None
        self.web=None
        self.address=None
        self.phone=None
        self.mail=None
        self.tpc=None
        self.pci=None
        self.apalancado=None
        self.bolsa=None
        self.yahoo=None
        self.priority=None
        self.priorityhistorical=None
        self.comentario=None
        self.obsolete=None
        self.deletable=None
        self.system=None
        
        self.quotes=None#Variable en la que se almacena QuotesResult
        self.estimaciones={}#Es un diccionario que guarda objetos estimaciones con clave el año

    def __repr__(self):
        return "{0} ({1}) de la {2}".format(self.name , self.id, self.bolsa.name)
                
    def init__db_row(self, row):
        """row es una fila de un pgcursro de investmentes"""
        self.name=row['name']
        self.isin=row['isin']
        self.currency=self.cfg.currencies.find(row['currency'])
        self.type=self.cfg.types.find(row['type'])
        self.agrupations=SetAgrupations(self.cfg).init__create_from_dbstring(row['agrupations'])
        self.active=row['active']
        self.id=row['id']
        self.web=row['web']
        self.address=row['address']
        self.phone=row['phone']
        self.mail=row['mail']
        self.tpc=row['tpc']
        self.pci=row['pci']
        self.apalancado=self.cfg.apalancamientos.find(row['apalancado'])
        self.bolsa=self.cfg.bolsas.find(row['id_bolsas'])
        self.yahoo=row['yahoo']
        self.priority=SetPriorities(self.cfg).init__create_from_db(row['priority'])
        self.priorityhistorical=SetPrioritiesHistorical(self.cfg).init__create_from_db(row['priorityhistorical'])
        self.comentario=row['comentario']
        self.obsolete=row['obsolete']
        self.deletable=row['deletable']
        self.system=row['system']
        
        self.quotes=QuotesResult(self.cfg,self)
        return self
        
                
    def init__create(self, name,  isin, currency, type, agrupations, active, web, address, phone, mail, tpc, pci, apalancado, bolsa, yahoo, priority, priorityhistorical, comentario, obsolete, deletable, system, id=None):
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
        self.pci=pci
        self.apalancado=apalancado        
        self.bolsa=id_bolsas
        self.yahoo=yahoo
        self.priority=priority
        self.priorityhistorical=priorityhistorical
        self.comentario=comentario
        self.obsolete=obsolete
        self.deletable=deletable
        self.system=system
        
        self.quotes=QuotesResult(self.cfg,self)
        return self        

    def init__db(self, id):
        """Se pasa id porque se debe usar cuando todavía no se ha generado."""
        curmq=self.cfg.conmq.cursor()
        curmq.execute("select * from investments where id=%s", (id, ))
        row=curmq.fetchone()
        curmq.close()
        return self.init__db_row(row)
        
    def load_estimacion(self, year=None):
        """Si year es none carga todas las estimaciones de la inversionmq"""
        curmq=self.cfg.conmq.cursor()
        if year==None:
            year=datetime.date.today().year
        curmq.execute("select * from estimaciones where year=%s and id=%s", (year, self.id))
        if curmq.rowcount==0:        
            e=Estimacion().init__create(year, 0, datetime.date(2012, 7, 3), "Vacio por código", False, 0, self)
        else:
            e=Estimacion().init__db_row(curmq.fetchone(), self)
        self.estimaciones[str(e.year)]=e
        curmq.close()
        
    def save(self):
        """Esta función inserta una inversión manual"""
        """Los arrays deberan pasarse como parametros ARRAY[1,2,,3,] o None"""
        
        cur=self.cfg.conmq.cursor()
        if self.id==None:
            cur.execute(" select min(id)-1 from investments;")
            id=cur.fetchone()[0]
            cur.execute("insert into investments (id, name,  isin,  currency,  type,  agrupations,  active,  web, address,  phone, mail, tpc, pci,  apalancado, id_bolsas, yahoo, priority, priorityhistorical , comentario,  obsolete, system) values ({0}, '{1}', '{2}', '{3}', {4}, '{5}', {6}, '{7}', '{8}', '{9}', '{10}', {11}, '{12}', {13}, {14}, '{15}', {16}, {17}, '{18}', {19}, {20})".format(id, self.name,  self.isin,  self.currency.id,  self.type.id,  self.agrupations.dbstring(),  self.active,  self.web, self.address,  self.phone, self.mail, self.tpc, self.pci,  self.apalancado.id, self.bolsa.id, self.yahoo, self.priority.dbstring(), self.priorityhistorical.dbstring() , self.comentario, self.obsolete, False))
            self.id=id
        else:
            sql="update investments set name='{0}', isin='{1}',currency='{2}',type={3}, agrupations='{4}', active={5}, web='{6}', address='{7}', phone='{8}', mail='{9}', tpc={10}, pci='{11}', apalancado={12}, id_bolsas={13}, yahoo='{14}', priority={15}, priorityhistorical={16}, comentario='{17}', obsolete={18} where id={19}".format( self.name,  self.isin,  self.currency.id,  self.type.id,  self.agrupations.dbstring(),  self.active,  self.web, self.address,  self.phone, self.mail, self.tpc, self.pci,  self.apalancado.id, self.bolsa.id, self.yahoo, self.priority.dbstring(), self.priorityhistorical.dbstring() , self.comentario, self.obsolete,  self.id)
            cur.execute(sql)
        cur.close()
    
    def changeDeletable(ids,  deletable):
        """Modifica a deletable"""
        curmq=self.cfg.conmq.cursor()
        sql="update investments set deletable={0} where id in ({1})".format( deletable,  str(ids)[1:-1])
        curmq.execute(sql)
        curmq.close()
        
    def priority_change(self, cur):
        """Cambia la primera prioridad y la pone en último lugar, necesita un commit()"""
        idtochange=self.priority[0]
        self.priority.remove(idtochange)
        self.priority.append(idtochange)
        cur.execute("update investments set priority=%s", (str(self.priority)))
        
    def priorityhistorical_change(self):
        """Cambia la primera prioridad y la pone en último lugar"""
        idtochange=self.priorityhistorical[0]
        self.priorityhistorical.remove(idtochange)
        self.priorityhistorical.append(idtochange)
        cur.execute("update investments set priorityhistorical=%s", (str(self.priorityhistorical)))
        return


        
class QuotesSet:
    """Clase que agrupa quotes un una lista arr. Util para operar con ellas como por ejemplo insertar"""
    def __init__(self):
        self.arr=[]
    
    def save(self, curmq,  source):
        """Recibe con code,  date,  time, value, zone
            Para poner el dato en close, el valor de time debe ser None
            Devuelve una tripleta (insertado,buscados,modificados)
        """
        (insertados, buscados, modificados)=(0, 0, 0)
        if len(self.arr)==0:
            log("QUOTES",source,  QApplication.translate("Core","No se ha parseado nada"))
            return
            
        for p in self.arr:
            ibm=p.save(curmq)
            if ibm==0:
                buscados=buscados+1
            elif ibm==1:
                insertados=insertados+1
            elif ibm==2:
                modificados=modificados+1

        if insertados>0 or modificados>0:
            log("QUOTES" , source,  QApplication.translate("Core","Se han buscado %(b)d, modificado %(m)d e insertado %(i)d registros de %(c)s") %{"b":buscados, "m": modificados,   "i":insertados,  "c":source})
        #        return resultado
        
    def append(self, quote):
        self.arr.append(quote)
        
class Quote:
    """"Un quote no puede estar duplicado en un datetime solo puede haber uno"""
    def __init__(self, cfg):
        self.cfg=cfg
        self.investment=None
        self.quote=None
        self.datetime=None
        self.datetimeasked=None
        
    def __repr__(self):
        return "Quote de {0} de fecha {1} vale {2}".format(self.investment.name, self.datetime, self.quote)

        
    def init__create(self,  investment,  datetime,  quote):
        """Función que crea un Quote nuevo, con la finalidad de insertarlo"""
        self.investment=investment
        self.datetime=datetime
        self.quote=quote
        return self
        
    def exists(self, curmq):
        """Función que comprueba si existe en la base de datos y devuelve el valor de quote en caso positivo en una dupla"""     
        curmq.execute("select quote from quotes where id=%s and  datetime=%s;", (self.investment.id, self.datetime))
        if curmq.rowcount==0: #No Existe el registro
            return (False,  None)
        return (True,  curmq.fetchone()['quote'])
        
    def save(self, curmq):
        """Función que graba el quotes si coincide todo lo ignora. Si no coincide lo inserta o actualiza.
        No hace commit a la conexión
        Devuelve un número 1 si insert 2, update, 0  exisitia
        """
        
        exists=self.exists(curmq)
        if exists[0]==False:
            curmq.execute('insert into quotes (id, datetime, quote) values (%s,%s,%s)', ( self.investment.id, self.datetime, self.quote))
            return 1
        else:
            if exists[1]!=self.quote:
                curmq.execute("update quotes set quote=%swhere id=%s and datetime=%s", (self.quote, self.investment.id, self.datetime))
                return 2
            else:
                return 3
                
    def delete(self, curmq):
        curmq.execute("delete from quotes where id=%s and datetime=%s", (self.investment.id, self.datetime))

    def init__db_row(self, row, investment,   datetimeasked=None):
        """si datetimeasked es none se pone la misma fecha"""
        self.investment=investment
        self.quote=row['quote']
        self.datetime=row['datetime']
        if datetimeasked==None:
            self.datetimeasked=row['datetime']
        return self
        
        
    def init__from_query(self, curmq, investment, dt): 
        """Función que busca el quote de un id y datetime con timezone"""
        sql="select * from quote(%s, '%s'::timestamptz)" %(investment.id,  dt)
        curmq.execute(sql)
        return self.init__db_row(curmq.fetchone(), dt)
                
    def init__from_query_penultima(self,curmq,  investment,  lastdate=None):
        if lastdate==None:
            curmq.execute("select * from penultimate(%s)", (investment.id, ))
        else:
            curmq.execute("select * from penultimate(%s,%s)", (investment.id, lastdate ))
        return self.init__db_row(curmq.fetchone(), None)        
    def init__from_query_triplete(self, investment): 
        """Función que busca el last, penultimate y endlastyear de golpe
       Devuelve un array de Quote en el que arr[0] es endlastyear, [1] es penultimate y [2] es last
      Si no devuelve tres Quotes devuelve None y debera´a calcularse de otra forma"""
        curmq=self.cfg.conmq.cursor()
        endlastyear=dt(datetime.date(datetime.date.today().year -1, 12, 31), datetime.time(23, 59, 59), config.localzone)
        curmq.execute("select * from quote (%s, now()) union select * from penultimate(%s) union select * from quote(%s,%s) order by datetime", (investment.id, investment.id, investment.id,  endlastyear))
        if curmq.rowcount!=3:
            curmq.close()
            return None
        resultado=[]
        for row in  curmq:
            if row['datetime']==None: #Pierde el orden y no se sabe cual es cual
                curmq.close()
                return None
            resultado.append(Quote(self.cfg).init__db_row(row, investment))
        curmq.close()
        return resultado

class OCHL:
    def __init__(self, investment, datetime, open, close, high, low ):
        self.investment=investment
        self.datetime=datetime
        self.open=open
        self.close=close
        self.high=high
        self.low=low
        
    def get_interval(self, ochlposterior):
        """Calcula el intervalo entre dos ochl. El posteror es el que se pasa como par´ametro"""
        return ochlposterior.datetime-self.datetime
        
class QuotesGenOHCL:
    def __init__(self, mem):
        self.mem=mem
        
    def recalculateAllAndDelete(self):
        """REcalcula todo y borra los innecesarios"""
        cur=self.mem.con.cursor()
        cur.execute("select * from investments where type in (1,3,4,5) order by name")
        for row in cur:
            inv=Investment(self.cfg).init__db_row(self.mem, row)
            print (inv.name,  cur.rownumber, cur.rowcount)
            self.recalculateInvestmentDelete(inv, False)
        cur.close()
        
    def recalculateInvestmentDelete(self, investment, regenerate=False):
        self.recalculateInvestment(investment, regenerate)
        self.deleteUnnecesary(investment)
        
    def recalculateInvestment(self, investment,  regenerate=False):
        cur=self.mem.con.cursor()
        if regenerate==False:
            cur.execute("select distinct(datetime::date) from quotes where id=%s and open=false and low=false and close=false and high=false and important=false", (investment.id, ))
        else:
            cur.execute("select distinct(datetime::date) from quotes where id=%s", (investment.id, ))

        for row in cur:
            sys.stdout.write("\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b  - {0}/{1}: ".format(cur.rownumber, cur.rowcount) )
            sys.stdout.flush()
            self.recalculateInvestmentDay(investment, row[0])
        cur.close()
        
    def recalculateInvestmentDay(self, investment,  date):
        """Funci´on que recalcula los booleanos, partiendo del localconfig de la bolsa que pertenece
        """
        if investment.type not in (2, ):#Son intradia
            iniciodia=dt(date,datetime.time(0,0),investment.bolsa.zone)
            findia=dt(date,datetime.time(23,59,59), investment.bolsa.zone)
            cur=self.mem.con.cursor()
            cur.execute("select datetime,quote from quotes where id=%s and datetime>=%s and datetime<=%s order by datetime",(investment.id,iniciodia,findia))
            rows=cur.fetchall()
            if len(rows)>0:        
                firstdatetime=rows[0][0]
                lastdatetime=rows[len(rows)-1][0]        
                maxquote=-1
                maxdatetime=None
                minquote=10000000
                mindatetime=None
                for q in rows:
                    if q[1]>=maxquote:
                        maxquote=q[1]
                        maxdatetime=q[0]
                    if q[1]<=minquote:
                        minquote=q[1]
                        mindatetime=q[0]        
                cur.execute("update quotes set open=false, low=false, high=false, close=false where id=%s and datetime>=%s and datetime<=%s",(investment.id,iniciodia,findia))
                cur.execute("update quotes set open=true where id=%s and datetime=%s", (investment.id, firstdatetime))        
                cur.execute("update quotes set low=true where id=%s and datetime=%s", (investment.id, mindatetime))      
                cur.execute("update quotes set high=true where id=%s and datetime=%s", (investment.id, maxdatetime))      
                cur.execute("update quotes set close=true where id=%s and datetime=%s", (investment.id, lastdatetime))                        

                cur.close()                
                self.mem.con.commit()
            else:
                print ("No recalcula booleanos por no haber datos intradia")
    def deleteUnnecesary(self, investment):
        """Borra de una inversi´on los innecesarios de todas las fechas menos los ´ultimos 7 dias"""
        cur=self.mem.con.cursor()
        cur.execute("delete from quotes where open=false and low=false and high=false and close=false and important=false and id=%s and datetime::date< now()::date- interval '7 days'", (investment.id, ))
        self.mem.con.commit()
        cur.close()
    
        
class QuotesResult:
    """Función que consigue resultados de myquotes de un id pasado en el constructor"""
    def __init__(self,cfg,  investment):
        self.cfg=cfg
        self.investment=investment
        self.last=None
        self.lastdpa=None
        self.penultimate=None
        self.endlastyear=None
        self.limit=None
        self.year=[] #ordinados de forma inversa
        self.month=[]
        self.currentweek=None
        self.currentmonth=None
        self.currentyear=None
        self.several=[]
        self.all=[]
        self.ochlDaily=[]
    
    
    
    def hasBasic(self):
        """Función que devuelve si se han descargado datos básicos"""
        if self.last==None:
            return False
        return True
#    def hasAnalisis(self):
#        """Función que devuelve si se han descargado datos básicos"""
#        if len(self.year)==0:
#            return False
#        return True
    def hasAll(self):
        """Función que devuelve si se han descargado datos básicos"""
        if len(self.all)==0:
            return False
        return True
    
    def get_basic(self):
        """Función que calcula last, penultimate y lastdate y el lastdpa"""
#        inicio=datetime.datetime.now()
        curmq=self.cfg.conmq.cursor()
        triplete=Quote(self.cfg).init__from_query_triplete(self.investment)
        if triplete!=None:
            self.endlastyear=triplete[0]
            self.penultimate=triplete[1]
            self.last=triplete[2]
#            print ("Por triplete {0}".format(str(datetime.datetime.now()-inicio)))
        else:
            self.last=Quote(self.cfg).init__from_query(curmq,  self.investment,  datetime.datetime.now(pytz.timezone(config.localzone)))
            if self.last.datetime!=None: #Solo si hay last puede haber penultimate
                self.penultimate=Quote(self.cfg).init__from_query_penultima(curmq,  self.investment, dt_changes_tz(self.last.datetime, config.localzone).date())
            else:
                self.penultimate=Quote(self.cfg).init__create(self.investment, None, None)
            self.endlastyear=Quote(self.cfg).init__from_query(curmq,  self.investment,  datetime.datetime(datetime.date.today().year-1, 12, 31, 23, 59, 59, tzinfo=pytz.timezone('UTC')))
#            print ("Por tres consultad {0}".format(str(datetime.datetime.now()-inicio)))
        self.lastdpa=DividendoEstimacion.dpa(curmq, self.investment, datetime.date.today().year)
        curmq.close()


    
    def get_basic_in_all(self):
        """Función que calcula last, penultimate y lastdate y el lastdpa"""
        self.last=self.all[len(self.all)-1]
        #penultimate es el ultimo del penultimo dia localizado
        dtpenultimate=day_end(self.last.datetime-datetime.timedelta(days=1), self.investment.bolsa.zone)
        self.penultimate=self.find_quote_in_all(dtpenultimate)
        dtendlastyear=dt(datetime.date(self.last.datetime.year-1, 12, 31),  datetime.time(23, 59, 59), self.investment.bolsa.zone)
        self.endlastyear=self.find_quote_in_all(dtendlastyear)
#        self.lastdpa=DividendoEstimacion.dpa(curmq, self.investment, datetime.date.today().year)
        
#        
#    def get_analisis_from_all(self, curmq, limit):
#        """Función que calcula current..., year, month desde la fecha pasada como parámetro"""
#        self.iniciosemana=self.__find_quote_date(datetime.date.today()-datetime.timedelta(days=datetime.date.today().weekday()+1))
#        self.semana=self.__find_quote_date(datetime.date.today()-datetime.timedelta(7))
#        self.mes=self.__find_quote_date(datetime.date.today()-datetime.timedelta(30))
#        self.meses3=self.__find_quote_date(datetime.date.today()-datetime.timedelta(90))
#        self.meses6=self.__find_quote_date(datetime.date.today()-datetime.timedelta(180))
#        self.ano1=self.__find_quote_date(datetime.date.today()-datetime.timedelta(365))
#        self.inicioano=self.__find_quote_date(datetime.date(datetime.date.today().year-1, 12, 31))
#        self.ano2=self.__find_quote_date(datetime.date.today()-datetime.timedelta(365*2))
#        self.ano3=self.__find_quote_date(datetime.date.today()-datetime.timedelta(365*3))
#        self.ano4=self.__find_quote_date(datetime.date.today()-datetime.timedelta(365*4))
#        self.ano5=self.__find_quote_date(datetime.date.today()-datetime.timedelta(365*5))
#        self.ano10=self.__find_quote_date(datetime.date.today()-datetime.timedelta(365*10))
#        self.ano20=self.__find_quote_date(datetime.date.today()-datetime.timedelta(365*20))
#        self.ano30=self.__find_quote_date(datetime.date.today()-datetime.timedelta(365*30))      


    def get_intraday(self, curmq, date,  tzinfo):
        """Función que devuelve un array ordenado de objetos Quote"""
        resultado=[]
        iniciodia=dt(date, datetime.hour(0, 0), tzinfo)
        siguientedia=iniciodia+datetime.timedelta(days=1)
        curmq.execute("select * from quotes where id=%s and datetime>=%s and datetime<%s order by datetime", (self.investment.id,  iniciodia, siguientedia))
        for row in curmq:
            resultado.append(Quote(self.cfg).init__db_row(row,  self.investment))
        return resultado
            
                
    def __find_ochlDiary_since_date(self, date):
        resultado=[]
        date=datetime.datetime(date.year, date.month, date.day)
        for d in self.ochlDaily:
            if d[0]>=date:
                resultado.append(d)
        return resultado
                    
            
    def __first(self, interval, dt):
        """Función que devuelve un first redondeado trabaja con utc aunque no lo tiene"""
        if interval==datetime.timedelta(days=1):
            return datetime.datetime(dt.year, dt.month, dt.day, 0, 0, 0, 0, pytz.timezone(config.localzone))
        elif interval==datetime.timedelta(days=7):
            dt=datetime.datetime(dt.year, dt.month, dt.day, 0, 0, 0, 0, pytz.timezone(config.localzone))
            while dt.weekday()!=0:
                dt=dt-datetime.timedelta(days=1)
            return dt
        elif interval==datetime.timedelta(days=30):
            return datetime.datetime(dt.year, dt.month, 1, 0, 0, 0, 0, pytz.timezone(config.localzone))
        elif interval==datetime.timedelta(days=365):
            return datetime.datetime(dt.year, 1, 1, 0, 0, 0, 0, pytz.timezone(config.localzone))
                
    def __last(self, interval, dt):
        """Función que devuelve un first redondeado"""
        if interval==datetime.timedelta(days=1):
            return datetime.datetime(dt.year, dt.month, dt.day, 0, 0, 0, 0, pytz.timezone(config.localzone))+interval
        elif interval==datetime.timedelta(days=7):
            return self.__first(interval, dt)+datetime.timedelta(days=7)
        elif interval==datetime.timedelta(days=30):
            sumomes=datetime.datetime(dt.year, dt.month, 1, 0, 0, 0, 0, pytz.timezone(config.localzone))+datetime.timedelta(days=31)
            return sumomes.replace(day=1)
        elif interval==datetime.timedelta(days=365):
            sumoano=datetime.datetime(dt.year, 1, 1, 0, 0, 0, 0, pytz.timezone(config.localzone))+datetime.timedelta(days=366)
            return sumoano.replace(day=1).replace(month=1)
        
    def __find_ochl_date(self, date):
        for i in range(len(self.ochlDaily)-1,  -1, -1):
            if self.ochlDaily[i][0]<=date:
                return {"date":self.ochlDaily[i][0],  "open":self.ochlDaily[i][1],  "high":self.ochlDaily[i][3],  "low":self.ochlDaily[i][4],  "close":self.ochlDaily[i][2],  "volumen":self.ochlDaily[i][5]}
        return None
        
    def find_quote_in_all(self, datetime):
        return self.all[self.get_all_position(datetime)]

        
    def get_intraday_from_all(self, date, tzinfo):        
        """Función que devuelve un array ordenado de objetos Quote"""
        resultado=[]
        iniciodia=dt(date, datetime.time(0, 0),   tzinfo)
        siguientedia=iniciodia+datetime.timedelta(days=1)
        for i in range(self.get_all_position(iniciodia), len(self.all)):
            if self.all[i].datetime>=iniciodia and self.all[i].datetime<siguientedia:
                resultado.append(self.all[i])
        return resultado

    def decimalesSignificativos(self):
        """ESta función busca en quotes_basic para calcular los bits significativos de los quotes, para poder mostrarlos mejor"""
        resultado=2
        if self.last==None or self.penultimate==None or self.endlastyear==None:
#            print ("mal",  resultado)
            return resultado
        
        for num in [self.last.quote, self.penultimate.quote, self.endlastyear.quote]:
            decimales=str(num).split(".")
            if len(decimales)==2:
                cadena=decimales[1]
                while len(cadena)>=2:
                    if cadena[len(cadena)-1]=="0":
                        cadena=cadena[:-1]
                    else:
                        resultado=len(cadena)
                        break
#        print ("significativos",  self.last.quote,  self.penultimate.quote,  self.endlastyear.quote,  resultado)
        return resultado

    def get_all_position(self,  dattime):
        """Saca la posición en el array all, en el que se encuentra el datetime
        dattime tiene pytz"""
        if len(self.all)<2:#Si es 0,1 o 2 que lo recorra
            return 0
        for i,  q in enumerate(self.all):
            if q.datetime==dattime:
                return i
            elif q.datetime>dattime:
                return i-1
        return 0
        
        
    def get_all(self, curmq):
        """Función que devuelve un array ordenado de objetos Quote
        actualiza o carga todo seg´un haya registros
        Actualiza get_basic_in_all
        """
        inicio=datetime.datetime.now()
        if len(self.all)==0:
            curmq.execute("select * from quotes where id=%s order by datetime;", (self.investment.id, ))
        else:
            curmq.execute("select * from quotes where id=%s and datetime>%s order by datetime;", (self.investment.id, self.all[len(self.all)-1].datetime))
        for row in curmq:
            self.all.append(Quote(self.cfg).init__db_row(row,  self.investment))
        print ("Descarga de {0} datos: {1}".format(curmq.rowcount,   datetime.datetime.now()-inicio))
        self.get_basic_in_all()
        
    def calculate_ochl_diary(self):
        """Este el que se calcula por defecto, el resto se calcula a partir de este"""            
        def to_ochl(  quot, puntdt):
            if len(quot)==0:
                return None
            dt=puntdt#siempre debe ser un datetime para matplotlib
            open=quot[0]
            close=quot[len(quot)-1]
            high=max(quot)
            low=min(quot)
            return OCHL(self.investment, dt, open, close, high, low )



        if len(self.all)==0:
            return []
        inicio=datetime.datetime.now()
        interval=datetime.timedelta(days=1)
        self.ochlDaily=[]
        first=self.__first(interval, self.all[0].datetime)
        last=self.__last(interval, self.all[len(self.all)-1].datetime)
        puntdt=first#puntero datetime
        pudb=0#puntero db desde el que leer
#        parsed=0
        while puntdt<=last:
            tmpQuot=[]
            newpunt=puntdt+interval
            for i in range (pudb, len(self.all)):
                if self.all[i].datetime>=newpunt:
                    break
                tmpQuot.append(self.all[i].quote)
#                parsed=parsed+1
                pudb=i+1

            o=to_ochl( tmpQuot, puntdt)
            if o!=None:
                self.ochlDaily.append(o)
            puntdt=newpunt
        print ("Calculo de ochlDiario con {0} datos: {1}".format(len(self.all),   datetime.datetime.now()-inicio))

    def __calculate_ochl_from_ochlDaily(self, interval):
        """Este el que se calcula por defecto, el resto se calcula a partir de este"""
#   
#        def to_ochl(  quot, puntdt):
#            if len(quot)==0:
#                return None
#            dt=puntdt#siempre debe ser un datetime para matplotlib
#            open=quot[0]
#            close=quot[len(quot)-1]
#            high=max(quot)
#            low=min(quot)
#            return OCHL(self.investment, dt, open, close, high, low )

        def to_ochl_from_ochl(  ochl, puntdt):
            if len(ochl)==0:
                return None
#            datetimes, open,  close, high, low, volumen=zip(*ochl)
#            dt=puntdt#siempre debe ser un datetime para matplotlib
            open=ochl[0].open
            close=ochl[len(ochl)-1].close
            ma=max(ochl,key=lambda o: o.high) 
            mi=min(ochl,key=lambda o: o.low) 
            return OCHL(self.investment, puntdt, open, close, ma.high, mi.low)



        def __next(puntdt, interval):
            """Función que devuelve la suma del siguiente intervale"""
            if interval==datetime.timedelta(days=7): #Saca el siguiente lunes
                return puntdt+interval #solo suma ya que puntdt viene lkos lunes
            elif interval==datetime.timedelta(days=30):
                return (puntdt+datetime.timedelta(days=31)).replace(day=1)
            elif interval==datetime.timedelta(days=365):
                return puntdt.replace(year=puntdt.year+1)
        ## def generate_ochl_from_ochl
        if len(self.ochlDaily)==0:
            return []
            
        resultado=[]
        first=self.__first(interval, self.ochlDaily[0].datetime)
        last=self.__last(interval, self.ochlDaily[len(self.ochlDaily)-1].datetime)
        puntdt=first#puntero datetime
        pudb=0#puntero db desde el que leer
#        parsed=0
        while puntdt<=last:
            tmpQuot=[]
            newpunt=__next(puntdt, interval)
            for i in range (pudb, len(self.ochlDaily)):
                if self.ochlDaily[i].datetime>=newpunt:
                    break
                tmpQuot.append(self.ochlDaily[i])
#                parsed=parsed+1
                pudb=i+1

            o=to_ochl_from_ochl( tmpQuot, puntdt)
            if o!=None:
                resultado.append(o)
            puntdt=newpunt
#            print ("Han quedado sin parsear ",  len(self.ochlDaily)-parsed)
        return resultado            
  
        
        
    def get_dpa(self, curmq, year):
        """Busca el dpa y lo amacena en dpa"""
        return DividendoEstimacion.dpa(cur2, self.investment.id, year)

    def tpc_diario(self):
        if self.hasBasic():
            if self.penultimate.quote==None or self.penultimate.quote==0 or self.last.quote==None:
                return None
            else:
                return round((self.last.quote-self.penultimate.quote)*100/self.penultimate.quote, 2)
            
    def ochlWeekly(self):
        return self.__calculate_ochl_from_ochlDaily(datetime.timedelta(days=7))
    def ochlMonthly(self):
        return self.__calculate_ochl_from_ochlDaily(datetime.timedelta(days=30))
    def ochlYearly(self):
        return self.__calculate_ochl_from_ochlDaily(datetime.timedelta(days=365))
            
    def tpc_anual(self):
        if self.hasBasic():
            if self.endlastyear.quote==None or self.endlastyear.quote==0 or self.last.quote==None:
                return None
            else:
                return round((self.last.quote-self.endlastyear.quote)*100/self.endlastyear.quote, 2)       
    
    def tpc_dpa(self):
        """Calcula el tpc del dpa del utlimo año lastdpa"""
        if self.hasBasic():
            if self.lastdpa!=None and self.last.quote!=None and self.last.quote!=0:
                return 100*self.lastdpa/self.last.quote
            else:
                return None    





class Apalancamiento:
    def __init__(self, cfg):
        self.id=None
        self.name=None
    def init__create(self, id, name):
        self.id=id
        self.name=name
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
    def __init__(self,  cfg):
        self.cfg=cfg
        self.id=None
        self.name=None
        self.type=None
        self.bolsa=None

        
    def init__create(self, id,  name, type, bolsa):
        self.id=id
        self.name=name
        self.type=type
        self.bolsa=bolsa
        return self
        
class SetTypes:
    def __init__(self, cfg):
        self.cfg=cfg
        self.dic_arr={}
        
            
    def load_all(self):
        self.dic_arr["1"]=Type().init__create(1,QApplication.translate("Core","Acciones"))
        self.dic_arr["2"]=Type().init__create(2,QApplication.translate("Core","Fondos de inversión"))
        self.dic_arr["3"]=Type().init__create(3,QApplication.translate("Core","índices"))
        self.dic_arr["4"]=Type().init__create(4,QApplication.translate("Core","ETFs"))
        self.dic_arr["5"]=Type().init__create(5,QApplication.translate("Core","Warrants"))
        self.dic_arr["6"]=Type().init__create(6,QApplication.translate("Core","Divisas"))
        self.dic_arr["7"]=Type().init__create(7,QApplication.translate("Core","Deuda Pública"))
        self.dic_arr["8"]=Type().init__create(8,QApplication.translate("Core","Planes de pensiones"))
        self.dic_arr["9"]=Type().init__create(9,QApplication.translate("Core","Deuda Privada"))
        self.dic_arr["10"]=Type().init__create(10,QApplication.translate("Core","Depósitos"))
        self.dic_arr["11"]=Type().init__create(11,QApplication.translate("Core","Cuentas bancarias"))


    def list(self):
        return dic2list(self.dic_arr)

    def find(self, id):
        return self.dic_arr[str(id)]        
        
    def investments(self):
        return {k:v for k,v in self.dic_arr.items() if k in ("1", "2", "4", "5", "7","8")}


class ConfigMQ:
    def __init__(self):
        self.user=None
        self.db=None
        self.port=None
        self.server=None
        self.password=None
        self.consqlite=None#Update internetquery fro Process
        self.cac40=set([])
        self.dax=set([])
        self.eurostoxx=set([])
        self.ibex=set([])
        self.nyse=set([])
        self.debug=False
        self.inifile=os.environ['HOME']+ "/.myquotes/myquotes.cfg"
        self.inittime=datetime.datetime.now()#Tiempo arranca el config
        self.dbinitdate=None#Fecha de inicio bd.
        self.dic_activas={}#Diccionario cuyo indice es el id de la inversión id['1'] corresponde a la IvestmenActive(1) #se usa en myquotesd
        
        self.conmq=None#Conexión a myquotes
        self.countries=SetCountries(self)
        self.bolsas=SetBolsas(self)
        self.currencies=SetCurrencies(self)
        self.types=SetTypes(self)
        self.agrupations=SetAgrupations(self)
        self.apalancamientos=SetApalancamientos(self)
        self.priorities=SetPriorities(self)
        self.prioritieshistorical=SetPrioritiesHistorical(self)
        self.zones=SetZones(self)
        
        
        
    def actualizar_memoria(self):
        ###Esto debe ejecutarse una vez establecida la conexi´on
        print ("Cargando ConfigMQ")
        self.countries.load_all()
        self.currencies.load_all()
        self.priorities.load_all()
        self.prioritieshistorical.load_all()
        self.types.load_all()
        self.bolsas.load_all_from_db()
        self.agrupations.load_all()
        self.apalancamientos.load_all()
        self.zones.load_all()



    def connect_myquotesd(self):        
        strcon="dbname='%s' port='%s' user='%s' host='%s' password='%s'" % (config.dbname,  config.port, config.user, config.host,  config.password)
        while True:
            try:
                con=psycopg2.extras.DictConnection(strcon)
                return con
            except psycopg2.Error:
                print ("Error en la conexion, esperando 10 segundos")
                time.sleep(10)

    def disconnect_myquotesd(self, con):
        con.close()

    def connect_myquotes(self):        
        strmq="dbname='%s' port='%s' user='%s' host='%s' password='%s'" % (self.db,  self.port, self.user, self.server,  self.password)
        try:
            mq=psycopg2.extras.DictConnection(strmq)
            return mq
        except psycopg2.Error:
            m=QMessageBox()
            m.setText(QApplication.translate("Config","Error en la conexión, vuelva a entrar"))
            m.exec_()
            sys.exit()

    def disconnect_myquotes(self,  mq):
        mq.close()
    
    def carga_ia(self, cur,  where=""):
        """La variable where sera del tipo:
        where="where priority=5"""
        cur.execute("select * from investments {0}".format(where))
        for row in cur:
            self.dic_activas[str(row['id'])]=Investment(self.cfg).init__db_row(self, row)
            

    def activas(self, id=None):
        if id==None:
            return dic2list(self.dic_activas)
        else:
            return self.dic_activas[str(id)]
                        

            
class ConfigXulpy(ConfigMQ):
    def __init__(self):
        ConfigMQ.__init__(self)
        self.con=None#Conexión a xulpymoney
        self.inifile=os.environ['HOME']+ "/.xulpymoney/xulpymoney.cfg"
        
    def __del__(self):
        self.disconnect_myquotes(self.conmq)
        self.disconnect_xulpymoney(self.con)
        



    def actualizar_memoria(self):
        """Solo se cargan datos  de myquotes y operinversiones en las activas
        Pero se general el InversionMQ de las inactivas
        Se vinculan todas"""
        super(ConfigXulpy, self).actualizar_memoria()
        inicio=datetime.datetime.now()
        print ("Cargando estáticos")
        self.tiposoperaciones=SetTiposOperaciones(self)
        self.tiposoperaciones.load()
        self.conceptos=SetConceptos(self, self.tiposoperaciones)
        self.conceptos.load_from_db()
        self.localcurrency=self.currencies.find(config.localcurrency) #Currency definido en config
        self.indicereferencia=Investment(self).init__db( config.indicereferencia)
        self.indicereferencia.quotes.get_basic()
        print(datetime.datetime.now()-inicio)
        

        
    def connect_xulpymoney(self):        
        strcon="dbname='%s' port='%s' user='%s' host='%s' password='%s'" % (self.db,  self.port, self.user, self.server,  self.password)
        try:
            con=psycopg2.extras.DictConnection(strcon)
        except psycopg2.Error:
            m=QMessageBox()
            m.setText(QApplication.translate("Config","Error en la conexión a xulpymoney, vuelva a entrar"))
            m.exec_()        
            sys.exit()
        return con
        
    def disconnect_xulpymoney(self, con):
        con.close()
 
    def connect_myquotes(self):        
        strmq="dbname='%s' port='%s' user='%s' host='%s' password='%s'" % (config.dbname,  config.port, config.user, config.host,  config.password)
        try:
            mq=psycopg2.extras.DictConnection(strmq)
        except psycopg2.Error:
            m=QMessageBox()
            m.setText(QApplication.translate("Config","Error en la conexión a myquotes, vuelva a entrar"))
            m.exec_()        
            sys.exit()
        return mq
        
    def disconnect_myquotes(self,  mq):
        mq.close()

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
        else:
            return QPixmap(":/xulpymoney/star.gif")
            
class Global:
    def __init__(self, cfg):
        self.cfg=cfg
    def get_database_version(self):
        cur=self.cfg.conmq.cursor()
        cur.execute("select value from globals where id_globals=1;")
        resultado=cur.fetchone()['value']
        cur.close()
        return resultado

    def get_database_init_date(self):
        cur=self.cfg.conmq.cursor()
        cur.execute("select value from globals where id_globals=5;")
        resultado=cur.fetchone()['value']
        cur.close()
        return resultado

    def get_session_counter(self):
        cur=self.cfg.conmq.cursor()
        cur.execute("select value from globals where id_globals=3;")
        resultado=cur.fetchone()['value']
        cur.close()
        return resultado

    def get_system_counter(self):
        cur=self.cfg.conmq.cursor()
        cur.execute("select value from globals where id_globals=2;")
        resultado=cur.fetchone()['value']
        cur.close()
        return resultado

    def set_database_init_date(self, valor):
        cur=self.cfg.conmq.cursor()
        cur.execute("update globals set value=%s where id_globals=5;", (valor, ))
        cur.close()

    def set_database_version(self, valor):
        cur=self.cfg.conmq.cursor()
        cur.execute("update globals set value=%s where id_globals=1;", (valor, ))
        cur.close()

    def set_session_counter(self, valor):
        cur=self.cfg.conmq.cursor()
        cur.execute("update globals set value=%s where id_globals=3;", (valor, ))
        cur.close()

    def set_system_counter(self, valor):
        cur=self.cfg.conmq.cursor()
        cur.execute("update globals set value=%s where id_globals=2;", (valor, ))
        cur.close()
    
    def set_sourceforge_version(self):
        cur=self.cfg.conmq.cursor()
        try:
            serverversion=""
            comand='http://myquotes.svn.sourceforge.net/viewvc/myquotes/libxulpymoney.py'
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
        cur=self.cfg.conmq.cursor()
        cur.execute("select value from globals where id_globals=4;")
        resultado=cur.fetchone()['value']
        cur.close()
        return resultado


class Zone:
    def __init__(self, cfg):
        self.cfg=cfg
        self.name=None
        
class SetZones:
    def __init__(self, cfg):
        self.cfg=cfg
        self.dic_arr={}
        
    def load_all(self):
        self.dic_arr["Europe/Madrid"]=Type().init__create(1,'Europe/Madrid')

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
    tzt=pytz.timezone(tztarjet)
    tarjet=tzt.normalize(dt.astimezone(tzt))
    return tarjet

    
def list_loadprops(file,  section,  name):
    """Carga una section name parseada con strings y separadas por | y devuelve un arr"""
    config = configparser.ConfigParser()
    config.read(file)
    try:
        cadena=config.get(section, name )
#        print cadena.split("|")
        return cadena.split("|")
    except:
        print ("No hay fichero de configuración")
        return []

def list_saveprops(file, section,  name,  list):
    """Graba una cadena en formato str|str para luego ser parseado en lista"""
    config = configparser.ConfigParser()
    config.read(file)
#    print config.has_section(section)
    if config.has_section(section)==False:
        config.add_section(section)
    cadena=""
    for item in list:
        cadena=cadena+str(item)+'|'
#        config.remove_option(section, (table.objectName())+'_column'+str(i))
    config.set(section,  name,  cadena[:-1])
    # Writing our configuration file to 'example.cfg'
    with open(file, 'w') as configfile:
        config.write(configfile)

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



def qdatetime(dt, pixmap=True):
    """dt es un datetime con timezone
    dt, tiene timezone, 
    Convierte un datetime a string, teniendo en cuenta los microsehgundos, para ello se convierte a datetime local
    SE PUEDE OPTIMIZAR
    No hace falta cambiar antes a dt con local.config, ya que lo hace la función
    """
    if dt==None:
        resultado="None"
    else:    
        dt=dt_changes_tz(dt,  config.localzone)#sE CONVIERTE A LOCAL DE dt_changes_tz 2012-07-11 08:52:31.311368-04:00 2012-07-11 14:52:31.311368+02:00
        if dt.microsecond==4 or (dt.hour==23 and dt.minute==59 and dt.second==59):
            resultado=str(dt.date())
        elif dt.second>0:
            resultado=str(dt.date())+" "+str(dt.hour).zfill(2)+":"+str(dt.minute).zfill(2)+":"+str(dt.second).zfill(2)
        else:
            resultado=str(dt.date())+" "+str(dt.hour).zfill(2)+":"+str(dt.minute).zfill(2)   
    a=QTableWidgetItem(resultado)
    if dt==None:
        a.setTextColor(QColor(0, 0, 255))
    a.setTextAlignment(Qt.AlignVCenter|Qt.AlignRight)
    return a

def log(tipo, funcion,  mensaje):
    """Tipo es una letra mayuscula S sistema H historico D diario"""
    if funcion!="":
        funcion= funcion + " "
    f=codecs.open("/tmp/myquotes.log",  "a", "utf-8-sig")
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


def qcombobox_loadapalancamiento(combo, arr):
    """Carga entidades bancarias en combo"""
    arr=sorted(arr, key=lambda a: a.name,  reverse=False) 
    for a in arr:
        combo.addItem(a.name, a.id)       

def qcombobox_loadtypes(combo, arr):
    """Carga entidades bancarias en combo"""
    arr=sorted(arr, key=lambda a: a.name,  reverse=False) 
    for a in arr:
        combo.addItem(a.name, a.id)        

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

def dic2list(dic):
    """Función que convierte un diccionario pasado como parametro a una lista de objetos"""
    resultado=[]
    for k,  v in dic.items():
        resultado.append(v)
    return resultado

def dt(date, hour, zone):
    """Función que devuleve un datetime con zone info"""    
    z=pytz.timezone(zone)
    a=datetime.datetime(date.year,  date.month,  date.day,  hour.hour,  hour.minute,  hour.second, hour.microsecond)
    a=z.localize(a)
    return a

        
def s2pd(s):
    """python string isodate 2 python datetime.date"""
    a=str(s).split(" ")[0]#por si viene un 2222-22-22 12:12
    a=str(s).split("-")
    return datetime.date(int(a[0]), int(a[1]),  int(a[2]))
    

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

def qcenter(string):
    a=QTableWidgetItem((string))
    a.setTextAlignment(Qt.AlignVCenter|Qt.AlignCenter)
    return a

def qright(string):
    a=QTableWidgetItem((string))
    a.setTextAlignment(Qt.AlignVCenter|Qt.AlignRight)
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
