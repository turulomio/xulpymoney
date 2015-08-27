from PyQt5.QtCore import *
from PyQt5.QtGui import *
from Ui_frmInvestmentReport import *
from frmInvestmentOperationsAdd import *
from frmDividendsAdd import *
from frmSellingPoint import *
from wdgDisReinvest import *
from frmSharesTransfer import *
from libxulpymoney import *

class frmInvestmentReport(QDialog, Ui_frmInvestmentReport):
    def __init__(self, mem, inversion=None,  parent=None):
        """Accounts es un set cuentas"""
        """TIPOS DE ENTRADAS:        
         1   : Inserción de Opercuentas
         2   inversion=x"""
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.showMaximized()
        self.mem=mem
        self.inversion=inversion
        
        self.selDividend=None#Dividend seleccionado
        
        #arrays asociados a tablas
        self.op=None#Sera un SetInvestmentOperations
        self.dividends=SetDividends(self.mem)
        self.mem.data.load_inactives()
        
        self.ise.setupUi(self.mem,  self.inversion)
        self.tblDividends.settings("frmInvestmentReport",  self.mem)
        self.cmdInvestment.setEnabled(False)                                     
        self.ise.cmd.released.connect(self.on_cmdISE_released)
        self.mem.data.accounts_active.qcombobox(self.cmbAccount)
        
        if self.inversion==None:
            self.tipo=1
            self.cmdInvestment.setText(self.tr("Add a new investment"))
            self.lblTitulo.setText(self.tr("New investment"))
            self.inversion=None
            self.tab.setCurrentIndex(0)
            self.tabDividends.setEnabled(False)
            self.tabOperacionesHistoricas.setEnabled(False)
            self.tabInvestmentCurrent.setEnabled(False)
            self.ise.setSelected(None)
            self.cmdPuntoVenta.setEnabled(False)
        else:
            self.tipo=2    
            self.tab.setCurrentIndex(1)
            self.lblTitulo.setText((self.inversion.name))
            self.txtInvestment.setText((self.inversion.name))
            self.txtVenta.setText(str((self.inversion.venta)))
            if self.inversion.selling_expiration==None:
                self.chkExpiration.setCheckState(Qt.Unchecked)
            else:
                self.chkExpiration.setCheckState(Qt.Checked)
                self.calExpiration.setSelectedDate(self.inversion.selling_expiration)
            self.ise.setSelected(self.inversion.product)
            self.cmdPuntoVenta.setEnabled(True)
            self.cmbAccount.setCurrentIndex(self.cmbAccount.findData(self.inversion.account.id))
            self.update_tables()      
            if len(self.op.arr)!=0 or len(self.dividends.arr)!=0:#CmbAccount está desabilitado si hay dividends o operinversiones
                self.cmbAccount.setEnabled(False)  

    def load_tabDividends(self):        
        (sumneto, sumbruto, sumretencion, sumcomision)=self.dividends.myqtablewidget(self.tblDividends, "frmInvestmentReport")
        if self.chkHistoricalDividends.checkState()==Qt.Unchecked:
            if len(self.dividends.arr)>0 and len(self.inversion.op_actual.arr)>0:
                importeinvertido=self.inversion.invertido()
                dias=(datetime.date.today()-self.inversion.op_actual.datetime_first_operation().date()).days+1
                dtpc=100*sumbruto/importeinvertido
                dtae=365*dtpc/abs(dias)
            else:
                dtpc=0
                dtae=0
            
            estimacion=self.inversion.product.estimations_dps.currentYear()
            if estimacion.estimation!=None:
                acciones=self.inversion.acciones()
                tpccalculado=100*estimacion.estimation/self.inversion.product.result.basic.last.quote
                self.lblDivFechaRevision.setText(self.tr('Estimation review date: {0}').format(estimacion.date_estimation))
                self.lblDivAnualEstimado.setText(self.tr("Estimated annual dividend is {0} ({1} per share)").format(tpc(tpccalculado),  self.inversion.product.currency.string(estimacion.estimation)))
                self.lblDivSaldoEstimado.setText(self.tr("Estimated balance: {0} ({1} after taxes)").format( self.inversion.product.currency.string(acciones*estimacion.estimation),  self.inversion.product.currency.string(acciones*estimacion.estimation*(1-self.mem.dividendwithholding))))
            self.lblDivTPC.setText(self.tr("% Invested: {0}").format(tpc(dtpc)))
            self.lblDivTAE.setText(self.tr("% APR from invested: {0}").format(tpc(dtae)))
            self.grpDividendsEstimation.show()
            self.grpDividendsEfectivos.show()
        else:
            self.grpDividendsEstimation.hide()
            self.grpDividendsEfectivos.hide()
       
    def on_chkOperaciones_stateChanged(self, state):
        if state==Qt.Unchecked:
            primera=self.inversion.op_actual.datetime_first_operation()
            if primera==None:
                primera=self.mem.localzone.now()
            self.op=self.inversion.op.clone_from_datetime(primera)
        else:
            self.op=self.inversion.op
        self.op.selected=None
        self.op.myqtablewidget(self.tblOperaciones, "frmInvestmentReport")
            
        
    def update_tables(self):             
        #Actualiza el indice de referencia porque ha cambiado
        self.inversion.op_actual.get_valor_benchmark(self.mem.data.benchmark)
        self.on_chkOperaciones_stateChanged(self.chkOperaciones.checkState())
        self.inversion.op_actual.myqtablewidget(self.tblInvestmentCurrent,  "frmInvestmentReport")
        self.lblAge.setText(self.tr("Current operations average age: {0}".format(days_to_year_month(self.inversion.op_actual.average_age()))))
        self.inversion.op_historica.myqtablewidget(self.tblInvestmentHistorical,  "frmInvestmentReport"  )
        if self.inversion!=None:#We are adding a new investment
            self.on_chkHistoricalDividends_stateChanged(self.chkHistoricalDividends.checkState())
    

    @QtCore.pyqtSlot() 
    def on_actionDividendAdd_triggered(self):
        w=frmDividendsAdd(self.mem, self.inversion,  None)
        w.exec_()
        self.on_chkHistoricalDividends_stateChanged(self.chkHistoricalDividends.checkState())

        
    @QtCore.pyqtSlot() 
    def on_actionDividendEdit_triggered(self):
        w=frmDividendsAdd(self.mem, self.inversion, self.selDividend)
        w.exec_()
        self.on_chkHistoricalDividends_stateChanged(self.chkHistoricalDividends.checkState())

        
    @QtCore.pyqtSlot() 
    def on_actionDividendRemove_triggered(self):
        self.selDividend.borrar()
        self.mem.con.commit()
        self.on_chkHistoricalDividends_stateChanged(self.chkHistoricalDividends.checkState())

    @QtCore.pyqtSlot() 
    def on_actionDisReinvest_triggered(self):
        d=QDialog()       
        d.showMaximized()
        d.setWindowTitle(self.tr("Divest / Reinvest simulation"))
        w=wdgDisReinvest(self.mem, self.inversion, d)
        lay = QVBoxLayout(d)
        lay.addWidget(w)
        d.exec_()
        
    @QtCore.pyqtSlot() 
    def on_actionOperationAdd_triggered(self):
        if self.inversion.product.result.basic.last.quote==None:
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.tr("Before adding a operation, you must add the current price of the product."))
            m.exec_()    
            w=frmQuotesIBM(self.mem,  self.inversion.product)
            w.exec_()   
            if w.result()==QDialog.Accepted:
                self.inversion.product.result.basic.load_from_db()
            else:
                return
            
        w=frmInvestmentOperationsAdd(self.mem, self.inversion, None, self)
        w.exec_()
        self.update_tables()    
        
    @QtCore.pyqtSlot() 
    def on_actionOperationEdit_triggered(self):
        w=frmInvestmentOperationsAdd(self.mem, self.inversion, self.op.selected, self)
        w.exec_()
        self.update_tables() 

    @QtCore.pyqtSlot() 
    def on_actionSplit_triggered(self):
        w=frmSplit(self.mem, self.inversion.product)
        w.exec_()   
        if w.result()==QDialog.Accepted:
            self.update_tables()
        
    @QtCore.pyqtSlot() 
    def on_actionSharesTransfer_triggered(self):
        w=frmSharesTransfer(self.mem, self.inversion, self)
        w.exec_()
        self.update_tables()                 
        
    @QtCore.pyqtSlot() 
    def on_actionSharesTransferUndo_triggered(self):
        if self.mem.data.investments_active.traspaso_valores_deshacer(self.op.selected)==False:
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.tr("Shares transfer couldn't be done."))
            m.exec_()          
            return
        self.update_tables()       

    @QtCore.pyqtSlot() 
    def on_cmdPuntoVenta_released(self):
        f=frmSellingPoint(self.mem, self.inversion)
        f.txtPrice.setText(self.txtVenta.text())
        f.exec_()
        self.txtVenta.setText(str(f.puntoventa))

    @QtCore.pyqtSlot() 
    def on_actionOperationDelete_triggered(self):
        self.inversion.op.remove(self.op.selected)#debe borrarse de self.inversion.op, no de self.op, ya qque self.update_tables reescribe clone_from_datetime
        self.mem.con.commit()     
        self.update_tables()

    def on_chkHistoricalDividends_stateChanged(self, state):
        dtfo=self.inversion.op_actual.datetime_first_operation()
        self.tblDividends.clearSelection()
        self.selDividend=None        

        if state==Qt.Unchecked and dtfo!=None:   
            self.dividends.load_from_db("select * from dividends where id_inversiones={0} and fecha >='{1}'  order by fecha".format(self.inversion.id, dtfo.date()))
        elif state==Qt.Checked:
            self.dividends.load_from_db("select * from dividends where id_inversiones={0} order by fecha".format(self.inversion.id ))  
        else:
            self.dividends.clean()
        self.load_tabDividends()

    def on_cmdISE_released(self):
        self.cmdInvestment.setEnabled(True)
    def on_txtVenta_textChanged(self):
        self.cmdInvestment.setEnabled(True)
    def on_txtInvestment_textChanged(self):
        self.cmdInvestment.setEnabled(True)
    def on_cmbTipoInvestment_currentIndexChanged(self, index):
        self.cmdInvestment.setEnabled(True)
        

            
    def on_cmdInvestment_released(self):
        if self.ise.selected==None:
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.tr("You must select a product to continue."))
            m.exec_()     
            return
        inversion=self.txtInvestment.text()
        venta=self.txtVenta.decimal()
        id_cuentas=int(self.cmbAccount.itemData(self.cmbAccount.currentIndex()))
        products_id=int(self.ise.selected.id) 
        if self.chkExpiration.checkState()==Qt.Unchecked:
            expiration=None
        else:
            expiration=self.calExpiration.selectedDate().toPyDate()
        
        
        if self.mem.data.products_active.find(products_id)==None:
            print ("Cargando otro mqinversiones")
            inv=Product(self.mem).init__db(products_id)
            inv.estimations_dps.load_from_db()
            inv.result.basic.load_from_db()
            self.mem.data.products_active.append(inv)
            
        

        if self.tipo==1:        #insertar
            i=Investment(self.mem).create(inversion,   venta,  self.mem.data.accounts_active.find(id_cuentas), expiration, self.mem.data.products_active.find(products_id))      
            i.save()
            self.mem.con.commit()
            ##Se añade a mem y vincula. No carga datos porque products_id debe existir            
            #Lo añade con las operaciones vacias pero calculadas.
            i.op=SetInvestmentOperations(self.mem)
            (i.op_actual, i.op_historica)=i.op.calcular()
            self.mem.data.investments_active.append(i)
            self.done(0)
        elif self.tipo==2:
            self.inversion.name=inversion
            self.inversion.venta=venta
            self.inversion.product=self.mem.data.products_active.find(products_id)
            self.inversion.selling_expiration=expiration
            self.inversion.save()##El id y el id_cuentas no se pueden modificar
            self.mem.con.commit()
            self.cmdInvestment.setEnabled(False)
        
    def on_tblOperaciones_customContextMenuRequested(self,  pos):
        if self.inversion.qmessagebox_inactive() or self.inversion.account.qmessagebox_inactive()or self.inversion.account.eb.qmessagebox_inactive():
            return
        
        if self.op.selected==None:
            self.actionOperationDelete.setEnabled(False)
            self.actionOperationEdit.setEnabled(False)
        else:
            if self.op.selected.tipooperacion.id==10:#Traspaso valores destino
                self.actionOperationDelete.setEnabled(False)
                self.actionOperationEdit.setEnabled(False)
            else:
                self.actionOperationDelete.setEnabled(True)
                self.actionOperationEdit.setEnabled(True)
            
            
        menu=QMenu()
        menu.addAction(self.actionOperationAdd)
        
        menu.addAction(self.actionOperationEdit)
        menu.addAction(self.actionOperationDelete)
        
        if self.op.selected!=None:
            if self.op.selected.tipooperacion.id==9:#Traspaso valores origen
                menu.addSeparator()
                menu.addAction(self.actionSharesTransferUndo)
                
        menu.addSeparator()
        menu.addAction(self.actionSplit)
        menu.exec_(self.tblOperaciones.mapToGlobal(pos))

    def on_tblInvestmentCurrent_customContextMenuRequested(self,  pos):
        
        if self.inversion.qmessagebox_inactive() or self.inversion.account.qmessagebox_inactive() or self.inversion.account.eb.qmessagebox_inactive():
            return
        menu=QMenu()
        menu.addAction(self.actionDisReinvest)
        menu.addSeparator()
        menu.addAction(self.actionOperationAdd)
        menu.addSeparator()
        menu.addAction(self.actionSharesTransfer)
        
        
        menu.exec_(self.tblInvestmentCurrent.mapToGlobal(pos))


    def on_tblOperaciones_itemSelectionChanged(self):
        try:
            for i in self.tblOperaciones.selectedItems():#itera por cada item no row.
                self.op.selected=self.op.arr[i.row()]
        except:
            self.op.selected=None
        print (self.tr("Selected: {0}".format(str(self.op.selected))))
        
        
    def on_tblDividends_customContextMenuRequested(self,  pos):
        if self.inversion.qmessagebox_inactive() or self.inversion.account.qmessagebox_inactive() or self.inversion.account.eb.qmessagebox_inactive():
            return
        
        if self.selDividend==None:
            self.actionDividendRemove.setEnabled(False)
            self.actionDividendEdit.setEnabled(False)
        else:
            self.actionDividendRemove.setEnabled(True)
            self.actionDividendEdit.setEnabled(True)
            
        menu=QMenu()
        menu.addAction(self.actionDividendAdd)
        menu.addAction(self.actionDividendRemove)
        menu.addAction(self.actionDividendEdit)
        menu.exec_(self.tblDividends.mapToGlobal(pos))

    def on_tblDividends_itemSelectionChanged(self):
        try:
            for i in self.tblDividends.selectedItems():#itera por cada item no rowse.
                self.selDividend=self.dividends.arr[i.row()]
        except:
            self.selDividend=None
        print ("Dividend selected: " +  str(self.selDividend))        

