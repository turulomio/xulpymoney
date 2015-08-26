from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from Ui_wdgSimulationsAdd import *
from libxulpymoney import Assets,  Simulation,  Connection,  DBAdmin

class wdgSimulationsAdd(QWidget, Ui_wdgSimulationsAdd):
    def __init__(self, mem,  parent = None, name = None):
        QWidget.__init__(self,  parent)
        self.setupUi(self)
        self.mem=mem
        self.parent=parent
        self.mem.simulationtypes.qcombobox(self.cmbSimulationTypes)
        self.wdgStarting.set(self.mem, Assets(self.mem).first_datetime_with_user_data(), self.mem.localzone)
        self.wdgEnding.set(self.mem)
        self.simcon=None#Simulation connection


    @pyqtSlot()
    def on_buttonbox_accepted(self):
        if self.mem.con.is_superuser()==False:
            self.mem.frmMain.access.qmessagebox_error_not_superuser()
            self.parent.reject()
            return
        
        
        type_id=self.cmbSimulationTypes.itemData(self.cmbSimulationTypes.currentIndex())
        s=Simulation(self.mem, self.mem.con.db).init__create(type_id, self.wdgStarting.datetime(), self.wdgEnding.datetime())
        s.save()
        self.simcon=Connection().init__create(self.mem.con.user, self.mem.con.password, self.mem.con.server, self.mem.con.port, self.mem.con.db)
        self.simcon.connect()

        
        if self.simcon.is_active()==False:
            self.access.qmessagebox_error_connecting()
            self.mem.con.rollback()
            self.parent.reject()
            return
            

        admin=DBAdmin(self.simcon)
        admin.create_db(s.simulated_db())
        if s.type==1:
            pass
            
            
        self.mem.con.commit()
        self.simcon.commit()
        self.parent.accept()    
        
    @pyqtSlot()
    def on_buttonbox_rejected(self):
        self.parent.reject()
