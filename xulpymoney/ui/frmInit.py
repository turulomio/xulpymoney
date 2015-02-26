from PyQt5.QtCore import *
from PyQt5.QtGui import *
import psycopg2,  psycopg2.extras
from Ui_frmInit import *
from libsources import *
from libxulpymoney import *
from wdgSource import *

class frmInit(QDialog, Ui_frmInit):
    def __init__(self, parent = None, name = None, modal = False):
        QDialog.__init__(self,  parent)
        self.setupUi(self)
        self.mem=MemProducts()
        
        locale=QLocale()
        a=locale.system().name()
        if len(a)!=2:
            a=a[:-len(a)+2]
            
        print (a)
        self.mem.languages.qcombobox(self.cmbLanguage, self.mem.languages.find(a))
        self.wyahoohistorical=wdgSource(self.mem, Sources.WorkerYahooHistorical, self) 
        self.laySource.addWidget(self.wyahoohistorical)
        self.wyahoohistorical.setEnabled(False)
        self.wyahoohistorical.setWidgetToUpdate(self)


    
    @pyqtSlot()
    def on_cmdCreate_released(self):
        respuesta = QMessageBox.warning(self, self.windowTitle(), self.tr("Do you want to create needed Xulpymoney databases in {0}?".format(self.cmbLanguage.currentText())), QMessageBox.Ok | QMessageBox.Cancel)
        if respuesta==QMessageBox.Ok:             
            self.cmbLanguage.setEnabled(False)
            self.txtPass.setEnabled(False)
            self.txtPort.setEnabled(False)
            self.txtServer.setEnabled(False)
            self.txtUser.setEnabled(False)
            self.txtXulpymoney.setEnabled(False)
            if self.create_db(self.txtXulpymoney.text())==False  or self.create_xulpymoney()==False:
                m=QMessageBox()
                m.setText(self.tr("Error creating database. Maybe it already exist"))
                m.exec_()        
                self.reject()
                return


            respuesta2 = QMessageBox.warning(self, self.windowTitle(), self.tr("Database created. Xulpymoney needs to insert quotes from yahoo. This is a long process. Do you want to insert them now?"), QMessageBox.Ok | QMessageBox.Cancel)
            if respuesta2==QMessageBox.Ok:             
                #Insert quotes of yahoo
                strtemplate1="dbname='%s' port='%s' user='%s' host='%s' password='%s'" % (self.txtXulpymoney.text(), self.txtPort.text(), self.txtUser.text(),  self.txtServer.text(), self.txtPass.text())
                self.mem.con=psycopg2.extras.DictConnection(strtemplate1)
                self.mem.con.set_isolation_level(0)
                self.mem.actualizar_memoria()     
                self.cmdCreate.setEnabled(False)
                self.wyahoohistorical.setEnabled(True)
                self.wyahoohistorical.on_cmdRun_released()
#                
#                m=QMessageBox()
#                m.setText(self.tr("Process finished. Now you can use Xulpymoney"))
#                m.exec_()         
        else:
            self.cmbLanguage.setEnabled(True)
            self.txtPass.setEnabled(True)
            self.txtPort.setEnabled(True)
            self.txtServer.setEnabled(True)
            self.txtUser.setEnabled(True)
            self.txtXulpymoney.setEnabled(True)
            

    def on_cmdExit_released(self):
        self.close()


    @pyqtSlot()
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
            print ("Error in create_db()")
            cur.close()
            cont.close()
            return False
        return True
        
    def drop_db(self):
        strtemplate1="dbname='template1' port='%s' user='%s' host='%s' password='%s'" % (self.txtPort.text(), self.txtUser.text(),  self.txtServer.text(), self.txtPass.text())
        cont=psycopg2.extras.DictConnection(strtemplate1)
        cont.set_isolation_level(0)                                    
        try:
            cur=cont.cursor()
            cur.execute("drop database xulpymoney_pruebas;")
            cur.close()
            cont.close()
        except:
            print ("Error in drop_db()")
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

        
    @pyqtSlot()
    def create_xulpymoney(self):
        try:
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
            return True
        except:
            print ("Error in create_xulpymoney()")
            return False
