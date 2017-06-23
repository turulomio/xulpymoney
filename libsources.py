import json
import logging
import os
import urllib.request
import time
import datetime
import sys
from PyQt5.QtWebEngineWidgets import QWebEnginePage
from PyQt5.QtWidgets import QWidget, QMenu, QDialog, QVBoxLayout, QTableWidgetItem, QTextEdit, QApplication
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QCoreApplication, QProcess, QUrl
from PyQt5.QtGui import QIcon
from Ui_wdgSource import Ui_wdgSource
from myqtablewidget import myQTableWidget
from libxulpymoney import Quote, SetProducts, SetQuotes, ampm_to_24, qleft, b2s, dt, dt_with_pytz, qmessagebox
from decimal import Decimal
from concurrent.futures import ThreadPoolExecutor,  as_completed

class SourceStatus:
    Loaded=0 #Means Source object has been ccreated
    Prepared=1 # Has been comunicated sql and prepared ui, if there
    Running=2 #Fetching page and processing
    Finished=3 # Finished

class Sources:
    WorkerGoogle=1
    WorkerGoogleHistorical=2
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
        if Worker==WorkerGoogleHistorical:
            s=WorkerGoogleHistorical(self.mem, 0)
        elif Worker==WorkerGoogle:
            s=WorkerGoogle(self.mem)
        elif Worker==WorkerMercadoContinuo:
            s=WorkerMercadoContinuo(self.mem)
        elif Worker==WorkerMorningstar:
            s=WorkerMorningstar(self.mem, 0)
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
        
        self.progress.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
        
        menu=QMenu()
        menu.addAction(self.actionProducts)
        menu.addSeparator()   
        menu.addAction(self.actionInserted)   
        menu.addAction(self.actionEdited)   
        menu.addAction(self.actionIgnored)   
        menu.addAction(self.actionErrors)        
        menu.addAction(self.actionWrong)
        menu.addSeparator()   
        menu.addAction(self.actionHTML)
        self.cmdDropDown.setMenu(menu)
        
        self.cmdCancel.setEnabled(False)
        
        
    def setSource(self, mem, source):
        self.mem=mem
        self.source=source
        self.grp.setTitle(self.source.getName())
        self.source.stepFinished.connect(self.on_stepFinished)
        self.source.statusChanged.connect(self.on_statusChanged)

    def on_statusChanged(self, status):
        logging.debug("wdgSource statusChanged {}".format(status))
        if status==SourceStatus.Prepared:
            self.cmdRun.setEnabled(False)     
            self.chkUserOnly.setEnabled(False)
        elif status==SourceStatus.Finished:
            self.grp.setTitle(self.grp.title()+" ({})".format(self.source.timeElapsed()))
            self.cmdCancel.setEnabled(False)
            self.cmdDropDown.setEnabled(True)       
            self.actionInserted.setText(self.tr("Inserted quotes ({})").format(self.source.inserted.length()))
            self.actionEdited.setText(self.tr("Edited quotes ({})").format(self.source.modified.length()))
            self.actionIgnored.setText(self.tr("Ignored quotes ({})").format(self.source.ignored.length()))
            self.actionErrors.setText(self.tr("Parsing errors ({})").format(len(self.source.errors)))
            self.actionWrong.setText(self.tr("Wrong quotes ({})").format(self.source.bad.length()))
            self.actionProducts.setText(self.tr("Products searched ({})".format(self.source.products.length())))

    def setWidgetToUpdate(self, widget):
        """Used to update when runing, by default is parent parent"""
        self.widgettoupdate=widget
        
    def on_stepFinished(self):
        """Update progress bar"""
        self.progress.setValue(self.source.step)
        self.progress.setMaximum(self.source.steps())
        QCoreApplication.processEvents() 

    def on_cmdRun_released(self):
        """Without multiprocess due to needs one independent connection per thread"""
        self.cmdCancel.setEnabled(True)
        self.cmdRun.setEnabled(False)
        self.chkUserOnly.setEnabled(False)
        if self.source.getStatus()==SourceStatus.Loaded:#Cmd directly in wdgSource
            self.source.setSQL(self.chkUserOnly.isChecked())
        self.source.run()



    def on_cmdCancel_released(self):
        self.cmdCancel.setEnabled(False)
        self.source.stopping=True

    @pyqtSlot() 
    def on_actionInserted_triggered(self):
        d=QDialog(self)     
        d.resize(800, 600)
        d.setWindowTitle(self.tr("Inserted quotes from {}").format(self.source.getName()))
        t=myQTableWidget(d)
        t.settings(self.mem,"wdgSource" , "tblInserted")
        self.source.inserted.myqtablewidget(t)
        lay = QVBoxLayout(d)
        lay.addWidget(t)
        d.show()
        
    @pyqtSlot() 
    def on_actionEdited_triggered(self):
        d=QDialog(self)        
        d.resize(800, 600)
        d.setWindowTitle(self.tr("Edited quotes from {}").format(self.source.getName()))
        t=myQTableWidget(d)
        t.settings(self.mem,"wdgSource" , "tblEdited")
        self.source.modified.myqtablewidget(t)
        lay = QVBoxLayout(d)
        lay.addWidget(t)
        d.show()
        
    @pyqtSlot() 
    def on_actionIgnored_triggered(self):
        d=QDialog(self)        
        d.resize(800, 600)
        d.setWindowTitle(self.tr("Ignored quotes from {}").format(self.source.getName()))
        t=myQTableWidget(d)
        t.settings(self.mem,"wdgSource" , "tblIgnored")
        self.source.ignored.myqtablewidget(t)
        lay = QVBoxLayout(d)
        lay.addWidget(t)
        d.show()
        
    @pyqtSlot() 
    def on_actionErrors_triggered(self):
        d=QDialog(self)        
        d.resize(800, 600)
        d.setWindowTitle(self.tr("Errors procesing the source {}").format(self.source.getName()))
        terrors=myQTableWidget(d)
        terrors.settings(self.mem,"wdgSource" , "tblErrors")
        self.source.myqtablewidget_errors(terrors)
        lay = QVBoxLayout(d)
        lay.addWidget(terrors)
        d.show()

    @pyqtSlot() 
    def on_actionWrong_triggered(self):
        d=QDialog(self)        
        d.resize(800, 600)
        d.setWindowTitle(self.tr("Bad prices procesing the source {}").format(self.source.getName()))
        t=myQTableWidget(d)
        t.settings(self.mem,"wdgSource" , "tblWrong")
        self.source.bad.myqtablewidget(t)
        lay = QVBoxLayout(d)
        lay.addWidget(t)
        d.show()
        
    @pyqtSlot() 
    def on_actionProducts_triggered(self):
        d=QDialog(self)        
        d.resize(800, 600)
        d.setWindowTitle(self.tr("Searched products from {}").format(self.source.getName()))
        t=myQTableWidget(d)
        t.settings(self.mem,"wdgSource" , "tblProducts")
        self.source.products.myqtablewidget(t)
        lay = QVBoxLayout(d)
        lay.addWidget(t)
        d.show()        
    @pyqtSlot() 
    def on_actionHTML_triggered(self):
        if os.path.exists("/usr/bin/kwrite"):
            file="/tmp/xulpymoney-weblog-{}.txt".format(self.source.getName())
            f=open(file, "w")
            f.write(self.source.weblog)
            f.close()
            QProcess.startDetached("kwrite", [file,  ] )
        else:
            d=QDialog(self)        
            d.resize(800, 600)
            d.setWindowTitle(self.tr("Showing HTML").format(self.source.getName()))
            t=QTextEdit(d)
            t.setText(self.source.weblog)
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
        self.weblog=""#Stores all web downloads, to show later in ui to debug
        self._runningtime=None
        self._finishedtime=None
        
    def setStatus(self, status):
