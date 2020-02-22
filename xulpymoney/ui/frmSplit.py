from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog, QDialogButtonBox
from xulpymoney.objects.split import Split
import datetime

from xulpymoney.ui.Ui_frmSplit import Ui_frmSplit

class frmSplit(QDialog, Ui_frmSplit):
    def __init__(self, mem, product, split=None,  parent = None):
        """
        Constructor
        
        @param parent The parent widget of this dialog. (QWidget)
        @param name The name of this dialog. (QString)
        @param modal Flag indicating a modal dialog. (boolean)
        """
        QDialog.__init__(self, parent)
        self.mem=mem
        self.product=product
        self.split=split
         
        self.setModal(True)
        self.setupUi(self)
        
        self.wdgDT.blockSignals(True)
        self.wdgDT.setLocalzone(self.mem.localzone_name)
        self.wdgDT.show_microseconds(False)
        self.wdgDt.grp.setTitle(self.tr("Select the day and time of split"))
        
        if self.split==None:
            self.wdgDT.set(datetime.datetime.now(), self.mem.localzone_name)
            self.split=Split(self.mem)
            self.split.product=self.product
        else:
            self.split=split
            self.wdgDT.set(self.split.datetime, self.mem.localzone_name)
            self.txtInitial.setText(self.split.before)
            self.txtFinal.setText(self.split.after)
            self.txtComment.setText(self.split.comment)
        self.wdgDt.blockSignals(False)
        self.generateExample()
        
        
    def generateExample(self):
        try:
            self.split.datetime=self.wdgDt.datetime()
            self.split.after=self.txtFinal.decimal()
            self.split.before=self.txtInitial.decimal()
            self.split.comment=self.txtComment.text()
            self.lblExample.setText(self.tr("If you have 1000 shares of 10 \u20ac of price, you will have {0:.6f} shares of {1:.6f} \u20ac of price after the {2}".format(self.split.convertShares(1000),self.split.convertPrices(10),  self.split.type())))
            self.buttonbox.button(QDialogButtonBox.Ok).setEnabled(True)
        except:
            self.lblExample.setText("")
            self.buttonbox.button(QDialogButtonBox.Ok).setEnabled(False)

    def on_wdgDt_changed(self):
        self.generateExample()

    def on_txtInitial_textChanged(self):
        self.generateExample()

    def on_txtFinal_textChanged(self):
        self.generateExample()
        
    @pyqtSlot()
    def on_buttonbox_accepted(self):
        self.split.save()
        self.accept()#No haría falta pero para recordar que hay buttonbox
        
    @pyqtSlot()
    def on_buttonbox_rejected(self):
        self.reject()#No haría falta pero para recordar que hay buttonbox
    
