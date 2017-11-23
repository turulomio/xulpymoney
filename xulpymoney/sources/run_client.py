import datetime
import multiprocessing
import math
import platform
import sys
import subprocess


def concurrent_log(s):
    """EL sistema tiene un log que se guarda en /var/lib/pysgae/pysgae.log
        Tiene entradas (Formato de s)
        Fecha;INIT
        Fecha;comando;ouputcode;took
        Fecha;END
        
        
        Outputcode puede ser OK,ERROR;TIMEOUT;OTROS
    """
    print(s)
        
def call_back(para):
#            log2=log2+para
    counter.next_step()
def mysubprocess_check_output(arr):        
#            try:
        inicio=datetime.datetime.now()
        comand=" ".join(arr)
        s=subprocess.check_output(arr, timeout=30)
        concurrent_log("{};{};{};{}\n".format(datetime.datetime.now(), comand, "OK", datetime.datetime.now()-inicio ))
#            except subprocess.CalledProcessError:
#                concurrent_log("{};{};{};{}\n".format(datetime.datetime.now(), comand, "ERROR", datetime.datetime.now()-inicio ))
#            except subprocess.TimeoutExpired:
#                concurrent_log("{};{};{};{}\n".format(datetime.datetime.now(), comand, "TIMEOUT", datetime.datetime.now()-inicio ))
#            except:
#                print("Error Comorl")
        return s

#######################################3
                
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
#############################################

def call_proc(cmd):
    """ This runs in a separate thread. """
    #subprocess.call(shlex.split(cmd))  # This will block until cmd finishes
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    return out


counter=Counter(len(arr))
#        for l in arr:
#            s=mysubprocess_check_output(l)
#            print(s)
#            log=log+s
#            counter.next_step()




#        lock=multiprocessing.Lock()
counter=Counter(len(arr))
results=[]
pool=multiprocessing.Pool(10)
for p in arr:
    results.append(pool.apply_async(mysubprocess_check_output, [p, ],  callback=call_back))
pool.close()
pool.join()
#        print(log)
print(results[0].get())
counter.message_final()
#        
#        
#        print(call_proc(arr[0]))
#
#        pool = ThreadPool(multiprocessing.cpu_count())
#        results = []
#        for l in arr:
#            results.append(pool.apply_async(call_proc, l))
#
#        # Close the pool and wait for each running task to complete
#        pool.close()
#        pool.join()
#        for result in results:
#            print(result.get())
##            out, err = result.get()
##            print("out: {} err: {}".format(out, err))