#        print ("{}: setStatus {}".format(self.getName(), self.getStatus()))
        if status==SourceStatus.Running:
            self._runningtime=datetime.datetime.now()
        if status==SourceStatus.Finished:
            self._finishedtime=datetime.datetime.now()
        self._status=status
        self.statusChanged.emit(status)
        
    def timeElapsed(self):
        """Tiempo transcurrido"""
        return self._finishedtime-self._runningtime
    
    def getStatus(self):
        return self._status
        
    def setWdgSource(self, widget):
        self.ui=widget
        widget.setSource(self.mem, self) #Links wdg with source
        
    def setName(self, name):
        self._name=name
        
    def getName(self):
        return self._name
        
    def log(self, error):
        self.errors.append("{} {}".format(datetime.datetime.now(), error))
        
    def next_step(self):
        self.step=self.step+1
        self.stepFinished.emit()

    def myqtablewidget_errors(self, tabla):
        tabla.setColumnCount(2)
        tabla.setHorizontalHeaderItem(0, QTableWidgetItem(QApplication.translate("Core", "Date and time" )))
        tabla.setHorizontalHeaderItem(1, QTableWidgetItem(QApplication.translate("Core", "Log" )))
        tabla.clearContents()
        tabla.applySettings()
        tabla.setRowCount(len(self.errors))
        for rownumber, line in enumerate(self.errors):
            a=line.split(" ")
            strdate="{} {}".format(a[0], a[1])
            tabla.setItem(rownumber, 0, qleft(strdate))
            tabla.setItem(rownumber, 1, qleft(line[len(strdate)+1:]))
            
    def toWebLog(self,  object):
        self.weblog=self.weblog +"\n\n\n###### FETCHED AT {} #######\n\n\n".format(datetime.datetime.now())
#        print ("toWebLog", object.__class__.__name__)
        if object.__class__.__name__=='HTTPResponse':
            for line in object.readlines():
                self.weblog=self.weblog+b2s(line)
        elif object.__class__.__name__=='list':
            for line in object:
                self.weblog=self.weblog+line +"\n"
        else:
            self.weblog=self.weblog+str(object)+"\n"

    def quotes_save(self):
        """Saves all quotes after product iteration. If I want to do something different. I must override this function"""
        
        (self.inserted, self.ignored, self.modified, self.bad)=self.quotes.save()
        #El commit se hace dentro porque hay veces hay muchas
        logging.info("{} finished. {} inserted, {} ignored, {} modified and {} bad. Total quotes {}".format(self.__class__.__name__, self.inserted.length(), self.ignored.length(), self.modified.length(), self.bad.length(), self.quotes.length()))
            
    def errors_show(self):
        """Shwo errors aappended with log"""
        if len(self.errors)>0:
            logging.warning ("{} Errors in {}:".format(len(self.errors), self.__class__.__name__))
            for e in self.errors:
                logging.warning ("  + {}".format(e))
        
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
        logging.info ("This function must be overrided in Worker")
        
    def steps(self):
        """Define  the number of steps of the source run"""
        logging.info ("This function must be overrided in Worker")

        
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
        
        
        
#
#    def on_execute_product(self, id_product):
#        """This is the function to override. In the overrided function I must add Quotes with self.quotes.append. Will be saved later"""
#        pass

    def products_iterate(self):
        """Makes iteration. When its cancelled clears self.quotes.arr"""
        for i,  product in enumerate(self.products.arr): 
            if self.type==1:
                stri="{0}: {1}/{2} {3}. Appended: {4}            ".format(self.__class__.__name__, i+1, self.products.length(), product, self.quotes.length()) 
                sys.stdout.write("\b"*1000+stri)
                sys.stdout.flush()
            if self.stopping==True:
                logging.debug ("Stopping")
                self.quotes.clear()
                break
            self.execute_product.emit(product.id)
            self.next_step()
            time.sleep(self.sleep)#time step
        print("")

    
