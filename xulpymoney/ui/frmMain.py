from PyQt5.QtCore import pyqtSlot, QProcess, QUrl,  QSize
from PyQt5.QtGui import QIcon, QDesktopServices
from PyQt5.QtWidgets import QMainWindow,  QWidget, QLabel, QMessageBox, QProgressDialog, QDialog,  QApplication, QVBoxLayout
import os
import datetime
import math
import platform
import sys
import multiprocessing
from multiprocessing.pool import ThreadPool
import subprocess
from Ui_frmMain import Ui_frmMain
from frmAbout import frmAbout
from libxulpymoney import AssetsReport, list2string, qmessagebox, Product,  SetProducts
from libxulpymoneyversion import version_date
from libsources import sync_data
from frmAccess import frmAccess
from wdgTotal import wdgTotal
from wdgDividendsReport import wdgDividendsReport
from wdgInvestmentClasses import wdgInvestmentClasses
from wdgAPR import wdgAPR
from wdgAccounts import wdgAccounts
from wdgBanks import wdgBanks
from wdgConcepts import wdgConcepts
from wdgCalculator import wdgCalculator
from wdgCuriosities import wdgCuriosities
from wdgIndexRange import wdgIndexRange
from wdgInvestments import wdgInvestments
from wdgInvestmentsOperations import wdgInvestmentsOperations
from wdgInvestmentsRanking import wdgInvestmentsRanking
from frmAuxiliarTables import frmAuxiliarTables
from frmTransfer import frmTransfer
from frmSettings import frmSettings
from frmHelp import frmHelp
from wdgOrders import wdgOrders
from wdgProducts import wdgProducts
from wdgSimulations import wdgSimulations
from wdgQuotesUpdate import wdgQuotesUpdate
from wdgLastCurrent import wdgLastCurrent

class frmMain(QMainWindow, Ui_frmMain):
    def __init__(self, mem, parent = 0,  flags = False):
        QMainWindow.__init__(self, None)
        self.setupUi(self)
        self.showMaximized()
        
        self.mem=mem
        self.mem.con.inactivity_timeout.connect(self.inactivity_timeout)        
        self.sqlvacio="select * from products where id=-999999"
        #print ("Xulpymoney 2010-{0} © €".encode('unicode-escape'))
        
        self.w=QWidget()       

        self.statusBar.addWidget(QLabel(self.tr("Server: {}:{}      Database: {}      User: {}").format(self.mem.con.server, self.mem.con.port,  self.mem.con.db, self.mem.con.user)))

        self.mem.load_db_data() ##CARGA TODOS LOS DATOS Y LOS VINCULA       
  
        if self.mem.con.is_superuser():
            self.setWindowTitle(self.tr("Xulpymoney 2010-{0} \xa9 (Admin mode)").format(version_date().year))
            self.setWindowIcon(self.mem.qicon_admin())
        else:
            self.setWindowTitle(self.tr("Xulpymoney 2010-{0} \xa9").format(version_date().year))

