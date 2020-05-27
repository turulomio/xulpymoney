from PyQt5.QtCore import QObject
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QProgressDialog
from datetime import date, timedelta, datetime
from decimal import Decimal
from logging import debug, info, critical
from xulpymoney.datetime_functions import dt_day_end,  dtaware_day_start_from_date, string2dtaware
from  xulpymoney.libmanagers import ObjectManager
from xulpymoney.libxulpymoneytypes import   eHistoricalChartAdjusts, eQColor, eOHCLDuration
from xulpymoney.objects.money import Money
from xulpymoney.objects.percentage import Percentage, percentage_between
from xulpymoney.objects.ohcl import OHCLDailyManager, OHCLMonthlyManager, OHCLWeeklyManager, OHCLYearlyManager
## Class that represents a Quote
## A quote can be a datetime duplicated
class Quote:
    """Un quote no puede estar duplicado en un datetime solo puede haber uno"""
    def __init__(self, mem):
        self.mem=mem
        self.product=None
        self.quote=None
        self.datetime=None
        
    def __repr__(self):
        return "Quote de {} ({}) de fecha {} vale {}".format(self.product.name, self.product.id,  self.datetime, self.quote)
        
    def init__create(self,  product,  datetime,  quote):
        """Función que crea un Quote nuevo, con la finalidad de insertarlo
        quote must be a Decimal object."""
        self.product=product
        self.datetime=datetime
        self.quote=quote
        return self
        
    def exists(self):
        """Función que comprueba si existe en la base de datos y devuelve el valor de quote en caso positivo en una dupla""" 
        (status, reg)=(False, None)
        cur=self.mem.con.cursor()
        cur.execute("select quote from quotes where id=%s and  datetime=%s;", (self.product.id, self.datetime))
        if cur.rowcount!=0:
            reg=cur.fetchone()[0]
            status=True
        cur.close()
        return (status, reg)
        
        
    def can_be_saved(self):
        """Returns a boolean True if can be saved, debe usurse en los autokkmaticos. Puede haber algun manual que quiera ser 0"""
        r=True
        if self.quote==Decimal(0):
            r=False
        return r
        
    ## Returns a MOney Object
    def money(self):
        return Money(self.mem, self.quote, self.product.currency)
    
    def none(self, product):
        return self.init__create(product, None, None)

    def save(self):
        """Función que graba el quotes si coincide todo lo ignora. Si no coincide lo inserta o actualiza.
        No hace commit a la conexión
        Devuelve un número 1 si insert, 2 update, 3 ya  exisitia
        """
        r=None
        cur=self.mem.con.cursor()
        exists=self.exists()
        if exists[0]==False:
            cur.execute('insert into quotes (id, datetime, quote) values (%s,%s,%s)', ( self.product.id, self.datetime, self.quote))
            r=1
        else:
            if exists[1]!=self.quote:
                cur.execute("update quotes set quote=%s where id=%s and datetime=%s", (self.quote, self.product.id, self.datetime))
                r=2
            else: #ignored
                r=3
        cur.close()
        return r
                
    def delete(self):
        cur=self.mem.con.cursor()
        cur.execute("delete from quotes where id=%s and datetime=%s", (self.product.id, self.datetime))
        cur.close()

    def init__db_row(self, row, product):
        if row==None:
            return self.init__create(product, None, None)
        return self.init__create(product, row['datetime'], row['quote'])

    def init__from_query(self, product, dt): 
        """Función que busca el quote de un id y datetime con timezone"""
        cur=self.mem.con.cursor()
        cur.execute("select * from quote (%s,%s)", (product.id,  dt))
        row=cur.fetchone()
        cur.close()
        return self.init__db_row(row, product)
                
    def init__from_query_penultima(self,product,  lastdate=None):
        cur=self.mem.con.cursor()
        if lastdate==None:
            lastdate=date.today()
        cur.execute("select * from penultimate(%s,%s)", (product.id, lastdate ))
        row=cur.fetchone()
        cur.close()
        return self.init__db_row(row, product)

    def init__from_client_string(self, s):
        """
            Creates a Quote object from client scrapper line
            PRICE | XULPYMONEY | 78139 | 2017-11-20 23:00:00+00:00 | 12.66
        """
        try:
            a=s.split(" | ")
            self.product=self.mem.data.products.find_by_id(int(a[2]))
            if a[3].find(".")!=-1:#With microseconds
                self.datetime=string2dtaware(a[3], "%Y-%m-%d %H:%M:%S.%z")
            else:#Without microsecond
                self.datetime=string2dtaware(a[3], "%Y-%m-%d %H:%M:%S%z")
            self.quote=Decimal(a[4])
        except:
            return None
        return self