class WorkerMercadoContinuo(Source):
    def __init__(self,  mem):
        SourceParsePage.__init__(self, mem)   
        self.setName(self.tr("Mercado Continuo source"))
        
    @pyqtSlot(str)
    def callbackHTML(self, html):       
        self.numpage=self.numpage+1
        if self.numpage==1:
            self.page.runJavaScript("__doPostBack('ctl00$Contenido$Todos','')")
        elif self.numpage==2:
            self.processCompleto(html)
#        logging.debug("Callback {}".format(self.numpage))
        
    def run(self):
        self.setStatus(SourceStatus.Running)
        self.products.load_from_db(self.sql)     
        self.next_step()
        self.numpage=0
        self.page=QWebEnginePage()
        self.page.loadFinished.connect(self.on_load_page)
        self.page.load(QUrl("http://www.bolsamadrid.es/esp/aspx/Mercados/Precios.aspx?mercado=MC"))#asincronou

    def on_load_page(self):
        """
            Se ejecuta después de cargar la url y despues de ejecutar el Javascript
        """
        logging.debug("Page loaded")
        self.page.toHtml(self.callbackHTML)
    
    @pyqtSlot(str)
    def processCompleto(self, html):
        logging.debug("Processing completo")
        self.toWebLog(html)
        for l in html.split("\n"):
            if l.find("ISIN=")!=-1:
#                logging.debug(l)
                isin=l.split("ISIN=")[1].split('">')[0]
                p=self.products.find_by_isin(isin)
                if p!=None:
                    arrdate=l.split('<td align="center">')[1].split("</td>")[0].split("/")
                    date=datetime.date(int(arrdate[2]),  int(arrdate[1]),  int(arrdate[0]))
                    strtime=l.split('class="Ult" align="center">')[1].split("</td>")[0]
                    if strtime=="Cierre":
                        time=p.stockmarket.closes
                    else:
                        arrtime=strtime.split(":")
                        time=datetime.time(int(arrtime[0]), int(arrtime[1]))
                    quot=Decimal(self.comaporpunto(l.split("</a></td><td>")[1].split("</td><td ")[0]))
                    datime=dt(date,time,p.stockmarket.zone)
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

    def setSQL(self, useronly):
        if useronly==True:
            self.sql="select * from products where 9=any(priority) and obsolete=false and id in (select distinct(products_id) from inversiones) order by name"
        else:
            self.sql="select * from products where 9=any(priority) and obsolete=false order by name"
        self.setStatus(SourceStatus.Prepared)


class WorkerMorningstar(Source):
    """Clase que recorre las inversiones activas y busca la última  que tiene el microsecond 4. Busca en internet los historicals a partir de esa fecha"""
    def __init__(self, mem, type,   sleep=0):
        Source.__init__(self, mem)
        self.type=type
        self.sleep=sleep
        self.setName(self.tr("Morningstar source"))
#        self.lock=multiprocessing.Lock()
        
    def on_execute_product(self,  product):
        quotes=[]
        if product.result.basic.last.datetime.date()==datetime.date.today()-datetime.timedelta(days=1):#if I already got yesterday's price return
            self.log("I already got yesterday's price: {}".format(product.name))
            return quotes

        web2=self.load_page('http://www.morningstar.es/es/funds/snapshot/snapshot.aspx?id='+product.ticker)
        if web2==None:
            return quotes

        for l in web2.readlines():
            self.mem.con.restart_timeout()#To avoid connection timeout (long process)
            l=b2s(l)
            if l.find("Estadística Rápida")!=-1:
                datestr=l.split("<br />")[1].split("</span")[0]
                datarr=datestr.split("/")
                date=datetime.date(int(datarr[2]), int(datarr[1]), int(datarr[0]))
                dat=dt(date, product.stockmarket.closes, product.stockmarket.zone)
                value=Decimal(self.comaporpunto(l.split('line text">')[1].split("</td")[0].split("\xa0")[1]))
                quotes.append(Quote(self.mem).init__create(product, dat, value))
                return quotes
        self.log("Error parsing: {}".format(product.name))
        return quotes

    def on_regenerate_product(self,  product, save=False):
        """
            save indica su guarda el tiecker calculado
            returns idmorningstar
        """       
        #Search morningstar code
        url='http://www.morningstar.es/es/funds/SecuritySearchResults.aspx?search='+product.isin+'&type='
        mweb=self.load_page(url)
        if mweb==None:
            return
        web=[]
        ##TRansform httpresopone to list to iterate several times
        for line in mweb.readlines():
            web.append(b2s(line))
            
        idmorningstar=None
        for i in web: 
            if i.find("searchIsin")!=-1:
                try:
                    idmorningstar=i.split('href="')[1].split('">')[0].split("=")[1]
                except:
                    self.log("Error parsing: {}".format(product.name))
        product.ticker=idmorningstar
        product.save()
        return idmorningstar
        
    def setSQL(self, useronly):
        if useronly==True:
            self.sql="select * from products where priorityhistorical[1]=8 and obsolete=false and id in (select distinct(products_id) from inversiones) and ticker is not null order by name;"
        else:
            self.sql="select * from products where priorityhistorical[1]=8 and obsolete=false and ticker is not null order by name;"
        self.setStatus(SourceStatus.Prepared)

    def steps(self):
        """Define  the number of steps of the source run"""
        return 2+ self.products.length()#CORRECT
  
    def run(self):
        self.setStatus(SourceStatus.Running)
        self.products.load_from_db(self.sql)
        self.next_step()
        futures=[]
        with ThreadPoolExecutor(max_workers=10) as executor:
            for i,  product in enumerate(self.products.arr): 
                futures.append(executor.submit(self.on_execute_product,  product))
            
            for i,  future in enumerate(as_completed(futures)):
                for quote in future.result():
                    self.quotes.append(quote)
                    if self.type==1:
                        stri="{0}: {1}/{2} {3}. Appended: {4}            ".format(self.__class__.__name__, i+1, self.products.length(), product, self.quotes.length()) 
                        sys.stdout.write("\b"*1000+stri)
                        sys.stdout.flush()
                    if self.stopping==True:
                        logging.debug ("Stopping")
                        self.quotes.clear()
                        break
                self.next_step()
        print("")

        
        self.quotes_save()
        self.mem.con.commit()
        self.next_step()
        
        self.setStatus(SourceStatus.Finished)

    def regenerate_tickers(self):
        self.setStatus(SourceStatus.Running)
        self.products.load_from_db("select * from products where priorityhistorical[1]=8 and obsolete=false order by name;")
        self.next_step()
        regenerate=0
        for i,  product in enumerate(self.products.arr): 
            stri="{0}: {1}/{2} {3}. Found: {4}            ".format(self.__class__.__name__, i+1, self.products.length(), product,  regenerate) 
            sys.stdout.write("\b"*1000+stri)
            sys.stdout.flush()
            id=self.on_regenerate_product(product, save=True)
            if id!=None:
                regenerate=regenerate+1
            self.next_step()
            time.sleep(self.sleep)#time step
        print("")
        self.mem.con.commit()
        self.next_step()
        
        self.setStatus(SourceStatus.Finished)

