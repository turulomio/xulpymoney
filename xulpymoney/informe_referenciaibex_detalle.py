# -*- coding: UTF-8 -*-
from mod_python import util
from core import *
from xul import *

def index(req):
    def page():
        s=xulheaderwindowmenu("Informe de referencia al Ibex35")
        s=s+'<vbox align="center">\n'
        s=s+'    <label id="titulo"  value="Informe de referencia al Ibex35" />\n'
        s=s+'    <label id="subtitulo"  value="Rango '+rangostr+'" />\n'
        s=s+'</vbox>\n'
        s=s+'<vbox flex="1">\n'
        s=s+tree
        s=s+'</vbox>\n'
        s=s+'</window>\n'
        return s

    form=util.FieldStorage(req)    
    
    if form.has_key('rango'):
       rango=int(form['rango'])
    else:
        util.redirect(req, 'informe_referenciaibex.py')
        
    rangostr=str(rango) + " - " + str(rango+1000)
    con=Conection()
    sql="select tmpoperinversiones.fecha, inversiones.inversion, tmpoperinversiones.importe, floor(ibex35.cierre) as ibex35 from inversiones, tmpoperinversiones, ibex35 where tmpoperinversiones.fecha=ibex35.fecha and inversiones.id_inversiones=tmpoperinversiones.id_inversiones and ibex35.cierre>="+str(rango)+" and ibex35.cierre<"+str(rango+1000)+" order by fecha;"
    tree=InversionOperacionTemporal().xultree_referenciaibex(sql)
    
    req.content_type="application/vnd.mozilla.xul+xml"
    return page()
