from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import datetime
from Ui_wdgYear import *

class wdgYear(QWidget, Ui_wdgYear):
    changed=pyqtSignal()
    def __init__(self,  parent = None, name = None):
        QWidget.__init__(self,  parent)
        self.setupUi(self)
        
        
    def initiate(self, firstyear,  lastyear, currentyear):
        """Debe ser la primera función después del constructor"""
        if firstyear==None:
            self.setEnabled(False)
            print (function_name(self), "Firstyear is None")
            return
        
        
        self.firstyear=firstyear
        self.lastyear=lastyear
        for year in range(firstyear, lastyear+1):
            self.cmbYear.addItem(str(year), year)
        self.set(currentyear)
        
    def set(self,  year):
        self.year=year
        self.cmbYear.setCurrentIndex(self.year-self.firstyear)

    @pyqtSlot(str)      
    def on_cmbYear_currentIndexChanged(self, text):
        self.year=int(text)
        self.changed.emit()
        
       
    def on_cmdNext_pressed(self):
        if self.year==self.lastyear:
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.tr("I can't show the next year"))
            m.exec_()   
            return
        self.year=self.year+1
        self.set(self.year)
        
    def on_cmdPrevious_pressed(self):
        if self.firstyear==self.year:
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.tr("I can't show the previous year"))
            m.exec_()   
            return
        self.year=self.year-1
        self.set(self.year)
        
    @pyqtSlot()      
    def on_cmdCurrent_pressed(self):
        self.set(datetime.date.today().year)
        
        

