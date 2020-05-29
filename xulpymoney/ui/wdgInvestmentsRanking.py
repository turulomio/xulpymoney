from PyQt5.QtWidgets import QWidget, QMenu
from PyQt5.QtCore import pyqtSlot, QObject
from xulpymoney.libmanagers import ObjectManager
from xulpymoney.libxulpymoneytypes import eMoneyCurrency
from xulpymoney.ui.Ui_wdgInvestmentsRanking import Ui_wdgInvestmentsRanking
from xulpymoney.ui.frmInvestmentReport import frmInvestmentReport
from xulpymoney.ui.frmProductReport import frmProductReport
from xulpymoney.objects.money import Money
    
class Ranking:
    def __init__(self, mem=None, product=None, current_gains=None, historical_gains=None, dividends=None):
        self.mem=mem
        self.product=product
        self.current_gains=current_gains
        self.historical_gains=historical_gains
        self.dividends=dividends
        
    def total(self):
        return self.current_gains+self.historical_gains+self.dividends

class RankingManager(ObjectManager, QObject):
    def __init__(self, mem):
        """Usa la variable mem.Agrupations"""
        ObjectManager.__init__(self)
        QObject.__init__(self)
        self.mem=mem

    def current_gains(self):
        r=Money(self.mem, 0, self.mem.localcurrency)
        for o in self:
            r=r+o.current_gains
        return r
    def historical_gains(self):
        r=Money(self.mem, 0, self.mem.localcurrency)
        for o in self:
            r=r+o.historical_gains
        return r
    def dividends(self):
        r=Money(self.mem, 0, self.mem.localcurrency)
        for o in self:
            r=r+o.dividends
        return r
    def total(self):
        r=Money(self.mem, 0, self.mem.localcurrency)
        for o in self:
            r=r+o.total()
        return r
        
    def sort_by_total(self):
        self.arr=sorted(self.arr, key=lambda c: c.total(),  reverse=True)     
        
    def myqtablewidget(self, wdg):
                
        hh=[self.tr("Investment"), self.tr("Current gains"),  self.tr("Historical gains"),  self.tr("Dividends"), self.tr("Total")]
        data=[]
        for o in self.arr:
            data.append((o.product, o.current_gains, o.historical_gains, o.dividends, o.total(), o))
            
        wdg.setDataWithObjects(hh, None, data, additional=self.myqtablewidget_additional)
        

    def myqtablewidget_additional(self, wdg):
        wdg.table.setRowCount(wdg.length()+1)
        wdg.addRow(wdg.length(), [self.tr("Total"), self.current_gains(), self.historical_gains(), self.dividends(), self.total()])

def RankingManager_from_current_operations(mem):
    r=RankingManager(mem)
    for product in mem.data.investments.ProductManager_with_investments_distinct_products().arr:
        current=Money(mem, 0, mem.localcurrency)
        historical=Money(mem, 0, mem.localcurrency)
        dividends=Money(mem, 0, mem.localcurrency)

        for inv in mem.data.investments.arr:
            if inv.product.id==product.id:
                current=current+inv.op_actual.pendiente(inv.product.result.basic.last, 3)
                historical=historical+inv.op_historica.consolidado_bruto(type=3)
                dividends=dividends+inv.dividends.gross(eMoneyCurrency.User, current=False)
        r.append(Ranking(mem, product, current, historical, dividends))
    r.sort_by_total()
    return r

def RankingManager_from_operations(mem):
    r=RankingManager(mem)
    for i, inv in enumerate(mem.data.investments.InvestmentManager_merging_investments_with_same_product_merging_operations()):
        inv.needStatus(3)
        gains_current=inv.op_actual.pendiente(inv.product.result.basic.last, type=3)
        gains_historical=inv.op_historica.consolidado_bruto(type=3)
        dividends_gross=inv.dividends.gross(eMoneyCurrency.User, current=False)
        r.append(Ranking(mem, inv.product, gains_current, gains_historical, dividends_gross))
    r.sort_by_total()
    return r

