from PyQt4.QtCore import *
from PyQt4.QtGui import *
from libxulpymoney import *

from Ui_frmSplit import *

class frmSplit(QDialog, Ui_frmSplit):
    def __init__(self, mem, product,  parent = None, name = None, modal = False):
        """
        Constructor
        
        @param parent The parent widget of this dialog. (QWidget)
        @param name The name of this dialog. (QString)
        @param modal Flag indicating a modal dialog. (boolean)
        """
        QDialog.__init__(self, parent)
        if name:
            self.setObjectName(name)
        self.mem=mem
        self.product=product
        self.mem.data.load_inactives()
        self.setModal(True)
        self.setupUi(self)
        
        self.all=SetQuotesAllIntradays(self.mem)
        self.all.load_from_db(self.product)
        
        self.wdgDtStart.show_microseconds(False)
        self.wdgDtEnd.show_microseconds(False)
        self.wdgDtStart.grp.setTitle(self.tr("Select the day and time of start"))
        self.wdgDtEnd.grp.setTitle(self.tr("Select the day and time of end"))
        self.wdgDtStart.set(self.mem, self.all.first_quote().datetime, self.mem.localzone)
        self.wdgDtEnd.set(self.mem, datetime.datetime.now(), self.mem.localzone)
        QObject.connect(self.wdgDtStart, SIGNAL("changed"), self.on_wdgDtStart_changed)   
        QObject.connect(self.wdgDtEnd, SIGNAL("changed"), self.on_wdgDtEnd_changed)   
        self.split=None
        self.generateExample()
        
        
    def generateExample(self):
        print("New split")
        try:
            self.split=Split(self.mem, self.product, self.txtInitial.decimal(), self.txtFinal.decimal(), self.wdgDtStart.datetime(), self.wdgDtEnd.datetime())
            self.lblExample.setText(self.trUtf8("If you have 1000 shares of 10 € of price, you will have {0:.6f} shares of {1:.6f} € of price after the {2}".format(self.split.convertShares(1000),self.split.convertPrices(10),  self.split.type())))
            self.buttonbox.button(QDialogButtonBox.Ok).setEnabled(True)
        except:
            self.lblExample.setText("")
            self.buttonbox.button(QDialogButtonBox.Ok).setEnabled(False)
        

    def on_wdgDtEnd_changed(self):
        self.generateExample()
        
    def on_wdgDtStart_changed(self):
        self.generateExample()

    def on_txtInitial_textChanged(self):
        self.generateExample()

    def on_txtFinal_textChanged(self):
        self.generateExample()
        
    @pyqtSignature("")
    def on_buttonbox_accepted(self):
        self.split.makeSplit()
        self.accept()#No haría falta pero para recordar que hay buttonbox
        
    @pyqtSignature("")
    def on_buttonbox_rejected(self):
        del self.split
        self.reject()#No haría falta pero para recordar que hay buttonbox
    
