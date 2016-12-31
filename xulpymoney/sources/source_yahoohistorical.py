#!/usr/bin/python3
import sys
sys.path.append("/usr/lib/xulpymoney")
from libxulpymoney import MemXulpymoney
from libsources import WorkerYahooHistorical

mem=MemXulpymoney()
mem.init__script('Yahoo Historical Updater')
w=WorkerYahooHistorical(mem, 1)
w.setSQL( "select * from products where char_length(ticker)>0 and priorityhistorical[1]=3 and obsolete=false")
w.run()
mem.con.disconnect()
