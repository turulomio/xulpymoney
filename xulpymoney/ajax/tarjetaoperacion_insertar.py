#-*- coding: UTF-8 -*-
from mod_python import util
from core import *
def index(req):
    form=util.FieldStorage(req)    
    if form.has_key("comentario")==False:
        form['comentario']=""
    con=Conection()
    if TarjetaOperacion().insertar(form['fecha'], form['id_conceptos'], form['id_tiposoperaciones'], form['importe'], form['comentario'], form['id_tarjetas'])==True:
        req.write ("Se ha insertado el dato")
    else:
        req.write ("Ha habido un error al insertar el dato")
    con.close()
