from PyQt5.QtCore import *
from PyQt5.QtGui import *
from Ui_frmQuotesIBM import *
from libxulpymoney import *
from wdgDatetime import *

class frmQuotesIBM(QDialog, Ui_frmQuotesIBM):
    def __init__(self, mem, product,  quote=None,   parent = None, name = None, modal = False):
        # tipo 1 - Insertar quote=None
        # tipo2 - Modificar quote!=None
        QDialog.__init__(self,  parent)
        self.setupUi(self)   
        self.product=product
        self.mem=mem
        self.lblInvestment.setText("{0} ({1})".format(self.product.name,  self.product.id))
        
        if quote==None:
            self.type="insert"
            self.quote=None
            if self.product.type.id in (2, 8):
                self.chkNone.setCheckState(Qt.Checked)       
            else:
                self.wdgDT.set(self.mem)
        else:
            self.type="update"
            self.quote=quote
            self.wdgDT.set(self.mem, quote.datetime, self.mem.localzone)
            if self.quote.datetime.microsecond!=5:
                self.chkCanBePurged.setCheckState(Qt.Unchecked)
            self.wdgDT.setEnabled(False)
            self.chkNone.setEnabled(False)
        
   

    def on_chkNone_stateChanged(self, state):
        if state==Qt.Checked:      
            self.wdgDT.set(self.mem, dt(datetime.date.today(), self.product.stockmarket.closes, self.product.stockmarket.zone), self.product.stockmarket.zone)
            self.wdgDT.teTime.setEnabled(False)
            self.wdgDT.cmbZone.setEnabled(False)
            self.wdgDT.cmdNow.setEnabled(False)
            self.wdgDT.teMicroseconds.setEnabled(False)
        else:
            self.wdgDT.teTime.setEnabled(True)
            self.wdgDT.cmbZone.setEnabled(True)
            self.wdgDT.cmdNow.setEnabled(True)
            self.wdgDT.teMicroseconds.setEnabled(True)

        
    @pyqtSlot()
    def on_buttonbox_accepted(self):
        if self.txtQuote.decimal()==None:
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.tr("Incorrect data. Try again."))
            m.exec_()    
            return
        if self.type=="insert":                        
            if self.chkCanBePurged.checkState()==Qt.Unchecked:#No puede ser purgado
                self.wdgDT.teMicroseconds.setValue(5)
            self.quote=Quote(self.mem).init__create(self.product, self.wdgDT.datetime(), self.txtQuote.decimal())
            self.quote.save()
        else:#update
            self.quote.quote=self.txtQuote.decimal()
            self.quote.save()
        self.mem.con.commit()
        
        self.accept()

    @pyqtSlot()
    def on_buttonbox_rejected(self):
        self.reject()#No haría falta pero para recordar que hay buttonbox