class QuoteManager(ObjectManager, QObject):
    """Clase que agrupa quotes un una lista arr. Util para operar con ellas como por ejemplo insertar, puede haber varios productos"""
    def __init__(self, mem):
        ObjectManager.__init__(self)
        QObject.__init__(self)
        self.mem=mem
    
    def save(self):
        """Recibe con code,  date,  time, value, zone
            Para poner el dato en close, el valor de time debe ser None
            Devuelve una tripleta (insertado,buscados,modificados)
        """
        insertados=QuoteManager(self.mem)
        ignored=QuoteManager(self.mem)
        modificados=QuoteManager(self.mem)    
        malos=QuoteManager(self.mem)
            
        for q in self.arr:
            if q.can_be_saved():#Debe hacerse en automaticos
                ibm=q.save()
                if ibm==1:
                    insertados.append(q)
                elif ibm==2:
                    modificados.append(q)
                elif ibm==3:
                    ignored.append(q)
            else:
                malos.append(q)
                
        debug ("Quotes: {} inserted, {} ignored, {} modified, {} errors".format(insertados.length(), ignored.length(), modificados.length(), malos.length()))
        return (insertados, ignored, modificados, malos)
        
    ## Return a product manager with added or updated quotes
    ## Usefull to reload just
    def change_products_status_after_save(self, added, updated, status, downgrade_to=None, progress=True):
        from xulpymoney.objects.product import ProductManager
        products=ProductManager(self.mem)
        for manager in [added, updated]:
            for quote in manager.arr:
                if quote.product not in products.arr:
                    products.append(quote.product)
        products.needStatus(status, downgrade_to=downgrade_to, progress=progress)
        self.mem.data.benchmark.needStatus(2) #If it's in products it has been downgraded
        self.mem.data.currencies.needStatus(3) #If it's in products it has been downgraded
        
    def addTo(self, settoadd):
        """Añade los quotes en array a un nuevo set paasado por parametro"""
        for q in self.arr:
            settoadd.append(q)

    def myqtablewidget(self, wdg):
        data=[]
        for rownumber, o in enumerate(self.arr):
            data.append([
                o.datetime, 
                o.product.name, 
                o.product.money(o.quote), 
                o
            ])
        wdg.setDataWithObjects(
            [self.tr("Date and time"), self.tr("Product"), self.tr("Price")], 
            None, 
            data, 
            zonename=self.mem.localzone_name, 
            additional=self.myqtablewidget_additional
        )
        
    def myqtablewidget_additional(self, wdg):
        for rownumber, o in enumerate(wdg.objects()):
            wdg.table.item(rownumber, 1).setIcon(o.product.stockmarket.country.qicon())
                
