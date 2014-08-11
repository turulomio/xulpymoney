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
            self.lblTitulo.setText(self.trUtf8("Nuevo movimiento de {0}".format(self.inversion.name)))
            self.wdgDT.set(self.mem)
        else:#editar movimiento
            self.type=2
            self.lblTitulo.setText(self.trUtf8("Edición del movimiento seleccionado de {0}".format(self.inversion.name)))
            self.cmbTiposOperaciones.setCurrentIndex(self.cmbTiposOperaciones.findData(self.operinversion.tipooperacion.id))
            self.wdgDT.set(self.mem, self.operinversion.datetime, self.mem.localzone)
            self.txtImporte.setText(str(self.operinversion.importe))
            self.txtImpuestos.setText(str(self.operinversion.impuestos))
            self.txtComision.setText(str(self.operinversion.comision))
            self.txtValorAccion.setText(str(self.operinversion.valor_accion))
            self.txtAcciones.setText(str(self.operinversion.acciones))

    def on_cmd_released(self):        
        id_tiposoperaciones=int(self.cmbTiposOperaciones.itemData(self.cmbTiposOperaciones.currentIndex()))
        self.operinversion.tipooperacion=self.mem.tiposoperaciones.find(id_tiposoperaciones)
        self.operinversion.impuestos=Decimal(self.txtImpuestos.text())
        self.operinversion.comision=Decimal(self.txtComision.text())
        self.operinversion.valor_accion=Decimal(self.txtValorAccion.text())
        self.operinversion.acciones=Decimal(self.txtAcciones.text())
        if id_tiposoperaciones==5: #Venta
            self.operinversion.importe=Decimal(self.txtImporteBruto.text())
            if self.operinversion.acciones>Decimal('0'):
                m=QMessageBox()
                m.setIcon(QMessageBox.Information)
                m.setText(self.trUtf8("El número de acciones en una venta debe ser negativo"))
                m.exec_()    
                return        
        elif id_tiposoperaciones==4: #Compra
            self.operinversion.importe=Decimal(self.txtImporte.text())
            if self.operinversion.acciones<0: 
                m=QMessageBox()
                m.setIcon(QMessageBox.Information)
                m.setText(self.trUtf8("El número de acciones en una compra debe ser positivo"))
                m.exec_()    
                return
        elif id_tiposoperaciones==6: #Añadido    
            self.operinversion.importe=Decimal(self.txtImporte.text())            
        elif id_tiposoperaciones==8: #Traspaso fondos
            self.operinversion.importe=self.txtImporte.decimal()
        
        if self.operinversion.impuestos<Decimal('0') or  self.operinversion.comision<Decimal('0') or self.operinversion.valor_accion<Decimal('0'):            
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.trUtf8("El valor de la acción, los impuestos y la comisión deben ser positivos"))
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
            self.txtValorAccion.setText("0")
            self.txtValorAccion.setEnabled(False)
        else:
            self.txtValorAccion.setEnabled(True)
        self.on_txtAcciones_textChanged()
            
    def on_txtAcciones_textChanged(self):
        """El importe a grabar en BD cuando es una compra es el importe neto, cuando es una venta es el importe bruto"""
        id_tiposoperaciones=int(self.cmbTiposOperaciones.itemData(self.cmbTiposOperaciones.currentIndex()))
        try:
            if id_tiposoperaciones==4:#Compra
                importe=abs(round(Decimal(self.txtAcciones.text())*Decimal(self.txtValorAccion.text()), 2))
                self.txtImporte.setText(str(importe))
                self.txtImporteBruto.setText(str(importe+Decimal(self.txtComision.text())+Decimal(self.txtImpuestos.text())))
            if id_tiposoperaciones==5:#Venta
                importe=abs(round(Decimal(self.txtAcciones.text())*Decimal(self.txtValorAccion.text()), 2))
                self.txtImporte.setText(str(importe-Decimal(self.txtComision.text())-Decimal(self.txtImpuestos.text())))
                self.txtImporteBruto.setText(str(importe))
            if id_tiposoperaciones==8:#Traspaso
                importe=abs(round(Decimal(self.txtAcciones.text())*Decimal(self.txtValorAccion.text()), 2))
                self.txtImporte.setText(str(importe))
                self.txtImporteBruto.setText(str(importe+Decimal(self.txtComision.text())+Decimal(self.txtImpuestos.text())))
        except:
            pass
        
        
    def on_txtValorAccion_textChanged(self):
        self.on_txtAcciones_textChanged()
        
    def on_txtComision_textChanged(self):
        self.on_txtAcciones_textChanged()
        
    def on_txtImpuestos_textChanged(self):
        self.on_txtAcciones_textChanged()
