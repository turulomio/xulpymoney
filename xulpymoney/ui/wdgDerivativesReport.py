from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget, QAbstractItemView, QProgressDialog, QApplication, QMenu, QHBoxLayout
from PyQt5.QtGui import QIcon
from datetime import date, datetime
from logging import debug, info
from xulpymoney.objects.investmentoperation import InvestmentOperationHistoricalHeterogeneusManager, InvestmentOperationCurrentHeterogeneusManager
from xulpymoney.casts import lor_transposed
from xulpymoney.libxulpymoneytypes import eConcept, eProductType
from xulpymoney.objects.accountoperation import AccountOperationManagerHeterogeneus_from_sql
from xulpymoney.objects.assets import Assets
from xulpymoney.objects.totalmonth import TotalMonthManager_from_manager_extracting_year, TotalMonthManager_from_month
from xulpymoney.ui.Ui_wdgDerivativesReport import Ui_wdgDerivativesReport
from xulpymoney.ui.myqtablewidget import mqtwObjects
from xulpymoney.ui.myqwidgets import qmessagebox

class wdgDerivativesReport(QWidget, Ui_wdgDerivativesReport):
    def __init__(self, mem,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        
        
        
        dtFirst=Assets(self.mem).first_datetime_allowed_estimated()  
        dtLast=Assets(self.mem).last_datetime_allowed_estimated()              

        #Adding more months that needed to allow month and december previous calculations
        self.tmm=TotalMonthManager_from_month(self.mem, dtFirst.year, dtFirst.month, dtLast.year, 12)

        
        self.mqtwTotal.setSettings(self.mem.settings, "wdgDerivativesReport", "mqtwTotal")
        self.mqtwTotal.table.cellDoubleClicked.connect(self.on_mqtwTotal_cellDoubleClicked)
        self.mqtwTotal.table.customContextMenuRequested.connect(self.on_mqtwTotal_customContextMenuRequested)
        self.mqtwTotal.table.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.mqtwTotal.table.itemSelectionChanged.connect(self.on_mqtwTotal_itemSelectionChanged)
        
        
        
        self.wyData.initiate(dtFirst.year,  dtLast.year, date.today().year)
        self.tab.setCurrentIndex(0)
        

        self.tmm_data=TotalMonthManager_from_manager_extracting_year(self.tmm, self.wyData.year)        
        self.load_data()
        self.load_data_second_tab()
        self.wyData.changed.connect(self.on_wyData_mychanged)#Used my due to it took default on_wyData_changed
        

    def load_data_second_tab(self):        
        adjustments=AccountOperationManagerHeterogeneus_from_sql(self.mem, "select * from opercuentas where id_conceptos in (%s)", (eConcept.DerivativesAdjustment, ))
        guarantees=AccountOperationManagerHeterogeneus_from_sql(self.mem, "select * from opercuentas where id_conceptos in (%s)", (eConcept.DerivativesGuarantee, ))
        commissions=AccountOperationManagerHeterogeneus_from_sql(self.mem, "select * from opercuentas where id_conceptos in (%s)", (eConcept.DerivativesCommission, ))
        rollover=AccountOperationManagerHeterogeneus_from_sql(self.mem, "select * from opercuentas where id_conceptos in (%s)", (eConcept.RolloverPaid, ))
        iohhm=self.InvestmentOperationHistoricalHeterogeneusManager_derivatives()
        iochm=self.InvestmentOperationCurrentHeterogeneusManager_derivatives()
        s=""
        s=s+"Total ajustes {}\n".format(adjustments.balance())
        s=s+"Total garantías: {}\n".format(guarantees.balance())
        s=s+"Total comisiones: {}\n".format(commissions.balance())
        s=s+"Total operaciones históricas: {}\n".format(iohhm.consolidado_bruto())
        s=s+"Total operaciones actuales: {}\n".format(iochm.pendiente())
        s=s+"Total rollover pagado: {}\n".format(rollover.balance())
        s=s+"Comisiones actuales e históricas: {} + {} = {}\n".format(iochm.commissions(), iohhm.commissions(), iohhm.commissions()+iochm.commissions())
        s=s+"Resultado=OpHist+OpActu-Comisiones-Rollover= {} + {} + {} + {} = {}".format(iohhm.consolidado_bruto(), iochm.pendiente(), commissions.balance(), rollover.balance(), iohhm.consolidado_bruto()+iochm.pendiente()+commissions.balance()+rollover.balance())
        self.textBrowser.setText(s)
        self.wdgIOHSLong.blockSignals(True)
        self.wdgIOHSLong.setManager(self.mem, iohhm, "wdgDerivativesReport", "wdgIOHSLong")
        self.wdgIOHSLong.setSelectedString(self.mem.settingsdb.value("strategyLongShort/historicalLong", ""))
        self.wdgIOHSLong.blockSignals(False)
        
    def on_wdgIOHSLong_itemChanged(self):
        self.mem.settingsdb.setValue("strategyLongShort/historicalLong", self.wdgIOHSLong.getSelectedString())
        debug("itemCheckStatusChanged {}".format(self.wdgIOHSLong.getSelectedString()))

    def InvestmentOperationHistoricalHeterogeneusManager_derivatives(self):
        r=InvestmentOperationHistoricalHeterogeneusManager(self.mem)
        for o in self.mem.data.investments.arr:
            if o.product.type.id in (eProductType.CFD, eProductType.Future):
                o.needStatus(2)
                for op in o.op_historica.arr:
                    r.append(op)
        return r

    def InvestmentOperationCurrentHeterogeneusManager_derivatives(self):
        r=InvestmentOperationCurrentHeterogeneusManager(self.mem)
        for o in self.mem.data.investments.arr:
            if o.product.type.id in (eProductType.CFD, eProductType.Future):
                o.needStatus(2)
                for op in o.op_actual.arr:
                    r.append(op)
        return r


    def load_data(self):
        inicio=datetime.now()
                
        pd= QProgressDialog("Loading data", None, 0, 12)
        pd.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
        pd.setModal(True)
        pd.setWindowTitle(self.tr("Generating derivatives total report..."))
        pd.forceShow()
        pd.setValue(0)
        
        
        hh=[self.tr("January"),  self.tr("February"), self.tr("March"), self.tr("April"), self.tr("May"), self.tr("June"), self.tr("July"), self.tr("August"), self.tr("September"), self.tr("October"), self.tr("November"), self.tr("December"), self.tr("Total")]
        hv=[self.tr("Adjustments"), ]
        data=[]
        tm_previous_december=self.tmm.find_previous_december(self.tmm_data.first())
        for m in self.tmm_data:
            tm_previous=self.tmm.find_previous(m)
            data.append([
                m.derivatives_adjustments(), 
            ])
            pd.setValue(pd.value()+1)
            QApplication.processEvents()
        data.append([
            self.tmm_data.derivatives_adjustments(), 
        ])

        data=lor_transposed(data)
        self.mqtwTotal.setData(hh, hv, data)
        
        self.mqtwTotal.table.setCurrentCell(6, date.today().month-1)
#        tm_lastyear=self.tmm.find(self.wyData.year-1, 12)
#        self.lblPreviousYear.setText(self.tr("Balance at {0}-12-31: {1}".format(tm_lastyear.year, tm_lastyear.total())))
#
#        invested=Assets(self.mem).invested(date.today())
#        current=Assets(self.mem).saldo_todas_inversiones( date.today())
#        s=self.tr("This year I've generated {}.").format(self.tmm_data.gains()+self.tmm_data.dividends())
#        s=s+"\n"+self.tr("Difference between invested amount and current invesment balance: {} - {} = {}").format(invested,  current,  current-invested)
#        self.lblInvested.setText(s)

        info("wdgTotal > load_data: {0}".format(datetime.now()-inicio))
        
    def on_wyData_mychanged(self):
        self.tmm_data=TotalMonthManager_from_manager_extracting_year(self.tmm, self.wyData.year)
        self.load_data()
                    
    def on_mqtwTotal_cellDoubleClicked(self, row, column):
        if row==0:#incomes
            self.on_actionShowAdjustments_triggered()


    def on_mqtwTotal_customContextMenuRequested(self,  pos):
        menu=QMenu()
        menu.addAction(self.actionShowAdjustments)
        menu.addSeparator()
        menu.exec_(self.mqtwTotal.table.mapToGlobal(pos))

    @pyqtSlot()
    def on_mqtwTotal_itemSelectionChanged(self):
        debug("NOW")
        self.month=None
        for i in self.mqtwTotal.table.selectedItems():#itera por cada item no row.
            self.month=i.column()+1
        debug("Selected month: {0}.".format(self.month))

        
    @pyqtSlot() 
    def on_actionShowAdjustments_triggered(self):
        newtab = QWidget()
        horizontalLayout = QHBoxLayout(newtab)
        wdg = mqtwObjects(newtab)
        wdg.setSettings(self.mem.settings, "wdgDerivativesReport","mqtwShowIncomes")
        wdg.table.setSelectionBehavior(QAbstractItemView.SelectItems)
        
        if self.month==13:#Year
            tabtitle=self.tr("Incomes of {}").format(self.wyData.year)
            manager=AccountOperationManagerHeterogeneus_from_sql(self.mem, """
select 
    id_opercuentas, datetime, id_conceptos, id_tiposoperaciones, importe, comentario, id_cuentas 
from 
    opercuentas 
where 
    id_conceptos in (%s) AND
    date_part('year',datetime)=%s
""", (eConcept.DerivativesAdjustment, self.wyData.year ))
        else:#Month
            tabtitle=self.tr("Incomes of {0} of {1}").format(self.mqtwTotal.table.horizontalHeaderItem(self.month-1).text(), self.wyData.year)
            manager=AccountOperationManagerHeterogeneus_from_sql(self.mem, """
select 
    id_opercuentas, datetime, id_conceptos, id_tiposoperaciones, importe, comentario, id_cuentas 
from 
    opercuentas 
where 
    id_conceptos in (%s) AND
    date_part('year',datetime)=%s and 
    date_part('month',datetime)=%s
""", (eConcept.DerivativesAdjustment, self.wyData.year, self.month ))
        manager.myqtablewidget(wdg,  True)
        wdg.drawOrderBy(0, False)
        horizontalLayout.addWidget(wdg)
        self.tab.addTab(newtab, tabtitle)
        self.tab.setCurrentWidget(newtab)

    def on_tab_tabCloseRequested(self, index):
        """Only removes dinamic tabs"""
        if index in (0, 1):
            qmessagebox(self.tr("You can't close this tab"))
        else:
            self.tab.setCurrentIndex(0)
            self.tab.removeTab(index)
