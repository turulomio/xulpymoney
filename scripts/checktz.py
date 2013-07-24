5#!/usr/bin/python3
# -*- coding: UTF-8  -*-
import urllib, sys,  datetime,  multiprocessing, time, gettext, os
sys.path.append("/usr/lib/myquotes")
from libmyquotes import *

id={}
inicio=datetime.datetime.now()         
str="dbname='myquotes' port='5433' user='postgres' host='localhost' password=' '"
con=psycopg2.extras.DictConnection(str)
cur=con.cursor()
cur.execute("drop table pruebatz;")
con.commit();
cur.execute("CREATE TABLE pruebatz(  tz timestamp with time zone,  stz timestamp without time zone) WITH (  OIDS=FALSE);")
con.commit()
stz=datetime.datetime.now()
tz=changetz(stz,'Europe/Madrid','Europe/Madrid')
print ("Variables (Con, Sin) TZ",tz, stz)
print (cur.mogrify("insert into pruebatz (tz,stz) values (%s,%s)",(tz,stz)))
cur.execute("insert into pruebatz (tz,stz) values (%s,%s)",(tz,stz))

con.commit()
cur.execute("select * from pruebatz");
for row in cur:
	print ("Lectura BD (Con, Sin) TZ", row['tz'],row['stz'])

stz=datetime.datetime.now()
tz=changetz(stz,'Europe/Madrid','America/New_York')
print ("Variables (Con, Sin) TZ",tz, stz)
print (cur.mogrify("insert into pruebatz (tz,stz) values (%s,%s)",(tz,stz)))
cur.execute("insert into pruebatz (tz,stz) values (%s,%s)",(tz,stz))

con.commit()
cur.execute("select * from pruebatz");
for row in cur:
        print ("Lectura BD (Con, Sin) TZ", row['tz'],row['stz'])

stz=datetime.datetime(2011,7,20,0,25)
tz=changetz(stz,'UTC','America/New_York') 
print ("Variables (Con, Sin) TZ",tz, stz)
print (cur.mogrify("insert into pruebatz (tz,stz) values (%s,%s)",(tz,stz)))
cur.execute("insert into pruebatz (tz,stz) values (%s,%s)",(tz,stz))

con.commit()
cur.execute("select * from pruebatz");
for row in cur:
        print ("Lectura BD (Con, Sin) TZ", row['tz'],row['stz'])

cur.close()
con.close()

