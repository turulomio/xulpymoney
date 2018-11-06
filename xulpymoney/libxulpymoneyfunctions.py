## @package libxulpymoneyfunctions
## @brief Package with all xulpymoney auxiliar functions.
from PyQt5.QtCore import Qt,  QCoreApplication, QLocale
from PyQt5.QtGui import QIcon,  QColor
from PyQt5.QtWidgets import QTableWidgetItem,  QWidget,  QMessageBox, QApplication, QCheckBox, QHBoxLayout
from decimal import Decimal
from os import path, makedirs
import datetime
import functools
import warnings
import inspect
import logging
import pytz
import sys
from xulpymoney.version import __version__, __versiondate__

## Sets debug sustem, needs
## @param args It's the result of a argparse     args=parser.parse_args()        
def addDebugSystem(args):
    logFormat = "%(asctime)s.%(msecs)03d %(levelname)s %(message)s [%(module)s:%(lineno)d]"
    dateFormat='%F %I:%M:%S'

    if args.debug=="DEBUG":#Show detailed information that can help with program diagnosis and troubleshooting. CODE MARKS
        logging.basicConfig(level=logging.DEBUG, format=logFormat, datefmt=dateFormat)
    elif args.debug=="INFO":#Everything is running as expected without any problem. TIME BENCHMARCKS
        logging.basicConfig(level=logging.INFO, format=logFormat, datefmt=dateFormat)
    elif args.debug=="WARNING":#The program continues running, but something unexpected happened, which may lead to some problem down the road. THINGS TO DO
        logging.basicConfig(level=logging.WARNING, format=logFormat, datefmt=dateFormat)
    elif args.debug=="ERROR":#The program fails to perform a certain function due to a bug.  SOMETHING BAD LOGIC
        logging.basicConfig(level=logging.ERROR, format=logFormat, datefmt=dateFormat)
    elif args.debug=="CRITICAL":#The program encounters a serious error and may stop running. ERRORS
        logging.basicConfig(level=logging.CRITICAL, format=logFormat, datefmt=dateFormat)

    logging.info("Debug level set to {}".format(args.debug))
    
## Adds the commons parameter of the program to argparse
## @param parser It's a argparse.ArgumentParser
def addCommonToArgParse(parser):
    parser.add_argument('--version', action='version', version="{} ({})".format(__version__, __versiondate__))
    parser.add_argument('--debug', help="Debug program information", choices=["DEBUG","INFO","WARNING","ERROR","CRITICAL"], default="ERROR")

## Function to conver hour strings with AM/PM to a iso string time
## @param s Is a string for time with AMPM and returns a 24 hours time string with zfill. AM/PM can be upper or lower case
## @param type Integer that can have this options 1: "5:35PM"
## @return String with hour in iso mode: "17:35"
def ampm2stringtime(s, type):
    s=s.upper()
    if type==1:#5:35PM > 17:35   ó 5:35AM > 05:35
        s=s.replace("AM", "")
        if s.find("PM"):
            s=s.replace("PM", "")
            points=s.split(":")
            s=str(int(points[0])+12).zfill(2)+":"+points[1]
        else:#AM
            points=s.split(":")
            s=str(int(points[0])).zfill(2)+":"+points[1]
        return s

## Changes zoneinfo from a dtaware object
## For example:
## - datetime.datetime(2018, 5, 18, 8, 12, tzinfo=<DstTzInfo 'Europe/Madrid' CEST+2:00:00 DST>)
## - libxulpymoneyfunctions.dtaware_changes_tz(a,"Europe/London")
## - datetime.datetime(2018, 5, 18, 7, 12, tzinfo=<DstTzInfo 'Europe/London' BST+1:00:00 DST>)
## @param dt datetime aware object
## @tzname String with datetime zone. For example: "Europe/Madrid"
## @return datetime aware object
def dtaware_changes_tz(dt,  tzname):
    if dt==None:
        return None
    tzt=pytz.timezone(tzname)
    tarjet=tzt.normalize(dt.astimezone(tzt))
    return tarjet

