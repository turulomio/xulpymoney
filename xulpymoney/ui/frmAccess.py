from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from Ui_frmAccess import *
from libxulpymoney import Connection

class frmAccess(QDialog, Ui_frmAccess):
    def __init__(self, mem, parent = None, name = None, modal = False):
        """Returns accepted if conection is done, or rejected if there's an error"""""
        QDialog.__init__(self,  parent)
        self.mem=mem
        self.setModal(True)
        self.setupUi(self)
        self.parent=parent
        self.mem.languages.qcombobox(self.cmbLanguages,self.mem.languages.find(self.mem.config.get_value("settings", "language")))
        self.setPixmap(QPixmap(":xulpymoney/coins.png"))
        self.setTitle(self.tr("Xulpymoney - Access"))
        self.con=Connection()#Pointer to connection


    def setPixmap(self, qpixmap):
        icon = QtGui.QIcon()
        icon.addPixmap(qpixmap, QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)        
        
    def setTitle(self, text):
        self.setWindowTitle(text)
        
    def setLabel(self, text):
        self.lbl.setText(text)
        
    def config_load(self):
        self.txtDB.setText(self.mem.config.get_value("frmAccess", "db" ))
        self.txtPort.setText(self.mem.config.get_value("frmAccess", "port" ))
        self.txtUser.setText(self.mem.config.get_value("frmAccess", "user" ))
        self.txtServer.setText(self.mem.config.get_value("frmAccess", "server" ))
        self.txtPass.setFocus()
        
    def config_save(self):
        self.mem.config.set_value("frmAccess", "db", self.txtDB.text() )
        self.mem.config.set_value("frmAccess", "port",  self.txtPort.text())
        self.mem.config.set_value("frmAccess", "user" ,  self.txtUser.text())
        self.mem.config.set_value("frmAccess", "server", self.txtServer.text())   
        self.mem.config.set_value("settings", "language", self.cmbLanguages.itemData(self.cmbLanguages.currentIndex()))
        self.mem.password=self.txtPass.text()
        self.mem.config.save()      

    @pyqtSlot(str)      
    def on_cmbLanguages_currentIndexChanged(self, stri):
        self.mem.languages.cambiar(self.cmbLanguages.itemData(self.cmbLanguages.currentIndex()))
        self.retranslateUi(self)

    def make_connection(self):
        """Función que realiza la conexión devolviendo true o false con el éxito"""
        try:
            self.con.init__create(self.txtUser.text(), self.txtPass.text(), self.txtServer.text(), self.txtPort.text(), self.txtDB.text())
            self.con.connect()
            return self.con.is_active()
        except:
            print ("Error in function make_connection",  self.mem.con)
            return False
    
    @QtCore.pyqtSlot() 
    def on_cmdYN_accepted(self):
        self.con.init__create(self.txtUser.text(), self.txtPass.text(), self.txtServer.text(), self.txtPort.text(), self.txtDB.text())
        self.con.connect()
        if self.con.is_active():
            self.accept()
        else:
            self.reject()

    @QtCore.pyqtSlot() 
    def on_cmdYN_rejected(self):
        self.reject()

    def qmessagebox_error_connecting(self):
        m=QMessageBox()
        m.setIcon(QMessageBox.Information)
        m.setText(self.tr("Error conecting to {} database in {} server").format(self.txtDB.text(), self.txtServer.text()))
        m.exec_()   
            
    def qmessagebox_error_not_superuser(self):
        m=QMessageBox()
        m.setIcon(QMessageBox.Information)
        m.setText(self.tr("The role of the user is not an administrator"))
        m.exec_()   
            

