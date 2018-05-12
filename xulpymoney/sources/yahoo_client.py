#!/usr/bin/python3
import argparse
import datetime
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QUrl,  QEventLoop
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from decimal import Decimal
import locale
import sys
import platform
if platform.system()=="Windows":
    sys.path.append("ui/")
    sys.path.append("images/")
else:
    sys.path.append("/usr/lib/xulpymoney")
import pytz
import time
from libxulpymoneyfunctions import  month2int, ampm2stringtime

class CurrentPriceTicker:
    def __init__(self,ticker, xulpymoney):
        self.ticker=ticker
        self.xulpymoney=xulpymoney
        self.datetime_aware=None
        self.price=None

    def __repr__(self):
        if self.xulpymoney!=None:
            return "PRICE | XULPYMONEY | {} | {} | {}".format(self.xulpymoney, self.datetime_aware, self.price)
        else:
            return "PRICE | STOCKMARKET | XX | TICKER | {} | {} | {}".format(self.ticker, self.datetime_aware , self.price)

    def get_price(self):
        class Render(QWebEngineView):
            def __init__(self, url):
                QWebEngineView.__init__(self)
                self.loop=QEventLoop()#Queda en un loop hasta que acaba la carga de todas las páginas
                self.loadFinished.connect(self._loadFinished)
                self.pages=[]
                self.page().profile().cookieStore().deleteAllCookies()
                self.page().profile().setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)
                self.load(QUrl(url))
                self.loop.exec()

            def numPages(self):
                return len(self.pages)

            def _loadFinished(self, result):
                """
                   This is an async call, you need to wait for this to be called before closing the app
                """
                self.page().toHtml(self._callable)

            def _callable(self, data):
                """
                   Se llama cada vez que una página es cargada con el html en data
                """                
                time.sleep(0.25)
                self.pages.append(data)
                self.loop.quit()#CUIDADO DEBE ESTAR EN EL ULTIMO
        ###########################
        r=Render('https://es.finance.yahoo.com/quote/{0}?p={0}'.format(self.ticker) )
        web=r.pages[0]
        if web==None:
            print ("ERROR | FETCHED EMPTY PAGE")
            sys.exit(0)
            
        for line in web.split("\n"):#Quita mucha porquería
            if line.find("<!-- react-text: 36 -->")!=-1:
                break
            
        try:
#            print(line)
            hora="INIT"
            zone="INIT"
            precio="INIT"
            
            precio=line.split('<!-- react-text: 36 -->')[2]#Antes
            precio=precio.split('<!-- /react-text -->')[0].replace(".","")#Después
            precio=precio.replace(",", ".")
            
            hora=line.split('<span data-reactid="40">')[1]#Antes
            hora=hora.split('</span>')[0]#Después
            hora=hora.replace("Al cierre: ", "").replace("de ", "")
            
            a=hora.split(" ")
            zone=a[3]
            hora="{} {} {} {}".format(a[0],month2int(a[1]), ampm2stringtime(a[2],type=1), datetime.date.today().year)
#            print(hora, zone, precio)
            dat=datetime.datetime.strptime( hora, "%d %m %H:%M %Y")
            z=pytz.timezone(zone)
            self.datetime_aware=z.localize(dat)
            self.price=Decimal(precio)
        except:
            print ("ERROR | GET PRICE FAILED: PRECIO {}. HORA {}. ZONE {}".format(precio, hora, zone))
            sys.exit(0)
            

if __name__=="__main__":
    app = QApplication(sys.argv)
    locale.setlocale(locale.LC_ALL,'en_US.UTF-8')
    parser=argparse.ArgumentParser()
    group1=parser.add_mutually_exclusive_group(required=True)
    group1.add_argument('--TICKER_XULPYMONEY', help='XULPYMONEY code', nargs=2, metavar="VALUE")
    args=parser.parse_args()

    if args.TICKER_XULPYMONEY:
        s=CurrentPriceTicker(args.TICKER_XULPYMONEY[0], args.TICKER_XULPYMONEY[1])
        s.get_price()
        print(s)

