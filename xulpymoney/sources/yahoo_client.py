import argparse
from PyQt5.QtCore import QUrl,  QEventLoop
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from decimal import Decimal
import logging
import sys

import time
from xulpymoney.mem import MemSources








## NO FUNCIONA ##








class CurrentPriceTicker:
    def __init__(self,ticker, xulpymoney, stockmarket):
        self.ticker=ticker
        self.xulpymoney=xulpymoney
        self.stockmarket=stockmarket
        self.dtaware=self.stockmarket.estimated_datetime_for_intraday_quote()
        self.price=None

    def __repr__(self):
        if self.xulpymoney!=None:
            return "PRICE | XULPYMONEY | {} | {} | {}".format(self.xulpymoney, self.dtaware, self.price)
        else:
            return "PRICE | STOCKMARKET | XX | TICKER | {} | {} | {}".format(self.ticker, self.dtaware , self.price)

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
        try:
            ## ESTAN AHORA CON AVISO OAUTH
            if web.find("Mercado abierto")!=-1:
                
                logging.debug("Mercado abierto")
                self.price=web.split('"regularMarketPrice":{"raw":')[1]#Antes
                self.price=self.price.split(',"fmt":')[0].replace(".","")#Después
                logging.debug(self.price)
                self.price=self.price.replace(",", ".")
                self.price=Decimal(self.price)
                logging.debug(self.price)
            else: # Mercado cerrado
                logging.debug("Mercado cerrado")
                self.price=web.split('data-reactid="35">')[3]#Antes
                self.price=self.price.split('</span><span clas')[0].replace(".","")#Después
                self.price=self.price.replace(",", ".")
                logging.debug(self.price)
                self.price=Decimal(self.price)

        except:
            print ("ERROR | GET PRICE FAILED: PRECIO {}. DATETIME {}".format(self.price, self.dtaware))
            sys.exit(0)
    
def main():
    mem=MemSources(coreapplication=False)
    parser=argparse.ArgumentParser()
    mem.addCommonToArgParse(parser)
    parser.add_argument('--TICKER_XULPYMONEY', help='XULPYMONEY code', nargs=2, metavar="VALUE", required=True)
    parser.add_argument('--STOCKMARKET', help='Stock market id', metavar="ID", required=True)
    args=parser.parse_args()        
    mem.addDebugSystem(args)

    stockmarket=mem.stockmarkets.find_by_id(int(args.STOCKMARKET))
    logging.info(stockmarket)
    if args.TICKER_XULPYMONEY:
        s=CurrentPriceTicker(args.TICKER_XULPYMONEY[0], args.TICKER_XULPYMONEY[1], stockmarket)
        s.get_price()
        print(s)

