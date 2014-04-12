from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Ui_frmTraspasoValores import *
from libxulpymoney import *

class frmTraspasoValores(QDialog, Ui_frmTraspasoValores):
    def __init__(self, cfg, origen,   parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.cfg=cfg
        self.origen=origen#Clase inversión
        self.lbl.setText(self.trUtf8("Traspaso de valores desde\n{0}".format(self.origen.name)))
        self.txtAcciones.setText(str(self.origen.acciones()))
        self.cfg.data.inversiones_active.qcombobox_same_investmentmq(self.combo, self.origen.product)

    @QtCore.pyqtSlot()  
    def on_buttons_accepted(self):
        destino=self.cfg.data.inversiones_active.find(self.combo.itemData(self.combo.currentIndex()))
        if self.origen==destino:            
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.trUtf8("El origen  y el destino del traspaso de valores no puede ser el mismo"))
            m.exec_()  
            return
            
        if self.txtComision.decimal()<Decimal('0'):
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.trUtf8("La comisión debe ser un número positivo"))
            m.exec_()
            return            
            
        if self.cfg.data.inversiones_active.traspaso_valores(self.origen, destino, self.txtAcciones.decimal(), self.txtComision.decimal())==False: 
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.trUtf8("No se ha podido hacer el traspaso de valores"))
            m.exec_()  
        self.accept()
        

    @QtCore.pyqtSlot()  
    def on_buttons_rejected(self):
        self.reject()
