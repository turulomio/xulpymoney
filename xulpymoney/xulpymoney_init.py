#!/usr/bin/python3
import sys,  os

sys.path.append("/usr/lib/xulpymoney")

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from frmInit import *

try:
    os.makedirs( os.environ['HOME']+"/.xulpymoney/")
except:
    pass

app = QApplication(sys.argv)

translator = QTranslator(app)
locale=QLocale()
a=locale.system().name()
if len(a)!=2:
    a=a[:-len(a)+2]
s= tr(  "Local language detected:{0}").format(a)
print (s)
translator.load("/usr/lib/xulpymoney/xulpymoney_" + a + ".qm")
app.installTranslator(translator);

frm = frmInit() 
frm.show()

sys.exit(app.exec_())
