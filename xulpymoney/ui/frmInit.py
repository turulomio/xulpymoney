from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QDialog
from xulpymoney.ui.Ui_frmInit import *
from xulpymoney.libxulpymoney import *

class frmInit(QDialog, Ui_frmInit):
    def __init__(self, parent = None, name = None, modal = False):
        QDialog.__init__(self,  parent)
        locale=QLocale()
        id=locale.system().name()
        if len(id)!=2:
            id=id[:-len(id)+2]
        print("Locale {} detected".format(id))
        self.setupUi(self)
        self.mem=MemXulpymoney()      
        self.mem.setQTranslator(QTranslator(QApplication.instance()))  
        self.mem.languages.qcombobox(self.cmbLanguage, self.mem.languages.find_by_id(id))
    
    @pyqtSlot(str)      
    def on_cmbLanguage_currentIndexChanged(self, stri):
        self.mem.language=self.mem.languages.find_by_id(self.cmbLanguage.itemData(self.cmbLanguage.currentIndex()))
        self.mem.languages.cambiar(self.mem.language.id)
        self.retranslateUi(self)
    
    @pyqtSlot()
    def on_cmdCreate_released(self):
        respuesta = QMessageBox.warning(self, self.windowTitle(), self.tr("Do you want to create {} database in {}?".format(self.txtXulpymoney.text(), self.cmbLanguage.currentText())), QMessageBox.Ok | QMessageBox.Cancel)
        if respuesta==QMessageBox.Ok:             
            self.cmbLanguage.setEnabled(False)
            self.txtPass.setEnabled(False)
            self.txtPort.setEnabled(False)
            self.txtServer.setEnabled(False)
            self.txtUser.setEnabled(False)
            self.txtXulpymoney.setEnabled(False)
            
            con=Connection()
            con.user=self.txtUser.text()
            con.db=self.txtXulpymoney.text()
            con.server=self.txtServer.text()
            con.port=self.txtPort.text()
            con.password=self.txtPass.text()
            self.mem.con=con            
            admin=DBAdmin(self.mem.con)
            
            print("Aq1uin")
            
            if admin.check_connection()==False:
                qmessagebox(self.tr("Error conecting to table template1 in database server"))
                self.reject()
                return            

            if admin.create_db(self.txtXulpymoney.text())==False:
                qmessagebox(self.tr("Error creating database. You need to be superuser or maybe it already exist"))
                self.reject()
                return
            
            #Una vez creada la base de datos me conecto
            self.mem.con.connect()
            
            if admin.xulpymoney_basic_schema()==False:
                qmessagebox(self.tr("Error processing SQL init scripts"))
                self.reject()
                return
            self.mem.con.commit()
            self.cmdCreate.setEnabled(False)

            qmessagebox(self.tr("Database created. User xulpymoney_user and xulpymoney_admin have been created. Please run Xulpymoney and login"))        
            print ("App correctly closed")
            self.close()
        else:
            self.cmbLanguage.setEnabled(True)
            self.txtPass.setEnabled(True)
            self.txtPort.setEnabled(True)
            self.txtServer.setEnabled(True)
            self.txtUser.setEnabled(True)
            self.txtXulpymoney.setEnabled(True)
