<%#-*- coding: UTF-8 -*-
from core import *
con=Conection()
if Dividendo().insertar(form['fecha'], form['valorxaccion'], form['bruto'], form['retencion'], form['liquido'], form['id_inversiones'])==True:
    req.write ("Se ha insertado el dato")
else:
    req.write ("Ha habido un error al insertar el dato")
con.close()
%>
