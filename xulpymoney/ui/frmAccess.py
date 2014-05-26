from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Ui_frmAccess import *

class frmAccess(QDialog, Ui_frmAccess):
    def __init__(self, mem, app, parent = None, name = None, modal = False):
        QDialog.__init__(self,  parent)
        self.mem=mem
        self.setModal(True)
        self.setupUi(self)
        self.app=app
        self.mem.languages.qcombobox(self.cmbLanguages,self.mem.config.get_value("settings", "language"))
        
        if self.app==1:
            icon = QtGui.QIcon()
            pix=QtGui.QPixmap(":xulpymoney/kmplot.jpg")
            icon.addPixmap(pix, QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.setWindowIcon(icon)     
            self.setWindowTitle(self.trUtf8("MyStocks - Access"))
            self.txtDB.setText(self.mem.config.get_value("frmAccessMS", "db" ))
            self.txtPort.setText(self.mem.config.get_value("frmAccessMS", "port" ))
            self.txtUser.setText(self.mem.config.get_value("frmAccessMS", "user" ))
            self.txtServer.setText(self.mem.config.get_value("frmAccessMS", "server" ))
        elif self.app==2:
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
            if self.app==1:
                self.mem.config.set_value("frmAccessMS", "db", self.txtDB.text() )
                self.mem.config.set_value("frmAccessMS", "port",  self.txtPort.text())
                self.mem.config.set_value("frmAccessMS", "user" ,  self.txtUser.text())
                self.mem.config.set_value("frmAccessMS", "server", self.txtServer.text())      
                self.mem.config.save()    
                self.mem.conms=self.mem.connect_mystocks()      
            elif self.app==2:
                self.mem.config.set_value("frmAccess", "db", self.txtDB.text() )
                self.mem.config.set_value("frmAccess", "port",  self.txtPort.text())
                self.mem.config.set_value("frmAccess", "user" ,  self.txtUser.text())
                self.mem.config.set_value("frmAccess", "server", self.txtServer.text())     
                self.mem.config.save()    
                self.mem.con=self.mem.connect_xulpymoney()   
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

