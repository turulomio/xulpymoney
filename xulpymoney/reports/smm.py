import os, sys, glob, datetime, psycopg2, psycopg2.extras, shutil
import pkg_resources
import argparse
import datetime
import getpass
import gettext
from xulpymoney.version import __version__, __versiondate__
from xulpymoney.connection_pg import Connection
from xulpymoney.libmanagers import ObjectManager
from xulpymoney.libxulpymoney import Product, Zone, StockMarket
from officegenerator import ODS_Write, Coord


try:
    t=gettext.translation('xulpymoney',pkg_resources.resource_filename("xulpymoney","locale"))
    _=t.gettext
except:
    _=str


class Mem:
    def __init__(self):
        self.con=Connection()

class DV:
    def __init__(self):
        self.date=None
        self.value=None

    def __repr__(self):
        return "DV {} = {}".format(self.date,self.value)

class SmmManager(ObjectManager):
    def __init__(self,ohcldailymanager,periods):
        ObjectManager.__init__(self)
        self.periods=periods
        for i in range(self.periods-1, ohcldailymanager.length()):
            smm=DV()
            smm.date=ohcldailymanager.arr[i].date
            smm.value=0
            for p in range(self.periods):
                smm.value=smm.value+ohcldailymanager.arr[i-p].close
            smm.value=smm.value/self.periods
            self.append(smm)

    def find_by_date(self,date):
        for o in self.arr:
            if o.date==date:
                return o
        return None

class SmmDiffManager(ObjectManager):
    def __init__(self,smmm):
        ObjectManager.__init__(self)
        for i in range(1,smmm.length()):
            diff=DV()
            diff.date=smmm.arr[i].date
            diff.value=smmm.arr[i].value-smmm.arr[i-1].value
            self.append(diff)
    def find_by_date(self,date):
        for o in self.arr:
            if o.date==date:
                return o
        return None

## Almacena diff values
class Racha(ObjectManager):
    def __init__(self,ohcldailymanager):
        ObjectManager.__init__(self)
        self.ohcldailymanager=ohcldailymanager

    def __repr__(self):
        if self.is_positive():
            return "Racha positiva {}:{} con {} diffs".format(self.arr[0].date, self.arr[self.length()-1].date, self.length())
        else:
            return "Racha negativa {}:{} con {} diffs".format(self.arr[0].date, self.arr[self.length()-1].date, self.length())

#    ## CREO QUE MAL
#    def diff(self):
#        return self.ohcldailymanager.find(self.arr[self.length()-1].date).close-self.ohcldailymanager.find(self.arr[0].date).close

    def is_positive(self):
        if self.arr[0].value>=0:
            return True
        return False


## Almacena diff values
class RachaManager(ObjectManager):
    def __init__(self,ohcldailymanager):
        ObjectManager.__init__(self)
        self.ohcldailymanager=ohcldailymanager
   
    def suma_contenido_rachas(self):
        r=0
        for racha in self.arr:
            r=r+racha.length()
        return r

    ## Diferencia del ohcl, es decir del producto
    def diffProduct(self,racha):
        ind=self.arr.index(racha)
        if ind==self.length()-1:
            primera_fecha_racha_actual=racha.arr[0].date
            primera_fecha_racha_siguiente=racha.arr[racha.length()-1].date
        else:
            racha_siguiente=self.arr[ind+1]
            primera_fecha_racha_actual=racha.arr[0].date
            primera_fecha_racha_siguiente=racha_siguiente.arr[0].date
        ohcl_primera_fecha_racha_actual=self.ohcldailymanager.find(primera_fecha_racha_actual).close
        ohcl_primera_fecha_racha_siguiente=self.ohcldailymanager.find(primera_fecha_racha_siguiente).close
        return ohcl_primera_fecha_racha_siguiente-ohcl_primera_fecha_racha_actual

    ## Se resta el primera de la siguiente racha que es el precio en el que ha cambiado el signo del cdf, con el primer precio de la racha, que fue cando cambie el signo del cdf
    ## Se evalua si estoy a cortos o a largos
    def diffRacha(self,racha):
        value= self.diffProduct(racha)
        if racha.is_positive()==True and value>=0:
            return value
        elif racha.is_positive()==True and value<0:
            return value
        elif racha.is_positive()==False and value>=0:
            return -value
        elif racha.is_positive()==False and value<0:
            return -value

    def suma_diffs_year(self,year):
        r=0
        for racha in self.arr:
            if racha.arr[0].date.year==year:
                r=r+self.diffRacha(racha)
        return r