## Creates a QTableWidgetItem with the date
def qdate(date):
    if date==None:
        return qempty()
    return qcenter(str(date))

def qmessagebox(text):
    m=QMessageBox()
    m.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
    m.setIcon(QMessageBox.Information)
    m.setText(text)
    m.exec_()   

def sync_data(con_source, con_target, progress=None):
    """con is con_target, 
    progress is a pointer to progressbar
    returns a tuple (numberofproductssynced, numberofquotessynced)"""
    #Checks if database has same version
    cur_target=con_target.cursor()
    cur2_target=con_target.cursor()
    cur_source=con_source.cursor()
    
    
    #Checks if database has same version
    cur_source.execute("select value from globals where id_globals=1")
    cur_target.execute("select value from globals where id_globals=1")
    
    if cur_source.fetchone()[0]!=cur_target.fetchone()[0]:
        logging.critical ("Databases has diferent versions, please update them")
        sys.exit(0)
    
    quotes=0#Number of quotes synced
    estimation_dps=0#Number of estimation_dps synced
    estimation_eps=0#Number of estimation_eps synced
    dps=0
    splits=0 #Number of splits synced
    products=0#Number of products synced
    
    #Iterate all products
    cur_target.execute("select id,name from products where id>0 order by name;")
    logging.info ("Syncing {} products".format (cur_target.rowcount))
    for row in cur_target:
        output="{}: ".format(row['name'])
        ## QUOTES #####################################################################
        #Search last datetime
        cur2_target.execute("select max(datetime) as max from quotes where id=%s", (row['id'], ))
        max=cur2_target.fetchone()[0]
        #Ask for quotes in source with last datetime
        if max==None:#No hay ningun registro y selecciona todos
            cur_source.execute("select * from quotes where id=%s", (row['id'], ))
        else:#Hay registro y selecciona los posteriores a el
            cur_source.execute("select * from quotes where id=%s and datetime>%s", (row['id'], max))
        if cur_source.rowcount!=0:
            print("  - Syncing {} since {} ".format(row['name'], max),end="")
            for  row_source in cur_source: #Inserts them 
                cur2_target.execute("insert into quotes (id, datetime, quote) values (%s,%s,%s)", ( row_source['id'], row_source['datetime'], row_source['quote']))
                quotes=quotes+1
                output=output+"."
                
        ## DPS ################################################################################
        #Search last datetime
        cur2_target.execute("select max(date) as max from dps where id=%s", (row['id'], ))
        max=cur2_target.fetchone()[0]
        #Ask for quotes in source with last datetime
        if max==None:#No hay ningun registro y selecciona todos
            cur_source.execute("select * from dps where id=%s", (row['id'], ))
        else:#Hay registro y selecciona los posteriores a el
            cur_source.execute("select * from dps where id=%s and date>%s", (row['id'], max))
        if cur_source.rowcount!=0:
            for  row_source in cur_source: #Inserts them 
                cur2_target.execute("insert into dps (date, gross, id) values (%s,%s,%s)", ( row_source['date'], row_source['gross'], row_source['id']))
                dps=dps+1
                output=output+"-"

        ## DPS ESTIMATIONS #####################################################################
        #Search last datetime
        cur2_target.execute("select max(year) as max from estimations_dps where id=%s", (row['id'], ))
        max=cur2_target.fetchone()[0]
        #Ask for quotes in source with last datetime
        if max==None:#No hay ningun registro y selecciona todos
            cur_source.execute("select * from estimations_dps where id=%s", (row['id'], ))
        else:#Hay registro y selecciona los posteriores a el
            cur_source.execute("select * from estimations_dps where id=%s and year>%s", (row['id'], max))
        if cur_source.rowcount!=0:
            for  row_source in cur_source: #Inserts them 
                cur2_target.execute("insert into estimations_dps (year, estimation, date_estimation, source, manual, id) values (%s,%s,%s,%s,%s,%s)", ( row_source['year'], row_source['estimation'], row_source['date_estimation'], row_source['source'], row_source['manual'],  row_source['id']))
                estimation_dps=estimation_dps+1
                output=output+"+"
                
        ## EPS ESTIMATIONS #####################################################################
        #Search last datetime
        cur2_target.execute("select max(year) as max from estimations_eps where id=%s", (row['id'], ))
        max=cur2_target.fetchone()[0]
        #Ask for quotes in source with last datetime
        if max==None:#No hay ningun registro y selecciona todos
            cur_source.execute("select * from estimations_eps where id=%s", (row['id'], ))
        else:#Hay registro y selecciona los posteriores a el
            cur_source.execute("select * from estimations_eps where id=%s and year>%s", (row['id'], max))
        if cur_source.rowcount!=0:
            for  row_source in cur_source: #Inserts them 
                cur2_target.execute("insert into estimations_eps (year, estimation, date_estimation, source, manual, id) values (%s,%s,%s,%s,%s,%s)", ( row_source['year'], row_source['estimation'], row_source['date_estimation'], row_source['source'], row_source['manual'],  row_source['id']))
                estimation_eps=estimation_eps+1
                output=output+"*"
                
        ## SPLITS  #####################################################################
        #Search last datetime
        cur2_target.execute("select max(datetime) as max from splits where products_id=%s", (row['id'], ))
        max=cur2_target.fetchone()[0]
        #Ask for quotes in source with last datetime
        if max==None:#No hay ningun registro y selecciona todos
            cur_source.execute("select * from splits where products_id=%s", (row['id'], ))
        else:#Hay registro y selecciona los posteriores a el
            cur_source.execute("select * from splits where products_id=%s and datetime>%s", (row['id'], max))
        if cur_source.rowcount!=0:
            for  row_source in cur_source: #Inserts them 
                cur2_target.execute("insert into splits (datetime, products_id, before, after, comment) values (%s,%s,%s,%s,%s)", ( row_source['datetime'], row_source['products_id'], row_source['before'], row_source['after'], row_source['comment']))
                splits=splits+1
                output=output+"s"

        if output!="{}: ".format(row['name']):
            products=products+1
            print(output)
            
        if progress!=None:#If there's a progress bar
            progress.setValue(cur_target.rownumber)
            progress.setMaximum(cur_target.rowcount)
            QCoreApplication.processEvents()
    con_target.commit()
    print("")
    
    if progress!=None:
        s=QCoreApplication.translate("Core", """From {} desynchronized products added:
    - {} quotes
    - {} dividends per share
    - {} dividend per share estimations
    - {} earnings per share estimations
    - {} splits / contrasplits""").format(  products,  quotes, dps, estimation_dps,  estimation_eps, splits)
            
        qmessagebox(s)  
    
