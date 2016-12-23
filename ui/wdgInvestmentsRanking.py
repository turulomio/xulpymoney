from PyQt5.QtWidgets import QWidget,  QTableWidgetItem
from Ui_wdgInvestmentsRanking import Ui_wdgInvestmentsRanking
from libxulpymoney import Money

class wdgInvestmentsRanking(QWidget, Ui_wdgInvestmentsRanking):
    def __init__(self, mem,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
            
        self.tblOperations.settings(self.mem,"wdgInvestmentsRanking" , "self.tblOperations")
        self.tblOperations.setColumnCount(6)
        self.tblOperations.setHorizontalHeaderItem(0, QTableWidgetItem(self.tr("Investment")))
        self.tblOperations.setHorizontalHeaderItem(1, QTableWidgetItem(self.tr("Current gains")))
        self.tblOperations.setHorizontalHeaderItem(2, QTableWidgetItem(self.tr("Historical gains")))
        self.tblOperations.setHorizontalHeaderItem(3, QTableWidgetItem(self.tr("Gains")))
        self.tblOperations.setHorizontalHeaderItem(4, QTableWidgetItem(self.tr("Dividends")))
        self.tblOperations.setHorizontalHeaderItem(5, QTableWidgetItem(self.tr("Total")))

        set=self.mem.data.investments.setInvestments_merging_investments_with_same_product_merging_operations()
        self.tblOperations.applySettings()
        self.tblOperations.clearContents()
        self.tblOperations.setRowCount(set.length()+1)
        list=[]
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
            list.append((inv.product, gains_current, gains_historical, dividends_gross, total))
            
        list=sorted(list, key=lambda c: c[4],  reverse=True)     
            
        for i, l in enumerate(list):
            self.tblOperations.setItem(i, 0, QTableWidgetItem(l[0].name))
            self.tblOperations.setItem(i, 1, l[1].qtablewidgetitem())
            self.tblOperations.setItem(i, 2,  l[2].qtablewidgetitem())
            self.tblOperations.setItem(i, 3,  (l[1]+l[2]).qtablewidgetitem())
            self.tblOperations.setItem(i, 4, l[3].qtablewidgetitem())
            self.tblOperations.setItem(i, 5, l[4].qtablewidgetitem())
        self.tblOperations.setItem(i+1, 0, QTableWidgetItem(self.tr("Total")))
        self.tblOperations.setItem(i+1, 1, sumcurrent.qtablewidgetitem())
        self.tblOperations.setItem(i+1, 2, sumhistorical.qtablewidgetitem())
        self.tblOperations.setItem(i+1, 3, (sumcurrent+sumhistorical).qtablewidgetitem())
        self.tblOperations.setItem(i+1, 4, sumdividends.qtablewidgetitem())
        self.tblOperations.setItem(i+1, 5, (sumcurrent+sumhistorical+sumdividends).qtablewidgetitem())

#####################################################################################################################33
          
        self.tblCurrentOperations.settings(self.mem,"wdgInvestmentsRanking" , "self.tblCurrentOperations")
        self.tblCurrentOperations.setColumnCount(6)
        self.tblCurrentOperations.setHorizontalHeaderItem(0, QTableWidgetItem(self.tr("Investment")))
        self.tblCurrentOperations.setHorizontalHeaderItem(1, QTableWidgetItem(self.tr("Current gains")))
        self.tblCurrentOperations.setHorizontalHeaderItem(2, QTableWidgetItem(self.tr("Historical gains")))
        self.tblCurrentOperations.setHorizontalHeaderItem(3, QTableWidgetItem(self.tr("Gains")))
        self.tblCurrentOperations.setHorizontalHeaderItem(4, QTableWidgetItem(self.tr("Dividends")))
        self.tblCurrentOperations.setHorizontalHeaderItem(5, QTableWidgetItem(self.tr("Total")))

        self.tblCurrentOperations.applySettings()
        self.tblCurrentOperations.clearContents()
        self.tblCurrentOperations.setRowCount(set.length()+1)
        list=[]
        sumcurrent=Money(self.mem, 0, self.mem.localcurrency)
        sumhistorical=Money(self.mem, 0, self.mem.localcurrency)
        sumdividends=Money(self.mem, 0, self.mem.localcurrency)
        for product in self.mem.data.investments.products_distinct().arr:
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
            list.append((product, current, historical, dividends, current+historical+dividends))
            
        list=sorted(list, key=lambda c: c[4],  reverse=True)     
            
        for i, l in enumerate(list):
            self.tblCurrentOperations.setItem(i, 0, QTableWidgetItem(l[0].name))
            self.tblCurrentOperations.setItem(i, 1, l[1].qtablewidgetitem())
            self.tblCurrentOperations.setItem(i, 2,  l[2].qtablewidgetitem())
            self.tblCurrentOperations.setItem(i, 3,  (l[1]+l[2]).qtablewidgetitem())
            self.tblCurrentOperations.setItem(i, 4, l[3].qtablewidgetitem())
            self.tblCurrentOperations.setItem(i, 5, l[4].qtablewidgetitem())
        self.tblCurrentOperations.setItem(i+1, 0, QTableWidgetItem(self.tr("Total")))
        self.tblCurrentOperations.setItem(i+1, 1, sumcurrent.qtablewidgetitem())
        self.tblCurrentOperations.setItem(i+1, 2, sumhistorical.qtablewidgetitem())
        self.tblCurrentOperations.setItem(i+1, 3, (sumcurrent+sumhistorical).qtablewidgetitem())
        self.tblCurrentOperations.setItem(i+1, 4, sumdividends.qtablewidgetitem())
        self.tblCurrentOperations.setItem(i+1, 5, (sumcurrent+sumhistorical+sumdividends).qtablewidgetitem())

