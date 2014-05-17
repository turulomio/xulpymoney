from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys
from Ui_frmMain import *
from frmAbout import *
from libxulpymoney import *
from frmAccess import *
from wdgTotal import *
from wdgDividendsReport import *
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
    def __init__(self, mem, parent = 0,  flags = False):
        QMainWindow.__init__(self, None)
        self.setupUi(self)
        self.showMaximized()
        self.setWindowTitle(self.trUtf8("Xulpymoney 2010-{0} ©".format(version[:4])))
        
        self.mem=mem
        
        self.w=QWidget()       
        
        access2=frmAccess(self.mem, 1)        
        access2.exec_()
        if access2.result()==QDialog.Rejected:
            self.on_actionSalir_activated()
            sys.exit(1)

        access=frmAccess(self.mem, 2)        
        access.exec_()
        
        if access.result()==QDialog.Rejected:
            self.on_actionSalir_activated()
            sys.exit(1)

        
        self.mem.actualizar_memoria() ##CARGA TODOS LOS DATOS Y LOS VINCULA       
        
        
        print ("Protecting products needed in xulpymoney")
        cur=self.mem.con.cursor()
        cur.execute("select distinct(mystocksid) from inversiones;")
        ids2protect=[]
        for row in cur:
            ids2protect.append(row[0])
        if len(ids2protect)>0:
            Product(self.mem).changeDeletable(  ids2protect,  False)
        self.mem.conms.commit()
        
        
        #Mantenimiento(self.mem).regenera_todas_opercuentasdeoperinversiones()

        
    @QtCore.pyqtSlot()  
    def on_actionSalir_activated(self):
        self.mem.__del__()
        print ("App correctly closed")
        self.close()
        
    @pyqtSignature("")
    def on_actionAcercaDe_activated(self):
        fr=frmAbout(self.mem, self, "frmabout")
        fr.open()

    @QtCore.pyqtSlot()  
    def on_actionBancos_activated(self):
        self.w.close()
        self.w=wdgBancos(self.mem)
                
        self.layout.addWidget(self.w)
        self.w.show()
        
    @QtCore.pyqtSlot()  
    def on_actionConceptos_activated(self):
        self.w.close()
        self.w=wdgConceptos(self.mem)
                
        self.layout.addWidget(self.w)
        self.w.show()
        
    @QtCore.pyqtSlot()  
    def on_actionCuentas_activated(self):
        self.w.close()
        self.w=wdgCuentas(self.mem)
                
        self.layout.addWidget(self.w)
        self.w.show()
    
    @QtCore.pyqtSlot()  
    def on_actionMemoria_activated(self):        
        self.mem.data.reload()
        
        
    @QtCore.pyqtSlot()  
    def on_actionDividendsReport_activated(self):
        self.w.close()
        self.w=wdgDividendsReport(self.mem)
                
        self.layout.addWidget(self.w)
        self.w.show()
        
    @QtCore.pyqtSlot()  
    def on_actionInformeClases_activated(self):
        self.w.close()
        self.w=wdgInformeClases(self.mem)
                
        self.layout.addWidget(self.w)
        self.w.show()

    @QtCore.pyqtSlot()  
    def on_actionInformeHistorico_activated(self):
        self.w.close()
        self.w=wdgInformeHistorico(self.mem)
                
        self.layout.addWidget(self.w)
        self.w.show()        
            
    @QtCore.pyqtSlot()  
    def on_actionInformeTotal_activated(self):
        self.w.close()
        self.w=wdgTotal(self.mem)
                
        self.layout.addWidget(self.w)
        self.w.show()

    @QtCore.pyqtSlot()  
    def on_actionEstudioTAE_activated(self):
        self.w.close()
        self.w=wdgAPR(self.mem)
              
        self.layout.addWidget(self.w)
        self.w.show()
        
    @QtCore.pyqtSlot()  
    def on_actionHelp_activated(self):
        w=frmHelp(self.mem)
        w.exec_()
    @QtCore.pyqtSlot()  
    def on_actionIndexRange_activated(self):
        self.w.close()
        self.w=wdgIndexRange(self.mem)
                
        self.layout.addWidget(self.w)
        self.w.show()

    @QtCore.pyqtSlot()  
    def on_actionInversiones_activated(self):
        self.w.close()
        self.w=wdgInversiones(self.mem)
               
        self.layout.addWidget(self.w)
        self.w.show()
        
    @QtCore.pyqtSlot()  
    def on_actionInvestmentsOperations_activated(self):
        self.w.close()
        self.w=wdgInvestmentsOperations(self.mem)
        self.layout.addWidget(self.w)
        self.w.show()

    @QtCore.pyqtSlot()  
    def on_actionTablasAuxiliares_activated(self):
        w=frmTablasAuxiliares(self.mem)
        w.exec_()
        
    @QtCore.pyqtSlot()  
    def on_actionSettings_activated(self):
        w=frmSettings(self.mem)
        w.exec_()
        self.retranslateUi(self)

    @QtCore.pyqtSlot()  
    def on_actionTransferencia_activated(self):
        w=frmTransferencia(self.mem)
        w.exec_()
        self.on_actionCuentas_activated()

#    def closeEvent(self,  event):
#        self.on_actionSalir_activated()
