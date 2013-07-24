from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Ui_frmDividendosIBM import *
from libxulpymoney import *
from decimal import Decimal

class frmDividendosIBM(QDialog, Ui_frmDividendosIBM):
    def __init__(self, cfg, inversion, dividendo=None,  parent=None):
        """
        Si dividendo es None se insertar
        Si dividendo es un objeto se modifica"""
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.cfg=cfg
        self.dividendo=dividendo
        self.inversion=inversion
        
        self.neto=0
        self.tpc=0
        if dividendo==None:#insertar
            self.dividendo=Dividendo(self.cfg)
            self.dividendo.inversion=inversion
            self.cmd.setText(self.trUtf8("Insertar nuevo dividendo"))
        else:#modificar
            if self.dividendo.concepto.id==62:
                self.chk.setCheckState(Qt.Checked)            
            self.cal.setSelectedDate(self.dividendo.fecha)
            self.txtBruto.setText(str(self.dividendo.bruto))
            self.txtNeto.setText(str(self.dividendo.neto))
            self.txtRetencion.setText(str(self.dividendo.retencion))
            self.txtComision.setText(str(self.dividendo.comision))
            self.txtDPA.setText(str(self.dividendo.dpa))
            self.cmd.setText(self.trUtf8("Modificar dividendo"))
 
    def on_txtBruto_textChanged(self):
        self.calcular()
    def on_txtRetencion_textChanged(self):
        self.calcular()
    def on_txtComision_textChanged(self):
        self.calcular()
        
    def calcular(self):
        try:
            self.neto=Decimal(self.txtBruto.text())-Decimal(self.txtRetencion.text())-Decimal(self.txtComision.text())
            self.tpc=100*Decimal(self.txtRetencion.text())/Decimal(self.txtBruto.text())
            self.txtNeto.setText(str(self.neto))
            self.lblTPC.setText(self.trUtf8("{0} % de retención".format(round(self.tpc, 2))))
            self.cmd.setEnabled(True)
        except:
            self.txtNeto.setText(self.trUtf8("Error calculando"))
            self.lblTPC.setText(self.trUtf8("Error calculando"))
            self.cmd.setEnabled(False)
 


    def on_cmd_pressed(self):
        try:
            if self.chk.checkState()==Qt.Checked:
                self.dividendo.concepto=self.cfg.conceptos.find(62)
            else:
                self.dividendo.concepto=self.cfg.conceptos.find(39)
            self.dividendo.bruto=Decimal(self.txtBruto.text())
            self.dividendo.retencion=Decimal(self.txtRetencion.text())
            self.dividendo.neto=self.neto
            self.dividendo.dpa=Decimal(self.txtDPA.text())
            self.dividendo.fecha=self.cal.selectedDate().toPyDate()
            self.dividendo.comision=Decimal(self.txtComision.text())
        except:            
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.trUtf8("Error al introducir los datos. Compruébelos"))
            m.exec_()    
            return
        
        if self.dividendo.bruto<0 or self.dividendo.retencion<0 or self.dividendo.neto<0 or self.dividendo.dpa<0 or self.dividendo.comision<0:
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.trUtf8("Todos los campos deben ser positivos. Revíselos"))
            m.exec_()    
            return
        
        
        con=self.cfg.connect_xulpymoney()
        cur = con.cursor()
        self.dividendo.save(cur)
        con.commit()
        cur.close()      
        self.cfg.disconnect_xulpymoney(con)                  
        self.done(0)
