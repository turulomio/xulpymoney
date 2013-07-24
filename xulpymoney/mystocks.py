#!/usr/bin/python3
#-*- coding: utf-8 -*- 

import sys,  os
sys.path.append("/usr/lib/xulpymoney")

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from frmMain2 import *
from libxulpymoney import *

try:
    os.makedirs(os.environ['HOME']+"/.xulpymoney/")
except:
    pass
    

app = QApplication(sys.argv)
QTextCodec.setCodecForTr(QTextCodec.codecForName("UTF-8"));

translator = QTranslator(app)
locale=QLocale()
a=locale.system().name()
if len(a)!=2:
    a=a[:-len(a)+2]

translator.load("/usr/lib/xulpymoney/xulpymoney_" + a + ".qm")
app.installTranslator(translator);

tmp=QApplication.translate("xulpymoney", "Lenguage local detectado: {0}".format(a))
print ((tmp))


frmMain = frmMain2() 
frmMain.show()

sys.exit(app.exec_())
