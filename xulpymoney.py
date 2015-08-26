#!/usr/bin/python3
import sys
import os

sys.path.append("/usr/lib/xulpymoney")

from PyQt5.QtCore import *
from PyQt5.QtGui import *
import libdbupdates
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
mem.qtranslator.load("/usr/lib/xulpymoney/xulpymoney_{0}.qm".format(mem.config.get_value("settings", "language")))
app.installTranslator(mem.qtranslator)



access=frmAccess(mem)
access.setLabel(tr("Please login to the xulpymoney database"))
access.config_load()
access.exec_()

if access.result()==QDialog.Rejected: 
    access.qmessagebox_error_connecting()
    sys.exit(1)
access.config_save()
mem.con=access.con

##Update database
update=libdbupdates.Update(mem)
if update.need_update()==True:
    if update.check_superuser_role(access.txtUser.text())==True:
        update.run()
    else:
        m=QMessageBox()
        m.setIcon(QMessageBox.Information)
        m.setText(tr("Xulpymoney needs to be updated. Please login with a superuser role."))
        m.exec_()   
        sys.exit(2)
if "admin" in sys.argv:
    mem.adminmode=True


mem.frmMain = frmMain(mem)
mem.frmMain.show()

sys.exit(app.exec_())
