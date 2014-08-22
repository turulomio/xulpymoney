from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Ui_frmHelp import *

class frmHelp(QDialog, Ui_frmHelp):
    def __init__(self,mem, parent = None, name = None, modal = False):
        QDialog.__init__(self, parent)
        self.mem=mem
        self.setupUi(self)
