from PyQt5.QtCore import pyqtSlot,  Qt
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import  QWidget, QMenu, QProgressDialog, QVBoxLayout, QHBoxLayout, QAbstractItemView, QTableWidgetItem, QLabel, QApplication
from datetime import date, datetime
from decimal import Decimal
from logging import info, debug
from xulpymoney.datetime_functions import dtaware_day_end_from_date
from xulpymoney.objects.concept import ConceptManager_considered_dividends_in_totals
from xulpymoney.objects.dividend import DividendHeterogeneusManager
from xulpymoney.objects.investmentoperation import InvestmentOperationHistoricalHeterogeneusManager
from xulpymoney.objects.totalmonth import TotalMonthManager_from_manager_extracting_year, TotalMonthManager_from_month, TotalMonthManager_from_manager_extracting_from_month
from xulpymoney.libxulpymoneyfunctions import  qmessagebox
from xulpymoney.casts import list2string, none2decimal0, lor_transposed
from xulpymoney.ui.myqtablewidget import qcenter, qleft, mqtwObjects, mqtw
from xulpymoney.libxulpymoneytypes import eQColor, eMoneyCurrency
from xulpymoney.objects.annualtarget import AnnualTarget
from xulpymoney.objects.assets import Assets
from xulpymoney.objects.accountoperation import AccountOperationManagerHeterogeneus
from xulpymoney.objects.money import Money
from xulpymoney.ui.Ui_wdgTotal import Ui_wdgTotal


