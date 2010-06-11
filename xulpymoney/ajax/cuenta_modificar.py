#-*- coding: UTF-8 -*-
from mod_python import util
from core import *
def index(req):
    form=util.FieldStorage(req)    
    con=Conection()
    if Cuenta().modificar(form['id_cuentas'],form['cuenta'], form['id_entidadesbancarias'], form['numero_cuenta'])==True:
        req.write ("Se ha modificado el dato")
    else:
        req.write ("Ha habido un error al modificar el dato")
    con.close()
