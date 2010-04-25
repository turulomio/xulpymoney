# -*- coding: UTF-8 -*-
import sys,  os
sys.path.append("/usr/lib/xulpymoney/")
import datetime,  math
import adodb
import config
from formato import *  
from xul import *

class Banco:    
    def cmb(self, name,  sql,  selected,  js=True):
        jstext=""
        if js:
            jstext= ' oncommand="'+name+'_submit();"'
        s= '<menulist id="'+name+'" '+jstext+' align="center">\n'
        s=s + '      <menupopup align="center">\n';
        curs=con.Execute(sql)
        while not curs.EOF:
            row = curs.GetRowAssoc(0)   
            if int(row['id_entidadesbancarias'])==int(selected):
                s=s +  '       <menuitem label="'+utf82xul(row['entidadesbancaria'])+'" value="'+str(row['id_entidadesbancarias'])+'" selected="true"/>\n'
            else:
                s=s +  '       <menuitem label="'+utf82xul(row['entidadesbancaria'])+'" value="'+str(row['id_entidadesbancarias'])+'"/>\n'
            curs.MoveNext()     
        curs.Close()
        s=s +  '     </menupopup>\n'
        s=s + '</menulist>\n'
        return s
    def insertar(self,  entidadesbancaria,  eb_activa):
        sql="insert into entidadesbancarias (entidadesbancaria, eb_activa) values ('" + entidadesbancaria + "'," + str(eb_activa)+")"
        try:
            con.Execute(sql);
        except:
            return False
        return True
        
    def modificar(self, id_bancos, entidadesbancaria):
        sql="update entidadesbancarias set entidadesbancaria='"+str(entidadesbancaria)+"' where id_entidadesbancarias="+ str(id_bancos)
        try:
            con.Execute(sql);
        except:
            return False
        return True
        
    def modificar_activa(self, id_bancos,  activa):
        sql="update entidadesbancarias set eb_activa="+str(activa)+" where id_entidadesbancarias="+ str(id_bancos)
        curs=con.Execute(sql); 
        return sql

        
    def saldo(self,id_entidadesbancarias,fecha):
        curs = con.Execute('select banco_saldo('+ str(id_entidadesbancarias) + ",'"+str(fecha)+"') as saldo;"); 
        if curs == None: 
            print self.cfg.con.ErrorMsg()        
        row = curs.GetRowAssoc(0)      
        curs.Close()
        if row['saldo']==None:
            return 0
        else:
            return row['saldo']

    def xultree(self, inactivas,  fecha):
        if inactivas==True:
            sql="select * from entidadesbancarias order by entidadesbancaria";
        else:
            sql="select * from entidadesbancarias where eb_activa='t' order by entidadesbancaria";
        curs=con.Execute(sql)
        s=      '<script>\n<![CDATA[\n'
        s= s+ 'function popupBancos(){\n'
        s= s+ '     var tree = document.getElementById("treeBancos");\n'
        #el boolean de un "0" es true y bolean de un 0 es false
        s= s+ '     var activa=Boolean(Number(tree.view.getCellText(tree.currentIndex,tree.columns.getNamedColumn( "activa"))));\n'
        s= s+ '     id_bancos=tree.view.getCellText(tree.currentIndex,tree.columns.getNamedColumn("id"));\n'
        s= s+ '     var popup = document.getElementById("popupBancos");\n'
        s= s+ '     if (document.getElementById("popmodificar")){\n'#Con que exista este vale
        s= s+ '         popup.removeChild(document.getElementById("popmodificar"));\n'
        s= s+ '         popup.removeChild(document.getElementById("popseparator1"));\n'
        s= s+ '         popup.removeChild(document.getElementById("poppatrimonio"));\n'
        s= s+ '         popup.removeChild(document.getElementById("popseparator2"));\n'
        s= s+ '         popup.removeChild(document.getElementById("popactiva"));\n'
        s= s+ '     }\n'
        s= s+ '     var popmodificar=document.createElement("menuitem");\n'
        s= s+ '     popmodificar.setAttribute("id", "popmodificar");\n'
        s= s+ '     popmodificar.setAttribute("label", "Modificar el banco");\n'
        s= s+ '     popmodificar.setAttribute("class", "menuitem-iconic");\n'
        s= s+ '     popmodificar.setAttribute("image", "images/edit.png");\n'
        s= s+ '     popmodificar.setAttribute("oncommand", "banco_modificar();");\n'
        s= s+ '     popup.appendChild(popmodificar);\n'
        s= s+ '     var popseparator1=document.createElement("menuseparator");\n'
        s= s+ '     popseparator1.setAttribute("id", "popseparator1");\n'
        s= s+ '     popup.appendChild(popseparator1);\n'
        s= s+ '     var poppatrimonio=document.createElement("menuitem");\n'
        s= s+ '     poppatrimonio.setAttribute("id", "poppatrimonio");\n'
        s= s+ '     poppatrimonio.setAttribute("label", "Patrimonio en el banco");\n'
        s= s+ '     poppatrimonio.setAttribute("oncommand", "alert(\'Falta desarrollar\');");\n'
        s= s+ '     popup.appendChild(poppatrimonio);\n'
        s= s+ '     var popseparator2=document.createElement("menuseparator");\n'
        s= s+ '     popseparator2.setAttribute("id", "popseparator2");\n'
        s= s+ '     popup.appendChild(popseparator2);\n'
        s= s+ '     var popactiva=document.createElement("menuitem");\n'
        s= s+ '     popactiva.setAttribute("id", "popactiva");\n'
        s= s+ '     if (activa){\n'
        s= s+ '         popactiva.setAttribute("label", "Desactivar el banco");\n'
        s= s+ '         popactiva.setAttribute("checked", "false");\n'
        s= s+ '         popactiva.setAttribute("oncommand", "banco_modificar_activa();");\n'
        s= s+ '     }else{\n'
        s= s+ '         popactiva.setAttribute("label", "Activar el banco");\n'
        s= s+ '         popactiva.setAttribute("checked", "true");\n'
        s= s+ '         popactiva.setAttribute("oncommand", "banco_modificar_activa();");\n'
        s= s+ '     }\n'
        s= s+ '     popup.appendChild(popactiva);\n'
        s= s+ '}\n\n'

        s= s+ 'function banco_modificar(){\n'
        s= s+ '     var tree = document.getElementById("treeBancos");\n'
        s= s+ '     id_entidadesbancarias=tree.view.getCellText(tree.currentIndex,tree.columns.getNamedColumn("id"));\n'
        s= s+ '     location=\'banco_modificar.psp?id_entidadesbancarias=\' + id_entidadesbancarias;\n'
        s= s+ '}\n\n'
        
        s= s+ 'function banco_modificar_activa(){\n'
        s= s+ '     var tree = document.getElementById("treeBancos");\n'
        s= s+ '     var xmlHttp;\n'
        s= s+ '     var activa=Boolean(Number(tree.view.getCellText(tree.currentIndex,tree.columns.getNamedColumn("activa"))));\n'
        s= s+ '     xmlHttp=new XMLHttpRequest();\n'
        s= s+ '     xmlHttp.onreadystatechange=function(){\n'
        s= s+ '         if(xmlHttp.readyState==4){\n'
        s= s+ '             var ale=xmlHttp.responseText;\n'
        s= s+ '             location="banco_listado.psp";\n'
        s= s+ '         }\n'
        s= s+ '     }\n'
        s= s+ '     var url="ajax/banco_modificar_activa.psp?id_bancos="+id_bancos+\'&activa=\'+!activa;\n'
        s= s+ '     xmlHttp.open("GET",url,true);\n'
        s= s+ '     xmlHttp.send(null);\n'
        s= s+ '}\n'
        s= s+ ']]>\n</script>\n\n'        
        
        s= s+ '<popupset>\n'
        s= s+ '    <popup id="popupBancos" >\n'
        s= s+ '        <menuitem label="Nuevo banco" oncommand="location=\'banco_insertar.psp\'" class="menuitem-iconic"  image="images/item_add.png"/>\n'
        s= s+ '    </popup>\n'
        s= s+ '</popupset>\n'
        
        s= s+ '<tree id="treeBancos" enableColumnDrag="true" flex="6"   context="popupBancos"  onselect="popupBancos();">\n'
        s= s+ '    <treecols>\n'
        s= s+  '        <treecol id="id" label="id" hidden="true" />\n'
        s= s+  '        <treecol id="activa" label="Activa" hidden="true" />\n'
        s= s+  '        <treecol label="Banco" flex="2"/>\n'       
        s= s+  '        <treecol label="% saldo total" style="text-align: right" flex="2"/>\n'
        s= s+  '        <treecol label="Saldo" style="text-align: right" flex="2"/>\n'
        s= s+  '    </treecols>\n'
        s= s+  '    <treechildren>\n'     
        total=Total().saldo_total(fecha)
        while not curs.EOF:
            row = curs.GetRowAssoc(0)   
            s= s + '        <treeitem>\n'
            s= s + '            <treerow>\n'
            s= s + '                <treecell label="'+str(row["id_entidadesbancarias"])+ '" />\n'
            s= s + '                <treecell label="'+str(row["eb_activa"])+ '" />\n'
            s= s + '                <treecell label="'+str(row["entidadesbancaria"])+ '" style="text-align: right"/>\n'
            saldo=Banco().saldo(row["id_entidadesbancarias"], datetime.date.today())
            if total==0: # Zero division
                s= s + '                '+treecell_tpc(0)
            else:
                s= s + '                '+treecell_tpc(100*saldo/total)
            s= s + '                '+treecell_euros(saldo)
            s= s + '            </treerow>\n'
            s= s + '        </treeitem>\n'
            curs.MoveNext()    
        s= s + '    </treechildren>\n'
        s= s + '</tree>\n'
        s= s + '<label flex="1"  style="text-align: center;font-weight : bold;" value="Saldo total: '+ euros(total)+'" />\n'
        curs.Close()
        return s


