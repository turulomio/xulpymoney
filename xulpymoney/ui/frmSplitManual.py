from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog, QDialogButtonBox
from xulpymoney.objects.quote import QuoteAllIntradayManager
from xulpymoney.objects.split import SplitManual
import datetime

from xulpymoney.ui.Ui_frmSplitManual import Ui_frmSplitManual

class frmSplitManual(QDialog, Ui_frmSplitManual):
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
         
        self.setModal(True)
        self.setupUi(self)
        
        self.all=QuoteAllIntradayManager(self.mem)
        self.all.load_from_db(self.product)
        
        self.wdgDtStart.show_microseconds(False)
        self.wdgDtEnd.show_microseconds(False)
        self.wdgDtStart.grp.setTitle(self.tr("Select the day and time of start"))
        self.wdgDtEnd.grp.setTitle(self.tr("Select the day and time of end"))
        self.wdgDtStart.set(self.all.first().open().datetime, self.mem.localzone_name)
        self.wdgDtEnd.set(datetime.datetime.now(), self.mem.localzone_name)
        self.wdgDtStart.changed.connect(self.on_wdgDtStart_changed)
        self.wdgDtEnd.changed.connect(self.on_wdgDtEnd_changed)
        self.split=None
        self.generateExample()
        
        
    def generateExample(self):
        try:
            self.split=SplitManual(self.mem, self.product, self.txtInitial.decimal(), self.txtFinal.decimal(), self.wdgDtStart.datetime(), self.wdgDtEnd.datetime())
            self.lblExample.setText(self.tr("If you have 1000 shares of 10 \u20ac of price, you will have {0:.6f} shares of {1:.6f} \u20ac of price after the {2}".format(self.split.convertShares(1000),self.split.convertPrices(10),  self.split.type())))
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
        
    @pyqtSlot()
    def on_buttonbox_accepted(self):
        self.split.makeSplit()
        self.accept()#No haría falta pero para recordar que hay buttonbox
        
    @pyqtSlot()
    def on_buttonbox_rejected(self):
        del self.split
        self.reject()#No haría falta pero para recordar que hay buttonbox
    
