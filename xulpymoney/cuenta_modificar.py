# -*- coding: UTF-8 -*-
from mod_python import util
import time
from core import *
from xul import *

def index(req):
    def page():
        s=xulheaderwindowmenu("Xulpymoney > Cuenta > Modificar")
        s=s+'<script>\n'
        s=s+'<![CDATA[        \n'
        s=s+'function cuenta_modificar(){\n'
        s=s+'    if (check_data()==false){\n'
        s=s+'        return;\n'
        s=s+'    }\n'
        s=s+'    var xmlHttp;\n'
        s=s+'    xmlHttp=new XMLHttpRequest();\n'
        s=s+'    xmlHttp.onreadystatechange=function(){\n'
        s=s+'        if(xmlHttp.readyState==4){\n'
        s=s+'            var ale=xmlHttp.responseText;\n'
        s=s+'            location="cuenta_listado.py";\n'
        s=s+'        }\n'
        s=s+'    }\n'
        s=s+'    var id_cuentas = '+str(form['id_cuentas'])+';\n'
        s=s+'    var cuenta = document.getElementById("cuenta").value;\n'
        s=s+'    var id_entidadesbancarias = document.getElementById("id_entidadesbancarias").value;\n'
        s=s+'    var numero_cuenta = document.getElementById("numero_cuenta").value;\n'
        s=s+'    var url="ajax/cuenta_modificar.py?id_cuentas="+id_cuentas+"&cuenta="+cuenta+"&id_entidadesbancarias="+id_entidadesbancarias+"&numero_cuenta="+numero_cuenta;\n'
        s=s+'    xmlHttp.open("GET",url,true);\n'
        s=s+'    xmlHttp.send(null);\n'
        s=s+'}\n'

        s=s+'function check_data(){\n'
        s=s+'    resultado=true;\n'
        s=s+'    if (document.getElementById("numero_cuenta").value.length!=20){\n'
        s=s+'        alert("El número de cuenta debe tener 20 caractéres");\n'
        s=s+'        resultado=false;\n'
        s=s+'    }\n'
        s=s+'    if (document.getElementById("numero_cuenta").value.search(/[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]/)==-1){\n'
        s=s+'        alert("Todos los caracteres deben ser numéricos");\n'
        s=s+'        resultado=false;\n'
        s=s+'    }    \n'
        s=s+'    return resultado;\n'
        s=s+'}\n'

        s=s+']]>\n'
        s=s+'</script>\n'

        s=s+'<vbox flex="1">\n'
        s=s+'    <label id="titulo" flex="0" value="Modificar cuenta" />\n'
        s=s+'    <label value="" />\n'
        s=s+'    <hbox flex="1">\n'
        s=s+'    <grid align="center">\n'
        s=s+'        <rows>\n'
        s=s+'        <row><label value="Nombre de la cuenta"/><hbox><textbox id="cuenta" value="'+row["cuenta"]+'"/></hbox></row>\n'
        s=s+'        <row><label value="Entidad Bancaria al que pertenece"/><hbox>'+cmbentidadesbancarias+'</hbox></row>\n'
        s=s+'        <row><label value="Número de cuenta" /><hbox><textbox id="numero_cuenta" value="'+row["numero_cuenta"]+'"/></hbox></row>        \n'
        s=s+'        <row><label value=""/><hbox><button id="cmd" label="Aceptar" onclick="cuenta_modificar();"/></hbox></row>\n'
        s=s+'        </rows>\n'
        s=s+'    </grid>\n'
        s=s+'    </hbox>\n'
        s=s+'</vbox>\n'
        s=s+'</window>        \n'
        return s

    form=util.FieldStorage(req)    
    req.content_type="application/vnd.mozilla.xul+xml"
    
    cd=ConectionDirect()
    con=Conection()
    row=cd.con.Execute("select * from cuentas where id_cuentas="+ form["id_cuentas"]).GetRowAssoc(0)
    cmbentidadesbancarias=EntidadBancaria().cmb('id_entidadesbancarias','select * from entidadesbancarias where eb_activa=true order by entidadbancaria',  row['id_entidadesbancarias'],  False)
    cd.close()
    con.close()
    return page()
