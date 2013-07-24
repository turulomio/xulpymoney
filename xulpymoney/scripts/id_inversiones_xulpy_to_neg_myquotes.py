#!/usr/bin/python3
# -*- coding: UTF-8  -*-
import urllib, sys,  datetime,  multiprocessing, time, gettext, os

sys.path.append("/usr/lib/myquotes")
from libmyquotes import *
"""ESTE SCRIPT MODIFICA EN XULPYMONEY EL IDMYQUOTES PASADO COMO PARAMETRO  Y LO PONE A NEG -1 Y MODIFICA TODO EN MYQUOTES
PARA QUE EL ID ANTIGUO PASE A NUEVO. DEVUELVE EL ULTIMO
"""

oldid=int(sys.argv[1])

strm="dbname='myquotes' port='5433' user='postgres' host='localhost' password=' '"
strx="dbname='xulpymoney' port='5433' user='postgres' host='localhost' password=' '"
conm=psycopg2.extras.DictConnection(strm)
conx=psycopg2.extras.DictConnection(strx)
curm=conm.cursor()
curx=conx.cursor()


#Saca siguiente id negativo
curm.execute("select id-1 as newid from investments order by id limit 1;")
newid=int(curm.fetchone()[0])

print (oldid , ">>>", newid)

curx.execute("update inversiones set myquotesid=%s where myquotesid=%s",(str(newid),str(oldid)))
curm.execute("update quotes set id=%s where id=%s",(newid,oldid))
curm.execute("update investments set id=%s where id=%s",(newid,oldid))
curm.execute("update dividendosestimaciones set id=%s where id=%s",(newid,oldid))

conx.commit()
conm.commit()

curm.close()               
curx.close()
conm.close()
conx.close()

