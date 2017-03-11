from PyQt5.QtCore import QMetaObject, Qt,  pyqtSlot,  QObject
from PyQt5.QtGui import QPainter, QFont
from PyQt5.QtWidgets import QAction, QApplication, QMenu, QSizePolicy, QWidget
from libxulpymoney import day_start, str2bool,  Percentage, epochms2aware, aware2epochms
from matplotlib.finance import candlestick2_ohlc,  plot_day_summary_oclh
from decimal import Decimal
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.dates import MonthLocator, YearLocator,   DateFormatter, date2num, num2date,  DayLocator
from matplotlib.figure import Figure
import pytz
import datetime

from PyQt5.QtChart import QChart,  QLineSeries, QChartView, QValueAxis, QDateTimeAxis,  QPieSeries



class VCTemporalSeries(QChartView):
    def __init__(self):
        QChartView.__init__(self)
        self.clear()
        self._allowHideSeries=True

    def setAxisFormat(self, axis,  min, max, type, zone=None):
        """
            type=0 #Value
            type=1 # Datetime
            
            if zone=None remains in UTC, zone is a zone object.
        """
        if type==0:
            if max-min<=0.01:
                axis.setLabelFormat("%.4f")
            elif max-min<=1:
                axis.setLabelFormat("%.2f")
            else:
                axis.setLabelFormat("%i")
        elif type==1:
            max=epochms2aware(max)#UTC aware
            min=epochms2aware(min)
            print(max, min, max-min)
            if max-min<datetime.timedelta(days=1):
                axis.setFormat("hh:mm")
            else:
                axis.setFormat("yyyy-MMM")
                


    def clear(self):
        self.chart=QChart()        
        self.chart.setAnimationOptions(QChart.AllAnimations);
        self.chart.layout().setContentsMargins(0,0,0,0);

#        #Axis cration
        self.axisX=QDateTimeAxis()
        self.axisX.setTickCount(15);
        
        self.axisY = QValueAxis()

        self.setRenderHint(QPainter.Antialiasing);
        self.setRubberBand(QChartView.VerticalRubberBand)
        
        self.series=[]
        self.maxx=None
        self.maxy=None
        self.minx=None
        self.miny=None
        font=QFont()
        font.setBold(True)
        font.setPointSize(12)
        self.chart.setTitleFont(font)


    def setAllowHideSeries(self, boolean):
        self._allowHideSeries=boolean

    def appendSeries(self, name,  currency=None):
        """
            currency is a Currency object
        """
        self.currency=currency
        ls=QLineSeries()
        ls.setName(name)
        self.series.append(ls)
        return ls


    def mouseMoveEvent(self, event):
        """
            event is a QMouseEvent
        """
        x=self.chart.mapToValue(event.pos()).x()
        y=self.chart.mapToValue(event.pos()).y()
#        for serie in self.series:
#            sx=None
#            sy=None
#            for point in serie.points():
#                if point.x()>x:
#                    sx=point.x()
#                    break
#            for point in serie.points():
#                if point.y()>y:
#                    sy=point.y()
#                    break
#            print(serie, sx, sy)
        print(x, y)
    @pyqtSlot()
    def on_marker_clicked(self):
        marker=QObject.sender(self)#Busca el objeto que ha hecho la signal en el slot en el que está conectado, ya que estaban conectados varios objetos a una misma señal
        marker.series().setVisible(not marker.series().isVisible())
        marker.setVisible(True)
        if marker.series().isVisible():
            alpha = 1
        else:
            alpha=0.5

        lbrush=marker.labelBrush()
        color=lbrush.color()
        color.setAlphaF(alpha)
        lbrush.setColor(color)
        marker.setLabelBrush(lbrush)

        brush=marker.brush()
        color=brush.color()
        color.setAlphaF(alpha)
        brush.setColor(color)
        marker.setBrush(brush)
        
        pen=marker.pen()
        color=pen.color()
        color.setAlphaF(alpha)
        pen.setColor(color)
        marker.setPen(pen)
        
        
    def appendData(self, ls, x, y):
        """
            x is a datetime zone aware
        """
        x=aware2epochms(x)
        ls.append(x, y)
        
        if ls.count()==1:#Gives first maxy and miny
            self.maxy=y
            self.miny=y
            self.maxx=x
            self.minx=x
            
        if y>self.maxy:
            self.maxy=y
        if y<self.miny:
            self.miny=y
        if x>self.maxx:
            self.maxx=x
        if x<self.minx:
            self.minx=x

    def display(self):
        self.setChart(self.chart)
        self.setAxisFormat(self.axisX, self.minx, self.maxx, 1)
        self.setAxisFormat(self.axisY, self.miny, self.maxy, 0)
        self.chart.addAxis(self.axisY, Qt.AlignLeft);
        self.chart.addAxis(self.axisX, Qt.AlignBottom);
        for s in self.series:
            self.chart.addSeries(s)
            s.attachAxis(self.axisX)
            s.attachAxis(self.axisY)
        self.axisY.setRange(self.miny, self.maxy)
        
        
        if self._allowHideSeries==True:
            for marker in self.chart.legend().markers():
                try:
                    marker.clicked.disconnect()
                except:
                    print("No estaba conectada")
                marker.clicked.connect(self.on_marker_clicked)
        
        
        self.repaint()

class VCPie(QChartView):
    def __init__(self):
        QChartView.__init__(self)
        self.setRenderHint(QPainter.Antialiasing)
        self.clear()
        
    def setCurrency(self, currency):
        """
            currency is a Currency Object
        """
        self.currency=currency

    def appendData(self, name, value,  exploded=False):
        slice=self.serie.append(name, value)
        slice.setExploded(exploded)
        slice.setLabelVisible()
        
    def display(self):
        tooltip=""
        c=self.currency.string
        for slice in self.serie.slices():
            tooltip=tooltip+"{}: {} ({})\n".format(slice.label(), c(slice.value()), Percentage(slice.percentage(), 1)).upper()
            slice.setLabel("{}: {}".format(slice.label(), Percentage(slice.percentage(), 1)).upper())
            if slice.percentage()<0.005:
                slice.setLabelVisible(False)
        tooltip=tooltip+"*** Total: {} ***".format(c(self.serie.sum())).upper()
        self.setChart(self.chart)
        self.chart.addSeries(self.serie)
        
        self.setToolTip(tooltip)
        self.repaint()
        
    def clear(self):
        self.chart=QChart()
        self.chart.legend().hide()
        font=QFont()
        font.setBold(True)
        font.setPointSize(12)
        self.chart.setTitleFont(font)
        self.chart.layout().setContentsMargins(0,0,0,0);
        self.chart.setAnimationOptions(QChart.AllAnimations);
        self.serie=QPieSeries()
        self.serie.setPieStartAngle(90)
        self.serie.setPieEndAngle(450)
        
class VCCandlestick(QChartView):
    def __init__(self):
        QChartView.__init__(self)
        self.chart=QChart()
        self.chart.setAnimationOptions(QChart.AllAnimations);
        self.chart.layout().setContentsMargins(0,0,0,0);

