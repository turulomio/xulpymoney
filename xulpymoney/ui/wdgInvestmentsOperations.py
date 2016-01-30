from libxulpymoney import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from Ui_wdgInvestmentsOperations import *
from frmInvestmentReport import *
from frmInvestmentOperationsAdd import *
from frmAccountsReport import *

class wdgInvestmentsOperations(QWidget, Ui_wdgInvestmentsOperations):
    def __init__(self, mem,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        fechainicio=Assets(self.mem).first_datetime_with_user_data()         

         
        self.wy.initiate(fechainicio.year, datetime.date.today().year, datetime.date.today().year)
        self.wy.changed.connect(self.on_wy_mychanged)
        self.wy.label.hide()
        self.wy.hide()
        self.wym.initiate(fechainicio.year, datetime.date.today().year, datetime.date.today().year,  datetime.date.today().month)
        self.wym.changed.connect(self.on_wym_mychanged)
        self.wym.label.hide()
        self.setOperations=SetInvestmentOperations(self.mem)
        self.setCurrent=SetInvestmentOperationsCurrent(self.mem)
        self.selOperation=None#For table
        self.selCurrentOperation=None#For tblCurrent
        self.table.settings(self.mem,  "wdgInvestmentsOperations")
        self.tblCurrent.settings(self.mem, "wdgInvestmentsOperations")
        self.tab.setCurrentIndex(0)
        self.load()
        self.load_current()
        
    def load(self):
        del self.setOperations.arr
        self.setOperations.arr=[]
        cur=self.mem.con.cursor()
        filters=""
        if self.cmbFilters.currentIndex()==0:#All
            filters=""
        elif self.cmbFilters.currentIndex()==1:#Purchasing
            filters=" and id_tiposoperaciones in (4)"
        elif self.cmbFilters.currentIndex()==2:#Purchasing
            filters=" and id_tiposoperaciones in (5)"
        elif self.cmbFilters.currentIndex()==3:#Purchasing
            filters=" and id_tiposoperaciones not in (4, 5)"
        
        
        if self.radYear.isChecked()==True:
            cur.execute("select * from operinversiones where date_part('year',datetime)=%s "+filters+" order by datetime",(self.wy.year,  ) )
        else:
            cur.execute("select * from operinversiones where date_part('year',datetime)=%s and date_part('month',datetime)=%s "+filters+" order by datetime",(self.wym.year, self.wym.month) )
        for row in cur:
            self.setOperations.append(InvestmentOperation(self.mem).init__db_row(row, self.mem.data.investments_all().find_by_id(row['id_inversiones']), self.mem.tiposoperaciones.find_by_id(row['id_tiposoperaciones'])))
        cur.close()
        
        self.setOperations.myqtablewidget(self.table)
        
    def load_current(self):
        for inv in self.mem.data.investments_active.arr:
            for o in inv.op_actual.arr:
                self.setCurrent.append(o)
        self.setCurrent.order_by_datetime()
        self.setCurrent.myqtablewidget_heterogeneus(self.tblCurrent, True)

        
    @QtCore.pyqtSlot(int) 
    def on_cmbFilters_currentIndexChanged(self, index):
        self.load()
        
    def on_radYear_toggled(self, toggle):
        if toggle==True:
            self.wym.hide()
            self.wy.show()
        else:
            self.wym.show()
            self.wy.hide()
        self.load()
        
    def on_wym_mychanged(self):
        self.load()            
    def on_wy_mychanged(self):
        self.load()    

    def on_table_itemSelectionChanged(self):
        self.selOperation=None
        for i in self.table.selectedItems():#itera por cada item no row.
            self.selOperation=self.setOperations.arr[i.row()]
            
    def on_tblCurrent_itemSelectionChanged(self):
        try: #Due it has one more row and crashes
            for i in self.tblCurrent.selectedItems():#itera por cada item no row.
                self.selCurrentOperation=self.setCurrent.arr[i.row()]
        except:
            self.selCurrentOperation=None
            
    
    @QtCore.pyqtSlot() 
    def on_actionShowAccount_triggered(self):
        if self.tab.currentIndex()==0:#Operation list
            cuenta=self.selOperation.inversion.account
        else:#Current operation list
            cuenta=self.selCurrentOperation.inversion.account
        w=frmAccountsReport(self.mem, cuenta, self)
        w.exec_()
        self.load()
        
    @QtCore.pyqtSlot() 
    def on_actionShowInvestment_triggered(self):
        if self.tab.currentIndex()==0:#Operation list
            investment=self.selOperation.inversion
        else:#Current operation list
            investment=self.selCurrentOperation.inversion
        w=frmInvestmentReport(self.mem, investment, self)
        w.exec_()
        self.load()
                
    @QtCore.pyqtSlot() 
    def on_actionShowProduct_triggered(self):
        if self.tab.currentIndex()==0:#Operation list
            investment=self.selOperation.inversion
        else:#Current operation list
            investment=self.selCurrentOperation.inversion
        w=frmProductReport(self.mem, investment.product, investment, self)
        w.exec_()
        self.load()
                
    @QtCore.pyqtSlot() 
    def on_actionRangeReport_triggered(self):
        self.selOperation.show_in_ranges= not self.selOperation.show_in_ranges
        self.selOperation.save()
        self.mem.con.commit()
        #self.selOperation doesn't belong to self.mem.data, it's a set of this widget, so I need to reload investment of the self.mem.data
        self.mem.data.investments_all().find_by_id(self.selOperation.inversion.id).get_operinversiones()
        self.load()
        
    @QtCore.pyqtSlot() 
    def on_actionShowInvestmentOperation_triggered(self):
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
            if self.selOperation.inversion.account.active==True:#only enabled if it's active
                self.actionShowAccount.setEnabled(True)
            if self.selOperation.inversion.active==True:
                self.actionShowInvestment.setEnabled(True)
                self.actionShowInvestmentOperation.setEnabled(True)
            self.actionShowProduct.setEnabled(True)
            if self.selOperation.show_in_ranges==True:
                self.actionRangeReport.setText(self.tr("Hide in range report"))
                self.actionRangeReport.setIcon(QIcon(":/xulpymoney/eye_red.png"))
            else:
                self.actionRangeReport.setText(self.tr("Show in range report"))
                self.actionRangeReport.setIcon(QIcon(":/xulpymoney/eye.png"))

        menu=QMenu()
        menu.addAction(self.actionShowAccount)   
        menu.addSeparator()   
        menu.addAction(self.actionShowInvestment)   
        menu.addSeparator()   
        menu.addAction(self.actionShowInvestmentOperation)      
        menu.addSeparator()
        menu.addAction(self.actionShowProduct)
        menu.addSeparator()
        menu.addAction(self.actionRangeReport)
        menu.exec_(self.table.mapToGlobal(pos))
                
    def on_tblCurrent_customContextMenuRequested(self,  pos):
        if self.selCurrentOperation==None:
            self.actionShowAccount.setEnabled(False)
            self.actionShowInvestment.setEnabled(False)
            self.actionShowProduct.setEnabled(False)
        else:
            self.actionShowAccount.setEnabled(True)
            self.actionShowInvestment.setEnabled(True)
            self.actionShowProduct.setEnabled(True)

        menu=QMenu()
        menu.addAction(self.actionShowAccount)   
        menu.addSeparator()   
        menu.addAction(self.actionShowInvestment)   
        menu.addSeparator()
        menu.addAction(self.actionShowProduct)
        menu.exec_(self.tblCurrent.mapToGlobal(pos))
        
        
