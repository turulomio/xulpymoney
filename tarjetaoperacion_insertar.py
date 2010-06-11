# -*- coding: UTF-8 -*-
from mod_python import util
from core import *
from xul import *

def index(req):
    if form.has_key('concepto'):
       concepto=int(form['concepto'])
    else:
        concepto=""
        
    con=Conection()
    cmbconcepto=Concepto().cmb('select * from conceptos where id_tiposoperaciones in (1,2) order by concepto',  concepto,  False)
    
    req.content_type="application/vnd.mozilla.xul+xml"
    req.write(xulheaderwindowmenu("Insertando una operación de tarjeta"))
    con.close()

    req.write('<script>\n')
    req.write('<![CDATA[\n')
    req.write('function insert(){\n')
    req.write('    var xmlHttp;    \n')
    req.write('    var sp=document.getElementById("cmbconceptos").value.split(";")\n')
    req.write('    var importe=document.getElementById("importe").value;\n')
    req.write('    var id_conceptos=sp[0];\n')
    req.write('    var id_tiposoperaciones=sp[1];\n')
    req.write('    var comentario= document.getElementById("comentario").value;\n')
    req.write('    var fecha = document.getElementById("fecha").value;\n')
    req.write('    spfecha=fecha.split("-");\n')
    req.write('    var id_tarjetas='+str(form['id_tarjetas'])+';\n')
    req.write('    var url="ajax/tarjetaoperacion_insertar.py?fecha="+fecha+"&id_conceptos="+id_conceptos+"&id_tiposoperaciones="+id_tiposoperaciones+"&importe="+importe+"&comentario="+comentario+"&id_tarjetas="+id_tarjetas;\n')
    req.write('    xmlHttp=new XMLHttpRequest();\n')
    req.write('    xmlHttp.onreadystatechange=function(){\n')
    req.write('        if(xmlHttp.readyState==4){\n')
    req.write('            var ale=xmlHttp.responseText;\n')
    req.write('            location="tarjetaoperacion_listado.py?id_tarjetas="+ id_tarjetas ;\n')
    req.write('        }\n')
    req.write('    }\n')

    req.write('    xmlHttp.open("GET",url,true);\n')
    req.write('    xmlHttp.send(null);\n')
    req.write('}\n')
    req.write(']]>\n')
    req.write('</script>\n')
    req.write('<label id="titulo" value="Nueva operación de tarjeta" />\n')
    req.write('<vbox flex="5">\n')
    req.write('<grid pack="center">\n')
    req.write('    <columns>\n')
    req.write('        <column flex="1" />\n')
    req.write('        <column flex="1" />\n')
    req.write('    </columns>\n')
    req.write('    <rows>\n')
    req.write('        <row>\n')
    req.write('            <label id="negrita" value="Fecha"/>\n')
    req.write('            <datepicker id="fecha" type="grid"  firstdayofweek="1"/>\n')
    req.write('        </row>\n')
    req.write('        <row>\n')
    req.write('            <label id="negrita" value="Concepto"/>\n')
    req.write(cmbconcepto)
    req.write('        </row>\n')
    req.write('        <row>\n')
    req.write('            <label id="negrita" value="Importe"/>\n')
    req.write('            <textbox id="importe"/>\n')
    req.write('        </row>\n')
    req.write('        <row>\n')
    req.write('            <label id="negrita" value="Comentario"/>\n')
    req.write('            <textbox id="comentario"/>\n')
    req.write('        </row>\n')
    req.write('    </rows>\n')
    req.write('</grid>\n')
    req.write('    <button label="Aceptar" oncommand="insert();"/>\n')

    req.write('</vbox>\n')
    req.write('</window>\n')
