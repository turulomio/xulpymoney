from PyQt5.QtCore import pyqtSlot, QObject
from PyQt5.QtWidgets import QMenu, QWidget, QDialog, QVBoxLayout, QAction
from datetime import date
from logging import debug
from xulpymoney.decorators import timeit
from xulpymoney.ui.myqdialog import MyModalQDialog
from xulpymoney.ui.myqwidgets import qmessagebox
from xulpymoney.libxulpymoneytypes import eMoneyCurrency
from xulpymoney.objects.assets import Assets
from xulpymoney.objects.percentage import Percentage, percentage_between
from xulpymoney.objects.productrange import ProductRangeManager
from xulpymoney.ui.Ui_wdgProductRange import Ui_wdgProductRange

class wdgProductRange(QWidget, Ui_wdgProductRange):
    def __init__(self,mem, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem

        self.mqtw.setSettings(self.mem.settings, "wdgProductRange", "mqtw")
        self.mqtw.table.customContextMenuRequested.connect(self.on_mqtw_customContextMenuRequested)
        self.mqtw.setVerticalHeaderHeight(None)#Must be after settings, to allow wrap text in qtablewidgetitems
        product_in_settings=self.mem.data.products.find_by_id(self.mem.settingsdb.value_integer("wdgProductRange/product", "79329"))

        products=self.mem.data.investments_active().ProductManager_with_investments_distinct_products(only_with_shares=False)
        products.order_by_name()
        products.qcombobox(self.cmbProducts, product_in_settings)

    @timeit
    def load_data(self):
        self.product.needStatus(2)
        percentage_down=Percentage(self.spnDown.value(), 100)
        percentage_gains=Percentage(self.spnGains.value(), 100)
        self.prm=ProductRangeManager(self.mem, self.product, percentage_down, percentage_gains)
        self.prm.setInvestRecomendation(self.cmbRecomendations.currentIndex())
        self.prm.mqtw(self.mqtw)

        self.mem.settingsdb.setValue("wdgProductRange/spnDown_product_{}".format(self.product.id), self.spnDown.value())
        self.mem.settingsdb.setValue("wdgProductRange/spnGains_product_{}".format(self.product.id), self.spnGains.value())
        self.mem.settingsdb.setValue("wdgProductRange/invest_product_{}".format(self.product.id), self.txtInvertir.text())
        self.mem.settingsdb.setValue("wdgProductRange/invest_recomendation_{}".format(self.product.id), self.cmbRecomendations.currentIndex())
        self.mem.settingsdb.setValue("wdgProductRange/product", self.product.id)
        self.mem.settings.sync()

        s=self.tr("Product current price: {} at {}").format(
            self.product.result.basic.last.money(),
            self.product.result.basic.last.datetime, 
        )
        s=s + "\n" + self.tr("Product price limits: {}").format(self.product.result.ohclYearly.string_limits())
        s=s + "\n" + self.tr("Total invested: {}. Current balance: {} ({})").format(
            self.investment_merged.invertido(),  
            self.investment_merged.balance(), 
            self.investment_merged.op_actual.tpc_total(self.product.result.basic.last), 
        )
        s=s + "\n" + self.tr("Average price: {}").format(
            self.investment_merged.op_actual.average_price()
        )
        s=s + "\n" + self.tr("Selling price to gain {}: {}. Gains at this selling price: {} ({})").format(
            percentage_gains, 
            self.investment_merged.op_actual.selling_price_to_gain_percentage_of_invested(percentage_gains, eMoneyCurrency.Product), 
            self.investment_merged.op_actual.gains_from_percentage(percentage_gains, eMoneyCurrency.Product), 
            percentage_between(self.product.result.basic.last.money(), self.investment_merged.op_actual.selling_price_to_gain_percentage_of_invested(percentage_gains, eMoneyCurrency.Product)), 
        )
        
        s=s + "\n\n"+ self.tr("Zero risk assets: {}".format(Assets(self.mem).patrimonio_riesgo_cero(date.today())))

        self.lblTotal.setText(s)
        
    def on_cmd_pressed(self):
        if hasattr(self, "product"):
            self.load_data()
        else:
            qmessagebox(self.tr("You must select a product"))

    @pyqtSlot(int)
    def on_cmbProducts_currentIndexChanged(self, index):
        if index>=0:
            debug("cmbProducts index changed to {}".format(index))
            self.product=self.mem.data.products.find_by_id(self.cmbProducts.itemData(index))
            self.investment_merged=self.mem.data.investments.Investment_merging_current_operations_with_same_product(self.product)
            self.spnDown.setValue(self.mem.settingsdb.value_float("wdgProductRange/spnDown_product_{}".format(self.product.id), "5"))
            self.spnGains.setValue(self.mem.settingsdb.value_float("wdgProductRange/spnGains_product_{}".format(self.product.id), "5"))
            self.txtInvertir.setText(self.mem.settingsdb.value_decimal("wdgProductRange/invest_product_{}".format(self.product.id), "10000"))
            self.cmbRecomendations.setCurrentIndex(self.mem.settingsdb.value_integer("wdgProductRange/invest_recomendation_{}".format(self.product.id), "2"))
            self.load_data()

    def on_cmdIRAnalisis_pressed(self):
        from xulpymoney.ui.frmProductReport import frmProductReport
        w=frmProductReport(self.mem, self.product, None,  self)
        w.exec_()

    def on_cmdDrawRanges_pressed(self):       
        from xulpymoney.ui.wdgProductHistoricalChart import wdgProductHistoricalChart
        d=MyModalQDialog(self)     
        d.setSettings(self.mem.settings, "wdgProductRange","MyModalQDialog")
        d.setWindowTitle(self.tr("Historical report of {}").format(self.product.name))
        wdgTSHistorical=wdgProductHistoricalChart(d)
        wdgTSHistorical.setProduct(self.product, None)
        wdgTSHistorical.setDrawRangeLines(self.prm.list_of_range_values())
        wdgTSHistorical.generate()
        wdgTSHistorical.display()
        d.setWidgets(wdgTSHistorical)
        d.exec_()

    def on_cmdIRInsertar_pressed(self):
        from xulpymoney.ui.frmQuotesIBM import frmQuotesIBM
        w=frmQuotesIBM(self.mem, self.product, None,  self)
        w.exec_() 
        self.product.needStatus(2, downgrade_to=0)
        self.load_data()

    def on_mqtw_customContextMenuRequested(self,  pos):    
        # Dinamic action trigerred
        def on_menuInvestment_action_triggered():
            from xulpymoney.ui.frmInvestmentReport import frmInvestmentReport
            action=QObject.sender(self)#Busca el objeto que ha hecho la signal en el slot en el que está conectado
            investment=self.mem.data.investments.find_by_fullName(action.text())
            w=frmInvestmentReport(self.mem,  investment, self)
            w.exec_()
            self.load_data()
        # -------------------------------------------------------------
        if self.mqtw.selected is not None:
            if hasattr(self, "investment_merged")==True:
                self.actionInvestmentMergingCurrent.setEnabled=True
            else:
                self.actionInvestmentMergingCurrent.setEnabled=False

            menu=QMenu()
            menu.addAction(self.actionRangeInformation)   
            menu.addSeparator()
            menu.addAction(self.actionOrderAdd)   
            #Dinamic investments by range
            menuInvestments=QMenu(self.tr("Investments in this range"))
            for o in self.mqtw.selected.getInvestmentsInside().arr:
                action=QAction(o.fullName(), menuInvestments)
                action.triggered.connect(on_menuInvestment_action_triggered)
                action.setIcon(o.qicon())
                menuInvestments.addAction(action)
            menu.addMenu(menuInvestments)
            menu.addSeparator()
            menu.addAction(self.actionInvestmentMergingCurrent)
            menu.addSeparator()

            #mqtw menu
            menu.addMenu(self.mqtw.qmenu())
            menu.exec_(self.mqtw.table.mapToGlobal(pos))
            
    @pyqtSlot() 
    def on_actionRangeInformation_triggered(self):
        qmessagebox(self.tr("Range limits are {}").format(self.mqtw.selected))

    @pyqtSlot() 
    def on_actionInvestmentMergingCurrent_triggered(self):
        from xulpymoney.ui.frmInvestmentReport import frmInvestmentReport
        w=frmInvestmentReport(self.mem,  self.investment_merged, self)
        w.exec_()
        self.load_data()

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
        self.load_data()