## Class that stores all kind of quotes asociated to a product
class QuotesResult:
    def __init__(self,mem,  product):
        self.mem=mem
        self.product=product

    def get_basic(self):
        self.basic=QuoteBasicManager(self.mem, self.product)
        self.basic.load_from_db()

    def get_intraday(self, date):
        self.intradia=QuoteIntradayManager(self.mem)
        self.intradia.load_from_db(date,  self.product)

    ## Function that generate all results and computes splits and dividends
    def get_ohcls(self):
        """Tambien sirve para recargar"""
        inicioall=datetime.now()  
                       
        # These are without splits nor dividends
        self.ohclDailyBeforeSplits=OHCLDailyManager(self.mem, self.product)
        self.ohclMonthlyBeforeSplits=OHCLMonthlyManager(self.mem, self.product)
        self.ohclYearlyBeforeSplits=OHCLYearlyManager(self.mem, self.product)
        self.ohclWeeklyBeforeSplit=OHCLWeeklyManager(self.mem, self.product)
        
        # These are with splits and without dividends
        self.ohclDaily=OHCLDailyManager(self.mem, self.product)
        self.ohclMonthly=OHCLMonthlyManager(self.mem, self.product)
        self.ohclYearly=OHCLYearlyManager(self.mem, self.product)
        self.ohclWeekly=OHCLWeeklyManager(self.mem, self.product)

        # These are with splits and dividends
        self.ohclDailyAfterDividends=OHCLDailyManager(self.mem, self.product)
        self.ohclMonthlyAfterDividends=OHCLMonthlyManager(self.mem, self.product)
        self.ohclYearlyAfterDividends=OHCLYearlyManager(self.mem, self.product)
        self.ohclWeeklyAfterDividends=OHCLWeeklyManager(self.mem, self.product)
        
        self.ohclDailyBeforeSplits.load_from_db("""
            select 
                id, 
                datetime::date as date, 
                (array_agg(quote order by datetime))[1] as first, 
                min(quote) as low, 
                max(quote) as high, 
                (array_agg(quote order by datetime desc))[1] as last 
            from quotes 
            where id={} 
            group by id, datetime::date 
            order by datetime::date 
            """.format(self.product.id))#necesario para usar luego ohcl_otros
            
        if self.product.splits.length()>0:
            self.ohclDaily=self.ohclDailyBeforeSplits.clone()
            self.ohclDaily=self.product.splits.adjustOHCLDailyManager(self.ohclDaily)
        else:
            self.ohclDaily=self.ohclDailyBeforeSplits
            
        if self.product.dps.length()>0:
            self.ohclDailyAfterDividends=self.ohclDaily.clone()
            self.ohclDailyAfterDividends=self.product.dps.adjustOHCLDailyManager(self.ohclDailyAfterDividends)
        else:
            self.ohclDailyAfterDividends=self.ohclDaily
            
        self.ohclMonthly.load_from_db("""
            select 
                id, 
                date_part('year',datetime) as year, 
                date_part('month', datetime) as month, 
                (array_agg(quote order by datetime))[1] as first, 
                min(quote) as low, 
                max(quote) as high, 
                (array_agg(quote order by datetime desc))[1] as last 
            from quotes 
            where id={} 
            group by id, year, month 
            order by year, month
        """.format(self.product.id))
        
        self.ohclWeekly.load_from_db("""
            select 
                id, 
                date_part('year',datetime) as year, 
                date_part('week', datetime) as week, 
                (array_agg(quote order by datetime))[1] as first, 
                min(quote) as low, 
                max(quote) as high, 
                (array_agg(quote order by datetime desc))[1] as last 
            from quotes 
            where id={} 
            group by id, year, week 
            order by year, week 
        """.format(self.product.id))
        
        self.ohclYearly.load_from_db("""
            select 
                id, 
                date_part('year',datetime) as year, 
                (array_agg(quote order by datetime))[1] as first, 
                min(quote) as low, max(quote) as high, 
                (array_agg(quote order by datetime desc))[1] as last 
            from quotes 
            where id={} 
            group by id, year 
            order by year 
        """.format(self.product.id))
        
        debug ("QuotesResult.get_ohcls of '{}' took {} with {} splits and {} dividends".format(self.product.name, datetime.now()-inicioall, self.product.splits.length(), self.product.dps.length()))
        

    def get_all(self):
        """Gets all in a set intradays form"""
        self.all=QuoteAllIntradayManager(self.mem)
        self.all.load_from_db(self.product)

    ## Returns the OHCLManager corresponding to it's duration and if has splits and dividends adjust
    def ohcl(self,  ohclduration, historicalchartadjust=eHistoricalChartAdjusts.NoAdjusts):
        if ohclduration==eOHCLDuration.Day:
            if historicalchartadjust==eHistoricalChartAdjusts.Splits:
                return self.ohclDaily
            elif historicalchartadjust==eHistoricalChartAdjusts.NoAdjusts:
                return self.ohclDailyBeforeSplits
            elif historicalchartadjust==eHistoricalChartAdjusts.SplitsAndDividends:
                return self.ohclDailyAfterDividends
        if ohclduration==eOHCLDuration.Week:
            return self.ohclWeekly
        if ohclduration==eOHCLDuration.Month:
            return self.ohclMonthly
        if ohclduration==eOHCLDuration.Year:
            return self.ohclYearly

