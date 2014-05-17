#!/usr/bin/python3
import sys, os

sys.path.append("/usr/lib/xulpymoney")

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from frmMain import *

try:
    os.makedirs(os.environ['HOME'] + "/.xulpymoney/")
except:
    pass

app = QApplication(sys.argv)
QTextCodec.setCodecForTr(QTextCodec.codecForName("UTF-8"))

mem=MemXulpymoney()
mem.setQTranslator(QTranslator(app))
#
#locale = QLocale()
#a = locale.system().name()
#if len(a)!=2:
#    a = a[:-len(a) + 2]
a=mem.config.get_value("settings", "language")
mem.qtranslator.load("/usr/lib/xulpymoney/xulpymoney_" + a + ".qm")
app.installTranslator(mem.qtranslator)

#s = QApplication.translate("Core",  "Local language detected: {0}".format(a))
#print (s)

frmMain = frmMain(mem)
frmMain.show()

sys.exit(app.exec_())
