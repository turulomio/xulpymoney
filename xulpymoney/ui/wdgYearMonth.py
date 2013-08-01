from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Ui_wdgYearMonth import *

class wdgYearMonth(QWidget, Ui_wdgYearMonth):
    def __init__(self,  parent = None, name = None):
        QWidget.__init__(self,  parent)
        self.setupUi(self)
        
        
    def initiate(self, firstyear,  lastyear, currentyear, currentmonth):
        """Debe ser la primera funci´on despu´es del constructor"""
        self.firstyear=firstyear
        self.lastyear=lastyear
        for year in range(firstyear, lastyear+1):
            self.cmbYear.addItem(str(year), year)
        self.set(currentyear, currentmonth)
        
    def set(self,  year , month):
        self.year=year
        self.month=month
        self.cmbYear.setCurrentIndex(self.year-self.firstyear)
        self.cmbMonth.setCurrentIndex(self.month-1)

    @pyqtSlot(str)      
    def on_cmbYear_currentIndexChanged(self, text):
        self.year=int(text)
        self.emit(SIGNAL("changed"))
        
    @pyqtSlot(int)      
    def on_cmbMonth_currentIndexChanged(self, integ):
        self.month=integ+1
        self.emit(SIGNAL("changed"))
        
    def on_cmdNext_pressed(self):
        if self.month==12:
            if self.year==self.lastyear:
                m=QMessageBox()
                m.setIcon(QMessageBox.Information)
                m.setText(self.trUtf8("I can't show the next month"))
                m.exec_()   
                return
            self.month=1
            self.year=self.year+1
        else:
            self.month=self.month+1
        self.set(self.year, self.month)
        
    def on_cmdPrevious_pressed(self):
        if self.month==1:
            if self.firstyear==self.year:
                m=QMessageBox()
                m.setIcon(QMessageBox.Information)
                m.setText(self.trUtf8("I can't show the previous month"))
                m.exec_()   
                return
            self.month=12
            self.year=self.year-1
        else:
            self.month=self.month-1
        self.set(self.year, self.month)

