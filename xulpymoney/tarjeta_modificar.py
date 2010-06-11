# -*- coding: UTF-8 -*-
from mod_python import util
import time
from core import *
from xul import *

def index(req):
    
    req.content_type="application/vnd.mozilla.xul+xml"
    req.write(xulheaderwindowmenu("Xulpymoney > Tarjetas > Modificar"))
    
    cd=ConectionDirect()
    con=Conection()
    row=cd.con.Execute("select * from tarjetas where id_tarjetas="+ form["id_tarjetas"]).GetRowAssoc(0)
    cmbcuentas=Cuenta().cmb('id_cuentas','select * from cuentas where cu_activa=true order by cuenta',  row['id_cuentas'],  False)
    cd.close()
    con.close()
    checked=""
    if row['pago_diferido']==True:
        checked=' checked="true" '

    req.write('<script>\n')
    req.write('<![CDATA[        \n')
    req.write('function tarjeta_modificar(){\n')
    req.write('    var xmlHttp;\n')
    req.write('    xmlHttp=new XMLHttpRequest();\n')
    req.write('    xmlHttp.onreadystatechange=function(){\n')
    req.write('        if(xmlHttp.readyState==4){\n')
    req.write('            var ale=xmlHttp.responseText;\n')
    req.write('            location="tarjeta_listado.py";\n')
    req.write('        }\n')
    req.write('    }\n')
    req.write('    var id_tarjetas = '+str(form['id_tarjetas'])+';\n')
    req.write('    var tarjeta = document.getElementById("tarjeta").value;\n')
    req.write('    var id_cuentas = document.getElementById("id_cuentas").value;\n')
    req.write('    var numero = document.getElementById("numero").value;\n')
    req.write('    var pago_diferido = document.getElementById("pago_diferido").checked;\n')
    req.write('    var saldomaximo = document.getElementById("saldomaximo").value;\n')
    req.write('    var url="ajax/tarjeta_modificar.py?id_tarjetas="+id_tarjetas+"&tarjeta="+tarjeta+"&id_cuentas="+id_cuentas+"&numero="+numero+"&pago_diferido="+pago_diferido+"&saldomaximo="+saldomaximo;\n')
    req.write('    xmlHttp.open("GET",url,true);\n')
    req.write('    xmlHttp.send(null);\n')
    req.write('}\n')
    req.write(']]>\n')
    req.write('</script>\n')

    req.write('<vbox flex="1">\n')
    req.write('    <label id="titulo" flex="0" value="Modificar tarjeta" />\n')
    req.write('    <label value="" />\n')
    req.write('    <hbox flex="1">\n')
    req.write('    <grid align="center">\n')
    req.write('        <rows>\n')
    req.write('        <row><label value="Nombre de la tarjeta"/><hbox><textbox id="tarjeta" value="'+row["tarjeta"]+'"/></hbox></row>\n')
    req.write('        <row><label value="Cuenta asociada"/><hbox>'+str(cmbcuentas)+'</hbox></row>\n')
    req.write('        <row><label value="Número de tarjeta" /><hbox><textbox id="numero" value="'+str(row["numero"])+'"/></hbox></row>        \n')
    req.write('        <row><label value="Pago diferido" /><hbox><checkbox id="pago_diferido" '+checked+'/></hbox></row>\n')
    req.write('        <row><label value="Saldo máximo" /><hbox><textbox id="saldomaximo" value="'+str(row["saldomaximo"])+'"/></hbox></row>\n')
    req.write('        <row><label value=""/><hbox><button id="cmd" label="Aceptar" onclick="tarjeta_modificar();"/></hbox></row>\n')
    req.write('        </rows>\n')
    req.write('    </grid>\n')
    req.write('    </hbox>\n')
    req.write('</vbox>\n')
    req.write('</window>\n')
    
