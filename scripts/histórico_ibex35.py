#!/usr/bin/python    
# -*- coding: utf-8 -*-  
import os, sys, adodb, datetime

cwd=os.getcwd()

dsn = "dbname=programas host=localhost port=5432 user=postgres password=***"
con = adodb.NewADOConnection("postgres")
con.Connect("127.0.0.1","postgres","*","cuentas")

# BORRA LA BASE DE DATOS
con.Execute("delete from ibex35")

# SE DESCARGA UNA NUEVA
hoy=datetime.date.today()
os.system ("wget 'http://ichart.yahoo.com/table.csv?s=%5EIBEX&a=01&b=15&c=1993&d=" + str(datetime.date.today().month-1) + "&e=" + str(datetime.date.today().day) + "&f="+ str(datetime.date.today().year) + "&g=d&ignore=.csv' -O /tmp/ibex35.csv")

# INSERTA LA NUEVA
f=open("/tmp/ibex35.csv","r")
f.readline()
for line in f:
	arrline=line.split(",")
	con.Execute ("insert into ibex35 (fecha, cierre) values ('" + arrline[0] + "', " +  arrline[4] + ");")
f.close()
con.Close()

