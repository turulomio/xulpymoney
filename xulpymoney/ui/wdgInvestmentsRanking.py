from PyQt5.QtWidgets import QWidget,  QTableWidgetItem,  QMenu
from PyQt5.QtCore import pyqtSlot
from xulpymoney.ui.Ui_wdgInvestmentsRanking import Ui_wdgInvestmentsRanking
from xulpymoney.ui.frmInvestmentReport import frmInvestmentReport
from xulpymoney.ui.frmProductReport import frmProductReport
from xulpymoney.libxulpymoney import Money

class wdgInvestmentsRanking(QWidget, Ui_wdgInvestmentsRanking):
    def __init__(self, mem,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        self.selOperations=None
        self.selCurrentOperations=None
            
        self.tab.setCurrentIndex(0)
        self.tblOperations.settings(self.mem,"wdgInvestmentsRanking" , "self.tblOperations")
        self.tblOperations.setColumnCount(5)
        self.tblOperations.setHorizontalHeaderItem(0, QTableWidgetItem(self.tr("Investment")))
        self.tblOperations.setHorizontalHeaderItem(1, QTableWidgetItem(self.tr("Current gains")))
        self.tblOperations.setHorizontalHeaderItem(2, QTableWidgetItem(self.tr("Historical gains")))
        self.tblOperations.setHorizontalHeaderItem(3, QTableWidgetItem(self.tr("Dividends")))
        self.tblOperations.setHorizontalHeaderItem(4, QTableWidgetItem(self.tr("Total")))

        set=self.mem.data.investments.setInvestments_merging_investments_with_same_product_merging_operations()
        self.tblOperations.applySettings()
        self.tblOperations.clearContents()
        self.tblOperations.setRowCount(set.length()+1)
        self.listOperations=[]
        sumcurrent=Money(self.mem, 0, self.mem.localcurrency)
        sumhistorical=Money(self.mem, 0, self.mem.localcurrency)
        sumdividends=Money(self.mem, 0, self.mem.localcurrency)
        for i, inv in enumerate(set.arr):
            gains_current=inv.op_actual.pendiente(inv.product.result.basic.last, type=3)
            gains_historical=inv.op_historica.consolidado_bruto(type=3)
            dividends=self.mem.data.investments.setDividends_merging_operation_dividends(inv.product)
            dividends_gross=dividends.gross(type=3)
            total=gains_current+gains_historical+dividends_gross
            sumcurrent=sumcurrent+gains_current
            sumhistorical=sumhistorical+gains_historical
            sumdividends=sumdividends+dividends_gross
            self.listOperations.append((inv, gains_current, gains_historical, dividends_gross, total))
            
        self.listOperations=sorted(self.listOperations, key=lambda c: c[4],  reverse=True)     
            
        for i, l in enumerate(self.listOperations):
            self.tblOperations.setItem(i, 0, QTableWidgetItem(l[0].product.name))
            self.tblOperations.setItem(i, 1, l[1].qtablewidgetitem())
            self.tblOperations.setItem(i, 2,  l[2].qtablewidgetitem())
            self.tblOperations.setItem(i, 3, l[3].qtablewidgetitem())
            self.tblOperations.setItem(i, 4, l[4].qtablewidgetitem())
        self.tblOperations.setItem(i+1, 0, QTableWidgetItem(self.tr("Total")))
        self.tblOperations.setItem(i+1, 1, sumcurrent.qtablewidgetitem())
        self.tblOperations.setItem(i+1, 2, sumhistorical.qtablewidgetitem())
        self.tblOperations.setItem(i+1, 3, sumdividends.qtablewidgetitem())
        self.tblOperations.setItem(i+1, 4, (sumcurrent+sumhistorical+sumdividends).qtablewidgetitem())

#####################################################################################################################33
          
        self.tblCurrentOperations.settings(self.mem,"wdgInvestmentsRanking" , "self.tblCurrentOperations")
        self.tblCurrentOperations.setColumnCount(5)
        self.tblCurrentOperations.setHorizontalHeaderItem(0, QTableWidgetItem(self.tr("Investment")))
        self.tblCurrentOperations.setHorizontalHeaderItem(1, QTableWidgetItem(self.tr("Current gains")))
        self.tblCurrentOperations.setHorizontalHeaderItem(2, QTableWidgetItem(self.tr("Historical gains")))
        self.tblCurrentOperations.setHorizontalHeaderItem(3, QTableWidgetItem(self.tr("Dividends")))
        self.tblCurrentOperations.setHorizontalHeaderItem(4, QTableWidgetItem(self.tr("Total")))

        self.tblCurrentOperations.applySettings()
        self.tblCurrentOperations.clearContents()
        self.tblCurrentOperations.setRowCount(set.length()+1)
        self.listCurrentOperations=[]
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
                    dividends=dividends+inv.setDividends_from_operations().gross(type=3)
            sumcurrent=sumcurrent+current
            sumhistorical=sumhistorical+historical
            sumdividends=sumdividends+dividends
            self.listCurrentOperations.append((product, current, historical, dividends, current+historical+dividends))
            
        self.listCurrentOperations=sorted(self.listCurrentOperations, key=lambda c: c[4],  reverse=True)     
            
        for i, l in enumerate(self.listCurrentOperations):
            self.tblCurrentOperations.setItem(i, 0, QTableWidgetItem(l[0].name))
            self.tblCurrentOperations.setItem(i, 1, l[1].qtablewidgetitem())
            self.tblCurrentOperations.setItem(i, 2,  l[2].qtablewidgetitem())
            self.tblCurrentOperations.setItem(i, 3, l[3].qtablewidgetitem())
            self.tblCurrentOperations.setItem(i, 4, l[4].qtablewidgetitem())
        self.tblCurrentOperations.setItem(i+1, 0, QTableWidgetItem(self.tr("Total")))
        self.tblCurrentOperations.setItem(i+1, 1, sumcurrent.qtablewidgetitem())
        self.tblCurrentOperations.setItem(i+1, 2, sumhistorical.qtablewidgetitem())
        self.tblCurrentOperations.setItem(i+1, 3, sumdividends.qtablewidgetitem())
        self.tblCurrentOperations.setItem(i+1, 4, (sumcurrent+sumhistorical+sumdividends).qtablewidgetitem())
        
    @pyqtSlot() 
    def on_actionSameProduct_triggered(self):
        inv=self.mem.data.investments.investment_merging_current_operations_with_same_product(self.selCurrentOperations)
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
            inv=self.mem.data.investments.investment_merging_current_operations_with_same_product(self.selCurrentOperations)
        else:
            product=self.selOperations.product
            inv=self.selOperations
        
        w=frmProductReport(self.mem, product, inv, self)
        w.exec_()
        
    def on_tblOperations_customContextMenuRequested(self,  pos):
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
        menu.exec_(self.tblOperations.mapToGlobal(pos))

    def on_tblOperations_itemSelectionChanged(self):
        self.selOperations=None
        try:
            for i in self.tblOperations.selectedItems():#itera por cada item no row.
                self.selOperations=self.listOperations[i.row()][0]
        except:
            pass
            
            
        
    def on_tblCurrentOperations_customContextMenuRequested(self,  pos):
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
        menu.exec_(self.tblCurrentOperations.mapToGlobal(pos))

    def on_tblCurrentOperations_itemSelectionChanged(self):
        self.selCurrentOperations=None
        try:
            for i in self.tblCurrentOperations.selectedItems():#itera por cada item no row.
                self.selCurrentOperations=self.listCurrentOperations[i.row()][0]
        except:
            pass
