<%
#-*- coding: UTF-8 -*-
from core import *
from validar import *
import validar, sys
con=Conection()

arr=("fecha","id_tiposoperaciones","importe",  "acciones",  "impuestos",  "comision",  "valor_accion",  "id_inversiones")
if hasReferer(req) and checkParametros(req,arr):
    if isDate(form['fecha']) and isInt(form['id_tiposoperaciones']) and isFloat(form['importe']) and isFloat(form['acciones']) and isFloat(form['impuestos']) and isFloat(form['comision']) and isFloat(form['valor_accion']) and isInt(form['id_inversiones']):
        if InversionOperacion().insertar(form['fecha'], form['id_tiposoperaciones'], form['importe'], form['acciones'], form['impuestos'], form['comision'], form['valor_accion'], form['id_inversiones'])==True:
            req.write ("True|")
        else:
            req.write ("False|Ha habido un error en la base de datos")
    else:
        req.write ("False|Error de validación del servidor. Incidencia registrada")
else:
    req.write ("Logout|Se ha registrado una incidencia grave de seguridad. Ha sido expulsado de la sesión")
con.close()
%>
