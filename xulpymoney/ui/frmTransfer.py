from PyQt5.QtWidgets import QDialog
from xulpymoney.ui.Ui_frmTransfer import Ui_frmTransfer

from xulpymoney.objects.account import  Account
from xulpymoney.ui.myqwidgets import qmessagebox

class frmTransfer(QDialog, Ui_frmTransfer):
    def __init__(self, mem, origen=None, destino=None, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        
        self.origen=origen
        self.destino=destino
        
        self.mem.data.accounts_active().qcombobox(self.cmbOrigen,  origen)
        self.mem.data.accounts_active().qcombobox(self.cmbDestino,  destino)
        self.wdgDT.show_microseconds(False)
        self.wdgDT.setLocalzone(self.mem.localzone_name)
        self.wdgDT.set()


    def on_cmd_pressed(self):
        try:
            id_origen=int(self.cmbOrigen.itemData(self.cmbOrigen.currentIndex()))
            id_destino=int(self.cmbDestino.itemData(self.cmbDestino.currentIndex()))
            importe=abs(self.txtImporte.decimal())
            comision=abs(self.txtComision.decimal())
        except:
            qmessagebox(self.tr("Error adding data"))
            return            
        if id_origen==id_destino:
            qmessagebox(self.tr("Origin and destiny accounts can't be the same"))
            return 
            
        Account(self.mem).transferencia(self.wdgDT.datetime(),  self.mem.data.accounts_active().find_by_id(id_origen), self.mem.data.accounts_active().find_by_id(id_destino),  importe,  comision)
        self.mem.con.commit()##Para commit la transferencia   
        
        self.done(0)
