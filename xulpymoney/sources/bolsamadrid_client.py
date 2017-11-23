#!/usr/bin/python3
import argparse
import datetime
import time
from decimal import Decimal
import sys
import pytz
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QUrl,  QEventLoop
from PyQt5.QtWebEngineWidgets import QWebEngineView,  QWebEngineProfile

########################## COPIED FUNCTIONS #######################################

#FROM LIBXULPYMONEY
def string2date(iso, type=1):
    """
        date string to date, with type formats
    """
    if type==1: #YYYY-MM-DD
        d=iso.split("-")
        return datetime.date(int(d[0]), int(d[1]),  int(d[2]))
    if type==2: #DD/MM/YYYY
        d=iso.split("/")
        return datetime.date(int(d[2]), int(d[1]),  int(d[0]))


#FROM LIBXULPYMONEY
def string2datetime(s, type):
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

################################################################


class ProductType:
    Share=1
    ETF=4
    PublicBond=7
    PrivateBond=9

class OHCL:
    def __init__(self,isin, xulpymoney):
        self.date=None
        self.open=None
        self.close=None
        self.high=None
        self.low=None
        self.isin=isin
        self.xulpymoney=xulpymoney

    def init__from_html_line(self,line,  productype):
        """
        Returns None if fails    
        """
        try:
            line=line.replace(' class="Ult"', "")#Quita anomalía en td
            line=line.split('"center">')[1]#Removes beginning
            line=line[:-5]#Removes end
            l=line.split("</td><td>")#Arr
            self.date=string2date(l[0], type=2)
            if productype==ProductType.Share:
                self.close=Decimal(l[1].replace(",","."))
                self.open=Decimal(l[2].replace(",","."))
                self.high=Decimal(l[6].replace(",","."))
                self.low=Decimal(l[7].replace(",","."))
            else:
                self.close=Decimal(l[8].replace(",","."))
                self.open=Decimal(l[4].replace(",","."))
                self.high=Decimal(l[5].replace(",","."))
                self.low=Decimal(l[6].replace(",","."))
            return self
        except:
            print (l)
            return None

    def __repr__(self):
        if self.xulpymoney!=None:
            return "OHCL | XULPYMONEY | {} | {} | {} | {} | {} | {}".format(self.xulpymoney, self.date, self.open,self.high,self.close,self.low)
        else:
            return "OHCL | STOCKMARKET | ES | ISIN | {} | {} | {} | {} | {} | {}".format(self.isin, self.date, self.open,self.high,self.close,self.low)

class SetOHCL:
    def __init__(self, isin, xulpymoney, productype):
        self.arr=[]
        self.isin=isin
        self.xulpymoney=xulpymoney
        self.productype=productype

    def searchQuotesInHtml(self,html):
        """Looks for quotes line in html and creates ohcl"""
        for line in html.split("\n"):
            if line.find('<td align="center">')!=-1:
                ohcl=OHCL(self.isin,  self.xulpymoney).init__from_html_line(line, self.productype)
                if ohcl!=None:
                    self.arr.append(ohcl)

    def get_prices( self, from_date):

        class Render(QWebEngineView):
            def __init__(self, url, from_date):
                QWebEngineView.__init__(self)
                self.loop=QEventLoop()#Queda en un loop hasta que acaba la carga de todas las páginas
                self.loadFinished.connect(self._loadFinished)
                self.pages=[]
                self.from_date=from_date
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
                self.pages.append(data)
                time.sleep(0.125)

                if self.numPages()==1:
                    self.page().runJavaScript('''
                                                 var dDia = document.getElementsByName("ctl00$Contenido$Desde$Dia")[0]; dDia.value={};
                                                 var dMes = document.getElementsByName("ctl00$Contenido$Desde$Mes")[0]; dMes.value={};
                                                 var dAnio = document.getElementsByName("ctl00$Contenido$Desde$Año")[0]; dAnio.value={};
                                                 var Button = document.getElementsByName("ctl00$Contenido$Buscar")[0]; Button.click();
                                              '''.format(self.from_date.day,self.from_date.month,self.from_date.year))
                else:
                    if data.find("ctl00_Contenido_SiguientesAbj")!=-1:
                        self.page().runJavaScript('var link= document.getElementById("ctl00_Contenido_SiguientesAbj"); link.click();')
                    else:
                        self.loop.quit()#CUIDADO DEBE ESTAR EN EL ULTIMO
        ###########################
        if self.productype==ProductType.Share:
            r=Render("http://www.bolsamadrid.es/esp/aspx/Empresas/InfHistorica.aspx?ISIN={}".format(self.isin), from_date)
        else:
            r=Render("http://www.bolsamadrid.es/esp/aspx/ETFs/Mercados/InfHistorica.aspx?ISIN={}".format(self.isin), from_date)

        for i,page in enumerate(r.pages):
            if i==0:#Era la de la búsqueda
                continue
            #print ("Page", i+1, len(r.pages[i]))
            self.searchQuotesInHtml(page)

    def print(self):
        for ohcl in self.arr:
            print (ohcl)


