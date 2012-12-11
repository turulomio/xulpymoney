from PyQt4.QtCore import *
from PyQt4.QtGui import *

from Ui_frmSettings import *

class frmSettings(QDialog, Ui_frmSettings):
    def __init__(self, cfg, parent = None, name = None, modal = False):
        """
        Constructor
        
        @param parent The parent widget of this dialog. (QWidget)
        @param name The name of this dialog. (QString)
        @param modal Flag indicating a modal dialog. (boolean)
        """
        QDialog.__init__(self, parent)
        if name:
            self.setObjectName(name)
        self.setModal(True)
        self.setupUi(self)
        self.cfg=cfg
        