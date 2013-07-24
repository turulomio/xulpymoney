from PyQt4.QtCore import *
from PyQt4.QtGui import *
from libxulpymoney import *
import static

class QComboBoxCountry(QComboBox):
    def __init__(self, parent=None):
        QComboBox.__init__(self, parent)
        arr=[]
        for k, v in static.Countries.items():
            arr.append([v, k])
        arr=sorted(arr, key=lambda row: row[0],  reverse=False)             
        for c in arr:
            icon = QIcon()
            icon.addPixmap(qpixmap_pais(c[1]), QIcon.Normal, QIcon.Off)
            self.addItem(icon,  (c[0]),  c[1])
