#!/usr/bin/python3
# -*- coding: UTF-8  -*-
import urllib, sys,  datetime,  multiprocessing, time, gettext, os

sys.path.append("/usr/lib/myquotes")
if len(sys.argv)!=5:
    print ("change_id idviejo idnuevo dbxulpy port")
    print ("change_id idviejo system dbxulpy port ->> crea en el último id disponible")
    print ("change_id idviejo manual dbxulpy port ->> crea en el menor id negativo disponible")
    sys.exit(0)

from libmyquotes import *
"""ESTE SCRIPT MODIFICA EN XULPYMONEY EL IDMYQUOTES PASADO COMO PARAMETRO  Y LO PONE A NEG -1 Y MODIFICA TODO EN MYQUOTES
PARA QUE EL ID ANTIGUO PASE A NUEVO. DEVUELVE EL ULTIMO
"""



port=sys.argv[4]
xulpydb=sys.argv[3]

strm="dbname='myquotes' port='{0}' user='postgres' host='localhost' password=' '".format(port)
strx="dbname='{0}' port='{1}' user='postgres' host='localhost' password=' '".format(xulpydb,port)
conm=psycopg2.extras.DictConnection(strm)
conx=psycopg2.extras.DictConnection(strx)
curm=conm.cursor()
curx=conx.cursor()

oldid=int(sys.argv[1])

if sys.argv[2]=='system':
    curm.execute("select max(id)+1 from investments;")
    newid=int(curm.fetchone()[0])
elif sys.argv[2]=='manual':
    curm.execute("select min(id)-1 from investments;")
    newid=int(curm.fetchone()[0])
else:
    newid=int(sys.argv[2])

print (oldid , ">>>", newid)

curx.execute("update inversiones set myquotesid=%s where myquotesid=%s",(str(newid),str(oldid)))
curm.execute("update quotes set id=%s where id=%s",(newid,oldid))
curm.execute("update investments set id=%s where id=%s",(newid,oldid))
curm.execute("update estimaciones set id=%s where id=%s",(newid,oldid))

conx.commit()
conm.commit()

curm.close()               
curx.close()
conm.close()
conx.close()