class Conection:
    """Funciona para no tener que pasar con a las funciones de core, pero no funciona en conexiones directas desde un psp"""
    def __init__(self):
        self.host,self.dbname,self.user,self.password,self.type=config.host, config.dbname, config.user, config.password, config.type
        global con
        con=self.open()
        
    def open(self):    
        c = adodb.NewADOConnection(self.type)
        c.Connect(self.host,self.user,self.password,self.dbname)
        return c
        
    def close(self):
        con.Close()
        


class ConectionDirect:
    def __init__(self):
        self.con = adodb.NewADOConnection(config.type)
        self.con.Connect(config.host,config.user,config.password,config.dbname)
        
    def close(self):
        self.con.Close()

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
        
    def insertar(self,  id_entidadesbancarias,  cuenta,  numero_cuenta, cu_activa):
        sql="insert into cuentas (ma_entidadesbancarias, cuenta, numero_cuenta, cu_activa) values (" + str(id_entidadesbancarias )+ ", '" + str(cuenta)+"', '"+ str(numero_cuenta) +"', "+str(cu_activa)+")"
        try:
            con.Execute(sql);
        except:
            return False
        return True


    def xul_listado(self, inactivas,  fecha):
        if inactivas==True:
            sql="select id_cuentas, cu_activa, cuenta, entidadesbancarias.entidadesbancaria, numero_cuenta, cuentas_saldo(id_cuentas,'"+str(fecha)+"') as saldo from cuentas, entidadesbancarias where cuentas.ma_entidadesbancarias=entidadesbancarias.id_entidadesbancarias order by cuenta";
        else:
            sql="select id_cuentas, cu_activa, cuenta, entidadesbancarias.entidadesbancaria, numero_cuenta, cuentas_saldo(id_cuentas,'"+str(fecha)+"') as saldo from cuentas, entidadesbancarias where cuentas.ma_entidadesbancarias=entidadesbancarias.id_entidadesbancarias and cu_activa='t' order by cuenta";
        sumsaldos=0;
        s=      '<script>\n<![CDATA[\n'
        s= s+ 'function popupCuentas(){\n'
        s= s+ '     var tree = document.getElementById("treeCuentas");\n'
        #el boolean de un "0" es true y bolean de un 0 es false
        s= s+ '     var activa=Boolean(Number(tree.view.getCellText(tree.currentIndex,tree.columns.getNamedColumn( "activa"))));\n'
        s= s+ '     id_cuentas=tree.view.getCellText(tree.currentIndex,tree.columns.getNamedColumn("id"));\n'
        s= s+ '     var popup = document.getElementById("popupCuentas");\n'
        s= s+ '     if (document.getElementById("popmodificar")){\n'#Con que exista este vale
        s= s+ '         popup.removeChild(document.getElementById("popmodificar"));\n'
        s= s+ '         popup.removeChild(document.getElementById("popactiva"));\n'
        s= s+ '         popup.removeChild(document.getElementById("popseparator1"));\n'
        s= s+ '         popup.removeChild(document.getElementById("popmovimientos"));\n'
        s= s+ '     }\n'
        s= s+ '     var popmodificar=document.createElement("menuitem");\n'
        s= s+ '     popmodificar.setAttribute("id", "popmodificar");\n'
        s= s+ '     popmodificar.setAttribute("label", "Modificar la cuenta");\n'
        s= s+ '     popmodificar.setAttribute("class", "menuitem-iconic");\n'
        s= s+ '     popmodificar.setAttribute("image", "images/edit.png");\n'
        s= s+ '     popmodificar.setAttribute("oncommand", "cuenta_modificar();");\n'
        s= s+ '     popup.appendChild(popmodificar);\n'
        s= s+ '     var popactiva=document.createElement("menuitem");\n'
        s= s+ '     popactiva.setAttribute("id", "popactiva");\n'
        s= s+ '     if (activa){\n'
        s= s+ '         popactiva.setAttribute("label", "Desactivar la cuenta");\n'
        s= s+ '         popactiva.setAttribute("checked", "false");\n'
        s= s+ '         popactiva.setAttribute("oncommand", "cuenta_modificar_activa();");\n'
        s= s+ '     }else{\n'
        s= s+ '         popactiva.setAttribute("label", "Activar la cuenta");\n'
        s= s+ '         popactiva.setAttribute("checked", "true");\n'
        s= s+ '         popactiva.setAttribute("oncommand", "cuenta_modificar_activa();");\n'
        s= s+ '     }\n'
        s= s+ '     popup.appendChild(popactiva);\n'
        s= s+ '     var popseparator1=document.createElement("menuseparator");\n'
        s= s+ '     popseparator1.setAttribute("id", "popseparator1");\n'
        s= s+ '     popup.appendChild(popseparator1);\n'
        s= s+ '     var popmovimientos=document.createElement("menuitem");\n'
        s= s+ '     popmovimientos.setAttribute("id", "popmovimientos");\n'
        s= s+ '     popmovimientos.setAttribute("label", "Movimientos en la cuenta");\n'
        s= s+ '     popmovimientos.setAttribute("oncommand", "cuenta_movimientos();");\n'
        s= s+ '     popup.appendChild(popmovimientos);\n'
        s= s+ '}\n\n'

        s= s+ 'function cuenta_modificar(){\n'
        s= s+ '     var tree = document.getElementById("treeCuentas");\n'
        s= s+ '     id_cuentas=tree.view.getCellText(tree.currentIndex,tree.columns.getNamedColumn("id"));\n'
        s= s+ '     location=\'cuenta_modificar.psp?id_cuentas=\' + id_cuentas;\n'
        s= s+ '}\n\n'
        
        s= s+ 'function cuenta_movimientos(){\n'
        s= s+ '     var tree = document.getElementById("treeCuentas");\n'
        s= s+ '     id_cuentas=tree.view.getCellText(tree.currentIndex,tree.columns.getNamedColumn("id"));\n'
        s= s+ '     location=\'cuenta_informacion.psp?id_cuentas=\' + id_cuentas;\n'
        s= s+ '}\n\n'
        
        s= s+ 'function cuenta_modificar_activa(){\n'
        s= s+ '     var tree = document.getElementById("treeCuentas");\n'
        s= s+ '     var xmlHttp;\n'
        s= s+ '     var activa=Boolean(Number(tree.view.getCellText(tree.currentIndex,tree.columns.getNamedColumn("activa"))));\n'
        s= s+ '     xmlHttp=new XMLHttpRequest();\n'
        s= s+ '     xmlHttp.onreadystatechange=function(){\n'
        s= s+ '         if(xmlHttp.readyState==4){\n'
        s= s+ '             var ale=xmlHttp.responseText;\n'
        s= s+ '             location="cuenta_listado.psp";\n'
        s= s+ '         }\n'
        s= s+ '     }\n'
        s= s+ '     var url="ajax/cuenta_modificar_activa.psp?id_cuentas="+id_cuentas+\'&activa=\'+!activa;\n'
        s= s+ '     xmlHttp.open("GET",url,true);\n'
        s= s+ '     xmlHttp.send(null);\n'
        s= s+ '}\n'
        s= s+ ']]>\n</script>\n\n'                
        s= s+ '<popupset>\n'
        s= s+ '     <popup id="popupCuentas" >\n'
        s= s+ '          <menuitem label="Transferencia bancaria"  onclick="location=\'cuenta_transferencia.psp\';"  class="menuitem-iconic"  image="images/hotsync.png" />\n'
        s=s + '          <menuitem label="Listado de tarjetas"  onclick="location=\'tarjeta_listado.psp\';"   class="menuitem-iconic"  image="images/visa.png"/>\n'
        s= s+ '          <menuseparator/>\n'
        s= s+ '          <menuitem label="Cuenta nueva" oncommand="location=\'cuenta_insertar.psp\'" class="menuitem-iconic"  image="images/item_add.png"/>\n'
#    <menuitem label="Modificar la cuenta"  oncommand='location="cuentas_ibm.psp?id_cuentas=" + idcuenta  + "&amp;ibm=modificar&amp;regresando=0";'   class="menuitem-iconic"  image="images/toggle_log.png"/>
#    <menuitem label="Borrar la cuenta"  oncommand='location="cuentas_ibm.psp?id_cuentas=" + idcuenta  + "&amp;ibm=borrar&amp;regresando=0";'  class="menuitem-iconic" image="images/eventdelete.png"/>
#    <menuitem label="Movimientos de cuenta"  oncommand="location='cuenta_informacion.psp?id_cuentas=' + idcuenta;"/> 
#    <menuseparator/>
        s= s+ '     </popup>\n'
        s= s+ '</popupset>\n'

        s= s+ '<vbox flex="1">\n'
        s= s+ '<tree id="treeCuentas" flex="6"   context="popupCuentas"  onselect="popupCuentas();">\n'
        s= s+ '     <treecols>\n'
        s= s+  '          <treecol id="id" label="Id" hidden="true" />\n'
        s= s+  '          <treecol id="activa" label="Activa" hidden="true" />\n'
        s= s+  '          <treecol id="col_cuenta" label="Cuenta" sort="?col_cuenta"  sortDirection="descending" flex="2"/>\n'
        s= s+  '          <treecol id="col_entidad_bancaria" label="Entidad Bancaria"  sort="?col_entidad_bancaria" sortActive="true"  flex="2"/>\n'
        s= s+  '          <treecol id="col_valor" label="Número de cuenta" flex="2" style="text-align: right" />\n'
        s= s+  '          <treecol id="col_saldo" label="Saldo" flex="1" style="text-align: right"/>\n'
        s= s+  '     </treecols>\n'
        s= s+  '     <treechildren>\n'
        curs=con.Execute(sql);         
        while not curs.EOF:
            row = curs.GetRowAssoc(0)   
            sumsaldos=sumsaldos+ dosdecimales(row['saldo'])
            s= s + '          <treeitem >\n'
            s= s + '               <treerow>\n'
            s= s + '                    <treecell label="'+str(row["id_cuentas"])+ '" />\n'
            s= s + '                    <treecell label="'+str(row["cu_activa"])+ '" />\n'
            s= s + '                    <treecell label="'+ row["cuenta"]+ '" />\n'
            s= s + '                    <treecell label="'+row["entidadesbancaria"]+ '" />\n'
            s= s + '                    <treecell label="'+ str(row["numero_cuenta"])+ '" />\n'
            s= s + '                    '+treecell_euros(row['saldo'])
            s= s + '               </treerow>\n'
            s= s + '          </treeitem>\n'
            curs.MoveNext()     
        s= s + '     </treechildren>\n'
        s= s + '</tree>\n'
        s= s + '<label flex="1"  style="text-align: center;font-weight : bold;" value="Saldo total de todas las cuentas: '+ euros(sumsaldos)+'" />\n'
        s= s + '</vbox>\n'
        curs.Close()
        return s
