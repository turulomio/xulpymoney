from libxulpymoney import *
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
        self.tblInvestments.settings("wdgInvestments",  self.mem)
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())#Carga la tabla
                
    def tblInvestments_load(self):
        """Función que carga la tabla de inversiones con el orden que tenga el arr serl.inversiones"""
        self.tblInvestments.setRowCount(len(self.inversiones.arr))
        self.tblInvestments.clearContents()
        sumpendiente=0
        sumdiario=0
        suminvertido=0
        i=0
        sumpositivos=0
        sumnegativos=0
        gainsyear=str2bool(self.mem.config.get_value("settings", "gainsyear"))
        for inv in self.inversiones.arr:            
            self.tblInvestments.setItem(i, 0, QTableWidgetItem("{0} ({1})".format(inv.name, inv.cuenta.name)))            
            self.tblInvestments.setItem(i, 1, qdatetime(inv.product.result.basic.last.datetime, inv.product.stockexchange.zone))
            self.tblInvestments.setItem(i, 2, inv.product.currency.qtablewidgetitem(inv.product.result.basic.last.quote,  6))#Se debería recibir el parametro currency
            
            diario=inv.diferencia_saldo_diario()
            try:
                sumdiario=sumdiario+diario
            except:
                pass
            self.tblInvestments.setItem(i, 3, inv.product.currency.qtablewidgetitem(diario))
            self.tblInvestments.setItem(i, 4, qtpc(inv.product.result.basic.tpc_diario()))
            self.tblInvestments.setItem(i, 5, inv.product.currency.qtablewidgetitem(inv.balance()))
            suminvertido=suminvertido+inv.invertido()
            pendiente=inv.pendiente()
            if pendiente>0:
                sumpositivos=sumpositivos+pendiente
            else:
                sumnegativos=sumnegativos+pendiente
            sumpendiente=sumpendiente+pendiente
            self.tblInvestments.setItem(i, 6, inv.product.currency.qtablewidgetitem(pendiente))
            tpc_invertido=inv.tpc_invertido()
            self.tblInvestments.setItem(i, 7, qtpc(tpc_invertido))
            tpc_venta=inv.tpc_venta()
            self.tblInvestments.setItem(i, 8, qtpc(tpc_venta))
            if gainsyear==True and inv.op_actual.less_than_a_year()==True:
                self.tblInvestments.item(i, 8).setIcon(QIcon(":/xulpymoney/new.png"))
            if tpc_invertido!=None and tpc_venta!=None:
                if tpc_invertido<=-50:   
                    self.tblInvestments.item(i, 7).setBackground(QColor(255, 148, 148))
                if (tpc_venta<=5 and tpc_venta>0) or tpc_venta<0:
                    self.tblInvestments.item(i, 8).setBackground(QColor(148, 255, 148))
            i=i+1
        if suminvertido!=0:
            self.lblTotal.setText(self.tr("Invested assets: {0}. Pending: {1} - {2} = {3} ({4} assets)\nDaily Diff: {5}. Assets average age: {6}").format(self.mem.localcurrency.string(suminvertido), self.mem.localcurrency.string(sumpositivos),  self.mem.localcurrency.string(-sumnegativos),  self.mem.localcurrency.string(sumpendiente), tpc(100*sumpendiente/suminvertido) , self.mem.localcurrency.string( sumdiario), days_to_year_month(self.inversiones.average_age())))
        else:
            self.lblTotal.setText(self.tr("There aren't invested assets"))
            
    def tblInvestments_load_inactivas(self):
        """Función que carga la tabla de inversiones con el orden que tenga el arr serl.inversiones"""
        self.tblInvestments.setRowCount(len(self.inversiones.arr))
        self.tblInvestments.clearContents()
        for i, inv in enumerate(self.inversiones.arr):
            self.tblInvestments.setItem(i, 0, QTableWidgetItem("{0} ({1})".format(inv.name, inv.cuenta.name)))
            self.tblInvestments.setItem(i, 5, inv.product.currency.qtablewidgetitem(inv.balance()))

    @QtCore.pyqtSlot() 
    def on_actionActive_triggered(self):
        if self.selInvestment.cuenta.eb.qmessagebox_inactive()  or self.selInvestment.cuenta.qmessagebox_inactive():
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
            self.tblInvestments_reload_after_order()    
        else:
            qmessagebox_error_ordering()     
        
    @QtCore.pyqtSlot() 
    def on_actionSortTPCVenta_triggered(self):
        if self.inversiones.order_by_percentage_sellingpoint():
            self.tblInvestments_reload_after_order()    
        else:
            qmessagebox_error_ordering()     
        
    @QtCore.pyqtSlot() 
    def on_actionSortTPC_triggered(self):
        if self.inversiones.order_by_percentage_invested():
            self.tblInvestments_reload_after_order()    
        else:
            qmessagebox_error_ordering()     
        
    @QtCore.pyqtSlot() 
    def on_actionSortHour_triggered(self):
        if self.inversiones.order_by_datetime():
            self.tblInvestments_reload_after_order()    
        else:
            qmessagebox_error_ordering()     
        
    @QtCore.pyqtSlot() 
    def on_actionSortName_triggered(self):
        if self.inversiones.order_by_name():
            self.tblInvestments_reload_after_order()    
        else:
            qmessagebox_error_ordering()     
        
    def tblInvestments_reload_after_order(self):
        if self.chkInactivas.checkState()==Qt.Unchecked:
            self.tblInvestments_load()
        else:
            self.tblInvestments_load_inactivas()
        self.tblInvestments.clearSelection()
        self.selInvestment=None   
        
    def on_chkInactivas_stateChanged(self, state):
        if state==Qt.Unchecked:
            self.inversiones=self.mem.data.investments_active
            self.on_actionSortTPCVenta_triggered()
            self.tblInvestments_load()
        else:
            self.mem.data.load_inactives()
            self.inversiones=self.mem.data.investments_inactive
            self.on_actionSortName_triggered()
            self.tblInvestments_load_inactivas()
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
            myQTableWidget.on_cellDoubleClicked(self.tblInvestments, row, column)
