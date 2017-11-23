#!/usr/bin/python3
import argparse
import datetime
from urllib.request import urlopen
from decimal import Decimal
import sys
import pytz
from PyQt5.QtWidgets import QApplication

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
                datarr=datestr.split("/")
                date=datetime.date(int(datarr[2]), int(datarr[1]), int(datarr[0]))
                z=pytz.timezone("UTC")
                a=datetime.datetime(date.year,date.month,date.day, 23 , 00)
                self.datetime_aware=z.localize(a)
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
    parser.add_argument('--ISIN', help='ISIN code')
    parser.add_argument('--TICKER', help='TICKER code')
    parser.add_argument('--XULPYMONEY', help='XULPYMONEY code')
    args=parser.parse_args()

    if args.ISIN:
        s=CurrentPriceISIN(args.ISIN)
        s.get_prices()
        s.print()

    if args.TICKER:
        s=CurrentPriceTicker(args.TICKER, args.XULPYMONEY)
        s.get_price()
        print(s)

