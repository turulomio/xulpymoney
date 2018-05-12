#!/usr/bin/python3
import argparse
from urllib.request import urlopen
from decimal import Decimal
import sys
import platform
if platform.system()=="Windows":
    sys.path.append("ui/")
    sys.path.append("images/")
else:
    sys.path.append("/usr/lib/xulpymoney")
from PyQt5.QtWidgets import QApplication
from libxulpymoneyfunctions import string2datetime

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
        try:
            web=urlopen('http://www.morningstar.es/es/funds/snapshot/snapshot.aspx?id='+self.ticker)
        except:
            print ("ERROR | ERROR LOADING MORNINGSTAR PAGE")
            sys.exit(255)
            
        if web==None:
            print ("ERROR | FETCHED EMPTY PAGE")
            sys.exit(255)

        for l in web.readlines():
            l=l.decode('UTF-8')
            if l.find("Estadística Rápida")!=-1:
                datestr=l.split("<br />")[1].split("</span")[0]
                self.datetime_aware=string2datetime("{} 23:00".format(datestr), type=3, zone="Europe/Madrid")
                self.price=Decimal(l.split('line text">')[1].split("</td")[0].split("\xa0")[1].replace(",","."))
                return
        print ("ERROR | ERROR PARSING")

class CurrentPriceISIN:
    def __init__(self):
        self.isin=None
        self.datetime_aware=None
        self.price=None

    def __repr__(self):
        return "PRICE | STOCKMARKET | ES | ISIN | {} | {} | {}".format(self.isin, self.datetime_aware , self.price)
if __name__=="__main__":
    app = QApplication(sys.argv)
    parser=argparse.ArgumentParser()
    group1=parser.add_mutually_exclusive_group(required=True)
    group1.add_argument('--ISIN', help='ISIN code')
    group1.add_argument('--TICKER', help='TICKER code')
    group1.add_argument('--TICKER_XULPYMONEY', help='XULPYMONEY code', nargs=2, metavar="VALUE")
    args=parser.parse_args()

    if args.ISIN:
        s=CurrentPriceISIN(args.ISIN)
        s.get_prices()
        s.print()

    if args.TICKER:
        s=CurrentPriceTicker(args.TICKER, None)
        s.get_price()
        print(s)

    if args.TICKER_XULPYMONEY:
    
        s=CurrentPriceTicker(args.TICKER_XULPYMONEY[0], args.TICKER_XULPYMONEY[1])
        s.get_price()
        print(s)

