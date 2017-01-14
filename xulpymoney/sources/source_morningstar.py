#!/usr/bin/python3
import sys
sys.path.append("/usr/lib/xulpymoney")
from libxulpymoney import MemXulpymoney
from libsources import WorkerMorningstar

mem=MemXulpymoney()
args=mem.init__script('Morningstar update',  tickers=True, sql=True)


w=WorkerMorningstar(mem, 1)
w.setSQL(useronly=False)#"select * from products where type=2 and char_length(isin)>0  and obsolete=false")

if args.sql==True:
    cur=mem.con.cursor()
    cur.execute("select id, ticker from products where priorityhistorical[1]=8 and obsolete=false and ticker is not null order by name")
    for row in cur:
        print("UPDATE products SET ticker='{}' WHERE id={};".format(row['ticker'], row['id']))
    cur.close()
    sys.exit(0)

if args.tickers==True:
    w.regenerate_tickers()
else:
    w.run()
mem.con.disconnect()
