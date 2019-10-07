import argparse
import multiprocessing
from subprocess import  check_output,    DEVNULL
from concurrent.futures import ProcessPoolExecutor,  as_completed
from multiprocessing import cpu_count

from xulpymoney.casts import  b2s
from xulpymoney.libcounter import Counter
from xulpymoney.mem import MemRunClient

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
    return commands, sourceoutput
    ###################################################################

def main():
    mem=MemRunClient()
    parser=argparse.ArgumentParser("xulpymoney_sync_quotes")
    mem.addCommonToArgParse(parser)
    parser.add_argument('--filename', help='Filename',action="store", metavar="X", default=None)
    args=parser.parse_args()
    mem.addDebugSystem(args.debug)

    arrBolsaMadrid=[]
    arrMorningStar=[]
    arrQueFondos=[]
    arrGoogle=[]
    arrYahoo=[]
    arrInfobolsa=[]
    global lock
    lock=multiprocessing.Lock()
    if args.filename==None:
        filename="{}/clients.txt".format(mem.dir_tmp)
        output="{}/clients_result.txt".format(mem.dir_tmp)
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
        if line.find("infobolsa")!=-1:
            arrYahoo.append(line)
    f.close()

    futures=[]
    with ProcessPoolExecutor(max_workers=cpu_count()+1) as executor:
            futures.append(executor.submit(appendSource, arrBolsaMadrid, "xulpymoney_bolsamadrid_client"))
            futures.append(executor.submit(appendSourceWithConcurrence, arrMorningStar, "xulpymoney_morningstar_client", cpu_count()+1))
            futures.append(executor.submit(appendSourceWithConcurrence, arrQueFondos, "xulpymoney_quefondos_client", cpu_count()+1))
            futures.append(executor.submit(appendSourceWithConcurrence, arrGoogle, "xulpymoney_google_client",cpu_count()+1))
            futures.append(executor.submit(appendSourceWithConcurrence, arrYahoo, "xulpymoney_yahoo_client", cpu_count()+1))
            futures.append(executor.submit(appendSourceWithConcurrence, arrInfobolsa, "xulpymoney_infobolsa_client", cpu_count()+1))

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