class WorkerSGWarrants(SourceParsePage):
    """Clase que recorre las inversiones activas y calcula según este la prioridad de la previsión"""
    def __init__(self, mem):
        SourceParsePage.__init__(self, mem)
        self.setName(self.tr("SG Warrants source"))
        
        
    def on_load_page(self):
        """Overrided this function because web needs to create a session"""
        #driver = webdriver.HtmlUnitDriver()
#        profile = webdriver.FirefoxProfile()
#        profile.native_events_enabled = True
##        driver = webdriver.Firefox(profile)
##        driver = webdriver.Remote(desired_capabilities=webdriver.DesiredCapabilities.HTMLUNIT)
#        driver.get('https://es.warrants.com')
#        form=driver.find_element_by_id('id3e9b')
#        form.click()
#        driver.quit()
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
                bolsa=self.mem.stockmarkets.find_by_id(2)#'US/Eastern'
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
#class WorkerYahoo(SourceParsePage):
#    """Clase que recorre las inversiones activas y calcula según este la prioridad de la previsión"""
#    def __init__(self, mem):
#        SourceParsePage.__init__(self, mem)
#        self.setName(self.tr("Yahoo source"))
#
#    def sum_tickers(self, setproducts):
#        s=""
#        for p in setproducts.arr:
#            if p.ticker==None:
#                continue
#            if p.ticker=="":
#                continue
#            s=s+p.ticker+"+"
#        return s[:-1]
#                
#    def setSQL(self, useronly):
#        self.userinvestmentsonly=useronly
#        if self.userinvestmentsonly==True:
#            self.sql="""
#                select * 
#                from 
#                    products 
#                where 
#                    priority[1]=1 and 
#                    obsolete=false and 
#                    id in 
#                        (
#                            select distinct(products_id) from inversiones UNION 
#                            select id from products where id={} UNION 
#                            select id from products where type=6
#                        )
#                order by name
#            """.format(self.mem.data.benchmark.id)#type=76 divisas
#            
#        else:
#            self.sql="select * from products where priority[1]=1 and obsolete=false order by name"
#        self.setStatus(SourceStatus.Prepared)
#
#    def my_load_page(self, setproducts):
#        "Overrides SourceParsePage"
#        self.url='http://download.finance.yahoo.com/d/quotes.csv?s=' + self.sum_tickers(setproducts) + '&f=sl1d1t1&e=.csv'
#        logging.debug(self.url)
#
#        web=self.load_page(self.url)
#        if web==None:
#            self.web=None
#            return
#        self.web=[]
#        ##TRansform httpresopone to list to iterate several times
#        for line in web.readlines():
#            self.web.append(b2s(line))
#        self.toWebLog(self.web)
#        
#    def my_parse_page(self):
#        "Overrides SourceParsePage"
#        for i in self.web:
#            logging.debug(i)
#            try:
#                datos=i[:-2].split(",")#Se quita dos creo que por caracter final linea windeos.
#                product=self.products.find_by_ticker(datos[0][1:-1])
#
#                if product==None:
#                    self.log("{} Not found".format(datos[0][1:-1] ))
#                    continue                
#                
#                quote=Decimal(datos[1])
#                d=int(datos[2][1:-1].split("/")[1])
#                M=int(datos[2][1:-1].split("/")[0])
#                Y=int(datos[2][1:-1].split("/")[2])
#                H=int(datos[3][1:-1].split(":")[0])
#                m=int(datos[3][1:-1].split(":")[1][:-2])
#                pm=datos[3][1:-1].split(":")[1][2:]
#                
#                #Conversion
#                H=ampm_to_24(H, pm)
#                dat=datetime.date(Y, M, d)
#                tim=datetime.time(H, m)
#                bolsa=self.mem.stockmarkets.find_by_id(2)#'US/Eastern'
#                self.quotes.append(Quote(self.mem).init__create(product,dt(dat,tim,bolsa.zone), quote))
#            except:#
#                self.log("Error parsing: {}".format(i[:-1]))
#                continue                
#                
#    def run(self):
#        """OVerrides ParsePage"""
#        self.setStatus(SourceStatus.Running)
#        self.agrupation=[]#used to iterate sets de products 
#        self.totals=Source(self.mem)# Used to show totals of agrupation
#        self.products=SetProducts(self.mem)#Total of products of an Agrupation
#        self.products.load_from_db(self.sql)    
#        items=150
#        
#        logging.debug (self.products.length())
#               
#        for i in range(int(self.products.length()/items)+1) :#Creo tantos SetProducts como bloques de 150
#            self.agrupation.append(SetProducts(self.mem))
#            
#        for i, p in enumerate(self.products.arr):
#            self.agrupation[int(i/items)].append(p)#Añado en array que correspoonda el p
#            
#        for setproduct in self.agrupation:
#            self.my_load_page(setproduct)
#            self.next_step()
#            self.my_parse_page()
#            self.next_step()
#            
#        self.quotes_save()
#        self.mem.con.commit()
#        self.next_step()
#            
#        self.setStatus(SourceStatus.Finished)
#
#
#
#    def steps(self):
#        """Define  the number of steps of the source run"""
#        return len(self.agrupation)*2 +1#CORRECT
#
#class WorkerYahooHistorical(Source):
#    """Clase que recorre las inversiones activas y busca la última  que tiene el microsecond 4. Busca en internet los historicals a partir de esa fecha"""
#    def __init__(self, mem, type,  sleep=0):
#        Source.__init__(self, mem)
#        self.setName(self.tr("Yahoo Historical source"))
#        self.type=type
#        self.sleep=sleep
#        
#    def on_execute_product(self,  product):
#        """inico y fin son dos dates entre los que conseguir los datos."""
#        quotes=[]
#        ultima=product.fecha_ultima_actualizacion_historica()
#        if ultima==datetime.date.today()-datetime.timedelta(days=1):
#            return quotes
#        inicio= ultima+datetime.timedelta(days=1)
#        fin= datetime.date.today()
#        url='http://ichart.finance.yahoo.com/table.csv?s='+product.ticker+'&a='+str(inicio.month-1)+'&b='+str(inicio.day)+'&c='+str(inicio.year)+'&d='+str(fin.month-1)+'&e='+str(fin.day)+'&f='+str(fin.year)+'&g=d&ignore=.csv'
#        mweb=self.load_page(url)
#        if mweb==None:
#            return quotes
#        web=[]
#        ##TRansform httpresopone to list to iterate several times
#        for line in mweb.readlines():
#            web.append(b2s(line)[:-1])
#        web=web[1:]#Quita primera file de encabezado
#        self.toWebLog(web)
#        
#        for i in web: 
#            datos=i.split(",")
#            fecha=datos[0].split("-")
#            date=datetime.date(int(fecha[0]), int(fecha[1]),  int(fecha[2]))
#            
#            datestart=dt(date,product.stockmarket.starts,product.stockmarket.zone)
#            dateends=dt(date,product.stockmarket.closes,product.stockmarket.zone)
#            datetimefirst=datestart-datetime.timedelta(seconds=1)
#            datetimelow=(datestart+(dateends-datestart)*1/3)
#            datetimehigh=(datestart+(dateends-datestart)*2/3)
#            datetimelast=dateends+datetime.timedelta(microseconds=4)
#
#            quotes.append(Quote(self.mem).init__create(product,datetimelast, Decimal(datos[4])))#closes
#            quotes.append(Quote(self.mem).init__create(product,datetimelow, Decimal(datos[3])))#low
#            quotes.append(Quote(self.mem).init__create(product,datetimehigh, Decimal(datos[2])))#high
#            quotes.append(Quote(self.mem).init__create(product, datetimefirst, Decimal(datos[1])))#open
#        return quotes
#
#    def setSQL(self, useronly):
#        self.userinvestmentsonly=useronly
#        if self.userinvestmentsonly==True:
#            self.sql="""
#                select * 
#                from 
#                    products 
#                where 
#                    priorityhistorical[1]=3 and 
#                    obsolete=false and 
#                    id in 
#                        (
#                            select distinct(products_id) from inversiones UNION 
#                            select id from products where id={} UNION 
#                            select id from products where type=6
#                        )
#                order by name
#            """.format(self.mem.data.benchmark.id)#type=76 divisas
#        else:
#            self.sql="select * from products where priorityhistorical[1]=3 and obsolete=false order by name"
#        self.setStatus(SourceStatus.Loaded)
#        
#    def run(self):
##        self.setStatus(SourceStatus.Running)
##        self.products.load_from_db(self.sql)
##        self.next_step()
##        for i,  product in enumerate(self.products.arr): 
##            if self.type==1:
##                stri="{0}: {1}/{2} {3}. Appended: {4}            ".format(self.__class__.__name__, i+1, self.products.length(), product, self.quotes.length()) 
##                sys.stdout.write("\b"*1000+stri)
##                sys.stdout.flush()
##            if self.stopping==True:
##                print ("Stopping")
##                self.quotes.clear()
##                break
##            self.on_execute_product(product.id)
##            self.next_step()
##            time.sleep(self.sleep)#time step
##        print("")
##        self.quotes_save()
##        self.mem.con.commit()
##        self.next_step()
##        
##        self.setStatus(SourceStatus.Finished)
##        
#        
#        #
#        self.setStatus(SourceStatus.Running)
#        self.products.load_from_db(self.sql)
#        self.next_step()
#        futures=[]
#        with ThreadPoolExecutor(max_workers=10) as executor:
#            for i,  product in enumerate(self.products.arr): 
#
#                futures.append(executor.submit(self.on_execute_product,  product))
#            
#            for i,  future in enumerate(as_completed(futures)):
#                for quote in future.result():
#                    self.quotes.append(quote)
#                    if self.type==1:
#                        stri="{0}: {1}/{2} {3}. Appended: {4}            ".format(self.__class__.__name__, i+1, self.products.length(), product, self.quotes.length()) 
#                        sys.stdout.write("\b"*1000+stri)
#                        sys.stdout.flush()
#                    if self.stopping==True:
#                        logging.debug ("Stopping")
#                        self.quotes.clear()
#                        break
#                self.next_step()
#        print("")
#
#        
#        self.quotes_save()
#        self.mem.con.commit()
#        self.next_step()
#        
#        self.setStatus(SourceStatus.Finished)
#        
#    def steps(self):
#        """Define  the number of steps of the source run"""
#        return 2+self.products.length() #CORRECT
#        
        
