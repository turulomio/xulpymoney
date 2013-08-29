from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Ui_frmAccess import *

class frmAccess(QDialog, Ui_frmAccess):
    def __init__(self, cfg, app, parent = None, name = None, modal = False):
        QDialog.__init__(self,  parent)
        self.cfg=cfg
        if name:
            self.setObjectName(name)
        self.setModal(True)
        self.setupUi(self)
        self.app=app
        if self.app==1:
            icon = QtGui.QIcon()
            pix=QtGui.QPixmap(":xulpymoney/kmplot.jpg")
            icon.addPixmap(pix, QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.setWindowIcon(icon)        
            self.lbl.setPixmap(pix)
            self.setWindowTitle(self.trUtf8("MyStocks - Acceso"))
            self.txtDB.setText(self.cfg.config.get_value("frmAccessMS", "db" ))
            self.txtPort.setText(self.cfg.config.get_value("frmAccessMS", "port" ))
            self.txtUser.setText(self.cfg.config.get_value("frmAccessMS", "user" ))
            self.txtServer.setText(self.cfg.config.get_value("frmAccessMS", "server" ))
        elif self.app==2:
            icon = QtGui.QIcon()
            pix=QtGui.QPixmap(":xulpymoney/coins.png")
            icon.addPixmap(pix, QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.setWindowIcon(icon)        
            self.lbl.setPixmap(pix)
            self.setWindowTitle(self.trUtf8("Xulpymoney - Acceso"))
            self.txtDB.setText(self.cfg.config.get_value("frmAccess", "db" ))
            self.txtPort.setText(self.cfg.config.get_value("frmAccess", "port" ))
            self.txtUser.setText(self.cfg.config.get_value("frmAccess", "user" ))
            self.txtServer.setText(self.cfg.config.get_value("frmAccess", "server" ))



    def make_connection(self):
        """Función que realiza la conexión devolviendo true o false con el éxito"""
        try:
            if self.app==1:
                self.cfg.config.set_value("frmAccessMS", "db", self.txtDB.text() )
                self.cfg.config.set_value("frmAccessMS", "port",  self.txtPort.text())
                self.cfg.config.set_value("frmAccessMS", "user" ,  self.txtUser.text())
                self.cfg.config.set_value("frmAccessMS", "server", self.txtServer.text())      
                self.cfg.config.save()    
                self.cfg.conms=self.cfg.connect_myquotes()      
            elif self.app==2:
                self.cfg.config.set_value("frmAccess", "db", self.txtDB.text() )
                self.cfg.config.set_value("frmAccess", "port",  self.txtPort.text())
                self.cfg.config.set_value("frmAccess", "user" ,  self.txtUser.text())
                self.cfg.config.set_value("frmAccess", "server", self.txtServer.text())     
                self.cfg.config.save()    
                self.cfg.con=self.cfg.connect_xulpymoney()   
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

