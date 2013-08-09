from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys, psycopg2,  psycopg2.extras
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



    def check_connection(self):
        strmq="dbname='{0}' port='{1}' user='{2}' host='{3}' password='{4}'".format(self.txtDB.text(),  self.txtPort.text(), self.txtUser.text(), self.txtServer.text(),  self.txtPass.text())
        print (strmq)
        try:
            con=psycopg2.extras.DictConnection(strmq)
            con.close()
            return True
        except psycopg2.Error:
            return False

    
    @pyqtSignature("")
    def on_cmdYN_accepted(self):
        if self.check_connection()==False:
            m=QMessageBox()
            m.setText(self.trUtf8("Error en la conexión, vuelva a entrar"))
            m.exec_()        
            sys.exit(255)

        if self.app==1:
            self.cfg.config_set_value(self.cfg.config, "frmAccessMS", "db", self.txtDB.text() )
            self.cfg.config_set_value(self.cfg.config, "frmAccessMS", "port",  self.txtPort.text())
            self.cfg.config_set_value(self.cfg.config, "frmAccessMS", "user" ,  self.txtUser.text())
            self.cfg.config_set_value(self.cfg.config, "frmAccessMS", "server", self.txtServer.text())    
        elif self.app==2:
            self.cfg.config_set_value(self.cfg.config, "frmAccess", "db", self.txtDB.text() )
            self.cfg.config_set_value(self.cfg.config, "frmAccess", "port",  self.txtPort.text())
            self.cfg.config_set_value(self.cfg.config, "frmAccess", "user" ,  self.txtUser.text())
            self.cfg.config_set_value(self.cfg.config, "frmAccess", "server", self.txtServer.text())            
        self.cfg.configs_save()
        self.done(0)

    @pyqtSignature("")
    def on_cmdYN_rejected(self):
        sys.exit(255)
