<%
#-*- coding: UTF-8 -*-
from core import *
from validar import *
con=Conection()

arr=("fecha","cmbcuentaorigen","cmbcuentadestino", "importe", "comision")
if hasReferer(req) and checkParametros(req,arr):
    if isDate(form['fecha']) and isInt(form['cmbcuentaorigen']) and isInt(form['cmbcuentadestino']) and isFloat(form['importe']) and isFloat(form['comision']):
        if CuentaOperacion().transferencia(form['fecha'], form['cmbcuentaorigen'],  form['cmbcuentadestino'],  form['importe'], form['comision'])==True:
            req.write ("True|")
        else:
            req.write ("False|Ha habido un error en la base de datos")
    else:
        req.write ("False|Error de validación del servidor. Incidencia registrada")
else:
    req.write ("Logout|Se ha registrado una incidencia grave de seguridad. Ha sido expulsado de la sesión")
con.close()
%>

