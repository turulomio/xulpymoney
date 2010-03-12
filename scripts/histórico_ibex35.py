#!/usr/bin/python    
# -*- coding: utf-8 -*-  
import os, adodb, datetime

cwd=os.getcwd()

dsn = "dbname=programas host=localhost port=5432 user=postgres password=***"
con = adodb.NewADOConnection("postgres")
con.Connect("127.0.0.1","postgres","*","cuentas")

# BORRA LA BASE DE DATOS
con.Execute("delete from ibex35")

# SE DESCARGA UNA NUEVA
print "* Descargando fichero..."
os.system ("wget 'http://ichart.yahoo.com/table.csv?s=%5EIBEX&a=01&b=15&c=1993&d=" + str(datetime.date.today().month-1) + "&e=" + str(datetime.date.today().day) + "&f="+ str(datetime.date.today().year) + "&g=d&ignore=.csv' -O /tmp/ibex35.csv &> /dev/null")

# INSERTA LA NUEVA
print "* Procesando el fichero..."
f=open("/tmp/ibex35.csv","r")
f.readline()
arr=[]
for line in f:
	arrline=line.split(",")
	arr.append((arrline[0], float(arrline[4]), 0.0))
f.close()


n=len(arr)-1
con.Execute ("insert into ibex35 (fecha, cierre, diff) values ('" + arr[n][0] + "', " + str(arr[n][1]) + ", "+ str(arr[n][2])+ ");")
for i in range(0,n):
	arr[n-1-i]=(arr[n-1-i][0], arr[n-1-i][1], arr[n-1-i][1]-arr[n-i][1])
        con.Execute ("insert into ibex35 (fecha, cierre, diff) values ('" + arr[n-1-i][0] + "', " + str(arr[n-1-i][1]) + ", "+ str(arr[n-1-i][2])+ ");")
con.Close()
print "  - Se han añadido", len (arr), "registros"