def dtaware2epochms(d):
    """
        Puede ser dateime o date
        Si viene con zona datetime zone aware, se convierte a UTC y se da el valor en UTC
        return datetime.datetime.now(pytz.timezone(self.name))
    """
    if d.__class__==datetime.datetime:
        if d.tzname()==None:#unaware datetine
            logging.critical("Must be aware")
        else:#aware dateime changed to unawar
            utc=dtaware_changes_tz(d, 'UTC')
            return utc.timestamp()*1000
    logging.critical("{} can't be converted to epochms".format(d.__class__))
    
## Return a UTC datetime aware
def epochms2dtaware(n):
    utc_unaware=datetime.datetime.utcfromtimestamp(n/1000)
    utc_aware=utc_unaware.replace(tzinfo=pytz.timezone('UTC'))
    return utc_aware


## Returns a formated string of a dtaware string formatting with a zone name
## @param dt datetime aware object
## @param zonename String with a zone name like "Europe/Madrid"
## @return String
def dtaware2string(dt, zonename):
    if dt==None:
        resultado="None"
    else:    
        
        #print (dt,  dt.__class__,  dt.tzinfo, dt.tzname())
        if dt.tzname()==None:
            logging.critical("Datetime should have tzname")
            sys.exit(178)   
        dt=dtaware_changes_tz(dt,  zonename)
        if dt.microsecond==4 :
            resultado="{}-{}-{}".format(dt.year, str(dt.month).zfill(2), str(dt.day).zfill(2))
        else:
            resultado="{}-{}-{} {}:{}:{}".format(dt.year, str(dt.month).zfill(2), str(dt.day).zfill(2), str(dt.hour).zfill(2), str(dt.minute).zfill(2),  str(dt.second).zfill(2))
    return resultado

