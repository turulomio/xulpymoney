import logging
from PyQt5.QtCore import pyqtSlot, QLocale
from PyQt5.QtWidgets import QDialog, QMessageBox
from xulpymoney.ui.Ui_frmInit import Ui_frmInit
from xulpymoney.ui.myqwidgets import qmessagebox
from xulpymoney.xulpymoney_schema import XulpymoneyDatabase

class frmInit(QDialog, Ui_frmInit):
    def __init__(self, mem, parent = None, name = None, modal = False):
        QDialog.__init__(self,  parent)
        locale=QLocale()
        id=locale.system().name()
        if len(id)!=2:
            id=id[:-len(id)+2]
        print("Locale {} detected".format(id))
        self.setupUi(self)
        self.mem=mem
        self.mem.languages.qcombobox(self.cmbLanguage, self.mem.languages.find_by_id(id))
    
    @pyqtSlot(str)      
    def on_cmbLanguage_currentIndexChanged(self, stri):
        self.mem.language=self.mem.languages.find_by_id(self.cmbLanguage.itemData(self.cmbLanguage.currentIndex()))
        self.mem.languages.cambiar(self.mem.language.id, "xulpymoney")
        self.retranslateUi(self)
    
    @pyqtSlot()
    def on_cmdCreate_released(self):
        respuesta = QMessageBox.warning(self, self.windowTitle(), self.tr("Do you want to create {} database in {}?".format(self.txtXulpymoney.text(), self.cmbLanguage.currentText())), QMessageBox.Ok | QMessageBox.Cancel)
        if respuesta==QMessageBox.Ok:                
            self.newdb=XulpymoneyDatabase(self.txtUser.text(), self.txtPass.text(),  self.txtServer.text(),  self.txtPort.text(), self.txtXulpymoney.text())
            if self.newdb.create()==False:
                qmessagebox(self.newdb.error)
            else:
                qmessagebox(self.tr("Database created. User xulpymoney_user and xulpymoney_admin have been created. Please run Xulpymoney and login"))        
                self.mem.settings.sync()
                logging.info ("App correctly closed")
                self.close()

