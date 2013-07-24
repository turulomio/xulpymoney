# -*- coding: UTF-8  -*-
import gettext,  multiprocessing
from libmyquotes import *


class MercadoContinuo(Source):
    def __init__(self,  cfg):
        Source.__init__(self, cfg)
        self.time_before_dividends=180
        self.time_after_dividends=86400
        self.time_before_quotes=0
        self.time_after_quotes=60
        self.time_before_statics=120
        self.time_after_statics=86400
        self.name="MERCADOCONTINUO"
#        self.debug=True
        self.time_before_historicals=180 #Alto para que ya esten los staticsc
        self.time_step_historical=200
        self.time_after_historicals=86400       
        self.utctime_start=self.utctime(datetime.time(8, 0), 'Europe/Madrid')
        self.utctime_stop=self.utctime(datetime.time(18, 30), 'Europe/Madrid')

    def start(self):
#        q1 = multiprocessing.Process(target=self.update_dividends, args=())
#        q1.start()
        q2 = multiprocessing.Process(target=self.update_quotes, args=())
        q2.start()    
        q3 = multiprocessing.Process(target=self.update_statics, args=())
        q3.start()    
        
        yesterday=str(datetime.date.today()-datetime.timedelta(days=7))
        sql="select isin from investments, quotes where quotes.code=investments.code and quotes.code like 'MC#%' and isin like 'ES%' and quotes.date='"+yesterday+"' and last<>'close' order by isin;"

        q4 = multiprocessing.Process(target=self.update_step_historicals_by_isin, args=(sql,))
        q4.start()
        
    def arr_historical(self, yahoocode, isin):
        """isin se usa cuando se ha obtenido el code por isin2yahoocode para poner el nombre en code con yahoo_historical"""
        resultado=self.yahoo_historical(yahoocode,  "MC#"+isin)
        return resultado
    
    def arr_quotes(self):    
        resultado=[]

        web=self.download('http://www.bolsamadrid.es/esp/mercados/acciones/accmerc2_c.htm', 'ARR_QUOTES')
        if web==None:
            return []          
        
        error=0
 
        line=web.readline()
        for line in web.readlines():
#            print(dir(line))
            try:
                if line.find(b'/comun/fichaemp/fichavalor.asp?isin=')!=-1:#Saca todo de valores
                    d= {'code': None, 'date': None, 'time':None,'quote': None ,  'zone':'Europe/Madrid'}
                    d['code']=b2s(b"MC#"+line.split(b'?isin=')[1].split(b'"><IMG SRC="')[0])
                    date=line.split(b'</TD><TD align=center>')[1].split(b"/")
#                    print(date)
#                    if date[0]=='Cierre<': #Error raro
#                        continue
                    d['date']=datetime.date(int(date[2]),  int(date[1]),  int(date[0]))
                    d['quote']=float(comaporpunto(line.split(b'</TD><TD>')[1].split(b'</TD><TD')[0]))
                    tim=line.split(b'</TD><TD align=center>')[2].split(b"</TD></TR>")[0]
                    if tim==b'Cierre':
                        d['time']=datetime.time(17, 38)
                    else:
                        tim=tim.split(b":")
                        d['time']=datetime.time(int(tim[0]),  int(tim[1]))
                    (d['date'], d['time'], d['zone'])=utc2(d['date'], d['time'], d['zone'])
                    resultado.append(d)
            except:
                error=error+1
                continue    
        if error>0:
            log(self.name,"ARR_QUOTES",  gettext.gettext("Error parseando %(e)d errores") %  {"e":error})
        return resultado
            
    def arr_statics(self): 
        resultado=[]

        web=self.download('http://www.bolsamadrid.es/esp/mercados/acciones/accmerc2_c.htm', 'ARR_QUOTES', False)
        if web==None:
            return []          

        error=0
        line=web.readline()    
        for line in web.readlines():
            try:
                if line.find(b'/comun/fichaemp/fichavalor.asp?isin=')!=-1:
                    d= {'code': None, 'country': 'es', 'currency': 'EUR', 'isin': None, 'name': None, 'type': Type.share, 'agrupations': None, 'manual': False}
                    d['isin']=b2s(line.split(b'?isin=')[1].split(b'"><IMG SRC="')[0])
                    d['code']="MC#"+d['isin']
                    d['name']=b2s(line.split(b'BORDER=0> ')[1].split(b'</A></TD>')[0])#, 'ISO-8859-15')
                    d['agrupations']=self.agrupations(d['isin'], ['MERCADOCONTINUO', ])
                    resultado.append(d)
            except:
                error=error+1
                continue    
        if error>0:
            log(self.name,"ARR_STATICS",  gettext.gettext("Error parseando %(e)d errores") %  {"e":error})
        return resultado
     
