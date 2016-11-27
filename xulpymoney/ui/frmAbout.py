from PyQt5.QtWidgets import QDialog, QTableWidgetItem
from libxulpymoney import qcenter
from Ui_frmAbout import Ui_frmAbout

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
        
        self.tblStatistics.settings(self.mem, "frmAbout")
        self.load_tblStatistics() 
        self.tblStatistics.applySettings()    
    
    def load_tblStatistics(self):
        def pais(cur, columna, bolsa):
            """Si pais es Null es para todos"""
            total=0
            cur.execute("select count(*) from products where type=1 and obsolete=false and stockmarkets_id=%s", (bolsa.id,))
            tmp=cur.fetchone()[0]
            total=total+tmp
            self.tblStatistics.setItem(0, columna , qcenter(tmp))
            cur.execute("select count(*) from products where type=2 and obsolete=false and stockmarkets_id=%s", (bolsa.id,))
            tmp=cur.fetchone()[0]
            total=total+tmp
            self.tblStatistics.setItem(1, columna , qcenter(tmp))
            cur.execute("select count(*) from products where type=3 and obsolete=false and stockmarkets_id=%s", (bolsa.id,))
            tmp=cur.fetchone()[0]
            total=total+tmp
            self.tblStatistics.setItem(2, columna , qcenter(tmp))
            cur.execute("select count(*) from products where type=4 and obsolete=false and stockmarkets_id=%s", (bolsa.id,))
            tmp=cur.fetchone()[0]
            total=total+tmp
            self.tblStatistics.setItem(3, columna , qcenter(tmp))
            cur.execute("select count(*) from products where type=5 and obsolete=false and stockmarkets_id=%s", (bolsa.id,))
            tmp=cur.fetchone()[0]
            total=total+tmp
            self.tblStatistics.setItem(4, columna , qcenter(tmp))
            cur.execute("select count(*) from products where type=7 and obsolete=false and stockmarkets_id=%s", (bolsa.id,))
            tmp=cur.fetchone()[0]
            total=total+tmp
            self.tblStatistics.setItem(5, columna , qcenter(tmp))
            cur.execute("select count(*) from products where type=9 and obsolete=false and stockmarkets_id=%s", (bolsa.id,))
            tmp=cur.fetchone()[0]
            total=total+tmp
            self.tblStatistics.setItem(6, columna , qcenter(tmp))
            self.tblStatistics.setItem(7, columna , QTableWidgetItem(""))
            cur.execute("select count(*) from products where obsolete=true and stockmarkets_id=%s", (bolsa.id,))
            tmp=cur.fetchone()[0]
            self.tblStatistics.setItem(8, columna , qcenter(tmp))
            self.tblStatistics.setItem(9, columna , QTableWidgetItem(""))
            self.tblStatistics.setItem(10, columna , qcenter(total))
            self.tblStatistics.horizontalHeaderItem (columna).setIcon(bolsa.country.qicon())
            self.tblStatistics.horizontalHeaderItem (columna).setToolTip((bolsa.country.name))
                
        def todos(cur):
            """Si pais es Null es para todos"""
            total=0
            cur.execute("select count(*) from products where type=1 and obsolete=false")
            tmp=cur.fetchone()[0]
            total=total+tmp
            self.tblStatistics.setItem(0, 0 , qcenter(tmp))
            cur.execute("select count(*) from products where type=2  and obsolete=false")
            tmp=cur.fetchone()[0]
            total=total+tmp
            self.tblStatistics.setItem(1, 0 , qcenter(tmp))
            cur.execute("select count(*) from products where type=3  and obsolete=false")
            tmp=cur.fetchone()[0]
            total=total+tmp
            self.tblStatistics.setItem(2, 0 , qcenter(tmp))
            cur.execute("select count(*) from products where type=4  and obsolete=false")
            tmp=cur.fetchone()[0]
            total=total+tmp
            self.tblStatistics.setItem(3, 0 , qcenter(tmp))
            cur.execute("select count(*) from products where type=5  and obsolete=false")
            tmp=cur.fetchone()[0]
            total=total+tmp
            self.tblStatistics.setItem(4, 0 , qcenter(tmp))
            cur.execute("select count(*) from products where type=7  and obsolete=false")
            tmp=cur.fetchone()[0]
            total=total+tmp
            self.tblStatistics.setItem(5, 0 , qcenter(tmp))
            cur.execute("select count(*) from products where type=9  and obsolete=false")
            tmp=cur.fetchone()[0]
            total=total+tmp
            self.tblStatistics.setItem(6, 0 , qcenter(tmp))
            self.tblStatistics.setItem(7, 0 , QTableWidgetItem(""))
            cur.execute("select count(*) from products where obsolete=true ")
            tmp=cur.fetchone()[0]
            self.tblStatistics.setItem(8, 0 , qcenter(tmp))
            self.tblStatistics.setItem(9, 0 , QTableWidgetItem(""))
            self.tblStatistics.setItem(10, 0 , qcenter(total))

    
        cur = self.mem.con.cursor()
        todos(cur)
        pais(cur, 1, self.mem.stockmarkets.find_by_id(1))
        pais(cur, 2, self.mem.stockmarkets.find_by_id(2))
        pais(cur, 3, self.mem.stockmarkets.find_by_id(3))
        pais(cur, 4, self.mem.stockmarkets.find_by_id(4))
        pais(cur, 5, self.mem.stockmarkets.find_by_id(5))
        pais(cur, 6,self.mem.stockmarkets.find_by_id(6))
        pais(cur, 7, self.mem.stockmarkets.find_by_id(7))
        pais(cur, 8, self.mem.stockmarkets.find_by_id(8))
        pais(cur, 9, self.mem.stockmarkets.find_by_id(9))
        pais(cur, 10, self.mem.stockmarkets.find_by_id(10))
        pais(cur, 11, self.mem.stockmarkets.find_by_id(11))
        pais(cur, 12, self.mem.stockmarkets.find_by_id(12))
        pais(cur, 13, self.mem.stockmarkets.find_by_id(13))
        pais(cur, 14, self.mem.stockmarkets.find_by_id(14))
        pais(cur, 15, self.mem.stockmarkets.find_by_id(15))
        cur.close()
