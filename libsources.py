from libxulpymoney import *
from urllib import *
        
class SetQuotes:
    """Clase que agrupa quotes un una lista arr. Util para operar con ellas como por ejemplo insertar"""
    def __init__(self, mem):
        self.mem=mem
        self.arr=[]
    
    def print(self):
        for q in self.arr:
            print(" * {}".format(q))
    
    def save(self):
        """Recibe con code,  date,  time, value, zone
            Para poner el dato en close, el valor de time debe ser None
            Devuelve una tripleta (insertado,buscados,modificados)
        """
        insertados=SetQuotes(self.mem)
        ignored=SetQuotes(self.mem)
        modificados=SetQuotes(self.mem)         
            
        for q in self.arr:
            if q.can_be_saved():
                ibm=q.save()
                if ibm==0:
                    ignored.append(q)
                elif ibm==1:
                    insertados.append(q)
                elif ibm==2:
                    modificados.append(q)
#        print (insertados.length(), ignored.length(), modificados.length())
        return (insertados, ignored, modificados)
             
             
    def addTo(self, settoadd):
        """Añade los quotes en array a un nuevo set paasado por parametro"""
        for q in self.arr:
            settoadd.append(q)

    def append(self, quote):
        self.arr.append(quote)        
        
    def length(self):
        return len(self.arr)
        
    def clear(self):
        del self.arr
        self.arr=[]
        
    def myqtablewidget(self, tabla, section):
        tabla.setColumnCount(3)
        tabla.setHorizontalHeaderItem(0, QTableWidgetItem(QApplication.translate(section, "Date and time", None, QApplication.UnicodeUTF8)))
        tabla.setHorizontalHeaderItem(1, QTableWidgetItem(QApplication.translate(section, "Product", None, QApplication.UnicodeUTF8)))
        tabla.setHorizontalHeaderItem(2, QTableWidgetItem(QApplication.translate(section, "Price", None, QApplication.UnicodeUTF8)))        
        tabla.clearContents()
        tabla.settings(section,  self.mem)       
        tabla.setRowCount(len(self.arr))
        for rownumber, a in enumerate(self.arr):
            tabla.setItem(rownumber, 0, qdatetime(a.datetime, self.mem.localzone))
            tabla.setItem(rownumber, 1, qleft(a.product.name))
            tabla.setItem(rownumber, 2, a.product.currency.qtablewidgetitem(a.quote))

class Source(QObject):
    """Clase nueva para todas las sources
    Debera:
    - load_products
    - fech_page
    - parse_page
    - check_quotes"""
    def __init__(self, mem):
        QObject.__init__(self)
        self.mem=mem
        self.quotes=SetQuotes(self.mem)#Quotes without valida
        self.errors=[]#Array the strings
        
        self.ignored=SetQuotes(self.mem)
        self.modified=SetQuotes(self.mem)
        self.inserted=SetQuotes(self.mem)
        
    def log(self, error):
        self.errors.append("{} {}".format(datetime.datetime.now(), error))

            


    def myqtablewidget_errors(self, tabla, section):
        tabla.setColumnCount(2)
        tabla.setHorizontalHeaderItem(0, QTableWidgetItem(QApplication.translate(section, "Date and time", None, QApplication.UnicodeUTF8)))
        tabla.setHorizontalHeaderItem(1, QTableWidgetItem(QApplication.translate(section, "Log", None, QApplication.UnicodeUTF8)))
        tabla.clearContents()
        tabla.settings(section,  self.mem)       
        tabla.setRowCount(len(self.errors))
        for rownumber, line in enumerate(self.errors):
            a=line.split(" ")
            strdate="{} {}".format(a[0], a[1])
            tabla.setItem(rownumber, 0, qleft(strdate))
            tabla.setItem(rownumber, 1, qleft(line[len(strdate)+1:]))
            
    def quotes_save(self):
        """Saves all quotes after product iteration. If I want to do something different. I must override this function"""
        
        (self.inserted, self.ignored, self.modified)=self.quotes.save()
        
        #El commit se hace dentro porque hay veces hay muchas
#        inserted.addTo(self.inserted)
#        ignored.addTo(self.ignored)
#        modified.addTo(self.modified)
        print("{} finished. {} inserted, {} ignored and {} modified. Total quotes {}".format(self.__class__.__name__, self.inserted.length(), self.ignored.length(), self.modified.length(), self.quotes.length()))
            
    def errors_show(self):
        """Shwo errors aappended with log"""
        if len(self.errors)>0:
            print ("{} Errors in {}:".format(len(self.errors), self.__class__.__name__))
            for e in self.errors:
                print ("  + {}".format(e))
        
    def load_page(self, url ):
        """Función que devuelve la salida del comando urllib es un objeto HTTPResponse, normalmente es el parametro web o None si ha salido mal la descarga
        """        
        try:
            web=urllib.request.urlopen(url)
        except:            
            self.log("Error loading {}".format(url))
            return None
        return web        

    def comaporpunto(self, cadena):
        cadena=cadena.replace('.','')#Quita puntos
        cadena=cadena.replace(',','.')#Cambia coma por punto
        return cadena        