class QuoteAllIntradayManager(ObjectManager):
    """Class that groups all quotes of the database. It's an array of QuoteIntradayManager"""
    def __init__(self, mem):
        ObjectManager.__init__(self)
        self.mem=mem
        self.product=None
 
    def load_from_db(self,  product):
        """Función que mete en setquotesintradia ordenado de objetos Quote, no es el ultimo día es un día"""
        del self.arr
        self.arr=[]
        self.product=product
        cur=self.mem.con.cursor()
        cur.execute("select * from quotes where id=%s order by datetime", (self.product.id,  ))
        
        intradayarr=[]
        dt_end=None
        for row in cur:
            if dt_end==None:#Loads the first datetime
                dt_end=dt_day_end(row['datetime'])
            if row['datetime']>dt_end:#Cambio de QuoteIntradayManager
                self.arr.append(QuoteIntradayManager(self.mem).init__create(self.product, dt_end.date(), intradayarr))
                dt_end=dt_day_end(row['datetime'])
                #crea otro intradayarr
                del intradayarr
                intradayarr=[]
                intradayarr.append(Quote(self.mem).init__db_row(row, self.product))
            else:
                intradayarr.append(Quote(self.mem).init__db_row(row, self.product))
        #No entraba si hay dos días en el primer día
        if len(intradayarr)!=0:
            self.arr.append(QuoteIntradayManager(self.mem).init__create(self.product, dt_end.date(), intradayarr))
            
        cur.close()

        
    def find(self, dattime):
        """Recorro de mayor a menor"""
        for i,  sqi in enumerate(reversed(self.arr)):
            if sqi.date<=dattime.date():
                found=sqi.find(dattime)
                if found==None:#Si no lo encuntra por que hay un quote de la misma fecha, pero es mayor que el que busco. Daba errores
                    continue
                else:
                    return found                    
        critical("Quote not found in QuoteAllIntradayManager of {} at {}".format(self.product, dattime))
        return None
            
            
    def purge(self, progress=False):
        """Purga todas las quotes de la inversión. Si progress es true muestra un QProgressDialog. 
        Devuelve el numero de quotes purgadas
        Si devuelve None, es que ha sido cancelado por el usuario, y no debería hacerse un comiti en el UI
        Sólo purga fichas menores a hoy()-30"""
        if progress==True:
            pd= QProgressDialog(QApplication.translate("Mem","Purging innecesary data"), QApplication.translate("Mem","Cancel"), 0,len(self.arr))
            pd.setModal(True)
            pd.setWindowTitle(QApplication.translate("Mem","Purging quotes"))
            pd.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
            pd.setMinimumDuration(0)          
        counter=0
        for i, sqi in enumerate(self.arr):
            if progress==True:
                pd.setValue(i)
                pd.setLabelText(QApplication.translate("Mem","Purged {0} quotes from {1}").format(counter, self.product.name))
                pd.update()
                QApplication.processEvents()
                if pd.wasCanceled():
                    return None
                QApplication.processEvents()
            if sqi.date<date.today()-timedelta(days=30):
                counter=counter+sqi.purge()
        return counter
        
class QuoteBasicManager:
    """Clase que agrupa quotes basic, last penultimate, lastyear """
    def __init__(self, mem, product):
        self.mem=mem
        self.lastyear=None
        self.last=None
        self.penultimate=None
        self.product=product       
        
    def init__create(self, last,  penultimate, lastyear):
        self.last=last
        self.penultimate=penultimate
        self.lastyear=lastyear
        return self
       
    
    def load_from_db(self):
        """
            Función que carga last, penultimate y lastdate 
            To see if there is a good value, You must search for datetime!= None or quote!=None
        """
        cur=self.mem.con.cursor()
        cur.execute("select * from last_penultimate_lastyear(%s, %s)", (self.product.id, self.mem.localzone.now() ))
        row=cur.fetchone()
        self.last=Quote(self.mem).init__create(self.product, row['last_datetime'], row['last'])
        self.penultimate=Quote(self.mem).init__create(self.product, row['penultimate_datetime'], row['penultimate'])
        self.lastyear=Quote(self.mem).init__create(self.product, row['lastyear_datetime'], row['lastyear'])

    def tpc_diario(self):
        if self.last.quote==None or self.penultimate.quote==None:
            return Percentage()
        else:
            return Percentage(self.last.quote-self.penultimate.quote, self.penultimate.quote)

    def tpc_anual(self):
        if self.lastyear.quote==None or self.lastyear.quote==0 or self.last.quote==None:
            return Percentage()
        else:
            return Percentage(self.last.quote-self.lastyear.quote, self.lastyear.quote)

