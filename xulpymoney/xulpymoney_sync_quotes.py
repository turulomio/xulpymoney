#!/usr/bin/python3
import sys
import argparse
import getpass
import psycopg2
import psycopg2.extras
from libsources import sync_data

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

print ("Insert {} source database password for {} in {} with port {}".format(args.db_source,args.user_source,args.host_source,args.port_source))
password_source=getpass.getpass()

strcon_source="dbname='{}' port='{}' user='{}' host='{}' password='{}'".format(args.db_source, args.port_source, args.user_source, args.host_source, password_source)
try:
    con_source=psycopg2.extras.DictConnection(strcon_source)
except psycopg2.Error as e:
    print ("Error conecting to source Xulpymoney")
    sys.exit(1)

print ("Insert {} target database password for {} in {} with port {}".format(args.db,args.user,args.host,args.port))
password=getpass.getpass()

strcon="dbname='{}' port='{}' user='{}' host='{}' password='{}'".format(args.db, args.port, args.user, args.host, password)
try:
    con=psycopg2.extras.DictConnection(strcon)
except psycopg2.Error as e:
    print ("Error conecting to Xulpymoney")
    sys.exit(2)

sync_data(con_source, con)
