# -*- coding: UTF-8 -*-
import string

def dosdecimales(num):
    return float("%.2f" % num)
    
def euros(num,  numdec=2):
    if numdec==2:
        return "%.2f €" %num
    elif numdec==3:
        return "%.3f €" %num
    
def tpc(num):
    str="%.2f " %num
    return str+"%"
def xul2utf8(cadena):
    cadena=string.replace(cadena,'&amp;','&')
    return cadena
    
def utf82xul(cadena):
    cadena=string.replace(cadena,'&','&amp;')
    return cadena
