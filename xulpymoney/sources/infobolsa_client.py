import argparse
from urllib.request import urlopen
from decimal import Decimal
import logging
import sys
from xulpymoney.mem import MemSources

class CurrentPriceTicker:
    def __init__(self,ticker, xulpymoney, stockmarket):
        self.ticker=ticker
        self.stockmarket=stockmarket
        self.xulpymoney=xulpymoney
        self.dtaware=self.stockmarket.estimated_datetime_for_intraday_quote()
        self.price=None

    def __repr__(self):
        if self.xulpymoney!=None:
            return "PRICE | XULPYMONEY | {} | {} | {}".format(self.xulpymoney, self.dtaware, self.price)
        else:
            return "PRICE | STOCKMARKET | XX | TICKER | {} | {} | {}".format(self.ticker, self.dtaware , self.price)

    def get_price(self):
        try:
            web=urlopen('http://www.infobolsa.es/divisas')
        except:
            print ("ERROR | ERROR LOADING QUEFONDOS PAGE")
            sys.exit(255)

        if web==None:
            print ("ERROR | FETCHED EMPTY PAGE")
            sys.exit(255)

        web=web.read().decode('UTF-8')

        #Each currency data begins with <div class="currencyCont01">
        a=web.split("""<div class="currencyCont01">""")
        for block in a[1:]:
            if self.ticker=="EURUSD=X" and block.find("EUR/USD")!=-1:
                 self.price=Decimal(block.split("""<li class="txtCurren_ult top">""")[1].split("</li>")[0].replace(",","."))
                 return
        print ("ERROR | ERROR PARSING")
def main():
    mem=MemSources()
    parser=argparse.ArgumentParser()
    mem.addCommonToArgParse(parser)
    parser.add_argument('--TICKER_XULPYMONEY', help='XULPYMONEY code', nargs=2, metavar="VALUE", required=True)
    parser.add_argument('--STOCKMARKET', help='Stock market id', metavar="ID", required=True)
    args=parser.parse_args()        
    mem.addDebugSystem(args)
    stockmarket=mem.stockmarkets.find_by_id(int(args.STOCKMARKET))
    logging.info(stockmarket)
    s=CurrentPriceTicker(args.TICKER_XULPYMONEY[0], args.TICKER_XULPYMONEY[1], stockmarket)
    s.get_price()
    print(s)

