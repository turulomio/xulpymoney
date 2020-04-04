## @namespace xulpymoney.libxulpymoneyfunctions
## @brief Package with all xulpymoney auxiliar functions.
from PyQt5.QtCore import Qt,  QCoreApplication
from decimal import Decimal
from xulpymoney.ui.myqwidgets import qmessagebox
import inspect
import logging
import sys

## con is con_target, 
## progress is a pointer to progressbar
## returns a tuple (numberofproductssynced, numberofquotessynced)
def sync_data(con_source, con_target, progress=None):
    #Checks if database has same version
    source_version=con_source.cursor_one_field("select value from globals where global='Version'")
    target_version=con_target.cursor_one_field("select value from globals where global='Version'")
    if source_version!=target_version:
        logging.critical ("Databases has diferent versions, please update them")
        sys.exit(0)

    quotes=0#Number of quotes synced
    estimation_dps=0#Number of estimation_dps synced
    estimation_eps=0#Number of estimation_eps synced
    dps=0
    splits=0 #Number of splits synced
    products=0#Number of products synced

    #Iterate all products
    rows_target=con_target.cursor_rows("select id,name from products where id>0 order by name")
    logging.info ("Syncing {} products".format (len(rows_target)))
    for i_target, row in enumerate(rows_target):
        output="Syncing {}: ".format(row['name'])
        ## QUOTES #####################################################################
        #Search last datetime
        max=con_target.cursor_one_field("select max(datetime) as max from quotes where id=%s", (row['id'], ))
        #Ask for quotes in source with last datetime
        if max==None:#No hay ningun registro y selecciona todos
            rows_source=con_source.cursor_rows("select * from quotes where id=%s", (row['id'], ))
        else:#Hay registro y selecciona los posteriores a el
            rows_source=con_source.cursor_rows("select * from quotes where id=%s and datetime>%s", (row['id'], max))
        if len(rows_source)>0:
            for  row_source in rows_source: #Inserts them 
                con_target.execute("insert into quotes (id, datetime, quote) values (%s,%s,%s)", ( row_source['id'], row_source['datetime'], row_source['quote']))
                quotes=quotes+1
                output=output+"."

        ## DPS ################################################################################
        #Search last datetime
        max=con_target.cursor_one_field("select max(date) as max from dps where id=%s", (row['id'], ))
        #Ask for quotes in source with last datetime
        if max==None:#No hay ningun registro y selecciona todos
            rows_source=con_source.cursor_rows("select * from dps where id=%s", (row['id'], ))
        else:#Hay registro y selecciona los posteriores a el
            rows_source=con_source.cursor_rows("select * from dps where id=%s and date>%s", (row['id'], max))
        if len(rows_source)>0:
            for row_source in rows_source: #Inserts them 
                con_target.execute("insert into dps (date, gross, id) values (%s,%s,%s)", ( row_source['date'], row_source['gross'], row_source['id']))
                dps=dps+1
                output=output+"-"

        ## DPS ESTIMATIONS #####################################################################
        #Search last datetime
        max=con_target.cursor_one_field("select max(year) as max from estimations_dps where id=%s", (row['id'], ))
        #Ask for quotes in source with last datetime
        if max==None:#No hay ningun registro y selecciona todos
            rows_source=con_source.cursor_rows("select * from estimations_dps where id=%s", (row['id'], ))
        else:#Hay registro y selecciona los posteriores a el
            rows_source=con_source.cursor_rows("select * from estimations_dps where id=%s and year>%s", (row['id'], max))
        if len(rows_source)>0:
            for row_source in rows_source: #Inserts them 
                con_target.execute("insert into estimations_dps (year, estimation, date_estimation, source, manual, id) values (%s,%s,%s,%s,%s,%s)", ( row_source['year'], row_source['estimation'], row_source['date_estimation'], row_source['source'], row_source['manual'],  row_source['id']))
                estimation_dps=estimation_dps+1
                output=output+"+"

        ## EPS ESTIMATIONS #####################################################################
        #Search last datetime
        max=con_target.cursor_one_field("select max(year) as max from estimations_eps where id=%s", (row['id'], ))
        #Ask for quotes in source with last datetime
        if max==None:#No hay ningun registro y selecciona todos
            rows_source=con_source.cursor_rows("select * from estimations_eps where id=%s", (row['id'], ))
        else:#Hay registro y selecciona los posteriores a el
            rows_source=con_source.cursor_rows("select * from estimations_eps where id=%s and year>%s", (row['id'], max))
        if len(rows_source)>0:
            for row_source in rows_source: #Inserts them 
                con_target.execute("insert into estimations_eps (year, estimation, date_estimation, source, manual, id) values (%s,%s,%s,%s,%s,%s)", ( row_source['year'], row_source['estimation'], row_source['date_estimation'], row_source['source'], row_source['manual'],  row_source['id']))
                estimation_eps=estimation_eps+1
                output=output+"*"

        ## SPLITS  #####################################################################
        #Search last datetime
        max=con_target.cursor_one_field("select max(datetime) as max from splits where products_id=%s", (row['id'], ))
        #Ask for quotes in source with last datetime
        if max==None:#No hay ningun registro y selecciona todos
            rows_source=con_source.cursor_rows("select * from splits where products_id=%s", (row['id'], ))
        else:#Hay registro y selecciona los posteriores a el
            rows_source=con_source.cursor_rows("select * from splits where products_id=%s and datetime>%s", (row['id'], max))
        if len(rows_source)>0:
            for row_source in rows_source: #Inserts them 
                con_target.execute("insert into splits (datetime, products_id, before, after, comment) values (%s,%s,%s,%s,%s)", ( row_source['datetime'], row_source['products_id'], row_source['before'], row_source['after'], row_source['comment']))
                splits=splits+1
                output=output+"s"

        if output!="Syncing {}: ".format(row['name']):
            products=products+1
            logging.debug(output)

        if progress!=None:#If there's a progress bar
            progress.setValue(i_target)
            progress.setMaximum(len(rows_target))
            QCoreApplication.processEvents()
    con_target.commit()

    if progress!=None:
        s=QCoreApplication.translate("Mem", """From {} desynchronized products added:
    - {} quotes
    - {} dividends per share
    - {} dividend per share estimations
    - {} earnings per share estimations
    - {} splits / contrasplits""").format(  products,  quotes, dps, estimation_dps,  estimation_eps, splits)

        qmessagebox(s)

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

## Sets the sign of other number
def set_sign_of_other_number(number, number_to_change):
    if is_positive(number):
       return abs(number_to_change)
    return -abs(number_to_change)

        
def setReadOnly(wdg, boolean):
    if wdg.__class__.__name__=="QCheckBox":
        wdg.blockSignals(boolean)
        wdg.setAttribute(Qt.WA_TransparentForMouseEvents)
        wdg.setFocusPolicy(Qt.NoFocus)
