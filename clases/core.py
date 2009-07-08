#-*- coding: UTF-8 -*- 
import sys,  os
sys.path.append("/usr/local/lib/cuentas/")
import datetime,  math
import adodb
import config
from fecha import *
from formato import *  
from xul import *

class Banco:
    
  
    def saldo(self,id_entidadesbancarias,fecha):
        curs = con.Execute('select banco_saldo('+ str(id_entidadesbancarias) + ",'"+fecha+"') as saldo;"); 
        if curs == None: 
            print self.cfg.con.ErrorMsg()        
        row = curs.GetRowAssoc(0)      
        curs.Close()
        return row['saldo']

    def xultree(self, inactivas,  fecha):
        if inactivas==True:
            sql="select * from entidadesbancarias order by entidadesbancaria";
        else:
            sql="select * from entidadesbancarias where eb_activa='t' order by entidadesbancaria";
        curs=con.Execute(sql)
        
        s= '<popupset>\n'
        s= s+ '   <popup id="treepopup" >\n'
        s= s+ '      <menuitem label="Nuevo Banco" oncommand="location=\'cuentas_ibm.psp?ibm=insertar&amp;regresando=0;\'" class="menuitem-iconic"  image="images/item_add.png"/>\n'
        s= s+ '      <menuitem label="Modificar Banco"  oncommand=\'location="informe_total.svg";\'   class="menuitem-iconic"  image="images/toggle_log.png"/>\n'
        s= s+ '      <menuitem label="Borrar Banco"  oncommand=\'location="cuentas_ibm.psp?id_cuentas=" + idcuenta  + "&amp;ibm=borrar&amp;regresando=0";\'  class="menuitem-iconic" image="images/eventdelete.png"/>\n'
        s= s+ '      <menuseparator/>'
        s= s+ '      <menuitem label="Patrimonio en el banco"  oncommand="location=\'cuentasinformacion.psp?id_cuentas=\' + idcuenta;"/>\n'
        s= s+ '   </popup>\n'
        s= s+ '</popupset>\n'
        
        s= s+ '<tree id="tree" enableColumnDrag="true" flex="6"   context="treepopup"  onselect="tree_getid();">\n'
        s= s+ '<treecols>\n'
        s= s+  '<treecol label="id" hidden="true" />\n'
        s= s+  '<treecol label="Banco" flex="2"/>\n'       
        s= s+  '<treecol label="% saldo total" style="text-align: right" flex="2"/>\n'
        s= s+  '<treecol label="Saldo" style="text-align: right" flex="2"/>\n'
        s= s+  '</treecols>\n'
        s= s+  '<treechildren>\n'     
        total=Total().saldo_total(fecha)
        while not curs.EOF:
            row = curs.GetRowAssoc(0)   
            s= s + '<treeitem>\n'
            s= s + '<treerow>\n'
            s= s + '<treecell label="'+str(row["id_entidadesbancarias"])+ '" />\n'
            s= s + '<treecell label="'+str(row["entidadesbancaria"])+ '" style="text-align: right"/>\n'
            saldo=Banco().saldo(row["id_entidadesbancarias"], hoy())
            s= s + treecell_tpc(100*saldo/total)
            s= s + treecell_euros(saldo)
            s= s + '</treerow>\n'
            s= s + '</treeitem>\n'
            curs.MoveNext()     
        s= s + '</treechildren>\n'
        s= s + '</tree>\n'
        s= s + '<label flex="1"  style="text-align: center;font-weight : bold;" value="Saldo total: '+ euros(total)+'" />\n'
        curs.Close()
        return s


class Conection:
    def __init__(self):
        self.host,self.dbname,self.user,self.password,self.type=config.host, config.dbname, config.user, config.password, config.type
        global con
        con=self.open()
        
    def open(self):    
        con = adodb.NewADOConnection(self.type)
        con.Connect(self.host,self.user,self.password,self.dbname)
        return con
        
    def close(self):
        con.Close()

class Concepto:
    def cmb(self, sql,  selected,  js=True):        
        jstext=""
        if js:
            jstext= ' oncommand="cmbconceptos_submit();"'
        s= '<menulist id="cmbconceptos" '+jstext+'>\n'
        s=s + '<menupopup>\n';
        curs=con.Execute(sql)
        while not curs.EOF:
            row = curs.GetRowAssoc(0)   
            if row['id_conceptos']==selected:
                s=s +  '       <menuitem label="'+utf82xul(row['concepto'])+'" value="'+str(row['id_conceptos'])+";"+str(row['lu_tipooperacion'])+'" selected="true"/>\n'
            else:
                s=s +  '       <menuitem label="'+utf82xul(row['concepto'])+'" value="'+str(row['id_conceptos'])+';'+str(row['lu_tipooperacion'])+'"/>\n'
            curs.MoveNext()     
        curs.Close()
        s=s +  '     </menupopup>\n'
        s=s + '</menulist>\n'
        return s


class Cuenta:
    def cmb(self, name,  sql,  selected,  js=True):
        jstext=""
        if js:
            jstext= ' oncommand="'+name+'_submit();"'
        s= '<menulist id="'+name+'" '+jstext+' align="center">\n'
        s=s + '      <menupopup align="center">\n';
        curs=con.Execute(sql)
        while not curs.EOF:
            row = curs.GetRowAssoc(0)   
            if int(row['id_cuentas'])==int(selected):
                s=s +  '       <menuitem label="'+utf82xul(row['cuenta'])+'" value="'+str(row['id_cuentas'])+'" selected="true"/>\n'
            else:
                s=s +  '       <menuitem label="'+utf82xul(row['cuenta'])+'" value="'+str(row['id_cuentas'])+'"/>\n'
            curs.MoveNext()     
        curs.Close()
        s=s +  '     </menupopup>\n'
        s=s + '</menulist>\n'
        return s

    def cursor_listado(self, inactivas,  fecha):
        if inactivas==True:
            sql="select id_cuentas, cuenta, entidadesbancarias.entidadesbancaria, numero_cuenta, cuentas_saldo(id_cuentas,'"+fecha+"') as saldo from cuentas, entidadesbancarias where cuentas.ma_entidadesbancarias=entidadesbancarias.id_entidadesbancarias order by cuenta";
        else:
            sql="select id_cuentas, cuenta, entidadesbancarias.entidadesbancaria, numero_cuenta, cuentas_saldo(id_cuentas,'"+fecha+"') as saldo from cuentas, entidadesbancarias where cuentas.ma_entidadesbancarias=entidadesbancarias.id_entidadesbancarias and cu_activa='t' order by cuenta";
        return con.Execute(sql); 


    def xul_listado(self, curs):
        sumsaldos=0;
        s= '<vbox flex="1">\n'
        s= s+ '<tree id="tree" flex="6"   context="treepopup"  onselect="tree_getid();">\n'
        s= s+ '<treecols>\n'
        s= s+  '<treecol id="col_id" label="id" hidden="true" />\n'
        s= s+  '<treecol id="col_cuenta" label="Cuenta" sort="?col_cuenta"  sortDirection="descending" flex="2"/>\n'
        s= s+  '<treecol id="col_entidad_bancaria" label="Entidad Bancaria"  sort="?col_entidad_bancaria" sortActive="true"  flex="2"/>\n'
        s= s+  '<treecol id="col_valor" label="Número de cuenta" flex="2" style="text-align: right" />\n'
        s= s+  '<treecol id="col_saldo" label="Saldo" flex="1" style="text-align: right"/>\n'
        s= s+  '</treecols>\n'
        s= s+  '<treechildren>\n'
        while not curs.EOF:
            row = curs.GetRowAssoc(0)   
            sumsaldos=sumsaldos+ dosdecimales(row['saldo'])
            s= s + '<treeitem >\n'
            s= s + '<treerow>\n'
            s= s + '<treecell label="'+str(row["id_cuentas"])+ '" />\n'
            s= s + '<treecell label="'+ row["cuenta"]+ '" />\n'
            s= s + '<treecell label="'+row["entidadesbancaria"]+ '" />\n'
            s= s + '<treecell label="'+ str(row["numero_cuenta"])+ '" />\n'
            s= s + treecell_euros(row['saldo'])
            s= s + '</treerow>\n'
            s= s + '</treeitem>\n'
            curs.MoveNext()     
        s= s + '</treechildren>\n'
        s= s + '</tree>\n'
        s= s + '<label flex="1"  style="text-align: center;font-weight : bold;" value="Saldo total de todas las cuentas: '+ euros(sumsaldos)+'" />\n'
        s= s + '</vbox>\n'
        curs.Close()
        return s

    def registro(self,id_cuentas):
        curs = con.Execute('select * from cuentas where id_cuentas='+ str(id_cuentas)); 
        if curs == None: 
            print self.cfg.con.ErrorMsg()        
        row = curs.GetRowAssoc(0)      
        curs.Close()
        return row
        
    def saldo(self,id_cuentas,  fecha):
        curs = con.Execute('select sum(importe) as "suma" from opercuentas where ma_cuentas='+ str(id_cuentas) +" and fecha<='"+str(fecha)+"';") 
        if curs == None: 
            print self.cfg.con.ErrorMsg()        
        row = curs.GetRowAssoc(0)      
        return row['suma']


