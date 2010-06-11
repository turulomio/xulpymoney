#-*- coding: UTF-8 -*-
from mod_python import util
from core import *
def index(req):
    form=util.FieldStorage(req)    
    con=Conection()
    if Tarjeta().modificar(form['id_tarjetas'],form['tarjeta'], form['id_cuentas'], form['numero'], form['pago_diferido'], form['saldomaximo'])==True:
        req.write ("Se ha modificado el dato")
    else:
        req.write ("Ha habido un error al modificar el dato")
    con.close()
