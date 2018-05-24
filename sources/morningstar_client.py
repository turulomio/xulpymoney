#!/usr/bin/python3
import argparse
from urllib.request import urlopen
from decimal import Decimal
import sys
import platform
import logging
if platform.system()=="Windows":
    sys.path.append("ui/")
    sys.path.append("images/")
else:
    sys.path.append("/usr/lib/xulpymoney")
from PyQt5.QtWidgets import QApplication
from libxulpymoney import MemSources
from libxulpymoneyfunctions import addDebugSystem, addCommonToArgParse

class CurrentPriceTicker:
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

if __name__=="__main__":
    app = QApplication(sys.argv)
    parser=argparse.ArgumentParser()
    parser.add_argument('--TICKER_XULPYMONEY', help='XULPYMONEY code', nargs=2, metavar="VALUE")
    parser.add_argument('--STOCKMARKET', help='Stock market id', metavar="ID", required=True)
    addCommonToArgParse(parser)
    args=parser.parse_args() 
    addDebugSystem(args)

    mem=MemSources()
    stockmarket=mem.stockmarkets.find_by_id(int(args.STOCKMARKET))
    logging.info(stockmarket)

    if args.TICKER_XULPYMONEY:
        s=CurrentPriceTicker(args.TICKER_XULPYMONEY[0], args.TICKER_XULPYMONEY[1], stockmarket)
        s.get_price()
        print(s)