class CuentaOperacion:
    def borrar(self,  id_opercuentas):
        sql="delete from opercuentas where id_opercuentas="+ str(id_opercuentas);
        try:
            con.Execute(sql);
        except:
            return False
        return True
        
    def cursor_listado(self, id_cuentas,  year,  month):
        sql="select * from todo_opercuentas where id_cuentas="+str(id_cuentas)+" and date_part('year',fecha)='"+str(year)+"' and date_part('month',fecha)='"+str(month)+"' order by fecha,id_opercuentas";
        return con.Execute(sql); 

    def insertar(self,  fecha, lu_conceptos, lu_tiposoperaciones,  importe,  comentario,  id_cuentas):
        sql="insert into opercuentas (fecha, lu_conceptos, lu_tiposoperaciones, importe, comentario, ma_cuentas) values ('" + fecha + "'," + str(lu_conceptos)+","+ str(lu_tiposoperaciones) +","+str(importe)+", '"+comentario+"', "+str(id_cuentas)+")"
        try:
            con.Execute(sql);
        except:
            return False
        return True



    def transferencia(self, fecha,  cmbcuentaorigen,  cmbcuentadestino, importe, comision ):
        sql="select transferencia('"+fecha+"', "+ str(cmbcuentaorigen) +', ' + str(cmbcuentadestino)+', '+str(importe) +', '+str(comision)+');'
        mylog ("CuentaOperacion::transferencia: SQL: "+ sql)       
        try:
            con.Execute(sql);
        except:
            mylog ("CuentaOperacion::transferencia: "+ self.cfg.con.ErrorMsg() )       
            return False
        return True


    def xul_listado(self, curs,  id_cuentas,  year,  month):
        primeromes=datetime.date(int(year),  int(month),  1)
        diamenos=primeromes-datetime.timedelta(days=1)      
        saldo=Cuenta().saldo(id_cuentas, diamenos.isoformat())
        s=    '<popupset>\n'
        s= s+ '   <popup id="treepopup">\n'
        s= s+ '      <menuitem label="Nueva operación" oncommand="location=\'cuentas_ibm.psp?ibm=insertar&amp;regresando=0&amp;id_cuentas='+str(id_cuentas)+';\'" class="menuitem-iconic"  image="images/item_add.png"/>\n'
        s= s+ '      <menuitem label="Modificar la operación"  oncommand=\'location="cuentas_ibm.psp?id_cuentas=" + idcuenta  + "&amp;ibm=modificar&amp;regresando=0";\'/>\n'
        s= s+ '      <menuitem label="Borrar la operación"  oncommand="borrar();" class="menuitem-iconic" image="images/eventdelete.png"/>\n'
        s= s+ '      <menuseparator/>\n'
        s=s +  '            <menuitem label="Transferencia bancaria"  onclick="location=\'cuenta_transferencia.psp\';"  class="menuitem-iconic"  image="images/hotsync.png" />\n'
        s= s+ '      <menuseparator/>\n'
        s= s+ '      <menuitem label="Operación de tarjeta"   onclick="location=\'tarjetaslistado.psp\';"   class="menuitem-iconic"  image="images/visa.png"/>\n'
        s= s+ '   </popup>\n'
        s= s+ '</popupset>\n'
        s= s+ '<tree id="tree" enableColumnDrag="true" flex="6"   context="treepopup"  onselect="tree_getid();">\n'
        s= s+ '   <treecols>\n'
        s= s+ '      <treecol id="col_id" label="id" hidden="true" />\n'
        s= s+ '      <treecol label="Fecha" flex="1" style="text-align: center"/>\n'
        s= s+ '      <treecol label="Concepto"  flex="3"/>\n'
        s= s+ '      <treecol label="Importe" flex="1" style="text-align: right" />\n'
        s= s+ '      <treecol label="Saldo" flex="1" style="text-align: right"/>\n'
        s= s+ '      <treecol label="Comentario" flex="7" style="text-align: left"/>\n'
        s= s+ '   </treecols>\n'
        s= s+ '   <treechildren>\n'
        s= s + '      <treeitem>\n'
        s= s + '         <treerow>\n'
        s= s + '            <treecell label="0" />\n'
        s= s + '            <treecell label="" />\n'
        s= s + '            <treecell label="Saldo a inicio de mes" />\n'
        s= s + '            '+ treecell_euros(0)
        s= s + '            '+ treecell_euros(saldo)
        s= s + '            <treecell label="" />\n'
        s= s + '         </treerow>\n'
        s= s + '      </treeitem>\n'
        while not curs.EOF:
            row = curs.GetRowAssoc(0)   
            saldo=saldo+ dosdecimales(row['importe'])
            s= s + '      <treeitem>\n'
            s= s + '         <treerow>\n'
            s= s + '            <treecell label="'+str(row["id_opercuentas"])+ '" />\n'
            s= s + '            <treecell label="'+ str(row["fecha"])[:-12]+ '" />\n'
            s= s + '            <treecell label="'+utf82xul(row["concepto"])+ '" />\n'
            s= s + '            '+ treecell_euros(row['importe'])
            s= s + '            '+ treecell_euros(saldo)
            s= s + '            <treecell label="'+str(utf82xul(row['comentario']))+'" />\n'
            s= s + '         </treerow>\n'
            s= s + '      </treeitem>\n'
            curs.MoveNext()     
        s= s+ '   </treechildren>\n'
        s= s + '</tree>\n'
        curs.Close()
        return s


