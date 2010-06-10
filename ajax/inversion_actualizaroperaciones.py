<%#-*- coding: UTF-8 -*-
import datetime
from core import *
con=Conection()
if InversionOperacionTemporal().actualizar(form['id_inversiones']):
    req.write ("Se ha actualizado las operaciones de la inversión correctamente")
else:
    req.write ("Ha habido un error en la actualización de la inversión")
con.close()
%>
