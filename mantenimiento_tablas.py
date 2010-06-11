# -*- coding: UTF-8 -*-
from mod_python import util
import sys
from xul import *
from core import *

def index(req):
    req.content_type="application/vnd.mozilla.xul+xml"
    req.write(xulheaderwindowmenu("Xulpymoney > Mantenimiento > Tablas auxiliares"))
    
    con=Conection()
    lstConceptos=Concepto().xultree("select * from conceptos, tiposoperaciones where conceptos.id_tiposoperaciones=tiposoperaciones.id_tiposoperaciones order by concepto" )
    con.close()

    req.write('<vbox  flex="5">\n')
    req.write('<label id="titulo" value="Tablas auxiliares"/>\n')
    req.write('<hbox flex="4">\n')
    req.write('<tabbox orient="vertical" flex="1">\n')
    req.write('<tabs>\n')
    req.write('<tab label="Conceptos" />\n')
    req.write('</tabs>\n')
    req.write('<tabpanels flex="1">\n')
    req.write('<vbox>\n')
    req.write(lstConceptos)
    req.write('</vbox>\n')
    req.write('</tabpanels>\n')
    req.write('</tabbox>\n')

    req.write('</hbox>\n')

    req.write('</vbox>\n')
    req.write(xulfoot())