class Dividendo:
    def suma_liquido_todos(self, inicio,final):
        sql="select sum(liquido) as suma from dividendos where fecha between '"+inicio+"' and '"+final+"';"
        curs = con.Execute(sql); 
        if curs == None: 
            print self.cfg.con.ErrorMsg()        
        row = curs.GetRowAssoc(0)      
        return row['suma'];
        
    def xultree(self, sql):
        sumsaldos=0
        #sql="select id_dividendos, cuenta, fecha, liquido, inversione, entidadesbancaria from dividendos, inversiones, cuentas where cuentas.id_cuentas=inversiones.lu_cuentas and dividendos.lu_inversiones=inversiones.id_inversiones and dividendos.lu_inversiones="+str(id_inversiones) + " order by fecha;"
        curs=con.Execute(sql); 
        s=     '<vbox flex="1">\n'
        s=s+ '        <tree id="tree" flex="3">\n'
        s=s+ '          <treecols>\n'
        s=s+ '    <treecol label="Fecha" flex="1"  style="text-align: center"/>\n'
        s=s+ '    <treecol label="Cuenta cobro" flex="2" style="text-align: left" />\n'
        s=s+ '    <treecol label="Liquido" flex="1" style="text-align: right"/>\n'
        s=s+ '  </treecols>\n'
        s=s+ '  <treechildren>\n'
        while not curs.EOF:
            row = curs.GetRowAssoc(0)   
            sumsaldos=sumsaldos+dosdecimales(row['liquido'])
            s=s+ '    <treeitem>\n'
            s=s+ '      <treerow>\n'
            s=s+ '       <treecell label="'+ str(row["fecha"])[:-12]+ '" />\n'
            s=s+ '       <treecell label="'+ row["cuenta"]+ '" />\n'
            s=s+        treecell_euros(row['liquido']);
            s=s+ '      </treerow>\n'
            s=s+ '    </treeitem>\n'
            curs.MoveNext()     
        curs.Close()
      
        s=s+ '  </treechildren>\n'
        s=s+ '</tree>\n'
        
        s= s + '<label flex="0"  style="text-align: center;font-weight : bold;" value="Suma de dividendos de la inversión: '+ euros(sumsaldos)+'." />\n'
        s= s + '</vbox>\n'
        return s
        

class Inversion:
    def aplicar_tipo_fiscal(self, plusvalias,minusvalias):
        tipofiscal=0.18;
        dif=plusvalias+minusvalias;
        if (dif<=0):
            resultado=dif;
        else:
            resultado=dif*(1-tipofiscal);
        return resultado;

    def cursor_listado(self, inactivas,  fecha):
        if inactivas==True:
            sql="select id_inversiones, inversione, entidadesbancaria, inversiones_saldo(id_inversiones,'"+fecha+"') as saldo, inversion_actualizacion(id_inversiones,'"+fecha+"') as actualizacion, inversion_pendiente(id_inversiones,'"+fecha+"')  as pendiente, inversion_invertido(id_inversiones,'"+fecha+"')  as invertido, 'rendanual' as rendanual, 'rendtotal' as rendtotal from inversiones, cuentas, entidadesbancarias where cuentas.ma_entidadesbancarias=entidadesbancarias.id_entidadesbancarias and cuentas.id_cuentas=inversiones.lu_cuentas order by inversione;"

        else:
            sql="select id_inversiones, inversione, entidadesbancaria, inversiones_saldo(id_inversiones,'"+fecha+"') as saldo, inversion_actualizacion(id_inversiones,'"+fecha+"') as actualizacion, inversion_pendiente(id_inversiones,'"+fecha+"')  as pendiente,  inversion_invertido(id_inversiones,'"+fecha+"')  as invertido, 'rendanual' as rendanual, 'rendtotal' as rendtotal from inversiones, cuentas, entidadesbancarias where cuentas.ma_entidadesbancarias=entidadesbancarias.id_entidadesbancarias and cuentas.id_cuentas=inversiones.lu_cuentas and in_activa='t' order by inversione;"
        return con.Execute(sql); 
        

    def nombre(self, id_inversiones):
        sql="select inversione from inversiones where id_inversiones="+ str(id_inversiones)
        curs=con.Execute(sql); 
        row = curs.GetRowAssoc(0)   
        return row["inversione"]

    def nombre_tpcvariable(self,  tpcvariable):
        if tpcvariable==-100:
            return "Fondos de dinero o depósitos"
        if tpcvariable==0:
            return "Renta fija"
        if tpcvariable==50:
            return "Inversiones expuestas hasta un 50% en renta variable"
        if tpcvariable==100:
            return "Inversiones expuestas hasta un 100% en renta variable"

    def xultree_compraventa(self):
        sql="select id_inversiones, inversione, inversion_actualizacion(id_inversiones,'"+hoy()+"') as actualizacion, compra, venta from inversiones where venta<> compra and in_activa=true order by inversione;"
        curs=con.Execute(sql); 
        s= '<vbox flex="1">\n'
        s= s+ '<popupset>\n'
        s= s+ '<popup id="treepopup" >\n'
        s= s+ '<menuitem label="Modificar la inversión"  oncommand=\'location="inversion_ibm.psp?id_inversiones=" + idinversion  + "&amp;ibm=modificar&amp;regresando=0";\'   class="menuitem-iconic"  image="images/edit.png" />\n'
        s= s+ '<menuitem label="Estudio de la inversión"  oncommand="location=\'inversion_informacion.psp?id_inversiones=\' + idinversion;"  class="menuitem-iconic"  image="images/toggle_log.png" />\n'
        s= s+ '</popup>\n'
        s= s+ '</popupset>\n'

        s= s+ '<tree id="tree" flex="6"   context="treepopup"  onselect="tree_getid();">\n'
        s= s+ '<treecols>\n'
        s= s+  '<treecol label="Id" hidden="true" />\n'
        s= s+  '<treecol label="Inversión" flex="2"/>\n'
        s= s+  '<treecol label="Valor Acción" flex="1" style="text-align: right" />\n'
        s= s+  '<treecol label="Valor Compra" flex="1" style="text-align: right" />\n'
        s= s+  '<treecol label="Valor Venta " flex="1" style="text-align: right"/>\n'
        s= s+  '<treecol label="% Compra    " flex="1" style="text-align: right"/>\n'
        s= s+  '<treecol label="% Venta     " flex="1" style="text-align: right"/>\n'
        s= s+  '</treecols>\n'
        s= s+  '<treechildren>\n'
        while not curs.EOF:
            row = curs.GetRowAssoc(0)   
            tpcc=(row["compra"]-row["actualizacion"])*100/row["actualizacion"]
            tpcv=(row["venta"]-row["actualizacion"])*100/row["actualizacion"]
            s= s + '<treeitem>\n'
            s= s + '<treerow>\n'
            s= s + '<treecell label="'+str(row["id_inversiones"])+ '" />\n'
            s= s + '<treecell label="'+str(row["inversione"])+ '" />\n'
            s= s + treecell_euros(row["actualizacion"])
            s= s + treecell_euros_alerta_compra(row['actualizacion'], row["compra"], 0.10)
            s= s + treecell_euros_alerta_venta(row['actualizacion'], row["venta"], 0.10)
            s= s + treecell_tpc(tpcc)
            s= s + treecell_tpc(tpcv)
            s= s + '</treerow>\n'
            s= s + '</treeitem>\n'
            curs.MoveNext()     
        s= s + '</treechildren>\n'
        s= s + '</tree>\n'
        s= s + '</vbox>\n'
        curs.Close()
        return s
        

    def xul_listado(self, curs):
        sumsaldos=0;
        sumpendiente=0
        s= '<vbox flex="1">\n'
        s= s+ '<tree id="tree" enableColumnDrag="true" flex="6"   context="treepopup"  onselect="tree_getid();">\n'
        s= s+ '<treecols>\n'
        s= s+  '<treecol id="col_id" label="id" hidden="true" />\n'
        s= s+  '<treecol id="col_cuenta" label="Inversión" sort="?col_inversion" sortActive="true" sortDirection="descending" flex="2"/>\n'
        s= s+  '<treecol id="col_entidad_bancaria" label="Entidad Bancaria"  sort="?col_entidad_bancaria" sortActive="true" sortDirection="descending" flex="2"/>\n'
        s= s+  '<treecol id="col_valor" label="Valor Acción" flex="2" style="text-align: right" />\n'
        s= s+  '<treecol id="col_valor" label="Saldo" flex="2" style="text-align: right" />\n'
        s= s+  '<treecol id="col_saldo" label="Pendiente" flex="1" style="text-align: right"/>\n'
        s= s+  '<treecol label="Invertido" hidden="true"  flex="1" style="text-align: right" />\n'
        s= s+  '<treecol id="col_saldo" label="Rendimiento" flex="1" style="text-align: right"/>\n'
        s= s+  '</treecols>\n'
        s= s+  '<treechildren>\n'
        while not curs.EOF:
            row = curs.GetRowAssoc(0)   
            sumsaldos=sumsaldos+ dosdecimales(row['saldo'])
            sumpendiente=sumpendiente+dosdecimales(row['pendiente'])
            s= s + '<treeitem>\n'
            s= s + '<treerow>\n'
            s= s + '<treecell label="'+str(row["id_inversiones"])+ '" />\n'
            s= s + '<treecell label="'+str(row["inversione"])+ '" />\n'
            s= s + '<treecell label="'+ row["entidadesbancaria"]+ '" />\n'
            s= s + treecell_euros(row["actualizacion"])
            s= s + treecell_euros(row['saldo'])
            s= s + treecell_euros(row['pendiente'])
            s= s + treecell_euros(row['invertido'])
            s= s + treecell_tpc(100*row['pendiente']/row['invertido'])
            s= s + '</treerow>\n'
            s= s + '</treeitem>\n'
            curs.MoveNext()     
        s= s + '</treechildren>\n'
        s= s + '</tree>\n'
        s= s + '<label flex="0"  style="text-align: center;font-weight : bold;" value="Saldo total de todas las inversiones: '+ euros(sumsaldos)+'. Pendiente de consolidar: '+euros(sumpendiente)+'." />\n'
        s= s + '</vbox>\n'
        curs.Close()
        return s
        
