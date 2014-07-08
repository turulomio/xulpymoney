from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys
from Ui_frmMain import *
from frmAbout import *
from libxulpymoney import *
from frmAccess import *
from wdgTotal import *
from wdgDividendsReport import *
from wdgInvestmentClasses import *
from wdgJointReport import *
from wdgAPR import *
from wdgAccounts import *
from wdgBanks import *
from wdgConcepts import *
from wdgCalculator import *
from wdgIndexRange import *
from wdgInvestments import *
from wdgInvestmentsOperations import *
from frmAuxiliarTables import *
from frmTransfer import *
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
        
        access2=frmAccess(self.mem, 1, self)
        access2.exec_()
        self.retranslateUi(self)
        if access2.result()==QDialog.Rejected:
            self.on_actionExit_activated()
            sys.exit(1)

        access=frmAccess(self.mem, 2, self)
        access.exec_()
        self.retranslateUi(self)
        
        if access.result()==QDialog.Rejected:
            self.on_actionExit_activated()
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
        
#        self.mem.data.load_inactives()
#        print ("==========================================")
#        Maintenance(self.mem).show_investments_status(datetime.date(2007, 2, 28))
#        print ("==========================================")
#        Maintenance(self.mem).show_investments_status(datetime.date(2007, 3, 30))
#        print ("==========================================")
#        Maintenance(self.mem).show_investments_status(datetime.date(2007, 4, 30))
#        print ("==========================================")

        
    @QtCore.pyqtSlot()  
    def on_actionExit_activated(self):
        self.mem.__del__()
        print ("App correctly closed")
        self.close()
        
    @pyqtSignature("")
    def on_actionAbout_activated(self):
        fr=frmAbout(self.mem, self, "frmabout")
        fr.open()

    @QtCore.pyqtSlot()  
    def on_actionBanks_activated(self):
        self.w.close()
        self.w=wdgBanks(self.mem)
                
        self.layout.addWidget(self.w)
        self.w.show()
        
    @QtCore.pyqtSlot()  
    def on_actionCalculator_activated(self):
        d=QDialog(self)        
        d.setFixedSize(670, 670)
        d.setWindowTitle(self.trUtf8("Investment calculator"))
        w=wdgCalculator(self.mem)
        lay = QVBoxLayout(d)
        lay.addWidget(w)
        d.exec_()
    @QtCore.pyqtSlot()  
    def on_actionConcepts_activated(self):
        self.w.close()
        self.w=wdgConcepts(self.mem)
                
        self.layout.addWidget(self.w)
        self.w.show()
        
    @QtCore.pyqtSlot()  
    def on_actionAccounts_activated(self):
        self.w.close()
        self.w=wdgAccounts(self.mem)
                
        self.layout.addWidget(self.w)
        self.w.show()
    
    @QtCore.pyqtSlot()  
    def on_actionMemory_activated(self):        
        self.mem.data.reload()
        
        
    @QtCore.pyqtSlot()  
    def on_actionDividendsReport_activated(self):
        self.w.close()
        self.w=wdgDividendsReport(self.mem)
                
        self.layout.addWidget(self.w)
        self.w.show()
        
    @QtCore.pyqtSlot()  
    def on_actionInvestmentsClasses_activated(self):
        self.w.close()
        self.w=wdgInvestmentClasses(self.mem)
                
        self.layout.addWidget(self.w)
        self.w.show()

    @QtCore.pyqtSlot()  
    def on_actionJointReport_activated(self):
        self.w.close()
        self.w=wdgJointReport(self.mem)
                
        self.layout.addWidget(self.w)
        self.w.show()        
            
    @QtCore.pyqtSlot()  
    def on_actionTotalReport_activated(self):
        self.w.close()
        self.w=wdgTotal(self.mem)
                
        self.layout.addWidget(self.w)
        self.w.show()

    @QtCore.pyqtSlot()  
    def on_actionReportAPR_activated(self):
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
    def on_actionInvestments_activated(self):
        self.w.close()
        self.w=wdgInvestments(self.mem)
               
        self.layout.addWidget(self.w)
        self.w.show()
        
    @QtCore.pyqtSlot()  
    def on_actionInvestmentsOperations_activated(self):
        self.w.close()
        self.w=wdgInvestmentsOperations(self.mem)
        self.layout.addWidget(self.w)
        self.w.show()

    @QtCore.pyqtSlot()  
    def on_actionAuxiliarTables_activated(self):
        w=frmAuxiliarTables(self.mem)
        w.exec_()
        
    @QtCore.pyqtSlot()  
    def on_actionSettings_activated(self):
        w=frmSettings(self.mem, self)
        w.exec_()
        self.retranslateUi(self)

    @QtCore.pyqtSlot()  
    def on_actionTransfer_activated(self):
        w=frmTransfer(self.mem)
        w.exec_()
        self.on_actionAccounts_activated()

#    def closeEvent(self,  event):
#        self.on_actionExit_activated()
