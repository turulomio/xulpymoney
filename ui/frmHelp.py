from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Ui_frmHelp import *

class frmHelp(QDialog, Ui_frmHelp):
    def __init__(self,mem, parent = None, name = None, modal = False):
        QDialog.__init__(self, parent)
        self.mem=mem
        self.setupUi(self)
        s=(self.trUtf8("<h1>User manual</h1>") +
        self.trUtf8("<h2>User interface</h2>") +
        self.trUtf8("Xulpymoney uses a lot of tables, so they have an improved user interface.") + " " +
        self.trUtf8("If you move the mouse wheel, the table resizes column to allow view all fields.") + " " +
        self.trUtf8("If you double click in a table, the table is resized to minimum column size.") + " " +
        
        self.trUtf8("<h2>MyStocks</h2>") +
        self.trUtf8("Products are permanent, so they can't be deleted.") + " " +
        
        
        self.trUtf8("<h2>Xulpymoney</h2>")
        
        
        )
        
        self.browser.setHtml(s)

