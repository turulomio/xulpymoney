from PyQt5.QtCore import *
from PyQt5.QtGui import *
from Ui_wdgAPR import *
from libxulpymoney import *
from matplotlib.finance import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT 
from matplotlib.dates import *
from matplotlib.figure import Figure

import datetime

# Matplotlib Figure object
class canvasAPR(FigureCanvasQTAgg):
    def __init__(self, mem, parent):
        self.mem=mem
        self.fig = Figure()
        FigureCanvasQTAgg.__init__(self, self.fig)
        FigureCanvasQTAgg.setSizePolicy(self,QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvasQTAgg.updateGeometry(self)
        self.ax = self.fig.add_subplot(111)
        self.labels=[]
        self.plot_expenses=None
        self.plot_gains=None
        self.plot_incomes=None
        self.plot_dividends=None
        self.plotted=False#Shown if the graphics has been plotted anytime.
        
    
    def price(self, x): 
        return self.mem.localcurrency.string(x)
        
    def mydraw(self, mem, dates,  expenses, incomes, gains,  dividends):
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
        
        self.plot_dividends, =self.ax.plot_date(dates, dividends, '-')
        self.plot_gains, =self.ax.plot_date(dates, gains, '-')
        self.plot_expenses, =self.ax.plot_date(dates, expenses, '-')
        self.plot_incomes, =self.ax.plot_date(dates, incomes, '-')
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
            self.labels.append((self.plot_incomes,self.tr("Incomes")))
            self.labels.append((self.plot_expenses,self.tr("Expenses")))
            self.labels.append((self.plot_gains,self.tr("Gains")))
            self.labels.append((self.plot_dividends, self.tr("Dividends")))


class wdgAPR(QWidget, Ui_wdgAPR):
    def __init__(self, mem,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        self.progress = QProgressDialog(self.tr("Filling data of the report"), self.tr("Cancel"), 0,0)
        self.progress.setModal(True)
        self.progress.setWindowTitle(self.tr("Calculating data..."))
        self.progress.setMinimumDuration(0)        
        self.table.settings("wdgAPR",  self.mem)
        
        
        self.dates=[]
        self.incomes=[]
        self.expenses=[]
        self.gains=[]
        self.dividends=[]
        
        
        self.mem.data.load_inactives()
        self.load_data()

        self.canvas=canvasAPR(self.mem,  self)
        self.ntb = NavigationToolbar2QT(self.canvas, self)
        
        self.tabGraph.addWidget(self.canvas)
        self.tabGraph.addWidget(self.ntb)
        self.canvas.mydraw(self.mem, self.dates,  self.expenses, self.incomes, self.gains,  self.dividends)

    def load_data(self):        
        inicio=datetime.datetime.now()       
        anoinicio=Assets(self.mem).primera_datetime_con_datos_usuario().year       
        anofinal=datetime.date.today().year+1        
        
        self.progress.reset()
        self.progress.setMinimum(1)
        self.progress.setMaximum(anofinal-anoinicio+1)
        self.progress.forceShow()
        self.progress.setValue(1)
        self.table.setRowCount(anofinal-anoinicio+1)
        lastsaldo=0
        sumdividends=0
        sumgains=0
        sumexpenses=0
        sumincomes=0
        sumicdg=0
        for i in range(anoinicio, anofinal):
            if self.progress.wasCanceled():
                break;
            else:
                self.progress.setValue(self.progress.value()+1)                     
            si=lastsaldo
            sf=Assets(self.mem).saldo_total(self.mem.data.investments_all(),  datetime.date(i, 12, 31))
            expenses=Assets(self.mem).saldo_anual_por_tipo_operacion( i,1)#+Assets(self.mem).saldo_anual_por_tipo_operacion (cur,i, 7)#expenses + Facturación de tarjeta
            dividends=Investment(self.mem).dividends_bruto( i)
            incomes=Assets(self.mem).saldo_anual_por_tipo_operacion(  i,2)-dividends #Se quitan los dividends que luego se suman
            gains=Assets(self.mem).consolidado_neto(self.mem.data.investments_all(),  i)
            
            self.dates.append(datetime.datetime(i, 12, 31))
            self.expenses.append(-expenses)
            self.dividends.append(dividends)
            self.incomes.append(incomes)
            self.gains.append(gains)

            gi=incomes+dividends+gains+expenses     
            self.table.setItem(i-anoinicio, 0, qcenter(str(i)))
            self.table.setItem(i-anoinicio, 1, self.mem.localcurrency.qtablewidgetitem(si))
            self.table.setItem(i-anoinicio, 2, self.mem.localcurrency.qtablewidgetitem(sf))
            self.table.setItem(i-anoinicio, 3, self.mem.localcurrency.qtablewidgetitem(sf-si))
            self.table.setItem(i-anoinicio, 4, self.mem.localcurrency.qtablewidgetitem(incomes))
            self.table.setItem(i-anoinicio, 5, self.mem.localcurrency.qtablewidgetitem(gains))
            self.table.setItem(i-anoinicio, 6, self.mem.localcurrency.qtablewidgetitem(dividends))
            self.table.setItem(i-anoinicio, 7, self.mem.localcurrency.qtablewidgetitem(expenses))
            self.table.setItem(i-anoinicio, 8, self.mem.localcurrency.qtablewidgetitem(gi))
            sumdividends=sumdividends+dividends
            sumgains=sumgains+gains
            sumexpenses=sumexpenses+expenses
            sumincomes=sumincomes+incomes
            sumicdg=sumicdg+gi
            if si==0:
                tae=0
            else:
                tae=(sf -si)*100/si
            self.table.setItem(i-anoinicio, 9, qtpc(tae))
            lastsaldo=sf
        self.table.setItem(anofinal-anoinicio, 0, qcenter((self.tr("TOTAL"))))
        self.table.setItem(anofinal-anoinicio, 4, self.mem.localcurrency.qtablewidgetitem(sumincomes))
        self.table.setItem(anofinal-anoinicio, 5, self.mem.localcurrency.qtablewidgetitem(sumgains))
        self.table.setItem(anofinal-anoinicio, 6, self.mem.localcurrency.qtablewidgetitem(sumdividends))
        self.table.setItem(anofinal-anoinicio, 7, self.mem.localcurrency.qtablewidgetitem(sumexpenses))
        self.table.setItem(anofinal-anoinicio, 8, self.mem.localcurrency.qtablewidgetitem(sumicdg))
        final=datetime.datetime.now()          
        print ("wdgAPR > load_data: {0}".format(final-inicio))
