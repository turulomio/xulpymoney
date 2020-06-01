from PyQt5.QtCore import Qt,  pyqtSlot
from PyQt5.QtWidgets import QDialog
from xulpymoney.ui.Ui_frmQuotesIBM import Ui_frmQuotesIBM
from xulpymoney.objects.quote import Quote
from xulpymoney.datetime_functions import dtaware
from xulpymoney.ui.myqwidgets import qmessagebox
from xulpymoney.libxulpymoneytypes import eProductType

class frmQuotesIBM(QDialog, Ui_frmQuotesIBM):
    def __init__(self, mem, product,  quote=None,   parent = None):
        QDialog.__init__(self,  parent)
        self.setupUi(self)   
        self.product=product
        self.mem=mem
        self.lblInvestment.setText("{0} ({1})".format(self.product.name,  self.product.id))
        self.quote=quote

        if quote==None:#Insert
            if self.product.type.id in (eProductType.Fund, eProductType.PensionPlan):
                self.chkNone.setCheckState(Qt.Checked)       
            else:
                self.wdgDT.setLocalzone(self.mem.localzone_name)
                if self.product.type.id in (eProductType.CFD, eProductType.Future) and self.mem.localzone.now()>=self.product.stockmarket.dtaware_today_closes_futures():
                    self.wdgDT.set(self.product.stockmarket.dtaware_today_closes_futures(),  self.mem.localzone_name)
                elif self.product.type.id not in (eProductType.CFD, eProductType.Future) and self.mem.localzone.now()>=self.product.stockmarket.dtaware_today_closes():#Si ya ha cerrado la bolsa
                    self.wdgDT.set(self.product.stockmarket.dtaware_today_closes(),  self.mem.localzone_name)
                else:
                    self.wdgDT.set()
        else:#Update
            self.wdgDT.set(quote.datetime, self.mem.localzone_name)
            if self.quote.datetime.microsecond!=5:
                self.chkCanBePurged.setCheckState(Qt.Unchecked)
            self.wdgDT.setEnabled(False)
            self.chkNone.setEnabled(False)

    def on_chkNone_stateChanged(self, state):
        if state==Qt.Checked:      
            self.wdgDT.set(dtaware(self.wdgDT.date(), self.product.stockmarket.closes, self.product.stockmarket.zone.name), self.product.stockmarket.zone.name)
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
        if not self.txtQuote.isValid():
            qmessagebox(self.tr("Incorrect data. Try again."))
            return
        if self.quote==None:#insert
            if self.chkCanBePurged.checkState()==Qt.Unchecked:#No puede ser purgado
                self.wdgDT.teMicroseconds.setValue(5)
            self.quote=Quote(self.mem).init__create(self.product, self.wdgDT.datetime(), self.txtQuote.decimal())
            self.quote.save()
        else:#update
            self.quote.quote=self.txtQuote.decimal()
            self.quote.save()
        self.product.needStatus(1, downgrade_to=0)
        self.mem.con.commit()
        self.accept()

    @pyqtSlot()
    def on_buttonbox_rejected(self):
        self.reject()#No haría falta pero para recordar que hay buttonbox
