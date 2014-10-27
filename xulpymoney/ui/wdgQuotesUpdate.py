from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Ui_wdgQuotesUpdate import *
from wdgSource import *

class wdgQuotesUpdate(QWidget, Ui_wdgQuotesUpdate):
    def __init__(self, mem,  parent = None, name = None):
        QWidget.__init__(self,  parent)
        self.setupUi(self)
        self.mem=mem
        self.parent=parent
        
        self.wyahoo=wdgSource(self.mem, Sources.WorkerYahoo, self)
        self.layIntraday.addWidget(self.wyahoo, 0, 0)
        self.wmc=wdgSource(self.mem, Sources.WorkerMercadoContinuo, self)
        self.layIntraday.addWidget(self.wmc, 1, 0)
        
        self.wyahoohistorical=wdgSource(self.mem, Sources.WorkerYahooHistorical, self)
        self.layDaily.addWidget(self.wyahoohistorical)
        
    def on_cmdIntraday_released(self):
        self.cmdIntraday.setEnabled(False)
        
        if self.wyahoo.cmdRun.isEnabled():
            self.wyahoo.on_cmdRun_released()
        if self.wmc.cmdRun.isEnabled():
            self.wmc.on_cmdRun_released()
        
        self.mem.data.reload_prices()
        
        
    def on_cmdDaily_released(self):
        self.cmdDaily.setEnabled(False)
        
        if self.wyahoohistorical.cmdRun.isEnabled():
            self.wyahoohistorical.on_cmdRun_released()
            
        self.mem.data.reload_prices()
            
        
    def on_cmdAll_released(self):
        self.cmdIntraday.setEnabled(False)
        self.cmdDaily.setEnabled(False)
        self.cmdAll.setEnabled(False)
        
        if self.wyahoo.cmdRun.isEnabled():
            self.wyahoo.on_cmdRun_released()
        if self.wmc.cmdRun.isEnabled():
            self.wmc.on_cmdRun_released()
        
        if self.wyahoohistorical.cmdRun.isEnabled():
            self.wyahoohistorical.on_cmdRun_released()
            
        self.mem.data.reload_prices()
            
            