#        #Axis cration
        self.axisX=QDateTimeAxis()
        self.axisX.setTickCount(15);
        self.axisX.setFormat("yyyy-MM");
        
        self.axisY = QValueAxis()
        self.axisY.setLabelFormat("%i")

        self.setRenderHint(QPainter.Antialiasing);
        self.setRubberBand(QChartView.VerticalRubberBand)
        
        self.series=[]
        self.maxy=0
        self.miny=0

    def appendSeries(self, name):
#        ls=QCandlestickSeries()
#        ls.setName(name)
#        ls.setIncreasingColor(QColor(Qt.green));
#        ls.setDecreasingColor(QColor(Qt.red));
#        self.series.append(ls)
#        return ls
        pass    
        
    def appendData(self, ls, ohcl):
#        set=QCandlestickSet(ohcl.open, ohcl.high, ohcl.low, ohcl.close,  aware2epochms(ohcl.datetime()))
#        ls.append(set)
#        if ohcl.high>self.maxy:
#            self.maxy=ohcl.high
#        if ohcl.low<self.miny:
#            self.miny=ohcl.low
        pass

    def display(self):
        self.setChart(self.chart)
        self.chart.addAxis(self.axisY, Qt.AlignLeft);
        self.chart.addAxis(self.axisX, Qt.AlignBottom);
        for s in self.series:
            self.chart.addSeries(s)
            s.attachAxis(self.axisX)
            s.attachAxis(self.axisY)
        self.axisY.setRange(self.miny, self.maxy)
        self.repaint()
        
class ChartType:
    lines=0
    ohcl=1
    candles=2
    
    
class wdgMatplotlib(QWidget):
    def __init__(self):
        pass

class canvas(FigureCanvasQTAgg):
    def __init__(self, parent):       
        # setup Matplotlib Figure and Axis
        self.fig = Figure()
        FigureCanvasQTAgg.__init__(self, self.fig)
        # we define the widget as expandable
        FigureCanvasQTAgg.setSizePolicy(self,QSizePolicy.Expanding, QSizePolicy.Expanding)
        # notify the system of updated policy
        FigureCanvasQTAgg.updateGeometry(self)        


#class canvasChartIntraday(FigureCanvasQTAgg):
#    def __init__(self, mem,  parent):
#        # setup Matplotlib Figure and Axis
#        self.fig = Figure()
#        FigureCanvasQTAgg.__init__(self, self.fig)
#        # we define the widget as expandable
#        FigureCanvasQTAgg.setSizePolicy(self,QSizePolicy.Expanding, QSizePolicy.Expanding)
#        # notify the system of updated policy
#        FigureCanvasQTAgg.updateGeometry(self)        
#        
#        self.ax = self.fig.add_subplot(111)
#        
#        self.mem=mem
#
#    def get_locators(self):
#        self.ax.set_title(self.tr("Intraday graph"), fontsize=30, fontweight="bold", y=1.02)
#        self.ax.xaxis.set_major_locator(HourLocator(interval=1 , tz=pytz.timezone(self.mem.localzone.name)))
#        self.ax.xaxis.set_minor_locator(HourLocator(interval=1 , tz=pytz.timezone(self.mem.localzone.name)))
#        self.ax.xaxis.set_major_formatter(DateFormatter('%H:%M'))    
#        self.ax.fmt_xdata=DateFormatter('%H:%M')        
#
#        self.ax.fmt_ydata = self.price  
#        self.ax.grid(True)
#
#    def updateData(self, product, setquotesintraday):
#        """Loads a SetQuotesIntraday"""
#        self.product=product
#        self.setquotesintraday=setquotesintraday
#        
#        if self.setquotesintraday.length()<2:
#            return
#
#        self.ax.clear()
#        self.get_locators()
#        self.ax.plot_date(self.setquotesintraday.datetimes(), self.setquotesintraday.quotes(), '-',  tz=pytz.timezone(self.mem.localzone.name),  label=self.product.name)        
#        self.ax.set_ylabel(self.tr("{} quotes ({})".format(self.product.name, self.product.currency.symbol)))
#        self.ax.set_xlabel("{}".format(self.setquotesintraday.date))
#        self.draw()
#        
#    def price(self, x): 
#        return self.product.currency.string(x)

class canvasChartCompare(FigureCanvasQTAgg):
    def __init__(self, mem,   productcomparation, type,  parent):
        self.mem=mem
        self.comparation=productcomparation
        self.type=type
                
        # setup Matplotlib Figure and Axis
        self.fig = Figure()
        FigureCanvasQTAgg.__init__(self, self.fig)
        # we define the widget as expandable
        FigureCanvasQTAgg.setSizePolicy(self,QSizePolicy.Expanding, QSizePolicy.Expanding)
        # notify the system of updated policy
        FigureCanvasQTAgg.updateGeometry(self)        
        
        self.plot1=None
        self.plot2=None
        
        
        
        self.mydraw(self.type)

    def footer(self, date, y): 
        dt=num2date(date)
        dat=dt.date()
        return self.tr("{}. {}: {}, {}: {}.".format(dat, self.comparation.product1.name, self.comparation.set1.find(dat).close, self.comparation.product2.name, self.comparation.set2.find(dat).close))
        
    def mydraw(self, type):
        """self.setdata es un SetOHCLDaily"""
        self.ax= self.fig.add_subplot(111)
        self.ax.grid()
        if type==0:#Not changed data
            self.ax.set_title(self.tr("Comparing product quotes"), fontsize=30, fontweight="bold", y=1.02)
            self.ax.set_ylabel(self.tr("{} quotes ({})".format(self.comparation.product1.name, self.comparation.product1.currency.symbol)))
            self.ax2=self.ax.twinx()
            self.ax2.set_ylabel(self.tr("{} quotes ({})".format(self.comparation.product2.name, self.comparation.product2.currency.symbol)))
            self.plot1=self.ax.plot_date(self.comparation.dates(), self.comparation.product1Closes(), '-',  color="blue", label=self.comparation.product1.name)
            self.plot2=self.ax2.plot_date(self.comparation.dates(), self.comparation.product2Closes(), '-', color="green", label=self.comparation.product2.name)
            self.ax2.legend(loc="upper right")
            self.ax2.format_coord = self.footer
            self.get_locators()
            self.ax.legend(loc="upper left")
        elif type==1:#Scatter
            self.ax.set_title(self.tr("Comparing products with a scattering"), fontsize=30, fontweight="bold", y=1.02)
            self.ax.set_ylabel(self.tr("{} quotes ({})".format(self.comparation.product2.name, self.comparation.product2.currency.symbol)))
            self.ax.set_xlabel(self.tr("{} quotes ({})".format(self.comparation.product1.name, self.comparation.product1.currency.symbol)))
            self.plot1=self.ax.scatter(self.comparation.product1Closes(), self.comparation.product2Closes(), c=[date2num(date) for date in self.comparation.dates()])
            self.ax.annotate(xy=(5, 5), xycoords="figure pixels",  s=self.tr("Blue circles are older quotes and red ones are newer."))
        elif type==2:#Controlling percentage evolution.
            self.ax.set_title(self.tr("Comparing products with percentage evolution"), fontsize=30, fontweight="bold", y=1.02)
            self.plot1=self.ax.plot_date(self.comparation.dates(), self.comparation.product1PercentageFromFirstProduct2Price(), '-',  color="blue", label=self.comparation.product1.name)
            self.plot2=self.ax.plot_date(self.comparation.dates(), self.comparation.product2Closes(), '-', color="green", label=self.comparation.product2.name)
            self.ax.format_coord = self.footer  
            self.get_locators()
            self.ax.legend(loc="upper left")
        elif type==3:#Controlling percentage evolution.
            self.ax.set_title(self.tr("Comparing products with percentage evolution considering leverage multiplier"), fontsize=30, fontweight="bold", y=1.02)
            self.plot1=self.ax.plot_date(self.comparation.dates(), self.comparation.product1PercentageFromFirstProduct2PriceLeveragedReduced(), '-',  color="blue", label=self.comparation.product1.name)
            self.plot2=self.ax.plot_date(self.comparation.dates(), self.comparation.product2Closes(), '-', color="green", label=self.comparation.product2.name)
            self.ax.format_coord = self.footer  
            self.get_locators()
            self.ax.legend(loc="upper left")
        
        self.draw()

    def get_locators(self):
        interval=(self.mem.localzone.now()-self.comparation.set1.first().datetime()).days+1
        
        if interval<365:
            self.ax.xaxis.set_minor_locator(MonthLocator())
            self.ax.xaxis.set_major_locator(MonthLocator())
            self.ax.xaxis.set_major_formatter( DateFormatter('%Y-%m-%d'))   
        elif interval>=365:
            self.ax.xaxis.set_minor_locator(MonthLocator())
            self.ax.xaxis.set_major_locator(YearLocator())   
            self.ax.xaxis.set_major_formatter( DateFormatter('%Y'))
        self.ax.grid(True)


