<%#-*- coding: UTF-8 -*-
from core import *
con=Conection().open()
if CuentaOperacion().borrar(form['id_opercuentas'])==True:
    req.write ("Se ha borrado el dato")
else:
    req.write ("Ha habido un error en el borrado del dato")
con.Close()
%>
