from PyQt5.QtCore import *
from PyQt5.QtGui import *
from libxulpymoney import *
from wdgOrdersAdd import *
from Ui_wdgOrders import *

class wdgOrders(QWidget, Ui_wdgOrders):
    def __init__(self, mem,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        self.orders=None 
         
        self.wdgYear.initiate(self.mem.data.orders.date_first_db_order().year,  datetime.date.today().year, datetime.date.today().year)
        self.tblOrders.settings(self.mem, "wdgOrders")
        self.on_cmbMode_currentIndexChanged(self.cmbMode.currentIndex())
        
        
    @QtCore.pyqtSlot()  
    def on_actionOrderNew_triggered(self):
        d=QDialog(self)     
        d.setWindowTitle(self.tr("Add new order"))
        w=wdgOrdersAdd(self.mem, None, None, d)
        lay = QVBoxLayout(d)
        lay.addWidget(w)
        d.show()    
        self.on_cmbMode_currentIndexChanged(self.cmbMode.currentIndex())
    
    @QtCore.pyqtSlot()  
    def on_actionOrderEdit_triggered(self):
        d=QDialog(self)     
        d.setWindowTitle(self.tr("Edit order"))
        w=wdgOrdersAdd(self.mem, self.orders.selected, self.orders.selected.investment, d)
        lay = QVBoxLayout(d)
        lay.addWidget(w)
        d.show()
        self.on_cmbMode_currentIndexChanged(self.cmbMode.currentIndex())
        
    @QtCore.pyqtSlot() 
    def on_actionOrderDelete_triggered(self):
        self.orders.remove(self.orders.selected, True)
        self.mem.con.commit()
        self.on_cmbMode_currentIndexChanged(self.cmbMode.currentIndex())
        
        
    @pyqtSlot(int)     
    def on_cmbMode_currentIndexChanged(self, index):
        if index==0:#Current
            self.wdgYear.hide()
            self.orders=self.mem.data.orders
        elif index==1: #show expired
            self.wdgYear.show()
            self.orders=SetOrders(self.mem).init__from_db(self.mem.con.mogrify("""
                SELECT * 
                FROM 
                    ORDERS
                WHERE
                    DATE BETWEEN '%s-1-1' AND '%s-12-31' AND
                    EXPIRATION<NOW()::DATE AND
                    INVESTMENTOPERATIONS_ID IS NULL
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
                    INVESTMENTOPERATIONS_ID IS NOT NULL
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
        
