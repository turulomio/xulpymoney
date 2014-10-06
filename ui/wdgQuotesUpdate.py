from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Ui_wdgQuotesUpdate import *
from wdgSource import *

class wdgQuotesUpdate(QWidget, Ui_wdgQuotesUpdate):
    def __init__(self, mem,  parent = None, name = None):
        QWidget.__init__(self,  parent)
        self.setupUi(self)
        self.mem=mem
        
        wyahoo=wdgSource(self.mem, Sources.WorkerYahoo)
        self.layIntraday.addWidget(wyahoo)
        wmc=wdgSource(self.mem, Sources.WorkerMercadoContinuo)
        self.layIntraday.addWidget(wmc)
        
        wyahoohistorical=wdgSource(self.mem, Sources.WorkerYahooHistorical)
        self.layDaily.addWidget(wyahoohistorical)
