from PyQt5.QtCore import pyqtSlot,  Qt
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtChart import QChart
from PyQt5.QtWidgets import  QWidget, QMenu, QProgressDialog, QVBoxLayout, QHBoxLayout, QAbstractItemView, QTableWidgetItem, QLabel
from xulpymoney.libxulpymoney import AnnualTarget, Assets, Money, AccountOperationManager, DividendHeterogeneusManager, InvestmentOperationHistoricalHeterogeneusManager, Percentage
from xulpymoney.libxulpymoneyfunctions import  list2string, none2decimal0, qcenter, qleft, qmessagebox,  day_end_from_date
from xulpymoney.libxulpymoneytypes import eQColor
from xulpymoney.ui.myqtablewidget import myQTableWidget
from decimal import Decimal
from xulpymoney.ui.canvaschart import VCTemporalSeries
from xulpymoney.ui.Ui_wdgTotal import Ui_wdgTotal
import datetime
import logging



class TotalMonth:
    """All values are calculated in last day of the month"""
    def __init__(self, mem, year, month):
        self.mem=mem
        self.year=year
        self.month=month
        self.expenses_value=None
        self.no_loses_value=None
        self.dividends_value=None
        self.incomes_value=None
        self.funds_revaluation_value=None
        self.gains_value=None
        self.total_accounts_value=None
        self.total_investments_value=None
        self.total_zerorisk_value=None
        self.total_bonds_value=None
        
    def i_d_g_e(self):
        return self.incomes()+self.dividends()+self.gains()+self.expenses()
        
    def d_g(self):
        """Dividends+gains"""
        return self.gains()+self.dividends()

        
    def expenses(self):
        if self.expenses_value==None:
            self.expenses_value=Assets(self.mem).saldo_por_tipo_operacion( self.year,self.month, 1)#La facturación de tarjeta dentro esta por el union
        return self.expenses_value
        
    def dividends(self):
        if self.dividends_value==None:
            self.dividends_value=Assets(self.mem).dividends_neto(  self.year, self.month)
        return self.dividends_value
        
    def incomes(self):
        if self.incomes_value==None:
            self.incomes_value=Assets(self.mem).saldo_por_tipo_operacion(  self.year,self.month,2)-self.dividends()
        return self.incomes_value
        
    def gains(self):
        if self.gains_value==None:
            self.gains_value=Assets(self.mem).consolidado_neto(self.mem.data.investments, self.year, self.month)
        return self.gains_value
        
    def funds_revaluation(self):
        if self.funds_revaluation_value==None:
            self.funds_revaluation_value=self.mem.data.investments_active().revaluation_monthly(2, self.year, self.month)#2 if type funds
        return self.funds_revaluation_value
        
    def name(self):
        return "{}-{}".format(self.year, self.month)
        
    def last_day(self):
        date=datetime.date(self.year, self.month, 1)
        if date.month == 12:
            return date.replace(day=31)
        return date.replace(month=date.month+1, day=1) - datetime.timedelta(days=1)
            
    def first_day(self):
        return datetime.date(self.year, self.month, self.day)
        
    def total(self):
        """Total assests in the month"""
        return self.total_accounts()+self.total_investments()
        
    def total_accounts(self):
        if self.total_accounts_value==None:
            self.total_accounts_value=Assets(self.mem).saldo_todas_cuentas( self.last_day())
        return self.total_accounts_value
        
    def total_investments(self):
        if self.total_investments_value==None:
            self.total_investments_value=Assets(self.mem).saldo_todas_inversiones(self.mem.data.investments,  self.last_day())
        return self.total_investments_value
        
    def total_zerorisk(self): 
        if self.total_zerorisk_value==None:
            self.total_zerorisk_value=Assets(self.mem).patrimonio_riesgo_cero(self.mem.data.investments, self.last_day())
        return self.total_zerorisk_value
        
    def total_bonds(self):
        if self.total_bonds_value==None:
            self.total_bonds_value=Assets(self.mem).saldo_todas_inversiones_bonds(self.last_day())
        return self.total_bonds_value

    def total_no_losses(self):
        """
        """
        if self.no_loses_value==None:
            self.no_loses_value=Assets(self.mem).invested(self.last_day())+self.total_accounts()
        return self.no_loses_value        
class TotalYear:
    """Set of 12 totalmonths in the same year"""
    def __init__(self, mem, year):
        self.mem=mem
        self.year=year
        self.arr=[]
        self.total_last_year=Assets(self.mem).saldo_total(self.mem.data.investments,  datetime.date(self.year-1, 12, 31))
        self.generate()
        
    def generate(self):
        for i in range(1, 13):
            self.arr.append(TotalMonth(self.mem, self.year, i))
        
    def find(self, year, month):
        for m in self.arr:
            if m.year==year and m.month==month:
                return m
        return None
        
    def expenses(self):
        result=Money(self.mem, 0, self.mem.localcurrency)
        for m in self.arr:
            result=result+m.expenses()
        return result
        
    def i_d_g_e(self):
        return self.incomes()+self.dividends()+self.gains()+self.expenses()
        
    def funds_revaluation(self):
        return self.mem.data.investments_active().revaluation_annual(2, self.year)#2 if type funds
        
        
    def incomes(self):
        result=Money(self.mem, 0, self.mem.localcurrency)
        for m in self.arr:
            result=result+m.incomes()
        return result

    def gains(self):
        result=Money(self.mem, 0, self.mem.localcurrency)
        for m in self.arr:
            result=result+m.gains()
        return result        

    def dividends(self):
        result=Money(self.mem, 0, self.mem.localcurrency)
        for m in self.arr:
            result=result+m.dividends()
        return result
        
    def d_g(self):
        """Dividends+gains"""
        return self.gains()+self.dividends()
        
    def difference_with_previous_month(self, totalmonth):
        """Calculates difference between totalmonth and the total with previous month"""
        if totalmonth.month==1:
            totalprevious=self.total_last_year
        else:
            previous=self.find(self.year, totalmonth.month-1)
            totalprevious=previous.total()
        return totalmonth.total()-totalprevious
        

    def difference_with_previous_year(self):
        """Calculates difference between totalmonth of december and the total last year"""
        return self.find(self.year, 12).total()-self.total_last_year
        
    def assets_percentage_in_month(self, month):
        """Calculates the percentage of the assets in this month from total last year"""
