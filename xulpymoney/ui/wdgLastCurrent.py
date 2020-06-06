from xulpymoney.objects.percentage import Percentage
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
        self.mqtwInvestments.setSettings(self.mem.settings, "wdgLastCurrent", "mqtwInvestments")
        self.mqtwInvestments.table.customContextMenuRequested.connect(self.on_mqtwInvestments_customContextMenuRequested)
        
        self.spin.blockSignals(True)
        self.spin.setValue(self.mem.settingsdb.value_integer("wdgLastCurrent/spin", "-33"))
        self.spin.blockSignals(False)

        self.cmbSameProduct.setCurrentIndex(self.mem.settingsdb.value_integer("wdgLastCurrent/viewmode", "0"))
        
    def mqtwInvestments_reload(self):
        self.investments.myqtablewidget_lastCurrent(self.mqtwInvestments, Percentage(self.spin.value(), 100))
        self.mqtwInvestments.setOrderBy(6, True)

    @pyqtSlot(int) 
    def on_spin_valueChanged(self, value):
        self.mem.settingsdb.setValue("wdgLastCurrent/spin", str(value))
        self.mqtwInvestments_reload()
        self.mem.settings.sync()

    @pyqtSlot() 
    def on_actionInvestmentReport_triggered(self):
        w=frmInvestmentReport(self.mem, self.mqtwInvestments.selected, self)
        w.exec_()
        self.mqtwInvestments_reload()
        
    @pyqtSlot() 
    def on_actionCalculate_triggered(self):
        d=QDialog(self)        
        d.setFixedSize(850, 850)
        d.setWindowTitle(self.tr("Investment last operation calculator"))
        w=wdgCalculator(self.mem)
        w.setInvestment(self.mqtwInvestments.selected)
        price=self.mqtwInvestments.selected.op_actual.last().valor_accion*(1+self.spin.value()/Decimal(100))#Is + because -·-
        w.txtFinalPrice.setText(price)
        lay = QVBoxLayout(d)
        lay.addWidget(w)
        d.show()        
        
    @pyqtSlot() 
    def on_actionReinvest_triggered(self):
        d=QDialog()       
        d.resize(self.mem.settings.value("frmInvestmentReport/qdialog_disreinvest", QSize(1024, 768)))
        d.setWindowTitle(self.tr("Divest / Reinvest simulation"))
        w=wdgDisReinvest(self.mem, self.mqtwInvestments.selected, False,  d)
        price=self.mqtwInvestments.selected.op_actual.last().valor_accion*(1+self.spin.value()/Decimal(100))#Is + because -·-        
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
        w=wdgDisReinvest(self.mem, self.mqtwInvestments.selected, False,  d)
        lay = QVBoxLayout(d)
        lay.addWidget(w)
        d.exec_()
        self.mem.settings.setValue("frmInvestmentReport/qdialog_disreinvest", d.size())
                
    @pyqtSlot() 
    def on_actionProduct_triggered(self):
        w=frmProductReport(self.mem, self.mqtwInvestments.selected.product, self.mqtwInvestments.selected, self)
        w.exec_()
        self.mqtwInvestments_reload()
      
    def on_mqtwInvestments_customContextMenuRequested(self,  pos):
        if self.mqtwInvestments.selected==None:
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
        menu.addMenu(self.mqtwInvestments.qmenu())
        menu.exec_(self.mqtwInvestments.table.mapToGlobal(pos))

    @pyqtSlot(int)
    def on_cmbSameProduct_currentIndexChanged(self, index):
        if index==0:
            self.investments=self.mem.data.investments_active()
        elif index==1:
            self.investments=self.mem.data.investments_active().InvestmentManager_merging_investments_with_same_product_merging_current_operations()
        elif index==2:
            self.investments=self.mem.data.investments_active().InvestmentManager_merging_investments_with_same_product_merging_operations()
        self.investments.order_by_percentage_last_operation()
        self.mqtwInvestments_reload()
        self.mem.settingsdb.setValue("wdgLastCurrent/viewmode", index)
