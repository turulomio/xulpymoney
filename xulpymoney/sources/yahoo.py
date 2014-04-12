from libmystocks import *
import math
class WorkerYahoo(Source):
    """Clase que recorre las inversiones activas y calcula según este la prioridad de la previsión"""
    def __init__(self, cfg):
        Source.__init__(self, cfg)
        self.cfg=cfg
        self.id_source=1
        self.ids=[]
        self.name="YAHOO"
        
    def start(self):
        print (self.name)
        while (True):
            con=self.cfg.connect_mystocksd()
            cur = con.cursor()     
            self.ids=self.filtrar_horario_bolsa(self.find_ids())
            (p,e)=(SetQuotes(),[])
#            print (arr_split(self.ids, math.ceil(float(len(self.ids))/180)))
            for a in arr_split(self.ids, math.ceil(float(len(self.ids))/180)):
                (parsed, errors)=self.execute(a)
                p.arr=p.arr+parsed.arr
                e=e+errors
                time.sleep(3)
            self.parse_errors(cur,  e)
            p.save(cur,"YAHOO")

#            Quote(self.cfg).insert(cur, p, self.name)
            con.commit()
            cur.close()                
            self.cfg.disconnect_mystocksd(con)
            time.sleep(60)

    
    def ids2yahoo(self, products):
        if products==None:
            print ("ids2yahoo > Tenemos un yahoo None")
        yahoos=[]
        for inv in products:
            yahoos.append(inv.yahoo)
        return yahoos
            
    
    def execute(self, ids):
        (resultado, error)=(SetQuotes(), [])
        
        web=self.download('http://download.finance.yahoo.com/d/quotes.csv?s=' + strnames(self.ids2yahoo(ids)) + '&f=sl1d1t1&e=.csv', 'YAHOO_QUOTES')
        print ('http://download.finance.yahoo.com/d/quotes.csv?s=' + strnames(self.ids2yahoo(ids)) + '&f=sl1d1t1&e=.csv')
        if web==None:
            return (resultado, error)   

        for i in web.readlines():
            try:
#                dic= {'id': None, 'datetime': None, 'quote': None }
                i=b2s(i)
                datos=i[:-2].split(",")#Se quita dos creo que por caracter final linea windeos.
                inv=self.yahoo2investment(datos[0][1:-1],self.ids)
#                print (inv)
                #dic['id']=inv.id
                quote=datos[1]
                d=int(datos[2][1:-1].split("/")[1])
                M=int(datos[2][1:-1].split("/")[0])
                Y=int(datos[2][1:-1].split("/")[2])
                H=int(datos[3][1:-1].split(":")[0])
                m=int(datos[3][1:-1].split(":")[1][:-2])
                pm=datos[3][1:-1].split(":")[1][2:]
                
                #Conversion
                H=ampm_to_24(H, pm)
                dat=datetime.date(Y, M, d)
                tim=datetime.time(H, m)
                zon='America/New_York'#'US/Eastern'
                #dic['datetime']=dt(dat,tim,zon)
                if inv==None:
                    print("none paresed")
                    continue
                resultado.append(Quote().init__create(inv,dt(dat,tim,zon), quote))
            except:#
                log(self.name, "ERROR PARSING",  "{0}".format("yahoo"))
                continue
#        print (resultado)
        return (resultado,  error)