### MAIN SCRIPT ###
def main(parameters=None):
    parser=argparse.ArgumentParser(prog='xulpymoney', description=_('Generate your personal movie collection book'), epilog=_("Developed by Mariano Muñoz 2012-{}".format(__versiondate__.year)), formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--version', action='version', version=__version__)

    group = parser.add_argument_group("productrequired=True")
    group.add_argument('--id', help=_('Insert films from current numbered directory'), action="store", default=79329)
    group.add_argument('--periods', help=_('Insert films from current numbered directory'), action="store", default=5)

    group_db=parser.add_argument_group(_("Postgres database connection parameters"))
    group_db.add_argument('--user', help=_('Postgresql user'), default='postgres')
    group_db.add_argument('--port', help=_('Postgresql server port'), default=5432)
    group_db.add_argument('--server', help=_('Postgresql server address'), default='127.0.0.1')
    group_db.add_argument('--db', help=_('Postgresql database'), default='xulpymoney')

    mem=Mem()
    global args
    args=parser.parse_args(parameters)
    args.periods=int(args.periods)
    args.id=int(args.id)


    mem.con.user=args.user
    mem.con.server=args.server
    mem.con.port=args.port
    mem.con.db=args.db

    print(_("Write the password for {}").format(mem.con.url_string()))
    mem.con.password=getpass.getpass()
    mem.con.connect()

    strdate=str(datetime.date.today()).replace("-","")
    doc=ODS_Write("{} Xulpymoney Report. SMM{}.ods".format(strdate,args.periods))
    doc.setMetadata("Xulpymoney SMM Report",  "SMM report", "Xulpymoney-{}".format(__version__))
    s1=doc.createSheet("MM5")
    s1.add("A1",[["Fecha","Ibex35","MMS5","Diff","Diff racha", "Gains"]], "OrangeCenter")
    product=Product(mem)
    product.id=args.id
    #product.zone=Zone(mem,1,'Europe/Madrid', None)
    #product.stockmarket=StockMarket(mem).init__create( 1, "Bolsa de Madrid", "es", datetime.time(9, 0), datetime.time(17, 38), "Europe/Madrid")
    product.needStatus(2)

    smmm=SmmManager(product.result.ohclDaily, args.periods)
    smmdm=SmmDiffManager(smmm)

    racham=RachaManager(product.result.ohclDaily)
    racha=Racha(product.result.ohclDaily)
    racham.append(racha)
    for i, o in enumerate(smmdm.arr):
        s1.add(Coord("A2").addRow(i), o.date, "WhiteDate")
        s1.add(Coord("B2").addRow(i), product.result.ohclDaily.find(o.date).close, "WhiteDecimal2")
        s1.add(Coord("C2").addRow(i), smmm.find_by_date(o.date).value, "WhiteDecimal2")
        s1.add(Coord("D2").addRow(i), o.value, "WhiteDecimal2")

        if racha.length()==0:
            racha.append(o)
        elif o.value>=0 and racha.arr[0].value>=0:
            racha.append(o)
        elif o.value<0 and racha.arr[0].value<0:
            racha.append(o)
        elif o.value>=0 and racha.arr[0].value<0:
            racha=Racha(product.result.ohclDaily)
            racha.append(o)
            racham.append(racha)
        elif o.value<0 and racha.arr[0].value>=0:
            racha=Racha(product.result.ohclDaily)
            racha.append(o)
            racham.append(racha)
    s1.setCursorPosition(Coord("A1").addRow(smmdm.length()))
    s1.setSplitPosition(Coord("A2"))


    s2=doc.createSheet("Rachas")
    s2.add("A1",[["Desde","Hasta","Días","Diff Product", "Gains Product"]], "OrangeCenter")

    for i, racha in enumerate(racham.arr):
        s2.add(Coord("A2").addRow(i), racha.arr[0].date, "WhiteDate")
        s2.add(Coord("B2").addRow(i), racha.arr[racha.length()-1].date, "WhiteDate")
        s2.add(Coord("C2").addRow(i), (racha.arr[racha.length()-1].date-racha.arr[0].date).days, "WhiteInteger")
        s2.add(Coord("D2").addRow(i), racham.diffProduct(racha), "WhiteDecimal2")
        s2.add(Coord("E2").addRow(i), racham.diffRacha(racha), "WhiteDecimal2")
        sentido="LARGOS" if racha.is_positive() else "CORTOS"
        s2.add(Coord("F2").addRow(i), sentido, "WhiteDecimal2")


    for year in range(datetime.date.today().year-10,datetime.date.today().year+1):
         print("{}: {}".format(year,racham.suma_diffs_year(year)))

    print ("Hay {} ohcls".format(product.result.ohclDaily.length()))
    print ("Hay {} diffs".format(smmdm.length()))
    print ("Hay {} rachas".format(racham.length()))
    print ("Hay {} diffs en rachas".format(racham.suma_contenido_rachas()))
    mem.con.disconnect()

    doc.save()