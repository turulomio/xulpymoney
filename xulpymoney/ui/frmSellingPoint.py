import datetime
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QDialog
from xulpymoney.ui.Ui_frmSellingPoint import Ui_frmSellingPoint
from xulpymoney.objects.currency import currency_symbol
from xulpymoney.objects.investmentoperation import InvestmentOperationCurrentHomogeneusManager
from xulpymoney.objects.money import Money
from xulpymoney.objects.percentage import Percentage
from xulpymoney.objects.quote import Quote
from xulpymoney.ui.myqwidgets import qmessagebox
from xulpymoney.libxulpymoneytypes import eMoneyCurrency
from decimal import Decimal

class frmSellingPoint(QDialog, Ui_frmSellingPoint):
    def __init__(self, mem,  inversion ,   parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.showMaximized()
        self.mem=mem
        self.investment=inversion
        
        if self.investment.id==None:
            qmessagebox(self.tr("You can't set a selling price to a unsaved investment"))
            return

        if self.investment.op_actual.length()==0:
            qmessagebox(self.tr("You don't have shares to sale in this investment"))
            return
        
        self.puntoventa=Decimal(0)#Guarda el resultado de los cálculos
        self.operinversiones=None 

        if self.mem.gainsyear==True:
            self.chkGainsTime.setCheckState(Qt.Checked)
        else:
            self.chkGainsTime.setEnabled(False)

        self.mqtw.setSettings(self.mem.settings, "frmSellingPoint", "mqtw")
        self.mqtwSP.setSettings(self.mem.settings, "frmSellingPoint", "mqtwSP")
        
        self.spnGainsPercentage.setValue(self.mem.settingsdb.value_float("frmSellingPoint/lastgainpercentage",  "10"))
        
        self.lblPriceSymbol.setText(currency_symbol(self.investment.product.currency))
        self.lblAmountSymbol.setText(currency_symbol(self.investment.account.currency))
        
    def __calcular(self):
        #Setting self.operinversiones variable
        if self.chkPonderanAll.checkState()==Qt.Checked:#Results are in self.mem.localcurrency
            self.operinversiones=self.mem.data.investments_active().Investment_merging_current_operations_with_same_product(self.investment.product).op_actual
            self.operinversiones.myqtablewidget(self.mqtw)
        else:#Results in account currency
            self.operinversiones=InvestmentOperationCurrentHomogeneusManager(self.mem, self.investment)

            if self.chkGainsTime.checkState()==Qt.Checked:
                self.operinversiones=self.investment.op_actual.ObjectManager_copy_until_datetime(self.mem.localzone.now()-datetime.timedelta(days=365))
            else:
                self.operinversiones=self.investment.op_actual.ObjectManager_copy_until_datetime(self.mem.localzone.now())
            self.operinversiones.myqtablewidget(self.mqtw, self.investment.product.result.basic.last,  eMoneyCurrency.Account)
        sumacciones=self.operinversiones.shares()
        
        #Calculations
        if sumacciones==Decimal(0):
            self.puntoventa=Money(self.mem, 0, self.investment.account.currency)
        else:
            if self.radTPC.isChecked()==True:
                percentage=Percentage(self.spnGainsPercentage.value(), 100)
                self.puntoventa=self.operinversiones.selling_price_to_gain_percentage_of_invested(percentage, eMoneyCurrency.Account)
            elif self.radPrice.isChecked()==True:
                if self.txtPrice.isValid():#Si hay un numero bien
                    self.puntoventa=Money(self.mem,  self.txtPrice.decimal(),  self.investment.product.currency)
                    self.cmd.setEnabled(True)
                else:
                    self.puntoventa=Money(self.mem, 0, self.investment.product.currency)
                    self.cmd.setEnabled(False)
            elif self.radGain.isChecked()==True:
                if self.txtGanancia.isValid():#Si hay un numero bien
                    self.puntoventa=self.operinversiones.selling_price_to_gain_money(Money(self.mem, self.txtGanancia.decimal(), self.investment.product.currency))
                    self.cmd.setEnabled(True)
                else:
                    self.puntoventa=Money(self.mem, 0, self.investment.account.currency)
                    self.cmd.setEnabled(False)

        quote=Quote(self.mem).init__create(self.investment.product, self.mem.localzone.now(), self.puntoventa.amount)
        self.tab.setTabText(1, self.tr("Selling point: {0}".format(self.puntoventa)))
        self.tab.setTabText(0, self.tr("Current state: {0}".format(quote.money())))
        self.operinversiones.myqtablewidget(self.mqtwSP, quote, eMoneyCurrency.Account) 
        
        if self.chkPonderanAll.checkState()==Qt.Checked:
            self.cmd.setText(self.tr("Set selling price to all investments  of {0} to gain {1}").format(self.puntoventa, self.operinversiones.pendiente(quote, eMoneyCurrency.Account)))
        else:
            self.cmd.setText(self.tr("Set {0} shares selling price to {1} to gain {2}").format(sumacciones, self.puntoventa, self.operinversiones.pendiente(quote, eMoneyCurrency.Account)))

    def on_radTPC_clicked(self):
        self.__calcular()
        
    def on_radPrice_clicked(self):
        self.__calcular()
        
    def on_radGain_clicked(self):
        self.__calcular()
        
    @pyqtSlot(float) 
    def on_spnGainsPercentage_valueChanged(self, value):
        self.__calcular()
        
    def on_txtGanancia_textChanged(self):
        self.__calcular()
        
    def on_txtPrice_textChanged(self):
        self.__calcular()
        
    def on_chkPonderanAll_stateChanged(self, state):
        self.__calcular()
        
    def on_chkGainsTime_stateChanged(self, state):
        self.__calcular()

    @pyqtSlot() 
    def on_cmd_released(self):
        if self.chkPonderanAll.checkState()==Qt.Checked:
            for inv in self.mem.data.investments_active().arr:
                if inv.product.id==self.investment.product.id:
                    inv.venta=self.puntoventa.round(inv.product.decimals)
                    inv.save()
            self.mem.con.commit()
        
        #Save in settings the last selling percentage, if that's the case
        if self.radTPC.isChecked():
            percentage=Decimal(self.spnGainsPercentage.value())
            self.mem.settingsdb.setValue("frmSellingPoint/lastgainpercentage", percentage)
        self.done(0)