class WorkerGoogle(Source):
    """Clase que recorre las inversiones activas y calcula según este la prioridad de la previsión"""
    def __init__(self, mem):
        SourceParsePage.__init__(self, mem)
        self.setName(self.tr("Google source"))

    def sum_tickers(self, setproducts):
        s=""
        for p in setproducts.arr:
            if p.ticker==None:
                continue
            if p.ticker=="":
                continue
            s=s+ticker2googleticker(p.ticker)+","
        return s[:-1]
                
    def setSQL(self, useronly):
        self.userinvestmentsonly=useronly
        if self.userinvestmentsonly==True:
            self.sql="""
                select * 
                from 
                    products 
                where 
                    priority[1] in(1,9) and 
                    obsolete=false and 
                    id in 
                        (
                            select distinct(products_id) from inversiones UNION 
                            select id from products where id={} UNION 
                            select id from products where type=6
                        )
                order by name
            """.format(self.mem.data.benchmark.id)#type=76 divisas
            
        else:
            self.sql="select * from products where priority[1]=1 and obsolete=false order by name"
        self.setStatus(SourceStatus.Prepared)

    @classmethod
    def parse_stock(cls, data):
        stock = {'c': data['c'],
                 'c_fix': data['c_fix'],
                 'cp': data['cp'],
                 'cp_fix': data['cp_fix'],
                 'l_fix': data['l_fix'],  #Quote
                 'pcls_fix': data['pcls_fix'],
                 'id': data['id'],
                 'ccol': data['ccol'],
                 'e': data['e'],
                 't': data['t'],
                 's': data['s'],
                 'l_cur': data['l_cur'],
                 'lt': data['lt'],  # u'Aug 22, 2:12PM GMT-3'
                 'lt_dts': data['lt_dts'],  # u'2016-08-22T14:12:01Z'
                 'ltt': data['ltt']  # u'2:12PM GMT-3'
                 }
        return stock
        
    def my_load_page(self, setproducts):
        "Overrides SourceParsePage"
        #self.url='http://download.finance.yahoo.com/d/quotes.csv?s=' + self.sum_tickers(setproducts) + '&f=sl1d1t1&e=.csv'
        
        self.url = 'http://finance.google.com/finance/info?client=ig&q={}'.format(self.sum_tickers(setproducts))
        logging.debug(self.url)

        web=self.load_page(self.url)
        if web==None:
            self.web=None
            return
        self.web=b2s(web.read()).replace("//", "")
        all_data = json.loads(self.web)
        for data in all_data:
            stock = self.parse_stock(data)
            googleticker="{}:{}".format(stock["e"], stock["t"])
            if stock["lt_dts"]=="":
                logging.debug("{} has no date".format(googleticker))
                continue
            product=self.products.find_by_ticker(googleticker2ticker(googleticker))
            if product==None:
                logging.error(stock)
                logging.error("{} => {}".format(googleticker, googleticker2ticker(googleticker)))
                continue
            quote=Decimal(stock["l_fix"])
            dat=datetime.datetime.strptime( stock["lt_dts"], "%Y-%m-%dT%H:%M:%SZ" )
            self.quotes.append(Quote(self.mem).init__create(product,dt_with_pytz(dat.date(),dat.time(),googleticker2pytz(googleticker)), quote))
            
            
        self.toWebLog(self.web)
                
    def run(self):
        """OVerrides ParsePage"""
        self.setStatus(SourceStatus.Running)
        self.agrupation=[]#used to iterate sets de products 
        self.totals=Source(self.mem)# Used to show totals of agrupation
        self.products=SetProducts(self.mem)#Total of products of an Agrupation
        self.products.load_from_db(self.sql)    
        items=150
        
        logging.debug (self.products.length())
               
        for i in range(int(self.products.length()/items)+1) :#Creo tantos SetProducts como bloques de 150
            self.agrupation.append(SetProducts(self.mem))
            
        for i, p in enumerate(self.products.arr):
            self.agrupation[int(i/items)].append(p)#Añado en array que correspoonda el p
            
        for setproduct in self.agrupation:
            self.my_load_page(setproduct)
            self.next_step()
            
        self.quotes_save()
        self.mem.con.commit()
        self.next_step()
            
        self.setStatus(SourceStatus.Finished)



    def steps(self):
        """Define  the number of steps of the source run"""
        return len(self.agrupation) +1#CORRECT

