from PyQt5.QtCore import Qt, QSize, pyqtSlot
from PyQt5.QtWidgets import QMenu, QWidget, QTableWidgetItem, QInputDialog, QLineEdit, QDialog, QVBoxLayout
from PyQt5.QtGui import QIcon
from xulpymoney.objects.bank import Bank
from xulpymoney.objects.money import Money
from xulpymoney.objects.account import AccountManager
from xulpymoney.objects.investment import InvestmentManager
from xulpymoney.libxulpymoneyfunctions import qmessagebox
from xulpymoney.ui.myqtablewidget import wdgBool
from xulpymoney.ui.myqcharts import VCPie
from xulpymoney.ui.frmAccountsReport import frmAccountsReport
from xulpymoney.ui.frmInvestmentReport import frmInvestmentReport
from xulpymoney.ui.Ui_wdgBanks import Ui_wdgBanks

class wdgBanks(QWidget, Ui_wdgBanks):
    def __init__(self, mem,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem

        self.banks=None#Set in on_chkActives_stateChanged
        self.investments=InvestmentManager(self.mem, self.mem.data.accounts, self.mem.data.products, self.mem.data.benchmark) #Set
        self.accounts=AccountManager(self.mem, self.mem.data.banks)#Set

        self.mqtwBanks.settings(self.mem.settings, "wdgBanks", "mqtwBanks")
        self.mqtwBanks.table.customContextMenuRequested.connect(self.on_mqtwBanks_customContextMenuRequested)
        self.mqtwBanks.tableSelectionChanged.connect(self.on_mqtwBanks_tableSelectionChanged)
        self.mqtwAccounts.settings(self.mem.settings, "wdgBanks", "mqtwAccounts")
        self.mqtwAccounts.table.customContextMenuRequested.connect(self.on_mqtwAccounts_customContextMenuRequested)
        self.mqtwAccounts.table.itemSelectionChanged.connect(self.on_mqtwAccounts_itemSelectionChanged)
        self.mqtwInvestments.settings(self.mem.settings, "wdgBanks", "mqtwInvestments")
        self.mqtwInvestments.table.customContextMenuRequested.connect(self.on_mqtwInvestments_customContextMenuRequested)
        self.mqtwInvestments.table.itemSelectionChanged.connect(self.on_mqtwInvestments_itemSelectionChanged)

        self.on_chkActives_stateChanged(Qt.Checked)#Carga eb

    def load_cuentas(self):
        self.mqtwAccounts.table.setColumnCount(3)
        self.mqtwAccounts.table.setHorizontalHeaderItem(0, QTableWidgetItem(self.tr("Account" )))
        self.mqtwAccounts.table.setHorizontalHeaderItem(1, QTableWidgetItem(self.tr("Active" )))
        self.mqtwAccounts.table.setHorizontalHeaderItem(2, QTableWidgetItem(self.tr("Balance" )))
        self.accounts.order_by_name()
        self.mqtwAccounts.applySettings()
        self.mqtwAccounts.table.clearContents()
        self.mqtwAccounts.table.setRowCount(self.accounts.length()+1);
        sumsaldos=Money(self.mem, 0,  self.mem.localcurrency)
        for i,  c in enumerate(self.accounts.arr):
            self.mqtwAccounts.table.setItem(i, 0, QTableWidgetItem(c.name))
            self.mqtwAccounts.table.setCellWidget(i, 1, wdgBool(c.active))
            balance=c.balance().local()
            self.mqtwAccounts.table.setItem(i, 2, balance.qtablewidgetitem())
            sumsaldos=sumsaldos+balance
        self.mqtwAccounts.table.setItem(self.accounts.length(), 0, QTableWidgetItem(self.tr('TOTAL')))
        self.mqtwAccounts.table.setItem(self.accounts.length(), 2, sumsaldos.qtablewidgetitem())  

    def load_inversiones(self):
        self.mqtwInvestments.table.setColumnCount(3)
        self.mqtwInvestments.table.setHorizontalHeaderItem(0, QTableWidgetItem(self.tr("Investment" )))
        self.mqtwInvestments.table.setHorizontalHeaderItem(1, QTableWidgetItem(self.tr("Active" )))
        self.mqtwInvestments.table.setHorizontalHeaderItem(2, QTableWidgetItem(self.tr("Balance" )))
        self.investments.order_by_name()
        self.mqtwInvestments.applySettings()
        self.mqtwInvestments.table.clearContents()
        self.mqtwInvestments.table.setRowCount(self.investments.length()+1);
        sumsaldos=Money(self.mem,  0,  self.mem.localcurrency)
        for i, inv in enumerate(self.investments.arr):
            self.mqtwInvestments.table.setItem(i, 0, QTableWidgetItem(inv.name))
            self.mqtwInvestments.table.setCellWidget(i, 1, wdgBool(inv.active))
            balanc=inv.balance().local()
            self.mqtwInvestments.table.setItem(i, 2, balanc.qtablewidgetitem())
            sumsaldos=sumsaldos+balanc
        self.mqtwInvestments.table.setItem(self.investments.length(), 0, QTableWidgetItem(self.tr('TOTAL')))
        self.mqtwInvestments.table.setItem(self.investments.length(), 2, sumsaldos.qtablewidgetitem())

    def on_chkActives_stateChanged(self, state):
        self.banks=self.mem.data.banks_set(self.chkActives.isChecked())
        self.banks.mqtw(self.mqtwBanks)
        self.mqtwBanks.table.clearSelection()   
        self.mqtwAccounts.table.setRowCount(0)
        self.mqtwAccounts.table.clearContents()
        self.mqtwInvestments.table.setRowCount(0);
        self.mqtwInvestments.table.clearContents()

    @pyqtSlot()
    def on_mqtwBanks_tableSelectionChanged(self):
        print("AHORA")
        self.investments.clean()
        self.accounts.clean()

        if self.mqtwBanks.selected==None: #mqtwBanks manages selection, not self.banks due to it's a mqtDataObjectos
            self.mqtwAccounts.table.setRowCount(0)
            self.mqtwAccounts.table.clearContents()
            self.mqtwInvestments.table.setRowCount(0);
            self.mqtwInvestments.table.clearContents()
            return

        for i in self.mem.data.investments.arr:
            if i.account.eb.id==self.mqtwBanks.selected.id:
                if (self.chkActives.isChecked() and i.active==True) or (self.chkActives.isChecked()==False):
                    self.investments.append(i)

        for v in self.mem.data.accounts.arr:
            if v.eb.id==self.mqtwBanks.selected.id:
                if (self.chkActives.isChecked() and v.active==True) or (self.chkActives.isChecked()==False):
                    self.accounts.append(v)

        self.load_cuentas()
        self.load_inversiones()

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
        self.load_cuentas()

    @pyqtSlot() 
    def on_actionInvestmentReport_triggered(self):
        w=frmInvestmentReport(self.mem,   self.investments.selected)
        w.exec_()
        self.load_inversiones()

    def on_mqtwAccounts_itemSelectionChanged(self):
        self.accounts.selected=None
        for i in self.mqtwAccounts.table.selectedItems():#itera por cada item no row.
            if i.row()<self.accounts.length():#Necesario porque tiene fila de total
                self.accounts.selected=self.accounts.arr[i.row()]
        print ("Seleccionado: " +  str(self.accounts.selected))

    ## Displays a pie graph of banks
    @pyqtSlot()
    def on_cmdGraph_released(self):
        d=QDialog(self)     
        d.setWindowIcon(QIcon(":/xulpymoney/bank.png"))
        d.resize(self.mem.settings.value("wdgBanks/qdialog_graph", QSize(800, 600)))
        d.setWindowTitle(self.tr("Banks graph"))
        view=VCPie(d)
        view.settings(self.mem.settings, "wdgBanks", "pie")
        view.pie.clear()
        for bank in self.mem.data.banks_active().arr:
            view.pie.appendData(bank.name, bank.balance())
        view.pie.display()
        lay = QVBoxLayout(d)
        lay.addWidget(view)
        d.exec_()
        self.mem.settings.setValue("frmAccountsReport/qdialog_conceptreport", d.size())

    def on_mqtwAccounts_customContextMenuRequested(self,  pos):
        if self.accounts.selected==None:
            self.actionAccountReport.setEnabled(False)
        else:
            self.actionAccountReport.setEnabled(True)
        menu=QMenu()
        menu.addAction(self.actionAccountReport)
        menu.exec_(self.mqtwAccounts.table.mapToGlobal(pos))


    def on_mqtwInvestments_itemSelectionChanged(self):
        self.investments.selected=None
        for i in self.mqtwInvestments.table.selectedItems():#itera por cada item no row.
            if i.row()<self.investments.length():#Necesario porque tiene fila de total
                self.investments.selected=self.investments.arr[i.row()]
        print ("Seleccionado: " +  str(self.investments.selected))


    def on_mqtwInvestments_customContextMenuRequested(self,  pos):
        if self.investments.selected==None:
            self.actionInvestmentReport.setEnabled(False)
        else:
            self.actionInvestmentReport.setEnabled(True)
        menu=QMenu()
        menu.addAction(self.actionInvestmentReport)        
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
