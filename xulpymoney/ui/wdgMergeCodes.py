
from PyQt5.QtWidgets import QWidget, QTableWidgetItem
from xulpymoney.ui.Ui_wdgMergeCodes import Ui_wdgMergeCodes
from xulpymoney.libxulpymoneyfunctions import qcenter, qmessagebox

class wdgMergeCodes(QWidget, Ui_wdgMergeCodes):
    def __init__(self, mem,  origen, destino, parent = None, name = None, modal = False):
        QWidget.__init__(self,  parent)
        self.mem=mem
        self.origen=origen
        self.destino=destino
        self.setupUi(self)
         

        self.table.settings(self.mem, "wdgMergeCodes") 
        self.reload()
        
    def on_cmdInterchange_released(self):
        tmp=self.origen
        self.origen=self.destino
        self.destino=tmp
        self.reload()
    
    def reload(self):
        #Carga tabla origen
        cur = self.mem.con.cursor()
        self.table.setItem(0, 0, qcenter(str(self.destino.id)))
        self.table.item(0, 0).setIcon(self.destino.stockmarket.country.qicon())
        self.table.setItem(0, 1, QTableWidgetItem(self.destino.name))
        self.table.setItem(0, 2, QTableWidgetItem(self.destino.isin))
        cur.execute("select count(*) from quotes where id=%s", (self.destino.id, ))
        self.table.setItem(0, 3, QTableWidgetItem(str(cur.fetchone()[0])))
        cur.execute("select count(*) from dps where id=%s", (self.destino.id, ))
        self.table.setItem(0, 4, QTableWidgetItem(str(cur.fetchone()[0])))

        ##################
        self.table.setItem(1, 0, qcenter(str(self.origen.id)))
        self.table.item(1, 0).setIcon(self.origen.stockmarket.country.qicon())
        self.table.setItem(1, 1, QTableWidgetItem(self.origen.name))
        self.table.setItem(1, 2, QTableWidgetItem(self.origen.isin))
        cur.execute("select count(*) from quotes where id=%s", (self.origen.id, ))
        self.table.setItem(1, 3, QTableWidgetItem(str(cur.fetchone()[0])))
        cur.execute("select count(*) from dps where id=%s", (self.origen.id, ))
        self.table.setItem(1, 4, QTableWidgetItem(str(cur.fetchone()[0])))
        cur.close()         
        
        if self.origen.is_deletable()==False:
            qmessagebox(self.tr("I couldn't do the merge, because product is marked as not removable"))
            self.cmd.setEnabled(False)
        else:
            self.cmd.setEnabled(True)
            
        
  
    def on_cmd_released(self):
        cur=self.mem.con.cursor()
        cur.execute("update quotes set id=%s  where id=%s", (self.destino.id, self.origen.id))
        cur.execute("update dps set id=%s where id=%s", (self.destino.id, self.origen.id))
        cur.execute("delete from quotes where id=%s", (self.origen.id, ))
        cur.execute("delete from products where id=%s", (self.origen.id, ))
        cur.execute("delete from estimations_dps where id=%s", (self.origen.id, ))
        cur.execute("delete from estimations_eps where id=%s", (self.origen.id, ))
        cur.execute("delete from dps where id=%s", (self.origen.id, ))
        self.mem.con.commit()
        cur.close()   
        qmessagebox(self.tr("You have to update Xulpymoney if the deleted product is used in Xulpymoney"))
        self.cmd.setEnabled(False)
