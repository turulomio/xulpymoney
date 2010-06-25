# -*- coding: UTF-8 -*-
from mod_python import util
import time
from core import *
from xul import *
from translate import  _

def index(req):
    def page():
        s=xulheaderwindowmenu(_("Xulpymoney > Concepto > Nuevo"))
        s=s+'<script>\n'
        s=s+'<![CDATA[\n'
         
        s=s+'function concepto_insert(){\n'
        s=s+'    var xmlHttp;\n'
        s=s+'    xmlHttp=new XMLHttpRequest();\n'
        s=s+'    xmlHttp.onreadystatechange=function(){\n'
        s=s+'        if(xmlHttp.readyState==4){\n'
        s=s+'            var ale=xmlHttp.responseText;\n'
        s=s+'            location="mantenimiento_tablas.psp";\n'
        s=s+'        }\n'
        s=s+'    }\n'
        s=s+'    var id_tiposoperaciones = document.getElementById("cmbtiposoperaciones").value;\n'
        s=s+'    var concepto = document.getElementById("concepto").value;\n'
        s=s+'    var url="ajax/concepto_insertar.psp?id_tiposoperaciones="+id_tiposoperaciones+"&concepto="+concepto; \n'
        s=s+'    xmlHttp.open("GET",url,true);\n'
        s=s+'    xmlHttp.send(null);\n'
        s=s+'}\n'

        s=s+']]>\n'
        s=s+'</script>\n'

        s=s+'<vbox flex="1">\n'
        s=s+'    <label id="titulo" flex="0" value="'+_('Nuevo concepto')+'" />\n'
        s=s+'    <label value="" />\n'
        s=s+'    <hbox flex="1">\n'
        s=s+'    <grid align="center">\n'
        s=s+'        <rows>\n'
        s=s+'        <row><label value="Concepto"/><hbox><textbox id="concepto" value="'+_('Nuevo concepto')+'"/></hbox></row>\n'
        s=s+'        <row><label value="'+_('Tipo de operación')+'"/><hbox>'+cmbTO+'</hbox></row>\n'
        s=s+'        <row><label value="" /><hbox><button id="cmd" label="'+_('Aceptar')+'" onclick="concepto_insert();"/></hbox></row>\n'
        s=s+'        </rows>\n'
        s=s+'    </grid>\n'
        s=s+'    </hbox>\n'
        s=s+'</vbox>\n'
        s=s+'</window>\n'
        return s

    form=util.FieldStorage(req)    
    #Consultas BD
    con=Conection()
    cmbTO=TipoOperacion().cmb('select * from tiposoperaciones order by tipooperacion',  1,  False)
    con.close()
    
    req.content_type="application/vnd.mozilla.xul+xml"
    return page()
