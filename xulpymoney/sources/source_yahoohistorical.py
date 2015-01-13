#!/usr/bin/python3
import sys
sys.path.append("/usr/lib/xulpymoney")
from libxulpymoney import *
from libsources import *

mem=MemProducts()
mem.init__script('Yahoo Historical Updater')

w=WorkerYahooHistorical(mem, 1, "select * from products where active=true and priorityhistorical[1]=3")
w.run()

mem.disconnect(mem.con)
