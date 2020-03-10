from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QMenu, QWidget
from xulpymoney.ui.Ui_wdgAccounts import Ui_wdgAccounts
from xulpymoney.ui.frmTransfer import frmTransfer
from xulpymoney.ui.frmAccountsReport import frmAccountsReport
from xulpymoney.libxulpymoneyfunctions import qmessagebox

class wdgAccounts(QWidget, Ui_wdgAccounts):
    def __init__(self, mem,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        self.mqtwAccounts.settings(self.mem.settings, "wdgAccounts", "mqtwAccounts")
        self.mqtwAccounts.table.cellDoubleClicked.connect(self.on_mqtwAccounts_cellDoubleClicked)
        self.mqtwAccounts.table.customContextMenuRequested.connect(self.on_mqtwAccounts_customContextMenuRequested)
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())

    @pyqtSlot() 
    def on_actionAccountReport_triggered(self):
        f=frmAccountsReport(self.mem, self.accounts.selected)
        f.exec_()
        self.update()
        
    @pyqtSlot() 
    def on_actionAccountAdd_triggered(self):
        f=frmAccountsReport(self.mem, None)
        f.exec_()
        self.update()
      
    @pyqtSlot() 
    def on_actionAccountDelete_triggered(self):
        if self.accounts.selected.eb.qmessagebox_inactive() or self.accounts.selected.qmessagebox_inactive():
            return
        cur = self.mem.con.cursor()
        if self.accounts.selected.is_deletable()==False:
            qmessagebox(self.tr("This account has associated investments, credit cards or operations. It can't be deleted"))
        else:
            self.accounts.selected.borrar(cur)
            self.mem.con.commit()
            #Only can't be deleted an active account, so I remove from active set
            self.mem.data.accounts.remove(self.accounts.selected)
        cur.close()
        self.update()
        
    def on_chkInactivas_stateChanged(self, state):
        if state==Qt.Unchecked:
            self.accounts=self.mem.data.accounts_active()
        else:
            self.accounts=self.mem.data.accounts_inactive()
        self.update()
        

    def on_mqtwAccounts_customContextMenuRequested(self,  pos):
        if self.accounts.selected==None:
            self.actionAccountDelete.setEnabled(False)
            self.actionAccountReport.setEnabled(False)
            self.actionActive.setEnabled(False)
            self.actionAccountReport.setEnabled(False)
        else:
            self.actionAccountDelete.setEnabled(True)
            self.actionAccountReport.setEnabled(True)
            self.actionActive.setEnabled(True)
            self.actionAccountReport.setEnabled(True)
            self.actionActive.setChecked(self.accounts.selected.active)
        
        menu=QMenu()
        menu.addAction(self.actionAccountAdd)
        menu.addAction(self.actionAccountDelete)
        menu.addSeparator()
        menu.addAction(self.actionActive)
        menu.addSeparator()
        menu.addAction(self.actionTransfer)
        menu.addSeparator()
        menu.addAction(self.actionAccountReport)
        menu.addSeparator()
        menu.addMenu(self.mqtwAccounts.qmenu())
        menu.exec_(self.mqtwAccounts.table.mapToGlobal(pos))

    @pyqtSlot() 
    def on_actionActive_triggered(self):
        if self.accounts.selected.eb.qmessagebox_inactive()==True:
            return
        
         #Debe tenerlas para borrarla luego
        self.accounts.selected.active=self.chkInactivas.isChecked()
        self.accounts.selected.save()
        self.mem.con.commit()
        self.update()

    @pyqtSlot()  
    def on_actionTransfer_triggered(self):
        f=frmTransfer(self.mem, self.accounts.selected)
        f.exec_()
        self.update()
        
    def on_mqtwAccounts_cellDoubleClicked(self, row,  column):
        self.on_actionAccountReport_triggered()

    ## Updates table
    def update(self):
        self.accounts.mqtw(self.mqtwAccounts)
        self.mqtwAccounts.setOrderBy(0, False)
        self.lblTotal.setText(self.tr("Accounts balance: {0}".format(self.accounts.balance())))
