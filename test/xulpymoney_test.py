import unittest,  sys
sys.path.append("/usr/lib/xulpymoney")
from libxulpymoney import *
from frmMain import *
from frmInit import *

class TestXulpymoneyData(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.mem=mem
        self.frmMain=frmMain 
        
    def test_bank_add(self):
        #Banks IBM        
        self.frmMain.on_actionBanks_activated()
        self.frmMain.w.bank_add("Banco Santander malo")#It will be bank 4
        self.frmMain.w.tblEB.setCurrentCell(self.frmMain.w.banks.arr_position(4), 0)
        self.frmMain.w.bank_edit("Banco de Santander malo")
        self.frmMain.w.tblEB.setCurrentCell(self.frmMain.w.banks.arr_position(4), 0)
        self.assertEqual(self.frmMain.w.banks.length(), 2)       
        self.frmMain.w.on_actionBankDelete_activated()
        self.assertEqual(self.frmMain.w.banks.length(), 1)        
        self.frmMain.w.bank_add("Banco de Santander")#it will be bank5
        self.assertEqual(self.frmMain.w.banks.length(), 2)
        
        #Accounts IBM
        self.frmMain.on_actionAccounts_activated()
        ##Add
        w=frmAccountsReport(self.mem, None)
        w.cmbEB.setCurrentIndex(w.cmbEB.findData(5))
        w.txtAccount.setText("Cuenta Corriente Santander malo")
        w.cmbCurrency.setCurrentIndex(w.cmbCurrency.findData("EUR"))
        w.txtNumero.setText("01234567890123456789")
        w.on_cmdDatos_released()#it will be account 5
        self.frmMain.w.on_chkInactivas_stateChanged(self.frmMain.w.chkInactivas.checkState())
        self.frmMain.w.load_table()
        ##Edit
        self.frmMain.w.tblAccounts.setCurrentCell(self.frmMain.w.cuentas.arr_position(5), 0)
        w=frmAccountsReport(self.mem, self.frmMain.w.selAccount)
        w.txtAccount.setText("Cuenta Corriente Santander")
        w.on_cmdDatos_released()
        self.frmMain.w.on_chkInactivas_stateChanged(self.frmMain.w.chkInactivas.checkState())
        self.frmMain.w.load_table()
        ##Delete
        self.frmMain.w.tblAccounts.setCurrentCell(self.frmMain.w.cuentas.arr_position(5), 0)
        self.frmMain.w.on_actionAccountDelete_activated()
        ##Add other
        w=frmAccountsReport(self.mem, None)
        w.cmbEB.setCurrentIndex(w.cmbEB.findData(5))
        w.txtAccount.setText("Cuenta Corriente Santander")
        w.cmbCurrency.setCurrentIndex(w.cmbCurrency.findData("EUR"))
        w.txtNumero.setText("01234567890123456790")
        w.on_cmdDatos_released()#it will be account 5
        self.frmMain.w.on_chkInactivas_stateChanged(self.frmMain.w.chkInactivas.checkState())
        self.frmMain.w.load_table()
        
        
        

class TestXulpymoneyControlData(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.mem=mem
        self.frmMain=frmMain   
        
    def test_wdgProducts_search(self):
        self.frmMain.on_actionSearch_activated()
        self.frmMain.w.txt.setText("monetario")
        self.frmMain.w.on_cmd_pressed()
        self.assertEqual(17, self.frmMain.w.tblInvestments.rowCount())        

if __name__ == '__main__':
    #Create db pruebas
    app = QApplication(sys.argv)
    QTextCodec.setCodecForTr(QTextCodec.codecForName("UTF-8"));
    
    translator = QTranslator(app)
    locale=QLocale()
    a=locale.system().name()
    if len(a)!=2:
        a=a[:-len(a)+2]
    s= QApplication.translate("Core",  "Local language detected:{0}").format(a)
    print (s)
    translator.load("/usr/lib/xulpymoney/xulpymoney_" + a + ".qm")
    app.installTranslator(translator);
    
    frm = frmInit() 
    frm.txtXulpymoney.setText("xulpymoney_pruebas")
    frm.drop_db() 
    if frm.create_db(frm.txtXulpymoney.text()) and frm.create_xulpymoney():
        #Load data Xulpymoney infraestructure
        mem=MemXulpymoney()
        mem.setQTranslator(QTranslator(app))
        mem.qtranslator.load("/usr/lib/xulpymoney/xulpymoney_{0}.qm".format(mem.config.get_value("settings", "language")))
        app.installTranslator(mem.qtranslator)
        frmMain= frmMain(mem)
        strcon="dbname='xulpymoney_pruebas' port='5432' user='postgres' host='127.0.0.1' password='*'"
        mem.con=psycopg2.extras.DictConnection(strcon) 
        mem.actualizar_memoria()       
        
        #Launch tests
        unittest.main()
    else:
        print("No pude crear db")

 
