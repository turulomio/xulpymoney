#!/usr/bin/python3
import sys
sys.path.append("/usr/lib/myquotes")
from libmyquotes import *
from config import *
"""Este script saca información de la pagina productoscotizados.com"""


class WorkerYahooHistorical(Source):
    """Clase que recorre las inversiones activas y busca la última  que tiene el microsecond 4. Busca en internet los historicals a partir de esa fecha"""
    def __init__(self, cfg):
        Source.__init__(self, cfg)
        self.cfg=cfg
        self.id_source=3
        self.ids=[]
        self.name="YAHOOHISTORICAL"

    def start(self):
        print(self.name)
        while (True):
            time.sleep(5)#time before            
            self.ids=self.find_ids_historical()
            log (self.name, "FILTROS",  "Han pasado los filtros {0} inversiones".format(len(self.ids)))
            for inv in self.ids:
                con=self.cfg.connect_myquotesd()
                cur = con.cursor()     
                cur.execute("select max(datetime)::date as date from quotes where date_part('microsecond',datetime)=4 and id=%s order by date", (inv.id, ))
                inicio=cur.fetchone()[0]

                if inicio==None:
                    inicio=datetime.date(config.fillfromyear, 1, 1)

                (set, errors)=self.execute(cur, inv, inicio, datetime.date.today())

                set.save(cur,self.name)

                con.commit()
                cur.close()                
                self.cfg.disconnect_myquotesd(con)
                time.sleep(30)#time step
            time.sleep(60*60*24) #time after
        
    def execute(self, cur,  investment, inicio, fin):
        """inico y fin son dos dates entre los que conseguir los datos."""
        url='http://ichart.finance.yahoo.com/table.csv?s='+investment.yahoo+'&a='+str(inicio.month-1)+'&b='+str(inicio.day)+'&c='+str(inicio.year)+'&d='+str(fin.month-1)+'&e='+str(fin.day)+'&f='+str(fin.year)+'&g=d&ignore=.csv'
        (set, error)=(QuotesSet(), [])
        web=self.download(url, 'YAHOO_HISTORICAL')
        if web==None:
            return (set, error)
        web.readline()
        for i in web.readlines(): 
#            try:  
                i=b2s(i)
                datos=i.split(",")
                fecha=datos[0].split("-")
                date=datetime.date(int(fecha[0]), int(fecha[1]),  int(fecha[2]))
		#Calcula el datetime del low y del high, min y maxdatetime respectivamente
                iniciodia=dt(date,datetime.time(0,0),investment.bolsa.zone)
                findia=dt(date,datetime.time(23,59,59), investment.bolsa.zone)
                cur.execute("select datetime,quote from quotes where id=%s and datetime>=%s and datetime<=%s order by datetime",(investment.id,iniciodia,findia))
                if cur.rowcount>0:
                    maxquote=0
                    maxdatetime=None
                    minquote=1000000
                    mindatetime=None
                    for q in cur:
                        if q['quote']>=maxquote:
                            maxquote=q['quote']
                            maxdatetime=q['datetime']
                        if q['quote']<=minquote:
                            minquote=q['quote']
                            mindatetime=q['datetime']
                else:
                    maxdatetime=dt(date,investment.bolsa.close,investment.bolsa.zone)-datetime.timedelta(seconds=1)
                    mindatetime=dt(date,investment.bolsa.starts,investment.bolsa.zone)+datetime.timedelta(seconds=1)

                set.append(Quote().init__create(investment,dt(date,investment.bolsa.close,investment.bolsa.zone), float(datos[4])))#close
                set.append(Quote().init__create(investment,mindatetime, float(datos[3])))#low
                set.append(Quote().init__create(investment,maxdatetime, float(datos[2])))#high
                set.append(Quote().init__create(investment,dt(date,investment.bolsa.starts,investment.bolsa.zone), float(datos[1])))#open
        if inicio==datetime.date(config.fillfromyear, 1, 1) and len(set.arr)<10:
            print ("No hay YAHOO HISTORICALS DE:",  id, inicio, fin, url)
        return (set,  error)


if __name__ == '__main__':
    cfg=ConfigMQ()
    if len(sys.argv)>1:
        if sys.argv[1]=="debug":
            log("STARTING", "","Debugging")
            cfg.debug=True

    con=cfg.connect_myquotesd()
    cur = con.cursor()
    cfg.actualizar_memoria(cur)
    cfg.carga_ia(cur, "where priority[1]=1")
    cur.close()
    cfg.disconnect_myquotesd(con)

    w=WorkerYahooHistorical(cfg)
    w.start()
