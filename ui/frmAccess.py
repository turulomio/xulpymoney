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
            self.txtDB.setText(self.cfg.config.get("frmAccessMS", "db" ))
            self.txtPort.setText(self.cfg.config.get("frmAccessMS", "port" ))
            self.txtUser.setText(self.cfg.config.get("frmAccessMS", "user" ))
            self.txtServer.setText(self.cfg.config.get("frmAccessMS", "server" ))
        elif self.app==2:
            icon = QtGui.QIcon()
            pix=QtGui.QPixmap(":xulpymoney/coins.png")
            icon.addPixmap(pix, QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.setWindowIcon(icon)        
            self.lbl.setPixmap(pix)
            self.setWindowTitle(self.trUtf8("Xulpymoney - Acceso"))
            self.txtDB.setText(self.cfg.config.get("frmAccess", "db" ))
            self.txtPort.setText(self.cfg.config.get("frmAccess", "port" ))
            self.txtUser.setText(self.cfg.config.get("frmAccess", "user" ))
            self.txtServer.setText(self.cfg.config.get("frmAccess", "server" ))



    def make_connection(self):
        """Funci´on que realiza la conexi´on devolviendo true o false con el ´exito"""
        try:
            if self.app==1:
                self.cfg.config_set_value(self.cfg.config, "frmAccessMS", "db", self.txtDB.text() )
                self.cfg.config_set_value(self.cfg.config, "frmAccessMS", "port",  self.txtPort.text())
                self.cfg.config_set_value(self.cfg.config, "frmAccessMS", "user" ,  self.txtUser.text())
                self.cfg.config_set_value(self.cfg.config, "frmAccessMS", "server", self.txtServer.text())      
                self.cfg.configs_save()    
                self.cfg.conms=self.cfg.connect_myquotes()      
            elif self.app==2:
                self.cfg.config_set_value(self.cfg.config, "frmAccess", "db", self.txtDB.text() )
                self.cfg.config_set_value(self.cfg.config, "frmAccess", "port",  self.txtPort.text())
                self.cfg.config_set_value(self.cfg.config, "frmAccess", "user" ,  self.txtUser.text())
                self.cfg.config_set_value(self.cfg.config, "frmAccess", "server", self.txtServer.text())     
                self.cfg.configs_save()    
                self.cfg.con=self.cfg.connect_xulpymoney()   
            return True
        except:
            return False

    
    @pyqtSignature("")
    def on_cmdYN_accepted(self):
        if self.make_connection()==False:
            m=QMessageBox()
            m.setText(self.trUtf8("Error en la conexión, vuelva a entrar"))
            m.exec_()        
            self.reject()
        self.accept()


