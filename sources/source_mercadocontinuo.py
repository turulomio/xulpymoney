#!/usr/bin/python3
import sys
sys.path.append("/usr/lib/xulpymoney")
from PyQt5.QtWidgets import QApplication
from libxulpymoney import MemXulpymoney
from libsources import WorkerMercadoContinuo

app = QApplication(sys.argv)
app.setOrganizationName("Mariano Muñoz ©")
app.setOrganizationDomain("turulomio.users.sourceforge.net")
app.setApplicationName("Xulpymoney")

mem=MemXulpymoney()
mem.init__script('Mercado Continuo Updater')
w=WorkerMercadoContinuo(mem,)
w.setSQL(  "select * from products where 9=any(priority) and obsolete=false;")
w.run()
mem.con.disconnect()

