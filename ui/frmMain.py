from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Ui_frmMain import *
from frmAbout import *
from libxulpymoney import *
from frmAccess import *
from wdgTotal import *
from wdgInformeDividendos import *
from wdgInformeClases import *
from wdgInformeHistorico import *
from wdgAPR import *
from wdgCuentas import *
from wdgConceptos import *
from wdgBancos import *
from wdgIndexRange import *
from wdgInversiones import *
from frmTablasAuxiliares import *
from frmTransferencia import *
from frmSettings import *

class frmMain(QMainWindow, Ui_frmMain):
    """Clase principal del programa"""
    def __init__(self, parent = 0,  flags = False):
        QMainWindow.__init__(self, None)
        self.setupUi(self)
        self.showMaximized()
        self.setWindowTitle(self.trUtf8("Xulpymoney 2010-{0} ©".format(version[:4])))
        
        self.cfg=ConfigXulpymoney()
        
        self.w=QWidget()       
        
        access2=frmAccess(self.cfg, 1)        
        QObject.connect(access2.cmdYN, SIGNAL("rejected()"), self, SLOT("close()"))
        access2.exec_()
        access=frmAccess(self.cfg, 2)        
        QObject.connect(access.cmdYN, SIGNAL("rejected()"), self, SLOT("close()"))
        access.exec_()

        
        self.cfg.actualizar_memoria() ##CARGA TODOS LOS DATOS Y LOS VINCULA       
        
        
        print ("Protecting investments needed in xulpymoney")
        cur=self.cfg.con.cursor()
        cur.execute("select distinct(myquotesid) from inversiones;")
        ids2protect=[]
        for row in cur:
            ids2protect.append(row[0])
        if len(ids2protect)>0:
            Investment(self.cfg).changeDeletable(  ids2protect,  False)
        self.cfg.conms.commit()
        
#        self.tupdatedata=TUpdateData(self.cfg)
#        self.tupdatedata.start()
#        
#        
#        self.mytimer = QTimer()
#        QObject.connect(self.mytimer, SIGNAL("timeout()"), self.update_quotes)
#        self.mytimer.start(60000)      
#
#    def update_quotes(self):
#        if self.tupdatedata.isAlive()==False:
#            QCoreApplication.processEvents()
#            self.tupdatedata=TUpdateData(self.cfg)
#            self.tupdatedata.start()      
                
    def __del__(self):
        print ("Saliendo de la aplicación")
        del self.cfg
        
    @pyqtSignature("")
    def on_actionAcercaDe_activated(self):
        fr=frmAbout(self.cfg, self, "frmabout")
        fr.open()

    @QtCore.pyqtSlot()  
    def on_actionBancos_activated(self):
        self.w.close()
        self.w=wdgBancos(self.cfg)
                
        self.layout.addWidget(self.w)
        self.w.show()
        
    @QtCore.pyqtSlot()  
    def on_actionConceptos_activated(self):
        self.w.close()
        self.w=wdgConceptos(self.cfg)
                
        self.layout.addWidget(self.w)
        self.w.show()
        
    @QtCore.pyqtSlot()  
    def on_actionCuentas_activated(self):
        self.w.close()
        self.w=wdgCuentas(self.cfg)
                
        self.layout.addWidget(self.w)
        self.w.show()
    
    def on_actionMemoria_activated(self):        
        con=self.cfg.connect_xulpymoney()
        cur = con.cursor()                   
        mq=self.cfg.connect_myquotes()
        curms=mq.cursor()        
        
        self.cfg.actualizar_memoria(cur, curms) 

        curms.close()
        self.cfg.disconnect_myquotes(mq)
        cur.close()     
        self.cfg.disconnect_xulpymoney(con)        
    
#    @QtCore.pyqtSlot()      
#    def on_actionSalir_activated(self):
#        self.cfg.__del__()
#        sys.exit()

    @QtCore.pyqtSlot()  
    def on_actionInformeDividendos_activated(self):
        self.w.close()
        self.w=wdgInformeDividendos(self.cfg)
                
        self.layout.addWidget(self.w)
        self.w.show()
        
    @QtCore.pyqtSlot()  
    def on_actionInformeClases_activated(self):
        self.w.close()
        self.w=wdgInformeClases(self.cfg)
                
        self.layout.addWidget(self.w)
        self.w.show()

    @QtCore.pyqtSlot()  
    def on_actionInformeHistorico_activated(self):
        self.w.close()
        self.w=wdgInformeHistorico(self.cfg)
                
        self.layout.addWidget(self.w)
        self.w.show()        
            
    @QtCore.pyqtSlot()  
    def on_actionInformeTotal_activated(self):
        self.w.close()
        self.w=wdgTotal(self.cfg)
                
        self.layout.addWidget(self.w)
        self.w.show()

    @QtCore.pyqtSlot()  
    def on_actionEstudioTAE_activated(self):
        self.w.close()
        self.w=wdgAPR(self.cfg)
              
        self.layout.addWidget(self.w)
        self.w.show()
        
    @QtCore.pyqtSlot()  
    def on_actionIndexRange_activated(self):
        self.w.close()
        self.w=wdgIndexRange(self.cfg)
                
        self.layout.addWidget(self.w)
        self.w.show()

    @QtCore.pyqtSlot()  
    def on_actionInversiones_activated(self):
        self.w.close()
        self.w=wdgInversiones(self.cfg)
               
        self.layout.addWidget(self.w)
        self.w.show()

    @QtCore.pyqtSlot()  
    def on_actionTablasAuxiliares_activated(self):
        w=frmTablasAuxiliares(self.cfg)
        w.exec_()
        
    @QtCore.pyqtSlot()  
    def on_actionSettings_activated(self):
        w=frmSettings(self.cfg)
        w.exec_()

    @QtCore.pyqtSlot()  
    def on_actionTransferencia_activated(self):
        w=frmTransferencia(self.cfg)
        w.exec_()
        self.on_actionCuentas_activated()

#    def closeEvent(self,  event):
#        self.on_actionSalir_activated()
