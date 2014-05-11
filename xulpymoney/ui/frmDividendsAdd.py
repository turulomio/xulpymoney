from PyQt4.QtCore import *
from PyQt4.QtGui import *
from libxulpymoney import *
from Ui_frmDividendsAdd import *

class frmDividendsAdd(QDialog, Ui_frmDividendsAdd):
    def __init__(self, cfg, inversion, dividend=None,  parent=None):
        """
        Si dividend es None se insertar
        Si dividend es un objeto se modifica"""
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.cfg=cfg
        self.dividend=dividend
        self.inversion=inversion
        
        self.neto=0
        self.tpc=0
        if dividend==None:#insertar
            if self.inversion.product.type.id in (7, 9):#Bonds
                self.cfg.conceptos.load_bonds_qcombobox(self.cmb)
            else:
                self.cfg.conceptos.load_dividend_qcombobox(self.cmb)
            self.dividend=Dividend(self.cfg)
            self.dividend.inversion=inversion
            self.cmd.setText(self.trUtf8("Insertar nuevo dividend"))
        else:#modificar 
            if self.inversion.product.type.id in (7, 9):#Bonds
                self.cfg.conceptos.load_bonds_qcombobox(self.cmb, self.dividend.concepto) 
            else:
                self.cfg.conceptos.load_dividend_qcombobox(self.cmb, self.dividend.concepto) 
            self.cal.setSelectedDate(self.dividend.fecha)
            self.txtBruto.setText(str(self.dividend.bruto))
            self.txtNeto.setText(str(self.dividend.neto))
            self.txtRetencion.setText(str(self.dividend.retencion))
            self.txtComision.setText(str(self.dividend.comision))
            self.txtDPA.setText(str(self.dividend.dpa))
            self.cmd.setText(self.trUtf8("Modificar dividend"))
 
    def on_txtBruto_textChanged(self):
        self.calcular()
    def on_txtRetencion_textChanged(self):
        self.calcular()
    def on_txtComision_textChanged(self):
        self.calcular()
        
    def calcular(self):
        try:
            if self.txtBruto.decimal()<Decimal(0):
                self.txtRetencion.setEnabled(False)
                self.txtDPA.setEnabled(False)
                self.txtComision.setEnabled(False)
                self.txtRetencion.setText(0)
                self.txtDPA.setText(0)
                self.txtComision.setText(0)
                self.neto=self.txtBruto.decimal()-self.txtComision.decimal()
                self.tpc=0
            else:
                self.txtRetencion.setEnabled(True)
                self.txtDPA.setEnabled(True)
                self.txtComision.setEnabled(True)
                self.neto=self.txtBruto.decimal()-self.txtRetencion.decimal()-self.txtComision.decimal()
                self.tpc=100*self.txtRetencion.decimal()/self.txtBruto.decimal()
            self.txtNeto.setText(str(self.neto))
            self.lblTPC.setText(self.trUtf8("{0} % de retención".format(round(self.tpc, 2))))
            self.cmd.setEnabled(True)
        except:
            self.txtNeto.setText(self.trUtf8("Error calculando"))
            self.lblTPC.setText(self.trUtf8("Error calculando"))
            self.cmd.setEnabled(False)
 


    def on_cmd_pressed(self):
        concepto=self.cfg.conceptos.find(self.cmb.itemData(self.cmb.currentIndex()))
        tipooperacion=concepto.tipooperacion
                        
        if tipooperacion.id==1 and (self.txtBruto.decimal()>Decimal('0') or self.txtNeto.decimal()>Decimal('0')):
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.trUtf8("Un gasto no puede tener un importe positivo"))
            m.exec_()    
            return
            
        if tipooperacion.id==2 and (self.txtBruto.decimal()<Decimal('0') or self.txtNeto.decimal()<Decimal('0')):
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.trUtf8("Un ingreso no puede tener un importe negativo"))
            m.exec_()
            return
        if self.txtRetencion.decimal()<Decimal('0') or self.txtDPA.decimal()<Decimal('0') or self.txtComision.decimal()<Decimal('0'):
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.trUtf8("Retention, earnings por share and commission must be greater than zero"))
            m.exec_()    
            return
        
        
        try:
            self.dividend.concepto=concepto
            self.dividend.bruto=self.txtBruto.decimal()
            self.dividend.retencion=self.txtRetencion.decimal()
            self.dividend.neto=self.neto
            self.dividend.dpa=self.txtDPA.decimal()
            self.dividend.fecha=self.cal.selectedDate().toPyDate()
            self.dividend.comision=self.txtComision.decimal()
        except:            
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.trUtf8("Error al introducir los datos. Compruébelos"))
            m.exec_()    
            return

        
        self.dividend.save()
        self.cfg.con.commit()
        self.done(0)
