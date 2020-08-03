from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget
from xulpymoney.ui.Ui_wdgSimulationsAdd import Ui_wdgSimulationsAdd
from xulpymoney.objects.assets import Assets
from xulpymoney.objects.simulation import Simulation
#from xulpymoney.xulpymoney_schema import XulpymoneyDatabase
from xulpymoney.ui.myqwidgets import qmessagebox

class wdgSimulationsAdd(QWidget, Ui_wdgSimulationsAdd):
    def __init__(self, mem,   parent = None, name = None):
        """Simulations is the SimulationManager where the new simulation is going to be appended"""
        QWidget.__init__(self,  parent)
        self.setupUi(self)
        self.mem=mem
        self.parent=parent
        self.simulation=None#Simulation to be created
        self.mem.simulationtypes.qcombobox(self.cmbSimulationTypes)
        self.wdgStarting.set(Assets(self.mem).first_datetime_allowed_estimated(), self.mem.localzone_name)
        self.wdgEnding.set(Assets(self.mem).last_datetime_allowed_estimated(), self.mem.localzone_name)
        self.simcon=None#Simulation connection

    @pyqtSlot()
    def on_buttonbox_accepted(self):
        if self.mem.con.is_superuser()==False:
            qmessagebox("The role of the user is not an administrator")
            self.parent.reject()
            return
        
        type_id=self.cmbSimulationTypes.itemData(self.cmbSimulationTypes.currentIndex())
        print(type_id)
        self.simulation=Simulation(self.mem, self.mem.con.db).init__create(type_id, self.wdgStarting.datetime(), self.wdgEnding.datetime())
        self.simulation.save()
        
        newdb=None
        #newdb=XulpymoneyDatabase(self.mem.con.user, self.mem.con.password, self.mem.con.server, self.mem.con.port, self.simulation.simulated_db())
        if newdb.create()==False:
            qmessagebox(self.tr("I couldn't create simulation"))
            return

        if type_id==1:#Copy between dates 
            print("Copying")
            cur=newdb.newdbcon.cursor()#Deleting tables with register from empty creation
            cur.execute("delete from public.products")
            cur.execute("delete from public.conceptos")
            cur.close()
            newdb.copy(self.mem.con, newdb.newdbcon, "select * from entidadesbancarias where id_entidadesbancarias not in (3)",  "entidadesbancarias")#Due to 3 already is in schema
            newdb.copy(self.mem.con, newdb.newdbcon, "select * from cuentas where id_cuentas not in (4)",  "cuentas")
            newdb.copy(self.mem.con, newdb.newdbcon, "select * from tarjetas",  "tarjetas")
            newdb.copy(self.mem.con, newdb.newdbcon, "select * from products",  "products")
            newdb.copy(self.mem.con, newdb.newdbcon, "select * from quotes",  "quotes")
            newdb.copy(self.mem.con, newdb.newdbcon, "select * from dps",  "dps")
            newdb.copy(self.mem.con, newdb.newdbcon, "select * from estimations_dps",  "estimations_dps")
            newdb.copy(self.mem.con, newdb.newdbcon, "select * from estimations_eps ",  "estimations_eps")
            newdb.copy(self.mem.con, newdb.newdbcon, "select * from inversiones",  "inversiones")
            newdb.copy(self.mem.con, newdb.newdbcon, "select * from conceptos",  "conceptos")
            newdb.copy(self.mem.con, newdb.newdbcon, "select * from dividends",  "dividends")
        newdb.newdbcon.commit()
        self.parent.accept()    
        
    @pyqtSlot()
    def on_buttonbox_rejected(self):
        self.parent.reject()
