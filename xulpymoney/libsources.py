from libxulpymoney import *
import urllib
import time
from PyQt5.QtWebKitWidgets import *

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from Ui_wdgSource import *
#from libsources import *
from myqtablewidget import *

class SourceStatus:
    Loaded=0 #Means Source object has been ccreated
    Prepared=1 # Has been comunicated sql and prepared ui, if there
    Running=2 #Fetching page and processing
    Finished=3 # Finished

class Sources:
    WorkerYahoo=1
    WorkerYahooHistorical=2
    WorkerMercadoContinuo=3
    WorkerMorningstar=4

class SetSources(QObject):
    """Set of wdgSources"""
    runs_finished=pyqtSignal()
    def __init__(self, mem):
        QObject.__init__(self)
        self.mem=mem
        self.arr=[]
        self.runners=[]#Array of selected to run

    def append(self, Worker, wdgSource=None):
        """Add a source especifing class, sql and wdgSource el widget"""
        if Worker==WorkerYahooHistorical:
            s=WorkerYahooHistorical(self.mem, 0)
        elif Worker==WorkerYahoo:
            s=WorkerYahoo(self.mem)
        elif Worker==WorkerMercadoContinuo:
            s=WorkerMercadoContinuo(self.mem)
        elif Worker==WorkerMorningstar:
            s=WorkerMorningstar(self, 0)
        self.arr.append(s)
        s.setWdgSource(wdgSource) #Links source with wdg

        
    def append_runners(self, s):
        self.runners.append(s)
            
    def remove_finished(self):
        """Remove finished wdgSource from self.runners, iterating self.arr"""
        for s in self.arr:
            if s.isFinished():
                self.runners.remove(s)

    def allFinished(self):
        for s in self.runners:
            if s.getStatus()!=SourceStatus.Finished:
                return False
        return True
        
    def checkFinished(self):
        if self.allFinished():
            self.runs_finished.emit()
            
        
    def length(self):
        return len(self.arr)
        
    def length_runners(self):
        return len(self.runners)
    

