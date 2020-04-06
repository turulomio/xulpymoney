from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget, QMenu, QMessageBox
from datetime import date
from logging import debug
from xulpymoney.objects.order import OrderManager
from xulpymoney.ui.Ui_wdgOrders import Ui_wdgOrders
from xulpymoney.ui.frmInvestmentReport import frmInvestmentReport
from xulpymoney.ui.myqdialog import MyModalQDialog
from xulpymoney.ui.myqwidgets import qmessagebox
from xulpymoney.ui.wdgOrdersAdd import wdgOrdersAdd
from xulpymoney.ui.wdgDisReinvest import wdgDisReinvest

class wdgOrders(QWidget, Ui_wdgOrders):
    def __init__(self, mem,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        self.orders=None 
         
        self.mqtwOrders.setSettings(self.mem.settings, "wdgOrders", "mqtwOrders")#mqtwDataWithOrders
        self.mqtwOrders.table.customContextMenuRequested.connect(self.on_mqtwOrders_customContextMenuRequested) 
        self.mqtwSellingPoints.setSettings(self.mem.settings, "wdgOrders", "mqtwSellingPoints")
        self.mem.data.investments_active().mqtw_sellingpoints(self.mqtwSellingPoints)
        self.mqtwSellingPoints.setOrderBy(4, False)
        self.on_cmbMode_currentIndexChanged(self.cmbMode.currentIndex())
        self.wdgYear.initiate(self.orders.date_first_db_order().year,  date.today().year, date.today().year)

    @pyqtSlot()  
    def on_actionOrderNew_triggered(self):
        d=MyModalQDialog(self)
        d.setWindowTitle(self.tr("Add new order"))
        d.setSettings(self.mem.settings, "wdgOrders", "frmOrderAdd", 600, 400)
        w=wdgOrdersAdd(self.mem, None, None, d)
        d.setWidgets(w)
        d.exec_()    
        self.on_cmbMode_currentIndexChanged(self.cmbMode.currentIndex())
    
    @pyqtSlot()  
    def on_actionOrderEdit_triggered(self):
        d=MyModalQDialog(self)
        d.setWindowTitle(self.tr("Edit order"))
        d.setSettings(self.mem.settings, "wdgOrders", "frmOrderAdd", 600, 400)
        w=wdgOrdersAdd(self.mem, self.mqtwOrders.selected, self.mqtwOrders.selected.investment, d)
        d.setWidgets(w)
        d.exec_()    
        self.on_cmbMode_currentIndexChanged(self.cmbMode.currentIndex())
        
    @pyqtSlot() 
    def on_actionOrderDelete_triggered(self):
        self.orders.remove(self.mqtwOrders.selected)
        self.mem.con.commit()
        self.on_cmbMode_currentIndexChanged(self.cmbMode.currentIndex())
        
        
    @pyqtSlot()
    def on_actionShowReinvest_triggered(self):
        if self.mqtwOrders.selected.price is None or self.mqtwOrders.selected.shares is None or self.mqtwOrders.selected.investment.shares()==0:
            qmessagebox(self.tr("This order can't be simulated"))
            return
        
        d=MyModalQDialog()
        d.setWindowTitle(self.tr("Order reinvest simulation"))
        d.setSettings(self.mem.settings, "wdgOrders", "frmDisReinvest")
        w=wdgDisReinvest(self.mem, self.mqtwOrders.selected.investment, False,  d)
        w.txtValorAccion.setText(self.mqtwOrders.selected.price)
        w.txtSimulacion.setText(self.mqtwOrders.selected.price*self.mqtwOrders.selected.shares)
        d.setWidgets(w)
        d.exec_()
                
    @pyqtSlot()
    def on_actionShowReinvestSameProduct_triggered(self):
        investment=self.mem.data.investments_active().Investment_merging_current_operations_with_same_product(self.mqtwOrders.selected.investment.product)
        if self.mqtwOrders.selected.price==None or self.mqtwOrders.selected.shares==None or investment.shares()==0:
            qmessagebox(self.tr("This order can't be simulated"))
            return
        
        d=MyModalQDialog()
        d.setWindowTitle(self.tr("Order reinvest simulation with all investments with the same product"))
        d.setSettings(self.mem.settings, "wdgOrders", "frmDisReinvest")
        w=wdgDisReinvest(self.mem, investment, True,  d)
        w.txtValorAccion.setText(self.mqtwOrders.selected.price)
        w.txtSimulacion.setText(self.mqtwOrders.selected.price*self.mqtwOrders.selected.shares)
        d.setWidgets(w)
        d.exec_()
        
    @pyqtSlot() 
    def on_actionExecute_triggered(self):
        if self.mqtwOrders.selected.investment.questionbox_inactive()==QMessageBox.No:#It's not active, after all.
            return
        
        if self.mqtwOrders.selected.executed==None:#Only adds operation if it's not executed
            debug(self.mqtwOrders.selected.investment)
            w=frmInvestmentReport(self.mem, self.mqtwOrders.selected.investment, self)
            w.frmInvestmentOperationsAdd_initiated.connect(self.load_OrderData)
            w.on_actionOperationAdd_triggered()        
            w.exec_()
        
        if self.mqtwOrders.selected.executed==None:
            self.mqtwOrders.selected.executed=self.mem.localzone.now()#Set execution
        else:
            self.mqtwOrders.selected.executed=None#Remove execution
        self.mqtwOrders.selected.save()
        self.mem.con.commit()

        self.on_cmbMode_currentIndexChanged(self.cmbMode.currentIndex())
        
    def load_OrderData(self, frm):
        """Carga los datos de la orden en el frmInvestmentOperationsAdd"""
        if self.mqtwOrders.selected.shares<0:
            frm.cmbTiposOperaciones.setCurrentIndex(frm.cmbTiposOperaciones.findData(5))#Sale
        else:
            frm.cmbTiposOperaciones.setCurrentIndex(frm.cmbTiposOperaciones.findData(4))#Purchase
        frm.txtAcciones.setText(self.mqtwOrders.selected.shares)
        frm.wdg2CPrice.setTextA(self.mqtwOrders.selected.price)

    @pyqtSlot(int)     
    def on_cmbMode_currentIndexChanged(self, index):
        if index==0:#Current
            self.wdgYear.hide()            
            self.orders=OrderManager(self.mem).init__from_db("""
                SELECT * 
                FROM 
                    ORDERS
                WHERE
                    EXPIRATION>=NOW()::DATE AND
                    EXECUTED IS NULL
                ORDER BY DATE
           """)
            self.orders.order_by_percentage_from_current_price()
        elif index==1: #show expired
            self.wdgYear.show()
            self.orders=OrderManager(self.mem).init__from_db(self.mem.con.mogrify("""
                SELECT * 
                FROM 
                    ORDERS
                WHERE
                    DATE BETWEEN '%s-1-1' AND '%s-12-31' AND
                    EXPIRATION<NOW()::DATE AND
                    EXECUTED IS NULL
                ORDER BY DATE
           """, (self.wdgYear.year, self.wdgYear.year)))
            self.orders.order_by_expiration()
        elif index==2: #show executed
            self.wdgYear.show()
            self.orders=OrderManager(self.mem).init__from_db(self.mem.con.mogrify("""
                SELECT * 
                FROM 
                    ORDERS
                WHERE
                    DATE BETWEEN '%s-1-1' AND '%s-12-31' AND
                    EXECUTED IS NOT NULL
                ORDER BY DATE
           """, (self.wdgYear.year, self.wdgYear.year)))
            self.orders.order_by_execution()
        else:
            self.wdgYear.show()
            self.orders=OrderManager(self.mem).init__from_db(self.mem.con.mogrify("""
                SELECT * 
                FROM 
                    ORDERS
                WHERE
                    DATE BETWEEN '%s-1-1' AND '%s-12-31'
                ORDER BY DATE
           """, (self.wdgYear.year, self.wdgYear.year)))
            self.orders.order_by_date()
        self.orders.mqtw(self.mqtwOrders)
        self.mqtwOrders.setOrderBy(6, True)
        self.lblBalance.setText(self.tr("Ordered balance: {}").format(self.orders.amount()))
       
    def on_mqtwOrders_customContextMenuRequested(self,  pos):
        if self.mqtwOrders.selected==None:
            self.actionOrderDelete.setEnabled(False)
            self.actionOrderEdit.setEnabled(False)
            self.actionExecute.setEnabled(False)
            self.actionShowReinvest.setEnabled(False)
            self.actionShowReinvestSameProduct.setEnabled(False)
        else:
            self.actionOrderDelete.setEnabled(True)
            self.actionOrderEdit.setEnabled(True)
            self.actionExecute.setEnabled(True)
            if self.mqtwOrders.selected.executed==None:
                self.actionExecute.setText("Execute order")
            else:
                self.actionExecute.setText("Remove execution time")
            self.actionShowReinvest.setEnabled(True)
            self.actionShowReinvestSameProduct.setEnabled(True)

        menu=QMenu()
        menu.addAction(self.actionOrderNew)
        menu.addSeparator()
        menu.addAction(self.actionOrderEdit)
        menu.addAction(self.actionOrderDelete)
        menu.addSeparator()
        menu.addAction(self.actionExecute)        
        menu.addSeparator()
        menu.addAction(self.actionShowReinvest)
        menu.addAction(self.actionShowReinvestSameProduct)
        menu.addMenu(self.mqtwOrders.qmenu())
        menu.exec_(self.mqtwOrders.table.mapToGlobal(pos))
                
    def on_wdgYear_changed(self):
        self.on_cmbMode_currentIndexChanged(self.cmbMode.currentIndex())
