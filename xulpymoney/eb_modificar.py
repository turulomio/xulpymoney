# -*- coding: UTF-8 -*-
from mod_python import util
import time
from core import *
from xul import *

def index(req):
    def page():
        xulheaderwindowmenu("Xulpymoney > Entidades Bancarias > Modificar")
        s=s+'<script>\n'
        s=s+'<![CDATA[        \n'
        s=s+'function eb_modificar(){\n'
        s=s+'    var xmlHttp;\n'
        s=s+'    xmlHttp=new XMLHttpRequest();\n'
        s=s+'    xmlHttp.onreadystatechange=function(){\n'
        s=s+'        if(xmlHttp.readyState==4){\n'
        s=s+'            var ale=xmlHttp.responseText;\n'
        s=s+'            location="eb_listado.py";\n'
        s=s+'        }\n'
        s=s+'    }\n'
        s=s+'    var id_entidadesbancarias ='+str(form['id_entidadesbancarias'])+' ;\n'
        s=s+'    var entidadbancaria = document.getElementById("entidadbancaria").value;\n'
        s=s+'    var url="ajax/eb_modificar.py?id_entidadesbancarias="+id_entidadesbancarias+"&entidadbancaria="+entidadbancaria;\n'
        s=s+'    xmlHttp.open("GET",url,true);\n'
        s=s+'    xmlHttp.send(null);\n'
        s=s+'}\n'
        s=s+']]>\n'
        s=s+'</script>\n'

        s=s+'<vbox flex="1">\n'
        s=s+'    <label id="titulo" flex="0" value="Modificar entidad bancaria" />\n'
        s=s+'    <label value="" />\n'
        s=s+'    <hbox flex="1">\n'
        s=s+'    <grid align="center">\n'
        s=s+'        <rows>\n'
        s=s+'        <row><label value="Nombre de la entidad"/><hbox><textbox id="entidadbancaria" value="'+row["entidadbancaria"]+'"/></hbox></row>\n'
        s=s+'        <row><label value=""/><hbox><button id="cmd" label="Aceptar" onclick="eb_modificar();"/></hbox></row>\n'
        s=s+'        </rows>\n'
        s=s+'    </grid>\n'
        s=s+'    </hbox>\n'
        s=s+'</vbox>\n'
        s=s+'</window>\n'
        return s

    form=util.FieldStorage(req)    
    cd=ConectionDirect()
    row=cd.con.Execute("select * from entidadesbancarias where id_entidadesbancarias="+ form["id_entidadesbancarias"]).GetRowAssoc(0)
    cd.close()
    req.content_type="application/vnd.mozilla.xul+xml"
    return page()
