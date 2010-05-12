# -*- coding: UTF-8  -*-
import urllib

def comaporpunto(cadena):
    return cadena.replace(',','.')
    
def bolsamadrid(arr):
    web=urllib.urlopen('http://www.bolsamadrid.es/esp/mercados/acciones/accmerc2_c.htm')
    lineainv=""
    for i in range(30):
        web.readline()
    for line in web.readlines():    
        if line.find("fichavalor.asp") != -1:
            nombre=line.split("BORDER=0> ")[1].split("</A>")[0]
            valor=float(comaporpunto(line.split("</A></TD><TD>")[1].split("</TD>")[0]))
            arr.append((nombre, valor))
    return arr
    
def getvalor(arr, valor):
    for i in arr:
        if i[0]==valor:
            return i[1]
    return 0
