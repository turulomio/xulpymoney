import sys
sys.path.append("/usr/lib/xulpymoney")
from libxulpymoney import *
from frmMain import *
from frmInit import *
from libsources import *
from wdgProductSelector import *

#Parameters simulation
class MemSimulation(MemXulpymoney):
    def __init__(self):
        MemXulpymoney.__init__(self)
        self.database="xulpymoney_simulation"
        self.database_real="xulpymoney"
        self.date_start=datetime.date(2005,1,1)
        self.ranges_percentaje=2
        self.money=Decimal(100000)
        self.index_lowest=4000
        self.strcon_real="dbname='{}' port='5432' user='postgres' host='127.0.0.1' password='*'".format(self.database_real)
        self.con_real=psycopg2.extras.DictConnection(self.strcon_real)
        
    def drop_db(self):
        strtemplate1="dbname='template1' port='5432' user='postgres' host='127.0.0.1' password='*'" 
        cont=psycopg2.extras.DictConnection(strtemplate1)
        cont.set_isolation_level(0)                                    
        try:
            cur=cont.cursor()
            cur.execute("drop database {};".format(self.database))
            cur.close()
            cont.close()
        except:
            cur.close()
            cont.close()
            return False
        return True        

init=datetime.datetime.now()
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

    mem=MemSimulation()
    frm = frmInit() 
    frm.txtXulpymoney.setText(mem.database)
    mem.drop_db() 
    if frm.create_db(frm.txtXulpymoney.text()) and frm.create_xulpymoney():
        #Load data Xulpymoney infraestructure
        mem.setQTranslator(QTranslator(app))
        mem.qtranslator.load("/usr/lib/xulpymoney/xulpymoney_{0}.qm".format(mem.config.get_value("settings", "language")))
        app.installTranslator(mem.qtranslator)
        frmMain= frmMain(mem)
        strcon="dbname='{}' port='5432' user='postgres' host='127.0.0.1' password='*'".format(mem.database)
        mem.con=psycopg2.extras.DictConnection(strcon) 
        mem.actualizar_memoria()
    else:
        print("No pude crear db")


    
    #Load quotes from real database
    print (mem.data.benchmark.id)
    cur=mem.con_real.cursor()
    cur.execute("select * from quotes where id=79329")
    for row in cur:
        quote=Quote(mem).init__db_row(row, mem.data.benchmark)
        quote.save()
    cur.close()
    mem.con.commit()

    #Create bank
    frmMain.on_actionBanks_activated()
    frmMain.w.bank_add("Simulated bank")#It will be bank 4
    
    #Create account
    frmMain.on_actionAccounts_activated()
    w=frmAccountsReport(mem, None)
    w.cmbEB.setCurrentIndex(w.cmbEB.findData(4))
    w.txtAccount.setText("Simulated account")
    w.cmbCurrency.setCurrentIndex(w.cmbCurrency.findData("EUR"))
    w.txtNumero.setText("01234567890123456789")
    w.on_cmdDatos_released()#it will be account 5
    frmMain.w.on_chkInactivas_stateChanged(frmMain.w.chkInactivas.checkState())
    frmMain.w.load_table()
    
    # Create investments
    frmMain.on_actionInvestments_activated()
    ##Add
    for i in range(1, 21):
        w=frmInvestmentReport(mem, None)
        w.cmbAccount.setCurrentIndex(w.cmbAccount.findData(5))
        w.txtInvestment.setText("Simulated Investment {}".format(i))
        d=frmProductSelector(None, mem)
        d.txt.setText("79329")
        d.on_cmd_released()
        d.tblInvestments.setCurrentCell(0, 0)
        w.ise.setSelected(d.selected)
        w.on_cmdInvestment_pressed()
    frmMain.w.on_chkInactivas_stateChanged(frmMain.w.chkInactivas.checkState())#Carga la tabla
#        frmMain.w.tblInvestments.setCurrentCell(0, 0)
#        frmMain.w.on_actionActive_activated()

        
    
    print ("Simulation duration: {}".format(datetime.datetime.now()-init))
    
    
    frmMain.show()
    
    sys.exit(app.exec_())    
