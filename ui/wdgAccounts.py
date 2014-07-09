from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Ui_wdgAccounts import *
from frmTransfer import *
from frmAccountsReport import *

class wdgAccounts(QWidget, Ui_wdgAccounts):
    def __init__(self, mem,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        self.tblAccounts.settings("wdgAccounts",  self.mem)
        self.cuentas=self.mem.data.cuentas_active
        self.selAccount=None
        self.load_table()

    def load_table(self):
        """Función que carga la tabla de cuentas"""
        self.cuentas.sort()
        self.tblAccounts.setRowCount(len(self.cuentas.arr));
        sumsaldos=0
        for i, c in enumerate(self.cuentas.arr):
            self.tblAccounts.setItem(i, 0, QTableWidgetItem((c.name)))
            self.tblAccounts.setItem(i, 1, QTableWidgetItem((c.eb.name)))
            self.tblAccounts.setItem(i, 2, QTableWidgetItem((c.numero)))
            self.tblAccounts.setItem(i, 3, c.currency.qtablewidgetitem(c.balance))
            sumsaldos=sumsaldos+c.balance  
        self.lblTotal.setText(self.tr("Accounts balance: {0}".format(self.mem.localcurrency.string(sumsaldos))))
        self.tblAccounts.clearSelection()
        
    @QtCore.pyqtSlot() 
    def on_actionAccountReport_activated(self):
        w=frmAccountsReport(self.mem,   self.selAccount, self)
        w.exec_()
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())
        self.load_table()
        
    @QtCore.pyqtSlot() 
    def on_actionAccountAdd_activated(self):
        w=frmAccountsReport(self.mem, None)
        w.exec_()
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())
        self.load_table()
      
    @QtCore.pyqtSlot() 
    def on_actionAccountDelete_activated(self):
        if self.selAccount.eb.qmessagebox_inactive() or self.selAccount.qmessagebox_inactive():
            return
        cur = self.mem.con.cursor()
        if self.selAccount.es_borrable(cur)==False:
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.trUtf8("This account has associated investments, credit cards or operations. It can't be deleted"))
            m.exec_()
        else:
            self.selAccount.borrar(cur)
            self.mem.con.commit()
            self.mem.data.cuentas_active.arr.remove(self.selAccount)
            self.cuentas.arr.remove(self.selAccount)
        cur.close()
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())
        self.load_table()
        
    def on_chkInactivas_stateChanged(self, state):
        if state==Qt.Unchecked:
            self.cuentas=self.mem.data.cuentas_active
        else:
            self.mem.data.load_inactives()
            self.cuentas=self.mem.data.cuentas_inactive
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
            self.actionActive.setChecked(self.selAccount.activa)
        
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

        
    @QtCore.pyqtSlot() 
    def on_actionActive_activated(self):
        if self.selAccount.eb.qmessagebox_inactive()==True:
            return
        
        self.mem.data.load_inactives()#Debe tenerlas para borrarla luego
        self.selAccount.activa=self.chkInactivas.isChecked()
        self.selAccount.save()
        self.mem.con.commit()     
        #Recoloca en los Setcuentas
        if self.selAccount.activa==True:#Está todavía en inactivas
            self.mem.data.cuentas_active.arr.append(self.selAccount)
            self.mem.data.cuentas_inactive.arr.remove(self.selAccount)
        else:#Está todavía en activas
            self.mem.data.cuentas_active.arr.remove(self.selAccount)
            self.mem.data.cuentas_inactive.arr.append(self.selAccount)    
        self.load_table()

    @QtCore.pyqtSlot()  
    def on_actionTransfer_activated(self):
        w=frmTransfer(self.mem, self.selAccount)
        w.exec_()
        self.load_table()

    def on_tblAccounts_itemSelectionChanged(self):
        self.selAccount=None
        for i in self.tblAccounts.selectedItems():#itera por cada item no row.
            if i.column()==0:
                self.selAccount=self.cuentas.arr[i.row()]
                break
        print (self.selAccount)
