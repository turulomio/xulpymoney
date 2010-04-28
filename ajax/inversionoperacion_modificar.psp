<%#-*- coding: UTF-8 -*-
from core import *
con=Conection()
if InversionOperacion().modificar(form['id_operinversiones'], form['fecha'], form['id_tiposoperaciones'], form['importe'], form['acciones'], form['impuestos'], form['comision'], form['comentario'], form['valor_accion'], form['id_inversiones'])==True:
    req.write ("Se ha modificado el dato")
else:
    req.write ("Ha habido un error al modificar el dato")
con.close()
%>
