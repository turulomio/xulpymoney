import datetime
from PyQt5.QtCore import pyqtSlot, QSize
from PyQt5.QtWidgets import QWidget, QDialog, QVBoxLayout, QMenu, QMessageBox
from xulpymoney.libxulpymoney import OrderManager
from xulpymoney.libxulpymoneyfunctions import qmessagebox
from xulpymoney.ui.wdgOrdersAdd import wdgOrdersAdd
from xulpymoney.ui.wdgDisReinvest import wdgDisReinvest
from xulpymoney.ui.Ui_wdgOrders import Ui_wdgOrders
from xulpymoney.ui.frmInvestmentReport import frmInvestmentReport

class wdgOrders(QWidget, Ui_wdgOrders):
    def __init__(self, mem,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        self.orders=None 
         
        self.tblOrders.settings(self.mem, "wdgOrders")
        self.tblSellingPoints.settings(self.mem, "wdgOrders")
        self.mem.data.investments_active().myqtablewidget_sellingpoints(self.tblSellingPoints)
        self.on_cmbMode_currentIndexChanged(self.cmbMode.currentIndex())
        self.wdgYear.initiate(self.orders.date_first_db_order().year,  datetime.date.today().year, datetime.date.today().year)
        
        
    @pyqtSlot()  
    def on_actionOrderNew_triggered(self):
        d=QDialog(self)     
        d.setModal(True)
        d.setWindowTitle(self.tr("Add new order"))
        w=wdgOrdersAdd(self.mem, None, None, d)
        lay = QVBoxLayout(d)
        lay.addWidget(w)
        d.exec_()    
        self.on_cmbMode_currentIndexChanged(self.cmbMode.currentIndex())
    
    @pyqtSlot()  
    def on_actionOrderEdit_triggered(self):
        d=QDialog(self)     
        d.setModal(True)
        d.setWindowTitle(self.tr("Edit order"))
        w=wdgOrdersAdd(self.mem, self.orders.selected, self.orders.selected.investment, d)
        lay = QVBoxLayout(d)
        lay.addWidget(w)
        d.exec_()
        self.on_cmbMode_currentIndexChanged(self.cmbMode.currentIndex())
        
    @pyqtSlot() 
    def on_actionOrderDelete_triggered(self):
        self.orders.remove(self.orders.selected)
        self.mem.con.commit()
        self.on_cmbMode_currentIndexChanged(self.cmbMode.currentIndex())
        
        
    @pyqtSlot()
    def on_actionShowReinvest_triggered(self):
        if self.orders.selected.price==None or self.orders.selected.shares==None or self.orders.selected.investment.shares()==0:
            qmessagebox(self.tr("This order can't be simulated"))
            return
        
        
        
        d=QDialog()       
        d.resize(self.mem.settings.value("wdgOrders/qdialog_disreinvest", QSize(1024, 768)))
        d.setWindowTitle(self.tr("Order reinvest simulation"))
        w=wdgDisReinvest(self.mem, self.orders.selected.investment, False,  d)
        w.txtValorAccion.setText(self.orders.selected.price)
        w.txtSimulacion.setText(self.orders.selected.price*self.orders.selected.shares)
        lay = QVBoxLayout(d)
        lay.addWidget(w)
        d.exec_()
        self.mem.settings.setValue("frmInvestmentReport/qdialog_disreinvest", d.size())
                
    @pyqtSlot()
    def on_actionShowReinvestSameProduct_triggered(self):
        if self.orders.selected.price==None or self.orders.selected.shares==None or self.orders.selected.investment.shares()==0:
            qmessagebox(self.tr("This order can't be simulated"))
            return
        
        d=QDialog()       
        d.resize(self.mem.settings.value("wdgOrders/qdialog_disreinvest", QSize(1024, 768)))
        d.setWindowTitle(self.tr("Order reinvest simulation with all investments with the same product"))
        w=wdgDisReinvest(self.mem, self.orders.selected.investment, True,  d)
        w.txtValorAccion.setText(self.orders.selected.price)
        w.txtSimulacion.setText(self.orders.selected.price*self.orders.selected.shares)
        lay = QVBoxLayout(d)
        lay.addWidget(w)
        d.exec_()
        self.mem.settings.setValue("frmInvestmentReport/qdialog_disreinvest", d.size())
        
    @pyqtSlot() 
    def on_actionExecute_triggered(self):
        if self.orders.selected.investment.questionbox_inactive()==QMessageBox.No:#It's not active, after all.
            return
        
        if self.orders.selected.executed==None:#Only adds operation if it's not executed
            w=frmInvestmentReport(self.mem, self.orders.selected.investment, self)
            w.frmInvestmentOperationsAdd_initiated.connect(self.load_OrderData)
            w.on_actionOperationAdd_triggered()        
            w.exec_()
        
        if self.orders.selected.executed==None:
            self.orders.selected.executed=self.mem.localzone.now()#Set execution
        else:
            self.orders.selected.executed=None#Remove execution
        self.orders.selected.save()
        self.mem.con.commit()

        self.on_cmbMode_currentIndexChanged(self.cmbMode.currentIndex())
        
    def load_OrderData(self, frm):
        """Carga los datos de la orden en el frmInvestmentOperationsAdd"""
        if self.orders.selected.shares<0:
            frm.cmbTiposOperaciones.setCurrentIndex(frm.cmbTiposOperaciones.findData(5))#Sale
        else:
            frm.cmbTiposOperaciones.setCurrentIndex(frm.cmbTiposOperaciones.findData(4))#Purchase
        frm.txtAcciones.setText(self.orders.selected.shares)
        frm.wdg2CPrice.setTextA(self.orders.selected.price)

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
        self.orders.myqtablewidget(self.tblOrders)
       
    def on_tblOrders_customContextMenuRequested(self,  pos):
        if self.orders.selected==None:
            self.actionOrderDelete.setEnabled(False)
            self.actionOrderEdit.setEnabled(False)
            self.actionExecute.setEnabled(False)
            self.actionShowReinvest.setEnabled(False)
            self.actionShowReinvestSameProduct.setEnabled(False)
        else:
            self.actionOrderDelete.setEnabled(True)
            self.actionOrderEdit.setEnabled(True)
            self.actionExecute.setEnabled(True)
            if self.orders.selected.executed==None:
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
        menu.exec_(self.tblOrders.mapToGlobal(pos))

    def on_tblOrders_itemSelectionChanged(self):
        self.orders.selected=None
        for i in self.tblOrders.selectedItems():
            if i.column()==0:#only once per row
                self.orders.selected=self.orders.arr[i.row()]
                
    def on_wdgYear_changed(self):
        self.on_cmbMode_currentIndexChanged(self.cmbMode.currentIndex())
        
