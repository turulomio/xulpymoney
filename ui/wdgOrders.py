from PyQt5.QtCore import *
from PyQt5.QtGui import *
from libxulpymoney import *
from libqmessagebox import *
from wdgOrdersAdd import *
from Ui_wdgOrders import *
from frmInvestmentReport import *

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
        
        
    @QtCore.pyqtSlot()  
    def on_actionOrderNew_triggered(self):
        d=QDialog(self)     
        d.setModal(True)
        d.setWindowTitle(self.tr("Add new order"))
        w=wdgOrdersAdd(self.mem, None, None, d)
        lay = QVBoxLayout(d)
        lay.addWidget(w)
        d.exec_()    
        self.on_cmbMode_currentIndexChanged(self.cmbMode.currentIndex())
    
    @QtCore.pyqtSlot()  
    def on_actionOrderEdit_triggered(self):
        d=QDialog(self)     
        d.setModal(True)
        d.setWindowTitle(self.tr("Edit order"))
        w=wdgOrdersAdd(self.mem, self.orders.selected, self.orders.selected.investment, d)
        lay = QVBoxLayout(d)
        lay.addWidget(w)
        d.exec_()
        self.on_cmbMode_currentIndexChanged(self.cmbMode.currentIndex())
        
    @QtCore.pyqtSlot() 
    def on_actionOrderDelete_triggered(self):
        self.orders.remove(self.orders.selected)
        self.mem.con.commit()
        self.on_cmbMode_currentIndexChanged(self.cmbMode.currentIndex())
        
    @QtCore.pyqtSlot() 
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
        frm.txtValorAccion.setText(self.orders.selected.price)
        
        
    @pyqtSlot(int)     
    def on_cmbMode_currentIndexChanged(self, index):
        if index==0:#Current
            self.wdgYear.hide()            
            self.orders=SetOrders(self.mem).init__from_db("""
                SELECT * 
                FROM 
                    ORDERS
                WHERE
                    EXPIRATION>=NOW()::DATE AND
                    EXECUTED IS NULL
                ORDER BY DATE
           """)
        elif index==1: #show expired
            self.wdgYear.show()
            self.orders=SetOrders(self.mem).init__from_db(self.mem.con.mogrify("""
                SELECT * 
                FROM 
                    ORDERS
                WHERE
                    DATE BETWEEN '%s-1-1' AND '%s-12-31' AND
                    EXPIRATION<NOW()::DATE AND
                    EXECUTED IS NULL
                ORDER BY DATE
           """, (self.wdgYear.year, self.wdgYear.year)))
        elif index==2: #show executed
            self.wdgYear.show()
            self.orders=SetOrders(self.mem).init__from_db(self.mem.con.mogrify("""
                SELECT * 
                FROM 
                    ORDERS
                WHERE
                    DATE BETWEEN '%s-1-1' AND '%s-12-31' AND
                    EXECUTED IS NOT NULL
                ORDER BY DATE
           """, (self.wdgYear.year, self.wdgYear.year)))
        else:
            self.wdgYear.show()
            self.orders=SetOrders(self.mem).init__from_db(self.mem.con.mogrify("""
                SELECT * 
                FROM 
                    ORDERS
                WHERE
                    DATE BETWEEN '%s-1-1' AND '%s-12-31'
                ORDER BY DATE
           """, (self.wdgYear.year, self.wdgYear.year)))
        self.orders.myqtablewidget(self.tblOrders)
       
    def on_tblOrders_customContextMenuRequested(self,  pos):
        if self.orders.selected==None:
            self.actionOrderDelete.setEnabled(False)
            self.actionOrderEdit.setEnabled(False)
            self.actionExecute.setEnabled(False)
        else:
            self.actionOrderDelete.setEnabled(True)
            self.actionOrderEdit.setEnabled(True)
            self.actionExecute.setEnabled(True)
            if self.orders.selected.executed==None:
                self.actionExecute.setText("Execute order")
            else:
                self.actionExecute.setText("Remove execution time")
            
        menu=QMenu()
        menu.addAction(self.actionOrderNew)
        menu.addSeparator()
        menu.addAction(self.actionOrderEdit)
        menu.addAction(self.actionOrderDelete)
        menu.addSeparator()
        menu.addAction(self.actionExecute)        
        menu.exec_(self.tblOrders.mapToGlobal(pos))

    def on_tblOrders_itemSelectionChanged(self):
        self.orders.selected=None
        for i in self.tblOrders.selectedItems():
            if i.column()==0:#only once per row
                self.orders.selected=self.orders.arr[i.row()]
        
