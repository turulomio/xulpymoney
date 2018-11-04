import datetime
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog,  QMessageBox, QVBoxLayout
from xulpymoney.ui.wdgTwoCurrencyLineEdit import wdgTwoCurrencyLineEdit
from xulpymoney.libxulpymoney import InvestmentOperation, Money,  qmessagebox
from xulpymoney.ui.frmQuotesIBM import frmQuotesIBM
from xulpymoney.ui.Ui_frmInvestmentOperationsAdd import Ui_frmInvestmentOperationsAdd
from decimal import Decimal

class frmInvestmentOperationsAdd(QDialog, Ui_frmInvestmentOperationsAdd):
    def __init__(self, mem, inversion, operinversion,   parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        self.investment=inversion
        self.operinversion=operinversion

        if self.investment.hasSameAccountCurrency():
            self.wdg2CCurrencyConversion.hide()
            
        self.lblType.setFixedWidth(200)
        self.lblShares.setFixedWidth(200)

        self.wdgDT.show_microseconds(False)
        self.wdg2CComission.setLabel(self.tr("Comission"))
        self.wdg2CTaxes.setLabel(self.tr("Taxes"))
        self.wdg2CCurrencyConversion.setLabel(self.tr("Conversion factor"))
        self.wdg2CPrice.setLabel(self.tr("Price"))
        self.wdg2CGross.setLabel(self.tr("Gross"))
        self.wdg2CNet.setLabel(self.tr("Net"))

        self.wdg2CGross.setReadOnly(True)
        self.wdg2CNet.setReadOnly(True)

        if self.operinversion==None:
            factor=Money(self.mem, 0, self.investment.product.currency).conversionFactor(self.investment.account.currency, self.mem.localzone.now())
        else:
            factor=self.operinversion.currency_conversion
        self.wdg2CCurrencyConversion.set(self.mem, self.investment.product.currency, self.investment.account.currency,  factor)
        self.wdg2CCurrencyConversion.setFactorMode(True)
        self.wdg2CTaxes.set(self.mem, self.investment.product.currency, self.investment.account.currency,  factor)
        self.wdg2CPrice.set(self.mem, self.investment.product.currency, self.investment.account.currency,  factor)
        self.wdg2CComission.set(self.mem, self.investment.product.currency, self.investment.account.currency,  factor)
        self.wdg2CCurrencyConversion.factorChanged.connect(self.on_wdg2CCurrencyConversion_factorChanged)

        if self.operinversion==None:#nuevo movimiento
            self.type=1
            self.operinversion=InvestmentOperation(self.mem)
            self.operinversion.investment=self.investment
            self.lblTitulo.setText(self.tr("New operation of {}").format(self.investment.name))
            self.mem.tiposoperaciones.qcombobox_investments_operations(self.cmbTiposOperaciones)
            self.wdgDT.set(self.mem)
        else:#editar movimiento
            self.type=2
            self.lblTitulo.setText(self.tr("{} operation edition").format(self.investment.name))
            self.mem.tiposoperaciones.qcombobox_investments_operations(self.cmbTiposOperaciones, self.operinversion.tipooperacion)
            self.wdgDT.set(self.mem, self.operinversion.datetime, self.mem.localzone)
            self.wdg2CGross.setTextA(self.operinversion.net(type=1))
            self.wdg2CNet.setTextA(self.operinversion.gross(type=1))
            self.wdg2CTaxes.setTextA(self.operinversion.impuestos)
            self.wdg2CComission.setTextA(self.operinversion.comision)
            self.wdg2CPrice.setTextA(self.operinversion.valor_accion)
            self.txtAcciones.setText(self.operinversion.shares)

        self.wdg2CTaxes.textChanged.connect(self.on_wdg2CTaxes_mytextChanged)
        self.wdg2CComission.textChanged.connect(self.on_wdg2CComission_mytextChanged)
        self.wdg2CPrice.textChanged.connect(self.on_wdg2CPrice_mytextChanged)

    def on_wdg2CCurrencyConversion_factorChanged(self, factor):
        self.wdg2CComission.set(self.mem, self.investment.product.currency, self.investment.account.currency,  factor)
        self.wdg2CPrice.set(self.mem, self.investment.product.currency, self.investment.account.currency,  factor)
        self.wdg2CTaxes.set(self.mem, self.investment.product.currency, self.investment.account.currency,  factor)
        self.wdg2CGross.set(self.mem, self.investment.product.currency, self.investment.account.currency,  factor)
        self.wdg2CNet.set(self.mem, self.investment.product.currency, self.investment.account.currency,  factor)

    def on_cmdComissionCalculator_released(self):
        d=QDialog(self)     
        d.resize(800, 80)
        d.setWindowTitle(self.tr("Comission calculator"))
        d.setWindowIcon(QIcon(":/xulpymoney/tools-wizard.png"))
        t=wdgTwoCurrencyLineEdit(d)
        t.label.setWordWrap(True)
        t.set(self.mem, self.investment.product.currency, self.investment.account.currency, self.wdg2CCurrencyConversion.factor)
        t.setLabel(self.tr("Please add the final amount annoted in your bank account, then close this window"))
        lay = QVBoxLayout(d)
        lay.addWidget(t)
        d.exec_()
        self.wdg2CComission.setTextA(t.decimalA()-self.wdg2CPrice.decimalA()*self.txtAcciones.decimal())

    def on_cmd_released(self):        
        if self.wdg2CComission.isValid() and self.wdg2CCurrencyConversion.isValid() and self.wdg2CPrice.isValid() and self.wdg2CTaxes.isValid()==False:
            qmessagebox(self.tr("Some fields are wrong"))
            return

        id_tiposoperaciones=int(self.cmbTiposOperaciones.itemData(self.cmbTiposOperaciones.currentIndex()))
        self.operinversion.tipooperacion=self.mem.tiposoperaciones.find_by_id(id_tiposoperaciones)
        self.operinversion.impuestos=self.wdg2CTaxes.decimalA()
        self.operinversion.comision=self.wdg2CComission.decimalA()
        self.operinversion.valor_accion=self.wdg2CPrice.decimalA()
        self.operinversion.currency_conversion=self.wdg2CCurrencyConversion.factor
        self.operinversion.shares=self.txtAcciones.decimal()
        if id_tiposoperaciones==5: #Venta
#            self.operinversion.importe=self.txtNetBruto.decimal()
            self.operinversion.show_in_ranges=False
            if self.operinversion.shares>Decimal('0'):
                m=QMessageBox()
                m.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
                m.setIcon(QMessageBox.Information)
                m.setText(self.tr("Sale Shares number must be negative"))
                m.exec_()    
                return        
        elif id_tiposoperaciones==4: #Compra
#            self.operinversion.importe=self.txtNet.decimal()
            if self.operinversion.shares<0: 
                m=QMessageBox()
                m.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
                m.setIcon(QMessageBox.Information)
                m.setText(self.tr("Purchase shares number must be positive"))
                m.exec_()    
                return
        elif id_tiposoperaciones==6: #Añadido    
#            self.operinversion.importe=self.txtNet.decimal()
            if self.operinversion.shares<0: 
                m=QMessageBox()
                m.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
                m.setIcon(QMessageBox.Information)
                m.setText(self.tr("Added shares number must be positive"))
                m.exec_()    
                return            
#        elif id_tiposoperaciones==8: #Traspaso fondos
#            self.operinversion.importe=self.txtNet.decimal()
        
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
        if self.txtAcciones.isValid() and self.wdg2CPrice.isValid():
            self.cmdComissionCalculator.setEnabled(True)
        else:
            self.cmdComissionCalculator.setEnabled(False)
        id_tiposoperaciones=int(self.cmbTiposOperaciones.itemData(self.cmbTiposOperaciones.currentIndex()))
        try:
            if id_tiposoperaciones==4:#Compra
                importe=abs(round(self.txtAcciones.decimal()*self.wdg2CPrice.decimalA(), 2))
                self.wdg2CGross.setTextA(importe)
                self.wdg2CNet.setTextA(importe+self.wdg2CComission.decimalA()+self.wdg2CTaxes.decimalA())
            if id_tiposoperaciones==5:#Venta
                importe=abs(round(self.txtAcciones.decimal()*self.wdg2CPrice.decimalA(), 2))
                self.wdg2CGross.setTextA(importe)
                self.wdg2CNet.setTextA(importe-self.wdg2CComission.decimalA()-self.wdg2CTaxes.decimalA())
            if id_tiposoperaciones==8:#Traspaso
                importe=abs(round(self.txtAcciones.decimal()*self.wdg2CPrice.decimalA(), 2))
                self.wdg2CGross.setTextA(importe)
                self.wdg2CNet.setTextA(importe+self.wdg2CComission.decimalA()+self.wdg2CTaxes.decimalA())
        except:
            pass

    @pyqtSlot()
    def on_wdg2CPrice_mytextChanged(self):
        self.on_txtAcciones_textChanged()

    @pyqtSlot()
    def on_wdg2CComission_mytextChanged(self):
        self.on_txtAcciones_textChanged()

    @pyqtSlot()
    def on_wdg2CTaxes_mytextChanged(self):
        self.on_txtAcciones_textChanged()


