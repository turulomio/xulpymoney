from PyQt4.QtCore import *
from PyQt4.QtGui import *
from libxulpymoney import *
from matplotlib.finance import *
from decimal import Decimal
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.dates import *

# Matplotlib Figure object
from matplotlib.figure import Figure


class ChartType:
    lines=0
    ochl=1
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
        self.original=None#Almacena los datos originales
        self.currentMatrizDataLength=0#Almacena la longitud de los datos dibujados
        self.since=None #Muestra todos los datos
        self.periodo=None
        
#        self.num=540#Numéro de items a dibujar
        
        
        self.type=None
        
        self.ax = self.fig.add_subplot(111)
        
        #Para grabar settings
        self.inifile=None
        self.section=None
        
          
        
    def settings(self, section,  inifile):		
        """Esta funcion debe ejecutarse despues de haber creado las columnas"""
        self.inifile=inifile
        self.section=section

        #Crea seccion
        config = configparser.ConfigParser()
        config.read(self.inifile)
        if config.has_section(self.section)==False:
            config.add_section(self.section)
            with open(self.inifile, 'w') as configfile:
                config.write(configfile)        

        try:
            self.type=config.getint(section, "type" )
        except:
            self.type=ChartType.lines
            
        try:
            self.actionSMA50.setChecked(config.getboolean(section, "sma50" ))
        except:
            self.actionSMA50.setChecked(False)

        try:
            self.actionSMA200.setChecked(config.getboolean(section, "sma200" ))
        except:
            self.actionSMA200.setChecked(False)
            
#    def setCurrency(self, currency):
#        """Función que modifica el valor de la divisa por defecto es EUR (statics.Currencies)"""
#        self.currency=currency
        
#
#    def format_data(self,  columns, interval=None):
#        """Puede ser columns 2 o 6
#        Cuando es 6 hat que dar el valor al formato
#        parte de self.original
#        interval es un timedelta"""
#
#        
#        def to_ochl(tmp, puntdt):
#            """Función que recibe un array de la forma data2 y lo convierte a un registro de la forma data 6"""
#            if len(tmp)==0:
#                return None
#            dt=puntdt
#            first=tmp[0][1]
#            last=tmp[len(tmp)-1][1]
#            (datestimes, quotes)=zip(*tmp)
#            high=max(quotes)
#            low=min(quotes)
#            volumen=0
#            return (dt, first,  last, high,  low,  volumen)
#        
#        data=self.original
#        if len(data)==0:
#            return data
#            
#        if columns==2 and len(data[0])==2:
#            return data        
#        if columns==6 and len(data[0])==6:
#            return data
#        if columns==2 and len(data[0])==6:
#            resultado=[]
#            for d in data:
#                   #data.append((i['date'],  i['first'], i['last'],  i['high'], i['low'], 0))    
#                date=datetime.datetime(d[0].year, d[0].month, d[0].day)
#                resultado.append((date.replace(microsecond=1), d[1]))
#                resultado.append((date.replace(microsecond=4), d[1]))
#                resultado.append((date.replace(microsecond=3), d[1]))
#                resultado.append((date.replace(microsecond=2), d[1]))
#            return resultado
#        if columns==6 and len(data[0])==2:
#            resultado=[]
#            first=data[0][0]
#            last=data[len(data)-1][0]
##            diff=last-first
##            print(diff)
#            puntdt=first
#            while puntdt<=last:
#                tmp=[]
#                for d in data:
#                    if puntdt<=d[0] and d[0]<puntdt+interval:
#                        tmp.append(d)
#                        data.remove(d)
#                o=to_ochl(tmp, puntdt)
#                if o!=None:
#                    resultado.append(o)
##                    print (o)
#                puntdt=puntdt+interval
##            print (data)
##            print (puntdt)
#            return resultado




    def on_actionLinesIntraday_activated(self):
        self._settings_saveprop("type", self.type)
        (dates, quotes)=zip(*self.data)
        self._draw_lines_from_quotes(dates, quotes)
                

    def on_actionLines1d_activated(self):
        self._settings_saveprop("type", ChartType.lines)
        self.currentMatrizDataLength=len(self.result.ochlDaily)
        
        if len(self.result.ochlDaily)>self.num:              
            self._draw_lines_from_ochl(self.result.ochlDaily[len(self.result.ochlDaily)-1-self.num:len(self.result.ochlDaily)])      
        else:
            self._draw_lines_from_ochl(self.result.ochlDaily)     
