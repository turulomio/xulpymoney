from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget
from xulpymoney.ui.Ui_wdgInvestmentOperationsSelector import Ui_wdgInvestmentOperationsSelector

class wdgInvestmentOperationsSelector(QWidget, Ui_wdgInvestmentOperationsSelector):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        
    ## Manager must be a manager with objects with id
    def setManager(self, mem, manager, list_selected_ids, tblname):
        self.mem=mem
        self.tbl.settings(self.mem, tblname)
        self.manager=manager
        self.manager.myqtablewidget(self.tbl)
        for i in range(self.tbl.rowCount()):
            item=self.tbl.item(i, 0)
            if item!=None:
                item.setCheckState(Qt.Checked)
        
    def setBoxTitle(self, title):
        pass

    def getSelectedIds(self):
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

