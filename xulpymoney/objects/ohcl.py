from datetime import timedelta, date
from decimal import Decimal
from xulpymoney.datetime_functions import dtaware_day_end_from_date,  string2date, dtaware
from xulpymoney.libmanagers import ObjectManager, DatetimeValueManager
from xulpymoney.objects.percentage import Percentage

## Class to manage Open High Close Low Values in a period of time of a productº
class OHCL:
    def __init__(self,  mem):
        self.mem=mem
        self.product=None
        self.open=None
        self.close=None
        self.high=None
        self.low=None
        
    
    ## Calcula el intervalo entre dos ohcl. El posteror es el que se pasa como parámetro
    def get_interval(self, ohclposterior):
        return ohclposterior.datetime-self.datetime

    def percentage(self, ohcl):
        """CAlcula el incremento en % en el cierre del ohcl actual y el pasado como parametro. Siendo el pasado como parametro posterior en el tiempo"""
        if ohcl:
            return Percentage(ohcl.close-self.close, self.close)            
        else:
            return Percentage()

        
class OHCLDaily(OHCL):
    def __init__(self, mem):
        OHCL.__init__(self, mem)
        self.date=None
        
    def init__from_client_string(self, s):
        """
            Generates a OHCL object from string from scrapper clients
            OHCL | XULPYMONEY | 81093 | 2017-11-21 | 0.0330 | 0.0330 | 0.0320 | 0.0310
        """
        a=s.split(" | ")
        try:
            self.product=self.mem.data.products.find_by_id(int(a[2]))
            self.date=string2date(a[3])
            self.open=Decimal(a[4])
            self.high=Decimal(a[5])
            self.close=Decimal(a[6])
            self.low=Decimal(a[7])
        except:
            return None
        return self

    def generate_4_quotes(self):
        from xulpymoney.objects.quote import Quote
        quotes=[]
        datestart=dtaware(self.date,self.product.stockmarket.starts,self.product.stockmarket.zone.name)
        dateends=dtaware(self.date,self.product.stockmarket.closes,self.product.stockmarket.zone.name)
        datetimefirst=datestart-timedelta(seconds=1)
        datetimelow=(datestart+(dateends-datestart)*1/3)
        datetimehigh=(datestart+(dateends-datestart)*2/3)
        datetimelast=dateends+timedelta(microseconds=4)

        quotes.append(Quote(self.mem).init__create(self.product,datetimelast, Decimal(self.close)))#closes
        quotes.append(Quote(self.mem).init__create(self.product,datetimelow, Decimal(self.low)))#low
        quotes.append(Quote(self.mem).init__create(self.product,datetimehigh, Decimal(self.high)))#high
        quotes.append(Quote(self.mem).init__create(self.product, datetimefirst, Decimal(self.open)))#open        
        return quotes
        
    def init__from_dbrow(self, row, product):
        self.product=product
        self.date=row['date']
        self.open=row['first']
        self.close=row['last']
        self.high=row['high']
        self.low=row['low']
        return self
        
    def datetime(self):
        """Devuelve un datetime usado para dibujar en gráficos"""
        return dtaware_day_end_from_date(self.date, self.product.stockmarket.zone.name)
        
    def print_time(self):
        return "{0}".format(self.date)
        
    def clone(self):
        o=OHCLDaily(self.mem)
        o.product=self.product
        o.date=self.date
        o.open=self.open
        o.close=self.close
        o.high=self.high
        o.low=self.low
        return o
        
    ## Removes all quotes of the selected day
    def delete(self):
        cur=self.mem.con.cursor()
        cur.execute("delete from quotes where id=%s and datetime::date=%s", (self.product.id, self.date))
        cur.close()
        
