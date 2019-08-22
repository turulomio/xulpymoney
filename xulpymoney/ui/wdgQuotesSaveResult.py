from PyQt5.QtWidgets import QWidget
from xulpymoney.ui.Ui_wdgQuotesSaveResult import Ui_wdgQuotesSaveResult
from xulpymoney.ui.myqdialog import MyQDialog

class wdgQuotesSaveResult(QWidget, Ui_wdgQuotesSaveResult):
    def __init__(self, parent = None):
        QWidget.__init__(self,  parent)
        self.setupUi(self)
        self.parent=parent
        self.tab.setCurrentIndex(0)

    ## Load information in widget
    def display(self, mem, added, ignored, updated, errors):
        self.mem=mem
        self.tblAdded.settings(self.mem, "wdgQuotesSaveResult") 
        self.tblIgnored.settings(self.mem, "wdgQuotesSaveResult") 
        self.tblUpdated.settings(self.mem, "wdgQuotesSaveResult") 
        self.tblErrors.settings(self.mem, "wdgQuotesSaveResult") 
        self.tab.setTabText(0, self.tr("Added") + " ({})".format(added.length()))
        self.tab.setTabText(1, self.tr("Updated") + " ({})".format(updated.length()))
        self.tab.setTabText(2, self.tr("Ignored") + " ({})".format(ignored.length()))
        self.tab.setTabText(3, self.tr("Errors") + " ({})".format(errors.length()))
        added.myqtablewidget(self.tblAdded)
        ignored.myqtablewidget(self.tblIgnored)
        updated.myqtablewidget(self.tblUpdated)
        errors.myqtablewidget(self.tblErrors)

class frmQuotesSaveResult(MyQDialog):
    def __init__(self, parent=None):
        MyQDialog.__init__(self, parent=None)
    
    ## Includes an exec_
    def settings_and_exec_(self, mem, added, ignored, updated, errors):
        self.mem=mem
        self.wdg=wdgQuotesSaveResult(self)        
        self.wdg.display(self.mem, added, ignored, updated, errors)
        MyQDialog.settings_and_exec_(self, self.mem, "frmQuotesSaveResult/qdialog", [self.wdg, ], self.tr("Report after saving quotes"))
