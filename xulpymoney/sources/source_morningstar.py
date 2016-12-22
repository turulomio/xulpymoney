#!/usr/bin/python3
import sys
sys.path.append("/usr/lib/xulpymoney")
from libxulpymoney import MemXulpymoney
from libsources import WorkerMorningstar

mem=MemXulpymoney()
mem.init__script('Morningstar update')
w=WorkerMorningstar(mem, 1)
w.setSQL("select * from products where type=2 and char_length(isin)>0  and obsolete=false")
w.run()
mem.con.disconnect()
