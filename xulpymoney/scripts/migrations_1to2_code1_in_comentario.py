#!/usr/bin/python3
# -*- coding: UTF-8  -*-
import urllib, sys,  datetime,  multiprocessing, time, gettext, os

sys.path.append("/usr/lib/myquotes")
from libmyquotes import *
"""ESTE SCRIPT METE EN MYQUOT2 TODOS LOS DATOS DE MYQUOTES CUYO CODIGO ESTA EN MYQUOTES;
"""


sys.path.append("/usr/lib/myquotes")
from libmyquotes import *
def myquotescode2id(cur2, code):
	cur2.execute("select id, comentario from investments where comentario like '%{0}%'".format(code))
	r=cur2.fetchone()
	myquotescode=r['comentario'].split("||")[0]
	if cur2.rowcount==2:
		print ("MAAAAAAAAAAAAAAAAAAAAl")
	id[myquotescode]=r['id']

def parserow(m,row):
	if row==None:
		print("Fila None en {0}".format(m))
	global n
	s=""
	for h in range(24):
		for m in range(60):
			campo="{0}{1}".format(str(h).zfill(2), str(m).zfill(2))
			if row[campo]!=None:
				dt=datetime.datetime(row['date'].year,	row['date'].month, row['date'].day,h,m)
				s=s+"{0}\t{1}\t{2}\t{3}\n".format(str(dt),row[campo],n,id[row['code']])
				n=n+1
	if row['last']=='close':
		dt=datetime.datetime(row['date'].year,  row['date'].month, row['date'].day,23,59,59)
		s=s+"{0}\t{1}\t{2}\t{3}\n".format(str(dt),row['close'],n,id[row['code']])
		n=n+1
	return s
				
n=1
	
id={}
inicio=datetime.datetime.now()         
str1="dbname='myquotes.old' port='5432' user='postgres' host='localhost' password=' '"
str2="dbname='myquotes' port='5432' user='postgres' host='localhost' password=' '"
strx="dbname='xulpymoney' port='5432' user='postgres' host='localhost' password=' '"
con1=psycopg2.extras.DictConnection(str1)
con2=psycopg2.extras.DictConnection(str2)
conx=psycopg2.extras.DictConnection(strx)
cur11=con1.cursor()
cur21=con2.cursor()
curx1=conx.cursor()
#Borra todo de myquotes
cur21.execute("delete from quotes")
con2.commit()

#SACA MYQUOTESCODE DE XULPYMONEY Y LOS CONVIERTE A IDS
curx1.execute("select distinct(myquotescode) from inversiones");
for m in curx1:
	myquotescode2id(cur21,m['myquotescode'])
#LOS BUSCA Y LOS INTRODUCE PARSEADOS EN myquotes
mm=1
p=""
for m in id:
	print (mm, len(id), n)
	cur11.execute("select * from quotes where code=%s order by date",(m,))
	for row in cur11:
		p=p+parserow(m, row)
	mm=mm+1

#MODIFICA MYQUOTESCODE EN XULPYMONEY
for m in id:
	curx1.execute("update inversiones set myquotesid=%s where myquotescode=%s",(id[m], m))
conx.commit()


s="""COPY quotes (datetime, quote, id_quotes, id) FROM stdin;
"""+p+"""\.\n""" 


f=open("copy.sql","w")
f.write(s)
f.close()


cur11.close()               
cur21.close() 
curx1.close()
con1.close()
con2.close()
conx.close()

