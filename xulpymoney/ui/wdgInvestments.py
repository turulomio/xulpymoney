from xulpymoney.libxulpymoney import Percentage, Quote,  ProductUpdate
from xulpymoney.libxulpymoneyfunctions import days2string, qmessagebox
from PyQt5.QtCore import Qt,  pyqtSlot
from PyQt5.QtWidgets import QMenu, QWidget
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
        self.selInvestment=None##Apunta a un objeto inversión
        self.loadedinactive=False

        self.tblInvestments.settings(self.mem, "wdgInvestments")
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())
    
    def tblInvestments_reload(self):
        """Función que carga la tabla de inversiones con el orden que tenga el arr serl.investments"""
        if self.chkInactivas.checkState()==Qt.Checked:
            self.tblInvestments.setSaveSettings(False) #Must be before than hidden, because hide resizes
            self.tblInvestments.setColumnHidden(8, True)
        else:
            self.tblInvestments.setSaveSettings(True)
            self.tblInvestments.setColumnHidden(8, False)
            
        self.investments.myqtablewidget(self.tblInvestments)
        invested=self.investments.invested()
        pendiente=self.investments.pendiente()
        if invested.isZero():
            self.lblTotal.setText(self.tr("There aren't invested assets"))
        else:
            self.lblTotal.setText(self.tr("Invested assets: {0}. Pending: {1}{2} = {3} ({4} assets)\nDaily Diff: {5}. Investment average age: {6}").format(
                            invested,self.investments.pendiente_positivo(),
                            self.investments.pendiente_negativo(),  
                            pendiente, 
                            Percentage(pendiente, invested),  
                            self.investments.gains_last_day()
                            , days2string(self.investments.average_age())))


    @pyqtSlot() 
    def on_actionActive_triggered(self):
        if self.selInvestment.account.eb.qmessagebox_inactive()  or self.selInvestment.account.qmessagebox_inactive():
            return  
    
        self.selInvestment.active=not self.selInvestment.active
        self.selInvestment.save()
        self.mem.con.commit()     

        self.chkInactivas.setCheckState(Qt.Unchecked)
        self.on_chkInactivas_stateChanged(Qt.Unchecked)

            
    @pyqtSlot() 
    def on_actionInvestmentDelete_triggered(self):
        """
            on_tblInvestments_customContextMenuRequested validates if it's deletable
        """
        self.selInvestment.borrar()
        self.mem.data.investments.remove(self.selInvestment)
        self.mem.con.commit()
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())

          
    @pyqtSlot() 
    def on_actionInvestmentAdd_triggered(self):
        w=frmInvestmentReport(self.mem,   None, self)
        w.exec_()
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())
        
    @pyqtSlot() 
    def on_actionInvestmentReport_triggered(self):
        w=frmInvestmentReport(self.mem, self.selInvestment, self)
        w.exec_()
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())

    @pyqtSlot() 
    def on_actionProduct_triggered(self):
        w=frmProductReport(self.mem, self.selInvestment.product, self.selInvestment, self)
        w.exec_()
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())

    @pyqtSlot() 
    def on_actionProductUpdate_triggered(self):
        update=ProductUpdate(self.mem)
        update.setCommands(self.selInvestment.product)
        quotes=update.run()
        quotes.save()
        self.mem.con.commit()
        quotes.print()
        
    @pyqtSlot() 
    def on_actionSameProduct_triggered(self):
        inv=self.mem.data.investments.investment_merging_current_operations_with_same_product(self.selInvestment.product)
        w=frmInvestmentReport(self.mem, inv, self)
        w.exec_()
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())
                    
    @pyqtSlot() 
    def on_actionSameProductFIFO_triggered(self):
        inv=self.mem.data.investments.investment_merging_operations_with_same_product(self.selInvestment.product)
        w=frmInvestmentReport(self.mem, inv, self)
        w.exec_()
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())
            
            
    @pyqtSlot() 
    def on_actionProductPrice_triggered(self):
        w=frmQuotesIBM(self.mem, self.selInvestment.product,None,  self)
        w.exec_()
        self.selInvestment.product.needStatus(1, downgrade_to=0)
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())
        
    @pyqtSlot() 
    def on_actionProductPriceLastRemove_triggered(self):
        self.selInvestment.product.result.basic.last.delete()
        self.mem.con.commit()
        self.selInvestment.product.needStatus(1, downgrade_to=0)
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())

    @pyqtSlot() 
    def on_actionSortTPCDiario_triggered(self):
        if self.investments.order_by_percentage_daily():
            self.tblInvestments_reload()    
        else:
            qmessagebox(self.tr("I couldn't order data due to they have null values"))  
            self.tblInvestments_reload()       
        
    @pyqtSlot() 
    def on_actionSortTPCVenta_triggered(self):
        if self.investments.order_by_percentage_invested() and self.investments.order_by_percentage_sellingpoint():
            self.tblInvestments_reload()    
        else:
            qmessagebox(self.tr("I couldn't order data due to they have null values"))     
            self.tblInvestments_reload()    
        
    @pyqtSlot() 
    def on_actionSortTPC_triggered(self):
        if self.investments.order_by_percentage_invested():
            self.tblInvestments_reload()    
        else:
            qmessagebox(self.tr("I couldn't order data due to they have null values"))     
            self.tblInvestments_reload()    
        
    @pyqtSlot() 
    def on_actionSortHour_triggered(self):
        if self.investments.order_by_datetime():
            self.tblInvestments_reload()    
        else:
            qmessagebox(self.tr("I couldn't order data due to they have null values"))     
            self.tblInvestments_reload()    
        
    @pyqtSlot() 
    def on_actionSortName_triggered(self):
        if self.investments.order_by_name():
            self.tblInvestments_reload()    
        else:
            qmessagebox(self.tr("I couldn't order data due to they have null values"))     
            self.tblInvestments_reload()    
            
    @pyqtSlot(int) 
    def on_chkInactivas_stateChanged(self, state):
        if state==Qt.Unchecked:
            self.investments=self.mem.data.investments_active()
            self.on_actionSortTPCVenta_triggered()
        else:
            self.investments=self.mem.data.investments_inactive()
            self.on_actionSortName_triggered()
        self.tblInvestments.clearSelection()
        self.selInvestment=None   

    def on_tblInvestments_customContextMenuRequested(self,  pos):
        if self.selInvestment==None:
            self.actionInvestmentReport.setEnabled(False)
            self.actionInvestmentDelete.setEnabled(False)
            self.actionActive.setEnabled(False)
            self.actionProduct.setEnabled(False)
            self.actionProductPrice.setEnabled(False)
            self.actionProductPriceLastRemove.setEnabled(False)
            self.actionProductUpdate.setEnabled(False)
        else:
            self.actionInvestmentReport.setEnabled(True)
            self.actionActive.setEnabled(True)       
            self.actionProduct.setEnabled(True)
            if self.mem.data.investments.numberWithSameProduct(self.selInvestment.product)>1:
                self.actionSameProduct.setEnabled(True)
                self.actionSameProductFIFO.setEnabled(True)
            else:
                self.actionSameProduct.setEnabled(False)
                self.actionSameProductFIFO.setEnabled(False)
            self.actionProductPrice.setEnabled(True)
            if self.selInvestment.es_borrable()==True:
                self.actionInvestmentDelete.setEnabled(True)
            else:
                self.actionInvestmentDelete.setEnabled(False)
                
            self.actionProductPriceLastRemove.setEnabled(True)
            self.actionProductUpdate.setEnabled(True)
                
            if self.selInvestment.active==True:
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
        menu.addAction(self.actionProductUpdate)
        menu.addSeparator()
        menu.addAction(self.actionActive)
        menu.addSeparator()        
        ordenar=QMenu(self.tr("Order by"))
        ordenar.addAction(self.actionSortName)
        ordenar.addAction(self.actionSortHour)
        ordenar.addAction(self.actionSortTPCDiario)
        ordenar.addAction(self.actionSortTPC)
        ordenar.addAction(self.actionSortTPCVenta)
        menu.addMenu(ordenar)        
        menu.exec_(self.tblInvestments.mapToGlobal(pos))

    def on_tblInvestments_itemSelectionChanged(self):
        self.selInvestment=None
        for i in self.tblInvestments.selectedItems():#itera por cada item no row.
            self.selInvestment=self.investments.arr[i.row()]

    @pyqtSlot(int, int) 
    def on_tblInvestments_cellDoubleClicked(self, row, column):
        if column==8:#TPC Venta
            qmessagebox(self.tr("Shares number: {0}").format(self.selInvestment.shares())+"\n"+
                    self.tr("Purchase price average: {0}").format(self.selInvestment.op_actual.average_price().local())+"\n"+
                    self.tr("Selling point: {}").format(self.selInvestment.venta)+"\n"+
                    self.tr("Selling all shares you get {}").format(self.selInvestment.op_actual.pendiente(Quote(self.mem).init__create(self.selInvestment.product, self.mem.localzone.now(),  self.selInvestment.venta)).local())
            )  
        else:
            self.on_actionInvestmentReport_triggered()