#
#    def registro(self,id_cuentas):
#        curs = con.Execute('select * from cuentas where id_cuentas='+ str(id_cuentas)); 
#        if curs == None: 
#            print self.cfg.con.ErrorMsg()        
#        row = curs.GetRowAssoc(0)      
#        curs.Close()
#        return row
        
    def modificar(self, id_cuentas, cuenta,  ma_entidadesbancarias,  numero_cuenta):
        sql="update cuentas set cuenta='"+str(cuenta)+"', ma_entidadesbancarias="+str(ma_entidadesbancarias)+", numero_cuenta='"+str(numero_cuenta)+"' where id_cuentas="+ str(id_cuentas)
        try:
            con.Execute(sql);
        except:
            return False
        return True
        
    def modificar_activa(self, id_cuentas,  activa):
        sql="update cuentas set cu_activa="+str(activa)+" where id_cuentas="+ str(id_cuentas)
        curs=con.Execute(sql); 
        return sql

    def saldo(self,id_cuentas,  fecha):
        curs = con.Execute('select sum(importe) as "suma" from opercuentas where ma_cuentas='+ str(id_cuentas) +" and fecha<='"+str(fecha)+"';") 
        if curs == None: 
            print self.cfg.con.ErrorMsg()        
        row = curs.GetRowAssoc(0)      
        if row['suma']==None:
            return 0
        else:
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

    def id_opercuentas_insertado_en_session(self):
        return con.Execute("select currval('seq_opercuentas') as seq;").GetRowAssoc(0)["seq"]

    def xul_listado(self, curs,  id_cuentas,  year,  month):
        primeromes=datetime.date(int(year),  int(month),  1)
        diamenos=primeromes-datetime.timedelta(days=1)      
        saldo=Cuenta().saldo(id_cuentas, diamenos.isoformat())
        s=    '<popupset>\n'
        s= s+ '   <popup id="treepopup">\n'
        s= s+ '      <menuitem label="Nueva operación" oncommand="location=\'cuentaoperacion_insertar.psp?ibm=insertar&amp;regresando=0&amp;id_cuentas='+str(id_cuentas)+';\'" class="menuitem-iconic"  image="images/item_add.png"/>\n'
        s= s+ '      <menuitem label="Modificar la operación"  oncommand=\'location="cuentaoperacion_modificar.psp?id_cuentas=" + idcuenta  + "&amp;ibm=modificar&amp;regresando=0";\'/>\n'
        s= s+ '      <menuitem label="Borrar la operación"  oncommand="borrar();" class="menuitem-iconic" image="images/eventdelete.png"/>\n'
        s= s+ '      <menuseparator/>\n'
        s=s +  '            <menuitem label="Transferencia bancaria"  onclick="location=\'cuenta_transferencia.psp\';"  class="menuitem-iconic"  image="images/hotsync.png" />\n'
        s= s+ '      <menuseparator/>\n'
        s= s+ '      <menuitem label="Operación de tarjeta"   onclick="location=\'tarjeta_listado.psp\';"   class="menuitem-iconic"  image="images/visa.png"/>\n'
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


class CuentaOperacionHeredadaInversion:
    """Clase parar trabajar con las opercuentas generadas automaticamente por los movimientos de las inversiones"""
    def insertar(self,  fecha, lu_conceptos, lu_tiposoperaciones, importe, comentario,id_cuentas,id_operinversiones,id_inversiones):
        sql="insert into tmpinversionesheredada (fecha, lu_conceptos, lu_tiposoperaciones, importe, comentario,ma_cuentas, id_operinversiones,id_inversiones) values ('"+str(fecha)+"', "+str(lu_conceptos)+", "+str(lu_tiposoperaciones)+", "+str(importe)+", '"+str(comentario)+"' ,"+str(id_cuentas)+", "+str(id_operinversiones)+", "+str(id_inversiones)+")"
        con.Execute(sql);


    def actualizar_una_operacion(self,id_operinversiones):
        """Esta función actualiza la tabla tmpinversionesheredada que es una tabla temporal donde 
        se almacenan las opercuentas automaticas por las operaciones con inversiones. Es una tabla 
        que se puede actualizar en cualquier momento con esta función"""

#    //Borra la tabla tmpinversionesheredada
        sqldel="delete from tmpinversionesheredada where id_operinversiones="+str(id_operinversiones)
        resultdel=con.Execute(sqldel);
        row = con.Execute('select * from operinversiones where id_operinversiones='+str(id_operinversiones)).GetRowAssoc(0)
        fecha=row['fecha'];
        importe=row['importe'];
        id_inversiones=row['ma_inversiones'];
        regInversion=Inversion().registro(id_inversiones);
        id_cuentas=regInversion['lu_cuentas']
        comision=row['comision'];
        impuestos=row['impuestos'];
      
#        //Dependiendo del tipo de operaci�n se ejecuta una operaci�n u otra.
        if row['lu_tiposoperaciones']==4:#Compra Acciones
            #Se pone un registro de compra de acciones que resta el saldo de la opercuenta
            CuentaOperacionHeredadaInversion().insertar(fecha, 29, 4, -importe-comision, regInversion['inversione']+". Importe: " + str(importe)+". Comisión: " + str(comision)+ ". Impuestos: " + str(impuestos),id_cuentas,id_operinversiones,id_inversiones);
            #//Si hubiera comisi�n se a�ade la comisi�n.
#            if(comision!=0):
#                CuentaOperacionHeredadaInversion().insertar(fecha, 38, 1, -comision, regInversion['inversione']+". Comisión (Id. id_operinversiones)",id_cuentas,id_operinversiones,id_inversiones)
        elif row['lu_tiposoperaciones']==5:#// Venta Acciones
            #//Se pone un registro de compra de acciones que resta el saldo de la opercuenta
            CuentaOperacionHeredadaInversion().insertar(fecha, 35, 5, importe-comision-impuestos, regInversion['inversione']+". Importe: " + str(importe)+". Comisión: " + str(comision)+ ". Impuestos: " + str(impuestos),id_cuentas,id_operinversiones,id_inversiones);
            #//Si hubiera comisi�n se a�ade la comisi�n.
#            if(comision!=0):
#                CuentaOperacionHeredadaInversion().insertar( fecha, 38, 1, -comision, regInversion['inversione']+". Comisión (Id. id_operinversiones)",id_cuentas,id_operinversiones,id_inversiones);
            #//Si hubiera pago de impuestos se pone
#            if(impuestos!=0):
#                CuentaOperacionHeredadaInversion().insertar(fecha, 37, 1, -impuestos, regInversion['inversione']+". Pago de impuestos (Id. id_operinversiones)",id_cuentas,id_operinversiones,id_inversiones);
        elif row['lu_tiposoperaciones']==6:# // A�adido de Acciones
            #//Si hubiera comisi�n se a�ade la comisi�n.
            if(comision!=0):
                CuentaOperacionHeredadaInversion().insertar(fecha, 38, 1, -comision-impuestos, regInversion['inversione']+". Importe: " + str(importe)+". Comisión: " + str(comision)+ ". Impuestos: " + str(impuestos), id_cuentas,id_operinversiones,id_inversiones);
            #//Si hubiera pago de impuestos se pone
#            if(impuestos!=0):
#                CuentaOperacionHeredadaInversion().insertar(fecha, 37, 1, -impuestos, regInversion['inversione']+". Pago de impuestos (Id. id_operinversiones)",id_cuentas,id_operinversiones,id_inversiones);

  
    #/**
    # * Esta funci�n actualiza la tabla tmpinversionesheredada que es una tabla temporal donde
    # * se almacenan las opercuentas automaticas por las operaciones con inversiones. Es una tabla
    # * que se puede actualizar en cualquier momento con esta funci�n
    # *
    # *  \param con Conector a la base de datos.
    # *  \param id_inversiones Id de la inversi�n
    # */
    def actualizar_una_inversion(self,id_inversiones):
#    //Borra la tabla tmpinversionesheredada
        sqldel="delete from tmpinversionesheredada where id_inversiones="+str(id_inversiones)
        con.Execute(sqldel);

#    //Se cogen todas las operaciones de inversiones de la base de datos
        sql="SELECT * from operinversiones where ma_inversiones="+str(id_inversiones)
        curs=con.Execute(sql); 
        while not curs.EOF:
            row = curs.GetRowAssoc(0)   
            CuentaOperacionHeredadaInversion().actualizar_una_operacion(row['id_operinversiones']);
            curs.MoveNext()     
        curs.Close()


