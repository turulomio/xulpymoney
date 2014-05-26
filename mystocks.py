#!/usr/bin/python3
#-*- coding: utf-8 -*- 

import sys,  os
sys.path.append("/usr/lib/xulpymoney")

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from frmMainMS import *
from libxulpymoney import *

try:
    os.makedirs(os.environ['HOME']+"/.xulpymoney/")
except:
    pass
    

app = QApplication(sys.argv)
QTextCodec.setCodecForTr(QTextCodec.codecForName("UTF-8"));

mem=MemMyStock()

if "admin" in sys.argv:
    mem.adminmode=True
    print ("Activated admin mode")
if "debug" in sys.argv:
    mem.debugmode=True
    print ("Activated debug mode")
    
mem.setQTranslator(QTranslator(app))
mem.qtranslator.load("/usr/lib/xulpymoney/xulpymoney_{0}.qm".format(mem.config.get_value("settings", "language")))
app.installTranslator(mem.qtranslator)

frmMain = frmMainMS(mem) 
frmMain.show()

sys.exit(app.exec_())
