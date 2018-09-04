from PyQt5.QtCore import Qt,  pyqtSlot
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QApplication, QHeaderView, QTableWidget, QFileDialog
from officegenerator import ODS_Write,  columnAdd,  rowAdd,  OdfMoney,  OdfPercentage
import datetime
import logging
from decimal import Decimal

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
        if  event.matches(QKeySequence.ZoomIn) and self._last_height!=None:
            height=int(self.mem.settings.value("myQTableWidget/rowheight", 24))
            self.mem.settings.setValue("myQTableWidget/rowheight", height+1)
            logging.info("Setting myQTableWidget/rowheight set to {}".format(self.mem.settings.value("myQTableWidget/rowheight", 24)))
            self.setVerticalHeaderHeight(int(self.mem.settings.value("myQTableWidget/rowheight", 24)))
        elif  event.matches(QKeySequence.ZoomOut) and self._last_height!=None:
            height=int(self.mem.settings.value("myQTableWidget/rowheight", 24))
            self.mem.settings.setValue("myQTableWidget/rowheight", height-1)
            ("Setting myQTableWidget/rowheight set to {}".format(self.mem.settings.value("myQTableWidget/rowheight", 24)))
            self.setVerticalHeaderHeight(int(self.mem.settings.value("myQTableWidget/rowheight", 24)))
        elif event.matches(QKeySequence.Print):
            filename = QFileDialog.getSaveFileName(self, self.tr("Save File"), "table.ods", self.tr("Libreoffice calc (*.ods)"))[0]
            if filename:
                Table2ODS(self.mem,filename, self, "My table")
            
class Table2ODS(ODS_Write):
    def __init__(self, mem, filename, table, title):
        ODS_Write.__init__(self, filename)
        self.mem=mem
#        numrows=table.rowCount() if table.horizontalHeader().isHidden() else table.rowCount()+1
#        numcolumns=table.columnCount() if table.verticalHeader().isHidden() else table.columnCount()+1
        sheet=self.createSheet(title)
        #Array width
        widths=[]
        if not table.verticalHeader().isHidden():
            widths.append(table.verticalHeader().width()*0.90)
        for i in range(table.columnCount()):
            widths.append(table.columnWidth(i)*0.90)
        sheet.setColumnsWidth(widths)
        
        #firstcontentletter and firstcontentnumber
        if table.horizontalHeader().isHidden() and not table.verticalHeader().isHidden():
            firstcontentletter="B"
            firstcontentnumber="1"
        elif not table.horizontalHeader().isHidden() and table.verticalHeader().isHidden():
            firstcontentletter="A"
            firstcontentnumber="2"
        elif not table.horizontalHeader().isHidden() and not table.verticalHeader().isHidden():
            firstcontentletter="B"
            firstcontentnumber="2"
        elif table.horizontalHeader().isHidden() and table.verticalHeader().isHidden():
            firstcontentletter="A"
            firstcontentnumber="1"
        sheet.setSplitPosition(firstcontentletter, firstcontentnumber)
        #HH
        if not table.horizontalHeader().isHidden():
            for letter in range(table.columnCount()):
                sheet.add(columnAdd(firstcontentletter, letter), "1", table.horizontalHeaderItem(letter).text(), "HeaderOrange")
        #VH
        if not table.verticalHeader().isHidden():
            for number in range(table.rowCount()):
                try:#Caputuro cuando se numera sin items 1, 2, 3
                    sheet.add("A", rowAdd(firstcontentnumber, number), table.verticalHeaderItem(number).text(), "HeaderYellow")
                except:
                    pass
        #Items
        for number in range(table.rowCount()):
            for letter in range(table.columnCount()):
                try:
                    o=self.itemtext2object(table.item(number, letter).text())
                    sheet.add(columnAdd(firstcontentletter, letter), rowAdd(firstcontentnumber, number),o, self.object2style(o))
                except:#Not a QTableWidgetItem or NOne
                    pass
        sheet.setCursorPosition(firstcontentletter, table.rowCount()+2)
        self.save()
        
    def itemtext2object(self, t):
        """
            Convierte t en un Money, Percentage o lo deja como text
        """
        if t[-2:]==" %":
            try:
                number=Decimal(t.replace(" %", ""))
                return OdfPercentage(number, 100)
            except:
                logging.info("Error converting percentage")
                pass
        elif t[-2:] in (" €"," $"):
           try:
                number=Decimal(t.replace(t[-2:], ""))
                return OdfMoney(number, self.mem.currencies.find_by_symbol(t[-1:]).id)
           except:
                logging.info("Error converting Money")
        elif t.find(":")!=-1 and t.find("-")!=-1:
            try:
                return datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
            except:
                logging.info("Error convertir datetime {}".format(t))
        elif t.find("-")!=-1:
            try:
                return datetime.datetime.strptime(t, "%Y-%m-%d").date()
            except:
                logging.info("Error convertir date {}".format(t))
        elif t.find(".")!=-1:
            try:
                return Decimal(t)
            except:
                logging.info("Error convertir Decimal {}".format(t))
        else:
            try:
                return int(t)
            except:
                logging.info("Error convertir Integer {}".format(t))
        return t


    def object2style(self, o):
        """
            Define el style de un objeto
        """
        if o.__class__==OdfMoney:
            return "EuroColor"
        elif o.__class__==OdfPercentage:
            return "TextRight"
        else:
            return "TextLeft"
