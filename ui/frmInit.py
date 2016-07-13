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
        source=WorkerYahooHistorical(self.mem, 0 )
        self.wyahoohistorical=wdgSource(self) 
        source.setWdgSource(self.wyahoohistorical) #Links source with wdg
        self.wyahoohistorical.setSource(self.mem, source)
        self.laySource.addWidget(self.wyahoohistorical)
        self.wyahoohistorical.setEnabled(False)
        self.wyahoohistorical.chkUserOnly.setCheckState(Qt.Unchecked)
        self.wyahoohistorical.chkUserOnly.hide()
        self.wyahoohistorical.setWidgetToUpdate(self)


    
    @pyqtSlot()
    def on_cmdCreate_released(self):
        respuesta = QMessageBox.warning(self, self.windowTitle(), self.tr("Do you want to create needed Xulpymoney databases in {0}?".format(self.cmbLanguage.currentText())), QMessageBox.Ok | QMessageBox.Cancel)
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
                m=QMessageBox()
                m.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
                m.setText(self.tr("Error creating database. Maybe it already exist"))
                m.exec_()        
                self.reject()
                return
            
            #Una vez creada la base de datos me conecto
            self.mem.con.connect()
            
            if admin.xulpymoney_basic_schema()==False:
                m=QMessageBox()
                m.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
                m.setText(self.tr("Error creating database. Maybe it already exist"))
                m.exec_()        
                self.reject()
                return
            self.mem.con.commit()
            self.cmdCreate.setEnabled(False)

            respuesta2 = QMessageBox.warning(self, self.windowTitle(), self.tr("Database created. Xulpymoney needs to insert quotes from yahoo. This is a long process. Do you want to insert them now?"), QMessageBox.Ok | QMessageBox.Cancel)
            if respuesta2==QMessageBox.Ok:             
                self.mem.load_db_data()     
                self.wyahoohistorical.setEnabled(True)
                self.wyahoohistorical.on_cmdRun_released()  
        else:
            self.cmbLanguage.setEnabled(True)
            self.txtPass.setEnabled(True)
            self.txtPort.setEnabled(True)
            self.txtServer.setEnabled(True)
            self.txtUser.setEnabled(True)
            self.txtXulpymoney.setEnabled(True)
            

    def on_cmdExit_released(self):
        self.close()
