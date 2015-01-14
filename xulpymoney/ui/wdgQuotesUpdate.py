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
        self.sources_active=0

        self.wyahoo=wdgSource(self.mem, Sources.WorkerYahoo, self)             
        QObject.connect(self.wyahoo, SIGNAL("started"), self.after_source_start)   
        QObject.connect(self.wyahoo, SIGNAL("finished"), self.after_source_stop)   
        self.layIntraday.addWidget(self.wyahoo, 0, 0)
        
        self.wmc=wdgSource(self.mem, Sources.WorkerMercadoContinuo, self)      
        QObject.connect(self.wmc, SIGNAL("started"), self.after_source_start)   
        QObject.connect(self.wmc, SIGNAL("finished"), self.after_source_stop)   
        self.layIntraday.addWidget(self.wmc, 1, 0)
        
        self.wyahoohistorical=wdgSource(self.mem, Sources.WorkerYahooHistorical, self)     
        QObject.connect(self.wyahoohistorical, SIGNAL("started"), self.after_source_start)   
        QObject.connect(self.wyahoohistorical, SIGNAL("finished"), self.after_source_stop)   
        self.layDaily.addWidget(self.wyahoohistorical)
        
        self.wmorning=wdgSource(self.mem, Sources.WorkerMorningstar, self)
        QObject.connect(self.wmorning, SIGNAL("started"), self.after_source_start)   
        QObject.connect(self.wmorning, SIGNAL("finished"), self.after_source_stop)   
        self.layDaily.addWidget(self.wmorning)
        
        self.on_chkUserOnly_stateChanged(self.chkUserOnly.checkState())
        
    def on_chkUserOnly_stateChanged(self, state):
        self.wyahoo.chkUserOnly.setCheckState(state)
        self.wyahoohistorical.chkUserOnly.setCheckState(state)
        self.wmc.chkUserOnly.setCheckState(state)
        self.wmorning.chkUserOnly.setCheckState(state)
        
    def on_cmdIntraday_released(self):
        if self.wyahoo.cmdRun.isEnabled():
            self.wyahoo.on_cmdRun_released()
        if self.wmc.cmdRun.isEnabled():
            self.wmc.on_cmdRun_released()
        
        self.mem.data.reload_prices()
        
        
    def on_cmdDaily_released(self):
        if self.wyahoohistorical.cmdRun.isEnabled():
            self.wyahoohistorical.on_cmdRun_released()
        if self.wmorning.cmdRun.isEnabled():
            self.wmorning.on_cmdRun_released()
            
        self.mem.data.reload_prices()
            
        
    def on_cmdAll_released(self):        
        if self.wyahoo.cmdRun.isEnabled():
            self.wyahoo.on_cmdRun_released()
        if self.wmc.cmdRun.isEnabled():
            self.wmc.on_cmdRun_released()
        if self.wyahoohistorical.cmdRun.isEnabled():
            self.wyahoohistorical.on_cmdRun_released()
        if self.wmorning.cmdRun.isEnabled():
            self.wmorning.on_cmdRun_released()
            
        self.mem.data.reload_prices()
        
    def after_source_start(self):
        self.sources_active=self.sources_active+1
        self.mem.frmMain.actionsEnabled(False)
        #Disables  button when wdgSources cmdRun are disabled
        if self.wyahoo.cmdRun.isEnabled()==False and self.wmc.cmdRun.isEnabled()==False:
            self.cmdIntraday.setEnabled(False)
        if self.wyahoohistorical.cmdRun.isEnabled()==False and self.wmorning.isEnabled()==False:
            self.cmdDaily.setEnabled(False)
        if self.cmdDaily.isEnabled()==False and self.cmdIntraday.isEnabled()==False:
            self.cmdAll.setEnabled(False)
        QCoreApplication.processEvents()
        
    def after_source_stop(self):
        self.sources_active=self.sources_active-1
        if self.sources_active==0:
            self.mem.frmMain.actionsEnabled(True)
        QCoreApplication.processEvents()            
            
            
