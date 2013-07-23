import sys,  os,  datetime,  threading
from decimal import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
version="0.2"
sys.path.append("/etc/xulpymoney")
import config
sys.path.append(config.myquoteslib)
from libmyquotes import *

class ConfigXulpy(ConfigMQ):
    def __init__(self):
        ConfigMQ.__init__(self)
        self.con=None#Conexión a xulpymoney
        self.conmq=None#Conexión a myquotes
        self.inifile=os.environ['HOME']+ "/.xulpymoney/xulpymoney.cfg"
        
    def __del__(self):
        self.disconnect_myquotes(self.conmq)
        self.disconnect_xulpymoney(self.con)
        



    def actualizar_memoria(self, cur, curmq):
        """Solo se cargan datos  de myquotes y operinversiones en las activas
        Pero se general el InversionMQ de las inactivas
        Se vinculan todas"""
        super(ConfigXulpy, self).actualizar_memoria(curmq)
        inicio=datetime.datetime.now()
        print ("Cargando estáticos")
        self.tiposoperaciones=SetTiposOperaciones(self)
        self.tiposoperaciones.load()
        self.conceptos=SetConceptos(self, self.tiposoperaciones)
        self.conceptos.load_from_db()
        self.localcurrency=self.currencies(config.localcurrency) #Currency definido en config
        self.indicereferencia=Investment().init__db(self,  curmq, config.indicereferencia)
        self.indicereferencia.quotes.get_basic(curmq)
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
        curmq2=self.cfg.conmq.cursor()
        cur.execute(sql)#"Select distinct(myquotesid) from inversiones"
        
        ##Conviert cur a lista separada comas
        lista=""
        for row in cur:
            lista=lista+ str(row['myquotesid']) + ", "
        lista=lista[:-2]
        
        ##Carga los investments
        curmq.execute("select * from investments where id in ("+lista+")" )
        for rowmq in curmq:
            inv=Investment().init__db_row(self.cfg, rowmq)
            inv.load_estimacion(curmq2)
            inv.quotes.get_basic(curmq2)
            self.arr.append(inv)
            sys.stdout.write("\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\bInvestment {0}/{1}: ".format(curmq.rownumber, curmq.rowcount) )
            sys.stdout.flush()
        cur.close()
        curmq.close()
        curmq2.close()
                           
    def find(self, id):
        for a in self.arr:
            if a.id==id:
                return a
        
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
            c=Cuenta().init__db_row(self.cfg, row, self.ebs.find(row['id_entidadesbancarias']))
            c.saldo_from_db(cur2)
            self.arr.append(c)
        cur.close()
        cur2.close()
                               
    def find(self, id):
        for a in self.arr:
            if a.id==id:
                return a
                
    def sort(self):
        self.arr=sorted(self.arr, key=lambda c: c.name,  reverse=False)         
    
    
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
                    sioh.arr.append(InversionOperacionHistorica(self.cfg).init__create(ioa, io.inversion, ioa.datetime.date(), -ioa.acciones*io.valor_accion, io.tipooperacion, -ioa.acciones, 0, 0, io.datetime.date(), ioa.valor_accion, io.valor_accion))
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
        quote=Quote().init__from_query(curmq, self.cfg.indicereferencia, self.datetime)
        if quote==None:
            self.referenciaindice= Quote().init__create(self.cfg.indicereferencia, self.datetime, 0)
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
    def __init__(self):
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
        
    def init__db_row(self, cfg,  row, eb):
        self.id=row['id_cuentas']
        self.name=row['cuenta']
        self.eb=eb
        self.activa=row['cu_activa']
        self.numero=row['numerocuenta']
        self.currency=cfg.currencies(row['currency'])
        return self
    
    def saldo_from_db(self,cur,  fecha=None):
        """Función que calcula el saldo de una cuenta
        Solo asigna saldo al atributo saldo si la fecha es actual, es decir la actual
        Parámetros:
            - pg_cursor cur Cursor de base de datos
            - datetime.date fecha Fecha en la que calcular el saldo
        Devuelve:
            - Decimal saldo Valor del saldo
        """
        
        if fecha==None:
            fecha=datetime.date.today()
        cur.execute('select sum(importe)  from opercuentas where id_cuentas='+ str(self.id) +" and fecha<='"+str(fecha)+"';") 
        saldo=cur.fetchone()[0]
        if saldo==None:
            return 0        
        if fecha==datetime.date.today():
            self.saldo=saldo
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

    def transferencia(self, cur,  fecha,  cuentaorigen,  cuentadestino, importe, comision ):
        """Cuenta origen y cuenta destino son objetos cuenta"""
        sql="select transferencia('"+str(fecha)+"', "+ str(cuentaorigen.id) +', ' + str(cuentadestino.id)+', '+str(importe) +', '+str(comision)+');'
        cur.execute(sql)
        cuentaorigen.saldo_from_db(cur)
        cuentadestino.saldo_from_db(cur)
        
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
            quote=Quote().init__from_query(curmq, self.mq, day_end_from_date(fecha, config.localzone))
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
        mq=self.cfg.connect_myquotes()
        curmq=mq.cursor()       
        self.cfg.indicereferencia.quotes.get_basic(curmq)
#        for k, v in self.cfg.dic_mqinversiones.items():
#            v.quotes.get_basic(curmq)
        curmq.close()
        self.cfg.disconnect_myquotes(mq)

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

def qcombobox_loadcuentas(combo, cuentas):
    """Función que carga en un combo pasado como parámetro y con un SetCuentas pasado como parametro
        Se ordena por nombre""" 
    cuentas.sort()
    for cu in cuentas.arr:
        combo.addItem(cu.name, cu.id)
        

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
