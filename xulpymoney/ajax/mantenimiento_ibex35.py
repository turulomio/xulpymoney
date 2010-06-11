#-*- coding: UTF-8 -*-
from mod_python import util
from core import *
def index(req):
    form=util.FieldStorage(req)    
    cd=ConectionDirect()
    registros=int(os.popen("xulpymoney_actualizar_datos_ibex35 "+config.dbname+"| grep registros").read().split(" ")[6])
    fecha=cd.con.Execute("select fecha from ibex35 order by fecha desc limit 1;").GetRowAssoc(0)['fecha'].date
    cd.close()
    if registros==0:
        req.write ("Ha habido un error al actualizar los registros del Ibex35. Comprueba tu conexión")
    else:
        req.write ("El último registro del Ibex35 es del " + str(fecha))
    
