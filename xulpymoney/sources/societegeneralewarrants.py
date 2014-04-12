# -*- coding: UTF-8  -*-
import gettext,  multiprocessing
from libmystocks import *

    
class SocieteGeneraleWarrants(Source):
    def __init__(self,  cfg):
        Source.__init__(self, cfg)
        self.time_before_dividends=180
        self.time_after_dividends=86400
        self.time_before_quotes=0
        self.time_after_quotes=300
        self.time_before_statics=10
        self.time_step_static=600
        self.time_after_statics=86400
        self.name="SGWARRANTS"
        self.utctime_start=self.utctime(datetime.time(8, 0), 'Europe/Madrid')
        self.utctime_stop=self.utctime(datetime.time(18, 30), 'Europe/Madrid')
#        self.debug=True

    def start(self):
        q1 = multiprocessing.Process(target=self.update_dividends, args=())
        q1.start()
        q2 = multiprocessing.Process(target=self.update_quotes, name="Prueba", args=())
        q2.start()    
        q3 = multiprocessing.Process(target=self.update_step_statics, args=("select code from products where name is null and code like 'SGW#%'",))
        q3.start()          

    
    def arr_dividends(self):
        resultado=[]
        con=self.cfg.connect_mystocksd()
        cur=con.cursor()
        cur.execute("select code from products where dividend is null and code like 'SGW#%'")
        if cur.rowcount!=0:
            for row in cur:
                d={"code":row['code'], "dividend": 0}
                resultado.append(d)
        cur.close()
        self.cfg.disconnect_mystocksd(con)            
        return resultado
        
    
    def arr_quotes(self):    
        def s_inline():#Yahoo en EST 200 primeros
            web=self.download('http://es.warrants.com/services/quotes/products.php?family=WARRANT&typeul=INDEX&ullabel=IBEX+35+inLine', 'S_INLINE')
            if web==None:
                return []

            resultado=[]
            error=0
            for line in web.readlines():
                try:
                    if line.find(b'ltima actualizaci')!=-1:
                        dt=line.split(b" : ")[1].split(b"'</i>")[0]
                        d=int(dt.split(b" ")[0].split(b"/")[0])
                        M=int(dt.split(b" ")[0].split(b"/")[1])
                        Y=int(dt.split(b" ")[0].split(b"/")[2])
                        H=int(dt.split(b" ")[1].split(b":")[0])
                        m=int(dt.split(b" ")[1].split(b":")[1])
                        date=datetime.date(Y, M, d)
                        time=datetime.time(H, m)
                        curi=1
                        i=line.split(b"';\">")
        #                for inl in i:
        #                    print inl
                        while True:
        #                    print i[curi]
                            dic= {'code': None, 'date': None, 'time':None,'quote': None, 'zone':'Europe/Paris' }   
                            dic['date']=date
                            dic['time']=time
                            dic['code']=b2s(b'SGW#'+i[curi].split(b'</a></div></td>')[0])
                            curi=curi+3
                            #Cuando cierra el mercado pone 12.12(c)
                            quote=i[curi].split(b'</a></div></td>')[0]
#                            print "|%s|%s|"% (quote,  quote[len(quote)-3:])
                            if quote[len(quote)-3:]==b'(c)':
                                dic['quote']=float(quote[0:-3])
                            else:
                                dic['quote']=float(quote)
                            curi=curi+7
                            (dic['date'], dic['time'], dic['zone'])=utc2(dic['date'], dic['time'], dic['zone'])
                            resultado.append(dic)
                            if curi+10>len(i):
                                break
                except:
                    error=error +1
                    continue           
            if error>0:
                log(self.name, "S_INLINE", gettext.gettext("Han habido %(errores)d errores en el parseo" %{ "errores":error}))
            return resultado
            
        def s_turbo():
            web=self.download('http://es.warrants.com/services/quotes/products.php?family=TURBO&typeul=INDEX&ullabel=IBEX+35',  'S_TURBO')
            if web==None:
                return []

            resultado=[]
            error=0
            for line in web.readlines():
                if line.find(b'ltima actualizaci')!=-1:
                    dt=line.split(b" : ")[1].split(b"'</i>")[0]
                    d=int(dt.split(b" ")[0].split(b"/")[0])
                    M=int(dt.split(b" ")[0].split(b"/")[1])
                    Y=int(dt.split(b" ")[0].split(b"/")[2])
                    H=int(dt.split(b" ")[1].split(b":")[0])
                    m=int(dt.split(b" ")[1].split(b":")[1])
                    date=datetime.date(Y, M, d)
                    time=datetime.time(H, m)
                    trs=line.split(b"<tr class=")
                    for i in trs:
