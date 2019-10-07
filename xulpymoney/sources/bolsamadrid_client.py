import argparse
import time
from decimal import Decimal
import sys
import platform
if platform.system()=="Windows":
    sys.path.append("ui/")
    sys.path.append("images/")
else:
    sys.path.append("/usr/lib/xulpymoney")
from PyQt5.QtCore import QUrl,  QEventLoop
from PyQt5.QtWebEngineWidgets import QWebEngineView,  QWebEngineProfile
from xulpymoney.datetime_functions import string2date, string2dtaware
from xulpymoney.libxulpymoneytypes import eProductType
from xulpymoney.mem import MemSources

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
            line=line.replace(".", "")#Elimina ceros de miles
            l=line.split("</td><td>")#Arr
            self.date=string2date(l[0], "DD/MM/YYYY")
            if productype==eProductType.Share:
                self.close=Decimal(l[1].replace(",","."))
                self.open=Decimal(l[2].replace(",","."))
                self.high=Decimal(l[6].replace(",","."))
                self.low=Decimal(l[7].replace(",","."))
            elif productype==eProductType.ETF:
                self.close=Decimal(l[8].replace(",","."))
                self.open=Decimal(l[4].replace(",","."))
                self.high=Decimal(l[5].replace(",","."))
                self.low=Decimal(l[6].replace(",","."))
            elif productype==eProductType.Index:
                self.close=Decimal(l[1].replace(",","."))
                self.open=Decimal(l[2].replace(",","."))
                self.high=Decimal(l[3].replace(",","."))
                self.low=Decimal(l[4].replace(",","."))
            return self
        except:
            print ("ERROR | OHCL COULDN'T HAVE BEING  GENERATED | {}".format(line))
            return None

    def __repr__(self):
        if self.xulpymoney!=None:
            return "OHCL | XULPYMONEY | {} | {} | {} | {} | {} | {}".format(self.xulpymoney, self.date, self.open,self.high,self.close,self.low)
        else:
            return "OHCL | STOCKMARKET | ES | ISIN | {} | {} | {} | {} | {} | {}".format(self.isin, self.date, self.open,self.high,self.close,self.low)

class SetOHCL:
    def __init__(self, isin, xulpymoney, productype):
        self.arr=[]
        self.isin=isin# Is a value, not a list
        self.xulpymoney=xulpymoney#Is a value, not a list
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
        if self.productype==eProductType.Share:
            r=Render("http://www.bolsamadrid.es/esp/aspx/Empresas/InfHistorica.aspx?ISIN={}".format(self.isin), from_date)
        elif self.productype==eProductType.ETF:
            r=Render("http://www.bolsamadrid.es/esp/aspx/ETFs/Mercados/InfHistorica.aspx?ISIN={}".format(self.isin), from_date)
        elif self.productype==eProductType.Index:
            r=Render("http://www.bolsamadrid.es/esp/aspx/Indices/InfHistorica.aspx?grupo=IBEX", from_date)
        for i,page in enumerate(r.pages):
            if i==0:#Era la de la búsqueda
                continue
            self.searchQuotesInHtml(page)

    def print(self):
        for ohcl in self.arr:
            print (ohcl)


class CurrentPrice:
    def __init__(self):
        self.isin=None
        self.xulpymoney=None 
        self.dtaware=None
        self.price=None

    def init__from_html_line_without_date(self,line,  productype, dtaware):
        """
        Returns None if fails    
        """
        self.dtaware=dtaware
        try:
            l=line.split("</td>")#Arr
            if productype==eProductType.PublicBond:
                self.isin=l[1][-12:]
                self.price=Decimal(l[4].split(">")[1].replace(",","."))
            return self
        except:
            print ("ERROR | CURRENT PRICE COULDN'T HAVE BEING  GENERATED | {}".format(line))
            return None
            
    def init__from_html_line_with_date(self, line):
        line=line.split("FichaValor.aspx?ISIN=")[1]#Removes begin
        line=line[:-5]#Removes end
        line=line.replace(' class="DifClIg"', "").replace(' class="DifClSb"', "").replace(' class="DifClBj"', "").replace(' align="center" colspan="2"', "").replace(' class="Ult" align="center"',"").replace(' align="center"',"")#Removes anomalies to live td /td
        a=line.split("</td><td>")
        self.isin=a[0][:12]
        self.price=a[1].replace(",", ".")
        if len(a)==9:#Ignoring suspendido
            if a[8]=="Cierre":
                hour="17:38"
            else:
                hour=a[8]
            self.dtaware=string2dtaware("{} {}".format(a[7], hour), "%d/%m/%Y %H:%M",  "Europe/Madrid")
            return self
        return None

    def __repr__(self):
        if self.xulpymoney!=None:
            return "PRICE | XULPYMONEY | {} | {} | {}".format(self.xulpymoney, self.dtaware, self.price)
        else:
            return "PRICE | STOCKMARKET | ES | ISIN | {} | {} | {}".format(self.isin, self.dtaware , self.price)

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
        if self.productype==eProductType.PublicBond:
            for line in html.split("\n"):#Extracts datetime
                if line.find("sh_titulo")!=-1:
                    dt_aware=string2dtaware(line.split(">")[1].split("<")[0], "%d/%m/%Y %H:%M", "Europe/Madrid")
                    break
            for line in html.split("\n"):
                if line.find('000.000')!=-1:
                    cp=CurrentPrice().init__from_html_line_without_date(line, self.productype,dt_aware)
                    if cp!=None:
                        self.arr.append(cp)
                        
        elif self.productype in [eProductType.Share, eProductType.ETF]:
            for line in html.split("\n"):
                if line.find("FichaValor")!=-1:
                    cp=CurrentPrice().init__from_html_line_with_date(line)
                    if cp!=None:
                        self.arr.append(cp)

    def get_prices( self):
        class RenderCurrentPrice(QWebEngineView):
            def __init__(self, url, productype):
                QWebEngineView.__init__(self)
                self.loop=QEventLoop()#Queda en un loop hasta que acaba la carga de todas las páginas
                self.loadFinished.connect(self._loadFinished)
                self.pages=[]
                self.productype=productype
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
                if self.productype==eProductType.PublicBond:
                    if self.numPages()==1:
                        self.page().runJavaScript('''window.location.href="/esp/aspx/aiaf/Precios.aspx?menu=47"''')
                    elif self.numPages()==2:
                        self.page().runJavaScript('''window.location.href="/esp/aspx/send/posicionesDPublica_v2.aspx"''')
                    elif self.numPages()==3:
                        self.loop.quit()#CUIDADO DEBE ESTAR EN EL ULTIMO
                elif self.productype==eProductType.Share:
                    if self.numPages()==1:
                        self.page().runJavaScript('''
                                                var select= document.getElementsByName("ctl00$Contenido$SelMercado")[0]; select.value="MC";
                                                var Button = document.getElementsByName("ctl00$Contenido$Consultar")[0]; Button.click();''')
                    elif self.numPages()==2:
                        self.page().runJavaScript('''__doPostBack("ctl00$Contenido$Todos","");''')
                    elif self.numPages()==3:
                        self.loop.quit()#CUIDADO DEBE ESTAR EN EL ULTIMO
                elif self.productype==eProductType.ETF:
                    if self.numPages()==1:
                        self.page().runJavaScript('''
                                                var select= document.getElementsByName("ctl00$Contenido$SelMercado")[0]; select.value="ETF";
                                                var Button = document.getElementsByName("ctl00$Contenido$Consultar")[0]; Button.click();''')
                    elif self.numPages()==2:
                        self.loop.quit()#CUIDADO DEBE ESTAR EN EL ULTIMO
        ###########################
        if self.productype==eProductType.PublicBond:
            r=RenderCurrentPrice("http://www.bmerf.es", self.productype)
        elif self.productype in [eProductType.Share,  eProductType.ETF]:
            r=RenderCurrentPrice("http://www.bolsamadrid.es/esp/aspx/Mercados/Precios.aspx?indice=ESI100000000", self.productype)
            
        for i,page in enumerate(r.pages):
