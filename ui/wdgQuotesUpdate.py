from PyQt5.QtCore import *
from PyQt5.QtGui import *
from Ui_wdgQuotesUpdate import *
from wdgSource import *

class wdgQuotesUpdate(QWidget, Ui_wdgQuotesUpdate):
    def __init__(self, mem,  parent = None, name = None):
        QWidget.__init__(self,  parent)
        self.setupUi(self)
        self.mem=mem
        self.parent=parent
        
        self.sources=SetWdgSources(self.mem)#All wdgSources agrupations

        self.wyahoo=wdgSource(self.mem, Sources.WorkerYahoo, self)    
        self.layIntraday.addWidget(self.wyahoo, 0, 0)
        self.sources.append(self.wyahoo)
        
        self.wmc=wdgSource(self.mem, Sources.WorkerMercadoContinuo, self)     
        self.layIntraday.addWidget(self.wmc, 1, 0)
        self.sources.append(self.wmc)
        
        self.wyahoohistorical=wdgSource(self.mem, Sources.WorkerYahooHistorical, self)   
        self.layDaily.addWidget(self.wyahoohistorical)
        self.sources.append(self.wyahoohistorical)
        
        self.wmorning=wdgSource(self.mem, Sources.WorkerMorningstar, self)
        self.layDaily.addWidget(self.wmorning)
        self.sources.append(self.wmorning)
        
        for s in self.sources.arr:#Conects after finishing a wdgSource
            s.finished.connect(self.after_source_stop)
        
        self.on_chkUserOnly_stateChanged(self.chkUserOnly.checkState())
        
    def running_sources_run(self):
        """Used to set unenabled fine"""
        for s in self.sources.runners:
            if s.status==0:
                s.prepare()
            
        self.mem.frmMain.actionsEnabled(False)
        #Disables  button when wdgSources cmdRun are disabled
        
        if self.wyahoo.cmdRun.isEnabled()==False and self.wmc.cmdRun.isEnabled()==False:
            self.cmdIntraday.setEnabled(False)
        if self.wyahoohistorical.cmdRun.isEnabled()==False and self.wmorning.isEnabled()==False:
            self.cmdDaily.setEnabled(False)
        if self.cmdDaily.isEnabled()==False and self.cmdIntraday.isEnabled()==False:
            self.cmdAll.setEnabled(False)

        QCoreApplication.processEvents()   
        
        for s in self.sources.runners:
            print (s,  self.sources.runners)
            if s.status==1:
                s.on_cmdRun_released()
        print ("FINISHED RUNNING_SOURCES_RUN, AQUI PROBLEMA")
        
    def on_chkUserOnly_stateChanged(self, state):
        for s in self.sources.arr:
            s.chkUserOnly.setCheckState(state)
        
    def on_cmdIntraday_released(self):
        self.sources.append_runners(self.wyahoo)
        self.sources.append_runners(self.wmc)
        
        self.running_sources_run()
            
        
    def on_cmdDaily_released(self):
        self.sources.append_runners(self.wyahoohistorical)
        self.sources.append_runners(self.wmorning)
        
        self.running_sources_run()

    def on_cmdAll_released(self):        
        for s in sources.arr:
            self.sources.append_runners(s)
        self.running_sources_run()

    def after_source_stop(self):
        print (self.sources.length_runners())
        self.sources.remove_finished()
        print (self.sources.length_runners())
                
        if self.sources.length_runners()==0:
            self.mem.frmMain.actionsEnabled(True)
            self.mem.data.reload_prices()
        QCoreApplication.processEvents()            
            
            
