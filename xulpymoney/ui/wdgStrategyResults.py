from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget, QInputDialog
from xulpymoney.ui.Ui_wdgStrategyResults import Ui_wdgStrategyResults
from xulpymoney.objects.strategy import StrategyManager_all, Strategy

class wdgStrategyResults(QWidget, Ui_wdgStrategyResults):
    def __init__(self, mem,  parent = None, name = None):
        QWidget.__init__(self,  parent)
        self.setupUi(self)
        self.mem=mem
        self.parent=parent  
        self.update_strategies(self.mem.settingsdb.value_integer("wdgStrategyResults/cmbStrategies", None))
        
    def update_strategies(self, strategy_id=None):
        self.strategies=StrategyManager_all(self.mem)
        self.strategies.order_by_name()
        if strategy_id is not None:
            self.strategies.selected=self.strategies.find_by_id(strategy_id)
        else:
            self.strategies.selected=None
        self.strategies.qcombobox(self.cmbStrategies, self.strategies.selected)
        
        if self.strategies.selected is not None:
        
            self.wdgDtFrom.setLocalzone(self.mem.localzone_name)
            self.wdgDtFrom.show_microseconds(False)
            self.wdgDtTo.setLocalzone(self.mem.localzone_name)
            self.wdgDtTo.show_microseconds(False)
        
        self.cmsInvestments.setManagers(self.mem.settings,"wdgStrategyResults", "cmsInvestments", self.mem.data.investments, None)
        

    @pyqtSlot(int)
    def on_cmbLanguages_currentIndexChanged(self, index):
        self.strategies.selected=self.strategies.find_by_id(self.cmbStrategies.itemData(index))
        self.mem.settingsdb.setValue("wdgStrategyResults/cmbStrategies", self.strategies.selected.id )
        self.update_strategies()

    def on_cmdStrategyAdd_released(self):
        self.strategies.selected=Strategy(self.mem)
        self.strategies.selected.name=QInputDialog().getText(self,  "Xulpymoney",  self.tr("Change name"))
        self.strategies.selected.save()
        self.strategies.append(self.strategies.selected)
        self.mem.settingsdb.setValue("wdgStrategyResults/cmbStrategies", self.strategies.selected.id )
        self.update()
        
        
