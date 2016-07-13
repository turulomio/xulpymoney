from PyQt5.QtCore import *
from PyQt5.QtGui import *
from Ui_frmInit import *
from libsources import *
from libxulpymoney import *

class frmInit(QDialog, Ui_frmInit):
    def __init__(self, parent = None, name = None, modal = False):
        QDialog.__init__(self,  parent)
        self.setupUi(self)
        self.mem=MemXulpymoney()
        
        locale=QLocale()
        a=locale.system().name()
        if len(a)!=2:
            a=a[:-len(a)+2]
            
        print (a)
        self.mem.languages.qcombobox(self.cmbLanguage, self.mem.languages.find_by_id(a))
    
    @pyqtSlot()
    def on_cmdCreate_released(self):
        respuesta = QMessageBox.warning(self, self.windowTitle(), self.tr("Do you want to create {} databases in {0}?".format(self.txtXulpymoney.text(), self.cmbLanguage.currentText())), QMessageBox.Ok | QMessageBox.Cancel)
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
            
            if admin.create_db(self.txtXulpymoney.text())==False:
                qmessagebox(self.tr("Error creating database. Maybe it already exist"))
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
        else:
            self.cmbLanguage.setEnabled(True)
            self.txtPass.setEnabled(True)
            self.txtPort.setEnabled(True)
            self.txtServer.setEnabled(True)
            self.txtUser.setEnabled(True)
            self.txtXulpymoney.setEnabled(True)
