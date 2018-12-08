from PyQt5.QtWidgets import QDialog
from decimal import Decimal
from xulpymoney.libxulpymoney import HlContract
from xulpymoney.libxulpymoneyfunctions import qmessagebox
from xulpymoney.libxulpymoneytypes import eMoneyCurrency
from xulpymoney.ui.Ui_frmHlContractAdd import Ui_frmHlContractAdd

class frmHlContractAdd(QDialog, Ui_frmHlContractAdd):
    def __init__(self, mem, investment, hlcontract=None,  parent=None):
        """
        Si dividend es None se insertar
        Si dividend es un objeto se modifica"""
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        self.investment=investment
        self.hlcontract=hlcontract

        self.wdgDT.show_microseconds(False)
        self.wdgDT.show_timezone(False)
        if self.hlcontract==None:#insert
            self.hlcontract=HlContract(self.mem, self.investment)
            self.cmd.setText(self.tr("Add new High-Low contract"))
            self.wdgDT.set(self.mem, None, self.mem.localzone)
        else:#update
            self.wdgDT.set(self.mem, self.hlcontract.datetime, self.mem.localzone)
            self.txtGuarantee.setText(self.hlcontract.getGuarantee(eMoneyCurrency.Product).amount)
            self.txtAdjustment.setText(self.hlcontract.getAdjustment(eMoneyCurrency.Product).amount)
            self.txtInterest.setText(self.hlcontract.getInterest(eMoneyCurrency.Product).amount)
            self.txtCommission.setText(self.hlcontract.getCommission(eMoneyCurrency.Product).amount)
            self.cmd.setText(self.tr("Update High-Low contract"))

    def on_cmd_pressed(self):                        
        if self.txtCommission.decimal()<Decimal('0'):
            qmessagebox(self.tr("Commissions can't be a negative amount"))
            return
        
        try:
            self.hlcontract.setGuarantee(self.txtGuarantee.decimal())
            self.hlcontract.setAdjustment(self.txtAdjustment.decimal())
            self.hlcontract.setCommission(self.txtCommission.decimal())
            self.hlcontract.setInterest(self.txtInterest.decimal())
            self.hlcontract.datetime=self.wdgDT.datetime()
        except:
            qmessagebox(self.tr("Data error. Please check them."))
            return

        
        self.hlcontract.save()
        self.mem.con.commit()
        self.done(0)