class WorkerGoogleHistorical(Source):
    """Clase que recorre las inversiones activas y busca la última  que tiene el microsecond 4. Busca en internet los historicals a partir de esa fecha"""
    def __init__(self, mem, type,  sleep=0):
        Source.__init__(self, mem)
        self.setName(self.tr("Google Historical source"))
        self.type=type
        self.sleep=sleep
        
    def on_execute_product(self,  product):
        """inico y fin son dos dates entre los que conseguir los datos."""
        quotes=[]
        ultima=product.fecha_ultima_actualizacion_historica()
        if ultima==datetime.date.today()-datetime.timedelta(days=1):
            return quotes
        inicio= ultima+datetime.timedelta(days=1)
        fin= datetime.date.today()
        #https://www.google.com/finance/historical?cid=368894934436308&startdate=Jun+5%2C+2016&enddate=Jun+18%2C+2017&num=30&ei=op5MWbneEsSLUKDklIAF
        url='http://www.google.com/finance/historical?q={}&output=csv'.format(product.ticker)#+product.ticker+'&a='+str(inicio.month-1)+'&b='+str(inicio.day)+'&c='+str(inicio.year)+'&d='+str(fin.month-1)+'&e='+str(fin.day)+'&f='+str(fin.year)+'&g=d&ignore=.csv'
        mweb=self.load_page(url)
        if mweb==None:
            return quotes
        web=[]
        ##TRansform httpresopone to list to iterate several times
        for line in mweb.readlines():
            web.append(b2s(line)[:-1])
        web=web[1:]#Quita primera file de encabezado
        self.toWebLog(web)
        
        for i in web: 
            datos=i.split(",")
            fecha=datos[0].split("-")
            date=datetime.date(int(fecha[0]), int(fecha[1]),  int(fecha[2]))
            
            datestart=dt(date,product.stockmarket.starts,product.stockmarket.zone)
            dateends=dt(date,product.stockmarket.closes,product.stockmarket.zone)
            datetimefirst=datestart-datetime.timedelta(seconds=1)
            datetimelow=(datestart+(dateends-datestart)*1/3)
            datetimehigh=(datestart+(dateends-datestart)*2/3)
            datetimelast=dateends+datetime.timedelta(microseconds=4)

            quotes.append(Quote(self.mem).init__create(product,datetimelast, Decimal(datos[4])))#closes
            quotes.append(Quote(self.mem).init__create(product,datetimelow, Decimal(datos[3])))#low
            quotes.append(Quote(self.mem).init__create(product,datetimehigh, Decimal(datos[2])))#high
            quotes.append(Quote(self.mem).init__create(product, datetimefirst, Decimal(datos[1])))#open
        return quotes

    def setSQL(self, useronly):
        self.userinvestmentsonly=useronly
        if self.userinvestmentsonly==True:
            self.sql="""
                select * 
                from 
                    products 
                where 
                    priorityhistorical[1]=3 and 
                    obsolete=false and 
                    id in 
                        (
                            select distinct(products_id) from inversiones UNION 
                            select id from products where id={} UNION 
                            select id from products where type=6
                        )
                order by name
            """.format(self.mem.data.benchmark.id)#type=76 divisas
        else:
            self.sql="select * from products where priorityhistorical[1]=3 and obsolete=false order by name"
        self.setStatus(SourceStatus.Loaded)
        
    def run(self):
