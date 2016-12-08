import datetime
from PyQt5.QtCore import QSize, Qt,  pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QDialog,  QMenu, QMessageBox,  QVBoxLayout
from Ui_frmInvestmentReport import Ui_frmInvestmentReport
from frmInvestmentOperationsAdd import frmInvestmentOperationsAdd
from frmDividendsAdd import frmDividendsAdd
from frmSellingPoint import frmSellingPoint
from frmQuotesIBM import frmQuotesIBM
from wdgDisReinvest import wdgDisReinvest
from frmSharesTransfer import frmSharesTransfer
from frmSplit import frmSplit
from libxulpymoney import Investment, Money, SetDividendsHomogeneus,  SetInvestmentOperationsHomogeneus,  days_to_year_month, tpc

class frmInvestmentReport(QDialog, Ui_frmInvestmentReport):
    frmInvestmentOperationsAdd_initiated=pyqtSignal(frmInvestmentOperationsAdd)#Se usa para cargar datos de ordenes en los datos de este formulario
    def __init__(self, mem, inversion=None,  parent=None):
        """Accounts es un set cuentas
        TIPOS DE ENTRADAS:        
         1  Inserción de Opercuentas
         2  Inversion=x"""
        QDialog.__init__(self, parent)
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.hide()
        self.setupUi(self)
        self.mem=mem
        self.inversion=inversion
        
        self.selDividend=None#Dividend seleccionado
        
        #arrays asociados a tablas
        self.op=None#Sera un SetInvestmentOperations
         
         