#    /**
#     * Esta funci�n actualiza la tabla tmpinversionesheredada que es una tabla temporal donde
#     * se almacenan las opercuentas automaticas por las operaciones con inversiones. Es una tabla
#     * que se puede actualizar en cualquier momento con esta funci�n
#     *
#     *  \param con Conector a la base de datos.
#     */
    def actualizar_todas(self):
#    //Borra la tabla tmpinversionesheredada
        sqldel="delete from tmpinversionesheredada";
        con.Execute(sqldel);

#    //Se cogen todas las operaciones de inversiones de la base de datos
        sql="SELECT * from operinversiones";
        curs=con.Execute(sql); 
        while not curs.EOF:
            row = curs.GetRowAssoc(0)   
            CuentaOperacionHeredadaInversion().actualizar_una_operacion(row['id_operinversiones']);
            curs.MoveNext()     
        curs.Close()

class Dividendo:
    def insertar(self,fecha,valorxaccion,bruto,retencion,liquido,id_inversiones):
        """Insertar un dividendo y una opercuenta vinculada a la tabla dividendos en el campo id_opercuentas"""
        inv=con.Execute("select * from inversiones where id_inversiones="+ str(id_inversiones)).GetRowAssoc(0)   
        CuentaOperacion().insertar( fecha, 39, 2, liquido, inv['inversione']+" (Bruto="+str(bruto)+"€. Retención="+str(retencion)+"€.)",inv['lu_cuentas'])
        id_opercuentas=con.Execute("select currval('seq_opercuentas') as seq;").GetRowAssoc(0)["seq"]   
        #Añade el dividendo
        sql="insert into dividendos (fecha, valorxaccion, bruto, retencion, liquido, lu_inversiones,id_opercuentas) values ('"+str(fecha)+"', "+str(valorxaccion)+", "+str(bruto)+", "+str(retencion)+", "+str(liquido)+", "+str(id_inversiones)+", "+str(id_opercuentas)+")"
        try:
            con.Execute(sql);
        except:
            return False
        return True


    def borrar(self, id_dividendos):
        """Borra un dividendo, para ello borra el registro de la tabla dividendos 
            y el asociado en la tabla opercuentas"""
        div=con.Execute("select * from dividendos where id_dividendos="+ str(id_dividendos)).GetRowAssoc(0)
        CuentaOperacion().borrar(div['id_opercuentas'])
        sql="delete from dividendos where id_dividendos="+ str(id_dividendos)
        try:
            con.Execute(sql);
        except:
            return False
        return True
        
    def obtenido_mensual(self, ano,  mes):
        """Dividendo cobrado en un año y mes pasado como parámetro, independientemente de si la inversión esta activa o no"""
        sql="select sum(liquido) as liquido from dividendos where date_part('year',fecha) = "+str(ano)+" and date_part('month',fecha)= " + str(mes)
        curs=con.Execute(sql); 
        row = curs.GetRowAssoc(0)   
        curs.Close()
        if row['liquido']==None:
            resultado=0
        else:
            resultado=float(row['liquido'])
        return resultado
        
    def suma_liquido_todos(self, inicio,final):
        sql="select sum(liquido) as suma from dividendos where fecha between '"+inicio+"' and '"+final+"';"
        curs = con.Execute(sql); 
        if curs == None: 
            print self.cfg.con.ErrorMsg()        
        row = curs.GetRowAssoc(0)      
        if row['suma']==None:
            return 0
        else:
            return row['suma'];
            
        
    def xultree(self, sql, id_inversiones):
        sumsaldos=0
        curs=con.Execute(sql); 
        
        s=       '<script>\n<![CDATA[\n'
        s= s+ 'function dividendo_borrar(){\n'
        s= s+ '    var xmlHttp;        \n'
        s= s+ '    var tree = document.getElementById("treeDiv");\n'
        s= s+ '    var id_inversiones='+str(id_inversiones)+';\n'
        s= s+ '    var id_dividendos=tree.view.getCellText(tree.currentIndex,tree.columns.getNamedColumn("id"));\n'
        s= s+ '    var url="ajax/dividendo_borrar.psp?id_dividendos=" + id_dividendos;\n'
        s= s+ '    xmlHttp=new XMLHttpRequest();\n'
        s= s+ '    xmlHttp.onreadystatechange=function(){\n'
        s= s+ '        if(xmlHttp.readyState==4){\n'
        s= s+ '            var ale=xmlHttp.responseText;\n'
        s= s+ '            location="inversion_informacion.psp?id_inversiones="+ id_inversiones;\n'
        s= s+ '        }\n'
        s= s+ '    }\n'
        s= s+ '    xmlHttp.open("GET",url,true);\n'
        s= s+ '    xmlHttp.send(null);\n'
        s= s+ '}\n'
        s= s+ ']]>\n</script>\n\n'

        s= s+ '<vbox flex="1">\n'
        s= s+ '<popupset>\n'
        s= s+ '    <popup id="divpopup" >\n'  
        s= s+ '        <menuitem label="Nuevo dividendo" oncommand="location=\'dividendo_insertar.psp?id_inversiones=\' +'+str(id_inversiones)+' ;"  class="menuitem-iconic"  image="images/item_add.png" />\n'
        s= s+ '        <menuitem label="Borrar el dividendo"  oncommand="dividendo_borrar();"   class="menuitem-iconic"  image="images/eventdelete.png"/>\n'
        s= s+ '    </popup>\n'
        s= s+ '</popupset>\n'
        s=s+ '<tree id="treeDiv" flex="3" tooltiptext="Sólo se muestran los dividendos desde la primera operación actual, no desde la primera operación histórica" context="divpopup">\n'
        s=s+ '    <treecols>\n'
        s=s+ '        <treecol id="id" label="id" flex="1" hidden="true"/>\n'
        s=s+ '        <treecol label="Fecha" flex="1"  style="text-align: center"/>\n'
        s=s+ '        <treecol label="Cuenta cobro" flex="2" style="text-align: left" />\n'
        s=s+ '        <treecol label="Liquido" flex="1" style="text-align: right"/>\n'
        s=s+ '    </treecols>\n'
        s=s+ '    <treechildren tooltiptext="Sólo se muestran los dividendos desde la primera operación actual, no desde la primera operación histórica">\n'
        while not curs.EOF:
            row = curs.GetRowAssoc(0)   
            sumsaldos=sumsaldos+dosdecimales(row['liquido'])
            s=s+ '        <treeitem>\n'
            s=s+ '            <treerow>\n'
            s=s+ '                <treecell label="'+ str(row["id_dividendos"])+ '" />\n'
            s=s+ '                <treecell label="'+ str(row["fecha"])[:-12]+ '" />\n'
            s=s+ '                <treecell label="'+ row["cuenta"]+ '" />\n'
            s=s+ '                '+ treecell_euros(row['liquido']);
            s=s+ '            </treerow>\n'
            s=s+ '        </treeitem>\n'
            curs.MoveNext()     
        curs.Close()
      
        s=s+ '    </treechildren>\n'
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

    def cmb_tpcvariable(self, name,   selected,  js=True):
        jstext=""
        if js:
            jstext= ' oncommand="'+name+'_submit();"'
        s= '<menulist id="'+name+'" '+jstext+' align="center">\n'
        s=s + '      <menupopup align="center">\n';
        for i in (-100, 0, 50, 100) :
            if i==int(selected):
                s=s +  '       <menuitem label="'+utf82xul(self.nombre_tpcvariable(i))+'" value="'+str(i)+'" selected="true"/>\n'
            else:
                s=s +  '       <menuitem label="'+utf82xul(self.nombre_tpcvariable(i))+'" value="'+str(i)+'"/>\n'
        s=s +  '     </menupopup>\n'
        s=s + '</menulist>\n'
        return s

    def cursor_listado(self, inactivas,  fecha):
        if inactivas==True:
            sql="select id_inversiones, in_activa, inversione, entidadesbancaria, inversiones_saldo(id_inversiones,'"+str(fecha)+"') as saldo, inversion_actualizacion(id_inversiones,'"+str(fecha)+"') as actualizacion, inversion_pendiente(id_inversiones,'"+str(fecha)+"')  as pendiente, inversion_invertido(id_inversiones,'"+str(fecha)+"')  as invertido from inversiones, cuentas, entidadesbancarias where cuentas.ma_entidadesbancarias=entidadesbancarias.id_entidadesbancarias and cuentas.id_cuentas=inversiones.lu_cuentas order by inversione;"

        else:
            sql="select id_inversiones, in_activa, inversione, entidadesbancaria, inversiones_saldo(id_inversiones,'"+str(fecha)+"') as saldo, inversion_actualizacion(id_inversiones,'"+str(fecha)+"') as actualizacion, inversion_pendiente(id_inversiones,'"+str(fecha)+"')  as pendiente,  inversion_invertido(id_inversiones,'"+str(fecha)+"')  as invertido from inversiones, cuentas, entidadesbancarias where cuentas.ma_entidadesbancarias=entidadesbancarias.id_entidadesbancarias and cuentas.id_cuentas=inversiones.lu_cuentas and in_activa='t' order by inversione;"
        return con.Execute(sql); 
            
    def insertar(self,  inversione,  compra,  venta,  tpcvariable,  lu_cuentas):
        sql="insert into inversiones (inversione, compra, venta, tpcvariable, lu_cuentas, in_activa, cotizamercado) values ('"+inversione+"', "+str(compra)+", "+str(venta)+", "+str(tpcvariable)+", "+str(lu_cuentas)+", true, true);"
        curs=con.Execute(sql); 
        return sql            
        
    def modificar(self, id_inversiones, inversione,  compra,  venta,  tpcvariable,  lu_cuentas):
        sql="update inversiones set inversione='"+inversione+"', compra="+str(compra)+", venta="+str(venta)+", tpcvariable="+str(tpcvariable)+", lu_cuentas="+str(lu_cuentas)+" where id_inversiones="+ str(id_inversiones)
        curs=con.Execute(sql); 
        return sql
        
    def modificar_activa(self, id_inversiones,  activa):
        sql="update inversiones set in_activa="+str(activa)+" where id_inversiones="+ str(id_inversiones)
        curs=con.Execute(sql); 
        return sql
        
    def nombre(self, id_inversiones):
        sql="select inversione from inversiones where id_inversiones="+ str(id_inversiones)
        curs=con.Execute(sql); 
        row = curs.GetRowAssoc(0)   
        return row["inversione"]

    def nombre_tpcvariable(self,  tpcvariable):
        if tpcvariable==-100:
            return "ETF Inversos"
        if tpcvariable==0:
            return "Fondos de dinero y depósitos"
        if tpcvariable==50:
            return "P. Pensiones e inversiones hasta un 50% en renta variable, fondos alternativos y renta fija"
        if tpcvariable==100:
            return "P. Pensiones e inversiones hasta un 100% en renta variable y acciones"
        return None
            
    def numero_acciones(self, id_inversiones, fecha):
        resultado=0;
        sql="SELECT Acciones from operinversiones where ma_Inversiones="+str(id_inversiones)+" and fecha<='"+str(fecha)+"'"
        curs=con.Execute(sql); 
        while not curs.EOF:
            row = curs.GetRowAssoc(0)   
            resultado=resultado+ row['acciones']
            curs.MoveNext()     
        curs.Close()
        return resultado

    def registro(self, id_inversiones):
        sql="select * from inversiones where id_inversiones="+ str(id_inversiones)
        curs=con.Execute(sql); 
        row = curs.GetRowAssoc(0)   
        return row
        
    def xultree_compraventa(self):
        sql="select id_inversiones, inversione, entidadesbancaria,  inversion_actualizacion(id_inversiones,'"+str(datetime.date.today())+"') as actualizacion, compra, venta from inversiones, cuentas, entidadesbancarias where venta<> compra and in_activa=true and cuentas.ma_entidadesbancarias=entidadesbancarias.id_entidadesbancarias and cuentas.id_cuentas=inversiones.lu_cuentas order by inversione;"
        curs=con.Execute(sql); 
        s= '<vbox flex="1">\n'
        s= s+ '<popupset>\n'
        s= s+ '<popup id="treepopup" >\n'   
        s= s+ '    <menuitem label="Actualizar el valor" oncommand="location=\'inversion_actualizacion.psp?id_inversiones=\' + id_inversiones;"  class="menuitem-iconic"  image="images/hotsync.png" />\n'
        s= s+ '    <menuitem label="Modificar la inversión"  oncommand="location=\'inversion_modificar.psp?id_inversiones=\' + id_inversiones;"   class="menuitem-iconic"  image="images/edit.png" />\n'
        s= s+ '<menuitem label="Estudio de la inversión"  oncommand="location=\'inversion_informacion.psp?id_inversiones=\' + id_inversiones;"  class="menuitem-iconic"  image="images/toggle_log.png" />\n'
        s= s+ '</popup>\n'
        s= s+ '</popupset>\n'

        s= s+ '<tree id="tree" flex="6"   context="treepopup"  onselect="tree_getid();">\n'
        s= s+ '<treecols>\n'
        s= s+  '<treecol label="Id" hidden="true" />\n'
        s= s+  '<treecol label="Inversión" flex="2"/>\n'
        s= s+  '<treecol label="Banco" flex="2"/>\n'
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
            if tpcc>0:
                prop=' properties="rowsoftred"'
            elif tpcv<5:
                prop=' properties="rowsoftgreen"'
            else:
                prop=''
            s= s + '<treerow'+prop+'>\n'
            s= s + '<treecell label="'+str(row["id_inversiones"])+ '" />\n'
            s= s + '<treecell label="'+str(row["inversione"])+ '" />\n'
            s= s + '<treecell label="'+str(row["entidadesbancaria"])+ '" />\n'
            s= s + treecell_euros(row["actualizacion"],  3)
            s= s + treecell_euros( row["compra"] , 3)
            s= s + treecell_euros( row["venta"],  3)
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
        s= s+  '<treecol id="id" label="id" hidden="true" />\n'
        s= s+  '<treecol id="activa" label="activa" hidden="true" />\n'
        s= s+  '<treecol id="inversion" label="Inversión" sort="?col_inversion" sortActive="true" sortDirection="descending" flex="2"/>\n'
        s= s+  '<treecol id="col_entidad_bancaria" label="Entidad Bancaria"  sort="?col_entidad_bancaria" sortActive="true" sortDirection="descending" flex="2"/>\n'
        s= s+  '<treecol id="col_valor" label="Valor Acción" flex="2" style="text-align: right" />\n'
        s= s+  '<treecol id="col_valor" label="Saldo" flex="2" style="text-align: right" />\n'
        s= s+  '<treecol id="col_saldo" label="Pendiente" flex="1" style="text-align: right"/>\n'
        s= s+  '<treecol label="Invertido" hidden="true"  flex="1" style="text-align: right" />\n'
        s= s+  '<treecol id="col_saldo" label="Rendimiento"   sort="?Rendimiento" sortActive="true" sortDirection="descending" flex="1" style="text-align: right"/>\n'
        s= s+  '</treecols>\n'
        s= s+  '<treechildren>\n'
        while not curs.EOF:
            row = curs.GetRowAssoc(0)   
            sumsaldos=sumsaldos+ dosdecimales(row['saldo'])
            sumpendiente=sumpendiente+dosdecimales(row['pendiente'])
            s= s + '<treeitem>\n'
            s= s + '<treerow>\n'
            s= s + '<treecell label="'+str(row["id_inversiones"])+ '" />\n'
            s= s + '<treecell label="'+str(row["in_activa"])+ '" />\n'
            s= s + '<treecell label="'+str(row["inversione"])+ '" />\n'
            s= s + '<treecell label="'+ row["entidadesbancaria"]+ '" />\n'
            s= s + treecell_euros(row["actualizacion"], 3)
            s= s + treecell_euros(row['saldo'])
            s= s + treecell_euros(row['pendiente'])
            s= s + treecell_euros(row['invertido'])
            if row['saldo']==0 or row['invertido']==0:
                tpc=0
            else:
                tpc=100*row['pendiente']/row['invertido']
            s= s + treecell_tpc(tpc)
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
        delete="delete from actuinversiones where ma_inversiones="+str(id_inversiones)+" and fecha ='"+str(fecha)+"';"
        con.Execute(delete);
        sql="insert into actuinversiones (fecha,ma_inversiones,actualizacion) values ('"+ str(fecha) +"',"+str(id_inversiones)+","+str(valor)+")";
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
        if curs.RecordCount()==0:
            resultado.append("1900-1-1")
            resultado.append(0)
        else:
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

