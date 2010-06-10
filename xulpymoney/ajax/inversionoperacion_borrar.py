<%#-*- coding: UTF-8 -*-
from core import *
con=Conection()
if InversionOperacion().borrar(form['id_operinversiones'],  form['id_inversiones'])==True:
    req.write ("Se ha borrado el dato")
else:
    req.write ("Ha habido un error en el borrado del dato")
con.close()
%>