#        for o in self.inversion.op.arr:
#            print(o)
#        for o in self.inversion.op_actual.arr:
#            print(o)
#        for o in self.inversion.op_historica.arr:
#            print(o)
        
        self.ise.setupUi(self.mem,  self.inversion)
        
        self.dividends=SetDividendsHomogeneus(self.mem, self.inversion)
        
        self.tblDividends.settings(self.mem, "frmInvestmentReport")         
        self.tblDividendsAccountCurrency.settings(self.mem, "frmInvestmentReport")
        self.tblInvestmentCurrent.settings(self.mem, "frmInvestmentReport")
        self.tblInvestmentCurrentAccountCurrency.settings(self.mem, "frmInvestmentReport")
        self.tblOperations.settings(self.mem, "frmInvestmentReport")
        self.tblOperationsAccountCurrency.settings(self.mem, "frmInvestmentReport")
        self.tblInvestmentHistorical.settings(self.mem, "frmInvestmentReport")
        self.tblInvestmentHistoricalAccountCurrency.settings(self.mem,  "frmInvestmentReport")
        self.ise.cmd.released.connect(self.on_cmdISE_released)
        self.mem.data.accounts_active().qcombobox(self.cmbAccount)
        
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
            self.lblTitulo.setText(self.inversion.name)
            self.txtInvestment.setText(self.inversion.name)
            self.txtVenta.setText(self.inversion.venta)
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

        self.cmdInvestment.setEnabled(False)    
        self.showMaximized()
        QApplication.restoreOverrideCursor()

    def load_tabDividends(self):        
        (sumneto, sumbruto, sumretencion, sumcomision)=self.dividends.myqtablewidget(self.tblDividends)
        if self.inversion.account.currency==self.inversion.product.currency:
            self.grpDividendsAccountCurrency.hide()
        else:
            self.dividends.myqtablewidget(self.tblDividendsAccountCurrency, type=2)
        if self.chkHistoricalDividends.checkState()==Qt.Unchecked:
            if len(self.dividends.arr)>0 and len(self.inversion.op_actual.arr)>0:
                importeinvertido=self.inversion.invertido()
                dias=(datetime.date.today()-self.inversion.op_actual.first().datetime.date()).days+1
                dtpc=100*sumbruto.amount/importeinvertido.amount
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
            first=self.inversion.op_actual.first()
            if first==None:
                dt=self.mem.localzone.now()
            else:
                dt=first.datetime
            self.op=self.inversion.op.subSet_from_datetime(dt)
        else:
            self.op=self.inversion.op
        self.op.selected=None
        self.op.myqtablewidget(self.tblOperations)
        
        if self.inversion.product.currency==self.inversion.account.currency:#Multidivisa
            self.grpOperationsAccountCurrency.hide()
        else:
            self.op.myqtablewidget(self.tblOperationsAccountCurrency, type=2)
            
        
    def update_tables(self):             
        #Actualiza el indice de referencia porque ha cambiado
        self.inversion.op_actual.get_valor_benchmark(self.mem.data.benchmark)
        
        self.on_chkOperaciones_stateChanged(self.chkOperaciones.checkState())
        
        self.inversion.op_actual.myqtablewidget(self.tblInvestmentCurrent, self.inversion.product.result.basic.last, type=1)
        self.inversion.op_historica.myqtablewidget(self.tblInvestmentHistorical,  type=1 )
        if self.inversion.product.currency==self.inversion.account.currency:#Multidivisa
            self.grpCurrentAccountCurrency.hide()
            self.grpHistoricalAccountCurrency.hide()
        else:
            m=Money(self.mem, 1, self.inversion.account.currency)
            
            self.grpCurrentAccountCurrency.setTitle(self.tr("Current status in account currency ( {} = {} at {} )").format(m.string(6), m.convert(self.inversion.product.currency, self.mem.localzone.now()).string(6), m.conversionDatetime(self.inversion.product.currency, self.mem.localzone.now())))
            self.inversion.op_actual.myqtablewidget(self.tblInvestmentCurrentAccountCurrency, self.inversion.product.result.basic.last,  type=2)
            self.inversion.op_historica.myqtablewidget(self.tblInvestmentHistoricalAccountCurrency, type=2 )
        
        self.lblAge.setText(self.tr("Current operations average age: {0}".format(days_to_year_month(self.inversion.op_actual.average_age()))))
        
        if self.inversion!=None:#We are adding a new investment
            if self.inversion.merge==0:
                self.on_chkHistoricalDividends_stateChanged(self.chkHistoricalDividends.checkState())
            else:
                self.chkHistoricalDividends.setChecked(Qt.Checked)
                self.chkHistoricalDividends.setEnabled(False)
    

    @pyqtSlot() 
    def on_actionDividendAdd_triggered(self):
        w=frmDividendsAdd(self.mem, self.inversion,  None)
        w.exec_()
        self.on_chkHistoricalDividends_stateChanged(self.chkHistoricalDividends.checkState())

        
    @pyqtSlot() 
    def on_actionDividendEdit_triggered(self):
        w=frmDividendsAdd(self.mem, self.inversion, self.selDividend)
        w.exec_()
        self.on_chkHistoricalDividends_stateChanged(self.chkHistoricalDividends.checkState())

        
    @pyqtSlot() 
    def on_actionDividendRemove_triggered(self):
        self.selDividend.borrar()
        self.mem.con.commit()
        self.on_chkHistoricalDividends_stateChanged(self.chkHistoricalDividends.checkState())

    @pyqtSlot() 
    def on_actionChangeBenchmarkPrice_triggered(self):
        w=frmQuotesIBM(self.mem, self.mem.data.benchmark, self.inversion.op_actual.selected.referenciaindice, self)
        w.txtQuote.setFocus()
        w.exec_() 
        self.update_tables()

    @pyqtSlot() 
    def on_actionDisReinvest_triggered(self):
        d=QDialog()       
        d.resize(self.mem.settings.value("frmInvestmentReport/qdialog_disreinvest", QSize(1024, 768)))
        d.setWindowTitle(self.tr("Divest / Reinvest simulation"))
        w=wdgDisReinvest(self.mem, self.inversion, False, d)
        lay = QVBoxLayout(d)
        lay.addWidget(w)
        d.exec_()
        self.mem.settings.setValue("frmInvestmentReport/qdialog_disreinvest", d.size())
        
    @pyqtSlot() 
    def on_actionDisReinvestProduct_triggered(self):
        d=QDialog()       
        d.resize(self.mem.settings.value("frmInvestmentReport/qdialog_disreinvest", QSize(1024, 768)))
        d.setWindowTitle(self.tr("Divest / Reinvest simulation"))
        w=wdgDisReinvest(self.mem, self.inversion, True,  d)
        lay = QVBoxLayout(d)
        lay.addWidget(w)
        d.exec_()
        self.mem.settings.setValue("frmInvestmentReport/qdialog_disreinvest", d.size())
        
    @pyqtSlot() 
    def on_actionOperationAdd_triggered(self):
        if self.inversion.product.result.basic.last.quote==None:
            m=QMessageBox()
            m.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
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
        self.frmInvestmentOperationsAdd_initiated.emit(w)
        w.exec_()
        
        #if num shares after add is 0, changes expiration date to today-1
        if self.inversion.acciones()==0:
            self.calExpiration.setSelectedDate(datetime.date.today()-datetime.timedelta(days=1))
            self.on_cmdInvestment_released()
            
        self.update_tables()    
        
    @pyqtSlot() 
    def on_actionOperationEdit_triggered(self):
        w=frmInvestmentOperationsAdd(self.mem, self.inversion, self.op.selected, self)
        w.exec_()
        self.update_tables() 
        
        #if num shares after add is 0, changes expiration date to today-1
        if self.inversion.acciones()==0:
            self.calExpiration.setSelectedDate(datetime.date.today()-datetime.timedelta(days=1))
            self.on_cmdInvestment_released()

    @pyqtSlot() 
    def on_actionSplit_triggered(self):
        w=frmSplit(self.mem, self.inversion.product)
        w.exec_()   
        if w.result()==QDialog.Accepted:
            self.update_tables()
        
    @pyqtSlot() 
    def on_actionSharesTransfer_triggered(self):
        w=frmSharesTransfer(self.mem, self.inversion, self)
        w.exec_()
        
        #if num shares after add is 0, changes expiration date to today-1
        if self.inversion.acciones()==0:
            self.calExpiration.setSelectedDate(datetime.date.today()-datetime.timedelta(days=1))
            self.on_cmdInvestment_released()
        
        self.update_tables()                 
    
    @pyqtSlot() 
    def on_actionRangeReport_triggered(self):
        self.op.selected.show_in_ranges= not self.op.selected.show_in_ranges
        self.op.selected.save()
        self.mem.con.commit()
        #self.op doesn't belong to self.mem.data, it's a set of this widget, so I need to reload investment of the self.mem.data
        self.mem.data.investments.find_by_id(self.inversion.id).get_operinversiones()
        self.update_tables()

    @pyqtSlot() 
    def on_actionSharesTransferUndo_triggered(self):
        if self.mem.data.investments_active().traspaso_valores_deshacer(self.op.selected)==False:
            m=QMessageBox()
            m.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
            m.setIcon(QMessageBox.Information)
            m.setText(self.tr("Shares transfer couldn't be done."))
            m.exec_()          
            return
        self.update_tables()       

    @pyqtSlot() 
    def on_cmdPuntoVenta_released(self):
        f=frmSellingPoint(self.mem, self.inversion)
        f.txtPrice.setText(self.txtVenta.text())
        f.exec_()
        self.txtVenta.setText(str(f.puntoventa.round(6)))

    @pyqtSlot() 
    def on_actionOperationDelete_triggered(self):
        self.inversion.op.remove(self.op.selected)#debe borrarse de self.inversion.op, no de self.op, ya qque self.update_tables reescribe clone_from_datetime
        self.mem.con.commit()     
        
        #if num shares after add is 0, changes expiration date to today-1
        if self.inversion.acciones()==0:
            self.calExpiration.setSelectedDate(datetime.date.today()-datetime.timedelta(days=1))
            self.on_cmdInvestment_released()
        
        self.update_tables()

        
        
    def on_chkHistoricalDividends_stateChanged(self, state):
        self.tblDividends.clearSelection()
        self.tblDividendsAccountCurrency.clearSelection()
        self.selDividend=None        
        if self.inversion.merge==0:
            if state==Qt.Unchecked:   
                self.dividends=self.inversion.setDividends_from_current_operations()
            elif state==Qt.Checked:
                self.dividends=self.inversion.setDividends_from_operations()
            else:
                self.dividends.clean()
        elif self.inversion.merge==1:
            self.dividends=self.mem.data.investments_active().setDividends_merging_current_operation_dividends(self.inversion.product)
        elif self.inversion.merge==2:
            self.dividends=self.mem.data.investments.setDividends_merging_operation_dividends(self.inversion.product)
        self.load_tabDividends()

    def on_cmdISE_released(self):
        self.cmdInvestment.setEnabled(True)
    def on_txtVenta_textChanged(self):
        self.cmdInvestment.setEnabled(True)
    def on_txtInvestment_textChanged(self):
        self.cmdInvestment.setEnabled(True)
    def on_cmbTipoInvestment_currentIndexChanged(self, index):
        self.cmdInvestment.setEnabled(True)
    def on_calExpiration_selectionChanged(self):
        self.cmdInvestment.setEnabled(True)
    def on_chkExpiration_stateChanged(self, state):
        self.cmdInvestment.setEnabled(True)
        
    def on_cmdToday_released(self):
        self.calExpiration.setSelectedDate(datetime.date.today())
            
    def on_cmdInvestment_released(self):
        if self.ise.selected==None:
            m=QMessageBox()
            m.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
            m.setIcon(QMessageBox.Information)
            m.setText(self.tr("You must select a product to continue."))
            m.exec_()     
            return
        inversion=self.txtInvestment.text()
        venta=self.txtVenta.decimal()
        id_cuentas=int(self.cmbAccount.itemData(self.cmbAccount.currentIndex()))
        product=self.ise.selected
        if self.chkExpiration.checkState()==Qt.Unchecked:
            expiration=None
        else:
            expiration=self.calExpiration.selectedDate().toPyDate()

        if self.mem.data.products.find_by_id(product.id)==None:
            print ("Cargando otro producto en mem")
            product.estimations_dps.load_from_db()
            product.result.basic.load_from_db()
            self.mem.data.products.append(product)        

        if self.tipo==1:        #insertar
            self.inversion=Investment(self.mem).init__create(inversion,   venta,  self.mem.data.accounts_active().find_by_id(id_cuentas), product, expiration, True)      
            self.inversion.save()
            self.mem.con.commit()    
            #Lo añade con las operaciones vacias pero calculadas.
            self.inversion.op=SetInvestmentOperationsHomogeneus(self.mem, self.inversion)
            (self.inversion.op_actual, self.inversion.op_historica)=self.inversion.op.calcular()
            self.mem.data.investments.append(self.inversion)
            self.done(0)
        elif self.tipo==2:
            self.inversion.name=inversion
            self.inversion.venta=venta
            self.inversion.product=product
            self.inversion.selling_expiration=expiration
            self.inversion.save()##El id y el id_cuentas no se pueden modificar
            self.mem.con.commit()
            self.cmdInvestment.setEnabled(False)
        
    def on_tblOperations_customContextMenuRequested(self,  pos):
        if self.inversion.qmessagebox_inactive() or self.inversion.account.qmessagebox_inactive()or self.inversion.account.eb.qmessagebox_inactive():
            return
        
        if self.op.selected==None:
            self.actionOperationDelete.setEnabled(False)
            self.actionOperationEdit.setEnabled(False)
            self.actionRangeReport.setEnabled(False)
        else:
            if self.op.selected.tipooperacion.id==10:#Traspaso valores destino
                self.actionOperationDelete.setEnabled(False)
                self.actionOperationEdit.setEnabled(False)
            else:
                self.actionOperationDelete.setEnabled(True)
                self.actionOperationEdit.setEnabled(True)
            self.actionRangeReport.setEnabled(True)

        menu=QMenu()
        menu.addAction(self.actionOperationAdd)
        
        menu.addAction(self.actionOperationEdit)
        menu.addAction(self.actionOperationDelete)
        
        if self.op.selected!=None:
            if self.op.selected.tipooperacion.id==9:#Traspaso valores origen
                menu.addSeparator()
                menu.addAction(self.actionSharesTransferUndo)
                
        menu.addSeparator()
        menu.addAction(self.actionRangeReport)
        menu.addSeparator()
        menu.addAction(self.actionSplit)
        menu.exec_(self.tblOperations.mapToGlobal(pos))
        
    def on_tblInvestmentCurrent_itemSelectionChanged(self):
        self.inversion.op_actual.selected=None
        try:
            for i in self.tblInvestmentCurrent.selectedItems():#itera por cada item no row.
                if i.row()<self.inversion.op_actual.length():#Due to total file
                    self.inversion.op_actual.selected=self.inversion.op_actual.arr[i.row()]
        except:
            self.inversion.op_actual.selected=None
        print (self.tr("Selected: {0}".format(str(self.inversion.op_actual.selected))))
        
        
    def on_tblInvestmentCurrent_customContextMenuRequested(self,  pos):
        
        if self.inversion.qmessagebox_inactive() or self.inversion.account.qmessagebox_inactive() or self.inversion.account.eb.qmessagebox_inactive():
            return
                
        if self.inversion.op_actual.selected:
            self.actionChangeBenchmarkPrice.setEnabled(True)
        else:
            self.actionChangeBenchmarkPrice.setEnabled(False)
            
        menu=QMenu()
        menu.addAction(self.actionDisReinvest)
        menu.addAction(self.actionDisReinvestProduct)
        menu.addSeparator()
        menu.addAction(self.actionOperationAdd)
        menu.addSeparator()
        menu.addAction(self.actionSharesTransfer)
        menu.addSeparator()
        menu.addAction(self.actionChangeBenchmarkPrice)
        
        
        menu.exec_(self.tblInvestmentCurrent.mapToGlobal(pos))


    def on_tblOperations_itemSelectionChanged(self):
        self.op.selected=None
        try:
            for i in self.tblOperations.selectedItems():#itera por cada item no row.
                self.op.selected=self.op.arr[i.row()]
                if self.op.selected.show_in_ranges==True:
                    self.actionRangeReport.setText(self.tr("Hide in range report"))
                    self.actionRangeReport.setIcon(QIcon(":/xulpymoney/eye_red.png"))
                else:
                    self.actionRangeReport.setText(self.tr("Show in range report"))
                    self.actionRangeReport.setIcon(QIcon(":/xulpymoney/eye.png"))
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

