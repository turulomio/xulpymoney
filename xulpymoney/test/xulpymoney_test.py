import unittest
import sys
sys.path.append("/usr/lib/xulpymoney")
from PyQt5.QtWidgets import QDialog
from xulpymoney.libxulpymoney import *
from xulpymoney.ui.frmMain import *
from xulpymoney.ui.frmInit import *
from xulpymoney.ui.wdgProductSelector import *

class TestXulpymoneyData(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.mem=mem
        self.frmMain=frmMain 
        
    def test_data_minimal(self):
        #Check empyt actions
#        self.frmMain.on_actionAbout_triggered()
        self.frmMain.on_actionAccounts_triggered()
        self.frmMain.on_actionActive_triggered()
#        self.frmMain.on_actionAuxiliarTables_triggered()
        self.frmMain.on_actionBanks_triggered()
        self.frmMain.on_actionBondsAll_triggered()
        self.frmMain.on_actionBondsObsolete_triggered()
        self.frmMain.on_actionBondsPrivate_triggered()
        self.frmMain.on_actionBondsPublic_triggered()
        self.frmMain.on_actionCAC40_triggered()
        self.frmMain.on_actionCalculator_triggered()
        self.frmMain.on_actionConcepts_triggered()
        self.frmMain.on_actionCuriosities_triggered()
        self.frmMain.on_actionCurrenciesAll_triggered()
        self.frmMain.on_actionDividendsReport_triggered()
        
        
        
        
        #Banks IBM        
        self.frmMain.on_actionBanks_triggered()
        self.frmMain.w.bank_add("Banco Santander malo")#It will be bank 4
        self.frmMain.w.tblEB.setCurrentCell(self.frmMain.w.banks.arr_position(4), 0)
        self.frmMain.w.bank_edit("Banco de Santander malo")
        self.frmMain.w.tblEB.setCurrentCell(self.frmMain.w.banks.arr_position(4), 0)
        self.assertEqual(self.frmMain.w.banks.length(), 2)       
        self.frmMain.w.on_actionBankDelete_triggered()
        self.assertEqual(self.frmMain.w.banks.length(), 1)        
        self.frmMain.w.bank_add("Banco de Santander")#it will be bank5
        self.assertEqual(self.frmMain.w.banks.length(), 2)
        
        #Accounts IBM
        self.frmMain.on_actionAccounts_triggered()
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
        self.frmMain.w.tblAccounts.setCurrentCell(self.frmMain.w.accounts.arr_position(5), 0)
        w=frmAccountsReport(self.mem, self.frmMain.w.selAccount)
        w.txtAccount.setText("Cuenta Corriente Santander")
        w.on_cmdDatos_released()
        self.frmMain.w.on_chkInactivas_stateChanged(self.frmMain.w.chkInactivas.checkState())
        self.frmMain.w.load_table()
        ##Delete
        self.frmMain.w.tblAccounts.setCurrentCell(self.frmMain.w.accounts.arr_position(5), 0)
        self.frmMain.w.on_actionAccountDelete_triggered()
        ##Add other
        w=frmAccountsReport(self.mem, None)
        w.cmbEB.setCurrentIndex(w.cmbEB.findData(5))
        w.txtAccount.setText("Cuenta Corriente Santander")
        w.cmbCurrency.setCurrentIndex(w.cmbCurrency.findData("EUR"))
        w.txtNumero.setText("01234567890123456790")
        w.on_cmdDatos_released()#it will be account 5
        self.frmMain.w.on_chkInactivas_stateChanged(self.frmMain.w.chkInactivas.checkState())
        self.frmMain.w.load_table()
        
        #Investments IBM
        self.frmMain.on_actionInvestments_triggered()
        ##Add
        w=frmInvestmentReport(self.mem, None)
        w.cmbAccount.setCurrentIndex(w.cmbAccount.findData(6))
        w.txtInvestment.setText("Telefónica")
        d=frmProductSelector(w.ise, self.mem)
        d.txt.setText("78241")
        d.on_cmd_released()
        d.tblInvestments.setCurrentCell(0, 0)
        w.ise.setSelected(d.products.selected)
        w.on_cmdInvestment_released()
        
        #Load benchmark qquotes
#        w=WorkerYahooHistorical(mem, 1,  "select * from products where id="+str(self.mem.benchmark.id))
#        w.run()
#        
        
        
        

class TestXulpymoneyControlData(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.mem=mem
        self.frmMain=frmMain   
        
    def test_wdgProducts_search(self):
        self.frmMain.on_actionSearch_triggered()
        self.frmMain.w.txt.setText("monetario")
        self.frmMain.w.on_cmd_pressed()
        self.assertEqual(17, self.frmMain.w.tblInvestments.rowCount())        

if __name__ == '__main__':
    #Create db pruebas
    app = QApplication(sys.argv)
#    QTextCodec.setCodecForTr(QTextCodec.codecForName("UTF-8"));
    
    translator = QTranslator(app)
    locale=QLocale()
    a=locale.system().name()
    if len(a)!=2:
        a=a[:-len(a)+2]
    s= QApplication.translate("Core",  "Local language detected:{0}").format(a)
    print (s)
    translator.load("/usr/lib/xulpymoney/xulpymoney_" + a + ".qm")
    app.installTranslator(translator);
    
    mem=MemXulpymoney()
    mem.setQTranslator(QTranslator(app))
    #Crea conexi´on con frmAccess
    access=frmAccess(mem)
    access.txtServer.setText("127.0.0.1")
    access.txtPort.setText("5432")
    access.txtDB.setText("template1")
    access.txtUser.setText("postgres")
    access.txtPass.setFocus()
    access.exec_()
    if access==QDialog.Rejected:
        sys.exit(1)
    
    dbadmin=DBAdmin(access.con)
    dbadmin.drop_db("xulpymoney_pruebas")
    
    print(access.con)
    access.con.disconnect()
    frm = frmInit() 
    frm.txtXulpymoney.setText("xulpymoney_pruebas")
    frm.txtPass.setText(access.con.password)
    frm.on_cmdCreate_released()
    mem.con=Connection().init__create(access.con.user, access.con.password, access.con.server, access.con.port, "xulpymoney_pruebas")
    mem.con.connect()
    frmMain= frmMain(mem)
    mem.load_db_data()       
        #Launch tests
    unittest.main(argv=[sys.argv[0]])

 
