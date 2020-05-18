from datetime import date
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMenu, QWidget, QHBoxLayout
from xulpymoney.objects.assets import Assets
from xulpymoney.objects.concept import ConceptManager_by_operationtype
from xulpymoney.objects.percentage import Percentage
from xulpymoney.ui.myqwidgets import qmessagebox
from xulpymoney.libxulpymoneytypes import eQColor
from xulpymoney.ui.Ui_wdgConcepts import Ui_wdgConcepts
from xulpymoney.ui.myqtablewidget import qcenter, qleft
from xulpymoney.ui.wdgConceptsHistorical import wdgConceptsHistorical
from xulpymoney.ui.myqcharts import VCPie

class wdgConcepts(QWidget, Ui_wdgConcepts):
    def __init__(self, mem,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        self.selected=None
        
        self.viewIncomes=VCPie()
        self.viewIncomes.setSettings(self.mem.settings, "wdgConcepts", "viewIncomes")
        self.layIncomes.addWidget(self.viewIncomes)
        self.viewExpenses=VCPie()
        self.viewExpenses.setSettings(self.mem.settings, "wdgConcepts", "viewExpenses")
        self.layExpenses.addWidget(self.viewExpenses)
        self.expenses=ConceptManager_by_operationtype(mem, 1)
        self.expenseslist=None
        self.incomes=ConceptManager_by_operationtype(mem, 2)
        self.incomeslist=None

        self.mqtwExpenses.setSettings(self.mem.settings, "wdgConcepts", "mqtwExpenses")
        self.mqtwExpenses.table.customContextMenuRequested.connect(self.on_mqtwExpenses_customContextMenuRequested)
        self.mqtwIncomes.setSettings(self.mem.settings, "wdgConcepts", "mqtwIncomes")
        self.mqtwIncomes.table.customContextMenuRequested.connect(self.on_mqtwIncomes_customContextMenuRequested)
        
        dtFirst=Assets(self.mem).first_datetime_allowed_estimated()       
        dtLast=Assets(self.mem).last_datetime_allowed_estimated()
        self.wdgYM.initiate(dtFirst.year,  dtLast.year, date.today().year, date.today().month)
        self.wdgYM.changed.connect(self.on_wdgYM_changed)
        
        
        self.on_wdgYM_changed()
        
        self.tab.setCurrentIndex(0)
        
    def load_gastos(self,  year,  month):
        self.viewExpenses.pie.clear()
        self.viewExpenses.pie.setTitle(self.tr("Concepts chart"))   
        
        self.mqtwExpenses.table.setColumnCount(4)
        self.mqtwExpenses.table.setHorizontalHeaderItem(0, qcenter(self.tr("Concept" )))
        self.mqtwExpenses.table.setHorizontalHeaderItem(1, qcenter(self.tr("Monthly expenses" )))
        self.mqtwExpenses.table.setHorizontalHeaderItem(2, qcenter(self.tr("% Monthly expenses" )))
        self.mqtwExpenses.table.setHorizontalHeaderItem(3, qcenter(self.tr("Monthly average" )))
        (self.expenseslist, totalexpenses,  totalaverageexpenses)=self.expenses.percentage_monthly(year, month)
        self.mqtwExpenses.applySettings()
        self.mqtwExpenses.table.clearContents()
        self.mqtwExpenses.table.setRowCount(len(self.expenseslist)+1)
        
        for i, a in enumerate(self.expenseslist):
            self.mqtwExpenses.table.setItem(i, 0, qleft(a[0].name))
            self.mqtwExpenses.table.setItem(i, 1, self.mem.localmoney(a[1]).qtablewidgetitem())
            self.mqtwExpenses.table.setItem(i, 2, Percentage(a[2], 100).qtablewidgetitem())#tpc
            self.mqtwExpenses.table.setItem(i, 3, self.mem.localmoney(a[3]).qtablewidgetitem())
            
            if a[1]!=0:
                if a[1]>a[3]:
                    self.mqtwExpenses.table.item(i, 1).setBackground( eQColor.Green)          
                else:
                    self.mqtwExpenses.table.item(i, 1).setBackground( eQColor.Red)      
                self.viewExpenses.pie.appendData(a[0].name.upper(), a[1])
        self.viewExpenses.display()
                
        self.mqtwExpenses.table.setItem(len(self.expenseslist), 0, qleft(self.tr('TOTAL')))
        self.mqtwExpenses.table.setItem(len(self.expenseslist), 1, self.mem.localmoney(totalexpenses).qtablewidgetitem())
        self.mqtwExpenses.table.setItem(len(self.expenseslist), 2, Percentage(1, 1).qtablewidgetitem())
        self.mqtwExpenses.table.setItem(len(self.expenseslist), 3, self.mem.localmoney(totalaverageexpenses).qtablewidgetitem())

    def load_ingresos(self,  year,  month):
        self.viewIncomes.pie.clear()
        self.viewIncomes.pie.setTitle(self.tr("Concepts chart"))   
        
        (self.incomeslist, totalincomes,  totalaverageincomes)=self.incomes.percentage_monthly(year, month)
        self.mqtwIncomes.table.setColumnCount(4)
        self.mqtwIncomes.table.setHorizontalHeaderItem(0, qcenter(self.tr("Concept" )))
        self.mqtwIncomes.table.setHorizontalHeaderItem(1, qcenter(self.tr("Monthly expenses" )))
        self.mqtwIncomes.table.setHorizontalHeaderItem(2, qcenter(self.tr("% Monthly expenses" )))
        self.mqtwIncomes.table.setHorizontalHeaderItem(3, qcenter(self.tr("Monthly average" )))
        self.mqtwIncomes.applySettings()
        self.mqtwIncomes.table.clearContents()
        self.mqtwIncomes.table.setRowCount(len(self.incomeslist)+1)
        
        for i, a in enumerate(self.incomeslist):
            self.mqtwIncomes.table.setItem(i, 0, qleft(a[0].name))
            self.mqtwIncomes.table.setItem(i, 1, self.mem.localmoney(a[1]).qtablewidgetitem())
            self.mqtwIncomes.table.setItem(i, 2, Percentage(a[2], 100).qtablewidgetitem())#tpc
            self.mqtwIncomes.table.setItem(i, 3, self.mem.localmoney(a[3]).qtablewidgetitem())
            
            if a[1]!=0:
                if a[1]>a[3]:
                    self.mqtwIncomes.table.item(i, 1).setBackground( eQColor.Green)          
                else:
                    self.mqtwIncomes.table.item(i, 1).setBackground( eQColor.Red)      
                self.viewIncomes.pie.appendData(a[0].name.upper(), a[1])
        self.viewIncomes.display()
        self.mqtwIncomes.table.setItem(len(self.incomeslist), 0, qleft(self.tr('TOTAL')))
        self.mqtwIncomes.table.setItem(len(self.incomeslist), 1, self.mem.localmoney(totalincomes).qtablewidgetitem())
        self.mqtwIncomes.table.setItem(len(self.incomeslist), 2, Percentage(1, 1).qtablewidgetitem())
        self.mqtwIncomes.table.setItem(len(self.incomeslist), 3, self.mem.localmoney(totalaverageincomes).qtablewidgetitem())

    @pyqtSlot() 
    def on_wdgYM_changed(self):
        self.load_gastos(self.wdgYM.year, self.wdgYM.month)
        self.load_ingresos(self.wdgYM.year,  self.wdgYM.month)
        
    def on_mqtwExpenses_customContextMenuRequested(self, pos):
        self.selected=None
        for i in self.mqtwExpenses.table.selectedItems():#itera por cada item no row.
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
        menu.exec_(self.mqtwExpenses.table.mapToGlobal(pos))
        
    def on_mqtwIncomes_customContextMenuRequested(self, pos):
        self.selected=None
        for i in self.mqtwIncomes.table.selectedItems():#itera por cada item no row.
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
        menu.exec_(self.mqtwIncomes.table.mapToGlobal(pos))
        
    
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

