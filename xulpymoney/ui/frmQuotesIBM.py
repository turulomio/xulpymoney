from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Ui_frmQuotesIBM import *
from libxulpymoney import *

class frmQuotesIBM(QDialog, Ui_frmQuotesIBM):
    def __init__(self, mem, product,  quote=None,   parent = None, name = None, modal = False):
        # tipo 1 - Insertar quote=None
        # tipo2 - Modificar quote!=None
        QDialog.__init__(self,  parent)
        self.setupUi(self)   
        self.product=product
        self.mem=mem
        self.lblInversion.setText("{0} ({1})".format(self.product.name,  self.product.id))
        
        if quote==None:
            self.type="insert"
            self.quote=None
            t=self.mem.localzone.now()
            self.txtTime.setTime(QTime(t.hour, t.minute))
            self.mem.zones.load_qcombobox(self.cmbZone, self.mem.localzone)
            if self.product.type.id in (2, 8):
                self.chkNone.setCheckState(Qt.Checked)         
        else:
            self.type="update"
            self.quote=quote
            self.calendar.setSelectedDate(self.quote.datetime.date())
            self.txtTime.setTime(QTime(self.quote.datetime.hour, self.quote.datetime.minute))
            self.mem.zones.load_qcombobox(self.cmbZone, quote.product.bolsa.zone)
            if self.quote.datetime.microsecond!=5:
                self.chkCanBePurged.setCheckState(Qt.Unchecked)
            self.calendar.setEnabled(False)
            self.txtTime.setEnabled(False)
            self.chkNone.setEnabled(False)
            self.cmbZone.setEnabled(False)
        
   

    def on_chkNone_stateChanged(self, state):
        if state==Qt.Checked:          
            self.txtTime.setTime(self.product.bolsa.closes)
            self.txtTime.setEnabled(False)
        else:
            t=datetime.datetime.now()
            self.txtTime.setTime(QTime(t.hour, t.minute))
            self.txtTime.setEnabled(True)
            

        
    @pyqtSignature("")
    def on_buttonbox_accepted(self):
        if self.txtQuote.decimal()==None:
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.trUtf8("Datos incorrectos. Vuelva a introducirlos"))
            m.exec_()    
            return
        if self.type=="insert":        
            try:
                fecha=self.calendar.selectedDate().toPyDate()
                zone=self.mem.zones.find(self.cmbZone.currentText())
            except:
                m=QMessageBox()
                m.setIcon(QMessageBox.Information)
                m.setText(self.trUtf8("Datos incorrectos. Vuelva a introducirlos"))
                m.exec_()    
                return
            
            if self.chkNone.checkState()==Qt.Checked:
                da=dt(fecha, self.product.bolsa.closes, self.product.bolsa.zone)
            else:
                time=self.txtTime.time().toPyTime()
                da=dt(fecha, time, zone)
                
            if self.chkCanBePurged.checkState()==Qt.Unchecked:#No puede ser purgado
                da=da.replace(microsecond=5)

            self.quote=Quote(self.mem).init__create(self.product, da, self.txtQuote.decimal())
            self.quote.save()
        else:#update
            self.quote.quote=self.txtQuote.decimal()
            self.quote.save()
        self.mem.conms.commit()
        
        self.accept()

    @pyqtSignature("")
    def on_buttonbox_rejected(self):
        self.reject()#No haría falta pero para recordar que hay buttonbox
