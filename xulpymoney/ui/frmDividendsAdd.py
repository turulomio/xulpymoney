from PyQt5.QtWidgets import QDialog,  QWidget
from decimal import Decimal
from xulpymoney.libxulpymoney import Dividend,  Money
from xulpymoney.libxulpymoneyfunctions import qmessagebox
from xulpymoney.libxulpymoneytypes import eProductType
from xulpymoney.ui.Ui_frmDividendsAdd import Ui_frmDividendsAdd

class frmDividendsAdd(QDialog, Ui_frmDividendsAdd):
    def __init__(self, mem, inversion, dividend=None,  parent=None):
        """
        Si dividend es None se insertar
        Si dividend es un objeto se modifica"""
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        self.dividend=dividend
        self.investment=inversion
        
        self.neto=0
        self.tpc=0
        self.wdgDT.show_microseconds(False)
        self.wdgDT.show_timezone(False)
        self.lblGross.setText(self.tr("Gross in {}".format(self.investment.product.currency.symbol)))
        self.lblGrossAccount.setText(self.tr("Gross converted to {}".format(self.investment.account.currency.symbol)))
        if dividend==None:#insertar
            if self.investment.product.type.id in (eProductType.PrivateBond, eProductType.PublicBond):#Bonds
                self.mem.conceptos.load_bonds_qcombobox(self.cmb)
            else:
                self.mem.conceptos.load_dividend_qcombobox(self.cmb)
            self.dividend=Dividend(self.mem)
            self.dividend.investment=inversion
            self.cmd.setText(self.tr("Add new dividend"))
            self.wdgDT.set(self.mem, None, self.mem.localzone)
            self.wdgCurrencyConversion.setConversion(Money(self.mem, self.txtBruto.decimal(), self.investment.product.currency), self.investment.account.currency, self.wdgDT.datetime(), None)
        else:#modificar 
            if self.investment.product.type.id in (eProductType.PrivateBond, eProductType.PublicBond):#Bonds
                self.mem.conceptos.load_bonds_qcombobox(self.cmb, self.dividend.concepto) 
            else:
                self.mem.conceptos.load_dividend_qcombobox(self.cmb, self.dividend.concepto) 
            self.wdgDT.set(self.mem, self.dividend.datetime, self.mem.localzone)
            self.wdgCurrencyConversion.setConversion(Money(self.mem, self.txtBruto.decimal(), self.investment.product.currency), self.investment.account.currency, self.wdgDT.datetime(), self.dividend.currency_conversion)
            self.txtBruto.setText(self.dividend.bruto)
            self.txtNeto.setText(self.dividend.neto)
            self.txtRetencion.setText(self.dividend.retencion)
            self.txtComision.setText(self.dividend.comision)
            self.txtDPA.setText(self.dividend.dpa)
            self.cmd.setText(self.tr("Edit dividend"))
 
    def on_txtBruto_textChanged(self):
        self.wdgCurrencyConversion.setConversion(Money(self.mem, self.txtBruto.decimal(), self.investment.product.currency), self.investment.account.currency, self.wdgDT.datetime(), self.wdgCurrencyConversion.factor)
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
            self.txtNeto.setText(self.neto)
            self.lblTPC.setText(self.tr("Withhonding tax retention percentage: {} %".format(self.tpc)))
            self.cmd.setEnabled(True)
        except:
            self.txtNeto.setText(self.tr("Calculation error"))
            self.lblTPC.setText(self.tr("Calculation error"))
            self.cmd.setEnabled(False)
 


    def on_cmd_pressed(self):
        concepto=self.mem.conceptos.find_by_id(self.cmb.itemData(self.cmb.currentIndex()))
        tipooperacion=concepto.tipooperacion
                        
        if tipooperacion.id==1 and (self.txtBruto.decimal()>Decimal('0') or self.txtNeto.decimal()>Decimal('0')):
            qmessagebox(self.tr("Expenses can't have a positive amount"))
            return
            
        if tipooperacion.id==2 and (self.txtBruto.decimal()<Decimal('0') or self.txtNeto.decimal()<Decimal('0')):
            qmessagebox(self.tr("Incomes can't have a negative amount"))
            return
        if self.txtRetencion.decimal()<Decimal('0') or self.txtDPA.decimal()<Decimal('0') or self.txtComision.decimal()<Decimal('0'):
            qmessagebox(self.tr("Retention, earnings por share and commission must be greater than zero"))
            return
        
        
        try:
            self.dividend.concepto=concepto
            self.dividend.bruto=self.txtBruto.decimal()
            self.dividend.retencion=self.txtRetencion.decimal()
            self.dividend.neto=self.neto
            self.dividend.dpa=self.txtDPA.decimal()
            self.dividend.datetime=self.wdgDT.datetime()
            self.dividend.comision=self.txtComision.decimal()
            self.dividend.currency_conversion=self.wdgCurrencyConversion.factor
        except:
            qmessagebox(self.tr("Data error. Please check them."))
            return

        
        self.dividend.save()
        self.mem.con.commit()
        self.done(0)