#     
#        if len(self.result.ochlDaily)>self.num:             
#            dates, open, close, high,  low, volumen=zip(*self.result.ochlDaily[len(self.result.ochlDaily)-1-self.num:len(self.result.ochlDaily)])  
##            self.ochl(self.result.ochlDaily[len(self.result.ochlDaily)-1-self.num:len(self.result.ochlDaily)], datetime.timedelta(days=1))       
#        else:   
#            dates, open, close, high,  low, volumen=zip(*self.result.ochlDaily)
##            self.ochl(self.result.ochlDaily, datetime.timedelta(days=1))          

        self.draw()

    def _settings_saveprop(self, prop, value):
        config = configparser.ConfigParser()
        config.read(self.inifile)
        config.set(self.section,  prop, str(value))
        f=open(self.inifile, 'w')
        config.write(f)
        f.close()

        
        
        
    @pyqtSignature("")
    def on_actionSMA50_activated(self):
        self._settings_saveprop("sma50", self.actionSMA50.isChecked())
        self._draw()
                
        
    @pyqtSignature("")
    def on_actionSMA200_activated(self):
        self._settings_saveprop("sma200", self.actionSMA200.isChecked())
        self._draw()
        
        
    def _draw_sma50(self,  datime, quotes):
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
        self.ax.plot_date(dat, sma, '-',  color='gray')     
    
    def _draw_sma200(self, datime, quotes):
        if self.actionSMA200.isChecked()==False:
            return
        if len(quotes)<200:
            return
        dat=[]
        sma=[]
        for i in range(200, len(quotes)):
            dat.append(datime[i-1])
            sma.append(sum(quotes[i-200:i])/Decimal(200))
        self.ax.plot_date(dat, sma, '-', color="red")    


#    def _draw_lines_ochl(self):
#        return
        
        
    def _get_locators(self, first,  last,  count):
        if count==0:
            return
        interval=(last-first).days
#        print ("Interval get locators",  interval)
        if interval==0:
            self.ax.xaxis.set_major_locator(HourLocator(interval=1 , tz=pytz.timezone(config.localzone)))
            self.ax.xaxis.set_minor_locator(HourLocator(interval=1 , tz=pytz.timezone(config.localzone)))
            self.ax.xaxis.set_major_formatter(DateFormatter('%H:%M'))            
        elif interval<365:
            self.ax.xaxis.set_minor_locator(MonthLocator())
            self.ax.xaxis.set_major_locator(MonthLocator())
            self.ax.xaxis.set_major_formatter( DateFormatter('%Y-%m-%d'))   
        elif interval>=365:
            self.ax.xaxis.set_minor_locator(MonthLocator())
            self.ax.xaxis.set_major_locator(YearLocator())   
            self.ax.xaxis.set_major_formatter( DateFormatter('%Y'))        
            self.ax.fmt_xdata=DateFormatter('%Y-%m-%d')
            #[xmin, xmax, ymin, ymax].
#            print (self.ax.axis())
#            self.ax.axis([0.0, 0.5, 0.0, 0.5])
                        
        self.ax.fmt_ydata = self.price  
        self.ax.grid(True)
#        for tick in self.ax.xaxis.get_major_ticks():
#            tick.label.set_fontsize(9) 
#            tick.label.set_rotation('vertical')
#            
    def _draw_lines_from_ochl(self, data):
        """Aqu´i  data es un array de OCHL"""
        self.ax.clear()      
        dates=[]
        quotes=[]
        for ochl in data:
            dates.append(ochl.datetime)
            quotes.append(ochl.close)
