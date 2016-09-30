from PyQt5.QtCore import *
from PyQt5.QtGui import *
from libxulpymoney import *
from matplotlib.finance import *
from decimal import Decimal
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.dates import MonthLocator, YearLocator, HourLocator,  DateFormatter,  num2date
from matplotlib.figure import Figure

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


class canvasChartIntraday(FigureCanvasQTAgg):
    def __init__(self, mem,  parent):
        # setup Matplotlib Figure and Axis
        self.fig = Figure()
        FigureCanvasQTAgg.__init__(self, self.fig)
        # we define the widget as expandable
        FigureCanvasQTAgg.setSizePolicy(self,QSizePolicy.Expanding, QSizePolicy.Expanding)
        # notify the system of updated policy
        FigureCanvasQTAgg.updateGeometry(self)        
        
        self.ax = self.fig.add_subplot(111)
        
        self.mem=mem

    def get_locators(self):
        self.ax.set_title(self.tr("Intraday graph"), fontsize=30, fontweight="bold", y=1.02)
        self.ax.xaxis.set_major_locator(HourLocator(interval=1 , tz=pytz.timezone(self.mem.localzone.name)))
        self.ax.xaxis.set_minor_locator(HourLocator(interval=1 , tz=pytz.timezone(self.mem.localzone.name)))
        self.ax.xaxis.set_major_formatter(DateFormatter('%H:%M'))    
        self.ax.fmt_xdata=DateFormatter('%H:%M')        

        self.ax.fmt_ydata = self.price  
        self.ax.grid(True)

    def updateData(self, product, setquotesintraday):
        """Loads a SetQuotesIntraday"""
        self.product=product
        self.setquotesintraday=setquotesintraday
        
        if self.setquotesintraday.length()<2:
            return

        self.ax.clear()
        self.get_locators()
        self.ax.plot_date(self.setquotesintraday.datetimes(), self.setquotesintraday.quotes(), '-',  tz=pytz.timezone(self.mem.localzone.name),  label=self.product.name)        
        self.ax.set_ylabel(self.tr("{} quotes ({})".format(self.product.name, self.product.currency.symbol)))
        self.ax.set_xlabel("{}".format(self.setquotesintraday.date))
        self.draw()
        
    def price(self, x): 
        return self.product.currency.string(x)

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
        self.plot_reference_buy=None
        self.plot_reference_sell=None
        self.plot_reference_1=None
        self.plot_reference_2=None
        self.plot_reference_3=None
        self.plot_reference_4=None
        self.plot_reference_5=None
        self.from_dt=self.mem.localzone.now()-datetime.timedelta(days=365)#Show days from this date
        
        self.purchase_type=None#None ninguno 0 con reinversi´on personalizada, 1 con reinversi´on dinero invertido, 2 con reinversi´on dinero invertido x2 y 3 con reinversion dinero invertido x1.5 

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
        
        self.actionPurchaseReferences=QAction(self)
        self.actionPurchaseReferences.setText(self.tr("Show purchase references"))
        self.actionPurchaseReferences.setObjectName("actionPurchaseReferences")
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

    @pyqtSlot()
    def on_actionPurchaseReferences_triggered(self):
        #self.mem.settings.setValue("canvasHistorical/sma50",   self.actionSMA50.isChecked())
        self.purchase_type=2
        self.mydraw()

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
            self.labels.append((self.plot_reference_buy, self.tr("Purchase references")))

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

    def draw_purchaseReferences(self, datime, quotes):
        if not self.purchase_type:
            return
        """Es un porcentaje  de disminuci´on haciendo compras de capital x2
        Si compro a 20 luego compro el doble a un -33% me queda de media todo 15.06 que es un 15.06/20 0.753%
        """
        percentages2=[0.753, 0.5185, 0.3495, 0.23464]
        
