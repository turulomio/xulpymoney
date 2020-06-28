from PyQt5.QtCore import Qt,  pyqtSlot
from PyQt5.QtWidgets import QMenu, QWidget
from xulpymoney.datetime_functions import days2string
from xulpymoney.ui.myqwidgets import qmessagebox
from xulpymoney.objects.assets import  Assets
from xulpymoney.objects.percentage import Percentage
from xulpymoney.objects.product import ProductUpdate
from xulpymoney.objects.quote import Quote
from xulpymoney.ui.Ui_wdgInvestments import Ui_wdgInvestments
from xulpymoney.ui.frmInvestmentReport import frmInvestmentReport
from xulpymoney.ui.frmQuotesIBM import frmQuotesIBM
from xulpymoney.ui.frmProductReport import frmProductReport

class wdgInvestments(QWidget, Ui_wdgInvestments):
    def __init__(self, mem,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        self.investments=None
        self.loadedinactive=False

        self.mqtwInvestments.setSettings(self.mem.settings, "wdgInvestments", "mqtwInvestments")#It's a mqtwObjects. Selection in mqtw, not in manager
        self.mqtwInvestments.table.cellDoubleClicked.connect(self.on_mqtwInvestments_cellDoubleClicked)
        self.mqtwInvestments.table.customContextMenuRequested.connect(self.on_mqtwInvestments_customContextMenuRequested)
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())

    ## Updates lblTotal
    def lblTotal_update(self):
        invested=self.investments.invested()
        pendiente=self.investments.pendiente()
        if invested.isZero():
            self.lblTotal.setText(self.tr("There aren't invested assets"))
        else:
            self.lblTotal.setText(self.tr("Invested assets: {0}. Current balance {7}\nPending: {1}{2} = {3} ({4} assets)\nDaily Diff: {5}. Investment average age: {6}").format(
                            invested,
                            self.investments.pendiente_positivo(),
                            self.investments.pendiente_negativo(),  
                            pendiente, 
                            Percentage(pendiente, invested),  
                            self.investments.gains_last_day(), 
                            days2string(self.investments.average_age()), 
                            self.investments.balance()
                            ))

    @pyqtSlot() 
    def on_actionActive_triggered(self):
        if self.mqtwInvestments.selected.account.bank.qmessagebox_inactive()  or self.mqtwInvestments.selected.account.qmessagebox_inactive():
            return  
    
        self.mqtwInvestments.selected.active=not self.mqtwInvestments.selected.active
        self.mqtwInvestments.selected.save()
        self.mem.con.commit()     

        self.chkInactivas.setCheckState(Qt.Unchecked)
        self.on_chkInactivas_stateChanged(Qt.Unchecked)

    @pyqtSlot() 
    def on_actionInformation_triggered(self):
        self.investments=self.mem.data.investments_active()
        self.investments.myqtablewidget_information(self.mqtwInvestments)
        self.mqtwInvestments.setOrderBy(0,  False)
        self.lblTotal_update()
        

    @pyqtSlot() 
    def on_actionInvestmentDelete_triggered(self):
        self.mqtwInvestments.selected.borrar()
        self.mem.data.investments.remove(self.mqtwInvestments.selected)
        self.mem.con.commit()
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())

    @pyqtSlot() 
    def on_actionInvestmentAdd_triggered(self):
        w=frmInvestmentReport(self.mem,   None, self)
        w.exec_()
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())
        
    @pyqtSlot() 
    def on_actionInvestmentReport_triggered(self):
        w=frmInvestmentReport(self.mem,  self.mqtwInvestments.selected, self)
        w.exec_()
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())

    @pyqtSlot() 
    def on_actionProduct_triggered(self):
        w=frmProductReport(self.mem, self.mqtwInvestments.selected.product, self.mqtwInvestments.selected, self)
        w.exec_()
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())

    @pyqtSlot() 
    def on_actionProductUpdate_triggered(self):
        update=ProductUpdate(self.mem)
        update.setCommands(self.mqtwInvestments.selected.product)
        quotes=update.run()
        quotes.save()
        self.mem.con.commit()
        quotes.print()
        
    @pyqtSlot() 
    def on_actionSameProduct_triggered(self):
        inv=self.mem.data.investments.Investment_merging_current_operations_with_same_product(self.mqtwInvestments.selected.product)
        w=frmInvestmentReport(self.mem, inv, self)
        w.exec_()
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())
                    
    @pyqtSlot() 
    def on_actionSameProductFIFO_triggered(self):
        inv=self.mem.data.investments.Investment_merging_operations_with_same_product(self.mqtwInvestments.selected.product)
        w=frmInvestmentReport(self.mem, inv, self)
        w.exec_()
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())

    @pyqtSlot() 
    def on_actionProductPrice_triggered(self):
        w=frmQuotesIBM(self.mem, self.mqtwInvestments.selected.product,None,  self)
        w.exec_()
        self.mqtwInvestments.selected.product.needStatus(1, downgrade_to=0)
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())
        
    @pyqtSlot() 
    def on_actionProductPriceLastRemove_triggered(self):
        self.mqtwInvestments.selected.product.result.basic.last.delete()
        self.mem.con.commit()
        self.mqtwInvestments.selected.product.needStatus(1, downgrade_to=0)
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())
            
    @pyqtSlot(int) 
    def on_chkInactivas_stateChanged(self, state):
        if state==Qt.Unchecked:
            self.investments=self.mem.data.investments_active()
            self.investments.myqtablewidget(self.mqtwInvestments)
            self.mqtwInvestments.setOrderBy(8,  False)
        else:
            self.investments=self.mem.data.investments_inactive()
            self.investments.myqtablewidget(self.mqtwInvestments)
            self.mqtwInvestments.setOrderBy(0, False)
        self.lblTotal_update()

    def on_mqtwInvestments_customContextMenuRequested(self,  pos):
        if self.mqtwInvestments.selected is None:
            self.actionInvestmentReport.setEnabled(False)
            self.actionInvestmentDelete.setEnabled(False)
            self.actionActive.setEnabled(False)
            self.actionProduct.setEnabled(False)
            self.actionProductPrice.setEnabled(False)
            self.actionProductPriceLastRemove.setEnabled(False)
            self.actionProductUpdate.setEnabled(False)
            self.actionSameProduct.setEnabled(False)
            self.actionSameProductFIFO.setEnabled(False)
            self.actionInformation.setEnabled(False)
        else:
            self.actionInvestmentReport.setEnabled(True)
            self.actionActive.setEnabled(True)       
            self.actionProduct.setEnabled(True)
            self.actionInformation.setEnabled(True)
            if self.mem.data.investments.numberWithSameProduct(self.mqtwInvestments.selected.product)>1:
                self.actionSameProduct.setEnabled(True)
                self.actionSameProductFIFO.setEnabled(True)
            else:
                self.actionSameProduct.setEnabled(False)
                self.actionSameProductFIFO.setEnabled(False)
            self.actionProductPrice.setEnabled(True)
            if self.mqtwInvestments.selected.is_deletable()==True:
                self.actionInvestmentDelete.setEnabled(True)
            else:
                self.actionInvestmentDelete.setEnabled(False)
                
            self.actionProductPriceLastRemove.setEnabled(True)
            self.actionProductUpdate.setEnabled(True)
                
            if self.mqtwInvestments.selected.active==True:
                self.actionActive.setText(self.tr('Deactivate investment'))
            else:
                self.actionActive.setText(self.tr('Activate investment'))
                
        menu=QMenu()
        menu.addAction(self.actionInvestmentAdd)
        menu.addAction(self.actionInvestmentDelete)   
        menu.addSeparator()   
        menu.addAction(self.actionInvestmentReport)     
        menu.addAction(self.actionProduct)
        menu.addSeparator()
        menu.addAction(self.actionSameProduct)
        menu.addAction(self.actionSameProductFIFO)   
        menu.addSeparator()
        menu.addAction(self.actionProductPrice)
        menu.addAction(self.actionProductPriceLastRemove)
        menu.addAction(self.mem.frmMain.actionQuoteImportInvestingComIntraday)
        menu.addAction(self.actionProductUpdate)
        menu.addSeparator()
        menu.addAction(self.actionActive)
        menu.addSeparator()
        menu.addAction(self.actionInformation)
        menu.addSeparator()
        menu.addMenu(self.mqtwInvestments.qmenu())
        menu.exec_(self.mqtwInvestments.table.mapToGlobal(pos))

    @pyqtSlot(int, int) 
    def on_mqtwInvestments_cellDoubleClicked(self, row, column):
        if column==8:#TPC Venta
            qmessagebox(self.tr("Shares number: {0}").format(self.mqtwInvestments.selected.shares())+"\n"+
                    self.tr("Purchase price average: {0}").format(self.mqtwInvestments.selected.op_actual.average_price().local())+"\n"+
                    self.tr("Selling point: {}").format(self.mqtwInvestments.selected.venta)+"\n"+
                    self.tr("Selling all shares you get {}").format(self.mqtwInvestments.selected.op_actual.pendiente(Quote(self.mem).init__create(self.mqtwInvestments.selected.product, self.mem.localzone.now(),  self.mqtwInvestments.selected.venta)).local())
            )  
        else:
            self.on_actionInvestmentReport_triggered()