#    def run(self):
#        """Function to override, when launching the worker"""
#        pass
        
class SourceParsePage(Source):
    def __init__(self, mem, sql ):
        Source.__init__(self, mem)

        self.url="urlempty"
        self.sql=sql
        
    def run(self):
        self.products=SetProducts(self.mem)
        self.products.load_from_db(self.sql)       
        print (self.products.length())
        
        QObject.connect(self, SIGNAL("load_page()"), self.on_load_page)   
        self.emit(SIGNAL("load_page()"))
        
        QObject.connect(self, SIGNAL("parse_page()"), self.on_parse_page)      
        self.emit(SIGNAL("parse_page()")) 
 
        self.quotes_save()
        
        self.errors_show()
        self.inserted.print()
        
        self.emit(SIGNAL("run_finished()"))
        

    def on_load_page(self):
#        print(self.url)
        self.web=self.load_page(self.url)
        if self.web==None:
            return

    def on_parse_page(self):
        """This is the function to override. In the overrided function I must add Quotes with self.quotes.append. Will be saved later"""
        pass

class SourceIterateProducts(Source):
    """Several products in several pages
    
    Clase nueva para todas las sources
    Debera:
    - load_products
    - fech_page
    - parse_page
    - check_quotes"""
    def __init__(self, mem, sql, type=2, sleep=0):
        Source.__init__(self, mem)
        self.sleep=sleep#wait between products
        self.type=type#0 silent, 1 console, 2 qtgui
        self.sql=sql
        QObject.connect(self, SIGNAL("execute_product(int)"), self.on_execute_product)       

        
    def run(self):
        self.products=SetProducts(self.mem)
        self.products.load_from_db(self.sql)
 
        if type==2:
            self.pd= QProgressDialog(QApplication.translate("Core","Inserting {} prices of {} investments").format(0, self.products.length()), QApplication.translate("Core","Cancel"), 0,len(self.products.arr))
            self.pd.setModal(True)
            self.pd.setMinimumDuration(0)          
            self.pd.setWindowTitle(QApplication.translate("Core","Updating product prices..."))
        self.products_iterate()
        
        self.quotes_save()
        
        self.errors_show()
        
        self.emit(SIGNAL("run_finished()"))
        print("finished")
        
        
        

    def on_execute_product(self, id_product):
        """This is the function to override. In the overrided function I must add Quotes with self.quotes.append. Will be saved later"""
        pass

    def products_iterate(self):
        """Makes iteration. When its cancelled clears self.quotes.arr"""
        for i,  product in enumerate(self.products.arr):
            if self.type==2:
                self.pd.setValue(i)
                self.pd.update()
                QApplication.processEvents()
                if self.pd.wasCanceled():
                    self.quotes.clear()
                    break
                self.pd.update()
                QApplication.processEvents()
                self.pd.update()       
                stri=QApplication.translate("Core","Inserting {} prices of {} products").format(self.quotes.length(),self.products.length())
                self.pd.setLabelText(stri)           
            elif self.type==1:
                stri="{0}: {1}/{2} {3}. Appended: {4}            ".format(self.__class__.__name__, i+1, self.products.length(), product, self.quotes.length()) 
                sys.stdout.write("\b"*1000+stri)
                sys.stdout.flush()
            self.emit(SIGNAL("execute_product(int)"), product.id)
            time.sleep(self.sleep)#time step
        print("")


class WorkerMercadoContinuo(SourceParsePage):
    def __init__(self,  mem):
        SourceParsePage.__init__(self, mem, "select * from products where agrupations ilike '%MERCADOCONTINUO%';")   
        
    def on_load_page(self):
        "Overrides SourceParsePage"
        self.url='http://www.infobolsa.es/mercado-nacional/mercado-continuo'
        SourceParsePage.on_load_page(self)
        
    def on_parse_page(self):
        while True:
