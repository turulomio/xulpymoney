# -*- coding: UTF-8 -*-
from mod_python import util
import time
from core import *
from xul import *


def index(req):
    def page():
        s=xulheaderwindowmenu("Actualizar el valor")
        s=s+'<script src="js/validar.js"></script>\n'
        s=s+'<script>\n'
        s=s+'<![CDATA[\n'
        
        
        s=s+'function borrar_tree() {    \n'
        s=s+'var tree= document.getElementById("tree");\n'
        s=s+'var treechildren= document.getElementById("mytreechildren");\n'
        s=s+'tree.removeChild(treechildren);\n'
        s=s+'}\n'
        
        s=s+'function borrar(){\n'
        s=s+'var tree = document.getElementById("tree");\n'
        s=s+'var selection = tree.contentView.getItemAtIndex(tree.currentIndex);\n'
        s=s+'var id_actuinversiones= selection.firstChild.firstChild.getAttribute("label");\n'
        s=s+'var xmlHttp;\n'
        s=s+'xmlHttp=new XMLHttpRequest();\n'
        s=s+'xmlHttp.onreadystatechange=function(){\n'
        s=s+'if(xmlHttp.readyState==4){\n'
        s=s+'var ale=xmlHttp.responseText;\n'
        s=s+'parse_ale(ale,"","");\n'
        s=s+'update_list();\n'
        s=s+'}\n'
        s=s+'}\n'
        s=s+'var url="ajax/inversionactualizacion_borrar.py?id_actuinversiones="+id_actuinversiones;\n'
        s=s+'xmlHttp.open("GET",url,true);\n'
        s=s+'xmlHttp.send(null);\n'
        s=s+'}\n'
        
        
        
        s=s+'function insert(){\n'
        s=s+'if (isFloat(document.getElementById("valor").value,"valor")==false){\n'
        s=s+'return;\n'
        s=s+'}\n'
        s=s+'var xmlHttp;\n'
        s=s+'xmlHttp=new XMLHttpRequest();\n'
        s=s+'xmlHttp.onreadystatechange=function(){\n'
        s=s+'if(xmlHttp.readyState==4){\n'
        s=s+'var ale=xmlHttp.responseText;\n'
        s=s+'parse_ale(ale,"inversion_listado.py","");\n'
        s=s+'}\n'
        s=s+'}\n'
        s=s+'var valor = document.getElementById("valor").value;\n'
        s=s+'var fecha = document.getElementById("fecha").value;\n'
        s=s+'var id_inversiones=parseInt('+str(id_inversiones)+')\n'
        s=s+'var url="ajax/inversionactualizacion_insertar.py?id_inversiones="+id_inversiones+"&fecha="+fecha+"&valor="+valor;\n'
        s=s+'xmlHttp.open("GET",url,true);\n'
        s=s+'xmlHttp.send(null);\n'
        s=s+'}\n'
        
        
        s=s+'function parse_actualizaciones( response) {\n'
        s=s+'borrar_tree();\n'
        s=s+'var tree = document.getElementById("tree");\n'
        s=s+'var treechildren=document.createElement(\'treechildren\');\n'
        s=s+'treechildren.setAttribute("id", "mytreechildren");\n'
        s=s+'tree.appendChild(treechildren);\n'
        s=s+'var paramList = response.getElementsByTagName(\'actualizacion\');\n'
        s=s+'for (i = 0; i< paramList.length; i++){\n'
        s=s+'var treeitem=document.createElement(\'treeitem\');\n'
        s=s+'treechildren.appendChild(treeitem);\n'
        s=s+'var treerow= document.createElement(\'treerow\');\n'
        s=s+'treeitem.appendChild(treerow);\n'
        s=s+'var treecellid= document.createElement(\'treecell\');\n'
        s=s+'treerow.appendChild(treecellid);\n'
        s=s+'treecellid.setAttribute("label", paramList[i].getAttribute(\'id_actuinversiones\'));\n'
        s=s+'var treecellfecha= document.createElement(\'treecell\');\n'
        s=s+'treerow.appendChild(treecellfecha);\n'
        s=s+'treecellfecha.setAttribute("label", paramList[i].getAttribute(\'fecha\'));\n'
        s=s+'var treecellactualizacion= document.createElement(\'treecell\');\n'
        s=s+'treerow.appendChild(treecellactualizacion);\n'
        s=s+'treecellactualizacion.setAttribute("label", paramList[i].getAttribute(\'actualizacion\')+ " €");\n'
        s=s+'}\n'
        s=s+'}\n'
        
        
        s=s+'function update_list(){\n'
        s=s+'var xmlHttp;\n'
        s=s+'xmlHttp=new XMLHttpRequest();\n'
        s=s+'xmlHttp.onreadystatechange=function(){\n'
        s=s+'if(xmlHttp.readyState==4){\n'
        s=s+'var ale=xmlHttp.responseXML;\n'
        s=s+'parse_actualizaciones(ale);\n'
        s=s+'}\n'
        s=s+'}\n'
        s=s+'var fecha = document.getElementById("fecha").value.split("-");\n'
        s=s+'var url="ajax/inversionactualizacion_listado.py?id_inversiones="+'+str(id_inversiones)+'+"&year="+fecha[0]+"&month="+(fecha[1]);\n'
        s=s+'xmlHttp.open("GET",url,true);\n'
        s=s+'xmlHttp.send(null);\n'
        s=s+'}\n'
        s=s+']]>\n'
        s=s+'</script>\n'
        
        s=s+'<popupset>\n'
        s=s+'<popup id="treepopup" >    \n'
        s=s+'<menuitem label="Borrar la actualización"  oncommand="borrar();"  class="menuitem-iconic" image="images/eventdelete.png"/>\n'
        s=s+'</popup>\n'
        s=s+'</popupset>\n'
        
        s=s+'<vbox flex="1">\n'
        
        s=s+'<label id="titulo" flex="0" value="Actualizar el valor" />\n'
        s=s+'<label id="subtitulo" flex="0" value="'+reg['inversion']+'" />\n'
        s=s+'<hbox flex="1">\n'
        s=s+'<grid align="center">\n'
        s=s+'<rows>\n'
        s=s+'<row><label value="Selecciona una fecha"/><datepicker id="fecha" type="grid"  firstdayofweek="1"  /></row>\n'
        s=s+'<row><label value="Actualiza el valor" /><hbox><textbox id="valor"/></hbox></row>\n'
        s=s+'<row><label value="Pulsa para guardar la actualización" /><hbox><button id="cmd" label="Aceptar" onclick="insert();"/></hbox></row>\n'
        s=s+'</rows>\n'
        s=s+'</grid>\n'
        s=s+'</hbox>\n'
        s=s+'<button id="cmd" label="Ver los datos del mes seleccionado"  class="menuitem-iconic" image="images/hotsync.png" onclick="update_list();"/>\n'
        s=s+'<tree id="tree" enableColumnDrag="true" flex="3"   context="treepopup"  onselect="get_id_actuinversiones();">\n'
        s=s+'<treecols>\n'
        s=s+'<treecol label="id" hidden="true" />\n'
        s=s+'<treecol label="Fecha" flex="1" />\n'
        s=s+'<treecol label="Valor"  flex="1" style="text-align: right"/>\n'
        s=s+'</treecols>\n'
        s=s+'<treechildren id="mytreechildren">\n'
        s=s+'</treechildren>\n'
        s=s+'</tree>\n'
        s=s+'</vbox>\n'
        s=s+'</window>\n'
        return s
    #Consultas BD
    form=util.FieldStorage(req)    
    con=Conection()
    cd=ConectionDirect()
    hoy=datetime.date.today()
    checked=""
    id_inversiones=0
    if form.has_key('id_inversiones'):
        id_inversiones=form['id_inversiones']
    reg=cd.con.Execute("select * from inversiones where id_inversiones="+ str(id_inversiones)).GetRowAssoc(0)
    con.close()
    cd.close()
    req.content_type="application/vnd.mozilla.xul+xml"
    return page()
