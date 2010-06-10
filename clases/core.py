# -*- coding: UTF-8 -*-
import sys,  os,  gettext
sys.path.append("/usr/lib/xulpymoney/")
sys.path.append("/etc/xulpymoney/")
import config

version="0.2"
gettext.bindtextdomain('xulpymoney','/usr/share/locale/')
gettext.textdomain('xulpymoney')
os.environ["LC_ALL"]=config.language
resultadovalidar=""

from translate import  _
import datetime,  math
import adodb
from formato import *  
from inversion_actualizacion import *
from xul import *

class EntidadBancaria:    
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
                s=s +  '       <menuitem label="'+utf82xul(row['entidadbancaria'])+'" value="'+str(row['id_entidadesbancarias'])+'" selected="true"/>\n'
            else:
                s=s +  '       <menuitem label="'+utf82xul(row['entidadbancaria'])+'" value="'+str(row['id_entidadesbancarias'])+'"/>\n'
            curs.MoveNext()     
        curs.Close()
        s=s +  '     </menupopup>\n'
        s=s + '</menulist>\n'
        return s
    def insertar(self,  entidadbancaria,  eb_activa):
        sql="insert into entidadesbancarias (entidadbancaria, eb_activa) values ('" + entidadbancaria + "'," + str(eb_activa)+")"
        try:
            con.Execute(sql);
        except:
            return False
        return True
        
    def modificar(self, id_entidadesbancarias, entidadbancaria):
        sql="update entidadesbancarias set entidadbancaria='"+str(entidadbancaria)+"' where id_entidadesbancarias="+ str(id_entidadesbancarias)
        try:
            con.Execute(sql);
        except:
            return False
        return True
        
    def modificar_activa(self, id_entidadesbancarias,  activa):
        sql="update entidadesbancarias set eb_activa="+str(activa)+" where id_entidadesbancarias="+ str(id_entidadesbancarias)
        curs=con.Execute(sql); 
        return sql

        
    def saldo(self,id_entidadesbancarias,fecha):
        curs = con.Execute('select eb_saldo('+ str(id_entidadesbancarias) + ",'"+str(fecha)+"') as saldo;"); 
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
            sql="select * from entidadesbancarias order by entidadbancaria";
        else:
            sql="select * from entidadesbancarias where eb_activa='t' order by entidadbancaria";
        curs=con.Execute(sql)
        s=      '<script>\n<![CDATA[\n'
        s= s+ 'function popupEntidadesBancarias(){\n'
        s= s+ '     var tree = document.getElementById("treeEntidadesBancarias");\n'
        #el boolean de un "0" es true y bolean de un 0 es false
        s= s+ '     var activa=Boolean(Number(tree.view.getCellText(tree.currentIndex,tree.columns.getNamedColumn( "activa"))));\n'
        s= s+ '     id_entidadesbancarias=tree.view.getCellText(tree.currentIndex,tree.columns.getNamedColumn("id"));\n'
        s= s+ '     var popup = document.getElementById("popupEntidadesBancarias");\n'
        s= s+ '     if (document.getElementById("popmodificar")){\n'#Con que exista este vale
        s= s+ '         popup.removeChild(document.getElementById("popmodificar"));\n'
        s= s+ '         popup.removeChild(document.getElementById("popseparator1"));\n'
        s= s+ '         popup.removeChild(document.getElementById("poppatrimonio"));\n'
        s= s+ '         popup.removeChild(document.getElementById("popseparator2"));\n'
        s= s+ '         popup.removeChild(document.getElementById("popactiva"));\n'
        s= s+ '     }\n'
        s= s+ '     var popmodificar=document.createElement("menuitem");\n'
        s= s+ '     popmodificar.setAttribute("id", "popmodificar");\n'
        s= s+ '     popmodificar.setAttribute("label", "'+_('Modificar la Entidad Bancaria')+'");\n'
        s= s+ '     popmodificar.setAttribute("class", "menuitem-iconic");\n'
        s= s+ '     popmodificar.setAttribute("image", "images/edit.png");\n'
        s= s+ '     popmodificar.setAttribute("oncommand", "eb_modificar();");\n'
        s= s+ '     popup.appendChild(popmodificar);\n'
        s= s+ '     var popseparator1=document.createElement("menuseparator");\n'
        s= s+ '     popseparator1.setAttribute("id", "popseparator1");\n'
        s= s+ '     popup.appendChild(popseparator1);\n'
        s= s+ '     var poppatrimonio=document.createElement("menuitem");\n'
        s= s+ '     poppatrimonio.setAttribute("id", "poppatrimonio");\n'
        s= s+ '     poppatrimonio.setAttribute("label", "'+_('Patrimonio en la Entidad Bancaria')+'");\n'
        s= s+ '     poppatrimonio.setAttribute("oncommand", "eb_patrimonio();");\n'
        s= s+ '     popup.appendChild(poppatrimonio);\n'
        s= s+ '     var popseparator2=document.createElement("menuseparator");\n'
        s= s+ '     popseparator2.setAttribute("id", "popseparator2");\n'
        s= s+ '     popup.appendChild(popseparator2);\n'
        s= s+ '     var popactiva=document.createElement("menuitem");\n'
        s= s+ '     popactiva.setAttribute("id", "popactiva");\n'
        s= s+ '     if (activa){\n'
        s= s+ '         popactiva.setAttribute("label", "'+_('Desactivar la Entidad Bancaria')+'");\n'
        s= s+ '         popactiva.setAttribute("checked", "false");\n'
        s= s+ '         popactiva.setAttribute("oncommand", "eb_modificar_activa();");\n'
        s= s+ '     }else{\n'
        s= s+ '         popactiva.setAttribute("label", "'+_('Activar la Entidad Bancaria')+'");\n'
        s= s+ '         popactiva.setAttribute("checked", "true");\n'
        s= s+ '         popactiva.setAttribute("oncommand", "eb_modificar_activa();");\n'
        s= s+ '     }\n'
        s= s+ '     popup.appendChild(popactiva);\n'
        s= s+ '}\n\n'

        s= s+ 'function eb_modificar(){\n'
        s= s+ '     var tree = document.getElementById("treeEntidadesBancarias");\n'
        s= s+ '     id_entidadesbancarias=tree.view.getCellText(tree.currentIndex,tree.columns.getNamedColumn("id"));\n'
        s= s+ '     location=\'eb_modificar.py?id_entidadesbancarias=\' + id_entidadesbancarias;\n'
        s= s+ '}\n\n'
        
        s= s+ 'function eb_modificar_activa(){\n'
        s= s+ '     var tree = document.getElementById("treeEntidadesBancarias");\n'
        s= s+ '     var xmlHttp;\n'
        s= s+ '     var activa=Boolean(Number(tree.view.getCellText(tree.currentIndex,tree.columns.getNamedColumn( "activa"))));\n'
        s= s+ '     xmlHttp=new XMLHttpRequest();\n'
        s= s+ '     xmlHttp.onreadystatechange=function(){\n'
        s= s+ '         if(xmlHttp.readyState==4){\n'
        s= s+ '             var ale=xmlHttp.responseText;\n'
        s= s+ '             location="eb_listado.py";\n'
        s= s+ '         }\n'
        s= s+ '     }\n'
        s= s+ '     var url="ajax/eb_modificar_activa.py?id_entidadesbancarias="+id_entidadesbancarias+\'&activa=\'+!activa;\n'
        s= s+ '     xmlHttp.open("GET",url,true);\n'
        s= s+ '     xmlHttp.send(null);\n'
        s= s+ '}\n'
        

        s= s+ 'function eb_patrimonio(){\n'
        s= s+ '     var tree = document.getElementById("treeEntidadesBancarias");\n'
        s= s+ '     id_entidadesbancarias=tree.view.getCellText(tree.currentIndex,tree.columns.getNamedColumn("id"));\n'
        s= s+ '     location=\'eb_patrimonio.py?id_entidadesbancarias=\' + id_entidadesbancarias;\n'
        s= s+ '}\n\n'        
        s= s+ ']]>\n</script>\n\n'        
        
        s= s+ '<popupset>\n'
        s= s+ '    <popup id="popupEntidadesBancarias" >\n'
        s= s+ '        <menuitem label="Nueva Entidad Bancaria" oncommand="location=\'eb_insertar.py\'" class="menuitem-iconic"  image="images/item_add.png"/>\n'
        s= s+ '    </popup>\n'
        s= s+ '</popupset>\n'
        
        s= s+ '<tree id="treeEntidadesBancarias" enableColumnDrag="true" flex="6"   context="popupEntidadesBancarias"  onselect="popupEntidadesBancarias();" ondblclick="eb_patrimonio();" >\n'
        s= s+ '    <treecols>\n'
        s= s+  '        <treecol id="id" label="id" hidden="true" />\n'
        s= s+  '        <treecol id="activa" label="'+_('Activa')+'" hidden="true" />\n'
        s= s+  '        <treecol label="'+_('Entidad Bancaria')+'" flex="2"/>\n'       
        s= s+  '        <treecol label="% '+_('saldo total')+'" style="text-align: right" flex="2"/>\n'
        s= s+  '        <treecol label="'+_('Saldo')+'" style="text-align: right" flex="2"/>\n'
        s= s+  '    </treecols>\n'
        s= s+  '    <treechildren>\n'     
        total=Total().saldo_total(fecha)
        while not curs.EOF:
            row = curs.GetRowAssoc(0)   
            s= s + '        <treeitem>\n'
            s= s + '            <treerow>\n'
            s= s + '                <treecell label="'+str(row["id_entidadesbancarias"])+ '" />\n'
            s= s + '                <treecell label="'+str(row["eb_activa"])+ '" />\n'
            s= s + '                <treecell label="'+str(row["entidadbancaria"])+ '" style="text-align: right"/>\n'
            saldo=EntidadBancaria().saldo(row["id_entidadesbancarias"], datetime.date.today())
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
        s= s + '<label flex="1"  style="text-align: center;font-weight : bold;" value="'+_('Saldo total')+': '+ euros(total)+'" />\n'
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
                s=s +  '       <menuitem label="'+utf82xul(row['concepto'])+'" value="'+str(row['id_conceptos'])+";"+str(row['id_tiposoperaciones'])+'" selected="true"/>\n'
            else:
                s=s +  '       <menuitem label="'+utf82xul(row['concepto'])+'" value="'+str(row['id_conceptos'])+';'+str(row['id_tiposoperaciones'])+'"/>\n'
            curs.MoveNext()     
        curs.Close()
        s=s +  '     </menupopup>\n'
        s=s + '</menulist>\n'
        return s
        
        
    def insertar(self,  concepto,  id_tiposoperaciones):
        sql="insert into conceptos (concepto, id_tiposoperaciones) values ('" + str(concepto)+ "', "+str(id_tiposoperaciones)+")"
        try:
            con.Execute(sql);
        except:
            return False
        return True
        
    def modificar(self, id_conceptos, concepto,  id_tiposoperaciones):
        sql="update conceptos set concepto='"+str(concepto)+"', id_tiposoperaciones="+str(id_tiposoperaciones)+" where id_conceptos="+ str(id_conceptos)
        try:
            con.Execute(sql);
        except:
            mylog("Error: " + sql)
            return False
        return True
        
    def saldo(self, id_conceptos, year,  month):
        sql="select sum(importe) as importe from opercuentastarjetas where id_conceptos="+str(id_conceptos)+" and date_part('year',fecha)='"+str(year)+"' and date_part('month',fecha)='"+str(month)+"'"
        saldoopercuentastarjetas=con.Execute(sql).GetRowAssoc(0)["importe"]
        if saldoopercuentastarjetas==None:
            saldoopercuentastarjetas=0
        return saldoopercuentastarjetas
        
    def xultree_informe(self, id_conceptos):
        s=''        
        s= s+ '<tree id="treeConceptos" flex="6">\n'
        s= s+ '     <treecols>\n'
        s= s+ '         <treecol label="'+_('Año ')+'" flex="1"  style="text-align: left"/>\n'
        s= s+ '         <treecol label="'+_('Enero     ')+'" flex="1" style="text-align: right"/>\n'
        s= s+ '         <treecol label="'+_('Febrero   ')+'" flex="1" style="text-align: right"/>\n'
        s= s+ '         <treecol label="'+_('Marzo     ')+'" flex="1" style="text-align: right"/>\n'
        s= s+ '         <treecol label="'+_('Abril     ')+'" flex="1" style="text-align: right"/>\n'
        s= s+ '         <treecol label="'+_('Mayo      ')+'" flex="1" style="text-align: right"/>\n'
        s= s+ '         <treecol label="'+_('Junio     ')+'" flex="1" style="text-align: right"/>\n'
        s= s+ '         <treecol label="'+_('Julio     ')+'" flex="1" style="text-align: right"/>\n'
        s= s+ '         <treecol label="'+_('Agosto    ')+'" flex="1" style="text-align: right"/>\n'
        s= s+ '         <treecol label="'+_('Septiembre')+'" flex="1" style="text-align: right"/>\n'
        s= s+ '         <treecol label="'+_('Octubre   ')+'" flex="1" style="text-align: right"/>\n'
        s= s+ '         <treecol label="'+_('Noviembre ')+'" flex="1" style="text-align: right"/>\n'
        s= s+ '         <treecol label="'+_('Diciembre ')+'" flex="1" style="text-align: right"/>\n'
        s= s+ '         <treecol label="'+_('Total     ')+'" flex="1" style="text-align: right"/>\n'
        s= s+  '     </treecols>\n'
        s= s+  '     <treechildren>\n'
        fechamenor=con.Execute("select min(fecha) as fecha from opercuentastarjetas where id_conceptos="+str(id_conceptos)).GetRowAssoc(0)['fecha']
        sumtotal=0
        for year in range(fechamenor.year, datetime.date.today().year+1):
            total=0
            s= s + '          <treeitem >\n'
            s= s + '               <treerow>\n'
            s= s + '                    <treecell label="'+str(year)+ '" />\n'
            for month in range(1, 13):
                saldo=Concepto().saldo(id_conceptos, year, month)
                total=total+saldo
                sumtotal=sumtotal+saldo
                s= s + '                    '+treecell_euros(saldo)
            s= s + '                    '+treecell_euros(total)
            s= s + '               </treerow>\n'
            s= s + '          </treeitem>\n'
        s= s + '     </treechildren>\n'
        s= s + '</tree>\n'        
        if(datetime.date.today().year-fechamenor.year)==0:
            mediamensual=sumtotal/(12)
            mediaanual=sumtotal
        else:
            mediamensual=sumtotal/(12*(datetime.date.today().year-fechamenor.year))
            mediaanual=sumtotal/(datetime.date.today().year-fechamenor.year)
        s= s + '<label flex="0"  style="text-align: center;font-weight : bold;" value="'+_('Media mensual')+': '+ euros(mediamensual)+'." />\n'
        s= s + '<label flex="0"  style="text-align: center;font-weight : bold;" value="'+_('Media anual')+': '+ euros(mediaanual)+'." />\n'
        return s

    def xultree(self, sql):
        sumsaldos=0;
        s=      '<script>\n<![CDATA[\n'
        s= s+ 'function popupConceptos(){\n'
        s= s+ '     var tree = document.getElementById("treeConceptos");\n'
        s= s+ '     id_conceptos=tree.view.getCellText(tree.currentIndex,tree.columns.getNamedColumn("id"));\n'
        s= s+ '     var popup = document.getElementById("popupConceptos");\n'
        s= s+ '     if (document.getElementById("popmodificar")){\n'#Con que exista este vale
        s= s+ '         popup.removeChild(document.getElementById("popmodificar"));\n'
#        s= s+ '         popup.removeChild(document.getElementById("popborrar"));\n'
        s= s+ '     }\n'
        s= s+ '     var popmodificar=document.createElement("menuitem");\n'
        s= s+ '     popmodificar.setAttribute("id", "popmodificar");\n'
        s= s+ '     popmodificar.setAttribute("label", "'+_('Modificar el concepto')+'");\n'
        s= s+ '     popmodificar.setAttribute("class", "menuitem-iconic");\n'
        s= s+ '     popmodificar.setAttribute("image", "images/edit.png");\n'
        s= s+ '     popmodificar.setAttribute("oncommand", "concepto_modificar();");\n'
        s= s+ '     popup.appendChild(popmodificar);\n'
#        s= s+ '     var popborrar=document.createElement("menuitem");\n'
#        s= s+ '     popborrar.setAttribute("id", "popborrar");\n'
#        s= s+ '     popborrar.setAttribute("label", "Borrar el concepto");\n'
#        s= s+ '     popborrar.setAttribute("oncommand", "concepto_borrar();");\n'
#        s= s+ '     popup.appendChild(popborrar);\n'
        s= s+ '}\n\n'

