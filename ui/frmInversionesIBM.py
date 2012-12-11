from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Ui_frmInversionesIBM import *
from core import *

class frmInversionesIBM(QDialog, Ui_frmInversionesIBM):
    def __init__(self, cfg, inversion, operinversion,   parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.cfg=cfg
        self.inversion=inversion
        self.operinversion=operinversion
  
        qcombobox_loadtiposoperaciones(self.cmbTiposOperaciones, self.cfg.tiposoperaciones_operinversiones())

        
        if self.operinversion==None:#nuevo movimiento
            self.operinversion=InversionOperacion()
            self.operinversion.inversion=self.inversion
            self.lblTitulo.setText(self.trUtf8("Nuevo movimiento de {0}".format(self.inversion.name)))
            t=datetime.datetime.now()
            self.timeedit.setTime(QTime(t.hour, t.minute))
        else:#editar movimiento
            self.lblTitulo.setText(self.trUtf8("Edición del movimiento seleccionado de {0}".format(self.inversion.name)))
            self.cmbTiposOperaciones.setCurrentIndex(self.cmbTiposOperaciones.findData(self.operinversion.tipooperacion.id))
            dt=dt_changes_tz(self.operinversion.datetime, config.localzone)
            self.calendar.setSelectedDate(dt.date())
            self.timeedit.setTime(dt.time())
            self.txtImporte.setText(str(self.operinversion.importe))
            self.txtImpuestos.setText(str(self.operinversion.impuestos))
            self.txtComision.setText(str(self.operinversion.comision))
            self.txtValorAccion.setText(str(self.operinversion.valor_accion))
            self.txtAcciones.setText(str(self.operinversion.acciones))
            self.cmbTZ.setCurrentIndex(self.cmbTZ.findText(config.localzone))

    def on_cmd_released(self):
        fecha=self.calendar.selectedDate().toPyDate()
        hora=self.timeedit.time().toPyTime()
        
        id_tiposoperaciones=int(self.cmbTiposOperaciones.itemData(self.cmbTiposOperaciones.currentIndex()))
        self.operinversion.tipooperacion=self.cfg.tiposoperaciones(id_tiposoperaciones)
        self.operinversion.impuestos=Decimal(self.txtImpuestos.text())
        self.operinversion.comision=Decimal(self.txtComision.text())
        self.operinversion.valor_accion=Decimal(self.txtValorAccion.text())
        self.operinversion.acciones=Decimal(self.txtAcciones.text())
        zone=(self.cmbTZ.currentText())
        if id_tiposoperaciones==5: #Venta
            self.operinversion.importe=Decimal(self.txtImporteBruto.text())
            if self.operinversion.acciones>0:
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
            self.operinversion.importe=self.txtImporte.decimal
        
        if self.operinversion.impuestos<0 or  self.operinversion.comision<0 or self.operinversion.valor_accion<0:            
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.trUtf8("El valor de la acción, los impuestos y la comisión deben ser positivos"))
            m.exec_()    
            return

        dat=dt(fecha,  hora, zone ) 
        self.operinversion.datetime=dat
        
        con=self.cfg.connect_xulpymoney()
        cur = con.cursor()    
        cur2= con.cursor()
        self.operinversion.save(cur, cur2)        
        con.commit()        
        cur.close()     
        cur2.close()
        self.cfg.disconnect_xulpymoney(con)        
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