class wdgInvestmentsRanking(QWidget, Ui_wdgInvestmentsRanking):
    def __init__(self, mem,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        self.tab.setCurrentIndex(0)

        self.mqtwOperations.setSettings(self.mem.settings,"wdgInvestmentsRanking" , "mqtwOperations")
        self.mqtwOperations.table.customContextMenuRequested.connect(self.on_mqtwOperations_customContextMenuRequested)
        self.mqtwOperations.table.verticalHeader().show()
        self.ranking_operations=RankingManager_from_operations(self.mem)
        self.ranking_operations.myqtablewidget(self.mqtwOperations)
        self.mqtwOperations.drawOrderBy(4, True)

        self.mqtwCurrentOperations.setSettings(self.mem.settings,"wdgInvestmentsRanking" , "mqtwCurrentOperations")
        self.mqtwCurrentOperations.table.customContextMenuRequested.connect(self.on_mqtwCurrentOperations_customContextMenuRequested)        
        self.mqtwCurrentOperations.table.verticalHeader().show()
        self.ranking_currrent_operations=RankingManager_from_current_operations(self.mem)
        self.ranking_currrent_operations.myqtablewidget(self.mqtwCurrentOperations)
        self.mqtwCurrentOperations.drawOrderBy(4, True)

    @pyqtSlot() 
    def on_actionSameProduct_triggered(self):
        inv=self.mem.data.investments.Investment_merging_current_operations_with_same_product(self.mqtwCurrentOperations.selected.product)
        w=frmInvestmentReport(self.mem, inv, self)
        w.exec_()

    @pyqtSlot() 
    def on_actionSameProductFIFO_triggered(self):
        inv=self.mem.data.investments.Investment_merging_operations_with_same_product(self.mqtwOperations.selected.product)
        w=frmInvestmentReport(self.mem, inv, self)
        w.exec_()

    @pyqtSlot() 
    def on_actionProduct_triggered(self):
        if self.tab.currentIndex()==0:
            product=self.mqtwCurrentOperations.selected.product
            inv=self.mem.data.investments.Investment_merging_current_operations_with_same_product(self.mqtwCurrentOperations.selected.product)
        else:
            product=self.mqtwOperations.selected.product
            inv=self.mem.data.investments.Investment_merging_operations_with_same_product(self.mqtwOperations.selected.product)
        w=frmProductReport(self.mem, product, inv)
        w.exec_()

    def on_mqtwOperations_customContextMenuRequested(self,  pos):
        if self.mqtwOperations.selected is None:
            self.actionProduct.setEnabled(False)
            self.actionSameProductFIFO.setEnabled(False)
        else:
            self.actionProduct.setEnabled(True)
            self.actionSameProductFIFO.setEnabled(True)

        menu=QMenu()
        menu.addAction(self.actionProduct)
        menu.addSeparator()
        menu.addAction(self.actionSameProductFIFO)   
        menu.addSeparator()
        menu.addMenu(self.mqtwOperations.qmenu())
        menu.exec_(self.mqtwOperations.table.mapToGlobal(pos))
        
    def on_mqtwCurrentOperations_customContextMenuRequested(self,  pos):
        if self.mqtwCurrentOperations.selected==None:
            self.actionProduct.setEnabled(False)
            self.actionSameProduct.setEnabled(False)
        else:
            self.actionProduct.setEnabled(True)
            self.actionSameProduct.setEnabled(True)

        menu=QMenu()
        menu.addAction(self.actionProduct)
        menu.addSeparator()
        menu.addAction(self.actionSameProduct)
        menu.addSeparator()
        menu.addMenu(self.mqtwCurrentOperations.qmenu())
        menu.exec_(self.mqtwCurrentOperations.table.mapToGlobal(pos))
