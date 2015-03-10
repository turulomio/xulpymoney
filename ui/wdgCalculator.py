from PyQt5.QtCore import *
from PyQt5.QtGui import *
from Ui_wdgCalculator import *
from libxulpymoney import *

class wdgCalculator(QWidget, Ui_wdgCalculator):
    def __init__(self, mem,  parent=None):
        """Compulsory fields are final price and amount"""
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        self.mem.data.load_inactives()
        self.hasProducts=True#Permits to show/hide the widget from external dialog
        if self.mem.data.products_all().length()==0:
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.tr("You need to create at least one investment"))
            m.exec_()
            self.hasProducts=False        
            return
        self.product=self.mem.data.products_all().find(self.mem.config.get_value("wdgCalculator", "Product"))
        
        self.load_cmbPrice()
        
        self.mem.data.products_all().qcombobox(self.cmbProducts, self.product)
        self.txtAmount.setText(self.mem.config.get_value("wdgCalculator", "Invested"))

    def init__percentagevariation_amount(self, percentagevariation, amount):
        if self.hasProducts==True:
            self.spnProductPriceVariation.setValue(percentagevariation)
            self.txtAmount.setText(amount)

    def load_cmbPrice(self):       
        self.cmbPrice.clear() 
        self.cmbPrice.addItem(self.tr("Penultimate price ({})".format(str(self.product.result.basic.penultimate.datetime)[:16])))
        self.cmbPrice.addItem(self.tr("Last price ({})".format(str(self.product.result.basic.last.datetime)[:16])))
        self.cmbPrice.setCurrentIndex(1)#Last price

    @pyqtSlot(int)  
    def on_cmbPrice_currentIndexChanged(self, index):
        if index==1:
            self.txtProductPrice.setText(self.product.result.basic.last.quote)
        else:
            self.txtProductPrice.setText(self.product.result.basic.penultimate.quote)
            
        self.txtFinalPrice.setText(self.txtProductPrice.decimal()*Decimal(1+Decimal(self.spnProductPriceVariation.value())*self.txtLeveraged.decimal()/100))
        self.calculate()
            
    @pyqtSlot(int)  
    def on_cmbProducts_currentIndexChanged(self, index):
        self.product=self.mem.data.products_all().find(self.cmbProducts.itemData(index))
        if self.product:
            self.mem.config.set_value("wdgCalculator", "Product", self.product.id)##Save selected product
            self.mem.config.save()
            
        self.load_cmbPrice()
        
        self.txtLeveraged.setText(self.product.apalancado.multiplier)
        self.txtFinalPrice.setText(self.txtProductPrice.decimal()*Decimal(1+Decimal(self.spnProductPriceVariation.value())*self.txtLeveraged.decimal()/100))
        self.calculate()
        
        
    @pyqtSlot(float)  
    def on_spnProductPriceVariation_valueChanged(self, value):
        self.on_cmbProducts_currentIndexChanged(self.cmbProducts.currentIndex())
        
    def on_txtFinalPrice_textChanged(self):
        self.calculate()
        
    def on_txtAmount_textChanged(self):
        if self.txtAmount.isValid():
            self.mem.config.set_value("wdgCalculator", "Invested", self.txtAmount.decimal())##Save invested amount
            self.mem.config.save()
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

