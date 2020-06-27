from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import  QWidget, QProgressDialog
from datetime import datetime, date
from logging import debug
from xulpymoney.datetime_functions import date_last_of_the_year, dtaware_year_end, dtaware_year_start
from xulpymoney.objects.assets import Assets
from xulpymoney.objects.money import Money
from xulpymoney.objects.percentage import  percentage_between
from xulpymoney.ui.Ui_wdgAPR import Ui_wdgAPR

class wdgAPR(QWidget, Ui_wdgAPR):
    def __init__(self, mem,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.tab.setCurrentIndex(0)
        self.mem=mem
        self.progress = QProgressDialog(self.tr("Filling data of the report"), self.tr("Cancel"), 0,0)
        self.progress.setModal(True)
        self.progress.setWindowTitle(self.tr("Calculating data..."))
        self.progress.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
        self.progress.setMinimumDuration(0)        
        self.mqtw.setSettings(self.mem.settings, "wdgAPR", "mqtw")
        self.mqtwReport.setSettings(self.mem.settings, "wdgAPR", "mqtwReport")
         
        
        dtFirst=Assets(self.mem).first_datetime_allowed_estimated()
        dtLast=Assets(self.mem).last_datetime_allowed_estimated()
        currentyear=self.mem.settingsdb.value_integer("wdgAPR/cmbYear", dtFirst.year)
        self.wdgYear.initiate(dtFirst.year,  dtLast.year, currentyear)#Push an wdgYear changed
        self.wdgYear.changed.connect(self.on_my_wdgYear_changed)
        self.on_my_wdgYear_changed()
        

    def on_my_wdgYear_changed(self):
        self.mem.settingsdb.setValue("wdgAPR/cmbYear", self.wdgYear.year )
        self.progress.reset()
        self.progress.setMinimum(0)
        self.progress.setMaximum((date.today().year-self.wdgYear.year+1)*2)
        self.progress.forceShow()
        self.progress.setValue(0)
        
        self.dt_report_start=dtaware_year_start(self.wdgYear.year, self.mem.localzone_name)
        self.dt_report_end=dtaware_year_end(date.today().year, self.mem.localzone_name)
        
        self.mqtw.clear()
        self.mqtwReport.clear()
        self.dates=[]
        self.incomes=[]
        self.expenses=[]
        self.gains=[]
        self.dividends=[]

        self.load_data()
        self.load_report()


    def load_data(self):        
        inicio=datetime.now()
        self.mqtw.applySettings()
        self.mqtw.table.setRowCount(date.today().year-self.wdgYear.year+1+1)
        lastsaldo=Money(self.mem)
        sumdividends=Money(self.mem)
        sumgains=Money(self.mem)
        sumexpenses=Money(self.mem)
        sumincomes=Money(self.mem)
        sumicdg=Money(self.mem)
        
        hh=[self.tr("Year"), self.tr("Initial balance"), self.tr("Final balance"), self.tr("Difference"), self.tr("Incomes"), self.tr("Net gains"), self.tr("Net dividends"), self.tr("Expenses"), self.tr("I+G+D-E")]
        data=[]
        for i in range(self.dt_report_start.year, self.dt_report_end.year+1):
            #dt_start=dtaware_year_start(i, self.mem.localzone_name)
            dt_end=dtaware_year_end(i, self.mem.localzone_name)
            if self.progress.wasCanceled():
                break;
            else:
                self.progress.setValue(self.progress.value()+1)
            si=lastsaldo
            sf=Assets(self.mem).saldo_total(self.mem.data.investments, dt_end.date())
            expenses=Assets(self.mem).saldo_anual_por_tipo_operacion( i,1)#+Assets(self.mem).saldo_anual_por_tipo_operacion (cur,i, 7)#expenses + Facturación de tarjeta
            dividends=Assets(self.mem).dividends_neto( i)
            incomes=Assets(self.mem).saldo_anual_por_tipo_operacion(  i,2)-dividends #Se quitan los dividends que luego se suman
            gains=Assets(self.mem).consolidado_neto(self.mem.data.investments,  i)
            
            self.dates.append(dt_end.date())
            self.expenses.append(-expenses.amount)
            self.dividends.append(dividends.amount)
            self.incomes.append(incomes.amount)
            self.gains.append(gains.amount)

            gi=incomes+dividends+gains+expenses     
            data.append([
                i, 
                si, 
                sf, 
                (sf-si), 
                incomes, 
                gains, 
                dividends,
                expenses, 
                gi, 
            ])
            sumdividends=sumdividends+dividends
            sumgains=sumgains+gains
            sumexpenses=sumexpenses+expenses
            sumincomes=sumincomes+incomes
            sumicdg=sumicdg+gi
            lastsaldo=sf
        data.append([self.tr("Total"), "#crossedout","#crossedout","#crossedout",sumincomes,sumgains,sumdividends,sumexpenses,sumicdg])
        self.mqtw.setData(hh, None, data)
        debug("wdgAPR > load_data: {}".format(datetime.now()-inicio))

    def load_report(self):
        inicio=datetime.now()
        sumgd=Money(self.mem, 0, self.mem.localcurrency)
        self.mqtwReport.applySettings()
        self.mqtwReport.table.setRowCount(date.today().year-self.wdgYear.year+1+1)
        hh=[self.tr("Year"), self.tr("Invested balance"), self.tr("Investment valoration"), self.tr("Difference"), 
            self.tr("%"), "", self.tr("Net gains + Dividends"), self.tr("Custody commissions"),  
            self.tr("Taxes"), "", self.tr("Investments Commissions")]
        data=[]
        for i in range(self.wdgYear.year, date.today().year+1):
            if self.progress.wasCanceled():
                break;
            else:
                self.progress.setValue(self.progress.value()+1)          
            dt_start=dtaware_year_start(i, self.mem.localzone_name)
            dt_end=dtaware_year_end(i, self.mem.localzone_name)           
            sinvested=Assets(self.mem).invested(date_last_of_the_year(i))
            sbalance=Assets(self.mem).saldo_todas_inversiones(date_last_of_the_year(i))+Assets(self.mem).saldo_todas_inversiones_with_daily_adjustment(date_last_of_the_year(i))
            gd=Assets(self.mem).consolidado_neto(self.mem.data.investments,  i)+Assets(self.mem).dividends_neto(i)
            sumgd=sumgd+gd
            
            data.append([
                i, 
                sinvested, 
                sbalance, 
                sbalance-sinvested, 
                percentage_between(sinvested, sbalance), 
                "#crossedout", 
                gd, 
                Assets(self.mem).custody_commissions(dt_start, dt_end),
                Assets(self.mem).taxes(dt_start, dt_end), 
                "#crossedout", 
                Assets(self.mem).investments_commissions(dt_start, dt_end)
            ])
            
        report_custody_commissions=Assets(self.mem).custody_commissions(self.dt_report_start, self.dt_report_end)
        report_taxes=Assets(self.mem).taxes(self.dt_report_start, self.dt_report_end)
        data.append([
            self.tr("Total"), 
            "#crossedout", 
            "#crossedout", 
            "#crossedout", 
            "#crossedout", 
            "#crossedout", 
            sumgd, 
            report_custody_commissions,
            report_taxes, 
            "#crossedout", 
            Assets(self.mem).investments_commissions(self.dt_report_start, self.dt_report_end)
            ])
        self.mqtwReport.setData(hh, None, data)

        diff=Assets(self.mem).saldo_todas_inversiones(date_last_of_the_year(date.today().year)) + Assets(self.mem).saldo_todas_inversiones_with_daily_adjustment(date_last_of_the_year(date.today().year)) - Assets(self.mem).invested(date_last_of_the_year(date.today().year))
        s=""
        s=s+"\n"+self.tr("Difference between invested amount and current invesment balance is {}.").format(diff)
        s=s+"\n"+self.tr("From {} I've generated {} gains (investment commisions are included).").format(self.wdgYear.year, sumgd)
        s=s+"\n"+self.tr("Sum of taxes and custody commissions is {}.".format(report_taxes+report_custody_commissions))
        s=s+"\n"+self.tr("So, I've generated {} gains.").format(sumgd+report_taxes+report_custody_commissions)
        balance=diff+sumgd+report_taxes+report_custody_commissions
        if balance.isGETZero():
            s=s+"\n"+self.tr("So I'm wining {} which is {} per year.").format(balance, self.mem.localmoney(balance.amount/(date.today().year-self.wdgYear.year+1)))
        else:
            s=s+"\n"+self.tr("So I'm losing {} which is {} per year.").format(balance, self.mem.localmoney(balance.amount/(date.today().year-self.wdgYear.year+1)))        

        self.lblReport.setText(s)

        debug("wdgAPR > load_report: {0}".format(datetime.now()-inicio))
