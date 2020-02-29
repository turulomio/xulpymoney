from .. datetime_functions import dtaware
from .. libmanagers import ObjectManager_With_IdName_Selectable
from datetime import date, time, timedelta

## Class that represents stock market object. It gives several utils to manage it.
class StockMarket:
    def __init__(self, mem):
        self.mem=mem
        self.id=None
        self.name=None
        self.country=None
        self.starts=None
        self.closes=None
        self.zone=None
        self.starts_futures=None
        self.closes_futures=None
        
    def __repr__(self):
        return self.name

    def init__create(self, id, name,  country_id, starts, closes, starts_futures, closes_futures, zone_name):
        self.id=id
        self.name=name
        self.country=self.mem.countries.find_by_id(country_id)
        self.starts=starts
        self.closes=closes
        self.starts_futures=starts_futures
        self.closes_futures=closes_futures
        self.zone=self.mem.zones.find_by_name(zone_name).first()
        return self

    ## Returns the close time of a given date
    def dtaware_closes(self, date):
        return dtaware(date, self.closes, self.zone.name)
    
    def dtaware_closes_futures(self, date):
        return dtaware(date, self.closes_futures, self.zone.name)

    def dtaware_today_closes_futures(self):
        return self.dtaware_closes_futures(date.today())
    
    ## Returns a datetime with timezone with the todays stockmarket closes
    def dtaware_today_closes(self):
        return self.dtaware_closes(date.today())

    ## Returns a datetime with timezone with the todays stockmarket closes
    def dtaware_today_starts(self):
        return dtaware(date.today(), self.starts, self.zone.name)

    ## When we don't know the datetime of a quote because the webpage we are scrapping doesn't gives us, we can use this functions
    ## - If it's saturday or sunday it returns last friday at close time
    ## - If it's not weekend and it's after close time it returns todays close time
    ## - If it's not weekend and it's before open time it returns yesterday close time. If it's monday it returns last friday at close time
    ## - If it's not weekend and it's after opent time and before close time it returns aware current datetime
    ## @param delay Boolean that if it's True (default) now  datetime is minus 15 minutes. If False uses now datetime
    ## @return Datetime aware, always. It can't be None
    def estimated_datetime_for_intraday_quote(self, delay=True):
        if delay==True:
            now=self.zone.now()-timedelta(minutes=15)
        else:
            now=self.zone.now()
        if now.weekday()<5:#Weekday
            if now>self.dtaware_today_closes():
                return self.dtaware_today_closes()
            elif now<self.dtaware_today_starts():
                if now.weekday()>0:#Tuesday to Friday
                    return dtaware(date.today()-timedelta(days=1), self.closes, self.zone.name)
                else: #Monday
                    return dtaware(date.today()-timedelta(days=3), self.closes, self.zone.name)
            else:
                return now
        elif now.weekday()==5:#Saturday
            return dtaware(date.today()-timedelta(days=1), self.closes, self.zone.name)
        elif now.weekday()==6:#Sunday
            return dtaware(date.today()-timedelta(days=2), self.closes, self.zone.name)

    ## When we don't know the date pf a quote of a one quote by day product. For example funds... we'll use this function
    ## - If it's saturday or sunday it returns last thursday at close time
    ## - If it's not weekend and returns yesterday close time except if it's monday that returns last friday at close time
    ## @return Datetime aware, always. It can't be None
    def estimated_datetime_for_daily_quote(self):
        now=self.zone.now()
        if now.weekday()<5:#Weekday
            if now.weekday()>0:#Tuesday to Friday
                return dtaware(date.today()-timedelta(days=1), self.closes, self.zone.name)
            else: #Monday
                return dtaware(date.today()-timedelta(days=3), self.closes, self.zone.name)
        elif now.weekday()==5:#Saturday
            return dtaware(date.today()-timedelta(days=2), self.closes, self.zone.name)
        elif now.weekday()==6:#Sunday
            return dtaware(date.today()-timedelta(days=3), self.closes, self.zone.name)

