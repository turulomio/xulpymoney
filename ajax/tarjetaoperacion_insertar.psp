<%#-*- coding: UTF-8 -*-
from core import *
con=Conection()
if TarjetaOperacion().insertar(form['fecha'], form['id_conceptos'], form['id_tiposoperaciones'], form['importe'], form['comentario'], form['id_tarjetas'])==True:
    req.write ("Se ha insertado el dato")
else:
    req.write ("Ha habido un error al insertar el dato")
con.close()
%>