class CurrentPrice:
    def __init__(self):
        self.isin=None
        self.xulpymoney=None
        self.datetime_aware=None
        self.price=None

    def init__from_html_line(self,line,  productype, datetime_aware):
        """
        Returns None if fails    
        """
        self.datetime_aware=datetime_aware
        try:
            l=line.split("</td>")#Arr
            if productype==ProductType.PublicBond:
                self.isin=l[1][-12:]
                self.price=Decimal(l[4].split(">")[1].replace(",","."))
            return self
        except:
            print (l)
            return None

    def __repr__(self):
        if self.xulpymoney!=None:
            return "OHCL | XULPYMONEY | {} | {} | {}".format(self.xulpymoney, self.datetime_aware, self.price)
        else:
            return "PRICE | STOCKMARKET | ES | ISIN | {} | {} | {}".format(self.isin, self.datetime_aware , self.price)

class SetCurrentPrice:
    def __init__(self, arrIsin, arrXulpymoney,  productype):
        """
           arrIsin is a list of isin of the same productype
        """
        self.arrIsin=arrIsin
        self.arrXulpymoney=arrXulpymoney
        self.arr=[]
        self.productype=productype

    def searchQuotesInHtml(self,html):
        """Looks for quotes line in html and creates all current prices in the pages"""
        for line in html.split("\n"):#Extracts datetime
            if line.find("sh_titulo")!=-1:
                z=pytz.timezone("Europe/Madrid")
                a=string2datetime(line.split(">")[1].split("<")[0], type=2)
                dt_aware=z.localize(a)
                break

        for line in html.split("\n"):
            if line.find('000.000')!=-1:
                cp=CurrentPrice().init__from_html_line(line, self.productype,dt_aware)
                if cp!=None:
                    self.arr.append(cp)

    def get_prices( self):
        class RenderCurrentPrice(QWebEngineView):
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
                self.page().toHtml(self._callable)

            def _callable(self, data):
                self.pages.append(data)
                time.sleep(0.25)

                if self.numPages()==1:
                    self.page().runJavaScript('''window.location.href="/esp/aspx/aiaf/Precios.aspx?menu=47"''')
                elif self.numPages()==2:
                    self.page().runJavaScript('''window.location.href="/esp/aspx/send/posicionesDPublica_v2.aspx"''')
                elif self.numPages()==3:
                    self.loop.quit()#CUIDADO DEBE ESTAR EN EL ULTIMO
        ###########################
        if self.productype==ProductType.PublicBond:
            r=RenderCurrentPrice("http://www.bmerf.es")
        else:
            r=RenderCurrentPrice("http://www.bolsamadrid.es/esp/aspx/ETFs/Mercados/InfHistorica.aspx?ISIN={}".format(self.isin))
            
        for i,page in enumerate(r.pages):
            #print ("Page", i+1, len(r.pages[i]))
            if i<2:#Era la de la búsqueda
                continue
            self.searchQuotesInHtml(page)

    def returnDesired(self):
        """
           Returns desired Quotes
        """
        desired=[]
        for i, isin in enumerate(self.arrIsin):
            for cp in self.arr:
                 if cp.isin==isin:
                     if self.arrXulpymoney!=None:
                        cp.xulpymoney=self.arrXulpymoney[i]
                     desired.append(cp)
        return desired

    def print(self):
        for cp in self.arr:
            print (cp)

if __name__=="__main__":
    app = QApplication(sys.argv)
    parser=argparse.ArgumentParser("xulpymoney_sync_quotes")
    parser.add_argument('--ISIN', help='ISIN code',action="append")
    parser.add_argument('--XULPYMONEY', help='XULPYMONEY code',action="append")
    parser.add_argument('--fromdate', help='Get data from date in YYYY-MM-DD format', default=str(datetime.date.today()-datetime.timedelta(days=30)))
    group=parser.add_mutually_exclusive_group()
    group.add_argument('--share', help="Share search", action='store_true', default=False)
    group.add_argument('--etf', help="ETF search", action='store_true', default=False) 
    group.add_argument('--publicbond', help="Public bond search", action='store_true', default=False) 
    args=parser.parse_args()

    if len(args.ISIN)!=1 and (args.share==True or args.etf==True):
        print("ERROR | TOO MANY ISIN CODES")
        sys.exit(0)

    try:
        fromdate=string2date(args.fromdate)
    except:
        print("ERROR | FROM DATE CONVERSION ERROR")
        sys.exit(0)

    if args.share==True:
        if args.XULPYMONEY==None:
            xulpymoney=None
        else:
            xulpymoney=args.XULPYMONEY[0]
        s=SetOHCL(args.ISIN[0], xulpymoney, ProductType.Share)
        s.get_prices(fromdate)
        s.print()

    if args.etf==True:
        if args.XULPYMONEY==None:
            xulpymoney=None
        else:
            xulpymoney=args.XULPYMONEY[0]
        s=SetOHCL(args.ISIN[0], xulpymoney, ProductType.ETF)
        s.get_prices(fromdate)
        s.print()

    if args.publicbond==True:
        s=SetCurrentPrice(args.ISIN, args.XULPYMONEY, ProductType.PublicBond)
        s.get_prices()
        for pc in s.returnDesired():
            print (pc)