#        input=QInputDialog.getText(self,  "Xulpymoney",  self.tr("Please introduce an amount"))
#        if input[1]==True:
#            try:
#                amount=Decimal(input[0])
#            except:
#                qmessagebox(self.tr("Amount is not a number"))
#                return
        percentage=Decimal(self.mem.settingsdb.value("frmSellingPoint/lastgainpercentage",  5))
        if self.inversion==None:
            if self.purchase_type==2:
                (dat, buy, sell, r1, r2, r3, r4)=([], [], [], [], [], [], [])                
                dat.append(datime[0])
                dat.append(datime[len(datime)-1])
                buy.append(quotes[len(quotes)-1])
                buy.append(quotes[len(quotes)-1])
                sell.append(buy[0]*(1+percentage/Decimal(100)))
                sell.append(buy[0]*(1+percentage/Decimal(100)))
                r1.append(buy[0]*Decimal(percentages2[0])*(1+percentage/Decimal(100)))
                r1.append(buy[0]*Decimal(percentages2[0])*(1+percentage/Decimal(100)))
                r2.append(buy[0]*Decimal(percentages2[1])*(1+percentage/Decimal(100)))
                r2.append(buy[0]*Decimal(percentages2[1])*(1+percentage/Decimal(100)))
                r3.append(buy[0]*Decimal(percentages2[2])*(1+percentage/Decimal(100)))
                r3.append(buy[0]*Decimal(percentages2[2])*(1+percentage/Decimal(100)))
                r4.append(buy[0]*Decimal(percentages2[3])*(1+percentage/Decimal(100)))
                r4.append(buy[0]*Decimal(percentages2[3])*(1+percentage/Decimal(100)))

        print("Compro a {}. Vendo a {} que es un {} %".format(buy[0], buy[0]*(1+percentage/Decimal(100)), percentage))
        print("r1: punto medio compra {}. Vendo a {} que es un {}".format(buy[0]*Decimal(percentages2[0]),buy[0]*Decimal(percentages2[0])*(1+percentage/Decimal(100)) , percentage))
        print("r2: punto medio compra {}. Vendo a {} que es un {}".format(buy[0]*Decimal(percentages2[1]),buy[0]*Decimal(percentages2[1])*(1+percentage/Decimal(100)) , percentage))
        print("r3: punto medio compra {}. Vendo a {} que es un {}".format(buy[0]*Decimal(percentages2[2]),buy[0]*Decimal(percentages2[2])*(1+percentage/Decimal(100)) , percentage))
        print("r4: punto medio compra {}. Vendo a {} que es un {}".format(buy[0]*Decimal(percentages2[3]),buy[0]*Decimal(percentages2[3])*(1+percentage/Decimal(100)) , percentage))
        self.plot_reference_sell, =self.ax.plot_date(dat, sell, '-.',  color='green')     
        self.plot_reference_buy, =self.ax.plot_date(dat, buy, '-.',  color='orange')     
        self.plot_reference_1, =self.ax.plot_date(dat, r1, '-.',  color='red')     
        self.plot_reference_2, =self.ax.plot_date(dat, r2, '-.',  color='red')     
#        self.plot_reference_3, =self.ax.plot_date(dat, r3, '-.',  color='red')     
#        self.plot_reference_4, =self.ax.plot_date(dat, r4, '-.',  color='red')     
        
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
        if self.inversion==None:
            return
        if self.inversion.venta!=0:
            dates=[]
            quotes=[]
            dates.append(self.from_dt-datetime.timedelta(days=7))#To see more margin
            dates.append(datetime.date.today()+datetime.timedelta(days=7))
            quotes.append(self.inversion.venta)
            quotes.append(self.inversion.venta)
            self.plot_selling, =self.ax.plot_date(dates, quotes, 'r--', color="darkblue",  tz=pytz.timezone(self.mem.localzone.name)) #fijarse en selling, podría ser sin ella selling[0]

    def draw_investment_operations(self):
        """Draws an horizontal line with the selling point price"""
        if self.inversion==None:
            return
        if self.inversion.op.length()>0:
            dates_p=[]#purchase
            quotes_p=[]
            dates_s=[]#sales
            quotes_s=[]
            for o in self.inversion.op.arr:
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
        if self.inversion==None:
            return
        dates=[]
        quotes=[]
        dates.append(self.from_dt-datetime.timedelta(days=7))#To see more margin
        dates.append(datetime.date.today()+datetime.timedelta(days=7))
        average=self.inversion.op_actual.valor_medio_compra()
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
        menu.addSeparator()
        menu.addAction(self.actionPurchaseReferences)
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
        self.draw_purchaseReferences(dates, quotes)
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
        self.draw_purchaseReferences(datetimes, quotes)
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
        self.inversion=inversion
        if self.inversion!=None:
            if self.inversion.op_actual.length()>0:
                self.from_dt=day_start(self.inversion.op_actual.datetime_first_operation(), self.mem.localzone)
        self.sd=SD#Sin descontar dividends, es decir sumará los dividends a las quotes.
        self.mydraw()