#                        print i
                        try:
                            dic= {'code': None, 'date': None, 'time':None,'quote': None, 'zone':'Europe/Madrid' }   
                            dic['date']=date
                            dic['time']=time
                            dic['code']=b2s(b'SGW#'+i.split(b'\';">')[1].split(b'</a></div></td>')[0])
                            #Cuando cierra el mercado pone 12.12(c)
                            
                            
                            quote=i.split('\';">')[6].split(b'</a></div></td>')[0]
#                            print quote
                            if quote[len(quote)-3:]==b'(c)':
                                dic['quote']=float(quote[0:-3])
                            else:
                                dic['quote']=float(quote)
#                            print dic
                            (dic['date'], dic['time'], dic['zone'])=utc2(dic['date'], dic['time'], dic['zone'])
                            resultado.append(dic)
                        except:
                            error=error +1
#                            print dic
                            continue   
            if error>0:
                log(self.name, "S_TURBO", gettext.gettext("Han habido %(errores)d errores en el parseo " %{ "errores":error}))
            return resultado            
            
        def s_ibex():
            def page(number):
                web=self.download('http://es.warrants.com/services/quotes/products.php?family=WARRANT&typeul=INDEX&ullabel=IBEX%2035&page='+str(number),  'S_IBEX')
                if web==None:
                    return []
    
                resultado=[]
                error=0
                for line in web.readlines():
                    if line.find(b'ltima actualizaci')!=-1:
                        try:
                            dt=line.split(b" : ")[1].split(b"'</i>")[0]
                            d=int(dt.split(b" ")[0].split(b"/")[0])
                            M=int(dt.split(b" ")[0].split(b"/")[1])
                            Y=int(dt.split(b" ")[0].split(b"/")[2])
                            H=int(dt.split(b" ")[1].split(b":")[0])
                            m=int(dt.split(b" ")[1].split(b":")[1])
                            date=datetime.date(Y, M, d)
                            time=datetime.time(H, m)
                            trs=line.split(b"<tr class=")
                        except:
                            error=error+1000
                            break
                        for i in trs:
    #                        print i
                            try:
                                dic= {'code': None, 'date': None, 'time':None,'quote': None, 'zone':'Europe/Madrid' }   
                                dic['date']=date
                                dic['time']=time
                                dic['code']=b2s(b'SGW#'+i.split(b'\';">')[2].split(b'</a></div></td>')[0])
                                #Cuando cierra el mercado pone 12.12(c)
                                
                                
                                quote=i.split(b'\';">')[6].split(b'</a></div></td>')[0]
    #                            print quote
                                if quote[len(quote)-3:]==b'(c)':
                                    dic['quote']=float(quote[0:-3])
                                else:
                                    dic['quote']=float(quote)
#                                print dic
                                (dic['date'], dic['time'], dic['zone'])=utc2(dic['date'], dic['time'], dic['zone'])
                                resultado.append(dic)
                            except:
                                error=error +1
#                                print dic
                                continue  
                        
                if error>0:
                    log(self.name, "S_IBEX", gettext.gettext("Han habido %(errores)d errores en el parseo " %{ "errores":error}))
                return resultado 
            return page(1)+page(2)+page(3)+page(4)
            
        return s_inline()+s_turbo() +s_ibex()
            
    def arr_static(self, code): 
        resultado=[]
        web=self.download('http://es.warrants.com/services/quotes/details.php?code=' + code[len('SGW#'):], 'ARR_STATIC')
        if web==None:
            return []

        dic= {'code': code, 'country': 'fr', 'currency': 'EUR', 'isin': None, 'name': None, 'type': Type.warrants, 'agrupations': '|SGW|', 'manual': False}
        while True:
            line=web.readline()
            try:
                if line.find(b'<span class=ullabel><a href="#" style=\'color:#FFFFFF; text-decoration:none;\'>')!=-1:
                    line=web.readline()
#                    print line
                    name=line.split(b'</b></span></a>')[0]
                    name=name.replace(b"<font style='text-transform:uppercase'>", b'')
                    name=name.replace(b'</font>',  b'')
                    name=name.replace(b'<span class=biggergray><b>',  b'')
                    name=name.replace(b'\x80', b'\xe2\x82\xac')
    #                name = unicode(name, 'ISO-8859-15')
                    dic['name']=b2s(name.strip())
                    line=web.readline()
                if line.find(b"digo ISIN</div><div class='right'>")!=-1:
                    dic['isin']=b2s(line.split(b"igo ISIN</div><div class='right'>")[1].split(b'</div></div><div style="background-image:url')[0])
                    resultado.append(dic)
                    break
            except:
                log(self.name,"ARR_STATIC",  gettext.gettext("Error en el parseo de %(code)" %{ "code":code}))
                break
#        print resultado
#        Product(self.cfg).update_static( resultado,  "S_SOCIETEGENERALEWARRANTS_STATIC")
        return resultado
