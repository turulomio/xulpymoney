from PyQt4.QtCore import *
from PyQt4.QtGui import *
from libxulpymoney import *
from matplotlib.finance import *
from decimal import Decimal
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.dates import *
from matplotlib.pyplot import *
# Matplotlib Figure object
from matplotlib.figure import Figure

class ChartType:
    lines=0
    ohcl=1
    candles=2

class canvasChart(FigureCanvas):
    """
        RECIBE DATOS DE LA FORMA DATETIME,VALUE
    
    Class to represent the FigureCanvas widget
    type 0:lineas
            since: datetime desde el que mostrar datos
            period: forma en que se muestran 0:5 minutos, 1: 15 minutos, 2:1 hora,3:diario,4:semanal,5 mensual

    Se crea el objeto
    objeto.settings
    objeto.load_data"""
    def __init__(self, parent):
        # setup Matplotlib Figure and Axis
        self.fig = Figure()
        FigureCanvas.__init__(self, self.fig)
        # we define the widget as expandable
        FigureCanvas.setSizePolicy(self,QSizePolicy.Expanding, QSizePolicy.Expanding)
        # notify the system of updated policy
        FigureCanvas.updateGeometry(self)        
        
        self.ax = self.fig.add_subplot(111)
        
        self.plot_sma200=None
        self.plot_sma50=None
 
    def price(self, x): 
        return self.investment.currency.string(x)

    def settings(self, section):		
        self.section=section
        self.actionSMA50.setChecked(str2bool(self.cfg.config_ui.get_value(section, "sma50" )))
        self.actionSMA200.setChecked(str2bool(self.cfg.config_ui.get_value(section, "sma200" )))           

    @pyqtSignature("")
    def on_actionSMA50_activated(self):
        self.cfg.config_ui.set_value(self.section, "sma50",   self.actionSMA50.isChecked())
        self.cfg.config_ui.save()
        
    @pyqtSignature("")
    def on_actionSMA200_activated(self):
        self.cfg.config_ui.set_value(self.section, "sma200",   self.actionSMA200.isChecked())
        self.cfg.config_ui.save()

    def draw_sma50(self,  datime, quotes):
        #Calculamos según
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


        
    def get_locators(self, first,  last,  count):
        if count==0:
            return
        interval=(last-first).days
        if interval==0:
            self.ax.xaxis.set_major_locator(HourLocator(interval=1 , tz=pytz.timezone(self.cfg.localzone.name)))
            self.ax.xaxis.set_minor_locator(HourLocator(interval=1 , tz=pytz.timezone(self.cfg.localzone.name)))
            self.ax.xaxis.set_major_formatter(DateFormatter('%H:%M'))    
            self.ax.fmt_xdata=DateFormatter('%H:%M')        
        elif interval<365:
            self.ax.xaxis.set_minor_locator(MonthLocator())
            self.ax.xaxis.set_major_locator(MonthLocator())
            self.ax.xaxis.set_major_formatter( DateFormatter('%Y-%m-%d'))   
            self.ax.fmt_xdata=DateFormatter('%Y-%m-%d')
        elif interval>=365:
            self.ax.xaxis.set_minor_locator(MonthLocator())
            self.ax.xaxis.set_major_locator(YearLocator())   
            self.ax.xaxis.set_major_formatter( DateFormatter('%Y'))        
            self.ax.fmt_xdata=DateFormatter('%Y')
                        
        self.ax.fmt_ydata = self.price  
        self.ax.grid(True)
        
    def draw_lines_from_ohcl(self, data):
        """Aquí  data es un array de OHCL"""
        self.ax.clear()      
        dates=[]
        quotes=[]
        for ohcl in data:
            dates.append(ohcl.datetime())
            quotes.append(ohcl.close)

        self.get_locators(dates[0],  dates[len(dates)-1], len(dates))
        self.ax.plot_date(dates, quotes, '-')
        self.draw_sma50(dates, quotes)
        self.draw_sma200(dates, quotes)
        self.draw()
        
    def draw_lines_from_quotes(self, data):
        """Deben estar con tz, se recibe data porque puede recortarese según zoom"""
        self.ax.clear()
        (datetimes, quotes)=([], [])
        for q in data:
            datetimes.append(q.datetime)
            quotes.append(q.quote)

        self.get_locators(datetimes[0],  datetimes[len(datetimes)-1], len(datetimes))
        self.ax.plot_date(datetimes, quotes, '-',  tz=pytz.timezone(self.cfg.localzone.name))
        
        self.draw_sma50(datetimes, quotes)
        self.draw_sma200(datetimes, quotes)
        self.draw()

        
    def ohcl(self, ohcldata,  interval):
        self.ax.clear()
        quotes=[]
        dates=[]
        close=[]
        self.get_locators(ohcldata[0].datetime(),  ohcldata[len(ohcldata)-1].datetime(), len(ohcldata))
        for d in ohcldata:
            quotes.append((d.datetime().toordinal(), d.open, d.close,  d.high, d.low))         #ESTE ES EL CAUSEANTE NO SE VEA MENOR DE DIARIO TOOARDIANL
            dates.append(d.datetime())
            close.append(d.close)
        self.ax.fmt_xdata = DateFormatter('%Y-%m-%d')
        left=ohcldata[0].datetime().toordinal()-interval.days#De margen
        right=ohcldata[len(ohcldata)-1].datetime().toordinal()+interval.days
        self.ax.set_xlim(left, right)
        plot_day_summary(self.ax, quotes,  ticksize=4)
        self.draw_sma50(dates, close)
        self.draw_sma200(dates, close)

    def candles(self, interval):
        """Interval 0.05 5minutos
        1 1 dia"""
        self.ax.clear()
