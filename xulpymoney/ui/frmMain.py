from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys
from Ui_frmMain import *
from frmAbout import *
from libxulpymoney import *
from frmAccess import *
from wdgTotal import *
from wdgDividendsReport import *
from wdgInvestmentClasses import *
from wdgJointReport import *
from wdgAPR import *
from wdgAccounts import *
from wdgBanks import *
from wdgConcepts import *
from wdgCalculator import *
from wdgIndexRange import *
from wdgInvestments import *
from wdgInvestmentsOperations import *
from frmAuxiliarTables import *
from frmTransfer import *
from frmSettings import *
from frmHelp import *
from wdgProducts import *
from libsources import WorkerYahooHistorical

class frmMain(QMainWindow, Ui_frmMain):
    """Clase principal del programa"""
    def __init__(self, mem, parent = 0,  flags = False):
        QMainWindow.__init__(self, None)
        self.setupUi(self)
        self.showMaximized()
        
        self.mem=mem
        self.sqlvacio="select * from products where id=-999999"
        self.setWindowTitle(self.trUtf8("Xulpymoney 2010-{0} ©").format(version_date.year))
        
        self.w=QWidget()       
        
    def init__continue(self):
        """Used to add frmAccess automatic access"""
        self.access=frmAccess(self.mem,  self)
        self.access.exec_()
        self.retranslateUi(self)
        
        if self.access.result()==QDialog.Rejected:
            self.on_actionExit_activated()
            sys.exit(1)

        
        self.mem.actualizar_memoria() ##CARGA TODOS LOS DATOS Y LOS VINCULA       
        
        ##Admin mode
        if self.mem.adminmode:
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            input=QInputDialog.getText(self,  "Xulpymoney",  self.tr("Please introduce Admin Mode password"), QLineEdit.Password)
            if input[1]==True:
                res=self.mem.check_admin_mode(input[0])
                if res==None:
                    self.setWindowTitle(self.trUtf8("Xulpymoney 2010-{0} © (Admin mode)").format(version_date.year))
                    self.setWindowIcon(self.mem.qicon_admin())
                    self.update()
                    self.mem.set_admin_mode(input[0])
                    self.mem.con.commit()
                    m.setText(self.trUtf8("You have set the admin mode password. Please login again"))
                    m.exec_()
                    self.on_actionExit_activated()
                    sys.exit(2)
                elif res==True:
                    self.setWindowTitle(self.trUtf8("Xulpymoney 2010-{0} © (Admin mode)").format(version_date.year))
                    self.setWindowIcon(self.mem.qicon_admin())
                    self.update()
                    m.setText(self.trUtf8("You are logged as an administrator"))
                    m.exec_()   
                elif res==False:
                    self.adminmode=False        
                    m.setText(self.trUtf8("Bad 'Admin mode' password. You are logged as a normal user"))
                    m.exec_()   
        
        print ("Protecting products needed in xulpymoney")
        cur=self.mem.con.cursor()
        cur.execute("select distinct(mystocksid) from inversiones;")
        ids2protect=[]
        for row in cur:
            ids2protect.append(row[0])
        if len(ids2protect)>0:
            Product(self.mem).changeDeletable(  ids2protect,  False)
        self.mem.con.commit()
        
        
    @QtCore.pyqtSlot()  
    def on_actionExit_activated(self):
        self.mem.__del__()
        print ("App correctly closed")
        self.close()
        
    @pyqtSignature("")
    def on_actionAbout_activated(self):
        fr=frmAbout(self.mem, self, "frmabout")
        fr.open()

    @QtCore.pyqtSlot()  
    def on_actionBanks_activated(self):
        self.w.close()
        self.w=wdgBanks(self.mem)
                
        self.layout.addWidget(self.w)
        self.w.show()
        
    @QtCore.pyqtSlot()  
    def on_actionCalculator_activated(self):
        d=QDialog(self)        
        d.setFixedSize(670, 670)
        d.setWindowTitle(self.trUtf8("Investment calculator"))
        w=wdgCalculator(self.mem)
        lay = QVBoxLayout(d)
        lay.addWidget(w)
        d.show()
    @QtCore.pyqtSlot()  
    def on_actionConcepts_activated(self):
        self.w.close()
        self.w=wdgConcepts(self.mem)
                
        self.layout.addWidget(self.w)
        self.w.show()
        
    @QtCore.pyqtSlot()  
    def on_actionAccounts_activated(self):
        self.w.close()
        self.w=wdgAccounts(self.mem)
                
        self.layout.addWidget(self.w)
        self.w.show()
    
    @QtCore.pyqtSlot()  
    def on_actionMemory_activated(self):        
        self.mem.data.reload()
        
        
    @QtCore.pyqtSlot()  
    def on_actionDividendsReport_activated(self):
        self.w.close()
        self.w=wdgDividendsReport(self.mem)
                
        self.layout.addWidget(self.w)
        self.w.show()
        
    @QtCore.pyqtSlot()  
    def on_actionInvestmentsClasses_activated(self):
        self.w.close()
        self.w=wdgInvestmentClasses(self.mem)
                
        self.layout.addWidget(self.w)
        self.w.show()

    @QtCore.pyqtSlot()  
    def on_actionJointReport_activated(self):
        self.w.close()
        self.w=wdgJointReport(self.mem)
                
        self.layout.addWidget(self.w)
        self.w.show()        
            
    @QtCore.pyqtSlot()  
    def on_actionTotalReport_activated(self):
        self.w.close()
        self.w=wdgTotal(self.mem)
                
        self.layout.addWidget(self.w)
        self.w.show()

    @QtCore.pyqtSlot()  
    def on_actionReloadPrices_activated(self):
        ##Selecting products to update
        if self.mem.data.loaded_inactive==False:
            products=self.mem.data.products_active
        else:
            products=self.mem.data.products_all()
        
        pd= QProgressDialog(self.tr("Reloading {0} product prices from database").format(len(products.arr)),None, 0,len(products.arr))
        pd.setModal(True)
        pd.setWindowTitle(self.tr("Reloading prices..."))
        pd.forceShow()
        for i, p in enumerate(products.arr):
            pd.setValue(i)
            pd.update()
            QApplication.processEvents()
            p.result.basic.load_from_db()
        self.mem.data.benchmark.result.basic.load_from_db()

    @QtCore.pyqtSlot()  
    def on_actionReportAPR_activated(self):
        self.w.close()
        self.w=wdgAPR(self.mem)
              
        self.layout.addWidget(self.w)
        self.w.show()
        
    @QtCore.pyqtSlot()  
    def on_actionHelp_activated(self):
        w=frmHelp(self.mem)
        w.exec_()
    @QtCore.pyqtSlot()  
    def on_actionIndexRange_activated(self):
        self.w.close()
        self.w=wdgIndexRange(self.mem)
                
        self.layout.addWidget(self.w)
        self.w.show()

    @QtCore.pyqtSlot()  
    def on_actionInvestments_activated(self):
        self.w.close()
        self.w=wdgInvestments(self.mem)
               
        self.layout.addWidget(self.w)
        self.w.show()
        
    @QtCore.pyqtSlot()  
    def on_actionInvestmentsOperations_activated(self):
        self.w.close()
        self.w=wdgInvestmentsOperations(self.mem)
        self.layout.addWidget(self.w)
        self.w.show()

    @QtCore.pyqtSlot()  
    def on_actionAuxiliarTables_activated(self):
        w=frmAuxiliarTables(self.mem)
        w.exec_()
        
    @QtCore.pyqtSlot()  
    def on_actionSettings_activated(self):
        w=frmSettings(self.mem, self)
        w.exec_()
        self.retranslateUi(self)

    @QtCore.pyqtSlot()  
    def on_actionTransfer_activated(self):
        w=frmTransfer(self.mem)
        w.exec_()
        self.on_actionAccounts_activated()

