#!/usr/bin/python3
import argparse
import datetime
from requests import get
from decimal import Decimal
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
            web=web.split('font-size:157%"><b>')[1]#Antes
            web=web.split('</span> - <a class="fl"')[0]#Después
            #print (web)
            self.price=Decimal(web.split("</b>")[0].replace(".","").replace(",","."))
            datestr=web.split('<span class="f">')[1].replace(".","")
            zone=web.split('<span class="f">')[1].split(" ")[3]
            if zone.find("GMT")!=-1:
                zone="Etc/{}".format(zone)
            #print (zone)
            datestr=datestr[:4].upper()+datestr[4:13]+str(datetime.date.today().year)
            #print(datestr)
            self.datetime_aware=string2datetime(datestr, type=4, zone=zone)
            return
        print ("ERROR | ERROR PARSING")

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    group1=parser.add_mutually_exclusive_group(required=True)
    group1.add_argument('--TICKER_XULPYMONEY', help='XULPYMONEY code', nargs=2, metavar="VALUE")
    args=parser.parse_args()

    if args.TICKER_XULPYMONEY:
        s=CurrentPriceTicker(args.TICKER_XULPYMONEY[0], args.TICKER_XULPYMONEY[1])
        s.get_price()
        print(s)

