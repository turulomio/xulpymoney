from xulpymoney.mem import MemInit
from xulpymoney.ui.frmInit import frmInit
from sys import exit

def main():
    mem=MemInit()
    mem.run()
    frm = frmInit(mem)
    frm.show()
    exit(mem.app.exec_())

#
#import sys
#import os
#from PyQt5.QtWidgets import QApplication
#from xulpymoney.ui.frmInit import frmInit
#
#
#def main():
#
#    try:
#        os.makedirs( os.environ['HOME']+"/.xulpymoney/tmp/")
#    except:
#        pass
#    app = QApplication(sys.argv)
#    app.setOrganizationName("Mariano Muñoz ©")
#    app.setOrganizationDomain("turulomio.users.sourceforge.net")
#    app.setApplicationName("Xulpymoney Init")
#
#    frm = frmInit()
#    frm.show()
#
#    sys.exit(app.exec_())
