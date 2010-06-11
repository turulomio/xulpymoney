# -*- coding: UTF-8 -*-
from mod_python import util
from core import *
from xul import *

def index(req):
    cd=ConectionDirect()
    
    try:
        fecha=cd.con.Execute("select fecha from ibex35 order by fecha desc limit 1;").GetRowAssoc(0)['fecha'].date
        fecha="El último registro del Ibex35 es del " + str(fecha)
    except:
        fecha="Nunca se ha actualizado los datos del Ibex35"
    
    req.content_type="application/vnd.mozilla.xul+xml"
    req.write(xulheaderwindowmenu("Xulpymoney > Mantenimiento > Mantenimiento Ibex 35 "))

    req.write('<script>\n')
    req.write('<![CDATA[\n')
         
    req.write('function update(){\n')
    req.write('    var xmlHttp;\n')
    req.write('    xmlHttp=new XMLHttpRequest();\n')
    req.write('    xmlHttp.onreadystatechange=function(){\n')
    req.write('        if(xmlHttp.readyState==4){\n')
    req.write('            var ale=xmlHttp.responseText;\n')
    req.write('            document.getElementById("resultado").value=ale;\n')
    req.write('            document.getElementById("subtitulo").value=ale;\n')
    req.write('            document.getElementById("button").disabled=false;\n')
    req.write('        }\n')
    req.write('    }\n')
    req.write('    document.getElementById("resultado").value="Este proceso puede durar unos minutos. Actualizando desde Internet ...";\n')
    req.write('    document.getElementById("button").disabled=true;\n')
    req.write('    var url="ajax/mantenimiento_ibex35.py";\n')
    req.write('    xmlHttp.open("GET",url,true);\n')
    req.write('    xmlHttp.send(null);\n')
    req.write('}\n')

    req.write(']]>\n')
    req.write('</script>\n')

    req.write('<vbox align="center">\n')
    req.write('    <label id="titulo"  value="Mantenimiento datos de Ibex 35" />\n')
    req.write('    <label id="subtitulo"  value="'+str(fecha)+'"/>\n')
    req.write('</vbox>\n')
    req.write('<label flex="0"  value="" />\n')
    req.write('<label flex="0"  style="text-align: center;font-weight : bold;" value="Para poder realizar estudios comparativos con el IBEX 35 es necesario actualizar los datos históricos en Internet. Para ello pulse en el siguiente botón" />\n')

    req.write('<label flex="0"  value="" />\n')
    req.write('<button id="button" label="Actualizar datos en Internet" oncommand="update();"/>\n')
    req.write('<label flex="0"  id="resultado" value="" />\n')
    req.write('</window>\n')
    
