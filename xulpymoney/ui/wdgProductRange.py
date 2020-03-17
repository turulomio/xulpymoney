from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMenu, QWidget, QDialog, QVBoxLayout
from logging import debug
from xulpymoney.ui.Ui_wdgProductRange import Ui_wdgProductRange
from xulpymoney.objects.productrange import ProductRangeManager
from xulpymoney.objects.percentage import Percentage
from decimal import Decimal

class wdgProductRange(QWidget, Ui_wdgProductRange):
    def __init__(self,mem, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem

        self.mqtw.settings(self.mem.settings, "wdgProductRange", "mqtw")
        self.mqtw.table.customContextMenuRequested.connect(self.on_mqtw_customContextMenuRequested)
        
        self.spnDown.setValue(float(self.mem.settings.value("wdgProductRange/spnDown", "5")))
        self.spnGains.setValue(float(self.mem.settings.value("wdgProductRange/spnGains", "5")))
        self.txtInvertir.setText(Decimal(self.mem.settings.value("wdgProductRange/invertir", "10000")))
        product_in_settings=self.mem.data.products.find_by_id(int(self.mem.settings.value("wdgProductRange/product", "79329")))

        products=self.mem.data.investments.ProductManager_with_investments_distinct_products()
        products.order_by_name()
        products.qcombobox(self.cmbProducts, product_in_settings)

    def load_data(self):
        self.prm=ProductRangeManager(self.mem, self.product, Percentage(self.spnDown.value(), 100), Percentage(self.spnGains.value(), 100))
        self.prm.mqtw(self.mqtw)
        
        self.mem.settings.setValue("wdgProductRange/spnDown", self.spnDown.value())
        self.mem.settings.setValue("wdgProductRange/spnGains", self.spnGains.value())
        self.mem.settings.setValue("wdgProductRange/invertir", self.txtInvertir.text())
        self.mem.settings.setValue("wdgProductRange/product", self.product.id)
        self.mem.settings.sync()
        
        self.lblTotal.setText(self.tr("Total invested: {}. Current balance: {} ({})").format(self.investment_merged.invertido(),  self.investment_merged.balance(), self.investment_merged.op_actual.tpc_total(self.product.result.basic.last)))

    def on_cmd_pressed(self):
        self.load_data()
        
    @pyqtSlot(int)
    def on_cmbShowOptions_currentIndexChanged(self, index):
        self.load_data()

    @pyqtSlot(int)
    def on_cmbProducts_currentIndexChanged(self, index):
        if index==-1:
            debug("-1")
            return
        debug("cmbProducts index changed to {}".format(index))
        self.product=self.mem.data.products.find_by_id(self.cmbProducts.itemData(index))
        self.investment_merged=self.mem.data.investments.Investment_merging_current_operations_with_same_product(self.product)
        self.load_data()

    def on_cmdIRAnalisis_pressed(self):
        from xulpymoney.ui.frmProductReport import frmProductReport
        w=frmProductReport(self.mem, self.product, None,  self)
        w.exec_()
        
    def on_cmdIRInsertar_pressed(self):
        from xulpymoney.ui.frmQuotesIBM import frmQuotesIBM
        w=frmQuotesIBM(self.mem, self.product, None,  self)
        w.exec_() 
        self.product.needStatus(2, downgrade_to=0)
        self.cmbBenchmarkCurrent_load()
        self.load_data()

    def on_mqtw_customContextMenuRequested(self,  pos):
        if self.mqtw.selected is not None:
            menu=QMenu()
            menu.addAction(self.actionOrderAdd)   
            menu.addSeparator()
            menu.addMenu(self.mqtw.qmenu())
            menu.exec_(self.mqtw.table.mapToGlobal(pos))

    @pyqtSlot() 
    def on_actionOrderAdd_triggered(self):
        from xulpymoney.ui.wdgOrdersAdd import wdgOrdersAdd
        d=QDialog(self)     
        d.setModal(True)
        d.setWindowTitle(self.tr("Add new order"))
        w=wdgOrdersAdd(self.mem, None, None, d)
        w.txtPrice.setText(self.mqtw.selected.value_rounded())
        w.txtShares.setText(int(self.txtInvertir.decimal()/self.mqtw.selected.value_rounded()))
        w.cmbProducts.setCurrentIndex(w.cmbProducts.findData(self.product.id))
        lay = QVBoxLayout(d)
        lay.addWidget(w)
        d.exec_()
        
