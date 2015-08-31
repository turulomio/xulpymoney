from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from libxulpymoney import *

class myQTableWidget(QTableWidget):
    def __init__(self, parent):
        QTableWidget.__init__(self, parent)
        self.parent=parent
        self.mem=None
        self.parentname=None


    def sectionResized(self, logicalIndex, oldSize, newSize):
        self.mem.settings.setValue("{}/{}_horizontalheader_state".format(self.parentname, self.objectName()), self.horizontalHeader().saveState() )
        
    def settings(self, mem, parentname=None):
        """Sometimes parentname is not wdg or frm  Widget (may be a groupbox), so I must define it manually"""    
        if parentname==None:
            self.parentname=self.parent.objectName()
        else:
            self.parentname=parentname
        self.mem=mem

        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.horizontalHeader().sectionResized.connect(self.sectionResized)
        state=self.mem.settings.value("{}/{}_horizontalheader_state".format(self.parentname, self.objectName()))
        if state:
            self.horizontalHeader().restoreState(state)
        

    def clear(self):
        """Clear table"""
        self.setRowCount(0)
        self.clearContents()

    def verticalScrollbarAction(self,  action):
        """Resizes columns if column width is less than table hint"""
        for i in range(self.columnCount()):
            if self.sizeHintForColumn(i)>self.columnWidth(i):
                self.setColumnWidth(i, self.sizeHintForColumn(i))
        self.resizeRowsToContents()

    def on_cellDoubleClicked(self, row,  column):
        """Resizes to minimum contents"""
        self.resizeColumnsToContents()
        self.resizeRowsToContents()
