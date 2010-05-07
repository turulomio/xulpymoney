# -*- coding: UTF-8 -*-
#Poblema de seguridad 001. No hay referer
#Poblema de seguridad 002. Número de parámetros erróneo
from core import * 
from mod_python import util

def isFloat(a):
    try:
        float(a)
    except:
        mylog("Error de validación: "  + str(a) + " no es un float,  es un " + str(a.__class__))
        return False
    return True
        
def isInt(a):
    try:
        int(a)
    except:
        mylog("Error de validación: " + str(a) + " no es un int,  es un " + str(a.__class__))
        return False
    return True
    
def isDate(a):
    try:
        b=a.split("-")
        datetime.date(int(b[0]), int(b[1]), int(b[2]))
    except:
        mylog("Error de validación: " + str(a) + " no es un datetime.date,  es un " + str(a.__class__))
        return False
    return True
        
        
def isStrDB(a):
    try:
        str(a)
        if a.find('"')!=-1 or a.find("'")!=-1:
            return False
    except:
        return False
    return True

def hasReferer(req):
    if req.headers_in.has_key("Referer")==False:
        mylog("Logout|No hay referer|" + req.filename + "|"+str(util.FieldStorage(req)))
        return False    
    return True
    

    
def checkParametros(req, parr):
    form=util.FieldStorage(req)
    if len(form)!=len(parr):
        mylog("Logout|Mal número parámetros|"  + req.filename + "|"+str(parr)+ "|" +str(util.FieldStorage(req)))
        return False  
    for i in parr:
        if form.has_key(i)==False:
            mylog("Logout|Parámetro no valido|"  + req.filename + "|"+str(parr)+ "|" + str(util.FieldStorage(req)))
            return False
    return True
