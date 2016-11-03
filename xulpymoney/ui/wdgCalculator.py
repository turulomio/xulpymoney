from PyQt5.QtCore import *
from PyQt5.QtGui import *
from Ui_wdgCalculator import *
from libxulpymoney import *
from wdgOrdersAdd import *
from frmInvestmentReport import *
from frmProductReport import *

class wdgCalculator(QWidget, Ui_wdgCalculator):
    def __init__(self, mem,  parent=None):
        """Compulsory fields are final price and amount"""
        QWidget.__init__(self, parent)
        self.setupUi(self)
        
        self.mem=mem
         
        self.table.settings(self.mem, "wdgCalculator")
        self.hasProducts=True#Permits to show/hide the widget from external dialog
        if self.mem.data.products.length()==0:
            m=QMessageBox()
            m.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
            m.setIcon(QMessageBox.Information)
            m.setText(self.tr("You need to create at least one investment"))
            m.exec_()
            self.hasProducts=False        
            self.close()
            return
            
        self.investments=None#SetINvestments of the selected product
        self.product=self.mem.data.products.find_by_id(int(self.mem.settings.value("wdgCalculator/product", 79228)))
        self.mem.data.products.qcombobox_not_obsolete(self.cmbProducts, self.product)
        
    def setProduct(self,  product):
        print("setproduct")
        self.cmbProducts.setCurrentIndex(self.cmbProducts.findData(product.id))
        self.txtAmount.setText(Decimal(self.mem.settingsdb.value("wdgIndexRange/invertir", "10000")))
        
    def setInvestment(self, investment):
        self.cmbInvestments.setCurrentIndex(self.cmbInvestments.findData(investment.id))
        self.txtAmount.setText(Decimal(self.mem.settingsdb.value("wdgIndexRange/invertir", "10000")))


    def cmbPrice_load(self):       
        if self.product:
            self.cmbPrice.clear() 
            self.cmbPrice.addItem(self.tr("Penultimate price ({})".format(str(self.product.result.basic.penultimate.datetime)[:16])))
            self.cmbPrice.addItem(self.tr("Last price ({})".format(str(self.product.result.basic.last.datetime)[:16])))
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
        self.txtFinalPrice.setText(self.txtProductPrice.decimal()*Decimal(1+Decimal(self.spnProductPriceVariation.value())*self.txtLeveraged.decimal()/100))
        self.txtFinalPrice.textChanged.connect(self.on_txtFinalPrice_textChanged)
        
        self.calculate()
            
    @pyqtSlot(int)  
    def on_cmbProducts_currentIndexChanged(self, index):
        """To invoke this function you must call self.cmbProducts.setCurrentIndex()"""
        self.product=self.mem.data.products.find_by_id(self.cmbProducts.itemData(index))
                
        self.investments=self.product.setinvestments()
        self.investments.qcombobox(self.cmbInvestments, tipo=3, selected=None, obsolete_product=False, investments_active=None, accounts_active=None)
        self.mem.settings.setValue("wdgCalculator/product", self.product.id)
        
        self.cmbPrice_load()        
        self.txtLeveraged.setText(self.product.leveraged.multiplier)
        self.txtFinalPrice.textChanged.disconnect()
        self.txtFinalPrice.setText(self.txtProductPrice.decimal()*Decimal(1+Decimal(self.spnProductPriceVariation.value())*self.txtLeveraged.decimal()/100))
        self.txtFinalPrice.textChanged.connect(self.on_txtFinalPrice_textChanged)
    
        self.calculate()

    @pyqtSlot(int)  
    def on_cmbInvestments_currentIndexChanged(self, index):
        """To invoke this function you must call self.cmbInvestments.setCurrentIndex()"""
        print (index)
        if index>=0:#Only enabled if some investment is selected
            self.cmdOrder.setEnabled(True)
        else:
            self.cmdOrder.setEnabled(False)
        self.investments.selected=self.mem.data.investments.find_by_id(self.cmbInvestments.itemData(index))

    @pyqtSlot()
    def on_cmdOrder_released(self):
        d=QDialog(self)     
        d.setModal(True)
        d.setWindowTitle(self.tr("Add new order"))
        w=wdgOrdersAdd(self.mem, None, self.investments.selected, d)
        w.txtShares.setText(self.txtShares.decimal())
        w.txtPrice.setText(self.txtFinalPrice.decimal())
        lay = QVBoxLayout(d)
        lay.addWidget(w)
        d.exec_()

    @pyqtSlot()
    def on_cmdGraph_released(self):
        self.product.result.get_basic_and_ohcls()
        d=QDialog(self)     
        d.setWindowTitle(self.tr("Purchase graph"))
        d.showMaximized()
        w=canvasChartHistoricalBuy(self.mem, d)
        w.load_data(self.product, self.txtFinalPrice.decimal())
        lay = QVBoxLayout(d)
        lay.addWidget(w)
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
        """Checks if compulsory fields are ok, if not changes style to red, else calculate table and shares"""
            
        if self.txtAmount.isValid() and self.txtFinalPrice.isValid():
            if self.product.type.id in (1, 4):#Shares
                self.txtShares.setText(round(self.txtAmount.decimal()/self.txtFinalPrice.decimal(), 0))
            else:
                self.txtShares.setText(round(self.txtAmount.decimal()/self.txtFinalPrice.decimal(), 6))
            porcentages=[2.5, 5, 7.5, 10, 15, 30]
            self.table.clearContents()
            self.table.setRowCount(len(porcentages))
            for i, tpc in enumerate(porcentages):        
                self.table.setItem(i, 0, qtpc(tpc))
                tpcprice= self.txtFinalPrice.decimal()*Decimal(1+tpc/100)
                self.table.setItem(i, 1, self.product.currency.qtablewidgetitem(tpcprice))       
                self.table.setItem(i, 2, self.product.currency.qtablewidgetitem(self.txtShares.decimal()*(tpcprice-self.txtFinalPrice.decimal())))