class InversionActualizacion:
    def borrar(self,  id_actuinversiones):
        sql="delete from actuinversiones where id_actuinversiones="+ str(id_actuinversiones);
        try:
            con.Execute(sql);
        except:
            return False
        return True

    def insertar(self,  id_inversiones,  fecha,  valor):
        delete="delete from actuinversiones where ma_inversiones="+str(id_inversiones)+" and fecha ='"+fecha+"';"
        con.Execute(delete);
        sql="insert into actuinversiones (fecha,ma_inversiones,actualizacion) values ('"+fecha+"',"+id_inversiones+","+valor+")";
        try:
            con.Execute(sql);
        except:
            return False
        return True
        
    def cursor_listado(self, id_inversiones,  year,  month):
        sql="select * from actuinversiones where ma_inversiones="+str(id_inversiones)+" and date_part('year',fecha)='"+str(year)+"' and date_part('month',fecha)='"+str(month)+"' order by fecha;"
        return con.Execute(sql); 
        
    def ultima(self,id_inversiones,ano):
        resultado = []
        sql="SELECT fecha,Actualizacion from actuinversiones where ma_Inversiones="+str(id_inversiones)+" and  fecha<='"+str(ano)+"-12-31' order by Fecha desc limit 1"
        curs=con.Execute(sql)
        row = curs.GetRowAssoc(0)   
        resultado.append(row["fecha"])
        resultado.append(row["actualizacion"])
        return resultado
        
    def valor(self,id_inversiones,fecha):
        sql="select actualizacion from actuinversiones where ma_Inversiones="+str(id_inversiones)+" and  fecha<='"+str(fecha)+"' order by Fecha desc limit 1"
        curs=con.Execute(sql)
        row = curs.GetRowAssoc(0)   
        return row["actualizacion"]

    def xml_listado(self, curs):
        s=  '<actualizaciones>\n'
        while not curs.EOF:
            row = curs.GetRowAssoc(0)   
            s= s + '   <actualizacion id_actuinversiones="'+str(row["id_actuinversiones"])+'" fecha="'+str(row["fecha"])[:-12]+ '" actualizacion="'+ str(row["actualizacion"])+ '"/>\n'
            curs.MoveNext()     
        s= s + '</actualizaciones>\n'
        curs.Close()
        print s
        return s        

        
class InversionOperacionHistorica:
    def consolidado_total_mensual(self, ano,  mes):
        resultado=0;
        sql="SELECT * from tmpoperinversioneshistoricas where date_part('year',fecha_venta)="+str(ano)+" and date_part('month',fecha_venta)="+ str(mes);
        curs=con.Execute(sql); 
        while not curs.EOF:
            row = curs.GetRowAssoc(0)   
            resultado=resultado+(row['valor_accion_venta']-row['valor_accion_compra'])*(-1)*row['acciones'];
            resultado=resultado-row['comision']-row['impuestos'];
            curs.MoveNext()     
        curs.Close()
        return resultado
    def rendimiento_total(self, id_tmpoperinversioneshistoricas):
        sql="SELECT fecha_inicio, fecha_venta, valor_accion_compra, valor_accion_venta,ma_inversiones from tmpoperinversioneshistoricas where id_tmpoperinversioneshistoricas= "+ str(id_tmpoperinversioneshistoricas)
        curs=con.Execute(sql); 
        row = curs.GetRowAssoc(0)   
        id_inversiones=row['ma_inversiones'];
        primera=row['valor_accion_compra'];
        ultima=row['valor_accion_venta'];
        Rendimiento=(ultima-primera)*100/primera;
        return Rendimiento;
    def xultree(self, sql):
        """
            El SQL deberá ser del tipo "SELECT * from tmpoperinversiones where ma_Inversiones=id_inversiones order by fecha"
        """  
        sumacciones=0;
        sumactualizacionesximportes=0;
        sumactualizacionesxacciones=0
        sumrendimientosanualesxacciones=0;
        sumrendimientostotalesxacciones=0;
        sumrendimientosanualesponderadosxacciones=0;
        sumpendiente=0;
        sumimporte=0;
        curs=con.Execute(sql); 
        s=     '<vbox flex="1">\n'
        s=s+ '        <tree id="tree" flex="3" context="treepopup"  onselect="tree_getid();">\n'
        s=s+ '          <treecols>\n'
        s=s+ '    <treecol label="Fecha" flex="1"  style="text-align: center"/>\n'
        s=s+ '    <treecol label="Acciones" flex="1" style="text-align: right" />\n'
        s=s+ '    <treecol label="Valor compra" flex="1" style="text-align: right"/>\n'
        s=s+ '    <treecol label="Importe" flex="1" style="text-align: right"/>\n'
        s=s+ '  </treecols>\n'
        s=s+ '  <treechildren>\n'
        while not curs.EOF:
            row = curs.GetRowAssoc(0)   
            fecha=row["fecha"];
            acciones=row['acciones'];
            actualizacion=row['valor_accion'];
            importe=acciones*actualizacion;

            s=s+ '    <treeitem>\n'
            s=s+ '      <treerow>\n'
            s=s+ '       <treecell label="'+ str(row["fecha"])[:-12]+ '" />\n'
            s=s+ '       <treecell label="'+ str(row["acciones"])+ '" />\n'
            s=s+        treecell_euros(row['valor_accion']);
            s=s+        treecell_euros(importe);
            s=s+ '      </treerow>\n'
            s=s+ '    </treeitem>\n'
            curs.MoveNext()     
        curs.Close()
      
        s=s+ '  </treechildren>\n'
        s=s+ '</tree>\n'
        s= s + '</vbox>\n'
        return s
        