class wdgTotal(QWidget, Ui_wdgTotal):
    def __init__(self, mem,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem   

        dtFirst=Assets(self.mem).first_datetime_allowed_estimated()  
        dtLast=Assets(self.mem).last_datetime_allowed_estimated()              

        #Adding more months that needed to allow month and december previous calculations
        self.tmm=TotalMonthManager_from_month(self.mem, dtFirst.year, dtFirst.month, dtLast.year, 12)

        
        self.mqtw.setSettings(self.mem.settings, "wdgTotal", "mqtw")
        self.mqtw.table.cellDoubleClicked.connect(self.on_mqtw_cellDoubleClicked)
        self.mqtw.table.customContextMenuRequested.connect(self.on_mqtw_customContextMenuRequested)
        self.mqtw.table.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.mqtw.table.itemSelectionChanged.connect(self.on_mqtw_itemSelectionChanged)
        self.mqtwTargets.setSettings(self.mem.settings, "wdgTotal", "mqtwTargets")
        self.mqtwTargetsPlus.setSettings(self.mem.settings, "wdgTotal", "mqtwTargetsPlus")
        self.mqtwInvestOrWork.setSettings(self.mem.settings,  "wdgTotal", "mqtwInvestOrWork")
        self.mqtwMakeEndsMeet.setSettings(self.mem.settings, "wdgTotal", "mqtwMakeEndsMeet")
        
        self.annualtarget=None#AnnualTarget Object
        
        self.wyData.initiate(dtFirst.year,  dtLast.year, date.today().year)
        self.wyChart.initiate(dtFirst.year,  date.today().year, date.today().year-3)
        self.wyChart.label.setText(self.tr("Data from selected year"))

        self.wdgTS.setSettings(self.mem.settings, "wdgTotal", "wdgTS")
        self.wdgTSInvested.setSettings(self.mem.settings, "wdgTotal", "wdgTSInvested")

        self.tab.setCurrentIndex(0)
        self.tabData.setCurrentIndex(0)
        self.tabPlus.setCurrentIndex(0)


        self.tmm_data=TotalMonthManager_from_manager_extracting_year(self.tmm, self.wyData.year)        
        self.tmm_graphics=TotalMonthManager_from_manager_extracting_from_month(self.tmm, self.wyChart.year, 1, date.today().year, date.today().month)

        self.load_data()
        self.load_targets()
        self.load_targets_with_funds_revaluation()
        self.load_invest_or_work()
        self.load_make_ends_meet()
        self.wyData.changed.connect(self.on_wyData_mychanged)#Used my due to it took default on_wyData_changed
        self.wyChart.changed.connect(self.on_wyChart_mychanged)


    def load_data(self):
        inicio=datetime.now()
                
        pd= QProgressDialog("Loading data", None, 0, 12)
        pd.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
        pd.setModal(True)
        pd.setWindowTitle(QApplication.translate("Mem","Generating total report..."))
        pd.forceShow()
        pd.setValue(0)
        
        
        hh=[self.tr("January"),  self.tr("February"), self.tr("March"), self.tr("April"), self.tr("May"), self.tr("June"), self.tr("July"), self.tr("August"), self.tr("September"), self.tr("October"), self.tr("November"), self.tr("December"), self.tr("Total")]
        hv=[self.tr("Incomes"), self.tr("Gains"), self.tr("Dividends"), self.tr("Expenses"), self.tr("I+G+D+E"), "", self.tr("Accounts"), self.tr("Investments"), self.tr("Total"), self.tr("Monthly difference"), "", self.tr("% Year to date")]
        data=[]
        tm_previous_december=self.tmm.find_previous_december(self.tmm_data.first())
        for m in self.tmm_data:
            tm_previous=self.tmm.find_previous(m)
            data.append([
                m.incomes(),
                m.gains(),
                m.dividends(),
                m.expenses(),
                m.i_d_g_e(),
                "", 
                m.total_accounts(),
                m.total_investments_real(),
                m.total_real(),
                m.total_difference(tm_previous),
                "", 
                m.total_difference_percentage(tm_previous_december),
            ])
            pd.setValue(pd.value()+1)
            QApplication.processEvents()
        data.append([
            self.tmm_data.incomes(),
            self.tmm_data.gains(),
            self.tmm_data.dividends(),
            self.tmm_data.expenses(),
            self.tmm_data.i_d_g_e(),
            "", 
            "", 
            "", 
            "", 
            self.tmm_data.last().total_difference(tm_previous_december),
            "", 
            self.tmm_data.last().total_difference_percentage(tm_previous_december),
        ])
        data=lor_transposed(data)
        self.mqtw.setData(hh, hv, data)
        
        self.mqtw.table.setCurrentCell(6, date.today().month-1)
        tm_lastyear=self.tmm.find(self.wyData.year-1, 12)
        self.lblPreviousYear.setText(self.tr("Balance at {0}-12-31: {1}".format(tm_lastyear.year, tm_lastyear.total())))

        invested=Assets(self.mem).invested(date.today())
        current=Assets(self.mem).saldo_todas_inversiones( date.today())
        s=self.tr("This year I've generated {}.").format(self.tmm_data.gains()+self.tmm_data.dividends())
        s=s+"\n"+self.tr("Difference between invested amount and current invesment balance: {} - {} = {}").format(invested,  current,  current-invested)
        self.lblInvested.setText(s)

        info("wdgTotal > load_data: {0}".format(datetime.now()-inicio))

    def load_targets(self):
        self.annualtarget=AnnualTarget(self.mem).init__from_db(self.wyData.year) 
        self.lblTarget.setText(self.tr("Annual target percentage of total assests balance at {}-12-31 ( {} )".format(self.annualtarget.year-1, self.annualtarget.lastyear_assests)))
        self.spinTarget.setValue(float(self.annualtarget.percentage))
        self.mqtwTargets.table.setColumnCount(13)
        self.mqtwTargets.table.setRowCount(5)
        for i, s in enumerate([self.tr("January"),  self.tr("February"), self.tr("March"), self.tr("April"), self.tr("May"), self.tr("June"), self.tr("July"), self.tr("August"), self.tr("September"), self.tr("October"), self.tr("November"), self.tr("December"), self.tr("Total")]):
            self.mqtwTargets.table.setHorizontalHeaderItem(i, QTableWidgetItem(s))
        for i, s in enumerate([self.tr("Monthly target"), self.tr("Total gains"), "", self.tr("Accumulated target"), self.tr("Accumulated total gains")]):
            self.mqtwTargets.table.setVerticalHeaderItem(i, QTableWidgetItem(s))
        self.mqtwTargets.table.verticalHeader().show()        
        self.mqtwTargets.table.clearContents()
        self.mqtwTargets.applySettings()
        inicio=datetime.now()     
        sumd_g=Money(self.mem, 0, self.mem.localcurrency)
        for i, m in enumerate(self.tmm_data): 
            i=i+1
            sumd_g=sumd_g+m.d_g()
            self.mqtwTargets.table.setItem(0, i-1, self.mem.localmoney(self.annualtarget.monthly_balance()).qtablewidgetitem())
            self.mqtwTargets.table.setItem(1, i-1, self.mem.localmoney(m.d_g().amount).qtablewidgetitem_with_target(self.annualtarget.monthly_balance()))
            self.mqtwTargets.table.setItem(3, i-1, self.mem.localmoney(self.annualtarget.monthly_balance()*i).qtablewidgetitem())
            self.mqtwTargets.table.setItem(4, i-1, self.mem.localmoney(sumd_g.amount).qtablewidgetitem_with_target(self.annualtarget.monthly_balance()*i))
        self.mqtwTargets.table.setItem(0, 12, self.mem.localmoney(self.annualtarget.annual_balance()).qtablewidgetitem())
        self.mqtwTargets.table.setItem(1, 12, self.mem.localmoney(sumd_g.amount).qtablewidgetitem_with_target(self.annualtarget.annual_balance()))
        self.mqtwTargets.table.setCurrentCell(2, date.today().month-1)   
                
        s=""
        s=s+self.tr("This report shows if the user reaches the annual and monthly target.") +"\n\n"
        s=s+self.tr("Total gains are the result of adding dividends to gains")+"\n\n"
        s=s+self.tr("The cumulative target row shows compliance of the target in the year.")+"\n\n"
        s=s+self.tr("Green color shows that target has been reached.")
        self.lblTargets.setText(s)
        
        info("wdgTargets > load_data_targets: {0}".format(datetime.now()  -inicio))
        
    def load_targets_with_funds_revaluation(self):        
        self.mqtwTargetsPlus.table.setColumnCount(13)
        self.mqtwTargetsPlus.table.setRowCount(7)
        for i, s in enumerate([self.tr("January"),  self.tr("February"), self.tr("March"), self.tr("April"), self.tr("May"), self.tr("June"), self.tr("July"), self.tr("August"), self.tr("September"), self.tr("October"), self.tr("November"), self.tr("December"), self.tr("Total")]):
            self.mqtwTargetsPlus.table.setHorizontalHeaderItem(i, QTableWidgetItem(s))
        for i, s in enumerate([self.tr("Monthly target"), self.tr("Total gains"), self.tr("Funds revaluation"), self.tr("Total"), "",  self.tr("Accumulated target"), self.tr("Accumulated total gains")]):
            self.mqtwTargetsPlus.table.setVerticalHeaderItem(i, QTableWidgetItem(s))
        self.mqtwTargetsPlus.table.verticalHeader().show()       
        self.mqtwTargetsPlus.table.clearContents()
        self.mqtwTargetsPlus.applySettings()
        inicio=datetime.now()     

        sumd_g=Money(self.mem, 0, self.mem.localcurrency)
        sumf=Money(self.mem, 0, self.mem.localcurrency)
        for i, m in enumerate(self.tmm_data): 
            i=i+1
            sumd_g=sumd_g+m.d_g()
            sumf=sumf+m.funds_revaluation()
            self.mqtwTargetsPlus.table.setItem(0, i-1, self.mem.localmoney(self.annualtarget.monthly_balance()).qtablewidgetitem())
            self.mqtwTargetsPlus.table.setItem(1, i-1,m.d_g().qtablewidgetitem())
            self.mqtwTargetsPlus.table.setItem(2, i-1, m.funds_revaluation().qtablewidgetitem())
            self.mqtwTargetsPlus.table.setItem(3, i-1, self.mem.localmoney(m.d_g().amount+m.funds_revaluation().amount).qtablewidgetitem_with_target(self.annualtarget.monthly_balance()))
            
            self.mqtwTargetsPlus.table.setItem(5, i-1, self.mem.localmoney(self.annualtarget.monthly_balance()*i).qtablewidgetitem())
            self.mqtwTargetsPlus.table.setItem(6, i-1, self.mem.localmoney(sumd_g.amount+sumf.amount).qtablewidgetitem_with_target(self.annualtarget.monthly_balance()*i))
        self.mqtwTargetsPlus.table.setItem(0, 12, self.mem.localmoney(self.annualtarget.annual_balance()).qtablewidgetitem())
        self.mqtwTargetsPlus.table.setItem(1, 12, sumd_g.qtablewidgetitem())
        self.mqtwTargetsPlus.table.setItem(2, 12, sumf.qtablewidgetitem())
        self.mqtwTargetsPlus.table.setItem(3, 12, self.mem.localmoney(sumd_g.amount+sumf.amount).qtablewidgetitem_with_target(self.annualtarget.annual_balance()))
        self.mqtwTargetsPlus.table.setCurrentCell(2, date.today().month-1)   
                
        s=""
        s=s+self.tr("This report shows if the user reaches the annual and monthly target.") +"\n\n"
        s=s+self.tr("Total is the result of adding dividends to gain and funds revaluation")+"\n\n"
        s=s+self.tr("The cumulative target row shows compliance of the target in the year.")+"\n\n"
        s=s+self.tr("Green color shows that target has been reached.")
        self.lblTargetsPlus.setText(s)
        
        info("wdgTargets > load_data_targets_with_funds_revaluation: {0}".format(datetime.now()  -inicio))

    def load_invest_or_work(self):
        def qresult(dg_e):
            """Returns a qtablewidgetitem with work or invest
            dg_e=dividends+gains-expenses
            dg_i=dividends+gains-incomes
            """
            item=qcenter("")
            if dg_e.isZero():
                return item
            if not dg_e.isGETZero():
                item.setText(self.tr("Work"))
                item.setBackground(eQColor.Red)
            else:
                item.setText(self.tr("Invest"))
                item.setBackground(eQColor.Green)
            return item            
        ##------------------------------------------------
        inicio=datetime.now()            
        self.mqtwInvestOrWork.table.setColumnCount(13)
        self.mqtwInvestOrWork.table.setRowCount(6)
        for i, s in enumerate([self.tr("January"),  self.tr("February"), self.tr("March"), self.tr("April"), self.tr("May"), self.tr("June"), self.tr("July"), self.tr("August"), self.tr("September"), self.tr("October"), self.tr("November"), self.tr("December"), self.tr("Total")]):
            self.mqtwInvestOrWork.table.setHorizontalHeaderItem(i, QTableWidgetItem(s))
        for i, s in enumerate([self.tr("Total gains"), self.tr("Expenses"), "",  self.tr("Total gains - Expenses"), "",  self.tr("Result")]):
            self.mqtwInvestOrWork.table.setVerticalHeaderItem(i, QTableWidgetItem(s))
        self.mqtwInvestOrWork.table.verticalHeader().show()       
        self.mqtwInvestOrWork.table.clearContents()
        self.mqtwInvestOrWork.applySettings()
        for i, m in enumerate(self.tmm_data): 
            i=i+1
            self.mqtwInvestOrWork.table.setItem(0, i-1, m.d_g().qtablewidgetitem())
            self.mqtwInvestOrWork.table.setItem(1, i-1, m.expenses().qtablewidgetitem())
            self.mqtwInvestOrWork.table.setItem(3, i-1, (m.d_g()+m.expenses()).qtablewidgetitem())#Es mas porque es - y gastos -
            self.mqtwInvestOrWork.table.setItem(5, i-1, qresult(m.d_g()+m.expenses()))
        self.mqtwInvestOrWork.table.setItem(0, 12, self.tmm_data.d_g().qtablewidgetitem())
        self.mqtwInvestOrWork.table.setItem(1, 12, self.tmm_data.expenses().qtablewidgetitem())
        self.mqtwInvestOrWork.table.setItem(3, 12, (self.tmm_data.d_g()+self.tmm_data.expenses()).qtablewidgetitem())
        self.mqtwInvestOrWork.table.setItem(5, 12, qresult(self.tmm_data.d_g()+self.tmm_data.expenses()))
        self.mqtwInvestOrWork.table.setCurrentCell(2, date.today().month-1)   
        
        s=""
        s=s+self.tr("This report shows if the user could retire due to its investments") +"\n\n"
        s=s+self.tr("Total gains are the result of adding dividends to gains")+"\n\n"
        s=s+self.tr("Difference between total gains and expenses shows if user could cover his expenses with his total gains")+"\n\n"
        s=s+self.tr("Investment taxes are not evaluated in this report")
        self.lblInvestOrWork.setText(s)
        info ("wdgTotal > load invest or work: {0}".format(datetime.now()  -inicio))

    def load_make_ends_meet(self):
        def qresult(res):
            """Returns a qtablewidgetitem with yes or no
            """
            item=qcenter("")
            if res.isZero():
                return item
            if not res.isGETZero():
                item.setText(self.tr("No"))
                item.setBackground(eQColor.Red)
            else:
                item.setText(self.tr("Yes"))
                item.setBackground(eQColor.Green)
            return item            
        ##------------------------------------------------
        inicio=datetime.now()    
        self.mqtwMakeEndsMeet.table.setColumnCount(13)
        self.mqtwMakeEndsMeet.table.setRowCount(6)
        for i, s in enumerate([self.tr("January"),  self.tr("February"), self.tr("March"), self.tr("April"), self.tr("May"), self.tr("June"), self.tr("July"), self.tr("August"), self.tr("September"), self.tr("October"), self.tr("November"), self.tr("December"), self.tr("Total")]):
            self.mqtwMakeEndsMeet.table.setHorizontalHeaderItem(i, QTableWidgetItem(s))
        for i, s in enumerate([self.tr("Incomes"), self.tr("Expenses"), "",  self.tr("Incomes - Expenses"), "",  self.tr("Result")]):
            self.mqtwMakeEndsMeet.table.setVerticalHeaderItem(i, QTableWidgetItem(s))
        self.mqtwMakeEndsMeet.table.verticalHeader().show()      
        self.mqtwMakeEndsMeet.table.clearContents()
        self.mqtwMakeEndsMeet.applySettings()
        for i, m in enumerate(self.tmm_data): 
            i=i+1
            self.mqtwMakeEndsMeet.table.setItem(0, i-1, m.incomes().qtablewidgetitem())
            self.mqtwMakeEndsMeet.table.setItem(1, i-1, m.expenses().qtablewidgetitem())
            self.mqtwMakeEndsMeet.table.setItem(3, i-1, (m.incomes()+m.expenses()).qtablewidgetitem())#Es mas porque es - y gastos -
            self.mqtwMakeEndsMeet.table.setItem(5, i-1, qresult(m.incomes()+m.expenses()))
        self.mqtwMakeEndsMeet.table.setItem(0, 12, self.tmm_data.incomes().qtablewidgetitem())
        self.mqtwMakeEndsMeet.table.setItem(1, 12, self.tmm_data.expenses().qtablewidgetitem())
        self.mqtwMakeEndsMeet.table.setItem(3, 12, (self.tmm_data.incomes()+self.tmm_data.expenses()).qtablewidgetitem())
        self.mqtwMakeEndsMeet.table.setItem(5, 12, qresult(self.tmm_data.incomes()+self.tmm_data.expenses()))
        self.mqtwMakeEndsMeet.table.setCurrentCell(2, date.today().month-1)   
        
        s=""
        s=s+self.tr("This report shows if the user makes ends meet") +"\n\n"
        s=s+self.tr("Difference between incomes and expenses shows if user could cover his expenses with his incomes")
        self.lblMakeEndsMeet.setText(s)
        info("wdgTotal > load_make_ends_meet: {0}".format(datetime.now()  -inicio))


    def load_graphic(self, animations=True):               
        inicio=datetime.now()  

        self.wdgTS.clear()
        self.wdgTS.ts.setAnimations(animations)
        
        #Series creation
        last=self.tmm_graphics.last()
        lsNoLoses=self.wdgTS.ts.appendTemporalSeries(self.tr("Total without losses assets")+": {}".format(last.total_no_losses()))
        lsMain=self.wdgTS.ts.appendTemporalSeries(self.tr("Total assets")+": {}".format(last.total()))
        lsZero=self.wdgTS.ts.appendTemporalSeries(self.tr("Zero risk assets")+": {}".format(last.total_zerorisk()))
        lsBonds=self.wdgTS.ts.appendTemporalSeries(self.tr("Bond assets")+": {}".format(last.total_bonds()))
        lsRisk=self.wdgTS.ts.appendTemporalSeries(self.tr("Risk assets")+": {}".format(last.total()-last.total_zerorisk()-last.total_bonds()))

        progress = QProgressDialog(self.tr("Filling report data"), self.tr("Cancel"), 0,self.tmm_graphics.length())
        progress.setModal(True)
        progress.setWindowTitle(self.tr("Calculating data..."))
        progress.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
        progress.setValue(0)
        for m in self.tmm_graphics:
            if progress.wasCanceled():
                break
            progress.setValue(progress.value()+1)
            epoch=dtaware_day_end_from_date(m.last_day(), self.mem.localzone_name)
            total=m.total().amount
            zero=m.total_zerorisk().amount
            bonds=m.total_bonds().amount
            self.wdgTS.ts.appendTemporalSeriesData(lsMain, epoch, m.total_real().amount)
            self.wdgTS.ts.appendTemporalSeriesData(lsZero, epoch, m.total_zerorisk().amount)
            self.wdgTS.ts.appendTemporalSeriesData(lsBonds, epoch, m.total_bonds().amount)
            self.wdgTS.ts.appendTemporalSeriesData(lsRisk, epoch, total-zero-bonds)
            self.wdgTS.ts.appendTemporalSeriesData(lsNoLoses, epoch, m.total_no_losses_real().amount)
        self.wdgTS.display()
        
        info("wdgTotal > load_graphic: {0}".format(datetime.now()-inicio))
        self.load_graphic_invested(animations)
        
        
    def load_graphic_invested(self, animations=True):               
        inicio=datetime.now()  

        self.wdgTSInvested.clear()
        self.wdgTSInvested.ts.setAnimations(animations)
        
        #Series creation
        last=self.tmm_graphics.last()
        lsNoLoses=self.wdgTSInvested.ts.appendTemporalSeries(self.tr("Total without losses assets")+": {}".format(last.total_no_losses()))
        lsMain=self.wdgTSInvested.ts.appendTemporalSeries(self.tr("Total assets")+": {}".format(last.total()))
        lsInvested=self.wdgTSInvested.ts.appendTemporalSeries(self.tr("Invested assets") + ": {}".format(last.total_invested()))
        lsAccounts=self.wdgTSInvested.ts.appendTemporalSeries(self.tr("Accounts assets") + ": {}".format(last.total_accounts()))

        progress = QProgressDialog(self.tr("Filling report data"), self.tr("Cancel"), 0,self.tmm_graphics.length())
        progress.setModal(True)
        progress.setWindowTitle(self.tr("Calculating data..."))
        progress.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
        progress.setValue(0)
        for m in self.tmm_graphics:
            if progress.wasCanceled():
                break
            progress.setValue(progress.value()+1)
            epoch=dtaware_day_end_from_date(m.last_day(), self.mem.localzone_name)
            self.wdgTSInvested.ts.appendTemporalSeriesData(lsMain, epoch, m.total_real().amount)
            self.wdgTSInvested.ts.appendTemporalSeriesData(lsNoLoses, epoch, m.total_no_losses_real().amount)
            self.wdgTSInvested.ts.appendTemporalSeriesData(lsInvested, epoch, m.total_invested_real().amount)
            self.wdgTSInvested.ts.appendTemporalSeriesData(lsAccounts, epoch, m.total_accounts().amount)
        self.wdgTSInvested.display()
        
        info("wdgTotal > load_graphic_invested: {0}".format(datetime.now()-inicio))

    def on_wyData_mychanged(self):
        self.tmm_data=TotalMonthManager_from_manager_extracting_year(self.tmm, self.wyData.year)
        self.load_data()    
        self.load_targets()
        self.load_targets_with_funds_revaluation()
        self.load_invest_or_work()
        self.load_make_ends_meet()

    def on_wyChart_mychanged(self):
        self.tmm_graphics=TotalMonthManager_from_manager_extracting_from_month(self.tmm, self.wyChart.year, 1, date.today().year, date.today().month)
        self.load_graphic()      
        
    def on_cmdTargets_released(self):
        self.annualtarget.percentage=self.spinTarget.value()
        self.annualtarget.save()
        self.mem.con.commit()
        self.load_targets()
        self.load_targets_with_funds_revaluation()

    def on_tab_currentChanged(self, index):
        if  index==1 and self.wdgTS.isEmpty(): #If has not been plotted, plots it.
            self.on_wyChart_mychanged()
        
    @pyqtSlot() 
    def on_actionShowIncomes_triggered(self):
        newtab = QWidget()
        horizontalLayout = QHBoxLayout(newtab)
        wdg = mqtwObjects(newtab)
        wdg.setSettings(self.mem.settings, "wdgTotal","mqtwShowIncomes")
        wdg.table.setSelectionBehavior(QAbstractItemView.SelectItems)
        
        id_tiposoperaciones=2
        set=AccountOperationManagerHeterogeneus(self.mem)
        conceptslist=ConceptManager_considered_dividends_in_totals(self.mem).array_of_ids()
        if self.month==13:#Year
            tabtitle=self.tr("Incomes of {}").format(self.wyData.year)
            set.load_from_db("""select id_opercuentas, datetime, id_conceptos, id_tiposoperaciones, importe, comentario, id_cuentas 
                                                    from opercuentas 
                                                    where id_tiposoperaciones={0} and 
                                                        date_part('year',datetime)={1} and
                                                        id_conceptos not in ({2}) 
                                                union all select id_opercuentas, datetime, id_conceptos, id_tiposoperaciones, importe, comentario, id_cuentas 
                                                    from opertarjetas,tarjetas 
                                                    where opertarjetas.id_tarjetas=tarjetas.id_tarjetas and 
                                                        id_tiposoperaciones={0} and 
                                                        date_part('year',datetime)={1}""".format (id_tiposoperaciones, self.wyData.year, list2string(conceptslist)))
        else:#Month
            tabtitle=self.tr("Incomes of {0} of {1}").format(self.mqtw.table.horizontalHeaderItem(self.month-1).text(), self.wyData.year)
            set.load_from_db("""select id_opercuentas, datetime, id_conceptos, id_tiposoperaciones, importe, comentario, id_cuentas 
                                                    from opercuentas 
                                                    where id_tiposoperaciones={0} and 
                                                        date_part('year',datetime)={1} and 
                                                        date_part('month',datetime)={2} and 
                                                        id_conceptos not in ({3}) 
                                                union all select id_opercuentas, datetime, id_conceptos, id_tiposoperaciones, importe, comentario, id_cuentas 
                                                    from opertarjetas,tarjetas 
                                                    where opertarjetas.id_tarjetas=tarjetas.id_tarjetas and 
                                                        id_tiposoperaciones={0} and 
                                                        date_part('year',datetime)={1} and 
                                                        date_part('month',datetime)={2}""".format (id_tiposoperaciones, self.wyData.year, self.month, list2string(conceptslist)))
        set.myqtablewidget(wdg,  True)
        wdg.drawOrderBy(0, False)
        horizontalLayout.addWidget(wdg)
        self.tab.addTab(newtab, tabtitle)
        self.tab.setCurrentWidget(newtab)            

       
    @pyqtSlot() 
    def on_actionShowExpenses_triggered(self):     
        newtab = QWidget()
        horizontalLayout = QHBoxLayout(newtab)
        wdg = mqtwObjects(newtab)
        wdg.setSettings(self.mem.settings, "wdgTotal","mqtwShowExpenses")
        wdg.table.setSelectionBehavior(QAbstractItemView.SelectItems)
        
        id_tiposoperaciones=1
        set=AccountOperationManagerHeterogeneus(self.mem)
        if self.month==13:#Year
            tabtitle=self.tr("Expenses of {0}").format(self.wyData.year)
            set.load_from_db("""select id_opercuentas, datetime, id_conceptos, id_tiposoperaciones, importe, comentario, id_cuentas , -1 as id_tarjetas 
                                                from opercuentas 
                                                where id_tiposoperaciones={0} and 
                                                           date_part('year',datetime)={1} 
                                                union all 
                                                select id_opercuentas, datetime, id_conceptos, id_tiposoperaciones, importe, comentario, id_cuentas ,tarjetas.id_tarjetas as id_tarjetas 
                                                from opertarjetas,tarjetas 
                                                where opertarjetas.id_tarjetas=tarjetas.id_tarjetas and 
                                                            id_tiposoperaciones={0} and 
                                                            date_part('year',datetime)={1}
                                                order by datetime""".format (id_tiposoperaciones, self.wyData.year))
        else:#Month
            tabtitle=self.tr("Expenses of {0} of {1}").format(self.mqtw.table.horizontalHeaderItem(self.month-1).text(), self.wyData.year)
            set.load_from_db("""select id_opercuentas, datetime, id_conceptos, id_tiposoperaciones, importe, comentario, id_cuentas , -1 as id_tarjetas 
                                                from opercuentas 
                                                where id_tiposoperaciones={0} and 
                                                           date_part('year',datetime)={1} and 
                                                           date_part('month',datetime)={2} 
                                                union all 
                                                select id_opercuentas, datetime, id_conceptos, id_tiposoperaciones, importe, comentario, id_cuentas ,tarjetas.id_tarjetas as id_tarjetas 
                                                from opertarjetas,tarjetas 
                                                where opertarjetas.id_tarjetas=tarjetas.id_tarjetas and 
                                                            id_tiposoperaciones={0} and 
                                                            date_part('year',datetime)={1} and 
                                                            date_part('month',datetime)={2}
                                                order by datetime""".format (id_tiposoperaciones, self.wyData.year, self.month))
        set.myqtablewidget(wdg,  True)
        wdg.drawOrderBy(0, False)
        horizontalLayout.addWidget(wdg)
        self.tab.addTab(newtab, tabtitle)
        self.tab.setCurrentWidget(newtab)

    @pyqtSlot() 
    def on_actionShowSellingOperations_triggered(self):
        def show_all():
            newtab = QWidget()
            horizontalLayout = QVBoxLayout(newtab)
            wdg = mqtwObjects(newtab)
            wdg.setSettings(self.mem.settings, "wdgTotal","tblShowShellingOperations")
            
            positive=Money(self.mem, 0, self.mem.localcurrency)
            negative=Money(self.mem, 0, self.mem.localcurrency)
            lbl=QLabel(newtab)
            
            set=InvestmentOperationHistoricalHeterogeneusManager(self.mem)
            for i in self.mem.data.investments.arr:
                for o in i.op_historica.arr:
                    if self.month==13:#Year
                        tabtitle=self.tr("Selling operations of {0}").format(self.wyData.year)
                        if o.dt_end.year==self.wyData.year:
                            set.arr.append(o)
                            if o.consolidado_bruto().isGETZero():
                                positive=positive+o.consolidado_bruto().local()
                            else:
                                negative=negative+o.consolidado_bruto().local()
                    else:#Month
                        tabtitle=self.tr("Selling operations of {0} of {1}").format(self.mqtw.table.horizontalHeaderItem(self.month-1).text(), self.wyData.year)
                        if o.dt_end.year==self.wyData.year and o.dt_end.month==self.month:#Venta y traspaso fondos inversion
                            set.arr.append(o)
                            if o.consolidado_bruto().isGETZero():
                                positive=positive+o.consolidado_bruto().local()
                            else:
                                negative=negative+o.consolidado_bruto().local()
            set.order_by_fechaventa()
            set.myqtablewidget(wdg)
            horizontalLayout.addWidget(wdg)
            lbl.setText(self.tr("Positive gross selling operations: {}. Negative gross selling operations: {}.").format(positive, negative))
            horizontalLayout.addWidget(lbl)
            self.tab.addTab(newtab, tabtitle)
            self.tab.setCurrentWidget(newtab)

        def show_more():
            newtab = QWidget()
            horizontalLayout = QVBoxLayout(newtab)
            wdg= mqtwObjects(newtab)
            wdg.table.setSelectionBehavior(QAbstractItemView.SelectItems)
            
            positive=Decimal(0)
            negative=Decimal(0)
            lbl=QLabel(newtab)
            
            set=InvestmentOperationHistoricalHeterogeneusManager(self.mem)
            for i in self.mem.data.investments.arr:
                for o in i.op_historica.arr:
                    if self.month==13:#Year
                        tabtitle=self.tr("Selling operations of {0}  (Sold after a year)").format(self.wyData.year)
                        if o.dt_end.year==self.wyData.year and o.tipooperacion.id in (5, 8)  and o.less_than_a_year()==False:#Venta y traspaso fondos inversion
                            set.arr.append(o)
                            if o.consolidado_bruto()>=0:
                                positive=positive+o.consolidado_bruto()
                            else:
                                negative=negative+o.consolidado_bruto()
                    else:#Month
                        tabtitle=self.tr("Selling operations of {0} of {1} (Sold after a year)").format(self.mqtw.table.horizontalHeaderItem(self.month-1).text(), self.wyData.year)
                        if o.dt_end.year==self.wyData.year and o.dt_end.month==self.month and o.tipooperacion.id in (5, 8)  and o.less_than_a_year()==False:#Venta y traspaso fondos inversion
                            set.arr.append(o)
                            if o.consolidado_bruto()>=0:
                                positive=positive+o.consolidado_bruto()
                            else:
                                negative=negative+o.consolidado_bruto()
            set.order_by_fechaventa()
            set.myqtablewidget(wdg, "wdgTotal")
            horizontalLayout.addWidget(wdg)
            lbl.setText(self.tr("Positive gross selling operations: {}. Negative gross selling operations: {}.").format(self.mem.localmoney(positive), self.mem.localmoney(negative)))
            horizontalLayout.addWidget(lbl)
            self.tab.addTab(newtab, tabtitle)
            self.tab.setCurrentWidget(newtab)
        def show_less():
            newtab = QWidget()
            horizontalLayout = QVBoxLayout(newtab)
            wdg = mqtwObjects(newtab)
            wdg.setSettings(self.mem.settings, "wdgTotal","tblShowSellingLessOperations")
            wdg.table.setSelectionBehavior(QAbstractItemView.SelectItems)
            
            positive=Decimal(0)
            negative=Decimal(0)
            lbl=QLabel(newtab)
            
            set=InvestmentOperationHistoricalHeterogeneusManager(self.mem)
            for i in self.mem.data.investments.arr:
                for o in i.op_historica.arr:
                    if self.month==13:#Year
                        tabtitle=self.tr("Selling operations of {0} (Sold before a year)").format(self.wyData.year)
                        if o.dt_end.year==self.wyData.year and o.tipooperacion.id in (5, 8) and o.less_than_a_year()==True:#Venta y traspaso fondos inversion
                            set.arr.append(o)
                            if o.consolidado_bruto()>=0:
                                positive=positive+o.consolidado_bruto()
                            else:
                                negative=negative+o.consolidado_bruto()
                    else:#Month
                        tabtitle=self.tr("Selling operations of {0} of {1} (Sold before a year)").format(self.mqtw.table.horizontalHeaderItem(self.month-1).text(), self.wyData.year)
                        if o.dt_end.year==self.wyData.year and o.dt_end.month==self.month and o.tipooperacion.id in (5, 8) and o.less_than_a_year()==True:#Venta y traspaso fondos inversion
                            set.arr.append(o)
                            if o.consolidado_bruto()>=0:
                                positive=positive+o.consolidado_bruto()
                            else:
                                negative=negative+o.consolidado_bruto()
            set.order_by_fechaventa()
            set.myqtablewidget(wdg)
            horizontalLayout.addWidget(wdg)
            lbl.setText(self.tr("Positive gross selling operations: {}. Negative gross selling operations: {}.").format(self.mem.localmoney(positive), self.mem.localmoney(negative)))
            horizontalLayout.addWidget(lbl)
            self.tab.addTab(newtab, tabtitle)
            self.tab.setCurrentWidget(newtab)            
        ##################################
        if self.mem.gainsyear==True:
            show_less()
            show_more()
        else:
            show_all()

    @pyqtSlot() 
    def on_actionShowDividends_triggered(self):
        newtab = QWidget()
        horizontalLayout = QHBoxLayout(newtab)
        wdg = mqtwObjects(newtab)
        wdg.setSettings(self.mem.settings,"wdgTotal","mqtwShowDividends")
        wdg.table.setSelectionBehavior(QAbstractItemView.SelectItems)
        
        set=DividendHeterogeneusManager(self.mem)
        for inv in self.mem.data.investments.arr:
            for dividend in inv.dividends.arr:
                if self.month==13:
                    tabtitle=self.tr("Dividends of {0}").format(self.wyData.year)
                    if dividend.datetime.year==self.wyData.year:
                        set.append(dividend)
                else:# With mounth
                    tabtitle=self.tr("Dividends of {0} of {1}").format(self.mqtw.table.horizontalHeaderItem(self.month-1).text(), self.wyData.year)
                    if dividend.datetime.year==self.wyData.year and dividend.datetime.month==self.month:
                        set.append(dividend)
        set.order_by_datetime()
        set.myqtablewidget(wdg,  True)
        horizontalLayout.addWidget(wdg)
        self.tab.addTab(newtab, tabtitle)
        self.tab.setCurrentWidget(newtab)            

    @pyqtSlot() 
    def on_actionShowComissions_triggered(self):
        newtab = QWidget()
        vlayout = QVBoxLayout(newtab)
        wdg = mqtwObjects(newtab)
        wdg.setSettings(self.mem.settings,"wdgTotal","mqtwShowComissions")
        wdg.table.setSelectionBehavior(QAbstractItemView.SelectItems)
        wdg.table.verticalHeader().show()
        
        wdg.table.setColumnCount(13)
        wdg.table.setHorizontalHeaderItem(0, QTableWidgetItem(self.tr( "January" )))
        wdg.table.setHorizontalHeaderItem(1, QTableWidgetItem(self.tr( "February" )))
        wdg.table.setHorizontalHeaderItem(2, QTableWidgetItem(self.tr( "March" )))
        wdg.table.setHorizontalHeaderItem(3, QTableWidgetItem(self.tr( "April" )))
        wdg.table.setHorizontalHeaderItem(4, QTableWidgetItem(self.tr( "May" )))
        wdg.table.setHorizontalHeaderItem(5, QTableWidgetItem(self.tr( "June" )))
        wdg.table.setHorizontalHeaderItem(6, QTableWidgetItem(self.tr( "July" )))
        wdg.table.setHorizontalHeaderItem(7, QTableWidgetItem(self.tr( "August" )))
        wdg.table.setHorizontalHeaderItem(8, QTableWidgetItem(self.tr( "September" )))
        wdg.table.setHorizontalHeaderItem(9, QTableWidgetItem(self.tr( "October" )))
        wdg.table.setHorizontalHeaderItem(10, QTableWidgetItem(self.tr( "November" )))
        wdg.table.setHorizontalHeaderItem(11, QTableWidgetItem(self.tr( "December" )))
        wdg.table.setHorizontalHeaderItem(12, QTableWidgetItem(self.tr( "Total" )))
        
        wdg.table.setRowCount(4)
        wdg.table.setVerticalHeaderItem(0, QTableWidgetItem(self.tr( "Bank commissions" )))
        wdg.table.setVerticalHeaderItem(1, QTableWidgetItem(self.tr( "Custody fees" )))
        wdg.table.setVerticalHeaderItem(2, QTableWidgetItem(self.tr( "Invesment operation commissions" )))
        wdg.table.setVerticalHeaderItem(3, QTableWidgetItem(self.tr( "Total" )))
        wdg.applySettings()
        (sum_bank_commissions, sum_custody_fees, sum_investment_commissions)=(Decimal("0"), Decimal("0"), Decimal("0"))

        for column in range (12):
            bank_commissions=none2decimal0(self.mem.con.cursor_one_row("""select sum(importe) 
                                                                                                            from opercuentas 
                                                                                                            where id_conceptos=%s and 
                                                                                                                date_part('year',datetime)=%s and 
                                                                                                                date_part('month',datetime)=%s;""", (38, self.wyData.year, column+1))[0])
            wdg.table.setItem(0, column, self.mem.localmoney(bank_commissions).qtablewidgetitem())
            sum_bank_commissions=sum_bank_commissions+bank_commissions
            
            custody_fees=none2decimal0(self.mem.con.cursor_one_row("""select sum(importe) 
                                                                                                            from opercuentas 
                                                                                                            where id_conceptos=%s and 
                                                                                                                date_part('year',datetime)=%s and 
                                                                                                                date_part('month',datetime)=%s;""", (59, self.wyData.year, column+1))[0])
            wdg.table.setItem(1, column, self.mem.localmoney(custody_fees).qtablewidgetitem())
            sum_custody_fees=sum_custody_fees+custody_fees
            
            investment_commissions=-none2decimal0(self.mem.con.cursor_one_row("""select sum(comision) 
                                                                                                            from operinversiones  
                                                                                                            where date_part('year',datetime)=%s and 
                                                                                                                date_part('month',datetime)=%s;""", (self.wyData.year, column+1))[0])
            wdg.table.setItem(2, column, self.mem.localmoney(investment_commissions).qtablewidgetitem())
            sum_investment_commissions=sum_investment_commissions+investment_commissions
            
            wdg.table.setItem(3, column, self.mem.localmoney(bank_commissions+custody_fees+investment_commissions).qtablewidgetitem())    
        wdg.table.setItem(0, 12, self.mem.localmoney(sum_bank_commissions).qtablewidgetitem()) 
        wdg.table.setItem(1, 12, self.mem.localmoney(sum_custody_fees).qtablewidgetitem())    
        wdg.table.setItem(2, 12, self.mem.localmoney(sum_investment_commissions).qtablewidgetitem())
        wdg.table.setItem(3, 12, self.mem.localmoney(sum_bank_commissions+sum_custody_fees+sum_investment_commissions).qtablewidgetitem())
        vlayout.addWidget(wdg)

        #Number of operations
        num_operations=0
        settypes=self.mem.types.with_operation_commissions_types()
        for i, type in enumerate(settypes.arr):
            for inv in self.mem.data.investments.arr:
                if inv.product.type.id==type.id:
                    for o in inv.op.arr:
                        if o.datetime.year==self.wyData.year and o.tipooperacion.id in (4, 5):#Purchase and sale
                            num_operations=num_operations+1            
        if num_operations>0:
            label=QLabel(newtab)
            font = QFont()
            font.setPointSize(8)
            font.setBold(True)
            font.setWeight(75)
            label.setFont(font)
            label.setAlignment(Qt.AlignCenter)
            cs=self.mem.localmoney
            label.setText(self.tr("Number of purchase and sale investment operations: {}. Commissions average: {}".format(int(num_operations), cs(sum_investment_commissions/num_operations))))
            vlayout.addWidget(label)
            
        self.tab.addTab(newtab, self.tr("Commision report of {}").format(self.wyData.year))
        self.tab.setCurrentWidget(newtab)        
        

    @pyqtSlot() 
    def on_actionGainsByProductType_triggered(self):
        newtab = QWidget()
        vlayout = QVBoxLayout(newtab)
        wdg = mqtw(newtab)
        wdg.setSettings(self.mem.settings,"wdgTotal","mqtwGainsByProductType")
        headers=[self.tr( "Product type" ), self.tr( "Gross gains" ), self.tr("Gross dividends"), self.tr( "Net gains" ), self.tr("Net dividends")]
        
        
        wdg.applySettings()
        sum_gains=Money(self.mem)
        sum_dividens=Money(self.mem)
        sum_netgains=Money(self.mem)
        sum_netdividends=Money(self.mem)
        
        settypes=self.mem.types.investment_types()
        wdg.table.setRowCount(settypes.length()+1)
        
        data=[]
        for i, type in enumerate(settypes.arr):
            wdg.table.setItem(i, 0, qleft(type.name))    
            gains=Money(self.mem,  0,  self.mem.localcurrency)
            netgains=Money(self.mem, 0, self.mem.localcurrency)
            dividends=Money(self.mem,  0,  self.mem.localcurrency)
            netdividends=Money(self.mem,  0, self.mem.localcurrency)
            for inv in self.mem.data.investments.arr:
                if inv.product.type.id==type.id:
                    #gains
                    for o in inv.op_historica.arr:
                        if o.dt_end.year==self.wyData.year:
                            gains=gains+o.consolidado_bruto(eMoneyCurrency.User)
                            netgains=netgains+o.consolidado_neto(eMoneyCurrency.User)
                    #dividends
                    inv.needStatus(3)
                    for d in inv.dividends.arr:
                        if d.datetime.year==self.wyData.year:
                            dividends=dividends+d.gross(eMoneyCurrency.User)
                            netdividends=netdividends+d.net(eMoneyCurrency.User)
            data.append([type.name, gains, dividends, netgains, netdividends])
            sum_gains=sum_gains+gains
            sum_netgains=sum_netgains+netgains
            sum_dividens=sum_dividens+dividends
            sum_netdividends=sum_netdividends+netdividends
        data.append([self.tr("Total"), sum_gains, sum_dividens, sum_netgains, sum_netdividends])
        wdg.setData(headers, None, data)

        label=QLabel(newtab)
        font = QFont()
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)
        label.setFont(font)
        label.setAlignment(Qt.AlignCenter)
        label.setText(self.tr("Gross gains + Gross dividends: {} + {} = {}\nNet gains + Net dividens: {} + {} = {}".format(sum_gains, sum_dividens, sum_gains+sum_dividens, sum_netgains, sum_netdividends, sum_netgains+sum_netdividends)))
            
        vlayout.addWidget(wdg)
        vlayout.addWidget(label)
        self.tab.addTab(newtab, self.tr("Gains by product type of {}").format(self.wyData.year))
        self.tab.setCurrentWidget(newtab)        

    @pyqtSlot() 
    def on_actionShowTaxes_triggered(self):
        newtab = QWidget()
        horizontalLayout = QVBoxLayout(newtab)
        wdg = mqtwObjects(newtab)
        wdg.setSettings(self.mem.settings,"wdgTotal","myqtwShowPaidTaxes")
        wdg.table.setSelectionBehavior(QAbstractItemView.SelectItems)
        wdg.table.verticalHeader().show()        
        
        wdg.table.setColumnCount(13)
        wdg.table.setHorizontalHeaderItem(0, QTableWidgetItem(self.tr( "January" )))
        wdg.table.setHorizontalHeaderItem(1, QTableWidgetItem(self.tr( "February" )))
        wdg.table.setHorizontalHeaderItem(2, QTableWidgetItem(self.tr( "March" )))
        wdg.table.setHorizontalHeaderItem(3, QTableWidgetItem(self.tr( "April" )))
        wdg.table.setHorizontalHeaderItem(4, QTableWidgetItem(self.tr( "May" )))
        wdg.table.setHorizontalHeaderItem(5, QTableWidgetItem(self.tr( "June" )))
        wdg.table.setHorizontalHeaderItem(6, QTableWidgetItem(self.tr( "July" )))
        wdg.table.setHorizontalHeaderItem(7, QTableWidgetItem(self.tr( "August" )))
        wdg.table.setHorizontalHeaderItem(8, QTableWidgetItem(self.tr( "September" )))
        wdg.table.setHorizontalHeaderItem(9, QTableWidgetItem(self.tr( "October" )))
        wdg.table.setHorizontalHeaderItem(10, QTableWidgetItem(self.tr( "November" )))
        wdg.table.setHorizontalHeaderItem(11, QTableWidgetItem(self.tr( "December" )))
        wdg.table.setHorizontalHeaderItem(12, QTableWidgetItem(self.tr( "Total" )))
        
        wdg.table.setRowCount(5)
        wdg.table.setVerticalHeaderItem(0, QTableWidgetItem(self.tr( "Investment operation retentions" )))
        wdg.table.setVerticalHeaderItem(1, QTableWidgetItem(self.tr( "Dividend retentions" )))
        wdg.table.setVerticalHeaderItem(2, QTableWidgetItem(self.tr( "Other paid taxes" )))
        wdg.table.setVerticalHeaderItem(3, QTableWidgetItem(self.tr( "Returned taxes" )))
        wdg.table.setVerticalHeaderItem(4,  QTableWidgetItem(self.tr( "Total" )))

        wdg.applySettings()
        (sum_io_retentions, sum_div_retentions, sum_other_taxes,  sum_returned_taxes)=(Decimal("0"), Decimal("0"), Decimal("0"), Decimal("0"))

        for column in range (12):
            io_retentions=-none2decimal0(self.mem.con.cursor_one_row("""select sum(impuestos) 
                                                                                                                                from operinversiones  
                                                                                                                                where date_part('year',datetime)=%s and 
                                                                                                                                    date_part('month',datetime)=%s;""", (self.wyData.year, column+1))[0])
            wdg.table.setItem(0, column, self.mem.localmoney(io_retentions).qtablewidgetitem())
            sum_io_retentions=sum_io_retentions+io_retentions
            
            div_retentions=-none2decimal0(self.mem.con.cursor_one_row("""select sum(retencion) 
                                                                                                            from dividends 
                                                                                                            where date_part('year',fecha)=%s and 
                                                                                                                date_part('month',fecha)=%s;""", (self.wyData.year, column+1))[0])
            wdg.table.setItem(1, column, self.mem.localmoney(div_retentions).qtablewidgetitem())
            sum_div_retentions=sum_div_retentions+div_retentions
            
            other_taxes=none2decimal0(self.mem.con.cursor_one_row("""select sum(importe) 
                                                                                                            from opercuentas 
                                                                                                            where id_conceptos=%s and 
                                                                                                                date_part('year',datetime)=%s and 
                                                                                                                date_part('month',datetime)=%s;""", (37, self.wyData.year, column+1))[0])
            wdg.table.setItem(2, column, self.mem.localmoney(other_taxes).qtablewidgetitem())
            sum_other_taxes=sum_other_taxes+other_taxes         
            
            returned_taxes=none2decimal0(self.mem.con.cursor_one_row("""select sum(importe) 
                                                                                                            from opercuentas 
                                                                                                            where id_conceptos=%s and 
                                                                                                                date_part('year',datetime)=%s and 
                                                                                                                date_part('month',datetime)=%s;""", (6, self.wyData.year, column+1))[0])
            wdg.table.setItem(3, column, self.mem.localmoney(returned_taxes).qtablewidgetitem())
            sum_returned_taxes=sum_returned_taxes+returned_taxes
            
            wdg.table.setItem(4, column, self.mem.localmoney(io_retentions+div_retentions+other_taxes+returned_taxes))    
        
        wdg.table.setItem(0, 12, self.mem.localmoney(sum_io_retentions).qtablewidgetitem())
        wdg.table.setItem(1, 12, self.mem.localmoney(sum_div_retentions).qtablewidgetitem())
        wdg.table.setItem(2, 12, self.mem.localmoney(sum_other_taxes).qtablewidgetitem())
        wdg.table.setItem(3, 12, self.mem.localmoney(sum_returned_taxes).qtablewidgetitem())
        wdg.table.setItem(4, 12, self.mem.localmoney(sum_io_retentions+sum_div_retentions+sum_other_taxes+sum_returned_taxes).qtablewidgetitem())

        horizontalLayout.addWidget(wdg)
        self.tab.addTab(newtab, self.tr("Taxes report of {}").format(self.wyData.year))
        self.tab.setCurrentWidget(newtab)        
            

    def on_tab_tabCloseRequested(self, index):
        """Only removes dinamic tabs"""
        if index in (0, 1):
            qmessagebox(self.tr("You can't close this tab"))
        else:
            self.tab.setCurrentIndex(0)
            self.tab.removeTab(index)
            
    def on_mqtw_cellDoubleClicked(self, row, column):
        if row==0:#incomes
            self.on_actionShowIncomes_triggered()
        elif row==1:#Gains
            self.on_actionShowSellingOperations_triggered()
        elif row==2:#Dividends
            self.on_actionShowDividends_triggered()
        elif row==3: #Expenses
            self.on_actionShowExpenses_triggered()
        elif row==7: #Investments
            totalmonth=self.tmm_data.arr[column]
            qmessagebox(self.tr("Investments with daily adjustments aren't sumarized here, due to they are sumarized in accounts.") + "\n\n" + self.tr("Their balance at the end of {}-{} is {}").format(totalmonth.year, totalmonth.month, totalmonth.total_investments_with_daily_adjustments()))
        else:
            qmessagebox(self.tr("You only can double click in incomes, gains, dividends and expenses.") + "\n\n" + self.tr("Make right click to see commission and tax reports"))

    def on_mqtw_customContextMenuRequested(self,  pos):
        menu=QMenu()
        menu.addAction(self.actionShowComissions)
        menu.addSeparator()
        menu.addAction(self.actionShowTaxes)
        menu.addSeparator()
        menu.addAction(self.actionGainsByProductType)
        menu.exec_(self.mqtw.table.mapToGlobal(pos))

    @pyqtSlot()
    def on_mqtw_itemSelectionChanged(self):
        debug("NOW")
        self.month=None
        for i in self.mqtw.table.selectedItems():#itera por cada item no row.
            self.month=i.column()+1
        debug("Selected month: {0}.".format(self.month))
