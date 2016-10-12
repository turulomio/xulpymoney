#!/usr/bin/python3
import sys
import platform
import logging

#Por defecto se pone WARNING y mostrar´ia ERROR y CRITICAL
logFormat = "%(asctime)s %(levelname)s %(module)s:%(lineno)d at %(funcName)s. %(message)s"
dateFormat='%Y%m%d %I%M%S'
if "DEBUG" in sys.argv:#Show detailed information that can help with program diagnosis and troubleshooting.
    logging.basicConfig(level=logging.DEBUG, format=logFormat, datefmt=dateFormat)
elif "INFO" in sys.argv:#Everything is running as expected without any problem.
    logging.basicConfig(level=logging.INFO, format=logFormat, datefmt=dateFormat)
elif "WARNING" in sys.argv:#The program continues running, but something unexpected happened, which may lead to some problem down the road.
    logging.basicConfig(level=logging.WARNING, format=logFormat, datefmt=dateFormat)
elif "ERROR" in sys.argv:#The program fails to perform a certain function due to a bug.
    logging.basicConfig(level=logging.ERROR, format=logFormat, datefmt=dateFormat)
elif "CRITICAL" in sys.argv:#The program encounters a serious error and may stop running.
    logging.basicConfig(level=logging.CRITICAL, format=logFormat, datefmt=dateFormat)

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

app = QApplication(sys.argv)
app.setOrganizationName("Mariano Muñoz ©")
app.setOrganizationDomain("turulomio.users.sourceforge.net")
app.setApplicationName("Xulpymoney")


mem=MemXulpymoney()
mem.setQTranslator(QTranslator(app))
mem.languages.cambiar(mem.language.id)

access=frmAccess(mem)
access.setLabel(QApplication.translate("Core","Please login to the xulpymoney database"))
access.config_load()
access.exec_()

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
