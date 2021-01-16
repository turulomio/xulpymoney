from PyQt5.QtWidgets import QDialog,  QWidget
from decimal import Decimal
from xulpymoney.libxulpymoneytypes import eMoneyCurrency
from xulpymoney.objects.concept import ConceptManager_for_dividends
from xulpymoney.objects.currency import currency_symbol
from xulpymoney.objects.dividend import Dividend
from xulpymoney.objects.money import Money
from xulpymoney.ui.myqwidgets import qmessagebox
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
        
        self.net=0
        self.tpc=0
        self.wdgDT.setLocalzone(self.mem.localzone_name)
        self.wdgDT.show_microseconds(False)
        self.wdgDT.show_timezone(False)
        self.lblGross.setText(self.tr("Gross in {}").format(currency_symbol(self.investment.product.currency)))
        self.lblGrossAccount.setText(self.tr("Gross converted to {}").format(currency_symbol(self.investment.account.currency)))
        if dividend==None:#insertar
            ConceptManager_for_dividends(mem).qcombobox(self.cmb)
            self.cmb.setCurrentIndex(0)
            self.dividend=Dividend(self.mem)
            self.dividend.investment=inversion
            self.cmd.setText(self.tr("Add new dividend"))
            self.wdgDT.set(None, self.mem.localzone_name)
            self.wdgCurrencyConversion.setConversion(Money(self.mem, self.txtBruto.decimal(), self.investment.product.currency), self.investment.account.currency, self.wdgDT.datetime(), None)
        else:#modificar 
            ConceptManager_for_dividends(mem).qcombobox(self.cmb, self.dividend.concept)
            self.wdgDT.set(self.dividend.datetime, self.mem.localzone_name)
            self.wdgCurrencyConversion.setConversion(Money(self.mem, self.txtBruto.decimal(), self.investment.product.currency), self.investment.account.currency, self.wdgDT.datetime(), self.dividend.currency_conversion)
            self.txtBruto.setText(self.dividend.gross(eMoneyCurrency.Account).amount)
            self.txtNeto.setText(self.dividend.net(eMoneyCurrency.Account).amount)
            self.txtRetencion.setText(self.dividend.taxes)
            self.txtComision.setText(self.dividend.commission(eMoneyCurrency.Account).amount)
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
                self.net=self.txtBruto.decimal()-self.txtComision.decimal()
                self.tpc=0
            else:
                self.txtRetencion.setEnabled(True)
                self.txtDPA.setEnabled(True)
                self.txtComision.setEnabled(True)
                self.net=self.txtBruto.decimal()-self.txtRetencion.decimal()-self.txtComision.decimal()
                self.tpc=100*self.txtRetencion.decimal()/self.txtBruto.decimal()
            self.txtNeto.setText(self.net)
            self.lblTPC.setText(self.tr("Withhonding tax retention percentage: {} %".format(self.tpc)))
            self.cmd.setEnabled(True)
        except:
            self.txtNeto.setText(self.tr("Calculation error"))
            self.lblTPC.setText(self.tr("Calculation error"))
            self.cmd.setEnabled(False)
 


    def on_cmd_pressed(self):
        concept=self.mem.concepts.find_by_id(self.cmb.itemData(self.cmb.currentIndex()))
        tipooperacion=concept.tipooperacion
                        
        if tipooperacion.id==1 and (self.txtBruto.decimal()>Decimal('0') or self.txtNeto.decimal()>Decimal('0')):
            qmessagebox(self.tr("Expenses can't have a positive amount"))
            return
            
        if tipooperacion.id==2 and (self.txtBruto.decimal()<Decimal('0') or self.txtNeto.decimal()<Decimal('0')):
            qmessagebox(self.tr("Incomes can't have a negative amount"))
            return
        if self.txtRetencion.decimal()<Decimal('0') or self.txtDPA.decimal()<Decimal('0') or self.txtComision.decimal()<Decimal('0'):
            qmessagebox(self.tr("Retention, earnings por share and commission must be greater than zero"))
            return
        
        print(self.net)
        try:
            self.dividend.concept=concept
            self.dividend._gross=self.txtBruto.decimal()
            self.dividend.taxes=self.txtRetencion.decimal()
            self.dividend._net=self.net
            self.dividend.dpa=self.txtDPA.decimal()
            self.dividend.datetime=self.wdgDT.datetime()
            self.dividend._commission=self.txtComision.decimal()
            self.dividend.currency_conversion=self.wdgCurrencyConversion.factor
        except:
            qmessagebox(self.tr("Data error. Please check them."))
            return

        
        self.dividend.save()
        self.mem.con.commit()
        self.investment.needStatus(3, downgrade_to=2)
        self.done(0)
