# -*- coding: UTF-8 -*-
from mod_python import util
import time,  calendar
from formato import *
from core import *
from xul import *


def index(req):
    #Consultas BD
    con=Conection()
    hoy=datetime.date.today()
    svg=Total().grafico_evolucion_total()
    
    con.close()
    req.content_type="application/vnd.mozilla.xul+xml"
    req.write(xulheaderwindowmenu("Xulpymoney > Informes > Total > Gráfico"))
    req.write('<vbox  flex="1"  style="overflow: auto">\n')
    req.write(svg)
    req.write('<label value=""/>\n')
    req.write('</vbox>\n')
    req.write('</window>\n')
