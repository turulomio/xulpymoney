# -*- coding: UTF-8 -*-
import string

def dosdecimales(num):
    return float("%.2f" % num)
    
def euros(num,  numdec=2):
    if numdec==2:
        return "%.2f €" %num
    elif numdec==3:
        return "%.3f €" %num

def svg2string(file):
    f=open(file, "r")
    f.readline()
    f.readline()
    f.readline()
    f.readline()
    s='<svg flex="1" style="width:100%; height:100%;" viewBox="0 0 1280 1024"\n'+f.read()
    f.close()
    return s
    
def tpc(num):
    str="%.2f " %num
    return str+"%"
def xul2utf8(cadena):
    cadena=string.replace(cadena,'&amp;','&')
    return cadena
    
def utf82xul(cadena):
    cadena=string.replace(cadena,'&','&amp;')
    return cadena
