from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys
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
from wdgInvestmentsOperations import *
from frmTablasAuxiliares import *
from frmTransferencia import *
from frmSettings import *
from frmHelp import *

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
        access2.exec_()
        if access2.result()==QDialog.Rejected:
            self.on_actionSalir_activated()
            sys.exit(1)

        access=frmAccess(self.cfg, 2)        
        access.exec_()
        
        if access.result()==QDialog.Rejected:
            self.on_actionSalir_activated()
            sys.exit(1)

        
        self.cfg.actualizar_memoria() ##CARGA TODOS LOS DATOS Y LOS VINCULA       
        
        
        print ("Protecting products needed in xulpymoney")
        cur=self.cfg.con.cursor()
        cur.execute("select distinct(mystocksid) from inversiones;")
        ids2protect=[]
        for row in cur:
            ids2protect.append(row[0])
        if len(ids2protect)>0:
            Product(self.cfg).changeDeletable(  ids2protect,  False)
        self.cfg.conms.commit()
        
        
    @QtCore.pyqtSlot()  
    def on_actionSalir_activated(self):
        self.cfg.__del__()
        print ("App correctly closed")
        self.close()
        
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
    
    @QtCore.pyqtSlot()  
    def on_actionMemoria_activated(self):        
        self.cfg.data.reload()
        
        
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
    def on_actionHelp_activated(self):
        w=frmHelp(self.cfg)
        w.exec_()
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
    def on_actionProductsOperations_activated(self):
        self.w.close()
        self.w=wdgProductsOperations(self.cfg)
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
