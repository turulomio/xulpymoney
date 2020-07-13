from PyQt5.QtCore import Qt,  pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QDialog,  QMenu
from datetime import date, timedelta
from xulpymoney.casts import c2b
from xulpymoney.datetime_functions import days2string
from xulpymoney.objects.currency import currency_symbol
from xulpymoney.objects.money import Money
from xulpymoney.objects.investment import Investment
from xulpymoney.objects.percentage import Percentage
from xulpymoney.objects.investmentoperation import InvestmentOperationHomogeneusManager
from xulpymoney.libxulpymoneytypes import eMoneyCurrency
from xulpymoney.ui.Ui_frmInvestmentReport import Ui_frmInvestmentReport
from xulpymoney.ui.frmInvestmentOperationsAdd import frmInvestmentOperationsAdd
from xulpymoney.ui.frmDividendsAdd import frmDividendsAdd
from xulpymoney.ui.frmSellingPoint import frmSellingPoint
from xulpymoney.ui.frmQuotesIBM import frmQuotesIBM
from xulpymoney.ui.wdgDisReinvest import wdgDisReinvest
from xulpymoney.ui.frmSharesTransfer import frmSharesTransfer
from xulpymoney.ui.frmSplit import frmSplit
from xulpymoney.ui.myqdialog import MyModalQDialog
from xulpymoney.ui.myqwidgets import qmessagebox