#        self.data=self.format_data(6, interval)

        quotes=[]
        for d in self.data:
            quotes.append((d[0].toordinal(), d[1], d[2], d[3], d[4]))


        # format the coords message box
        self.ax.fmt_xdata = DateFormatter('%Y-%m-%d')
        self.ax.fmt_ydata = self.price
        self.ax.grid(True)
        candlestick(self.ax,quotes,   width=0.6)
        self.ax.xaxis_date()


    def common_actions(self):
        self.actionSMA50=QAction(self)
        self.actionSMA50.setText(self.trUtf8("Media móvil simple 50"))
        self.actionSMA50.setCheckable(True)
        self.actionSMA50.setObjectName(self.trUtf8("actionSMA50"))
        self.actionSMA200=QAction(self)
        self.actionSMA200.setText(self.trUtf8("Media móvil simple 200"))
        self.actionSMA200.setCheckable(True)
        self.actionSMA200.setObjectName(self.trUtf8("actionSMA200"))
        
        self.actionLines5m=QAction(self)
        self.actionLines5m.setText(self.trUtf8("5 minutos"))
        self.actionLines5m.setObjectName(self.trUtf8("actionLines5m"))
        self.actionLines5m.setEnabled(False)
        self.actionLines10m=QAction(self)
        self.actionLines10m.setText(self.trUtf8("10 minutos"))
        self.actionLines10m.setObjectName(self.trUtf8("actionLines10m"))
        self.actionLines10m.setEnabled(False)
        self.actionLines30m=QAction(self)
        self.actionLines30m.setText(self.trUtf8("30 minutos"))
        self.actionLines30m.setObjectName(self.trUtf8("actionLines30m"))
        self.actionLines30m.setEnabled(False)
        self.actionLines60m=QAction(self)
        self.actionLines60m.setText(self.trUtf8("1 hora"))
        self.actionLines60m.setObjectName(self.trUtf8("actionLines60m"))
        self.actionLines60m.setEnabled(False)
        
        
        self.actionOHCL5m=QAction(self)
        self.actionOHCL5m.setText(self.trUtf8("5 minutos"))
        self.actionOHCL5m.setObjectName(self.trUtf8("actionOHCL5m"))
        self.actionOHCL5m.setEnabled(False)
        self.actionOHCL10m=QAction(self)
        self.actionOHCL10m.setText(self.trUtf8("10 minutos"))
        self.actionOHCL10m.setEnabled(False)
        self.actionOHCL10m.setObjectName(self.trUtf8("actionOHCL10m"))
        self.actionOHCL30m=QAction(self)
        self.actionOHCL30m.setText(self.trUtf8("30 minutos"))
        self.actionOHCL30m.setEnabled(False)
        self.actionOHCL30m.setObjectName(self.trUtf8("actionOHCL30m"))
        self.actionOHCL60m=QAction(self)
        self.actionOHCL60m.setText(self.trUtf8("1 hora"))
        self.actionOHCL60m.setEnabled(False)
        self.actionOHCL60m.setObjectName(self.trUtf8("actionOHCL60m"))
        
        self.actionCandles5m=QAction(self)
        self.actionCandles5m.setText(self.trUtf8("5 minutos"))
        self.actionCandles5m.setEnabled(False)
        self.actionCandles5m.setObjectName(self.trUtf8("actionCandles5m"))
        self.actionCandles10m=QAction(self)
        self.actionCandles10m.setText(self.trUtf8("10 minutos"))
        self.actionCandles10m.setEnabled(False)
        self.actionCandles10m.setObjectName(self.trUtf8("actionCandles10m"))
        self.actionCandles30m=QAction(self)
        self.actionCandles30m.setText(self.trUtf8("30 minutos"))
        self.actionCandles30m.setEnabled(False)
        self.actionCandles30m.setObjectName(self.trUtf8("actionCandles30m"))
        self.actionCandles60m=QAction(self)
        self.actionCandles60m.setText(self.trUtf8("1 hora"))
        self.actionCandles60m.setEnabled(False)
        self.actionCandles60m.setObjectName(self.trUtf8("actionCandles60m"))
        
        self.labels=[]#Array de tuplas (plot,label)

        
        QMetaObject.connectSlotsByName(self)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.connect(self,SIGNAL('customContextMenuRequested(QPoint)'), self.on_customContextMenuRequested)

    def showLegend(self):
        """Alterna mostrando y desmostrando legend, empieza con sí"""
        self.makeLegend()
                
        if self.ax.legend_==None:
            (plots, labels)=zip(*self.labels)
            self.ax.legend(plots, labels, "upper left")
        else:
            self.ax.legend_=None
        self.draw()

    def mouseReleaseEvent(self,  event):
        self.showLegend()