class wdgSource(QWidget, Ui_wdgSource):
    def __init__(self, parent = None, name = None):
        QWidget.__init__(self,  parent)
        self.setupUi(self)
        self.mem=None
        self.source=None
        self.parent=parent
        self.widgettoupdate=self.parent.parent
        
        
    def setSource(self, mem, source):
        self.mem=mem
        self.source=source
        self.grp.setTitle(self.source.name())
        self.source.stepFinished.connect(self.on_stepFinished)
        self.source.statusChanged.connect(self.on_statusChanged)

    def on_statusChanged(self, status):
        """Not running yet, but preparing GUI"""
        
        print("wdgSource statusChanged", status)
        if status==SourceStatus.Prepared:
            self.cmdRun.setEnabled(False)     
            self.chkUserOnly.setEnabled(False)
            self.progress.setMaximum(self.source.steps())
        elif status==SourceStatus.Running:
            pass
        elif status==SourceStatus.Finished:
            self.cmdInserted.setText(self.tr("{} Inserted").format(self.source.inserted.length()))
            self.cmdEdited.setText(self.tr("{} Edited").format(self.source.modified.length()))
            self.cmdIgnored.setText(self.tr("{} Ignored").format(self.source.ignored.length()))
            self.cmdErrors.setText(self.tr("{} errors parsing the source").format(len(self.source.errors)))
            self.cmdBad.setText(self.tr("{} bad").format(self.source.bad.length()))
            self.cmdSearched.setText(self.tr("{} products".format(self.source.products.length())))
            self.cmdInserted.setEnabled(True)
            self.cmdIgnored.setEnabled(True)
            self.cmdEdited.setEnabled(True)
            self.cmdErrors.setEnabled(True)
            self.cmdBad.setEnabled(True)       
            self.cmdSearched.setEnabled(True)
            self.cmdCancel.setEnabled(False)

    def setWidgetToUpdate(self, widget):
        """Used to update when runing, by default is parent parent"""
        self.widgettoupdate=widget
        
    def on_stepFinished(self):
        """Update progress bar"""
        self.progress.setValue(self.source.step)
        QCoreApplication.processEvents() 

    def on_cmdRun_released(self):
        """Without multiprocess due to needs one independent connection per thread"""
        if self.source.getStatus()==SourceStatus.Loaded:#Cmd directly in wdgSource
            self.source.setSQL(self.chkUserOnly.isChecked())
        self.source.run()

    def on_cmdCancel_released(self):
        self.cmdCancel.setEnabled(False)
        self.currentWorker.stopping=True
        self.currentWorker=None# Current worker working

    def on_cmdInserted_released(self):
        d=QDialog(self)     
        d.resize(800, 600)
        #d.showMaximized()
        d.setWindowTitle(self.tr("Inserted quotes from {}").format(self.source.name()))
        t=myQTableWidget(d)
        self.source.inserted.myqtablewidget(t, "wdgSource")
        lay = QVBoxLayout(d)
        lay.addWidget(t)
        d.show()
        
    def on_cmdEdited_released(self):
        d=QDialog(self)        
        d.resize(800, 600)
        d.setWindowTitle(self.tr("Edited quotes from {}").format(self.source.name()))
        t=myQTableWidget(d)
        self.source.modified.myqtablewidget(t, "wdgSource")
        lay = QVBoxLayout(d)
        lay.addWidget(t)
        d.show()
        
    def on_cmdIgnored_released(self):
        d=QDialog(self)        
        d.resize(800, 600)
        d.setWindowTitle(self.tr("Ignored quotes from {}").format(self.source.name()))
        t=myQTableWidget(d)
        self.source.ignored.myqtablewidget(t, "wdgSource")
        lay = QVBoxLayout(d)
        lay.addWidget(t)
        d.show()
        
    def on_cmdErrors_released(self):
        d=QDialog(self)        
        d.resize(800, 600)
        d.setWindowTitle(self.tr("Errors procesing the source {}").format(self.source.name()))
        terrors=myQTableWidget(d)
        self.source.myqtablewidget_errors(terrors, "wdgSource")
        lay = QVBoxLayout(d)
        lay.addWidget(terrors)
        d.show()

    def on_cmdBad_released(self):
        d=QDialog(self)        
        d.resize(800, 600)
        d.setWindowTitle(self.tr("Bad prices procesing the source {}").format(self.source.name()))
        t=myQTableWidget(d)
        self.source.bad.myqtablewidget(t, "wdgSource")
        lay = QVBoxLayout(d)
        lay.addWidget(t)
        d.show()
        
    def on_cmdSearched_released(self):
        d=QDialog(self)        
        d.resize(800, 600)
        d.setWindowTitle(self.tr("Searched products from {}").format(self.source.name()))
        t=myQTableWidget(d)
        self.source.products.myqtablewidget(t, "wdgSource")
        lay = QVBoxLayout(d)
        lay.addWidget(t)
        d.show()

