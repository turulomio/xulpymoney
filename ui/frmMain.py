from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
from Ui_frmMain import *
from frmAbout import *
import libdbupdates
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
from wdgQuotesUpdate import *

class frmMain(QMainWindow, Ui_frmMain):
    """Clase principal del programa"""
    def __init__(self, mem, parent = 0,  flags = False):
        QMainWindow.__init__(self, None)
        self.setupUi(self)
        self.showMaximized()
        
        self.mem=mem
        self.sqlvacio="select * from products where id=-999999"
        self.setWindowTitle(self.tr("Xulpymoney 2010-{0} ©").format(version_date.year))
        
        self.w=QWidget()       
        
    def actionsEnabled(self, bool):
        self.menuBar.setEnabled(bool)
        self.toolBar.setEnabled(bool)
        
    @pyqtSlot()
    def on_actionGlobalReport_triggered(self):
        self.mem.data.load_inactives()
        import libodfgenerator
        file="AssetsReport.odt"
        doc=libodfgenerator.AssetsReport(self.mem, file, "/usr/share/xulpymoney/report.odt")
#        os.system("libreoffice --headless --convert-to pdf {}".format(file))
        doc.generate()
        
        
        #Open file
        if os.path.exists("/usr/bin/lowriter"):
            QProcess.startDetached("lowriter", [file, ] )