class InversionOperacion:
    def borrar(self,  id_operinversiones,  id_inversiones):
        sql="delete from operinversiones where id_operinversiones="+ str(id_operinversiones);
        mylog(sql)
        try:
            con.Execute(sql);
        except:
            return False
        InversionOperacionHistorica().actualizar (id_inversiones);
        CuentaOperacionHeredadaInversion().actualizar_una_inversion(id_inversiones)#Es una inversion ya que la id_operinversion ya no existe. Se ha borrado
        return True
        
    def insertar(self,  fecha,  lu_tiposoperaciones,  importe, acciones,  impuestos,  comision,    comentario, valor_accion,  ma_inversiones):
        sql="insert into operinversiones(fecha,  lu_tiposoperaciones,  importe, acciones,  impuestos,  comision,    comentario, valor_accion,  ma_inversiones) values ('" + str(fecha) + "'," + str(lu_tiposoperaciones) +","+str(importe)+","+ str(acciones) +","+ str(impuestos) +","+ str(comision) +", '"+ str(comentario)+"', "+str(valor_accion)+","+ str(ma_inversiones)+');'
        try:
            con.Execute(sql);
        except:
            return False
#        id_operinversiones=con.Execute("select currval('seq_operinversiones') as seq;").GetRowAssoc(0)["seq"]   
        #//Funcion que actualiza la tabla tmpoperinversiones para ver operinversiones activas
        InversionOperacionHistorica().actualizar (ma_inversiones)
        #//Se actualiza la operinversion una funci<F3>n en tmpinversionesheredada que se refleja en opercuentas.
#        CuentaOperacionHeredadaInversion().actualizar_una_operacion(id_operinversiones)
        CuentaOperacionHeredadaInversion().actualizar_una_inversion(ma_inversiones)
        return True
        
    def referencia_ibex35(self, fecha):
        sql="select cierre from ibex35 where fecha<='"+str(fecha) + "' order by fecha desc limit 1"
        curs=con.Execute(sql)
        if curs.RecordCount()==0:
            return 0
        else:
            row = curs.GetRowAssoc(0)   
            return row['cierre']

class InversionOperacionHistorica:
    def actualizar(self, id_inversiones):
        #Borra las tmpooperinversiones de la inversión que existan
        sql="delete from tmpoperinversioneshistoricas where ma_inversiones="+str(id_inversiones)
        curs=con.Execute(sql)
        sql="delete from tmpoperinversiones where ma_Inversiones="+str(id_inversiones)
        curs=con.Execute(sql)
        InversionOperacionHistorica().aux_copiando_operinversiones_a_tmpoperinversiones(id_inversiones)
        i=0
        while (InversionOperacionHistorica().aux_quitando_negativos(id_inversiones)!=True):#Bucle recursivo.
            i=i+1
            
    def actualizar_todas(self):
