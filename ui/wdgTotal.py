from PyQt4.QtCore import *
from PyQt4.QtGui import *
from libxulpymoney import *
from libxulpymoney import *
from matplotlib.finance import *

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg 

from matplotlib.dates import *
from Ui_wdgTotal import *
import calendar,  datetime

# Matplotlib Figure object
from matplotlib.figure import Figure
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
        
    def mydraw(self, mem, data, zero,  bonds):
        self.plotted=True
        self.ax.clear()

        (dates, total)=zip(*data)
        (datesz, zero)=zip(*zero)
        (datesb, bonds)=zip(*bonds)
        if len(dates)<36:
            self.ax.xaxis.set_minor_locator(MonthLocator())
            self.ax.xaxis.set_major_locator(MonthLocator())
            self.ax.xaxis.set_major_formatter( DateFormatter('%Y-%m'))   
        elif len(dates)>=36:
            self.ax.xaxis.set_minor_locator(YearLocator())
            self.ax.xaxis.set_major_locator(YearLocator())    
            self.ax.xaxis.set_major_formatter( DateFormatter('%Y'))                   
        self.ax.autoscale_view()
        
        # format the coords message box
        self.ax.fmt_xdata = DateFormatter('%Y-%m-%d')
        self.ax.fmt_ydata = self.price
        self.ax.grid(True)
        self.fig.autofmt_xdate()
        self.plot_main, =self.ax.plot_date(dates, total, '-')
        self.plot_zero, =self.ax.plot_date(datesz, zero, '-')
        self.plot_bonds, =self.ax.plot_date(datesb, bonds, '-')
        self.showLegend()
        self.draw()
        
    def showLegend(self):
        """Alterna mostrando y desmostrando legend, empieza con sí"""
        self.makeLegend()
                
        if self.ax.legend_==None:
            (plots, labels)=zip(*self.labels)
            self.ax.legend(plots, labels, "upper left")
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

