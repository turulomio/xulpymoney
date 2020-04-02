from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget
from xulpymoney.casts import list2string, string2list_of_strings
from xulpymoney.ui.Ui_wdgInvestmentOperationsSelector import Ui_wdgInvestmentOperationsSelector

class wdgObjectSelector(QWidget, Ui_wdgInvestmentOperationsSelector):
#    itemChanged=pyqtSignal()
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
#        self.mqtwOperations.itemChanged.connect(self.__mqtwOperations_itemChanged)
#
#    @pyqtSlot()
#    def __mqtwOperations_itemChanged(self):
#        self.itemChanged.emit()
        
    ## Manager must be a manager with objects
    def setManager(self, mem, manager, settingsSection, settingsObject):
        self.mem=mem
        self._settingsSection=settingsSection
        self._settingsObject=settingsObject
        self.mqtwOperations.setSettings(self.mem.settings, settingsSection, "{}_tbl".format(settingsObject))
        self.manager=manager
        self.manager.myqtablewidget(self.mqtwOperations)

    def setBoxTitle(self, title):
        pass

    ## Objects must have id
    def getCheckedPositions(self):
        r=[]
        for i in range(self.mqtwOperations.table.rowCount()):
            item=self.mqtwOperations.table.item(i, 0)
            if item!=None:
                if item.checkState()==Qt.Checked:
                    r.append(i)
        return r
        
    ## Checks item from position list
    def setCheckedPositions(self, checked):
        self.mqtwOperations.table.blockSignals(True)
        for i in range(self.mqtwOperations.table.rowCount()):
            item=self.mqtwOperations.table.item(i, 0)
            if item!=None:
                if i in checked:
                    item.setCheckState(Qt.Checked)
                else:
                    item.setCheckState(Qt.Unchecked)
        self.mqtwOperations.table.blockSignals(False)

    ## Get selection position. It doesn
    def getCheckedObjectsList(self):
        r=[]
        for i in range(self.mqtwOperations.table.rowCount()):
            item=self.mqtwOperations.table.item(i, 0)
            if item!=None:
                if item.checkState()==Qt.Checked:
                    if i < self.manager.length():
                        r.append(self.manager.arr[i])
        return r

##IOH have id with a string "investment_id#IOH_position"
class wdgInvestmentOperationHistoricalSelector(wdgObjectSelector):
    def __init__(self, parent=None):
        wdgObjectSelector.__init__(self, parent)

    def getSelectedString(self):
        r=[]
        for o in self.getCheckedObjectsList():
            r.append(o.id)
        return list2string(r)
        
    ## Selects objects from a string
    def setSelectedString(self, s):
        positions=[]
        for id in string2list_of_strings(s):
            o=self.manager.find_by_id(id)
            if o==None:
                print("{} not found".format(id))
            else:
                positions.append(self.manager.arr.index(o))
        self.setCheckedPositions(positions)
        print(positions)
