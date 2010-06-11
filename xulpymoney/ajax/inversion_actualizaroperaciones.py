#-*- coding: UTF-8 -*-
from mod_python import util
import datetime
from core import *
def index(req):
    form=util.FieldStorage(req) 
    con=Conection()
    if InversionOperacionTemporal().actualizar(form['id_inversiones']):
        req.write ("Se ha actualizado las operaciones de la inversión correctamente")
    else:
        req.write ("Ha habido un error en la actualización de la inversión")
    con.close()