#            QProcess.startDetached("okular", [file[:-3]+"pdf", ] )
        elif os.path.exists("/usr/bin/kfmclient"):
            QProcess.startDetached("kfmclient", ["openURL", file] )
        elif os.path.exists("/usr/bin/gnome-open"):
            QProcess.startDetached( "gnome-open '" + file + "'" );
        else:         
            QDesktopServices.openUrl(QUrl("file://"+file));


        
    def init__continue(self):
        """Used to add frmAccess automatic access"""
        self.access=frmAccess(self.mem,  self)
        self.access.exec_()
        self.retranslateUi(self)
        
        if self.access.result()==QDialog.Rejected:
            self.on_actionExit_triggered()
            sys.exit(1)

        ##Update database
        libdbupdates.Update(self.mem)
        
        
        self.mem.actualizar_memoria() ##CARGA TODOS LOS DATOS Y LOS VINCULA       
        
        
        
        ##Admin mode
        if self.mem.adminmode:
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            input=QInputDialog.getText(self,  "Xulpymoney",  self.tr("Please introduce Admin Mode password"), QLineEdit.Password)
            if input[1]==True:
                res=self.mem.check_admin_mode(input[0])
                if res==None:
                    self.setWindowTitle(self.tr("Xulpymoney 2010-{0} © (Admin mode)").format(version_date.year))
                    self.setWindowIcon(self.mem.qicon_admin())
                    self.update()
                    self.mem.set_admin_mode(input[0])
                    self.mem.con.commit()
                    m.setText(self.tr("You have set the admin mode password. Please login again"))
                    m.exec_()
                    self.on_actionExit_triggered()
                    sys.exit(2)
                elif res==True:
                    self.setWindowTitle(self.tr("Xulpymoney 2010-{0} © (Admin mode)").format(version_date.year))
                    self.setWindowIcon(self.mem.qicon_admin())
                    self.update()
                    m.setText(self.tr("You are logged as an administrator"))
                    m.exec_()   
                elif res==False:
                    self.adminmode=False        
                    m.setText(self.tr("Bad 'Admin mode' password. You are logged as a normal user"))
                    m.exec_()   

    @QtCore.pyqtSlot()  
    def on_actionExit_triggered(self):
        self.mem.__del__()
        print ("App correctly closed")
        self.close()
        
    @pyqtSlot()
    def on_actionAbout_triggered(self):
        fr=frmAbout(self.mem, self, "frmabout")
        fr.open()

    @QtCore.pyqtSlot()  
    def on_actionBanks_triggered(self):
        self.w.close()
        self.w=wdgBanks(self.mem)
                
        self.layout.addWidget(self.w)
        self.w.show()
        
    @QtCore.pyqtSlot()  
    def on_actionCalculator_triggered(self):
        d=QDialog(self)        
        d.setFixedSize(850, 850)
        d.setWindowTitle(self.tr("Investment calculator"))
        w=wdgCalculator(self.mem)
        lay = QVBoxLayout(d)
        lay.addWidget(w)
        if w.hasProducts==True:
            d.show()
        else:
            d.close()
        
    @QtCore.pyqtSlot()  
    def on_actionConcepts_triggered(self):
        self.w.close()
        self.w=wdgConcepts(self.mem)
                
        self.layout.addWidget(self.w)
        self.w.show()
        
    @QtCore.pyqtSlot()  
    def on_actionAccounts_triggered(self):
        self.w.close()
        self.w=wdgAccounts(self.mem)
                
        self.layout.addWidget(self.w)
        self.w.show()
    
    @QtCore.pyqtSlot()  
    def on_actionMemory_triggered(self):        
        self.mem.data.reload()
        
        
    @QtCore.pyqtSlot()  
    def on_actionDividendsReport_triggered(self):
        self.w.close()
        self.w=wdgDividendsReport(self.mem)
                
        self.layout.addWidget(self.w)
        self.w.show()
        
    @QtCore.pyqtSlot()  
    def on_actionInvestmentsClasses_triggered(self):
        self.w.close()
        self.w=wdgInvestmentClasses(self.mem)
                
        self.layout.addWidget(self.w)
        self.w.show()

    @QtCore.pyqtSlot()  
    def on_actionJointReport_triggered(self):
        self.w.close()
        self.w=wdgJointReport(self.mem)
                
        self.layout.addWidget(self.w)
        self.w.show()        
            
    @QtCore.pyqtSlot()  
    def on_actionTotalReport_triggered(self):
        self.w.close()
        self.w=wdgTotal(self.mem)
                
        self.layout.addWidget(self.w)
        self.w.show()

    @QtCore.pyqtSlot()  
    def on_actionReloadPrices_triggered(self):
        self.mem.data.reload_prices()

    @QtCore.pyqtSlot()  
    def on_actionReportAPR_triggered(self):
        self.w.close()
        self.w=wdgAPR(self.mem)
              
        self.layout.addWidget(self.w)
        self.w.show()
        
    @QtCore.pyqtSlot()  
    def on_actionHelp_triggered(self):
        w=frmHelp(self.mem)
        w.exec_()
    @QtCore.pyqtSlot()  
    def on_actionIndexRange_triggered(self):
        self.w.close()
        self.w=wdgIndexRange(self.mem)
                
        self.layout.addWidget(self.w)
        self.w.show()


    @QtCore.pyqtSlot()  
    def on_actionInvestments_triggered(self):
        self.w.close()
        self.w=wdgInvestments(self.mem)
               
        self.layout.addWidget(self.w)
        self.w.show()
        
    @QtCore.pyqtSlot()  
    def on_actionInvestmentsOperations_triggered(self):
        self.w.close()
        self.w=wdgInvestmentsOperations(self.mem)
        self.layout.addWidget(self.w)
        self.w.show()

    @QtCore.pyqtSlot()  
    def on_actionAuxiliarTables_triggered(self):
        w=frmAuxiliarTables(self.mem)
        w.exec_()
        
    @QtCore.pyqtSlot()  
    def on_actionSettings_triggered(self):
        w=frmSettings(self.mem, self)
        w.exec_()
        self.retranslateUi(self)

    @QtCore.pyqtSlot()  
    def on_actionTransfer_triggered(self):
        w=frmTransfer(self.mem)
        w.exec_()
        self.on_actionAccounts_triggered()

#    def closeEvent(self,  event):
#        self.on_actionExit_triggered()
################################
                
    @QtCore.pyqtSlot()  
    def on_actionCAC40_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where agrupations like '%|CAC|%' order by name,id")

        self.layout.addWidget(self.w)
        self.w.show()                
    @QtCore.pyqtSlot()  
    def on_actionActive_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where obsolete=false order by name")

        self.layout.addWidget(self.w)
        self.w.show()
    
    @QtCore.pyqtSlot()  
    def on_actionCurrenciesAll_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where type=6 order by name,id")

        self.layout.addWidget(self.w)
        self.w.show()
    @QtCore.pyqtSlot()  
    def on_actionDividends_triggered(self):
        """Shows products with current year estimations_dps and with quotes in current year"""
        self.w.close()
        self.w=wdgProducts(self.mem, "select * from products where id in (select id from estimations_dps where year=date_part('year',now()) and estimation is not null) and id in (select distinct(id) from quotes where date_part('year', datetime)=date_part('year',now()));")
