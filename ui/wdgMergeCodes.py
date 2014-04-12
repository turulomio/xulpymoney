from PyQt4.QtCore import *
from PyQt4.QtGui import *

from Ui_wdgMergeCodes import *
from libxulpymoney import *

class wdgMergeCodes(QWidget, Ui_wdgMergeCodes):
    def __init__(self, cfg,  idorigen, iddestino, parent = None, name = None, modal = False):
        QWidget.__init__(self,  parent)
        self.cfg=cfg
        self.idorigen=idorigen
        self.iddestino=iddestino
        if name:
            self.setObjectName(name)
        self.setupUi(self)

        self.table.settings("wdgMergeCodes",  self.cfg)    
        self.reload()
        
    def on_cmdInterchange_released(self):
        tmp=self.idorigen
        self.idorigen=self.iddestino
        self.iddestino=tmp
        self.reload()
    
    def reload(self):
        #Carga tabla origen
        con=self.cfg.connect_mystocks()
        cur = con.cursor()
        cur.execute("select * from products where id=%s", (self.iddestino, ))
        d=cur.fetchone()
        icon=QtGui.QIcon()
        icon.addPixmap(qpixmap_pais(self.cfg.bolsas[str(d['id_bolsas'])].country), QtGui.QIcon.Normal, QtGui.QIcon.Off)    
        self.table.setItem(0, 0, qcenter(str(self.iddestino)))
        self.table.item(0, 0).setIcon(icon)
        self.table.setItem(0, 1, QTableWidgetItem(d['name']))
        self.table.setItem(0, 2, QTableWidgetItem(d['isin']))
        self.table.setItem(0, 3, QTableWidgetItem(d['agrupations']))
        cur.execute("select count(*) from quotes where id=%s", (self.iddestino, ))
        self.table.setItem(0, 4, QTableWidgetItem(str(cur.fetchone()[0])))
        cur.execute("select count(*) from estimaciones where id=%s", (self.iddestino, ))
        self.table.setItem(0, 5, QTableWidgetItem(str(cur.fetchone()[0])))



##################
        cur.execute("select * from products  where id=%s;", (self.idorigen, ))
        o=cur.fetchone()
        icon=QtGui.QIcon()
        icon.addPixmap(qpixmap_pais(self.cfg.bolsas[str(o['id_bolsas'])].country), QtGui.QIcon.Normal, QtGui.QIcon.Off)    
        self.table.setItem(1, 0, qcenter(str(self.idorigen)))
        self.table.item(1, 0).setIcon(icon)
        self.table.setItem(1, 1, QTableWidgetItem(o['name']))
        self.table.setItem(1, 2, QTableWidgetItem(o['isin']))
        self.table.setItem(1, 3, QTableWidgetItem(o['agrupations']))
        cur.execute("select count(*) from quotes where id=%s", (self.idorigen, ))
        self.table.setItem(1, 4, QTableWidgetItem(str(cur.fetchone()[0])))
        cur.execute("select count(*) from estimaciones where id=%s", (self.idorigen, ))
        self.table.setItem(1, 5, QTableWidgetItem(str(cur.fetchone()[0])))
        cur.close()     
        self.cfg.disconnect_mystocksd(con)         
        
        if o['deletable']==False:
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.trUtf8("No se ha puede realizar esta combinación, ya que la inversión a borrar esta marcada como NO BORRABLE"))
            m.exec_()     
            self.cmd.setEnabled(False)
        else:
            self.cmd.setEnabled(True)
            
        
  
    def on_cmd_released(self):
        con=self.cfg.connect_mystocks()
        cur = con.cursor()
        cur.execute("select merge_codes(%s,%s)",(self.iddestino, self.idorigen ))
        con.commit()
        cur.close()     
        self.cfg.disconnect_mystocksd(con)         
        self.cmd.setEnabled(False)
