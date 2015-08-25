from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from wdgSimulationsAdd import *
from Ui_wdgSimulations import *
from libxulpymoney import SetSimulations

class wdgSimulations(QWidget, Ui_wdgSimulations):
    def __init__(self, mem,  parent = None, name = None):
        QWidget.__init__(self,  parent)
        self.setupUi(self)
        self.resize(1000, 600)
        self.mem=mem
        self.parent=parent
        self.simulations=SetSimulations(self.mem)
        cur=self.mem.con.cursor()
        database=self.mem.frmMain.access.txtDB.text()
        self.simulations.load_from_db(cur.mogrify("select * from simulations where database=%s order by creation",(database, ) ), database)
        cur.close()
        self.reload()
        
    def reload(self):
        self.simulations.myqtablewidget(self.tblSimulations, "wdgSimulations")

    def on_cmdCreate_released(self):
        d=QDialog(self)     
        d.setWindowTitle(self.tr("Create new simulation"))
        t=wdgSimulationsAdd(self.mem, d)
        lay = QVBoxLayout(d)
        lay.addWidget(t)
        d.exec_()
        if t.result==QDialog.Accepted:
            self.reload()
            
        