#        for i in range(len(data)):
#            dates[i]=datetime.datetime.combine(dates[i], datetime.time(0, 0))

        self._get_locators(dates[0],  dates[len(dates)-1], len(dates))
        self.ax.plot_date(dates, quotes, '-')
        self._draw_sma50(dates, quotes)
        self._draw_sma200(dates, quotes)
        self.draw()
        
    def _draw_lines_from_quotes(self, data):
        """Deben estar con tz, se recibe data porque puede recortarese seg´un zoom"""
        self.ax.clear()
        (datetimes, quotes)=([], [])
        for q in data:
            datetimes.append(q.datetime)
            quotes.append(q.quote)

        self._get_locators(datetimes[0],  datetimes[len(datetimes)-1], len(datetimes))
        self.ax.plot_date(datetimes, quotes, '-',  tz=pytz.timezone(config.localzone))
        
        self._draw_sma50(datetimes, quotes)
        self._draw_sma200(datetimes, quotes)
        self.draw()

#    @pyqtSignature("")
#    def on_actionOCHL5m_activated(self):
#        print ("Una vez")
#        self.ochl(datetime.timedelta(minutes=5))
#
#        self.ax.xaxis.set_major_locator(HourLocator(interval=1 , tz=pytz.timezone(config.localzone)))
#        self.ax.xaxis.set_minor_locator(HourLocator(interval=1, tz=pytz.timezone(config.localzone)))
#        self.ax.xaxis.set_major_formatter(DateFormatter('%H:%M'))      
#        self.ax.autoscale_view()
#        self.ax.fmt_xdata = DateFormatter('%Y-%m-%d')
#        self.draw()
        
    @pyqtSignature("")
    def on_actionOCHL1d_activated(self):
        self._settings_saveprop("type", ChartType.ochl)
        self.currentMatrizDataLength=len(self.result.ochlDaily)
        
        if len(self.result.ochlDaily)>self.num:            
            self.ochl(self.result.ochlDaily[len(self.result.ochlDaily)-1-self.num:len(self.result.ochlDaily)], datetime.timedelta(days=1))       
        else:
            self.ochl(self.result.ochlDaily, datetime.timedelta(days=1))     
     
        self.draw()
                
#    @pyqtSignature("")
#    def on_actionOCHL30d_activated(self):
#        print ("Una vez")
#        self.ochl(datetime.timedelta(days=30))
#        if len(self.data)<60:
#            self.ax.xaxis.set_minor_locator(DayLocator())
#            self.ax.xaxis.set_major_locator(MonthLocator())
#            self.ax.xaxis.set_major_formatter( DateFormatter('%Y-%m-%d'))   
#        else:
#            self.ax.xaxis.set_minor_locator(MonthLocator())
#            self.ax.xaxis.set_major_locator(YearLocator())                    
#        self.ax.autoscale_view()
#        self.ax.fmt_xdata = DateFormatter('%Y-%m-%d')
#        self.draw()
        
    def ochl(self, ochldata,  interval):
        self.ax.clear()
            
#        dates, open,  close, high, low, volumen=zip(*ochldata)
        quotes=[]
        dates=[]
        close=[]
        self._get_locators(ochldata[0].datetime,  ochldata[len(ochldata)-1].datetime, len(ochldata))
        for d in ochldata:
            quotes.append((d.datetime.toordinal(), d.open, d.close,  d.high, d.low))         #ESTE ES EL CAUSEANTE NO SE VEA MENOR DE DIARIO TOOARDIANL
            dates.append(d.datetime)
            close.append(d.close)

#        self.ax.autoscale_view()
        self.ax.fmt_xdata = DateFormatter('%Y-%m-%d')
        left=ochldata[0].datetime.toordinal()-interval.days#De margen
        right=ochldata[len(ochldata)-1].datetime.toordinal()+interval.days
        self.ax.set_xlim(left, right)
        plot_day_summary(self.ax, quotes,  ticksize=4)
        self._draw_sma50(dates, close)
        self._draw_sma200(dates, close)

    @pyqtSignature("")
    def on_actionCandles1d_activated(self):
        self.candles(datetime.timedelta(days=1))
        if len(self.data)<1000:
            self.ax.xaxis.set_minor_locator(DayLocator())
            self.ax.xaxis.set_major_locator(MonthLocator())
            self.ax.xaxis.set_major_formatter( DateFormatter('%Y-%m-%d'))   
        else:
            self.ax.xaxis.set_minor_locator(MonthLocator())
            self.ax.xaxis.set_major_locator(YearLocator())
        self.ax.autoscale_view()
        self.__draw()
        
    def candles(self, interval):
        """Interval 0.05 5minutos
        1 1 dia"""
        self.ax.clear()
        self.data=self.format_data(6, interval)

        quotes=[]
        for d in self.data:
            quotes.append((d[0].toordinal(), d[1], d[2], d[3], d[4]))


        # format the coords message box
        self.ax.fmt_xdata = DateFormatter('%Y-%m-%d')
        self.ax.fmt_ydata = self.price
        self.ax.grid(True)
