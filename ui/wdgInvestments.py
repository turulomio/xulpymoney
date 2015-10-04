from libxulpymoney import *
from libqmessagebox import qmessagebox_error_ordering
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from Ui_wdgInvestments import *
from frmInvestmentReport import *
from frmQuotesIBM import *
from frmProductReport import *

class wdgInvestments(QWidget, Ui_wdgInvestments):
    def __init__(self, mem,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        self.inversiones=None
        self.selInvestment=None##Apunta a un objeto inversión
        self.loadedinactive=False

        self.progress = QProgressDialog(self.tr("Receiving requested data"), self.tr("Cancel"), 0,0)
        self.progress.setModal(True)
        self.progress.setWindowTitle(self.tr("Receiving data..."))
        self.progress.setMinimumDuration(0)     
        self.tblInvestments.settings(self.mem)
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())#Carga la tabla
    
    def tblInvestments_reload(self):
        """Función que carga la tabla de inversiones con el orden que tenga el arr serl.inversiones"""
        if self.chkInactivas.checkState()==Qt.Checked:
            self.tblInvestments.setSaveSettings(False) #Must be before than hidden, because hide resizes
            self.tblInvestments.setColumnHidden(8, True)
        else:
            self.tblInvestments.setSaveSettings(True)
            self.tblInvestments.setColumnHidden(8, False)
            
        r=self.inversiones.myqtablewidget(self.tblInvestments)
        if r["suminvertido"]!=0:
            self.lblTotal.setText(self.tr("Invested assets: {0}. Pending: {1} - {2} = {3} ({4} assets)\nDaily Diff: {5}. Investment average age: {6}").format(self.mem.localcurrency.string(r['suminvertido']), self.mem.localcurrency.string(r['sumpositivos']),  self.mem.localcurrency.string(-r['sumnegativos']),  self.mem.localcurrency.string(r['sumpendiente']), tpc(100*r['sumpendiente']/r['suminvertido']) , self.mem.localcurrency.string( r['sumdiario']), days_to_year_month(self.inversiones.average_age())))
        else:
            self.lblTotal.setText(self.tr("There aren't invested assets"))


    @QtCore.pyqtSlot() 
    def on_actionActive_triggered(self):
        if self.selInvestment.account.eb.qmessagebox_inactive()  or self.selInvestment.account.qmessagebox_inactive():
            return  
        
        self.mem.data.load_inactives()
        if self.actionActive.isChecked()==True:
            self.selInvestment.active=True
        else:
            self.selInvestment.active=False
        self.selInvestment.save()
        self.mem.con.commit()     
        #Recoloca en los SetInvestments
        if self.selInvestment.active==True:#Está todavía en inactivas
            self.mem.data.investments_active.append(self.selInvestment)
            if self.mem.data.investments_inactive!=None:#Puede que no se haya cargado
                self.mem.data.investments_inactive.remove(self.selInvestment)
        else:#Está todavía en activas
            self.mem.data.investments_active.remove(self.selInvestment)
            if self.mem.data.investments_inactive!=None:#Puede que no se haya cargado
                self.mem.data.investments_inactive.append(self.selInvestment)
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())#Carga la tabla

            
    @QtCore.pyqtSlot() 
    def on_actionInvestmentDelete_triggered(self):
        cur = self.mem.con.cursor()
        self.selInvestment.borrar(cur)
        self.mem.con.commit()
        self.mem.data.investments_active.remove(self.selInvestment)
        cur.close()
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())#Carga la tabla

          
    @QtCore.pyqtSlot() 
    def on_actionInvestmentAdd_triggered(self):
        w=frmInvestmentReport(self.mem,   None, self)
        w.exec_()
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())#Carga la tabla
        
    @QtCore.pyqtSlot() 
    def on_actionInvestmentReport_triggered(self):
        w=frmInvestmentReport(self.mem, self.selInvestment, self)
        w.exec_()
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())#Carga la tabla

                
    @QtCore.pyqtSlot() 
    def on_actionProduct_triggered(self):
        w=frmProductReport(self.mem, self.selInvestment.product, self.selInvestment, self)
        w.exec_()
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())#Carga la tabla
            
            
    @QtCore.pyqtSlot() 
    def on_actionProductPrice_triggered(self):
        w=frmQuotesIBM(self.mem, self.selInvestment.product,None,  self)
        w.exec_()
        self.selInvestment.product.result.basic.load_from_db()
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())#Carga la tabla

    @QtCore.pyqtSlot() 
    def on_actionSortTPCDiario_triggered(self):
        if self.inversiones.order_by_percentage_daily():
            self.tblInvestments_reload()    
        else:
            qmessagebox_error_ordering()     
        
    @QtCore.pyqtSlot() 
    def on_actionSortTPCVenta_triggered(self):
        if self.inversiones.order_by_percentage_sellingpoint():
            self.tblInvestments_reload()    
        else:
            qmessagebox_error_ordering()     
        
    @QtCore.pyqtSlot() 
    def on_actionSortTPC_triggered(self):
        if self.inversiones.order_by_percentage_invested():
            self.tblInvestments_reload()    
        else:
            qmessagebox_error_ordering()     
        
    @QtCore.pyqtSlot() 
    def on_actionSortHour_triggered(self):
        if self.inversiones.order_by_datetime():
            self.tblInvestments_reload()    
        else:
            qmessagebox_error_ordering()     
        
    @QtCore.pyqtSlot() 
    def on_actionSortName_triggered(self):
        if self.inversiones.order_by_name():
            self.tblInvestments_reload()    
        else:
            qmessagebox_error_ordering()     
            
    def on_chkInactivas_stateChanged(self, state):
        if state==Qt.Unchecked:
            self.inversiones=self.mem.data.investments_active
            self.on_actionSortTPCVenta_triggered()
        else:
            self.mem.data.load_inactives()
            self.inversiones=self.mem.data.investments_inactive
            self.on_actionSortName_triggered()
        self.tblInvestments_reload()
        self.tblInvestments.clearSelection()
        self.selInvestment=None   

    def on_tblInvestments_customContextMenuRequested(self,  pos):
        if self.selInvestment==None:
            self.actionInvestmentReport.setEnabled(False)
            self.actionInvestmentDelete.setEnabled(False)
            self.actionActive.setEnabled(False)
            self.actionProduct.setEnabled(False)
            self.actionProductPrice.setEnabled(False)
        else:
            self.actionInvestmentReport.setEnabled(True)
            self.actionActive.setEnabled(True)       
            self.actionProduct.setEnabled(True)
            self.actionProductPrice.setEnabled(True)
            if self.selInvestment.es_borrable()==True:
                self.actionInvestmentDelete.setEnabled(True)
            else:
                self.actionInvestmentDelete.setEnabled(False)
            if self.selInvestment.active==True:
                self.actionActive.setChecked(True)
            else:
                self.actionActive.setChecked(False)

        menu=QMenu()
        menu.addAction(self.actionInvestmentAdd)
        menu.addAction(self.actionInvestmentDelete)   
        menu.addSeparator()   
        menu.addAction(self.actionInvestmentReport)        
        menu.addAction(self.actionProduct)
        menu.addSeparator()
        menu.addAction(self.actionProductPrice)
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
            self.selInvestment=self.inversiones.arr[i.row()]

    @QtCore.pyqtSlot(int, int) 
    def on_tblInvestments_cellDoubleClicked(self, row, column):
        if column==8:#TPC Venta
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.tr("Shares number: {0}").format(self.selInvestment.acciones())+"\n"+
                    self.tr("Purchase price average: {0}").format(self.selInvestment.product.currency.string(self.selInvestment.op_actual.valor_medio_compra()))+"\n"+
                    self.tr("Selling point: {}").format(self.selInvestment.product.currency.string(self.selInvestment.venta))+"\n"+
                    self.tr("Selling all shares you get {}").format(self.selInvestment.product.currency.string(self.selInvestment.op_actual.pendiente(Quote(self.mem).init__create(self.selInvestment.product, self.mem.localzone.now(),  self.selInvestment.venta))))
            )
            m.exec_()     
        else:
            self.on_actionInvestmentReport_triggered()
