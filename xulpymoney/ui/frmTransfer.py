from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Ui_frmTransfer import *

from libxulpymoney import *

class frmTransfer(QDialog, Ui_frmTransfer):
    def __init__(self, mem, origen=None, destino=None,   parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        
        self.origen=origen
        self.destino=destino
        
        self.mem.data.cuentas_active.qcombobox(self.cmbOrigen,  origen)
        self.mem.data.cuentas_active.qcombobox(self.cmbDestino,  destino)


    def on_cmd_pressed(self):
        try:
            fecha=self.calendar.selectedDate().toPyDate()
            id_origen=int(self.cmbOrigen.itemData(self.cmbOrigen.currentIndex()))
            id_destino=int(self.cmbDestino.itemData(self.cmbDestino.currentIndex()))
            importe=abs(self.txtImporte.decimal())
            comision=abs(self.txtComision.decimal())
        except:
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.trUtf8("Se ha producido un error al introducir los datos"))
            m.exec_()             
            return            
        if id_origen==id_destino:
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.trUtf8("La cuenta origen y destino no puede ser la misma"))
            m.exec_()             
            return 
            
        Account(self.mem).transferencia(fecha,  self.mem.data.cuentas_active.find(id_origen), self.mem.data.cuentas_active.find(id_destino),  importe,  comision)
        self.mem.con.commit()##Para commit la transferencia   
        
        self.done(0)