#        s= s+ 'function concepto_borrar(){\n'
#        s= s+ '     var tree = document.getElementById("treeConceptos");\n'
#        s= s+ '     id_conceptos=tree.view.getCellText(tree.currentIndex,tree.columns.getNamedColumn("id"));\n'
#        s= s+ '     location=\'concepto_borrar.py?id_conceptos=\' + id_conceptos;\n'
#        s= s+ '}\n\n'
        
        s= s+ 'function concepto_modificar(){\n'
        s= s+ '     var tree = document.getElementById("treeConceptos");\n'
        s= s+ '     id_conceptos=tree.view.getCellText(tree.currentIndex,tree.columns.getNamedColumn("id"));\n'
        s= s+ '     location=\'concepto_modificar.py?id_conceptos=\' + id_conceptos;\n'
        s= s+ '}\n\n'
        
        s= s+ 'function concepto_insertar(){\n'
        s= s+ '     var tree = document.getElementById("treeConceptos");\n'
        s= s+ '     id_conceptos=tree.view.getCellText(tree.currentIndex,tree.columns.getNamedColumn("id"));\n'
        s= s+ '     location=\'concepto_insertar.py\';\n'
        s= s+ '}\n'
        s= s+ ']]>\n</script>\n\n'                

        s= s+ '<popupset>\n'
        s= s+ '     <popup id="popupConceptos" >\n'
        s= s+ '          <menuitem label="'+_('Nuevo concepto')+'" oncommand="location=\'concepto_insertar.py\'" class="menuitem-iconic"  image="images/item_add.png"/>\n'
        s= s+ '     </popup>\n'
        s= s+ '</popupset>\n'

        s= s+ '<tree id="treeConceptos" flex="6"   context="popupConceptos"  onselect="popupConceptos();" >\n'
        s= s+ '     <treecols>\n'
        s= s+  '          <treecol id="id" label="Id" hidden="true" />\n'
        s= s+  '          <treecol label="'+_('Concepto')+'"  flex="2"/>\n'
        s= s+  '          <treecol label="'+_('Tipo de operación')+'"  flex="2"/>\n'
        s= s+  '     </treecols>\n'
        s= s+  '     <treechildren>\n'
        curs=con.Execute(sql);         
        while not curs.EOF:
            row = curs.GetRowAssoc(0)   
            s= s + '          <treeitem >\n'
            s= s + '               <treerow>\n'
            s= s + '                    <treecell label="'+str(row["id_conceptos"])+ '" />\n'
            s= s + '                    <treecell label="'+ utf82xul(row["concepto"])+ '" />\n'
            s= s + '                    <treecell label="'+ row["tipooperacion"]+ '" />\n'
            s= s + '               </treerow>\n'
            s= s + '          </treeitem>\n'
            curs.MoveNext()     
        s= s + '     </treechildren>\n'
        s= s + '</tree>\n'
        curs.Close()
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
        sql="insert into cuentas (id_entidadesbancarias, cuenta, numero_cuenta, cu_activa) values (" + str(id_entidadesbancarias )+ ", '" + str(cuenta)+"', '"+ str(numero_cuenta) +"', "+str(cu_activa)+")"
        try:
            con.Execute(sql);
        except:
            return False
        return True


    def xul_listado(self, sql):
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
        s= s+ '     popmodificar.setAttribute("label", "'+_('Modificar la cuenta')+'");\n'
        s= s+ '     popmodificar.setAttribute("class", "menuitem-iconic");\n'
        s= s+ '     popmodificar.setAttribute("image", "images/edit.png");\n'
        s= s+ '     popmodificar.setAttribute("oncommand", "cuenta_modificar();");\n'
        s= s+ '     popup.appendChild(popmodificar);\n'
        s= s+ '     var popactiva=document.createElement("menuitem");\n'
        s= s+ '     popactiva.setAttribute("id", "popactiva");\n'
        s= s+ '     if (activa){\n'
        s= s+ '         popactiva.setAttribute("label", "'+_('Desactivar la cuenta')+'");\n'
        s= s+ '         popactiva.setAttribute("checked", "false");\n'
        s= s+ '         popactiva.setAttribute("oncommand", "cuenta_modificar_activa();");\n'
        s= s+ '     }else{\n'
        s= s+ '         popactiva.setAttribute("label", "'+_('Activar la cuenta')+'");\n'
        s= s+ '         popactiva.setAttribute("checked", "true");\n'
        s= s+ '         popactiva.setAttribute("oncommand", "cuenta_modificar_activa();");\n'
        s= s+ '     }\n'
        s= s+ '     popup.appendChild(popactiva);\n'
        s= s+ '     var popseparator1=document.createElement("menuseparator");\n'
        s= s+ '     popseparator1.setAttribute("id", "popseparator1");\n'
        s= s+ '     popup.appendChild(popseparator1);\n'
        s= s+ '     var popmovimientos=document.createElement("menuitem");\n'
        s= s+ '     popmovimientos.setAttribute("id", "popmovimientos");\n'
        s= s+ '     popmovimientos.setAttribute("label", "'+_('Movimientos en la cuenta')+'");\n'
        s= s+ '     popmovimientos.setAttribute("oncommand", "cuenta_movimientos();");\n'
        s= s+ '     popup.appendChild(popmovimientos);\n'
        s= s+ '}\n\n'

        s= s+ 'function cuenta_modificar(){\n'
        s= s+ '     var tree = document.getElementById("treeCuentas");\n'
        s= s+ '     id_cuentas=tree.view.getCellText(tree.currentIndex,tree.columns.getNamedColumn("id"));\n'
        s= s+ '     location=\'cuenta_modificar.py?id_cuentas=\' + id_cuentas;\n'
        s= s+ '}\n\n'
        
        s= s+ 'function cuenta_movimientos(){\n'
        s= s+ '     var tree = document.getElementById("treeCuentas");\n'
        s= s+ '     id_cuentas=tree.view.getCellText(tree.currentIndex,tree.columns.getNamedColumn("id"));\n'
        s= s+ '     location=\'cuentaoperacion_listado.py?id_cuentas=\' + id_cuentas;\n'
        s= s+ '}\n\n'
        
        s= s+ 'function cuenta_modificar_activa(){\n'
        s= s+ '     var tree = document.getElementById("treeCuentas");\n'
        s= s+ '     var xmlHttp;\n'
        s= s+ '     var activa=Boolean(Number(tree.view.getCellText(tree.currentIndex,tree.columns.getNamedColumn("activa"))));\n'
        s= s+ '     xmlHttp=new XMLHttpRequest();\n'
        s= s+ '     xmlHttp.onreadystatechange=function(){\n'
        s= s+ '         if(xmlHttp.readyState==4){\n'
        s= s+ '             var ale=xmlHttp.responseText;\n'
        s= s+ '             location="cuenta_listado.py";\n'
        s= s+ '         }\n'
        s= s+ '     }\n'
        s= s+ '     var url="ajax/cuenta_modificar_activa.py?id_cuentas="+id_cuentas+\'&activa=\'+!activa;\n'
        s= s+ '     xmlHttp.open("GET",url,true);\n'
        s= s+ '     xmlHttp.send(null);\n'
        s= s+ '}\n'
        s= s+ ']]>\n</script>\n\n'                
        s= s+ '<popupset>\n'
        s= s+ '     <popup id="popupCuentas" >\n'
        s= s+ '          <menuitem label="'+_('Transferencia bancaria')+'"  onclick="location=\'cuenta_transferencia.py\';"  class="menuitem-iconic"  image="images/hotsync.png" />\n'
        s=s + '          <menuitem label="'+_('Listado de tarjetas')+'"  onclick="location=\'tarjeta_listado.py\';"   class="menuitem-iconic"  image="images/visa.png"/>\n'
        s= s+ '          <menuseparator/>\n'
        s= s+ '          <menuitem label="'+_('Cuenta nueva')+'" oncommand="location=\'cuenta_insertar.py\'" class="menuitem-iconic"  image="images/item_add.png"/>\n'
#    <menuitem label="Modificar la cuenta"  oncommand='location="cuentas_ibm.py?id_cuentas=" + idcuenta  + "&amp;ibm=modificar&amp;regresando=0";'   class="menuitem-iconic"  image="images/toggle_log.png"/>
#    <menuitem label="Borrar la cuenta"  oncommand='location="cuentas_ibm.py?id_cuentas=" + idcuenta  + "&amp;ibm=borrar&amp;regresando=0";'  class="menuitem-iconic" image="images/eventdelete.png"/>
#    <menuitem label="Movimientos de cuenta"  oncommand="location='cuentaoperacion_listado.py?id_cuentas=' + idcuenta;"/> 
#    <menuseparator/>
        s= s+ '     </popup>\n'
        s= s+ '</popupset>\n'

        s= s+ '<vbox flex="1">\n'
        s= s+ '<tree id="treeCuentas" flex="6"   context="popupCuentas"  onselect="popupCuentas();" ondblclick="cuenta_movimientos();" >\n'
        s= s+ '     <treecols>\n'
        s= s+  '          <treecol id="id" label="Id" hidden="true" />\n'
        s= s+  '          <treecol id="activa" label="'+_('Activa')+'" hidden="true" />\n'
        s= s+  '          <treecol id="col_cuenta" label="'+_('Cuenta')+'" sort="?col_cuenta"  sortDirection="descending" flex="2"/>\n'
        s= s+  '          <treecol id="col_entidad_bancaria" label="'+_('Entidad Bancaria')+'"  sort="?col_entidad_bancaria" sortActive="true"  flex="2"/>\n'
        s= s+  '          <treecol id="col_valor" label="'+_('Número de cuenta')+'" flex="2" style="text-align: right" />\n'
        s= s+  '          <treecol id="col_saldo" label="'+_('Saldo')+'" flex="1" style="text-align: right"/>\n'
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
            s= s + '                    <treecell label="'+row["entidadbancaria"]+ '" />\n'
            s= s + '                    <treecell label="'+ str(row["numero_cuenta"])+ '" />\n'
            s= s + '                    '+treecell_euros(row['saldo'])
            s= s + '               </treerow>\n'
            s= s + '          </treeitem>\n'
            curs.MoveNext()     
        s= s + '     </treechildren>\n'
        s= s + '</tree>\n'
        s= s + '<label flex="1"  id="totalcuentas" style="text-align: center;font-weight : bold;" value="'+_('Saldo total de todas las cuentas')+': '+ euros(sumsaldos)+'" total="'+str(sumsaldos)+'" />\n'
        s= s + '</vbox>\n'
        curs.Close()
        return s

        
    def modificar(self, id_cuentas, cuenta,  id_entidadesbancarias,  numero_cuenta):
        sql="update cuentas set cuenta='"+str(cuenta)+"', id_entidadesbancarias="+str(id_entidadesbancarias)+", numero_cuenta='"+str(numero_cuenta)+"' where id_cuentas="+ str(id_cuentas)
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
        curs = con.Execute('select sum(importe) as "suma" from opercuentas where id_cuentas='+ str(id_cuentas) +" and fecha<='"+str(fecha)+"';") 
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
        


    def insertar(self,  fecha, id_conceptos, id_tiposoperaciones,  importe,  comentario,  id_cuentas):
        sql="insert into opercuentas (fecha, id_conceptos, id_tiposoperaciones, importe, comentario, id_cuentas) values ('" + fecha + "'," + str(id_conceptos)+","+ str(id_tiposoperaciones) +","+str(importe)+", '"+comentario+"', "+str(id_cuentas)+")"
        try:
            con.Execute(sql);
        except:
            return False
        return True

    def modificar(self, id_opercuentas,  fecha, id_conceptos, id_tiposoperaciones,  importe,  comentario,  id_cuentas):
        sql="update opercuentas set fecha='" + fecha + "', id_conceptos=" + str(id_conceptos)+", id_tiposoperaciones="+ str(id_tiposoperaciones) +", importe="+str(importe)+", comentario='"+comentario+"', id_cuentas="+str(id_cuentas)+" where id_opercuentas=" + str(id_opercuentas)
        try:
            con.Execute(sql);
        except:
            return False
        return True



    def transferencia(self, fecha,  cmbcuentaorigen,  cmbcuentadestino, importe, comision ):
        sql="select transferencia('"+fecha+"', "+ str(cmbcuentaorigen) +', ' + str(cmbcuentadestino)+', '+str(importe) +', '+str(comision)+');'
        try:
            con.Execute(sql);
        except:
            mylog("BDError|CuentaOperacion.transferencia|" +sql)
            return False
        return True

    def id_opercuentas_insertado_en_session(self):
        return con.Execute("select currval('seq_opercuentas') as seq;").GetRowAssoc(0)["seq"]

    def xul_listado(self,   id_cuentas,  year,  month):
        sql="SELECT cuentas.id_cuentas, cuentas.cuenta, cuentas.id_entidadesbancarias AS ma_entidadesbancarias, cuentas.cu_activa, cuentas.numero_cuenta, opercuentas.id_opercuentas, opercuentas.fecha, opercuentas.id_conceptos AS lu_conceptos, opercuentas.id_tiposoperaciones AS lu_tiposoperaciones, opercuentas.importe, opercuentas.comentario, opercuentas.id_cuentas AS ma_cuentas, conceptos.id_conceptos, conceptos.concepto, conceptos.id_tiposoperaciones AS lu_tipooperacion, entidadesbancarias.id_entidadesbancarias, entidadesbancarias.entidadbancaria AS entidadesbancaria, entidadesbancarias.eb_activa, tiposoperaciones.id_tiposoperaciones, tiposoperaciones.tipooperacion AS tipo_operacion, tiposoperaciones.modificable, tiposoperaciones.operinversion, tiposoperaciones.opercuentas   FROM cuentas, opercuentas, conceptos, entidadesbancarias, tiposoperaciones where cuentas.id_cuentas = opercuentas.id_cuentas AND cuentas.id_entidadesbancarias = entidadesbancarias.id_entidadesbancarias AND opercuentas.id_conceptos = conceptos.id_conceptos AND conceptos.id_tiposoperaciones = tiposoperaciones.id_tiposoperaciones and opercuentas.id_cuentas="+str(id_cuentas)+" and date_part('year',fecha)='"+str(year)+"' and date_part('month',fecha)='"+str(month)+"' order by opercuentas.fecha, opercuentas.id_opercuentas";
        
        curs= con.Execute(sql);         
        primeromes=datetime.date(int(year),  int(month),  1)
        diamenos=primeromes-datetime.timedelta(days=1)      
        saldo=Cuenta().saldo(id_cuentas, diamenos.isoformat()) 
        s=      '<script>\n<![CDATA[\n'
        s= s+ 'function popupOpercuentas(){\n'
        s= s+ '     var tree = document.getElementById("treeOpercuentas");\n'
        s= s+ '     id_opercuentas=tree.view.getCellText(tree.currentIndex,tree.columns.getNamedColumn("id"));\n'        
        s= s+ '     var popup = document.getElementById("popupOpercuentas");\n'#se debe borrar antes del if
        s= s+ '     if (document.getElementById("popmodificar")){\n'#Con que exista este vale
        s= s+ '         popup.removeChild(document.getElementById("popmodificar"));\n'
        s= s+ '         popup.removeChild(document.getElementById("popborrar"));\n'
        s= s+ '     }\n'
        s= s+ '     if(id_opercuentas==0){;\n'
        s= s+ '         return;\n'
        s= s+ '     }\n'

        s= s+ '     var popmodificar=document.createElement("menuitem");\n'
        s= s+ '     popmodificar.setAttribute("id", "popmodificar");\n'
        s= s+ '     popmodificar.setAttribute("label", "'+_('Modificar la operación')+'");\n'
        s= s+ '     popmodificar.setAttribute("class", "menuitem-iconic");\n'
        s= s+ '     popmodificar.setAttribute("image", "images/edit.png");\n'
        s= s+ '     popmodificar.setAttribute("oncommand", "opercuenta_modificar();");\n'
        s= s+ '     popup.appendChild(popmodificar);\n'
        s= s+ '     var popborrar=document.createElement("menuitem");\n'
        s= s+ '     popborrar.setAttribute("id", "popborrar");\n'
        s= s+ '     popborrar.setAttribute("label", "'+_('Borra la operación')+'");\n'
        s= s+ '     popborrar.setAttribute("oncommand", "opercuenta_borrar();");\n'
        s= s+ '     popup.appendChild(popborrar);\n'
        s= s+ '}\n\n'

        s= s+ 'function opercuenta_insertar(){\n'
        s= s+ '     var tree = document.getElementById("treeOpercuentas");\n'
        s= s+ '     var id_opercuentas=tree.view.getCellText(tree.currentIndex,tree.columns.getNamedColumn("id"));\n'
        s= s+ '     location="cuentaoperacion_insertar.py?id_cuentas=' +str(id_cuentas) + '&year='+str(year)+'&month='+str(month)+'";\n'
        s= s+ '}\n\n'
        
        s= s+ 'function opercuenta_modificar(){\n'
        s= s+ '     var tree = document.getElementById("treeOpercuentas");\n'
        s= s+ '     var id_opercuentas=tree.view.getCellText(tree.currentIndex,tree.columns.getNamedColumn("id"));\n'
        s= s+ '     location=\'cuentaoperacion_modificar.py?id_opercuentas=\' + id_opercuentas;\n'
        s= s+ '}\n\n'
        
        
        
        
        s= s+ 'function opercuenta_borrar(){\n'
        s= s+ '     var tree = document.getElementById("treeOpercuentas");\n'
        s= s+ '     var id_opercuentas=tree.view.getCellText(tree.currentIndex,tree.columns.getNamedColumn("id"));\n'
        s= s+ '     var xmlHttp;\n'
        s= s+ '     xmlHttp=new XMLHttpRequest();\n'
        s= s+ '     xmlHttp.onreadystatechange=function(){\n'
        s= s+ '         if(xmlHttp.readyState==4){\n'
        s= s+ '             var ale=xmlHttp.responseText;\n'
        s= s+ '             location="cuentaoperacion_listado.py?id_cuentas='+str(id_cuentas)+'";\n'
        s= s+ '         }\n'
        s= s+ '     }\n'
        s= s+ '     var url="ajax/cuentaoperacion_borrar.py?id_opercuentas="+id_opercuentas;\n'
        s= s+ '     xmlHttp.open("GET",url,true);\n'
        s= s+ '     xmlHttp.send(null);\n'
        s= s+ '}\n'
        s= s+ ']]>\n</script>\n\n'                
        s= s+ '<popupset>\n'
        s= s+ '    <popup id="popupOpercuentas">\n'
        s=s + '        <menuitem label="'+_('Transferencia bancaria')+'"  onclick="location=\'cuenta_transferencia.py\';"  class="menuitem-iconic"  image="images/hotsync.png" />\n'
        s= s+ '        <menuitem label="'+_('Operación de tarjeta')+'"   onclick="location=\'tarjeta_listado.py\';"   class="menuitem-iconic"  image="images/visa.png"/>\n'
        s= s+ '        <menuseparator/>\n'
        s= s+ '        <menuitem label="'+_('Nueva operación')+'" oncommand="opercuenta_insertar();" class="menuitem-iconic"  image="images/item_add.png"/>\n'
        s= s+ '    </popup>\n'
        s= s+ '</popupset>\n'
        s= s+ '<tree id="treeOpercuentas" enableColumnDrag="true" flex="6"   context="popupOpercuentas"  onselect="popupOpercuentas();">\n'
        s= s+ '    <treecols>\n'
        s= s+ '        <treecol id="id" label="id" hidden="true" />\n'
        s= s+ '        <treecol label="'+_('Fecha')+'" flex="1" style="text-align: center"/>\n'
        s= s+ '        <treecol label="'+_('Concepto')+'"  flex="3"/>\n'
        s= s+ '        <treecol label="'+_('Importe')+'" flex="1" style="text-align: right" />\n'
        s= s+ '        <treecol label="'+_('Saldo')+'" flex="1" style="text-align: right"/>\n'
        s= s+ '        <treecol label="'+_('Comentario')+'" flex="7" style="text-align: left"/>\n'
        s= s+ '    </treecols>\n'
        s= s+ '    <treechildren>\n'
        s= s+ '      <treeitem>\n'
        s= s+ '         <treerow>\n'
        s= s+ '            <treecell label="0" />\n'
        s= s+ '            <treecell label="" />\n'
        s= s+ '            <treecell label="'+_('Saldo a inicio de mes')+'" />\n'
        s= s+ '            '+ treecell_euros(0)
        s= s+ '            '+ treecell_euros(saldo)
        s= s+ '            <treecell label="" />\n'
        s= s+ '         </treerow>\n'
        s= s+ '      </treeitem>\n'
        while not curs.EOF:
            row = curs.GetRowAssoc(0)   
            saldo=saldo+ dosdecimales(row['importe'])
            s= s + '      <treeitem>\n'
            s= s + '         <treerow>\n'
            #Impide la edición de id_opercuentas especiales poniendolo a 0
            if row["id_tiposoperaciones"] in (0, 4, 5, 6, 7, 8, 9, 10) or row["id_conceptos"]==39: #dividendos
                id_opercuentas=0
            else:
                id_opercuentas=row["id_opercuentas"]
            s= s + '            <treecell label="'+str(id_opercuentas)+ '" />\n'
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
    def insertar(self,  fecha, id_conceptos, id_tiposoperaciones, importe, comentario,id_cuentas,id_operinversiones,id_inversiones):
        sql="insert into tmpinversionesheredada (fecha, id_conceptos, id_tiposoperaciones, importe, comentario,id_cuentas, id_operinversiones,id_inversiones) values ('"+str(fecha)+"', "+str(id_conceptos)+", "+str(id_tiposoperaciones)+", "+str(importe)+", '"+str(comentario)+"' ,"+str(id_cuentas)+", "+str(id_operinversiones)+", "+str(id_inversiones)+")"
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
        id_inversiones=row['id_inversiones'];
        regInversion=con.Execute("select * from inversiones where id_inversiones="+ str(row['id_inversiones'])).GetRowAssoc(0)
        id_cuentas=regInversion['id_cuentas']
        comision=row['comision'];
        impuestos=row['impuestos'];
      
