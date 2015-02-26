from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from Ui_frmHelp import *

class frmHelp(QDialog, Ui_frmHelp):
    def __init__(self,mem, parent = None, name = None, modal = False):
        QDialog.__init__(self, parent)
        self.mem=mem
        self.setupUi(self)
        self.showMaximized()
