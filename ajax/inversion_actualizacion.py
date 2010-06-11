#-*- coding: UTF-8 -*-
from mod_python import util
import datetime
from validar import *
from core import *
from inversion_actualizacion import *
def index(req):
    form=util.FieldStorage(req)    
    con=Conection()
    if isInt(form['id_inversiones']) and  actualizar(form['inversion']
    if InversionActualizacion().insertar(form['id_inversiones'], datetime.date.today(), actualizar(form['inversion']))==True:
        req.write ("Se ha actualizado la inversión correctamente")
    else:
        req.write ("Ha habido un error en la actualización de la inversión")
    con.close()