class InversionOperacionTemporal:
    def pendiente_consolidar(self, id_tmpoperinversiones,id_inversiones,fecha):
        sql="SELECT acciones,valor_accion  from tmpoperinversiones where id_tmpoperinversiones="+str(id_tmpoperinversiones);
        curs=con.Execute(sql); 
        row = curs.GetRowAssoc(0)   
        saldoinicio=float(row["acciones"])*float(row['valor_accion']);
        saldofinal=float(row["acciones"])*float(InversionActualizacion().valor(id_inversiones,fecha))
        pendiente=float(saldofinal)-float(saldoinicio);
        return pendiente;    
        
    def xultree(self, sql):
        """
            El SQL deberá ser del tipo "SELECT * from tmpoperinversiones where ma_Inversiones=id_inversiones order by fecha"
        """  
        sumacciones=0;
        sumactualizacionesximportes=0;
        sumactualizacionesxacciones=0
        sumrendimientosanualesxacciones=0;
        sumrendimientostotalesxacciones=0;
        sumrendimientosanualesponderadosxacciones=0;
        sumpendiente=0;
        sumimporte=0;
        curs=con.Execute(sql); 
        s=     '<vbox flex="1">\n'
        s=s+ '        <tree id="tree" flex="3" >\n'
        s=s+ '          <treecols>\n'
        s=s+ '    <treecol label="Fecha" flex="1"  style="text-align: center"/>\n'
        s=s+ '    <treecol label="Acciones" flex="1" style="text-align: right" />\n'
        s=s+ '    <treecol label="Valor compra" flex="1" style="text-align: right"/>\n'
        s=s+ '    <treecol label="Importe" flex="1" style="text-align: right"/>\n'
        s=s+ '    <treecol label="Pendiente consolidar" flex="1" style="text-align: right"/>\n'
        s=s+ '    <treecol label="% Año" flex="1" style="text-align: right"/>\n'
        s=s+ '    <treecol label="% TAE" flex="1" style="text-align: right"/>\n'
        s=s+ '    <treecol label="% Total" flex="1" style="text-align: right"/>\n'
        s=s+ '  </treecols>\n'
        s=s+ '  <treechildren>\n'
        while not curs.EOF:
            row = curs.GetRowAssoc(0)   
            fecha=row["fecha"];
            acciones=row['acciones'];
            actualizacion=row['valor_accion'];
            importe=acciones*actualizacion;
            actualizacionxacciones=actualizacion*acciones;
            pendiente=InversionOperacionTemporal().pendiente_consolidar(row['id_tmpoperinversiones'],row['ma_inversiones'],hoy());
            sumacciones=sumacciones+acciones;
            sumimporte=sumimporte+importe;
            sumpendiente=sumpendiente+pendiente;
            rendimientoanual=InversionOperacionTemporalRendimiento().anual( row['id_tmpoperinversiones'], row['ma_inversiones'],ano(hoy()));
            rendimientototal=InversionOperacionTemporalRendimiento().total( row['id_tmpoperinversiones'], row['ma_inversiones']);
            rendimientoanualponderado=365*rendimientoanual/(datetime.date.today()-datetime.date(ano(hoy()), 1, 1)).days #La resta es un objeto timedelta
            sumactualizacionesxacciones=sumactualizacionesxacciones+actualizacionxacciones;
            sumrendimientosanualesxacciones=sumrendimientosanualesxacciones+rendimientoanual*acciones;
            sumrendimientostotalesxacciones=sumrendimientostotalesxacciones+rendimientototal*acciones;
            sumrendimientosanualesponderadosxacciones=sumrendimientosanualesponderadosxacciones+rendimientoanualponderado*acciones;
            s=s+ '    <treeitem>\n'
            s=s+ '      <treerow>\n'
            s=s+ '       <treecell label="'+ str(row["fecha"])[:-12]+ '" />\n'
            s=s+ '       <treecell label="'+ str(row["acciones"])+ '" />\n'
            s=s+        treecell_euros(row['valor_accion']);
            s=s+        treecell_euros(importe);
            s=s+        treecell_euros(pendiente)
            s=s+        treecell_tpc(rendimientoanual)
            s=s+        treecell_tpc(rendimientoanualponderado)
            s=s+        treecell_tpc(rendimientototal)
            s=s+ '      </treerow>\n'
            s=s+ '    </treeitem>\n'
            curs.MoveNext()     
        curs.Close()
      
        s=s+ '  </treechildren>\n'
        s=s+ '</tree>\n'
        
        s= s + '<label flex="0"  style="text-align: center;font-weight : bold;" value="Saldo pendiente '+ euros(sumpendiente)+'. " />\n'
        s= s + '</vbox>\n'
        return s
        

class InversionOperacionTemporalRendimiento:
    def anual(self,id_tmpoperinversiones,id_inversiones,year):
        sql="SELECT fecha,valor_accion from tmpoperinversiones where id_tmpoperinversiones="+str(id_tmpoperinversiones)
        curs=con.Execute(sql); 
        row = curs.GetRowAssoc(0)   
        curs.Close()
        anobd=ano(str(row['fecha'])[:-12])
        if anobd>year:
            return 0
        
        actualizacionBD=row['valor_accion'];
        actualizacionPrimera= InversionActualizacion().ultima(id_inversiones,year-1);
        actualizacionUltima= InversionActualizacion().ultima(id_inversiones,year);
        Rendimiento=0;
        if (actualizacionBD==0):
            return 0;#Evita errores de división 0
        
        
        if (anobd==year):
            if(row['fecha']>actualizacionPrimera[0]):
                Rendimiento=(actualizacionUltima[1]-actualizacionBD)*100/actualizacionBD;
        else:
                Rendimiento=(actualizacionUltima[1]-actualizacionPrimera[1])*100/actualizacionPrimera[1];
        
        if (anobd<year):
            Rendimiento=(actualizacionUltima[1]-actualizacionPrimera[1])*100/actualizacionPrimera[1];
        return Rendimiento;
    
    
    def total(self, id_tmpoperinversiones,id_inversiones):
        sql="SELECT fecha,valor_accion from tmpoperinversiones where id_tmpoperinversiones="+ str( id_tmpoperinversiones)
        curs=con.Execute(sql); 
        row = curs.GetRowAssoc(0)   
        curs.Close()
        primera= row['valor_accion'];
        if primera==0: 
            return 0; #Evita error de división por 0
        ultima=InversionActualizacion().ultima(id_inversiones,ano(hoy()));
        Rendimiento=(ultima[1]-primera)*100/primera;
        return Rendimiento;