class canvasChartIntraday(canvasChart):
    def __init__(self, cfg,  parent):
        self.cfg=cfg
        canvasChart.__init__(self, parent)
        self.setupUi()
        self.settings("canvasIntraday")

    def load_data_intraday(self, investment):
        """Needs basic e Intraday"""
        self.investment=investment
        self.draw_lines_from_quotes(self.investment.result.intradia.arr)
    
    def on_actionLinesIntraday_activated(self):
        self.cfg.config_ui.set_value(self.section, "type",   ChartType.lines)
        (dates, quotes)=zip(*self.data)
        self.draw_lines_from_quotes(dates, quotes)

       
    def on_customContextMenuRequested(self, pos):
        menu=QMenu()
        ohcl=QMenu("OHCL")
        ohcl.addAction(self.actionOHCL5m)
        ohcl.addAction(self.actionOHCL10m)
        ohcl.addAction(self.actionOHCL30m)
        ohcl.addAction(self.actionOHCL60m)
        menu.addMenu(ohcl)        
        lines=QMenu("Líneas")
        lines.addAction(self.actionLinesIntraday)
        lines.addAction(self.actionLines5m)
        lines.addAction(self.actionLines10m)
        lines.addAction(self.actionLines30m)
        lines.addAction(self.actionLines60m)
        menu.addMenu(lines)        
        candles=QMenu("Candles")
        candles.addAction(self.actionCandles5m)
        candles.addAction(self.actionCandles10m)
        candles.addAction(self.actionCandles30m)
        candles.addAction(self.actionCandles60m)
        menu.addMenu(candles)        
        menu.addSeparator()
        indicadores=QMenu("Indicadores")
        indicadores.addAction(self.actionSMA50)
        indicadores.addAction(self.actionSMA200)
        menu.addMenu(indicadores)            
        menu.exec_(self.mapToGlobal(pos))
        
    def setupUi(self):
        self.actionLinesIntraday=QAction(self)
        self.actionLinesIntraday.setText(self.trUtf8("Intradia"))
        self.actionLinesIntraday.setObjectName(self.trUtf8("actionLinesIntraday"))
        self.common_actions()
        
        
