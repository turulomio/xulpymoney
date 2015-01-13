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
        self.on_chkUserOnly_stateChanged(self.chkUserOnly.checkState())
        
    def on_chkUserOnly_stateChanged(self, state):
        if state==Qt.Checked:#User only
            self.wyahoo=wdgSource(self.mem, Sources.WorkerYahooUserOnly, self)
            self.wmc=wdgSource(self.mem, Sources.WorkerMercadoContinuoUserOnly, self)            
            self.wyahoohistorical=wdgSource(self.mem, Sources.WorkerYahooHistoricalUserOnly, self)            
            self.wmorning=wdgSource(self.mem, Sources.WorkerMorningstarUserOnly, self)
        else:
            self.wyahoo=wdgSource(self.mem, Sources.WorkerYahoo, self)
            self.wmc=wdgSource(self.mem, Sources.WorkerMercadoContinuo, self)            
            self.wyahoohistorical=wdgSource(self.mem, Sources.WorkerYahooHistorical, self)            
            self.wmorning=wdgSource(self.mem, Sources.WorkerMorningstar, self)

        QObject.connect(self.wyahoo, SIGNAL("started"), self.after_source_start)   
        QObject.connect(self.wyahoo, SIGNAL("finished"), self.after_source_stop)   
        self.layIntraday.addWidget(self.wyahoo, 0, 0)
        
        QObject.connect(self.wmc, SIGNAL("started"), self.after_source_start)   
        QObject.connect(self.wmc, SIGNAL("finished"), self.after_source_stop)   
        self.layIntraday.addWidget(self.wmc, 1, 0)
        
        QObject.connect(self.wyahoohistorical, SIGNAL("started"), self.after_source_start)   
        QObject.connect(self.wyahoohistorical, SIGNAL("finished"), self.after_source_stop)   
        self.layDaily.addWidget(self.wyahoohistorical)
        
        QObject.connect(self.wmorning, SIGNAL("started"), self.after_source_start)   
        QObject.connect(self.wmorning, SIGNAL("finished"), self.after_source_stop)   
        self.layDaily.addWidget(self.wmorning)
        
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
            
            
