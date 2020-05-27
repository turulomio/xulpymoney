from PyQt5.QtWidgets import QWidget,  QTableWidgetItem,  QMenu
from PyQt5.QtCore import pyqtSlot
from xulpymoney.libxulpymoneytypes import eMoneyCurrency
from xulpymoney.ui.Ui_wdgInvestmentsRanking import Ui_wdgInvestmentsRanking
from xulpymoney.ui.frmInvestmentReport import frmInvestmentReport
from xulpymoney.ui.frmProductReport import frmProductReport
from xulpymoney.objects.money import Money

class wdgInvestmentsRanking(QWidget, Ui_wdgInvestmentsRanking):
    def __init__(self, mem,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        self.selOperations=None
        self.selCurrentOperations=None

        self.tab.setCurrentIndex(0)
        self.mqtwOperations.setSettings(self.mem.settings,"wdgInvestmentsRanking" , "mqtwOperations")
        self.mqtwOperations.table.customContextMenuRequested.connect(self.on_mqtwOperations_customContextMenuRequested)
        self.mqtwOperations.table.itemSelectionChanged.connect(self.on_mqtwOperations_itemSelectionChanged)
        self.mqtwOperations.table.setColumnCount(5)
        self.mqtwOperations.table.setHorizontalHeaderItem(0, QTableWidgetItem(self.tr("Investment")))
        self.mqtwOperations.table.setHorizontalHeaderItem(1, QTableWidgetItem(self.tr("Current gains")))
        self.mqtwOperations.table.setHorizontalHeaderItem(2, QTableWidgetItem(self.tr("Historical gains")))
        self.mqtwOperations.table.setHorizontalHeaderItem(3, QTableWidgetItem(self.tr("Dividends")))
        self.mqtwOperations.table.setHorizontalHeaderItem(4, QTableWidgetItem(self.tr("Total")))

        set=self.mem.data.investments.InvestmentManager_merging_investments_with_same_product_merging_operations()
        self.mqtwOperations.applySettings()
        self.mqtwOperations.table.clearContents()
        self.mqtwOperations.table.setRowCount(set.length()+1)
        self.listOperations=[]
        sumcurrent=Money(self.mem, 0, self.mem.localcurrency)
        sumhistorical=Money(self.mem, 0, self.mem.localcurrency)
        sumdividends=Money(self.mem, 0, self.mem.localcurrency)
        for i, inv in enumerate(set.arr):
            inv.needStatus(3)
            gains_current=inv.op_actual.pendiente(inv.product.result.basic.last, type=3)
            gains_historical=inv.op_historica.consolidado_bruto(type=3)
            dividends_gross=inv.dividends.gross(eMoneyCurrency.User, current=False)
            total=gains_current+gains_historical+dividends_gross
            sumcurrent=sumcurrent+gains_current
            sumhistorical=sumhistorical+gains_historical
            sumdividends=sumdividends+dividends_gross
            self.listOperations.append((inv, gains_current, gains_historical, dividends_gross, total))

        self.listOperations=sorted(self.listOperations, key=lambda c: c[4],  reverse=True)     

        for i, l in enumerate(self.listOperations):
            self.mqtwOperations.table.setItem(i, 0, QTableWidgetItem(l[0].product.name))
            self.mqtwOperations.table.setItem(i, 1, l[1].qtablewidgetitem())
            self.mqtwOperations.table.setItem(i, 2,  l[2].qtablewidgetitem())
            self.mqtwOperations.table.setItem(i, 3, l[3].qtablewidgetitem())
            self.mqtwOperations.table.setItem(i, 4, l[4].qtablewidgetitem())
        self.mqtwOperations.table.setItem(len(self.listOperations)+1, 0, QTableWidgetItem(self.tr("Total")))
        self.mqtwOperations.table.setItem(len(self.listOperations)+1, 1, sumcurrent.qtablewidgetitem())
        self.mqtwOperations.table.setItem(len(self.listOperations)+1, 2, sumhistorical.qtablewidgetitem())
        self.mqtwOperations.table.setItem(len(self.listOperations)+1, 3, sumdividends.qtablewidgetitem())
        self.mqtwOperations.table.setItem(len(self.listOperations)+1, 4, (sumcurrent+sumhistorical+sumdividends).qtablewidgetitem())

#####################################################################################################################33



        self.mqtwCurrentOperations.setSettings(self.mem.settings,"wdgInvestmentsRanking" , "mqtwCurrentOperations")
        self.mqtwCurrentOperations.table.customContextMenuRequested.connect(self.on_mqtwCurrentOperations_customContextMenuRequested)
        
        hh=[self.tr("Investment"), self.tr("Current gains"),  self.tr("Historical gains"),  self.tr("Dividends"), self.tr("Total")]
        data=[]
        sumcurrent=Money(self.mem, 0, self.mem.localcurrency)
        sumhistorical=Money(self.mem, 0, self.mem.localcurrency)
        sumdividends=Money(self.mem, 0, self.mem.localcurrency)
        for product in self.mem.data.investments.ProductManager_with_investments_distinct_products().arr:
            current=Money(self.mem, 0, self.mem.localcurrency)
            historical=Money(self.mem, 0, self.mem.localcurrency)
            dividends=Money(self.mem, 0, self.mem.localcurrency)

            for inv in self.mem.data.investments.arr:
                if inv.product.id==product.id:
                    current=current+inv.op_actual.pendiente(inv.product.result.basic.last, 3)
                    historical=historical+inv.op_historica.consolidado_bruto(type=3)
                    dividends=dividends+inv.dividends.gross(eMoneyCurrency.User, current=False)
            sumcurrent=sumcurrent+current
            sumhistorical=sumhistorical+historical
            sumdividends=sumdividends+dividends
            data.append((product, current, historical, dividends, current+historical+dividends))

        data=sorted(data, key=lambda c: c[4],  reverse=True)     
       
        self.mqtwCurrentOperations.setData(hh, None, data)
        self.mqtwCurrentOperations.table.setRowCount(self.mqtwCurrentOperations.length()+1)
        self.mqtwCurrentOperations.addRow(self.mqtwCurrentOperations.length(), [self.tr("Total"), sumcurrent, sumhistorical, sumdividends, sumcurrent+sumhistorical+sumdividends])

    @pyqtSlot() 
    def on_actionSameProduct_triggered(self):
        inv=self.mem.data.investments.Investment_merging_current_operations_with_same_product(self.selCurrentOperations)
        w=frmInvestmentReport(self.mem, inv, self)
        w.exec_()

    @pyqtSlot() 
    def on_actionSameProductFIFO_triggered(self):
        w=frmInvestmentReport(self.mem, self.selOperations, self)
        w.exec_()

    @pyqtSlot() 
    def on_actionProduct_triggered(self):
        if self.tab.currentIndex()==0:
            product=self.selCurrentOperations
            inv=self.mem.data.investments.Investment_merging_current_operations_with_same_product(self.selCurrentOperations)
        else:
            product=self.selOperations.product
            inv=self.selOperations

        w=frmProductReport(self.mem, product, inv, self)
        w.exec_()

    def on_mqtwOperations_customContextMenuRequested(self,  pos):
        if self.selOperations==None:
            self.actionProduct.setEnabled(False)
            self.actionSameProductFIFO.setEnabled(False)
        else:
            self.actionProduct.setEnabled(True)
            self.actionSameProductFIFO.setEnabled(True)

        menu=QMenu()
        menu.addAction(self.actionProduct)
        menu.addSeparator()
        menu.addAction(self.actionSameProductFIFO)      
        menu.exec_(self.mqtwOperations.table.mapToGlobal(pos))

    def on_mqtwOperations_itemSelectionChanged(self):
        self.selOperations=None
        try:
            for i in self.mqtwOperations.table.selectedItems():#itera por cada item no row.
                self.selOperations=self.listOperations[i.row()][0]
        except:
            pass
            
            
        
    def on_mqtwCurrentOperations_customContextMenuRequested(self,  pos):
        if self.selCurrentOperations==None:
            self.actionProduct.setEnabled(False)
            self.actionSameProduct.setEnabled(False)
        else:
            self.actionProduct.setEnabled(True)
            self.actionSameProduct.setEnabled(True)

        menu=QMenu()
        menu.addAction(self.actionProduct)
        menu.addSeparator()
        menu.addAction(self.actionSameProduct)
        menu.exec_(self.mqtwCurrentOperations.table.mapToGlobal(pos))

