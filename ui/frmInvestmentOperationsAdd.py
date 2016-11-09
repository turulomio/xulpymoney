from PyQt5.QtCore import *
from PyQt5.QtGui import *
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
  
  
        if self.inversion.hasSameAccountCurrency():
            self.wdg2CCurrencyConversion.hide()
            
  
        self.wdgDT.show_microseconds(False)
        self.wdg2CComission.setLabel(self.tr("Comission"))
        self.wdg2CTaxes.setLabel(self.tr("Taxes"))
        self.wdg2CCurrencyConversion.setLabel(self.tr("Conversion factor"))
        self.wdg2CPrice.setLabel(self.tr("Price"))
        
        factor=Money(self.mem, 0, self.inversion.product.currency).conversionFactor(self.inversion.account.currency, self.mem.localzone.now())
        self.wdg2CCurrencyConversion.set(self.mem, self.inversion.product.currency, self.inversion.account.currency,  factor)
        self.wdg2CCurrencyConversion.setFactorMode(True)
        self.wdg2CTaxes.set(self.mem, self.inversion.product.currency, self.inversion.account.currency,  factor)
        self.wdg2CPrice.set(self.mem, self.inversion.product.currency, self.inversion.account.currency,  factor)
        self.wdg2CComission.set(self.mem, self.inversion.product.currency, self.inversion.account.currency,  factor)
        self.wdg2CCurrencyConversion.factorChanged.connect(self.on_wdg2CCurrencyConversion_factorChanged)
        
        if self.operinversion==None:#nuevo movimiento
            self.type=1
            self.operinversion=InvestmentOperation(self.mem)
            self.operinversion.inversion=self.inversion
            self.lblTitulo.setText(self.tr("New operation of {}").format(self.inversion.name))
            self.mem.tiposoperaciones.qcombobox_investments_operations(self.cmbTiposOperaciones)
            self.wdgDT.set(self.mem)
        else:#editar movimiento
            self.type=2
            self.lblTitulo.setText(self.tr("{} operation edition").format(self.inversion.name))
            self.mem.tiposoperaciones.qcombobox_investments_operations(self.cmbTiposOperaciones, self.operinversion.tipooperacion)
            self.wdgDT.set(self.mem, self.operinversion.datetime, self.mem.localzone)
            self.txtImporte.setText(self.operinversion.importe)
            self.wdg2CTaxes.setTextA(self.operinversion.impuestos)
            self.wdg2CComission.setTextA(self.operinversion.comision)
            self.wdg2CPrice.setTextA(self.operinversion.valor_accion)
            self.txtAcciones.setText(self.operinversion.acciones)

        print("AQUI")

        self.wdg2CTaxes.textChanged.connect(self.on_wdg2CTaxes_mytextChanged)
        self.wdg2CComission.textChanged.connect(self.on_wdg2CComission_mytextChanged)
        self.wdg2CPrice.textChanged.connect(self.on_wdg2CPrice_mytextChanged)
        

    def on_wdg2CCurrencyConversion_factorChanged(self, factor):
        self.wdg2CComission.set(self.mem, self.inversion.product.currency, self.inversion.account.currency,  factor)
        self.wdg2CPrice.set(self.mem, self.inversion.product.currency, self.inversion.account.currency,  factor)
        self.wdg2CTaxes.set(self.mem, self.inversion.product.currency, self.inversion.account.currency,  factor)
        
    def on_cmd_released(self):        
        id_tiposoperaciones=int(self.cmbTiposOperaciones.itemData(self.cmbTiposOperaciones.currentIndex()))
        self.operinversion.tipooperacion=self.mem.tiposoperaciones.find_by_id(id_tiposoperaciones)
        self.operinversion.impuestos=self.wdg2CTaxes.decimalA()
        self.operinversion.comision=self.wdg2CComission.decimalA()
        self.operinversion.valor_accion=self.wdg2CPrice.decimalA()
        self.operinversion.currency_conversion=self.wdg2CCurrencyConversion.factor
        self.operinversion.acciones=self.txtAcciones.decimal()
        if id_tiposoperaciones==5: #Venta
            self.operinversion.importe=self.txtImporteBruto.decimal()
            self.operinversion.show_in_ranges=False
            if self.operinversion.acciones>Decimal('0'):
                m=QMessageBox()
                m.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
                m.setIcon(QMessageBox.Information)
                m.setText(self.tr("Sale Shares number must be negative"))
                m.exec_()    
                return        
        elif id_tiposoperaciones==4: #Compra
            self.operinversion.importe=self.txtImporte.decimal()
            if self.operinversion.acciones<0: 
                m=QMessageBox()
                m.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
                m.setIcon(QMessageBox.Information)
                m.setText(self.tr("Purchase shares number must be positive"))
                m.exec_()    
                return
        elif id_tiposoperaciones==6: #Añadido    
            self.operinversion.importe=self.txtImporte.decimal()
            if self.operinversion.acciones<0: 
                m=QMessageBox()
                m.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
                m.setIcon(QMessageBox.Information)
                m.setText(self.tr("Added shares number must be positive"))
                m.exec_()    
                return            
        elif id_tiposoperaciones==8: #Traspaso fondos
            self.operinversion.importe=self.txtImporte.decimal()
        
        if self.operinversion.impuestos<Decimal('0') or  self.operinversion.comision<Decimal('0') or self.operinversion.valor_accion<Decimal('0'):            
            m=QMessageBox()
            m.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
            m.setIcon(QMessageBox.Information)
            m.setText(self.tr("Share price, taxes and comission must be positive amounts"))
            m.exec_()    
            return
            
        self.operinversion.datetime=self.wdgDT.datetime()
        self.operinversion.save()    
        self.mem.con.commit()#Guarda todos los cambios en bd.
        
        ##Mete indice referencia.
        if self.type==1  and id_tiposoperaciones==4:#Añadir y compra
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
            self.wdg2CPrice.setTextA(0)
            self.wdg2CPrice.setEnabled(False)
        else:
            self.wdg2CPrice.setEnabled(True)
        self.on_txtAcciones_textChanged()
            
    def on_txtAcciones_textChanged(self):
        """El importe a grabar en BD cuando es una compra es el importe neto, cuando es una venta es el importe bruto"""
        id_tiposoperaciones=int(self.cmbTiposOperaciones.itemData(self.cmbTiposOperaciones.currentIndex()))
        try:
            if id_tiposoperaciones==4:#Compra
                importe=abs(round(self.txtAcciones.decimal()*self.wdg2CPrice.decimalA(), 2))
                self.txtImporte.setText(importe)
                self.txtImporteBruto.setText(importe+self.wdg2CComission.decimalA()+self.wdg2CTaxes.decimalA())
            if id_tiposoperaciones==5:#Venta
                importe=abs(round(self.txtAcciones.decimal()*self.wdg2CPrice.decimalA(), 2))
                self.txtImporte.setText(importe-self.wdg2CComission.decimalA()-self.wdg2CTaxes.decimalA())
                self.txtImporteBruto.setText(importe)
            if id_tiposoperaciones==8:#Traspaso
                importe=abs(round(self.txtAcciones.decimal()*self.wdg2CPrice.decimaAl(), 2))
                self.txtImporte.setText(importe)
                self.txtImporteBruto.setText(importe+self.wdg2CComission.decimalA()+self.wdg2CTaxes.decimalA())
        except:
            pass

    def on_wdg2CPrice_mytextChanged(self):
        self.on_txtAcciones_textChanged()
        
    def on_wdg2CComission_mytextChanged(self):
        self.on_txtAcciones_textChanged()
        
    def on_wdg2CTaxes_mytextChanged(self):
        self.on_txtAcciones_textChanged()
