from PyQt4.QtCore import *
from PyQt4.QtGui import *
from libxulpymoney import *
from frmProductReport import *
from Ui_frmInvestmentOperationsAdd import *

class frmInvestmentOperationsAdd(QDialog, Ui_frmInvestmentOperationsAdd):
    def __init__(self, mem, inversion, operinversion,   parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        self.inversion=inversion
        self.operinversion=operinversion
  
        self.mem.tiposoperaciones.qcombobox(self.cmbTiposOperaciones)
        self.wdgDT.show_microseconds(False)
        
        if self.operinversion==None:#nuevo movimiento
            self.type=1
            self.operinversion=InvestmentOperation(self.mem)
            self.operinversion.inversion=self.inversion
            self.lblTitulo.setText(self.tr("New operation of {}").format(self.inversion.name))
            self.wdgDT.set(self.mem)
        else:#editar movimiento
            self.type=2
            self.lblTitulo.setText(self.tr("{} operation edition").format(self.inversion.name))
            self.cmbTiposOperaciones.setCurrentIndex(self.cmbTiposOperaciones.findData(self.operinversion.tipooperacion.id))
            self.wdgDT.set(self.mem, self.operinversion.datetime, self.mem.localzone)
            self.txtImporte.setText(self.operinversion.importe)
            self.txtImpuestos.setText(self.operinversion.impuestos)
            self.txtComision.setText(self.operinversion.comision)
            self.txtValorAccion.setText(self.operinversion.valor_accion)
            self.txtAcciones.setText(self.operinversion.acciones)

    def on_cmd_released(self):        
        id_tiposoperaciones=int(self.cmbTiposOperaciones.itemData(self.cmbTiposOperaciones.currentIndex()))
        self.operinversion.tipooperacion=self.mem.tiposoperaciones.find(id_tiposoperaciones)
        self.operinversion.impuestos=self.txtImpuestos.decimal()
        self.operinversion.comision=self.txtComision.decimal()
        self.operinversion.valor_accion=self.txtValorAccion.decimal()
        self.operinversion.acciones=self.txtAcciones.decimal()
        if id_tiposoperaciones==5: #Venta
            self.operinversion.importe=self.txtImporteBruto.decimal()
            if self.operinversion.acciones>Decimal('0'):
                m=QMessageBox()
                m.setIcon(QMessageBox.Information)
                m.setText(self.tr("Sale Shares number must be negative"))
                m.exec_()    
                return        
        elif id_tiposoperaciones==4: #Compra
            self.operinversion.importe=self.txtImporte.decimal()
            if self.operinversion.acciones<0: 
                m=QMessageBox()
                m.setIcon(QMessageBox.Information)
                m.setText(self.tr("Purchase shares number must be positive"))
                m.exec_()    
                return
        elif id_tiposoperaciones==6: #Añadido    
            self.operinversion.importe=self.txtImporte.decimal()
        elif id_tiposoperaciones==8: #Traspaso fondos
            self.operinversion.importe=self.txtImporte.decimal()
        
        if self.operinversion.impuestos<Decimal('0') or  self.operinversion.comision<Decimal('0') or self.operinversion.valor_accion<Decimal('0'):            
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.tr("Share price, taxes and comission must be positive amounts"))
            m.exec_()    
            return
            
        self.operinversion.datetime=self.wdgDT.datetime()
        self.operinversion.save()    
        self.mem.con.commit()#Guarda todos los cambios en bd.
        
        ##Mete indice referencia.
        if self.type==1:
            w=frmQuotesIBM(self.mem, self.mem.data.benchmark, None, self)
            #Quita un minuto para que enganche con operación
            w.wdgDT.set(self.mem, self.wdgDT.datetime()-datetime.timedelta(seconds=1), self.mem.localzone)
            w.chkCanBePurged.setCheckState(Qt.Unchecked)
            w.txtQuote.setFocus()
            w.exec_() 
            self.mem.data.benchmark.result.basic.load_from_db()                
        self.done(0)

    def on_cmbTiposOperaciones_currentIndexChanged(self, index):
        id_tiposoperaciones=int(self.cmbTiposOperaciones.itemData(self.cmbTiposOperaciones.currentIndex()))
        if id_tiposoperaciones==6:#Añadido acciones
            self.txtValorAccion.setText(0)
            self.txtValorAccion.setEnabled(False)
        else:
            self.txtValorAccion.setEnabled(True)
        self.on_txtAcciones_textChanged()
            
    def on_txtAcciones_textChanged(self):
        """El importe a grabar en BD cuando es una compra es el importe neto, cuando es una venta es el importe bruto"""
        id_tiposoperaciones=int(self.cmbTiposOperaciones.itemData(self.cmbTiposOperaciones.currentIndex()))
        try:
            if id_tiposoperaciones==4:#Compra
                importe=abs(round(self.txtAcciones.decimal()*self.txtValorAccion.decimal(), 2))
                self.txtImporte.setText(importe)
                self.txtImporteBruto.setText(importe+self.txtComision.decimal()+self.txtImpuestos.decimal())
            if id_tiposoperaciones==5:#Venta
                importe=abs(round(self.txtAcciones.decimal()*self.txtValorAccion.decimal()), 2)
                self.txtImporte.setText(importe-self.txtComision.decimal()-self.txtImpuestos.decimal())
                self.txtImporteBruto.setText(importe)
            if id_tiposoperaciones==8:#Traspaso
                importe=abs(round(self.txtAcciones.decimal()*self.txtValorAccion.decimal(), 2))
                self.txtImporte.setText(importe)
                self.txtImporteBruto.setText(importe+self.txtComision.decimal()+self.txtImpuestos.decimal())
        except:
            pass
        
        
    def on_txtValorAccion_textChanged(self):
        self.on_txtAcciones_textChanged()
        
    def on_txtComision_textChanged(self):
        self.on_txtAcciones_textChanged()
        
    def on_txtImpuestos_textChanged(self):
        self.on_txtAcciones_textChanged()
