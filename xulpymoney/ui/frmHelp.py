from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Ui_frmHelp import *

class frmHelp(QDialog, Ui_frmHelp):
    def __init__(self,mem, parent = None, name = None, modal = False):
        QDialog.__init__(self, parent)
        self.mem=mem
        self.setupUi(self)
        s=(self.trUtf8("<h1>User manual</h1>") +
        self.trUtf8("<h2>Myquotes</h2>") +
        self.trUtf8("<h2>Xulpymoney</h2>")
        )
        
        self.browser.setHtml(s)

