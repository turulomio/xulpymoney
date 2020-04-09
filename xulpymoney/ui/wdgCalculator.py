from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QWidget, QTableWidgetItem
from xulpymoney.ui.Ui_wdgCalculator import Ui_wdgCalculator
from xulpymoney.objects.money import Money
from xulpymoney.objects.percentage import Percentage
from xulpymoney.libxulpymoneytypes import eProductType
from xulpymoney.ui.myqdialog import MyModalQDialog
from xulpymoney.ui.wdgOrdersAdd import wdgOrdersAdd
from xulpymoney.ui.wdgProductHistoricalChart import wdgProductHistoricalBuyChart
from xulpymoney.objects.currency import currency_symbol
from decimal import Decimal

class wdgCalculator(QWidget, Ui_wdgCalculator):
    def __init__(self, mem,  parent=None):
        """Compulsory fields are final price and amount"""
        QWidget.__init__(self, parent)
        self.setupUi(self)
        
        self.mem=mem

        self.mqtw.setSettings(self.mem.settings, "wdgCalculator", "mqtw")

        self.investments=None#SetINvestments of the selected product
        self.product=self.mem.data.products.find_by_id(int(self.mem.settings.value("wdgCalculator/product", -9999)), logging=True)
        self.mem.data.investments.ProductManager_with_investments_distinct_products().qcombobox_not_obsolete(self.cmbProducts, self.product)
        self.lblAmount.setText(self.tr("Amount to invest in {} ({})").format(self.mem.localcurrency, currency_symbol(self.mem.localcurrency)))

    def setProduct(self,  product):
        self.cmbProducts.setCurrentIndex(self.cmbProducts.findData(product.id))
        self.txtAmount.setText(self.mem.settingsdb.value_decimal("wdgIndexRange/invertir", "10000"))
        
    ## Sets an investment programatically
    def setInvestment(self, investment):
        self.cmbInvestments.setCurrentIndex(self.cmbInvestments.findData(investment.id))
        self.txtAmount.setText(self.mem.settingsdb.value_decimal("wdgIndexRange/invertir", "10000"))

    def cmbPrice_load(self):       
        if self.product:
            self.cmbPrice.clear() 
            self.cmbPrice.addItem(self.tr("Penultimate price at {} in {} ({})".format(str(self.product.result.basic.penultimate.datetime)[:16], self.product.currency, currency_symbol(self.product.currency))))
            self.cmbPrice.addItem(self.tr("Last price at {} in {} ({})".format(str(self.product.result.basic.last.datetime)[:16], self.product.currency, currency_symbol(self.product.currency))))
            self.cmbPrice.setCurrentIndex(1)#Last price
        else:
            self.cmbPrice.clear()
        

    @pyqtSlot(int)  
    def on_cmbPrice_currentIndexChanged(self, index):
        """To invoke this function you must call self.cmbPrice.setCurrentIndex()"""
        if index==1:
            self.txtProductPrice.setText(self.product.result.basic.last.quote)
        else:
            self.txtProductPrice.setText(self.product.result.basic.penultimate.quote)
            
        self.txtFinalPrice.textChanged.disconnect()
        self.txtFinalPrice.setText(round(self.txtProductPrice.decimal()*Decimal(1+Decimal(self.spnProductPriceVariation.value())*self.txtLeveraged.decimal()/100), 6))
        self.txtFinalPrice.textChanged.connect(self.on_txtFinalPrice_textChanged)
        
        self.calculate()
            
    @pyqtSlot(int)  
    def on_cmbProducts_currentIndexChanged(self, index):
        """To invoke this function you must call self.cmbProducts.setCurrentIndex()"""
        self.product=self.mem.data.products.find_by_id(self.cmbProducts.itemData(index))
        if self.product!=None:
            self.lblFinalPrice.setText(self.tr("Final price in {} ({})").format(self.product.currency, currency_symbol(self.product.currency)))
            if self.product.hasSameLocalCurrency():
                self.lblShares.setText(self.tr("Shares calculated"))
            else:
                self.lblShares.setText(self.tr("Shares calculated with {} at {}").format(Money(self.mem, 1, self.mem.localcurrency).conversionFactorString(self.product.currency, self.mem.localzone.now()), self.mem.localzone.now()))
            
            #Fills self.cmbInvestments with all product investments or with zero shares product investments
            if self.chkWithoutShares.checkState()==Qt.Checked:
                self.investments=self.mem.data.investments.InvestmentManager_with_investments_with_the_same_product_with_zero_shares(self.product)
            else:
                self.investments=self.mem.data.investments.InvestmentManager_with_investments_with_the_same_product(self.product)
            self.investments.qcombobox(self.cmbInvestments, tipo=3, selected=None, obsolete_product=False, investments_active=None, accounts_active=None)
 
            self.mem.settings.setValue("wdgCalculator/product", self.product.id)
            
            self.cmbPrice_load()        
            self.txtLeveraged.setText(self.product.leveraged.multiplier)
            self.txtFinalPrice.textChanged.disconnect()
            self.txtFinalPrice.setText(round(self.txtProductPrice.decimal()*Decimal(1+Decimal(self.spnProductPriceVariation.value())*self.txtLeveraged.decimal()/100), 6))
            self.txtFinalPrice.textChanged.connect(self.on_txtFinalPrice_textChanged)
        
            self.calculate()

    @pyqtSlot(int)  
    def on_cmbInvestments_currentIndexChanged(self, index):
        """To invoke this function you must call self.cmbInvestments.setCurrentIndex()"""
        if index>=0:#Only enabled if some investment is selected
            self.cmdOrder.setEnabled(True)
        else:
            self.cmdOrder.setEnabled(False)
        self.investments.selected=self.mem.data.investments.find_by_id(self.cmbInvestments.itemData(index))


    ## This check filters investments showing ones with 0 currrent shares
    def on_chkWithoutShares_stateChanged(self, state):
        self.on_cmbProducts_currentIndexChanged(self.cmbProducts.currentIndex())
        
    @pyqtSlot()
    def on_cmdOrder_released(self):
        d=MyModalQDialog(self)
        d.setWindowTitle(self.tr("Add new order"))
        d.setSettings(self.mem.settings,"wdgCalculator", "mqdOrdersAdd ")
        w=wdgOrdersAdd(self.mem, None, self.investments.selected, d)
        w.txtShares.setText(self.txtShares.decimal())
        w.txtPrice.setText(self.txtFinalPrice.decimal())
        d.setWidgets(w)
        d.exec_()

    @pyqtSlot()
    def on_cmdGraph_released(self):
        self.product.needStatus(2)
        d=MyModalQDialog(self)     
        d.showMaximized()
        d.setWindowTitle(self.tr("Purchase graph"))
        d.setSettings(self.mem.settings, "wdgCalculator", "mqdBuyGraph")
        wc=wdgProductHistoricalBuyChart()
        wc.setProduct(self.product, None)
        wc.setPrice(self.txtFinalPrice.decimal())
        wc.generate()
        wc.display()
        d.setWidgets(wc)
        d.exec_()

    @pyqtSlot(float)
    def on_spnProductPriceVariation_valueChanged(self, value):
        self.on_cmbProducts_currentIndexChanged(self.cmbProducts.currentIndex())
        
    def on_txtFinalPrice_textChanged(self):
        self.spnProductPriceVariation.valueChanged.disconnect()
        self.spnProductPriceVariation.setValue(100*(self.txtFinalPrice.decimal()-self.txtProductPrice.decimal())/self.txtProductPrice.decimal()/self.txtLeveraged.decimal())
        self.spnProductPriceVariation.valueChanged.connect(self.on_spnProductPriceVariation_valueChanged)
        self.calculate()

    def on_txtAmount_textChanged(self):
        self.calculate()

    def calculate(self):
        """Checks if compulsory fields are ok, if not changes style to red, else calculate mqtw and shares"""
        if self.txtAmount.isValid() and self.txtFinalPrice.isValid():
            finalprice=Money(self.mem, self.txtFinalPrice.decimal(), self.product.currency).convert(self.mem.localcurrency).amount
            if self.product.type.id in (eProductType.Share, eProductType.ETF):#Shares
                self.txtShares.setText(round(self.txtAmount.decimal()/finalprice, 0))
            else:
                self.txtShares.setText(round(self.txtAmount.decimal()/finalprice, 6))
            porcentages=[2.5, 5, 7.5, 10, 15, 30]
            self.mqtw.table.setColumnCount(3)
            self.mqtw.table.setHorizontalHeaderItem(0, QTableWidgetItem(self.tr("% Gains" )))
            self.mqtw.table.setHorizontalHeaderItem(1, QTableWidgetItem(self.tr("Price" )))
            self.mqtw.table.setHorizontalHeaderItem(2, QTableWidgetItem(self.tr("Gains" )))
            self.mqtw.table.clearContents()
            self.mqtw.applySettings()
            self.mqtw.table.setRowCount(len(porcentages))
            for i, tpc in enumerate(porcentages):        
                self.mqtw.table.setItem(i, 0, Percentage(tpc, 100).qtablewidgetitem())
                tpcprice= self.txtFinalPrice.decimal()*Decimal(1+tpc/100)
                self.mqtw.table.setItem(i, 1, self.product.money(tpcprice).qtablewidgetitem())       
                self.mqtw.table.setItem(i, 2, self.product.money(self.txtShares.decimal()*(tpcprice-self.txtFinalPrice.decimal())).qtablewidgetitem())