#        //Dependiendo del tipo de operaci�n se ejecuta una operaci�n u otra.
        if row['id_tiposoperaciones']==4:#Compra Acciones
            #Se pone un registro de compra de acciones que resta el saldo de la opercuenta
            CuentaOperacionHeredadaInversion().insertar(fecha, 29, 4, -importe-comision, regInversion['inversion']+'. '+_('Importe')+': ' + str(importe)+". "+_('Comisión')+": " + str(comision)+ ". "+_('Impuestos')+": " + str(impuestos),id_cuentas,id_operinversiones,id_inversiones);
            #//Si hubiera comisi�n se a�ade la comisi�n.
#            if(comision!=0):
#                CuentaOperacionHeredadaInversion().insertar(fecha, 38, 1, -comision, regInversion['inversion']+". Comisión (Id. id_operinversiones)",id_cuentas,id_operinversiones,id_inversiones)
        elif row['id_tiposoperaciones']==5:#// Venta Acciones
            #//Se pone un registro de compra de acciones que resta el saldo de la opercuenta
            CuentaOperacionHeredadaInversion().insertar(fecha, 35, 5, importe-comision-impuestos, regInversion['inversion']+". "+_('Importe')+": " + str(importe)+". "+_('Comisión')+": " + str(comision)+ ". "+_('Impuestos')+": " + str(impuestos),id_cuentas,id_operinversiones,id_inversiones);
            #//Si hubiera comisi�n se a�ade la comisi�n.
#            if(comision!=0):
#                CuentaOperacionHeredadaInversion().insertar( fecha, 38, 1, -comision, regInversion['inversion']+". Comisión (Id. id_operinversiones)",id_cuentas,id_operinversiones,id_inversiones);
            #//Si hubiera pago de impuestos se pone
#            if(impuestos!=0):
#                CuentaOperacionHeredadaInversion().insertar(fecha, 37, 1, -impuestos, regInversion['inversion']+". Pago de impuestos (Id. id_operinversiones)",id_cuentas,id_operinversiones,id_inversiones);
        elif row['id_tiposoperaciones']==6:# // A�adido de Acciones
            #//Si hubiera comisi�n se a�ade la comisi�n.
            if(comision!=0):
                CuentaOperacionHeredadaInversion().insertar(fecha, 38, 1, -comision-impuestos, regInversion['inversion']+". "+_('Importe')+": " + str(importe)+". "+_('Comisión')+": " + str(comision)+ ". "+_('Impuestos')+": " + str(impuestos), id_cuentas,id_operinversiones,id_inversiones);
            #//Si hubiera pago de impuestos se pone
#            if(impuestos!=0):
#                CuentaOperacionHeredadaInversion().insertar(fecha, 37, 1, -impuestos, regInversion['inversion']+". Pago de impuestos (Id. id_operinversiones)",id_cuentas,id_operinversiones,id_inversiones);

  
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
        sql="SELECT * from operinversiones where id_inversiones="+str(id_inversiones)
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
        CuentaOperacion().insertar( fecha, 39, 2, liquido, inv['inversion']+" ("+_('Bruto')+"="+str(bruto)+"€. "+_('Retención')+"="+str(retencion)+"€.)",inv['id_cuentas'])
        id_opercuentas=con.Execute("select currval('seq_opercuentas') as seq;").GetRowAssoc(0)["seq"]   
        #Añade el dividendo
        sql="insert into dividendos (fecha, valorxaccion, bruto, retencion, liquido, id_inversiones,id_opercuentas) values ('"+str(fecha)+"', "+str(valorxaccion)+", "+str(bruto)+", "+str(retencion)+", "+str(liquido)+", "+str(id_inversiones)+", "+str(id_opercuentas)+")"
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
        
    def suid_liquido_todos(self, inicio,final):
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
        s= s+ '    var url="ajax/dividendo_borrar.py?id_dividendos=" + id_dividendos;\n'
        s= s+ '    xmlHttp=new XMLHttpRequest();\n'
        s= s+ '    xmlHttp.onreadystatechange=function(){\n'
        s= s+ '        if(xmlHttp.readyState==4){\n'
        s= s+ '            var ale=xmlHttp.responseText;\n'
        s= s+ '            location="inversionoperacion_listado.py?id_inversiones="+ id_inversiones;\n'
        s= s+ '        }\n'
        s= s+ '    }\n'
        s= s+ '    xmlHttp.open("GET",url,true);\n'
        s= s+ '    xmlHttp.send(null);\n'
        s= s+ '}\n'
        s= s+ ']]>\n</script>\n\n'

        s= s+ '<vbox flex="1">\n'
        s= s+ '<popupset>\n'
        s= s+ '    <popup id="divpopup" >\n'  
        s= s+ '        <menuitem label="Nuevo dividendo" oncommand="location=\'dividendo_insertar.py?id_inversiones=\' +'+str(id_inversiones)+' ;"  class="menuitem-iconic"  image="images/item_add.png" />\n'
        s= s+ '        <menuitem label="Borrar el dividendo"  oncommand="dividendo_borrar();"   class="menuitem-iconic"  image="images/eventdelete.png"/>\n'
        s= s+ '    </popup>\n'
        s= s+ '</popupset>\n'
        s=s+ '<tree id="treeDiv" flex="3" tooltiptext="'+_('Sólo se muestran los dividendos desde la primera operación actual, no desde la primera operación histórica')+'" context="divpopup">\n'
        s=s+ '    <treecols>\n'
        s=s+ '        <treecol id="id" label="id" flex="1" hidden="true"/>\n'
        s=s+ '        <treecol label="'+_('Fecha')+'" flex="1"  style="text-align: center"/>\n'
        s=s+ '        <treecol label="'+_('Cuenta cobro')+'" flex="2" style="text-align: left" />\n'
        s=s+ '        <treecol label="'+_('Liquido')+'" flex="1" style="text-align: right"/>\n'
        s=s+ '    </treecols>\n'
        s=s+ '    <treechildren tooltiptext="'+_('Sólo se muestran los dividendos desde la primera operación actual, no desde la primera operación histórica')+'">\n'
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
        if curs.RecordCount()!=0:
            importeinvertido=InversionOperacionTemporal().importe_invertido(id_inversiones)
            dias=(datetime.date.today()-InversionOperacionTemporal().fecha_primera_operacion(id_inversiones)).days
            dtpc=100*sumsaldos/importeinvertido
            dtae=365*dtpc/abs(dias)
        else:
            dtpc=0
            dtae=0
        s= s + '<label flex="0"  style="text-align: center;font-weight : bold;" value="'+_('Suma de dividendos de la inversión')+': '+ euros(sumsaldos)+'." />\n'        
        s= s + '<label flex="0"  style="text-align: center;font-weight : bold;" value="% '+_('de lo invertido')+': '+tpc(dtpc)+'. %'+_('TAE de lo invertido')+': '+ tpc(dtae)+'." />\n'
        s= s + '</vbox>\n'
        return s
        

