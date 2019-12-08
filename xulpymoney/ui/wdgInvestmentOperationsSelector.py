from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget
from xulpymoney.ui.Ui_wdgInvestmentOperationsSelector import Ui_wdgInvestmentOperationsSelector

class wdgInvestmentOperationsSelector(QWidget, Ui_wdgInvestmentOperationsSelector):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        
    ## Manager must be a manager with objects
    def setManager(self, mem, manager, objectname):
        self.mem=mem
        self.tbl.settings(self.mem, "{}_tbl".format(objectname))
        self.manager=manager
        self.manager.myqtablewidget(self.tbl)
        
    ## Checks item from position list
    def setCheckedPositions(self, checked):
        for i in range(self.tbl.rowCount()):
            item=self.tbl.item(i, 0)
            if item!=None:
                if i in checked:
                    item.setCheckState(Qt.Checked)
                else:
                    item.setCheckState(Qt.Unchecked)
        
    def setBoxTitle(self, title):
        pass

    ## Objects must have id
    def getCheckedIds(self):
        r=[]
        for i in range(self.tbl.rowCount()):
            item=self.tbl.item(i, 0)
            if item!=None:
                if item.checkState()==Qt.Checked:
                    try:
                        print(dir(self.manager.arr[i]))
                        
                        id=self.manager.arr[i].id
                        print(id)
                        r.append(id)
                    except:
                        pass
        return r

    ## Get selection position. It doesn
    def getCheckedPositions(self):
        r=[]
        for i in range(self.tbl.rowCount()):
            item=self.tbl.item(i, 0)
            if item!=None:
                if item.checkState()==Qt.Checked:
                    if i < self.manager.length():
                        r.append(i)
        return r
