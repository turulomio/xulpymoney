#!/usr/bin/python3
import sys
sys.path.append("/usr/lib/xulpymoney")
from libxulpymoney import *
from libsources import *

mem=MemProducts()
mem.init__script('Morningstar update')

w=WorkerMorningstar(mem, 1)
w.run()

mem.disconnect(mem.con)