class canvasChartHistorical(canvasChart):
    def __init__(self, cfg,   parent):
        self.cfg=cfg
        canvasChart.__init__(self, parent)
        self.num=60#Numero de items a mostrar
        self.setupUi()
        self.data=None#Array de Datos to show, variará según ohclDaily, Monthly,, no se usa en Intradia, sale todo
        self.plot_average=None
        self.plot_selling=None
        self.settings("canvasHistorical")
    
    def makeLegend(self):
        if len(self.labels)==0:
            self.labels.append((self.plot_sma200,"SMA200"))
            self.labels.append((self.plot_sma50,"SMA50"))      
            self.labels.append((self.plot_selling, self.trUtf8("Selling price")))
            self.labels.append((self.plot_average, self.trUtf8("Average purchase price")))
            
    def setData(self, arr):
        if self.num<60:
            QApplication.beep()
            self.num=60
        elif self.num>=len(arr):
            QApplication.beep()
            self.num=len(arr)
        if self.sd==False:##Sin descontar dividendos, es decir sumando dividendos desde principio
            return arr[len(arr)-self.num:len(arr)]
        else:
            result=[]
            for a in arr[len(arr)-self.num:len(arr)]:
                o=a.clone()
                sum=self.investment.dps.sum(o.datetime().date())
                o.close=o.close+sum
                o.high=o.high+sum
                o.low=o.low+sum
                o.open=o.open+sum
                result.append(o)
            return result

    def mydraw(self):
        """Punto de entrada de inicio, cambio de rueda, """
        type=int(self.cfg.config_ui.get_value(self.section, "type"))
        interval=int(self.cfg.config_ui.get_value(self.section, "interval"))
        if type==ChartType.lines:
            if interval==1:
                self.on_actionLines1d_activated()
        elif type==ChartType.ohcl:
            if interval==1:
                self.on_actionOHCL1d_activated()
            if interval==7:
                self.on_actionOHCL7d_activated()
            if interval==30:
                self.on_actionOHCL30d_activated()
            if interval==365:
                self.on_actionOHCL365d_activated()
        elif type==ChartType.candles:
            self.on_actionCandles1d_activated()
        self.draw()


    def setupUi(self):
        self.actionLinesIntraday=QAction(self)
        self.actionLinesIntraday.setText(self.trUtf8("Intradia"))
        self.actionLinesIntraday.setObjectName(self.trUtf8("actionLinesIntraday"))
        
        self.actionLines1d=QAction(self)
        self.actionLines1d.setText(self.trUtf8("1 dia"))
        self.actionLines1d.setObjectName(self.trUtf8("actionLines1d"))
        self.actionLines7d=QAction(self)
        self.actionLines7d.setText(self.trUtf8("1 semana"))
        self.actionLines7d.setObjectName(self.trUtf8("actionLines7d"))
        self.actionLines7d.setEnabled(False)
        self.actionLines30d=QAction(self)
        self.actionLines30d.setText(self.trUtf8("1 mes"))
        self.actionLines30d.setObjectName(self.trUtf8("actionLines30d"))
        self.actionLines30d.setEnabled(False)
        self.actionLines365d=QAction(self)
        self.actionLines365d.setText(self.trUtf8("1 año"))
        self.actionLines365d.setObjectName(self.trUtf8("actionLines365d"))        
        self.actionLines365d.setEnabled(False)
        
        self.actionOHCL1d=QAction(self)
        self.actionOHCL1d.setText(self.trUtf8("1 dia"))
        self.actionOHCL1d.setObjectName(self.trUtf8("actionOHCL1d"))
        self.actionOHCL7d=QAction(self)
        self.actionOHCL7d.setText(self.trUtf8("1 semana"))
        self.actionOHCL7d.setObjectName(self.trUtf8("actionOHCL7d"))
        self.actionOHCL30d=QAction(self)
        self.actionOHCL30d.setText(self.trUtf8("1 mes"))
        self.actionOHCL30d.setObjectName(self.trUtf8("actionOHCL30d"))
        self.actionOHCL365d=QAction(self)
        self.actionOHCL365d.setText(self.trUtf8("1 año"))
        self.actionOHCL365d.setObjectName(self.trUtf8("actionOHCL365d"))
        
        self.actionCandles1d=QAction(self)
        self.actionCandles1d.setText(self.trUtf8("1 dia"))
        self.actionCandles1d.setEnabled(False)
        self.actionCandles1d.setObjectName(self.trUtf8("actionCandles1d"))
        self.actionCandles7d=QAction(self)
        self.actionCandles7d.setText(self.trUtf8("1 semana"))
        self.actionCandles7d.setEnabled(False)
        self.actionCandles7d.setObjectName(self.trUtf8("actionCandles7d"))
        self.actionCandles30d=QAction(self)
        self.actionCandles30d.setText(self.trUtf8("1 mes"))
        self.actionCandles30d.setEnabled(False)
        self.actionCandles30d.setObjectName(self.trUtf8("actionCandles30d"))
        self.actionCandles365d=QAction(self)
        self.actionCandles365d.setText(self.trUtf8("1 año"))
        self.actionCandles365d.setEnabled(False)
        self.actionCandles365d.setObjectName(self.trUtf8("actionCandles365d"))
        
        self.common_actions()
        self.fig.canvas.mpl_connect('scroll_event', self.on_wheelEvent)
        
    @pyqtSignature("")
    def on_wheelEvent(self, event):
        if event.button=='up':
            self.num=self.num-360 
        else:
            self.num=self.num+360
        self.mydraw()
        
    @pyqtSignature("")
    def on_actionOHCL1d_activated(self):
        self.cfg.config_ui.set_value(self.section, "type", ChartType.ohcl)
        self.cfg.config_ui.set_value(self.section, "interval",   "1")
        self.data=self.setData(self.investment.result.ohclDaily.arr)
        self.ohcl(self.data, datetime.timedelta(days=1))     
        self.draw_selling_point()
        self.draw_average_purchase_price()
        self.showLegend()

    @pyqtSignature("")
    def on_actionLines1d_activated(self):
        self.cfg.config_ui.set_value(self.section, "type",   ChartType.lines)
        self.cfg.config_ui.set_value(self.section, "interval",   "1")
        self.data=self.setData(self.investment.result.ohclDaily.arr)
        self.draw_lines_from_ohcl(self.data)     
        self.draw_selling_point()
        self.draw_average_purchase_price()
        self.showLegend()

    @pyqtSignature("")
    def on_actionCandles1d_activated(self):
        self.cfg.config_ui.set_value(self.section, "type",   ChartType.candles)
        self.cfg.config_ui.set_value(self.section, "interval",   "1")
        self.data=self.setData(self.investment.result.ohclDaily.arr)
        self.candles(datetime.timedelta(days=1))
        if len(self.data)<1000:
            self.ax.xaxis.set_minor_locator(DayLocator())
            self.ax.xaxis.set_major_locator(MonthLocator())
            self.ax.xaxis.set_major_formatter( DateFormatter('%Y-%m-%d'))   
        else:
            self.ax.xaxis.set_minor_locator(MonthLocator())
            self.ax.xaxis.set_major_locator(YearLocator())
        self.ax.autoscale_view()

    @pyqtSignature("")
    def on_actionOHCL7d_activated(self):
        self.cfg.config_ui.set_value(self.section, "type", ChartType.ohcl)
        self.cfg.config_ui.set_value(self.section, "interval",   "7")
        self.data=self.setData(self.investment.result.ohclWeekly.arr)
        self.ohcl(self.data, datetime.timedelta(days=7))     
        self.draw_selling_point()
        self.draw_average_purchase_price()
        self.showLegend()   

    @pyqtSignature("")
    def on_actionOHCL30d_activated(self):
        self.cfg.config_ui.set_value(self.section, "type", ChartType.ohcl)
        self.cfg.config_ui.set_value(self.section, "interval",   "30")
        self.data=self.setData(self.investment.result.ohclMonthly.arr)
        self.ohcl(self.data, datetime.timedelta(days=30))     
        self.draw_selling_point()
        self.draw_average_purchase_price()
        self.showLegend()   

    @pyqtSignature("")
    def on_actionOHCL365d_activated(self):
        self.cfg.config_ui.set_value(self.section, "type", ChartType.ohcl)
        self.cfg.config_ui.set_value(self.section, "interval",   "365")
        self.data=self.setData(self.investment.result.ohclYearly.arr)
        self.ohcl(self.data, datetime.timedelta(days=365))     
        self.draw_selling_point()
        self.draw_average_purchase_price()
        self.showLegend()   

    def draw_selling_point(self):
        """Draws an horizontal line with the selling point price"""
        if self.inversion==None:
            return
        if self.inversion.venta!=0 and len(self.data)>0:
            dates=[]
            quotes=[]
            dates.append(self.data[0].datetime().date()-datetime.timedelta(days=1))
            dates.append(datetime.date.today()+datetime.timedelta(days=1))
            quotes.append(self.inversion.venta)
            quotes.append(self.inversion.venta)
            self.plot_selling, =self.ax.plot_date(dates, quotes, 'r--', color="darkblue",  tz=pytz.timezone(self.cfg.localzone.name)) #fijarse en selling, podría ser sin ella selling[0]

        
        
    def draw_average_purchase_price(self):
        """Draws an horizontal line with the average purchase price"""
        if self.inversion==None:
            return
        if  len(self.data)>0:
            dates=[]
            quotes=[]
            dates.append(self.data[0].datetime().date()-datetime.timedelta(days=1))
            dates.append(datetime.date.today()+datetime.timedelta(days=1))
            average=self.inversion.op_actual.valor_medio_compra()
            quotes.append(average)
            quotes.append(average)
            self.plot_average, =self.ax.plot_date(dates, quotes, 'r--', color="orange",  tz=pytz.timezone(self.cfg.localzone.name))


    def on_customContextMenuRequested(self, pos):
        menu=QMenu()
        ohcl=QMenu("OHCL")
        ohcl.addAction(self.actionOHCL5m)
        ohcl.addAction(self.actionOHCL10m)
        ohcl.addAction(self.actionOHCL30m)
        ohcl.addAction(self.actionOHCL60m)
        ohcl.addAction(self.actionOHCL1d)
        ohcl.addAction(self.actionOHCL7d)
        ohcl.addAction(self.actionOHCL30d)
        ohcl.addAction(self.actionOHCL365d)
        menu.addMenu(ohcl)        
        lines=QMenu("Líneas")
        lines.addAction(self.actionLines5m)
        lines.addAction(self.actionLines10m)
        lines.addAction(self.actionLines30m)
        lines.addAction(self.actionLines60m)
        lines.addAction(self.actionLines1d)
        lines.addAction(self.actionLines7d)
        lines.addAction(self.actionLines30d)
        lines.addAction(self.actionLines365d)
        menu.addMenu(lines)        
        candles=QMenu("Candles")
        candles.addAction(self.actionCandles5m)
        candles.addAction(self.actionCandles10m)
        candles.addAction(self.actionCandles30m)
        candles.addAction(self.actionCandles60m)
        candles.addAction(self.actionCandles1d)
        candles.addAction(self.actionCandles7d)
        candles.addAction(self.actionCandles30d)
        candles.addAction(self.actionCandles365d)
        menu.addMenu(candles)        
        menu.addSeparator()
        indicadores=QMenu("Indicadores")
        indicadores.addAction(self.actionSMA50)
        indicadores.addAction(self.actionSMA200)
        menu.addMenu(indicadores)            
        menu.exec_(self.mapToGlobal(pos)) 

    def load_data(self, investment,   inversion=None, SD=False):
        """Debe tener cargado los ohcl, no el all"""
        self.investment=investment
        self.inversion=inversion
        self.sd=SD#Sin descontar dividendos, es decir sumará los dividendos a las quotes.
        self.mydraw()
