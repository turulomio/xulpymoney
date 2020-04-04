from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget, QCheckBox, QDialogButtonBox
from os import remove,  path
from xulpymoney.ui.myqwidgets import qmessagebox
from xulpymoney.ui.Ui_wdgQuotesSaveResult import Ui_wdgQuotesSaveResult
from xulpymoney.ui.myqdialog import MyModalQDialog

## Shows a quotes manager save result, it doesn't commit results
class wdgQuotesSaveResult(QWidget, Ui_wdgQuotesSaveResult):
    def __init__(self, parent = None):
        QWidget.__init__(self,  parent)
        self.setupUi(self)
        self.parent=parent
        self.tab.setCurrentIndex(0)

    ## Load information in widget
    def display(self, mem, added, ignored, updated, errors):
        self.mem=mem
        self.mqtwAdded.setSettings(self.mem.settings, "wdgQuotesSaveResult", "mqtwAdded") 
        self.mqtwIgnored.setSettings(self.mem.settings, "wdgQuotesSaveResult", "mqtwIgnored") 
        self.mqtwUpdated.setSettings(self.mem.settings, "wdgQuotesSaveResult", "mqtwUpdated") 
        self.mqtwErrors.setSettings(self.mem.settings, "wdgQuotesSaveResult", "mqtwErrors") 
        self.tab.setTabText(0, self.tr("Added") + " ({})".format(added.length()))
        self.tab.setTabText(1, self.tr("Updated") + " ({})".format(updated.length()))
        self.tab.setTabText(2, self.tr("Ignored") + " ({})".format(ignored.length()))
        self.tab.setTabText(3, self.tr("Errors") + " ({})".format(errors.length()))
        added.myqtablewidget(self.mqtwAdded)
        ignored.myqtablewidget(self.mqtwIgnored)
        updated.myqtablewidget(self.mqtwUpdated)
        errors.myqtablewidget(self.mqtwErrors)
        for mq in [self.mqtwAdded, self.mqtwIgnored, self.mqtwUpdated, self.mqtwErrors]:
            mq.setOrderBy(1, False)
            mq.setGenericContextMenu()

## Shows a quotes manager save result
## If widget is accepted it buttonbox is accepted it commits con, else rollback
class frmQuotesSaveResult(MyModalQDialog):
    def __init__(self, parent=None):
        MyModalQDialog.__init__(self, parent=None)
        self._fileToDelete=None
        self.wdg=wdgQuotesSaveResult(self)               
        self.setWindowTitle(self.tr("Report after saving quotes"))
        
        self.chkDeleteFile = QCheckBox(self)
        self.chkDeleteFile.setChecked(True)
        self.bb = QDialogButtonBox(self)
        self.bb.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.bb.setCenterButtons(True)
        self.bb.accepted.connect(self.on_bb_accepted)
        self.bb.rejected.connect(self.on_bb_rejected)

    ## Sets the filename to delete before clossing
    def setFileToDelete(self, filename):
        self._fileToDelete=filename
        self.chkDeleteFile.setText(self.tr("Delete '{}' after accepting this dialog".format(filename)))

    def fileToDelete(self):
        return self._fileToDelete
        
    @pyqtSlot()
    def on_bb_accepted(self):
        if self.chkDeleteFile.isChecked()==True:
            remove(self.fileToDelete())
            if path.exists(self.fileToDelete())==True:
                qmessagebox(self.tr("There was an error deleting file"))
        self.mem.con.commit()
        self.accept()

    @pyqtSlot()
    def on_bb_rejected(self):
        self.mem.con.rollback()
        self.reject()#No haría falta pero para recordar que hay buttonbox
    
    def setQuotesManagers(self, added, ignored, updated, errors):
        self.mem=added.mem
        self.setSettings(self.mem.settings, "frmQuotesSaveResult", "myqdialog")
        self.setWidgets(self.wdg, self.chkDeleteFile, self.bb)
        self.wdg.display(self.mem, added, ignored, updated, errors)

    def exec_(self):
        if self.fileToDelete()==None:
            self.chkDeleteFile.hide()        
        MyModalQDialog.exec_(self)
