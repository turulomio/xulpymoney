#!/usr/bin/python3
import sys, os

sys.path.append("/usr/lib/xulpymoney")

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from frmMain import *

try:
    os.makedirs(os.environ['HOME'] + "/.xulpymoney/")
except:
    pass

app = QApplication(sys.argv)
app.setOrganizationName("Mariano Muñoz ©")
app.setOrganizationDomain("turulomio.users.sourceforge.net")
app.setApplicationName("Xulpymoney")
#QTextCodec.setCodecForTr(QTextCodec.codecForName("UTF-8"))


mem=MemXulpymoney()

if "admin" in sys.argv:
    mem.adminmode=True

mem.setQTranslator(QTranslator(app))
mem.qtranslator.load("/usr/lib/xulpymoney/xulpymoney_{0}.qm".format(mem.config.get_value("settings", "language")))
app.installTranslator(mem.qtranslator)

mem.frmMain = frmMain(mem)
mem.frmMain.init__continue()
mem.frmMain.show()

sys.exit(app.exec_())