#        if self.total_last_year==Decimal(0):
#            return None
        m=self.find(self.year, month)
#        return 100*((m.total()-self.total_last_year)/self.total_last_year).amount
        return Percentage(m.total()-self.total_last_year, self.total_last_year)



class TotalGraphic:
    """Set of totalmonths to generate a graphic"""
    def __init__(self, mem, startyear, startmonth):
        self.mem=mem
        self.startyear=startyear
        self.startmonth=startmonth
        self.arr=[]
        self.generate()
        
    def generate(self):
        date=self.previousmonth_lastday()
        while datetime.date.today()>=date:
            self.arr.append(TotalMonth(self.mem, date.year, date.month))
            date=self.nextmonth_firstday(date)#Only gets year  and month, so  I can use first day
        
    def find(self, year, month):
        for m in self.arr:
            if m.year==year and m.month==month:
                return m
        return None
        
    def length(self):
        return len(self.arr)
        
    def previousmonth_lastday(self, date=None):
        """If date is None, it users start year and start month"""
        if date==None:
            date=datetime.date(self.startyear, self.startmonth, 1)
        return datetime.date(date.year, date.month, 1)-datetime.timedelta(days=1)
        
    def nextmonth_firstday(self, date=None):
        """If date is None, date is today"""
        if date==None:
            date=datetime.date.today()
            
        if date.month==12:
            month=1
            year=date.year+1
        else:
            month=date.month+1
            year=date.year
            
        return datetime.date(year, month, 1)

        
        


