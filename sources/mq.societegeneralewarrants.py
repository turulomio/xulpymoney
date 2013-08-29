#!/usr/bin/python3
import sys
sys.path.append("/usr/lib/mystocks")
from libmystocks import *
from config import *
"""Este script saca información de la pagina productoscotizados.com"""

class WorkerSGWarrants(Source):
    """Clase que recorre las inversiones activas y calcula según este la prioridad de la previsión"""
    def __init__(self, cfg):
        Source.__init__(self, cfg)
        self.cfg=cfg
        self.id_source=6
        self.ids=[]
        self.name="SGWARRANTS"
        
    def start(self):
        print (self.name)
        while (True):
            con=self.cfg.connect_mystocksd()
            cur = con.cursor()     
            self.ids=self.find_ids()

            self.ids=self.filtrar_horario_bolsa(self.ids)

            (p, e)=self.execute()
            p=self.parse_resultado(p)
            if self.cfg.debug==True:
                self.print_parsed(p)
            else:
                Quotes(self.cfg).insert(cur, p, self.name)
            con.commit()
            cur.close()
            self.cfg.disconnect_mystocksd(con)
            time.sleep(120)

    def parse_resultado(self, resultado):
        """Función que saca el id y los compara con los filtrados, es decir con los activos¡"""
        parsed=[]
        for d in resultado:
            if d['id'] in self.ids:
                parsed.append(d)
        return parsed
        
    def productid2id(self, productid):
        """Product id debe ser un entero"""
        if productid==8050:#u0024
            return 74742
        elif productid==6425:#u0017
            return  81678
        elif productid==6426:#u0018
            return  74741
        elif productid==7876:#u0021
            return 74745
        elif productid==8049:#u0023
            return 81677

        return None
    
    def execute(self):
        (resultado, error)=([], [])
        
        web=self.download('http://www.productoscotizados.com/es/Bonus.aspx', 'PRODUCTOSCOTIZADOS_QUOTES')
        if web==None:
            return (resultado, error)   
            
        bloques=web.read().split(b"Producto.aspx?ProductId=")
        for i in range(1, len(bloques)):
            d={}
            productid=int(bloques[i].split(b'">')[0])
            d["id"]=self.productid2id(productid)
            d["quote"]=float(comaporpunto(bloques[i].split(b'type="Bid" manageColor="true">')[1].split(b"</")[0]))
            d['datetime']=datetime.datetime.now(pytz.timezone('Europe/Madrid'))
            if d["id"]!=None:
                resultado.append(d)
        return (resultado,  error)


if __name__ == '__main__':
    cfg=ConfigMQ()
    if len(sys.argv)>1:
        if "debug" in sys.argv:
            log("STARTING", "","Debugging")
            cfg.debug=True
            
        if "temp.xls" in sys.argv:
            log ("File detected")
        else:
            log ("File must be temp.xls")
            sys.exit(0)

    con=cfg.connect_mystocksd()
    cur = con.cursor()
    cfg.carga_ia(cur, "where priority[1]=6")

    cfg.carga_bolsas(cur)
    cur.close()
    cfg.disconnect_mystocksd(con)

    w=WorkerSGWarrants(cfg)
    w.start()
