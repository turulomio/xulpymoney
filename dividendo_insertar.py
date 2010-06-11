# -*- coding: UTF-8 -*-
from mod_python import util
import time
from core import *
from xul import *

def index(req):
    def page():
        s=xulheaderwindowmenu("Xulpymoney > Inversiones > Dividendo > Nuevo")
        s=s+'<script>\n'
        s=s+'<![CDATA[\n'
        s=s+'function insert(){\n'
        s=s+'    var id_inversiones='+str(id_inversiones)+';\n'
        s=s+'    var fecha = document.getElementById("fecha").value;\n'
        s=s+'    var valorxaccion = document.getElementById("valorxaccion").value;\n'
        s=s+'    var bruto = document.getElementById("bruto").value;\n'
        s=s+'    var retencion = document.getElementById("retencion").value;\n'
        s=s+'    var liquido = document.getElementById("liquido").value;\n'
        s=s+'    var xmlHttp;\n'
        s=s+'    xmlHttp=new XMLHttpRequest();\n'
        s=s+'    xmlHttp.onreadystatechange=function(){\n'
        s=s+'        if(xmlHttp.readyState==4){\n'
        s=s+'            var ale=xmlHttp.responseText;\n'
        s=s+'            location="inversionoperacion_listado.py?id_inversiones="+id_inversiones;\n'
        s=s+'        }\n'
        s=s+'    }\n'
        s=s+'    var url="ajax/dividendo_insertar.py?fecha="+fecha+"&valorxaccion="+valorxaccion+"&bruto="+bruto+"&retencion="+retencion+"&liquido="+liquido+"&id_inversiones="+id_inversiones;\n'
        s=s+'    xmlHttp.open("GET",url,true);\n'
        s=s+'    xmlHttp.send(null);\n'
        s=s+'}\n'
        
        s=s+']]>\n'
        s=s+'</script>\n'
        
        s=s+'<vbox flex="1">\n'
        s=s+'    <label id="titulo" flex="0" value="Nuevo dividendo" />\n'
        s=s+'    <label value="" />\n'
        s=s+'    <hbox flex="1">\n'
        s=s+'    <grid align="center">\n'
        s=s+'        <rows>\n'
        s=s+'        <row><label value="Introduce la fecha"/><hbox><datepicker id="fecha" type="grid"  firstdayofweek="1"/></hbox></row>\n'
        s=s+'        <row><label value="Valor de la acción"/><hbox><textbox id="valorxaccion" value="0"/></hbox></row>\n'
        s=s+'        <row><label value="Importe bruto" /><hbox><textbox id="bruto" value="0"/></hbox></row>        \n'
        s=s+'        <row><label value="Retención" /><hbox><textbox id="retencion" value="0"/></hbox></row>\n'
        s=s+'        <row><label value="Valor líquido" /><hbox><textbox id="liquido" value="0"/></hbox></row>\n'
        s=s+'        <row><label value="" /><hbox><button id="cmd" label="Aceptar" onclick="insert();"/></hbox></row>\n'
        s=s+'        </rows>\n'
        s=s+'    </grid>\n'
        s=s+'    </hbox>\n'
        s=s+'</vbox>\n'
        s=s+'</window>\n'
        return s

    form=util.FieldStorage(req)    
    #Consultas BD
    con=Conection()
    checked=""
    id_inversiones=0
    if form.has_key('id_inversiones'):
        id_inversiones=form['id_inversiones']
    
    con.close()
    
    req.content_type="application/vnd.mozilla.xul+xml"
    return page()
