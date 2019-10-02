## @namespace xulpymoney.libxulpymoneyfunctions
## @brief Package with all xulpymoney auxiliar functions.
from PyQt5.QtCore import Qt,  QCoreApplication, QLocale
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget,  QMessageBox, QApplication, QCheckBox, QHBoxLayout
from decimal import Decimal
from os import path, remove
import inspect
import logging
import socket
import sys

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
            logging.debug(output)
            
        if progress!=None:#If there's a progress bar
            progress.setValue(cur_target.rownumber)
            progress.setMaximum(cur_target.rowcount)
            QCoreApplication.processEvents()
    con_target.commit()
    
    if progress!=None:
        s=QCoreApplication.translate("Core", """From {} desynchronized products added:
    - {} quotes
    - {} dividends per share
    - {} dividend per share estimations
    - {} earnings per share estimations
    - {} splits / contrasplits""").format(  products,  quotes, dps, estimation_dps,  estimation_eps, splits)
            
        qmessagebox(s)  
    

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
            
def string2list_of_integers(s, separator=", "):
    """Convers a string of integer separated by comma, into a list of integer"""
    arr=[]
    if s!="":
        arrs=s.split(separator)
        for a in arrs:
            arr.append(int(a))
    return arr


## Converts a string  to a decimal
def string2decimal(s, type=1):
    if type==1: #2.123,25
        try:
            return Decimal(s.replace(".","").replace(",", "."))
        except:
            return None


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
    
## Function that converts a None value into a Decimal('0')
## @param dec Should be a Decimal value or None
## @return Decimal
def none2decimal0(dec):
    if dec==None:
        return Decimal('0')
    return dec

## Relation between gains and risk. Should be over 2 to be a good investment
## @param target Decimal with investment price target
## @param entry Decimal with investment entry price
## @param stoploss Decimal with investment stoploss price
## @return Decimal or None if relation can't be calculated
def relation_gains_risk(target, entry,  stoploss):
    try:
        return Decimal(abs(target-entry)/abs(entry-stoploss))
    except:
        return None

    
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
    

## Check if two numbers has the same sign
## @param number1 First number used in check
## @param number2 Second number used in check
## @return bool True if they have the same sign
def have_same_sign(number1, number2):
    if (is_positive(number1)==True and is_positive(number2)==True) or (is_positive(number1)==False and is_positive(number2)==False):
        return True
    return False

## Check if a number is positive
## @param number Number used in check
## @return bool True if number is positive, else False
def is_positive(number):
    if number>=0:
        return True
    return False

## Checks if there is internet
def is_there_internet():
    try:
        # connect to the host -- tells us if the host is actually
        # reachable
        socket.create_connection(("www.google.com", 80))
        return True
    except OSError:
        return False


## Sets the sign of other number
def set_sign_of_other_number(number, number_to_change):
    if is_positive(number):
       return abs(number_to_change)
    return -abs(number_to_change)

## Asks a a question to delete a file
## Returns True or False if file has been deleted
def question_delete_file(filename):
    reply = QMessageBox.question(
                    None, 
                    QApplication.translate("Core", 'File deletion question'), 
                    QApplication.translate("Core", "Do you want to delete this file:\n'{}'?").format(filename), 
                    QMessageBox.Yes, 
                    QMessageBox.No
                )
    if reply==QMessageBox.Yes:
        remove(filename)
        if path.exists(filename)==False:
            return True
    return False
        
def setReadOnly(wdg, boolean):
    if wdg.__class__.__name__=="QCheckBox":
        wdg.blockSignals(boolean)
        wdg.setAttribute(Qt.WA_TransparentForMouseEvents)
        wdg.setFocusPolicy(Qt.NoFocus)
    
        