class Source(QObject):
    """Clase nueva para todas las sources
    Debera:
    - load_products
    - fech_page
    - parse_page
    - check_quotes"""
    stepFinished=pyqtSignal()
    statusChanged=pyqtSignal(int)
    finished=pyqtSignal()
    def __init__(self, mem):
        QObject.__init__(self)
        self.mem=mem
        self._name=self.tr("Source Name unknown")
        self.products=SetProducts(self.mem)
        self.quotes=SetQuotes(self.mem)#Quotes without valida
        self.errors=[]#Array the strings
        self.finished=False#Switch to mark when the run process in finished
        self.ignored=SetQuotes(self.mem)
        self.modified=SetQuotes(self.mem)
        self.inserted=SetQuotes(self.mem)
        self.bad=SetQuotes(self.mem)
        self._status=None
        self.setStatus(SourceStatus.Loaded)
        self.step=0#step of the source run. maximal is in steps()
        self.stopping=False
        self.ui=None#This must be linked to a wdgSource with setWdgSource
        self.agrupation=[]#Used if it must bu run several times due to large amounts (Yahoo)
        self.sql=None
        
    def setStatus(self, status):
        print ("{}: setStatus {}".format(self.name(), self.getStatus()))
        self._status=status
        self.statusChanged.emit(status)
        
    def getStatus(self):
        return self._status
        
    def setWdgSource(self, widget):
        self.ui=widget
        widget.setSource(self.mem, self) #Links wdg with source
        
    def setName(self, name):
        self._name=name
        
    def name(self):
        return self._name
        
    def log(self, error):
        self.errors.append("{} {}".format(datetime.datetime.now(), error))
        
    def next_step(self):
        self.step=self.step+1
        self.stepFinished.emit()

    def myqtablewidget_errors(self, tabla, section):
        tabla.setColumnCount(2)
        tabla.setHorizontalHeaderItem(0, QTableWidgetItem(QApplication.translate(section, "Date and time" )))
        tabla.setHorizontalHeaderItem(1, QTableWidgetItem(QApplication.translate(section, "Log" )))
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
        
        
    def setSQL(self, useronly):
        print ("This function must be overrided in Worker")
        
    def steps(self):
        """Define  the number of steps of the source run"""
        print ("This function must be overrided in Worker")

        
class SourceParsePage(Source):
    loaded_page=pyqtSignal()
    parse_page=pyqtSignal()
    def __init__(self, mem,  ):
        Source.__init__(self, mem)

        self.url="urlempty"
        
    def run(self):  
        self.setStatus(SourceStatus.Running)
        self.products.load_from_db(self.sql)     
        self.next_step()
        self.loaded_page.connect(self.on_load_page)
        self.loaded_page.emit()
        self.next_step()
        
        self.parse_page.connect(self.on_parse_page)
        self.parse_page.emit()
        self.next_step()
 
        self.quotes_save()
        self.mem.con.commit()
        self.next_step()
        
        self.setStatus(SourceStatus.Finished)
        
        
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
    execute_product=pyqtSignal(int)
    def __init__(self, mem,  type=2, sleep=0):
        Source.__init__(self, mem)
        self.sleep=sleep#wait between products
        self.type=type#0 silent in xulpymoney, 1 console
        self.execute_product.connect(self.on_execute_product) 

        
    def steps(self):
        """Define  the number of steps of the source run"""
        return self.products.length()+3
        
    def run(self):
        self.setStatus(SourceStatus.Running)
        self.products.load_from_db(self.sql)
        self.next_step()
 
        self.products_iterate()
        
        self.quotes_save()
        self.mem.con.commit()
        self.next_step()
        
        self.setStatus(SourceStatus.Finished)
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
            self.execute_product.emit(product.id)
#            self.emit(SIGNAL("execute_product(int)"), product.id)
            self.next_step()
            time.sleep(self.sleep)#time step
        print("")


