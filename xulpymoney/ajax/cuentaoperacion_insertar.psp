<%
#-*- coding: UTF-8 -*-
from core import *
from validar import *
con=Conection()

arr=("fecha","id_conceptos","id_tiposoperaciones", "importe", "comentario", "id_cuentas")
if hasReferer(req) : #No se puede chequear parametros porque comentario es "" y no lo mete en el field
    if isDate(form['fecha']) and isInt(form['id_conceptos']) and isInt(form['id_tiposoperaciones']) and isFloat(form['importe']) and isStrDB(form['comentario']) and isInt(form['id_cuentas']) :
        if CuentaOperacion().insertar(form['fecha'], form['id_conceptos'], form['id_tiposoperaciones'], form['importe'], form['comentario'], form['id_cuentas'])==True:
            req.write ("True|")
        else:
            req.write ("False|Ha habido un error en la base de datos")
    else:
        req.write ("False|Error de validación del servidor. Incidencia registrada")
else:
    req.write ("Logout|Se ha registrado una incidencia grave de seguridad. Ha sido expulsado de la sesión")
con.close()
%>