#    //Se cogen todas las operaciones de inversiones de la base de datos
        sql="SELECT * from inversiones";
        curs=con.Execute(sql); 
        while not curs.EOF:
            row = curs.GetRowAssoc(0)   
            self.actualizar(row['id_inversiones']);
            curs.MoveNext()     
        curs.Close()

#/**
# * Funci�n que auxiliar que utiliza actualizar y va quitando negativos de la tabla tmpoper
# * inversiones de forma recursiva hasta que no quede ninguno. Mientras se van insertando en
# * tmpoperi0nverhistoricos.
# *
# * Devuelve false si hay negativos y true si ya no hay.
# *
# * OJO DEBE ESTAR MUY BIEN LOS DECIMALES O PETARA.
# */
    def aux_quitando_negativos(self,id_inversiones):
        #Mira si hay negativos y sino sale
        sqlneg="SELECT * from tmpoperinversiones where ma_Inversiones="+str(id_inversiones)+" and acciones <0 order by fecha";
        resultneg=con.Execute(sqlneg)
        if resultneg.RecordCount()==0: #Por si no hubiera negativos
            return True;
  
        rowneg= resultneg.GetRowAssoc(0)   
        accionesneg=rowneg['acciones'];
        actuventa=rowneg['valor_accion'];
    
        sqlpos="select * from tmpoperinversiones where ma_Inversiones="+str(id_inversiones)+" and acciones >0 order by fecha";
        resultpos=con.Execute(sqlpos)
        accionespos=0;
        while not resultpos.EOF:
            rowpos = resultpos.GetRowAssoc(0)   
            accionespos=rowpos['acciones'];
            dif=accionespos-(-accionesneg);
            if dif>=-0.1 and dif<=0.1: #Si es 0 se inserta el historico que coincide con la venta y se borra el registro negativo
                InversionOperacionHistorica().insertar( rowneg['ma_operinversiones'], rowpos['fecha'], rowneg['fecha'], rowneg['lu_tiposoperaciones'], rowneg['ma_inversiones'], accionesneg, -accionesneg*actuventa, rowneg['impuestos'], rowneg['comision'], rowpos['valor_accion'], rowneg['valor_accion'])#; //Se pone acciones neg porque puede venir de <0.
                InversionOperacionTemporal().borrar(rowneg["id_tmpoperinversiones"]);
                InversionOperacionTemporal().borrar(rowpos["id_tmpoperinversiones"]);
                break
            elif dif<-0.1:#   //Si es <0 es decir hay más acciones negativas que positivas. Se debe introducir en el historico la tmpoperinversion y borrarlo y volver a recorrer el bucle. Restando a accionesneg las acciones ya apuntadas en el historico
                InversionOperacionHistorica().insertar( rowpos['ma_operinversiones'], rowpos['fecha'], rowneg['fecha'], rowneg['lu_tiposoperaciones'], rowpos['ma_inversiones'], -rowpos['acciones'],  rowpos['acciones']*actuventa, rowneg['impuestos'], rowneg['comision'],rowpos['valor_accion'], rowneg['valor_accion']);
                InversionOperacionTemporal().borrar(rowpos["id_tmpoperinversiones"]);
                accionesneg=accionesneg+accionespos#ya que accionesneg es negativo
            elif(dif>0.1):# //Cuando es >0 es decir hay mas acciones positivos se a�ade el registro en el historico con los datos de la operaci�n negativa en su totalidad. Se borra el registro de negativos y de positivos en tmpoperinversiones y se inserta uno con los datos positivos menos lo quitado por el registro negativo. Y se sale del bucle. //Aqu� no se insert la comisi�n porque solo cuando se acaba las acciones positivos   
                InversionOperacionHistorica().insertar( rowpos['ma_operinversiones'], rowpos['fecha'], rowneg['fecha'], rowneg['lu_tiposoperaciones'], rowneg['ma_inversiones'], accionesneg, -accionesneg*actuventa, rowneg['impuestos'], rowneg['comision'],rowpos['valor_accion'], rowneg['valor_accion'])#;//Se pone acciones neg porque puede venir de <0.
                InversionOperacionTemporal().borrar(rowpos["id_tmpoperinversiones"]);
                InversionOperacionTemporal().borrar(rowneg["id_tmpoperinversiones"]);
                InversionOperacionTemporal().insertar(rowpos['ma_operinversiones'],rowpos['ma_inversiones'], rowpos['fecha'], rowpos['acciones']-(-accionesneg), rowpos['lu_tiposoperaciones'],(rowpos['acciones']-(-accionesneg))*actuventa,0,0,rowpos['valor_accion']);
                break;
            resultpos.MoveNext()     
        resultpos.Close()
        #Mira si hay negativos y sino sale debe hacerse otra vez porque aveces se inserta un negativo
        sqlneg="SELECT * from tmpoperinversiones where ma_Inversiones="+str(id_inversiones)+" and acciones <0 order by fecha";
        resultneg=con.Execute(sqlneg)   
        if resultneg.RecordCount()==0:#Para ver si era el ultimo
            return True;
        else: 
            return False;

#/**
# * Funci�n que auxiliar que utiliza actualizar y copia la tabla operinversiona a tmpoper
# * inversiones para luego trabajaor con ellos.
# */
    def aux_copiando_operinversiones_a_tmpoperinversiones(self, id_inversiones):
        sql="SELECT * from operinversiones where ma_Inversiones="+str(id_inversiones)+" order by fecha";
        curs=con.Execute(sql); 
        while not curs.EOF:
            row = curs.GetRowAssoc(0)   
            InversionOperacionTemporal().insertar(row['id_operinversiones'],row['ma_inversiones'], row['fecha'],row['acciones'],row['lu_tiposoperaciones'],row['importe'],row['impuestos'],row['comision'],row['valor_accion']);
            curs.MoveNext()     
        curs.Close()

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

    def insertar(self, ma_operinversiones,fecha_inicio, fecha_venta, lu_tiposoperaciones, id_inversiones, acciones, importe, impuestos, comision, valor_accion_compra, valor_accion_venta):
# id_cuentas=Inversion::id_cuentas(con, id_inversiones);
# nombre_inversion=Inversion::nombre(con,id_inversiones);
        sql="insert into tmpoperinversioneshistoricas (fecha_inicio, fecha_venta,ma_operinversiones, lu_tiposoperaciones, ma_inversiones, acciones, importe, impuestos, comision, valor_accion_compra, valor_accion_venta) values ('"+str(fecha_inicio)+"', '"+str(fecha_venta)+"', "+str(ma_operinversiones)+", "+str(lu_tiposoperaciones)+", "+str(id_inversiones)+", "+str(acciones)+", "+str(importe)+", "+str(impuestos)+", "+str(comision)+", "+str(valor_accion_compra)+", "+str(valor_accion_venta)+")";
        curs=con.Execute(sql); 
        
    def rendimiento_total(self, id_tmpoperinversioneshistoricas):
        """
            Si primera es 0 por ejempleo acciones de ampliaciones de capital que no cuestan nada devuelve 100
        """ 
        sql="SELECT fecha_inicio, fecha_venta, valor_accion_compra, valor_accion_venta,ma_inversiones from tmpoperinversioneshistoricas where id_tmpoperinversioneshistoricas= "+ str(id_tmpoperinversioneshistoricas)
        curs=con.Execute(sql); 
        row = curs.GetRowAssoc(0)   
        id_inversiones=row['ma_inversiones'];
        primera=row['valor_accion_compra'];
        ultima=row['valor_accion_venta'];
        if primera==0:
            return 100
        Rendimiento=(ultima-primera)*100/primera;
        return Rendimiento;
    def xultree(self, sql):
        """El SQL deberá ser del tipo "SELECT * from tmpoperinversiones"""  
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
        s=s+ '        <tree id="treeIOH" flex="3" context="treepopup" >\n'
        s=s+ '          <treecols>\n'
        s=s+ '    <treecol id="id" label="id" flex="1" hidden="true"/>\n'
        s=s+ '    <treecol label="Fecha" flex="1"  style="text-align: center"/>\n'
        s=s+ '    <treecol label="Acciones" flex="1" style="text-align: right" />\n'
        s=s+ '    <treecol label="Valor compra" flex="1" style="text-align: right"/>\n'
        s=s+ '    <treecol label="Importe" flex="1" style="text-align: right"/>\n'
        s=s+ '    <treecol label="Comisión" flex="1" style="text-align: right"/>\n'
        s=s+ '    <treecol label="Impuestos" flex="1" style="text-align: right"/>\n'
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
            s=s+ '       <treecell label="'+ str(row["id_operinversiones"])+ '" />\n'
            s=s+ '       <treecell label="'+ str(row["fecha"])[:-12]+ '" />\n'
            s=s+ '       <treecell label="'+ str(row["acciones"])+ '" />\n'
            s=s+        treecell_euros(row['valor_accion']);
            s=s+        treecell_euros(importe);
            s=s+        treecell_euros(row['comision']);
            s=s+        treecell_euros(row['impuestos']);
            s=s+ '      </treerow>\n'
            s=s+ '    </treeitem>\n'
            curs.MoveNext()     
        curs.Close()
      
        s=s+ '  </treechildren>\n'
        s=s+ '</tree>\n'
        s= s + '</vbox>\n'
        return s
        

