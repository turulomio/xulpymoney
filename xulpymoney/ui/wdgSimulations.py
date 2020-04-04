from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QWidget,  QDialog, QVBoxLayout, QMessageBox
from xulpymoney.ui.wdgSimulationsAdd import wdgSimulationsAdd
from xulpymoney.admin_pg import AdminPG
import xulpymoney.ui.frmMain
from xulpymoney.ui.Ui_wdgSimulations import Ui_wdgSimulations
from xulpymoney.objects.simulation import  SimulationManager
from xulpymoney.mem import MemXulpymoney
from xulpymoney.connection_pg_qt import ConnectionQt
from xulpymoney.ui.myqwidgets import qmessagebox
from xulpymoney.version import __versiondate__

class wdgSimulations(QWidget, Ui_wdgSimulations):
    def __init__(self, mem,  parent = None, name = None):
        QWidget.__init__(self,  parent)
        self.setupUi(self)
        self.resize(1000, 600)
        self.mem=mem
        self.parent=parent
        self.mqtwSimulations.setSettings(self.mem.settings, "wdgSimulations", "mqtwSimulations")
        self.simulations=SimulationManager(self.mem)
        cur=self.mem.con.cursor()
        self.simulations.load_from_db(self.mem.con.mogrify("select * from simulations where database=%s order by creation",(self.mem.con.db, ) ), self.mem.con.db)
        cur.close()
        self.reload()
        self.mem_sim=None
        
    def reload(self):
        self.simulations.myqtablewidget(self.mqtwSimulations)

    def on_cmdCreate_released(self):
        d=QDialog(self)     
        d.setWindowTitle(self.tr("Create new simulation"))
        t=wdgSimulationsAdd(self.mem, d)
        lay = QVBoxLayout(d)
        lay.addWidget(t)
        d.exec_()
        if d.result()==QDialog.Accepted:
            self.simulations.append(t.simulation)
            self.reload()

    def on_mqtwSimulations_itemSelectionChanged(self):
        self.simulations.selected=None
        for i in self.mqtwSimulations.table.selectedItems():#itera por cada item no row.
            if i.column()==0:
                self.simulations.selected=self.simulations.arr[i.row()]
                
        if self.simulations.selected==None:
            self.cmdDelete.setEnabled(False)
            self.cmdConnect.setEnabled(False)
        else:
            self.cmdDelete.setEnabled(True)
            self.cmdConnect.setEnabled(True)
            
    def on_cmdDelete_released(self):
        reply = QMessageBox.question(self, 'Deleting a simulation', self.tr("Do you really want to delete this simulation?"), QMessageBox.Yes, QMessageBox.No)            
        if reply == QMessageBox.Yes:
            self.simulations.delete(self.simulations.selected)
            
            simcon=ConnectionQt().init__create(self.mem.con.user, self.mem.con.password, self.mem.con.server, self.mem.con.port, self.mem.con.db)
            simcon.connect()


            admin=AdminPG(self.txtUser.text(), self.txtPass.text(),  self.txtServer.text(),  self.txtPort.text())
            admin.drop_db(self.simulations.selected.simulated_db())
            self.mem.con.commit()
            simcon.commit()            
            self.reload()

    def on_cmdConnect_released(self):
        if not self.mem.con.is_superuser():
            qmessagebox(self.tr("The role of the user is not an administrator"))
            return
        simcon=ConnectionQt().init__create(self.mem.con.user, self.mem.con.password, self.mem.con.server, self.mem.con.port, self.simulations.selected.simulated_db())
        simcon.connect()
        self.mem_sim=MemXulpymoney()
        self.mem_sim.con=simcon
        
        ##Update database
        update=xulpymoney.libdbupdates.Update(self.mem_sim, "Qt")
        if update.need_update()==True:
            update.run()
        
        self.mem_sim.frmMain = xulpymoney.ui.frmMain.frmMain(self.mem_sim)
        #No puedo visualizarlo, luego voy a usar un qdialog , ya que qmainwindow viene de qwidget.
        
        d=QDialog(self)        
        d.setStyleSheet("QDialog { background-color: rgb(255, 182, 182);  }");        
        d.setWindowTitle(self.tr("Xulpymoney SIMULATED IN {} 2010-{} \xa9").format(self.simulations.selected.simulated_db(),  __versiondate__.year))
        icon = QIcon()
        icon.addPixmap(QPixmap(":/xulpymoney/replication.png"), QIcon.Normal, QIcon.Off)
        d.setWindowIcon(icon)
        d.showMaximized()
        lay = QVBoxLayout(d)
        lay.addWidget(self.mem_sim.frmMain)
        d.exec_()
        
