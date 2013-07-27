from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Ui_frmTransferencia import *

from libxulpymoney import *

class frmTransferencia(QDialog, Ui_frmTransferencia):
    def __init__(self, cfg, origen=None, destino=None,   parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.cfg=cfg
        
        self.origen=origen
        self.destino=destino
        
        self.load_data_from_db()
        self.data_cuentas.load_qcombobox(self.cmbOrigen,  origen)
        self.data_cuentas.load_qcombobox(self.cmbDestino,  destino)

    def load_data_from_db(self):
        inicio=datetime.datetime.now()
        self.data_ebs=SetEntidadesBancarias(self.cfg)
        self.data_ebs.load_from_db("select * from entidadesbancarias where eb_activa=true")
        self.data_cuentas=SetCuentas(self.cfg, self.data_ebs)
        self.data_cuentas.load_from_db("select * from cuentas where cu_activa=true")
        print("\n","Cargando data en frmTransferencia",  datetime.datetime.now()-inicio)

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
            
        Cuenta(self.cfg).transferencia(fecha,  self.data_cuentas.find(id_origen), self.data_cuentas.find(id_destino),  importe,  comision)
        self.cfg.con.commit()##Para commit la transferencia   
        
        self.done(0)