#                self.fig.autofmt_xdate()
        candlestick(self.ax,quotes,   width=0.6)
        self.ax.xaxis_date()


    def clear(self):
        self.ax.clear()
    

#        
#        
#    def is_intraday(self, data2):
#        first=data2[0][0].day
#        for d in data2:
#            if d[0].day!=first:
#                return False
#        return True        
#    def is_intramonth(self, data2):
#        first=data2[0][0].month
#        for d in data2:
#            if d[0].month!=first:
#                return False
#        return True
#        
#        
#    def quita_ochl(self, data):
#        resultado=[]
#        for d in self.data:
#            if d[0].microsecond in (1, 2, 3, 4):
#                continue
#            else:
#                resultado.append(d)
#        return resultado
        
#    def dibuja_ochl(self, data):
#        return
#    
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
        
        
        self.actionOCHL5m=QAction(self)
        self.actionOCHL5m.setText(self.trUtf8("5 minutos"))
        self.actionOCHL5m.setObjectName(self.trUtf8("actionOCHL5m"))
        self.actionOCHL5m.setEnabled(False)
        self.actionOCHL10m=QAction(self)
        self.actionOCHL10m.setText(self.trUtf8("10 minutos"))
        self.actionOCHL10m.setEnabled(False)
        self.actionOCHL10m.setObjectName(self.trUtf8("actionOCHL10m"))
        self.actionOCHL30m=QAction(self)
        self.actionOCHL30m.setText(self.trUtf8("30 minutos"))
        self.actionOCHL30m.setEnabled(False)
        self.actionOCHL30m.setObjectName(self.trUtf8("actionOCHL30m"))
        self.actionOCHL60m=QAction(self)
        self.actionOCHL60m.setText(self.trUtf8("1 hora"))
        self.actionOCHL60m.setEnabled(False)
        self.actionOCHL60m.setObjectName(self.trUtf8("actionOCHL60m"))
        
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
        
        QMetaObject.connectSlotsByName(self)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.connect(self,SIGNAL('customContextMenuRequested(QPoint)'), self.on_customContextMenuRequested)
#        self.connect(self, SIGNAL('wheelEvent(QWheelEvent'), self.on_wheelEvent)
#        self.connect(self.fig.canvas, SIGNAL('button_press_event), self.on_press)
#        cid = self.fig.canvas.mpl_connect('button_press_event', self.on_press)
#        
#    def on_press(self, event):
#        print ('you pressed', event.button, event.xdata, event.ydata)

# {
#     int numDegrees = event->delta() / 8;
#     int numSteps = numDegrees / 15;
#
#     if (event->orientation() == Qt.Horizontal) {
#         scrollHorizontally(numSteps);
#     } else {
#         scrollVertically(numSteps);
#     }
#     event->accept();
# }

class canvasChartIntraday(canvasChart):
    def __init__(self,  parent):
        canvasChart.__init__(self, parent)
        self.setupUi()
        

    def price(self, x): 
        """Se sobreescribe para mostrar el % de inicio"""
