<%#-*- coding: UTF-8 -*-
from core import *

con=Conection()
if CuentaOperacion().modificar(form['id_opercuentas'],form['fecha'], form['id_conceptos'], form['id_tiposoperaciones'], form['importe'], form['comentario'], form['id_cuentas'])==True:
    req.write ("Se ha modificado la opercuenta correctamente")
else:
    req.write ("Ha habido un error en la modificación de la opercuenta")
con.close()
%>