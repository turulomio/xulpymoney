#!/usr/bin/python3
# -*- coding: UTF-8  -*-
import urllib, sys,  datetime,  multiprocessing, time, gettext, os

sys.path.append("/usr/lib/myquotes2")
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

def parserow(m,row,cur21):
	if row==None:
		print("Fila None en {0}".format(m))
	global n
	s=""
	for h in range(24):
		for m in range(60):
			campo="{0}{1}".format(str(h).zfill(2), str(m).zfill(2))
			if row[campo]!=None:
				dt=datetime.datetime(row['date'].year,	row['date'].month, row['date'].day,h,m)
				s=s+"{0}\t{1}\t{2}\t{3}\n".format(str(dt),row[campo],n,79329)
				cur21.execute("insert into quotes(datetime,quote,id)  values ( %s, %s, 79329);",(str(dt),row[campo]))
				n=n+1
	if row['last']=='close':
		dt=datetime.datetime(row['date'].year,  row['date'].month, row['date'].day,23,59,59)
		s=s+"{0}\t{1}\t{2}\t{3}\n".format(str(dt),row['close'],n,79329)
		cur21.execute("insert into quotes(datetime,quote,id)  values ( %s, %s, 79329);",(str(dt),row['close']))
		n=n+1
	return s
				
n=1
m=1
p=""	
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
#Borra todo de myquotes2
cur21.execute("delete from quotes where id=79329")
con2.commit()

cur11.execute("select * from quotes where code=%s order by date",('^IBEX',))
for row in cur11:
	p=p+parserow(m, row,cur21)
con2.commit()
s="""COPY quotes (datetime, quote, id_quotes, id) FROM stdin;
"""+p+"""\.\n""" 


f=open("ibex.sql","w")
f.write(s)
f.close()


cur11.close()               
cur21.close() 
curx1.close()
con1.close()
con2.close()
conx.close()

