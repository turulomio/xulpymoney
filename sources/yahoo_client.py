#!/usr/bin/python3
import argparse
import datetime
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QUrl,  QEventLoop
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from decimal import Decimal
import locale
import sys
import pytz



########################## COPIED FUNCTIONS #######################################
#FROM LIBXULPYMONEY
def string2datetime(s, type, zone="Europe/Madrid"):
    """
        s is a string for datetime
        type is the diferent formats id
    """
    if type==1:#2017-11-20 23:00:00+00:00  ==> Aware
        s=s[:-3]+s[-2:]
        dat=datetime.datetime.strptime( s, "%Y-%m-%d %H:%M:%S%z" )
        return dat
    if type==2:#20/11/2017 23:00 ==> Naive
        dat=datetime.datetime.strptime( s, "%d/%m/%Y %H:%M" )
        return dat
    if type==3:#20/11/2017 23:00 ==> Aware, using zone parameter
        dat=datetime.datetime.strptime( s, "%d/%m/%Y %H:%M" )
        z=pytz.timezone(zone)
        return z.localize(dat)
    if type==4:#27 Nov 16:54 2017==> Aware, using zone parameter
        dat=datetime.datetime.strptime( s, "%d %b %H:%M %Y")
        z=pytz.timezone(zone)
        return z.localize(dat)
################################################################
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
                self.pages.append(data)
                self.loop.quit()#CUIDADO DEBE ESTAR EN EL ULTIMO
        ###########################
        r=Render('https://es.finance.yahoo.com/quote/{0}?p={0}'.format(self.ticker) )
        web=r.pages[0]
        if web==None:
            print ("ERROR | FETCHED EMPTY PAGE")
            sys.exit(255)
        precio=web.split('<!-- react-text: 36 -->')[1]#Antes
        precio=precio.split('<!-- /react-text -->')[0].replace(".","")#Después
        print(precio)
        self.price=Decimal(precio.replace(",", "."))
        hora=web.split('<span data-reactid="41">')[1]#Antes
        hora=hora.split('</span>')[0]#Después
        #Method 1
        hora=hora.replace("Al cierre: ", "").replace("de ", "")
        a=hora.split(" ")
        zone=a[3]
        a[2]=a[2].replace("AM", "")
        points=a[2].split(":")
        if a[2].find("PM"):
            a[2]=str(int(points[0])+12).zfill(2)+":"+points[1].replace("PM", "")
        hora=" ".join(a[0:3])+ " "+ str(datetime.date.today().year)
#        hora=hora[:4].upper()+hora[4:]#First month letter to upper
        print(zone)
        print(hora)
        print (datetime.datetime.now().strftime("%d %B %H:%M %Y"))
        dat=datetime.datetime.strptime( hora, "%d %B %H:%M %Y")
        z=pytz.timezone(zone)
        self.datetime_aware=z.localize(dat)

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

