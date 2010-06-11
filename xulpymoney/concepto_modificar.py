# -*- coding: UTF-8 -*-
from mod_python import util
import time
from core import *
from xul import *

def index(req):
    def page():
        s=xulheaderwindowmenu("Xulpymoney > Concepto > Modificar")

        s=s+'<script>\n'
        s=s+'<![CDATA[\n'
         
        s=s+'function concepto_modificar(){\n'
        s=s+'    var xmlHttp;\n'
        s=s+'    xmlHttp=new XMLHttpRequest();\n'
        s=s+'    xmlHttp.onreadystatechange=function(){\n'
        s=s+'        if(xmlHttp.readyState==4){\n'
        s=s+'            var ale=xmlHttp.responseText;\n'
        s=s+'            location="mantenimiento_tablas.psp";\n'
        s=s+'        }\n'
        s=s+'    }\n'
        s=s+'    var id_conceptos='+form["id_conceptos"]+';\n'
        s=s+'    var id_tiposoperaciones = document.getElementById("cmbtiposoperaciones").value;\n'
        s=s+'    var concepto = document.getElementById("concepto").value;\n'
        s=s+'    var url="ajax/concepto_modificar.psp?id_conceptos="+id_conceptos+"&id_tiposoperaciones="+id_tiposoperaciones+"&concepto="+concepto; \n'
        s=s+'    xmlHttp.open("GET",url,true);\n'
        s=s+'    xmlHttp.send(null);\n'
        s=s+'}\n'

        s=s+']]>\n'
        s=s+'</script>\n'

        s=s+'<vbox flex="1">\n'
        s=s+'    <label id="titulo" flex="0" value="Modificar concepto" />\n'
        s=s+'    <label value="" />\n'
        s=s+'    <hbox flex="1">\n'
        s=s+'    <grid align="center">\n'
        s=s+'        <rows>\n'
        s=s+'        <row><label value="Concepto"/><hbox><textbox id="concepto" value="<%=utf82xul(regcon["concepto"])%>"/></hbox></row>\n'
        s=s+'        <row><label value="Tipo de operación"/><hbox>'+cmbTO+'</hbox></row>\n'
        s=s+'        <row><label value="" /><hbox><button id="cmd" label="Aceptar" onclick="concepto_modificar();"/></hbox></row>\n'
        s=s+'        </rows>\n'
        s=s+'    </grid>\n'
        s=s+'    </hbox>\n'
        s=s+'</vbox>\n'
        s=s+'</window>\n'
        
        return s

    form=util.FieldStorage(req)    
    #Consultas BD
    con=Conection()
    cd=ConectionDirect()
    
    regcon=cd.con.Execute("select * from conceptos where id_conceptos="+ form["id_conceptos"]).GetRowAssoc(0)
    cmbTO=TipoOperacion().cmb('select * from tiposoperaciones order by tipooperacion',  regcon["id_tiposoperaciones"],  False)
    con.close()
    cd.close()
    req.content_type="application/vnd.mozilla.xul+xml"
    return page()