class QuoteIntradayManager(QuoteManager):
    """Clase que agrupa quotes un una lista arr de una misma inversión y de un mismo día. """
    def __init__(self, mem):
        QuoteManager.__init__(self, mem)
        self.product=None
        self.date=None
        
    def load_from_db(self,  date, product):
        """Función que mete en setquotesintradia ordenado de objetos Quote, no es el ultimo día es un día"""
        del self.arr
        self.arr=[]
        self.product=product
        self.date=date
        cur=self.mem.con.cursor()
        iniciodia=dtaware_day_start_from_date(date, self.product.stockmarket.zone.name)
        siguientedia=iniciodia+timedelta(days=1)
        cur.execute("select * from quotes where id=%s and datetime>=%s and datetime<%s order by datetime", (self.product.id,  iniciodia, siguientedia))
        for row in cur:
            self.append(Quote(self.mem).init__db_row(row,  self.product))
        cur.close()
        
    def init__create(self, product, date, arrquotes):
        self.product=product
        self.date=date
        for q in arrquotes:
            self.arr.append(q)
        return self
        
    def open(self):
        """Devuelve el quote cuyo datetime es menor"""
        if len(self.arr)>0:
            return self.arr[0]
        return None
            
    def close(self):
        """Devuelve el quote cuyo datetime es mayor"""
        if len(self.arr)>0:
            return self.arr[len(self.arr)-1]
        return None
            
    def high(self):
        """Devuelve el quote cuyo quote es mayor"""
        if len(self.arr)==0:
            return None
        high=self.arr[0]
        for q in self.arr:
            if q.quote>high.quote:
                high=q
        return high
        
    def low(self):
        """Devuelve el quote cuyo quote es menor"""
        if len(self.arr)==0:
            return None
        low=self.arr[0]
        for q in self.arr:
            if q.quote<low.quote:
                low=q
        return low
        
    def find(self, dt):
        for q in reversed(self.arr):
            if q.datetime<=dt:
                return q
        info("Quote not found in QuoteIntradayManager ({}) of {} at {}. En el set hay {}".format(self.date,  self.product, dt, self.arr))
        return None

    def datetimes(self):
        """Returns a list with datetimes"""
        r=[]
        for quote in self.arr:
            r.append(quote.datetime)
        return r
        
    def quotes(self):
        """Show product quotes of the day"""
        r=[]
        for quote in self.arr:
            r.append(quote.quote)
        return r



    def purge(self):
        """Función que purga una inversión en un día dado, dejando ohlc y microsecond=5, que son los no borrables.
        Devuelve el número que se han quitado
        Esta función no hace un commit.
        """
        todelete=[]
        protected=[self.open(), self.close(), self.high(), self.low()]
        for q in self.arr:
            if q not in protected:
                if q.datetime.microsecond!=5:
                    todelete.append(q)

        if len(todelete)>0:
            for q in todelete:
                self.arr.remove(q)
                q.delete()
                
            ##Reescribe microseconds si ya el close tenía un 4
            if self.close().datetime.microsecond==4 : #SOLO SI TODELETE >0
                self.rewrite_microseconds()
                
        return len(todelete)
        
    def rewrite_microseconds(self):
        """Reescribe los microseconds de close,...
        Los escribe en orden de importancia"""
        c=self.close()
        if c!=None:
            c.delete()
            c.datetime=c.datetime.replace(microsecond=4)
            c.save()
            
    def variance(self):
        """Gives difference between highest and lowest prices"""
        return self.high().quote - self.low().quote
        
    def variance_percentage(self):
        """Gives variance percentage, using the lowest quote to calculate it to see daily volatility only. It's always a positive number"""
        h=self.high().quote
        l=self.low().quote
        return Percentage(h-l, l)

    def myqtablewidget(self, wdg): 
        
        hh=[self.tr("Time"), self.tr("Price"), self.tr("% Daily")]
        if self.product.hasSameLocalCurrency()==False:
            hh=hh + [self.tr("Price"), self.tr("% Daily")]
        QuoteDayBefore=Quote(self.mem).init__from_query(self.product, dtaware_day_start_from_date(self.date, self.mem.localzone_name))#day before as selected

        data=[]
        ##Construye tabla
        for i , q in enumerate(self.arr):
            row=[]
            row.append(q.datetime.time())
            row.append(q.quote)
            row.append(percentage_between(QuoteDayBefore.quote, q.quote))
            if self.product.hasSameLocalCurrency()==False:
                moneybefore=QuoteDayBefore.money().convert(self.mem.localcurrency, q.datetime)
                money=q.money().convert(self.mem.localcurrency, q.datetime)
                row.append(money)
                row.append(percentage_between(moneybefore, money))
            row.append(q)
            data.append(row)

        wdg.setDataWithObjects(hh, None,  data, decimals=6, zonename=self.mem.localzone_name, additional=self.myqtablewidget_additional)

    def myqtablewidget_additional(self, wdg):
        for i , q in enumerate(wdg.objects()):
            if q==self.high():
                wdg.table.item(i, 1).setBackground(eQColor.Green)
            elif q==self.product.result.intradia.low():
                wdg.table.item(i, 1).setBackground(eQColor.Red)             
        wdg.table.setCurrentCell(self.length()-1, 0)
        wdg.table.clearSelection()
