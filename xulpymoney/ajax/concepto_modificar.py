#-*- coding: UTF-8 -*-
from core import *
def index(req):
    form=req.form
    con=Conection()
    if Concepto().modificar(form['id_conceptos'], form['concepto'],  form['id_tiposoperaciones'])==True:
        req.write ("Se ha modificado el dato")
    else:
        req.write ("Ha habido un error al modificar el dato")
    con.close()
    
