## @package libcounter
## This file is from pysgae project
## Do not edit, It will be overriden

import datetime
import math
import platform
from colorama import Style, Fore, init

init(autoreset=True)

# FROM PYSGAE
class Counter:
    def __init__(self, maxsteps):
        self.current=0
        self.max=maxsteps
        self.dt_start=datetime.datetime.now()
        self.dt_end=None
        self.name="Counter"

    def setName(self, name):
        self.name=name
        
    def segundos2fechastring(self, segundos):
        dias=int(segundos/(24*60*60))
        segundosquedan=math.fmod(segundos,24*60*60)
        horas=int(segundosquedan/(60*60))
        segundosquedan=math.fmod(segundosquedan,60*60)
        minutos=int(segundosquedan/60)
        segundosquedan=math.fmod(segundosquedan,60)
        segundos=int(segundosquedan)
        return "{0}d {1}h {2}m {3}s".format(dias,  horas,  minutos, segundos)
        
        
    def seconds_estimated_resting(self):
        """
            Función que devuelve segundos estimados que quedan
        """
        if self.current==0:
            return 0
        resultado=(self.max-self.current)*(datetime.datetime.now()-self.dt_start).total_seconds()/self.current
        return resultado    
        
    def seconds_estimated(self):
        """
            Función que devuelve segundos totales estimados que durará el proceso
        """
        if self.current==0:
            return 0
        resultado=self.max*(datetime.datetime.now()-self.dt_start).total_seconds()/self.current
        return resultado
        
    def seconds_current(self):
        """Tiempo actual"""
        return (datetime.datetime.now()-self.dt_start).total_seconds()
        
    def next_step(self):
        self.current=self.current+1
        if self.current>self.max:
            print ("You need to change counter maximum steps in the constructor to {}".format(self.current))
        self.message_step()
        
    def tpc_completado(self):
        if self.max==0:
            return int(0)
        return int(100*self.current/self.max)

    def message_step(self):
        global parser
        if platform.system()=="Windows":
            tpc_completado=self.tpc_completado()
            segundos_current=self.segundos2fechastring(self.seconds_current())
            segundos_estimados=self.segundos2fechastring(self.seconds_estimated())
        else:
            tpc_completado=Style.BRIGHT+Fore.GREEN + str(self.tpc_completado())+ Style.NORMAL+ Fore.WHITE
            segundos_current=Style.BRIGHT+Fore.GREEN + self.segundos2fechastring(self.seconds_current())+ Style.NORMAL+ Fore.WHITE
            segundos_estimados=Style.BRIGHT+Fore.RED + self.segundos2fechastring(self.seconds_estimated())+ Style.NORMAL+ Fore.WHITE
        print ("{}. Completado {} %. Tiempo transcurrido: {}. Tiempo estimado: {}. ".format(self.name, tpc_completado, segundos_current, segundos_estimados))

    def message_final(self):
        print("El proceso duró {}".format(Style.BRIGHT+Fore.RED+self.segundos2fechastring(self.seconds_current())+ Style.NORMAL+ Fore.WHITE))
