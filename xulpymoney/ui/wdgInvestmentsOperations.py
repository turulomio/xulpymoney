from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMenu, QWidget
from datetime import date
from xulpymoney.objects.investmentoperation import InvestmentOperationHeterogeneusManager_from_sql, InvestmentOperationCurrentHeterogeneusManager
from xulpymoney.objects.assets import Assets
from xulpymoney.ui.Ui_wdgInvestmentsOperations import Ui_wdgInvestmentsOperations
from xulpymoney.ui.frmInvestmentReport import frmInvestmentReport
from xulpymoney.ui.frmInvestmentOperationsAdd import frmInvestmentOperationsAdd
from xulpymoney.ui.frmAccountsReport import frmAccountsReport
from xulpymoney.ui.frmProductReport import frmProductReport

class wdgInvestmentsOperations(QWidget, Ui_wdgInvestmentsOperations):
    def __init__(self, mem,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        dtFirst=Assets(self.mem).first_datetime_allowed_estimated()
        dtLast=Assets(self.mem).last_datetime_allowed_estimated()       

        self.wy.initiate(dtFirst.year,  dtLast.year, date.today().year)
        self.wy.changed.connect(self.on_wy_mychanged)
        self.wy.label.hide()
        self.wy.hide()
        
        self.wym.initiate(dtFirst.year,  dtLast.year, date.today().year, date.today().month)
        self.wym.changed.connect(self.on_wym_mychanged)
        self.wym.label.hide()
        
        self.mqtw.setSettings(self.mem.settings,  "wdgInvestmentsOperations", "mqtw")
        self.mqtw.table.customContextMenuRequested.connect(self.on_mqtw_customContextMenuRequested)
        self.mqtwCurrent.setSettings(self.mem.settings, "wdgInvestmentsOperations", "mqtwCurrent")
        self.mqtwCurrent.table.customContextMenuRequested.connect(self.on_mqtwCurrent_customContextMenuRequested)
        self.tab.setCurrentIndex(0)
        self.load()
        self.load_current()
        
    def load(self):
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
            self.operations=InvestmentOperationHeterogeneusManager_from_sql(self.mem,"select * from operinversiones where date_part('year',datetime)=%s "+filters+" order by datetime",(self.wy.year,  ) )
        else:
            self.operations=InvestmentOperationHeterogeneusManager_from_sql(self.mem,"select * from operinversiones where date_part('year',datetime)=%s and date_part('month',datetime)=%s "+filters+" order by datetime",(self.wym.year, self.wym.month) )
        self.operations.myqtablewidget(self.mqtw)
        self.mqtw.drawOrderBy(0, False)

    def load_current(self):
        self.setCurrent=InvestmentOperationCurrentHeterogeneusManager(self.mem)
        for inv in self.mem.data.investments_active():
            for o in inv.op_actual.arr:
                self.setCurrent.append(o)
        self.setCurrent.myqtablewidget(self.mqtwCurrent)
        self.mqtwCurrent.setOrderBy(0, False)

    @pyqtSlot(int) 
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
    
    @pyqtSlot() 
    def on_actionShowAccount_triggered(self):
        if self.tab.currentIndex()==0:#Operation list
            cuenta=self.mqtw.selected.investment.account
        else:#Current operation list
            cuenta=self.mqtwCurrent.selected.investment.account
        w=frmAccountsReport(self.mem, cuenta, self)
        w.exec_()
        self.load()
        
    @pyqtSlot() 
    def on_actionShowInvestment_triggered(self):
        if self.tab.currentIndex()==0:#Operation list
            investment=self.mqtw.selected.investment
        else:#Current operation list
            investment=self.mqtwCurrent.selected.investment
        w=frmInvestmentReport(self.mem, investment, self)
        w.exec_()
        self.load()
                
    @pyqtSlot() 
    def on_actionShowProduct_triggered(self):
        if self.tab.currentIndex()==0:#Operation list
            investment=self.mqtw.selected.investment
        else:#Current operation list
            investment=self.mqtwCurrent.selected.investment
        w=frmProductReport(self.mem, investment.product, investment, self)
        w.exec_()
        self.load()
                
    @pyqtSlot() 
    def on_actionRangeReport_triggered(self):
        self.mqtw.selected.show_in_ranges= not self.mqtw.selected.show_in_ranges
        self.mqtw.selected.save()
        self.mem.con.commit()
        #self.mqtw.selected doesn't belong to self.mem.data, it's a set of this widget, so I need to reload investment of the self.mem.data
        self.mem.data.investments.find_by_id(self.mqtw.selected.investment.id).get_operinversiones()
        self.load()
        
    @pyqtSlot() 
    def on_actionShowInvestmentOperation_triggered(self):
        if self.tab.currentIndex()==0:#Operation list
            operation=self.mqtw.selected
        else:#Current operation list
            operation=self.mqtwCurrent.selected
        w=frmInvestmentOperationsAdd(self.mem, operation.investment, operation, self)
        w.exec_()
        self.load()
        

    def on_mqtw_customContextMenuRequested(self,  pos):
        self.actionShowAccount.setEnabled(False)
        self.actionShowInvestment.setEnabled(False)
        self.actionShowInvestmentOperation.setEnabled(False)
        self.actionShowProduct.setEnabled(False)
        if self.mqtw.selected is not None:
            self.actionShowAccount.setEnabled(True)
            self.actionShowInvestment.setEnabled(True)
            self.actionShowInvestmentOperation.setEnabled(True)
            self.actionShowProduct.setEnabled(True)
            if self.mqtw.selected.show_in_ranges==True:
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
        menu.addSeparator()
        menu.addMenu(self.mqtw.qmenu())
        menu.exec_(self.mqtw.table.mapToGlobal(pos))
                
    def on_mqtwCurrent_customContextMenuRequested(self,  pos):
        if self.mqtwCurrent.selected is None:
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
        menu.addSeparator()
        menu.addMenu(self.mqtwCurrent.qmenu())
        menu.exec_(self.mqtwCurrent.table.mapToGlobal(pos))
