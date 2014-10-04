from libxulpymoney import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Ui_wdgInvestmentsOperations import *
from frmInvestmentReport import *
from frmInvestmentOperationsAdd import *
from frmAccountsReport import *

class wdgInvestmentsOperations(QWidget, Ui_wdgInvestmentsOperations):
    def __init__(self, mem,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        fechainicio=Assets(self.mem).primera_datetime_con_datos_usuario()         

        self.mem.data.load_inactives()
        self.wym.initiate(fechainicio.year, datetime.date.today().year, datetime.date.today().year,  datetime.date.today().month)
        QObject.connect(self.wym, SIGNAL("changed"), self.on_wym_changed)
        self.setOperations=SetInvestmentOperations(self.mem)
        self.setCurrent=SetInvestmentOperationsCurrent(self.mem)
        self.selOperation=None#For table
        self.selCurrentOperation=None#For tblCurrent
        self.table.settings("wdgInvestmentsOperations",  self.mem)
        self.tblCurrent.settings("wdgInvestmentsOperations",  self.mem)
        self.tab.setCurrentIndex(0)
        self.load()
        self.load_current()
        
    def load(self):
        del self.setOperations.arr
        self.setOperations.arr=[]
        cur=self.mem.con.cursor()
        if self.radYear.isChecked()==True:
            cur.execute("select * from operinversiones where date_part('year',datetime)=%s order by datetime",(self.wym.year, ) )
        else:
            cur.execute("select * from operinversiones where date_part('year',datetime)=%s and date_part('month',datetime)=%s order by datetime",(self.wym.year, self.wym.month) )
        for row in cur:
            self.setOperations.append(InvestmentOperation(self.mem).init__db_row(row, self.mem.data.investments_all().find(row['id_inversiones']), self.mem.tiposoperaciones.find(row['id_tiposoperaciones'])))
        cur.close()
        
        self.setOperations.myqtablewidget(self.table, "wdgInvestmentsOperations")
        
    def load_current(self):
        for inv in self.mem.data.investments_active.arr:
            for o in inv.op_actual.arr:
                self.setCurrent.append(o)
        self.setCurrent.sort()
        self.setCurrent.myqtablewidget(self.tblCurrent, "wdgInvestmentsOperations")

        
        
        
    def on_radYear_toggled(self, toggle):
        self.load()
        
    def on_wym_changed(self):
        self.load()    

    def on_table_itemSelectionChanged(self):
        self.selOperation=None
        for i in self.table.selectedItems():#itera por cada item no row.
            self.selOperation=self.setOperations.arr[i.row()]
            
    def on_tblCurrent_itemSelectionChanged(self):
        self.selCurrentOperation=None
        for i in self.tblCurrent.selectedItems():#itera por cada item no row.
            self.selCurrentOperation=self.setCurrent.arr[i.row()]
    
    @QtCore.pyqtSlot() 
    def on_actionShowAccount_activated(self):
        if self.tab.currentIndex()==0:#Operation list
            cuenta=self.selOperation.inversion.cuenta
        else:#Current operation list
            cuenta=self.selCurrentOperation.inversion.cuenta
        w=frmAccountsReport(self.mem, cuenta, self)
        w.exec_()
        self.load()
        
    @QtCore.pyqtSlot() 
    def on_actionShowInvestment_activated(self):
        if self.tab.currentIndex()==0:#Operation list
            investment=self.selOperation.inversion
        else:#Current operation list
            investment=self.selCurrentOperation.inversion
        w=frmInvestmentReport(self.mem, investment, self)
        w.exec_()
        self.load()
                
    @QtCore.pyqtSlot() 
    def on_actionShowProduct_activated(self):
        if self.tab.currentIndex()==0:#Operation list
            investment=self.selOperation.inversion
        else:#Current operation list
            investment=self.selCurrentOperation.inversion
        w=frmProductReport(self.mem, investment.product, investment, self)
        w.exec_()
        self.load()

    @QtCore.pyqtSlot() 
    def on_actionShowInvestmentOperation_activated(self):
        if self.tab.currentIndex()==0:#Operation list
            operation=self.selOperation
        else:#Current operation list
            operation=self.selCurrentOperation
        w=frmInvestmentOperationsAdd(self.mem, operation.inversion, operation, self)
        w.exec_()
        self.load()

    def on_table_customContextMenuRequested(self,  pos):
        self.actionShowAccount.setEnabled(False)
        self.actionShowInvestment.setEnabled(False)
        self.actionShowInvestmentOperation.setEnabled(False)
        self.actionShowProduct.setEnabled(False)
        if self.selOperation!=None:
            if self.selOperation.inversion.cuenta.activa==True:#only enabled if it's active
                self.actionShowAccount.setEnabled(True)
            if self.selOperation.inversion.activa==True:
                self.actionShowInvestment.setEnabled(True)
                self.actionShowInvestmentOperation.setEnabled(True)
            self.actionShowProduct.setEnabled(True)

        menu=QMenu()
        menu.addAction(self.actionShowAccount)   
        menu.addSeparator()   
        menu.addAction(self.actionShowInvestment)   
        menu.addSeparator()   
        menu.addAction(self.actionShowInvestmentOperation)      
        menu.addSeparator()
        menu.addAction(self.actionShowProduct)
        menu.exec_(self.table.mapToGlobal(pos))
                
    def on_tblCurrent_customContextMenuRequested(self,  pos):
        if self.selCurrentOperation==None:
            self.actionShowAccount.setEnabled(False)
            self.actionShowInvestment.setEnabled(False)
            self.actionShowInvestmentOperation.setEnabled(False)
            self.actionShowProduct.setEnabled(False)
        else:
            self.actionShowAccount.setEnabled(True)
            self.actionShowInvestment.setEnabled(True)
            self.actionShowInvestmentOperation.setEnabled(True)
            self.actionShowProduct.setEnabled(True)

        menu=QMenu()
        menu.addAction(self.actionShowAccount)   
        menu.addSeparator()   
        menu.addAction(self.actionShowInvestment)   
        menu.addSeparator()   
        menu.addAction(self.actionShowInvestmentOperation)      
        menu.addSeparator()
        menu.addAction(self.actionShowProduct)
        menu.exec_(self.tblCurrent.mapToGlobal(pos))
        
        
