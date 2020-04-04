from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QMenu, QWidget, QInputDialog, QLineEdit
from PyQt5.QtGui import QIcon
from xulpymoney.objects.bank import Bank
from xulpymoney.objects.account import AccountManager
from xulpymoney.objects.investment import InvestmentManager
from xulpymoney.ui.myqwidgets import qmessagebox
from xulpymoney.ui.myqcharts import VCPie
from xulpymoney.ui.myqdialog import MyModalQDialog
from xulpymoney.ui.frmAccountsReport import frmAccountsReport
from xulpymoney.ui.frmInvestmentReport import frmInvestmentReport
from xulpymoney.ui.Ui_wdgBanks import Ui_wdgBanks

class wdgBanks(QWidget, Ui_wdgBanks):
    def __init__(self, mem,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem

        self.banks=None#Set in on_chkActives_stateChanged
        self.investments=InvestmentManager(self.mem) #Set
        self.accounts=AccountManager(self.mem)#Set

        self.mqtwBanks.setSettings(self.mem.settings, "wdgBanks", "mqtwBanks")
        self.mqtwBanks.table.customContextMenuRequested.connect(self.on_mqtwBanks_customContextMenuRequested)
        self.mqtwBanks.tableSelectionChanged.connect(self.on_mqtwBanks_tableSelectionChanged)
        self.mqtwAccounts.setSettings(self.mem.settings, "wdgBanks", "mqtwAccounts")
        self.mqtwAccounts.table.customContextMenuRequested.connect(self.on_mqtwAccounts_customContextMenuRequested)
        self.mqtwInvestments.setSettings(self.mem.settings, "wdgBanks", "mqtwInvestments")
        self.mqtwInvestments.table.customContextMenuRequested.connect(self.on_mqtwInvestments_customContextMenuRequested)

        self.on_chkActives_stateChanged(Qt.Checked)#Carga eb


    def on_chkActives_stateChanged(self, state):
        self.banks=self.mem.data.banks_set(self.chkActives.isChecked())
        self.banks.order_by_name()
        self.banks.mqtw(self.mqtwBanks)
        self.mqtwBanks.setOrderBy(0, False)
        self.mqtwBanks.table.clearSelection()   
        self.mqtwAccounts.table.setRowCount(0)
        self.mqtwAccounts.table.clearContents()
        self.mqtwInvestments.table.setRowCount(0);
        self.mqtwInvestments.table.clearContents()

    @pyqtSlot()
    def on_mqtwBanks_tableSelectionChanged(self):
        self.investments.clean()
        self.accounts.clean()

        if self.mqtwBanks.selected==None: #mqtwBanks manages selection, not self.banks due to it's a mqtDataObjectos
            self.mqtwAccounts.table.setRowCount(0)
            self.mqtwAccounts.table.clearContents()
            self.mqtwInvestments.table.setRowCount(0);
            self.mqtwInvestments.table.clearContents()
            return

        for i in self.mem.data.investments.arr:
            if i.account.bank.id==self.mqtwBanks.selected.id:
                if (self.chkActives.isChecked() and i.active==True) or (self.chkActives.isChecked()==False):
                    self.investments.append(i)

        for v in self.mem.data.accounts.arr:
            if v.bank.id==self.mqtwBanks.selected.id:
                if (self.chkActives.isChecked() and v.active==True) or (self.chkActives.isChecked()==False):
                    self.accounts.append(v)

        self.accounts.order_by_name()
        self.investments.order_by_name()
        self.accounts.mqtw_active(self.mqtwAccounts)
        self.mqtwAccounts.setOrderBy(0, False)
        self.investments.mqtw_active(self.mqtwInvestments)
        self.mqtwInvestments.setOrderBy(0, False)

    def on_mqtwBanks_customContextMenuRequested(self,  pos):
        if self.mqtwBanks.selected==None:
            self.actionBankDelete.setEnabled(False)
            self.actionBankEdit.setEnabled(False)
            self.actionActive.setEnabled(False)
        else:
            self.actionBankDelete.setEnabled(True)
            self.actionBankEdit.setEnabled(True)
            self.actionActive.setEnabled(True)
            self.actionActive.setChecked(self.mqtwBanks.selected.active)

        menu=QMenu()
        menu.addAction(self.actionBankAdd)
        menu.addAction(self.actionBankEdit)
        menu.addAction(self.actionBankDelete)
        menu.addSeparator()
        menu.addAction(self.actionActive)
        menu.addSeparator()
        menu.addMenu(self.mqtwBanks.qmenu())
        menu.exec_(self.mqtwBanks.table.mapToGlobal(pos))

    @pyqtSlot() 
    def on_actionAccountReport_triggered(self):
        w=frmAccountsReport(self.mem, self.accounts.selected)
        w.exec_()
        self.accounts.mqtw_active(self.mqtwAccounts)

    @pyqtSlot() 
    def on_actionInvestmentReport_triggered(self):
        w=frmInvestmentReport(self.mem,   self.investments.selected)
        w.exec_()
        self.investments.mqtw_active(self.mqtwInvestments)

    ## Displays a pie graph of banks
    @pyqtSlot()
    def on_cmdGraph_released(self):
        d=MyModalQDialog(self)     
        d.setWindowIcon(QIcon(":/xulpymoney/bank.png"))
        d.setSettings(self.mem.settings, "wdgBanks", "mqdGraph")
        d.setWindowTitle(self.tr("Banks graph"))
        view=VCPie(d)
        view.pie.setTitle(self.tr("Banks graph"))
        view.setSettings(self.mem.settings, "wdgBanks", "pie")
        for bank in self.mem.data.banks_active().arr:
            view.pie.appendData(bank.name, bank.balance())
        view.display()
        d.setWidgets(view)
        d.exec_()

    def on_mqtwAccounts_customContextMenuRequested(self,  pos):
        if self.accounts.selected==None:
            self.actionAccountReport.setEnabled(False)
        else:
            self.actionAccountReport.setEnabled(True)
        menu=QMenu()
        menu.addAction(self.actionAccountReport)
        menu.addSeparator()
        menu.addMenu(self.mqtwAccounts.qmenu())
        menu.exec_(self.mqtwAccounts.table.mapToGlobal(pos))

    def on_mqtwInvestments_customContextMenuRequested(self,  pos):
        if self.investments.selected==None:
            self.actionInvestmentReport.setEnabled(False)
        else:
            self.actionInvestmentReport.setEnabled(True)
        menu=QMenu()
        menu.addAction(self.actionInvestmentReport)       
        menu.addSeparator()
        menu.addMenu(self.mqtwInvestments.qmenu()) 
        menu.exec_(self.mqtwInvestments.table.mapToGlobal(pos))

    @pyqtSlot()  
    def on_actionBankDelete_triggered(self):
        if self.mqtwBanks.selected.qmessagebox_inactive():
            return        
        if self.mqtwBanks.selected.is_deletable()==False:
            qmessagebox(self.tr("This bank has dependent accounts and it can't be deleted"))
        else:
            self.mem.data.banks.delete(self.mqtwBanks.selected)
            self.mem.con.commit()  
            self.on_chkActives_stateChanged(self.chkActives.checkState())    

    @pyqtSlot()  
    def on_actionBankAdd_triggered(self):
        tipo=QInputDialog().getText(self,  "Xulpymoney",  self.tr("Add a new bank"))
        if tipo[1]==True:
            self.bank_add(tipo[0])

    def bank_add(self, bank):
        """Permits unit tests if separated"""
        eb=Bank(self.mem).init__create(bank)
        eb.save()
        self.mem.con.commit()  
        self.mem.data.banks.append(eb)
        self.on_chkActives_stateChanged(self.chkActives.checkState())


    @pyqtSlot()  
    def on_actionBankEdit_triggered(self):
        tipo=QInputDialog().getText(self,  "Xulpymoney", self.tr("Edit selected bank") , QLineEdit.Normal,   (self.mqtwBanks.selected.name))       
        if tipo[1]==True:
            self.bank_edit(tipo[0])

    def bank_edit(self, bank):
        """Permits unit tests if separated"""
        self.mqtwBanks.selected.name=bank
        self.mqtwBanks.selected.save()
        self.mem.con.commit()
        self.on_chkActives_stateChanged(self.chkActives.checkState())   

    @pyqtSlot() 
    def on_actionActive_triggered(self):
        self.mqtwBanks.selected.active=not self.mqtwBanks.selected.active
        self.mqtwBanks.selected.save()
        self.mem.con.commit()   
        self.on_chkActives_stateChanged(self.chkActives.checkState())
