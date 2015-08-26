from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from Ui_wdgSimulationsAdd import *
from libxulpymoney import Assets,  Simulation

class wdgSimulationsAdd(QWidget, Ui_wdgSimulationsAdd):
    def __init__(self, mem,  parent = None, name = None):
        QWidget.__init__(self,  parent)
        self.setupUi(self)
        self.mem=mem
        self.parent=parent
        self.mem.simulationtypes.qcombobox(self.cmbSimulationTypes)
        self.wdgStarting.set(self.mem, Assets(self.mem).first_datetime_with_user_data(), self.mem.localzone)
        self.wdgEnding.set(self.mem)

    @pyqtSlot()
    def on_buttonbox_accepted(self):
        database=self.mem.frmMain.access.txtDB.text()
        type_id=self.cmbSimulationTypes.itemData(self.cmbSimulationTypes.currentIndex())
        s=Simulation(self.mem, database).init__create(type_id, self.wdgStarting.datetime(), self.wdgEnding.datetime())
        s.save()
        self.mem.con.commit()
        self.parent.accept()    
        
    @pyqtSlot()
    def on_buttonbox_rejected(self):
        self.parent.reject()