#            try:
                line=b2s(self.web.readline())[:-1]
                if line.find('<td class="ticker">')!=-1: #Empieza bloque
                    ticker=b2s(self.web.readline())[:-1].strip()+".MC"
                    self.web.readline()
                    self.web.readline()
                    quote=Decimal(self.comaporpunto(b2s(self.web.readline())[:-1].strip()))
                    for i in range(18):
                        self.web.readline()
                    hour=b2s(self.web.readline())[:-1].strip().split(":")
                    time=datetime.time(int(hour[0]), int(hour[1]))
                    self.web.readline()
                    self.web.readline()
                    self.web.readline()
                    date=b2s(self.web.readline())[:-1].strip().split("/")
                    date=datetime.date(int(date[2]), int(date[1]), int(date[0]))
                    #print(ticker,  quote, time,  date)
                    product=self.products.find_by_ticker(ticker)
                    if product:
                        datime=dt(date,time,product.stockexchange.zone)
                        self.quotes.append(Quote(self.mem).init__create(product, datime, quote))#closes
                    else:
                        self.log("El ticker {} no ha sido encontrado".format(ticker))
                if line.find('</html')!=-1:
                    break
#            except:
#                self.log("El ticker {} no ha sido formateado correctamente".format(ticker))

class WorkerYahoo(SourceParsePage):
    """Clase que recorre las inversiones activas y calcula según este la prioridad de la previsión"""
    def __init__(self, mem, sql):
        SourceParsePage.__init__(self, mem, sql)

    def sum_tickers(self):
        s=""
        for p in self.products.arr:
            if p.ticker!=None or p.ticker!="":
                s=s+p.ticker+"+"
        return s[:-1]
        
    def on_load_page(self):
        "Overrides SourceParsePage"
        self.url='http://download.finance.yahoo.com/d/quotes.csv?s=' + self.sum_tickers() + '&f=sl1d1t1&e=.csv'
        SourceParsePage.on_load_page(self)
        
        
    def on_parse_page(self):
        "Overrides SourceParsePage"
        for i in self.web.readlines():
            try:
                i=b2s(i)
                datos=i[:-2].split(",")#Se quita dos creo que por caracter final linea windeos.
                product=self.products.find_by_ticker(datos[0][1:-1])

                if product==None:
                    self.log("{} Not found".format(datos[0][1:-1] ))
                    continue                
                
                quote=Decimal(datos[1])
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
                bolsa=self.mem.stockexchanges.find(2)#'US/Eastern'
                self.quotes.append(Quote(self.mem).init__create(product,dt(dat,tim,bolsa.zone), quote))
            except:#
                self.log("Error parsing: {}".format(i[:-1]))
                continue

class WorkerYahooHistorical(SourceIterateProducts):
    """Clase que recorre las inversiones activas y busca la última  que tiene el microsecond 4. Busca en internet los historicals a partir de esa fecha"""
    def __init__(self, mem, type, sleep=0):
        SourceIterateProducts.__init__(self, mem,"select * from products where active=true and priorityhistorical[1]=3", type, sleep)
        #SourceIterateProducts.__init__(self, mem,"select * from products where id in (79329,81105)", type, sleep)        
        
    def on_execute_product(self,  id_product):
        """inico y fin son dos dates entre los que conseguir los datos."""
        product=self.products.find(id_product)

        ultima=product.fecha_ultima_actualizacion_historica()
        if ultima==datetime.date.today()-datetime.timedelta(days=1):
            return
        inicio= ultima+datetime.timedelta(days=1)
        fin= datetime.date.today()
        url='http://ichart.finance.yahoo.com/table.csv?s='+product.ticker+'&a='+str(inicio.month-1)+'&b='+str(inicio.day)+'&c='+str(inicio.year)+'&d='+str(fin.month-1)+'&e='+str(fin.day)+'&f='+str(fin.year)+'&g=d&ignore=.csv'

        web=self.load_page(url)
        if web==None:
            return
        
        web.readline()
        for i in web.readlines(): 
            i=b2s(i)
            datos=i.split(",")
            fecha=datos[0].split("-")
            date=datetime.date(int(fecha[0]), int(fecha[1]),  int(fecha[2]))
            
            datestart=dt(date,product.stockexchange.starts,product.stockexchange.zone)
            dateends=dt(date,product.stockexchange.closes,product.stockexchange.zone)
            datetimefirst=datestart-datetime.timedelta(seconds=1)
            datetimelow=(datestart+(dateends-datestart)*1/3)
            datetimehigh=(datestart+(dateends-datestart)*2/3)
            datetimelast=dateends+datetime.timedelta(microseconds=4)

            self.quotes.append(Quote(self.mem).init__create(product,datetimelast, Decimal(datos[4])))#closes
            self.quotes.append(Quote(self.mem).init__create(product,datetimelow, Decimal(datos[3])))#low
            self.quotes.append(Quote(self.mem).init__create(product,datetimehigh, Decimal(datos[2])))#high
            self.quotes.append(Quote(self.mem).init__create(product, datetimefirst, Decimal(datos[1])))#open

        self.mem.con.commit()      #To avoid big amounts at the end      
