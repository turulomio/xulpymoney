#-*- coding: UTF-8 -*-
from core import *
def index(req):
    form=req.form
    if form.has_key('internet')==False:
        form['id_inversiones']=""
    con=Conection()
    req.write (Inversion().insertar(form['inversion'],  form['compra'],  form['venta'],  form['tpcvariable'],  form['id_cuentas'],  form['internet']))
    con.close()
    
