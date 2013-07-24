from PyQt4.QtCore import *
from PyQt4.QtGui import *

import sys, psycopg2,  psycopg2.extras,  configparser
from Ui_frmAccess import *

class frmAccess(QDialog, Ui_frmAccess):
    def __init__(self, cfg, configfile, parent = None, name = None, modal = False):
        QDialog.__init__(self,  parent)
        self.cfg=cfg
        self.configfile=configfile
        if name:
            self.setObjectName(name)
        self.setModal(True)
        self.setupUi(self)
        self.configfile_load(configfile)


    
    def configfile_load( self,  file):
        config = configparser.ConfigParser()
        config.read(file)
        try:
                self.txtDB.setText(config.get("frmAccess", "db" ))
                self.txtPort.setText(config.get("frmAccess", "port" ))
                self.txtUser.setText(config.get("frmAccess", "user" ))
                self.txtServer.setText(config.get("frmAccess", "server" ))
        except:
            print (self.trUtf8("Error al leer del fichero de configuración o no hay error")    )

    
    
    def configfile_save(self, file):
        config = configparser.ConfigParser()
        config.read(file)
        if config.has_section("frmAccess")==False:
            config.add_section("frmAccess")
        config.set("frmAccess", "db", self.txtDB.text() )
        config.set("frmAccess", "port",  self.txtPort.text())
        config.set("frmAccess", "user" ,  self.txtUser.text())
        config.set("frmAccess", "server", self.txtServer.text())
        with open(file, 'w') as configfile:
            config.write(configfile)


    def check_connection(self):
        strmq="dbname='{0}' port='{1}' user='{2}' host='{3}' password='{4}'".format(self.txtDB.text(),  self.txtPort.text(), self.txtUser.text(), self.txtServer.text(),  self.txtPass.text())
        try:
            con=psycopg2.extras.DictConnection(strmq)
            con.close()
            return True
        except psycopg2.Error:
            return False

    
    @pyqtSignature("")
    def on_cmdYN_accepted(self):
        
        self.cfg.db=(self.txtDB.text())
        self.cfg.port=(self.txtPort.text())
        self.cfg.user=(self.txtUser.text()) 
        self.cfg.password=(self.txtPass.text()) 
        self.cfg.server=(self.txtServer.text()) 
        if self.check_connection()==False:
            m=QMessageBox()
            m.setText(self.trUtf8("Error en la conexión, vuelva a entrar"))
            m.exec_()        
            sys.exit(255)
        self.configfile_save(self.configfile)
        self.done(0)

    @pyqtSignature("")
    def on_cmdYN_rejected(self):
        sys.exit(255)
