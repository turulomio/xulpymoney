# -*- coding: UTF-8  -*-
import gettext,  multiprocessing
from libmystocks import *


class Euronext(Source):
    def __init__(self,  cfg):
        Source.__init__(self, cfg)
        self.time_before_dividends=180
        self.time_after_dividends=86400
        self.time_before_quotes=0
        self.time_after_quotes=300
        self.time_before_statics=250
        self.time_after_statics=86400
        self.name="EURONEXT"        
        self.time_before_historicals=180 #Alto para que ya esten los staticsc
        self.time_step_historical=300
        self.time_after_historicals=86400       
        self.utctime_start=self.utctime(datetime.time(8, 0), 'CET')
        self.utctime_stop=self.utctime(datetime.time(18, 30), 'CET')
#        self.downloadalways=True
#        self.debug=True

    def start(self):
#        q1 = multiprocessing.Process(target=self.update_dividends, args=())
#        q1.start()
        q2 = multiprocessing.Process(target=self.update_quotes, args=())
        q2.start()    
        q3 = multiprocessing.Process(target=self.update_statics, args=())
        q3.start()    
        yesterday=str(datetime.date.today()-datetime.timedelta(days=7))
        sql="select isin from products, quotes where quotes.code=products.code and quotes.code like 'EURONEXT#%' and isin is not null and quotes.date='"+yesterday+"' and last<>'close' order by isin;"
        q4 = multiprocessing.Process(target=self.update_step_historicals_by_isin, args=(sql,))
        q4.start()
        
    def arr_historical(self, yahoocode, isin):
        """isin se usa cuando se ha obtenido el code por isin2yahoocode para poner el nombre en code con yahoo_historical"""
        resultado=self.yahoo_historical(yahoocode, "EURONEXT#"+isin)
        return resultado
    
    def arr_quotes(self):    
        web=self.download('http://www.euronext.com/search/download/trapridownloadpopup.jcsv?cha=1800&countrygp=Europe&lan=EN&pricesearchresults=actif&resultsTitle=All+Euronext+-+Euronext&totalOfInstruments=1093&format=txt&formatDicimal=.&formatDate=dd/MM/yy', 'ARR_QUOTES')
        if web==None:
            return []
        
        resultado=[]
        error=0
        for line in web.readlines():
            try:
                arr=line.split(b";")
                if len(arr)<5 or arr[0]==b"Instrument's name":
#                    print ("mal")
                    continue
#                print (arr)
                d= {'code': None, 'date': None, 'time':None,'quote': None ,  'zone':'CET'}
                d['code']=b2s(b"EURONEXT#"+arr[1])
                date=b2s(arr[10].split(b" ")[0]).split("/")
#                print (date)
                d['date']=datetime.date(2000+int(date[2]),  int(date[1]),  int(date[0]))
                d['quote']=float(arr[7])
                tim=b2s(arr[10].split(b" ")[1]).split(":")
                d['time']=datetime.time(int(tim[0]),  int(tim[1]))
                (d['date'], d['time'], d['zone'])=utc2(d['date'], d['time'], d['zone'])
                resultado.append(d)
            except:
                error=error+1
                continue    

        log(self.name,"ARR_QUOTES",gettext.gettext("%(e)d errores parseando") %  {"e":error})
#        print len(resultado)
        return resultado
                
    def country(self, co):
        if co=="AMS":
            return 'nl'
        elif co=="PAR":
            return 'fr'
        elif co=="BRU":
            return 'be'
        elif co=="LIS":
            return 'pt'
        else:
            print (co+  " country no exite")
            return None
    def arr_statics(self):             
        resultado=[]
        error=0
        web=self.download('http://www.euronext.com/search/download/trapridownloadpopup.jcsv?cha=1800&countrygp=Europe&lan=EN&pricesearchresults=actif&resultsTitle=All+Euronext+-+Euronext&totalOfInstruments=1093&format=txt&formatDicimal=.&formatDate=dd/MM/yy', 'ARR_STATICS',  False)
        if web==None:
            return []        

        for line in web.readlines():
            try:
                arr=line.split(b";")
                if len(arr)<5 or arr[0]==b"Instrument's name":
#                    print ("mal")
                    continue
                d= {'code': None, 'country': None, 'currency': 'EUR', 'isin': None, 'name': None, 'type': Type.share, 'agrupations': None, 'manual': False}
                d['code']=b2s(b"EURONEXT#"+arr[1])
                d['country']=self.country(b2s(arr[3]))
                d['quote']=float(b2s(arr[7]))
                d['isin']=b2s(arr[1])
                d['name']=b2s(arr[0])
                d['agrupations']=self.agrupations(d['isin'], ['EURONEXT', ])
                resultado.append(d)
            except:
                error=error+1
                line=web.readline()
                continue    

            line=web.readline()
        if error>0:
            log(self.name,"ARR_STATICS " ,  gettext.gettext("%(e)d errores parseando") %  {"e":error })            
        return resultado
