#!/usr/bin/python3
# -*- coding: UTF-8  -*-
import urllib, sys,  datetime,  multiprocessing, time, gettext, os

sys.path.append("/usr/lib/myquotes2")
from libmyquotes import *
"""ESTE SCRIPT METE EN MYQUOT2 TODOS LOS DATOS DE ESTIMACIONES DE DIVIDENDO MYQUOTES CUYO CODIGO ESTA EN MYQUOTES;
"""

def myquotescode2id(cur2, code):
	cur2.execute("select id, comentario from investments where comentario like '%{0}%'".format(code))
	r=cur2.fetchone()
	myquotescode=r['comentario'].split("||")[0]
	if cur2.rowcount==2:
		print ("MAAAAAAAAAAAAAAAAAAAAl")
	return r['id']

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
str1="dbname='myquotes.old' port='5433' user='postgres' host='localhost' password=' '"
str2="dbname='myquotes' port='5433' user='postgres' host='localhost' password=' '"

con1=psycopg2.extras.DictConnection(str1)
con2=psycopg2.extras.DictConnection(str2)
cur11=con1.cursor()
cur21=con2.cursor()
#Borra todo de estimacionesdividendo
cur21.execute("delete from dividendosestimaciones")
con2.commit()



#SACA MYQUOTESCODE DE XULPYMONEY Y LOS CONVIERTE A IDS
cur11.execute("select * from dividendosestimaciones");
for row in cur11:
	id=myquotescode2id(cur21, row['code'])
	cur21.execute("insert into dividendosestimaciones (year, dpa, fechaestimacion, fuente, manual, id) values (%s, %s,%s,%s,%s,%s)",(row['year'],row['dpa'],row['fechaestimacion'], row['fuente'], row['manual'], id))
con2.commit()
cur11.close()               
cur21.close() 
con1.close()
con2.close()

