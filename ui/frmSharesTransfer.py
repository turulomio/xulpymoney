from PyQt5.QtCore import *
from PyQt5.QtGui import *
from Ui_frmSharesTransfer import *
from libxulpymoney import *

class frmSharesTransfer(QDialog, Ui_frmSharesTransfer):
    def __init__(self, mem, origen,   parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        self.origen=origen#Clase inversión
        self.lbl.setText(self.tr("Shares transfer from\n{0}").format(self.origen.name))
        self.txtAcciones.setText(str(self.origen.acciones()))
        self.mem.data.investments_active.qcombobox_same_investmentmq(self.combo, self.origen.product)

    @QtCore.pyqtSlot()  
    def on_buttons_accepted(self):
        destino=self.mem.data.investments_active.find_by_id(self.combo.itemData(self.combo.currentIndex()))
        if self.origen==destino:            
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.tr("Origin and destiny transfer can't be the same"))
            m.exec_()  
            return
            
        if self.txtComision.decimal()<Decimal('0'):
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.tr("Comission must be a positive amount"))
            m.exec_()
            return            
            
        if self.mem.data.investments_active.traspaso_valores(self.origen, destino, self.txtAcciones.decimal(), self.txtComision.decimal())==False: 
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.tr("The shares transfer couldn't be done"))
            m.exec_()  
        self.accept()
        

    @QtCore.pyqtSlot()  
    def on_buttons_rejected(self):
        self.reject()
