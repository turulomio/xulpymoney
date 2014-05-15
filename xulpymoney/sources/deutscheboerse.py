# -*- coding: UTF-8  -*-
import gettext,  multiprocessing
from libmystocks import *


class DeutscheBoerse(Source):
    def __init__(self,  mem):
        Source.__init__(self, mem)
        self.time_before_dividends=180
        self.time_after_dividends=86400
        self.time_before_quotes=0
        self.time_after_quotes=300
        self.time_before_statics=100
        self.time_after_statics=86400

        self.time_before_historicals=180 #Alto para que ya esten los staticsc
        self.time_step_historical=300
        self.time_after_historicals=86400        
        self.name="DEUTSCHEBOERSE"
        self.utctime_start=self.utctime(datetime.time(8, 0), 'Europe/Berlin')
        self.utctime_stop=self.utctime(datetime.time(18, 30), 'Europe/Berlin')
#        self.debug=True

    def start(self):
#        q1 = multiprocessing.Process(target=self.update_dividends, args=())
#        q1.start()
        q2 = multiprocessing.Process(target=self.update_quotes, args=())
        q2.start()    
        q3 = multiprocessing.Process(target=self.update_statics, args=())
        q3.start()    
        
        yesterday=str(datetime.date.today()-datetime.timedelta(days=7))
        sql="select isin from products, quotes where quotes.code=products.code and quotes.code like 'DEUTSCHEBOERSE#%' and isin like 'DE%' and quotes.date='"+yesterday+"' and last<>'close' order by isin;"

        q4 = multiprocessing.Process(target=self.update_step_historicals_by_isin, args=(sql,))
        q4.start()
        
    def arr_historical(self, yahoocode, isin):
        """isin se usa cuando se ha obtenido el code por isin2yahoocode para poner el nombre en code con yahoo_historical"""
        resultado=self.yahoo_historical(yahoocode, "DEUTSCHEBOERSE#"+isin)
        return resultado
        
    def arr_quotes(self):    
        resultado=[]
        error=0
        ##self.add_internetquery_into_sqlite(self.mem.consqlite)
        web=self.download('http://deutsche-boerse.com/bf4dbag/EN/export/export.aspx?module=IndexConstituents&isin=DE0007203325&title=Constituent+Equities&perpage=1000', 'ARR_QUOTES')
        if web==None:
            return []                
#        line=web.readline()
#        while line.find('</html>')==-1:
        for line in web.readlines():
#            print ("otrabaez")
            try:
                if line.find(b'<td class="column-name first" rowspan="2">')!=-1:
                    d= {'code': None, 'date': None, 'time':None,'quote': None ,  'zone':'Europe/Berlin'}
                    d['code']=b2s(b"DEUTSCHEBOERSE#"+line.split(b'<br />')[1].split(b'</td>')[0])
                    date=line.split(b'"column-timestamp">')[1].split(b'</td>')[0].split(b' ')[0].split(b'.')
                    d['date']=datetime.date(datetime.date.today().year,  int(date[1]),  int(date[0]))
                    d['quote']=float(line.split(b'"column-price">')[1].split(b'</td>')[0])
                    tim=line.split(b'"column-timestamp">')[1].split(b'</td>')[0].split(b' ')[1].split(b':')
                    d['time']=datetime.time(int(tim[0]),  int(tim[1]))
                    (d['date'], d['time'], d['zone'])=utc2(d['date'], d['time'], d['zone'])                    
                    resultado.append(d)
            except:
                error=error+1
#                line=web.readline()
                continue    

#            line=web.readline()
        if error>0:
            log(self.name,"ARR_QUOTES", gettext.gettext("%(e)d errores parseando") %  {"e":error })            
#        print ("FINE")
        return resultado
            
    def arr_statics(self): 
        resultado=[]
        error=0
        ##self.add_internetquery_into_sqlite(self.mem.consqlite)
        web=self.download('http://deutsche-boerse.com/bf4dbag/EN/export/export.aspx?module=IndexConstituents&isin=DE0007203325&title=Constituent+Equities&perpage=1000', 'ARR_STATICS', False)
        if web==None:
            return []                 
        line=web.readline().decode()
        while line.find('</html>')==-1:
            try:
                if line.find('<td class="column-name first" rowspan="2">')!=-1:
                    d= {'code': None, 'country': 'de', 'currency': 'EUR', 'isin': None, 'name': None, 'type': Type.share, 'agrupations': None, 'manual': False}
                    d['isin']=line.split('<br />')[1].split('</td>')[0]
                    d['code']="DEUTSCHEBOERSE#"+d['isin']
                    d['agrupations']=self.agrupations(d['isin'], ['DEUTSCHEBOERSE', ])
                    d['name']=web2utf8(line.split('"column-name first" rowspan="2">')[1].split('<br />')[0])

                    resultado.append(d)
            except:
                error=error+1
                line=web.readline().decode()
                continue    

            line=web.readline().decode()

        if error>0:
            log(self.name,"ARR_STATICS", gettext.gettext("%(e)d errores parseandox") %  {"e":error  })            
        return resultado        
            
