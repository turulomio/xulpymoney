from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Ui_frmQuotesIBM import *
from libxulpymoney import *

class frmQuotesIBM(QDialog, Ui_frmQuotesIBM):
    def __init__(self, cfg, investment,  quote=None,   parent = None, name = None, modal = False):
        # tipo 1 - Insertar quote=None
        # tipo2 - Modificar quote!=None
        QDialog.__init__(self,  parent)
        self.setupUi(self)   
        self.investment=investment
        self.cfg=cfg
        self.lblInversion.setText("{0} ({1})".format(self.investment.name,  self.investment.id))
        
        if quote==None:
            self.type="insert"
            self.quote=None
            t=self.cfg.localzone.now()
            self.txtTime.setTime(QTime(t.hour, t.minute))
            self.cfg.zones.load_qcombobox(self.cmbZone, self.cfg.localzone)
            if self.investment.type.id in (2, 8):
                self.chkNone.setCheckState(Qt.Checked)         
        else:
            self.type="update"
            self.quote=quote
            self.calendar.setSelectedDate(self.quote.datetime.date())
            self.txtTime.setTime(QTime(self.quote.datetime.hour, self.quote.datetime.minute))
            self.cfg.zones.load_qcombobox(self.cmbZone, quote.investment.bolsa.zone)
            if self.quote.datetime.microsecond!=5:
                self.chkCanBePurged.setCheckState(Qt.Unchecked)
            self.calendar.setEnabled(False)
            self.txtTime.setEnabled(False)
            self.chkNone.setEnabled(False)
            self.cmbZone.setEnabled(False)
        
   

    def on_chkNone_stateChanged(self, state):
        if state==Qt.Checked:          
            self.txtTime.setTime(self.investment.bolsa.closes)
            self.txtTime.setEnabled(False)
        else:
            t=datetime.datetime.now()
            self.txtTime.setTime(QTime(t.hour, t.minute))
            self.txtTime.setEnabled(True)
            

        
    @pyqtSignature("")
    def on_buttonbox_accepted(self):
        if self.type=="insert":        
            try:
                fecha=self.calendar.selectedDate().toPyDate()
                zone=self.cfg.zones.find(self.cmbZone.currentText())
            except:
                m=QMessageBox()
                m.setIcon(QMessageBox.Information)
                m.setText(self.trUtf8("Datos incorrectos. Vuelva a introducirlos"))
                m.exec_()    
                return
            
            if self.chkNone.checkState()==Qt.Checked:
                da=dt(fecha, self.investment.bolsa.closes, self.investment.bolsa.zone)
            else:
                time=self.txtTime.time().toPyTime()
                da=dt(fecha, time, zone)
                
            if self.chkCanBePurged.checkState()==Qt.Unchecked:#No puede ser purgado
                da=da.replace(microsecond=5)

            self.quote=Quote(self.cfg).init__create(self.investment, da, self.txtQuote.decimal())
            self.quote.save()
        else:#update
            self.quote.quote=self.txtQuote.decimal()
            self.quote.save()
        self.cfg.conms.commit()
        
        self.accept()

    @pyqtSignature("")
    def on_buttonbox_rejected(self):
        self.reject()#No har´ia falta pero para recordar que hay buttonbox
