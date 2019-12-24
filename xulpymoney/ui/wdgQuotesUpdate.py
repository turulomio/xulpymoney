from PyQt5.QtWidgets import QWidget,  QApplication, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from xulpymoney.ui.Ui_wdgQuotesUpdate import Ui_wdgQuotesUpdate
from xulpymoney.objects.product import ProductUpdate

class wdgQuotesUpdate(QWidget, Ui_wdgQuotesUpdate):
    def __init__(self, mem,  parent = None, name = None):
        QWidget.__init__(self,  parent)
        self.setupUi(self)
        self.mem=mem
        self.parent=parent
        self.update=ProductUpdate(self.mem)
        self.index=0
        self.wdgquotessaveresult.hide()
        self.txtCR2Q.hide()

    def run(self):
        self.mem.frmMain.setEnabled(False)
        self.mem.frmMain.repaint()
        QApplication.setOverrideCursor(Qt.WaitCursor)
        QApplication.processEvents()
        ##### PROCESS #####
        self.quotes=self.update.run()
        result=self.quotes.save()
        self.mem.con.commit()
        self.txtCR2Q.append(self.update.readResults())

        #Adds txtCR2Q to wdgQuotesSaveResult tab
        self.tabTXT = QWidget()
        self.horizontalLayout_31 = QHBoxLayout(self.tabTXT)
        self.horizontalLayout_31.addWidget(self.txtCR2Q)
        self.wdgquotessaveresult.tab.addTab(self.tabTXT, QIcon(":/xulpymoney/document-edit.png"), self.tr("Command output"))

        #Shows results
        self.wdgquotessaveresult.display(self.mem, *result)
        #Reloads changed data
        self.quotes.change_products_status_after_save(result[0], result[2], 1, downgrade_to=0, progress=True)
            
        self.wdgquotessaveresult.show()
        self.txtCR2Q.show()
        self.cmdUsed.hide()
        self.cmdAll.hide()

        #Restores
        self.mem.frmMain.setEnabled(True)
        QApplication.restoreOverrideCursor()

    def on_cmdUsed_released(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.update.setGlobalCommands(all=False)
        self.run()
        QApplication.restoreOverrideCursor()

    def on_cmdAll_released(self):        
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.update.setGlobalCommands(all=True)
        self.run()
        QApplication.restoreOverrideCursor()