class WorkerMercadoContinuo(SourceParsePage):
    def __init__(self,  mem):
        SourceParsePage.__init__(self, mem)   
        self.setName(self.tr("Mercado Continuo source"))
        self.webView= QWebView()
        self.webView.loadFinished.connect(self.on_load_page)
        
    def on_load_page(self):
        self.frame = self.webView.page().mainFrame()      
        print (self.webView.page().bytesReceived())  
        self.frame.evaluateJavaScript("__doPostBack('ctl00$Contenido$Todos','')")
        if self.frame.toHtml().find("Completo")==-1:
            self.web=self.frame.toHtml().split("\n")
            for l in self.web:
                if l.find("ISIN=")!=-1:
                    isin=l.split("ISIN=")[1].split('">')[0]
                    p=self.products.find_by_isin(isin)
                    if p!=None:
                        arrdate=l.split('<td align="center">')[1].split("</td>")[0].split("/")
                        date=datetime.date(int(arrdate[2]),  int(arrdate[1]),  int(arrdate[0]))
                        strtime=l.split('class="Ult" align="center">')[1].split("</td>")[0]
                        if strtime=="Cierre":
                            time=p.stockexchange.closes
                        else:
                            arrtime=strtime.split(":")
                            time=datetime.time(int(arrtime[0]), int(arrtime[1]))
                        quot=Decimal(self.comaporpunto(l.split("</a></td><td>")[1].split("</td><td ")[0]))
                        datime=dt(date,time,p.stockexchange.zone)
                        quote=Quote(self.mem).init__create(p, datime, quot)    
                        self.quotes.append(quote)
                    else:
                        self.log("El isin {} no ha sido encontrado".format(isin))        
                        
            self.next_step()
            self.quotes_save()
            self.mem.con.commit()
            self.next_step()
            
            self.setStatus(SourceStatus.Finished)

    def steps(self):
        """Define  the number of steps of the source run"""
        return 3

    def run(self):
        self.setStatus(SourceStatus.Running)
        self.products.load_from_db(self.sql)     
        self.next_step()
        self.webView.load(QUrl("http://www.bolsamadrid.es/esp/aspx/Mercados/Precios.aspx?mercado=MC"))            

        
    def setSQL(self, useronly):
        if useronly==True:
            self.sql="select * from products where 9=any(priority) and obsolete=false and id in (select distinct(products_id) from inversiones) order by name"
        else:
            self.sql="select * from products where 9=any(priority) and obsolete=false order by name"
        self.setStatus(SourceStatus.Prepared)

    def on_parse_page(self):
        pass


class WorkerMorningstar(SourceIterateProducts):
    """Clase que recorre las inversiones activas y busca la última  que tiene el microsecond 4. Busca en internet los historicals a partir de esa fecha"""
    def __init__(self, mem, type,   sleep=0):
        SourceIterateProducts.__init__(self, mem,type, sleep)    
        self.setName(self.tr("Morningstar source"))
        
    def on_execute_product(self,  id_product):
        """inico y fin son dos dates entre los que conseguir los datos."""
        product=self.products.find(id_product)
        
        if product.result.basic.last.datetime.date()==datetime.date.today()-datetime.timedelta(days=1):#if I already got yesterday's price return
            self.log("I already got yesterday's price: {}".format(product.name))
            return

        #Search morningstar code
        url='http://www.morningstar.es/es/funds/SecuritySearchResults.aspx?search='+product.isin+'&type='
        web=self.load_page(url)
        if web==None:
            self.log("Error downloading page")
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
        
    def setSQL(self, useronly):
        self.userinvestmentsonly=useronly
        if self.userinvestmentsonly==True:
            self.sql="select * from products where priorityhistorical[1]=8 and obsolete=false and id in (select distinct(products_id) from inversiones) order by name;"
        else:
            self.sql="select * from products where priorityhistorical[1]=8 and obsolete=false order by name;"
        self.setStatus(SourceStatus.Prepared)

    def steps(self):
        """Define  the number of steps of the source run"""
        return 4 #CORRECT
class WorkerSGWarrants(SourceParsePage):
    """Clase que recorre las inversiones activas y calcula según este la prioridad de la previsión"""
    def __init__(self, mem):
        SourceParsePage.__init__(self, mem)
        self.setName(self.tr("SG Warrants source"))
        
        
    def on_load_page(self):
        """Overrided this function because web needs to create a session"""
        #driver = webdriver.HtmlUnitDriver()
        profile = webdriver.FirefoxProfile()
        profile.native_events_enabled = True
        driver = webdriver.Firefox(profile)
