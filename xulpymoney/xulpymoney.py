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
from libxulpymoneyversion import version, version_date
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
parser.add_argument('--version', action='version', version="{} ({})".format(version, version_date()))
parser.add_argument('--debug', help=app.translate("devicesinlan", "Debug program information"), choices=["DEBUG","INFO","WARNING","ERROR","CRITICAL"], default="ERROR")
args=parser.parse_args()        

#Por defecto se pone WARNING y mostrar´ia ERROR y CRITICAL
logFormat = "%(asctime)s.%(msecs)03d %(levelname)s %(message)s [%(module)s:%(lineno)d]"
dateFormat='%F %I:%M:%S'

if args.debug=="DEBUG":#Show detailed information that can help with program diagnosis and troubleshooting. CODE MARKS
    logging.basicConfig(level=logging.DEBUG, format=logFormat, datefmt=dateFormat)
elif args.debug=="INFO":#Everything is running as expected without any problem. TIME BENCHMARCKS
    logging.basicConfig(level=logging.INFO, format=logFormat, datefmt=dateFormat)
elif args.debug=="WARNING":#The program continues running, but something unexpected happened, which may lead to some problem down the road. THINGS TO DO
    logging.basicConfig(level=logging.WARNING, format=logFormat, datefmt=dateFormat)
elif args.debug=="ERROR":#The program fails to perform a certain function due to a bug.  SOMETHING BAD LOGIC
    logging.basicConfig(level=logging.ERROR, format=logFormat, datefmt=dateFormat)
elif args.debug=="CRITICAL":#The program encounters a serious error and may stop running. ERRORS
    logging.basicConfig(level=logging.CRITICAL, format=logFormat, datefmt=dateFormat)

logging.info("Debug level set to {}".format(args.debug))

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
