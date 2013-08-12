from PyQt4.QtCore import *
from PyQt4.QtGui import *
import psycopg2,  psycopg2.extras
from Ui_frmInit import *

class frmInit(QDialog, Ui_frmInit):
    def __init__(self, parent = None, name = None, modal = False):
        QDialog.__init__(self,  parent)
        self.setupUi(self)


    
    @pyqtSignature("")
    def on_cmdYN_accepted(self):
        respuesta = QMessageBox.warning(self, self.windowTitle(), self.trUtf8("Do you want to create Xulpymoney needed databases in {0}?".format(self.cmbLanguage.currentText())), QMessageBox.Ok | QMessageBox.Cancel)
        if respuesta==QMessageBox.Ok:             
            if self.create_db(self.txtMyStocks.text())==False or self.create_db(self.txtXulpymoney.text())==False or self.create_mystocks()==False or self.create_xulpymoney()==False:
                m=QMessageBox()
                m.setText(self.trUtf8("Error creating databases"))
                m.exec_()        
                self.reject()
                return

            
            m=QMessageBox()
            m.setText(self.trUtf8("Database created, please login again"))
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
        self.load_script(self.txtMyStocks.text(), "/usr/share/xulpymoney/sql/myquotes.sql")
        self.load_script(self.txtMyStocks.text(), "/usr/share/xulpymoney/sql/myquotes.data")
        
    @pyqtSignature("")
    def create_xulpymoney(self):
        self.load_script(self.txtXulpymoney.text(), "/usr/share/xulpymoney/sql/xulpymoney.sql")
        
        strtemplate1="dbname='%s' port='%s' user='%s' host='%s' password='%s'" % (self.txtXulpymoney.text(), self.txtPort.text(), self.txtUser.text(),  self.txtServer.text(), self.txtPass.text())
        con=psycopg2.extras.DictConnection(strtemplate1)
        con.set_isolation_level(0)
        cur= con.cursor()
        cur.execute("insert into entidadesbancarias values(3,{0}, true)".format(self.trUtf8("Personal Management")))
        cur.execute("insert into cuentas values(4,{0},3,true,NULL,'EUR')".format(self.trUtf8("Cash")))
        cur.execute("insert into conceptos values(39,{0},2,false)".format("Dividends"))
        con.commit()
        cur.close()
        con.close()