#        self.setStatus(SourceStatus.Running)
#        self.products.load_from_db(self.sql)
#        self.next_step()
#        for i,  product in enumerate(self.products.arr): 
#            if self.type==1:
#                stri="{0}: {1}/{2} {3}. Appended: {4}            ".format(self.__class__.__name__, i+1, self.products.length(), product, self.quotes.length()) 
#                sys.stdout.write("\b"*1000+stri)
#                sys.stdout.flush()
#            if self.stopping==True:
#                print ("Stopping")
#                self.quotes.clear()
#                break
#            self.on_execute_product(product.id)
#            self.next_step()
#            time.sleep(self.sleep)#time step
#        print("")
#        self.quotes_save()
#        self.mem.con.commit()
#        self.next_step()
#        
#        self.setStatus(SourceStatus.Finished)
#        
        
        #
        self.setStatus(SourceStatus.Running)
        self.products.load_from_db(self.sql)
        self.next_step()
        futures=[]
        with ThreadPoolExecutor(max_workers=10) as executor:
            for i,  product in enumerate(self.products.arr): 

                futures.append(executor.submit(self.on_execute_product,  product))
            
            for i,  future in enumerate(as_completed(futures)):
                for quote in future.result():
                    self.quotes.append(quote)
                    if self.type==1:
                        stri="{0}: {1}/{2} {3}. Appended: {4}            ".format(self.__class__.__name__, i+1, self.products.length(), product, self.quotes.length()) 
                        sys.stdout.write("\b"*1000+stri)
                        sys.stdout.flush()
                    if self.stopping==True:
                        logging.debug ("Stopping")
                        self.quotes.clear()
                        break
                self.next_step()
        print("")

        
        self.quotes_save()
        self.mem.con.commit()
        self.next_step()
        
        self.setStatus(SourceStatus.Finished)
        
    def steps(self):
        """Define  the number of steps of the source run"""
        return 2+self.products.length() #CORRECT


##################################

def ticker2googleticker(ticker):
    if  ticker[-3:]==".MC":
        return "BME:{}".format(ticker[:-3])
    if  ticker[-3:]==".DE":
        return "FRA:{}".format(ticker[:-3])
    if  ticker[-3:]==".PA":
        return "EPA:{}".format(ticker[:-3])
    if  ticker[-3:]==".MI":
        return "BIT:{}".format(ticker[:-3])
    if ticker=="^IBEX":
        return "INDEXBME:IB"
    if ticker in("AH.AS"):
        return ""
    if len(ticker.split("."))==1:##Americanas
        return ticker
    logging.debug("ticker2googleticker {} not found".format(ticker))
    

def googleticker2ticker(ticker):
    a=ticker.split(":")
    if  a[0]=="BME":
        return "{}.MC".format(a[1])
    if  a[0]=="FRA":
        return "{}.DE".format(a[1])
    if  a[0]=="EPA":
        return "{}.PA".format(a[1])
    if  a[0]=="BIT":
        return "{}.MI".format(a[1])
    if ticker=="INDEXBME:IB":
        return "^IBEX"
    if a[0] in ("NASDAQ",  "NYSEARCA", "NYSE"):
        return "{}".format(a[1])
    logging.debug("googleticker2ticker {} not found".format(ticker))
    
