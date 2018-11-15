#!/usr/bin/python3
## @package xulpymoney
## @brief Main Xulpymoney script.

import sys
import platform
import argparse
import logging
import signal
from colorama import init, Style, Fore

from PyQt5.QtCore import QTranslator
from PyQt5.QtWidgets import QApplication,  QDialog
import xulpymoney.libdbupdates
from xulpymoney.libxulpymoney import MemXulpymoney
from xulpymoney.version import  __versiondate__
from xulpymoney.libxulpymoneyfunctions import addDebugSystem, addCommonToArgParse
from xulpymoney.ui.frmAccess import frmAccess
from xulpymoney.ui.frmMain import frmMain

def signal_handler(signal, frame):
        logging.critical(Style.BRIGHT+Fore.RED+app.translate("Core","You pressed 'Ctrl+C', exiting..."))
        sys.exit(1)

######################

def main():
    init(autoreset=True)

    global app
    app = QApplication(sys.argv)
    app.setOrganizationName("Mariano Muñoz ©")
    app.setOrganizationDomain("turulomio.users.sourceforge.net")
    app.setApplicationName("Xulpymoney")

    signal.signal(signal.SIGINT, signal_handler)

    parser=argparse.ArgumentParser(
            prog='xulpymoney', 
            description=app.translate("Core",'Personal accounting system'),  
            epilog=app.translate("Core","If you like this app, please vote for it in Sourceforge (https://sourceforge.net/projects/xulpymoney/reviews/).")+"\n" +app.translate("Core","Developed by Mariano Muñoz 2015-{}".format(__versiondate__.year)),
            formatter_class=argparse.RawTextHelpFormatter
        )
    addCommonToArgParse(parser)
    if platform.system()=="Windows":
            parser.add_argument('--shortcuts-create', help="Create shortcuts for Windows", action='store_true', default=False)
            parser.add_argument('--shortcuts-remove', help="Remove shortcuts for Windows", action='store_true', default=False)

    args=parser.parse_args()        

    addDebugSystem(args)

    if platform.system()=="Windows":
            if args.shortcuts_create:
                    from xulpymoney.shortcuts import create
                    create()
                    sys.exit(0)
            if args.shortcuts_remove:
                    from xulpymoney.shortcuts import remove
                    remove()
                    sys.exit(0)

    mem=MemXulpymoney()
    mem.setQTranslator(QTranslator(app))
    mem.languages.cambiar(mem.language.id)

    access=frmAccess(mem)
    access.setLabel(QApplication.translate("Core","Please login to the xulpymoney database"))
    access.config_load()
    access.exec_()

    if access.result()==QDialog.Accepted:
        mem.con=access.con

        xulpymoney.libdbupdates.Update(mem)##Update database

        mem.frmMain = frmMain(mem)
        mem.frmMain.show()
        sys.exit(app.exec_())

if __name__=="__main__":
        main()