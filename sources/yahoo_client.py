#!/usr/bin/python3
import argparse
import datetime
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QUrl,  QEventLoop
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from decimal import Decimal
import logging
import sys
import platform
if platform.system()=="Windows":
    sys.path.append("ui/")
    sys.path.append("images/")
else:
    sys.path.append("/usr/lib/xulpymoney")
import time
from libxulpymoneyfunctions import  ampm2stringtime,  addDebugSystem,  addCommonToArgParse, dtaware, string2time

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
        url='https://es.finance.yahoo.com/quote/{0}?p={0}'.format(self.ticker)
        logging.debug("Searching in {}".format(url))

        r=Render(url)
        web=r.pages[0]
        if web==None:
            print ("ERROR | FETCHED EMPTY PAGE")
            sys.exit(0)

        for line in web.split("\n"):#Quita mucha porquería
            if line.find("<!-- react-text: 36 -->")!=-1:
                break

        try:
            logging.debug(line)
            hora="INIT"
            zone="INIT"
            precio="INIT"
            if line.find("Mercado abierto")!=-1:
                logging.debug("Mercado abierto")
                precio=line.split('<span class="Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)" data-reactid="35">')[1]#Antes
                precio=precio.split('</span><span')[0].replace(".","")#Después
                precio=precio.replace(",", ".")
                logging.debug(precio)

                hora=line.split('A partir del  ')[1]#Antes
                hora=hora.split('. Mercado abierto.')[0]#Después
                a=hora.split(" ")
                hora=ampm2stringtime(a[0], type=1)
                hora=string2time(hora)
                logging.debug(hora)

                zone='Europe/Madrid'#Because is a spanish url

                self.datetime_aware=dtaware(datetime.date.today(), hora, zone)
                self.price=Decimal(precio)
            else: # Mercado cerrado
                logging.debug("Mercado cerrado")
                precio=line.split('data-reactid="35">')[3]#Antes
                precio=precio.split('</span><span clas')[0].replace(".","")#Después
                precio=precio.replace(",", ".")
                logging.debug(precio)

                hora=line.split('Al cierre: ')[1]#Antes
                hora=hora.split(' CEST')[0]#Después
                hora=hora.replace("de ", "")
                hora=hora.split(" ")[2]
                hora=ampm2stringtime(hora, type=1)
                hora=string2time(hora)
                logging.debug(hora)

                zone='Europe/Madrid'#Because is a spanish url

                self.datetime_aware=dtaware(datetime.date.today(), hora, zone)
                self.price=Decimal(precio)
        except:
            print ("ERROR | GET PRICE FAILED: PRECIO {}. HORA {}. ZONE {}".format(precio, hora, zone))
            sys.exit(0)
    

if __name__=="__main__":#Por defecto se pone WARNING y mostrar´ia ERROR y CRITICAL


    app = QApplication(sys.argv)
    parser=argparse.ArgumentParser()
    parser.add_argument('--TICKER_XULPYMONEY', help='XULPYMONEY code', nargs=2, metavar="VALUE")
    addCommonToArgParse(parser)
    args=parser.parse_args()        
    addDebugSystem(args)

    if args.TICKER_XULPYMONEY:
        s=CurrentPriceTicker(args.TICKER_XULPYMONEY[0], args.TICKER_XULPYMONEY[1])
        s.get_price()
        print(s)

