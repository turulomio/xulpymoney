#!/usr/bin/python3
import argparse
import datetime
import math
import platform
import multiprocessing
from subprocess import  check_output,    DEVNULL
from concurrent.futures import ProcessPoolExecutor,  as_completed
from multiprocessing import cpu_count
from os import path,  makedirs

# #################### COPIED CODE ##################3
# FROM PYSGAE
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
            tpc_completado=Color.green(self.tpc_completado())
            segundos_current=Color.green(self.segundos2fechastring(self.seconds_current()))
            segundos_estimados=Color.red(self.segundos2fechastring(self.seconds_estimated()))
        print ("{}. Completado {} %. Tiempo transcurrido: {}. Tiempo estimado: {}. ".format(self.name, tpc_completado, segundos_current, segundos_estimados))

    def message_final(self):
        print("El proceso duró {}".format(Color.red(self.segundos2fechastring(self.seconds_current()))))
        
        
# FROM XULPYMONEY.LIBXULPYMONEY
def b2s(b, code='UTF-8'):
    """Bytes 2 string"""
    return b.decode(code)
    

# FROM XULPYMONEY.LIBXULPYMONEY
def dirs_create():
    """
        Returns xulpymoney_tmp_dir, ...
    """
    dir_tmp=path.expanduser("~/.xulpymoney/tmp/")
    try:
        makedirs(dir_tmp)
    except:
        pass
    return dir_tmp
    
##################END COPIED CODE###########################




def appendSource(arr, name):
    counter=Counter(len(arr))
    counter.setName(name)
    sourceoutput=[]
    commands=[]
    for c in arr:
        try:
            output=check_output(c,  shell=True,  timeout=30, stderr=DEVNULL)
            commands.append(c)
            sourceoutput.append(output)
            counter.next_step()
        except:
            sourceoutput.append(b"ERROR | appendSource\n")
    counter.message_final()
    return commands, sourceoutput

def appendSourceWithConcurrence(arr, name,  num_workers):
    def call_back(para):
        counter.next_step()
        
    counter=Counter(len(arr))
    counter.setName(name)
    sourceoutput=[]
    commands=[]
    futures=[]
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        for   a in arr: 
            try:
                future=executor.submit(check_output,  a,  timeout=30,  shell=True, stderr=DEVNULL)
                future.add_done_callback(call_back)
                futures.append([a, future])
            except:
                pass
        
        as_completed([f[1] for f in futures])#Extrae lista de futures
        for command,  future in futures:
            commands.append(command)
            try:
                sourceoutput.append(future.result())
            except:
                sourceoutput.append(b"ERROR | appendSourceWithConcurrence\n")
    counter.message_final()
    return commands, sourceoutput
    ###################################################################
parser=argparse.ArgumentParser("xulpymoney_sync_quotes")
parser.add_argument('--filename', help='Filename',action="store", metavar="X", default=None)
args=parser.parse_args()

dir_tmp=dirs_create()
arrBolsaMadrid=[]
arrMorningStar=[]
arrQueFondos=[]
arrGoogle=[]
arrYahoo=[]
lock=multiprocessing.Lock()
if args.filename==None:
    filename="{}/clients.txt".format(dir_tmp)
    output="{}/clients_result.txt".format(dir_tmp)
else:
    filename=args.filename
    output= "{}.clients_result.txt".format(filename)
f=open(filename, "r")
for line in f.readlines():
    line=line[:-1]
    if line.find("bolsamadrid")!=-1:
        arrBolsaMadrid.append(line)
    if line.find("morningstar")!=-1:
        arrMorningStar.append(line)
    if line.find("quefondos")!=-1:
        arrQueFondos.append(line)
    if line.find("google")!=-1:
        arrGoogle.append(line)
    if line.find("yahoo")!=-1:
        arrYahoo.append(line)
f.close()

futures=[]
with ProcessPoolExecutor(max_workers=cpu_count()+1) as executor:
        futures.append(executor.submit(appendSource, arrBolsaMadrid, "xulpymoney_bolsamadrid_client"))
        futures.append(executor.submit(appendSourceWithConcurrence, arrMorningStar, "xulpymoney_morningstar_client", cpu_count()+1))
        futures.append(executor.submit(appendSourceWithConcurrence, arrQueFondos, "xulpymoney_quefondos_client", cpu_count()+1))
        futures.append(executor.submit(appendSourceWithConcurrence, arrGoogle, "xulpymoney_google_client",cpu_count()+1))
        futures.append(executor.submit(appendSourceWithConcurrence, arrYahoo, "xulpymoney_yahoo_client", cpu_count()+1))

f=open(output, "w")
for fut in as_completed(futures):
    commands, out=fut.result()
    for i, c in enumerate(commands):
        f.write("{}\n".format(commands[i]))
        for o in b2s(out[i]).split("\n"):
            if o=="":
                f.write("\n")
            else:
                f.write("  + {}\n".format(o))
f.close()

