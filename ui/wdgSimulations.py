from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from wdgSimulationsAdd import *
from Ui_wdgSimulations import *

class wdgSimulations(QWidget, Ui_wdgSimulations):
    def __init__(self, mem,  parent = None, name = None):
        QWidget.__init__(self,  parent)
        self.setupUi(self)
        self.mem=mem
        self.parent=parent

    def on_cmdCreate_released(self):
        d=QDialog(self)     
        d.setWindowTitle(self.tr("Create new simulation"))
        t=wdgSimulationsAdd(self.mem, d)
        lay = QVBoxLayout(d)
        lay.addWidget(t)
        d.exec_()
        