def deprecated(func):
     """This is a decorator which can be used to mark functions
     as deprecated. It will result in a warning being emitted
     when the function is used."""
     @functools.wraps(func)
     def new_func(*args, **kwargs):
         warnings.simplefilter('always', DeprecationWarning)  # turn off filter
         warnings.warn("Call to deprecated function {}.".format(func.__name__),
                       category=DeprecationWarning,
                       stacklevel=2)
         warnings.simplefilter('default', DeprecationWarning)  # reset filter
         return func(*args, **kwargs)
     return new_func
 
def qdatetime(dt, zone):
    """
        dt es un datetime con timezone, que se mostrara con la zone pasado como parametro
        Convierte un datetime a string, teniendo en cuenta los microsehgundos, para ello se convierte a datetime local
    """
    a=QTableWidgetItem(dtaware2string(dt, zone.name))
    if dt==None:
        return qempty()
    a.setTextAlignment(Qt.AlignVCenter|Qt.AlignRight)
    return a

def qtime(dt):
    """
        Shows the time of a datetime
    """
    if dt==None:
        return qempty()
    if dt.microsecond==5:
        item=qleft(str(dt)[11:-13])
        item.setBackground(QColor(255, 255, 148))
    elif dt.microsecond==4:
        item=qleft(str(dt)[11:-13])
        item.setBackground(QColor(148, 148, 148))
    else:
        item=qleft(str(dt)[11:-6])
    return item
    
def list2string(lista):
        """Covierte lista a string"""
        if  len(lista)==0:
            return ""
        if str(lista[0].__class__) in ["<class 'int'>", "<class 'float'>"]:
            resultado=""
            for l in lista:
                resultado=resultado+ str(l) + ", "
            return resultado[:-2]
        elif str(lista[0].__class__) in ["<class 'str'>",]:
            resultado=""
            for l in lista:
                resultado=resultado+ "'" + str(l) + "', "
            return resultado[:-2]
            
def string2list(s):
    """Convers a string of integer separated by comma, into a list of integer"""
    arr=[]
    if s!="":
        arrs=s.split(",")
        for a in arrs:
            arr.append(int(a))
    return arr
    
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

## Function to generate a datetime (aware or naive) from a string
## @param s String
## @param type Integer
## @param zone Name of the zone. By default "Europe Madrid" only in type 3and 4
## @return Datetime
def string2datetime(s, type, zone="Europe/Madrid"):
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
    if type==4:#27 1 16:54 2017==> Aware, using zone parameter . 1 es el mes convertido con month2int
        dat=datetime.datetime.strptime( s, "%d %m %H:%M %Y")
        z=pytz.timezone(zone)
        return z.localize(dat)
    if type==5:#2017-11-20 23:00:00.000000+00:00  ==> Aware with microsecond
        s=s[:-3]+s[-2:]#quita el :
        arrPunto=s.split(".")
        s=arrPunto[0]+s[-5:]
        micro=int(arrPunto[1][:-5])
        dat=datetime.datetime.strptime( s, "%Y-%m-%d %H:%M:%S%z" )
        dat=dat+datetime.timedelta(microseconds=micro)
        return dat

## Converts a tring 12:23 to a datetime.time object
def string2time(s):
    a=s.split(":")
    return datetime.time(int(a[0]), int(a[1]))

## Bytes 2 string
def b2s(b, code='UTF-8'):
    return b.decode(code)
    
def s2b(s, code='UTF8'):
    """String 2 bytes"""
    if s==None:
        return "".encode(code)
    else:
        return s.encode(code)

def c2b(state):
    """QCheckstate to python bool"""
    if state==Qt.Checked:
        return True
    else:
        return False