#        driver = webdriver.Remote(desired_capabilities=webdriver.DesiredCapabilities.HTMLUNIT)
        driver.get('https://es.warrants.com')
        form=driver.find_element_by_id('id3e9b')
        form.click()
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
        
    def setSQL(self, useronly):
        self.userinvestmentsonly=useronly
        if self.userinvestmentsonly==True:
            self.sql="MALselect * from products where 9=any(priority) and obsolete=false and id in (select distinct(products_id) from inversiones) order by name".format(self.strUserOnly())
        else:
            self.sql="MALselect * from products where 9=any(priority) and obsolete=false order by name".format(self.strUserOnly())
        self.setStatus(SourceStatus.Prepared)

    def steps(self):
        """Define  the number of steps of the source run"""
        return 4 #CORRECT
class WorkerYahoo(SourceParsePage):
    """Clase que recorre las inversiones activas y calcula según este la prioridad de la previsión"""
    def __init__(self, mem):
        SourceParsePage.__init__(self, mem)
        self.setName(self.tr("Yahoo source"))

    def sum_tickers(self, setproducts):
        s=""
        for p in setproducts.arr:
            if p.ticker==None:
                continue
            if p.ticker=="":
                continue
            s=s+p.ticker+"+"
        return s[:-1]
                
    def setSQL(self, useronly):
        self.userinvestmentsonly=useronly
        if self.userinvestmentsonly==True:
            self.sql="select * from products where priority[1]=1 and obsolete=false and id in (select distinct(products_id) from inversiones) order by name"
        else:
            self.sql="select * from products where priority[1]=1 and obsolete=false order by name"
        self.setStatus(SourceStatus.Prepared)

    def my_load_page(self, setproducts):
        "Overrides SourceParsePage"
        self.url='http://download.finance.yahoo.com/d/quotes.csv?s=' + self.sum_tickers(setproducts) + '&f=sl1d1t1&e=.csv'

        self.web=self.load_page(self.url)
        if self.web==None:
            return
        
    def my_parse_page(self):
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
                
    def run(self):
        """OVerrides ParsePage"""
        self.setStatus(SourceStatus.Running)
        self.agrupation=[]#used to iterate sets de products 
        self.totals=Source(self.mem)# Used to show totals of agrupation
        self.products=SetProducts(self.mem)#Total of products of an Agrupation
        self.products.load_from_db(self.sql)    
        items=150
        
        print (self.products.length())
        
        print ("blocks", int(self.products.length()/items)+1 )
        
        for i in range(int(self.products.length()/items)+1) :#Creo tantos SetProducts como bloques de 150
            self.agrupation.append(SetProducts(self.mem))
            
        for i, p in enumerate(self.products.arr):
            self.agrupation[int(i/items)].append(p)#Añado en array que correspoonda el p
            
        for setproduct in self.agrupation:  
            print ("setproduct length",  setproduct.length())
            self.my_load_page(setproduct)
            self.next_step()
            self.my_parse_page()
            self.next_step()
            
        self.quotes_save()
        self.mem.con.commit()
        self.next_step()
            
        self.setStatus(SourceStatus.Finished)



    def steps(self):
        """Define  the number of steps of the source run"""
        return 4 #CORRECT

class WorkerYahooHistorical(SourceIterateProducts):
    """Clase que recorre las inversiones activas y busca la última  que tiene el microsecond 4. Busca en internet los historicals a partir de esa fecha"""
    def __init__(self, mem, type,  sleep=0):
        SourceIterateProducts.__init__(self, mem,type, sleep)
        #SourceIterateProducts.__init__(self, mem,"select * from products where id in (79329,81105)", type, sleep)
        self.setName(self.tr("Yahoo Historical source"))
        
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
        
    def setSQL(self, useronly):
        self.userinvestmentsonly=useronly
        if self.userinvestmentsonly==True:
            self.sql="select * from products where priorityhistorical[1]=3 and obsolete=false and id in (select distinct(products_id) from inversiones) order by name"
        else:
            self.sql="select * from products where priorityhistorical[1]=3 and obsolete=false order by name"
        self.setStatus(SourceStatus.Loaded)


    def steps(self):
        """Define  the number of steps of the source run"""
        return 4 #CORRECT