## Class to show Zero Risk investments
class wdgInvestmentsZeroRisk(wdgInvestments):
    def __init__(self, mem, parent=None):
        wdgInvestments.__init__(self, mem, parent)
        self.lbl.setText(self.tr("Zero risk investment list"))    

    ## Updates lblTotal, overrides supper method
    def lblTotal_update(self):
        investments=self.investments.balance()
        accounts=self.mem.data.accounts_active().balance()
        total=Assets(self.mem).saldo_total(self.mem.data.investments_active(), self.mem.localzone.now())
        if self.chkInactivas.checkState()==Qt.Checked:
            self.lblTotal.setText(self.tr("There aren't invested assets"))
        else:
            self.lblTotal.setText(self.tr("""Accounts balance: {0}
Zero risk investments balance: {1}
Zero risk assests balance: {2} ( {3} from your total assets {4} )""").format(
                            accounts, 
                            investments, 
                            accounts+investments, 
                            Percentage((accounts+investments).amount, total.amount), 
                            total
                        ))

    ## Overrides supper method and selects investments with zero risk
    @pyqtSlot(int) 
    def on_chkInactivas_stateChanged(self, state):
        if state==Qt.Unchecked:
            self.investments=self.mem.data.investments_active().InvestmentManager_with_investments_with_zero_risk()
            self.investments.myqtablewidget(self.mqtwInvestments)
            self.mqtwInvestments.setOrderBy(8, False)
        else:
            self.investments=self.mem.data.investments_inactive().InvestmentManager_with_investments_with_zero_risk()
            self.investments.myqtablewidget(self.mqtwInvestments)
            self.mqtwInvestments.setOrderBy(0, False)
        self.lblTotal_update()