class Inversion:
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
            
    def insertar(self,  inversion,  compra,  venta,  tpcvariable,  id_cuentas,  internet):
        sql="insert into inversiones (inversion, compra, venta, tpcvariable, id_cuentas, in_activa, internet) values ('"+inversion+"', "+str(compra)+", "+str(venta)+", "+str(tpcvariable)+", "+str(id_cuentas)+", true,'"+str(internet)+"');"
        curs=con.Execute(sql); 
        return sql            
        
    def modificar(self, id_inversiones, inversion,  compra,  venta,  tpcvariable,  id_cuentas,  internet):
        sql="update inversiones set inversion='"+inversion+"', compra="+str(compra)+", venta="+str(venta)+", tpcvariable="+str(tpcvariable)+", id_cuentas="+str(id_cuentas)+", internet='"+str(internet)+"' where id_inversiones="+ str(id_inversiones)
        curs=con.Execute(sql); 
        return sql
        
    def modificar_activa(self, id_inversiones,  activa):
        sql="update inversiones set in_activa="+str(activa)+" where id_inversiones="+ str(id_inversiones)
        curs=con.Execute(sql); 
        return sql
        
    def nombre_tpcvariable(self,  tpcvariable):
        if tpcvariable==-100:
            return _('ETF Inversos')
        if tpcvariable==0:
            return _("Fondos de dinero y depósitos")
        if tpcvariable==50:
            return _("P. Pensiones e inversiones hasta un 50% en renta variable, fondos alternativos y renta fija")
        if tpcvariable==100:
            return _("P. Pensiones e inversiones hasta un 100% en renta variable y acciones")
        return None
            
    def numero_acciones(self, id_inversiones, fecha):
        resultado=0;
        sql="SELECT Acciones from operinversiones where id_Inversiones="+str(id_inversiones)+" and fecha<='"+str(fecha)+"'"
        curs=con.Execute(sql); 
        while not curs.EOF:
            row = curs.GetRowAssoc(0)   
            resultado=resultado+ row['acciones']
            curs.MoveNext()     
        curs.Close()
        return resultado

        
    def xultree_compraventa(self):
        sql="select id_inversiones, inversion, entidadbancaria,  inversion_actualizacion(id_inversiones,'"+str(datetime.date.today())+"') as actualizacion, compra, venta from inversiones, cuentas, entidadesbancarias where venta<> compra and in_activa=true and cuentas.id_entidadesbancarias=entidadesbancarias.id_entidadesbancarias and cuentas.id_cuentas=inversiones.id_cuentas order by inversion;"
        curs=con.Execute(sql); 
        s=      '<script>\n<![CDATA[\n'
        s= s+ 'function actualizar_internet(){\n'
        s= s+ '     var tree = document.getElementById("treeInversiones");\n'
        s= s+ '     location=\'inversion_actualizar_internet.py\';\n'
        s= s+ '}\n\n'
        s= s+ ']]>\n</script>\n\n'    

        s= s+ '<vbox flex="1">\n'
        s= s+ '<popupset>\n'
        s= s+ '<popup id="treepopup" >\n'   
        s= s+ '    <menuitem label="'+_('Actualizar el valor')+'" oncommand="location=\'inversion_actualizar.py?id_inversiones=\' + id_inversiones;"  class="menuitem-iconic"  image="images/hotsync.png" />\n'
        s= s+ '        <menuitem label="'+_('Actualizar en Internet')+'" oncommand="actualizar_internet();"  class="menuitem-iconic"  image="images/hotsync.png" />           \n'
        s= s+ '        <menuseparator/>\n'
        s= s+ '    <menuitem label="'+_('Modificar la inversión')+'"  oncommand="location=\'inversion_modificar.py?id_inversiones=\' + id_inversiones;"   class="menuitem-iconic"  image="images/edit.png" />\n'
        s= s+ '<menuitem label="'+_('Estudio de la inversión')+'"  oncommand="location=\'inversionoperacion_listado.py?id_inversiones=\' + id_inversiones;"  class="menuitem-iconic"  image="images/toggle_log.png" />\n'
        s= s+ '</popup>\n'
        s= s+ '</popupset>\n'

        s= s+ '<tree id="tree" flex="6"   context="treepopup"  onselect="tree_getid();">\n'
        s= s+ '<treecols>\n'
        s= s+  '<treecol label="Id" hidden="true" />\n'
        s= s+  '<treecol label="'+_('Inversión')+'" flex="2"/>\n'
        s= s+  '<treecol label="'+_('Entidad Bancaria')+'" flex="2"/>\n'
        s= s+  '<treecol label="'+_('Valor Acción')+'" flex="1" style="text-align: right" />\n'
        s= s+  '<treecol label="'+_('Valor Compra')+'" flex="1" style="text-align: right" />\n'
        s= s+  '<treecol label="'+_('Valor Venta')+' " flex="1" style="text-align: right"/>\n'
        s= s+  '<treecol label="% '+_('Compra    ')+'" flex="1" style="text-align: right"/>\n'
        s= s+  '<treecol label="% '+_('Venta     ')+'" flex="1" style="text-align: right"/>\n'
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
            s= s + '<treecell label="'+str(row["inversion"])+ '" />\n'
            s= s + '<treecell label="'+str(row["entidadbancaria"])+ '" />\n'
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
        

    def xul_listado(self, sql):
        """Muestra un listado encapusulado de un listado deinversiones.
        En la etiqueta sumatoria del final y huna propiedad que es total y tiene el total numérico."""
        curs=con.Execute(sql)
        sumsaldos=0
        sumpendiente=0       
        s=      '<script>\n<![CDATA[\n'
        s= s+ 'function popupInversiones(){\n'
        s= s+ '     var tree = document.getElementById("treeInversiones");\n'
        #el boolean de un "0" es true y bolean de un 0 es false
        s= s+ '     var activa=Boolean(Number(tree.view.getCellText(tree.currentIndex,tree.columns.getNamedColumn( "activa"))));\n'
        s= s+ '     var id_inversiones=tree.view.getCellText(tree.currentIndex,tree.columns.getNamedColumn("id"));\n'
        s= s+ '     var popup = document.getElementById("popupInversiones");\n'
        s= s+ '     if (document.getElementById("popmodificar")){\n'#Con que exista este vale
        s= s+ '         popup.removeChild(document.getElementById("popmodificar"));\n'
        s= s+ '         popup.removeChild(document.getElementById("popactiva"));\n'
        s= s+ '         popup.removeChild(document.getElementById("popseparator1"));\n'
        s= s+ '         popup.removeChild(document.getElementById("popestudio"));\n'
        s= s+ '     }\n'
        s= s+ '     var popmodificar=document.createElement("menuitem");\n'
        s= s+ '     popmodificar.setAttribute("id", "popmodificar");\n'
        s= s+ '     popmodificar.setAttribute("label", "'+_('Modificar la inversión')+'");\n'
        s= s+ '     popmodificar.setAttribute("class", "menuitem-iconic");\n'
        s= s+ '     popmodificar.setAttribute("image", "images/edit.png");\n'
        s= s+ '     popmodificar.setAttribute("oncommand", "inversion_modificar();");\n'
        s= s+ '     popup.appendChild(popmodificar);\n'
        s= s+ '     var popactiva=document.createElement("menuitem");\n'
        s= s+ '     popactiva.setAttribute("id", "popactiva");\n'
        s= s+ '     if (activa){\n'
        s= s+ '         popactiva.setAttribute("label", "'+_('Desactivar la inversión')+'");\n'
        s= s+ '         popactiva.setAttribute("checked", "false");\n'
        s= s+ '         popactiva.setAttribute("oncommand", "inversion_modificar_activa();");\n'
        s= s+ '     }else{\n'
        s= s+ '         popactiva.setAttribute("label", "'+_('Activar la inversión')+'");\n'
        s= s+ '         popactiva.setAttribute("checked", "true");\n'
        s= s+ '         popactiva.setAttribute("oncommand", "inversion_modificar_activa();");\n'
        s= s+ '     }\n'
        s= s+ '     popup.appendChild(popactiva);\n'
        s= s+ '     var popseparator1=document.createElement("menuseparator");\n'
        s= s+ '     popseparator1.setAttribute("id", "popseparator1");\n'
        s= s+ '     popup.appendChild(popseparator1);\n'
        s= s+ '     var popestudio=document.createElement("menuitem");\n'
        s= s+ '     popestudio.setAttribute("id", "popestudio");\n'
        s= s+ '     popestudio.setAttribute("label", "'+_('Estudio de la inversión')+'");\n'
        s= s+ '     popestudio.setAttribute("oncommand", "inversion_estudio();");\n'
        s= s+ '     popup.appendChild(popestudio);\n'
        s= s+ '}\n\n'

        s= s+ 'function actualizar_internet(){\n'
        s= s+ '     var tree = document.getElementById("treeInversiones");\n'
        s= s+ '     location=\'inversion_actualizar_internet.py\';\n'
        s= s+ '}\n\n'

        s= s+ 'function inversion_actualizar(){\n'
        s= s+ '     var tree = document.getElementById("treeInversiones");\n'
        s= s+ '     var id_inversiones=tree.view.getCellText(tree.currentIndex,tree.columns.getNamedColumn("id"));\n'
        s= s+ '     location=\'inversion_actualizar.py?id_inversiones=\'+ id_inversiones;\n'
        s= s+ '}\n\n'
        
        s= s+ 'function inversion_modificar(){\n'
        s= s+ '     var tree = document.getElementById("treeInversiones");\n'
        s= s+ '     var id_inversiones=tree.view.getCellText(tree.currentIndex,tree.columns.getNamedColumn("id"));\n'
        s= s+ '     location=\'inversion_modificar.py?id_inversiones=\'+ id_inversiones;\n'
        s= s+ '}\n\n'
        
        s= s+ 'function inversion_estudio(){\n'
        s= s+ '     var tree = document.getElementById("treeInversiones");\n'
        s= s+ '     var id_inversiones=tree.view.getCellText(tree.currentIndex,tree.columns.getNamedColumn("id"));\n'
        s= s+ '     location=\'inversionoperacion_listado.py?id_inversiones=\' + id_inversiones;\n'
        s= s+ '}\n\n'
        
        s= s+ 'function inversion_modificar_activa(){\n'
        s= s+ '     var tree = document.getElementById("treeInversiones");\n'
        s= s+ '     var xmlHttp;\n'
        s= s+ '     var id_inversiones=tree.view.getCellText(tree.currentIndex,tree.columns.getNamedColumn("id"));\n'
        s= s+ '     var activa=Boolean(Number(tree.view.getCellText(tree.currentIndex,tree.columns.getNamedColumn( "activa"))));\n'
        s= s+ '     xmlHttp=new XMLHttpRequest();\n'
        s= s+ '     xmlHttp.onreadystatechange=function(){\n'
        s= s+ '         if(xmlHttp.readyState==4){\n'
        s= s+ '             var ale=xmlHttp.responseText;\n'
        s= s+ '             location="inversion_listado.py";\n'
        s= s+ '         }\n'
        s= s+ '     }\n'
        s= s+ '     var url="ajax/inversion_modificar_activa.py?id_inversiones="+id_inversiones+\'&activa=\'+!activa;\n'
        s= s+ '     xmlHttp.open("GET",url,true);\n'
        s= s+ '     xmlHttp.send(null);\n'
        s= s+ '}\n'
        s= s+ ']]>\n</script>\n\n'                

        s= s+ '<vbox flex="1">\n'
        s= s+ '<popupset>\n'
        s= s+ '    <popup id="popupInversiones" >\n'
        s= s+ '        <menuitem label="'+_('Actualizar el valor')+'" oncommand="inversion_actualizar();"  class="menuitem-iconic"  image="images/hotsync.png" />               \n'
        s= s+ '        <menuitem label="'+_('Actualizar en Internet')+'" oncommand="actualizar_internet();"  class="menuitem-iconic"  image="images/hotsync.png" />           \n'
        s= s+ '        <menuseparator/>\n'
        s= s+ '        <menuitem label="'+_('Nueva inversión')+'" oncommand="location=\'inversion_insertar.py\'" class="menuitem-iconic"  image="images/item_add.png"/>\n'
        s= s+ '    </popup>\n'
        s= s+ '</popupset>\n'

        s= s+ '<tree id="treeInversiones" enableColumnDrag="true" flex="6"   context="popupInversiones"  onselect="popupInversiones();"  ondblclick="inversion_estudio();" >\n'
        s= s+ '    <treecols>\n'
        s= s+  '        <treecol id="id" label="id" hidden="true" />\n'
        s= s+  '        <treecol id="activa" label="'+_('activa')+'" hidden="true" />\n'
        s= s+  '        <treecol id="inversion" label="'+_('Inversión')+'" sort="?col_inversion" sortActive="true" sortDirection="descending" flex="2"/>\n'
        s= s+  '        <treecol id="col_entidad_bancaria" label="'+_('Entidad Bancaria')+'"  sort="?col_entidad_bancaria" sortActive="true" sortDirection="descending" flex="2"/>\n'
        s= s+  '        <treecol id="col_valor" label="'+_('Valor Acción')+'" flex="2" style="text-align: right" />\n'
        s= s+  '        <treecol id="col_valor" label="'+_('Saldo')+'" flex="2" style="text-align: right" />\n'
        s= s+  '        <treecol id="col_saldo" label="'+_('Pendiente')+'" flex="1" style="text-align: right"/>\n'
        s= s+  '        <treecol label="'+_('Invertido')+'" hidden="true"  flex="1" style="text-align: right" />\n'
        s= s+  '        <treecol id="col_saldo" label="'+_('Rendimiento')+'"   sort="?Rendimiento" sortActive="true" sortDirection="descending" flex="1" style="text-align: right"/>\n'
        s= s+  '    </treecols>\n'
        s= s+  '    <treechildren>\n'
        while not curs.EOF:
            row = curs.GetRowAssoc(0)   
            sumsaldos=sumsaldos+ dosdecimales(row['saldo'])
            sumpendiente=sumpendiente+dosdecimales(row['pendiente'])
            s= s + '        <treeitem>\n'
            s= s + '            <treerow>\n'
            s= s + '                <treecell label="'+str(row["id_inversiones"])+ '" />\n'
            s= s + '                <treecell label="'+str(row["in_activa"])+ '" />\n'
            s= s + '                <treecell label="'+str(row["inversion"])+ '" />\n'
            s= s + '                <treecell label="'+ row["entidadbancaria"]+ '" />\n'
            s= s + '                ' + treecell_euros(row["actualizacion"], 3)
            s= s + '                ' + treecell_euros(row['saldo'])
            s= s + '                ' + treecell_euros(row['pendiente'])
            s= s +'                ' +  treecell_euros(row['invertido'])
            if row['saldo']==0 or row['invertido']==0:
                tpc=0
            else:
                tpc=100*row['pendiente']/row['invertido']
            s= s + treecell_tpc(tpc)
            s= s + '            </treerow>\n'
            s= s + '        </treeitem>\n'
            curs.MoveNext()     
        s= s + '    </treechildren>\n'
        s= s + '</tree>\n'
        s= s + '<label flex="0"  id="totalinversiones" style="text-align: center;font-weight : bold;" value="'+_('Saldo total de todas las inversiones')+': '+ euros(sumsaldos)+'. '+_('Pendiente de consolidar')+': '+euros(sumpendiente)+'." total="'+str(sumsaldos)+'" />\n'
        s= s + '</vbox>\n'
        curs.Close()
        return s

    def xul_listado_internet(self, sql):
        """Muestra un listado encapusulado de un listado deinversiones.
        En la etiqueta sumatoria del final y huna propiedad que es total y tiene el total numérico."""
        curs=con.Execute(sql)
        sumsaldos=0
        sumpendiente=0       
        sumdifdiaria=0
        internet=[]
        bolsamadrid(internet)
        bankintergestion(internet)
        carmignacpatrimoinea(internet)
        LyxorETFXBearEUROSTOXX50(internet)
        s=      '<script>\n<![CDATA[\n'
        s= s+ 'function check_data(){\n'
        s= s+ '    resultado=true;\n'
        s= s+ '     var tree = document.getElementById("treeInversiones");\n'
        s= s+ '    if (tree.view.getCellText(tree.currentIndex,tree.columns.getNamedColumn("internet")).split(" ")[0]==0){\n'
        s= s+ '        alert("'+_('Esta inversión no se ha podido actualizar en Internet')+'");\n'
        s= s+ '        resultado=false;\n'
        s= s+ '    }\n'
        s= s+ '    return resultado;\n'
        s= s+ '}\n'
                                    
        s= s+ 'function actualizar_inversion(){\n'
        s= s+ '    if (check_data()==false){\n'
        s= s+ '        return;\n'
        s= s+ '    }\n'                             
        s= s+ '     var tree = document.getElementById("treeInversiones");\n'
        s= s+ '     var id_inversiones=tree.view.getCellText(tree.currentIndex,tree.columns.getNamedColumn("id"));\n'
        s= s+ '     var antiguo=tree.view.getCellText(tree.currentIndex,tree.columns.getNamedColumn("internet"));\n'        
        s= s+ '     var valor=tree.view.getCellText(tree.currentIndex,tree.columns.getNamedColumn("internet")).split(" ")[0];\n'
        s= s+ '    var xmlHttp;\n'
        s= s+ '    xmlHttp=new XMLHttpRequest();\n'
        s= s+ '    xmlHttp.onreadystatechange=function(){\n'
        s= s+ '        if(xmlHttp.readyState==4){\n'
        s= s+ '            var ale=xmlHttp.responseText;\n'
        s= s+ '            parse_ale(ale,"","");\n'
        s= s+ '            tree.view.setCellText(tree.currentIndex,tree.columns.getNamedColumn("valor_accion"),antiguo);\n'
        s= s+ '            tree.view.setCellText(tree.currentIndex,tree.columns.getNamedColumn("ganancia"),"Actualizado");\n'
        s= s+ '        }\n'
        s= s+ '    }\n'
        s= s+ '    var f = new Date;var fecha=f.getFullYear()+"-" +(f.getMonth()+1)+"-"+f.getDate();\n'
        s= s+ '    var url="ajax/inversionactualizacion_insertar.py?id_inversiones="+id_inversiones+  "&fecha=" + fecha + "&valor=" + valor;\n'
        s= s+ '    xmlHttp.open("GET",url,true);\n'
        s= s+ '    xmlHttp.send(null);\n'
        s= s+ '}\n'

        s= s+ ']]>\n</script>\n\n'               
        s= s+ '<vbox flex="1">\n'
        s= s+ '<tree id="treeInversiones" enableColumnDrag="true" flex="6"  ondblclick="actualizar_inversion();">\n'
        s= s+ '<treecols>\n'
        s= s+  '<treecol id="id" label="Id" hidden="true" />\n'
        s= s+  '<treecol label="'+_('Inversión')+'" flex="2"/>\n'
        s= s+  '<treecol label="'+_('Entidad Bancaria')+'" flex="2"/>\n'
        s= s+  '<treecol id="valor_accion" label="'+_('Valor Acción')+'" flex="1" style="text-align: right" />\n'
        s= s+  '        <treecol id="internet" label="'+_('Valor Internet')+'" flex="2" style="text-align: right" />\n'
        s= s+  '        <treecol id="ganancia" label="'+_('Diferencia')+'" flex="2" style="text-align: right" />\n'
        s= s+  '        <treecol label="%" flex="2" style="text-align: right" />\n'
        s= s+  '<treecol label="'+_('Valor Compra')+'" flex="1" style="text-align: right"  hidden="true" />\n'
        s= s+  '<treecol label="'+_('Valor Venta ')+'" flex="1" style="text-align: right" hidden="true" />\n'
        s= s+  '<treecol label="% '+_('Compra    ')+'" flex="1" style="text-align: right"/>\n'
        s= s+  '<treecol label="% '+_('Venta     ')+'" flex="1" style="text-align: right"/>\n'
        s= s+  '</treecols>\n'
        s= s+  '    <treechildren>\n'
        while not curs.EOF:
            row = curs.GetRowAssoc(0)   
            valorInternet=getvalor(internet, str(row["internet"]))            
            if row['actualizacion']==0:
                difdiaria=0
                sumsaldos=sumsaldos
                tpcc=0
                tpcv=0
                tpc=0
            else:
                if valorInternet==0:
                    difdiaria=0
                    sumsaldos=sumsaldos+ dosdecimales(row['acciones']*row["actualizacion"])
                    tpcc=(row["compra"]-row["actualizacion"])*100/row["actualizacion"]
                    tpcv=(row["venta"]-row["actualizacion"])*100/row["actualizacion"]
                    tpc=0
                else:
                    difdiaria=(valorInternet-row["actualizacion"])*row["acciones"]
                    sumsaldos=sumsaldos+ dosdecimales(row['acciones']*valorInternet)
                    tpcc=(row["compra"]-valorInternet)*100/valorInternet
                    tpcv=(row["venta"]-valorInternet)*100/valorInternet
                    tpc=100*(valorInternet-row["actualizacion"])/row["actualizacion"]
                sumdifdiaria=sumdifdiaria+difdiaria            
            if tpcc>0:
                prop=' properties="rowsoftred"'
            elif tpcv<5:
                prop=' properties="rowsoftgreen"'
            else:
                prop=''
            if row['compra']==row['venta']:
                prop=''
            s= s + '<treeitem>\n'
            s= s + '<treerow'+prop+'>\n'
            s= s + '<treecell label="'+str(row["id_inversiones"])+ '" />\n'
            s= s + '<treecell label="'+str(row["inversion"])+ '" />\n'
            s= s + '<treecell label="'+str(row["entidadbancaria"])+ '" />\n'
            s= s + treecell_euros(row["actualizacion"],  3)
            s= s +'<treecell id="rowinternet" label="'+euros(valorInternet, 5)+'" />\n';
            s= s + treecell_euros(difdiaria)
            s= s + treecell_tpc(tpc)
            s= s + treecell_euros( row["compra"] , 3)
            s= s + treecell_euros( row["venta"],  3)
            s= s + treecell_tpc(tpcc)
            s= s + treecell_tpc(tpcv)
            s= s + '</treerow>\n'
            s= s + '</treeitem>\n'
            curs.MoveNext()     
        s= s + '    </treechildren>\n'
        s= s + '</tree>\n'
        s= s + '<label flex="0"  id="totalinversiones" style="text-align: center;font-weight : bold;" value="'+_('Saldo total de todas las inversiones')+': '+ euros(sumsaldos)+'. '+_('Diferencia diaria')+': '+euros(sumdifdiaria)+'" total="'+str(sumsaldos)+'" />\n'
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
        delete="delete from actuinversiones where id_inversiones="+str(id_inversiones)+" and fecha ='"+str(fecha)+"';"
        con.Execute(delete);
        sql="insert into actuinversiones (fecha,id_inversiones,actualizacion) values ('"+ str(fecha) +"',"+str(id_inversiones)+","+str(valor)+")";
        try:
            con.Execute(sql);
        except:
            return False
        return True
        
    def cursor_listado(self, id_inversiones,  year,  month):
        sql="select * from actuinversiones where id_inversiones="+str(id_inversiones)+" and date_part('year',fecha)='"+str(year)+"' and date_part('month',fecha)='"+str(month)+"' order by fecha;"
        return con.Execute(sql); 
        
    def ultima(self,id_inversiones,ano):
        resultado = []
        sql="SELECT fecha,Actualizacion from actuinversiones where id_Inversiones="+str(id_inversiones)+" and  fecha<='"+str(ano)+"-12-31' order by Fecha desc limit 1"
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
        sql="select actualizacion from actuinversiones where id_Inversiones="+str(id_inversiones)+" and  fecha<='"+str(fecha)+"' order by Fecha desc limit 1"
        curs=con.Execute(sql)
        if curs.RecordCount()==0:
            return 0
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
        try:
            con.Execute(sql);
        except:
            return False
        InversionOperacionHistorica().actualizar (id_inversiones);
        CuentaOperacionHeredadaInversion().actualizar_una_inversion(id_inversiones)#Es una inversion ya que la id_operinversion ya no existe. Se ha borrado
        return True
        
    def insertar(self,  fecha,  id_tiposoperaciones,  importe, acciones,  impuestos,  comision, valor_accion,  id_inversiones):
        sql="insert into operinversiones(fecha,  id_tiposoperaciones,  importe, acciones,  impuestos,  comision,  valor_accion,  id_inversiones) values ('" + str(fecha) + "'," + str(id_tiposoperaciones) +","+str(importe)+","+ str(acciones) +","+ str(impuestos) +","+ str(comision) +", "+str(valor_accion)+","+ str(id_inversiones)+');'
        try:
            con.Execute(sql);
            InversionOperacionHistorica().actualizar (id_inversiones)
            CuentaOperacionHeredadaInversion().actualizar_una_inversion(id_inversiones)            
        except:
            return False
        return True
        
    def modificar(self, id_operinversiones,  fecha,  id_tiposoperaciones,  importe, acciones,  impuestos,  comision,    comentario, valor_accion,  id_inversiones):
        sql="update operinversiones set fecha='" + str(fecha) + "', id_tiposoperaciones=" + str(id_tiposoperaciones) +", importe="+str(importe)+", acciones="+ str(acciones) +", impuestos="+ str(impuestos) +", comision="+ str(comision) +", comentario='"+ str(comentario)+"',  valor_accion="+str(valor_accion)+", id_Inversiones="+ str(id_inversiones)+' where id_operinversiones='+str(id_operinversiones)
        try:
            con.Execute(sql);
        except:
            return False
        #//Funcion que actualiza la tabla tmpoperinversiones para ver operinversiones activas
        InversionOperacionHistorica().actualizar (id_inversiones)
        #//Se actualiza la operinversion una funci<F3>n en tmpinversionesheredada que se refleja en opercuentas.
        CuentaOperacionHeredadaInversion().actualizar_una_inversion(id_inversiones)
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
        sql="delete from tmpoperinversioneshistoricas where id_inversiones="+str(id_inversiones)
        curs=con.Execute(sql)
        sql="delete from tmpoperinversiones where id_Inversiones="+str(id_inversiones)
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
        sqlneg="SELECT * from tmpoperinversiones where id_Inversiones="+str(id_inversiones)+" and acciones <0 order by fecha";
        resultneg=con.Execute(sqlneg)
        if resultneg.RecordCount()==0: #Por si no hubiera negativos
            return True;
  
        rowneg= resultneg.GetRowAssoc(0)   
        accionesneg=rowneg['acciones'];
        actuventa=rowneg['valor_accion'];
    
        sqlpos="select * from tmpoperinversiones where id_Inversiones="+str(id_inversiones)+" and acciones >0 order by fecha";
        resultpos=con.Execute(sqlpos)
        accionespos=0;
        while not resultpos.EOF:
            rowpos = resultpos.GetRowAssoc(0)   
            accionespos=rowpos['acciones'];
            dif=accionespos-(-accionesneg);
            if dif>=-0.1 and dif<=0.1: #Si es 0 se inserta el historico que coincide con la venta y se borra el registro negativo
                InversionOperacionHistorica().insertar( rowneg['id_operinversiones'], rowpos['fecha'], rowneg['fecha'], rowneg['id_tiposoperaciones'], rowneg['id_inversiones'], accionesneg, -accionesneg*actuventa, rowneg['impuestos'], rowneg['comision'], rowpos['valor_accion'], rowneg['valor_accion'])#; //Se pone acciones neg porque puede venir de <0.
                InversionOperacionTemporal().borrar(rowneg["id_tmpoperinversiones"]);
                InversionOperacionTemporal().borrar(rowpos["id_tmpoperinversiones"]);
                break
            elif dif<-0.1:#   //Si es <0 es decir hay más acciones negativas que positivas. Se debe introducir en el historico la tmpoperinversion y borrarlo y volver a recorrer el bucle. Restando a accionesneg las acciones ya apuntadas en el historico
                InversionOperacionHistorica().insertar( rowpos['id_operinversiones'], rowpos['fecha'], rowneg['fecha'], rowneg['id_tiposoperaciones'], rowpos['id_inversiones'], -rowpos['acciones'],  rowpos['acciones']*actuventa, rowneg['impuestos'], rowneg['comision'],rowpos['valor_accion'], rowneg['valor_accion']);
                InversionOperacionTemporal().borrar(rowpos["id_tmpoperinversiones"]);
                accionesneg=accionesneg+accionespos#ya que accionesneg es negativo
            elif(dif>0.1):# //Cuando es >0 es decir hay mas acciones positivos se a�ade el registro en el historico con los datos de la operaci�n negativa en su totalidad. Se borra el registro de negativos y de positivos en tmpoperinversiones y se inserta uno con los datos positivos menos lo quitado por el registro negativo. Y se sale del bucle. //Aqu� no se insert la comisi�n porque solo cuando se acaba las acciones positivos   
                InversionOperacionHistorica().insertar( rowpos['id_operinversiones'], rowpos['fecha'], rowneg['fecha'], rowneg['id_tiposoperaciones'], rowneg['id_inversiones'], accionesneg, -accionesneg*actuventa, rowneg['impuestos'], rowneg['comision'],rowpos['valor_accion'], rowneg['valor_accion'])#;//Se pone acciones neg porque puede venir de <0.
                InversionOperacionTemporal().borrar(rowpos["id_tmpoperinversiones"]);
                InversionOperacionTemporal().borrar(rowneg["id_tmpoperinversiones"]);
                InversionOperacionTemporal().insertar(rowpos['id_operinversiones'],rowpos['id_inversiones'], rowpos['fecha'], rowpos['acciones']-(-accionesneg), rowpos['id_tiposoperaciones'],(rowpos['acciones']-(-accionesneg))*actuventa,0,0,rowpos['valor_accion']);
                break;
            resultpos.MoveNext()     
        resultpos.Close()
        #Mira si hay negativos y sino sale debe hacerse otra vez porque aveces se inserta un negativo
        sqlneg="SELECT * from tmpoperinversiones where id_Inversiones="+str(id_inversiones)+" and acciones <0 order by fecha";
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
        sql="SELECT * from operinversiones where id_Inversiones="+str(id_inversiones)+" order by fecha";
        curs=con.Execute(sql); 
        while not curs.EOF:
            row = curs.GetRowAssoc(0)   
            InversionOperacionTemporal().insertar(row['id_operinversiones'],row['id_inversiones'], row['fecha'],row['acciones'],row['id_tiposoperaciones'],row['importe'],row['impuestos'],row['comision'],row['valor_accion']);
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

    def insertar(self, id_operinversiones,fecha_inicio, fecha_venta, id_tiposoperaciones, id_inversiones, acciones, importe, impuestos, comision, valor_accion_compra, valor_accion_venta):