def b2c(booleano):
    """Bool to QCheckstate"""
    if booleano==True:
        return Qt.Checked
    else:
        return Qt.Unchecked     

def day_end(dattime, zone):
    """Saca cuando acaba el dia de un dattime en una zona concreta"""
    return dtaware_changes_tz(dattime, zone.name).replace(hour=23, minute=59, second=59)
    
def day_start(dattime, zone):
    return dtaware_changes_tz(dattime, zone.name).replace(hour=0, minute=0, second=0)
    
def day_end_from_date(date, zone):
    """Saca cuando acaba el dia de un dattime en una zona concreta"""
    return dtaware(date, datetime.time(23, 59, 59), zone.name)
    
def day_start_from_date(date, zone):
    return dtaware(date, datetime.time(0, 0, 0), zone.name)
    
def month_start(year, month, zone):
    """datetime primero de un mes
    """
    return day_start_from_date(datetime.date(year, month, 1), zone)
    
def month2int(s):
    """
        Converts a month string to a int
    """
    if s in ["Jan", "Ene", "Enero", "January", "enero", "january"]:
        return 1
    if s in ["Feb", "Febrero", "February", "febrero", "february"]:
        return 2
    if s in ["Mar", "Marzo", "March", "marzo", "march"]:
        return 3
    if s in ["Apr", "Abr", "April", "Abril", "abril", "april"]:
        return 4
    if s in ["May", "Mayo", "mayo", "may"]:
        return 5
    if s in ["Jun", "June", "Junio", "junio", "june"]:
        return 6
    if s in ["Jul", "July", "Julio", "julio", "july"]:
        return 7
    if s in ["Aug", "Ago", "August", "Agosto", "agosto", "august"]:
        return 8
    if s in ["Sep", "Septiembre", "September", "septiembre", "september"]:
        return 9
    if s in ["Oct", "October", "Octubre", "octubre", "october"]:
        return 10
    if s in ["Nov", "Noviembre", "November", "noviembre", "november"]:
        return 11
    if s in ["Dic", "Dec", "Diciembre", "December", "diciembre", "december"]:
        return 12

def month_end(year, month, zone):
    """datetime último de un mes
    """
    return day_end_from_date(month_last_date(year, month), zone)
    
## Returns a date with the last day of a month
## @return datetime.date object
def month_last_date(year, month):
    if month == 12:
        return datetime.date(year, month, 31)
    return datetime.date(year, month+1, 1) - datetime.timedelta(days=1)

## Returns an aware datetime with the start of year
def year_start(year, zone):
    return day_start_from_date(datetime.date(year, 1, 1), zone)
    
## Returns an aware datetime with the last of year
def year_end(year, zone):
    return day_end_from_date(datetime.date(year, 12, 31), zone)
    
## Function that converts a number of days to a string showing years, months and days
## @param days Integer with the number of days
## @return String like " 0 years, 1 month and 3 days"
def days2string(days):
    years=days//365
    months=(days-years*365)//30
    days=int(days -years*365 -months*30)
    if years==1:
        stryears=QApplication.translate("Core", "year")
    else:
        stryears=QApplication.translate("Core", "years")
    if months==1:
        strmonths=QApplication.translate("Core", "month")
    else:
        strmonths=QApplication.translate("Core", "months")
    if days==1:
        strdays=QApplication.translate("Core", "day")
    else:
        strdays=QApplication.translate("Core", "days")
    return QApplication.translate("Core", "{} {}, {} {} and {} {}").format(years, stryears,  months,  strmonths, days,  strdays)


def dirs_create():
    """
        Returns xulpymoney_tmp_dir, ...
    """
    dir_tmp=path.expanduser("~/.xulpymoney/tmp/")
    try:
        makedirs(dir_tmp)
    except:
        pass
    return dir_tmp

## Function to create a datetime aware object
## @param date datetime.date object
## @param hour datetime.hour object
## @param zonename String with datetime zone name. For example "Europe/Madrid"
## @return datetime aware
def dtaware(date, hour, zonename):
    z=pytz.timezone(zonename)
    a=datetime.datetime(date.year,  date.month,  date.day,  hour.hour,  hour.minute,  hour.second, hour.microsecond)
    a=z.localize(a)
    return a
    
