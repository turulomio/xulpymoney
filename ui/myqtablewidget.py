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
        self._last_height=None
        
        
    def setVerticalHeaderHeight(self, height):
        """height, if null default.
        Must be after settings"""
        if height==None:
            self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            self._last_height=None
        else:
            self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
            self.verticalHeader().setDefaultSectionSize(height) 
            self._last_height=height

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
        self.setVerticalHeaderHeight(int(self.mem.settings.value("myQTableWidget/rowheight", 24)))
        self.sectionname=sectionname
        if objectname!=None:
            self.setObjectName(objectname)

    def applySettings(self):
        """settings must be defined before"""
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.horizontalHeader().sectionResized.connect(self.sectionResized)
        state=self.mem.settings.value("{}/{}_horizontalheader_state".format(self.sectionname, self.objectName()))
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

    @pyqtSlot()
    def keyPressEvent(self, event):
        if self._last_height==None:
            return
        height=int(self.mem.settings.value("myQTableWidget/rowheight", 24))
        if  event.matches(QKeySequence.ZoomIn):
            self.mem.settings.setValue("myQTableWidget/rowheight", height+1)
        elif  event.matches(QKeySequence.ZoomOut):
            self.mem.settings.setValue("myQTableWidget/rowheight", height-1)
        print("Setting myQTableWidget/rowheight set to {}".format(self.mem.settings.value("myQTableWidget/rowheight", 24)))
        self.setVerticalHeaderHeight(int(self.mem.settings.value("myQTableWidget/rowheight", 24)))

