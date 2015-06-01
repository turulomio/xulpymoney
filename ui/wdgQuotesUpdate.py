from PyQt5.QtCore import *
from PyQt5.QtGui import *
from Ui_wdgQuotesUpdate import *
from libsources import *

class wdgQuotesUpdate(QWidget, Ui_wdgQuotesUpdate):
    def __init__(self, mem,  parent = None, name = None):
        QWidget.__init__(self,  parent)
        self.setupUi(self)
        self.mem=mem
        self.parent=parent
        
        self.sources=SetSources(self.mem)#All sources
        self.sources.append(WorkerYahooHistorical, self.wyahoohistorical)
        self.sources.append(WorkerYahoo, self.wyahoo)
        self.sources.append(WorkerMercadoContinuo,self.wmc)
        self.sources.append(WorkerMorningstar, self.wmorningstar)
        self.sources.runs_finished.connect(self.runners_finished)
#        
#        for s in self.sources.arr:#Conects after finishing a wdgSource
#            s.ui.finished.connect(self.after_source_stop)
        
        self.on_chkUserOnly_stateChanged(self.chkUserOnly.checkState())
    


    def running_sources_run(self):
        """Used to set unenabled fine"""
        for s in self.sources.runners:
            if s.ui.status==0:
                s.prepare()
            
        self.mem.frmMain.actionsEnabled(False)
        #Disables  button when wdgSources cmdRun are disabled
        
        if self.wyahoo.cmdRun.isEnabled()==False and self.wmc.cmdRun.isEnabled()==False:
            self.cmdIntraday.setEnabled(False)
        if self.wyahoohistorical.cmdRun.isEnabled()==False and self.wmorningstar.isEnabled()==False:
            self.cmdDaily.setEnabled(False)
        if self.cmdDaily.isEnabled()==False and self.cmdIntraday.isEnabled()==False:
            self.cmdAll.setEnabled(False)

        QCoreApplication.processEvents()   
        
        for s in self.sources.runners:
            if s.ui.status==1:
                s.ui.on_cmdRun_released()
        
    def runners_finished(self):
        self.mem.frmMain.actionsEnabled(True)
        self.mem.data.reload_prices()
        QCoreApplication.processEvents()       
        self.sources.runners=[]
                    
        
    def on_chkUserOnly_stateChanged(self, state):
        for s in self.sources.arr:
            s.ui.chkUserOnly.setCheckState(state)
        
    def on_cmdIntraday_released(self):
        self.sources.append_runners(self.wyahoo.source)
        self.sources.append_runners(self.wmc.source)
        
        self.running_sources_run()
            
        
    def on_cmdDaily_released(self):
        self.sources.append_runners(self.wyahoohistorical.source)
        self.sources.append_runners(self.wmorningstar.source)
        
        self.running_sources_run()

    def on_cmdAll_released(self):        
        for s in sources.arr:
            self.sources.append_runners(s)
        self.running_sources_run()