class wdgTotal(QWidget, Ui_wdgTotal):
    def __init__(self, mem,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        self.progress = QProgressDialog(self.tr("Filling report data"), self.tr("Cancel"), 0,0)
        self.progress.setModal(True)
        self.progress.setWindowTitle(self.tr("Calculating data..."))
        self.progress.setMinimumDuration(0)        
        self.sumpopup=[]
        self.month=None#Used for popup
        for i in range(0, 13):
            self.sumpopup.append(0)

        fechainicio=Assets(self.mem).primera_datetime_con_datos_usuario()         

        self.mem.data.load_inactives()
        
        if fechainicio==None: #Base de datos vacía
            self.tab.setEnabled(False)
            return
        
        self.table.settings("wdgTotal",  self.mem)
        
        self.wyData.initiate(fechainicio.year, datetime.date.today().year, datetime.date.today().year)
        QObject.connect(self.wyData, SIGNAL("changed"), self.on_wyData_changed)
        self.wyChart.initiate(fechainicio.year, datetime.date.today().year, datetime.date.today().year)
        self.wyChart.label.setText(self.tr("Data from selected year"))
        QObject.connect(self.wyChart, SIGNAL("changed"), self.on_wyChart_changed)


        self.canvas=canvasTotal(self.mem,  self)
        self.ntb = NavigationToolbar2QTAgg(self.canvas, self)
        
        self.tabGraphTotal.addWidget(self.canvas)
        self.tabGraphTotal.addWidget(self.ntb)
        
        self.tab.setCurrentIndex(0)
        self.load_data()

        
    def load_data(self):        
        self.table.clearContents()
        inicio=datetime.datetime.now()     
        sumgastos=0
        sumdividends=0
        sumingresos=0        
        sumconsolidado=0
        sumdiferencia=0
        
        totallastmonth=Assets(self.mem).saldo_total(self.mem.data.investments_all(),  datetime.date(self.wyData.year-1, 12, 31))#Mes de 12 31 año anteriro
        self.lblPreviousYear.setText(self.tr("Balance at {0}-12-31: {1}".format(self.wyData.year-1, self.mem.localcurrency.string(totallastmonth))))
        inicioano=totallastmonth

        for i in range(12): 
            gastos=Assets(self.mem).saldo_por_tipo_operacion( self.wyData.year,i+1,1)#La facturación de tarjeta dentro esta por el union
            dividends=Investment(self.mem).dividends_neto(  self.wyData.year, i+1)
            ingresos=Assets(self.mem).saldo_por_tipo_operacion(  self.wyData.year,i+1,2)-dividends #Se quitan los dividends que luego se suman
            consolidado=Assets(self.mem).consolidado_neto(self.mem.data.investments_all(), self.wyData.year, i+1)
            gi=ingresos+dividends+consolidado+gastos
            self.sumpopup[i]=consolidado+dividends
            
            sumgastos=sumgastos+gastos
            sumdividends=sumdividends+dividends
            sumingresos=sumingresos+ingresos
            sumconsolidado=sumconsolidado+consolidado
            sumgi=sumgastos+sumdividends+sumingresos+sumconsolidado

            if  datetime.date.today()<datetime.date(self.wyData.year, i+1, 1):
                cuentas=0
                inversiones=0
                total=0
                diferencia=0
                tpc=0
            else:
                fecha=datetime.date (self.wyData.year, i+1, calendar.monthrange(self.wyData.year, i+1)[1])#Último día de mes.
                cuentas=Assets(self.mem).saldo_todas_cuentas( fecha)
                inversiones=Assets(self.mem).saldo_todas_inversiones(self.mem.data.investments_all(),  fecha)
                total=cuentas+inversiones
                diferencia=total-totallastmonth
                sumdiferencia=sumdiferencia+diferencia
                totallastmonth=total
                if inicioano==0:
                    tpc=None
                else:
                    tpc=100*(total-inicioano)/inicioano    
            
            self.table.setItem(0, i, self.mem.localcurrency.qtablewidgetitem(ingresos))
            self.table.setItem(1, i, self.mem.localcurrency.qtablewidgetitem(consolidado))
            self.table.setItem(2, i, self.mem.localcurrency.qtablewidgetitem(dividends))
            self.table.setItem(3, i, self.mem.localcurrency.qtablewidgetitem(gastos))
            self.table.setItem(4, i, self.mem.localcurrency.qtablewidgetitem(gi))
            self.table.setItem(6, i, self.mem.localcurrency.qtablewidgetitem(cuentas))
            self.table.setItem(7, i, self.mem.localcurrency.qtablewidgetitem(inversiones))
            self.table.setItem(8, i, self.mem.localcurrency.qtablewidgetitem(total))
            self.table.setItem(9, i, self.mem.localcurrency.qtablewidgetitem(diferencia))
            self.table.setItem(11, i, qtpc(tpc))
        self.table.setItem(0, 12, self.mem.localcurrency.qtablewidgetitem(sumingresos))
        self.table.setItem(1, 12, self.mem.localcurrency.qtablewidgetitem(sumconsolidado))
        self.table.setItem(2, 12, self.mem.localcurrency.qtablewidgetitem(sumdividends))
        self.table.setItem(3, 12, self.mem.localcurrency.qtablewidgetitem(sumgastos))
        self.table.setItem(4, 12, self.mem.localcurrency.qtablewidgetitem(sumgi))      
        self.sumpopup[12]=sumconsolidado+sumdividends
        self.table.setItem(9, 12, self.mem.localcurrency.qtablewidgetitem(sumdiferencia))    
        if inicioano==0:
            self.table.setItem(11, 12, qtpc(None))     
        else:
            self.table.setItem(11, 12, qtpc(sumdiferencia*100/inicioano))       
        
        self.table.setCurrentCell(6, datetime.date.today().month-1)

        final=datetime.datetime.now()          
        print ("wdgTotal > load_data: {0}".format(final-inicio))


    def load_graphic(self):          
        inicio=datetime.datetime.now()  
        data=[]#date,valor
        zero=[]#date, valor zero
        bonds=[]

        maximum=13*(datetime.date.today().year-self.wyChart.year)+datetime.date.today().month
        self.progress.reset()
        self.progress.setMinimum(1)
        self.progress.setMaximum(maximum)
        self.progress.forceShow()
        self.progress.setValue(0)       
        for year in range(self.wyChart.year, datetime.date.today().year+1):
            for month in range(1, 14):#12 primeros de mes y el 31 de diciembre
                self.progress.setValue(self.progress.value()+1)
                if month==13:
                    date=datetime.date(year, 12, 31)
                else:
                    date=datetime.date(year, month, 1)
                    
                if date.month==datetime.date.today().month and date.year==datetime.date.today().year:
                    date=datetime.date.today()
                elif self.progress.wasCanceled() or (date>datetime.date.today()):
                    self.progress.hide()
                    break
                

                data.append((date,Assets(self.mem).saldo_total(self.mem.data.investments_all(), date)))
                zero.append((date,Assets(self.mem).patrimonio_riesgo_cero(self.mem.data.investments_all(), date)))
                bonds.append((date,Assets(self.mem).saldo_todas_inversiones_bonds(date)))
        self.canvas.mydraw(self.mem, data, zero,  bonds)
        print ("wdgTotal > load_graphic: {0}".format(datetime.datetime.now()-inicio))

    def on_wyData_changed(self):
        self.load_data()    
        
    def on_wyChart_changed(self):
        self.load_graphic()      
        

    def on_tab_currentChanged(self, index):
        if  index==1 and self.canvas.plotted==False: #If has not been plotted, plots it.
            self.on_wyChart_changed()
            
        
    @QtCore.pyqtSlot() 
    def on_actionShowIncomes_activated(self):
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
    def on_actionShowSellingOperations_activated(self):
        newtab = QWidget()
        horizontalLayout = QHBoxLayout(newtab)
        table = myQTableWidget(newtab)
        set=SetInvestmentOperationsHistorical(self.mem)
        for i in self.mem.data.investments_all().arr:
            for o in i.op_historica.arr:
                if o.fecha_venta.year==self.wyData.year and o.fecha_venta.month==self.month and o.tipooperacion.id in (5, 8):#Venta y traspaso fondos inversion
                    set.arr.append(o)
        set.sort()
        set.myqtablewidget(table, "wdgTotal")
        horizontalLayout.addWidget(table)
        self.tab.addTab(newtab, self.tr("Product selling operations of {0} of {1}").format(self.table.horizontalHeaderItem(self.month-1).text(), self.wyData.year))
        self.tab.setCurrentWidget(newtab)
            

    @QtCore.pyqtSlot() 
    def on_actionShowDividends_activated(self):
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
    def on_actionShowExpenses_activated(self):     
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
    def on_actionSellingOperationsPlusDividends_activated(self):
        m=QMessageBox()
        message=self.tr("Gains and dividends sum from this month is {0}. In this year it's value rises to {1}").format(self.mem.localcurrency.string(self.sumpopup[self.month-1]), self.mem.localcurrency.string(self.sumpopup[12]))

        m.setText(message)
        m.exec_()    
    
    def on_tab_tabCloseRequested(self, index):
        """Only removes dinamic tabs"""
        if index in (0, 1):
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