class InversionRendimiento:
    def personal_anual(self, id_inversiones,ano):
#        if (InversionOperacionTemporal::count(con,id_inversiones)==0) return 0;
        sumatorioAccionesXRendimiento=0; #//Almacena el producto de Saldo de la Operación por su rendimiento.
        sumatorioAcciones=0.0001; #//Almacena la suma de Saldos
        sql="SELECT id_tmpoperinversiones, acciones  from tmpoperinversiones where ma_Inversiones="+ str(id_inversiones)
        curs=con.Execute(sql); 
        while not curs.EOF:
            row = curs.GetRowAssoc(0)   
            rendimiento=InversionOperacionTemporalRendimiento().anual(row['id_tmpoperinversiones'],id_inversiones,ano);
            acciones=row["acciones"];
            sumatorioAccionesXRendimiento=sumatorioAccionesXRendimiento+ acciones*rendimiento;
            sumatorioAcciones=sumatorioAcciones + acciones;
            curs.MoveNext()     
        curs.Close()     
        resultado=sumatorioAccionesXRendimiento/sumatorioAcciones;
        return resultado;

    def personal_total(self,  id_inversiones):
        sumatorioAccionesXRendimiento=0; #Almacena el producto de Saldo de la Operación por su rendimiento.
        sumatorioAcciones=0; #Almacena la suma de Saldos
        sql="SELECT id_tmpoperinversiones, acciones  from tmpoperinversiones where ma_Inversiones=" + str(id_inversiones)
        curs=con.Execute(sql); 
        while not curs.EOF:
            row = curs.GetRowAssoc(0)   
            rendimiento=InversionOperacionTemporalRendimiento().total(row['id_tmpoperinversiones'],id_inversiones);
            acciones=row["acciones"];
            sumatorioAccionesXRendimiento=sumatorioAccionesXRendimiento+ acciones*rendimiento;
            sumatorioAcciones=sumatorioAcciones + acciones;
            curs.MoveNext()     
        curs.Close()
    
        if sumatorioAcciones==0:
            return 0;
        resultado=sumatorioAccionesXRendimiento/sumatorioAcciones;
        return resultado

class Tarjeta:
    def cursor_listado(self, inactivas,  fecha):
        if inactivas==True:
            sql="select id_tarjetas, tarjeta, cuenta, numero, pago_diferido, saldomaximo from tarjetas,cuentas where tarjetas.lu_cuentas=cuentas.id_cuentas order by tarjetas.tarjeta"
        else:
            sql="select id_tarjetas, tarjeta, cuenta, numero, pago_diferido, saldomaximo from tarjetas,cuentas where tarjetas.lu_cuentas=cuentas.id_cuentas and tarjetas.tj_activa='t' order by tarjetas.tarjeta"
        return con.Execute(sql); 

    def xul_listado(self, curs):
        s= '<popupset>\n'
        s= s+ '   <popup id="treepopup" >\n'
        s= s+ '      <menuitem label="Tarjeta nueva" oncommand="location=\'cuentas_ibm.psp?ibm=insertar&amp;regresando=0;\'" class="menuitem-iconic"  image="images/item_add.png"/>\n'
        s= s+ '      <menuitem label="Modificar la tarjeta"  oncommand=\'location="cuentas_ibm.psp?id_cuentas=" + idcuenta  + "&amp;ibm=modificar&amp;regresando=0";\'   class="menuitem-iconic"  image="images/toggle_log.png"/>\n'
        s= s+ '      <menuitem label="Borrar la tarjeta"  oncommand=\'location="cuentas_ibm.psp?id_cuentas=" + idcuenta  + "&amp;ibm=borrar&amp;regresando=0";\'  class="menuitem-iconic" image="images/eventdelete.png"/>\n'
        s= s+ '      <menuseparator/>'
        s= s+ '      <menuitem label="Movimientos de la tarjeta"  oncommand="location=\'tarjetaoperacion_listado.psp?id_tarjetas=\' + id_tarjetas;"/>\n'
        s= s+ '   </popup>\n'
        s= s+ '</popupset>\n'
        
        s= s+ '<tree id="tree" enableColumnDrag="true" flex="6"   context="treepopup"  onselect="tree_getid();">\n'
        s= s+ '<treecols>\n'
        s= s+  '<treecol id="col_id" label="id" hidden="true" />\n'
        s= s+  '<treecol id="col_cuenta" label="Nombre Tarjeta" sort="?col_inversion" sortActive="true" sortDirection="descending" flex="2"/>\n'
        s= s+  '<treecol label="Cuenta asociada" flex="2"/>\n'
        s= s+  '<treecol label="Número de tarjeta" flex="2" style="text-align: right" />\n'
        s= s+  '<treecol label="Pago diferido" flex="1" style="text-align: right"/>\n'
        s= s+  '<treecol label="Saldo máximo" flex="1" style="text-align: right"/>\n'
        s= s+  '</treecols>\n'
        s= s+  '<treechildren>\n'
        while not curs.EOF:
            row = curs.GetRowAssoc(0)   
            s= s + '<treeitem>\n'
            s= s + '<treerow>\n'
            s= s + '<treecell label="'+str(row["id_tarjetas"])+ '" />\n'
            s= s + '<treecell label="'+ row["tarjeta"]+ '" />\n'
            s= s + '<treecell label="'+row["cuenta"]+ '" />\n'
            s= s + '<treecell label="'+ str(row["numero"])+ '" />\n'
            s= s + '<treecell label="'+ str(row["pago_diferido"])+ '" />\n'
            s= s + treecell_euros(row['saldomaximo'])
            s= s + '</treerow>\n'
            s= s + '</treeitem>\n'
            curs.MoveNext()     
        s= s + '</treechildren>\n'
        s= s + '</tree>\n'
        curs.Close()
        return s

class TarjetaOperacion:
    def borrar(self,  id_opertarjetas):
        sql="delete from opertarjetas where id_opertarjetas="+ str(id_opertarjetas);
        try:
            con.Execute(sql);
        except:
            return False
        return True
        
    def insertar(self,  fecha, lu_conceptos, lu_tiposoperaciones,  importe,  comentario,  id_tarjetas):
        sql="insert into opertarjetas (fecha, lu_conceptos, lu_tiposoperaciones, importe, comentario, ma_tarjetas, pagado) values ('" + fecha + "'," + str(lu_conceptos)+","+ str(lu_tiposoperaciones) +","+str(importe)+", '"+comentario+"', "+str(id_tarjetas)+", false)"
        mylog(sql)
        try:
            con.Execute(sql);
        except:
            return False
        return True


