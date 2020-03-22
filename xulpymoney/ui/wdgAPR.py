from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import  QWidget, QProgressDialog
from datetime import datetime, date
from decimal import Decimal
from logging import debug
from xulpymoney.datetime_functions import date_last_of_the_year
from xulpymoney.objects.assets import Assets
from xulpymoney.objects.money import Money
from xulpymoney.objects.percentage import Percentage, percentage_between
from xulpymoney.casts import none2decimal0
from xulpymoney.ui.Ui_wdgAPR import Ui_wdgAPR
from xulpymoney.ui.myqtablewidget import qright
from xulpymoney.libxulpymoneytypes import eConcept

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
        self.mqtw.settings(self.mem.settings, "wdgAPR", "mqtw")
        self.mqtwReport.settings(self.mem.settings, "wdgAPR", "mqtwReport")
         
        
        dtFirst=Assets(self.mem).first_datetime_allowed_estimated()
        dtLast=Assets(self.mem).last_datetime_allowed_estimated()
        currentyear=int(self.mem.settingsdb.value("wdgAPR/cmbYear", dtFirst.year))
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
        anoinicio=self.wdgYear.year
        anofinal=date.today().year
        
        self.mqtw.applySettings()
        self.mqtw.table.setRowCount(anofinal-anoinicio+1+1)
        lastsaldo=Money(self.mem)
        sumdividends=Money(self.mem)
        sumgains=Money(self.mem)
        sumexpenses=Money(self.mem)
        sumincomes=Money(self.mem)
        sumicdg=Money(self.mem)
        
        hh=[self.tr("Year"), self.tr("Initial balance"), self.tr("Final balance"), self.tr("Difference"), self.tr("Incomes"), self.tr("Net gains"), self.tr("Net dividends"), self.tr("Expenses"), self.tr("I+G+D-E")]
        data=[]
        for i in range(anoinicio, anofinal+1):
            if self.progress.wasCanceled():
                break;
            else:
                self.progress.setValue(self.progress.value()+1)
            si=lastsaldo
            sf=Assets(self.mem).saldo_total(self.mem.data.investments,  date(i, 12, 31))
            expenses=Assets(self.mem).saldo_anual_por_tipo_operacion( i,1)#+Assets(self.mem).saldo_anual_por_tipo_operacion (cur,i, 7)#expenses + Facturación de tarjeta
            dividends=Assets(self.mem).dividends_neto( i)
            incomes=Assets(self.mem).saldo_anual_por_tipo_operacion(  i,2)-dividends #Se quitan los dividends que luego se suman
            gains=Assets(self.mem).consolidado_neto(self.mem.data.investments,  i)
            
            self.dates.append(datetime(i, 12, 31))
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
            self.mqtw.table.setItem(i-anoinicio, 9, Percentage(sf -si, si).qtablewidgetitem())
            lastsaldo=sf
        data.append([self.tr("Total"), "#crossedout","#crossedout","#crossedout",sumincomes,sumgains,sumdividends,sumexpenses,sumicdg])
        self.mqtw.setData(hh, None, data)
        debug("wdgAPR > load_data: {}".format(datetime.now()-inicio))

    def load_report(self):
        inicio=datetime.now()       
        anoinicio=self.wdgYear.year
        anofinal=date.today().year
        sumgd=Money(self.mem, 0, self.mem.localcurrency)
        sumtaxes=Decimal(0)
        sumcommissions=Decimal(0)
        self.mqtwReport.applySettings()
        self.mqtwReport.table.setRowCount(anofinal-anoinicio+1+1)
        hh=[self.tr("Year"), self.tr("Invested balance"), self.tr("Investment valoration"), self.tr("Difference"), self.tr("%"), "", self.tr("Net gains + Dividends"), "", self.tr("Taxes"), self.tr("Commissions")]
        data=[]
        for i in range(anoinicio, anofinal+1):
            if self.progress.wasCanceled():
                break;
            else:
                self.progress.setValue(self.progress.value()+1)                     
            sinvested=Assets(self.mem).invested(date_last_of_the_year(i))
            sbalance=Assets(self.mem).saldo_todas_inversiones(date_last_of_the_year(i))
            gd=Assets(self.mem).consolidado_neto(self.mem.data.investments,  i)+Assets(self.mem).dividends_neto(i)
            sumgd=sumgd+gd
            taxes=none2decimal0(self.mem.con.cursor_one_field("select sum(importe) from opercuentas where id_conceptos in (%s, %s) and date_part('year',datetime)=%s", (int(eConcept.TaxesReturn), int(eConcept.TaxesPayment), i)))
            commissions=none2decimal0(self.mem.con.cursor_one_field("""
select 
    sum(suma) 
from (
            select 
                sum(importe) as suma 
            from 
                opercuentas 
            where 
                id_conceptos in (%s, %s) and  
                date_part('year',datetime)=%s
            union 
            select 
                -sum(comision) as suma 
            from 
                operinversiones 
            where  
                date_part('year',datetime)=%s
        ) as uni""", (int(eConcept.BankCommissions), int(eConcept.CommissionCustody), i,i)))
            self.mqtwReport.table.setItem(i-anoinicio, 9, qright(commissions))
            
            data.append([
                i, 
                sinvested, 
                sbalance, 
                sbalance-sinvested, 
                percentage_between(sinvested, sbalance), 
                "#crossedout", 
                gd, 
                "#crossedout", 
                taxes, 
                commissions
            ])
            sumtaxes=sumtaxes+taxes
            sumcommissions=sumcommissions+commissions
        data.append([self.tr("Total"), "#crossedout", "#crossedout", "#crossedout", "#crossedout", "#crossedout", sumgd, "#crossedout", sumtaxes, sumcommissions])
        self.mqtwReport.setData(hh, None, data)

        diff=Assets(self.mem).saldo_todas_inversiones(date_last_of_the_year(anofinal))-Assets(self.mem).invested(date_last_of_the_year(anofinal))
        s=""
        s=self.tr("From {} I have generated {}.").format(self.wdgYear.year, sumgd)
        s=s+"\n"+self.tr("Difference between invested amount and current invesment balance is {}").format(diff)
        if (diff+sumgd).isGETZero():
            s=s+"\n"+self.tr("So I'm wining {} which is {} per year.").format(sumgd+diff, self.mem.localmoney((sumgd+diff).amount/(anofinal-self.wdgYear.year+1)))
        else:
            s=s+"\n"+self.tr("So I'm losing {} which is {} per year.").format(sumgd+diff, self.mem.localmoney((sumgd+diff).amount/(anofinal-self.wdgYear.year+1)))        
        self.lblReport.setText(s)

        debug("wdgAPR > load_report: {0}".format(datetime.now()-inicio))