class wdgTotal(QWidget, Ui_wdgTotal):
    def __init__(self, mem,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem   

        fechainicio=Assets(self.mem).first_datetime_with_user_data()         

        self.setData=None#Será un TotalYear
        self.setGraphic=None #Será un TotalGraphic
        
        if fechainicio==None: #Base de datos vacía
            self.tab.setEnabled(False)
            return
        
        self.table.settings(self.mem, "wdgTotal")
        self.tblTargets.settings(self.mem, "wdgTotal")
        self.tblTargetsPlus.settings(self.mem, "wdgTotal")
        self.tblInvestOrWork.settings(self.mem,  "wdgTotal")
        self.tblMakeEndsMeet.settings(self.mem, "wdgTotal")
        
        self.annualtarget=None#AnnualTarget Object
        
        self.wyData.initiate(fechainicio.year, datetime.date.today().year, datetime.date.today().year)
        self.wyChart.initiate(fechainicio.year, datetime.date.today().year, datetime.date.today().year-3)
        self.wyChart.label.setText(self.tr("Data from selected year"))

        self.view=None#QChart view

        self.tab.setCurrentIndex(0)
        self.tabData.setCurrentIndex(0)
        self.tabPlus.setCurrentIndex(0)

        self.load_data()
        self.load_targets()
        self.load_targets_with_funds_revaluation()
        self.load_invest_or_work()
        self.load_make_ends_meet()
        self.wyData.changed.connect(self.on_wyData_mychanged)#Used my due to it took default on_wyData_changed
        self.wyChart.changed.connect(self.on_wyChart_mychanged)



    def load_data(self):
        self.table.clearContents()
        self.table.applySettings()
        inicio=datetime.datetime.now()     
        self.setData=TotalYear(self.mem, self.wyData.year)
        self.lblPreviousYear.setText(self.tr("Balance at {0}-12-31: {1}".format(self.setData.year-1, self.setData.total_last_year)))
        for i, m in enumerate(self.setData.arr):
            if m.year<datetime.date.today().year or (m.year==datetime.date.today().year and m.month<=datetime.date.today().month):
                self.table.setItem(0, i, m.incomes().qtablewidgetitem())
                self.table.setItem(1, i, m.gains().qtablewidgetitem())
                self.table.setItem(2, i, m.dividends().qtablewidgetitem())
                self.table.setItem(3, i, m.expenses().qtablewidgetitem())
                self.table.setItem(4, i, m.i_d_g_e().qtablewidgetitem())
                self.table.setItem(6, i, m.total_accounts().qtablewidgetitem())
                self.table.setItem(7, i, m.total_investments().qtablewidgetitem())
                self.table.setItem(8, i, m.total().qtablewidgetitem())
                self.table.setItem(9, i, self.setData.difference_with_previous_month(m).qtablewidgetitem())
                self.table.setItem(11, i, self.setData.assets_percentage_in_month(m.month).qtablewidgetitem())
        self.table.setItem(0, 12, self.setData.incomes().qtablewidgetitem())
        self.table.setItem(1, 12, self.setData.gains().qtablewidgetitem())
        self.table.setItem(2, 12, self.setData.dividends().qtablewidgetitem())
        self.table.setItem(3, 12, self.setData.expenses().qtablewidgetitem())
        self.table.setItem(4, 12, self.setData.i_d_g_e().qtablewidgetitem())      
        self.table.setItem(9, 12, self.setData.difference_with_previous_year().qtablewidgetitem())    
        self.table.setItem(11, 12, self.setData.assets_percentage_in_month(12).qtablewidgetitem())
        self.table.setCurrentCell(6, datetime.date.today().month-1)
        s=""
        s=self.tr("This year I've generated {}.").format(self.setData.gains()+self.setData.dividends())
        invested=Assets(self.mem).invested(datetime.date.today())
        current=Assets(self.mem).saldo_todas_inversiones(self.mem.data.investments, datetime.date.today())
        s=s+"\n"+self.tr("Difference between invested amount and current invesment balance: {} - {} = {}").format(invested,  current,  current-invested)
        self.lblInvested.setText(s)
        final=datetime.datetime.now()          
        logging.info("wdgTotal > load_data: {0}".format(final-inicio))

    def load_targets(self):
        self.annualtarget=AnnualTarget(self.mem).init__from_db(self.wyData.year) 
        self.lblTarget.setText(self.tr("Annual target percentage of total assests balance at {}-12-31 ( {} )".format(self.annualtarget.year-1, self.annualtarget.lastyear_assests)))
        self.spinTarget.setValue(float(self.annualtarget.percentage))
        self.tblTargets.clearContents()
        self.tblTargets.applySettings()
        inicio=datetime.datetime.now()     
        sumd_g=Money(self.mem, 0, self.mem.localcurrency)
        for i in range(1, 13): 
            m=self.setData.find(self.setData.year, i)
            sumd_g=sumd_g+m.d_g()
            self.tblTargets.setItem(0, i-1, self.mem.localcurrency.qtablewidgetitem(self.annualtarget.monthly_balance()))
            self.tblTargets.setItem(1, i-1, self.mem.localcurrency.qtablewidgetitem_with_target(m.d_g().amount, self.annualtarget.monthly_balance()))
            self.tblTargets.setItem(3, i-1, self.mem.localcurrency.qtablewidgetitem(self.annualtarget.monthly_balance()*i))
            self.tblTargets.setItem(4, i-1, self.mem.localcurrency.qtablewidgetitem_with_target(sumd_g.amount, self.annualtarget.monthly_balance()*i))
        self.tblTargets.setItem(0, 12, self.mem.localcurrency.qtablewidgetitem(self.annualtarget.annual_balance()))
        self.tblTargets.setItem(1, 12, self.mem.localcurrency.qtablewidgetitem_with_target(sumd_g.amount, self.annualtarget.annual_balance()))
        self.tblTargets.setCurrentCell(2, datetime.date.today().month-1)   
                
        s=""
        s=s+self.tr("This report shows if the user reaches the annual and monthly target.") +"\n\n"
        s=s+self.tr("Total gains are the result of adding dividends to gains")+"\n\n"
        s=s+self.tr("The cumulative target row shows compliance of the target in the year.")+"\n\n"
        s=s+self.tr("Green color shows that target has been reached.")
        self.lblTargets.setText(s)
        
        logging.info("wdgTargets > load_data_targets: {0}".format(datetime.datetime.now()  -inicio))
        
    def load_targets_with_funds_revaluation(self):
        self.tblTargetsPlus.clearContents()
        self.tblTargetsPlus.applySettings()
        inicio=datetime.datetime.now()     

        sumd_g=Money(self.mem, 0, self.mem.localcurrency)
        sumf=Money(self.mem, 0, self.mem.localcurrency)
        for i in range(1, 13): 
            m=self.setData.find(self.setData.year, i)
            sumd_g=sumd_g+m.d_g()
            sumf=sumf+m.funds_revaluation()
            self.tblTargetsPlus.setItem(0, i-1, self.mem.localcurrency.qtablewidgetitem(self.annualtarget.monthly_balance()))
            self.tblTargetsPlus.setItem(1, i-1,m.d_g().qtablewidgetitem())
            self.tblTargetsPlus.setItem(2, i-1, m.funds_revaluation().qtablewidgetitem())
            self.tblTargetsPlus.setItem(3, i-1, self.mem.localcurrency.qtablewidgetitem_with_target(m.d_g().amount+m.funds_revaluation().amount, self.annualtarget.monthly_balance()))
            
            self.tblTargetsPlus.setItem(5, i-1, self.mem.localcurrency.qtablewidgetitem(self.annualtarget.monthly_balance()*i))
            self.tblTargetsPlus.setItem(6, i-1, self.mem.localcurrency.qtablewidgetitem_with_target(sumd_g.amount+sumf.amount, self.annualtarget.monthly_balance()*i))
        self.tblTargetsPlus.setItem(0, 12, self.mem.localcurrency.qtablewidgetitem(self.annualtarget.annual_balance()))
        self.tblTargetsPlus.setItem(1, 12, sumd_g.qtablewidgetitem())
        self.tblTargetsPlus.setItem(2, 12, sumf.qtablewidgetitem())
        self.tblTargetsPlus.setItem(3, 12, self.mem.localcurrency.qtablewidgetitem_with_target(sumd_g.amount+sumf.amount,self.annualtarget.annual_balance()))
        self.tblTargetsPlus.setCurrentCell(2, datetime.date.today().month-1)   
                
        s=""
        s=s+self.tr("This report shows if the user reaches the annual and monthly target.") +"\n\n"
        s=s+self.tr("Total is the result of adding dividends to gain and funds revaluation")+"\n\n"
        s=s+self.tr("The cumulative target row shows compliance of the target in the year.")+"\n\n"
        s=s+self.tr("Green color shows that target has been reached.")
        self.lblTargetsPlus.setText(s)
        
        logging.info("wdgTargets > load_data_targets_with_funds_revaluation: {0}".format(datetime.datetime.now()  -inicio))

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
        inicio=datetime.datetime.now()    
        self.tblInvestOrWork.clearContents()
        self.tblInvestOrWork.applySettings()
        for i in range(1, 13): 
            m=self.setData.find(self.setData.year, i)
            self.tblInvestOrWork.setItem(0, i-1, m.d_g().qtablewidgetitem())
            self.tblInvestOrWork.setItem(1, i-1, m.expenses().qtablewidgetitem())
            self.tblInvestOrWork.setItem(3, i-1, (m.d_g()+m.expenses()).qtablewidgetitem())#Es mas porque es - y gastos -
            self.tblInvestOrWork.setItem(5, i-1, qresult(m.d_g()+m.expenses()))
        self.tblInvestOrWork.setItem(0, 12, self.setData.d_g().qtablewidgetitem())
        self.tblInvestOrWork.setItem(1, 12, self.setData.expenses().qtablewidgetitem())
        self.tblInvestOrWork.setItem(3, 12, (self.setData.d_g()+self.setData.expenses()).qtablewidgetitem())
        self.tblInvestOrWork.setItem(5, 12, qresult(self.setData.d_g()+self.setData.expenses()))
        self.tblInvestOrWork.setCurrentCell(2, datetime.date.today().month-1)   
        
        s=""
        s=s+self.tr("This report shows if the user could retire due to its investments") +"\n\n"
        s=s+self.tr("Total gains are the result of adding dividends to gains")+"\n\n"
        s=s+self.tr("Difference between total gains and expenses shows if user could cover his expenses with his total gains")+"\n\n"
        s=s+self.tr("Investment taxes are not evaluated in this report")
        self.lblInvestOrWork.setText(s)
        logging.info ("wdgTotal > load invest or work: {0}".format(datetime.datetime.now()  -inicio))

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
        inicio=datetime.datetime.now()    
        self.tblMakeEndsMeet.clearContents()
        self.tblMakeEndsMeet.applySettings()
        for i in range(1, 13): 
            m=self.setData.find(self.setData.year, i)
            self.tblMakeEndsMeet.setItem(0, i-1, m.incomes().qtablewidgetitem())
            self.tblMakeEndsMeet.setItem(1, i-1, m.expenses().qtablewidgetitem())
            self.tblMakeEndsMeet.setItem(3, i-1, (m.incomes()+m.expenses()).qtablewidgetitem())#Es mas porque es - y gastos -
            self.tblMakeEndsMeet.setItem(5, i-1, qresult(m.incomes()+m.expenses()))
        self.tblMakeEndsMeet.setItem(0, 12, self.setData.incomes().qtablewidgetitem())
        self.tblMakeEndsMeet.setItem(1, 12, self.setData.expenses().qtablewidgetitem())
        self.tblMakeEndsMeet.setItem(3, 12, (self.setData.incomes()+self.setData.expenses()).qtablewidgetitem())
        self.tblMakeEndsMeet.setItem(5, 12, qresult(self.setData.incomes()+self.setData.expenses()))
        self.tblMakeEndsMeet.setCurrentCell(2, datetime.date.today().month-1)   
        
        s=""
        s=s+self.tr("This report shows if the user makes ends meet") +"\n\n"
        s=s+self.tr("Difference between incomes and expenses shows if user could cover his expenses with his incomes")
        self.lblMakeEndsMeet.setText(s)
        logging.info("wdgTotal > load_make_ends_meet: {0}".format(datetime.datetime.now()  -inicio))


    def load_graphic(self, animations=True):               
        inicio=datetime.datetime.now()  
        
        self.setGraphic=TotalGraphic(self.mem, self.wyChart.year, 1)

        if self.view!=None:
            self.tabGraphTotal.removeWidget(self.view)
            self.view.close()
        self.view=VCTemporalSeries()
        
        if animations==False:
            self.view.chart.setAnimationOptions(QChart.NoAnimation)
                #Series creation
        last=self.setGraphic.find(datetime.date.today().year, datetime.date.today().month)
        lsNoLoses=self.view.appendTemporalSeries(self.tr("Total without losses assets")+": {}".format(last.total_no_losses()))
        lsMain=self.view.appendTemporalSeries(self.tr("Total assets")+": {}".format(last.total()))
        lsZero=self.view.appendTemporalSeries(self.tr("Zero risk assets")+": {}".format(last.total_zerorisk()))
        lsBonds=self.view.appendTemporalSeries(self.tr("Bond assets")+": {}".format(last.total_bonds()))
        lsRisk=self.view.appendTemporalSeries(self.tr("Risk assets")+": {}".format(last.total()-last.total_zerorisk()-last.total_bonds()))
                
        
        progress = QProgressDialog(self.tr("Filling report data"), self.tr("Cancel"), 0,self.setGraphic.length())
        progress.setModal(True)
        progress.setWindowTitle(self.tr("Calculating data..."))
        progress.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
        for m in self.setGraphic.arr:
            if progress.wasCanceled():
                break
            progress.setValue(progress.value()+1)
            epoch=day_end_from_date(m.last_day(), self.mem.localzone)
            total=m.total().amount
            zero=m.total_zerorisk().amount
            bonds=m.total_bonds().amount
            self.view.appendTemporalSeriesData(lsMain, epoch, m.total().amount)
            self.view.appendTemporalSeriesData(lsZero, epoch, m.total_zerorisk().amount)
            self.view.appendTemporalSeriesData(lsBonds, epoch, m.total_bonds().amount)
            self.view.appendTemporalSeriesData(lsRisk, epoch, total-zero-bonds)
            self.view.appendTemporalSeriesData(lsNoLoses, epoch, m.total_no_losses().amount)
        self.view.display()
        
        self.tabGraphTotal.addWidget(self.view)

            
        
        logging.info("wdgTotal > load_graphic: {0}".format(datetime.datetime.now()-inicio))



    def on_wyData_mychanged(self):
        self.load_data()    
        self.load_targets()
        self.load_targets_with_funds_revaluation()
        self.load_invest_or_work()
        self.load_make_ends_meet()

    def on_wyChart_mychanged(self):
        self.load_graphic()      
        
    def on_cmdTargets_released(self):
        self.annualtarget.percentage=self.spinTarget.value()
        self.annualtarget.save()
        self.mem.con.commit()
        self.load_targets()
        self.load_targets_with_funds_revaluation()

    def on_tab_currentChanged(self, index):
        if  index==1 and self.view==None: #If has not been plotted, plots it.
            self.on_wyChart_mychanged()
        
    @pyqtSlot() 
    def on_actionShowIncomes_triggered(self):
        
        newtab = QWidget()
        horizontalLayout = QHBoxLayout(newtab)
        table = myQTableWidget(newtab)
        table.settings(self.mem, "wdgTotal","tblShowIncomes")
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.verticalHeader().setVisible(False)
        
        id_tiposoperaciones=2
        set=AccountOperationManager(self.mem)
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
                                                        date_part('year',datetime)={1}""".format (id_tiposoperaciones, self.wyData.year, list2string(self.mem.conceptos.considered_dividends_in_totals())))
        else:#Month
            tabtitle=self.tr("Incomes of {0} of {1}").format(self.table.horizontalHeaderItem(self.month-1).text(), self.wyData.year)
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
                                                        date_part('month',datetime)={2}""".format (id_tiposoperaciones, self.wyData.year, self.month, list2string(self.mem.conceptos.considered_dividends_in_totals())))
        set.myqtablewidget(table,  True)
        horizontalLayout.addWidget(table)
        self.tab.addTab(newtab, tabtitle)
        self.tab.setCurrentWidget(newtab)            

       
    @pyqtSlot() 
    def on_actionShowExpenses_triggered(self):     
        newtab = QWidget()
        horizontalLayout = QHBoxLayout(newtab)
        table = myQTableWidget(newtab)
        table.settings(self.mem, "wdgTotal","tblShowExpenses")
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.verticalHeader().setVisible(False)
        
        id_tiposoperaciones=1
        set=AccountOperationManager(self.mem)
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
                                                            date_part('year',datetime)={1}""".format (id_tiposoperaciones, self.wyData.year))
        else:#Month
            tabtitle=self.tr("Expenses of {0} of {1}").format(self.table.horizontalHeaderItem(self.month-1).text(), self.wyData.year)
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
                                                            date_part('month',datetime)={2}""".format (id_tiposoperaciones, self.wyData.year, self.month))
        set.myqtablewidget(table,  True)
        horizontalLayout.addWidget(table)
        self.tab.addTab(newtab, tabtitle)
        self.tab.setCurrentWidget(newtab)

    @pyqtSlot() 
    def on_actionShowSellingOperations_triggered(self):
        def show_all():
            newtab = QWidget()
            horizontalLayout = QVBoxLayout(newtab)
            table = myQTableWidget(newtab)
            table.settings(self.mem, "wdgTotal","tblShowShellingOperations")
            table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            table.setSelectionMode(QAbstractItemView.SingleSelection)
            table.verticalHeader().setVisible(False)
            
            positive=Money(self.mem, 0, self.mem.localcurrency)
            negative=Money(self.mem, 0, self.mem.localcurrency)
            lbl=QLabel(newtab)
            
            set=InvestmentOperationHistoricalHeterogeneusManager(self.mem)
            for i in self.mem.data.investments.arr:
                for o in i.op_historica.arr:
                    if self.month==13:#Year
                        tabtitle=self.tr("Selling operations of {0}").format(self.wyData.year)
                        if o.fecha_venta.year==self.wyData.year and o.tipooperacion.id in (5, 8):#Venta y traspaso fondos inversion
                            set.arr.append(o)
                            if o.consolidado_bruto().isGETZero():
                                positive=positive+o.consolidado_bruto().local()
                            else:
                                negative=negative+o.consolidado_bruto().local()
                    else:#Month
                        tabtitle=self.tr("Selling operations of {0} of {1}").format(self.table.horizontalHeaderItem(self.month-1).text(), self.wyData.year)
                        if o.fecha_venta.year==self.wyData.year and o.fecha_venta.month==self.month and o.tipooperacion.id in (5, 8):#Venta y traspaso fondos inversion
                            set.arr.append(o)
                            if o.consolidado_bruto().isGETZero():
                                positive=positive+o.consolidado_bruto().local()
                            else:
                                negative=negative+o.consolidado_bruto().local()
            set.order_by_fechaventa()
            set.myqtablewidget(table)
            horizontalLayout.addWidget(table)
            lbl.setText(self.tr("Positive gross selling operations: {}. Negative gross selling operations: {}.").format(positive, negative))
            horizontalLayout.addWidget(lbl)
            self.tab.addTab(newtab, tabtitle)
            self.tab.setCurrentWidget(newtab)

        def show_more():
            newtab = QWidget()
            horizontalLayout = QVBoxLayout(newtab)
            table = myQTableWidget(newtab)
            table.setObjectName("tblShowShellingOperations")
            table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            table.setSelectionMode(QAbstractItemView.SingleSelection)
            table.verticalHeader().setVisible(False)
            
            positive=Decimal(0)
            negative=Decimal(0)
            lbl=QLabel(newtab)
            
            set=InvestmentOperationHistoricalHeterogeneusManager(self.mem)
            for i in self.mem.data.investments.arr:
                for o in i.op_historica.arr:
                    if self.month==13:#Year
                        tabtitle=self.tr("Selling operations of {0}  (Sold after a year)").format(self.wyData.year)
                        if o.fecha_venta.year==self.wyData.year and o.tipooperacion.id in (5, 8)  and o.less_than_a_year()==False:#Venta y traspaso fondos inversion
                            set.arr.append(o)
                            if o.consolidado_bruto()>=0:
                                positive=positive+o.consolidado_bruto()
                            else:
                                negative=negative+o.consolidado_bruto()
                    else:#Month
                        tabtitle=self.tr("Selling operations of {0} of {1} (Sold after a year)").format(self.table.horizontalHeaderItem(self.month-1).text(), self.wyData.year)
                        if o.fecha_venta.year==self.wyData.year and o.fecha_venta.month==self.month and o.tipooperacion.id in (5, 8)  and o.less_than_a_year()==False:#Venta y traspaso fondos inversion
                            set.arr.append(o)
                            if o.consolidado_bruto()>=0:
                                positive=positive+o.consolidado_bruto()
                            else:
                                negative=negative+o.consolidado_bruto()
            set.order_by_fechaventa()
            set.myqtablewidget(table, "wdgTotal")
            horizontalLayout.addWidget(table)
            lbl.setText(self.tr("Positive gross selling operations: {}. Negative gross selling operations: {}.").format(self.mem.localcurrency.string(positive), self.mem.localcurrency.string(negative)))
            horizontalLayout.addWidget(lbl)
            self.tab.addTab(newtab, tabtitle)
            self.tab.setCurrentWidget(newtab)
        def show_less():
            newtab = QWidget()
            horizontalLayout = QVBoxLayout(newtab)
            table = myQTableWidget(newtab)
            table.setObjectName("tblShowShellingOperations")
            table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            table.setSelectionMode(QAbstractItemView.SingleSelection)
            table.verticalHeader().setVisible(False)
            
            positive=Decimal(0)
            negative=Decimal(0)
            lbl=QLabel(newtab)
            
            set=InvestmentOperationHistoricalHeterogeneusManager(self.mem)
            for i in self.mem.data.investments.arr:
                for o in i.op_historica.arr:
                    if self.month==13:#Year
                        tabtitle=self.tr("Selling operations of {0} (Sold before a year)").format(self.wyData.year)
                        if o.fecha_venta.year==self.wyData.year and o.tipooperacion.id in (5, 8) and o.less_than_a_year()==True:#Venta y traspaso fondos inversion
                            set.arr.append(o)
                            if o.consolidado_bruto()>=0:
                                positive=positive+o.consolidado_bruto()
                            else:
                                negative=negative+o.consolidado_bruto()
                    else:#Month
                        tabtitle=self.tr("Selling operations of {0} of {1} (Sold before a year)").format(self.table.horizontalHeaderItem(self.month-1).text(), self.wyData.year)
                        if o.fecha_venta.year==self.wyData.year and o.fecha_venta.month==self.month and o.tipooperacion.id in (5, 8) and o.less_than_a_year()==True:#Venta y traspaso fondos inversion
                            set.arr.append(o)
                            if o.consolidado_bruto()>=0:
                                positive=positive+o.consolidado_bruto()
                            else:
                                negative=negative+o.consolidado_bruto()
            set.order_by_fechaventa()
            set.myqtablewidget(table, "wdgTotal")
            horizontalLayout.addWidget(table)
            lbl.setText(self.tr("Positive gross selling operations: {}. Negative gross selling operations: {}.").format(self.mem.localcurrency.string(positive), self.mem.localcurrency.string(negative)))
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
        table = myQTableWidget(newtab)
        table.settings(self.mem,"wdgTotal","tblShowDividends")
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.verticalHeader().setVisible(False)
        
        set=DividendHeterogeneusManager(self.mem)
        if self.month==13:#Year
            tabtitle=self.tr("Dividends of {0}").format(self.wyData.year)
            set.load_from_db("select * from dividends where id_conceptos not in (63) and date_part('year',fecha)={0}".format (self.wyData.year))
        else:#Month
            tabtitle=self.tr("Dividends of {0} of {1}").format(self.table.horizontalHeaderItem(self.month-1).text(), self.wyData.year)
            set.load_from_db("select * from dividends where id_conceptos not in (63) and date_part('year',fecha)={0} and date_part('month',fecha)={1}".format (self.wyData.year, self.month))
        set.order_by_datetime()
        set.myqtablewidget(table,  True)
        horizontalLayout.addWidget(table)
        self.tab.addTab(newtab, tabtitle)
        self.tab.setCurrentWidget(newtab)            


    @pyqtSlot() 
    def on_actionShowComissions_triggered(self):
        newtab = QWidget()
        vlayout = QVBoxLayout(newtab)
        table = myQTableWidget(newtab)
        table.settings(self.mem,"wdgTotal","tblShowComissions")
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        
        table.setColumnCount(13)
        table.setHorizontalHeaderItem(0, QTableWidgetItem(self.tr( "January" )))
        table.setHorizontalHeaderItem(1, QTableWidgetItem(self.tr( "February" )))
        table.setHorizontalHeaderItem(2, QTableWidgetItem(self.tr( "March" )))
        table.setHorizontalHeaderItem(3, QTableWidgetItem(self.tr( "April" )))
        table.setHorizontalHeaderItem(4, QTableWidgetItem(self.tr( "May" )))
        table.setHorizontalHeaderItem(5, QTableWidgetItem(self.tr( "June" )))
        table.setHorizontalHeaderItem(6, QTableWidgetItem(self.tr( "July" )))
        table.setHorizontalHeaderItem(7, QTableWidgetItem(self.tr( "August" )))
        table.setHorizontalHeaderItem(8, QTableWidgetItem(self.tr( "September" )))
        table.setHorizontalHeaderItem(9, QTableWidgetItem(self.tr( "October" )))
        table.setHorizontalHeaderItem(10, QTableWidgetItem(self.tr( "November" )))
        table.setHorizontalHeaderItem(11, QTableWidgetItem(self.tr( "December" )))
        table.setHorizontalHeaderItem(12, QTableWidgetItem(self.tr( "Total" )))
        
        table.setRowCount(4)
        table.setVerticalHeaderItem(0, QTableWidgetItem(self.tr( "Bank comissions" )))
        table.setVerticalHeaderItem(1, QTableWidgetItem(self.tr( "Custody fees" )))
        table.setVerticalHeaderItem(2, QTableWidgetItem(self.tr( "Invesment operation comissions" )))
        table.setVerticalHeaderItem(3, QTableWidgetItem(self.tr( "Total" )))
        table.applySettings()
        (sum_bank_comissions, sum_custody_fees, sum_investment_comissions)=(Decimal("0"), Decimal("0"), Decimal("0"))

        for column in range (12):
            bank_comissions=none2decimal0(self.mem.con.cursor_one_row("""select sum(importe) 
                                                                                                            from opercuentas 
                                                                                                            where id_conceptos=%s and 
                                                                                                                date_part('year',datetime)=%s and 
                                                                                                                date_part('month',datetime)=%s;""", (38, self.wyData.year, column+1))[0])
            table.setItem(0, column, self.mem.localcurrency.qtablewidgetitem(bank_comissions))    
            sum_bank_comissions=sum_bank_comissions+bank_comissions
            
            custody_fees=none2decimal0(self.mem.con.cursor_one_row("""select sum(importe) 
                                                                                                            from opercuentas 
                                                                                                            where id_conceptos=%s and 
                                                                                                                date_part('year',datetime)=%s and 
                                                                                                                date_part('month',datetime)=%s;""", (59, self.wyData.year, column+1))[0])
            table.setItem(1, column, self.mem.localcurrency.qtablewidgetitem(custody_fees))    
            sum_custody_fees=sum_custody_fees+custody_fees
            
            investment_comissions=-none2decimal0(self.mem.con.cursor_one_row("""select sum(comision) 
                                                                                                            from operinversiones  
                                                                                                            where date_part('year',datetime)=%s and 
                                                                                                                date_part('month',datetime)=%s;""", (self.wyData.year, column+1))[0])
            table.setItem(2, column, self.mem.localcurrency.qtablewidgetitem(investment_comissions))    
            sum_investment_comissions=sum_investment_comissions+investment_comissions
            
            table.setItem(3, column, self.mem.localcurrency.qtablewidgetitem(bank_comissions+custody_fees+investment_comissions))    
        table.setItem(0, 12, self.mem.localcurrency.qtablewidgetitem(sum_bank_comissions))    
        table.setItem(1, 12, self.mem.localcurrency.qtablewidgetitem(sum_custody_fees))    
        table.setItem(2, 12, self.mem.localcurrency.qtablewidgetitem(sum_investment_comissions))    
        table.setItem(3, 12, self.mem.localcurrency.qtablewidgetitem(sum_bank_comissions+sum_custody_fees+sum_investment_comissions))    
        vlayout.addWidget(table)

        #Number of operations
        num_operations=0
        settypes=self.mem.types.with_operation_comissions_types()
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
            cs=self.mem.localcurrency.string
            label.setText(self.tr("Number of purchase and sale investment operations: {}. Comissions average: {}".format(int(num_operations), cs(sum_investment_comissions/num_operations))))
            vlayout.addWidget(label)
            
        self.tab.addTab(newtab, self.tr("Commision report of {}").format(self.wyData.year))
        self.tab.setCurrentWidget(newtab)        
        

    @pyqtSlot() 
    def on_actionGainsByProductType_triggered(self):
        newtab = QWidget()
        vlayout = QVBoxLayout(newtab)
        table = myQTableWidget(newtab)
        table.settings(self.mem,"wdgTotal","tblGainsByProductType")
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        
        table.setColumnCount(3)
        
        table.setHorizontalHeaderItem(0, QTableWidgetItem(self.tr( "Product type" )))
        table.setHorizontalHeaderItem(1, QTableWidgetItem(self.tr( "Brut gains" )))
        table.setHorizontalHeaderItem(2, QTableWidgetItem(self.tr("Brut dividends")))
        table.applySettings()
        sum_gains=Money(self.mem)
        sum_dividens=Money(self.mem)
        
        settypes=self.mem.types.investment_types()
        table.setRowCount(settypes.length()+1)
        
        for i, type in enumerate(settypes.arr):
            table.setItem(i, 0, qleft(type.name))    
            gains=Money(self.mem,  0,  self.mem.localcurrency)
            dividends=Money(self.mem,  0,  self.mem.localcurrency)
            for inv in self.mem.data.investments.arr:
                if inv.product.type.id==type.id:
                    #gains
                    for o in inv.op_historica.arr:
                        if o.fecha_venta.year==self.wyData.year and o.tipooperacion.id in (5, 8):
                            gains=gains+o.consolidado_bruto().local()
                    #dividends
                    setdiv=DividendHeterogeneusManager(self.mem)
                    setdiv.load_from_db(self.mem.con.mogrify("select * from dividends where id_inversiones=%s and fecha>=%s and fecha<=%s order by fecha", (inv.id, datetime.datetime(self.wyData.year, 1, 1, 0, 0, 0), datetime.datetime(self.wyData.year+1, 12, 31, 23, 59, 59))))
                    dividends=dividends+setdiv.gross().local()
            table.setItem(i, 1, gains.qtablewidgetitem())
            table.setItem(i, 2, dividends.qtablewidgetitem())
            sum_gains=sum_gains+gains
            sum_dividens=sum_dividens+dividends
            
        table.setItem(i+1, 0, qleft(self.tr("Total")))
        table.setItem(i+1, 1, sum_gains.qtablewidgetitem())
        table.setItem(i+1, 2, sum_dividens.qtablewidgetitem())
        
        label=QLabel(newtab)
        font = QFont()
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)
        label.setFont(font)
        label.setAlignment(Qt.AlignCenter)
        label.setText(self.tr("Gains + Dividends: {} + {} = {}".format(sum_gains, sum_dividens, sum_gains+sum_dividens)))
            
        vlayout.addWidget(table)
        vlayout.addWidget(label)
        self.tab.addTab(newtab, self.tr("Gains by product type of {}").format(self.wyData.year))
        self.tab.setCurrentWidget(newtab)        
            
    @pyqtSlot() 
    def on_actionShowTaxes_triggered(self):
        newtab = QWidget()
        horizontalLayout = QVBoxLayout(newtab)
        table = myQTableWidget(newtab)
        table.settings(self.mem,"wdgTotal","tblShowPaidTaxes")
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        
        table.setColumnCount(13)
        table.setHorizontalHeaderItem(0, QTableWidgetItem(self.tr( "January" )))
        table.setHorizontalHeaderItem(1, QTableWidgetItem(self.tr( "February" )))
        table.setHorizontalHeaderItem(2, QTableWidgetItem(self.tr( "March" )))
        table.setHorizontalHeaderItem(3, QTableWidgetItem(self.tr( "April" )))
        table.setHorizontalHeaderItem(4, QTableWidgetItem(self.tr( "May" )))
        table.setHorizontalHeaderItem(5, QTableWidgetItem(self.tr( "June" )))
        table.setHorizontalHeaderItem(6, QTableWidgetItem(self.tr( "July" )))
        table.setHorizontalHeaderItem(7, QTableWidgetItem(self.tr( "August" )))
        table.setHorizontalHeaderItem(8, QTableWidgetItem(self.tr( "September" )))
        table.setHorizontalHeaderItem(9, QTableWidgetItem(self.tr( "October" )))
        table.setHorizontalHeaderItem(10, QTableWidgetItem(self.tr( "November" )))
        table.setHorizontalHeaderItem(11, QTableWidgetItem(self.tr( "December" )))
        table.setHorizontalHeaderItem(12, QTableWidgetItem(self.tr( "Total" )))
        
        table.setRowCount(5)
        table.setVerticalHeaderItem(0, QTableWidgetItem(self.tr( "Investment operation retentions" )))
        table.setVerticalHeaderItem(1, QTableWidgetItem(self.tr( "Dividend retentions" )))
        table.setVerticalHeaderItem(2, QTableWidgetItem(self.tr( "Other paid taxes" )))
        table.setVerticalHeaderItem(3, QTableWidgetItem(self.tr( "Returned taxes" )))
        table.setVerticalHeaderItem(4,  QTableWidgetItem(self.tr( "Total" )))

        table.applySettings()
        (sum_io_retentions, sum_div_retentions, sum_other_taxes,  sum_returned_taxes)=(Decimal("0"), Decimal("0"), Decimal("0"), Decimal("0"))

        for column in range (12):
            io_retentions=-none2decimal0(self.mem.con.cursor_one_row("""select sum(impuestos) 
                                                                                                                                from operinversiones  
                                                                                                                                where date_part('year',datetime)=%s and 
                                                                                                                                    date_part('month',datetime)=%s;""", (self.wyData.year, column+1))[0])
            table.setItem(0, column, self.mem.localcurrency.qtablewidgetitem(io_retentions))    
            sum_io_retentions=sum_io_retentions+io_retentions
            
            div_retentions=-none2decimal0(self.mem.con.cursor_one_row("""select sum(retencion) 
                                                                                                            from dividends 
                                                                                                            where date_part('year',fecha)=%s and 
                                                                                                                date_part('month',fecha)=%s;""", (self.wyData.year, column+1))[0])
            table.setItem(1, column, self.mem.localcurrency.qtablewidgetitem(div_retentions))    
            sum_div_retentions=sum_div_retentions+div_retentions
            
            other_taxes=none2decimal0(self.mem.con.cursor_one_row("""select sum(importe) 
                                                                                                            from opercuentas 
                                                                                                            where id_conceptos=%s and 
                                                                                                                date_part('year',datetime)=%s and 
                                                                                                                date_part('month',datetime)=%s;""", (37, self.wyData.year, column+1))[0])
            table.setItem(2, column, self.mem.localcurrency.qtablewidgetitem(other_taxes))    
            sum_other_taxes=sum_other_taxes+other_taxes         
            
            returned_taxes=none2decimal0(self.mem.con.cursor_one_row("""select sum(importe) 
                                                                                                            from opercuentas 
                                                                                                            where id_conceptos=%s and 
                                                                                                                date_part('year',datetime)=%s and 
                                                                                                                date_part('month',datetime)=%s;""", (6, self.wyData.year, column+1))[0])
            table.setItem(3, column, self.mem.localcurrency.qtablewidgetitem(returned_taxes))    
            sum_returned_taxes=sum_returned_taxes+returned_taxes
            
            table.setItem(4, column, self.mem.localcurrency.qtablewidgetitem(io_retentions+div_retentions+other_taxes+returned_taxes))    
        
        table.setItem(0, 12, self.mem.localcurrency.qtablewidgetitem(sum_io_retentions))    
        table.setItem(1, 12, self.mem.localcurrency.qtablewidgetitem(sum_div_retentions))    
        table.setItem(2, 12, self.mem.localcurrency.qtablewidgetitem(sum_other_taxes))    
        table.setItem(3, 12, self.mem.localcurrency.qtablewidgetitem(sum_returned_taxes))    
        table.setItem(4, 12, self.mem.localcurrency.qtablewidgetitem(sum_io_retentions+sum_div_retentions+sum_other_taxes+sum_returned_taxes))    

        horizontalLayout.addWidget(table)
        self.tab.addTab(newtab, self.tr("Taxes report of {}").format(self.wyData.year))
        self.tab.setCurrentWidget(newtab)        
            

    def on_tab_tabCloseRequested(self, index):
        """Only removes dinamic tabs"""
        if index in (0, 1):
            qmessagebox(self.tr("You can't close this tab"))
        else:
            self.tab.setCurrentIndex(0)
            self.tab.removeTab(index)
            
    def on_table_cellDoubleClicked(self, row, column):
        if row==0:#incomes
            self.on_actionShowIncomes_triggered()
        elif row==1:#Gains
            self.on_actionShowSellingOperations_triggered()
        elif row==2:#Dividends
            self.on_actionShowDividends_triggered()
        elif row==3: #Expenses
            self.on_actionShowExpenses_triggered()
        else:
            qmessagebox(self.tr("You only can double click in incomes, gains, dividends and expenses.") + "\n\n" + self.tr("Make right click to see comission and tax reports"))
        
    def on_table_customContextMenuRequested(self,  pos):
        menu=QMenu()
        menu.addAction(self.actionShowComissions)
        menu.addSeparator()
        menu.addAction(self.actionShowTaxes)
        menu.addSeparator()
        menu.addAction(self.actionGainsByProductType)
        menu.exec_(self.table.mapToGlobal(pos))

    def on_table_itemSelectionChanged(self):
        self.month=None
        for i in self.table.selectedItems():#itera por cada item no row.
            self.month=i.column()+1
        print ("Selected month: {0}.".format(self.month))
