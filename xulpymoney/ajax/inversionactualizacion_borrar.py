#-*- coding: UTF-8 -*-
from mod_python import util
from core import *
from validar import *
import validar, sys
def index(req):
    con=Conection()
    
    form=util.FieldStorage(req)    
    arr=[]
    arr.append("id_actuinversiones")
    if hasReferer(req) and checkParametros(req,arr):
        if isInt(form['id_actuinversiones']):
            if InversionActualizacion().borrar(form['id_actuinversiones'])==True:
                req.write ("True|")
            else:
                req.write ("False|Ha habido un error en la base de datos")
        else:
            req.write ("False|Error de validación del servidor. Incidencia registrada")
    else:
        req.write ("Logout|Se ha registrado una incidencia grave de seguridad. Ha sido expulsado de la sesión")
    con.close()

