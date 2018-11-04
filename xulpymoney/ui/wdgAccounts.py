from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QMenu, QTableWidgetItem, QWidget
from xulpymoney.ui.Ui_wdgAccounts import Ui_wdgAccounts
from xulpymoney.ui.frmTransfer import frmTransfer
from xulpymoney.ui.frmAccountsReport import frmAccountsReport
from xulpymoney.libxulpymoney import Money
from xulpymoney.libxulpymoneyfunctions import qmessagebox

class wdgAccounts(QWidget, Ui_wdgAccounts):
    def __init__(self, mem,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        self.tblAccounts.settings(self.mem, "wdgAccounts")
        self.accounts=self.mem.data.accounts_active()
        self.selAccount=None
        self.child=None#Used to access childs in automate unittests
        self.load_table()

    def load_table(self):
        """Función que carga la tabla de cuentas"""
        self.accounts.order_by_name()
        self.tblAccounts.applySettings()
        self.tblAccounts.setRowCount(self.accounts.length());
        sumsaldos=Money(self.mem, 0, self.mem.localcurrency)
        for i, c in enumerate(self.accounts.arr):
            self.tblAccounts.setItem(i, 0, QTableWidgetItem(c.name))
            self.tblAccounts.setItem(i, 1, QTableWidgetItem(c.eb.name))
            self.tblAccounts.setItem(i, 2, QTableWidgetItem(c.numero))
            balance=c.balance()
            self.tblAccounts.setItem(i, 3, balance.local().qtablewidgetitem())
            sumsaldos=sumsaldos+balance.local()
        self.lblTotal.setText(self.tr("Accounts balance: {0}".format(sumsaldos)))
        self.tblAccounts.clearSelection()
        
    @pyqtSlot() 
    def on_actionAccountReport_triggered(self):
        self.child=self.child=frmAccountsReport(self.mem,   self.selAccount, self)
        self.child.exec_()
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())
        
    @pyqtSlot() 
    def on_actionAccountAdd_triggered(self):
        self.child=frmAccountsReport(self.mem, None)
        self.child.exec_()
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())
      
    @pyqtSlot() 
    def on_actionAccountDelete_triggered(self):
        if self.selAccount.eb.qmessagebox_inactive() or self.selAccount.qmessagebox_inactive():
            return
        cur = self.mem.con.cursor()
        if self.selAccount.es_borrable()==False:
            qmessagebox(self.tr("This account has associated investments, credit cards or operations. It can't be deleted"))
        else:
            self.selAccount.borrar(cur)
            self.mem.con.commit()
            #Only can't be deleted an active account, so I remove from active set
            self.mem.data.accounts.remove(self.selAccount)
        cur.close()
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())
        self.load_table()
        
    def on_chkInactivas_stateChanged(self, state):
        if state==Qt.Unchecked:
            self.accounts=self.mem.data.accounts_active()
        else:
             
            self.accounts=self.mem.data.accounts_inactive()
        self.load_table()
        

    def on_tblAccounts_customContextMenuRequested(self,  pos):
        if self.selAccount==None:
            self.actionAccountDelete.setEnabled(False)
            self.actionAccountReport.setEnabled(False)
            self.actionActive.setEnabled(False)
            self.actionAccountReport.setEnabled(False)
        else:
            self.actionAccountDelete.setEnabled(True)
            self.actionAccountReport.setEnabled(True)
            self.actionActive.setEnabled(True)
            self.actionAccountReport.setEnabled(True)
            self.actionActive.setChecked(self.selAccount.active)
        
        menu=QMenu()
        menu.addAction(self.actionAccountAdd)
        menu.addAction(self.actionAccountDelete)
        menu.addSeparator()
        menu.addAction(self.actionActive)
        menu.addSeparator()
        menu.addAction(self.actionTransfer)
        menu.addSeparator()
        menu.addAction(self.actionAccountReport)
        menu.exec_(self.tblAccounts.mapToGlobal(pos))

        
    @pyqtSlot() 
    def on_actionActive_triggered(self):
        if self.selAccount.eb.qmessagebox_inactive()==True:
            return
        
         #Debe tenerlas para borrarla luego
        self.selAccount.active=self.chkInactivas.isChecked()
        self.selAccount.save()
        self.mem.con.commit()     
        #Recoloca en los Setcuentas
#        if self.selAccount.active==True:#Está todavía en inactivas
#            self.mem.data.accounts_active().append(self.selAccount)
#            self.mem.data.accounts_inactive().remove(self.selAccount)
#        else:#Está todavía en activas
#            self.mem.data.accounts_active().remove(self.selAccount)
#            self.mem.data.accounts_inactive().append(self.selAccount)    
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())
        self.load_table()

    @pyqtSlot()  
    def on_actionTransfer_triggered(self):
        self.child=frmTransfer(self.mem, self.selAccount)
        self.child.exec_()
        self.load_table()
        
    def on_tblAccounts_cellDoubleClicked(self, row,  column):
        self.on_actionAccountReport_triggered()
        
    def on_tblAccounts_itemSelectionChanged(self):
        self.selAccount=None
        for i in self.tblAccounts.selectedItems():#itera por cada item no row.
            if i.column()==0:
                self.selAccount=self.accounts.arr[i.row()]
                break
        print (self.selAccount)
