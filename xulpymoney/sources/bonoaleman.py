# -*- coding: UTF-8  -*-
import multiprocessing,  gettext
from libmyquotes import *

class WorkerBonoAleman(Source):
    def __init__(self,  cfg):
        Source.__init__(self, cfg)
        self.name="BONOALEMAN"
        self.id_source=4
        
    def start(self):
        print (self.name)
        while (True):
            (parsed, errors)=self.execute()
            con=self.cfg.connect_myquotesd()
            cur = con.cursor()
            self.parse_errors(cur,  errors)
            Quote(self.cfg).insert(cur, parsed, self.name)
            con.commit()
            cur.close()                
            self.cfg.disconnect_myquotesd(con)
            time.sleep(60)


    def execute(self):    
        resultado=[]
        errors=[]

        web=self.download('http://jcbcarc.dyndns.org/Defcon.php', 'ARR_QUOTES')
        if web==None:
            return (resultado,errors)          

        try:
            page=web.read()
            btime=page.split(b")<br>")[0].split(b'ltima actualizaci')[1]     
            time=datetime.datetime.strptime(b2s(btime, 'ISO-8859-1')[3:], "%H:%M").time()
            dat=dt(datetime.date.today(),time,'Europe/Madrid')
            #DIF ALEMAN
            a= {'id':74801, 'datetime': dat,'quote': None }
            a['quote']=float(comaporpunto(page.split(b'n a 10 a')[1].split(b"%")[0][5:]))
            if self.cfg.activas['74801'].active==True:
                resultado.append(a)
            #DIF ESPAÑOL
            e= {'id':  74803, 'datetime': dat,'quote': None }
            e['quote']=float(comaporpunto(page.split(b'ol a 10 a')[1].split(b"%")[0][5:]))
            if self.cfg.activas['74803'].active==True:
                resultado.append(e)

            #BUND_DIFERENCIALESPAÑOL
            d= {'id': 74804, 'datetime': dat,'quote': (e['quote']-a['quote'])*100 }
            if self.cfg.activas['74804'].active==True:
                resultado.append(d)
        except:
            log(self.name,"ARR_QUOTES", gettext.gettext("Error parseando"))

        return (resultado,errors)
