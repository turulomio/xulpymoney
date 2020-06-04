from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget, QMenu
from xulpymoney.objects.strategy import StrategyManager_all
from xulpymoney.ui.Ui_wdgStrategyResults import Ui_wdgStrategyResults
from xulpymoney.ui.myqdialog import MyModalQDialog
from xulpymoney.ui.myqwidgets import qmessagebox_question
from xulpymoney.ui.wdgStrategyResultsAdd import wdgStrategyResultsAdd

class wdgStrategyResults(QWidget, Ui_wdgStrategyResults):
    def __init__(self, mem,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        self.mqtwStrategies.setSettings(self.mem.settings, "wdgStrategyResults", "mqtwStrategies")
        self.mqtwStrategies.table.customContextMenuRequested.connect(self.on_mqtwStrategies_customContextMenuRequested) 
        self.mqtwStrategies.table.cellDoubleClicked.connect(self.on_mqtwStrategies_cellDoubleClicked)
        self.update()
         
    @pyqtSlot()  
    def on_actionStrategyNew_triggered(self):
        d=MyModalQDialog(self)
        d.setWindowTitle(self.tr("Add new strategy"))
        d.setSettings(self.mem.settings, "wdgStrategyResults", "wdgStrategyResultsAdd_dialog", 600, 400)
        w=wdgStrategyResultsAdd(self.mem, None, d)
        d.setWidgets(w)
        d.exec_() 
        self.update()
        
        
    def on_mqtwStrategies_cellDoubleClicked(self, row, column):
        self.on_actionStrategyEdit_triggered()
        
        
    @pyqtSlot()  
    def on_actionStrategyEdit_triggered(self):
        d=MyModalQDialog(self)
        d.setWindowTitle(self.tr("Edit a strategy"))
        d.setSettings(self.mem.settings, "wdgStrategyResults", "wdgStrategyResultsAdd_dialog", 600, 400)
        w=wdgStrategyResultsAdd(self.mem, self.mqtwStrategies.selected, d)
        d.setWidgets(w)
        d.exec_()
        self.update()

    @pyqtSlot()  
    def on_actionStrategyDelete_triggered(self):
        if qmessagebox_question(self.tr("Do you want to delete this strategy?")) is True:
            self.mqtwStrategies.selected.delete()
        self.mem.con.commit()
        self.update()

        
    def on_chkFinished_stateChanged(self, state):
        self.update()

    def on_mqtwStrategies_customContextMenuRequested(self,  pos):
        if self.mqtwStrategies.selected==None:
            self.actionStrategyDelete.setEnabled(False)
            self.actionStrategyEdit.setEnabled(False)
        else:
            self.actionStrategyDelete.setEnabled(True)
            self.actionStrategyEdit.setEnabled(True)

        menu=QMenu()
        menu.addAction(self.actionStrategyNew)
        menu.addSeparator()
        menu.addAction(self.actionStrategyEdit)
        menu.addAction(self.actionStrategyDelete)
        menu.addSeparator()
        menu.addMenu(self.mqtwStrategies.qmenu())
        menu.exec_(self.mqtwStrategies.table.mapToGlobal(pos))
        
        
    def update(self):
        self.strategies=StrategyManager_all(self.mem)
        self.strategies.myqtablewidget(self.mqtwStrategies, self.chkFinished.isChecked())
        