class OHCLMonthly(OHCL):
    def __init__(self, mem):
        OHCL.__init__(self, mem)
        self.year=None
        self.month=None
        
    def init__from_dbrow(self, row, product):
        self.product=product
        self.year=int(row['year'])
        self.month=int(row['month'])
        self.open=row['first']
        self.close=row['last']
        self.high=row['high']
        self.low=row['low']
        return self
    def print_time(self):
        return "{0}-{1}".format(int(self.year), int(self.month))
        
                
    def clone(self):
        o=OHCLMonthly(self.mem)
        o.product=self.product
        o.year=self.year
        o.month=self.month
        o.open=self.open
        o.close=self.close
        o.high=self.high
        o.low=self.low
        return o
    def datetime(self):
        """Devuelve un datetime usado para dibujar en gráficos, pongo el día 28 para no calcular el último"""
        return dtaware_day_end_from_date(date(self.year, self.month, 28), self.product.stockmarket.zone.name)
        
        
    ## Removes all quotes of the selected month and year
    def delete(self):
        cur=self.mem.con.cursor()
        cur.execute("delete from quotes where id=%s and date_part('month',datetime)=%s and date_part('year',datetime)=%s", (self.product.id, self.month, self.year))
        cur.close()        
                
class OHCLWeekly(OHCL):
    def __init__(self, mem):
        OHCL.__init__(self, mem)
        self.year=None
        self.week=None
        
    def init__from_dbrow(self, row, product):
        self.product=product
        self.year=int(row['year'])
        self.week=int(row['week'])
        self.open=row['first']
        self.close=row['last']
        self.high=row['high']
        self.low=row['low']
        return self
                        
    def clone(self):
        o=OHCLWeekly(self.mem)
        o.product=self.product
        o.year=self.year
        o.week=self.week
        o.open=self.open
        o.close=self.close
        o.high=self.high
        o.low=self.low
        return o
        
    def datetime(self):
        """Devuelve un datetime usado para dibujar en gráficos, con el último día de la semana"""
        d = date(self.year,1,1)
        d = d - timedelta(d.weekday())
        dlt = timedelta(days = (self.week-1)*7)
        lastday= d + dlt + timedelta(days=6)
        return dtaware_day_end_from_date(lastday, self.product.stockmarket.zone.name)
        
    def print_time(self):
        return "{0}-{1}".format(self.year, self.week)

class OHCLYearly(OHCL):
    def __init__(self, mem):
        OHCL.__init__(self, mem)
        self.year=None
        
    def __repr__(self):
        return ("OHCLYearly ({}) of product {}".format( self.year, self.product.id))
        
    def init__from_dbrow(self, row, product):
        self.product=product
        self.year=int(row['year'])
        self.open=row['first']
        self.close=row['last']
        self.high=row['high']
        self.low=row['low']
        return self
                        
    def clone(self):
        o=OHCLDaily(self.mem)
        o.product=self.product
        o.year=self.year
        o.open=self.open
        o.close=self.close
        o.high=self.high
        o.low=self.low
        return o
    def datetime(self):
        """Devuelve un datetime usado para dibujar en gráficos"""
        return dtaware_day_end_from_date(date(self.year, 12, 31), self.product.stockmarket.zone.name)
    def print_time(self):
        return "{0}".format(int(self.year))
    
    ## Removes all quotes of the selected year
    def delete(self):
        cur=self.mem.con.cursor()
        cur.execute("delete from quotes where id=%s and date_part('year',datetime)=%s", (self.product.id, self.year))
        cur.close()     

class OHCLManager(ObjectManager):
    def __init__(self, mem, product):
        ObjectManager.__init__(self)
        self.mem=mem
        self.product=product
    
    def load_from_db(self, sql):
        """El sql debe estar ordenado por date"""
        del self.arr
        self.arr=[]
        cur=self.mem.con.cursor()
        cur.execute(sql)#select * from ohclyearly where id=79329 order by date
        for row in cur:
            self.append(self.itemclass(self.mem).init__from_dbrow(row, self.product))
        cur.close()

    ## Returns a list with all the close of the array
    def closes(self, from_dt=None):
        closes=[]
        if from_dt==None:
            for ohcl in self.arr:
                closes.append(ohcl.close)
        else:
            for ohcl in self.arr:
                if ohcl.datetime()>=from_dt:
                    closes.append(ohcl.close)
        return closes