class canvasChartHistorical(FigureCanvasQTAgg):                
    def __init__(self, mem,   parent):
        self.mem=mem
        # setup Matplotlib Figure and Axis
        self.fig = Figure()
        FigureCanvasQTAgg.__init__(self, self.fig)
        # we define the widget as expandable
        FigureCanvasQTAgg.setSizePolicy(self,QSizePolicy.Expanding, QSizePolicy.Expanding)
        # notify the system of updated policy
        FigureCanvasQTAgg.updateGeometry(self)      
        self.ax= self.fig.add_subplot(111)
        self.plot_average=None
        self.plot_selling=None
        self.plot_purchases=None
        self.plot_sales=None
        self.plot_sma200=None
        self.plot_sma50=None
        self.from_dt=self.mem.localzone.now()-datetime.timedelta(days=365)#Show days from this date
        
        self.purchase_type=None#None ninguno 0 con reinversión personalizada, 1 con reinversión dinero invertido, 2 con reinversión dinero invertido x2 y 3 con reinversion dinero invertido x1.5 

        self.actionLines1d=QAction(self)
        self.actionLines1d.setText(self.tr("1 day"))
        self.actionLines1d.setObjectName("actionLines1d")
        self.actionLines7d=QAction(self)
        self.actionLines7d.setText(self.tr("1 week"))
        self.actionLines7d.setObjectName("actionLines7d")
        self.actionLines7d.setEnabled(False)
        self.actionLines30d=QAction(self)
        self.actionLines30d.setText(self.tr("1 month"))
        self.actionLines30d.setObjectName("actionLines30d")
        self.actionLines30d.setEnabled(False)
        self.actionLines365d=QAction(self)
        self.actionLines365d.setText(self.tr("1 year"))
        self.actionLines365d.setObjectName("actionLines365d")
        self.actionLines365d.setEnabled(False)
        
        self.actionOHCL1d=QAction(self)
        self.actionOHCL1d.setText(self.tr("1 day"))
        self.actionOHCL1d.setObjectName("actionOHCL1d")
        self.actionOHCL7d=QAction(self)
        self.actionOHCL7d.setText(self.tr("1 week"))
        self.actionOHCL7d.setObjectName("actionOHCL7d")
        self.actionOHCL30d=QAction(self)
        self.actionOHCL30d.setText(self.tr("1 month"))
        self.actionOHCL30d.setObjectName("actionOHCL30d")
        self.actionOHCL365d=QAction(self)
        self.actionOHCL365d.setText(self.tr("1 year"))
        self.actionOHCL365d.setObjectName("actionOHCL365d")
        
        self.actionCandles1d=QAction(self)
        self.actionCandles1d.setText(self.tr("1 day"))
        self.actionCandles1d.setEnabled(True)
        self.actionCandles1d.setObjectName("actionCandles1d")
        self.actionCandles7d=QAction(self)
        self.actionCandles7d.setText(self.tr("1 week"))
        self.actionCandles7d.setEnabled(False)
        self.actionCandles7d.setObjectName("actionCandles7d")
        self.actionCandles30d=QAction(self)
        self.actionCandles30d.setText(self.tr("1 month"))
        self.actionCandles30d.setEnabled(False)
        self.actionCandles30d.setObjectName("actionCandles30d")
        self.actionCandles365d=QAction(self)
        self.actionCandles365d.setText(self.tr("1 year"))
        self.actionCandles365d.setEnabled(False)
        self.actionCandles365d.setObjectName("actionCandles365d")
        
        self.actionSMA50=QAction(self)
        self.actionSMA50.setText(self.tr("Simple moving average 50"))
        self.actionSMA50.setCheckable(True)
        self.actionSMA50.setObjectName("actionSMA50")
        self.actionSMA200=QAction(self)
        self.actionSMA200.setText(self.tr("Simple moving average 200"))
        self.actionSMA200.setCheckable(True)
        self.actionSMA200.setObjectName("actionSMA200")
        
        self.labels=[]#Array de tuplas (plot,label)

        QMetaObject.connectSlotsByName(self)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.on_customContextMenuRequested)
        self.fig.canvas.mpl_connect('scroll_event', self.on_wheelEvent)
        self.actionSMA50.setChecked(str2bool(self.mem.settings.value("canvasHistorical/sma50", "True" )))
        self.actionSMA200.setChecked(str2bool(self.mem.settings.value("canvasHistorical/sma200", "True" )))           

    def footer(self, date, y): 
        dt=num2date(date)
        dat=dt.date()
        try:
            return self.tr("{}: {}.".format(dat, self.product.currency.string(self.setdata.find(dat).close)))
        except:
            return "Not found"

    @pyqtSlot()
    def on_actionSMA50_triggered(self):
        self.mem.settings.setValue("canvasHistorical/sma50",   self.actionSMA50.isChecked())
        
    @pyqtSlot()
    def on_actionSMA200_triggered(self):
        self.mem.settings.setValue("canvasHistorical/sma200",   self.actionSMA200.isChecked())

    def draw_sma50(self,  datime, quotes):
        """
        Calculamos segun
        a=[1,2,3,4]
        sum([0:2])=3
        """
        if self.actionSMA50.isChecked()==False:
            return
        if len(quotes)<50:
            return
        dat=[]
        sma=[]
        for i in range(50, len(quotes)):
            dat.append(datime[i-1])
            sma.append(sum(quotes[i-50:i])/Decimal(50))
        self.plot_sma50, =self.ax.plot_date(dat, sma, '-',  color='gray')     
    
    def draw_sma200(self, datime, quotes):
        if self.actionSMA200.isChecked()==False:
            return
        if len(quotes)<200:
            return
        dat=[]
        sma=[]
        for i in range(200, len(quotes)):
            dat.append(datime[i-1])
            sma.append(sum(quotes[i-200:i])/Decimal(200))
        self.plot_sma200, =self.ax.plot_date(dat, sma, '-', color="red")    

    def candles(self, interval):
        """Interval 0.05 5minutos
        1 1 dia
        
        setdata es un SetOHCLDaily"""
        self.ax.clear()
        if self.setdata.length()==0:
            return

        quotes=[]
        for d in self.setdata.arr:
            if d.datetime()>self.from_dt:
                quotes.append((d.date.toordinal(), d.open, d.high, d.low, d.close))
        self.ax.grid(True)
        candlestick2_ohlc(self.ax, self.setdata.opens(self.from_dt), self.setdata.highs(self.from_dt),  self.setdata.lows(self.from_dt), self.setdata.closes(self.from_dt),   width=0.7,  colorup='g')
        self.ax.xaxis_date()
    
    def makeLegend(self):
        if len(self.labels)==0:
            self.labels.append((self.plot_sma200, self.tr("SMA200")))
            self.labels.append((self.plot_sma50,self.tr("SMA50")))
            self.labels.append((self.plot_selling, self.tr("Selling price")))
            self.labels.append((self.plot_average, self.tr("Average purchase price")))
            self.labels.append((self.plot_purchases, self.tr("Purchase point")))
            self.labels.append((self.plot_sales, self.tr("Sales point")))

    def mydraw(self):
        """Punto de entrada de inicio, cambio de rueda, """
        type=int(self.mem.settings.value("canvasHistorical/type", "0"))
        interval=int(self.mem.settings.value("canvasHistorical/interval", "1"))
        if type==ChartType.lines:
            if interval==1:
                self.setdata=self.product.result.ohclDaily
                self.on_actionLines1d_triggered()
        elif type==ChartType.ohcl:
            if interval==1:
                self.setdata=self.product.result.ohclDaily
                self.on_actionOHCL1d_triggered()
            if interval==7:
                self.setdata=self.product.result.ohclWeekly
                self.on_actionOHCL7d_triggered()
            if interval==30:
                self.setdata=self.product.result.ohclMonthly
                self.on_actionOHCL30d_triggered()
            if interval==365:
                self.setdata=self.product.result.ohclYearly
                self.on_actionOHCL365d_triggered()
        elif type==ChartType.candles:
            self.setdata=self.product.result.ohclDaily
            self.on_actionCandles1d_triggered()
        self.ax.set_ylabel(self.tr("{} quotes ({})".format(self.product.name, self.product.currency.symbol)))
        self.ax.set_title(self.tr("Historical graph"), fontsize=30, fontweight="bold", y=1.02)
        self.draw()

    @pyqtSlot()
    def on_wheelEvent(self, event):
        now=self.mem.localzone.now()
        if event.button=='up':
            self.from_dt=self.from_dt+datetime.timedelta(days=365)
        else:
            self.from_dt=self.from_dt-datetime.timedelta(days=365)
        if self.from_dt>now-datetime.timedelta(days=365):
            self.from_dt=now-datetime.timedelta(days=365)
            QApplication.beep()
        self.mydraw()
        
    @pyqtSlot()
    def on_actionOHCL1d_triggered(self):
        self.mem.settings.setValue("canvasHistorical/type", ChartType.ohcl)
        self.mem.settings.setValue("canvasHistorical/interval",   "1")
        self.ohcl(self.setdata, datetime.timedelta(days=1))     
        self.draw_selling_point()
        self.draw_average_purchase_price()
        self.draw_investment_operations()
        self.showLegend()

    @pyqtSlot()
    def on_actionLines1d_triggered(self):
        self.mem.settings.setValue("canvasHistorical/type",   ChartType.lines)
        self.mem.settings.setValue("canvasHistorical/interval",   "1")
        self.draw_lines_from_ohcl()
        self.draw_selling_point()
        self.draw_average_purchase_price()
        self.draw_investment_operations()
        self.showLegend()

    @pyqtSlot()
    def on_actionCandles1d_triggered(self):
        self.mem.settings.setValue("canvasHistorical/type",   ChartType.candles)
        self.mem.settings.setValue("canvasHistorical/interval",   "1")
        self.candles(datetime.timedelta(days=1))
        if self.setdata.length()<1000:
            self.ax.xaxis.set_minor_locator(DayLocator())
            self.ax.xaxis.set_major_locator(MonthLocator())
            self.ax.xaxis.set_major_formatter( DateFormatter('%Y-%m-%d'))   
        else:
            self.ax.xaxis.set_minor_locator(MonthLocator())
            self.ax.xaxis.set_major_locator(YearLocator())
        self.ax.autoscale_view()

    @pyqtSlot()
    def on_actionOHCL7d_triggered(self):
        self.mem.settings.setValue("canvasHistorical/type", ChartType.ohcl)
        self.mem.settings.setValue("canvasHistorical/interval",   "7")
        self.ohcl(self.setdata, datetime.timedelta(days=7))     
        self.draw_selling_point()
        self.draw_average_purchase_price()
        self.showLegend()   

    @pyqtSlot()
    def on_actionOHCL30d_triggered(self):
        self.mem.settings.setValue("canvasHistorical/type", ChartType.ohcl)
        self.mem.settings.setValue("canvasHistorical/interval",   "30")
        self.ohcl(self.setdata, datetime.timedelta(days=30))     
        self.draw_selling_point()
        self.draw_average_purchase_price()
        self.showLegend()   

    @pyqtSlot()
    def on_actionOHCL365d_triggered(self):
        self.mem.settings.setValue("canvasHistorical/type", ChartType.ohcl)
        self.mem.settings.setValue("canvasHistorical/interval",   "365")
        self.ohcl(self.setdata, datetime.timedelta(days=365))     
        self.draw_selling_point()
        self.draw_average_purchase_price()
        self.showLegend()   

    def draw_selling_point(self):
        """Draws an horizontal line with the selling point price"""
        if self.investment==None:
            return
        if self.investment.venta!=0:
            dates=[]
            quotes=[]
            dates.append(self.from_dt-datetime.timedelta(days=7))#To see more margin
            dates.append(datetime.date.today()+datetime.timedelta(days=7))
            quotes.append(self.investment.venta)
            quotes.append(self.investment.venta)
            self.plot_selling, =self.ax.plot_date(dates, quotes, 'r--', color="darkblue",  tz=pytz.timezone(self.mem.localzone.name)) #fijarse en selling, podría ser sin ella selling[0]

    def draw_investment_operations(self):
        """Draws an horizontal line with the selling point price"""
        if self.investment==None:
            return
        if self.investment.op.length()>0:
            dates_p=[]#purchase
            quotes_p=[]
            dates_s=[]#sales
            quotes_s=[]
            for o in self.investment.op.arr:
                if o.datetime>=self.from_dt:
                    if o.acciones>=0:
                        dates_p.append(o.datetime.date())
                        quotes_p.append(o.valor_accion)
                    else:
                        dates_s.append(o.datetime.date())
                        quotes_s.append(o.valor_accion)
            self.plot_purchases, =self.ax.plot_date(dates_p, quotes_p, 'bo', color="green",  tz=pytz.timezone(self.mem.localzone.name))
            self.plot_sales, =self.ax.plot_date(dates_s, quotes_s, 'bo', color="red",  tz=pytz.timezone(self.mem.localzone.name)) 

    def draw_average_purchase_price(self):
        """Draws an horizontal line with the average purchase price"""
        if self.investment==None:
            return
        dates=[]
        quotes=[]
        dates.append(self.from_dt-datetime.timedelta(days=7))#To see more margin
        dates.append(datetime.date.today()+datetime.timedelta(days=7))
        average=self.investment.op_actual.average_price().amount
        quotes.append(average)
        quotes.append(average)
        self.plot_average, =self.ax.plot_date(dates, quotes, 'r--', color="orange",  tz=pytz.timezone(self.mem.localzone.name))


    def on_customContextMenuRequested(self, pos):
        menu=QMenu()
        ohcl=QMenu("OHCL")
        ohcl.addAction(self.actionOHCL1d)
        ohcl.addAction(self.actionOHCL7d)
        ohcl.addAction(self.actionOHCL30d)
        ohcl.addAction(self.actionOHCL365d)
        menu.addMenu(ohcl)        
        lines=QMenu(self.tr("Lines"))
        lines.addAction(self.actionLines1d)
        lines.addAction(self.actionLines7d)
        lines.addAction(self.actionLines30d)
        lines.addAction(self.actionLines365d)
        menu.addMenu(lines)        
        candles=QMenu(self.tr("Candles"))
        candles.addAction(self.actionCandles1d)
        candles.addAction(self.actionCandles7d)
        candles.addAction(self.actionCandles30d)
        candles.addAction(self.actionCandles365d)
        menu.addMenu(candles)        
        menu.addSeparator()
        menu.addAction(self.actionSMA50)
        menu.addAction(self.actionSMA200)
        menu.exec_(self.mapToGlobal(pos)) 

    def draw_lines_from_ohcl(self):
        """self.setdata es un SetOHCLDaily"""
        self.ax.clear()
        if self.setdata.length()<2:
            return
            
        dates=[]
        quotes=[]
        for ohcl in self.setdata.arr:
            dt=ohcl.datetime()
            if dt>self.from_dt:
                dates.append(dt)
                quotes.append(ohcl.close)

        self.get_locators()
        self.ax.plot_date(dates, quotes, '-')
        self.draw_sma50(dates, quotes)
        self.draw_sma200(dates, quotes)
        self.draw()
        
    def draw_lines_from_quotes(self):
        """Deben estar con tz, se recibe data porque puede recortarese según zoom
        set is a SetQuotesIntraday"""
        self.ax.clear()
        if self.setdata.length()<2:
            return
        (datetimes, quotes)=([], [])
        for q in self.setdata.arr:
            datetimes.append(q.datetime)
            quotes.append(q.quote)

        self.get_locators()
        self.ax.plot_date(datetimes, quotes, '-',  tz=pytz.timezone(self.mem.localzone.name))
        
        self.draw_sma50(datetimes, quotes)
        self.draw_sma200(datetimes, quotes)
        self.draw_newPurchaseReferences(datetimes, quotes)
        self.draw()

        
    def ohcl(self, setohcl,  interval):
        """setohcl es un setohcl"""
        self.ax.clear()
        if setohcl.length()<2:
            return
        quotes=[]
        dates=[]
        close=[]
        self.get_locators()
        for d in setohcl.arr:
            quotes.append((d.datetime().toordinal(), d.open, d.close,  d.high, d.low))         #ESTE ES EL CAUSEANTE NO SE VEA MENOR DE DIARIO TOOARDIANL
            dates.append(d.datetime())
            close.append(d.close)
        self.ax.fmt_xdata = DateFormatter('%Y-%m-%d')
        left=self.from_dt.toordinal()-interval.days#De margen
        right=self.mem.localzone.now().toordinal()+interval.days
        self.ax.set_xlim(left, right)
        plot_day_summary_oclh(self.ax, quotes,  ticksize=3)
        self.draw_sma50(dates, close)
        self.draw_sma200(dates, close)

    def showLegend(self):
        """Alterna mostrando y desmostrando legend, empieza con sí"""
        self.makeLegend()
                
        if self.ax.legend_==None:
            (plots, labels)=zip(*self.labels)
            self.ax.legend( plots, labels, loc="best")
        else:
            self.ax.legend_=None
        self.draw()

    def mouseReleaseEvent(self,  event):
        self.showLegend()
    def get_locators(self):
        interval=(self.mem.localzone.now()-self.from_dt).days+1
        
        if interval<365:
            self.ax.xaxis.set_minor_locator(MonthLocator())
            self.ax.xaxis.set_major_locator(MonthLocator())
            self.ax.xaxis.set_major_formatter( DateFormatter('%Y-%m-%d'))   