#        self.w=wdgProducts(self.mem,  "select * from products where id in (select distinct(quotes.id) from quotes, estimations_dps where quotes.id=estimations_dps.id and year={0}  and estimation is not null );".format(datetime.date.today().year))
        
        self.layout.addWidget(self.w)
        self.w.on_actionSortDividend_triggered()
        self.w.show()

        
    @QtCore.pyqtSlot()  
    def on_actionNasdaq100_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where agrupations like '%|NASDAQ100|%' order by name,id")

        self.layout.addWidget(self.w)
        self.w.show()
            
    @QtCore.pyqtSlot()  
    def on_actionISINDuplicado_triggered(self):
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
    def on_actionMC_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem, "select * from products where agrupations like '%|MERCADOCONTINUO|%' and obsolete=false  order by name,id")

        self.layout.addWidget(self.w)
        self.w.show()
        

    @QtCore.pyqtSlot()  
    def on_actionETFAll_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where type=4 and obsolete=false order by name, id")

        self.layout.addWidget(self.w)
        self.w.show()
        
    @QtCore.pyqtSlot()  
    def on_actionETFObsolete_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where type=4 and obsolete=true order by name, id")

        self.layout.addWidget(self.w)
        self.w.show()
        
    @QtCore.pyqtSlot()  
    def on_actionEurostoxx50_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where agrupations like '%|EUROSTOXX|%' order by name,id")

        self.layout.addWidget(self.w)
        self.w.show()
        

    @QtCore.pyqtSlot()  
    def on_actionFavorites_triggered(self):
        favoritos=self.mem.config.get_list("wdgProducts",  "favoritos")
        if len(favoritos)==0:
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.tr("There aren't favorite products"))
            m.exec_()     
            return
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where id in ("+str(favoritos)[1:-1]+") order by name, id")
        self.w.showingfavorites=True

        self.layout.addWidget(self.w)
        self.w.show()

    @QtCore.pyqtSlot()  
    def on_actionSharesAll_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where type=1 and obsolete=false order by name, id")

        self.layout.addWidget(self.w)
        self.w.show()         
        
    @QtCore.pyqtSlot()  
    def on_actionSharesObsolete_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where type=1  and obsolete=true order by name, id")

        self.layout.addWidget(self.w)
        self.w.show()        
        
    @QtCore.pyqtSlot()  
    def on_actionWarrantsAll_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where type=5 and obsolete=false order by name, id")

        self.layout.addWidget(self.w)
        self.w.show()          
        
    @QtCore.pyqtSlot()  
    def on_actionWarrantsObsolete_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where type=5 and obsolete=true order by name, id")

        self.layout.addWidget(self.w)
        self.w.show()          
        
    @QtCore.pyqtSlot()  
    def on_actionWarrantsCall_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where type=5 and pci='c'  and obsolete=false order by name, id")

        self.layout.addWidget(self.w)
        self.w.show()              
    @QtCore.pyqtSlot()  
    def on_actionWarrantsPut_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where type=5 and pci='p'  and obsolete=false order by name, id")

        self.layout.addWidget(self.w)
        self.w.show()              
    @QtCore.pyqtSlot()  
    def on_actionWarrantsInline_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where type=5 and pci='i'  and obsolete=false order by name, id")

        self.layout.addWidget(self.w)
        self.w.show()      

    @QtCore.pyqtSlot()  
    def on_actionFundsAll_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where type=2 and obsolete=false order by name, id")

        self.layout.addWidget(self.w)
        self.w.show()        
        
    @QtCore.pyqtSlot()  
    def on_actionFundsObsolete_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where type=2 and obsolete=true order by name, id")

        self.layout.addWidget(self.w)
        self.w.show()                        

    @QtCore.pyqtSlot()  
    def on_actionBondsPublic_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where type=7 and obsolete=false order by name, id")

        self.layout.addWidget(self.w)
        self.w.show()                        

    @QtCore.pyqtSlot()  
    def on_actionBondsPrivate_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where type=9 and obsolete=false order by name, id")

        self.layout.addWidget(self.w)
        self.w.show()

    @QtCore.pyqtSlot()  
    def on_actionPurgeAll_triggered(self):
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
        m.setText(self.tr("{0} quotes have been purged from {1} products".format(counter, len(products))))
        m.exec_()    
        
    @QtCore.pyqtSlot()  
    def on_actionBondsAll_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where type in (7,9) and obsolete=false order by name, id")

        self.layout.addWidget(self.w)
        self.w.show()
        
    @QtCore.pyqtSlot()  
    def on_actionBondsObsolete_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where type in (7,9) and obsolete=true order by name, id")

        self.layout.addWidget(self.w)
        self.w.show()

        

    @QtCore.pyqtSlot()  
    def on_actionIbex35_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select  * from products where agrupations like '%|IBEX|%' order by name,id")
        self.layout.addWidget(self.w)
        self.w.show()        

    @QtCore.pyqtSlot()  
    def on_actionLATIBEX_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select  * from products where agrupations like '%|LATIBEX|%' and obsolete=false order by name,id")
        self.layout.addWidget(self.w)
        self.w.show()
        
    @QtCore.pyqtSlot()  
    def on_actionIndexesAll_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select  * from products where type=3 order by id_bolsas,name")
        self.layout.addWidget(self.w)
        self.w.show()      
        
    @QtCore.pyqtSlot()  
    def on_actionIndexesObsolete_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select  * from products where type=3 and obsolete=true order by id_bolsas,name")
        self.layout.addWidget(self.w)
        self.w.show()        
                
    @QtCore.pyqtSlot()  
    def on_actionSP500_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where agrupations like '%|SP500|%' order by name,id")

        self.layout.addWidget(self.w)
        self.w.show()
    
    @QtCore.pyqtSlot()  
    def on_actionProductsInvestmentActive_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where id in (select products_id from inversiones where active=true) order by name")

        self.layout.addWidget(self.w)
        self.w.show()    
        
    @QtCore.pyqtSlot()  
    def on_actionProductsInvestmentInactive_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where id in (select products_id from inversiones where active=false) order by name")

        self.layout.addWidget(self.w)
        self.w.show()    
    @QtCore.pyqtSlot()  
    def on_actionProductsObsolete_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where obsolete=true order by name,id")

        self.layout.addWidget(self.w)
        self.w.show()
                
    @QtCore.pyqtSlot()  
    def on_actionProductsAutoUpdate_triggered(self):
        """Tuve muchos problemas alf inal si isin!='' o isin<>'', no muestra los null ni los '" """
        self.w.close()
        self.w=wdgProducts(self.mem,  """select * from products 
                where obsolete=false and 
                (
                    (9 = any(priority) and isin<>'')
                    or (8 = any(priorityhistorical) and isin<>'')
                    or (1 = any(priority) and ticker<>'')
                    or (3 = any(priorityhistorical) and ticker<>'')
                )
                order by name
                """)

        self.layout.addWidget(self.w)
        self.w.show()       
    
    @QtCore.pyqtSlot()  
    def on_actionProductsNotAutoUpdate_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  """select * from products where obsolete=false except 
                select * from products 
                where obsolete=false and 
                (
                    (9 = any(priority) and isin<>'')
                    or (8 = any(priorityhistorical) and isin<>'')
                    or (1 = any(priority) and ticker<>'')
                    or (3 = any(priorityhistorical) and ticker<>'')
                )
                order by name
                """)
        self.layout.addWidget(self.w)
        self.w.show()            
        
    @QtCore.pyqtSlot()  
    def on_actionProductsUser_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where id<0 order by name, id ")

        self.layout.addWidget(self.w)
        self.w.show()
        
    @QtCore.pyqtSlot()  
    def on_actionProductsWithoutISIN_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products  where obsolete=false and (isin is null or isin ='') order by name,id")

        self.layout.addWidget(self.w)
        self.w.show()

    @QtCore.pyqtSlot()  
    def on_actionTablasAuxiliares_triggered(self):
        w=frmAuxiliarTables(self.mem)
        w.tblTipos_reload()
        w.exec_()

                
    @QtCore.pyqtSlot()  
    def on_actionXetra_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where agrupations like '%|DAX|%' order by name,id")

        self.layout.addWidget(self.w)
        self.w.show()        
        
    @QtCore.pyqtSlot()  
    def on_actionSearch_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  self.sqlvacio)

        self.layout.addWidget(self.w)
        self.w.show()
        

    @QtCore.pyqtSlot()  
    def on_actionPriceUpdates_triggered(self):  
        self.w.close()
        self.w=wdgQuotesUpdate(self.mem, self)
        self.layout.addWidget(self.w)