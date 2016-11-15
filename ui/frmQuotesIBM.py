from PyQt5.QtCore import *
from PyQt5.QtGui import *
from Ui_frmQuotesIBM import *
from libxulpymoney import *
from wdgDatetime import *

class frmQuotesIBM(QDialog, Ui_frmQuotesIBM):
    def __init__(self, mem, product,  quote=None,   parent = None):
        QDialog.__init__(self,  parent)
        self.setupUi(self)   
        self.product=product
        self.mem=mem
        self.lblInvestment.setText("{0} ({1})".format(self.product.name,  self.product.id))
        self.quote=quote
        
        for s in self.mem.stockmarkets.arr:
            print (s.name,    s.today_starts() , "||||||||||||||||", s.today_closes() , "||||||||||||||||", dt_changes_tz(s.today_starts(), self.mem.localzone) , "||||||||||||||||",  dt_changes_tz(s.today_closes(), self.mem.localzone))
        
        
        
        if quote==None:#Insert
            if self.product.type.id in (2, 8):
                self.chkNone.setCheckState(Qt.Checked)       
            else:
                if self.mem.localzone.now()>=self.product.stockmarket.today_closes():#Si ya ha cerrado la bolsa
                    today_closes=dt_changes_tz(s.today_closes(), self.mem.localzone)
                    self.wdgDT.setCombine(self.mem,  today_closes.date(), today_closes.time(),  self.mem.localzone)
                else:
                    self.wdgDT.set(self.mem)
        else:#Update
            self.wdgDT.set(self.mem, quote.datetime, self.mem.localzone)
            if self.quote.datetime.microsecond!=5:
                self.chkCanBePurged.setCheckState(Qt.Unchecked)
            self.wdgDT.setEnabled(False)
            self.chkNone.setEnabled(False)

    def on_chkNone_stateChanged(self, state):
        if state==Qt.Checked:      
            self.wdgDT.set(self.mem, dt(self.wdgDT.date(), self.product.stockmarket.closes, self.product.stockmarket.zone), self.product.stockmarket.zone)
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
            m.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
            m.setIcon(QMessageBox.Information)
            m.setText(self.tr("Incorrect data. Try again."))
            m.exec_()    
            return
        if self.quote==None:#insert              
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
