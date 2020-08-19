import datetime
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog
from xulpymoney.ui.wdgTwoCurrencyLineEdit import wdgTwoCurrencyLineEdit
from xulpymoney.objects.investmentoperation import InvestmentOperation
from xulpymoney.objects.money import Money
from xulpymoney.objects.operationtype import OperationTypeManager_for_InvestmentOperations
from xulpymoney.ui.myqdialog import MyModalQDialog
from xulpymoney.ui.myqwidgets import  qmessagebox, qinputbox_decimal
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

        self.wdgDT.setLocalzone(self.mem.localzone_name)
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
            self.wdgDT.set()
            OperationTypeManager_for_InvestmentOperations(self.mem).qcombobox(self.cmbTiposOperaciones)
            self.cmbTiposOperaciones.setCurrentIndex(0)
        else:#editar movimiento
            self.type=2
            self.lblTitulo.setText(self.tr("{} operation edition").format(self.investment.name))
            OperationTypeManager_for_InvestmentOperations(self.mem).qcombobox(self.cmbTiposOperaciones, self.operinversion.tipooperacion)
            self.wdgDT.set(self.operinversion.datetime, self.mem.localzone_name)
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

    def on_cmdGuestCurrencyConversion_released(self):
        price_product_currency=qinputbox_decimal(self.tr("Please add the operation close price in product currency"))
        gains_account_currency=qinputbox_decimal(self.tr("Please add the final gains in account currency"))
        self.txtAcciones.setText(-self.investment.op_actual.shares())
        self.wdg2CCurrencyConversion.setTextB(self.investment.op_actual.guess_operation_currency_conversion(price_product_currency, gains_account_currency))
        self.wdg2CPrice.setTextA(price_product_currency)

    def on_cmdComissionCalculator_released(self):
        d=MyModalQDialog(self)
        d.setWindowTitle(self.tr("Comission calculator"))
        d.setWindowIcon(QIcon(":/xulpymoney/tools-wizard.png"))
        d.setSettings(self.mem.settings, "frmInvestmentOperationsAdd", "frmCommissionCalculator", 300, 50)
        t=wdgTwoCurrencyLineEdit(d)
        t.label.setWordWrap(True)
        t.set(self.mem, self.investment.product.currency, self.investment.account.currency, self.wdg2CCurrencyConversion.factor)
        t.setLabel(self.tr("Please add the final positive amount annoted in your bank account, then close this window"))
        d.setWidgets(t)
        d.exec_()
        self.wdg2CComission.setTextA(abs(t.decimalA())-abs(self.wdg2CPrice.decimalA()*self.txtAcciones.decimal()))

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
            self.operinversion.show_in_ranges=False
            if self.operinversion.shares>Decimal('0'):
                qmessagebox(self.tr("Sale Shares number must be negative"))
                return        
        elif id_tiposoperaciones==4: #Compra
            if self.operinversion.shares<0: 
                qmessagebox(self.tr("Purchase shares number must be positive"))
                return
        elif id_tiposoperaciones==6: #Añadido
            if self.operinversion.shares<0: 
                qmessagebox(self.tr("Added shares number must be positive"))
                return
        
        if self.operinversion.impuestos<Decimal('0') or  self.operinversion.comision<Decimal('0') or self.operinversion.valor_accion<Decimal('0'):            
            qmessagebox(self.tr("Share price, taxes and commission must be positive amounts"))
            return
            
        self.operinversion.datetime=self.wdgDT.datetime()
        self.operinversion.save()    
        self.mem.con.commit()#Guarda todos los cambios en bd.
        
        ##Mete indice referencia.
        if self.type==1  and id_tiposoperaciones==4:#Añadir y compra
            w=frmQuotesIBM(self.mem, self.mem.data.benchmark, None, self)
            #Quita un minuto para que enganche con operación
            w.wdgDT.set(self.wdgDT.datetime()-datetime.timedelta(seconds=1), self.mem.localzone_name)
            w.chkCanBePurged.setCheckState(Qt.Unchecked)
            w.txtQuote.setFocus()
            w.exec_() 
            self.mem.data.benchmark.result.basic.load_from_db()                
        self.done(0)

    @pyqtSlot(int)
    def on_cmbTiposOperaciones_currentIndexChanged(self, index):
        id_tiposoperaciones=int(self.cmbTiposOperaciones.itemData(index))
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


