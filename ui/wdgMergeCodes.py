from PyQt4.QtCore import *
from PyQt4.QtGui import *

from Ui_wdgMergeCodes import *
from libxulpymoney import *

class wdgMergeCodes(QWidget, Ui_wdgMergeCodes):
    def __init__(self, mem,  origen, destino, parent = None, name = None, modal = False):
        QWidget.__init__(self,  parent)
        self.mem=mem
        self.origen=origen
        self.destino=destino
        self.setupUi(self)

        self.table.settings("wdgMergeCodes",  self.mem)    
        self.reload()
        
    def on_cmdInterchange_released(self):
        tmp=self.origen
        self.origen=self.destino
        self.destino=tmp
        self.reload()
    
    def reload(self):
        #Carga tabla origen
        cur = self.mem.conms.cursor()
        self.table.setItem(0, 0, qcenter(str(self.destino.id)))
        self.table.item(0, 0).setIcon(self.destino.stockexchange.country.qicon())
        self.table.setItem(0, 1, QTableWidgetItem(self.destino.name))
        self.table.setItem(0, 2, QTableWidgetItem(self.destino.isin))
#        self.table.setItem(0, 3, QTableWidgetItem(self.destino.agrupations))
        cur.execute("select count(*) from quotes where id=%s", (self.destino.id, ))
        self.table.setItem(0, 4, QTableWidgetItem(str(cur.fetchone()[0])))
        cur.execute("select count(*) from estimations_dps where id=%s", (self.destino.id, ))
        self.table.setItem(0, 5, QTableWidgetItem(str(cur.fetchone()[0])))

        ##################
        self.table.setItem(1, 0, qcenter(str(self.origen.id)))
        self.table.item(1, 0).setIcon(self.origen.stockexchange.country.qicon())
        self.table.setItem(1, 1, QTableWidgetItem(self.origen.name))
        self.table.setItem(1, 2, QTableWidgetItem(self.origen.isin))
#        self.table.setItem(1, 3, QTableWidgetItem(self.origen.agrupations))
        cur.execute("select count(*) from quotes where id=%s", (self.origen.id, ))
        self.table.setItem(1, 4, QTableWidgetItem(str(cur.fetchone()[0])))
        cur.execute("select count(*) from estimations_dps where id=%s", (self.origen.id, ))
        self.table.setItem(1, 5, QTableWidgetItem(str(cur.fetchone()[0])))
        cur.close()         
        
        if self.origen.deletable==False:
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.trUtf8("No se ha puede realizar esta combinación, ya que la inversión a borrar esta marcada como NO BORRABLE"))
            m.exec_()     
            self.cmd.setEnabled(False)
        else:
            self.cmd.setEnabled(True)
            
        
  
    def on_cmd_released(self):
        cur = self.mem.conms.cursor()
        cur.execute("select merge_codes(%s,%s)",(self.destino.id, self.origen.id ))
        con.commit()
        cur.close()       
        self.cmd.setEnabled(False)
