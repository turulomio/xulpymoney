from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Ui_wdgSource import *
from libsources import *

class Sources:
    WorkerYahoo=1
    WorkerYahooHistorical=2
    WorkerMercadoContinuo=3


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
        
        
    def on_cmdRun_released(self):
        self.worker.run()
            
        
            
