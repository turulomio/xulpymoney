<%#-*- coding: UTF-8 -*-
from core import *
con=Conection()
req.write (Cuenta().modificar_activa( form['id_cuentas'],  form['activa']))
con.close()
%>
