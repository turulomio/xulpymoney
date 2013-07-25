from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Ui_frmQuotesIBM import *
from libxulpymoney import *

class frmQuotesIBM(QDialog, Ui_frmQuotesIBM):
    def __init__(self, cfg, investment,  selDate=None,   parent = None, name = None, modal = False):
        # tipo 1 - Insertar selDate=None
        # tipo2 - Modificar selDate!=None
        QDialog.__init__(self,  parent)
        self.setupUi(self)   
        self.investment=investment
        self.cfg=cfg
        self.lblInversion.setText("{0} ({1})".format(self.investment.name,  self.investment.id))
        t=datetime.datetime.now()
        self.txtTime.setTime(QTime(t.hour, t.minute))

        self.cfg.zones.load_qcombobox(self.cmbZone, self.cfg.localzone)
        if self.investment.type.id in (2, 8):
            self.chkNone.setCheckState(Qt.Checked)            

    def on_chkNone_stateChanged(self, state):
        if state==Qt.Checked:          
            self.txtTime.setTime(self.investment.bolsa.close)
            self.txtTime.setEnabled(False)
        else:
            t=datetime.datetime.now()
            self.txtTime.setTime(QTime(t.hour, t.minute))
            self.txtTime.setEnabled(True)
            


    def on_cmd_pressed(self):
        try:
            fecha=self.calendar.selectedDate().toPyDate()
            quote=float(self.txtQuote.text())
            zone=self.cfg.zones.find(self.cmbZone.currentText())
        except:
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.trUtf8("Datos incorrectos. Vuelva a introducirlos"))
            m.exec_()    
            return
        if self.chkNone.checkState()==Qt.Checked:
            da=dt(fecha, self.investment.bolsa.close.replace(microsecond=4), self.investment.bolsa.zone)
        else:
            time=self.txtTime.time().toPyTime()
            da=dt(fecha, time, zone)

        mq=Quote(self.cfg).init__create(self.investment, da, quote)
        mq.save()
        self.cfg.conms.commit()
        
        self.done(0)
