from PyQt5.QtCore import *
from PyQt5.QtGui import *
from libxulpymoney import *
from Ui_wdgOrdersAdd import *

class wdgOrdersAdd(QWidget, Ui_wdgOrdersAdd):
    def __init__(self, mem,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem

