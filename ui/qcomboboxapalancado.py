from PyQt4.QtCore import *
from PyQt4.QtGui import *

class QComboBoxApalancado(QComboBox):
    def __init__(self, parent=None):
        QComboBox.__init__(self, parent)
        
        for id,  apa in Apalancamiento.items():
            self.addItem(apa, int(id))
