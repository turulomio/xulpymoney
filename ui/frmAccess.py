from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Ui_frmAccess import *

class frmAccess(QDialog, Ui_frmAccess):
    def __init__(self, mem, parent = None, name = None, modal = False):
        QDialog.__init__(self,  parent)
        self.mem=mem
        self.setModal(True)
        self.setupUi(self)
        self.parent=parent
        self.mem.languages.qcombobox(self.cmbLanguages,self.mem.config.get_value("settings", "language"))

        icon = QtGui.QIcon()
        pix=QtGui.QPixmap(":xulpymoney/coins.png")
        icon.addPixmap(pix, QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)        
        self.setWindowTitle(self.trUtf8("Xulpymoney - Access"))
        self.txtDB.setText(self.mem.config.get_value("frmAccess", "db" ))
        self.txtPort.setText(self.mem.config.get_value("frmAccess", "port" ))
        self.txtUser.setText(self.mem.config.get_value("frmAccess", "user" ))
        self.txtServer.setText(self.mem.config.get_value("frmAccess", "server" ))

    @pyqtSlot(str)      
    def on_cmbLanguages_currentIndexChanged(self, stri):
        self.mem.languages.cambiar(self.cmbLanguages.itemData(self.cmbLanguages.currentIndex()))
        self.retranslateUi(self)

    def make_connection(self):
        """Función que realiza la conexión devolviendo true o false con el éxito"""
        try:
            self.mem.config.set_value("frmAccess", "db", self.txtDB.text() )
            self.mem.config.set_value("frmAccess", "port",  self.txtPort.text())
            self.mem.config.set_value("frmAccess", "user" ,  self.txtUser.text())
            self.mem.config.set_value("frmAccess", "server", self.txtServer.text())     
            self.mem.con=self.mem.connect_xulpymoney()           
            self.mem.config.set_value("settings", "language", self.cmbLanguages.itemData(self.cmbLanguages.currentIndex()))
            self.mem.config.save()                
            return True
        except:
            return False
    
    @QtCore.pyqtSlot() 
    def on_cmdYN_accepted(self):
        if self.make_connection()==False:
            self.reject()
            return
        self.accept()

    @QtCore.pyqtSlot() 
    def on_cmdYN_rejected(self):
        self.reject()