#            self.ax.fmt_xdata=DateFormatter('%Y-%m-%d')
        elif interval>=365:
            self.ax.xaxis.set_minor_locator(MonthLocator())
            self.ax.xaxis.set_major_locator(YearLocator())   
            self.ax.xaxis.set_major_formatter( DateFormatter('%Y'))        
                        
        self.ax.format_coord = self.footer  
        self.ax.grid(True)

    def load_data(self, product,   inversion=None, SD=False):
        """Debe tener cargado los ohcl, no el all"""
        self.product=product
        self.investment=inversion
        if self.investment!=None:
            if self.investment.op_actual.length()>0:
                self.from_dt=day_start(self.investment.op_actual.first().datetime, self.mem.localzone)
        self.sd=SD#Sin descontar dividends, es decir sumará los dividends a las quotes.
        self.mydraw()

class canvasChartHistoricalBuy(FigureCanvasQTAgg):                
    def __init__(self, mem,   parent):
        self.mem=mem
        # setup Matplotlib Figure and Axis
        self.fig = Figure()
        FigureCanvasQTAgg.__init__(self, self.fig)
        # we define the widget as expandable
        FigureCanvasQTAgg.setSizePolicy(self,QSizePolicy.Expanding, QSizePolicy.Expanding)
        # notify the system of updated policy
        FigureCanvasQTAgg.updateGeometry(self)      
        self.ax= self.fig.add_subplot(111)
        self.plot_sma200=None
        self.plot_sma50=None
        self.plot_reference_buy=None
        self.plot_reference_sell=None
        self.plot_reference_1b=None
        self.plot_reference_1s=None
        self.plot_reference_2b=None
        self.plot_reference_2s=None
        self.plot_reference_3b=None
        self.plot_reference_3s=None
        self.plot_reference_1a=None#Average
        self.plot_reference_2a=None
        self.plot_reference_3a=None
        
        
        self.purchase_type=None#None ninguno 0 con reinversión personalizada, 1 con reinversión dinero invertido, 2 con reinversión dinero invertido x2 y 3 con reinversion dinero invertido x1.5 
       
        self.actionSMA50=QAction(self)
        self.actionSMA50.setText(self.tr("Simple moving average 50"))
        self.actionSMA50.setCheckable(True)
        self.actionSMA50.setObjectName("actionSMA50")
        self.actionSMA200=QAction(self)
        self.actionSMA200.setText(self.tr("Simple moving average 200"))
        self.actionSMA200.setCheckable(True)
        self.actionSMA200.setObjectName("actionSMA200")
        
        self.labels=[]#Array de tuplas (plot,label)

        QMetaObject.connectSlotsByName(self)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.on_customContextMenuRequested)
        self.fig.canvas.mpl_connect('scroll_event', self.on_wheelEvent)
        self.actionSMA50.setChecked(str2bool(self.mem.settings.value("canvasHistorical/sma50", "True" )))
        self.actionSMA200.setChecked(str2bool(self.mem.settings.value("canvasHistorical/sma200", "True" )))           

    def footer(self, date, y): 
        dt=num2date(date)
        dat=dt.date()
        try:
            return self.tr("{}: {}.".format(dat, self.product.currency.string(self.setdata.find(dat).close)))
        except:
            return "Not found"

    @pyqtSlot()
    def on_actionSMA50_triggered(self):
        self.mem.settings.setValue("canvasHistorical/sma50",   self.actionSMA50.isChecked())
        
    @pyqtSlot()
    def on_actionSMA200_triggered(self):
        self.mem.settings.setValue("canvasHistorical/sma200",   self.actionSMA200.isChecked())

    def draw_sma50(self,  datime, quotes):
        """
        Calculamos segun
        a=[1,2,3,4]
        sum([0:2])=3
        """
        if self.actionSMA50.isChecked()==False:
            return
        if len(quotes)<50:
            return
        dat=[]
        sma=[]
        for i in range(50, len(quotes)):
            dat.append(datime[i-1])
            sma.append(sum(quotes[i-50:i])/Decimal(50))
        self.plot_sma50, =self.ax.plot_date(dat, sma, '-',  color='gray')     
    
    def draw_sma200(self, datime, quotes):
        if self.actionSMA200.isChecked()==False:
            return
        if len(quotes)<200:
            return
        dat=[]
        sma=[]
        for i in range(200, len(quotes)):
            dat.append(datime[i-1])
            sma.append(sum(quotes[i-200:i])/Decimal(200))
        self.plot_sma200, =self.ax.plot_date(dat, sma, '-', color="red")    



    def mydraw(self):
        """Punto de entrada de inicio, cambio de rueda, """
        self.setdata=self.product.result.ohclDaily       
        self.purchase_type=2
        self.draw_lines_from_ohcl()
        self.draw_newPurchaseReferences()

        self.ax.set_ylabel(self.tr("{} quotes ({})".format(self.product.name, self.product.currency.symbol)))
        self.ax.set_title(self.tr("Historical graph"), fontsize=30, fontweight="bold", y=1.02)
        self.showLegend()
        self.draw()

    def draw_newPurchaseReferences(self):        
        """Es un porcentaje  de disminución haciendo compras de capital x2
        Si compro a 20 luego compro el doble a un -33% me queda de media todo 15.06 que es un 15.06/20 0.753%
        Es decir precio medio de compra / precio inicial de compra
        """
        if not self.purchase_type:
            return

        percentages2=[0.753, 0.5185, 0.3495, 0.23464]
        print(percentages2)
        percentagespersonal=[0.777, 0.5225, 0.4035, 0.269]
        percentagesmy=percentagespersonal

        percentage=Decimal(self.mem.settingsdb.value("frmSellingPoint/lastgainpercentage",  5))

        if self.purchase_type==2:
            
            dat=[]
            dat.append(self.from_dt)
            dat.append(datetime.datetime.now())
            self.price_sell=self.price_buy*(1+percentage/Decimal(100))
            
            self.price_a1=self.price_buy*Decimal(percentagesmy[0])
            self.price_s1=self.price_a1*(1+percentage/Decimal(100))
            self.price_b1=self.price_buy*Decimal(1-0.33)
            
            self.price_a2=self.price_buy*Decimal(percentagesmy[1])
            self.price_s2=self.price_a2*(1+percentage/Decimal(100))
            self.price_b2=self.price_b1*Decimal(1-0.33)
            
            self.price_a3=self.price_buy*Decimal(percentagesmy[2])
            self.price_s3=self.price_a3*(1+percentage/Decimal(100))
            self.price_b3=self.price_b2*Decimal(1-0.33)
            
