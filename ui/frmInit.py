from PyQt4.QtCore import *
from PyQt4.QtGui import *
import psycopg2,  psycopg2.extras
from Ui_frmInit import *
from source_yahoohistorical import WorkerYahooHistorical
from libxulpymoney import *

class frmInit(QDialog, Ui_frmInit):
    def __init__(self, parent = None, name = None, modal = False):
        QDialog.__init__(self,  parent)
        self.setupUi(self)
        self.mem=MemMyStock()


    
    @pyqtSignature("")
    def on_cmdYN_accepted(self):
        respuesta = QMessageBox.warning(self, self.windowTitle(), self.tr("Do you want to create needed Xulpymoney databases in {0}?".format(self.cmbLanguage.currentText())), QMessageBox.Ok | QMessageBox.Cancel)
        if respuesta==QMessageBox.Ok:             
            if self.create_db(self.txtMyStocks.text())==False or self.create_db(self.txtXulpymoney.text())==False or self.create_mystocks()==False or self.create_xulpymoney()==False:
                m=QMessageBox()
                m.setText(self.tr("Error creating databases. Maybe they already exists"))
                m.exec_()        
                self.reject()
                return

            m=QMessageBox()
            m.setText(self.tr("Database created. Xulpymoney is going to insert quotes from yahoo. This is a long process, please wait."))
            m.exec_()         
            
            #Insert quotes of yahoo
            strtemplate1="dbname='%s' port='%s' user='%s' host='%s' password='%s'" % (self.txtMyStocks.text(), self.txtPort.text(), self.txtUser.text(),  self.txtServer.text(), self.txtPass.text())
            self.mem.con=psycopg2.extras.DictConnection(strtemplate1)
            self.mem.actualizar_memoria()            
            w=WorkerYahooHistorical(self.mem)
            w.start()           
            
            m=QMessageBox()
            m.setText(self.tr("Process finished. Now you can use MyStocks and Xulpymoney"))
            m.exec_()         
            self.accept()



    @pyqtSignature("")
    def create_db(self, database):
        strtemplate1="dbname='template1' port='%s' user='%s' host='%s' password='%s'" % (self.txtPort.text(), self.txtUser.text(),  self.txtServer.text(), self.txtPass.text())
        cont=psycopg2.extras.DictConnection(strtemplate1)
        cont.set_isolation_level(0)                                    
        try:
            cur=cont.cursor()
            cur.execute("create database {0};".format(database))
            cur.close()
            cont.close()
        except:
            cur.close()
            cont.close()
            return False
        return True
        

    def load_script(self, database, file):
        strtemplate1="dbname='%s' port='%s' user='%s' host='%s' password='%s'" % (database, self.txtPort.text(), self.txtUser.text(),  self.txtServer.text(), self.txtPass.text())
        con=psycopg2.extras.DictConnection(strtemplate1)
        con.set_isolation_level(0)
        cur= con.cursor()
        procedures  = open(file,'r').read() 
        cur.execute(procedures)
        
        con.commit()
        cur.close()
        con.close()

    @pyqtSignature("")
    def create_mystocks(self):
        self.load_script(self.txtMyStocks.text(), "/usr/share/xulpymoney/sql/mystocks.sql")
        self.load_script(self.txtMyStocks.text(), "/usr/share/xulpymoney/sql/mystocks.data")
        
    @pyqtSignature("")
    def create_xulpymoney(self):
        self.load_script(self.txtXulpymoney.text(), "/usr/share/xulpymoney/sql/xulpymoney.sql")
        
        strtemplate1="dbname='%s' port='%s' user='%s' host='%s' password='%s'" % (self.txtXulpymoney.text(), self.txtPort.text(), self.txtUser.text(),  self.txtServer.text(), self.txtPass.text())
        con=psycopg2.extras.DictConnection(strtemplate1)
        con.set_isolation_level(0)
        cur= con.cursor()
        cur.execute("insert into entidadesbancarias values(3,'{0}', true)".format(self.tr("Personal Management")))
        cur.execute("insert into cuentas values(4,'{0}',3,true,NULL,'EUR')".format(self.tr("Cash")))
        cur.execute("insert into conceptos values(1,'{0}',2,false)".format(self.tr("Initiating bank account")))
        cur.execute("insert into conceptos values(4,'{0}',3,false)".format(self.tr("Transfer. Origin")))
        cur.execute("insert into conceptos values(5,'{0}',3,false)".format(self.tr("Transfer. Destination")))
        cur.execute("insert into conceptos values(29,'{0}',4,false)".format(self.tr("Purchase investment product")))
        cur.execute("insert into conceptos values(35,'{0}',5,false)".format(self.tr("Sale investment product")))
        cur.execute("insert into conceptos values(38,'{0}',1,false)".format(self.tr("Bank commissions")))
        cur.execute("insert into conceptos values(39,'{0}',2,false)".format(self.tr("Dividends")))
        cur.execute("insert into conceptos values(40,'{0}',7,false)".format(self.tr("Credit card billing")))
        cur.execute("insert into conceptos values(43,'{0}',6,false)".format(self.tr("Added shares")))
        cur.execute("insert into conceptos values(50,'{0}',2,false)".format(self.tr("Attendance bonus")))
        cur.execute("insert into conceptos values(59,'{0}',1,false)".format(self.tr("Custody commission")))
        cur.execute("insert into conceptos values(62,'{0}',2,false)".format(self.tr("Dividends. Sale of rights")))
        cur.execute("insert into conceptos values(63,'{0}',1,false)".format(self.tr("Bonds. Running coupon payment")))
        cur.execute("insert into conceptos values(65,'{0}',2,false)".format(self.tr("Bonds. Running coupon collection")))
        cur.execute("insert into conceptos values(66,'{0}',2,false)".format(self.tr("Bonds. Coupon collection")))
        cur.execute("insert into conceptos values(2,'{0}',2,true)".format(self.tr("Paysheet")))
        cur.execute("insert into conceptos values(3,'{0}',1,true)".format(self.tr("Supermarket")))
        cur.execute("insert into conceptos values(6,'{0}',1,true)".format(self.tr("Restaurant")))
        cur.execute("insert into conceptos values(7,'{0}',1,true)".format(self.tr("Gas")))
        con.commit()
        cur.close()
        con.close()