class TipoOperacion:
    def registro(self,id_tiposoperaciones):
        sql="select *  from tiposoperaciones where id_tiposoperaciones=" + str(id_tiposoperaciones)
        curs=con.Execute(sql); 
        row = curs.GetRowAssoc(0)   
        return row



class Total:
    def grafico_evolucion_total(self):
        f=open("/tmp/informe_total.plot","w")
        s='set data style fsteps\n'
        s=s+"set xlabel 'Fechas'\n"
        s=s+"set timefmt '%Y-%m-%d'\n"
        s=s+"set xdata time\n"
        s=s+"set ylabel 'Valor'\n"
        s=s+"set yrange [ 0: ]\n"
        s=s+"set format x '%Y'\n"
        s=s+"set grid\n"
        s=s+"set key left\n"
        s=s+"set terminal png\n"
        s=s+"set output \"/var/www/localhost/htdocs/xulpymoney/informe_total.png\"\n"
        s=s+"plot \"/tmp/informe_total.dat\" using 1:2 smooth unique title \"Saldo total\""
        f.write(s)
        f.close()

        f=open("/tmp/informe_total.dat","w")
        for i in range (1997,  2010):
            f.write(str(i)+"-01-01\t"+str(Total().saldo_total(str(i)+"-01-01"))+"\n")
        f.write(hoy()+"\t"+str(Total().saldo_total(hoy()))+"\n")
        f.close()
        
        os.popen("gnuplot /tmp/informe_total.plot");
        
    def saldo_todas_cuentas(self, fecha):
        sql="select saldototalcuentasactivas('"+fecha+"') as saldo;";
        curs=con.Execute(sql); 
        row = curs.GetRowAssoc(0)   
        return row['saldo'];

    def saldo_total(self,fecha):
        sql="select saldo_total('"+fecha+"') as saldo;";
        curs=con.Execute(sql); 
        row = curs.GetRowAssoc(0)   
        return row['saldo'];

    def saldo_todas_inversiones(self,fecha):
        sql="select saldototalinversionesactivas('"+fecha+"') as saldo;";
        curs=con.Execute(sql); 
        row = curs.GetRowAssoc(0)   
        return row['saldo'];

    def saldo_todas_inversiones_cotizan_mercado(self,fecha):
        resultado=0;
        sql="SELECT ID_INVERSIONES FROM INVERSIONES where cotizamercado='t'";
        curs=con.Execute(sql); 
        while not curs.EOF:
            row = curs.GetRowAssoc(0)   
            resultado=resultado + Inversion().saldo(con,row["id_inversiones"],fecha);
            curs.MoveNext()     
        curs.Close()

    def saldo_todas_inversiones_no_cotizan_mercado(self,fecha):
        resultado=0;
        sql="SELECT ID_INVERSIONES FROM INVERSIONES where cotizamercado='f'";
        curs=con.Execute(sql); 
        while not curs.EOF:
            row = curs.GetRowAssoc(0)   
            resultado=resultado + Inversion().saldo(con,row["id_inversiones"],fecha);
            curs.MoveNext()     
        curs.Close()


    def saldo_por_tipo_operacion(self, ano,  mes,  tipooperacion):
        sql="select sum(Importe) as importe from opercuentas where lu_tiposoperaciones="+str(tipooperacion)+" and date_part('year',fecha) = "+str(ano)+" and date_part('month',fecha)= " + str(mes);
        curs=con.Execute(sql); 
        row = curs.GetRowAssoc(0)   
        if row['importe']==None:
            resultado=0
        else:
            resultado=float(row['importe'])
        curs.Close()
        return resultado

    def xultree_historico_dividendos(self, ano):
        sumsaldos=0
        sql="select id_dividendos, fecha, liquido, inversione, entidadesbancaria from dividendos, inversiones, cuentas, entidadesbancarias where entidadesbancarias.id_entidadesbancarias=cuentas.ma_entidadesbancarias and cuentas.id_cuentas=inversiones.lu_cuentas and dividendos.lu_inversiones=inversiones.id_inversiones and date_part('year',fecha)="+str(ano) + " order by fecha;"
        curs=con.Execute(sql); 
        s=     '<vbox flex="1">\n'
        s=s+ '        <tree id="tree" flex="3">\n'
        s=s+ '          <treecols>\n'
        s=s+ '    <treecol label="Fecha" flex="1"  style="text-align: center"/>\n'
        s=s+ '    <treecol label="Inversión" flex="2" style="text-align: left" />\n'
        s=s+ '    <treecol label="Banco" flex="2" style="text-align: left"/>\n'
        s=s+ '    <treecol label="Liquido" flex="1" style="text-align: right"/>\n'
        s=s+ '  </treecols>\n'
        s=s+ '  <treechildren>\n'
        while not curs.EOF:
            row = curs.GetRowAssoc(0)   
            sumsaldos=sumsaldos+dosdecimales(row['liquido'])
            s=s+ '    <treeitem>\n'
            s=s+ '      <treerow>\n'
            s=s+ '       <treecell label="'+ str(row["fecha"])[:-12]+ '" />\n'
            s=s+ '       <treecell label="'+ row["inversione"]+ '" />\n'
            s=s+ '       <treecell label="'+ row["entidadesbancaria"]+ '" />\n'
            s=s+        treecell_euros(row['liquido']);
            s=s+ '      </treerow>\n'
            s=s+ '    </treeitem>\n'
            curs.MoveNext()     
        curs.Close()
      
        s=s+ '  </treechildren>\n'
        s=s+ '</tree>\n'
        
        s= s + '<label flex="0"  style="text-align: center;font-weight : bold;" value="Suma de dividendos en el año '+str(ano)+': '+ euros(sumsaldos)+'." />\n'
        s= s + '</vbox>\n'
        return s
        
        
    def xultree_historico_inversiones(self, ano, desde_ano):
        sql="select * from tmpoperinversioneshistoricas where date_part('year',fecha_venta)="+str(ano)+" order by fecha_venta";
        curs=con.Execute(sql); 
        sumpendiente=0;
        sumrendponderado=0;
        sumrendtotal=0;
        sumimporteventa=0;
        sumsaldosinicio=0;
        sumsaldosfinal=0;
        sumanos=0;
        sumoperacionespositivas=0;
        sumoperacionesnegativas=0;
        sumrendtotalxsaldofinal=0;
        sumrendpondxsaldofinal=0;
        sumimpuestos=0;
        sumcomision=0;
        s='<vbox flex="1">\n'
        s=s+ '        <tree id="tree" enableColumnDrag="true" flex="3"   context="treepopup"  onselect="tree_getid();">\n'
        s=s+ '          <treecols>\n'
        s=s+ '<treecol id="col_fecha_venta" label="Fecha venta" sort="?col_inversion" sortActive="true" sortDirection="descending" flex="0"  style="text-align: center"/>\n'
        s=s+ '    <treecol id="col_anos_inversion" label="Años"  sort="?col_entidad_bancaria" sortActive="true" sortDirection="descending" flex="0"  style="text-align: center"/>\n'
        s=s+ '    <treecol id="col_valor" label="Inversión" flex="2" style="text-align: left" />\n'
        s=s+ '    <treecol id="col_saldo" label="Tipo Operación" flex="2" style="text-align: left"/>\n'
        s=s+ '    <treecol id="col_pendiente" label="Saldo inicio" flex="0" style="text-align: right"/>\n'
        s=s+ '    <treecol id="col_rend_anual" label="Saldo final" flex="0" style="text-align: right"/>\n'
        s=s+ '    <treecol id="col_rend_anual" label="Consolidado" flex="0" style="text-align: right"/>\n'
        s=s+ '    <treecol id="col_rend_total" label="Rend. ponderado" flex="0" style="text-align: right"/>\n'
        s=s+ '    <treecol id="col_rend_total" label="Rend. total" flex="0" style="text-align: right"/>\n'
        s=s+ '  </treecols>\n'
        s=s+ '  <treechildren>\n'
        while not curs.EOF:
            row = curs.GetRowAssoc(0)   
            id_inversiones=row['ma_inversiones'];
            saldoinicio=-row['acciones']*row['valor_accion_compra'];
            saldofinal=-row['acciones']*row['valor_accion_venta'];
            pendiente=saldofinal-saldoinicio;
            sumimpuestos=sumimpuestos-row['impuestos'];
            sumcomision=sumcomision-row['comision'];
            anos=anos_entre_fechas(row['fecha_venta'], row['fecha_inicio']);
            if anos==0:#Operación intradía
                anos=float(1/365.0);
            rendtotal=InversionOperacionHistorica().rendimiento_total(row['id_tmpoperinversioneshistoricas'])
            sumpendiente=sumpendiente+pendiente;
            sumsaldosinicio=sumsaldosinicio+saldoinicio;
            sumsaldosfinal=sumsaldosfinal+saldofinal;
            sumanos=sumanos+anos;
            sumrendpondxsaldofinal=sumrendpondxsaldofinal+(saldofinal*rendtotal/anos);
            sumrendtotalxsaldofinal=sumrendtotalxsaldofinal+rendtotal*saldofinal;
             
            #Calculo de operaciones positivas y negativas
            if pendiente>0:
                sumoperacionespositivas=sumoperacionespositivas+pendiente; 
            else:
                sumoperacionesnegativas=sumoperacionesnegativas+pendiente;
        
            regTipoOperacion=TipoOperacion().registro(row["lu_tiposoperaciones"])
            s=s+ '    <treeitem>\n'
            s=s+ '      <treerow>\n'
            s=s+ '       <treecell label="'+str(row["fecha_venta"])[:-12]+ '" />\n'
            s=s+ '       <treecell label="'+str(dosdecimales(anos))+ '" />\n'
            s=s+ '       <treecell label="'+Inversion().nombre(row["ma_inversiones"])+ '" />\n'
            s=s+ '       <treecell label="'+regTipoOperacion['tipo_operacion']+ '" />\n'
            s=s+        treecell_euros(saldoinicio);
            s=s+        treecell_euros(saldofinal);
            s=s+        treecell_euros(pendiente);
            s=s+        treecell_tpc(rendtotal/anos);
            s=s+        treecell_tpc(rendtotal);
            s=s+ '      </treerow>\n'
            s=s+ '    </treeitem>\n'
            curs.MoveNext()     
        curs.Close()
      
        s=s+ '  </treechildren>\n'
        s=s+ '</tree>\n'
        s= s + '<label flex="0"  style="text-align: center;font-weight : bold;" value="Suma de saldos consolidados en el año '+str(ano)+': '+ euros(sumpendiente)+'." />\n'
        s= s + '</vbox>\n'
        return s
        
    def xultree_historico_rendimientos(self, ano):
        inicio=str(ano)+"-01-01";
        fin=str(ano)+"-12-31";
        sql="select * from tmpoperinversioneshistoricas where date_part('year',fecha_venta)="+str(ano)+" order by fecha_venta";
        curs=con.Execute(sql); 
        sumpendiente=0;
        sumoperacionespositivas=0;
        sumoperacionesnegativas=0;
        sumimpuestos=0;
        sumcomision=0;
        while not curs.EOF:
            row = curs.GetRowAssoc(0)   
            saldoinicio=-row['acciones']*row['valor_accion_compra'];
            saldofinal=-row['acciones']*row['valor_accion_venta'];
            pendiente=saldofinal-saldoinicio;
            sumimpuestos=sumimpuestos-row['impuestos'];
            sumcomision=sumcomision-row['comision'];             
            #Calculo de operaciones positivas y negativas
            if pendiente>0:
                sumoperacionespositivas=sumoperacionespositivas+pendiente; 
            else:
                sumoperacionesnegativas=sumoperacionesnegativas+pendiente;
            curs.MoveNext()     
        curs.Close()
 
        beneficiocon=Inversion().aplicar_tipo_fiscal(sumoperacionespositivas,sumoperacionesnegativas)+sumimpuestos+sumcomision+Dividendo().suma_liquido_todos(inicio,fin)

        saldototal=Total().saldo_total(hoy());

        saldototalinicio=Total().saldo_total(inicio)

        beneficio=sumoperacionespositivas+sumoperacionesnegativas+sumimpuestos+sumcomision+(Dividendo().suma_liquido_todos(inicio,fin)*1.18)

        s=      '<vbox flex="1">\n'
        s=s+ ' <tree flex="1">\n'
        s=s+ '  <treecols>\n'
        s=s+ '    <treecol flex="1"  style="text-align: left"/>\n'
        s=s+ '    <treecol label="Beneficio" flex="1" style="text-align: center"/>\n'
        s=s+ '    <treecol label="% TAE desde '+inicio+' ('+euros(saldototalinicio)+')" flex="1" style="text-align: center"/>\n'
        s=s+ ' </treecols>\n'
        s=s+ '  <treechildren>\n'
        s=s+ '    <treeitem>\n'
        s=s+ '      <treerow>\n'
        s=s+ '          <treecell label="Sin impuestos" />\n'
        s=s+treecell_euros(beneficio);
        s=s+treecell_tpc((beneficio)*100/saldototalinicio)
        s=s+ '      </treerow>\n'
        s=s+ '   </treeitem>    \n'
        s=s+ '    <treeitem>\n'
        s=s+ '      <treerow>\n'
        s=s+ '         <treecell label="Con impuestos" />\n'
        s=s+treecell_euros(beneficiocon);
        s=s+treecell_tpc((beneficiocon)*100/saldototalinicio)
        s=s+ '      </treerow>\n'
        s=s+ '   </treeitem>\n'
        s=s+ '  </treechildren>\n'
        s=s+ '</tree>\n'
        s= s + '<label flex="0"  style="text-align: center;font-weight : bold;" value="Saldo a '+hoy()+': '+ euros(saldototal)+'." />\n'        
        s= s + '<label flex="0"  style="text-align: center;font-weight : bold;" value="Beneficio en el año '+str(ano)+': '+ euros(saldototal-saldototalinicio)+'." />\n'
        s= s + '</vbox>\n'
        return s        


def mylog(text):
    f=open("/tmp/xulpymoney.log","a")
    f.write(text + "\n")
    f.close()
