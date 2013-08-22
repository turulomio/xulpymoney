from PyQt4.QtCore import *
from PyQt4.QtGui import *
from libxulpymoney import *

from Ui_frmSplit import *

class frmSplit(QDialog, Ui_frmSplit):
    def __init__(self, cfg,  parent = None, name = None, modal = False):
        """
        Constructor
        
        @param parent The parent widget of this dialog. (QWidget)
        @param name The name of this dialog. (QString)
        @param modal Flag indicating a modal dialog. (boolean)
        """
        self.cfg=cfg
        QDialog.__init__(self, parent)
        if name:
            self.setObjectName(name)
        self.setModal(True)
        self.setupUi(self)
        self.split=Split(self.cfg, self.txtInitial.decimal(), self.txtFinal.decimal())
        self.generateExample()
        
        
    def generateExample(self):
        try:
            self.split.initial=self.txtInitial.decimal()
            self.split.final=self.txtFinal.decimal()
            self.lblExample.setText(self.trUtf8("If you have 1000 shares of 10 € of price, you will have {0:.6f} shares of {1:.6f} € of price after the {2}".format(self.split.convertShares(1000),self.split.convertPrices(10),  self.split.type())))
            self.buttonbox.button(QDialogButtonBox.Ok).setEnabled(True)
        except:
            self.lblExample.setText("")
            self.buttonbox.button(QDialogButtonBox.Ok).setEnabled(False)
        

    def on_txtInitial_textChanged(self):
        self.generateExample()

    def on_txtFinal_textChanged(self):
        self.generateExample()
        
    @pyqtSignature("")
    def on_buttonbox_accepted(self):
        self.accept()#No har´ia falta pero para recordar que hay buttonbox
    @pyqtSignature("")
    def on_buttonbox_rejected(self):
        del self.split
        self.reject()#No har´ia falta pero para recordar que hay buttonbox
    
