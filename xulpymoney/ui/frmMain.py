import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Ui_frmMain import *
from frmAbout import *
from core import *
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
        
        self.cfg=ConfigXulpy()
        
        self.w=QWidget()       
        
        access=frmAccess(self.cfg, self.cfg.inifile)        
        icon = QtGui.QIcon()
        pix=QtGui.QPixmap(":xulpymoney/coins.png")
        icon.addPixmap(pix, QtGui.QIcon.Normal, QtGui.QIcon.Off)
        access.setWindowIcon(icon)        
        access.lbl.setPixmap(pix)
        access.setWindowTitle(self.trUtf8("Xulpymoney - Acceso"))
        QObject.connect(access.cmdYN, SIGNAL("rejected()"), self, SLOT("on_actionSalir_activated()"))
        access.exec_()

        self.cfg.con=self.cfg.connect_xulpymoney()
        cur = self.cfg.con.cursor()                   
        self.cfg.conmq=self.cfg.connect_myquotes()
        curmq=self.cfg.conmq.cursor()        
        
        self.cfg.actualizar_memoria(cur, curmq) ##CARGA TODOS LOS DATOS Y LOS VINCULA       
        
        ids2protect=[i.id for i in self.cfg.mqinversiones()]##Protege registros de myquotes
        if len(ids2protect)>0:
            Investment.changeDeletable(curmq,  ids2protect,  False)
        self.cfg.conmq.commit()

        curmq.close()
        cur.close()     
        
        self.mytimer = QTimer()
        QObject.connect(self.mytimer, SIGNAL("timeout()"), self.update_quotes)
        self.mytimer.start(120000)      
        

        
                   
    def update_quotes(self):
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor));
        mq=self.cfg.connect_myquotes()
        curmq=mq.cursor()       
        print("Actualizando quotes",  datetime.datetime.now()) 
        self.mytimer.stop()
        self.cfg.indicereferencia.quotes.get_basic(curmq)
        for k, v in self.cfg.dic_mqinversiones.items():
            QCoreApplication.processEvents()
            v.quotes.get_basic(curmq)
        curmq.close()
        self.cfg.disconnect_myquotes(mq)
        self.mytimer.start()
        QApplication.restoreOverrideCursor ()
        
    @pyqtSignature("")
    def on_actionAcercaDe_activated(self):
        fr=frmAbout(self, "frmabout")
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
        curmq=mq.cursor()        
        
        self.cfg.actualizar_memoria(cur, curmq) 

        curmq.close()
        self.cfg.disconnect_myquotes(mq)
        cur.close()     
        self.cfg.disconnect_xulpymoney(con)        
    
    @QtCore.pyqtSlot()      
    def on_actionSalir_activated(self):
        self.cfg.__del__()
        sys.exit()

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

    def closeEvent(self,  event):
        self.on_actionSalir_activated()
