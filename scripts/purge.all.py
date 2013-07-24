#!/usr/bin/python3
import sys
sys.path.append("/usr/lib/myquotes")
from libmyquotes import *
from config import *
"""Este script regenera todos los booleanos open, high, close,..., de todo el sistema y borra los innecesarios de más de 7 días"""

if __name__ == '__main__':
    cfg=ConfigMQ()
    cfg.con=cfg.connect_myquotesd()
    gen=QuotesGenOHCL(cfg)
    gen.recalculateAllAndDelete()
    cfg.disconnect_myquotesd(cfg.con)

