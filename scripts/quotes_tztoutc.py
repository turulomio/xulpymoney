#!/usr/bin/python3
# -*- coding: UTF-8  -*-
import urllib, sys,  datetime,  multiprocessing, time, gettext, os

"""ESTE SCRIPT DEJA LA ZONE NONE SI SOLO SON CDTHOLCV POR ESO SELECCIONA LOS QUE ZONE NO SEA NONE NI UTC"""


sys.path.append("/usr/lib/myquotes")
from libmyquotes import *


def rewrite(row):
	resultado=[]
	last=""
	for h in range (24):
		for m in range(60):
			campo=str(h).zfill(2) + str(m).zfill(2)
			if row[campo]!=None:
				d= {'code': row['code'], 'date': None, 'time':None,'quote': row[campo] ,  'zone':None}
				(d['date'], d['time'], d['zone'])=utc2(row['date'], datetime.time(h,m), row['zone'])
				last=campo              
				resultado.append(d)
	if last!="":
		Quote(cfg).insert_cdtv(resultado,"MINUTOS")



	if row['open']==None and row['high']==None and row['low']==None and row['close']==None and row['volumen']==None:
		pass
	else:
		d={}
		d['code']=row['code']
		d['date']=row['date']
		d['open']=row['open']
		d['high']=row['high']
		d['low']=row['low']
		d['close']=row['close']
		d['volumen']=row['volumen']
		d['zone']='UTC'

		resultado=[]
		resultado.append(d)
		Quote(cfg).insert_cdtochlv(resultado)

if __name__ == '__main__':
	inicio=datetime.datetime.now()         
	cfg=Config()
	con=cfg.connect_myquotesd()
	cur = con.cursor()     
	cur2 = con.cursor()
	cur.execute("select count(*) from quotes where zone is not null and zone not in ('UTC');")
	print ("Quote sin zona UTC: " + str(cur.fetchone()[0]))

	cur.execute("select code, date  from quotes where zone not in ('UTC') order by code, date;")
	for c in cur:
		cur2.execute("select * from quotes where code=%s and date=%s",(c['code'],c['date']))
		row=cur2.fetchone()
	
#        print (row['code'],row['last'],  row['volumen'], row['open'], row['zone'])
		cur2.execute("delete from quotes where code=%s and date=%s",(row['code'],row['date']))
		con.commit()
		rewrite(row)
		if row['last']=="close":
			print ("Updating last")
			cur2.execute("update quotes set last='close' where code=%s and date=%s",(row['code'],row['date']))
#	con.commit()
#	cur2.execute("select   code, last,  volumen, open, zone from quotes where code=%s and date=%s",(row['code'],row['date']))	
		eta=cur.rowcount*(datetime.datetime.now()-inicio).total_seconds()/cur.rownumber
		print (cur.rownumber, cur.rowcount,  round(eta/60/60,2), row['code'], row['date'], row['last'], row['volumen'], row['open'], row['zone'])
#	time.sleep(10)
	cur.close()               
	cur2.close() 
	cfg.disconnect_myquotesd(con)

