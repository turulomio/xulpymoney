from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from libxulpymoney import *

class myQTableWidget(QTableWidget):
    def __init__(self, parent):
        QTableWidget.__init__(self, parent)
        self.parent=parent
        self.mem=None
        self.sectionname=None
        self._save_settings=True
        self.setAlternatingRowColors(True)
        self.saved_printed=False#To avoid printing a lot of times
        self.setStyleSheet("""
QHeaderView::section{
padding-left=0px;
color:red;
padding-top=0px;
}

QTableWidget{
padding:1px;
}
""")
        self.verticalHeader().setContentsMargins(0, 0, 0, 0)
        #        self.setVerticalHeaderHeight(24)
        
        
#    def setVerticalHeaderHeight(self, height):
#        """height, if null default."""
#        if height==None:
#            self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
#            self.verticalHeader().setSectionResizeMode(QHeaderView.Interactive)
##            self.resizeColumnsToContents()
#        else:
#            self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
#            self.verticalHeader().setDefaultSectionSize(24) 

    def setSaveSettings(self, state):
        """Used when i don't want my columns with being saved"""
        self._save_settings=state

    def sectionResized(self, logicalIndex, oldSize, newSize):
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ShiftModifier:
            for i in range(self.columnCount()):
                self.setColumnWidth(i, newSize)
        elif modifiers == Qt.ControlModifier:
            self.resizeRowsToContents()
            self.resizeColumnsToContents()
        self.save()
            
            
    def save(self):
        if self._save_settings==True:
            self.mem.settings.setValue("{}/{}_horizontalheader_state".format(self.sectionname, self.objectName()), self.horizontalHeader().saveState() )
            if self.saved_printed==False: 
                print("Saved {}/{}_horizontalheader_state".format(self.sectionname, self.objectName()))
                self.saved_printed=True
        
    def settings(self, mem, sectionname,  objectname=None):
        """objectname used for dinamic tables"""
        self.mem=mem
        self.sectionname=sectionname
        if objectname!=None:
            self.setObjectName(objectname)

    def applySettings(self):
        """settings must be defined before"""
#        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.horizontalHeader().sectionResized.connect(self.sectionResized)
        state=self.mem.settings.value("{}/{}_horizontalheader_state".format(self.sectionname, self.objectName()))
        if state:
#            print("Loaded {}/{}_horizontalheader_state".format(self.sectionname, self.objectName()))
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
#        self.resizeRowsToContents()
#        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
#        self.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)