class InversionOperacionTemporal:
    def borrar(self, id_tmpoperinversiones):
        sql="delete from tmpoperinversiones where id_tmpoperinversiones="+str(id_tmpoperinversiones)
        curs=con.Execute(sql); 

    def fecha_primera_operacion(self,id_inversiones):
        sql="SELECT fecha  from tmpoperinversiones where ma_inversiones="+str(id_inversiones) + " order by fecha limit 1";
        curs=con.Execute(sql); 
        if curs.RecordCount()>0:
            row = curs.GetRowAssoc(0)   
            return row['fecha'];    
        else:
            return None

    def insertar(self, ma_operinversiones,id_inversiones, fecha,acciones,lu_tiposoperaciones,importe,impuestos,comision,valor_accion):
        sql="insert into tmpoperinversiones (ma_operinversiones,ma_inversiones,fecha, acciones,lu_tiposoperaciones,importe,impuestos, comision, valor_accion) values ("+str(ma_operinversiones)+", "+str(id_inversiones)+",'"+str(fecha)+"',"+str(acciones)+", "+str(lu_tiposoperaciones)+","+str(importe)+","+str(impuestos)+","+str(comision)+", "+str(valor_accion)+")";
        curs=con.Execute(sql); 

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
        s=s+ '    <treecol label="Ref. Ibex35" flex="1" style="text-align: right"/>\n'
        s=s+ '  </treecols>\n'
        s=s+ '  <treechildren>\n'
        while not curs.EOF:
            row = curs.GetRowAssoc(0)   
            fecha=row["fecha"];
            acciones=row['acciones'];
            actualizacion=row['valor_accion'];
            importe=acciones*actualizacion;
            actualizacionxacciones=actualizacion*acciones;
            pendiente=InversionOperacionTemporal().pendiente_consolidar(row['id_tmpoperinversiones'],row['ma_inversiones'], datetime.date.today());
            sumacciones=sumacciones+acciones;
            sumimporte=sumimporte+importe;
            sumpendiente=sumpendiente+pendiente;
            rendimientoanual=InversionOperacionTemporalRendimiento().anual( row['id_tmpoperinversiones'], row['ma_inversiones'], datetime.date.today().year);
            rendimientototal=InversionOperacionTemporalRendimiento().total( row['id_tmpoperinversiones'], row['ma_inversiones']);     
            #tae
            dias=(datetime.date.today()-datetime.date(row["fecha"].year, row["fecha"].month, row["fecha"].day)).days 
            if dias==0:
                tae=rendimientototal*365/1
            else:
                tae=rendimientototal*365/dias                

            sumactualizacionesxacciones=sumactualizacionesxacciones+actualizacionxacciones;
            sumrendimientosanualesxacciones=sumrendimientosanualesxacciones+rendimientoanual*acciones;
            sumrendimientostotalesxacciones=sumrendimientostotalesxacciones+rendimientototal*acciones;
            sumrendimientosanualesponderadosxacciones=sumrendimientosanualesponderadosxacciones+tae*acciones;
            s=s+ '    <treeitem>\n'
            s=s+ '      <treerow>\n'
            s=s+ '       <treecell label="'+ str(row["fecha"])[:-12]+ '" />\n'
            s=s+ '       <treecell label="'+ str(row["acciones"])+ '" />\n'
            s=s+        treecell_euros(row['valor_accion']);
            s=s+        treecell_euros(importe);
            s=s+        treecell_euros(pendiente)
            s=s+        treecell_tpc(rendimientoanual)
            s=s+        treecell_tpc(tae)
            s=s+        treecell_tpc(rendimientototal)
            s=s+        treecell_euros(InversionOperacion().referencia_ibex35(fecha))
            s=s+ '      </treerow>\n'
            s=s+ '    </treeitem>\n'
            curs.MoveNext()     
        curs.Close()
        if sumacciones>0:
            valormedio=sumactualizacionesxacciones/sumacciones
        else:
            valormedio=0
        s=s+ '  </treechildren>\n'
        s=s+ '</tree>\n'
        
        s= s + '<label flex="0"  style="text-align: center;font-weight : bold;" value="Invertidos '+ euros(sumimporte)+' con un total de '+str(int(sumacciones))+' acciones y un valor medio de '+euros(valormedio)+'"/>\n'        
        s= s + '<label flex="0"  style="text-align: center;font-weight : bold;" value="Saldo pendiente '+ euros(sumpendiente)+'. " />\n'        
        s= s + '</vbox>\n'
        return s
        
    def xultree_referenciaibex(self, sql):
        # fecha
        # inversione
        # importe
        # ibex35
        sumimporte=0;
        curs=con.Execute(sql); 
        s=     ' <tree id="tree" flex="3" >\n'
        s=s+ '  <treecols>\n'
        s=s+ '    <treecol label="Fecha" flex="1"  style="text-align: center"/>\n'
        s=s+ '    <treecol label="Inversión" flex="1" style="text-align: left" />\n'
        s=s+ '    <treecol label="Importe" flex="1" style="text-align: right"/>\n'
        s=s+ '    <treecol label="Ref. Ibex35" flex="1" style="text-align: right"/>\n'
        s=s+ '  </treecols>\n'
        s=s+ '  <treechildren>\n'
        while not curs.EOF:
            row = curs.GetRowAssoc(0)   
            sumimporte=sumimporte+row['importe'];
            s=s+ '    <treeitem>\n'
            s=s+ '      <treerow>\n'
            s=s+ '       <treecell label="'+ str(row["fecha"])[:-12]+ '" />\n'
            s=s+ '       <treecell label="'+ str(row["inversione"])+ '" />\n'
            s=s+        treecell_euros(row['importe']);
            s=s+        treecell_euros(row['ibex35']);
            s=s+ '      </treerow>\n'
            s=s+ '    </treeitem>\n'
            curs.MoveNext()     
        curs.Close()
        s=s+ '    <treeitem>\n'
        s=s+ '      <treerow>\n'
        s=s+ '       <treecell label="" />\n'
        s=s+ '       <treecell label="TOTAL" />\n'
        s=s+        treecell_euros(sumimporte);
        s=s+ '       <treecell label="" />\n'
        s=s+ '      </treerow>\n'
        s=s+ '    </treeitem>\n'        
        s=s+ '  </treechildren>\n'
        s=s+ '</tree>\n'
        return s
    
    def actualizar(self, id_inversiones):
        sql="delete from tmpoperinversiones where ma_Inversiones="+ str(id_inversiones)+";"
        curs=con.Execute(sql)
        sql="delete from tmpoperinversioneshistoricas where ma_Inversiones="+str(id_inversiones)+";"
        curs=con.Execute(sql)
        #Calculo el número de acciones con un sum de las acciones
        numeroacciones=Inversion().numero_acciones(id_inversiones,datetime.date.today())
        #Voy recorriendo el array y a ese total le voy restando las positivas por orden de fecha descendente y las voy insertando en tmpooperinversiones
        sql="SELECT * from operinversiones where ma_Inversiones="+str(id_inversiones)+" and acciones >=0 order by fecha desc";
        curs=con.Execute(sql); 
        while not curs.EOF: #Cuando llega a <=0 me paro
            row = curs.GetRowAssoc(0)       
            numeroacciones=numeroacciones-row['acciones'];
            if (numeroacciones==0.0):   #Si es 0 queda como está
                InversionOperacionTemporal().insertar(row["id_operinversiones"],row["ma_inversiones"], row["fecha"],row["acciones"],row['lu_tiposoperaciones'],row['importe'],row['impuestos'],row['comision'],row['valor_accion'])
                break;
            else:
                if numeroacciones<0:   #Si es <0 le sumo le quito al numero de acciones de esa inversión la parte negativa
                    InversionOperacionTemporal().insertar(row['id_operinversiones'],row['ma_inversiones'], row['fecha'],row['acciones']+numeroacciones,row['lu_tiposoperaciones'],row['importe'],row['impuestos'],row['comision'],row['valor_accion']);
                    break;
                else: #Cuando es >0
                    InversionOperacionTemporal().insertar(row["id_operinversiones"],row["ma_inversiones"], row["fecha"],row["acciones"],row['lu_tiposoperaciones'],row['importe'],row['impuestos'],row['comision'],row['valor_accion'])
            curs.MoveNext()     
        curs.Close()

    def actualizar_todas(self):
        sql="SELECT id_inversiones from inversiones";
        curs=con.Execute(sql); 
        while not curs.EOF:
            row = curs.GetRowAssoc(0)   
            actualizar(row['id_inversiones'])
            curs.MoveNext()     
        curs.Close()
      
class InversionOperacionTemporalRendimiento:
    def anual(self,id_tmpoperinversiones,id_inversiones,year):
        sql="SELECT fecha,valor_accion from tmpoperinversiones where id_tmpoperinversiones="+str(id_tmpoperinversiones)
        curs=con.Execute(sql); 
        row = curs.GetRowAssoc(0)   
        curs.Close()
        anobd=row['fecha'].year
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
        ultima=InversionActualizacion().ultima(id_inversiones,datetime.date.today().year);
        Rendimiento=(ultima[1]-primera)*100/primera;
        return Rendimiento;



class InversionRendimiento:
    def personal_anual(self, id_inversiones,ano):