#
#    def sma(self, number):
#        """
#        simple movil average
#            Return a sma array of tuples (datetime,sma_n)
#            Normal numbers are 50 and 200
#            
#        Calculamos segun
#        a=[1,2,3,4]
#        sum([0:2])=3
#        """
#        def average(inicio, final):
#            suma=Decimal(0)
#            for ohcl in self.arr[inicio:final]:
#                suma=suma+ohcl.close
#            return suma/(final-inicio)
#        ######################
#        if self.length()<=number:
#            return None
#            
#        sma=[]
#        for i, ohcl in enumerate(self.arr):
#            if i>=number:
#                sma.append((ohcl.datetime(), average(i-number, i)))
#        return sma
        
    ## Calculates the median value of all OHCL.close values
    ## This function is in OHCLManager and can be used in all derivated classes
    ## @param from_dt Date from data is calculated. If it's None (default) if calculated the median value from all OHCL data in the array.
    def closes_median_value(self, from_dt=None):
        r=self.closes()
        r.sort()
        if self.length() % 2==0:#Par
            return r[self.length() // 2 -1]#n/2. But like I begin with 0 is -1
        else:
            return r[self.length() // 2]#If it's 5, median will be 3, but like I begin with 0 is integer division
        

    def opens(self, from_dt=None):
        """Returns a list with all the open of the array"""
        opens=[]
        if from_dt==None:
            for ohcl in self.arr:
                opens.append(ohcl.open)
        else:
            for ohcl in self.arr:
                if ohcl.datetime()>=from_dt:
                    opens.append(ohcl.open)
        return opens

    def highs(self, from_dt=None):
        """Returns a list with all the high of the array"""
        highs=[]
        if from_dt==None:
            for ohcl in self.arr:
                highs.append(ohcl.high)
        else:
            for ohcl in self.arr:
                if ohcl.datetime()>=from_dt:
                    highs.append(ohcl.high)
        return highs

    def lows(self, from_dt=None):
        """Returns a list with all the low of the array"""
        lows=[]
        if from_dt==None:
            for ohcl in self.arr:
                lows.append(ohcl.low)
        else:
            for ohcl in self.arr:
                if ohcl.datetime()>=from_dt:
                    lows.append(ohcl.low)
        return lows

    def datetimes(self, from_dt=None):
        """Returns a list with all the datetimes of the array"""
        datetimes=[]
        if from_dt==None:
            for ohcl in self.arr:
                datetimes.append(ohcl.datetime())
        else:
            for ohcl in self.arr:
                if ohcl.datetime()>=from_dt:
                    datetimes.append(ohcl.datetime())
        return datetimes
        
    ## From this value you can get sma, median...
    ## @return a DatetimeValueManager from libmanagers
    def DatetimeValueManager(self,attribute,  from_dt=None):
        r=DatetimeValueManager()
        if from_dt==None:
            for ohcl in self.arr:
                r.appendDV(ohcl.datetime(), getattr(ohcl, attribute))
        else:
            for ohcl in self.arr:
                if ohcl.datetime()>=from_dt:
                    r.appendDV(ohcl.datetime(), getattr(ohcl, attribute))
        return r

    ## Return the value of the attribute of the <= dat 
    ## @param dt datetime
    ## @param attribute. Can be "open", "high", "close","low"
    def find_by_datetime(self, dt, attribute):
        for o in reversed(self.arr):
            if o.datetime()<=dt:
                return dt
        return None

    ## Return the ohcl with the bigest ohcl.high
    def highest(self):
        if self.length()==0:
            return None
        r=self.first()
        for ohcl in self.arr:
            if ohcl.high>=r.high:
                r=ohcl
        return r

    ## Return the ohcl with the lowes ohcl.low
    def lowest(self):
        if self.length()==0:
            return None
        r=self.first()
        for ohcl in self.arr:
            if ohcl.low<=r.low:
                r=ohcl
        return r

    ## @returns string with the limits of the price [loweest, highest]
    def string_limits(self):
        return "[ {}, {} ]".format(self.product.money(self.lowest().low), self.product.money(self.highest().high))
        
    ## Returns a list of sma from smas, which dt values are over price parameter
    ## @param dt. datetime
    ## @param price Decimal to compare
    ## @param smas List of integers with the period of the sma
    ## @param dvm_smas. List of DatetimeValueManager with the SMAS with integers are in smas
    ## @param attribute. Can be "open", "high", "close","low"
    ## @return int. With the number of standard sma (10, 50,200) that are over product current price
    def list_of_sma_over_price(self,  dt, price, smas=[10, 50, 200], dvm_smas=None, attribute="close"):
        if dvm_smas==None:#Used when I only neet to calculate one value
            dvm=self.DatetimeValueManager(attribute)
        
            #Calculate smas for all values in smas
            dvm_smas=[]#Temporal list to store sma to fast calculations
            for sma in smas:
                dvm_smas.append(dvm.sma(sma))
            
        # Compare dt sma with price and return a List with smas integers
        r=[]
        for i, dvm_sma in enumerate(dvm_smas):
            sma_value=dvm_sma.find_le(dt).value
            if price<sma_value:
                r.append(smas[i])
        return r
        

class OHCLDailyManager(OHCLManager):
    def __init__(self, mem, product):
        OHCLManager.__init__(self, mem, product)
        self.setConstructorParameters(self.mem, product)
        self.itemclass=OHCLDaily

    def find(self, date):
        """Fucnción que busca un ohcldaily con fecha igual o menor de la pasada como parametro"""
        for ohcl in reversed(self.arr):
            if ohcl.date<=date:
                return ohcl
        return None



    ## Returns a QuoteBasicManager con los datos del setohcldairy
    def setquotesbasic(self):
        from xulpymoney.objects.quote import Quote, QuoteBasicManager
        last=None
        penultimate=None
        lastyear=None
        if self.length()==0:
            return QuoteBasicManager(self.mem, self.product).init__create(Quote(self.mem).none(self.product), Quote(self.mem).none(self.product),  Quote(self.mem).none(self.product))
        ohcl=self.arr[self.length()-1]#last
        last=Quote(self.mem).init__create(self.product, dtaware(ohcl.date, self.product.stockmarket.closes,  self.product.stockmarket.zone.name), ohcl.close)
        ohcl=self.find(ohcl.date-timedelta(days=1))#penultimate
        if ohcl!=None:
            penultimate=Quote(self.mem).init__create(self.product, dtaware(ohcl.date, self.product.stockmarket.closes,  self.product.stockmarket.zone.name), ohcl.close)
        ohcl=self.find(date(date.today().year-1, 12, 31))#lastyear
        if ohcl!=None:
            lastyear=Quote(self.mem).init__create(self.product, dtaware(ohcl.date, self.product.stockmarket.closes,  self.product.stockmarket.zone.name), ohcl.close)        
        return QuoteBasicManager(self.mem, self.product).init__create(last, penultimate, lastyear)

    ## Returns a list with all the dates of the array
    def dates(self):
        r=[]
        for ohcl in self.arr:
            r.append(ohcl.date)
        return r
        

class OHCLWeeklyManager(OHCLManager):
    def __init__(self, mem, product):
        OHCLManager.__init__(self, mem, product)
        self.itemclass=OHCLWeekly
        self.setConstructorParameters(self.mem, product)
        
class OHCLYearlyManager(OHCLManager):
    def __init__(self, mem, product):
        OHCLManager.__init__(self, mem, product)
        self.itemclass=OHCLYearly
        self.setConstructorParameters(self.mem, product)
        

        
    ## Returns a OHCLYearly
    def find(self, year):
        for ohcl in self.arr:
            if ohcl.year==year:
                return ohcl
        return None
        
    def percentage_by_year(self, year):
        """
            Calcula el porcentaje del mes partiendo del punto de cierre del mes anterior
        """
        ohcl=self.find(year)
        lastohcl=self.find(year-1)
        if lastohcl:
            return lastohcl.percentage(ohcl)
        if ohcl:
            return Percentage((ohcl.close-ohcl.open), ohcl.open)
        else:
            return Percentage()
        
class OHCLMonthlyManager(OHCLManager):
    def __init__(self, mem, product):
        OHCLManager.__init__(self, mem, product)
        self.itemclass=OHCLMonthly
        self.setConstructorParameters(self.mem, product)
        
    def find(self, year,  month):
        for ohcl in self.arr:
            if ohcl.year==year and ohcl.month==month:
                return ohcl
        return None
        
        
    def percentage_by_year_month(self, year, month):
        """
            Calcula el porcentaje del mes partiendo del punto de cierre del mes anterior
        """
        dat=date(year, month, 1)
        last=dat-timedelta(days=1)
        ohcl=self.find(year, month)
        lastohcl=self.find(last.year, last.month)
        if lastohcl:
            return lastohcl.percentage(ohcl)
        else:
            return Percentage()