#
#        print("Compro a {}. Vendo a {} que es un {} %".format(self.price_buy, sell.price_sell,  percentage))
#        print("r1: punto medio compra {}. Vendo a {} que es un {}".format(self.buyprice])*(+percentage/Decimal(100)) , percentage))
#        print("r2: punto medio compra {}. Vendo a {} que es un {}".format(self.buyprice*Decimal(percentagesmy[1]),self.buyprice*Decimal(percentagesmy[1])*(1+percentage/Decimal(100)) , percentage))
#        print("r3: punto medio compra {}. Vendo a {} que es un {}".format(self.buyprice*Decimal(percentagesmy[2]),self.buyprice*Decimal(percentagesmy[2])*(1+percentage/Decimal(100)) , percentage))
        self.plot_reference_sell, =self.ax.plot_date(dat, [self.price_sell]*2, '-',  color='green', lw=2)     
        self.plot_reference_buy, =self.ax.plot_date(dat, [self.price_buy]*2, '-',  color='red', lw=2)  
        
        self.plot_reference_s1, =self.ax.plot_date(dat, [self.price_s1]*2, '--',  color='green', lw=3) 
        self.plot_reference_b1, =self.ax.plot_date(dat, [self.price_b1]*2, '--',  color='red', lw=3) 
        self.plot_reference_a1, =self.ax.plot_date(dat, [self.price_a1]*2, '--',  color='orange', lw=3)   
        
        self.plot_reference_s2, =self.ax.plot_date(dat, [self.price_s2]*2, '--',  color='green', lw=2) 
        self.plot_reference_b2, =self.ax.plot_date(dat, [self.price_b2]*2, '--',  color='red', lw=2) 
        self.plot_reference_a2, =self.ax.plot_date(dat, [self.price_a2]*2, '--',  color='orange', lw=2)  
        
        self.plot_reference_s3, =self.ax.plot_date(dat, [self.price_s3]*2, '--',  color='green', lw=1) 
        self.plot_reference_b3, =self.ax.plot_date(dat, [self.price_b3]*2, '--',  color='red', lw=1) 
        self.plot_reference_a3, =self.ax.plot_date(dat, [self.price_a3]*2, '--',  color='orange', lw=1)  

        self.ax.annotate(xy=(5, 5), xycoords="figure pixels",  s=self.tr("Lines calculated investing: 2500 €, 3500 €, 12000 €, 12000 €." + " " + self.tr("Selling percentage: {} %.".format(percentage))))
        #self.ax.annotate(xy=(5, 5), xycoords="figure pixels",  s=self.tr("Gains percentage: {}. First Purchase price: {}. First Selling price: {}. Second: {}. Third: {}. Forth: {}.".format(tpc(percentage), c(self.price_buy), c(sell.self.buyprice*(1+percentage/Decimal(100))), c(self.buyprice*Decimal(percentagesmy[0])*(1+percentage/Decimal(100))), c(self.buyprice*Decimal(percentagesmy[1])*(1+percentage/Decimal(100))), c(self.buyprice*Decimal(percentagesmy[2])*(1+percentage/Decimal(100))))))

    def makeLegend(self):
        if len(self.labels)==0:
            c=self.product.currency.string
            self.labels.append((self.plot_sma200, self.tr("SMA200")))
            self.labels.append((self.plot_sma50,self.tr("SMA50")))
            self.labels.append((self.plot_reference_sell, self.tr("Sell reference ({})".format(c(self.price_sell)))))
            self.labels.append((self.plot_reference_buy, self.tr("Purchase reference ({})".format(c(self.price_buy)))))
            self.labels.append((self.plot_reference_s1,  self.tr("First reinvestment selling point ({})".format(c(self.price_s1)))))
            self.labels.append((self.plot_reference_a1, self.tr("First reinvestment average purchase point ({})".format(c(self.price_a1)))))
            self.labels.append((self.plot_reference_b1, self.tr("First reinvestment purchase point ({})".format(c(self.price_b1)))))
            self.labels.append((self.plot_reference_s2, self.tr("Second reinvestment selling point ({})".format(c(self.price_s2)))))
            self.labels.append((self.plot_reference_a2, self.tr("Second reinvestment average purchase point ({})".format(c(self.price_a2)))))
            self.labels.append((self.plot_reference_b2, self.tr("Second reinvestment purchase point ({})".format(c(self.price_b2)))))
            self.labels.append((self.plot_reference_s3, self.tr("Third reinvestment selling point ({})".format(c(self.price_s3)))))
            self.labels.append((self.plot_reference_a3, self.tr("Third reinvestment average purchase point ({})".format(c(self.price_a3)))))
            self.labels.append((self.plot_reference_b3, self.tr("Third reinvestment purchase point ({})".format(c(self.price_b3)))))

        
    @pyqtSlot()
    def on_wheelEvent(self, event):
        now=self.mem.localzone.now()
        if event.button=='up':
            self.from_dt=self.from_dt+datetime.timedelta(days=365)
        else:
            self.from_dt=self.from_dt-datetime.timedelta(days=365)
        if self.from_dt>now-datetime.timedelta(days=365):
            self.from_dt=now-datetime.timedelta(days=365)
            QApplication.beep()
        self.mydraw()

    def on_customContextMenuRequested(self, pos):
        menu=QMenu()
        menu.addAction(self.actionSMA50)
        menu.addAction(self.actionSMA200)
        menu.exec_(self.mapToGlobal(pos)) 

    def draw_lines_from_ohcl(self):
        """self.setdata es un SetOHCLDaily"""
        self.ax.clear()
        if self.setdata.length()<2:
            return
            
        dates=[]
        quotes=[]
        for ohcl in self.setdata.arr:
            dt=ohcl.datetime()
            if dt>self.from_dt:
                dates.append(dt)
                quotes.append(ohcl.close)

        self.get_locators()
        self.ax.plot_date(dates, quotes, '-')
        self.draw_sma50(dates, quotes)
        self.draw_sma200(dates, quotes)

    def showLegend(self):
        """Alterna mostrando y desmostrando legend, empieza con sí"""
        self.makeLegend()
                
        if self.ax.legend_==None:
            (plots, labels)=zip(*self.labels)
            self.ax.legend( plots, labels, loc="best")
        else:
            self.ax.legend_=None
        self.draw()

    def mouseReleaseEvent(self,  event):
        self.showLegend()

    def get_locators(self):
        interval=(self.mem.localzone.now()-self.from_dt).days+1
        
        if interval<365:
            self.ax.xaxis.set_minor_locator(MonthLocator())
            self.ax.xaxis.set_major_locator(MonthLocator())
            self.ax.xaxis.set_major_formatter( DateFormatter('%Y-%m-%d'))   
        elif interval>=365:
            self.ax.xaxis.set_minor_locator(MonthLocator())
            self.ax.xaxis.set_major_locator(YearLocator())   
            self.ax.xaxis.set_major_formatter( DateFormatter('%Y'))        
                        
        self.ax.format_coord = self.footer  
        self.ax.grid(True)

    def load_data(self, product,  buyprice):
        """Debe tener cargado los ohcl, no el all"""
        self.product=product
        self.from_dt=self.product.result.ohclDaily.arr[0].datetime()
        self.price_buy=buyprice
        self.price_sell=None
        self.price_b1=None
        self.price_b2=None
        self.price_b3=None
        self.price_s1=None
        self.price_s2=None
        self.price_s3=None
        self.mydraw()