#        model=ReinvestModel(mem, [2500, 3500, 12000, 12000], self.mem.data.products.find_by_id(79228), Percentage(1, 3), Percentage(1, 10))
#        model.print()
#        model=ReinvestModel(mem, [5000, 7000, 24000, 24000], self.mem.data.products.find_by_id(79228), Percentage(1, 3), Percentage(1, 10))
#        model.print()
#        a=2500
#        model=ReinvestModel(mem, [a, 2*a, 6*a, 18*a, 54*a], self.mem.data.products.find_by_id(79228), Percentage(1, 3), Percentage(1, 10))
#        model.print()


    def actionsEnabled(self, bool):
        self.menuBar.setEnabled(bool)
        self.toolBar.setEnabled(bool)
        
    @pyqtSlot()
    def on_actionGlobalReport_triggered(self):
        file="AssetsReport.odt"
        doc=AssetsReport(self.mem, file, "/usr/share/xulpymoney/report.odt")
        doc.generate()
        
        
        #Open file
        if os.path.exists("/usr/bin/lowriter"):
            QProcess.startDetached("lowriter", [file, ] )
        elif os.path.exists("/usr/bin/kfmclient"):
            QProcess.startDetached("kfmclient", ["openURL", file] )
        elif os.path.exists("/usr/bin/gnome-open"):
            QProcess.startDetached( "gnome-open '" + file + "'" );
        else:         
            QDesktopServices.openUrl(QUrl("file://"+file));


    def inactivity_timeout(self):
        self.hide()
        qmessagebox(self.tr("Disconnecting due to {} minutes of inactivity.".format(self.mem.con.inactivity_timeout_minutes)))
        self.on_actionExit_triggered()


    @pyqtSlot()  
    def on_actionExit_triggered(self):
        self.mem.__del__()
        print ("App correctly closed")
        self.close()
        self.destroy()
        
    @pyqtSlot()
    def on_actionAbout_triggered(self):
        fr=frmAbout(self.mem, self, "frmabout")
        fr.open()

    @pyqtSlot()  
    def on_actionBanks_triggered(self):
        self.w.close()
        self.w=wdgBanks(self.mem, self)
                
        self.layout.addWidget(self.w)
        self.w.show()
        
    @pyqtSlot()  
    def on_actionCalculator_triggered(self):
        d=QDialog(self)        
        d.setFixedSize(850, 850)
        d.setWindowTitle(self.tr("Investment calculator"))
        w=wdgCalculator(self.mem, self)
        w.setProduct(self.mem.data.products.find_by_id(int(self.mem.settings.value("wdgCalculator/product", "0"))))
        lay = QVBoxLayout(d)
        lay.addWidget(w)
        if w.hasProducts==True:
            d.show()
        else:
            d.close()
        
    @pyqtSlot()  
    def on_actionConcepts_triggered(self):
        self.w.close()
        self.w=wdgConcepts(self.mem, self)
                
        self.layout.addWidget(self.w)
        self.w.show()
        
    @pyqtSlot()  
    def on_actionAccounts_triggered(self):
        self.w.close()
        self.w=wdgAccounts(self.mem, self)
                
        self.layout.addWidget(self.w)
        self.w.show()
    
    @pyqtSlot()  
    def on_actionMemory_triggered(self):        
        self.mem.data.load()
        
        
    @pyqtSlot()  
    def on_actionDividendsReport_triggered(self):
        self.w.close()
        self.w=wdgDividendsReport(self.mem, self)
                
        self.layout.addWidget(self.w)
        self.w.show()
        
    @pyqtSlot()  
    def on_actionInvestmentsClasses_triggered(self):
        self.w.close()
        self.w=wdgInvestmentClasses(self.mem, self)
                
        self.layout.addWidget(self.w)
        self.w.update()
        self.w.show()

    @pyqtSlot()  
    def on_actionTotalReport_triggered(self):
        self.w.close()
        self.w=wdgTotal(self.mem, self)
                
        self.layout.addWidget(self.w)
        self.w.show()

    @pyqtSlot()  
    def on_actionEvolutionReport_triggered(self):
        self.w.close()
        self.w=wdgAPR(self.mem, self)
              
        self.layout.addWidget(self.w)
        self.w.show()
        
    @pyqtSlot()  
    def on_actionHelp_triggered(self):
        w=frmHelp(self.mem, self)
        w.exec_()

    @pyqtSlot()  
    def on_actionIndexRange_triggered(self):
        self.w.close()
        self.w=wdgIndexRange(self.mem, self)
                
        self.layout.addWidget(self.w)
        self.w.show()


    @pyqtSlot()  
    def on_actionInvestments_triggered(self):
        self.w.close()
        self.w=wdgInvestments(self.mem, self)               
        self.layout.addWidget(self.w)
        self.w.show()
    @pyqtSlot()  
    def on_actionLastOperation_triggered(self):
        self.w.close()
        self.w=wdgLastCurrent(self.mem, self)               
        self.layout.addWidget(self.w)
        self.w.show()
        
    @pyqtSlot()  
    def on_actionInvestmentsOperations_triggered(self):
        self.w.close()
        self.w=wdgInvestmentsOperations(self.mem, self)
        self.layout.addWidget(self.w)
        self.w.show()

    @pyqtSlot()  
    def on_actionAuxiliarTables_triggered(self):
        w=frmAuxiliarTables(self.mem, self)
        w.exec_()
        
    @pyqtSlot()  
    def on_actionSettings_triggered(self):
        w=frmSettings(self.mem, self)
        w.exec_()
        self.retranslateUi(self)

    @pyqtSlot()  
    def on_actionTransfer_triggered(self):
        w=frmTransfer(self.mem, parent=self)
        w.exec_()
        self.on_actionAccounts_triggered()

    @pyqtSlot()  
    def on_actionCAC40_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where agrupations like '%|CAC|%' and obsolete=false order by name,id")

        self.layout.addWidget(self.w)
        self.w.show()                
    @pyqtSlot()  
    def on_actionActive_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where obsolete=false order by name")

        self.layout.addWidget(self.w)
        self.w.show()
    
    @pyqtSlot()  
    def on_actionCuriosities_triggered(self):
        self.w.close()
        self.w=wdgCuriosities(self.mem,  self)
        self.layout.addWidget(self.w)
        self.w.show()
    
    @pyqtSlot()  
    def on_actionCurrenciesAll_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where type=6 order by name,id")
        self.layout.addWidget(self.w)
        self.w.show()

    @pyqtSlot()  
    def on_actionDividends_triggered(self):
        """Shows products with current year estimations_dps and with quotes in current year"""
        self.w.close()
        self.w=wdgProducts(self.mem, "select * from products where id in (select id from estimations_dps where year=date_part('year',now()) and estimation is not null) and id in (select distinct(id) from quotes where date_part('year', datetime)=date_part('year',now()));")
        self.layout.addWidget(self.w)
        self.w.on_actionSortDividend_triggered()
        self.w.show()

    @pyqtSlot()  
    def on_actionInvestmentRanking_triggered(self):
        self.w.close()
        self.w=wdgInvestmentsRanking(self.mem, self)
        self.layout.addWidget(self.w)
        self.w.show()
    
    @pyqtSlot()  
    def on_actionSimulations_triggered(self):
        d=QDialog(self)
        d.resize(self.mem.settings.value("wdgSimulations/qdialog", QSize(1024, 768)))
        d.setWindowTitle(self.tr("Xulpymoney Simulations"))
        w=wdgSimulations(self.mem, d)
        lay = QVBoxLayout(d)
        lay.addWidget(w)
        d.exec_() 
        self.mem.settings.setValue("wdgSimulations/qdialog", d.size())

    @pyqtSlot()  
    def on_actionSyncProducts_triggered(self):
        self.w.hide()
        
        source=frmAccess(self.mem,  self)
        source.showLanguage(False)
        source.setLabel(self.tr("Please login to the source xulpymoney database"))
        source.txtPort.setText(self.mem.settings.value("frmMain/syncproducts_port", "5432"))
        source.txtServer.setText(self.mem.settings.value("frmMain/syncproducts_server", "127.0.0.1"))
        source.txtUser.setText(self.mem.settings.value("frmMain/syncproducts_user", "postgres"))
        source.txtDB.setText(self.mem.settings.value("frmMain/syncproducts_db", ""))
        source.txtPass.setFocus()
        source.exec_()
        if source.result()==QDialog.Rejected:             
            qmessagebox(self.tr("Error conecting to {} database in {} server").format(source.con.db, source.con.server))
            return
        else:
            if source.con.db.strip()==self.mem.con.db.strip() and source.con.server.strip()==self.mem.con.server.strip() and source.con.port==self.mem.con.port:
                m=QMessageBox()
                m.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
                m.setIcon(QMessageBox.Information)
                m.setText(self.tr("Databases can't be the same"))
                m.exec_()   
                return

            self.mem.settings.setValue("frmMain/syncproducts_port", source.txtPort.text())
            self.mem.settings.setValue("frmMain/syncproducts_server", source.txtServer.text())
            self.mem.settings.setValue("frmMain/syncproducts_user", source.txtUser.text())
            self.mem.settings.setValue("frmMain/syncproducts_db", source.txtDB.text())
                
            pd= QProgressDialog(QApplication.translate("Core","Syncing databases from {} ({}) to {} ({})").format(source.txtServer.text(), source.txtDB.text(), self.mem.con.server, self.mem.con.db), None, 0, 10)
            pd.setModal(True)
            pd.setWindowTitle(QApplication.translate("Core","Processing products..."))
            pd.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
            pd.forceShow()
            
            sync_data(source.con, self.mem.con, pd)
            
            self.mem.data.load()

    @pyqtSlot()  
    def on_actionNasdaq100_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where agrupations like '%|NASDAQ100|%' and obsolete=false  order by name,id")

        self.layout.addWidget(self.w)
        self.w.show()
            
    @pyqtSlot()  
    def on_actionISINDuplicado_triggered(self):
        self.w.close()
        cur=self.mem.con.cursor()
        #ßaca los isin duplicados buscando distintct isin, bolsa con mas de dos registros
        cur.execute("select isin, stockmarkets_id, count(*) as num from products  where isin!='' group by isin, stockmarkets_id having count(*)>1 order by num desc;")
        isins=set([])
        for row in cur:
            isins.add(row['isin'] )
        if len(isins)>0:
            self.w=wdgProducts(self.mem,  "select * from products where isin in ("+list2string(list(isins))+") order by isin, stockmarkets_id")
        else:
            self.w=wdgProducts(self.mem, self.sqlvacio)

        self.layout.addWidget(self.w)
        self.w.show()
        
    @pyqtSlot()  
    def on_actionMC_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem, "select * from products where agrupations like '%|MERCADOCONTINUO|%' and obsolete=false  order by name,id")

        self.layout.addWidget(self.w)
        self.w.show()
        

    @pyqtSlot()  
    def on_actionETFAll_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where type=4 and obsolete=false order by name, id")

        self.layout.addWidget(self.w)
        self.w.show()
        
    @pyqtSlot()  
    def on_actionETFObsolete_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where type=4 and obsolete=true order by name, id")

        self.layout.addWidget(self.w)
        self.w.show()
        
    @pyqtSlot()  
    def on_actionEurostoxx50_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where agrupations like '%|EUROSTOXX|%'  and obsolete=false order by name,id")

        self.layout.addWidget(self.w)
        self.w.show()
        

    @pyqtSlot()  
    def on_actionFavorites_triggered(self):
        if len(self.mem.favorites)==0:
            m=QMessageBox()
            m.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
            m.setIcon(QMessageBox.Information)
            m.setText(self.tr("There aren't favorite products"))
            m.exec_()     
            return
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where id in ("+list2string(self.mem.favorites)+") order by name, id")
        self.w.showingfavorites=True

        self.layout.addWidget(self.w)
        self.w.show()

    @pyqtSlot()  
    def on_actionSharesAll_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where type=1 and obsolete=false order by name, id")

        self.layout.addWidget(self.w)
        self.w.show()         
        
    @pyqtSlot()  
    def on_actionSharesObsolete_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where type=1  and obsolete=true order by name, id")

        self.layout.addWidget(self.w)
        self.w.show()        
        
    @pyqtSlot()  
    def on_actionWarrantsAll_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where type=5 and obsolete=false order by name, id")

        self.layout.addWidget(self.w)
        self.w.show()          
        
    @pyqtSlot()  
    def on_actionWarrantsObsolete_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where type=5 and obsolete=true order by name, id")

        self.layout.addWidget(self.w)
        self.w.show()          
        
    @pyqtSlot()  
    def on_actionWarrantsCall_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where type=5 and pci='c'  and obsolete=false order by name, id")

        self.layout.addWidget(self.w)
        self.w.show()              
    @pyqtSlot()  
    def on_actionWarrantsPut_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where type=5 and pci='p'  and obsolete=false order by name, id")

        self.layout.addWidget(self.w)
        self.w.show()              
    @pyqtSlot()  
    def on_actionWarrantsInline_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where type=5 and pci='i'  and obsolete=false order by name, id")

        self.layout.addWidget(self.w)
        self.w.show()      

    @pyqtSlot()  
    def on_actionFundsAll_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where type=2 and obsolete=false order by name, id")

        self.layout.addWidget(self.w)
        self.w.show()        
        
    @pyqtSlot()  
    def on_actionFundsObsolete_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where type=2 and obsolete=true order by name, id")

        self.layout.addWidget(self.w)
        self.w.show()                        

    @pyqtSlot()  
    def on_actionBondsPublic_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where type=7 and obsolete=false order by name, id")

        self.layout.addWidget(self.w)
        self.w.show()                        

    @pyqtSlot()  
    def on_actionBondsPrivate_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where type=9 and obsolete=false order by name, id")

        self.layout.addWidget(self.w)
        self.w.show()

    @pyqtSlot()  
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
        pd.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
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
        m.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
        m.setIcon(QMessageBox.Information)
        m.setText(self.tr("{0} quotes have been purged from {1} products".format(counter, len(products))))
        m.exec_()    
        
    @pyqtSlot()  
    def on_actionBondsAll_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where type in (7,9) and obsolete=false order by name, id")

        self.layout.addWidget(self.w)
        self.w.show()
        
    @pyqtSlot()  
    def on_actionBondsObsolete_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where type in (7,9) and obsolete=true order by name, id")

        self.layout.addWidget(self.w)
        self.w.show()

    @pyqtSlot()  
    def on_actionIbex35_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select  * from products where agrupations like '%|IBEX|%' and obsolete=false  order by name,id")
        self.layout.addWidget(self.w)
        self.w.show()        

    @pyqtSlot()  
    def on_actionLATIBEX_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select  * from products where agrupations like '%|LATIBEX|%' and obsolete=false order by name,id")
        self.layout.addWidget(self.w)
        self.w.show()
        
    @pyqtSlot()  
    def on_actionIndexesAll_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select  * from products where type=3 and obsolete=False order by stockmarkets_id,name")
        self.layout.addWidget(self.w)
        self.w.show()      
        
    @pyqtSlot()  
    def on_actionIndexesObsolete_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select  * from products where type=3 and obsolete=true order by stockmarkets_id,name")
        self.layout.addWidget(self.w)
        self.w.show()        
                
    @pyqtSlot()  
    def on_actionSP500_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where agrupations like '%|SP500|%'  and obsolete=false order by name,id")

        self.layout.addWidget(self.w)
        self.w.show()
    
    @pyqtSlot()  
    def on_actionProductsInvestmentActive_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where id in (select products_id from inversiones where active=true) order by name")

        self.layout.addWidget(self.w)
        self.w.show()        
    @pyqtSlot()  
    def on_actionProductsWithoutQuotes_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select p.*,q.* from products p, quote(p.id, now()) q where p.id=q.id and q.quote is null and obsolete=False order by name")

        self.layout.addWidget(self.w)
        self.w.show()        
    @pyqtSlot()  
    def on_actionProductsWithOldPrice_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select p.* from products p, quote(p.id, now()) q where p.id=q.id and q.datetime<now() -interval '30 day' and obsolete=False order by name")
        self.layout.addWidget(self.w)
        self.w.show()    
        
    @pyqtSlot()  
    def on_actionProductsInvestmentInactive_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where id in (select products_id from inversiones where active=false) order by name")

        self.layout.addWidget(self.w)
        self.w.show()    
    @pyqtSlot()  
    def on_actionProductsObsolete_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where obsolete=true order by name,id")

        self.layout.addWidget(self.w)
        self.w.show()
                
    @pyqtSlot()  
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
    
    @pyqtSlot()  
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
        
    @pyqtSlot()  
    def on_actionProductsUser_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where id<0 order by name, id ")

        self.layout.addWidget(self.w)
        self.w.show()
        
    @pyqtSlot()  
    def on_actionProductsWithoutISIN_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products  where obsolete=false and (isin is null or isin ='') order by name,id")

        self.layout.addWidget(self.w)
        self.w.show()

    @pyqtSlot()  
    def on_actionTablasAuxiliares_triggered(self):
        w=frmAuxiliarTables(self.mem, self)
        w.tblTipos_reload()
        w.exec_()

                
    @pyqtSlot()  
    def on_actionXetra_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where agrupations like '%|DAX|%'  and obsolete=false order by name,id")

        self.layout.addWidget(self.w)
        self.w.show()        
        
    @pyqtSlot()  
    def on_actionSearch_triggered(self):
        self.w.close()
        self.w=wdgProducts(self.mem,  self.sqlvacio)

        self.layout.addWidget(self.w)
        self.w.show()
        
    @pyqtSlot()  
    def on_actionOrders_triggered(self):  
        self.w.close()
        self.w=wdgOrders(self.mem, self)
        self.layout.addWidget(self.w)


    @pyqtSlot()  
    def on_actionPriceUpdates_triggered(self):  
        self.w.close()
        self.w=wdgQuotesUpdate(self.mem, self)
        self.layout.addWidget(self.w)

        
    @pyqtSlot()  
    def on_actionPriceUpdatesNew_triggered(self):          
        arr=[]
        sql="select * from products where type in (1,4) and obsolete=false and stockmarkets_id=1 and isin is not null and isin<>'' order by name"
        products=SetProducts(self.mem)#Total of products of an Agrupation
        products.load_from_db(sql)    
        for p in products.arr:
            if p.type.id==4:
                arr.append(["xulpymoney_bolsamadrid_client","--ISIN",  p.isin, "--etf","--fromdate", str( p.fecha_ultima_actualizacion_historica()), "--XULPYMONEY", str(p.id)])
            elif p.type.id==1:
                arr.append(["xulpymoney_bolsamadrid_client","--ISIN",  p.isin, "--share","--fromdate", str( p.fecha_ultima_actualizacion_historica()), "--XULPYMONEY", str(p.id)])
                

        sql="select * from products where priorityhistorical[1]=8 and obsolete=false and ticker is not null order by name"
        products_morningstar=SetProducts(self.mem)#Total of products_morningstar of an Agrupation
        products_morningstar.load_from_db(sql)    
        for p in products_morningstar.arr:
            arr.append(["xulpymoney_morningstar_client","--TICKER",  p.ticker])       
                
        f=open("/tmp/clients.txt", "w")
        for a in arr:
            f.write(" ".join(a) + "\n")
        f.close()
