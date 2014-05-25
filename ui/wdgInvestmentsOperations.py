from libxulpymoney import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Ui_wdgInvestmentsOperations import *
from frmInvestmentReport import *
from frmInvestmentOperationsAdd import *
from frmAccountsReport import *

class wdgInvestmentsOperations(QWidget, Ui_wdgInvestmentsOperations):
    def __init__(self, mem,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        fechainicio=Assets(self.mem).primera_fecha_con_datos_usuario()         

        self.mem.data.load_inactives()
        self.wym.initiate(fechainicio.year, datetime.date.today().year, datetime.date.today().year,  datetime.date.today().month)
        QObject.connect(self.wym, SIGNAL("changed"), self.on_wym_changed)
        self.setOperations=SetInvestmentOperations(self.mem)
        self.setCurrent=SetInvestmentOperationsCurrent(self.mem)
        self.selProductOperation=None
        self.tblCurrent.settings("wdgInvestmentsOperations",  self.mem)
        self.load()
        self.load_current()
        
    def load(self):
        del self.setOperations.arr
        self.setOperations.arr=[]
        cur=self.mem.con.cursor()
        if self.radYear.isChecked()==True:
            cur.execute("select * from operinversiones where date_part('year',datetime)=%s order by datetime",(self.wym.year, ) )
        else:
            cur.execute("select * from operinversiones where date_part('year',datetime)=%s and date_part('month',datetime)=%s order by datetime",(self.wym.year, self.wym.month) )
        for row in cur:
            self.setOperations.append(InvestmentOperation(self.mem).init__db_row(row, self.mem.data.inversiones_all().find(row['id_inversiones']), self.mem.tiposoperaciones.find(row['id_tiposoperaciones'])))
        cur.close()
        
        self.setOperations.myqtablewidget(self.table, None)
        
    def load_current(self):
        for inv in self.mem.data.inversiones_active.arr:
            for o in inv.op_actual.arr:
                self.setCurrent.append(o)
        self.setCurrent.sort()
        self.setCurrent.myqtablewidget(self.tblCurrent, None)

        
        
        
    def on_radYear_toggled(self, toggle):
        self.load()
        
    def on_wym_changed(self):
        self.load()    

    def on_table_itemSelectionChanged(self):
        self.selProductOperation=None
        for i in self.table.selectedItems():#itera por cada item no row.
            self.selProductOperation=self.setOperations.arr[i.row()]
    
    @QtCore.pyqtSlot() 
    def on_actionShowAccount_activated(self):
        w=frmAccountsReport(self.mem,   self.selProductOperation.inversion.cuenta, self)
        w.exec_()
        self.load()
        
    @QtCore.pyqtSlot() 
    def on_actionShowInvestment_activated(self):
        w=frmInvestmentReport(self.mem, self.selProductOperation.inversion, self)
        w.exec_()
        self.load()
                
    @QtCore.pyqtSlot() 
    def on_actionShowProduct_activated(self):
        w=frmProductReport(self.mem, self.selProductOperation.inversion.product, self.selProductOperation.inversion, self)
        w.exec_()
        self.load()
        
    def on_table_customContextMenuRequested(self,  pos):
        if self.selProductOperation==None:
            self.actionShowAccount.setEnabled(False)
            self.actionShowInvestment.setEnabled(False)
            self.actionShowInvestmentOperation.setEnabled(False)
            self.actionShowProduct.setEnabled(False)
        else:
            self.actionShowAccount.setEnabled(True)
            self.actionShowInvestment.setEnabled(True)
            self.actionShowInvestmentOperation.setEnabled(True)
            self.actionShowProduct.setEnabled(True)

        menu=QMenu()
        menu.addAction(self.actionShowAccount)   
        menu.addSeparator()   
        menu.addAction(self.actionShowInvestment)   
        menu.addSeparator()   
        menu.addAction(self.actionShowInvestmentOperation)      
        menu.addSeparator()   
        menu.addAction(self.actionShowProduct)            
        menu.exec_(self.table.mapToGlobal(pos))
        
    @QtCore.pyqtSlot() 
    def on_actionShowInvestmentOperation_activated(self):
        w=frmInvestmentOperationsAdd(self.mem, self.selProductOperation.inversion, self.selProductOperation, self)
        w.exec_()
        self.load()
        
