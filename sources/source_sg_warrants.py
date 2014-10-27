#!/usr/bin/python3
import sys
sys.path.append("/usr/lib/xulpymoney")
from libxulpymoney import *
from libsources import *

mem=MemProducts()
mem.init__script('Societe Generale Warrants')

w=WorkerSGWarrants(mem)
w.run()

mem.disconnect(mem.con)
