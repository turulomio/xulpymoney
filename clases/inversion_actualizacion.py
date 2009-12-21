# -*- coding: UTF-8  -*-
import urllib,  re
def actualizar(inversion):
    if inversion=="ACS":
        return bolsamadrid(inversion)
    else if:
        return 0
        

def comaporpunto(cadena):
    return cadena.replace(',','.')
    
def bolsamadrid(inversion):
    web=urllib.urlopen('http://www.bolsamadrid.es/esp/mercados/acciones/accind1_1.htm')
    lineainv=""
    for line in web.readlines():    
        if line.find(inversion) != -1:
            lineainv= line
            break;
    lineainv=lineainv.split('</A></TD><TD>')[1]
    return float(comaporpunto(lineainv.split('</TD>')[0]))

