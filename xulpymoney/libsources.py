from libxulpymoney import *
import urllib
from selenium import webdriver
        
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
        malos=SetQuotes(self.mem)
            
        for q in self.arr:
            if q.can_be_saved():#Debe hacerse en automaticos
                ibm=q.save()
                if ibm==1:
                    insertados.append(q)
                elif ibm==2:
                    modificados.append(q)
                elif ibm==3:
                    ignored.append(q)
            else:
                malos.append(q)
                
        print ("{} SetMyquotes.save".format(len(self.arr)), insertados.length(), ignored.length(), modificados.length(), malos.length())
        return (insertados, ignored, modificados, malos)
             
             
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
            tabla.item(rownumber, 1).setIcon(a.product.stockexchange.country.qicon())
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
        self.products=SetProducts(self.mem)
        self.quotes=SetQuotes(self.mem)#Quotes without valida
        self.errors=[]#Array the strings
        self.finished=False#Switch to mark when the run process in finished
        self.ignored=SetQuotes(self.mem)
        self.modified=SetQuotes(self.mem)
        self.inserted=SetQuotes(self.mem)
        self.bad=SetQuotes(self.mem)
        self.finished=False
        self.step=0#step of the source run. maximal is in steps()
        self.stopping=False
        
    def log(self, error):
        self.errors.append("{} {}".format(datetime.datetime.now(), error))
        
    def next_step(self):
        self.step=self.step+1
        self.emit(SIGNAL("step_finished"))  

            


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
        
        (self.inserted, self.ignored, self.modified, self.bad)=self.quotes.save()
        #El commit se hace dentro porque hay veces hay muchas
        print("{} finished. {} inserted, {} ignored, {} modified and {} bad. Total quotes {}".format(self.__class__.__name__, self.inserted.length(), self.ignored.length(), self.modified.length(), self.bad.length(), self.quotes.length()))
            
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
        
    def steps(self):
        """Define  the number of steps of the source run"""
        pass

        
class SourceParsePage(Source):
    def __init__(self, mem, sql ):
        Source.__init__(self, mem)

        self.url="urlempty"
        self.sql=sql
        
    def run(self):
        self.products.load_from_db(self.sql)     
        self.next_step()
        
        QObject.connect(self, SIGNAL("load_page"), self.on_load_page)   
        self.emit(SIGNAL("load_page"))
        self.next_step()
        
        QObject.connect(self, SIGNAL("parse_page"), self.on_parse_page)      
        self.emit(SIGNAL("parse_page")) 
        self.next_step()
 
        self.quotes_save()
        self.mem.con.commit()
        self.next_step()
        
        self.finished=True
        self.emit(SIGNAL("run_finished"))
        self.next_step()
        
        
    def steps(self):
        """Define  the number of steps of the source run"""
        return 5

    def on_load_page(self):
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
        self.type=type#0 silent in xulpymoney, 1 console
        self.sql=sql
        QObject.connect(self, SIGNAL("execute_product(int)"), self.on_execute_product)       

        
    def steps(self):
        """Define  the number of steps of the source run"""
        return self.products.length()+3
        
    def run(self):
        self.products.load_from_db(self.sql)
        self.next_step()
 

        self.products_iterate()
        
        self.quotes_save()
        self.mem.con.commit()
        self.next_step()
        
        self.finished=True
        self.emit(SIGNAL("run_finished"))
        self.next_step()
        
        
        

    def on_execute_product(self, id_product):
        """This is the function to override. In the overrided function I must add Quotes with self.quotes.append. Will be saved later"""
        pass

    def products_iterate(self):
        """Makes iteration. When its cancelled clears self.quotes.arr"""
        for i,  product in enumerate(self.products.arr): 
            if self.type==1:
                stri="{0}: {1}/{2} {3}. Appended: {4}            ".format(self.__class__.__name__, i+1, self.products.length(), product, self.quotes.length()) 
                sys.stdout.write("\b"*1000+stri)
                sys.stdout.flush()
            if self.stopping==True:
                print ("Stopping")
                self.quotes.clear()
                break
            self.emit(SIGNAL("execute_product(int)"), product.id)
            self.next_step()
            time.sleep(self.sleep)#time step
        print("")


class WorkerMercadoContinuo(SourceParsePage):
    def __init__(self,  mem, sql):
        SourceParsePage.__init__(self, mem, sql)   
        
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
                        quote=Quote(self.mem).init__create(product, datime, quote)
#                        print(quote)
                        self.quotes.append(quote)#closes
                    else:
                        self.log("El ticker {} no ha sido encontrado".format(ticker))
                if line.find('</html')!=-1:
                    break
#            except:
#                self.log("El ticker {} no ha sido formateado correctamente".format(ticker))


class WorkerMorningstar(SourceIterateProducts):
    """Clase que recorre las inversiones activas y busca la última  que tiene el microsecond 4. Busca en internet los historicals a partir de esa fecha"""
    def __init__(self, mem, type, sql,  sleep=0):
        SourceIterateProducts.__init__(self, mem,sql, type, sleep)    
        
    def on_execute_product(self,  id_product):
        """inico y fin son dos dates entre los que conseguir los datos."""
        product=self.products.find(id_product)

        #Search morningstar code
        url='http://www.morningstar.es/es/funds/SecuritySearchResults.aspx?search='+product.isin+'&type='
        web=self.load_page(url)
        if web==None:
            return
            
        for i in web.readlines(): 
            i=b2s(i)
            if i.find("searchIsin")!=-1:
                urlmorningstar=i.split('href="')[1].split('">')[0]
                url2='http://www.morningstar.es'+urlmorningstar        
                web2=self.load_page(url2)
                if web2==None:
                    return
                for l in web2.readlines():
                    l=b2s(l)
                    if l.find("Estadística Rápida")!=-1:
                        datestr=l.split("<br />")[1].split("</span")[0]
                        datarr=datestr.split("/")
                        date=datetime.date(int(datarr[2]), int(datarr[1]), int(datarr[0]))
                        dat=dt(date, product.stockexchange.closes, product.stockexchange.zone)
                        value=Decimal(self.comaporpunto(l.split('line text">')[1].split("</td")[0].split("\xa0")[1]))
                        self.quotes.append(Quote(self.mem).init__create(product, dat, value))
                        return
        self.log("Error parsing: {}".format(product.name))
            

class WorkerSGWarrants(SourceParsePage):
    """Clase que recorre las inversiones activas y calcula según este la prioridad de la previsión"""
    def __init__(self, mem):
        SourceParsePage.__init__(self, mem, 'select * from products where type=5;')
        
        
    def on_load_page(self):
        """Overrided this function because web needs to create a session"""
        #driver = webdriver.HtmlUnitDriver()
        profile = webdriver.FirefoxProfile()
        profile.native_events_enabled = True
        driver = webdriver.Firefox(profile)
#        driver = webdriver.Remote(desired_capabilities=webdriver.DesiredCapabilities.HTMLUNIT)
        driver.get('https://es.warrants.com')
        print (driver.title)
        form=driver.find_element_by_id('id3e9b')
        form.click()
        print(driver.get_page_source())
        driver.quit()
        sys.exit()

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
    def __init__(self, mem, type, sql,  sleep=0):
        SourceIterateProducts.__init__(self, mem,sql, type, sleep)
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

