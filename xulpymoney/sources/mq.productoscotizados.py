#!/usr/bin/python3
import sys
sys.path.append("/usr/lib/mystocks")
from libmystocks import *
from config import *
"""Este script saca información de la pagina productoscotizados.com"""

class WorkerProductosCotizados(Source):
    """Clase que recorre las inversiones activas y calcula según este la prioridad de la previsión"""
    def __init__(self, cfg):
        Source.__init__(self, cfg)
        self.cfg=cfg
        self.id_source=5
        self.ids=[]
        self.name="PRODUCTOSCOTIZADOS"
        
    def start(self):
        print (self.name)
        while (True):
            con=self.cfg.connect_mystocksd()
            cur = con.cursor()     
            self.ids=self.find_ids()
            self.ids=self.filtrar_horario_bolsa(self.ids)

            (set, e)=self.execute()
            self.parse_resultado(set)
            if self.cfg.debug==True:
                self.print_parsed(p)
            else:
                set.save(cur, self.name)
            con.commit()
            cur.close()
            self.cfg.disconnect_mystocksd(con)
            time.sleep(120)

    def parse_resultado(self, set):
        """Función que saca el id y los compara con los filtrados, es decir con los activos¡"""
        resultado=[]
        for d in set.arr:
            if d.investment in self.ids:
                resultado.append(d)
        set.arr=resultado
        
    def productid2investment(self, productid):
        """Product id debe ser un entero"""
        if productid==8050:#u0024
            return self.cfg.activas( 74742)
        elif productid==6425:#u0017
            return self.cfg.activas(  81678)
        elif productid==6426:#u0018
            return self.cfg.activas(  74741)
        elif productid==7876:#u0021
            return self.cfg.activas( 74745)
        elif productid==8049:#u0023
            return self.cfg.activas( 81677)
        elif productid==6424:#u0016
            return self.cfg.activas( 81679)
        return None

    def execute(self):
        (set, error)=(SetQuotes(), [])
        
        web=self.download('http://www.productoscotizados.com/es/Bonus.aspx', 'PRODUCTOSCOTIZADOS_QUOTES')
        if web==None:
            return (set, error)   
            
        bloques=web.read().split(b"Producto.aspx?ProductId=")
        for i in range(1, len(bloques)):
            quote=Quote()
            productid=int(bloques[i].split(b'">')[0])
            quote.investment=self.productid2investment(productid)
            quote.quote=float(comaporpunto(bloques[i].split(b'type="Bid" manageColor="true">')[1].split(b"</")[0]))
            quote.datetime=datetime.datetime.now(pytz.timezone('Europe/Madrid'))
            if quote.investment!=None:
                set.append(quote)
        return (set,  error)


if __name__ == '__main__':
    cfg=ConfigMQ()
    if len(sys.argv)>1:
        if sys.argv[1]=="debug":
            log("STARTING", "","Debugging")
            cfg.debug=True

    con=cfg.connect_mystocksd()
    cur = con.cursor()
    cfg.actualizar_memoria(cur)
    cfg.carga_ia(cur, "where priority[1]=5")
    cur.close()
    cfg.disconnect_mystocksd(con)

    w=WorkerProductosCotizados(cfg)
    w.start()
