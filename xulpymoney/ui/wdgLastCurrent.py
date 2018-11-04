import logging
from xulpymoney.libxulpymoneyfunctions import qmessagebox
from PyQt5.QtCore import QSize, pyqtSlot
from PyQt5.QtWidgets import QDialog, QMenu, QVBoxLayout, QWidget
from xulpymoney.ui.Ui_wdgLastCurrent import Ui_wdgLastCurrent
from xulpymoney.ui.frmInvestmentReport import frmInvestmentReport
from xulpymoney.ui.frmProductReport import frmProductReport
from xulpymoney.ui.wdgCalculator import wdgCalculator
from xulpymoney.ui.wdgDisReinvest import wdgDisReinvest
from decimal import Decimal

class wdgLastCurrent(QWidget, Ui_wdgLastCurrent):
    def __init__(self, mem,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        self.investments=None
        self.tblInvestments.settings(self.mem, "wdgLastCurrent")
        self.spin.setValue(int(self.mem.settingsdb.value("wdgLastCurrent/spin", "-25")))
        self.on_cmbSameProduct_currentIndexChanged(int(self.mem.settingsdb.value("wdgLastCurrent/viewode", 0)))
#        self.cmbSameProduct.setCurrentIndex(int(self.mem.settingsdb.value("wdgLastCurrent/viewmode",0)))
#        self.cmbSameProduct.currentIndexChanged.emit(int(self.mem.settingsdb.value("wdgLastCurrent/viewode", 0)))

    def tblInvestments_reload(self):
        self.investments.myqtablewidget_lastCurrent(self.tblInvestments, self.spin.value())

    @pyqtSlot() 
    def on_actionInvestmentReport_triggered(self):
        w=frmInvestmentReport(self.mem, self.investments.selected, self)
        w.exec_()
        self.tblInvestments_reload()
        
    @pyqtSlot() 
    def on_actionCalculate_triggered(self):
        d=QDialog(self)        
        d.setFixedSize(850, 850)
        d.setWindowTitle(self.tr("Investment last operation calculator"))
        w=wdgCalculator(self.mem)
        w.setInvestment(self.investments.selected)
        price=self.investments.selected.op_actual.last().valor_accion*(1+self.spin.value()/Decimal(100))#Is + because -·-
        w.txtFinalPrice.setText(price)
        lay = QVBoxLayout(d)
        lay.addWidget(w)
        d.show()        
        
    @pyqtSlot() 
    def on_actionReinvest_triggered(self):
        d=QDialog()       
        d.resize(self.mem.settings.value("frmInvestmentReport/qdialog_disreinvest", QSize(1024, 768)))
        d.setWindowTitle(self.tr("Divest / Reinvest simulation"))
        w=wdgDisReinvest(self.mem, self.investments.selected, False,  d)
        price=self.investments.selected.op_actual.last().valor_accion*(1+self.spin.value()/Decimal(100))#Is + because -·-        
        w.txtValorAccion.setText(price)
        lay = QVBoxLayout(d)
        lay.addWidget(w)
        d.exec_()
        self.mem.settings.setValue("frmInvestmentReport/qdialog_disreinvest", d.size())        
        
    @pyqtSlot() 
    def on_actionReinvestCurrent_triggered(self):
        d=QDialog()       
        d.resize(self.mem.settings.value("frmInvestmentReport/qdialog_disreinvest", QSize(1024, 768)))
        d.setWindowTitle(self.tr("Divest / Reinvest simulation"))
        w=wdgDisReinvest(self.mem, self.investments.selected, False,  d)
        lay = QVBoxLayout(d)
        lay.addWidget(w)
        d.exec_()
        self.mem.settings.setValue("frmInvestmentReport/qdialog_disreinvest", d.size())
                
    @pyqtSlot() 
    def on_actionProduct_triggered(self):
        w=frmProductReport(self.mem, self.investments.selected.product, self.investments.selected, self)
        w.exec_()
        self.tblInvestments_reload()
      
   
    @pyqtSlot() 
    def on_actionSortTPCVenta_triggered(self):
        if self.investments.order_by_percentage_sellingpoint()==False:
            qmessagebox(self.tr("I couldn't order data due to they have null values"))     
        self.tblInvestments_reload()
        
    @pyqtSlot() 
    def on_actionSortTPC_triggered(self):
        if self.investments.order_by_percentage_invested()==False:
            qmessagebox(self.tr("I couldn't order data due to they have null values"))     
        self.tblInvestments_reload()
        
    @pyqtSlot() 
    def on_actionSortHour_triggered(self):
        if self.investments.order_by_datetime_last_operation()==False:
            qmessagebox(self.tr("I couldn't order data due to they have null values"))     
        self.tblInvestments_reload()
        
    @pyqtSlot() 
    def on_actionSortName_triggered(self):            
        if self.investments.order_by_name()==False:
            qmessagebox(self.tr("I couldn't order data due to they have null values"))     
        self.tblInvestments_reload()    

    @pyqtSlot() 
    def on_actionSortTPCLast_triggered(self):
        if self.investments.order_by_percentage_last_operation()==False:
            qmessagebox(self.tr("I couldn't order data due to they have null values"))     
        self.tblInvestments_reload()    
            

    def on_tblInvestments_customContextMenuRequested(self,  pos):
        if self.investments.selected==None:
            self.actionInvestmentReport.setEnabled(False)
            self.actionProduct.setEnabled(False)
        else:
            self.actionInvestmentReport.setEnabled(True)
            self.actionProduct.setEnabled(True)


        self.actionCalculate.setText("Calculate order at {} % since last operation".format(self.spin.value()))
        self.actionReinvest.setText("Simulate reinvestment at {} % since last operation".format(self.spin.value()))
        menu=QMenu()
        menu.addAction(self.actionCalculate)
        menu.addSeparator()
        menu.addAction(self.actionReinvestCurrent)
        menu.addAction(self.actionReinvest)
        menu.addSeparator()
        menu.addAction(self.actionInvestmentReport)        
        menu.addAction(self.actionProduct)
        menu.addSeparator()
        ordenar=QMenu(self.tr("Order by"))
        ordenar.addAction(self.actionSortName)
        ordenar.addAction(self.actionSortHour)
        ordenar.addAction(self.actionSortTPCLast)
        ordenar.addAction(self.actionSortTPC)
        ordenar.addAction(self.actionSortTPCVenta)
        menu.addMenu(ordenar)        
        menu.exec_(self.tblInvestments.mapToGlobal(pos))

    def on_cmd_released(self):
        self.tblInvestments_reload()
        self.mem.settingsdb.setValue("wdgLastCurrent/spin", self.spin.value())

    def on_tblInvestments_itemSelectionChanged(self):
        self.investments.selected=None
        for i in self.tblInvestments.selectedItems():#itera por cada item no row.
            self.investments.selected=self.investments.arr[i.row()]

    @pyqtSlot(int)
    def on_cmbSameProduct_currentIndexChanged(self, index):
        self.cmbSameProduct.setCurrentIndex(index)
        logging.debug("Changing to {} {}".format(index,index.__class__))
        if index==0:
            self.investments=self.mem.data.investments_active()
            self.on_actionSortTPCLast_triggered()
        elif index==1:
            self.investments=self.mem.data.investments_active().setInvestments_merging_investments_with_same_product_merging_current_operations()
            self.on_actionSortTPCLast_triggered()
        elif index==2:
            self.investments=self.mem.data.investments_active().setInvestments_merging_investments_with_same_product_merging_operations()
            self.on_actionSortTPCLast_triggered()
            self.tblInvestments_reload()
        self.mem.settingsdb.setValue("wdgLastCurrent/viewode", index)
