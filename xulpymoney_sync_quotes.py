#!/usr/bin/python3
import sys
import argparse
import getpass
import psycopg2
import psycopg2.extras

## TO SYNC MINE IN PAPA
##python3 xulpymoney_sync_quotes.py --db_source xulpymoney -d xulpymoneypapa




parser=argparse.ArgumentParser("xulpymoney_sync_quotes")
parser.add_argument('-Us', '--user_source', help='Postgresql source user', default='postgres')
parser.add_argument('-ps', '--port_source', help='Postgresql source server port', default=5432)
parser.add_argument('-Hs', '--host_source', help='Postgresql source server address', default='127.0.0.1')
parser.add_argument('-ds', '--db_source', help='Postgresql source database', default='xulpymoney_source')
parser.add_argument('-U', '--user', help='Postgresql user', default='postgres')
parser.add_argument('-p', '--port', help='Postgresql server port', default=5432)
parser.add_argument('-H', '--host', help='Postgresql server address', default='127.0.0.1')
parser.add_argument('-d', '--db', help='Postgresql database', default='xulpymoney')
args=parser.parse_args()
        

if args.db==args.db_source and args.host==args.host_source:
    print("Databases can't be the same")
    sys.exit(3)

print ("Source database password")
password_source=getpass.getpass()

strcon_source="dbname='{}' port='{}' user='{}' host='{}' password='{}'".format(args.db_source, args.port_source, args.user_source, args.host_source, password_source)
try:
    con_source=psycopg2.extras.DictConnection(strcon_source)
except psycopg2.Error as e:
    print ("Error conecting to source Xulpymoney")
    sys.exit(1)
    
print ("Database password")
password=getpass.getpass()

strcon="dbname='{}' port='{}' user='{}' host='{}' password='{}'".format(args.db, args.port, args.user, args.host, password)
try:
    con=psycopg2.extras.DictConnection(strcon)
except psycopg2.Error as e:
    print ("Error conecting to Xulpymoney")
    sys.exit(2)
    
    
#Checks if database has same version


    
cur=con.cursor()
cur2=con.cursor()
cur_source=con_source.cursor()


#Checks if database has same version
cur_source.execute("select value from globals where id_globals=1")
cur.execute("select value from globals where id_globals=1")

if cur_source.fetchone()[0]!=cur.fetchone()[0]:
    print ("Databases has diferent versions, please update them")
    sys.exit(0)
    
count=0
products=0

#Iterate all products
cur.execute("select id,name from products where id>0 order by name;")
for row in cur:
    #Search last datetime
    cur2.execute("select max(datetime) as max from quotes where id=%s", (row['id'], ))
    max=cur2.fetchone()[0]
    #Ask for quotes in source with last datetime
    if max==None:#No hay ningun registro y selecciona todos
        cur_source.execute("select * from quotes where id=%s", (row['id'], ))
    else:#Hay registro y selecciona los posteriores a el
        cur_source.execute("select * from quotes where id=%s and datetime>%s", (row['id'], max))
    if cur_source.rowcount!=0:
        print("Syncing from source: ", max, row['name'])
        products=products+1
        for  row_source in cur_source: #Inserts them 
            cur2.execute("insert into quotes (id, datetime, quote) values (%s,%s,%s)", ( row_source['id'], row_source['datetime'], row_source['quote']))
            count=count+1
            print (row_source)
        

cur.close()
cur2.close()
cur_source.close()
con_source.close()
con.commit()
con.close()
print ("Added {} quotes from {} products".format(count,  products))
