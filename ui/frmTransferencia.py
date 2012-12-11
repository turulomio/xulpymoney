## -*- coding: utf-8 -*-
#from apoyo import *

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Ui_frmTransferencia import *
#from apoyo import *
from core import *

class frmTransferencia(QDialog, Ui_frmTransferencia):
    def __init__(self, cfg, origen=None, destino=None,   parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.cfg=cfg
        
        self.origen=origen
        self.destino=destino
        
        cuentas=self.cfg.cuentas_activas()
        cuentas=sorted(cuentas, key=lambda c: c.name,  reverse=False) 
        for c in cuentas:
            self.cmbOrigen.addItem(c.name, c.id)
            self.cmbDestino.addItem(c.name, c.id)
        
        if origen!=None:
            self.cmbOrigen.setCurrentIndex(self.cmbOrigen.findData(origen.id))
        if destino!=None:
            self.cmbDestino.setCurrentIndex(self.cmbDestino.findData(destino.id))

    def on_cmd_pressed(self):
        try:
            fecha=self.calendar.selectedDate().toPyDate()
            id_origen=int(self.cmbOrigen.itemData(self.cmbOrigen.currentIndex()))
            id_destino=int(self.cmbDestino.itemData(self.cmbDestino.currentIndex()))
            importe=abs(Decimal(self.txtImporte.text()))
            comision=abs(Decimal(self.txtComision.text()))
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
        con=self.cfg.connect_xulpymoney()
        cur = con.cursor()    
        Cuenta().transferencia(cur,  fecha,  self.cfg.cuentas(id_origen), self.cfg.cuentas(id_destino),  importe,  comision)
        con.commit()     
        cur.close()     
        self.cfg.disconnect_xulpymoney(con)        
        self.done(0)
