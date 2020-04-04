from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog
from xulpymoney.ui.Ui_frmSharesTransfer import Ui_frmSharesTransfer
from xulpymoney.ui.myqwidgets import qmessagebox
from decimal import Decimal

class frmSharesTransfer(QDialog, Ui_frmSharesTransfer):
    def __init__(self, mem, origen,   parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        self.origen=origen#Clase inversión
        self.lbl.setText(self.tr("Shares transfer from\n{0}").format(self.origen.name))
        self.txtAcciones.setText(str(self.origen.shares()))
        self.mem.data.investments_active().qcombobox_same_investmentmq(self.combo, self.origen.product)

    @pyqtSlot()  
    def on_buttons_accepted(self):
        destino=self.mem.data.investments_active().find_by_id(self.combo.itemData(self.combo.currentIndex()))
        if self.origen==destino:
            qmessagebox(self.tr("Origin and destiny transfer can't be the same"))
            return
            
        if self.txtComision.decimal()<Decimal('0'):
            qmessagebox(self.tr("Comission must be a positive amount"))
            return            
            
        if self.mem.data.investments_active().traspaso_valores(self.origen, destino, self.txtAcciones.decimal(), self.txtComision.decimal())==False: 
            qmessagebox(self.tr("The shares transfer couldn't be done"))
        self.accept()
        

    @pyqtSlot()  
    def on_buttons_rejected(self):
        self.reject()
