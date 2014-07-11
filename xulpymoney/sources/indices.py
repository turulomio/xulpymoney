# -*- coding: UTF-8  -*-
import gettext
from decimal import Decimal
from libmystocks import *

class WorkerIndices(Source):
    def __init__(self,  mem):
        Source.__init__(self, mem)
        self.mem=mem
        self.id_source=4
        self.ids=[]
        self.name="INDICES"

    def start(self):
        print (self.name)
        while (True):
            con=self.mem.connect_xulpymoneyd()
            cur = con.cursor()
            self.ids=self.filtrar_horario_bolsa(self.find_ids())
            (set, errors)=self.execute()
            self.parse_resultado(set)
#            self.parse_errors(cur,  e)
            set.save(cur,self.name)
#            Quote(self.mem).insert(cur, set, self.name)
            con.commit()
            cur.close()
            self.mem.disconnect_xulpymoneyd(con)
            time.sleep(60)


    def parse_resultado(self, set):
        """Función que saca el id y los compara con los filtrados, es decir con los activos¡"""
        for q in set.arr:
            if q.product not in self.ids:
#                set.append({'id': d['id'], 'datetime': d['datetime'], 'quote': d['quote'] })
                set.arr.remove(q)
        



    def pagename2investment(self, name):
        if name==b'IBEX 35':
            return self.mem.activas(79329)
        else:
            return None
    
    def execute(self):    
        (resultado, error)=(SetQuotes(), [])

        web=self.download('http://infobolsa.es/indices-internacionales.htm', 'ARR_QUOTES')
        if web==None:
            return (resultado, error)   
        

        bloque=web.read().split(b'<td class="Tabla02_Izd"')
        for i in range(1, len(bloque)):
            try:
                quote=Quote()
                quote.product=self.pagename2investment(bloque[i].split(b'title="')[1].split(b'" >')[0])
                if quote.product==None:
                    continue
                lineas=bloque[i].split(b'</td>')
                quote.quote=float(comaporpunto(lineas[1].split(b">")[1].replace(b".", b"")))
                dat=datetime.datetime.strptime(b2s(lineas[9].split(b">")[1]), "%d/%m/%Y").date()
                tim=datetime.datetime.strptime(b2s(lineas[10].split(b">")[1])[:-3], "%H:%M").time()
                quote.datetime=dt(dat,tim,'Europe/Madrid')         
                resultado.append(quote)
            except:
                error.append(-999999999)
        if len(error)>0:
            log(self.name,"ARR_QUOTES", gettext.gettext("Error parseando %(e)d errores") %  {"e":len(error)})
        return (resultado, error)   