class StockMarketManager(ObjectManager_With_IdName_Selectable):
    def __init__(self, mem):
        ObjectManager_With_IdName_Selectable.__init__(self)
        self.mem=mem

    ## Load in the Manager all Stockmarket objects. Originally StockMarkets was a db table with this values.
    ## @code
    ##         id | country |  starts  |              name               |  closes  |       zone       
    ##----+---------+----------+---------------------------------+----------+------------------
    ## 11 | be      | 07:00:00 | Bolsa de Bélgica                | 17:38:00 | Europe/Madrid
    ## 12 | nl      | 07:00:00 | Bolsa de Amsterdam              | 17:38:00 | Europe/Madrid
    ## 13 | ie      | 07:00:00 | Bolsa de Dublín                 | 17:38:00 | Europe/Madrid
    ## 14 | fi      | 07:00:00 | Bolsa de Helsinki               | 17:38:00 | Europe/Madrid
    ##  6 | it      | 07:00:00 | Bolsa de Milán                  | 17:38:00 | Europe/Rome
    ##  7 | jp      | 09:00:00 | Bolsa de Tokio                  | 20:00:00 | Asia/Tokyo
    ##  5 | de      | 09:00:00 | Bosa de Frankfurt               | 17:38:00 | Europe/Berlin
    ##  2 | us      | 09:30:00 | Bolsa de New York               | 16:38:00 | America/New_York
    ## 10 | eu      | 07:00:00 | Bolsa Europea                   | 17:38:00 | Europe/Madrid
    ##  9 | pt      | 07:00:00 | Bolsa de Lisboa                 | 17:38:00 | Europe/Lisbon
    ##  4 | en      | 07:00:00 | Bolsa de Londres                | 17:38:00 | Europe/London
    ##  8 | cn      | 00:00:00 | Bolsa de Hong Kong              | 20:00:00 | Asia/Hong_Kong
    ##  1 | es      | 09:00:00 | Bolsa de Madrid                 | 17:38:00 | Europe/Madrid
    ##  3 | fr      | 09:00:00 | Bolsa de París                  | 17:38:00 | Europe/Paris
    ## 15 | earth   | 09:00:00 | No cotiza en mercados oficiales | 17:38:00 | Europe/Madrid
    ## @endcode
    def load_all(self):
        self.append(StockMarket(self.mem).init__create( 1, "Bolsa de Madrid", "es", time(9, 0), time(17, 38), time(8, 0), time(20, 0), "Europe/Madrid"))
        self.append(StockMarket(self.mem).init__create( 11, "Bolsa de Bélgica", "be", time(9, 0), time(17, 38), time(8, 0), time(17, 40), "Europe/Brussels"))
        self.append(StockMarket(self.mem).init__create( 12, "Bolsa de Amsterdam", "nl", time(9, 0), time(17, 38), time(8, 0), time(22, 0), "Europe/Amsterdam"))
        self.append(StockMarket(self.mem).init__create( 13, "Bolsa de Dublín", "ie", time(8, 0), time(16, 38), time(8, 0), time(20, 0), "Europe/Dublin"))
        self.append(StockMarket(self.mem).init__create( 14, "Bolsa de Helsinki", "fi", time(9, 0), time(18, 38), time(8, 0), time(20, 0), "Europe/Helsinki"))
        self.append(StockMarket(self.mem).init__create( 6, "Bolsa de Milán", "it", time(9, 0), time(17, 38), time(8, 0), time(20, 0), "Europe/Rome"))
        self.append(StockMarket(self.mem).init__create( 7, "Bolsa de Tokio", "jp", time(9, 0), time(15, 8), time(8, 0), time(20, 0), "Asia/Tokyo"))
        self.append(StockMarket(self.mem).init__create( 5, "Bolsa de Frankfurt", "de", time(9, 0), time(17, 38), time(1, 0), time(22, 0), "Europe/Berlin"))
        self.append(StockMarket(self.mem).init__create( 2, "NYSE Stock Exchange", "us", time(9, 30), time(16, 38), time(0, 0), time(23, 59), "America/New_York"))
        self.append(StockMarket(self.mem).init__create( 10, "Bolsa Europea", "eu", time(9, 0), time(17, 38), time(1, 0), time(22, 0), "Europe/Brussels"))
        self.append(StockMarket(self.mem).init__create( 9, "Bolsa de Lisboa", "pt", time(9, 0), time(17, 38), time(8, 0), time(17, 40), "Europe/Lisbon"))
        self.append(StockMarket(self.mem).init__create( 4, "Bolsa de Londres", "en", time(8, 0), time(16, 38), time(8, 0), time(20, 0), "Europe/London"))
        self.append(StockMarket(self.mem).init__create( 8, "Bolsa de Hong Kong", "cn", time(9, 30), time(16, 8), time(8, 0), time(20, 0), "Asia/Hong_Kong"))
        self.append(StockMarket(self.mem).init__create( 3, "Bolsa de Paris", "fr", time(9, 0), time(17, 38), time(8, 0), time(22, 0), "Europe/Paris"))
        self.append(StockMarket(self.mem).init__create( 15, "No cotiza en mercados oficiales", "earth", time(9, 0), time(17, 38), time(8, 0), time(20, 0), "Europe/Madrid"))
        self.append(StockMarket(self.mem).init__create( 16, "AMEX Stock Exchange", "us", time(9, 30), time(16, 38), time(0, 0), time(23, 59), "America/New_York"))
        self.append(StockMarket(self.mem).init__create( 17, "Nasdaq Stock Exchange", "us", time(9, 30), time(16, 38), time(0, 0), time(23, 59), "America/New_York"))
        self.append(StockMarket(self.mem).init__create( 18, "Luxembourg Stock Exchange", "lu", time(9, 0), time(17, 38), time(8, 0), time(20, 0), "Europe/Luxembourg"))

    ## Personalized combobox with country flag
    def qcombobox(self, combo, selected=None):   
        self.order_by_name()
        combo.clear()
        for a in self.arr:
            combo.addItem(a.country.qicon(), a.name, a.id)
 
        if selected!=None:
            combo.setCurrentIndex(combo.findData(selected.id))
