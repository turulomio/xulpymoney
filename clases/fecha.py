# -*- coding: UTF-8  -*-
import time
import datetime

def hoy():
    return time.strftime("%Y-%m-%d")

def ano(fecha):
    return int(fecha[:-6])
    
def anos_entre_fechas(fechaposterior, fechaanterior):
    return float((((fechaposterior-fechaanterior)/3600)/24)/365);

def dia(fecha):
    return int(dia[8:])


def mes(fecha):
    return int(fecha[5:-3])

#def restar_dia(fecha):
#    """
#        Recibe una cadena de testo  y devuelve cadena de texto
#    """
#    structfecha=time.strptime("2000-12-20", "%Y-%m-%d")
#    resta= structfecha-datetime.timedelta(days=1)
#    return resta.strftime("%Y-%m-%d")
#    #~datettime.date(2002, 12, 4).isoformat()

def ultimo_dia_mes(ano,  mes):
    if mes<=11:
        return datetime.date (ano, mes+1, 1)  - datetime.timedelta (days = 1)
    else:
        return datetime.date (ano+1, 1, 1)  - datetime.timedelta (days = 1)
            
            
