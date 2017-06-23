from PyQt5.QtCore import Qt, QCoreApplication
from PyQt5.QtWidgets import QWidget
from Ui_wdgQuotesUpdate import Ui_wdgQuotesUpdate
from libsources import WorkerMorningstar, WorkerGoogle, WorkerGoogleHistorical, SetSources
#from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor,   as_completed

class wdgQuotesUpdate(QWidget, Ui_wdgQuotesUpdate):
    def __init__(self, mem,  parent = None, name = None):
        QWidget.__init__(self,  parent)
        self.setupUi(self)
        self.mem=mem
        self.parent=parent
        
        self.sources=SetSources(self.mem)#All sources
        self.sources.append(WorkerGoogleHistorical, self.wgooglehistorical)
        self.sources.append(WorkerGoogle, self.wgoogle)
        self.sources.append(WorkerMorningstar, self.wmorningstar)
        for s in self.sources.arr:
            s.statusChanged.connect(self.on_source_statusChanged)
        
        self.on_chkUserOnly_stateChanged(self.chkUserOnly.checkState())
        self.wgooglehistorical.chkUserOnly.setCheckState(Qt.Unchecked)#Google historical must check all products
        
    


    def running_sources_run(self):
        self.mem.frmMain.actionsEnabled(False)
        for s in self.sources.runners:
            s.setSQL(s.ui.chkUserOnly.isChecked())
        
        #MAIL O DESACTIVAR TODO O CONTROLAR EL ESTADO
        if self.wgoogle.cmdRun.isEnabled()==False:
            self.cmdIntraday.setEnabled(False)
        if self.wgooglehistorical.cmdRun.isEnabled()==False and self.wmorningstar.isEnabled()==False:
            self.cmdDaily.setEnabled(False)
        if self.cmdDaily.isEnabled()==False and self.cmdIntraday.isEnabled()==False:
            self.cmdAll.setEnabled(False)

        QCoreApplication.processEvents()   
        
        for s in self.sources.runners:
            s.ui.on_cmdRun_released()
            
#        futures=[]
#        with ProcessPoolExecutor(max_workers=4) as executor:
#            for s in self.sources.runners:
#                futures.append(executor.submit(s.ui.on_cmdRun_released))
#            for i,  future in enumerate(as_completed(futures)):
#                QCoreApplication.processEvents()    
#                self.mem.frmMain.update()
        
    def on_source_statusChanged(self, status):
        if status==3:#Finished
            if self.sources.allFinished():
                print ("wdgQuotesUpdate runners finished")
                self.mem.frmMain.actionsEnabled(True)
                print ("wdgQuotesUpdate reloading prices")
                self.mem.data.load()
                QCoreApplication.processEvents()       
                self.sources.runners=[]
                    
        
    def on_chkUserOnly_stateChanged(self, state):
        for s in self.sources.arr:
            s.ui.chkUserOnly.setCheckState(state)
        
    def on_cmdIntraday_released(self):
        self.sources.append_runners(self.wgoogle.source)
        
        self.running_sources_run()
            
        
    def on_cmdDaily_released(self):
        self.sources.append_runners(self.wgooglehistorical.source)
        self.sources.append_runners(self.wmorningstar.source)
        
        self.running_sources_run()

    def on_cmdAll_released(self):        
        for s in self.sources.arr:
            self.sources.append_runners(s)
            
        self.running_sources_run()
