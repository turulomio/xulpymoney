from PyQt4.QtCore import *
from PyQt4.QtGui import *
import datetime
from Ui_wdgDatetime import *
from libxulpymoney import *

class wdgDatetime(QWidget, Ui_wdgDatetime):
    """Usage:
    Use constructor wdgDatetime()
    Set if show seconds, microseconds, zone
    Use set function to set the zone
    """
    def __init__(self,  parent = None, name = None):
        QWidget.__init__(self,  parent)
        self.setupUi(self)
        self.mem=None
        self.showMicroseconds=True
        self.showSeconds=True
        self.showZone=True
        self.zone=None#Set in set()
        self.teDate.calendarWidget().setFirstDayOfWeek(Qt.Monday)
        
    def show_microseconds(self, show):
        self.showMicroseconds=show
        if show==True:
            self.teMicroseconds.show()
        else:
            self.teMicroseconds.hide()
    
    def show_seconds(self, show):
        self.showSeconds=show
        if show==True:
            self.teTime.setDisplayFormat("HH:mm:ss")
        else:
            self.teTime.setDisplayFormat("HH:mm")
        
    def show_timezone(self, show):
        self.showZone=show
        if show==True:
            self.cmbZone.show()
        else:
            self.cmbZone.hide()
            
    def on_cmdNow_released(self):
        self.set(self.mem, datetime.datetime.now(), self.mem.localzone)
        
               
    def set(self,  mem, dt=None,  zone=None):
        """CAn be called several times"""
        self.mem=mem
        if dt==None or zone==None:
            self.on_cmdNow_released()
            return
            
        self.zone=zone
        self.mem.zones.qcombobox(self.cmbZone, self.zone)        
        
        self.teDate.setDate(dt.date())
        
        if self.showSeconds==False:
            dt=dt.replace(second=0)
        self.teTime.setTime(dt.time())
        
        if self.showMicroseconds==False:
            dt=dt.replace(microsecond=0)
        self.teMicroseconds.setValue(dt.microsecond)
        
        self.setZone(self.zone)
        
    def setZone(self, zone):
        """Zone es object"""
        self.cmbZone.setCurrentIndex(self.cmbZone.findData(zone.name))
        
        
    def datetime(self):
        #qt only miliseconds
        time=self.teTime.time().toPyTime()
        time=time.replace(microsecond=self.teMicroseconds.value())
        return dt(self.teDate.date().toPyDate(), time , self.zone)

    def on_teDate_dateChanged(self, date):
        print(self.datetime())
        
    def on_teTime_timeChanged(self, date):
        print(self.datetime())
        
    @pyqtSlot(int)   
    def on_teMicroseconds_valueChanged(self, date):
        print(self.datetime())
        
    @pyqtSlot(str)      
    def on_cmbZone_currentIndexChanged(self, stri):
        self.zone=self.mem.zones.find(self.cmbZone.itemData(self.cmbZone.currentIndex()))
        print(self.datetime())
        
        
        

