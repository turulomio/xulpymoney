#!/usr/bin/python3
import argparse
from requests import get
from decimal import Decimal
import sys
import platform
import logging
if platform.system()=="Windows":
    sys.path.append("ui/")
    sys.path.append("images/")
else:
    sys.path.append("/usr/lib/xulpymoney")
from libxulpymoneyfunctions import addCommonToArgParse, addDebugSystem
from libxulpymoney import MemSources
        
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
        url = 'http://www.google.com/search?q={}'.format(self.ticker)    # fails
        web=get(url).text

        if web==None:
            print ("ERROR | FETCHED EMPTY PAGE")
            sys.exit(255)

        if web.find('font-size:157%"><b>')!=-1:
            try:
                web=web.split('font-size:157%"><b>')[1]#Antes
                web=web.split('</span> - <a class="fl"')[0]#Después
                self.price=Decimal(web.split("</b>")[0].replace(".","").replace(",","."))
            except:
                print("ERROR | COULDN'T CONVERT DATETIME {} AND PRICE {}".format(self.dtaware, self.price))
                sys.exit(0)
            return

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument('--TICKER_XULPYMONEY', help='XULPYMONEY code', nargs=2, metavar="VALUE", required=True)
    parser.add_argument('--STOCKMARKET', help='Stock market id', metavar="ID", required=True)
    addCommonToArgParse(parser)
    args=parser.parse_args()        
    addDebugSystem(args)

    mem=MemSources()
    stockmarket=mem.stockmarkets.find_by_id(int(args.STOCKMARKET))
    logging.info(stockmarket)
    s=CurrentPriceTicker(args.TICKER_XULPYMONEY[0], args.TICKER_XULPYMONEY[1], stockmarket)
    s.get_price()
    print(s)

