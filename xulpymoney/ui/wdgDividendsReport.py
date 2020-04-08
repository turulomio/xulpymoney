from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMenu, QWidget
from xulpymoney.objects.assets import Assets
from xulpymoney.ui.Ui_wdgDividendsReport import Ui_wdgDividendsReport

class wdgDividendsReport(QWidget, Ui_wdgDividendsReport):
    def __init__(self, mem,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem

        self.mqtw.setSettings(self.mem.settings, "wdgDividendsReport", "mqtw")#mqtwObjects
        self.mqtw.table.customContextMenuRequested.connect(self.on_mqtw_customContextMenuRequested)
        
        self.on_chkInactivas_stateChanged(Qt.Unchecked)

    @pyqtSlot()  
    def on_actionEstimationDPSEdit_triggered(self):
        from xulpymoney.ui.frmEstimationsAdd import frmEstimationsAdd
        d=frmEstimationsAdd(self.mem, self.mqtw.selected.product, "dps")
        d.exec_()
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())
        self.mqtw.table.clearSelection()

    def on_chkInactivas_stateChanged(self,  state):               
        if state==Qt.Checked:
            self.investments=self.mem.data.investments_inactive()
        else:
            self.investments=self.mem.data.investments_active()
        self.load_inversiones()
        
    def load_inversiones(self):
        self.investments.mqtw_with_dps_estimations(self.mqtw)
        self.mqtw.setOrderBy(5, True)
        self.lblTotal.setText(self.tr("If I keep this investment during a year, I'll get {0}").format( Assets(self.mem).dividends_estimated()))

    ## It's here and not an additional due to depends self.spin.value()
    @pyqtSlot()
    def on_mqtw_setDataFinished(self):
        for i, inv in enumerate(self.mqtw.objects()):
            if inv.product.estimations_dps.dias_sin_actualizar()>self.spin.value():
                self.mqtw.table.item(i, 3).setIcon(QIcon(":/xulpymoney/alarm_clock.png"))

    @pyqtSlot() 
    def on_actionInvestmentReport_triggered(self):
        from xulpymoney.ui.frmInvestmentReport import frmInvestmentReport
        w=frmInvestmentReport(self.mem, self.mqtw.selected, self)
        w.exec_()
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())

    @pyqtSlot() 
    def on_actionProductReport_triggered(self):
        from xulpymoney.ui.frmProductReport import frmProductReport
        w=frmProductReport(self.mem, self.mqtw.selected.product, self.mqtw.selected, self)
        w.exec_()
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())

    def on_cmd_pressed(self):
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())

    def on_mqtw_customContextMenuRequested(self,  pos):
        if self.mqtw.selected is None:
            self.actionEstimationDPSEdit.setEnabled(False)
            self.actionInvestmentReport.setEnabled(False)
            self.actionProductReport.setEnabled(False)
        else:
            self.actionEstimationDPSEdit.setEnabled(True)
            self.actionInvestmentReport.setEnabled(True)
            self.actionProductReport.setEnabled(True)

        menu=QMenu()
        menu.addAction(self.actionEstimationDPSEdit)
        menu.addSeparator()
        menu.addAction(self.actionInvestmentReport) 
        menu.addAction(self.actionProductReport)    
        menu.addSeparator()
        menu.addMenu(self.mqtw.qmenu())
        menu.exec_(self.mqtw.table.mapToGlobal(pos))
