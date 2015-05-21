from libxulpymoney import *
import urllib
import time
from PyQt5.QtWebKitWidgets import *

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from Ui_wdgSource import *
#from libsources import *
from myqtablewidget import *

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
        wdgSource.setSource(self.mem, s) #Links wdg with source
        s.run_finished.connect(self.checkFinished)

        
    def append_runners(self, s):
        self.runners.append(s)
            
    def remove_finished(self):
        """Remove finished wdgSource from self.runners, iterating self.arr"""
        for s in self.arr:
            if s.isFinished():
                self.runners.remove(s)

    def allFinished(self):
        for s in self.runners:
            if s.isFinished()==False:
                return False
        return True
        
    def checkFinished(self):
        if self.allFinished():
            self.runner_finished.emit()
            
        
    def length(self):
        return len(self.arr)
        
    def length_runners(self):
        return len(self.runners)
    

class wdgSource(QWidget, Ui_wdgSource):
    started=pyqtSignal()
    finished=pyqtSignal()
    def __init__(self, parent = None, name = None):
        QWidget.__init__(self,  parent)
        self.setupUi(self)
        self.mem=None
        self.source=None
        self.parent=parent
        self.status=0# O Sin empezar, 1 Prepared, only needs to cmdRun, 2 Started, 3 Finished
        self.steps=None#Define the steps of the self.progress bar
        self.widgettoupdate=self.parent.parent
        
        
    def setSource(self, mem, source):
        self.mem=mem
        self.source=source
        self.grp.setTitle(self.source.name())
                
    def isFinished(self):
        if self.status==3:
            return True
        return False
            
    def strUserOnly(self,  withindex=False):
        """Returns a sql string if products must be filtered by user invesments"""
        if self.chkUserOnly.isChecked():
            if withindex==False:
                return " and id in (select distinct(products_id) from inversiones) "
            else:
                return " and (id in (select distinct(products_id) from inversiones) or id in (select distinct (id) from products where type=3))"
        return ""

        
    def prepare(self):
        """Not running yet, but preparing GUI"""
        self.status=1
        self.cmdRun.setEnabled(False)     
        self.chkUserOnly.setEnabled(False)


    def setWidgetToUpdate(self, widget):
        """Used to update when runing, by default is parent parent"""
        self.widgettoupdate=widget
        
    def progress_step(self,  last=False):
        """Define max steps y value. 
        If last=True puts the value to the max"""
        if self.class_sources==Sources.WorkerYahoo:
            self.progress.setMaximum(len(self.agrupation)*self.agrupation[0].steps())
        elif self.class_sources==Sources.WorkerYahooHistorical:
            self.progress.setMaximum(self.agrupation[0].steps())
        elif self.class_sources==Sources.WorkerMercadoContinuo:      
            self.progress.setMaximum(self.agrupation[0].steps())
        elif self.class_sources==Sources.WorkerMorningstar:
            self.progress.setMaximum(self.agrupation[0].steps())
            
        if last==True:
            self.progress.setValue(self.progress.maximum())
        else:
            self.progress.setValue(self.progress.value()+1)
        self.widgettoupdate.update()
        QCoreApplication.processEvents() 

    def on_cmdRun_released(self):
        """Without multiprocess due to needs one independent connection per thread"""

