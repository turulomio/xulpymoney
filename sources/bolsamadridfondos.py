from libmystocks import *
class WorkerBolsaMadridFondos(Source):
    """Clase que recorre las inversiones activas y calcula según este la prioridad de la previsión"""
    def __init__(self, cfg):
        Source.__init__(self, cfg)
        self.cfg=cfg
        self.id_source=2
        self.ids=[]
        self.name="BMF"
        
    def start(self):
        print (self.name)
        while (True):
            con=self.cfg.connect_mystocksd()
            cur = con.cursor()     
            self.ids=self.filtrar_ids_bmf()
            (resultado, errors)=self.execute()
            parsed=self.parse_resultado(resultado)
            print (parsed)
            Quote(self.cfg).insert(cur, parsed, self.name)
            con.commit()
            cur.close()                
            self.cfg.disconnect_mystocksd(con)
            time.sleep(60*60*24)

    def parse_resultado(self, resultado):
        """Función que saca el id y los compara con los filtrados, es decir con los activos¡"""
        parsed=[]
        for d in resultado:
            id=self.isin2id(d['isin'], 1) 
            if id in self.ids:
                parsed.append({'id': id, 'datetime': d['datetime'], 'quote': d['quote'] })
        return parsed
            
    
    def filtrar_ids_bmf(self):
        """Función qu filtra aquellos que su prioridad es 0 y que están active"""
        resultado=[]
        for i in self.cfg.activas:
            if self.cfg.activas[i].priority!=None:
                if len(self.cfg.activas[i].priority)>=1:
                    if self.cfg.activas[i].priority[0]==2 and self.cfg.activas[i].active==True:
                        resultado.append(self.cfg.activas[i].id)
        return resultado
    
    def ids2yahoo(self, ids):
        if ids==None:
            print ("ids2yahoo > Tenemos un yahoo NOne")
        yahoos=[]
        for id in ids:
            yahoos.append(self.cfg.activas[str(id)].yahoo)
        return yahoos
    
    def execute(self):    
        def pagina(comand):
            (resultado, error)=([], [])
            web=self.download(comand, 'ARR_QUOTES')
            if web==None:
                return (resultado, error)   
            line=web.readline()
            while line.find(b"</HTML>")==-1:
                try:
                    line=web.readline()
                    d= {'isin': None, 'datetime': None, 'quote': None }
                    if line.find(b"<TR ALIGN=RIGHT bgcolor=#ffffff>") != -1:
                        line=web.readline()
                        line=web.readline()
                        d['isin']=b2s(line.split(b"../fonficha.asp?fondo=")[1].split(b"')")[0])
                        line=web.readline()
                        line=web.readline()
                        dat=b2s(line.split(b"<TD align=center>")[1].split(b"</TD>")[0]).split("/")
                        date=datetime.date(int(dat[2]), int(dat[1]), int(dat[0]))
#                        dt=changetz(dt, self.cfg.bolsas['1'].zone, 'UTC')

                        bolsa=self.cfg.bolsas[str(1)]
                        ends=bolsa.ends.replace(microsecond=4)
                        datetim=dt(date,ends,"Europe/Madrid")+datetime.timedelta(minutes=10)
                        d['datetime']=datetim
                        line=web.readline()        
                        d['quote']=float(comaporpunto((line.split(b"<TD>")[1].split(b"</TD>")[0]).replace(b".", b"")))
                        resultado.append(d)                
                except:
                    error.append(d['isin'])
                    continue
            return (resultado,  error)
        while True:
            (resultado, error)=pagina('http://www.bolsamadrid.es/esp/mercados/fondos/htm/talfa.htm')
            time.sleep(1)
            for i in range(26):
                (r, e)=pagina('http://www.bolsamadrid.es/esp/mercados/fondos/htm/talfa'+str(i+1)+'00.htm')
                resultado=resultado+r
                error=error+e
                time.sleep(1)                    
            log(self.name, "ERROR PARSING",  "{0}".format(str(error)))
            return (resultado,  error)
            
