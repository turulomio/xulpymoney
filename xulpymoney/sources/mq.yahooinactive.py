#!/usr/bin/python3
import sys
sys.path.append("/usr/lib/mystocks")
#from config import *
from libmystocks import *
from yahoo import *
import math
class WorkerYahooInactive(WorkerYahoo):
    """Clase que recorre las inversiones activas y calcula según este la prioridad de la previsión"""
    def __init__(self, mem):
        Source.__init__(self, mem)
        self.mem=mem
        self.id_source=1
        self.ids=[]
        self.name="YAHOOINACTIVE"
        
    def start(self):
        print (self.name)
        while (True):
            con=self.mem.connect_xulpymoneyd()
            cur = con.cursor()     
            self.ids=self.filtrar_ids_inactivos_no_actualizados(cur,  1, 7,  False)      
            print (self.ids)
            (p, e)=(newSetQuotes(), [])
            for a in arr_split(self.ids, math.ceil(float(len(self.ids))/180)):
                (parsed, errors)=self.execute(a)
                p.arr=p.arr+parsed.arr
                e=e+errors
                time.sleep(3)
#            self.parse_errors(cur,  e)
#            Quotes(self.mem).insert(cur, p, self.name)
            p.save(cur,self.name)
            con.commit()
            cur.close()                
            self.mem.disconnect_xulpymoneyd(con)
            time.sleep(60*60*24)


if __name__ == '__main__':
    mem=ConfigMQ()
    if len(sys.argv)>1:
        if sys.argv[1]=="debug":
            log("STARTING", "","Debugging")
            mem.debug=True

    con=mem.connect_xulpymoneyd()
    cur = con.cursor()
    mem.actualizar_memoria(cur)
#    mem.carga_ia(cur, "where priority[1]=1")
#    print(mem.activas())
    cur.close()
    mem.disconnect_xulpymoneyd(con)

    w=WorkerYahooInactive(mem)
    w.start()

