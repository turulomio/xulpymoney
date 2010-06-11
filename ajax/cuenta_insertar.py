#-*- coding: UTF-8 -*-
from mod_python import util
from core import *
def index(req):
    form=util.FieldStorage(req)    
    con=Conection()
    if Cuenta().insertar(form['id_entidadesbancarias'],  form['cuenta'],  form['numero_cuenta'],  True)==True:
        req.write ("Se ha insertado el dato")
    else:
        req.write ("Ha habido un error al insertar el dato")
    con.close()
    
