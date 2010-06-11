# -*- coding: UTF-8 -*-
from mod_python import util
import time
from core import *
from xul import *

def index(req):
    #Consultas BD
    con=Conection()
    cd=ConectionDirect()
    hoy=datetime.date.today()
    checked=""
    id_inversiones=0
    if form.has_key('id_inversiones'):
        id_inversiones=form['id_inversiones']
    
    reg=cd.con.Execute("select * from inversiones where id_inversiones="+ str(id_inversiones)).GetRowAssoc(0)
    cmbcuentas=Cuenta().cmb('id_cuentas','select * from cuentas where cu_activa=true order by cuenta',  reg["id_cuentas"],  False)
    cmbtpcvariable=Inversion().cmb_tpcvariable('tpcvariable', reg['tpcvariable'], False)
    con.close()
    cd.close()
    req.content_type="application/vnd.mozilla.xul+xml"
    req.write(xulheaderwindowmenu("Xulpymoney > Inversiones > Modificar"))


    req.write('<script>\n')
    req.write('<![CDATA[\n')
         
    req.write('function insert(){\n')
    req.write('    var xmlHttp;\n')
    req.write('    xmlHttp=new XMLHttpRequest();\n')
    req.write('    xmlHttp.onreadystatechange=function(){\n')
    req.write('        if(xmlHttp.readyState==4){\n')
    req.write('            var ale=xmlHttp.responseText;\n')
    req.write('            location="inversion_listado.py";\n')
    req.write('        }\n')
    req.write('    }\n')
    req.write('    var inversion = document.getElementById("inversion").value;\n')
    req.write('    var compra = document.getElementById("compra").value;\n')
    req.write('    var venta = document.getElementById("venta").value;\n')
    req.write('    var id_cuentas = document.getElementById("id_cuentas").value;\n')
    req.write('    var tpcvariable = document.getElementById("tpcvariable").value;\n')
    req.write('    var internet = document.getElementById("internet").value;\n')
    req.write('    var url="ajax/inversion_modificar.py?id_inversiones="+'+str(id_inversiones )+'+"&inversion="+inversion+"&compra="+compra+"&venta="+venta+"&id_cuentas="+id_cuentas+"&tpcvariable="+tpcvariable +"&internet="+internet;\n')
    req.write('    xmlHttp.open("GET",url,true);\n')
    req.write('    xmlHttp.send(null);\n')
    req.write('}\n')

    req.write(']]>\n')
    req.write('</script>\n')

    req.write('<vbox flex="1">\n')
    req.write('    <label id="titulo" flex="0" value="Modificar la inversión" />\n')
    req.write('    <label id="subtitulo" flex="0" value="'+reg['inversion']+'" />\n')
    req.write('    <hbox flex="1">\n')
    req.write('    <grid align="center">\n')
    req.write('        <rows>\n')
    req.write('        <row><label value="Cuenta asignada"/><hbox><%=cmbcuentas%></hbox></row>\n')
    req.write('        <row><label value="Cambiar el nombre"/><hbox><textbox id="inversion" value="'+reg['inversion'] +'"/></hbox></row>\n')
    req.write('        <row><label value="Actualiza el valor de nueva compra" /><hbox><textbox id="compra" value="'+reg['compra']+'"/></hbox></row>        \n')
    req.write('        <row><label value="Actualiza el valor de venta" /><hbox><textbox id="venta" value="'+reg['venta']+'"/></hbox></row>\n')
    req.write('        <row><label value="Tipo de inversión" /><hbox>'+cmbtpcvariable+'</hbox></row>\n')
    req.write('        <row><label value="Nombre de Internet" /><hbox><textbox id="internet" value="'+reg['internet']+'"/></hbox></row>        \n')
    req.write('        <row><label value="" /><hbox><button id="cmd" label="Aceptar" onclick="insert();"/></hbox></row>\n')
    req.write('        </rows>\n')
    req.write('    </grid>\n')
    req.write('    </hbox>\n')
    req.write('</vbox>\n')
    req.write('</window>\n')