#    def closeEvent(self,  event):
#        self.on_actionExit_activated()
################################
                
    @QtCore.pyqtSlot()  
    def on_actionCAC40_activated(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where agrupations like '%|CAC|%' order by name,id")

        self.layout.addWidget(self.w)
        self.w.show()                
    @QtCore.pyqtSlot()  
    def on_actionActive_activated(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where active=true order by name")

        self.layout.addWidget(self.w)
        self.w.show()
    
    @QtCore.pyqtSlot()  
    def on_actionCurrenciesAll_activated(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where type=6 order by name,id")

        self.layout.addWidget(self.w)
        self.w.show()
    @QtCore.pyqtSlot()  
    def on_actionDividends_activated(self):
        """Shows products with current year estimations_dps and with quotes in current year"""
        self.w.close()
        self.w=wdgProducts(self.mem, "select * from products where id in (select id from estimations_dps where year=date_part('year',now()) and estimation is not null) and id in (select distinct(id) from quotes where date_part('year', datetime)=date_part('year',now()));")
#        self.w=wdgProducts(self.mem,  "select * from products where id in (select distinct(quotes.id) from quotes, estimations_dps where quotes.id=estimations_dps.id and year={0}  and estimation is not null );".format(datetime.date.today().year))
        
        self.layout.addWidget(self.w)
        self.w.on_actionSortDividend_activated()
        self.w.show()

        
    @QtCore.pyqtSlot()  
    def on_actionNasdaq100_activated(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where agrupations like '%|NASDAQ100|%' order by name,id")

        self.layout.addWidget(self.w)
        self.w.show()
            
    @QtCore.pyqtSlot()  
    def on_actionISINDuplicado_activated(self):
        self.w.close()
        cur=self.mem.con.cursor()
        #ßaca los isin duplicados buscando distintct isin, bolsa con mas de dos registros
        cur.execute("select isin, id_bolsas, count(*) as num from products  where isin!='' group by isin, id_bolsas having count(*)>1 order by num desc;")
        isins=set([])
        for row in cur:
            isins.add(row['isin'] )
        if len(isins)>0:
            self.w=wdgProducts(self.mem,  "select * from products where isin in ("+list2string(list(isins))+") order by isin, id_bolsas")
        else:
            self.w=wdgProducts(self.mem, self.sqlvacio)

        self.layout.addWidget(self.w)
        self.w.show()
        
    @QtCore.pyqtSlot()  
    def on_actionMC_activated(self):
        self.w.close()
        self.w=wdgProducts(self.mem, "select * from products where agrupations like '%|MERCADOCONTINUO|%' order by name,id")

        self.layout.addWidget(self.w)
        self.w.show()
        

    @QtCore.pyqtSlot()  
    def on_actionETFAll_activated(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where type=4 order by name, id")

        self.layout.addWidget(self.w)
        self.w.show()
        
    @QtCore.pyqtSlot()  
    def on_actionEurostoxx50_activated(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where agrupations like '%|EUROSTOXX|%' order by name,id")

        self.layout.addWidget(self.w)
        self.w.show()
        

    @QtCore.pyqtSlot()  
    def on_actionFavorites_activated(self):
        favoritos=self.mem.config.get_list("wdgProducts",  "favoritos")
        if len(favoritos)==0:
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.tr("There aren't favorite products"))
            m.exec_()     
            return
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where id in ("+str(favoritos)[1:-1]+") order by name, id")

        self.layout.addWidget(self.w)
        self.w.show()

    @QtCore.pyqtSlot()  
    def on_actionSharesAll_activated(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where type=1 order by name, id")

        self.layout.addWidget(self.w)
        self.w.show()          
    @QtCore.pyqtSlot()  
    def on_actionWarrantsAll_activated(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where type=5 order by name, id")

        self.layout.addWidget(self.w)
        self.w.show()          
        
    @QtCore.pyqtSlot()  
    def on_actionWarrantsCall_activated(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where type=5 and pci='c' order by name, id")

        self.layout.addWidget(self.w)
        self.w.show()              
    @QtCore.pyqtSlot()  
    def on_actionWarrantsPut_activated(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where type=5 and pci='p' order by name, id")

        self.layout.addWidget(self.w)
        self.w.show()              
    @QtCore.pyqtSlot()  
    def on_actionWarrantsInline_activated(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where type=5 and pci='i' order by name, id")

        self.layout.addWidget(self.w)
        self.w.show()      
    @QtCore.pyqtSlot()  
    def on_actionFundsAll_activated(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where type=2 order by name, id")

        self.layout.addWidget(self.w)
        self.w.show()                        

    @QtCore.pyqtSlot()  
    def on_actionBondsPublic_activated(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where type=7 order by name, id")

        self.layout.addWidget(self.w)
        self.w.show()                        

    @QtCore.pyqtSlot()  
    def on_actionBondsPrivate_activated(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where type=9 order by name, id")

        self.layout.addWidget(self.w)
        self.w.show()

    @QtCore.pyqtSlot()  
    def on_actionPurgeAll_activated(self):
        """Purga todas las quotes de todas inversión. """
        products=[]
        curms=self.mem.con.cursor()
        curms.execute("select * from products where id in ( select distinct( id) from quotes) order by name;")
        for row in curms:
            products.append(Product(self.mem).init__db_row(row))
        curms.close()
               
        
        pd= QProgressDialog(QApplication.translate("Core","Purging innecesary data from all products"), QApplication.translate("Core","Cancel"), 0,len(products))
        pd.setModal(True)
        pd.setWindowTitle(QApplication.translate("Core","Purging quotes from all products"))
        pd.setMinimumDuration(0)          
        counter=0      
        
        for i, inv in enumerate(products):
            pd.setValue(i)
            pd.setLabelText(QApplication.translate("Core","Purging quotes from {0}.\nTotal purged in global process: {1}").format(inv.name,  counter))
            pd.update()
            QApplication.processEvents()
            if pd.wasCanceled():
                self.mem.con.rollback()
                return
            pd.update()
            QApplication.processEvents()
            pd.update()            
            inv.result.all.load_from_db(inv)
            invcounter=inv.result.all.purge(progress=True)
            if invcounter==None:#Pulsado cancelar
                self.mem.con.rollback()
                break
            else:
                counter=counter+invcounter
                self.mem.con.commit()
        
        m=QMessageBox()
        m.setIcon(QMessageBox.Information)
        m.setText(self.trUtf8("{0} quotes have been purged from {1} products".format(counter, len(products))))
        m.exec_()    
        
    @QtCore.pyqtSlot()  
    def on_actionBondsAll_activated(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where type in (7,9) order by name, id")

        self.layout.addWidget(self.w)
        self.w.show()

        

    @QtCore.pyqtSlot()  
    def on_actionIbex35_activated(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select  * from products where agrupations like '%|IBEX|%' order by name,id")
        self.layout.addWidget(self.w)
        self.w.show()        

    @QtCore.pyqtSlot()  
    def on_actionLATIBEX_activated(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select  * from products where agrupations like '%|LATIBEX|%' order by name,id")
        self.layout.addWidget(self.w)
        self.w.show()
        
    @QtCore.pyqtSlot()  
    def on_actionIndexesAll_activated(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select  * from products where type=3 order by id_bolsas,name")
        self.layout.addWidget(self.w)
        self.w.show()        
                
    @QtCore.pyqtSlot()  
    def on_actionSP500_activated(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where agrupations like '%|SP500|%' order by name,id")

        self.layout.addWidget(self.w)
        self.w.show()
    
    @QtCore.pyqtSlot()  
    def on_actionInvestmentsDesaparecidas_activated(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where obsolete=true order by name,id")

        self.layout.addWidget(self.w)
        self.w.show()
                
    @QtCore.pyqtSlot()  
    def on_actionInvestmentsSinActualizar_activated(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where id in( select id  from quotes group by id having last(datetime::date)<now()::date-60)")

        self.layout.addWidget(self.w)
        self.w.show()       
    
    @QtCore.pyqtSlot()  
    def on_actionInvestmentsSinActualizarHistoricos_activated(self):
        self.w.close()
        self.w=wdgProducts(self.mem, "select * from products where id in (select id from quotes  group by id having date_part('microsecond',last(datetime))=4 and last(datetime)<now()-interval '60 days' );")

        self.layout.addWidget(self.w)
        self.w.show()            
        
    @QtCore.pyqtSlot()  
    def on_actionInvestmentsManual_activated(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where id<0 order by name, id ")

        self.layout.addWidget(self.w)
        self.w.show()
        
    @QtCore.pyqtSlot()  
    def on_actionInvestmentsSinISIN_activated(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products  where isin is null or isin ='' order by name,id")

        self.layout.addWidget(self.w)
        self.w.show()


    @QtCore.pyqtSlot()  
    def on_actionInvestmentsSinNombre_activated(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products  where name is null or name='' order by name,id")

        self.layout.addWidget(self.w)
        self.w.show()

        
    @QtCore.pyqtSlot()  
    def on_actionTablasAuxiliares_activated(self):
        w=frmAuxiliarTables(self.mem)
        w.tblTipos_reload()
        w.exec_()

                
    @QtCore.pyqtSlot()  
    def on_actionXetra_activated(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where agrupations like '%|DAX|%' order by name,id")

        self.layout.addWidget(self.w)
        self.w.show()        
        
    @QtCore.pyqtSlot()  
    def on_actionSearch_activated(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  self.sqlvacio)

        self.layout.addWidget(self.w)
        self.w.show()
        

    @QtCore.pyqtSlot()  
    def on_actionPriceUpdates_activated(self):  
        WorkerYahooHistorical(self.mem, 2)
        self.on_actionReloadPrices_activated()
