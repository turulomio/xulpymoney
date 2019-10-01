## @namespace xulpymoney.xulpymoney
## @brief Main Xulpymoney script.
from PyQt5.QtWidgets import  QDialog
from xulpymoney.mem import MemXulpymoney
from xulpymoney.ui.frmAccess import frmAccess
from xulpymoney.ui.frmMain import frmMain
from sys import exit

def main():
    from PyQt5 import QtWebEngineWidgets # To avoid error must be imported before QCoreApplication
    dir(QtWebEngineWidgets)
    
    mem=MemXulpymoney()
    mem.run()
    mem.frmAccess=frmAccess("xulpymoney","frmAccess")
    mem.frmAccess.setResources(":/xulpymoney/books.png", ":/xulpymoney/xulpymoney.png")
    mem.frmAccess.setLabel(mem.tr("Please login to the Xulpymoney database"))
    mem.frmAccess.exec_()

    if mem.frmAccess.result()==QDialog.Accepted:
        mem.con=mem.frmAccess.con
        mem.settings=mem.frmAccess.settings
        mem.setLocalzone()#Needs settings in mem

        mem.frmMain = frmMain(mem)
        mem.frmMain.show()
        exit(mem.app.exec_())
