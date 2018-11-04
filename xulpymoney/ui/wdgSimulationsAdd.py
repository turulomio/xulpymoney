from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget
from xulpymoney.ui.Ui_wdgSimulationsAdd import Ui_wdgSimulationsAdd
from xulpymoney.libxulpymoney import Assets,  Simulation,  Connection,  DBAdmin
from xulpymoney.libxulpymoneyfunctions import qmessagebox

class wdgSimulationsAdd(QWidget, Ui_wdgSimulationsAdd):
    def __init__(self, mem,   parent = None, name = None):
        """Simulations is the SimulationManager where the new simulation is going to be appended"""
        QWidget.__init__(self,  parent)
        self.setupUi(self)
        self.mem=mem
        self.parent=parent
        self.simulation=None#Simulation to be created
        self.mem.simulationtypes.qcombobox(self.cmbSimulationTypes)
        self.wdgStarting.set(self.mem, Assets(self.mem).first_datetime_with_user_data(), self.mem.localzone)
        self.wdgEnding.set(self.mem)
        self.simcon=None#Simulation connection

    @pyqtSlot()
    def on_buttonbox_accepted(self):
        if self.mem.con.is_superuser()==False:
            qmessagebox("The role of the user is not an administrator")
            self.parent.reject()
            return
        
        type_id=self.cmbSimulationTypes.itemData(self.cmbSimulationTypes.currentIndex())
        self.simulation=Simulation(self.mem, self.mem.con.db).init__create(type_id, self.wdgStarting.datetime(), self.wdgEnding.datetime())
        self.simulation.save()
        
        
        #Necesita solo roll superusuario y self.mem.con lo tiene
        createadmin=DBAdmin(self.mem.con)
        createadmin.create_db(self.simulation.simulated_db())
        self.mem.con.commit()

        #Crea nueva conexión
        self.con_sim=Connection().init__create(self.mem.con.user, self.mem.con.password, self.mem.con.server, self.mem.con.port, self.simulation.simulated_db())
        self.con_sim.connect()        
        admin=DBAdmin(self.con_sim)
        admin.xulpymoney_basic_schema()
        self.con_sim.commit()
        if self.simulation.type.id==1:#Copy between dates                    
            already_banks=self.con_sim.cursor_one_column("select id_entidadesbancarias from entidadesbancarias order by id_entidadesbancarias")
            mog=self.mem.con.mogrify("select * from entidadesbancarias where id_entidadesbancarias not in %s  order by id_entidadesbancarias", (tuple(already_banks), ))
            admin.copy(self.mem.con, mog,  "entidadesbancarias")
            
            admin.copy(self.mem.con, "select * from cuentas  order by id_cuentas",  "cuentas")
            
            admin.copy(self.mem.con, "select * from tarjetas  order by id_tarjetas",  "tarjetas")

            already_products=self.con_sim.cursor_one_column("select id from products order by id")#Rest personal products
            mog=self.mem.con.mogrify("select * from products where id not in %s  order by id", (tuple(already_products), ))
            admin.copy(self.mem.con, mog,  "products")
            
            admin.copy(self.mem.con, "select * from quotes ",  "quotes")
            
            admin.copy(self.mem.con, "select * from dps ",  "dps")
            
            admin.copy(self.mem.con, "select * from estimations_dps",  "estimations_dps")
            
            admin.copy(self.mem.con, "select * from estimations_eps ",  "estimations_eps")
            
            admin.copy(self.mem.con, "select * from inversiones order by id_inversiones",  "inversiones")
            
            admin.copy(self.mem.con, "select * from dividends order by id_dividends",  "dividends")
            
            already_conceptos=self.con_sim.cursor_one_column("select id_conceptos from conceptos order by id_conceptos")
            mog=self.mem.con.mogrify("select * from conceptos where id_conceptos not in %s  order by id_conceptos ", (tuple(already_conceptos), ))
            admin.copy(self.mem.con, mog,  "conceptos")
            
        self.con_sim.commit()
        self.con_sim.disconnect()
        self.parent.accept()    
        
    @pyqtSlot()
    def on_buttonbox_rejected(self):
        self.parent.reject()
