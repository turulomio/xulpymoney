#!/usr/bin/python3
import sys
sys.path.append("/usr/lib/xulpymoney")
from libxulpymoney import *
"""Este script saca información de la pagina productoscotizados.com"""


class WorkerYahooHistorical(Source):
    """Clase que recorre las inversiones activas y busca la última  que tiene el microsecond 4. Busca en internet los historicals a partir de esa fecha"""
    def __init__(self, cfg):
        Source.__init__(self, cfg)
        self.cfg=cfg
        self.id_source=3
        self.ids=[]
        self.name="YAHOOHISTORICAL"
        self.investments=SetInvestments(self.cfg)
        self.investments.load_from_db("select * from investments where active=true and priorityhistorical[1]=3")
        
    def start(self):
        log (self.name, "FILTROS",  "Se van a actualizar {0} inversiones".format(len(self.investments.arr)))
        for i,  inv in enumerate(self.investments.arr):
            sys.stdout.write("\b"*1000+"mq.yahoohistorical {0}/{1} {2}: ".format(i, len(self.investments.arr), inv) )
            sys.stdout.flush()
            ultima=inv.fecha_ultima_actualizacion_historica()
            if ultima==datetime.date.today()-datetime.timedelta(days=1):
                continue
            print (inv, ultima)
            (set, errors)=self.execute(inv, inv.fecha_ultima_actualizacion_historica()+datetime.timedelta(days=1), datetime.date.today())
            set.save(self.name)
            self.cfg.conms.commit()  
            time.sleep(10)#time step
        
    def execute(self,  investment, inicio, fin):
        """inico y fin son dos dates entre los que conseguir los datos."""
        url='http://ichart.finance.yahoo.com/table.csv?s='+investment.yahoo+'&a='+str(inicio.month-1)+'&b='+str(inicio.day)+'&c='+str(inicio.year)+'&d='+str(fin.month-1)+'&e='+str(fin.day)+'&f='+str(fin.year)+'&g=d&ignore=.csv'
        (set, error)=(QuotesSet(self.cfg), [])
        web=self.download(url, 'YAHOO_HISTORICAL')
        if web==None:
            return (set, error)
        web.readline()
        for i in web.readlines(): 
                i=b2s(i)
                datos=i.split(",")
                fecha=datos[0].split("-")
                date=datetime.date(int(fecha[0]), int(fecha[1]),  int(fecha[2]))
                
                datestart=dt(date,investment.bolsa.starts,investment.bolsa.zone)
                dateends=dt(date,investment.bolsa.closes,investment.bolsa.zone)
                datetimefirst=datestart-datetime.timedelta(seconds=1)+datetime.timedelta(microseconds=1)
                datetimelow=(datestart+(dateends-datestart)*1/3).replace(microsecond=2)
                datetimehigh=(datestart+(dateends-datestart)*2/3).replace(microsecond=3)
                datetimelast=dateends+datetime.timedelta(microseconds=4)

                set.append(Quote(self.cfg).init__create(investment,datetimelast, float(datos[4])))#closes
                set.append(Quote(self.cfg).init__create(investment,datetimelow, float(datos[3])))#low
                set.append(Quote(self.cfg).init__create(investment,datetimehigh, float(datos[2])))#high
                set.append(Quote(self.cfg).init__create(investment, datetimefirst, float(datos[1])))#open
        return (set,  error)

if __name__ == '__main__':
    cfg=ConfigMyStock()
    if len(sys.argv)>2:
        if sys.argv[2]=="debug":
            log("STARTING", "","Debugging")
            cfg.debug=True

    cfg.connect_myquotesd(sys.argv[1])
    cfg.actualizar_memoria()

    w=WorkerYahooHistorical(cfg)
    w.start()

    cfg.disconnect_myquotesd()
