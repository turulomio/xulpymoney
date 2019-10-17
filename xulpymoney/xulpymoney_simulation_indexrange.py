import sys
sys.path.append("/usr/lib/xulpymoney")
from xulpymoney.libxulpymoney import *
from xulpymoney.ui.frmMain import *
from xulpymoney.ui.frmInit import *
from xulpymoney.ui.wdgProductSelector import *

## Parameters simulation
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
        
        
    def investment_create(self, range):
        frmMain.on_actionInvestments_triggered()
        ##Add
        w=frmInvestmentReport(mem, None)
        w.cmbAccount.setCurrentIndex(w.cmbAccount.findData(5))
        w.txtInvestment.setText("Simulated Investment {}".format(int(range)))
        d=frmProductSelector(None, mem)
        d.txt.setText("79329")
        d.on_cmd_released()
        d.tblInvestments.setCurrentCell(0, 0)
        w.ise.setSelected(d.selected)
        w.on_cmdInvestment_pressed()
        
    def range_change(self, new):
        if new<current_range*1.02 or new>current_range*0.98:
           return False
        return True
        
    def range_already_invested(self, range):
        pass
        

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
    s= QApplication.translate("Mem",  "Local language detected:{0}").format(a)
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
        mem.qtranslator.load("/usr/lib/xulpymoney/xulpymoney_{0}.qm".format(mem.language.id))
        app.installTranslator(mem.qtranslator)
        frmMain= frmMain(mem)
        strcon="dbname='{}' port='5432' user='postgres' host='127.0.0.1' password='*'".format(mem.database)
        mem.con=psycopg2.extras.DictConnection(strcon) 
        mem.load_db_data()
    else:
        print("No pude crear db")


    
    #Load quotes from real database
    print (mem.data.benchmark.id)
    quotes=[]
    cur=mem.con_real.cursor()
    cur.execute("select * from quotes where id=79329")
    for row in cur:
        quote=Quote(mem).init__db_row(row, mem.data.benchmark)
        quote.save()
        quotes.append(quote)
    cur.close()
    mem.con.commit()

    #Create bank
    frmMain.on_actionBanks_triggered()
    frmMain.w.bank_add("Simulated bank")#It will be bank 4
    
    #Create account
    frmMain.on_actionAccounts_triggered()
    w=frmAccountsReport(mem, None)
    w.cmbEB.setCurrentIndex(w.cmbEB.findData(4))
    w.txtAccount.setText("Simulated account")
    w.cmbCurrency.setCurrentIndex(w.cmbCurrency.findData("EUR"))
    w.txtNumero.setText("01234567890123456789")
    w.on_cmdDatos_released()#it will be account 5
    frmMain.w.on_chkInactivas_stateChanged(frmMain.w.chkInactivas.checkState())
    frmMain.w.load_table()

    current_range=0
    current_time=None
    mem.investment_create(current_range)
    #iterate quotes
    for quote in quotes:
        
        #Hay venta
        
        #Hay cambio de rango
        if mem.range_change(quote.quote):
            #Se ha invertido en rango
            if mem.range_already_invested(current_range):
                pass
        
    
        #Hay reinversion
    print ("Simulation duration: {}".format(datetime.datetime.now()-init))
    
    
    frmMain.show()
    
    sys.exit(app.exec_())    
