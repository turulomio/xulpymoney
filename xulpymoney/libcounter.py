## @namespace xulpymoney.libcounter
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
        self.__maxsteps=maxsteps
        self.__start=datetime.datetime.now()
        self.__end=None
        self.setName("Counter")
        self.setSameLine(True)

    ## Gets start datetime. This parameter is set in Constructor
    ## @returns datetime
    def start(self):
        return self.__start
        
    ## Gets the end time of the counter. It's set when final message function is invoked
    ## return datetime or None.  If counter is working this value returns None
    def end(self):
        return self.__end
        
    ## Gets the number of max steps of the counter
    ## @return integer
    def maxSteps(self):
        return self.__maxsteps
    ## Sets if output must be shown in a line
    def setSameLine(self, bool):
        self.__sameline=bool

    def name(self):
        return self.__name

    def setName(self, name):
        self.__name=name
        
    ## Converts a number of seconds into a pretty string
    ## @param seconds Integer with the number of seconds
    ## @return string
    @staticmethod
    def seconds2pretty(segundos):
        dias=int(segundos/(24*60*60))
        segundosquedan=math.fmod(segundos,24*60*60)
        horas=int(segundosquedan/(60*60))
        segundosquedan=math.fmod(segundosquedan,60*60)
        minutos=int(segundosquedan/60)
        segundosquedan=math.fmod(segundosquedan,60)
        segundos=int(segundosquedan)
        return "{0}d {1}h {2}m {3}s".format(dias,  horas,  minutos, segundos)
        
    ## Function that returns the number of seconds remaining to end Counter
    def seconds_estimated_resting(self):
        """
            Función que devuelve segundos estimados que quedan
        """
        if self.__current==0:
            return 0
        resultado=(self.maxSteps()-self.__current)*(datetime.datetime.now()-self.start()).total_seconds()/self.__current
        return resultado    
        
    ## Function that returns the number of seconds the counter will last
    def seconds_estimated(self):
        if self.__current==0:
            return 0
        resultado=self.maxSteps()*(datetime.datetime.now()-self.start()).total_seconds()/self.__current
        return resultado
        
    ## Function that returns the number of seconds elapsed
    def seconds_currrent(self):
        """Tiempo actual"""
        return (datetime.datetime.now()-self.start()).total_seconds()
        
    def next_step(self):
        self.__current=self.__current+1
        if self.__current>self.maxSteps():
            print()
            print (Style.BRIGHT+Fore.RED+ "You need to change counter maximum steps in the Counter constructor to {}".format(self.__current))
        elif self.__current==self.maxSteps():
            self.__message_final()
        else:
            self.__message_step()
        
    def tpc_completado(self):
        if self.maxSteps()==0:
            return int(0)
        return int(100*self.__current/self.maxSteps())

    def __message_step(self):
        global parser
        if platform.system()=="Windows":
            tpc_completado=self.tpc_completado()
            segundos_current=Counter.seconds2pretty(self.seconds_currrent())
            segundos_estimados=Counter.seconds2pretty(self.seconds_estimated())
        else:
            tpc_completado=Style.BRIGHT+Fore.GREEN + str(self.tpc_completado())+ Style.NORMAL+ Fore.WHITE
            segundos_current=Style.BRIGHT+Fore.GREEN + Counter.seconds2pretty(self.seconds_currrent())+ Style.NORMAL+ Fore.WHITE
            segundos_estimados=Style.BRIGHT+Fore.RED + Counter.seconds2pretty(self.seconds_estimated())+ Style.NORMAL+ Fore.WHITE
        s="{}. Completado {} %. Tiempo transcurrido: {}. Tiempo estimado: {}. ".format(Fore.YELLOW + self.name()+Fore.RESET, tpc_completado, segundos_current, segundos_estimados)
        if self.__sameline==True:
            sys.stdout.write("\b"*(len(s)+10))
            sys.stdout.write(s)
            sys.stdout.flush()
        else:
            print(s)

    def __message_final(self):
        if self.__sameline==True:
            sys.stdout.flush()
            print("\n")
        self.__end=datetime.datetime.now()
        print("El proceso duró {}".format(Style.BRIGHT+Fore.RED+Counter.seconds2pretty(self.seconds_currrent())+ Style.NORMAL+ Fore.WHITE))


if __name__ == "__main__":
    import time
    print (Fore.GREEN + "This is a counter in the same line")
    example=Counter(10)
    example.setName("Counter in the same line")
    for x in range(example.maxSteps()):
        time.sleep(0.1)
        example.next_step()
        
    print()
    print (Fore.GREEN + "This is a normal counter")
    example=Counter(10)
    example.setName("Normal counter")
    example.setSameLine(False)
    for x in range(example.maxSteps()):
        time.sleep(0.1)
        example.next_step()
        
    print()
    print (Fore.GREEN + "This is a counter with bad max steps")
    example=Counter(9)
    example.setName("Counter in the same line")
    for x in range(10):
        time.sleep(0.1)
        example.next_step()
    print()
