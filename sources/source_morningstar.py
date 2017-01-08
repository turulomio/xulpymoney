#!/usr/bin/python3
import sys
sys.path.append("/usr/lib/xulpymoney")
from libxulpymoney import MemXulpymoney
from libsources import WorkerMorningstar

mem=MemXulpymoney()
args=mem.init__script('Morningstar update',  type=1)


w=WorkerMorningstar(mem, 1)
w.setSQL(useronly=False)#"select * from products where type=2 and char_length(isin)>0  and obsolete=false")

if args.tickers==True:
    w.regenerate_tickers()
else:
    w.run()
mem.con.disconnect()
