import datetime
from PyQt5.QtCore import QSize, Qt,  pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QDialog,  QMenu, QMessageBox,  QVBoxLayout
from xulpymoney.ui.Ui_frmInvestmentReport import Ui_frmInvestmentReport
from xulpymoney.ui.frmInvestmentOperationsAdd import frmInvestmentOperationsAdd
from xulpymoney.ui.frmDividendsAdd import frmDividendsAdd
from xulpymoney.ui.frmSellingPoint import frmSellingPoint
from xulpymoney.ui.frmQuotesIBM import frmQuotesIBM
from xulpymoney.ui.wdgDisReinvest import wdgDisReinvest
from xulpymoney.ui.frmSharesTransfer import frmSharesTransfer
from xulpymoney.ui.frmSplit import frmSplit
from xulpymoney.libxulpymoney import Investment, Money, Percentage, DividendHomogeneusManager,  InvestmentOperationHomogeneusManager,  days2string

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
        self.investment=inversion
        
        self.selDividend=None#Dividend seleccionado
        
        #arrays asociados a tablas
        self.op=None#Sera un SetInvestmentOperations
         
        self.ise.setupUi(self.mem,  self.investment)
        
        self.dividends=DividendHomogeneusManager(self.mem, self.investment)
        
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
        
        if self.investment==None:
            self.tipo=1
            self.cmdInvestment.setText(self.tr("Add a new investment"))
            self.lblTitulo.setText(self.tr("New investment"))
            self.investment=None
            self.tab.setCurrentIndex(0)
            self.tabDividends.setEnabled(False)
            self.tabOperacionesHistoricas.setEnabled(False)
            self.tabInvestmentCurrent.setEnabled(False)
            self.ise.setSelected(None)
            self.cmdPuntoVenta.setEnabled(False)
        else:
            self.tipo=2    
            self.tab.setCurrentIndex(1)
            self.lblTitulo.setText(self.investment.name)
            self.txtInvestment.setText(self.investment.name)
            self.txtVenta.setText(self.investment.venta)
            if self.investment.selling_expiration==None:
                self.chkExpiration.setCheckState(Qt.Unchecked)
            else:
                self.chkExpiration.setCheckState(Qt.Checked)
                self.calExpiration.setSelectedDate(self.investment.selling_expiration)
            self.ise.setSelected(self.investment.product)
            self.cmdPuntoVenta.setEnabled(True)
            self.cmbAccount.setCurrentIndex(self.cmbAccount.findData(self.investment.account.id))
            self.update_tables()      
            if len(self.op.arr)!=0 or len(self.dividends.arr)!=0:#CmbAccount está desabilitado si hay dividends o operinversiones
                self.cmbAccount.setEnabled(False)  

        self.cmdInvestment.setEnabled(False)    
        self.showMaximized()
        QApplication.restoreOverrideCursor()

    def load_tabDividends(self):        
        (sumneto, sumbruto, sumretencion, sumcomision)=self.dividends.myqtablewidget(self.tblDividends)
        if self.investment.account.currency==self.investment.product.currency:
            self.grpDividendsAccountCurrency.hide()
        else:
            self.dividends.myqtablewidget(self.tblDividendsAccountCurrency, type=2)
        if self.chkHistoricalDividends.checkState()==Qt.Unchecked:
            estimacion=self.investment.product.estimations_dps.currentYear()
            if estimacion.estimation!=None:
                acciones=self.investment.shares()
                tpccalculado=Percentage(estimacion.estimation, self.investment.product.result.basic.last.quote)
                self.lblDivFechaRevision.setText(self.tr('Estimation review date: {0}').format(estimacion.date_estimation))
                self.lblDivAnualEstimado.setText(self.tr("Estimated annual dividend is {0} ({1} per share)").format(tpccalculado,  self.investment.product.currency.string(estimacion.estimation)))
                self.lblDivSaldoEstimado.setText(self.tr("Estimated balance: {0} ({1} after taxes)").format( self.investment.product.currency.string(acciones*estimacion.estimation),  self.investment.product.currency.string(acciones*estimacion.estimation*(1-self.mem.dividendwithholding))))
            self.lblDivTPC.setText(self.tr("% Invested: {}").format(self.dividends.percentage_from_invested(type=1)))
            self.lblDivTAE.setText(self.tr("% APR from invested: {}").format(self.dividends.percentage_tae_from_invested(type=1)))
            self.grpDividendsEstimation.show()
            self.grpDividendsEfectivos.show()
        else:
            self.grpDividendsEstimation.hide()
            self.grpDividendsEfectivos.hide()
       
    def on_chkOperaciones_stateChanged(self, state):
        if state==Qt.Unchecked:
            first=self.investment.op_actual.first()
            if first==None:
                dt=self.mem.localzone.now()
            else:
                dt=first.datetime
            self.op=self.investment.op.subSet_from_datetime(dt, self.mem, self.investment)
        else:
            self.op=self.investment.op
            
        self.op.selected=None
        self.op.myqtablewidget(self.tblOperations)
        
        if self.investment.product.currency==self.investment.account.currency:#Multidivisa
            self.grpOperationsAccountCurrency.hide()
        else:
            self.op.myqtablewidget(self.tblOperationsAccountCurrency, type=2)

    def update_tables(self):             
        #Actualiza el indice de referencia porque ha cambiado
        self.investment.op_actual.get_valor_benchmark(self.mem.data.benchmark)
        
        if self.investment.merge==0:
            self.on_chkOperaciones_stateChanged(self.chkOperaciones.checkState())
            self.chkOperaciones.setEnabled(True)
        else:#merge 1 y 2
            self.chkOperaciones.setChecked(Qt.Checked)
            self.chkOperaciones.setEnabled(False)
        
        self.investment.op_actual.myqtablewidget(self.tblInvestmentCurrent, self.investment.product.result.basic.last, type=1)
        self.investment.op_historica.myqtablewidget(self.tblInvestmentHistorical,  type=1 )
        if self.investment.product.currency==self.investment.account.currency:#Multidivisa
            self.grpCurrentAccountCurrency.hide()
            self.grpHistoricalAccountCurrency.hide()
        else:
            m=Money(self.mem, 1, self.investment.account.currency)
            
            self.grpCurrentAccountCurrency.setTitle(self.tr("Current status in account currency ( {} = {} at {} )").format(m.string(6), m.convert(self.investment.product.currency, self.mem.localzone.now()).string(6), m.conversionDatetime(self.investment.product.currency, self.mem.localzone.now())))
            self.investment.op_actual.myqtablewidget(self.tblInvestmentCurrentAccountCurrency, self.investment.product.result.basic.last,  type=2)
            self.investment.op_historica.myqtablewidget(self.tblInvestmentHistoricalAccountCurrency, type=2 )
        
        self.lblAge.setText(self.tr("Current operations average age: {0}".format(days2string(self.investment.op_actual.average_age()))))
        
        if self.investment!=None:#We are adding a new investment
            if self.investment.merge==0:
                self.on_chkHistoricalDividends_stateChanged(self.chkHistoricalDividends.checkState())
                self.chkHistoricalDividends.setEnabled(True)
            else:
                self.chkHistoricalDividends.setChecked(Qt.Checked)
                self.chkHistoricalDividends.setEnabled(False)
    

    @pyqtSlot() 
    def on_actionDividendAdd_triggered(self):
        w=frmDividendsAdd(self.mem, self.investment,  None)
        w.exec_()
        self.on_chkHistoricalDividends_stateChanged(self.chkHistoricalDividends.checkState())

        
    @pyqtSlot() 
    def on_actionDividendEdit_triggered(self):
        w=frmDividendsAdd(self.mem, self.investment, self.selDividend)
        w.exec_()
        self.on_chkHistoricalDividends_stateChanged(self.chkHistoricalDividends.checkState())

        
    @pyqtSlot() 
    def on_actionDividendRemove_triggered(self):
        self.selDividend.borrar()
        self.mem.con.commit()
        self.on_chkHistoricalDividends_stateChanged(self.chkHistoricalDividends.checkState())

    @pyqtSlot() 
    def on_actionChangeBenchmarkPrice_triggered(self):
        w=frmQuotesIBM(self.mem, self.mem.data.benchmark, self.investment.op_actual.selected.referenciaindice, self)
        w.txtQuote.setFocus()
        w.exec_() 
        self.update_tables()

    @pyqtSlot() 
    def on_actionDisReinvest_triggered(self):
        d=QDialog()       
        d.resize(self.mem.settings.value("frmInvestmentReport/qdialog_disreinvest", QSize(1024, 768)))
        d.setWindowTitle(self.tr("Divest / Reinvest simulation"))
        w=wdgDisReinvest(self.mem, self.investment, False, d)
        lay = QVBoxLayout(d)
        lay.addWidget(w)
        d.exec_()
        self.mem.settings.setValue("frmInvestmentReport/qdialog_disreinvest", d.size())
        
    @pyqtSlot() 
    def on_actionDisReinvestProduct_triggered(self):
        d=QDialog()       
        d.resize(self.mem.settings.value("frmInvestmentReport/qdialog_disreinvest", QSize(1024, 768)))
        d.setWindowTitle(self.tr("Divest / Reinvest simulation"))
        w=wdgDisReinvest(self.mem, self.investment, True,  d)
        lay = QVBoxLayout(d)
        lay.addWidget(w)
        d.exec_()
        self.mem.settings.setValue("frmInvestmentReport/qdialog_disreinvest", d.size())
        
    @pyqtSlot() 
    def on_actionOperationAdd_triggered(self):
        if self.investment.product.result.basic.last.quote==None:
            m=QMessageBox()
            m.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
            m.setIcon(QMessageBox.Information)
            m.setText(self.tr("Before adding a operation, you must add the current price of the product."))
            m.exec_()    
            w=frmQuotesIBM(self.mem,  self.investment.product)
            w.exec_()   
            if w.result()==QDialog.Accepted:
                self.investment.product.result.basic.load_from_db()
            else:
                return
            
        w=frmInvestmentOperationsAdd(self.mem, self.investment, None, self)
        self.frmInvestmentOperationsAdd_initiated.emit(w)
        w.exec_()
        
        #if num shares after add is 0, changes expiration date to today-1
        if self.investment.shares()==0:
            self.calExpiration.setSelectedDate(datetime.date.today()-datetime.timedelta(days=1))
            self.on_cmdInvestment_released()
            
        self.update_tables()    
        
    @pyqtSlot() 
    def on_actionOperationEdit_triggered(self):
        w=frmInvestmentOperationsAdd(self.mem, self.investment, self.op.selected, self)
        w.exec_()
        self.update_tables() 
        
        #if num shares after add is 0, changes expiration date to today-1
        if self.investment.shares()==0:
            self.calExpiration.setSelectedDate(datetime.date.today()-datetime.timedelta(days=1))
            self.on_cmdInvestment_released()

    @pyqtSlot() 
    def on_actionSplit_triggered(self):
        w=frmSplit(self.mem, self.investment.product)
        w.exec_()   
        if w.result()==QDialog.Accepted:
            self.update_tables()
        
    @pyqtSlot() 
    def on_actionSharesTransfer_triggered(self):
        w=frmSharesTransfer(self.mem, self.investment, self)
        w.exec_()
        
        #if num shares after add is 0, changes expiration date to today-1
        if self.investment.shares()==0:
            self.calExpiration.setSelectedDate(datetime.date.today()-datetime.timedelta(days=1))
            self.on_cmdInvestment_released()
        
        self.update_tables()                 
    
    @pyqtSlot() 
    def on_actionRangeReport_triggered(self):
        self.op.selected.show_in_ranges= not self.op.selected.show_in_ranges
        self.op.selected.save()
        self.mem.con.commit()
        #self.op doesn't belong to self.mem.data, it's a set of this widget, so I need to reload investment of the self.mem.data
        self.mem.data.investments.find_by_id(self.investment.id).get_operinversiones()
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
        f=frmSellingPoint(self.mem, self.investment)
        f.txtPrice.setText(self.txtVenta.text())
        f.exec_()
        self.txtVenta.setText(str(f.puntoventa.round(6)))

    @pyqtSlot() 
    def on_actionOperationDelete_triggered(self):
        self.investment.op.remove(self.op.selected)#debe borrarse de self.investment.op, no de self.op, ya qque self.update_tables reescribe clone_from_datetime
        self.mem.con.commit()     
        
        #if num shares after add is 0, changes expiration date to today-1
        if self.investment.shares()==0:
            self.calExpiration.setSelectedDate(datetime.date.today()-datetime.timedelta(days=1))
            self.on_cmdInvestment_released()
        
        self.update_tables()

        
        
    def on_chkHistoricalDividends_stateChanged(self, state):
        self.tblDividends.clearSelection()
        self.tblDividendsAccountCurrency.clearSelection()
        self.selDividend=None        
        if self.investment.merge==0:
            if state==Qt.Unchecked:   
                self.dividends=self.investment.setDividends_from_current_operations()
            elif state==Qt.Checked:
                self.dividends=self.investment.setDividends_from_operations()
            else:
                self.dividends.clean()
        elif self.investment.merge==1:
            self.dividends=self.mem.data.investments_active().setDividends_merging_current_operation_dividends(self.investment.product)
        elif self.investment.merge==2:
            self.dividends=self.mem.data.investments.setDividends_merging_operation_dividends(self.investment.product)
        self.load_tabDividends()

    def on_cmdISE_released(self):
        if self.investment==None or self.investment.merge==0:
            self.cmdInvestment.setEnabled(True)

    def on_txtVenta_textChanged(self):
        if self.investment==None or self.investment.merge==0:
            self.cmdInvestment.setEnabled(True)

    def on_txtInvestment_textChanged(self):
        if self.investment==None or self.investment.merge==0:
            self.cmdInvestment.setEnabled(True)

    def on_cmbTipoInvestment_currentIndexChanged(self, index):
        if self.investment==None or self.investment.merge==0:
            self.cmdInvestment.setEnabled(True)

    def on_calExpiration_selectionChanged(self):
        if self.investment==None or self.investment.merge==0:
            self.cmdInvestment.setEnabled(True)

    def on_chkExpiration_stateChanged(self, state):
        if self.investment==None or self.investment.merge==0:
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
            self.investment=Investment(self.mem).init__create(inversion,   venta,  self.mem.data.accounts_active().find_by_id(id_cuentas), product, expiration, True)      
            self.investment.save()
            self.mem.con.commit()    
            #Lo añade con las operaciones vacias pero calculadas.
            self.investment.op=InvestmentOperationHomogeneusManager(self.mem, self.investment)
            (self.investment.op_actual, self.investment.op_historica)=self.investment.op.calcular()
            self.mem.data.investments.append(self.investment)
            self.done(0)
        elif self.tipo==2:
            self.investment.name=inversion
            self.investment.venta=venta
            self.investment.product=product
            self.investment.selling_expiration=expiration
            self.investment.save()##El id y el id_cuentas no se pueden modificar
            self.mem.con.commit()
            self.cmdInvestment.setEnabled(False)
        
    def on_tblOperations_customContextMenuRequested(self,  pos):
        if self.investment.qmessagebox_inactive() or self.investment.account.qmessagebox_inactive()or self.investment.account.eb.qmessagebox_inactive():
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


        if self.investment.merge!=0:
            self.actionOperationAdd.setEnabled(False)
            self.actionOperationDelete.setEnabled(False)
            self.actionOperationEdit.setEnabled(False)
            self.actionRangeReport.setEnabled(False)
            self.actionSplit.setEnabled(False)


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
        self.investment.op_actual.selected=None
        try:
            for i in self.tblInvestmentCurrent.selectedItems():#itera por cada item no row.
                if i.row()<self.investment.op_actual.length():#Due to total file
                    self.investment.op_actual.selected=self.investment.op_actual.arr[i.row()]
        except:
            self.investment.op_actual.selected=None
        print (self.tr("Selected: {0}".format(str(self.investment.op_actual.selected))))
        
        
    def on_tblInvestmentCurrent_customContextMenuRequested(self,  pos):
        
        if self.investment.qmessagebox_inactive() or self.investment.account.qmessagebox_inactive() or self.investment.account.eb.qmessagebox_inactive():
            return
                
        if self.investment.op_actual.selected:
            self.actionChangeBenchmarkPrice.setEnabled(True)
        else:
            self.actionChangeBenchmarkPrice.setEnabled(False)
            
        if self.investment.merge!=0:
            self.actionOperationAdd.setEnabled(False)
            self.actionChangeBenchmarkPrice.setEnabled(False)
            self.actionSharesTransfer.setEnabled(False)
            
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
        if self.investment.qmessagebox_inactive() or self.investment.account.qmessagebox_inactive() or self.investment.account.eb.qmessagebox_inactive():
            return

        if self.selDividend==None:
            self.actionDividendRemove.setEnabled(False)
            self.actionDividendEdit.setEnabled(False)
        else:
            self.actionDividendRemove.setEnabled(True)
            self.actionDividendEdit.setEnabled(True)
            
        if self.investment.merge!=0:
            self.actionDividendAdd.setEnabled(False)
            self.actionDividendRemove.setEnabled(False)
            self.actionDividendEdit.setEnabled(False)
            
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

