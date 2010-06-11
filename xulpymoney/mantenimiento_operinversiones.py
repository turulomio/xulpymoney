# -*- coding: UTF-8 -*-
from mod_python import util
from core import *
from xul import *

def index(req):
    con=Conection()
    InversionOperacionHistorica().actualizar_todas()
    CuentaOperacionHeredadaInversion().actualizar_todas()
    con.close()
    req.content_type="application/vnd.mozilla.xul+xml"
    req.write(xulheaderwindowmenu("Xulpymoney > Mantenimiento > Mantenimiento Operaciones Inversióno"))

req.write('<script>\n')
req.write('<![CDATA[\n')
         
req.write('function update(){\n')
req.write('    var xmlHttp;\n')
req.write('    xmlHttp=new XMLHttpRequest();\n')
req.write('    xmlHttp.onreadystatechange=function(){\n')
req.write('        if(xmlHttp.readyState==4){\n')
req.write('            var ale=xmlHttp.responseText;\n')
req.write('             document.getElementById("resultado").value=ale;\n')
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
req.write('    <label id="titulo"  value="Mantenimiento operaciones de inversión" />\n')
req.write('</vbox>\n')
req.write('<label flex="0"  value="" />\n')
req.write('<label flex="0"  style="text-align: center;font-weight : bold;" value="En esta pagina se ejecuta el mantenimiento de las operaciones de inversión" />\n')
req.write('</window>\n')
