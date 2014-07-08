from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Ui_wdgCalculator import *
from libxulpymoney import *

class wdgCalculator(QWidget, Ui_wdgCalculator):
    def __init__(self, mem,  parent=None):
        """Compulsory fields are final price and amount"""
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        self.mem.data.load_inactives()
        self.product=None
        self.mem.data.investments_all().qcombobox(self.cmbProducts)
        
        
        
    def init__percentagevariation_amount(self, percentagevariation, amount):
        self.spnProductPriceVariation.setValue(percentagevariation)
        self.txtAmount.setText(amount)

    @pyqtSlot(int)  
    def on_cmbProducts_currentIndexChanged(self, index):
        self.product=self.mem.data.investments_all().find(self.cmbProducts.itemData(index))
        self.txtLeveraged.setText(self.product.apalancado.multiplier)
        self.txtProductPrice.setText(self.product.result.basic.last.quote)
        self.txtFinalPrice.setText(self.txtProductPrice.decimal()*Decimal(1+Decimal(self.spnProductPriceVariation.value())*self.txtLeveraged.decimal()/100))
        self.calculate()
        
        
    @pyqtSlot(float)  
    def on_spnProductPriceVariation_valueChanged(self, value):
        self.on_cmbProducts_currentIndexChanged(self.cmbProducts.currentIndex())
        
    def on_txtFinalPrice_textChanged(self):
        self.calculate()
        
    def on_txtAmount_textChanged(self):
        self.calculate()

    def calculate(self):
        """Checks if compulsory fields are ok, if not changes style to red, else calculate table and shares"""
        if self.txtAmount.isValid() and self.txtFinalPrice.isValid():
            if self.product.type.id in (1, 4):#Shares
                self.txtShares.setText(round(self.txtAmount.decimal()/self.txtFinalPrice.decimal(), 0))
            porcentages=[2.5, 5, 7.5, 10, 15, 30]
            self.table.clearContents()
            self.table.setRowCount(len(porcentages))
            for i, tpc in enumerate(porcentages):        
                self.table.setItem(i, 0, qtpc(tpc))
                tpcprice= self.txtFinalPrice.decimal()*Decimal(1+tpc/100)
                self.table.setItem(i, 1, self.product.currency.qtablewidgetitem(tpcprice))       
                self.table.setItem(i, 2, self.product.currency.qtablewidgetitem(self.txtShares.decimal()*(tpcprice-self.txtFinalPrice.decimal())))

