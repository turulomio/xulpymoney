#!/usr/bin/python3
import sys
import os
import platform

if platform.system()=="Windows":
    sys.path.append("ui/")
    sys.path.append("images/")
else:
    sys.path.append("/usr/lib/xulpymoney")

from PyQt5.QtCore import *
from PyQt5.QtGui import *
import libdbupdates
from libqmessagebox import *
from frmMain import *

try:
    os.makedirs(os.environ['HOME'] + "/.xulpymoney/")
except:
    pass

app = QApplication(sys.argv)
app.setOrganizationName("Mariano Muñoz ©")
app.setOrganizationDomain("turulomio.users.sourceforge.net")
app.setApplicationName("Xulpymoney")


mem=MemXulpymoney()

mem.setQTranslator(QTranslator(app))
mem.qtranslator.load("/usr/lib/xulpymoney/xulpymoney_{0}.qm".format(mem.language.id))
app.installTranslator(mem.qtranslator)
print (mem.language.id)     

access=frmAccess(mem)
access.setLabel(QApplication.translate("Core","Please login to the xulpymoney database"))
access.config_load()
access.exec_()

if access.result()==QDialog.Rejected: 
    qmessagebox_connexion_error(access.con.db, access.con.server)
    sys.exit(1)
access.config_save()
mem.con=access.con

##Update database
update=libdbupdates.Update(mem)
if update.need_update()==True:
    if mem.con.is_superuser():
        update.run()
    else:
        qmessagebox_xulpymoney_update_and_superuser()
        sys.exit(2)
if "admin" in sys.argv:
    mem.adminmode=True


mem.frmMain = frmMain(mem)
mem.frmMain.show()

sys.exit(app.exec_())
