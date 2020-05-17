import argparse
from urllib.request import urlopen
from decimal import Decimal
import sys
import logging
from xulpymoney.mem import MemSources

class CurrentPriceTickerFund:
    def __init__(self,ticker, xulpymoney, stockmarket):
        self.ticker=ticker
        self.stockmarket=stockmarket
        self.xulpymoney=xulpymoney
        self.dtaware=self.stockmarket.estimated_datetime_for_daily_quote()
        self.price=None

    def __repr__(self):
        if self.xulpymoney!=None:
            return "PRICE | XULPYMONEY | {} | {} | {}".format(self.xulpymoney, self.dtaware, self.price)
        else:
            return "PRICE | STOCKMARKET | XX | TICKER | {} | {} | {}".format(self.ticker, self.dtaware , self.price)

    def get_price(self):
        try:
            url='http://www.morningstar.es/es/funds/snapshot/snapshot.aspx?id='+self.ticker
            logging.debug(url)
            web=urlopen(url)
        except:
            print ("ERROR | ERROR LOADING MORNINGSTAR PAGE")
            sys.exit(255)
            
        if web==None:
            print ("ERROR | FETCHED EMPTY PAGE")
            sys.exit(255)

        for l in web.readlines():
            l=l.decode('UTF-8')
            if l.find("Estadística Rápida")!=-1:
                self.price=Decimal(l.split('line text">')[1].split("</td")[0].split("\xa0")[1].replace(",","."))
                return
        print ("ERROR | ERROR PARSING")
        
## Class to parse etf in morningstar
class CurrentPriceTickerETF(CurrentPriceTickerFund):
    def __init__(self, ticker, xulpymoney, stockmarket):
        CurrentPriceTickerFund.__init__(self, ticker, xulpymoney, stockmarket)
        
    def stockmarket2url(self):
        if self.stockmarket.id==3:#Paris
            return "xpar"
            
    ## @return Returns LVE de LVE.PA
    def yahoo2url(self):
        return self.ticker.split(".")[0].lower()
        
    def get_price(self):
        try:
            url='https://www.morningstar.com/etfs/{}/{}/quote.html'.format(self.stockmarket2url(), self.yahoo2url())
            logging.debug(url)
            web=urlopen(url)
        except:
            print ("ERROR | ERROR LOADING MORNINGSTAR PAGE")
            sys.exit(255)
            
        if web==None:
            print ("ERROR | FETCHED EMPTY PAGE")
            sys.exit(255)

        for l in web.readlines():
            l=l.decode('UTF-8')
            if l.find("25")!=-1:
                print (l)
#                self.price=Decimal(l.split('line text">')[1].split("</td")[0].split("\xa0")[1].replace(",","."))
#                return
        print ("ERROR | ERROR PARSING")
def main():
    mem=MemSources()
    parser=argparse.ArgumentParser()
    mem.addCommonToArgParse(parser)
    parser.add_argument('--TICKER_XULPYMONEY', help='XULPYMONEY code', nargs=2, metavar="VALUE")
    parser.add_argument('--STOCKMARKET', help='Stock market id', metavar="ID", required=True)   
    group2=parser.add_mutually_exclusive_group(required=True)
    group2.add_argument('--fund', help="Fund search", action='store_true', default=False)
    group2.add_argument('--etf', help="ETF search", action='store_true', default=False) 
    args=parser.parse_args() 
    mem.addDebugSystem(args.debug)

    stockmarket=mem.stockmarkets.find_by_id(int(args.STOCKMARKET))
    logging.info(stockmarket)

    if args.TICKER_XULPYMONEY and args.fund==True:
        s=CurrentPriceTickerFund(args.TICKER_XULPYMONEY[0], args.TICKER_XULPYMONEY[1], stockmarket)
        s.get_price()
        print(s)
    elif args.TICKER_XULPYMONEY and args.etf==True:
        s=CurrentPriceTickerETF(args.TICKER_XULPYMONEY[0], args.TICKER_XULPYMONEY[1], stockmarket)
        s.get_price()
        print(s)

