# -*- coding: UTF-8  -*-
import gettext,  multiprocessing
from libmystocks import *

class Carmignac(Source):
    def __init__(self,  cfg):
        Source.__init__(self, cfg)
        self.time_before_dividends=180
        self.time_after_dividends=86400
        self.time_before_quotes=0
        self.time_after_quotes=86400
        self.time_before_statics=120
        self.time_after_statics=86400
        self.name="CARMIGNAC"
        self.utctime_start=self.utctime(datetime.time(8, 0), 'Europe/Paris')
        self.utctime_stop=self.utctime(datetime.time(18, 30), 'Europe/Paris')
#        self.debug=True

    def start(self):
        q1 = multiprocessing.Process(target=self.update_dividends, args=())
        q1.start()
        q2 = multiprocessing.Process(target=self.update_quotes, args=())
        q2.start()    
        q3 = multiprocessing.Process(target=self.update_statics, args=())
        q3.start()    

        
    def arr_dividends(self):
        resultado=[]
        con=self.cfg.connect_mystocksd()
        cur=con.cursor()
        cur.execute("select code from investments where dividend<>0 and agrupations like '%|CARMIGNAC|%'")
        if cur.rowcount!=0:
            for row in cur:
                d={"code":row['code'], "dividend": 0}
                resultado.append(d)
        cur.close()
        self.cfg.disconnect_mystocksd(con)            
        return resultado
    
    def arr_quotes(self):  
        resultado=[]           
        web=self.download('http://www.carmignac.es/es/valores-liquidativos.htm', 'ARR_QUOTES')
        if web==None:
            return []
 
        line=web.readline().decode()    
        while line.find("</html>")==-1: 
            try:
                if line.find('<td class="ref" style="height:19px;">') != -1:
                    d= {'code': None, 'date': None, 'time':None,'quote': None ,  'zone':'UTC'}
                    d['code']=line.split('<td class="ref" style="height:19px;">')[1].split('</td><td>')[0]
                    line=web.readline().decode()    
                    line=web.readline().decode()    
                    line=web.readline().decode()    
                    line=web.readline().decode()   
                    date=line[:-2].split('/')
                    d['date']=datetime.date(int(date[2]),  int(date[1]),  int(date[0]))
                    line=web.readline().decode()    
                    line=web.readline().decode()   
                    d['quote']=float(comaporpunto(line[:-1]))
                    d['time']=None
                    resultado.append(d)
            except:
                log(self.name,"ARR_QUOTES", gettext.gettext("Error parseando"))
                break    
                
            line=web.readline().decode()      
        return resultado
    
            
    def arr_statics(self):
        resultado=[]      
        web=self.download('http://www.carmignac.es/es/valores-liquidativos.htm', 'ARR_STATICS', False)
        if web==None:
            return []

        line=web.readline().decode()    
        while line.find("</html>")==-1: 
            try:
                d= {'code': None, 'country': 'fr', 'currency': 'EUR', 'isin': None, 'name': None, 'type': Type.fund, 'agrupations': '|CARMIGNAC|', 'manual': False}
                if line.find('<td class="ref" style="height:19px;">') != -1:
                    d['code']=line.split('<td class="ref" style="height:19px;">')[1].split('</td><td>')[0]
                    d['isin']=d['code']
                    a=web.readline().decode().strip()
                    b=web.readline().decode().strip()    #El nombre puede estar en dos líneas
                    name= a+b
                    name=name.replace('</a>', '')
                    name=name.replace('<br />', ' ')
                    d['name']=name.split('>')[1]
                    line=web.readline().decode()    
                    line=web.readline().decode()   
                    line=web.readline().decode()    
                    line=web.readline().decode()   
                    resultado.append(d) 
            except:
                log(self.name,"ARR_STATICS", gettext.gettext("Error parseando"))
                break    
            line=web.readline().decode()   
        return resultado
        