#        return '{0}{1}{2}'.format(round(x, 2), self.investment.currency.symbol,  (self.penultimate.quote-x)*100/self.penultimate.quote)
        return  (self.penultimate.quote-x)*100/self.penultimate.quote
        
    def load_data_intraday(self, investment,  dataintraday,  penultimate):
        self.data=dataintraday
        self.penultimate=penultimate
        self.investment=investment
        self._draw_lines_from_quotes(self.data)
        
    def on_customContextMenuRequested(self, pos):
        menu=QMenu()
        ochl=QMenu("OCHL")
        ochl.addAction(self.actionOCHL5m)
        ochl.addAction(self.actionOCHL10m)
        ochl.addAction(self.actionOCHL30m)
        ochl.addAction(self.actionOCHL60m)
        menu.addMenu(ochl)        
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
    
    def __init__(self,  parent):
        canvasChart.__init__(self, parent)
        self.num=50#Numero de items a mostrar
        self.setupUi()
        
    def __draw(self):
        if self.type==ChartType.lines:
            self.on_actionLines1d_activated()
        elif self.type==ChartType.ochl:
            self.on_actionOCHL1d_activated()
        elif self.type==ChartType.candles:
            self.on_actionCandles1d_activated()
            
           
    def price(self, x): 
        return '{0} {1}'.format(round(x, 2), self.investment.currency.symbol)
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
        
        self.actionOCHL1d=QAction(self)
        self.actionOCHL1d.setText(self.trUtf8("1 dia"))
        self.actionOCHL1d.setObjectName(self.trUtf8("actionOCHL1d"))
        self.actionOCHL7d=QAction(self)
        self.actionOCHL7d.setText(self.trUtf8("1 semana"))
        self.actionOCHL7d.setObjectName(self.trUtf8("actionOCHL7d"))
        self.actionOCHL30d=QAction(self)
        self.actionOCHL30d.setText(self.trUtf8("1 mes"))
        self.actionOCHL30d.setObjectName(self.trUtf8("actionOCHL30d"))
        self.actionOCHL365d=QAction(self)
        self.actionOCHL365d.setText(self.trUtf8("1 año"))
        self.actionOCHL365d.setObjectName(self.trUtf8("actionOCHL365d"))
        
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
        
    def on_wheelEvent(self, event):
#        print (event.button, event.step)
        if event.button=='up':
            self.num=self.num-120
        else:
            self.num=self.num+120
#        print (self.num)
        if self.num<50:
            QApplication.beep()
            self.num=50
            return
        elif self.num>=self.currentMatrizDataLength:
            QApplication.beep()
            self.num=self.currentMatrizDataLength
            return
        self.__draw()
#    figzoom.canvas.draw()
    @pyqtSignature("")
    def on_actionOCHL7d_activated(self):
        self._settings_saveprop("type", ChartType.ochl)
        ochlWeekly=self.result.ochlWeekly()
        self.currentMatrizDataLength=len(ochlWeekly)
        
        if len(ochlWeekly)>self.num:            
            self.ochl(ochlWeekly[len(ochlWeekly)-1-self.num:len(ochlWeekly)], datetime.timedelta(days=7))       
        else:
            self.ochl(ochlWeekly, datetime.timedelta(days=7))     
        self.draw()
    @pyqtSignature("")
    def on_actionOCHL30d_activated(self):
        self._settings_saveprop("type", ChartType.ochl)
        ochlMonthly=self.result.ochlMonthly()
        self.currentMatrizDataLength=len(ochlMonthly)
        
        if len(ochlMonthly)>self.num:            
            self.ochl(ochlMonthly[len(ochlMonthly)-1-self.num:len(ochlMonthly)], datetime.timedelta(days=30))       
        else:
            self.ochl(ochlMonthly, datetime.timedelta(days=30))     
        self.draw()
    @pyqtSignature("")
    def on_actionOCHL365d_activated(self):
        self._settings_saveprop("type", ChartType.ochl)
        ochlYearly=self.result.ochlYearly()
        self.currentMatrizDataLength=len(ochlYearly)
        
        if len(ochlYearly)>self.num:            
            self.ochl(ochlYearly[len(ochlYearly)-1-self.num:len(ochlYearly)], datetime.timedelta(days=365))       
        else:
            self.ochl(ochlYearly, datetime.timedelta(days=365))     
        self.draw()
        
    def on_customContextMenuRequested(self, pos):
        menu=QMenu()
        ochl=QMenu("OCHL")
        ochl.addAction(self.actionOCHL5m)
        ochl.addAction(self.actionOCHL10m)
        ochl.addAction(self.actionOCHL30m)
        ochl.addAction(self.actionOCHL60m)
        ochl.addAction(self.actionOCHL1d)
        ochl.addAction(self.actionOCHL7d)
        ochl.addAction(self.actionOCHL30d)
        ochl.addAction(self.actionOCHL365d)
        menu.addMenu(ochl)        
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

    def load_data(self, investment,  result):
        self.investment=investment
        self.result=result
        self.__draw()
