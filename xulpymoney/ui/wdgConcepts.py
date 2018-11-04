import datetime
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMenu, QWidget, QTableWidgetItem, QHBoxLayout
from xulpymoney.libxulpymoney import Assets,  Percentage
from xulpymoney.libxulpymoneyfunctions import qmessagebox
from xulpymoney.libxulpymoneytypes import eQColor
from xulpymoney.ui.Ui_wdgConcepts import Ui_wdgConcepts
from xulpymoney.ui.wdgConceptsHistorical import wdgConceptsHistorical
from xulpymoney.ui.canvaschart import VCPie

class wdgConcepts(QWidget, Ui_wdgConcepts):
    def __init__(self, mem,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        self.selected=None
        
        self.viewIncomes=VCPie()
        self.layIncomes.addWidget(self.viewIncomes)
        self.viewExpenses=VCPie()
        self.layExpenses.addWidget(self.viewExpenses)
        self.expenses=self.mem.conceptos.clone_x_tipooperacion(1)
        self.expenseslist=None
        self.incomes=self.mem.conceptos.clone_x_tipooperacion(2)
        self.incomeslist=None

        self.tblExpenses.settings(self.mem, "wdgConcepts")
        self.tblIncomes.settings(self.mem, "wdgConcepts")
        
        anoinicio=Assets(self.mem).first_datetime_with_user_data().year       
        self.wdgYM.initiate(anoinicio,  datetime.date.today().year, datetime.date.today().year, datetime.date.today().month)
        self.wdgYM.changed.connect(self.on_wdgYM_changed)
        
        
        self.on_wdgYM_changed()
        
        self.tab.setCurrentIndex(0)
        
    def load_gastos(self,  year,  month):
        self.viewExpenses.clear()
        self.viewExpenses.chart.setTitle(self.tr("Concepts chart"))   
        self.viewExpenses.setCurrency(self.mem.localcurrency)
        
        (self.expenseslist, totalexpenses,  totalaverageexpenses)=self.expenses.percentage_monthly(year, month)
        self.tblExpenses.applySettings()
        self.tblExpenses.clearContents()
        self.tblExpenses.setRowCount(len(self.expenseslist)+1)
        
        for i, a in enumerate(self.expenseslist):
            self.tblExpenses.setItem(i, 0, QTableWidgetItem(a[0].name))
            self.tblExpenses.setItem(i, 1, self.mem.localcurrency.qtablewidgetitem(a[1]))
            self.tblExpenses.setItem(i, 2, Percentage(a[2], 100).qtablewidgetitem())#tpc
            self.tblExpenses.setItem(i, 3, self.mem.localcurrency.qtablewidgetitem(a[3]))
            
            if a[1]!=0:
                if a[1]>a[3]:
                    self.tblExpenses.item(i, 1).setBackground( eQColor.Green)          
                else:
                    self.tblExpenses.item(i, 1).setBackground( eQColor.Red)      
                self.viewExpenses.appendData(a[0].name.upper(), a[1])
        self.viewExpenses.display()
                
        self.tblExpenses.setItem(len(self.expenseslist), 0, QTableWidgetItem(self.tr('TOTAL')))
        self.tblExpenses.setItem(len(self.expenseslist), 1, self.mem.localcurrency.qtablewidgetitem(totalexpenses))    
        self.tblExpenses.setItem(len(self.expenseslist), 2, Percentage(1, 1).qtablewidgetitem())
        self.tblExpenses.setItem(len(self.expenseslist), 3, self.mem.localcurrency.qtablewidgetitem(totalaverageexpenses))       

    def load_ingresos(self,  year,  month):
        self.viewIncomes.clear()
        self.viewIncomes.chart.setTitle(self.tr("Concepts chart"))   
        self.viewIncomes.setCurrency(self.mem.localcurrency)
        (self.incomeslist, totalincomes,  totalaverageincomes)=self.incomes.percentage_monthly(year, month)
        self.tblIncomes.applySettings()
        self.tblIncomes.clearContents()
        self.tblIncomes.setRowCount(len(self.incomeslist)+1)
        
        for i, a in enumerate(self.incomeslist):
            self.tblIncomes.setItem(i, 0, QTableWidgetItem(a[0].name))
            self.tblIncomes.setItem(i, 1, self.mem.localcurrency.qtablewidgetitem(a[1]))
            self.tblIncomes.setItem(i, 2, Percentage(a[2], 100).qtablewidgetitem())#tpc
            self.tblIncomes.setItem(i, 3, self.mem.localcurrency.qtablewidgetitem(a[3]))
            
            if a[1]!=0:
                if a[1]>a[3]:
                    self.tblIncomes.item(i, 1).setBackground( eQColor.Green)          
                else:
                    self.tblIncomes.item(i, 1).setBackground( eQColor.Red)      
                self.viewIncomes.appendData(a[0].name.upper(), a[1])
        self.viewIncomes.display()
        self.tblIncomes.setItem(len(self.incomeslist), 0, QTableWidgetItem(self.tr('TOTAL')))
        self.tblIncomes.setItem(len(self.incomeslist), 1, self.mem.localcurrency.qtablewidgetitem(totalincomes))    
        self.tblIncomes.setItem(len(self.incomeslist), 2, Percentage(1, 1).qtablewidgetitem())
        self.tblIncomes.setItem(len(self.incomeslist), 3, self.mem.localcurrency.qtablewidgetitem(totalaverageincomes))         

    @pyqtSlot() 
    def on_wdgYM_changed(self):
        self.load_gastos(self.wdgYM.year, self.wdgYM.month)
        self.load_ingresos(self.wdgYM.year,  self.wdgYM.month)
        
    def on_tblExpenses_customContextMenuRequested(self, pos):
        self.selected=None
        for i in self.tblExpenses.selectedItems():#itera por cada item no row.
            if i.row()==len(self.expenseslist):#Si pulsa en total
                self.selected=None
                break
            if i.column()==0:
                self.selected=self.expenseslist[i.row()]

        
        if self.selected!=None:
            self.actionHistoricalReport.setEnabled(True)
        else:
            self.actionHistoricalReport.setEnabled(False)

        menu=QMenu()
        menu.addAction(self.actionHistoricalReport)   
        menu.exec_(self.tblExpenses.mapToGlobal(pos))
        
    def on_tblIncomes_customContextMenuRequested(self, pos):
        self.selected=None
        for i in self.tblIncomes.selectedItems():#itera por cada item no row.
            if i.row()==len(self.incomeslist):#Si pulsa en total
                self.selected=None
                break
            if i.column()==0:
                self.selected=self.incomeslist[i.row()]

        if self.selected!=None:
            self.actionHistoricalReport.setEnabled(True)
        else:
            self.actionHistoricalReport.setEnabled(False)
        
        menu=QMenu()
        menu.addAction(self.actionHistoricalReport)   
        menu.exec_(self.tblIncomes.mapToGlobal(pos))
        
    
    def on_tab_tabCloseRequested(self, index):
        """Only removes dinamic tabs"""
        if index in (0, 1):
            qmessagebox(self.tr("You can't close this tab"))
        else:
            self.tab.removeTab(index)
        
    @pyqtSlot()
    def on_actionHistoricalReport_triggered(self):
        newtab = QWidget()
        horizontalLayout = QHBoxLayout(newtab)
        concepto=self.selected[0]
        wch = wdgConceptsHistorical(self.mem, concepto, newtab)
        horizontalLayout.addWidget(wch)
        self.tab.addTab(newtab, "{0}".format(concepto.name))
        self.tab.setCurrentWidget(newtab)

