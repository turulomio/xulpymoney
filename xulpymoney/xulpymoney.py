#!/usr/bin/python3
import sys
import platform
import argparse
import logging
import signal
from colorama import init, Style, Fore

def signal_handler(signal, frame):
        logging.critical(Style.BRIGHT+Fore.RED+app.translate("Core","You pressed 'Ctrl+C', exiting..."))
        sys.exit(1)

######################

init(autoreset=True)

if platform.system()=="Windows":
    sys.path.append("ui/")
    sys.path.append("images/")
else:
    sys.path.append("/usr/lib/xulpymoney")

from PyQt5.QtCore import QTranslator
from PyQt5.QtWidgets import QApplication,  QDialog
import libdbupdates
from libxulpymoney import MemXulpymoney
from libxulpymoneyversion import  version_date
from libxulpymoneyfunctions import addDebugSystem, addCommonToArgParse
from frmAccess import frmAccess
from frmMain import frmMain

app = QApplication(sys.argv)
app.setOrganizationName("Mariano Muñoz ©")
app.setOrganizationDomain("turulomio.users.sourceforge.net")
app.setApplicationName("Xulpymoney")

signal.signal(signal.SIGINT, signal_handler)

parser=argparse.ArgumentParser(
        prog='xulpymoney', 
        description=app.translate("Core",'Personal accounting system'),  
        epilog=app.translate("Core","If you like this app, please vote for it in Sourceforge (https://sourceforge.net/projects/xulpymoney/reviews/).")+"\n" +app.translate("Core","Developed by Mariano Muñoz 2015-{}".format(version_date().year)),
        formatter_class=argparse.RawTextHelpFormatter
    )
addCommonToArgParse(parser)
args=parser.parse_args()        

addDebugSystem(args)

mem=MemXulpymoney()
mem.setQTranslator(QTranslator(app))
mem.languages.cambiar(mem.language.id)

access=frmAccess(mem)
access.setLabel(QApplication.translate("Core","Please login to the xulpymoney database"))
access.config_load()
access.exec_()

if access.result()==QDialog.Accepted:
    mem.con=access.con

    libdbupdates.Update(mem)##Update database

    mem.frmMain = frmMain(mem)
    mem.frmMain.show()
    sys.exit(app.exec_())