## Converts strings True or False to boolean
## @param s String
## @return Boolean
def str2bool(s):
    if s=="True":
        return True
    return False    
## Converts boolean to  True or False string
## @param s String
## @return Boolean
def bool2string(b):
    if b==True:
        return "VERDADERO"
    return "FALSO"
    
def none2decimal0(s):
    if s==None:
        return Decimal('0')
    return s

def qbool(bool):
    """Prints bool and check. Is read only and enabled"""
    if bool==None:
        return qempty()
    a=QTableWidgetItem()
    a.setFlags( Qt.ItemIsSelectable |  Qt.ItemIsEnabled )#Set no editable
    if bool:
        a.setCheckState(Qt.Checked);
        a.setText(QApplication.translate("Core","True"))
    else:
        a.setCheckState(Qt.Unchecked);
        a.setText(QApplication.translate("Core","False"))
    a.setTextAlignment(Qt.AlignVCenter|Qt.AlignCenter)
    return a
    
def wdgBool(bool):
    """Center checkbox
    Yo must use with table.setCellWidget(0,0,wdgBool)
    Is disabled to be readonly"""
    pWidget = QWidget()
    pCheckBox = QCheckBox();
    if bool:
        pCheckBox.setCheckState(Qt.Checked);
    else:
        pCheckBox.setCheckState(Qt.Unchecked);
    pLayout = QHBoxLayout(pWidget);
    pLayout.addWidget(pCheckBox);
    pLayout.setAlignment(Qt.AlignCenter);
    pLayout.setContentsMargins(0,0,0,0);
    pWidget.setLayout(pLayout);
    pCheckBox.setEnabled(False)
    return pWidget
    
## Returns a QTableWidgetItem representing an empty value
def qempty():
    a=QTableWidgetItem("---")
    a.setTextAlignment(Qt.AlignVCenter|Qt.AlignRight)
    return a

def qcenter(string, digits=None):
    if string==None:
        return qempty()
    a=QTableWidgetItem(str(string))
    a.setTextAlignment(Qt.AlignVCenter|Qt.AlignCenter)
    return a
    
def qleft(string):
    if string==None:
        return qempty()
    a=QTableWidgetItem(str(string))
    a.setTextAlignment(Qt.AlignVCenter|Qt.AlignLeft)
    return a

def qright(string, digits=None):
    """When digits, limits the number to """
    if string==None:
        return qempty()
    if string!=None and digits!=None:
        string=round(string, digits)
    a=QTableWidgetItem(str(string))
    a.setTextAlignment(Qt.AlignVCenter|Qt.AlignRight)
    try:#If is a number corized it
        if string==None:
            a.setForeground(QColor(0, 0, 255))
        elif string<0:
            a.setForeground(QColor(255, 0, 0))
    except:
        pass
    return a
        
def web2utf8(cadena):
    cadena=cadena.replace('&#209;','Ñ')
    cadena=cadena.replace('&#241;','ñ')
    cadena=cadena.replace('&#252;','ü')
    cadena=cadena.replace('&#246;','ö')
    cadena=cadena.replace('&#233;','é')
    cadena=cadena.replace('&#228;','ä')
    cadena=cadena.replace('&#214;','Ö')
    cadena=cadena.replace('&amp;','&')
    cadena=cadena.replace('&AMP;','&')
    cadena=cadena.replace('&Ntilde;','Ñ')
    
    return cadena
    
## Converts a decimal to a localized number string
def l10nDecimal(dec, digits=2):
    l=QLocale()
    
    return l.toCurrencyString(float(dec))
    
    
def function_name(clas):
    #    print (inspect.stack()[0][0].f_code.co_name)
    #    print (inspect.stack()[0][3],  inspect.stack())
    #    print (inspect.stack()[1][3],  inspect.stack())
    #    print (clas.__class__.__name__)
    #    print (clas.__module__)
    return "{0}.{1}".format(clas.__class__.__name__,inspect.stack()[1][3])
