# -*- coding: UTF-8  -*-
import multiprocessing
from libmystocks import *


class NYSE(Source):
    def __init__(self,  mem):
        Source.__init__(self, mem)
        self.time_before_dividends=180
        self.time_after_dividends=86400
        self.time_before_quotes=0
        self.time_step_quotes=10
        self.time_after_quotes=300
        self.time_before_statics=250
        self.time_after_statics=86400
        self.name="NYSE"
        self.utctime_start=self.utctime(datetime.time(8, 0), 'US/Eastern')
        self.utctime_stop=self.utctime(datetime.time(18, 30), 'US/Eastern')
#        self.nyse=self.set_nyse()
#        self.debug=True

        self.time_before_historicals=180 #Alto para que ya esten los staticsc
        self.time_step_historical=300
        self.time_after_historicals=86400       

    def start(self):
#        q1 = multiprocessing.Process(target=self.update_dividends, args=())
#        q1.start()
        q2 = multiprocessing.Process(target=self.update_quotes, args=())
        q2.start()    
        q3 = multiprocessing.Process(target=self.update_statics, args=())
        q3.start()    
        yesterday=str(datetime.date.today()-datetime.timedelta(days=7))
        sql="select quotes.code from products, quotes where quotes.code=products.code and quotes.code like 'NYSE#%' and quotes.date='"+yesterday+"' and last<>'close' order by quotes.code;"
        con=self.mem.connect_xulpymoneyd()
        cur=con.cursor()
        cur.execute(sql)
        codes=[]
        for i in cur:
            codes.append(i['code'][5:])
        cur.close()
        self.mem.disconnect_xulpymoneyd(con)        

        q4 = multiprocessing.Process(target=self.update_step_historicals, args=(codes,))
        q4.start()
        
    def arr_historical(self, yahoocode, isin):
        """isin se usa cuando se ha obtenido el code por isin2yahoocode para poner el nombre en code con yahoo_historical"""
        resultado=self.yahoo_historical(yahoocode,  "NYSE#"+yahoocode)
        return resultado
    
    def arr_quotes(self):
        count=0
        errores=0
        resultado=[]
        quotes=[]
        for code  in self.mem.nyse:
            if count >90:
#                print code
                parsed=self.yahoo_quotes(quotes,  "NYSE#")
                resultado=resultado+parsed[0]
                errores=errores+parsed[1]
#                print len(resultado)
                quotes=[]
                count=0
            else:
                quotes.append(code)
                count=count +1

        if errores>0:
            log(self.name, "ARR_QUOTES " ,"Han habido %(e)d errores en el parseo" % {"e":errores})
        return resultado
            
    def arr_statics(self): 

        resultado=[]
        web=self.download('http://www.nyse.com/indexes/nyaindex.csv', 'ARR_STATICS', False)
        if web==None:
            return resultado        
        for line in web.readlines():
            
            d= {'code': None, 'country': 'us', 'currency': 'USD', 'isin': None, 'name': None, 'type': Type.share, 'agrupations': None, 'manual': False}
            arr=line.decode().replace('"', '').split(',')
            d['code']='NYSE#'+arr[1]
            d['name']=arr[0]
            d['isin']=None
            d['agrupations']=self.agrupations(d['isin'])#no hay base ya NYSE esta en agrupaciones
            resultado.append(d)
        return resultado
