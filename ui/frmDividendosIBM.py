from PyQt4.QtCore import *
from PyQt4.QtGui import *
from libxulpymoney import *
from Ui_frmDividendosIBM import *

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
            if self.inversion.investment.type.id in (7, 9):#Bonds
                self.cfg.conceptos.load_bonds_qcombobox(self.cmb)
            else:
                self.cfg.conceptos.load_dividend_qcombobox(self.cmb)
            self.dividendo=Dividendo(self.cfg)
            self.dividendo.inversion=inversion
            self.cmd.setText(self.trUtf8("Insertar nuevo dividendo"))
        else:#modificar 
            if self.inversion.investment.type.id in (7, 9):#Bonds
                self.cfg.conceptos.load_bonds_qcombobox(self.cmb, self.dividendo.concepto) 
            else:
                self.cfg.conceptos.load_dividend_qcombobox(self.cmb, self.dividendo.concepto) 
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
            if self.txtBruto.decimal()<Decimal(0):
                self.txtRetencion.setEnabled(False)
                self.txtDPA.setEnabled(False)
                self.txtComision.setEnabled(False)
                self.txtRetencion.setText(0)
                self.txtDPA.setText(0)
                self.txtComision.Decimal(0)
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
        
        (concepto, tipooperacion)=self.cfg.conceptos.strct2ct(self.cmb.itemData(self.cmb.currentIndex()))
                        
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
            self.dividendo.concepto=concepto
            self.dividendo.bruto=self.txtBruto.decimal()
            self.dividendo.retencion=self.txtRetencion.decimal()
            self.dividendo.neto=self.neto
            self.dividendo.dpa=self.txtDPA.decimal()
            self.dividendo.fecha=self.cal.selectedDate().toPyDate()
            self.dividendo.comision=self.txtComision.decimal()
        except:            
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.trUtf8("Error al introducir los datos. Compruébelos"))
            m.exec_()    
            return

        
        self.dividendo.save()
        self.cfg.con.commit()
        self.done(0)
