#!/usr/bin/python3
import sys,  os
import platform

if platform.system()=="Windows":
    sys.path.append("ui/")
    sys.path.append("images/")
else:
    sys.path.append("/usr/lib/xulpymoney")

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from frmInit import *

try:
    os.makedirs( os.environ['HOME']+"/.xulpymoney/tmp/")
except:
    pass

app = QApplication(sys.argv)
app.setOrganizationName("Mariano Muñoz ©")
app.setOrganizationDomain("turulomio.users.sourceforge.net")
app.setApplicationName("Xulpymoney Init")

frm = frmInit() 
frm.show()

sys.exit(app.exec_())
