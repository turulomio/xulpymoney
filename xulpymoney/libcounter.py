## @package libcounter
## This file is from xulpymoney project
## Do not edit, It will be overriden

import datetime
import math
import platform
import sys
from colorama import Style, Fore, init

init(autoreset=True)

class Counter:
    def __init__(self, maxsteps):
        self.__current=0
        self.setMaxSteps(maxsteps)
        self.dt_start=datetime.datetime.now()
        self.dt_end=None
        self.setName("Counter")
        self.setSameLine(True)
        
    ## Gets if output must be shown in a line
    ## @return Boolean
    def sameLine(self):
        return self.__sameline
        
    ## Sets if output must be shown in a line
    def setSameLine(self, bool):
        self.__sameline=bool
        
    def maxSteps(self):
        return self.__maxsteps
        
    def setMaxSteps(self, value):
        self.__maxsteps=value

    def name(self):
        return self.__name

    def setName(self, name):
        self.__name=name
        
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
        if self.__current==0:
            return 0
        resultado=(self.maxSteps()-self.__current)*(datetime.datetime.now()-self.dt_start).total_seconds()/self.__current
        return resultado    
        
    def seconds_estimated(self):
        """
            Función que devuelve segundos totales estimados que durará el proceso
        """
        if self.__current==0:
            return 0
        resultado=self.maxSteps()*(datetime.datetime.now()-self.dt_start).total_seconds()/self.__current
        return resultado
        
    def seconds_current(self):
        """Tiempo actual"""
        return (datetime.datetime.now()-self.dt_start).total_seconds()
        
    def next_step(self):
        self.__current=self.__current+1
        if self.__current>self.maxSteps():
            print ("You need to change counter maximum steps in the constructor to {}".format(self.__current))
        self.message_step()
        
    def tpc_completado(self):
        if self.maxSteps()==0:
            return int(0)
        return int(100*self.__current/self.maxSteps())

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
        s="{}. Completado {} %. Tiempo transcurrido: {}. Tiempo estimado: {}. ".format(Fore.YELLOW + self.name()+Fore.RESET, tpc_completado, segundos_current, segundos_estimados)
        if self.sameLine()==True:
            sys.stdout.write("\b"*(len(s)+10))
            sys.stdout.write(s)
            sys.stdout.flush()
        else:
            print(s)

    def message_final(self):
        if self.sameLine()==True:
            sys.stdout.flush()
            print("\n")
        print("El proceso duró {}".format(Style.BRIGHT+Fore.RED+self.segundos2fechastring(self.seconds_current())+ Style.NORMAL+ Fore.WHITE))


if __name__ == "__main__":
    import time
    print (Fore.GREEN + "This is a counter in the same line")
    c=Counter(10)
    c.setName("Counter in the same line")
    for x in range(c.maxSteps()):
        time.sleep(0.3)
        c.next_step()
    c.message_final()
    print()

    print (Fore.GREEN + "This is a normal counter")
    c=Counter(10)
    c.setName("Normal counter")
    c.setSameLine(False)
    for x in range(c.maxSteps()):
        time.sleep(0.3)
        c.next_step()
    c.message_final()
