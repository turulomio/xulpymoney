## -*- coding: utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from libxulpymoney import *
import pytz

class QComboBoxTZ(QComboBox):
    def __init__(self, parent=None):
        QComboBox.__init__(self, parent)
        arr=[]
        for c in pytz.country_timezones:
            for tz in pytz.country_timezones[c]:
                #zona, country_abrev
                arr.append([tz, c])
        arr=sorted(arr, key=lambda row: row[0],  reverse=False)          
        for c in arr:
#            icon = QIcon()
#            icon.addPixmap(qpixmap_pais(c[1].lower()), QIcon.Normal, QIcon.Off)
            self.addItem(  (c[0]),  c[1])
        self.setCurrentIndex(self.findText(config.localzone))