#        self.agrupation=[]#used to iterate workers 
#        self.totals=Source(self.mem)# Used to show totals of agrupation
#        self.products=SetProducts(self.mem)#Total of products of an Agrupation
#        if self.class_sources==Sources.WorkerYahoo:
#            cur=self.mem.con.cursor()
#            cur.execute("select count(*) from products where priority[1]=1 and obsolete=false {}".format(self.strUserOnly(True)))
#            num=cur.fetchone()[0]
#            step=150
#            for i in range (0, int(num/step)+1):
#                self.worker=WorkerYahoo(self.mem, "select * from products where priority[1]=1 and obsolete=false {} order by name limit {} offset {};".format(self.strUserOnly(True), step, step*i))
#                self.agrupation.append(self.worker)
#            cur.close()           
#        elif self.class_sources==Sources.WorkerYahooHistorical:
#            self.worker=WorkerYahooHistorical(self.mem, 0, "select * from products where priorityhistorical[1]=3 and obsolete=false {} order by name".format(self.strUserOnly(True)))
#            self.agrupation.append(self.worker)
#        elif self.class_sources==Sources.WorkerMercadoContinuo:                
#            self.worker=WorkerMercadoContinuo(self.mem, "select * from products where 9=any(priority) and obsolete=false {} order by name".format(self.strUserOnly()))
#            self.agrupation.append(self.worker)
#        elif self.class_sources==Sources.WorkerMorningstar:
#            self.worker=WorkerMorningstar(self.mem, 0,  "select * from products where priorityhistorical[1]=8 and obsolete=false {} order by name;".format(self.strUserOnly()))
#            self.agrupation.append(self.worker)
##        self.currentWorker=self.agrupation[0]# Current worker working

#        #Make connections
#        for worker in self.agrupation:
#            worker.step_finished.connect(self.progress_step)
#            worker.run_finished.connect(self.worker_run_finished)
        
        #Starts
        self.status=2
        self.started.emit()
        self.source.run()
#        for worker in self.agrupation:
#            self.currentWorker=worker
#            worker.run()
            
            
    def worker_run_finished(self):
        for worker in self.agrupation:
            if worker.finished==False:
                return
        #Si pasa es que todos han acab ado
        for worker in self.agrupation:
            self.products=self.products.union(worker.products, self.mem )
            worker.inserted.addTo(self.totals.inserted)
            worker.modified.addTo(self.totals.modified)
            worker.ignored.addTo(self.totals.ignored)
            worker.bad.addTo(self.totals.bad)
            worker.quotes.addTo(self.totals.quotes)
            self.totals.errors=worker.errors+self.totals.errors
            QCoreApplication.processEvents()
            self.update()
            if worker.stopping==True:
                self.progress_step(True)
                break
        
        self.cmdInserted.setText(self.tr("{} Inserted").format(self.totals.inserted.length()))
        self.cmdEdited.setText(self.tr("{} Edited").format(self.totals.modified.length()))
        self.cmdIgnored.setText(self.tr("{} Ignored").format(self.totals.ignored.length()))
        self.cmdErrors.setText(self.tr("{} errors parsing the source").format(len(self.totals.errors)))
        self.cmdBad.setText(self.tr("{} bad").format(self.totals.bad.length()))
        self.cmdSearched.setText(self.tr("{} products".format(self.products.length())))
        self.cmdInserted.setEnabled(True)
        self.cmdIgnored.setEnabled(True)
        self.cmdEdited.setEnabled(True)
        self.cmdErrors.setEnabled(True)
        self.cmdBad.setEnabled(True)       
        self.cmdSearched.setEnabled(True)
        self.cmdCancel.setEnabled(False)
        self.status=3
        self.finished.emit()
        
        
    def on_cmdCancel_released(self):
        self.cmdCancel.setEnabled(False)
        self.currentWorker.stopping=True
        self.currentWorker=None# Current worker working

    def on_cmdInserted_released(self):
        d=QDialog(self)        
        d.showMaximized()
        d.setWindowTitle(self.tr("Inserted quotes"))
        t=myQTableWidget(d)
        self.totals.inserted.myqtablewidget(t, "wdgSource")
        lay = QVBoxLayout(d)
        lay.addWidget(t)
        d.show()
        
    def on_cmdEdited_released(self):
        d=QDialog(self)        
        d.showMaximized()
        d.setWindowTitle(self.tr("Edited quotes"))
        t=myQTableWidget(d)
        self.totals.modified.myqtablewidget(t, "wdgSource")
        lay = QVBoxLayout(d)
        lay.addWidget(t)
        d.show()
        
    def on_cmdIgnored_released(self):
        d=QDialog(self)        
        d.showMaximized()
        d.setWindowTitle(self.tr("Ignored quotes"))
        t=myQTableWidget(d)
        self.totals.ignored.myqtablewidget(t, "wdgSource")
        lay = QVBoxLayout(d)
        lay.addWidget(t)
        d.show()
        
    def on_cmdErrors_released(self):
        d=QDialog(self)        
        d.showMaximized()
        d.setWindowTitle(self.tr("Error procesing the source"))
        terrors=myQTableWidget(d)
        self.totals.myqtablewidget_errors(terrors, "wdgSource")
        lay = QVBoxLayout(d)
        lay.addWidget(terrors)
        d.show()

    def on_cmdBad_released(self):
        d=QDialog(self)        
        d.showMaximized()
        d.setWindowTitle(self.tr("Error procesing the source"))
        t=myQTableWidget(d)
        self.totals.bad.myqtablewidget(t, "wdgSource")
        lay = QVBoxLayout(d)
        lay.addWidget(t)
        d.show()
        
    def on_cmdSearched_released(self):
        d=QDialog(self)        
        d.showMaximized()
        d.setWindowTitle(self.tr("Error procesing the source"))
        t=myQTableWidget(d)
        self.products.myqtablewidget(t, "wdgSource")
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
    step_finished=pyqtSignal()
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
        self.finished=False
        self.step=0#step of the source run. maximal is in steps()
        self.stopping=False
        self.ui=None#This must be linked to a wdgSource with setWdgSource
        self.agrupation=[]#Used if it must bu run several times due to large amounts (Yahoo)
        self.sql=None
        
    def setSQL(self, sql):
        """Establish sql"""
        
    def setWdgSource(self, widget):
        self.ui=widget
        
    def setName(self, name):
        self._name=name
        
    def name(self):
        return self._name
        
    def log(self, error):
        self.errors.append("{} {}".format(datetime.datetime.now(), error))
        
    def next_step(self):
        self.step=self.step+1
        self.step_finished.emit()

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
        
    def steps(self):
        """Define  the number of steps of the source run"""
        pass

        