#        if (InversionOperacionTemporal().count(id_inversiones)==0) return 0;
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
            sql="select id_tarjetas, lu_cuentas, tarjeta, cuenta, numero, pago_diferido, saldomaximo from tarjetas,cuentas where tarjetas.lu_cuentas=cuentas.id_cuentas order by tarjetas.tarjeta"
        else:
            sql="select id_tarjetas, lu_cuentas, tarjeta, cuenta, numero, pago_diferido, saldomaximo from tarjetas,cuentas where tarjetas.lu_cuentas=cuentas.id_cuentas and tarjetas.tj_activa=true order by tarjetas.tarjeta"
        return con.Execute(sql); 

    def insertar(self,  lu_cuentas,  tarjeta,  numero, pago_diferido, saldomaximo, tj_activa):
        sql="insert into tarjetas (lu_cuentas, tarjeta, numero, pago_diferido, saldomaximo, tj_activa) values ("+ str(lu_cuentas) +", '"+str(tarjeta)+"', '"+str(numero)+"', "+str(pago_diferido)+", " + str(saldomaximo) + ", "+str(tj_activa)+");"
        try:
            con.Execute(sql);
        except:
            return False
        return True

    def saldo_pendiente(self,id_tarjetas):
        sql='select sum(importe) as suma from opertarjetas where ma_tarjetas='+ str(id_tarjetas) +' and pagado=false'
        resultado=con.Execute(sql) .GetRowAssoc(0)["suma"]
        if resultado==None:
            return 0
        return resultado

    def xul_listado(self, curs):
        s= '<popupset>\n'
        s= s+ '   <popup id="treepopup" >\n'
        s= s+ '      <menuitem label="Añadir nueva tarjeta"  oncommand=\'location="tarjeta_insertar.psp";\'   class="menuitem-iconic"  image="images/item_add.png"/>\n'
        s= s+ '      <menuitem label="Modificar la tarjeta"   class="menuitem-iconic"  image="images/toggle_log.png"/>\n'
        s= s+ '      <menuitem label="Borrar la tarjeta"  class="menuitem-iconic" image="images/eventdelete.png"/>\n'
        s= s+ '      <menuseparator/>'
        s= s+ '      <menuitem id="Movimientos"/>\n'
        s= s+ '   </popup>\n'
        s= s+ '</popupset>\n'
        
        s= s+ '<tree id="tree" enableColumnDrag="true" flex="6"   context="treepopup"  onselect="tree_getid();">\n'
        s= s+ '<treecols>\n'
        s= s+  '<treecol id="id" label="id" hidden="true" />\n'
        s= s+  '<treecol id="id_cuentas" label="id_cuentas" hidden="true" />\n'
        s= s+  '<treecol label="Nombre Tarjeta"  flex="2"/>\n'
        s= s+  '<treecol label="Cuenta asociada" flex="2"/>\n'
        s= s+  '<treecol label="Número de tarjeta" flex="2" style="text-align: right" />\n'
        s= s+  '<treecol type="checkbox" id="diferido" label="Pago diferido" flex="1" style="text-align: right"/>\n'
        s= s+  '<treecol label="Saldo máximo" flex="1" style="text-align: right"/>\n'
        s= s+  '<treecol label="Saldo pendiente" flex="1" style="text-align: right"/>\n'
        s= s+  '</treecols>\n'
        s= s+  '<treechildren>\n'
        while not curs.EOF:
            row = curs.GetRowAssoc(0)   
            s= s + '<treeitem>\n'
            s= s + '<treerow>\n'
            s= s + '<treecell label="'+str(row["id_tarjetas"])+ '" />\n'
            s= s + '<treecell label="'+str(row["lu_cuentas"])+ '" />\n'
            s= s + '<treecell label="'+ row["tarjeta"]+ '" />\n'
            s= s + '<treecell label="'+row["cuenta"]+ '" />\n'
            s= s + '<treecell label="'+ str(row["numero"])+ '" />\n'
            s= s + '<treecell properties="'+str(bool(row['pago_diferido']))+'" label="'+ str(row["pago_diferido"])+ '" />\n'
            s= s + treecell_euros(row['saldomaximo'])
            s= s + treecell_euros(Tarjeta().saldo_pendiente(row['id_tarjetas']))
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
        try:
            con.Execute(sql);
        except:
            return False
        return True
        
    def modificar_fechapago(self, id_opertarjetas,  fechapago, id_opercuentas):
        sql="update opertarjetas set fechapago='"+str(fechapago)+"', pagado=true "+", lu_opercuentas="+str(id_opercuentas)+"  where id_opertarjetas=" +str(id_opertarjetas) 
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

    def cmb(self, sql,  selected,  js=True):        
        jstext=""
        if js:
            jstext= ' oncommand="cmbtiposoperaciones_submit();"'
        s= '<menulist id="cmbtiposoperaciones" '+jstext+'>\n'
        s=s + '<menupopup>\n';
        curs=con.Execute(sql)
        while not curs.EOF:
            row = curs.GetRowAssoc(0)   
            if row['id_tiposoperaciones']==selected:
                s=s +  '       <menuitem label="'+utf82xul(row['tipo_operacion'])+'" value="'+str(row['id_tiposoperaciones'])+'" selected="true"/>\n'
            else:
                s=s +  '       <menuitem label="'+utf82xul(row['tipo_operacion'])+'" value="'+str(row['id_tiposoperaciones'])+'"/>\n'
            curs.MoveNext()     
        curs.Close()
        s=s +  '     </menupopup>\n'
        s=s + '</menulist>\n'
        return s


class Total:
    def gastos_anuales(self,year):     
        """
            Saca la suma de todos los gastos producidos en un año.
        """
        sql="select sum(Importe) as importe from opercuentas where importe<0 and date_part('year',fecha) = "+str(year)+" and lu_tiposoperaciones in (1,7);"
        curs=con.Execute(sql); 
        row = curs.GetRowAssoc(0)   
        if row['importe']==None:
            return 0
        else:
            return row['importe'];
        
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
        for i in range (self.primera_fecha_con_datos_usuario().year,  datetime.date.today().year+1):
            f.write(str(i)+"-01-01\t"+str(Total().saldo_total(str(i)+"-01-01"))+"\n")               
	    if datetime.date.today()>datetime.date(i,7,1):
		f.write(str(i)+"-07-01\t"+str(Total().saldo_total(str(i)+"-07-01"))+"\n")
        f.write(str(datetime.date.today())+"\t"+str(Total().saldo_total(datetime.date.today()))+"\n")
        f.close()
        
        os.popen("gnuplot /tmp/informe_total.plot");

    def primera_fecha_con_datos_usuario(self):
        curs = con.Execute('select fecha from opercuentas UNION select fecha from operinversiones UNION select fecha from opertarjetas order by fecha limit 1;'); 
        row = curs.GetRowAssoc(0)      
        curs.Close()
        return row['fecha']
    

    def saldo_todas_cuentas(self, fecha):
        sql="select saldototalcuentasactivas('"+str(fecha)+"') as saldo;";
        curs=con.Execute(sql); 
        row = curs.GetRowAssoc(0)   
        return row['saldo'];

    def saldo_total(self,fecha):
        sql="select saldo_total('"+str(fecha)+"') as saldo;";
        curs=con.Execute(sql); 
        row = curs.GetRowAssoc(0)   
        return row['saldo'];

    def saldo_todas_inversiones(self,fecha):
        sql="select saldototalinversionesactivas('"+str(fecha)+"') as saldo;";
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

    def tae_anual(self, saldoinicio,  saldofinal):
        if saldoinicio==0:
            return 0
        return (saldofinal-saldoinicio)*100/saldoinicio
        
    def xultree_historico_dividendos(self, ano):
        sumsaldos=0
        sql="select id_dividendos, fecha, liquido, inversione, entidadesbancaria from dividendos, inversiones, cuentas, entidadesbancarias where entidadesbancarias.id_entidadesbancarias=cuentas.ma_entidadesbancarias and cuentas.id_cuentas=inversiones.lu_cuentas and dividendos.lu_inversiones=inversiones.id_inversiones and date_part('year',fecha)="+str(ano) + " order by fecha desc;"
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
        sql="select * from tmpoperinversioneshistoricas where date_part('year',fecha_venta)="+str(ano)+" order by fecha_venta desc";
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
            anos=(row['fecha_venta']- row['fecha_inicio']).days/365.0;
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

        saldototal=Total().saldo_total(datetime.date.today());

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
        try:
            s=s+treecell_tpc((beneficio)*100/saldototalinicio)
        except ZeroDivisionError:
            s=s+treecell_tpc(0)
            
        s=s+ '      </treerow>\n'
        s=s+ '   </treeitem>    \n'
        s=s+ '    <treeitem>\n'
        s=s+ '      <treerow>\n'
        s=s+ '         <treecell label="Con impuestos" />\n'
        s=s+treecell_euros(beneficiocon);
        try:
            s=s+treecell_tpc((beneficiocon)*100/saldototalinicio)
        except ZeroDivisionError:
            s=s+treecell_tpc(0)
        s=s+ '      </treerow>\n'
        s=s+ '   </treeitem>\n'
        s=s+ '    <treeitem>\n'
        s=s+ '      <treerow>\n'
        s=s+ '          <treecell label="Comisiones" />\n'
        s=s+treecell_euros(sumcomision);
        s=s+treecell_tpc(0)
        s=s+ '      </treerow>\n'
        s=s+ '   </treeitem>    \n'        
        s=s+ '    <treeitem>\n'
        s=s+ '      <treerow>\n'
        s=s+ '          <treecell label="Impuestos" />\n'
        s=s+treecell_euros(sumimpuestos);
        s=s+treecell_tpc(0)
        s=s+ '      </treerow>\n'
        s=s+ '   </treeitem>    \n'
        s=s+ '  </treechildren>\n'
        s=s+ '</tree>\n'
        s= s + '<label flex="0"  style="text-align: center;font-weight : bold;" value="Saldo a '+str(datetime.date.today())+': '+ euros(saldototal)+'." />\n'        
        s= s + '<label flex="0"  style="text-align: center;font-weight : bold;" value="Beneficio en el año '+str(ano)+': '+ euros(saldototal-saldototalinicio)+'." />\n'
        s= s + '</vbox>\n'
        return s        


def mylog(text):
    f=open("/tmp/xulpymoney.log","a")
    f.write(str(datetime.datetime.now()) + " " + text + "\n")
    f.close()
