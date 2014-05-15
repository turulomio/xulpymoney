# -*- coding: UTF-8  -*-
import gettext,  multiprocessing
from libmystocks import *

class Divisas(Source):
    def __init__(self,  mem):
        Source.__init__(self, mem)
        self.time_before_quotes=0
        self.time_after_quotes=300
        self.time_before_statics=15#0
        self.time_after_statics=86400
        self.name="DIVISAS"
        self.debug=True
        self.utctime_start=self.utctime(datetime.time(8, 0), 'Europe/Madrid')
        self.utctime_stop=self.utctime(datetime.time(18, 30), 'Europe/Madrid')

    def start(self):
#        q1 = multiprocessing.Process(target=self.update_dividends, args=())
#        q1.start()
        q2 = multiprocessing.Process(target=self.update_quotes, args=())
        q2.start()    
        q3 = multiprocessing.Process(target=self.update_statics, args=())
        q3.start()    

    
    def arr_quotes(self):    
        resultado=[]
        error=0
        ##self.add_internetquery_into_sqlite(self.mem.consqlite)
        web=self.download('http://www.fxstreet.es/cotizaciones/divisas-mundiales/', 'ARR_QUOTES')
        if web==None:
            return []                
        line=web.readline().decode()
        while line.find('</html>')==-1:
            try:
                if line.find('divisas-vista/cruce.aspx?id=')!=-1:
                    d= {'code': None, 'date': None, 'time':None,'quote': None ,  'zone':'Europe/Madrid'}
                    d['code']="DIVISAS#"+line.split('divisas-vista/cruce.aspx?id=')[1].split('" class="ttratescaglink')[0]
                    date=line.split('"column-timestamp">')[1].split('</td>')[0].split(' ')[0].split('.')
                    d['date']=datetime.date(datetime.date.today().year,  int(date[1]),  int(date[0]))
                    d['quote']=float(line.split('"column-price">')[1].split('</td>')[0])
                    tim=line.split('"column-timestamp">')[1].split('</td>')[0].split(' ')[1].split(':')
                    d['time']=datetime.time(int(tim[0]),  int(tim[1]))
                    (d['date'], d['time'], d['zone'])=utc2(d['date'], d['time'], d['zone'])                    
                    resultado.append(d)
            except:
                error=error+1
                line=web.readline().decode()
                continue    

            line=web.readline().decode()
        if error>0:
            log(self.name, "ARR_QUOTES",  gettext.gettext("{0} errores parseando".format(error)))            
        return resultado
            
    def arr_statics(self): 
        resultado=[]
        error=0
        ##self.add_internetquery_into_sqlite(self.mem.consqlite)
        web=self.download('http://www.fxstreet.es/cotizaciones/divisas-mundiales/', 'ARR_STATICS', False)
        if web==None:
            return []                 
        line=web.readline().decode()
        while line.find('</html>')==-1:
            try:
                if line.find('<td class="column-name first" rowspan="2">')!=-1:
                    d= {'code': None, 'country': 'eu', 'currency': '', 'isin': None, 'name': None, 'type': Type.divisas, 'agrupations': None, 'manual': False}
                    d['name']=line.split('"column-name first" rowspan="2">')[1].split('<br />')[0]
                    d['code']="DIVISAS#"+d['name']

                    resultado.append(d)
            except:
                error=error+1
                line=web.readline().decode()
                continue    

            line=web.readline().decode()

        if error>0:
            log(self.name, "ARR_STATICS", gettext.gettext("%(e)d errores parseandox") %  {"e":error  })            
        return resultado
        
