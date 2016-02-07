from libxulpymoney import *
from libqmessagebox import qmessagebox_error_ordering
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from Ui_wdgLastCurrent import *
from frmInvestmentReport import *
from frmQuotesIBM import *
from frmProductReport import *
from wdgCalculator import *
from wdgDisReinvest import *

class wdgLastCurrent(QWidget, Ui_wdgLastCurrent):
    def __init__(self, mem,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        self.selInvestment=None
        self.tblInvestments.settings(self.mem, "wdgLastCurrent")
        self.spin.setValue(int(self.mem.settingsdb.value("wdgLastCurrent/spin", "-25")))
        self.on_actionSortTPCLast_triggered()
        
    def tblInvestments_reload(self):
        self.mem.data.investments_active().myqtablewidget_lastCurrent(self.tblInvestments, self.spin.value())
        
    @QtCore.pyqtSlot() 
    def on_actionInvestmentReport_triggered(self):
        w=frmInvestmentReport(self.mem, self.selInvestment, self)
        w.exec_()
        self.tblInvestments_reload()
        
    @QtCore.pyqtSlot() 
    def on_actionCalculate_triggered(self):
        d=QDialog(self)        
        d.setFixedSize(850, 850)
        d.setWindowTitle(self.tr("Investment last operation calculator"))
        w=wdgCalculator(self.mem)
        w.cmbProducts.setCurrentIndex(w.cmbProducts.findData(self.selInvestment.product.id))
        price=self.selInvestment.op_actual.arr[self.selInvestment.op_actual.length()-1].valor_accion*(1+self.spin.value()/Decimal(100))#Is + because -·-
        w.txtFinalPrice.setText(price)
        lay = QVBoxLayout(d)
        lay.addWidget(w)
        d.show()        
        
    @QtCore.pyqtSlot() 
    def on_actionReinvest_triggered(self):
        d=QDialog()       
        d.resize(self.mem.settings.value("frmInvestmentReport/qdialog_disreinvest", QSize(1024, 768)))
        d.setWindowTitle(self.tr("Divest / Reinvest simulation"))
        w=wdgDisReinvest(self.mem, self.selInvestment, d)
        price=self.selInvestment.op_actual.arr[self.selInvestment.op_actual.length()-1].valor_accion*(1+self.spin.value()/Decimal(100))#Is + because -·-        
        w.txtValorAccion.setText(price)
        lay = QVBoxLayout(d)
        lay.addWidget(w)
        d.exec_()
        self.mem.settings.setValue("frmInvestmentReport/qdialog_disreinvest", d.size())
                
    @QtCore.pyqtSlot() 
    def on_actionProduct_triggered(self):
        w=frmProductReport(self.mem, self.selInvestment.product, self.selInvestment, self)
        w.exec_()
        self.tblInvestments_reload()
   
    @QtCore.pyqtSlot() 
    def on_actionSortTPCVenta_triggered(self):
        if self.mem.data.investments_active().order_by_percentage_sellingpoint():
            self.tblInvestments_reload()    
        else:
            qmessagebox_error_ordering()     
        
    @QtCore.pyqtSlot() 
    def on_actionSortTPC_triggered(self):
        if self.mem.data.investments_active().order_by_percentage_invested():
            self.tblInvestments_reload()    
        else:
            qmessagebox_error_ordering()     
        
    @QtCore.pyqtSlot() 
    def on_actionSortHour_triggered(self):
        if self.mem.data.investments_active().order_by_datetime_last_operation():
            self.tblInvestments_reload()    
        else:
            qmessagebox_error_ordering()     
        
    @QtCore.pyqtSlot() 
    def on_actionSortName_triggered(self):
        if self.mem.data.investments_active().order_by_name():
            self.tblInvestments_reload()    
        else:
            qmessagebox_error_ordering()     
            
    @QtCore.pyqtSlot() 
    def on_actionSortTPCLast_triggered(self):
        if self.mem.data.investments_active().order_by_percentage_last_operation():
            self.tblInvestments_reload()    
        else:
            qmessagebox_error_ordering()     
            

    def on_tblInvestments_customContextMenuRequested(self,  pos):
        if self.selInvestment==None:
            self.actionInvestmentReport.setEnabled(False)
            self.actionProduct.setEnabled(False)
        else:
            self.actionInvestmentReport.setEnabled(True)
            self.actionProduct.setEnabled(True)


        self.actionCalculate.setText("Calculate order at {} since last operation".format(tpc(self.spin.value())))
        self.actionReinvest.setText("Simulate reinvestment at {} since last operation".format(tpc(self.spin.value())))
        menu=QMenu()
        menu.addAction(self.actionCalculate)
        menu.addSeparator()
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
        self.selInvestment=None
        for i in self.tblInvestments.selectedItems():#itera por cada item no row.
            self.selInvestment=self.mem.data.investments_active().arr[i.row()]

    @QtCore.pyqtSlot(int, int) 
    def on_tblInvestments_cellDoubleClicked(self, row, column):
        if column==8:#TPC Venta
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.tr("Shares number: {0}").format(self.selInvestment.acciones())+"\n"+
                    self.tr("Purchase price average: {0}").format(self.selInvestment.product.currency.string(self.selInvestment.op_actual.valor_medio_compra()))+"\n"+
                    self.tr("Selling point: {}").format(self.selInvestment.product.currency.string(self.selInvestment.venta))+"\n"+
                    self.tr("Selling all shares you get {}").format(self.selInvestment.product.currency.string(self.selInvestment.op_actual.pendiente(Quote(self.mem).init__create(self.selInvestment.product, self.mem.localzone.now(),  self.selInvestment.venta))))
            )
            m.exec_()     
        else:
            self.on_actionCalculate_triggered()
