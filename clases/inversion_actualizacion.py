# -*- coding: UTF-8  -*-
import urllib

def comaporpunto(cadena):
    cadena=cadena.replace('.','')#Quita puntos
    cadena=cadena.replace(',','.')#Cambia coma por punto
    return cadena

def bankintergestion(arr):
    try:
        web=urllib.urlopen('http://www.bolsamadrid.es/esp/mercados/fondos/htmfondos/0055alfa.htm')
    except:
        return arr
    lineainv=""
    for i in range(30):
        web.readline()
    for line in web.readlines():    
        if line.find("fonficha") != -1:
            nombre=line.split(')">')[1].split("</a></TD>")[0]
            valor=float(comaporpunto(line.split("</TD><TD>")[1]))
            arr.append((nombre, valor))
    return arr

def bolsamadrid(arr):
    try:
        web=urllib.urlopen('http://www.bolsamadrid.es/esp/mercados/acciones/accmerc2_c.htm')
    except:
        return arr
    lineainv=""
    for i in range(30):
        web.readline()
    for line in web.readlines():    
        if line.find("fichavalor.asp") != -1:
            nombre=line.split("BORDER=0> ")[1].split("</A>")[0]
            valor=float(comaporpunto(line.split("</A></TD><TD>")[1].split("</TD>")[0]))
            arr.append((nombre, valor))
    return arr

def carmignacpatrimoinea(arr):
    try:
        web=urllib.urlopen('http://www.carmignac.es/es/carmignac-patrimoine-part-a.htm')
    except:
        return arr
    lineainv=""
    for line in web.readlines():
        if line.find('<?xml version="1.0" encoding="utf-8"?><p class="dr"><span>') != -1:
            nombre="CARMIGNAC PATRIMOINE A"
            valor=float(line.split("<span>")[1].split(" ")[0])
            arr.append((nombre, valor))
    return arr

def LyxorETFXBearEUROSTOXX50(arr):
    try:
        web=urllib.urlopen('http://www.boerse-frankfurt.de/EN/index.aspx?pageID=105&ISIN=FR0010424143')
    except:
        return arr
    lineainv=""
    for line in web.readlines():
        if line.find('Last Price') != -1:
            nombre="LyxorETFXBearEUROSTOXX50"
            valor=float(line.split("<span><b>")[2].split("</b>")[0])
            arr.append((nombre, valor))
    return arr


def getvalor(arr, valor):
    for i in arr:
        if i[0]==valor:
            return i[1]
    return 0