def googleticker2pytz(ticker):
    a=ticker.split(":")
    if a[0] in ("BME",  "INDEXBME"):
        return "Europe/Madrid"
    if a[0] in ("FRA", ):
        return "Europe/Berlin"
    if a[0] in ("EPA", ):
        return "Europe/Paris"
    if a[0] in ("BIT", ):
        return "Europe/Rome"
    if a[0] in ("NASDAQ",  "NYSEARCA", "NYSE"):
        return "America/New_York"
    return None

def sync_data(con_source, con_target, progress=None):
    """con is con_target, 
    progress is a pointer to progressbar
    returns a tuple (numberofproductssynced, numberofquotessynced)"""
    #Checks if database has same version
    cur_target=con_target.cursor()
    cur2_target=con_target.cursor()
    cur_source=con_source.cursor()
    
    
    #Checks if database has same version
    cur_source.execute("select value from globals where id_globals=1")
    cur_target.execute("select value from globals where id_globals=1")
    
    if cur_source.fetchone()[0]!=cur_target.fetchone()[0]:
        logging.critical ("Databases has diferent versions, please update them")
        sys.exit(0)
    
    quotes=0#Number of quotes synced
    estimation_dps=0#Number of estimation_dps synced
    estimation_eps=0#Number of estimation_eps synced
    dps=0
    products=0#Number of products synced
    
    #Iterate all products
    cur_target.execute("select id,name from products where id>0 order by name;")
    logging.info ("Syncing {} products".format (cur_target.rowcount))
    for row in cur_target:
        output="{}: ".format(row['name'])
        ## QUOTES #####################################################################
        #Search last datetime
        cur2_target.execute("select max(datetime) as max from quotes where id=%s", (row['id'], ))
        max=cur2_target.fetchone()[0]
        #Ask for quotes in source with last datetime
        if max==None:#No hay ningun registro y selecciona todos
            cur_source.execute("select * from quotes where id=%s", (row['id'], ))
        else:#Hay registro y selecciona los posteriores a el
            cur_source.execute("select * from quotes where id=%s and datetime>%s", (row['id'], max))
        if cur_source.rowcount!=0:
            print("  - Syncing {} since {} ".format(row['name'], max),end="")
            for  row_source in cur_source: #Inserts them 
                cur2_target.execute("insert into quotes (id, datetime, quote) values (%s,%s,%s)", ( row_source['id'], row_source['datetime'], row_source['quote']))
                quotes=quotes+1
                output=output+"."
                
        ## DPS ################################################################################
        #Search last datetime
        cur2_target.execute("select max(date) as max from dps where id=%s", (row['id'], ))
        max=cur2_target.fetchone()[0]
        #Ask for quotes in source with last datetime
        if max==None:#No hay ningun registro y selecciona todos
            cur_source.execute("select * from dps where id=%s", (row['id'], ))
        else:#Hay registro y selecciona los posteriores a el
            cur_source.execute("select * from dps where id=%s and date>%s", (row['id'], max))
        if cur_source.rowcount!=0:
            for  row_source in cur_source: #Inserts them 
                cur2_target.execute("insert into dps (date, gross, id) values (%s,%s,%s)", ( row_source['date'], row_source['gross'], row_source['id']))
                dps=dps+1
                output=output+"-"

        ## DPS ESTIMATIONS #####################################################################
        #Search last datetime
        cur2_target.execute("select max(year) as max from estimations_dps where id=%s", (row['id'], ))
        max=cur2_target.fetchone()[0]
        #Ask for quotes in source with last datetime
        if max==None:#No hay ningun registro y selecciona todos
            cur_source.execute("select * from estimations_dps where id=%s", (row['id'], ))
        else:#Hay registro y selecciona los posteriores a el
            cur_source.execute("select * from estimations_dps where id=%s and year>%s", (row['id'], max))
        if cur_source.rowcount!=0:
            for  row_source in cur_source: #Inserts them 
                cur2_target.execute("insert into estimations_dps (year, estimation, date_estimation, source, manual, id) values (%s,%s,%s,%s,%s,%s)", ( row_source['year'], row_source['estimation'], row_source['date_estimation'], row_source['source'], row_source['manual'],  row_source['id']))
                estimation_dps=estimation_dps+1
                output=output+"+"
                
        ## EPS ESTIMATIONS #####################################################################
        #Search last datetime
        cur2_target.execute("select max(year) as max from estimations_eps where id=%s", (row['id'], ))
        max=cur2_target.fetchone()[0]
        #Ask for quotes in source with last datetime
        if max==None:#No hay ningun registro y selecciona todos
            cur_source.execute("select * from estimations_eps where id=%s", (row['id'], ))
        else:#Hay registro y selecciona los posteriores a el
            cur_source.execute("select * from estimations_eps where id=%s and year>%s", (row['id'], max))
        if cur_source.rowcount!=0:
            for  row_source in cur_source: #Inserts them 
                cur2_target.execute("insert into estimations_eps (year, estimation, date_estimation, source, manual, id) values (%s,%s,%s,%s,%s,%s)", ( row_source['year'], row_source['estimation'], row_source['date_estimation'], row_source['source'], row_source['manual'],  row_source['id']))
                estimation_eps=estimation_eps+1
                output=output+"*"
                
        if output!="{}: ".format(row['name']):
            products=products+1
            logging.info(output)
            
        if progress!=None:#If there's a progress bar
            progress.setValue(cur_target.rownumber)
            progress.setMaximum(cur_target.rowcount)
            QCoreApplication.processEvents()
    con_target.commit()
    print("")
    
    if progress!=None:
        s=QCoreApplication.translate("Core", """From {} desynchronized products added:
    - {} quotes
    - {} dividends per share
    - {} dividend per share estimations
    - {} earnings per share estimations""").format(  products,  quotes, dps, estimation_dps,  estimation_eps)
            
        qmessagebox(s)  

