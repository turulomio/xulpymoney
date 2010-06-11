#-*- coding: UTF-8 -*-
from mod_python import util
from core import *
def index(req):
    form=util.FieldStorage(req) 
    con=Conection()
    req.write (Inversion().insertar(form['inversion'],  form['compra'],  form['venta'],  form['tpcvariable'],  form['id_cuentas'],  form['internet']))
    con.close()
    
