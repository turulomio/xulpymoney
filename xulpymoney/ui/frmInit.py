import pkg_resources
from PyQt5.QtCore import QTranslator,  pyqtSlot, QLocale
from PyQt5.QtWidgets import QDialog, QMessageBox, QApplication
from xulpymoney.ui.Ui_frmInit import Ui_frmInit
from xulpymoney.libxulpymoney import MemXulpymoney
from xulpymoney.admin_pg import AdminPG
from xulpymoney.libxulpymoneyfunctions import qmessagebox
from xulpymoney.libxulpymoneytypes import eOperationType

class frmInit(QDialog, Ui_frmInit):
    def __init__(self, parent = None, name = None, modal = False):
        QDialog.__init__(self,  parent)
        locale=QLocale()
        id=locale.system().name()
        if len(id)!=2:
            id=id[:-len(id)+2]
        print("Locale {} detected".format(id))
        self.setupUi(self)
        self.mem=MemXulpymoney()      
        self.mem.setQTranslator(QTranslator(QApplication.instance()))  
        self.mem.languages.qcombobox(self.cmbLanguage, self.mem.languages.find_by_id(id))
    
    @pyqtSlot(str)      
    def on_cmbLanguage_currentIndexChanged(self, stri):
        self.mem.language=self.mem.languages.find_by_id(self.cmbLanguage.itemData(self.cmbLanguage.currentIndex()))
        self.mem.languages.cambiar(self.mem.language.id)
        self.retranslateUi(self)
    
    @pyqtSlot()
    def on_cmdCreate_released(self):
        respuesta = QMessageBox.warning(self, self.windowTitle(), self.tr("Do you want to create {} database in {}?".format(self.txtXulpymoney.text(), self.cmbLanguage.currentText())), QMessageBox.Ok | QMessageBox.Cancel)
        if respuesta==QMessageBox.Ok:             
            self.cmbLanguage.setEnabled(False)
            self.txtPass.setEnabled(False)
            self.txtPort.setEnabled(False)
            self.txtServer.setEnabled(False)
            self.txtUser.setEnabled(False)
            self.txtXulpymoney.setEnabled(False)
   
            self.admin=AdminPG(self.txtUser.text(), self.txtPass.text(),  self.txtServer.text(),  self.txtPort.text())
                        
            if self.admin.con.is_active()==False:
                qmessagebox(self.tr("Error conecting to table template1 in database server"))
                self.reject()
                return            

            if self.admin.create_db(self.txtXulpymoney.text())==False:
                qmessagebox(self.tr("Error creating database. You need to be superuser or maybe it already exist"))
                self.reject()
                return
            
            #Una vez creada la base de datos me conecto
            self.newdbcon=self.admin.connect_to_database(self.txtXulpymoney.text())
            
            if self.xulpymoney_basic_schema()==False:
                qmessagebox(self.tr("Error processing SQL init scripts"))
                self.reject()
                return
            self.newdbcon.commit()
            self.cmdCreate.setEnabled(False)

            qmessagebox(self.tr("Database created. User xulpymoney_user and xulpymoney_admin have been created. Please run Xulpymoney and login"))        
            print ("App correctly closed")
            self.close()
        else:
            self.cmbLanguage.setEnabled(True)
            self.txtPass.setEnabled(True)
            self.txtPort.setEnabled(True)
            self.txtServer.setEnabled(True)
            self.txtUser.setEnabled(True)
            self.txtXulpymoney.setEnabled(True)

    ## In xulpymoney.sql there aren't concepts so we must add them after running it
    def xulpymoney_basic_schema(self):
            filename=pkg_resources.resource_filename("xulpymoney","sql/xulpymoney.sql")
            self.newdbcon.load_script(filename)
            
            cur= self.newdbcon.cursor()
            cur.execute("insert into public.entidadesbancarias values(3,'{0}', true)".format(QApplication.translate("Core","Personal Management")))
            cur.execute("insert into public.cuentas values(4,'{0}',3,true,NULL,'EUR')".format(QApplication.translate("Core","Cash")))
            cur.execute("insert into public.conceptos values(1,'{0}',2,false)".format(QApplication.translate("Core","Initiating bank account")))
            cur.execute("insert into public.conceptos values(2,'{0}',2,true)".format(QApplication.translate("Core","Paysheet")))
            cur.execute("insert into public.conceptos values(3,'{0}',1,true)".format(QApplication.translate("Core","Supermarket")))
            cur.execute("insert into public.conceptos values(4,'{0}',3,false)".format(QApplication.translate("Core","Transfer. Origin")))
            cur.execute("insert into public.conceptos values(5,'{0}',3,false)".format(QApplication.translate("Core","Transfer. Destination")))
            cur.execute("insert into public.conceptos values(6,'{0}',2,false)".format(QApplication.translate("Core","Taxes. Returned")))
            cur.execute("insert into public.conceptos values(7,'{0}',1,true)".format(QApplication.translate("Core","Gas")))
            cur.execute("insert into public.conceptos values(8,'{0}',1,true)".format(QApplication.translate("Core","Restaurant")))  
            cur.execute("insert into public.conceptos values(29,'{0}',4,false)".format(QApplication.translate("Core","Purchase investment product")))
            cur.execute("insert into public.conceptos values(35,'{0}',5,false)".format(QApplication.translate("Core","Sale investment product")))
            cur.execute("insert into public.conceptos values(37,'{0}',1,false)".format(QApplication.translate("Core","Taxes. Paid")))
            cur.execute("insert into public.conceptos values(38,'{0}',1,false)".format(QApplication.translate("Core","Bank commissions")))
            cur.execute("insert into public.conceptos values(39,'{0}',2,false)".format(QApplication.translate("Core","Dividends")))
            cur.execute("insert into public.conceptos values(40,'{0}',7,false)".format(QApplication.translate("Core","Credit card billing")))
            cur.execute("insert into public.conceptos values(43,'{0}',6,false)".format(QApplication.translate("Core","Added shares")))
            cur.execute("insert into public.conceptos values(50,'{0}',2,false)".format(QApplication.translate("Core","Attendance bonus")))
            cur.execute("insert into public.conceptos values(59,'{0}',1,false)".format(QApplication.translate("Core","Custody commission")))
            cur.execute("insert into public.conceptos values(62,'{0}',2,false)".format(QApplication.translate("Core","Dividends. Sale of rights")))
            cur.execute("insert into public.conceptos values(63,'{0}',1,false)".format(QApplication.translate("Core","Bonds. Running coupon payment")))
            cur.execute("insert into public.conceptos values(65,'{0}',2,false)".format(QApplication.translate("Core","Bonds. Running coupon collection")))
            cur.execute("insert into public.conceptos values(66,'{0}',2,false)".format(QApplication.translate("Core","Bonds. Coupon collection")))
            cur.execute("insert into public.conceptos values(67,'{0}',2,false)".format(QApplication.translate("Core","Credit card refund")))          
            cur.execute("insert into public.conceptos values(68,%s,%s,false)",("HL adjustment income", eOperationType.Income))    
            cur.execute("insert into public.conceptos values(69,%s,%s,false)",("HL adjustment expense", eOperationType.Expense))  
            cur.execute("insert into public.conceptos values(70,%s,%s,false)",("HL Guarantee payment", eOperationType.Expense))  
            cur.execute("insert into public.conceptos values(71,%s,%s,false)",("HL Guarantee return", eOperationType.Income))     
            cur.execute("insert into public.conceptos values(72,%s,%s,false)",("HL Operation commission", eOperationType.Expense))     
            cur.execute("insert into public.conceptos values(73,%s,%s,false)",("HL Paid interest", eOperationType.Expense))     
            cur.execute("insert into public.conceptos values(74,%s,%s,false)",("HL Received interest", eOperationType.Income))   
            cur.close()
#            return True
#        except:
#            print ("Error creating xulpymoney basic schema")
#            return False

