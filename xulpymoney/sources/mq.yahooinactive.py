#!/usr/bin/python3
import sys
sys.path.append("/usr/lib/myquotes")
#from config import *
from libmyquotes import *
from yahoo import *
import math
class WorkerYahooInactive(WorkerYahoo):
    """Clase que recorre las inversiones activas y calcula según este la prioridad de la previsión"""
    def __init__(self, cfg):
        Source.__init__(self, cfg)
        self.cfg=cfg
        self.id_source=1
        self.ids=[]
        self.name="YAHOOINACTIVE"
        
    def start(self):
        print (self.name)
        while (True):
            con=self.cfg.connect_myquotesd()
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
#            Quotes(self.cfg).insert(cur, p, self.name)
            p.save(cur,self.name)
            con.commit()
            cur.close()                
            self.cfg.disconnect_myquotesd(con)
            time.sleep(60*60*24)


if __name__ == '__main__':
    cfg=ConfigMQ()
    if len(sys.argv)>1:
        if sys.argv[1]=="debug":
            log("STARTING", "","Debugging")
            cfg.debug=True

    con=cfg.connect_myquotesd()
    cur = con.cursor()
    cfg.actualizar_memoria(cur)
#    cfg.carga_ia(cur, "where priority[1]=1")
#    print(cfg.activas())
    cur.close()
    cfg.disconnect_myquotesd(con)

    w=WorkerYahooInactive(cfg)
    w.start()

