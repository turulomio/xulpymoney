from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Ui_wdgSource import *
from libsources import *
from myqtablewidget import *

class Sources:
    WorkerYahoo=1
    WorkerYahooHistorical=2
    WorkerMercadoContinuo=3

#class TWorker(threading.Thread):
#    """Hilo que actualiza las products, solo el getBasic, cualquier cambio no de last, deberá ser desarrollado por código"""
#    def __init__(self, mem, worker):
#        threading.Thread.__init__(self)
#        self.mem=mem
#        self.worker=worker
#        
#    def run(self):
#        print ("TWorker started")
#        self.worker.run()
        
            
class wdgSource(QWidget, Ui_wdgSource):
    def __init__(self, mem, sources,  parent = None, name = None):
        QWidget.__init__(self,  parent)
        self.setupUi(self)
        self.mem=mem
        
        if sources==Sources.WorkerYahoo:
            cur=mem.con.cursor()
            cur.execute("select count(*) from products where active=true and priority[1]=1")
            num=cur.fetchone()[0]
            step=150
            for i in range (0, int(num/step)+1):
                self.worker=WorkerYahoo(mem, "select * from products where active=true and priority[1]=1 order by ticker limit {} offset {};".format(step, step*i))
            cur.close()           
        elif sources==Sources.WorkerYahooHistorical:
            self.worker=WorkerYahooHistorical(mem, 1)
        elif sources==Sources.WorkerMercadoContinuo:                
            self.worker=WorkerMercadoContinuo(mem)
        
        self.lbl.setText(self.worker.__class__.__name__)
        #self.thread=TWorker(self.mem, self.worker)
        
        QObject.connect(self.worker, SIGNAL("run_finished()"), self.on_worker_run_finished)    
        
        
    def on_cmdRun_released(self):
        QTimer.singleShot(200, self.worker, SLOT(self.worker.run()));
#        self.thread.start()
        self.cmdRun.setEnabled(False)
        
            
    def on_worker_run_finished(self):
        self.cmdInserted.setText(self.tr("{} Inserted").format(self.worker.inserted.length()))
        self.cmdEdited.setText(self.tr("{} Edited").format(self.worker.modified.length()))
        self.cmdIgnored.setText(self.tr("{} Ignored").format(self.worker.ignored.length()))
        self.cmdErrors.setText(self.tr("{} errors").format(len(self.worker.errors)))
        self.cmdInserted.setEnabled(True)
        self.cmdIgnored.setEnabled(True)
        self.cmdEdited.setEnabled(True)
        self.cmdErrors.setEnabled(True)
        
    def on_cmdInserted_released(self):
        d=QDialog(self)        
        d.setFixedSize(670, 670)
        d.setWindowTitle(self.trUtf8("Inserted quotes"))
        t=myQTableWidget(d)
        self.worker.inserted.myqtablewidget(t, "wdgSource")
        lay = QVBoxLayout(d)
        lay.addWidget(t)
        d.show()
        
    def on_cmdEdited_released(self):
        d=QDialog(self)        
        d.setFixedSize(670, 670)
        d.setWindowTitle(self.trUtf8("Edited quotes"))
        t=myQTableWidget(d)
        self.worker.modified.myqtablewidget(t, "wdgSource")
        lay = QVBoxLayout(d)
        lay.addWidget(t)
        d.show()
        
    def on_cmdIgnored_released(self):
        d=QDialog(self)        
        d.setFixedSize(670, 670)
        d.setWindowTitle(self.trUtf8("Ignored quotes"))
        t=myQTableWidget(d)
        self.worker.ignored.myqtablewidget(t, "wdgSource")
        lay = QVBoxLayout(d)
        lay.addWidget(t)
        d.show()
        
    def on_cmdErrors_released(self):
        d=QDialog(self)        
        d.setFixedSize(670, 670)
        d.setWindowTitle(self.trUtf8("Error procesing the source"))
        terrors=myQTableWidget(d)
        self.worker.myqtablewidget_errors(terrors, "wdgSource")
        lay = QVBoxLayout(d)
        lay.addWidget(terrors)
        d.show()