class frmInvestmentReport(QDialog, Ui_frmInvestmentReport):
    frmInvestmentOperationsAdd_initiated=pyqtSignal(frmInvestmentOperationsAdd)#Se usa para cargar datos de ordenes en los datos de este formulario
    def __init__(self, mem, inversion=None,  parent=None):
        QDialog.__init__(self, parent)
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.hide()
        self.setupUi(self)
        self.mem=mem
        self.investment=inversion
        self.ise.setupUi(self.mem,  self.investment)
        
        self.mqtwDividends.setSettings(self.mem.settings, "frmInvestmentReport", "mqtwDividends")
        self.mqtwDividends.table.customContextMenuRequested.connect(self.on_mqtwDividends_customContextMenuRequested)
        self.mqtwDividends.table.itemSelectionChanged.connect(self.on_mqtwDividends_itemSelectionChanged)
        self.mqtwDividendsAccountCurrency.setSettings(self.mem.settings, "frmInvestmentReport", "mqtwDividendsAccountCurrency")
        self.mqtwInvestmentCurrent.setSettings(self.mem.settings, "frmInvestmentReport", "mqtwInvestmentCurrent")
        self.mqtwInvestmentCurrent.table.customContextMenuRequested.connect(self.on_mqtwInvestmentCurrent_customContextMenuRequested)
        self.mqtwInvestmentCurrent.table.itemSelectionChanged.connect(self.on_mqtwInvestmentCurrent_itemSelectionChanged)
        self.mqtwInvestmentCurrentAccountCurrency.setSettings(self.mem.settings, "frmInvestmentReport", "mqtwInvestmentCurrentAccountCurrency")
        self.mqtwOperations.setSettings(self.mem.settings, "frmInvestmentReport", "mqtwOperations")
        self.mqtwOperations.table.customContextMenuRequested.connect(self.on_mqtwOperations_customContextMenuRequested)
        self.mqtwOperations.table.itemSelectionChanged.connect(self.on_mqtwOperations_itemSelectionChanged)
        self.mqtwOperationsAccountCurrency.setSettings(self.mem.settings, "frmInvestmentReport", "mqtwOperationsAccountCurrency")
        self.mqtwInvestmentHistorical.setSettings(self.mem.settings, "frmInvestmentReport", "mqtwInvestmentHistorical")
        self.mqtwInvestmentHistoricalAccountCurrency.setSettings(self.mem.settings,  "frmInvestmentReport", "mqtwInvestmentHistoricalAccountCurrency")
        self.ise.cmd.released.connect(self.on_cmdISE_released)
        self.mem.data.accounts_active().qcombobox(self.cmbAccount)

        self.wdgTS.setSettings(self.mem.settings, "frmInvestmentReport", "wdgTS")
        self.wdgTS.ts.setTitle(self.tr("Investment chart"))
            
        if self.investment==None:#ADD
            self.cmdInvestment.setText(self.tr("Add a new investment"))
            self.lblTitulo.setText(self.tr("New investment"))
            self.investment=None
            self.tab.setCurrentIndex(0)
            self.tabDividends.setEnabled(False)
            self.tabOperacionesHistoricas.setEnabled(False)
            self.tabInvestmentCurrent.setEnabled(False)
            self.ise.setSelected(None)
            self.cmdPuntoVenta.setEnabled(False)
        else:#UPDATE
            self.tab.setCurrentIndex(1)
            self.investment.needStatus(3)
            self.lblTitulo.setText(self.investment.name)
            self.txtInvestment.setText(self.investment.name)
            self.txtVenta.setText(self.investment.venta)
            self.chkDailyAdjustment.setChecked(self.investment.daily_adjustment)
            if self.investment.selling_expiration==None:
                self.chkExpiration.setCheckState(Qt.Unchecked)
            else:
                self.chkExpiration.setCheckState(Qt.Checked)
                self.calExpiration.setSelectedDate(self.investment.selling_expiration)
            self.ise.setSelected(self.investment.product)
            self.cmdPuntoVenta.setEnabled(True)
            self.cmbAccount.setCurrentIndex(self.cmbAccount.findData(self.investment.account.id))
            
            #CmbAccount está desabilitado si hay dividends o operinversiones
            if self.investment.op.length()!=0:
                self.cmbAccount.setEnabled(False)
    
            self.update_tables()

        self.cmdInvestment.setEnabled(False)    
        self.showMaximized()
        QApplication.restoreOverrideCursor()


       
    def on_chkOperaciones_stateChanged(self, state):
        if state==Qt.Unchecked:
            first=self.investment.op_actual.first()
            if first==None:
                dt=self.mem.localzone.now()
            else:
                dt=first.datetime
            self.op=self.investment.op.ObjectManager_from_datetime(dt)
        else:
            self.op=self.investment.op
            
        self.op.selected=None
        self.op.myqtablewidget(self.mqtwOperations)
        
        if self.investment.product.currency==self.investment.account.currency:#Multidivisa
            self.grpOperationsAccountCurrency.hide()
        else:
            self.op.myqtablewidget(self.mqtwOperationsAccountCurrency, type=2)

    def update_tables(self):             
        #Actualiza el indice de referencia porque ha cambiado
        self.investment.op_actual.get_valor_benchmark(self.mem.data.benchmark)
        
        self.on_chkOperaciones_stateChanged(self.chkOperaciones.checkState())
        self.chkOperaciones.setEnabled(True)
        
        self.investment.op_actual.myqtablewidget(self.mqtwInvestmentCurrent, self.investment.product.result.basic.last, type=1)
        self.investment.op_historica.myqtablewidget(self.mqtwInvestmentHistorical,  type=1 )
        if self.investment.product.currency==self.investment.account.currency:#Multidivisa
            self.grpCurrentAccountCurrency.hide()
            self.grpHistoricalAccountCurrency.hide()
        else:
            m=Money(self.mem, 1, self.investment.account.currency)
            
            self.grpCurrentAccountCurrency.setTitle(self.tr("Current status in account currency ( {} = {} at {} )").format(m.string(6), m.convert(self.investment.product.currency, self.mem.localzone.now()).string(6), m.conversionDatetime(self.investment.product.currency, self.mem.localzone.now())))
            self.investment.op_actual.myqtablewidget(self.mqtwInvestmentCurrentAccountCurrency, self.investment.product.result.basic.last,  type=2)
            self.investment.op_historica.myqtablewidget(self.mqtwInvestmentHistoricalAccountCurrency, type=2 )
        
        self.lblAge.setText(self.tr("Current operations average age: {0}".format(days2string(self.investment.op_actual.average_age()))))
        
        if self.investment!=None:#We are adding a new investment
            self.on_chkHistoricalDividends_stateChanged(self.chkHistoricalDividends.checkState())
            self.chkHistoricalDividends.setEnabled(True)

    @pyqtSlot() 
    def on_actionDividendAdd_triggered(self):
        w=frmDividendsAdd(self.mem, self.investment,  None)
        w.exec_()
        self.on_chkHistoricalDividends_stateChanged(self.chkHistoricalDividends.checkState())

    @pyqtSlot() 
    def on_actionDividendEdit_triggered(self):
        w=frmDividendsAdd(self.mem, self.investment, self.investment.dividends.selected)
        w.exec_()
        self.on_chkHistoricalDividends_stateChanged(self.chkHistoricalDividends.checkState())

        
    @pyqtSlot() 
    def on_actionDividendRemove_triggered(self):
        self.investment.dividends.selected.borrar()
        self.mem.con.commit()
        self.investment.needStatus(3, downgrade_to=2)
        self.on_chkHistoricalDividends_stateChanged(self.chkHistoricalDividends.checkState())

    @pyqtSlot() 
    def on_actionChangeBenchmarkPrice_triggered(self):
        w=frmQuotesIBM(self.mem, self.mem.data.benchmark, self.investment.op_actual.selected.referenciaindice, self)
        w.txtQuote.setFocus()
        w.exec_() 
        self.update_tables()

    @pyqtSlot() 
    def on_actionDisReinvest_triggered(self):
        d=MyModalQDialog()
        d.setWindowTitle(self.tr("Divest / Reinvest simulation"))
        d.setSettings(self.mem.settings, "frmInvestmentReport", "frmDisReinvest")
        d.setWidgets(wdgDisReinvest(self.mem, self.investment, False, d))
        d.exec_()
        
    @pyqtSlot() 
    def on_actionDisReinvestProduct_triggered(self):
        d=MyModalQDialog()
        d.setSettings(self.mem.settings, "frmInvestmentReport", "frmDisReinvestProduct")
        d.setWindowTitle(self.tr("Divest / Reinvest simulation"))
        d.setWidgets(wdgDisReinvest(self.mem, self.investment, True,  d))
        d.exec_()
        
    @pyqtSlot() 
    def on_actionOperationAdd_triggered(self):
        if self.investment.product.result.basic.last.quote==None:
            qmessagebox(self.tr("Before adding a operation, you must add the current price of the product."), ":/xulpymoney/coins.png")
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
            self.calExpiration.setSelectedDate(date.today()-timedelta(days=1))
            self.on_cmdInvestment_released()
            
        self.update_tables()    
        
    @pyqtSlot() 
    def on_actionOperationEdit_triggered(self):
        w=frmInvestmentOperationsAdd(self.mem, self.investment, self.op.selected, self)
        w.exec_()
        self.update_tables() 
        
        #if num shares after add is 0, changes expiration date to today-1
        if self.investment.shares()==0:
            self.calExpiration.setSelectedDate(date.today()-timedelta(days=1))
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
            self.calExpiration.setSelectedDate(date.today()-timedelta(days=1))
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
            qmessagebox(self.tr("Shares transfer couldn't be done."), ":/xulpymoney/coins.png")
            return
        self.update_tables()

    @pyqtSlot() 
    def on_cmdPuntoVenta_released(self):
        f=frmSellingPoint(self.mem, self.investment)
        f.txtPrice.setText(self.txtVenta.text())
        f.exec_()
        self.txtVenta.setText(f.puntoventa.round(self.investment.product.decimals))

    @pyqtSlot() 
    def on_actionOperationDelete_triggered(self):
        self.investment.op.remove(self.op.selected)#debe borrarse de self.investment.op, no de self.op, ya qque self.update_tables reescribe clone_from_datetime
        self.mem.con.commit()     
        
        #if num shares after add is 0, changes expiration date to today-1
        if self.investment.shares()==0:
            self.calExpiration.setSelectedDate(date.today()-timedelta(days=1))
            self.on_cmdInvestment_released()
        
        self.update_tables()

    def on_chkHistoricalDividends_stateChanged(self, state):
        self.mqtwDividends.table.clearSelection()
        self.mqtwDividendsAccountCurrency.table.clearSelection()
        self.investment.dividends.selected=None     
        (sumneto, sumbruto, sumretencion, sumcomision)=self.investment.dividends.myqtablewidget(self.mqtwDividends, eMoneyCurrency.Product, current=not c2b(state))
        if self.investment.account.currency==self.investment.product.currency:
            self.grpDividendsAccountCurrency.hide()
        else:
            self.investment.dividends.myqtablewidget(self.mqtwDividendsAccountCurrency, eMoneyCurrency.Product, not self.chkHistoricalDividends.isChecked())
        if state==Qt.Unchecked:
            estimacion=self.investment.product.estimations_dps.currentYear()
            if estimacion.estimation!=None:
                acciones=self.investment.shares()
                tpccalculado=Percentage(estimacion.estimation, self.investment.product.result.basic.last.quote)
                self.lblDivFechaRevision.setText(self.tr('Estimation review date: {0}').format(estimacion.date_estimation))
                self.lblDivAnualEstimado.setText(self.tr("Estimated annual dividend is {0} ({1} per share)").format(tpccalculado,  self.investment.money(estimacion.estimation)))
                self.lblDivSaldoEstimado.setText(self.tr("Estimated balance: {0} ({1} after taxes)").format( self.investment.money(acciones*estimacion.estimation),  self.investment.money(acciones*estimacion.estimation*(1-self.mem.dividendwithholding))))
            self.lblDivTPC.setText(self.tr("% Invested: {}").format(self.investment.dividends.percentage_from_invested(eMoneyCurrency.Product, current=True)))
            self.lblDivTAE.setText(self.tr("% APR from invested: {}").format(self.investment.dividends.percentage_tae_from_invested(eMoneyCurrency.Product, current=True)))
            self.grpDividendsEstimation.show()
            self.grpDividendsEfectivos.show()
        else:
            self.grpDividendsEstimation.hide()
            self.grpDividendsEfectivos.hide()

    def on_cmdISE_released(self):
        if self.investment==None or self.investment.merged==False:
            self.cmdInvestment.setEnabled(True)

    def on_txtVenta_textChanged(self):
        if self.investment==None or self.investment.merged==False:
            self.cmdInvestment.setEnabled(True)

    def on_txtInvestment_textChanged(self):
        if self.investment==None or self.investment.merged==False:
            self.cmdInvestment.setEnabled(True)

    def on_cmbTipoInvestment_currentIndexChanged(self, index):
        if self.investment==None or self.investment.merged==False:
            self.cmdInvestment.setEnabled(True)

    def on_calExpiration_selectionChanged(self):
        if self.investment==None or self.investment.merged==False:
            self.cmdInvestment.setEnabled(True)

    def on_chkExpiration_stateChanged(self, state):
        if self.investment==None or self.investment.merged==False:
            self.cmdInvestment.setEnabled(True)

    def on_chkDailyAdjustment_stateChanged(self, state):
        if self.investment==None or self.investment.merged==False:
            self.cmdInvestment.setEnabled(True)

    def on_cmdToday_released(self):
        self.calExpiration.setSelectedDate(date.today())

    def on_cmdInvestment_released(self):
        if self.ise.selected==None:
            qmessagebox(self.tr("You must select a product to continue."), ":/xulpymoney/coins.png")
            return
        inversion=self.txtInvestment.text()
        venta=self.txtVenta.decimal()
        daily_adjustment=self.chkDailyAdjustment.isChecked()
        account=self.mem.data.accounts_active().find_by_id(self.cmbAccount.itemData(self.cmbAccount.currentIndex()))
        if account is None:
            qmessagebox(self.tr("You must select an account"))
            return
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

        if self.investment==None: #insertar
            self.investment=Investment(self.mem).init__create(inversion,   venta,  account, product, expiration, True, daily_adjustment )
            self.investment.save()
            self.mem.con.commit()    
            #Lo añade con las operaciones vacias pero calculadas.
            self.investment.op=InvestmentOperationHomogeneusManager(self.mem, self.investment)
            (self.investment.op_actual, self.investment.op_historica)=self.investment.op.get_current_and_historical_operations()
            self.mem.data.investments.append(self.investment)
            self.done(0)
        else:#UPDATE
            self.investment.name=inversion
            self.investment.venta=venta
            self.investment.product=product
            self.investment.selling_expiration=expiration
            self.investment.daily_adjustment=daily_adjustment
            self.investment.save()##El id y el id_cuentas no se pueden modificar
            self.mem.con.commit()
            self.cmdInvestment.setEnabled(False)
        
    def on_mqtwOperations_customContextMenuRequested(self,  pos):
        if self.investment.qmessagebox_inactive() or self.investment.account.qmessagebox_inactive()or self.investment.account.bank.qmessagebox_inactive():
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


        if self.investment.merged==True:
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
        menu.exec_(self.mqtwOperations.table.mapToGlobal(pos))


    def on_mqtwInvestmentCurrent_itemSelectionChanged(self):
        self.investment.op_actual.selected=None
        try:
            for i in self.mqtwInvestmentCurrent.table.selectedItems():#itera por cada item no row.
                if i.row()<self.investment.op_actual.length():#Due to total file
                    self.investment.op_actual.selected=self.investment.op_actual.arr[i.row()]
        except:
            self.investment.op_actual.selected=None
        print (self.tr("Selected: {0}".format(str(self.investment.op_actual.selected))))
        
        
    def on_mqtwInvestmentCurrent_customContextMenuRequested(self,  pos):
        
        if self.investment.qmessagebox_inactive() or self.investment.account.qmessagebox_inactive() or self.investment.account.bank.qmessagebox_inactive():
            return
                
        if self.investment.op_actual.selected:
            self.actionChangeBenchmarkPrice.setEnabled(True)
        else:
            self.actionChangeBenchmarkPrice.setEnabled(False)
            
        if self.investment.merged==True:
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
        menu.exec_(self.mqtwInvestmentCurrent.table.mapToGlobal(pos))

    def on_mqtwOperations_itemSelectionChanged(self):
        self.op.selected=None
        try:
            for i in self.mqtwOperations.table.selectedItems():#itera por cada item no row.
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

    def on_mqtwDividends_customContextMenuRequested(self,  pos):
        if self.investment.qmessagebox_inactive() or self.investment.account.qmessagebox_inactive() or self.investment.account.bank.qmessagebox_inactive():
            return

        if self.investment.dividends.selected==None:
            self.actionDividendRemove.setEnabled(False)
            self.actionDividendEdit.setEnabled(False)
        else:
            self.actionDividendRemove.setEnabled(True)
            self.actionDividendEdit.setEnabled(True)
            
        if self.investment.merged==True:
            self.actionDividendAdd.setEnabled(False)
            self.actionDividendRemove.setEnabled(False)
            self.actionDividendEdit.setEnabled(False)
            
        menu=QMenu()
        menu.addAction(self.actionDividendAdd)
        menu.addAction(self.actionDividendRemove)
        menu.addAction(self.actionDividendEdit)
        menu.exec_(self.mqtwDividends.table.mapToGlobal(pos))

    def on_mqtwDividends_itemSelectionChanged(self):
        try:
            for i in self.mqtwDividends.table.selectedItems():#itera por cada item no rowse.
                self.investment.dividends.selected=self.investment.dividends.arr[i.row()]
        except:
            self.investment.dividends.selected=None
        print ("Dividend selected: " +  str(self.investment.dividends.selected))        

    def on_tab_currentChanged(self, index): 
        if  index==5: #Repaints chart
            self.wdgTS_update()
        
        
    def wdgTS_update(self):
        self.wdgTS.clear()
        self.investment.needStatus(3)
        if self.investment.op.length()>0:
            self.wdgTS.ts.setXFormat("date", self.tr("Date"))
            self.wdgTS.ts.setYFormat(self.investment.product.currency, self.tr("Amount ({})").format(currency_symbol(self.investment.account.currency)), self.investment.product.decimals)
            #Gets investment important datetimes: operations, dividends, init and current time. For each datetime adds another at the beginning of the day, to get mountains in graph
            datetimes=set()
            datetimes.add(self.investment.op.first().datetime -timedelta(days=30))
            for op in self.investment.op.arr:
                datetimes.add(op.datetime)
                datetimes.add(op.datetime-timedelta(seconds=1))
            for dividend in self.investment.dividends.arr:
                datetimes.add(dividend.datetime)
            datetimes.add(self.mem.localzone.now())
            datetimes_list=list(datetimes)
            datetimes_list.sort()
                    
            #Progress dialog 
            self.wdgTS.ts.setProgressDialogEnabled(True)
            self.wdgTS.ts.setProgressDialogAttributes(
                    None, 
                    self.tr("Loading {} special datetimes").format(len(datetimes_list)), 
                    QIcon(":xulpymoney/coins.png"), 
                    0, 
                    len(datetimes_list)
            )
            
            #Draw lines
            invested=self.wdgTS.ts.appendTemporalSeries(self.tr("Invested amount"))
            balance=self.wdgTS.ts.appendTemporalSeries(self.tr("Investment balance"))
            gains=self.wdgTS.ts.appendTemporalSeries(self.tr("Net gains"))
            dividends=self.wdgTS.ts.appendTemporalSeries(self.tr("Net dividends"))
            gains_dividends=self.wdgTS.ts.appendTemporalSeries(self.tr("Net gains with dividends"))
            for i, dt in enumerate(datetimes_list):
                #Shows progress dialog
                self.wdgTS.ts.setProgressDialogNumber(i+1)
                #Calculate dividends in datetime
                dividend_net=0
                for dividend in self.investment.dividends.arr:
                    if dividend.datetime<=dt:
                        dividend_net=dividend_net+dividend.neto
                #Append data of that datetime
                tmp_investment=self.investment.Investment_At_Datetime(dt)
                gains_net=tmp_investment.op_historica.consolidado_neto().amount
                self.wdgTS.ts.appendTemporalSeriesData(invested, dt, tmp_investment.invertido().amount)
                self.wdgTS.ts.appendTemporalSeriesData(gains_dividends, dt, gains_net+dividend_net)
                self.wdgTS.ts.appendTemporalSeriesData(balance, dt, tmp_investment.balance(dt.date()).amount)
                self.wdgTS.ts.appendTemporalSeriesData(dividends, dt, dividend_net)
                self.wdgTS.ts.appendTemporalSeriesData(gains, dt, gains_net)
            self.wdgTS.display()
            #Markers are generated in display so working with markers must be after it
            self.wdgTS.ts.chart().legend().markers(gains)[0].clicked.emit()
            self.wdgTS.ts.chart().legend().markers(dividends)[0].clicked.emit()
            self.wdgTS.ts.chart().legend().markers(balance)[0].clicked.emit()
