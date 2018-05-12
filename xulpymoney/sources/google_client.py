#!/usr/bin/python3
import argparse
import datetime
from requests import get
from decimal import Decimal
import sys
import platform
if platform.system()=="Windows":
    sys.path.append("ui/")
    sys.path.append("images/")
else:
    sys.path.append("/usr/lib/xulpymoney")
from libxulpymoneyfunctions import string2datetime, month2int        
        
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
        #try:
        url = 'http://www.google.com/search?q={}'.format(self.ticker)    # fails
        web=get(url).text
#        web=urlopen('https://www.google.com/search?q=NYSE%3AMMM')#.format(self.ticker))
        #except:
        #    print ("ERROR | ERROR LOADING GOOGLE PAGE")
        #    sys.exit(255)

        if web==None:
            print ("ERROR | FETCHED EMPTY PAGE")
            sys.exit(255)

        if web.find('font-size:157%"><b>')!=-1:
            try:
                web=web.split('font-size:157%"><b>')[1]#Antes
                web=web.split('</span> - <a class="fl"')[0]#Después
                price=Decimal(web.split("</b>")[0].replace(".","").replace(",","."))
                datestr=web.split('<span class="f">')[1].replace(".","")
                zone=web.split('<span class="f">')[1].split(" ")[3]
                if zone.find("GMT")!=-1:
                    zone="Etc/{}".format(zone)
                datestr=datestr[:4].upper()+datestr[4:13]+str(datetime.date.today().year)
                month=datestr.split(" ")[1]
                datestr=datestr.replace(month, str(month2int(month)))
#                print(datestr)
                self.datetime_aware=string2datetime(datestr, type=4, zone=zone)
                self.price=price
            except:
                print("ERROR | COULDN'T CONVERT DATATIME {} AND PRICE {}".format(datestr,price))
                sys.exit(0)
            return

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    group1=parser.add_mutually_exclusive_group(required=True)
    group1.add_argument('--TICKER_XULPYMONEY', help='XULPYMONEY code', nargs=2, metavar="VALUE")
    args=parser.parse_args()

    if args.TICKER_XULPYMONEY:
        s=CurrentPriceTicker(args.TICKER_XULPYMONEY[0], args.TICKER_XULPYMONEY[1])
        s.get_price()
        print(s)