# id_cuentas=Inversion::id_cuentas(con, id_inversiones);
# nombre_inversion=Inversion::nombre(con,id_inversiones);
        sql="insert into tmpoperinversioneshistoricas (fecha_inicio, fecha_venta,id_operinversiones, id_tiposoperaciones, id_inversiones, acciones, importe, impuestos, comision, valor_accion_compra, valor_accion_venta) values ('"+str(fecha_inicio)+"', '"+str(fecha_venta)+"', "+str(id_operinversiones)+", "+str(id_tiposoperaciones)+", "+str(id_inversiones)+", "+str(acciones)+", "+str(importe)+", "+str(impuestos)+", "+str(comision)+", "+str(valor_accion_compra)+", "+str(valor_accion_venta)+")";
        curs=con.Execute(sql); 
        
    def rendimiento_total(self, id_tmpoperinversioneshistoricas):
        """
            Si primera es 0 por ejempleo acciones de ampliaciones de capital que no cuestan nada devuelve 100
        """ 
        sql="SELECT fecha_inicio, fecha_venta, valor_accion_compra, valor_accion_venta,id_inversiones from tmpoperinversioneshistoricas where id_tmpoperinversioneshistoricas= "+ str(id_tmpoperinversioneshistoricas)
        curs=con.Execute(sql); 
        row = curs.GetRowAssoc(0)   
        id_inversiones=row['id_inversiones'];
        primera=row['valor_accion_compra'];
        ultima=row['valor_accion_venta'];
        if primera==0:
            return 100
        Rendimiento=(ultima-primera)*100/primera;
        return Rendimiento;
        
    def xultree(self, sql,  id_inversiones):
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
        s=      '<script>\n<![CDATA[\n'
        s= s+ 'function popupOperInversiones(){\n'
        s= s+ '     var tree = document.getElementById("treeOperInversiones");\n'
        #el boolean de un "0" es true y bolean de un 0 es false
        s= s+ '     var id_operinversiones=tree.view.getCellText(tree.currentIndex,tree.columns.getNamedColumn( "id"));\n'
        s= s+ '     var popup = document.getElementById("popupOperInversiones");\n'
        s= s+ '     if (document.getElementById("popmodificar")){\n'#Con que exista este vale
        s= s+ '         popup.removeChild(document.getElementById("popmodificar"));\n'
        s= s+ '         popup.removeChild(document.getElementById("popborrar"));\n'
        s= s+ '     }\n'
        s= s+ '     var popmodificar=document.createElement("menuitem");\n'
        s= s+ '     popmodificar.setAttribute("id", "popmodificar");\n'
        s= s+ '     popmodificar.setAttribute("label", "'+_('Modificar la operación de inversión')+'");\n'
        s= s+ '     popmodificar.setAttribute("class", "menuitem-iconic");\n'
        s= s+ '     popmodificar.setAttribute("image", "images/edit.png");\n'
        s= s+ '     popmodificar.setAttribute("oncommand", "inversionoperacion_modificar();");\n'
        s= s+ '     popup.appendChild(popmodificar);\n'
        s= s+ '     var popborrar=document.createElement("menuitem");\n'
        s= s+ '     popborrar.setAttribute("id", "popborrar");\n'
        s= s+ '     popborrar.setAttribute("label", "'+_('Borrar la operación de inversión')+'");\n'
        s= s+ '     popborrar.setAttribute("oncommand", "inversionoperacion_borrar();");\n'
        s= s+ '     popborrar.setAttribute("class", "menuitem-iconic");\n'
        s= s+ '     popborrar.setAttribute("image", "images/eventdelete.png");\n'
        s= s+ '     popup.appendChild(popborrar);\n'
        s= s+ '}\n\n'
                
        s= s+ 'function inversionoperacion_insertar(){\n'
        s= s+ '     var tree = document.getElementById("treeOperInversiones");\n'
        s= s+ '     location=\'inversionoperacion_insertar.py?id_inversiones=\'+'+str(id_inversiones)+';\n'
        s= s+ '}\n\n'
        
        s= s+ 'function inversionoperacion_modificar(){\n'
        s= s+ '     var tree = document.getElementById("treeOperInversiones");\n'
        s= s+ '     var id_operinversiones=tree.view.getCellText(tree.currentIndex,tree.columns.getNamedColumn("id"));\n'
        s= s+ '     location=\'inversionoperacion_modificar.py?id_operinversiones=\'+ id_operinversiones;\n'
        s= s+ '}\n\n'
        
        s= s+ 'function inversionoperacion_borrar(){\n'
        s= s+ '     var tree = document.getElementById("treeOperInversiones");\n'
        s= s+ '     var xmlHttp;\n'
        s= s+ '     var id_operinversiones=tree.view.getCellText(tree.currentIndex,tree.columns.getNamedColumn("id"));\n'
        s= s+ '     xmlHttp=new XMLHttpRequest();\n'
        s= s+ '     xmlHttp.onreadystatechange=function(){\n'
        s= s+ '         if(xmlHttp.readyState==4){\n'
        s= s+ '             var ale=xmlHttp.responseText;\n'
        s= s+ '             location="inversionoperacion_listado.py?id_inversiones='+str(id_inversiones)+'";\n'
        s= s+ '         }\n'
        s= s+ '     }\n'
        s= s+ '     var url="ajax/inversionoperacion_borrar.py?id_operinversiones="+id_operinversiones + "&id_inversiones='+str(id_inversiones)+'";\n'
        s= s+ '     xmlHttp.open("GET",url,true);\n'
        s= s+ '     xmlHttp.send(null);\n'
        s= s+ '}\n'
        s= s+ ']]>\n</script>\n\n'                

        s=s+ '<popupset>\n'
        s=s+ '    <popup id="popupOperInversiones" >\n'
        s=s+ '        <menuitem label="'+_('Actualizar las operaciones de la inversión')+'"  oncommand="inversion_actualizaroperaciones();"  />\n'
        s=s+ '        <menuseparator/>\n'
        s=s+ '        <menuitem label="'+_('Nueva operación de inversión')+'" oncommand="inversionoperacion_insertar();" class="menuitem-iconic"  image="images/item_add.png"/>\n'
        s=s+ '    </popup>\n'
        s=s+ '</popupset>\n'

        s=s+ '<vbox flex="1">\n'
        s=s+ '        <tree id="treeOperInversiones" flex="3" context="popupOperInversiones" onselect="popupOperInversiones();"  >\n'
        s=s+ '          <treecols>\n'
        s=s+ '    <treecol id="id" label="id" flex="1" hidden="true"/>\n'
        s=s+ '    <treecol label="'+_('Fecha')+'" flex="1"  style="text-align: center"/>\n'
        s=s+ '    <treecol label="'+_('Acciones')+'" flex="1" style="text-align: right" />\n'
        s=s+ '    <treecol label="'+_('Valor compra')+'" flex="1" style="text-align: right"/>\n'
        s=s+ '    <treecol label="'+_('Importe')+'" flex="1" style="text-align: right"/>\n'
        s=s+ '    <treecol label="'+_('Comisión')+'" flex="1" style="text-align: right"/>\n'
        s=s+ '    <treecol label="'+_('Impuestos')+'" flex="1" style="text-align: right"/>\n'
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
        sql="SELECT fecha  from tmpoperinversiones where id_inversiones="+str(id_inversiones) + " order by fecha limit 1";
        curs=con.Execute(sql); 
        if curs.RecordCount()>0:
            row = curs.GetRowAssoc(0)   
            return row['fecha'];    
        else:
            return None

    def importe_invertido(self, id_inversiones):
        sql="SELECT sum(importe) as suma  from tmpoperinversiones where id_inversiones="+str(id_inversiones);
        curs=con.Execute(sql); 
        row = curs.GetRowAssoc(0)   
        return row['suma'];    

    def insertar(self, id_operinversiones,id_inversiones, fecha,acciones,id_tiposoperaciones,importe,impuestos,comision,valor_accion):
        sql="insert into tmpoperinversiones (id_operinversiones,id_inversiones,fecha, acciones,id_tiposoperaciones,importe,impuestos, comision, valor_accion) values ("+str(id_operinversiones)+", "+str(id_inversiones)+",'"+str(fecha)+"',"+str(acciones)+", "+str(id_tiposoperaciones)+","+str(importe)+","+str(impuestos)+","+str(comision)+", "+str(valor_accion)+")";
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
            El SQL deberá ser del tipo "SELECT * from tmpoperinversiones where id_Inversiones=id_inversiones order by fecha"
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
        s=s+ '    <treecol label="'+_('Fecha')+'" flex="1"  style="text-align: center"/>\n'
        s=s+ '    <treecol label="'+_('Acciones')+'" flex="1" style="text-align: right" />\n'
        s=s+ '    <treecol label="'+_('Valor compra')+'" flex="1" style="text-align: right"/>\n'
        s=s+ '    <treecol label="'+_('Importe')+'" flex="1" style="text-align: right"/>\n'
        s=s+ '    <treecol label="'+_('Pendiente consolidar')+'" flex="1" style="text-align: right"/>\n'
        s=s+ '    <treecol label="% '+_('Año')+'" flex="1" style="text-align: right"/>\n'
        s=s+ '    <treecol label="% '+_('TAE')+'" flex="1" style="text-align: right"/>\n'
        s=s+ '    <treecol label="% '+_('Total')+'" flex="1" style="text-align: right"/>\n'
        s=s+ '    <treecol label="'+_('Ref. Ibex35')+'" flex="1" style="text-align: right"/>\n'
        s=s+ '  </treecols>\n'
        s=s+ '  <treechildren>\n'
        while not curs.EOF:
            row = curs.GetRowAssoc(0)   
            fecha=row["fecha"];
            acciones=row['acciones'];
            actualizacion=row['valor_accion'];
            importe=acciones*actualizacion;
            actualizacionxacciones=actualizacion*acciones;
            pendiente=InversionOperacionTemporal().pendiente_consolidar(row['id_tmpoperinversiones'],row['id_inversiones'], datetime.date.today());
            sumacciones=sumacciones+acciones;
            sumimporte=sumimporte+importe;
            sumpendiente=sumpendiente+pendiente;
            rendimientoanual=InversionOperacionTemporalRendimiento().anual( row['id_tmpoperinversiones'], row['id_inversiones'], datetime.date.today().year);
            rendimientototal=InversionOperacionTemporalRendimiento().total( row['id_tmpoperinversiones'], row['id_inversiones']);     
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
        
        s= s + '<label flex="0"  style="text-align: center;font-weight : bold;" value="'+_('Invertidos')+' '+ euros(sumimporte)+' '+_('con un total de')+' '+str(int(sumacciones))+' '+_('acciones y un valor medio de')+' '+euros(valormedio)+'"/>\n'        
        s= s + '<label flex="0"  style="text-align: center;font-weight : bold;" value="'+_('Saldo pendiente')+' '+ euros(sumpendiente)+'. " />\n'        
        s= s + '</vbox>\n'
        return s
        
    def xultree_referenciaibex(self, sql):
        # fecha
        # inversion
        # importe
        # ibex35
        sumimporte=0;
        curs=con.Execute(sql); 
        s=     ' <tree id="tree" flex="3" >\n'
        s=s+ '  <treecols>\n'
        s=s+ '    <treecol label="'+_('Fecha')+'" flex="1"  style="text-align: center"/>\n'
        s=s+ '    <treecol label="'+_('Inversión')+'" flex="1" style="text-align: left" />\n'
        s=s+ '    <treecol label="'+_('Importe')+'" flex="1" style="text-align: right"/>\n'
        s=s+ '    <treecol label="'+_('Ref. Ibex35')+'" flex="1" style="text-align: right"/>\n'
        s=s+ '  </treecols>\n'
        s=s+ '  <treechildren>\n'
        while not curs.EOF:
            row = curs.GetRowAssoc(0)   
            sumimporte=sumimporte+row['importe'];
            s=s+ '    <treeitem>\n'
            s=s+ '      <treerow>\n'
            s=s+ '       <treecell label="'+ str(row["fecha"])[:-12]+ '" />\n'
            s=s+ '       <treecell label="'+ str(row["inversion"])+ '" />\n'
            s=s+        treecell_euros(row['importe']);
            s=s+        treecell_euros(row['ibex35']);
            s=s+ '      </treerow>\n'
            s=s+ '    </treeitem>\n'
            curs.MoveNext()     
        curs.Close()
        s=s+ '    <treeitem>\n'
        s=s+ '      <treerow>\n'
        s=s+ '       <treecell label="" />\n'
        s=s+ '       <treecell label="'+_('TOTAL')+'" />\n'
        s=s+        treecell_euros(sumimporte);
        s=s+ '       <treecell label="" />\n'
        s=s+ '      </treerow>\n'
        s=s+ '    </treeitem>\n'        
        s=s+ '  </treechildren>\n'
        s=s+ '</tree>\n'
        return s
    
    def actualizar(self, id_inversiones):
        sql="delete from tmpoperinversiones where id_Inversiones="+ str(id_inversiones)+";"
        curs=con.Execute(sql)
        sql="delete from tmpoperinversioneshistoricas where id_Inversiones="+str(id_inversiones)+";"
        curs=con.Execute(sql)
        #Calculo el número de acciones con un sum de las acciones
        numeroacciones=Inversion().numero_acciones(id_inversiones,datetime.date.today())
        #Voy recorriendo el array y a ese total le voy restando las positivas por orden de fecha descendente y las voy insertando en tmpooperinversiones
        sql="SELECT * from operinversiones where id_Inversiones="+str(id_inversiones)+" and acciones >=0 order by fecha desc";
        curs=con.Execute(sql); 
        while not curs.EOF: #Cuando llega a <=0 me paro
            row = curs.GetRowAssoc(0)       
            numeroacciones=numeroacciones-row['acciones'];
            if (numeroacciones==0.0):   #Si es 0 queda como está
                InversionOperacionTemporal().insertar(row["id_operinversiones"],row["id_inversiones"], row["fecha"],row["acciones"],row['id_tiposoperaciones'],row['importe'],row['impuestos'],row['comision'],row['valor_accion'])
                break;
            else:
                if numeroacciones<0:   #Si es <0 le sumo le quito al numero de acciones de esa inversión la parte negativa
                    InversionOperacionTemporal().insertar(row['id_operinversiones'],row['id_inversiones'], row['fecha'],row['acciones']+numeroacciones,row['id_tiposoperaciones'],row['importe'],row['impuestos'],row['comision'],row['valor_accion']);
                    break;
                else: #Cuando es >0
                    InversionOperacionTemporal().insertar(row["id_operinversiones"],row["id_inversiones"], row["fecha"],row["acciones"],row['id_tiposoperaciones'],row['importe'],row['impuestos'],row['comision'],row['valor_accion'])
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
        sql="SELECT id_tmpoperinversiones, acciones  from tmpoperinversiones where id_Inversiones="+ str(id_inversiones)
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
        sql="SELECT id_tmpoperinversiones, acciones  from tmpoperinversiones where id_Inversiones=" + str(id_inversiones)
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
    def insertar(self,  id_cuentas,  tarjeta,  numero, pago_diferido, saldomaximo, tj_activa):
        sql="insert into tarjetas (id_cuentas, tarjeta, numero, pago_diferido, saldomaximo, tj_activa) values ("+ str(id_cuentas) +", '"+str(tarjeta)+"', '"+str(numero)+"', "+str(pago_diferido)+", " + str(saldomaximo) + ", "+str(tj_activa)+");"
        try:
            con.Execute(sql);
        except:
            return False
        return True
        
    def modificar(self, id_tarjetas, tarjeta,  id_cuentas,  numero,  pago_diferido,  saldomaximo):
        sql="update tarjetas set tarjeta='"+str(tarjeta)+"', id_cuentas="+str(id_cuentas)+", numero='"+str(numero)+"', pago_diferido="+str(pago_diferido)+", saldomaximo="+str(saldomaximo)+" where id_tarjetas="+ str(id_tarjetas)
        try:
            con.Execute(sql);
        except:
            return False
        return True

    def modificar_activa(self, id_tarjetas,  activa):
        sql="update tarjetas set tj_activa="+str(activa)+" where id_tarjetas="+ str(id_tarjetas)
        curs=con.Execute(sql); 
        return sql
        
    def saldo_pendiente(self,id_tarjetas):
        sql='select sum(importe) as suma from opertarjetas where id_tarjetas='+ str(id_tarjetas) +' and pagado=false'
        resultado=con.Execute(sql) .GetRowAssoc(0)["suma"]
        if resultado==None:
            return 0
        return resultado

    def xul_listado(self, inactivas,  fecha):
        if inactivas==True:
            sql="select id_tarjetas, cuentas.id_cuentas, tj_activa, tarjeta, cuenta, numero, pago_diferido, saldomaximo from tarjetas,cuentas where tarjetas.id_cuentas=cuentas.id_cuentas order by tarjetas.tarjeta"
        else:
            sql="select id_tarjetas, cuentas.id_cuentas, tj_activa, tarjeta, cuenta, numero, pago_diferido, saldomaximo from tarjetas,cuentas where tarjetas.id_cuentas=cuentas.id_cuentas and tarjetas.tj_activa=true order by tarjetas.tarjeta"
        curs=con.Execute(sql); 
        
        s=      '<script>\n<![CDATA[\n'
        s= s+ 'function popupTarjetas(){\n'
        s= s+ '     var tree = document.getElementById("treeTarjetas");\n'
        #el boolean de un "0" es true y bolean de un 0 es false
        s= s+ '     var activa=Boolean(Number(tree.view.getCellText(tree.currentIndex,tree.columns.getNamedColumn( "activa"))));\n'
        s= s+ '     var id_tarjetas=tree.view.getCellText(tree.currentIndex,tree.columns.getNamedColumn("id"));\n'
        s= s+ '     var diferido=Boolean(Number(tree.view.getCellText(tree.currentIndex,tree.columns.getNamedColumn("diferido"))));\n'
        s= s+ '     var popup = document.getElementById("popupTarjetas");\n'
        s= s+ '     if (document.getElementById("popmodificar")){\n'#Con que exista este vale
        s= s+ '         popup.removeChild(document.getElementById("popmodificar"));\n'
        s= s+ '         popup.removeChild(document.getElementById("popactiva"));\n'
        s= s+ '         popup.removeChild(document.getElementById("popseparator1"));\n'
        s= s+ '         popup.removeChild(document.getElementById("popmovimientos"));\n'
        s= s+ '         popup.removeChild(document.getElementById("popseparator2"));\n'
        s= s+ '     }\n'
        s= s+ '     var popmodificar=document.createElement("menuitem");\n'
        s= s+ '     popmodificar.setAttribute("id", "popmodificar");\n'
        s= s+ '     popmodificar.setAttribute("label", "'+_('Modificar la tarjeta')+'");\n'
        s= s+ '     popmodificar.setAttribute("class", "menuitem-iconic");\n'
        s= s+ '     popmodificar.setAttribute("image", "images/edit.png");\n'
        s= s+ '     popmodificar.setAttribute("oncommand", "tarjeta_modificar();");\n'
        s= s+ '     popup.appendChild(popmodificar);\n'
        s= s+ '     var popseparator1=document.createElement("menuseparator");\n'
        s= s+ '     popseparator1.setAttribute("id", "popseparator1");\n'
        s= s+ '     popup.appendChild(popseparator1);\n'
        s= s+ '     var popactiva=document.createElement("menuitem");\n'
        s= s+ '     popactiva.setAttribute("id", "popactiva");\n'
        s= s+ '     if (activa){\n'
        s= s+ '         popactiva.setAttribute("label", "'+_('Desactivar la tarjeta')+'");\n'
        s= s+ '         popactiva.setAttribute("checked", "false");\n'
        s= s+ '         popactiva.setAttribute("oncommand", "tarjeta_modificar_activa();");\n'
        s= s+ '     }else{\n'
        s= s+ '         popactiva.setAttribute("label", "'+_('Activar la tarjeta')+'");\n'
        s= s+ '         popactiva.setAttribute("checked", "true");\n'
        s= s+ '         popactiva.setAttribute("oncommand", "tarjeta_modificar_activa();");\n'
        s= s+ '     }\n'
        s= s+ '     popup.appendChild(popactiva);\n'
        s= s+ '     var popseparator2=document.createElement("menuseparator");\n'
        s= s+ '     popseparator2.setAttribute("id", "popseparator2");\n'
        s= s+ '     popup.appendChild(popseparator2);\n'
        s= s+ '     var popmovimientos=document.createElement("menuitem");\n'
        s= s+ '     popmovimientos.setAttribute("id", "popmovimientos");\n'
        s= s+ '     if (diferido==false){\n'
        s= s+ '         popmovimientos.setAttribute("label", "'+_('Insertar pago a débito')+'");\n'
        s= s+ '         popmovimientos.setAttribute("oncommand", "tarjeta_insertar_a_debito();");\n'
        s= s+ '     }else{\n'
        s= s+ '         popmovimientos.setAttribute("label", "'+_('Movimientos de la tarjeta')+'");\n'
        s= s+ '         popmovimientos.setAttribute("oncommand", "tarjeta_movimientos();");\n'
        s= s+ '     }\n'
        s= s+ '     popup.appendChild(popmovimientos);\n'
        s= s+ '}\n\n'

        s= s+ 'function tarjeta_modificar(){\n'
        s= s+ '     var tree = document.getElementById("treeTarjetas");\n'
        s= s+ '     var id_tarjetas=tree.view.getCellText(tree.currentIndex,tree.columns.getNamedColumn("id"));\n'
        s= s+ '     location=\'tarjeta_modificar.py?id_tarjetas=\' + id_tarjetas;\n'
        s= s+ '}\n\n'
        
        s= s+ 'function tarjeta_movimientos(){\n'
        s= s+ '     var tree = document.getElementById("treeTarjetas");\n'
        s= s+ '     var id_tarjetas=tree.view.getCellText(tree.currentIndex,tree.columns.getNamedColumn("id"));\n'
        s= s+ '     location=\'tarjetaoperacion_listado.py?id_tarjetas=\' + id_tarjetas;\n'
        s= s+ '}\n\n'
        
        s= s+ 'function tarjeta_insertar_a_debito(){\n'
        s= s+ '     var tree = document.getElementById("treeTarjetas");\n'
        s= s+ '     var id_cuentas=tree.view.getCellText(tree.currentIndex,tree.columns.getNamedColumn("id_cuentas"));\n'
        s= s+ '     var comentario="Operacion de tarjeta a débito";\n'
        s= s+ '     location=\'cuentaoperacion_insertar.py?comentario=\'+comentario+\'&id_cuentas=\'+id_cuentas;\n'
        s= s+ '}\n\n'
        
        s= s+ 'function tarjeta_modificar_activa(){\n'
        s= s+ '     var tree = document.getElementById("treeTarjetas");\n'
        s= s+ '     var xmlHttp;\n'
        s= s+ '     var activa=Boolean(Number(tree.view.getCellText(tree.currentIndex,tree.columns.getNamedColumn("activa"))));\n'
        s= s+ '     var id_tarjetas=tree.view.getCellText(tree.currentIndex,tree.columns.getNamedColumn("id"));\n'
        s= s+ '     xmlHttp=new XMLHttpRequest();\n'
        s= s+ '     xmlHttp.onreadystatechange=function(){\n'
        s= s+ '         if(xmlHttp.readyState==4){\n'
        s= s+ '             var ale=xmlHttp.responseText;\n'
        s= s+ '             location="tarjeta_listado.py";\n'
        s= s+ '         }\n'
        s= s+ '     }\n'
        s= s+ '     var url="ajax/tarjeta_modificar_activa.py?id_tarjetas="+id_tarjetas+\'&activa=\'+!activa;\n'
        s= s+ '     xmlHttp.open("GET",url,true);\n'
        s= s+ '     xmlHttp.send(null);\n'
        s= s+ '}\n'
        
        s= s+ 'function treeTarjetas_doubleclick(){\n'
        s= s+ '     var tree = document.getElementById("treeTarjetas");\n'
        s= s+ '     var diferido=Boolean(Number(tree.view.getCellText(tree.currentIndex,tree.columns.getNamedColumn("diferido"))));\n'
        s= s+ '     if (diferido==false){\n'
        s= s+ '         tarjeta_insertar_a_debito();\n'
        s= s+ '     }else{\n'
        s= s+ '         tarjeta_movimientos();\n'
        s= s+ '     }\n'        
        s= s+ '}\n\n'        
        
        s= s+ ']]>\n</script>\n\n'                   
        
        s= s+ '<popupset>\n'
        s= s+ '     <popup id="popupTarjetas" >\n'
        s= s+ '          <menuitem label="Añadir nueva tarjeta"  oncommand=\'location="tarjeta_insertar.py";\'   class="menuitem-iconic"  image="images/item_add.png"/>\n'
        s= s+ '     </popup>\n'
        s= s+ '</popupset>\n'
        
        s= s+ '<tree id="treeTarjetas" enableColumnDrag="true" flex="6"   context="popupTarjetas"  onselect="popupTarjetas();"  ondblclick="treeTarjetas_doubleclick();" >\n'
        s= s+ '     <treecols>\n'
        s= s+  '          <treecol id="id" label="Id" hidden="true" />\n'
        s= s+  '          <treecol id="id_cuentas" label="Id_cuentas" hidden="true" />\n'
        s= s+  '          <treecol id="activa" label="'+_('Activa')+'" hidden="true" />\n'
        s= s+  '          <treecol id="diferido" label="'+_('Diferido')+'" hidden="true" />\n'
        s= s+  '          <treecol label="'+_('Nombre Tarjeta')+'"  flex="2"/>\n'
        s= s+  '          <treecol label="'+_('Cuenta asociada')+'" flex="2"/>\n'
        s= s+  '          <treecol label="'+_('Número de tarjeta')+'" flex="2" style="text-align: right" />\n'
        s= s+  '          <treecol type="checkbox" label="'+_('Pago diferido')+'" flex="1" style="text-align: right"/>\n'
        s= s+  '          <treecol label="'+_('Saldo máximo')+'" flex="1" style="text-align: right"/>\n'
        s= s+  '          <treecol label="'+_('Saldo pendiente')+'" flex="1" style="text-align: right"/>\n'
        s= s+  '     </treecols>\n'
        s= s+  '     <treechildren>\n'
        while not curs.EOF:
            row = curs.GetRowAssoc(0)   
            s= s + '          <treeitem>\n'
            s= s + '               <treerow>\n'
            s= s + '                    <treecell label="'+str(row["id_tarjetas"])+ '" />\n'
            s= s + '                    <treecell label="'+str(row["id_cuentas"])+ '" />\n'
            s= s + '                    <treecell label="'+str(row["tj_activa"])+ '" />\n'
            s= s + '                    <treecell label="'+str(row["pago_diferido"])+ '" />\n'
            s= s + '                    <treecell label="'+ row["tarjeta"]+ '" />\n'
            s= s + '                    <treecell label="'+row["cuenta"]+ '" />\n'
            s= s + '                    <treecell label="'+ str(row["numero"])+ '" />\n'
            s= s + '                    <treecell properties="'+str(bool(row['pago_diferido']))+'" label="'+ str(row["pago_diferido"])+ '" />\n'
            s= s + '                    '+ treecell_euros(row['saldomaximo'])
            s= s + '                    '+ treecell_euros(Tarjeta().saldo_pendiente(row['id_tarjetas']))
            s= s + '               </treerow>\n'
            s= s + '          </treeitem>\n'
            curs.MoveNext()     
        s= s + '     </treechildren>\n'
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
        
    def insertar(self,  fecha, id_conceptos, id_tiposoperaciones,  importe,  comentario,  id_tarjetas):
        sql="insert into opertarjetas (fecha, id_conceptos, id_tiposoperaciones, importe, comentario, id_tarjetas, pagado) values ('" + fecha + "'," + str(id_conceptos)+","+ str(id_tiposoperaciones) +","+str(importe)+", '"+comentario+"', "+str(id_tarjetas)+", false)"
        try:
            con.Execute(sql);
        except:
            return False
        return True
        
    def modificar_fechapago(self, id_opertarjetas,  fechapago, id_opercuentas):
        sql="update opertarjetas set fechapago='"+str(fechapago)+"', pagado=true "+", id_opercuentas="+str(id_opercuentas)+"  where id_opertarjetas=" +str(id_opertarjetas) 
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
                s=s +  '       <menuitem label="'+utf82xul(row['tipooperacion'])+'" value="'+str(row['id_tiposoperaciones'])+'" selected="true"/>\n'
            else:
                s=s +  '       <menuitem label="'+utf82xul(row['tipooperacion'])+'" value="'+str(row['id_tiposoperaciones'])+'"/>\n'
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
        sql="select sum(Importe) as importe from opercuentas where importe<0 and date_part('year',fecha) = "+str(year)+" and id_tiposoperaciones in (1,7);"
        curs=con.Execute(sql); 
        row = curs.GetRowAssoc(0)   
        if row['importe']==None:
            return 0
        else:
            return row['importe'];


    def grafico_concepto_mensual(self, id,  sectors):
        """Recibe un arrays con dos columans la primera la descripción y la segunda el valor"""
        js=       '<script type="text/ecmascript">\n<![CDATA[\n'
        js= js+ 'function '+str(id)+'showCheese(i){\n'        
        js= js+ '     	document.getElementById("'+str(id)+'tpc").firstChild.nodeValue = document.getElementById("'+str(id)+'cheese" +  i).getAttribute("tpc");\n'
        js= js+ '     	document.getElementById("'+str(id)+'valor").firstChild.nodeValue = document.getElementById("'+str(id)+'cheese" +  i).getAttribute("valor");\n'
        js= js+ '}\n\n'        
        
        js= js+ 'function '+str(id)+'unshow(i){\n'        
        js= js+ '     	document.getElementById("'+str(id)+'tpc").firstChild.nodeValue = "";\n'
        js= js+ '     	document.getElementById("'+str(id)+'valor").firstChild.nodeValue =  "";\n'
        js= js+ '}\n\n'
        js= js+ ']]>\n</script>\n\n'           
        
        header='<svg flex="2" id="'+str(id)+'" width="800" height="340"  viewBox="0 0 800 340"  xmlns="http://www.w3.org/2000/svg" version="1.1" xmlns:xlink="http://www.w3.org/1999/xlink" >\n'
        header=header + '<!-- Gráfico que muestra importes por conceptos. http://xulpymoney.sourcefore.net -->\n'

        total = 0
        i = 0
        seg = 0
        radius = 160
        startx = 160   # The screen x-origin: center of pie chart
        starty = 170   # The screen y-origin: center of pie chart
        lastx = radius # Starting coordinates of 
        lasty = 0      # the first arc
        colors = ['red','blue','yellow','magenta',' thistle ','orange','slateblue','coral','slategrey','greenyellow','wheat','darksalmon','lime','olive', 'darkgreen','orangered', 'violet','brown','mediumslateblue','green', 'gray',  'black', 'gold','salmon',   'white',   'saddlebrown','pink']

        for n in sectors:
            total = total + n[1]  # we have to do this ahead, since we need the total for the next for loop
            
        s='    <defs>\n'        
        for n in sectors:
            arc = "0"                   # default is to draw short arc (< 180 degrees)
            seg = n[1]/total * 360 + seg   # this angle will be current plus all previous
            if ((n[1]/total * 360) > 180): # just in case this piece is > 180 degrees
                arc = "1"
            radseg = math.radians(seg)  # we need to convert to radians for cosine, sine functions
            nextx = int(math.cos(radseg) * radius)
            nexty = int(math.sin(radseg) * radius)
        
            s=s+'        <symbol id="'+str(id)+'def'+str("cheese"+str(i))+'" overflow="visible">\n'
            s=s+'            <path  d="M '+str(startx)+','+str(starty) + ' l '+str(lastx)+','+str(-(lasty))+' a' + str(radius) + ',' + str(radius) + ' 0 ' + arc + ',0 '+str(nextx - lastx)+','+str(-(nexty - lasty))+ ' z" fill="'+colors[i]+'" stroke="black" stroke-width="2" stroke-linejoin="round"/>\n'
            s=s+'        </symbol>\n'          
            lastx = nextx
            lasty = nexty
            i += 1        
        s=s+'    </defs>\n' 

        i=0
        for n in sectors:
            s=s+'        <use id="'+str(id)+str("cheese"+str(i))+'" x="0" y="0"   xlink:href="#'+str(id)+'def'+str("cheese"+str(i))+'" onmouseover="'+str(id)+'showCheese('+str(i)+');"   onmouseout="'+str(id)+'unshow();" valor="'+_('Importe')+': '+str(round(n[1], 2))+' € ('+str(round(n[1]*100/total,2))+' %)" tpc="'+_('Concepto')+': '+str(n[0])+'" />\n'
            i += 1        

        s=s+'        <text id="'+str(id)+'tpc" x="400" y="100"  font-family="Verdana" font-size="14" fill="grey"> </text>\n'
        s=s+'        <text id="'+str(id)+'valor" x="400" y="120"  font-family="Verdana" font-size="14" fill="grey"> </text>\n'
        s=s+'        <text id="'+str(id)+'total" x="400" y="180" font-family="Verdana" font-size="24" fill="blue">'+_('Total')+': '+str(round(total, 2))+' €</text>\n'
        s=s+'</svg>'        # End tag for the SVG file
        
        f=open("/tmp/informe_conceptos_mensual.svg","w")
        f.write('<?xml version="1.0" encoding="utf-8"  standalone="no"?>\n<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"\n "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n'+header +js+ s)
        f.close()
        return js + header + s









    def grafico_evolucion_total(self):
        #Genera informe_total.plot
        f=open("/tmp/informe_total.plot","w")
        s='set encoding utf8\n'
        s=s+'set title "'+_('Evolución temporal del patrimonio')+'"\n'
        s=s+'set style data fsteps\n'
        s=s+"set timefmt '%Y-%m-%d'\n"
        s=s+"set xdata time\n"
        s=s+"set ylabel '"+_('Patrimonio')+" (€)'\n"
        s=s+"set yrange [ 0: ]\n"
        s=s+"set format x '%Y'\n"
        s=s+"set grid\n"
        s=s+"set key left\n"
        s=s+'set term svg size 1000,500 font "/usr/share/fonts/dejavu/DejaVuSans.ttf"\n'
        s=s+"set output \"/tmp/informe_total.svg\"\n"
        s=s+"plot \"/tmp/informe_total.dat\" using 1:2 smooth unique title \""+_('Patrimonio')+"\""
        f.write(s)
        f.close()

        #Genera informe_total.dat
        f=open("/tmp/informe_total.dat","w")
        for i in range (self.primera_fecha_con_datos_usuario().year,  datetime.date.today().year+1):
            f.write(str(i)+"-01-01\t"+str(Total().saldo_total(str(i)+"-01-01"))+"\n")               
            if datetime.date.today()>datetime.date(i,7,1):
                f.write(str(i)+"-07-01\t"+str(Total().saldo_total(str(i)+"-07-01"))+"\n")
        f.write(str(datetime.date.today())+"\t"+str(Total().saldo_total(datetime.date.today()))+"\n")
        f.close()
       
        #Genera informe_total.svg y lo devuleve como string 
        os.popen("gnuplot /tmp/informe_total.plot; chown apache:apache /tmp/informe_total.svg");
        f=open("/tmp/informe_total.svg", "r")
        f.readline()
        f.readline()
        f.readline()
        f.readline()
        s='<svg id="informetotal.svg" flex="1" width="100%" height="100%"  version="1.1"  viewBox="0 0 1000 500"'+f.read()
        f.close()
        return s

    def grafico_inversion_clasificacion(self,  sectors):
        """Recibe un arrays con dos columans la primera la descripción y la segunda el valor"""        
        s='<svg xml:space="svg" flex="2" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg" version="1.1">\n'
        total = 0
        i = 0
        seg = 0
        radius = 150
        startx = 200   # The screen x-origin: center of pie chart
        starty = 200   # The screen y-origin: center of pie chart
        lastx = radius # Starting coordinates of 
        lasty = 0      # the first arc
        ykey = 125
        colors = ['red','blue','yellow','magenta','orange','slateblue','slategrey','greenyellow','wheat']

        for n in sectors:
            total = total + n[1]  # we have to do this ahead, since we need the total for the next for loop
        
        for n in sectors:
            arc = "0"                   # default is to draw short arc (< 180 degrees)
            seg = n[1]/total * 360 + seg   # this angle will be current plus all previous
            if ((n[1]/total * 360) > 180): # just in case this piece is > 180 degrees
                arc = "1"
            radseg = math.radians(seg)  # we need to convert to radians for cosine, sine functions
            nextx = int(math.cos(radseg) * radius)
            nexty = int(math.sin(radseg) * radius)
        
            # The weirdly placed minus signs [eg, (-(lasty))] are due to the fact that our calculations are for a graph with positive Y values going up, but on the screen positive Y values go down.
        
            s=s+'<path d="M '+str(startx)+','+str(starty) + ' l '+str(lastx)+','+str(-(lasty))+' a' + str(radius) + ',' + str(radius) + ' 0 ' + arc + ',0 '+str(nextx - lastx)+','+str(-(nexty - lasty))+ ' z" \n'
            s=s+'fill="'+colors[i]+'" stroke="black" stroke-width="2" stroke-linejoin="round" />\n'
            # We are writing the XML commands one segment at a time, so we abandon old points we don't need anymore, and nextx becomes lastx for the next segment
            s=s+'<rect x="375" y="'+ str(ykey) + '" width="40" height="30" fill="'+colors[i] + '" stroke="black" stroke-width="1"/><text x="425" y="'+str(ykey+20)+'"	style="font-family:verdana, arial, sans-serif;			font-size: 14;			fill: black;			stroke: none">'+n[0]+ ". " +  str(n[1])+ " €. (" +  str(round(n[1]*100/total, 2))+' %)</text>\n'
            ykey = ykey + 35
            lastx = nextx
            lasty = nexty
            i += 1        
        s=s+'<text x="425" y="'+str(ykey+20)+'"	style="font-family:verdana, arial, sans-serif;			font-size: 16;			fill: black;			stroke: none">'+_('TOTAL')+': ' +  str(round(total, 2))+ ' €.</text>\n'
        s=s+'</svg>'        # End tag for the SVG file
        return s













    def grafico_inversionoperacion_refibex(self, ibex,  points,  miles):
        """Recibe dos arrays del tipo operinversiones, ibex, calculos por miles
            points ((row["inversion"], row['fecha'], row['acciones'], row['importe'],referencia_ibex35(row['fecha']) )) 
            ibex((row["fecha"], row['cierre']))
            miles(row['miles'], row['importe'],  round(100*row['sumimporte']/total, 2))"""
 
        
        def fecha2x(fecha):
            """Función que cambia una fecha a una posicion x"""
            i=0
            for ib in ibex:
                if ib[0]==fecha:
                    return i
                else:
                    i=i+xstep
                
        def maximoibex():
            """Calculamos el máximo del ibex"""
            max=0
            for ib in ibex:
                if ib[1]>max:
                    max=ib[1]
            return (int(max/1000)+1)*1000                
        def minimoibex():
            """Calculamos el miniimo del ibex"""
            min=1000000
            for ib in ibex:
                if ib[1]<min:
                    min=ib[1]
            return (int(min/1000))*1000
            
        xstep=20#Avance en x por cada avance en fecha del ibex
        margin=2000#Margen que rodea el grafico por todos los lados
        maxibex=maximoibex()
        minibex=minimoibex()
        maxy=maxibex-minibex  #Maximo del ibex
        maxx=len(ibex)*20  #Maximo del ibex
        firstyear=ibex[0][0].year#Año de la primea operación. 

        js=       '<script type="text/ecmascript">\n<![CDATA[\n'        
        js= js+ 'function gioriShowData(i){\n'        
        js= js+ '     	document.getElementById("gioriover").firstChild.nodeValue = document.getElementById("gioricircle" +  i).getAttribute("inversion") + ". " + document.getElementById("gioricircle" +  i).getAttribute("importe")+ " €. Ibex="  + document.getElementById("gioricircle" +  i).getAttribute("ibex") +" €";\n'
        js= js+ '     	document.getElementById("gioricircle"+i).setAttribute("r","300");\n'
        js= js+ '     	document.getElementById("gioricircle"+i).setAttribute("style","stroke: black; stroke-width: 10; fill: deeppink;fill-opacity: 0.5;");\n'
        js= js+ '}\n\n'        

        js= js+ 'function gioriShowMiles(i){\n'        
        js= js+ '     	document.getElementById("gioriover").firstChild.nodeValue = "'+_('Rango')+' " + i + "000 - " + (i+1) + "000: "+ ". " + document.getElementById("giorirect" +  i).getAttribute("importe")+ " €. ("  + document.getElementById("giorirect" +  i).getAttribute("tpc") +" %)";\n'
        js= js+ '     	document.getElementById("giorirect"+i).setAttribute("style","stroke: none; fill: deeppink;fill-opacity: 0.5;");\n'
        js= js+ '}\n\n'                    

        js= js+ 'function ver_detalle(i){\n'
        js= js+ '    location=\'informe_referenciaibex_detalle.py?rango=\'+ (i*1000);\n'
        js= js+ '}\n'

        js= js+ 'function gioriUnshowMiles(i){\n'        
        js= js+ '     	document.getElementById("gioriover").firstChild.nodeValue = "";\n'
        js= js+ '     	document.getElementById("giorirect"+i).setAttribute("style","stroke: none; fill: gray;fill-opacity: 0;");\n'
        js= js+ '}\n\n'        

        js= js+ 'function gioriUnshow(i){\n'        
        js= js+ '     	document.getElementById("gioriover").firstChild.nodeValue = "";\n'
        js= js+ '     	document.getElementById("gioricircle"+i).setAttribute("r","200");\n'
        js= js+ '     	document.getElementById("gioricircle"+i).setAttribute("style","stroke: black; stroke-width: 10; fill: lime;");\n'
        js= js+ '}\n\n'
        js= js+ ']]>\n</script>\n\n'          
        
        header='<svg flex="1" id="giori" width="1000" height="500"  viewBox="-'+str(margin)+' -'+str(margin)+' '+ str(len(ibex)*xstep+2*margin) +' '+str(maxy+2*margin)+'" preserveAspectRatio="xMidYMid meet"  xmlns="http://www.w3.org/2000/svg" version="1.1" xmlns:xlink="http://www.w3.org/1999/xlink" >\n'
        header=header + '<!-- Gráfico que muestra las inversionoperacion refernciadas al ibex35. http://xulpymoney.sourcefore.net -->\n'

        circles='<!-- Circulos de operinversiones -->\n'
        for p in range(len(points)):
            circles=circles+'<circle id="gioricircle'+str(p)+'" cx="'+str(fecha2x(points[p][1]))+'" cy="'+str(maxibex-points[p][4])+'" r="200" style="stroke: black; stroke-width: 10; fill: lime;" inversion="'+str(points[p][0])+'" fecha="'+ str(points[p][1])[:-12] +'" acciones="'+ str(points[p][2]) +'" importe="'+str(points[p][3])+'"  ibex="'+str(points[p][4])+'"  onmouseover="gioriShowData('+str(p)+');"   onmouseout="gioriUnshow('+str(p)+');" />\n'
                
        libex='<!-- Linea del Ibex -->\n<polyline points="' 
        for i in range(len(ibex)):
            libex=libex+ str(i*xstep) + " " + str(maxibex-ibex[i][1]) + ", "
        libex=libex[:-2]+'" style="stroke: blue; stroke-width: 30; fill: none;" />\n'
        
        rvertical='<!-- Rallado vertical -->\n'        
        scalatexto=30
        rvertical=rvertical+'<line x1="0" y1="'+str(maxy)+'" x2="0" y2="0" style="stroke: black; stroke-width: 60; fill: none;" />\n'
        rvertical=rvertical+'<line x1="'+str(maxx)+'" y1="'+str(maxy)+'" x2="'+str(maxx)+'" y2="0" style="stroke: black; stroke-width: 60; fill: none;" />\n'
        p_year=firstyear
        for ib in ibex:
            if p_year==ib[0].year and ib[0].month==1:
                x=fecha2x(ib[0])
                rvertical=rvertical+'<line x1="'+str(x)+'" y1="'+str(0)+'" x2="'+ str(x) +'" y2="'+str(maxy)+'" style="stroke: gray; stroke-width: 30; fill: none;" />\n'
                rvertical=rvertical+'<text x="'+str(x/scalatexto)+'" y="'+str((maxy + 1000)/scalatexto)+'" transform="scale(30)">'+str(p_year)+'</text>\n' 
                p_year=p_year+1

        rhorizontal='<!-- Rallado horizontal -->\n'       
        for id in range(minibex/1000,  maxibex/1000):
            rhorizontal=rhorizontal+'<line x1="0" y1="'+str(maxibex-id*1000)+'" x2="'+str(maxx)+'" y2="'+str(maxibex-id*1000)+'" style="stroke: gray; stroke-width: 30; fill: none;" />\n'
            rhorizontal=rhorizontal+'<text x="'+str(-1600/scalatexto)+'" y="'+str((maxibex-id*1000)/scalatexto)+'" transform="scale(30)">'+str(id*1000)+'</text>\n' 
                        
        ahorizontal='<!-- Áreas horizontales -->\n'       
        scalatexto=30
        for mi in miles:
            id=int(mi[0]/1000)
            ahorizontal=ahorizontal+'<rect id="giorirect'+str(id)+'" x="0" y="'+str(maxibex-(id+1)*1000)+'" width="'+str(maxx)+'" height="1000" style="stroke: none; fill: gray;fill-opacity: 0;" onmouseover="gioriShowMiles('+str(id)+');" onmouseout="gioriUnshowMiles('+str(id)+');"  onclick="ver_detalle('+str(id)+');"  importe="'+str(mi[1])+'"  tpc="'+str(mi[2])+'" />\n'
        
        marco='<!-- Marco de ejes -->\n'       
        marco=marco+'<line x1="0" y1="'+str(maxy)+'" x2="'+ str(maxx) +'" y2="'+str(maxy)+'" style="stroke: black; stroke-width: 60; fill: none;" />\n' 
        marco=marco+'<line x1="0" y1="'+str(0)+'" x2="'+ str(maxx) +'" y2="'+str(0)+'" style="stroke: black; stroke-width: 60; fill: none;" />\n'
        marco=marco+'<line x1="0" y1="'+str(maxy)+'" x2="'+ str(maxx) +'" y2="'+str(maxy)+'" style="stroke: black; stroke-width: 60; fill: none;" />\n' 
        marco=marco+'<line x1="0" y1="'+str(0)+'" x2="'+ str(maxx) +'" y2="'+str(0)+'" style="stroke: black; stroke-width: 60; fill: none;" />\n'


        panel='<!-- Panel de resultados dinámico -->\n'       
        panel=panel+'<line x1="100" y1="400" x2="1000" y2="400" style="stroke: black; stroke-width: 30; fill: none;" />\n'
        panel=panel+'<text x="25" y="13"	   transform="scale(50)">Ibex 35</text>\n' 
        panel=panel+'<circle cx="600" cy="1000" r="150" style="stroke: black; stroke-width: 10; fill: lime;" />\n'
        panel=panel+'<text x="25" y="28"  transform="scale(50)">'+_('Operación de inversión')+'</text>\n' 
        panel=panel+'<text id="gioriover" x="25" y="43"  transform="scale(50)"> </text>\n' 
       

        foot='</svg>'              
        
        f=open("/tmp/inversionoperacion_refibex.svg","w")
        f.write('<?xml version="1.0" encoding="utf-8"  standalone="no"?>\n<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"\n "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n'+header +js+ marco + rhorizontal + rvertical + ahorizontal + circles +libex+panel+foot)
        f.close()
        return js + header + marco + rhorizontal + ahorizontal + rvertical +circles +libex+panel+foot



















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

    def saldo_por_tipo_operacion(self, ano,  mes,  tipooperacion):
        sql="select sum(Importe) as importe from opercuentas where id_tiposoperaciones="+str(tipooperacion)+" and date_part('year',fecha) = "+str(ano)+" and date_part('month',fecha)= " + str(mes);
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
        sql="select id_dividendos, fecha, liquido, inversion, entidadbancaria from dividendos, inversiones, cuentas, entidadesbancarias where entidadesbancarias.id_entidadesbancarias=cuentas.id_entidadesbancarias and cuentas.id_cuentas=inversiones.id_cuentas and dividendos.id_inversiones=inversiones.id_inversiones and date_part('year',fecha)="+str(ano) + " order by fecha desc;"
        curs=con.Execute(sql); 
        s=     '<vbox flex="1">\n'
        s=s+ '        <tree id="tree" flex="3">\n'
        s=s+ '          <treecols>\n'
        s=s+ '    <treecol label="Fecha" flex="1"  style="text-align: center"/>\n'
        s=s+ '    <treecol label="Inversión" flex="2" style="text-align: left" />\n'
        s=s+ '    <treecol label="Entidad Bancaria" flex="2" style="text-align: left"/>\n'
        s=s+ '    <treecol label="Liquido" flex="1" style="text-align: right"/>\n'
        s=s+ '  </treecols>\n'
        s=s+ '  <treechildren>\n'
        while not curs.EOF:
            row = curs.GetRowAssoc(0)   
            sumsaldos=sumsaldos+dosdecimales(row['liquido'])
            s=s+ '    <treeitem>\n'
            s=s+ '      <treerow>\n'
            s=s+ '       <treecell label="'+ str(row["fecha"])[:-12]+ '" />\n'
            s=s+ '       <treecell label="'+ row["inversion"]+ '" />\n'
            s=s+ '       <treecell label="'+ row["entidadbancaria"]+ '" />\n'
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
        s=s+ '<treecol id="col_fecha_venta" label="'+_('Fecha venta')+'" sort="?col_inversion" sortActive="true" sortDirection="descending" flex="0"  style="text-align: center"/>\n'
        s=s+ '    <treecol id="col_anos_inversion" label="'+_('Años')+'"  sort="?col_entidad_bancaria" sortActive="true" sortDirection="descending" flex="0"  style="text-align: center"/>\n'
        s=s+ '    <treecol id="col_valor" label="'+_('Inversión')+'" flex="2" style="text-align: left" />\n'
        s=s+ '    <treecol id="col_saldo" label="'+_('Tipo Operación')+'" flex="2" style="text-align: left"/>\n'
        s=s+ '    <treecol id="col_pendiente" label="'+_('Saldo inicio')+'" flex="0" style="text-align: right"/>\n'
        s=s+ '    <treecol id="col_rend_anual" label="'+_('Saldo final')+'" flex="0" style="text-align: right"/>\n'
        s=s+ '    <treecol id="col_rend_anual" label="'+_('Consolidado')+'" flex="0" style="text-align: right"/>\n'
        s=s+ '    <treecol id="col_rend_total" label="'+_('Rend. ponderado')+'" flex="0" style="text-align: right"/>\n'
        s=s+ '    <treecol id="col_rend_total" label="'+_('Rend. total')+'" flex="0" style="text-align: right"/>\n'
        s=s+ '  </treecols>\n'
        s=s+ '  <treechildren>\n'
        while not curs.EOF:
            row = curs.GetRowAssoc(0)   
            id_inversiones=row['id_inversiones'];
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
            rowinv=con.Execute("select * from inversiones where id_inversiones="+ str(row['id_inversiones'])).GetRowAssoc(0)
            regTipoOperacion=con.Execute("select *  from tiposoperaciones where id_tiposoperaciones=" + str(row['id_tiposoperaciones'])).GetRowAssoc(0)
            s=s+ '    <treeitem>\n'
            s=s+ '      <treerow>\n'
            s=s+ '       <treecell label="'+str(row["fecha_venta"])[:-12]+ '" />\n'
            s=s+ '       <treecell label="'+str(dosdecimales(anos))+ '" />\n'
            s=s+ '       <treecell label="'+rowinv['inversion']+ '" />\n'
            s=s+ '       <treecell label="'+regTipoOperacion['tipooperacion']+ '" />\n'
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
        s= s + '<label flex="0"  style="text-align: center;font-weight : bold;" value="'+_('Suma de saldos consolidados en el año')+' '+str(ano)+': '+ euros(sumpendiente)+'." />\n'
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
        sumcomisioncustodia=con.Execute("select sum(importe) as suma from opercuentas where id_conceptos=59 and date_part('year',fecha)="+str(ano)).GetRowAssoc(0)["suma"]
        

        plusvalias=sumoperacionespositivas+sumoperacionesnegativas
        dividendosconretencion=Dividendo().suid_liquido_todos(inicio,fin)
        dividendossinretencion=dividendosconretencion*(1+config.dividendwithholding)
        saldototal=Total().saldo_total(datetime.date.today());
        saldototalinicio=Total().saldo_total(inicio)
        beneficiosin=plusvalias+sumcomision+sumcomisioncustodia+dividendossinretencion
        if plusvalias>0:
            beneficiopag=plusvalias*(1-config.taxcapitalappreciation)+sumimpuestos+sumcomision+sumcomisioncustodia+dividendosconretencion
        else:            
            beneficiopag=plusvalias+sumimpuestos+sumcomision+sumcomisioncustodia+dividendosconretencion

        s=      '<vbox flex="1">\n'
        s=s+ ' <tree flex="1">\n'
        s=s+ '  <treecols>\n'
        s=s+ '    <treecol flex="1"  style="text-align: left"/>\n'
        s=s+ '    <treecol label="'+_('Beneficio')+'" flex="1" style="text-align: center"/>\n'
        s=s+ '    <treecol label="% '+_('TAE desde')+' '+inicio+' ('+euros(saldototalinicio)+')" flex="1" style="text-align: center"/>\n'
        s=s+ ' </treecols>\n'
        s=s+ '  <treechildren>\n'
        
        s=s+ '    <treeitem>\n'
        s=s+ '      <treerow>\n'
        s=s+ '          <treecell label="'+_('Plusvalías de inversiones')+'" />\n'
        s=s+treecell_euros(plusvalias);
        try:
            s=s+treecell_tpc((plusvalias)*100/saldototalinicio)
        except ZeroDivisionError:
            s=s+treecell_tpc(0)
        s=s+ '      </treerow>\n'
        s=s+ '   </treeitem>    \n'

        s=s+ '    <treeitem>\n'
        s=s+ '      <treerow>\n'
        s=s+ '          <treecell label="'+_('Dividendos sin retenciones')+'" />\n'
        s=s+treecell_euros(dividendossinretencion);
        try:
            s=s+treecell_tpc((dividendossinretencion)*100/saldototalinicio)
        except ZeroDivisionError:
            s=s+treecell_tpc(0)
        s=s+ '      </treerow>\n'
        s=s+ '   </treeitem>    \n'
        

        
        s=s+ '    <treeitem>\n'
        s=s+ '      <treerow>\n'
        s=s+ '          <treecell label="'+_('Comisiones en operaciones de inversión')+'" />\n'
        s=s+treecell_euros(sumcomision);
        try:
            s=s+treecell_tpc((sumcomision)*100/saldototalinicio)
        except ZeroDivisionError:
            s=s+treecell_tpc(0)
        s=s+ '      </treerow>\n'
        s=s+ '   </treeitem>    \n'        
        
        s=s+ '    <treeitem>\n'
        s=s+ '      <treerow>\n'
        s=s+ '          <treecell label="'+_('Comisiones de custodia')+'" />\n'
        s=s+treecell_euros(sumcomisioncustodia);
        try:
            s=s+treecell_tpc((sumcomisioncustodia)*100/saldototalinicio)
        except ZeroDivisionError:
            s=s+treecell_tpc(0)
        s=s+ '      </treerow>\n'
        s=s+ '   </treeitem>    \n'        
                
        s=s+ '    <treeitem><treerow><treecell label="" /><treecell label="" /><treecell label="" /></treerow></treeitem>    \n'     
                
        s=s+ '    <treeitem>\n'
        s=s+ '      <treerow>\n'
        s=s+ '          <treecell label="'+_('Retenciones venta fondos inversión al')+' '+str(config.taxcapitalappreciation*100)+'%" />\n'
        s=s+treecell_euros(sumimpuestos);
        try:
            s=s+treecell_tpc((sumimpuestos)*100/saldototalinicio)
        except ZeroDivisionError:
            s=s+treecell_tpc(0)
        s=s+ '      </treerow>\n'
        s=s+ '   </treeitem>    \n'
        
        s=s+ '    <treeitem>\n'
        s=s+ '      <treerow>\n'
        s=s+ '          <treecell label="'+_('Retenciones de los dividendos al')+' '+str(config.dividendwithholding*100)+'%" />\n'
        s=s+treecell_euros(dividendosconretencion-dividendossinretencion);
        try:
            s=s+treecell_tpc((dividendosconretencion-dividendossinretencion)*100/saldototalinicio)
        except ZeroDivisionError:
            s=s+treecell_tpc(0)
        s=s+ '      </treerow>\n'
        s=s+ '   </treeitem>    \n'
               
        s=s+ '    <treeitem>\n'
        s=s+ '      <treerow>\n'
        s=s+ '          <treecell label="'+_('Pago impuestos plusvalias al')+' '+str(config.taxcapitalappreciation*100)+'%" />\n'
        s=s+treecell_euros(-plusvalias*config.taxcapitalappreciation);
        try:
            s=s+treecell_tpc((-plusvalias*config.taxcapitalappreciation)*100/saldototalinicio)
        except ZeroDivisionError:
            s=s+treecell_tpc(0)
        s=s+ '      </treerow>\n'
        s=s+ '   </treeitem>    \n'
        
        s=s+ '    <treeitem><treerow><treecell label="" /><treecell label="" /><treecell label="" /></treerow></treeitem>    \n'     
        
        s=s+ '    <treeitem>\n'
        s=s+ '      <treerow>\n'
        s=s+ '         <treecell label="'+_('Beneficio sin impuestos')+'" />\n'
        s=s+treecell_euros(beneficiosin);
        try:
            s=s+treecell_tpc((beneficiosin)*100/saldototalinicio)
        except ZeroDivisionError:
            s=s+treecell_tpc(0)
        s=s+ '      </treerow>\n'
        s=s+ '   </treeitem>\n'
        
        s=s+ '    <treeitem>\n'
        s=s+ '      <treerow>\n'
        s=s+ '         <treecell label="'+_('Beneficio pagando impuestos')+'" />\n'
        s=s+treecell_euros(beneficiopag);
        try:
            s=s+treecell_tpc((beneficiopag)*100/saldototalinicio)
        except ZeroDivisionError:
            s=s+treecell_tpc(0)
        s=s+ '      </treerow>\n'
        s=s+ '   </treeitem>\n'
        
        s=s+ '  </treechildren>\n'
        s=s+ '</tree>\n'
        s= s + '<label flex="0"  style="text-align: center;font-weight : bold;" value="'+_('Valor de mi patrimonio a')+' '+str(datetime.date.today())+': '+ euros(saldototal)+' ( '+ euros(saldototal-saldototalinicio)+' '+_('en este año')+' )" />\n'
        s= s + '</vbox>\n'
        return s        


def mylog(text):
    f=open("/tmp/xulpymoney.log","a")
    f.write(str(datetime.datetime.now()) + "|" + text + "\n")
    f.close()