class SourceParsePage(Source):
    loaded_page=pyqtSignal()
    parse_page=pyqtSignal()
    run_finished=pyqtSignal()
    def __init__(self, mem,  ):
        Source.__init__(self, mem)

        self.url="urlempty"
        
    def run(self):  
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
        
        self.finished=True
        self.run_finished.emit()
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
    execute_product=pyqtSignal(int)
    run_finished=pyqtSignal()
    def __init__(self, mem,  type=2, sleep=0):
        Source.__init__(self, mem)
        self.sleep=sleep#wait between products
        self.type=type#0 silent in xulpymoney, 1 console
        self.execute_product.connect(self.on_execute_product) 

        
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
        self.run_finished.emit()
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
            
            self.finished=True
            print ("run_finished")
            self.run_finished.emit()
            self.next_step()



    def steps(self):
        """Define  the number of steps of the source run"""
        return 4

    def run(self):
        self.products.load_from_db(self.sql)     
        self.next_step()
        self.webView.load(QUrl("http://www.bolsamadrid.es/esp/aspx/Mercados/Precios.aspx?mercado=MC"))            

        
        
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

class WorkerYahoo(SourceParsePage):
    """Clase que recorre las inversiones activas y calcula según este la prioridad de la previsión"""
    def __init__(self, mem):
        SourceParsePage.__init__(self, mem)
        self.setName(self.tr("Yahoo source"))

    def sum_tickers(self):
        s=""
        for p in self.products.arr:
            if p.ticker==None:
                continue
            if p.ticker=="":
                continue
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
                
    def run(self):
        self.agrupation=[]#used to iterate workers 
        self.totals=Source(self.mem)# Used to show totals of agrupation
        self.products=SetProducts(self.mem)#Total of products of an Agrupation
        if self.class_sources==Sources.WorkerYahoo:
            cur=self.mem.con.cursor()
            cur.execute("select count(*) from products where priority[1]=1 and obsolete=false {}".format(self.strUserOnly(True)))
            num=cur.fetchone()[0]
            step=150
            for i in range (0, int(num/step)+1):
                self.worker=WorkerYahoo(self.mem, "select * from products where priority[1]=1 and obsolete=false {} order by name limit {} offset {};".format(self.strUserOnly(True), step, step*i))
                self.agrupation.append(self.worker)
            cur.close()           


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

