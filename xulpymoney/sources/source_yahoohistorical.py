#!/usr/bin/python3
import sys
sys.path.append("/usr/lib/xulpymoney")
from libxulpymoney import *
from libsources import *

mem=MemProducts()
mem.init__script('Yahoo Historical Updater')

w=WorkerYahooHistorical(mem, 1, "select * from products where  char_length(ticker)>0  and priorityhistorical[1]=3 and obsolete=false")
w.run()

mem.disconnect(mem.con)
