from PyQt4.QtCore import *
from PyQt4.QtGui import *

class QComboBoxPCI(QComboBox):
    def __init__(self,   parent=None):
        QComboBox.__init__(self, parent)
        self.cfg=None
        self.addItem("Call", "c")
        self.addItem("Inline", "i")
        self.addItem("Put", "p")