class canvasChartHistoricalReinvest(FigureCanvasQTAgg):
    def __init__(self, mem,   parent):
        self.mem=mem
        # setup Matplotlib Figure and Axis
        self.fig = Figure()
        FigureCanvasQTAgg.__init__(self, self.fig)
        # we define the widget as expandable
        FigureCanvasQTAgg.setSizePolicy(self,QSizePolicy.Expanding, QSizePolicy.Expanding)
        # notify the system of updated policy
        FigureCanvasQTAgg.updateGeometry(self)      
        self.ax= self.fig.add_subplot(111)
        self.plot_average=None
        self.plot_selling=None
        self.plot_purchases=None
        self.plot_sales=None
        self.plot_new_average=None
        self.plot_new_selling=None
        self.from_dt=self.mem.localzone.now()-datetime.timedelta(days=365)#Show days from this date
        
        self.purchase_type=None#None ninguno 0 con reinversión personalizada, 1 con reinversión dinero invertido, 2 con reinversión dinero invertido x2 y 3 con reinversion dinero invertido x1.5 

        self.labels=[]#Array de tuplas (plot,label)

        QMetaObject.connectSlotsByName(self)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.fig.canvas.mpl_connect('scroll_event', self.on_wheelEvent)

    def footer(self, date, y): 
        dt=num2date(date)
        dat=dt.date()
        try:
            return self.tr("{}: {}.".format(dat, self.investment.product.currency.string(self.setdata.find(dat).close)))
        except:
            return "Not found"


    def makeLegend(self):
        if len(self.labels)==0:
            self.labels.append((self.plot_selling, self.tr("Selling price: {}".format(self.investment.product.currency.string(self.sellprice)))))
            self.labels.append((self.plot_average, self.tr("Average purchase price: {}".format(self.investment.op_actual.average_price(type=1)))))
            self.labels.append((self.plot_purchases, self.tr("Purchase point")))
            self.labels.append((self.plot_sales, self.tr("Sales point")))
            self.labels.append((self.plot_new_selling, self.tr("New selling reference: {}".format(self.investment.product.currency.string(self.newsellprice)))))
            self.labels.append((self.plot_new_average, self.tr("New purchase average: {}".format(self.setcurrent.average_price(type=1)))))

    def draw_newPurchaseReferences(self):
        percentage=Decimal(self.mem.settingsdb.value("frmSellingPoint/lastgainpercentage",  5))
        (dat, average, sell)=([], [], [])                
        dat.append(self.setcurrent.arr[0].datetime)
        dat.append(datetime.datetime.now())
        avg=self.setcurrent.average_price().amount
        self.newsellprice=avg*(1+percentage/Decimal(100))
        
        average.append(avg)
        average.append(avg)
        sell.append(self.newsellprice)
        sell.append(self.newsellprice)
        self.plot_new_average, =self.ax.plot_date(dat, average, '-',  color='orange')     
        self.plot_new_selling, =self.ax.plot_date(dat, sell, '-',  color='darkblue')          
        
        #Prepare bottom label
        gains=(self.newsellprice-avg)*self.setcurrent.acciones()
        self.ax.annotate(xy=(5, 5), xycoords="figure pixels",  s=self.tr("Gains percentage: {} %. Gains in the new selling reference: {}".format(percentage, self.investment.product.currency.string(gains))))

        
    @pyqtSlot()
    def on_wheelEvent(self, event):
        now=self.mem.localzone.now()
        if event.button=='up':
            self.from_dt=self.from_dt+datetime.timedelta(days=365)
        else:
            self.from_dt=self.from_dt-datetime.timedelta(days=365)
        if self.from_dt>now-datetime.timedelta(days=365):
            self.from_dt=now-datetime.timedelta(days=365)
            QApplication.beep()
        self.mydraw()
        


    def draw_investment_operations(self):
        """Draws an horizontal line with the selling point price"""
        if self.setop.length()>0:
            dates_p=[]#purchase
            quotes_p=[]
            dates_s=[]#sales
            quotes_s=[]
            for o in self.setop.arr:
                if o.datetime>=self.from_dt:
                    if o.acciones>=0:
                        dates_p.append(o.datetime.date())
                        quotes_p.append(o.valor_accion)
                    else:
                        dates_s.append(o.datetime.date())
                        quotes_s.append(o.valor_accion)
            self.plot_purchases, =self.ax.plot_date(dates_p, quotes_p, 'bo', color="green",  tz=pytz.timezone(self.mem.localzone.name))
            self.plot_sales, =self.ax.plot_date(dates_s, quotes_s, 'bo', color="red",  tz=pytz.timezone(self.mem.localzone.name)) 

    def draw_purchaseReferences(self):
        """Draws an horizontal line with the average purchase price"""
        (dates, buy, sell)=([], [], [])                
        dates.append(self.from_dt-datetime.timedelta(days=7))#To see more margin
        dates.append(datetime.date.today()+datetime.timedelta(days=7))
        average=self.investment.op_actual.average_price().amount
        buy.append(average)
        buy.append(average)
        percentage=Decimal(self.mem.settingsdb.value("frmSellingPoint/lastgainpercentage",  5))
        self.sellprice=average*(1+percentage/Decimal(100))
        sell.append(self.sellprice)
        sell.append(self.sellprice)
        self.plot_average, =self.ax.plot_date(dates, buy, 'r--', color="orange",  tz=pytz.timezone(self.mem.localzone.name))
        self.plot_selling, =self.ax.plot_date(dates, sell, 'r--', color="darkblue",  tz=pytz.timezone(self.mem.localzone.name))

    def draw_lines_from_ohcl(self):
        """self.setdata es un SetOHCLDaily"""
        self.ax.clear()
        if self.setdata.length()<2:
            return
            
        self.get_locators()
        self.ax.plot_date(self.setdata.datetimes(self.from_dt), self.setdata.closes(self.from_dt), '-')
        self.draw()


    def showLegend(self):
        """Alterna mostrando y desmostrando legend, empieza con sí"""
        self.makeLegend()
                
        if self.ax.legend_==None:
            (plots, labels)=zip(*self.labels)
            self.ax.legend( plots, labels, loc="best")
        else:
            self.ax.legend_=None
        self.draw()

    def mouseReleaseEvent(self,  event):
        self.showLegend()

    def get_locators(self):
        interval=(self.mem.localzone.now()-self.from_dt).days+1
        
        if interval<365:
            self.ax.xaxis.set_minor_locator(MonthLocator())
            self.ax.xaxis.set_major_locator(MonthLocator())
            self.ax.xaxis.set_major_formatter( DateFormatter('%Y-%m-%d'))
        elif interval>=365:
            self.ax.xaxis.set_minor_locator(MonthLocator())
            self.ax.xaxis.set_major_locator(YearLocator())   
            self.ax.xaxis.set_major_formatter( DateFormatter('%Y'))        
                        
        self.ax.format_coord = self.footer  
        self.ax.grid(True)

    def load_data_reinvest(self,  inversion, setop, setcurrent):
        """
            setop es el SetInvestmentOperation simulado
            segcurrent es SetInvestmentOperationCurrent simulado
        """
        self.setcurrent=setcurrent
        self.setop=setop
        self.investment=inversion
        if self.investment.op_actual.length()>0:
            self.from_dt=day_start(self.investment.op_actual.first().datetime, self.mem.localzone)
        self.mydraw()
                
    def mydraw(self):
        self.setdata=self.investment.product.result.ohclDaily
        self.draw_lines_from_ohcl()
        self.draw_investment_operations()
        self.draw_purchaseReferences()
        self.draw_newPurchaseReferences()
        self.ax.set_ylabel(self.tr("{} quotes ({})".format(self.investment.product.name, self.investment.product.currency.symbol)))
        self.ax.set_title(self.tr("Reinvest graph"), fontsize=30, fontweight="bold", y=1.02)
        self.showLegend() 
        self.draw()
