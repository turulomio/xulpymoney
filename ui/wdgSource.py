from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Ui_wdgSource import *
from libsources import *
from myqtablewidget import *

class Sources:
    WorkerYahoo=1
    WorkerYahooHistorical=2
    WorkerMercadoContinuo=3
    WorkerMorningstar=4


class wdgSource(QWidget, Ui_wdgSource):
    def __init__(self, mem, class_sources,  parent = None, name = None):
        QWidget.__init__(self,  parent)
        self.setupUi(self)
        self.mem=mem
        self.parent=parent
        self.steps=None#Define the steps of the self.progress bar
        self.class_sources=class_sources
        self.widgettoupdate=self.parent.parent
        if self.class_sources==Sources.WorkerYahoo:
                self.grp.setTitle(self.tr("Yahoo source"))
        elif self.class_sources==Sources.WorkerYahooHistorical:
                self.grp.setTitle(self.tr("Yahoo historical source"))
        elif self.class_sources==Sources.WorkerMercadoContinuo:      
                self.grp.setTitle(self.tr("Mercado Continuo source"))
        elif self.class_sources==Sources.WorkerMorningstar:
                self.grp.setTitle(self.tr("Morningstar source"))

    def strUserOnly(self,  withindex=False):
        """Returns a sql string if products must be filtered by user invesments"""
        if self.chkUserOnly.isChecked():
            if withindex==False:
                return " and id in (select distinct(products_id) from inversiones) "
            else:
                return " and (id in (select distinct(products_id) from inversiones) or id in (select distinct (id) from products where type=3))"
        return ""

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
        self.cmdRun.setEnabled(False)     
        self.chkUserOnly.setEnabled(False)
        
        #Create objects
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
        elif self.class_sources==Sources.WorkerYahooHistorical:
            self.worker=WorkerYahooHistorical(self.mem, 0, "select * from products where priorityhistorical[1]=3 and obsolete=false {} order by name".format(self.strUserOnly(True)))
            self.agrupation.append(self.worker)
        elif self.class_sources==Sources.WorkerMercadoContinuo:                
            self.worker=WorkerMercadoContinuo(self.mem, "select * from products where 9=any(priority) obsolete=false {} order by name".format(self.strUserOnly()))
            self.agrupation.append(self.worker)
        elif self.class_sources==Sources.WorkerMorningstar:
            self.worker=WorkerMorningstar(self.mem, 0,  "select * from products where priorityhistorical[1]=8 and obsolete=false {} order by name;".format(self.strUserOnly()))
            self.agrupation.append(self.worker)
        self.currentWorker=self.agrupation[0]# Current worker working

        #Make connections
        for worker in self.agrupation:
            QObject.connect(worker, SIGNAL("step_finished"), self.progress_step)   
            QObject.connect(worker, SIGNAL("run_finished"), self.worker_run_finished)   
        
        #Starts
        self.emit(SIGNAL("started")) 
        for worker in self.agrupation:
            self.currentWorker=worker
            worker.run()
            
            
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
        self.emit(SIGNAL("finished")) 
        
        
    def on_cmdCancel_released(self):
        self.cmdCancel.setEnabled(False)
        self.currentWorker.stopping=True
        self.currentWorker=None# Current worker working

    def on_cmdInserted_released(self):
        d=QDialog(self)        
        d.showMaximized()
        d.setWindowTitle(self.trUtf8("Inserted quotes"))
        t=myQTableWidget(d)
        self.totals.inserted.myqtablewidget(t, "wdgSource")
        lay = QVBoxLayout(d)
        lay.addWidget(t)
        d.show()
        
    def on_cmdEdited_released(self):
        d=QDialog(self)        
        d.showMaximized()
        d.setWindowTitle(self.trUtf8("Edited quotes"))
        t=myQTableWidget(d)
        self.totals.modified.myqtablewidget(t, "wdgSource")
        lay = QVBoxLayout(d)
        lay.addWidget(t)
        d.show()
        
    def on_cmdIgnored_released(self):
        d=QDialog(self)        
        d.showMaximized()
        d.setWindowTitle(self.trUtf8("Ignored quotes"))
        t=myQTableWidget(d)
        self.totals.ignored.myqtablewidget(t, "wdgSource")
        lay = QVBoxLayout(d)
        lay.addWidget(t)
        d.show()
        
    def on_cmdErrors_released(self):
        d=QDialog(self)        
        d.showMaximized()
        d.setWindowTitle(self.trUtf8("Error procesing the source"))
        terrors=myQTableWidget(d)
        self.totals.myqtablewidget_errors(terrors, "wdgSource")
        lay = QVBoxLayout(d)
        lay.addWidget(terrors)
        d.show()

    def on_cmdBad_released(self):
        d=QDialog(self)        
        d.showMaximized()
        d.setWindowTitle(self.trUtf8("Error procesing the source"))
        t=myQTableWidget(d)
        self.totals.bad.myqtablewidget(t, "wdgSource")
        lay = QVBoxLayout(d)
        lay.addWidget(t)
        d.show()
        
    def on_cmdSearched_released(self):
        d=QDialog(self)        
        d.showMaximized()
        d.setWindowTitle(self.trUtf8("Error procesing the source"))
        t=myQTableWidget(d)
        self.products.myqtablewidget(t, "wdgSource")
        lay = QVBoxLayout(d)
        lay.addWidget(t)
        d.show()
