#!/usr/bin/python3
import datetime
import math
import platform
import sys
import multiprocessing
from subprocess import  check_output,    DEVNULL
from concurrent.futures import ProcessPoolExecutor,  as_completed
from multiprocessing import cpu_count

##################### COPIED CODE ##################3
#FROM PYSGAE
class Color:
    def green(s):
       return "\033[92m{}\033[0m".format(s)
    
    def red(s):
       return "\033[91m{}\033[0m".format(s)
    
    def bold(s):
       return "\033[1m{}\033[0m".format(s)

    def pink(s):
        return "\033[95m{}\033[0m".format(s)
        
    def yellow(s):
        return "\033[93m{}\033[0m".format(s)
        

#FROM PYSGAE
class Counter:
    def __init__(self, maxsteps):
        self.current=0
        self.max=maxsteps
        self.dt_start=datetime.datetime.now()
        self.dt_end=None
        
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
            tpc_completado=Color.green(self.tpc_completado())
            segundos_current=Color.green(self.segundos2fechastring(self.seconds_current()))
            segundos_estimados=Color.red(self.segundos2fechastring(self.seconds_estimated()))
        print ("{}. Completado {} %. Tiempo transcurrido: {}. Tiempo estimado: {}. ".format(sys.argv[0], tpc_completado, segundos_current, segundos_estimados))

    def message_final(self):
        print("El proceso duró {}".format(Color.red(self.segundos2fechastring(self.seconds_current()))))
##################END COPIED CODE###########################
def appendSource(arr):
    counter=Counter(len(arr))
    sourceoutput=b""
    for c in arr:
        try:
            output=check_output(c,  shell=True,  timeout=30, stderr=DEVNULL)
            sourceoutput=sourceoutput+output
            counter.next_step()
        except:
            sourceoutput=sourceoutput+b"ERROR | appendSource\n"
    counter.message_final()
    return sourceoutput

def appendSourceWithConcurrence(arr,  num_workers):
    def call_back(para):
        counter.next_step()
        
    counter=Counter(len(arr))
    sourceoutput=b""
    futures=[]
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        for   a in arr: 
            try:
                future=executor.submit(check_output,  a,  shell=True, stderr=DEVNULL)
                future.add_done_callback(call_back)
                futures.append(future)
            except:
                pass
        
        for  future in as_completed(futures):
            try:
                sourceoutput=sourceoutput+future.result()
            except:
                sourceoutput=sourceoutput+b"ERROR | appendSourceWithConcurrence\n"
    counter.message_final()
    return sourceoutput


arrBolsaMadrid=[]
arrMorningStar=[]
lock=multiprocessing.Lock()
f=open("/tmp/clients.txt", "r")
for line in f.readlines():
    line=line[:-1]
    if line.find("bolsamadrid")!=-1:
        arrBolsaMadrid.append(line)
    if line.find("morningstar")!=-1:
        arrMorningStar.append(line)
f.close()
#arrBolsaMadrid=arrBolsaMadrid[:5]
#arrMorningStar=arrMorningStar[:20]
counter=Counter(len(arrBolsaMadrid)+len(arrMorningStar))
futures=[]
with ProcessPoolExecutor(max_workers=cpu_count()+1) as executor:
        futures.append(executor.submit(appendSource, arrBolsaMadrid))
        futures.append(executor.submit(appendSourceWithConcurrence, arrMorningStar, 10))

finaloutput=b""

for f in as_completed(futures):
    finaloutput=finaloutput+f.result()
    
f=open("/tmp/clients_result.txt", "w")
f.write(finaloutput.decode("UTF-8"))
f.close()

