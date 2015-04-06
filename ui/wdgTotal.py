from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from libxulpymoney import *

from matplotlib.finance import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT 
from matplotlib.dates import *
from matplotlib.figure import Figure

from Ui_wdgTotal import *
import datetime

# Matplotlib Figure object
class canvasTotal(FigureCanvasQTAgg):
    def __init__(self, mem, parent):
        self.mem=mem
        self.fig = Figure()
        FigureCanvasQTAgg.__init__(self, self.fig)
        FigureCanvasQTAgg.setSizePolicy(self,QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvasQTAgg.updateGeometry(self)
        self.ax = self.fig.add_subplot(111)
        self.labels=[]
        self.plot_main=None
        self.plot_zero=None
        self.plot_bonds=None
        self.plotted=False#Shown if the graphics has been plotted anytime.
        
    
    def price(self, x): 
        return self.mem.localcurrency.string(x)
        
    def mydraw(self, mem, dates,  total, zero,  bonds):
        self.plotted=True
        self.ax.clear()
        
        self.ax.xaxis.set_major_locator(YearLocator())    
        self.ax.xaxis.set_minor_locator(MonthLocator())
        self.ax.xaxis.set_major_formatter( DateFormatter('%Y'))        
        self.ax.xaxis.set_minor_formatter( DateFormatter(''))                   
        self.ax.autoscale_view()
        
        # format the coords message box
        self.ax.fmt_xdata = DateFormatter('%Y-%m')
        self.ax.fmt_ydata = self.price
        self.ax.grid(True)
#        self.fig.autofmt_xdate()
        self.plot_main, =self.ax.plot_date(dates, total, '-')
        self.plot_zero, =self.ax.plot_date(dates, zero, '-')
        self.plot_bonds, =self.ax.plot_date(dates, bonds, '-')
        self.showLegend()
        self.draw()        
        
    def showLegend(self):
        """Alterna mostrando y desmostrando legend, empieza con sí"""
        self.makeLegend()
                
        if self.ax.legend_==None:
            (plots, labels)=zip(*self.labels)
            self.ax.legend(plots, labels, loc="best")
        else:
            self.ax.legend_=None

    def mouseReleaseEvent(self,  event):
        self.showLegend()
        self.draw()
    
    def makeLegend(self):
        if len(self.labels)==0:
            self.labels.append((self.plot_main, self.tr("Total assets")))
            self.labels.append((self.plot_zero,self.tr("Zero risk assets")))
            self.labels.append((self.plot_bonds,self.tr("Bond assets")))


class TotalMonth:
    """All values are calculated in last day of the month"""
    def __init__(self, mem, year, month):
        self.mem=mem
        self.year=year
        self.month=month
        self.expenses_value=None
        self.dividends_value=None
        self.incomes_value=None
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
            self.dividends_value=Investment(self.mem).dividends_neto(  self.year, self.month)
        return self.dividends_value
        
    def incomes(self):
        if self.incomes_value==None:
            self.incomes_value=Assets(self.mem).saldo_por_tipo_operacion(  self.year,self.month,2)-self.dividends()
        return self.incomes_value
        
    def gains(self):
        if self.gains_value==None:
            self.gains_value=Assets(self.mem).consolidado_neto(self.mem.data.investments_all(), self.year, self.month)
        return self.gains_value
        
    def name(self):
        return "{}-{}".format(year, month)
        
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
            self.total_investments_value=Assets(self.mem).saldo_todas_inversiones(self.mem.data.investments_all(),  self.last_day())
        return self.total_investments_value
        
    def total_zerorisk(self): 
        if self.total_zerorisk_value==None:
            self.total_zerorisk_value=Assets(self.mem).patrimonio_riesgo_cero(self.mem.data.investments_all(), self.last_day())
        return self.total_zerorisk_value
        
    def total_bonds(self):
        if self.total_bonds_value==None:
            self.total_bonds_value=Assets(self.mem).saldo_todas_inversiones_bonds(self.last_day())
        return self.total_bonds_value
        
class TotalYear:
    """Set of 12 totalmonths in the same year"""
    def __init__(self, mem, year):
        self.mem=mem
        self.year=year
        self.arr=[]
        self.total_last_year=Assets(self.mem).saldo_total(self.mem.data.investments_all(),  datetime.date(self.year-1, 12, 31))
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
        result=Decimal(0)
        for m in self.arr:
            result=result+m.expenses()
        return result
        
    def i_d_g_e(self):
        return self.incomes()+self.dividends()+self.gains()+self.expenses()
        
    def incomes(self):
        result=Decimal(0)
        for m in self.arr:
            result=result+m.incomes()
        return result

    def gains(self):
        result=Decimal(0)
        for m in self.arr:
            result=result+m.gains()
        return result        

    def dividends(self):
        result=Decimal(0)
        for m in self.arr:
            result=result+m.dividends()
        return result
        
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
        if self.total_last_year==Decimal(0):
            return None
        m=self.find(self.year, month)
        return 100*(m.total()-self.total_last_year)/self.total_last_year    



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
        self.progress = QProgressDialog(self.tr("Filling report data"), self.tr("Cancel"), 0,0)
        self.progress.setModal(True)
        self.progress.setWindowTitle(self.tr("Calculating data..."))
        self.progress.setMinimumDuration(0)        

        fechainicio=Assets(self.mem).primera_datetime_con_datos_usuario()         

        self.mem.data.load_inactives()
        
        self.setData=None#Ser´a un TotalYear
        self.setGraphic=None #Ser´a un TotalGraphic
        
        if fechainicio==None: #Base de datos vacía
            self.tab.setEnabled(False)
            return
        
        self.table.settings("wdgTotal",  self.mem)
        self.tblTargets.settings("wdgTotal", self.mem)
        
        self.annualtarget=None#AnnualTarget Object
        
        self.wyData.initiate(fechainicio.year, datetime.date.today().year, datetime.date.today().year)
        self.wyChart.initiate(fechainicio.year, datetime.date.today().year, datetime.date.today().year-3)
        self.wyChart.label.setText(self.tr("Data from selected year"))

        self.canvas=canvasTotal(self.mem,  self)
        self.ntb = NavigationToolbar2QT(self.canvas, self)
        
        self.tabGraphTotal.addWidget(self.canvas)
        self.tabGraphTotal.addWidget(self.ntb)
        
        self.tab.setCurrentIndex(0)
        self.load_data()
        self.load_targets()
        self.wyData.changed.connect(self.on_wyData_mychanged)#Used my due to it took default on_wyData_changed
        self.wyChart.changed.connect(self.on_wyChart_mychanged)

    def load_data(self):        
        print ("loading data")
        self.table.clearContents()
        inicio=datetime.datetime.now()     
        self.setData=TotalYear(self.mem, self.wyData.year)
        self.lblPreviousYear.setText(self.tr("Balance at {0}-12-31: {1}".format(self.setData.year-1, self.mem.localcurrency.string(self.setData.total_last_year))))
        for i, m in enumerate(self.setData.arr):
            if m.year<datetime.date.today().year or (m.year==datetime.date.today().year and m.month<=datetime.date.today().month):
                self.table.setItem(0, i, self.mem.localcurrency.qtablewidgetitem(m.incomes()))
                self.table.setItem(1, i, self.mem.localcurrency.qtablewidgetitem(m.gains()))
                self.table.setItem(2, i, self.mem.localcurrency.qtablewidgetitem(m.dividends()))
                self.table.setItem(3, i, self.mem.localcurrency.qtablewidgetitem(m.expenses()))
                self.table.setItem(4, i, self.mem.localcurrency.qtablewidgetitem(m.i_d_g_e()))
                self.table.setItem(6, i, self.mem.localcurrency.qtablewidgetitem(m.total_accounts()))
                self.table.setItem(7, i, self.mem.localcurrency.qtablewidgetitem(m.total_investments()))
                self.table.setItem(8, i, self.mem.localcurrency.qtablewidgetitem(m.total()))
                self.table.setItem(9, i, self.mem.localcurrency.qtablewidgetitem(self.setData.difference_with_previous_month(m)))
                self.table.setItem(11, i, qtpc(self.setData.assets_percentage_in_month(m.month)))
        self.table.setItem(0, 12, self.mem.localcurrency.qtablewidgetitem(self.setData.incomes()))
        self.table.setItem(1, 12, self.mem.localcurrency.qtablewidgetitem(self.setData.gains()))
        self.table.setItem(2, 12, self.mem.localcurrency.qtablewidgetitem(self.setData.dividends()))
        self.table.setItem(3, 12, self.mem.localcurrency.qtablewidgetitem(self.setData.expenses()))
        self.table.setItem(4, 12, self.mem.localcurrency.qtablewidgetitem(self.setData.i_d_g_e()))      
        self.table.setItem(9, 12, self.mem.localcurrency.qtablewidgetitem(self.setData.difference_with_previous_year()))    
        self.table.setItem(11, 12, qtpc(self.setData.assets_percentage_in_month(12)))        
        self.table.setCurrentCell(6, datetime.date.today().month-1)

        final=datetime.datetime.now()          
        print ("wdgTotal > load_data: {0}".format(final-inicio))
    def load_targets(self):
        print ("loading targets")
        self.annualtarget=AnnualTarget(self.mem).init__from_db(self.wyData.year) 
        self.lblTarget.setText(self.tr("Annual target percentage of total assests balance at {}-12-31 ( {} )".format(self.annualtarget.year-1, self.mem.localcurrency.string(self.annualtarget.lastyear_assests))))
        self.spinTarget.setValue(float(self.annualtarget.percentage))
        self.tblTargets.clearContents()
        inicio=datetime.datetime.now()     
        sumd_g=Decimal(0)
        for i in range(1, 13): 
            m=self.setData.find(self.setData.year, i)
            sumd_g=sumd_g+m.d_g()
            self.tblTargets.setItem(0, i-1, self.mem.localcurrency.qtablewidgetitem(m.gains()))
            self.tblTargets.setItem(1, i-1, self.mem.localcurrency.qtablewidgetitem(m.dividends()))
            self.tblTargets.setItem(3, i-1, self.annualtarget.qtablewidgetitem_monthly(m.d_g()))
            self.tblTargets.setItem(4, i-1, self.mem.localcurrency.qtablewidgetitem(self.annualtarget.monthly_balance()))
            self.tblTargets.setItem(6, i-1, self.annualtarget.qtablewidgetitem_accumulated(sumd_g, i))
            self.tblTargets.setItem(7, i-1, self.mem.localcurrency.qtablewidgetitem(self.annualtarget.monthly_balance()*i))
        self.tblTargets.setItem(0, 12, self.mem.localcurrency.qtablewidgetitem(self.setData.gains()))
        self.tblTargets.setItem(1, 12, self.mem.localcurrency.qtablewidgetitem(self.setData.dividends()))
        self.tblTargets.setItem(3, 12, self.annualtarget.qtablewidgetitem_annual(sumd_g))
        self.tblTargets.setItem(4, 12, self.mem.localcurrency.qtablewidgetitem(self.annualtarget.annual_balance()))
        self.tblTargets.setCurrentCell(2, datetime.date.today().month-1)   
        print ("wdgTargets > load_data_targets: {0}".format(datetime.datetime.now()  -inicio))
        


    def load_graphic(self, savefile=None):   
        print("loading graphic")
        inicio=datetime.datetime.now()  
        total=[]#date,valor
        zero=[]#date, valor zero
        bonds=[]
        dates=[]
        
        self.setGraphic=TotalGraphic(self.mem, self.wyChart.year, 1)

        self.progress.reset()
        self.progress.setMaximum(self.setGraphic.length())
        self.progress.forceShow()
        self.progress.setValue(0)  
        for m in self.setGraphic.arr:
            if self.progress.wasCanceled():
                break
            self.progress.setValue(self.progress.value()+1)
            dates.append(m.last_day())
            total.append(m.total())
            zero.append(m.total_zerorisk())
            bonds.append(m.total_bonds())

        self.canvas.mydraw(self.mem, dates, total, zero,  bonds)
        
        if savefile!=None:
            self.canvas.fig.savefig(savefile, dpi=200)
        
        print ("wdgTotal > load_graphic: {0}".format(datetime.datetime.now()-inicio))

    def on_wyData_mychanged(self):
        self.load_data()    
        self.load_targets()

    def on_wyChart_mychanged(self):
        self.load_graphic()      
        
    def on_cmdTargets_released(self):
        self.annualtarget.percentage=self.spinTarget.value()
        self.annualtarget.save()
        self.mem.con.commit()
        self.load_targets()

    def on_tab_currentChanged(self, index):
        if  index==1 and self.canvas.plotted==False: #If has not been plotted, plots it.
            self.on_wyChart_mychanged()
        
    @QtCore.pyqtSlot() 
    def on_actionShowIncomes_triggered(self):
        id_tiposoperaciones=2
        newtab = QWidget()
        horizontalLayout = QHBoxLayout(newtab)
        table = myQTableWidget(newtab)
        set=SetAccountOperations(self.mem)
        set.load_from_db("select datetime, id_conceptos, id_tiposoperaciones, importe, comentario, id_cuentas from opercuentas where id_tiposoperaciones={0} and date_part('year',datetime)={1} and date_part('month',datetime)={2} and id_conceptos not in ({3}) union all select datetime, id_conceptos, id_tiposoperaciones, importe, comentario, id_cuentas from opertarjetas,tarjetas where opertarjetas.id_tarjetas=tarjetas.id_tarjetas and id_tiposoperaciones={0} and date_part('year',datetime)={1} and date_part('month',datetime)={2}".format (id_tiposoperaciones, self.wyData.year, self.month, list2string(self.mem.conceptos.considered_dividends_in_totals())))
        set.sort()
        set.myqtablewidget(table, "wdgTotal", True)
        horizontalLayout.addWidget(table)
        self.tab.addTab(newtab, self.tr("Incomes of {0} of {1}").format(self.table.horizontalHeaderItem(self.month-1).text(), self.wyData.year))
        self.tab.setCurrentWidget(newtab)

    @QtCore.pyqtSlot() 
    def on_actionShowSellingOperations_triggered(self):
        newtab = QWidget()
        horizontalLayout = QHBoxLayout(newtab)
        table = myQTableWidget(newtab)
        set=SetInvestmentOperationsHistorical(self.mem)
        for i in self.mem.data.investments_all().arr:
            for o in i.op_historica.arr:
                if o.fecha_venta.year==self.wyData.year and o.fecha_venta.month==self.month and o.tipooperacion.id in (5, 8):#Venta y traspaso fondos inversion
                    set.arr.append(o)
        set.order_by_fechaventa()
        set.myqtablewidget(table, "wdgTotal")
        horizontalLayout.addWidget(table)
        self.tab.addTab(newtab, self.tr("Product selling operations of {0} of {1}").format(self.table.horizontalHeaderItem(self.month-1).text(), self.wyData.year))
        self.tab.setCurrentWidget(newtab)
            

    @QtCore.pyqtSlot() 
    def on_actionShowDividends_triggered(self):
        newtab = QWidget()
        horizontalLayout = QHBoxLayout(newtab)
        table = myQTableWidget(newtab)
        set=SetDividends(self.mem)
        set.load_from_db("select * from dividends where id_conceptos not in (63) and date_part('year',fecha)={0} and date_part('month',fecha)={1}".format (self.wyData.year, self.month))
        set.sort()
        set.myqtablewidget(table, "wdgTotal", True)
        horizontalLayout.addWidget(table)
        self.tab.addTab(newtab, self.tr("Dividends of {0} of {1}").format(self.table.horizontalHeaderItem(self.month-1).text(), self.wyData.year))
        self.tab.setCurrentWidget(newtab)            
            
       
    @QtCore.pyqtSlot() 
    def on_actionShowExpenses_triggered(self):     
        id_tiposoperaciones=1
        newtab = QWidget()
        horizontalLayout = QHBoxLayout(newtab)
        table = myQTableWidget(newtab)
        set=SetAccountOperations(self.mem)
        set.load_from_db_with_creditcard("select datetime, id_conceptos, id_tiposoperaciones, importe, comentario, id_cuentas , -1 as id_tarjetas from opercuentas where id_tiposoperaciones={0} and date_part('year',datetime)={1} and date_part('month',datetime)={2} union all select datetime, id_conceptos, id_tiposoperaciones, importe, comentario, id_cuentas ,tarjetas.id_tarjetas as id_tarjetas from opertarjetas,tarjetas where opertarjetas.id_tarjetas=tarjetas.id_tarjetas and id_tiposoperaciones={0} and date_part('year',datetime)={1} and date_part('month',datetime)={2}".format (id_tiposoperaciones, self.wyData.year, self.month)      )
        set.sort()
        set.myqtablewidget(table, "wdgTotal", True)
        horizontalLayout.addWidget(table)
        self.tab.addTab(newtab, self.tr("Expenses of {0} of {1}").format(self.table.horizontalHeaderItem(self.month-1).text(), self.wyData.year))
        self.tab.setCurrentWidget(newtab)
        
    
    @QtCore.pyqtSlot() 
    def on_actionSellingOperationsPlusDividends_triggered(self):
        m=QMessageBox()
        value=self.setData.find(self.setData.year, self.month).d_g()
        message=self.tr("Gains and dividends sum from this month is {0}. In this year it's value rises to {1}").format(self.mem.localcurrency.string(value), self.mem.localcurrency.string(self.sumpopup[12]))

        m.setText(message)
        m.exec_()    
    
    def on_tab_tabCloseRequested(self, index):
        """Only removes dinamic tabs"""
        if index in (0, 1, 2):
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.tr("You can't close this tab"))
            m.exec_()  
        else:
            self.tab.setCurrentIndex(0)
            self.tab.removeTab(index)
            
    def on_table_customContextMenuRequested(self,  pos):
        if self.month==None:
            self.actionShowIncomes.setEnabled(False)
            self.actionShowExpenses.setEnabled(False)
            self.actionShowSellingOperations.setEnabled(False)
            self.actionShowDividends.setEnabled(False)
            self.actionSellingOperationsPlusDividends.setEnabled(False)
        else:
            self.actionShowIncomes.setEnabled(True)
            self.actionShowExpenses.setEnabled(True)
            self.actionShowSellingOperations.setEnabled(True)
            self.actionShowDividends.setEnabled(True)
            self.actionSellingOperationsPlusDividends.setEnabled(True)

        menu=QMenu()
        menu.addAction(self.actionShowIncomes)
        menu.addAction(self.actionShowSellingOperations)
        menu.addAction(self.actionShowDividends)
        menu.addAction(self.actionShowExpenses)
        menu.addSeparator()
        menu.addAction(self.actionSellingOperationsPlusDividends)      
        menu.exec_(self.table.mapToGlobal(pos))

    def on_table_itemSelectionChanged(self):
        self.month=None
        for i in self.table.selectedItems():#itera por cada item no row.
            self.month=i.column()+1
            if self.month>12:
                self.month=None
        print ("Selected month: {0}.".format(self.month))
