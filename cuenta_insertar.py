# -*- coding: UTF-8 -*-
from mod_python import util
import time
from core import *
from xul import *

def index(req):
    def page():
        s=xulheaderwindowmenu("Xulpymoney > Cuentas > Nueva")
        s=s+'<script>\n'
        s=s+'<![CDATA[\n'
         
        s=s+'function cuenta_insert(){\n'
        s=s+'    var xmlHttp;\n'
        s=s+'    xmlHttp=new XMLHttpRequest();\n'
        s=s+'    xmlHttp.onreadystatechange=function(){\n'
        s=s+'        if(xmlHttp.readyState==4){\n'
        s=s+'            var ale=xmlHttp.responseText;\n'
        s=s+'            location="cuenta_listado.py";\n'
        s=s+'        }\n'
        s=s+'    }\n'
        s=s+'    var id_entidadesbancarias = document.getElementById("id_entidadesbancarias").value;\n'
        s=s+'    var cuenta = document.getElementById("cuenta").value;\n'
        s=s+'    var numero_cuenta = document.getElementById("numero_cuenta").value;\n'
        s=s+'    var url="ajax/cuenta_insertar.py?id_entidadesbancarias="+id_entidadesbancarias+"&cuenta="+cuenta+"&numero_cuenta="+numero_cuenta;\n'
        s=s+'    xmlHttp.open("GET",url,true);\n'
        s=s+'    xmlHttp.send(null);\n'
        s=s+'}\n'

        s=s+']]>\n'
        s=s+'</script>\n'

        s=s+'<vbox flex="1">\n'
        s=s+'    <label id="titulo" flex="0" value="Nueva cuenta" />\n'
        s=s+'    <label value="" />\n'
        s=s+'    <hbox flex="1">\n'
        s=s+'    <grid align="center">\n'
        s=s+'        <rows>\n'
        s=s+'        <row><label value="Entidad Bancaria al que pertenece"/><hbox><%=cmbentidadesbancarias%></hbox></row>\n'
        s=s+'        <row><label value="Nombre de la cuenta"/><hbox><textbox id="cuenta" value="Nueva cuenta"/></hbox></row>\n'
        s=s+'        <row><label value="Número de cuenta" /><hbox><textbox id="numero_cuenta" value="XXXXXXXXXXXXXXXXXXX"/></hbox></row>        \n'
        s=s+'        <row><label value="" /><hbox><button id="cmd" label="Aceptar" onclick="cuenta_insert();"/></hbox></row>\n'
        s=s+'        </rows>\n'
        s=s+'    </grid>\n'
        s=s+'    </hbox>\n'
        s=s+'</vbox>\n'
        s=s+'</window>\n'
        return s

    form=util.FieldStorage(req)    
    #Consultas BD
    con=Conection()
    hoy=datetime.date.today()
    checked=""
    id_inversiones=0
    if form.has_key('id_inversiones'):
        id_inversiones=form['id_inversiones']
    
    cmbentidadesbancarias=EntidadBancaria().cmb('id_entidadesbancarias','select * from entidadesbancarias where eb_activa=true order by entidadbancaria',  0,  False)
    con.close()
    
    req.content_type="application/vnd.mozilla.xul+xml"
    return page()