#            print ("Page", i+1, len(r.pages[i]))
            if self.productype in [eProductType.Share, eProductType.PublicBond]:
                if i<2:#Era la de la búsqueda
                    continue
            elif self.productype==eProductType.ETF:
                if i<1:
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

def main():
    global mem
    mem=MemSources(coreapplication=False)
    parser=argparse.ArgumentParser("xulpymoney_sync_quotes")
    mem.addCommonToArgParse(parser)
    group1=parser.add_mutually_exclusive_group(required=True)
    group1.add_argument('--ISIN', help='ISIN code',action="append", metavar="X")
    group1.add_argument('--ISIN_XULPYMONEY', help='Pass ISIN and XULPYMONEY code',action="append", nargs=2, metavar="X")
    parser.add_argument('--fromdate', help='Get historcal prices from date in YYYY-MM-DD format. Without this parameter it gets current price')
    group2=parser.add_mutually_exclusive_group(required=True)
    group2.add_argument('--share', help="Share search", action='store_true', default=False)
    group2.add_argument('--index', help="Index search", action='store_true', default=False) 
    group2.add_argument('--etf', help="ETF search", action='store_true', default=False) 
    group2.add_argument('--publicbond', help="Public bond search", action='store_true', default=False) 

    args=parser.parse_args() 
    mem.addDebugSystem(args.debug)

    #Array ISIN and XULPYMONEY. If no xulpymoney it creates a list of None values
    ISIN=[]
    XULPYMONEY=[]
    if args.ISIN:
        for isin in args.ISIN:
            ISIN.append(isin)
            XULPYMONEY.append(None)
    else:#ISIN_XULPYMONEY
        for isin, xulpymoney in args.ISIN_XULPYMONEY:
            ISIN.append(isin)
            XULPYMONEY.append(xulpymoney)

    if len(ISIN)>1 and args.fromdate:
        print("ERROR | TOO MANY ISIN CODES | {}".format(sys.argv))
        sys.exit(0)

    if args.fromdate:
        try:
            fromdate=string2date(args.fromdate)
        except:
            print("ERROR | FROM DATE CONVERSION ERROR | {}".format(args.fromdate))
            sys.exit(0)

        if args.share==True:
            s=SetOHCL(ISIN[0], XULPYMONEY[0], eProductType.Share)
            s.get_prices(fromdate)
            s.print()

        if args.etf==True:
            s=SetOHCL(ISIN[0], XULPYMONEY[0], eProductType.ETF)
            s.get_prices(fromdate)
            s.print()

        if args.index==True:
            s=SetOHCL(ISIN[0], XULPYMONEY[0], eProductType.Index)
            s.get_prices(fromdate)
            s.print()
    else:
        if args.publicbond==True:
            s=SetCurrentPrice(ISIN, XULPYMONEY, eProductType.PublicBond)
            s.get_prices()
            for pc in s.returnDesired():
                print (pc)

        if args.share==True:
            s=SetCurrentPrice(ISIN, XULPYMONEY, eProductType.Share)
            s.get_prices()
            for pc in s.returnDesired():
                print (pc)
        if args.etf==True:
            s=SetCurrentPrice(ISIN, XULPYMONEY, eProductType.ETF)
            s.get_prices()
            for pc in s.returnDesired():
                print (pc)

