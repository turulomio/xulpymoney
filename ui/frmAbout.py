from PyQt4.QtCore import *
from PyQt4.QtGui import *
from libxulpymoney import *
from Ui_frmAbout import *

class frmAbout(QDialog, Ui_frmAbout):
    def __init__(self, mem,  parent = None, name = None, modal = False):
        """
        Constructor
        
        @param parent The parent widget of this dialog. (QWidget)
        @param name The name of this dialog. (QString)
        @param modal Flag indicating a modal dialog. (boolean)
        """
        self.mem=mem
        QDialog.__init__(self, parent)
        if name:
            self.setObjectName(name)
        self.setModal(True)
        self.setupUi(self)
        
        self.tblStatistics.settings("frmAbout", self.mem)
        self.load_tblStatistics() 
        self.connect(self.cmd, SIGNAL("clicked()"), self.on_cmd_clicked)
    
    @pyqtSignature("")
    def on_cmd_clicked(self):
        """
        Slot documentation goes here.
        """
        self.done(0)
    
    def load_tblStatistics(self):
        def pais(cur, columna, bolsa):
            """Si pais es Null es para todos"""
            total=0
            cur.execute("select count(*) from products where type=1 and id_bolsas=%s", (bolsa.id,))
            tmp=cur.fetchone()[0]
            total=total+tmp
            self.tblStatistics.setItem(0, columna , qcenter(tmp))
            cur.execute("select count(*) from products where type=2 and id_bolsas=%s", (bolsa.id,))
            tmp=cur.fetchone()[0]
            total=total+tmp
            self.tblStatistics.setItem(1, columna , qcenter(tmp))
            cur.execute("select count(*) from products where type=3 and id_bolsas=%s", (bolsa.id,))
            tmp=cur.fetchone()[0]
            total=total+tmp
            self.tblStatistics.setItem(2, columna , qcenter(tmp))
            cur.execute("select count(*) from products where type=4 and id_bolsas=%s", (bolsa.id,))
            tmp=cur.fetchone()[0]
            total=total+tmp
            self.tblStatistics.setItem(3, columna , qcenter(tmp))
            cur.execute("select count(*) from products where type=5 and id_bolsas=%s", (bolsa.id,))
            tmp=cur.fetchone()[0]
            total=total+tmp
            self.tblStatistics.setItem(4, columna , qcenter(tmp))
            cur.execute("select count(*) from products where type=7 and id_bolsas=%s", (bolsa.id,))
            tmp=cur.fetchone()[0]
            total=total+tmp
            self.tblStatistics.setItem(5, columna , qcenter(tmp))
            cur.execute("select count(*) from products where type=9 and id_bolsas=%s", (bolsa.id,))
            tmp=cur.fetchone()[0]
            total=total+tmp
            self.tblStatistics.setItem(6, columna , qcenter(tmp))
            self.tblStatistics.setItem(7, columna , QTableWidgetItem(""))
            self.tblStatistics.setItem(8, columna , qcenter(total))
            self.tblStatistics.horizontalHeaderItem (columna).setIcon(bolsa.country.qicon())
            self.tblStatistics.horizontalHeaderItem (columna).setToolTip((bolsa.country.name))
                
        def todos(cur):
            """Si pais es Null es para todos"""
            total=0
            cur.execute("select count(*) from products where type=1 ")
            tmp=cur.fetchone()[0]
            total=total+tmp
            self.tblStatistics.setItem(0, 0 , qcenter(tmp))
            cur.execute("select count(*) from products where type=2 ")
            tmp=cur.fetchone()[0]
            total=total+tmp
            self.tblStatistics.setItem(1, 0 , qcenter(tmp))
            cur.execute("select count(*) from products where type=3 ")
            tmp=cur.fetchone()[0]
            total=total+tmp
            self.tblStatistics.setItem(2, 0 , qcenter(tmp))
            cur.execute("select count(*) from products where type=4 ")
            tmp=cur.fetchone()[0]
            total=total+tmp
            self.tblStatistics.setItem(3, 0 , qcenter(tmp))
            cur.execute("select count(*) from products where type=5 ")
            tmp=cur.fetchone()[0]
            total=total+tmp
            self.tblStatistics.setItem(4, 0 , qcenter(tmp))
            cur.execute("select count(*) from products where type=7 ")
            tmp=cur.fetchone()[0]
            total=total+tmp
            self.tblStatistics.setItem(5, 0 , qcenter(tmp))
            cur.execute("select count(*) from products where type=9 ")
            tmp=cur.fetchone()[0]
            total=total+tmp
            self.tblStatistics.setItem(6, 0 , qcenter(tmp))
            self.tblStatistics.setItem(7, 0 , QTableWidgetItem(""))
            self.tblStatistics.setItem(8, 0 , qcenter(total))

    
        cur = self.mem.con.cursor()
        todos(cur)
        pais(cur, 1, self.mem.stockexchanges.find(1))
        pais(cur, 2, self.mem.stockexchanges.find(2))
        pais(cur, 3, self.mem.stockexchanges.find(3))
        pais(cur, 4, self.mem.stockexchanges.find(4))
        pais(cur, 5, self.mem.stockexchanges.find(5))
        pais(cur, 6,self.mem.stockexchanges.find(6))
        pais(cur, 7, self.mem.stockexchanges.find(7))
        pais(cur, 8, self.mem.stockexchanges.find(8))
        pais(cur, 9, self.mem.stockexchanges.find(9))
        pais(cur, 10, self.mem.stockexchanges.find(10))
        pais(cur, 11, self.mem.stockexchanges.find(11))
        pais(cur, 12, self.mem.stockexchanges.find(12))
        pais(cur, 13, self.mem.stockexchanges.find(13))
        cur.close()
