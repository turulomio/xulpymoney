from PyQt5.QtWidgets import QDialog
from xulpymoney.ui.Ui_frmHelp import Ui_frmHelp

class frmHelp(QDialog, Ui_frmHelp):
    def __init__(self,mem, parent = None, name = None, modal = False):
        QDialog.__init__(self, parent)
        self.mem=mem
        self.setupUi(self)
        self.showMaximized()
