#-*- coding: UTF-8 -*-
from mod_python import util
from core import *
def index(req):
    form=util.FieldStorage(req)    
    con=Conection()
    if TarjetaOperacion().borrar(form['id_opertarjetas'])==True:
        req.write ("Se ha borrado el dato")
    else:
        req.write ("Ha habido un error en el borrado del dato")
    con.close()
