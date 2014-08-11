from PyQt4.QtCore import *
from PyQt4.QtGui import *
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
            self.wdgDT.set(self.mem)
            if self.product.type.id in (2, 8):
                self.chkNone.setCheckState(Qt.Checked)         
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
            self.wdgDT.teTime.setTime(self.product.stockexchange.closes)
            self.wdgDT.setZone(self.product.stockexchange.zone)
            self.wdgDT.teTime.setEnabled(False)
            self.wdgDT.cmbZone.setEnabled(False)
            self.wdgDT.cmdNow.setEnabled(False)
            self.wdgDT.teMicroseconds.setEnabled(False)
            self.wdgDT.teMicroseconds.setValue(0)
        else:
            self.wdgDT.set(self.mem)
            self.wdgDT.teTime.setEnabled(True)
            self.wdgDT.cmbZone.setEnabled(True)
            self.wdgDT.cmdNow.setEnabled(True)
            self.wdgDT.teMicroseconds.setEnabled(True)

        
    @pyqtSignature("")
    def on_buttonbox_accepted(self):
        if self.txtQuote.decimal()==None:
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.trUtf8("Datos incorrectos. Vuelva a introducirlos"))
            m.exec_()    
            return
        if self.type=="insert":        
#            try:
#                fecha=self.calendar.selectedDate().toPyDate()
#                zone=self.mem.zones.find(self.cmbZone.currentText())
#            except:
#                m=QMessageBox()
#                m.setIcon(QMessageBox.Information)
#                m.setText(self.trUtf8("Datos incorrectos. Vuelva a introducirlos"))
#                m.exec_()    
#                return
#            
#            if self.chkNone.checkState()==Qt.Checked:
#                da=dt(fecha, self.product.stockexchange.closes, self.product.stockexchange.zone)
#            else:
#                time=self.txtTime.time().toPyTime()
#                da=dt(fecha, time, zone)
                
            if self.chkCanBePurged.checkState()==Qt.Unchecked:#No puede ser purgado
                self.wdgDT.teMicroseconds.setValue(5)

            self.quote=Quote(self.mem).init__create(self.product, self.wdgDT.datetime(), self.txtQuote.decimal())
            self.quote.save()
        else:#update
            self.quote.quote=self.txtQuote.decimal()
            self.quote.save()
        self.mem.con.commit()
        
        self.accept()

    @pyqtSignature("")
    def on_buttonbox_rejected(self):
        self.reject()#No haría falta pero para recordar que hay buttonbox
