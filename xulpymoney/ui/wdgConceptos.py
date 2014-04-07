from PyQt4.QtCore import *
from PyQt4.QtGui import *
from libxulpymoney import *
from Ui_wdgConceptos import *
from frmConceptsHistorical import *

class wdgConceptos(QWidget, Ui_wdgConceptos):
    def __init__(self, cfg,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.cfg=cfg
        self.selected=None
        
        self.expenses=self.cfg.conceptos.clone_x_tipooperacion(1)
        self.expenseslist=None
        self.incomes=self.cfg.conceptos.clone_x_tipooperacion(2)
        self.incomeslist=None

        self.tblExpenses.settings(None,  self.cfg)
        self.tblIncomes.settings(None,  self.cfg)
        
        anoinicio=Patrimonio(self.cfg).primera_fecha_con_datos_usuario().year       
        self.wdgYM.initiate(anoinicio,  datetime.date.today().year, datetime.date.today().year, datetime.date.today().month)
        QObject.connect(self.wdgYM, SIGNAL("changed"), self.on_wdgYM_changed)
        
        self.on_wdgYM_changed()
        
    def load_gastos(self,  year,  month):
        
        (self.expenseslist, totalexpenses,  totalaverageexpenses)=self.expenses.percentage_monthly(year, month)
        self.tblExpenses.clearContents()
        self.tblExpenses.setRowCount(len(self.expenseslist)+1)
        
        for i, a in enumerate(self.expenseslist):
            self.tblExpenses.setItem(i, 0, QTableWidgetItem(a[0].name))
            self.tblExpenses.setItem(i, 1, self.cfg.localcurrency.qtablewidgetitem(a[1]))
            self.tblExpenses.setItem(i, 2, qtpc(a[2]))
            self.tblExpenses.setItem(i, 3, self.cfg.localcurrency.qtablewidgetitem(a[3]))
            
            if a[1]!=0:
                if a[1]>a[3]:
                    self.tblExpenses.item(i, 1).setBackgroundColor( QColor(182, 255, 182))          
                else:
                    self.tblExpenses.item(i, 1).setBackgroundColor( QColor(255, 182, 182))      
                
        self.tblExpenses.setItem(len(self.expenseslist), 0, QTableWidgetItem(self.tr('TOTAL')))
        self.tblExpenses.setItem(len(self.expenseslist), 1, self.cfg.localcurrency.qtablewidgetitem(totalexpenses))    
        self.tblExpenses.setItem(len(self.expenseslist), 2, qtpc(100))    
        self.tblExpenses.setItem(len(self.expenseslist), 3, self.cfg.localcurrency.qtablewidgetitem(totalaverageexpenses))       

    def load_ingresos(self,  year,  month):
        (self.incomeslist, totalincomes,  totalaverageincomes)=self.incomes.percentage_monthly(year, month)
        self.tblIncomes.clearContents()
        self.tblIncomes.setRowCount(len(self.incomeslist)+1)
        
        for i, a in enumerate(self.incomeslist):
            self.tblIncomes.setItem(i, 0, QTableWidgetItem(a[0].name))
            self.tblIncomes.setItem(i, 1, self.cfg.localcurrency.qtablewidgetitem(a[1]))
            self.tblIncomes.setItem(i, 2, qtpc(a[2]))
            self.tblIncomes.setItem(i, 3, self.cfg.localcurrency.qtablewidgetitem(a[3]))
            
            if a[1]!=0:
                if a[1]>a[3]:
                    self.tblIncomes.item(i, 1).setBackgroundColor( QColor(182, 255, 182))          
                else:
                    self.tblIncomes.item(i, 1).setBackgroundColor( QColor(255, 182, 182))      
                
        self.tblIncomes.setItem(len(self.incomeslist), 0, QTableWidgetItem(self.tr('TOTAL')))
        self.tblIncomes.setItem(len(self.incomeslist), 1, self.cfg.localcurrency.qtablewidgetitem(totalincomes))    
        self.tblIncomes.setItem(len(self.incomeslist), 2, qtpc(100))    
        self.tblIncomes.setItem(len(self.incomeslist), 3, self.cfg.localcurrency.qtablewidgetitem(totalaverageincomes))         

    @QtCore.pyqtSlot() 
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
        
        
    @pyqtSignature("")
    def on_actionHistoricalReport_activated(self):
        d=frmConceptsHistorical(self.cfg, self.selected[0], self)
        d.exec_()
