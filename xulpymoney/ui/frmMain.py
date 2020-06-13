## @namesapace xulpymoney.ui.frmMain
## @brief User interface main window.

from PyQt5.QtCore import pyqtSlot, QProcess, QUrl
from PyQt5.QtGui import QIcon, QDesktopServices
from PyQt5.QtWidgets import QMainWindow,  QWidget, QLabel, QMessageBox, QProgressDialog, QDialog,  QApplication, QFileDialog
from os import environ, path
from datetime import datetime
from logging import info
from sys import exit
from stdnum.isin import is_valid
from xulpymoney.ui.Ui_frmMain import Ui_frmMain
from xulpymoney.objects.product import Product, ProductManager
from xulpymoney.casts import list2string
from xulpymoney.datetime_functions import dtnaive2string
from xulpymoney.ui.myqwidgets import qmessagebox
from xulpymoney.ui.myqdialog import MyNonModalQDialog, MyModalQDialog
from xulpymoney.libxulpymoneytypes import eProductType
from xulpymoney.version import __versiondate__
from xulpymoney.ui.myqlineedit import myQLineEdit

class frmMain(QMainWindow, Ui_frmMain):
    def __init__(self, mem, parent = 0,  flags = False):
        QMainWindow.__init__(self, None)
        self.setupUi(self)
        self.showMaximized()
        
        self.mem=mem
        self.mem.con.inactivity_timeout.connect(self.inactivity_timeout)        
        
        self.w=QWidget()       
        self.statusBar.addWidget(QLabel(self.mem.con.url_string()))
   
  
        if self.mem.con.is_superuser():
            self.setWindowTitle(self.tr("Xulpymoney 2010-{0} \xa9 (Admin mode)").format(__versiondate__.year))#print ("Xulpymoney 2010-{0} © €".encode('unicode-escape'))
            self.setWindowIcon(self.mem.qicon_admin())
        else:
            self.setWindowTitle(self.tr("Xulpymoney 2010-{0} \xa9").format(__versiondate__.year))
            self.actionDocumentsPurge.setEnabled(False)

    def actionsEnabled(self, bool):
        self.menuBar.setEnabled(bool)
        self.toolBar.setEnabled(bool)
        
    @pyqtSlot()
    def on_actionGlobalReport_triggered(self):
        from xulpymoney.objects.assetsreport import AssetsReport
        file="{} AssetsReport.odt".format(dtnaive2string(datetime.now(), "%Y%m%d %H%M"))
        doc=AssetsReport(self.mem, file)
        doc.generate()
        
        
        #Open file
        if path.exists("/usr/bin/lowriter"):
            QProcess.startDetached("lowriter", [file, ] )
        elif path.exists("/usr/bin/kfmclient"):
            QProcess.startDetached("kfmclient", ["openURL", file] )
        elif path.exists("/usr/bin/gnome-open"):
            QProcess.startDetached( "gnome-open '" + file + "'" );
        else:         
            QDesktopServices.openUrl(QUrl("file://"+file));


    @pyqtSlot()
    def closeEvent(self, event):
        event.accept()
        self.on_actionExit_triggered()
        
    def inactivity_timeout(self):
        self.hide()
        qmessagebox(self.tr("Disconnecting due to {} minutes of inactivity.".format(self.mem.con.connectionTimeout()/60)))
        self.on_actionExit_triggered()


    @pyqtSlot()  
    def on_actionExit_triggered(self):
        info("App correctly closed")
        exit(0)
        
    @pyqtSlot()
    def on_actionAbout_triggered(self):
        from xulpymoney.ui.frmAbout import frmAbout
        fr=frmAbout(self.mem)
        fr.exec_()

    @pyqtSlot()  
    def on_actionBanks_triggered(self):
        from xulpymoney.ui.wdgBanks import wdgBanks
        self.w.close()
        self.w=wdgBanks(self.mem, self)
                
        self.layout.addWidget(self.w)
        self.w.show()
        
    @pyqtSlot()  
    def on_actionCalculator_triggered(self):
        from xulpymoney.ui.wdgCalculator import wdgCalculator
        d=MyNonModalQDialog(self)
        d.setSettings(self.mem.settings, "frmMain", "wdgCalculator", 850, 850)
        d.setWindowTitle(self.tr("Investment calculator"))
        w=wdgCalculator(self.mem, self)
        w.setProduct(self.mem.data.products.find_by_id(int(self.mem.settings.value("wdgCalculator/product", "0"))))
        d.setWidgets(w)
        d.show()
        
    @pyqtSlot()  
    def on_actionConcepts_triggered(self):
        from xulpymoney.ui.wdgConcepts import wdgConcepts
        self.w.close()
        self.w=wdgConcepts(self.mem, self)
                
        self.layout.addWidget(self.w)
        self.w.show()
        
    @pyqtSlot()  
    def on_actionAccounts_triggered(self):
        from xulpymoney.ui.wdgAccounts import wdgAccounts
        self.w.close()
        self.w=wdgAccounts(self.mem, self)
                
        self.layout.addWidget(self.w)
        self.w.show()
    
    @pyqtSlot()  
    def on_actionMemory_triggered(self):        
        self.mem.settings.sync()
        self.mem.load_db_data()

    @pyqtSlot()
    def on_actionDerivativesReport_triggered(self):
        from xulpymoney.ui.wdgDerivativesReport import wdgDerivativesReport
        self.w.close()
        self.w=wdgDerivativesReport(self.mem, self)
        self.layout.addWidget(self.w)
        self.w.show()

    @pyqtSlot()
    def on_actionDividendsReport_triggered(self):
        from xulpymoney.ui.wdgDividendsReport import wdgDividendsReport
        self.w.close()
        self.w=wdgDividendsReport(self.mem, self)
                
        self.layout.addWidget(self.w)
        self.w.show()
        
    @pyqtSlot()  
    def on_actionInvestmentsClasses_triggered(self):
        from xulpymoney.ui.wdgInvestmentClasses import wdgInvestmentClasses
        self.w.close()
        self.w=wdgInvestmentClasses(self.mem, self)
        self.layout.addWidget(self.w)
        self.w.update(animations=True)
        self.w.show()

    @pyqtSlot()  
    def on_actionTotalReport_triggered(self):
        from xulpymoney.ui.wdgTotal import wdgTotal
        self.w.close()
        self.w=wdgTotal(self.mem, self)
                
        self.layout.addWidget(self.w)
        self.w.show()

    @pyqtSlot()  
    def on_actionEvolutionReport_triggered(self):
        from xulpymoney.ui.wdgAPR import wdgAPR
        self.w.close()
        self.w=wdgAPR(self.mem, self)
              
        self.layout.addWidget(self.w)
        self.w.show()
        
    @pyqtSlot()  
    def on_actionHelp_triggered(self):
        def in_external():
            QDesktopServices.openUrl(QUrl(self.mem.url_wiki))

        try:
            user=environ['USER']
        except:
            user=None

        try: ## Remove when qwebwenginewidgets work again
            from xulpymoney.ui.frmHelp import frmHelp

            if user!=None and user=="root":
                in_external()
            else:
                w=frmHelp(self.mem, self)
                w.show()
        except:
            in_external()

    @pyqtSlot()  
    def on_actionIndexRange_triggered(self):
        from xulpymoney.ui.wdgIndexRange import wdgIndexRange
        if self.mem.data.benchmark.result.ohclDaily.length()==0:
            qmessagebox(self.tr("There isn't any benchmark data yet."))
            return
        
        self.w.close()
        self.w=wdgIndexRange(self.mem, self)
                
        self.layout.addWidget(self.w)
        self.w.show()

    @pyqtSlot()  
    def on_actionProductRange_triggered(self):
        from xulpymoney.ui.wdgProductRange import wdgProductRange
        self.w.close()
        self.w=wdgProductRange(self.mem, self)
                
        self.layout.addWidget(self.w)
        self.w.show()

    @pyqtSlot()  
    def on_actionInvestments_triggered(self):
        from xulpymoney.ui.wdgInvestments import wdgInvestments
        self.w.close()
        self.w=wdgInvestments(self.mem, self)               
        self.layout.addWidget(self.w)
        self.w.show()

    @pyqtSlot()
    def on_actionInvestmentsZeroRisk_triggered(self):
        from xulpymoney.ui.wdgInvestments import wdgInvestmentsZeroRisk
        self.w.close()
        self.w=wdgInvestmentsZeroRisk(self.mem, self)
        self.layout.addWidget(self.w)
        self.w.show()

    @pyqtSlot()  
    def on_actionLastOperation_triggered(self):
        from xulpymoney.ui.wdgLastCurrent import wdgLastCurrent
        self.w.close()
        self.w=wdgLastCurrent(self.mem, self)               
        self.layout.addWidget(self.w)
        self.w.show()

    @pyqtSlot()  
    def on_actionInvestmentsOperations_triggered(self):
        from xulpymoney.ui.wdgInvestmentsOperations import wdgInvestmentsOperations
        self.w.close()
        self.w=wdgInvestmentsOperations(self.mem, self)
        self.layout.addWidget(self.w)
        self.w.show()

    @pyqtSlot()  
    def on_actionAuxiliarTables_triggered(self):
        from xulpymoney.ui.frmAuxiliarTables import frmAuxiliarTables
        w=frmAuxiliarTables(self.mem, self)
        w.exec_()
        
    @pyqtSlot()  
    def on_actionSettings_triggered(self):
        from xulpymoney.ui.frmSettings import frmSettings
        w=frmSettings(self.mem, self)
        w.exec_()
        self.retranslateUi(self)

    @pyqtSlot()  
    def on_actionTransfer_triggered(self):
        from xulpymoney.ui.frmTransfer import frmTransfer
        w=frmTransfer(self.mem, parent=self)
        w.exec_()
        self.on_actionAccounts_triggered()

    @pyqtSlot()  
    def on_actionCAC40_triggered(self):
        from xulpymoney.ui.wdgProducts import wdgProducts
        self.w.close()
        arrInt=[]
        for p in self.mem.data.products.arr:
            if p.agrupations.dbstring().find("|CAC|")!=-1 and p.obsolete==False:
                arrInt.append(p.id)
        self.w=wdgProducts(self.mem,  arrInt)
        self.layout.addWidget(self.w)
        self.w.show()
        
    @pyqtSlot()  
    def on_actionActive_triggered(self):
        from xulpymoney.ui.wdgProducts import wdgProducts
        self.w.close()
        self.w=wdgProducts(self.mem,  "select * from products where obsolete=false order by name")

        self.layout.addWidget(self.w)
        self.w.show()
    
    @pyqtSlot()  
    def on_actionCuriosities_triggered(self):
        from xulpymoney.ui.wdgCuriosities import wdgCuriosities
        self.w.close()
        self.w=wdgCuriosities(self.mem,  self)
        self.layout.addWidget(self.w)
        self.w.show()
    
    @pyqtSlot()  
    def on_actionCurrenciesAll_triggered(self):
        from xulpymoney.ui.wdgProducts import wdgProducts
        self.w.close()
        arrInt=[]
        for p in self.mem.data.products.arr:
            if p.type.id==eProductType.Currency and p.obsolete==False:
                arrInt.append(p.id)
            
        self.w=wdgProducts(self.mem,  arrInt)
        self.layout.addWidget(self.w)
        self.w.show()

    @pyqtSlot()  
    def on_actionDividends_triggered(self):
        """Shows products with current year estimations_dps and with quotes in current year"""
        from xulpymoney.ui.wdgProducts import wdgProducts
        self.w.close()
        prod=ProductManager(self.mem)
        prod.load_from_db("select * from products where id in (select id from estimations_dps where year=date_part('year',now()) and estimation is not null) and id in (select distinct(id) from quotes where date_part('year', datetime)=date_part('year',now()))")
        self.w=wdgProducts(self.mem,  prod.array_of_ids())
        self.layout.addWidget(self.w)
        self.w.on_actionSortDividend_triggered()
        self.w.show()

    @pyqtSlot()  
    def on_actionInvestmentRanking_triggered(self):
        from xulpymoney.ui.wdgInvestmentsRanking import wdgInvestmentsRanking
        self.w.close()
        self.w=wdgInvestmentsRanking(self.mem, self)
        self.layout.addWidget(self.w)
        self.w.show()
        
    @pyqtSlot()  
    def on_actionShowBenchmark_triggered(self):
        from xulpymoney.ui.frmProductReport import frmProductReport
        self.w.close()
        self.w=frmProductReport(self.mem, self.mem.data.benchmark)
        self.layout.addWidget(self.w)
        self.w.show()
    
    @pyqtSlot()  
    def on_actionSimulations_triggered(self):
        from xulpymoney.ui.wdgSimulations import wdgSimulations
        d=MyModalQDialog(self)
        d.setSettings(self.mem.settings, "wdgSimulations", "mqdSimulations")
        d.setWindowTitle(self.tr("Xulpymoney Simulations"))
        d.setWidgets(wdgSimulations(self.mem, d))
        d.exec_()

    
    @pyqtSlot()  
    def on_actionStrategyResults_triggered(self):
        self.w.close()
        from xulpymoney.ui.wdgStrategyResults import wdgStrategyResults
        self.w=wdgStrategyResults(self.mem, self)
        self.layout.addWidget(self.w)
        self.w.show()


    @pyqtSlot()  
    def on_actionSyncProducts_triggered(self):
        from xulpymoney.libxulpymoneyfunctions import sync_data
        from xulpymoney.ui.frmAccess import frmAccess   
        self.w.hide()
        
        source=frmAccess("xulpymoney", "frmSync", self.mem.frmAccess.settings, self)
        source.setResources(":/xulpymoney/database.png", ":/xulpymoney/database.png")
        source.setLanguagesVisible(False)
        source.setLabel(self.tr("Please login to the source xulpymoney database"))
        source.exec_()
        if source.result()==QDialog.Rejected:             
            qmessagebox(self.tr("Error conecting to {} database in {} server").format(source.con.db, source.con.server))
            return
        else:
            if source.con.db.strip()==self.mem.con.db.strip() and source.con.server.strip()==self.mem.con.server.strip() and source.con.port==self.mem.con.port:
                qmessagebox(self.tr("Databases can't be the same"))
                return
                
            pd= QProgressDialog(QApplication.translate("Mem","Syncing databases from {} ({}) to {} ({})").format(source.txtServer.text(), source.txtDB.text(), self.mem.con.server, self.mem.con.db), None, 0, 10)
            pd.setModal(True)
            pd.setWindowTitle(QApplication.translate("Mem","Processing products..."))
            pd.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
            pd.forceShow()
            
            sync_data(source.con, self.mem.con, pd)
            
            self.mem.data.load()

    @pyqtSlot()  
    def on_actionNasdaq100_triggered(self):
        from xulpymoney.ui.wdgProducts import wdgProducts
        self.w.close()

        arrInt=[]
        for p in self.mem.data.products.arr:
            if p.agrupations.dbstring().find("|NASDAQ100|")!=-1 and p.obsolete==False:
                arrInt.append(p.id)
        self.w=wdgProducts(self.mem,  arrInt)
        self.layout.addWidget(self.w)
        self.w.show()
            
    @pyqtSlot()  
    def on_actionISINDuplicado_triggered(self):
        from xulpymoney.ui.wdgProducts import wdgProducts
        self.w.close()
        cur=self.mem.con.cursor()
        
        
        #ßaca los isin duplicados buscando distintct isin, bolsa con mas de dos registros
        cur.execute("select isin, stockmarkets_id, count(*) as num from products  where isin!='' group by isin, stockmarkets_id having count(*)>1 order by num desc;")
        isins=set([])
        for row in cur:
            isins.add(row['isin'] )
        arrInt=[]
        if len(isins)>0:
            for p in self.mem.data.products.arr:
                if p.isin in isins:
                    arrInt.append(p.id)
        self.w=wdgProducts(self.mem,  arrInt)
        self.layout.addWidget(self.w)
        self.w.show()
        
    @pyqtSlot()  
    def on_actionMC_triggered(self):
        from xulpymoney.ui.wdgProducts import wdgProducts
        self.w.close()
        arrInt=[]
        for p in self.mem.data.products.arr:
            if p.agrupations.dbstring().find("|MERCADOCONTINUO|")!=-1 and p.obsolete==False:
                arrInt.append(p.id)
        self.w=wdgProducts(self.mem,  arrInt)
        self.layout.addWidget(self.w)
        self.w.show()
        

    @pyqtSlot()  
    def on_actionETFAll_triggered(self):
        from xulpymoney.ui.wdgProducts import wdgProducts
        self.w.close()
        arrInt=[]
        for p in self.mem.data.products.arr:
            if p.type.id==eProductType.ETF and p.obsolete==False:
                arrInt.append(p.id)
        self.w=wdgProducts(self.mem,  arrInt)
        self.layout.addWidget(self.w)
        self.w.show()
        
    @pyqtSlot()  
    def on_actionETFObsolete_triggered(self):
        from xulpymoney.ui.wdgProducts import wdgProducts
        self.w.close()
        arrInt=[]
        for p in self.mem.data.products.arr:
            if p.type.id==eProductType.ETF and p.obsolete==True:
                arrInt.append(p.id)
        self.w=wdgProducts(self.mem,  arrInt)
        self.layout.addWidget(self.w)
        self.w.show()
        
    @pyqtSlot()  
    def on_actionEurostoxx50_triggered(self):
        from xulpymoney.ui.wdgProducts import wdgProducts
        self.w.close()
        arrInt=[]
        for p in self.mem.data.products.arr:
            if p.agrupations.dbstring().find("|EUROSTOXX|")!=-1 and p.obsolete==False:
                arrInt.append(p.id)
        self.w=wdgProducts(self.mem,  arrInt)
        self.layout.addWidget(self.w)
        self.w.show()
        

    @pyqtSlot()  
    def on_actionFavorites_triggered(self):
        from xulpymoney.ui.wdgProducts import wdgProducts
        favorites=self.mem.settingsdb.value_list_of_integers("mem/favorites", "")
        if len(favorites)==0:
            qmessagebox(self.tr("There aren't favorite products"))
            return
        self.w.close()
        self.w=wdgProducts(self.mem, favorites)
        self.layout.addWidget(self.w)
        self.w.show()


    @pyqtSlot()  
    def on_actionReportIssue_triggered(self):        
            QDesktopServices.openUrl(QUrl("https://github.com/turulomio/xulpymoney/issues/new"))

    @pyqtSlot()  
    def on_actionSharesAll_triggered(self):
        from xulpymoney.ui.wdgProducts import wdgProducts
        self.w.close()
        arrInt=[]
        for p in self.mem.data.products.arr:
            if p.type.id==eProductType.Share and p.obsolete==False:
                arrInt.append(p.id)
        self.w=wdgProducts(self.mem,  arrInt)
        self.layout.addWidget(self.w)
        self.w.show()         
        
    @pyqtSlot()  
    def on_actionSharesObsolete_triggered(self):
        from xulpymoney.ui.wdgProducts import wdgProducts
        self.w.close()
        arrInt=[]
        for p in self.mem.data.products.arr:
            if p.type.id==eProductType.Share and p.obsolete==True:
                arrInt.append(p.id)
        self.w=wdgProducts(self.mem,  arrInt)
        self.layout.addWidget(self.w)
        self.w.show()        
        
    @pyqtSlot()  
    def on_actionWarrantsAll_triggered(self):
        from xulpymoney.ui.wdgProducts import wdgProducts
        self.w.close()
        arrInt=[]
        for p in self.mem.data.products.arr:
            if p.type.id==eProductType.Warrant and p.obsolete==False:
                arrInt.append(p.id)
        self.w=wdgProducts(self.mem,  arrInt)
        self.layout.addWidget(self.w)
        self.w.show()          
        
    @pyqtSlot()  
    def on_actionWarrantsObsolete_triggered(self):
        from xulpymoney.ui.wdgProducts import wdgProducts
        self.w.close()
        arrInt=[]
        for p in self.mem.data.products.arr:
            if p.type.id==eProductType.Warrant and p.obsolete==True:
                arrInt.append(p.id)
        self.w=wdgProducts(self.mem,  arrInt)
        self.layout.addWidget(self.w)
        self.w.show()          
        
    @pyqtSlot()  
    def on_actionWarrantsCall_triggered(self):
        from xulpymoney.ui.wdgProducts import wdgProducts
        self.w.close()
        arrInt=[]
        for p in self.mem.data.products.arr:
            if p.type.id==eProductType.Warrant and p.mode.id=='c' and p.obsolete==False:
                arrInt.append(p.id)
        self.w=wdgProducts(self.mem,  arrInt)
        self.layout.addWidget(self.w)
        self.w.show()

    @pyqtSlot()  
    def on_actionWarrantsPut_triggered(self):
        from xulpymoney.ui.wdgProducts import wdgProducts
        self.w.close()
        arrInt=[]
        for p in self.mem.data.products.arr:
            if p.type.id==eProductType.Warrant and p.mode.id=='p' and p.obsolete==False:
                arrInt.append(p.id)
        self.w=wdgProducts(self.mem,  arrInt)
        self.layout.addWidget(self.w)
        self.w.show()              
        
    @pyqtSlot()  
    def on_actionWarrantsInline_triggered(self):
        from xulpymoney.ui.wdgProducts import wdgProducts
        self.w.close()
        arrInt=[]
        for p in self.mem.data.products.arr:
            if p.type.id==eProductType.Warrant and p.mode.id=='i' and p.obsolete==False:
                arrInt.append(p.id)
        self.w=wdgProducts(self.mem,  arrInt)
        self.layout.addWidget(self.w)
        self.w.show()      

    @pyqtSlot()  
    def on_actionFundsAll_triggered(self):
        from xulpymoney.ui.wdgProducts import wdgProducts
        self.w.close()
        arrInt=[]
        for p in self.mem.data.products.arr:
            if p.type.id==eProductType.Fund and p.obsolete==False:
                arrInt.append(p.id)
        self.w=wdgProducts(self.mem,  arrInt)
        self.layout.addWidget(self.w)
        self.w.show()        
        
    @pyqtSlot()  
    def on_actionFundsObsolete_triggered(self):
        from xulpymoney.ui.wdgProducts import wdgProducts
        self.w.close()
        arrInt=[]
        for p in self.mem.data.products.arr:
            if p.type.id==eProductType.Fund and p.obsolete==True:
                arrInt.append(p.id)
        self.w=wdgProducts(self.mem,  arrInt)
        self.layout.addWidget(self.w)
        self.w.show()                        

    @pyqtSlot()  
    def on_actionBondsPublic_triggered(self):
        from xulpymoney.ui.wdgProducts import wdgProducts
        self.w.close()
        arrInt=[]
        for p in self.mem.data.products.arr:
            if p.type.id==eProductType.PublicBond and p.obsolete==False:
                arrInt.append(p.id)
            
        self.w=wdgProducts(self.mem,  arrInt)
        self.layout.addWidget(self.w)
        self.w.show()                        

    @pyqtSlot()  
    def on_actionBondsPrivate_triggered(self):
        from xulpymoney.ui.wdgProducts import wdgProducts
        self.w.close()
        arrInt=[]
        for p in self.mem.data.products.arr:
            if p.type.id==eProductType.PrivateBond and p.obsolete==False:
                arrInt.append(p.id)
            
        self.w=wdgProducts(self.mem,  arrInt)
        self.layout.addWidget(self.w)
        self.w.show()

    @pyqtSlot()  
    def on_actionPurchaseOpportunities_triggered(self):
        from xulpymoney.ui.wdgOpportunities import wdgOpportunities
        self.w.close()
        self.w=wdgOpportunities(self.mem, self)
        self.layout.addWidget(self.w)
        
    @pyqtSlot()  
    def on_actionPurgeAll_triggered(self):
        """Purga todas las quotes de todas inversión. """
        products=[]
        curms=self.mem.con.cursor()
        curms.execute("select * from products where id in ( select distinct( id) from quotes) order by name;")
        for row in curms:
            products.append(Product(self.mem).init__db_row(row))
        curms.close()
               
        
        pd= QProgressDialog(QApplication.translate("Mem","Purging innecesary data from all products"), QApplication.translate("Mem","Cancel"), 0,len(products))
        pd.setModal(True)
        pd.setWindowTitle(QApplication.translate("Mem","Purging quotes from all products"))
        pd.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
        pd.setMinimumDuration(0)          
        counter=0      
        
        for i, inv in enumerate(products):
            pd.setValue(i)
            pd.setLabelText(QApplication.translate("Mem","Purging quotes from {0}.\nTotal purged in global process: {1}").format(inv.name,  counter))
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
        
        qmessagebox(self.tr("{0} quotes have been purged from {1} products".format(counter, len(products))))

    @pyqtSlot()  
    def on_actionBondsAll_triggered(self):
        from xulpymoney.ui.wdgProducts import wdgProducts
        self.w.close()
        arrInt=[]
        for p in self.mem.data.products.arr:
            if p.type.id in (eProductType.PrivateBond,  eProductType.PublicBond) and p.obsolete==False:
                arrInt.append(p.id)
            
        self.w=wdgProducts(self.mem,  arrInt)

        self.layout.addWidget(self.w)
        self.w.show()
        
    @pyqtSlot()  
    def on_actionBondsObsolete_triggered(self):
        from xulpymoney.ui.wdgProducts import wdgProducts
        self.w.close()
        arrInt=[]
        for p in self.mem.data.products.arr:
            if p.type.id in (eProductType.PrivateBond,  eProductType.PublicBond) and p.obsolete==True:
                arrInt.append(p.id)
            
        self.w=wdgProducts(self.mem,  arrInt)
        self.layout.addWidget(self.w)
        self.w.show()

    @pyqtSlot()  
    def on_actionIbex35_triggered(self):
        from xulpymoney.ui.wdgProducts import wdgProducts
        self.w.close()
        arrInt=[]
        for p in self.mem.data.products.arr:
            if p.agrupations.dbstring().find("|IBEX|")!=-1 and p.obsolete==False:
                arrInt.append(p.id)
        self.w=wdgProducts(self.mem,  arrInt)
        self.layout.addWidget(self.w)
        self.w.show()        

    @pyqtSlot()  
    def on_actionIndexesAll_triggered(self):
        from xulpymoney.ui.wdgProducts import wdgProducts
        self.w.close()
        arrInt=[]
        for p in self.mem.data.products.arr:
            if p.type.id==eProductType.Index:
                arrInt.append(p.id)
        self.w=wdgProducts(self.mem,  arrInt)
        self.layout.addWidget(self.w)
        self.w.show()      
        
    @pyqtSlot()  
    def on_actionIndexesObsolete_triggered(self):
        from xulpymoney.ui.wdgProducts import wdgProducts
        self.w.close()
        arrInt=[]
        for p in self.mem.data.products.arr:
            if p.type.id==eProductType.Index and p.obsolete==True:
                arrInt.append(p.id)
        self.w=wdgProducts(self.mem,  arrInt)
        self.layout.addWidget(self.w)
        self.w.show()

    @pyqtSlot()  
    def on_actionQuoteImportInvestingComIntraday_triggered(self):
        from xulpymoney.investing_com import InvestingCom
        self.w.close()
        filename=QFileDialog.getOpenFileName(self, "", "", "Texto CSV (*.csv)")[0]
        if filename!="":
            set=InvestingCom(self.mem, filename)
            result=set.save()
            self.mem.con.commit()
            #Display result
            from xulpymoney.ui.wdgQuotesSaveResult import frmQuotesSaveResult
            d=frmQuotesSaveResult()
            d.setFileToDelete(filename)
            d.setQuotesManagers(*result)
            d.exec_()
            #Reloads changed data
            set.change_products_status_after_save(result[0], result[2], 1, downgrade_to=0, progress=True)
            self.on_actionInvestments_triggered()
                
    @pyqtSlot()  
    def on_actionSP500_triggered(self):
        from xulpymoney.ui.wdgProducts import wdgProducts
        self.w.close()
        arrInt=[]
        for p in self.mem.data.products.arr:
            if p.agrupations.dbstring().find("|SP500|")!=-1 and p.obsolete==False:
                arrInt.append(p.id)
        self.w=wdgProducts(self.mem,  arrInt)
        self.layout.addWidget(self.w)
        self.w.show()
    
    @pyqtSlot()  
    def on_actionProductsComparation_triggered(self):
        from xulpymoney.ui.wdgProductsComparation import wdgProductsComparation
        self.w.close()
        self.w=wdgProductsComparation(self.mem)

        self.layout.addWidget(self.w)
        self.w.show()            

    @pyqtSlot()  
    def on_actionProductsInvestmentActive_triggered(self):
        from xulpymoney.ui.wdgProducts import wdgProducts
        self.w.close()       
        prod=ProductManager(self.mem)
        prod.load_from_db("select * from products where id in (select products_id from inversiones where active=true) order by name")
        arrInt=[]
        for p in prod.arr:
            arrInt.append(p.id)
        self.w=wdgProducts(self.mem,  arrInt)
        self.layout.addWidget(self.w)
        self.w.show()        

    @pyqtSlot()  
    def on_actionProductsInvalidISIN_triggered(self):
        from xulpymoney.ui.wdgProducts import wdgProducts
        self.w.close()
        arrInt=[]
        for p in self.mem.data.products.arr:
            if p.isin!=None and is_valid(p.isin)==False:
                arrInt.append(p.id)
        self.w=wdgProducts(self.mem,  arrInt)
        self.layout.addWidget(self.w)
        self.w.show()

    @pyqtSlot()  
    def on_actionProductsWithoutQuotes_triggered(self):
        from xulpymoney.ui.wdgProducts import wdgProducts
        self.w.close()
        prod=ProductManager(self.mem)
        prod.load_from_db("select p.*,q.* from products p, quote(p.id, now()) q where p.id=q.id and q.quote is null and obsolete=False order by name")
        arrInt=[]
        for p in prod.arr:
            arrInt.append(p.id)
        self.w=wdgProducts(self.mem,  arrInt)
        self.layout.addWidget(self.w)
        self.w.show()       

    @pyqtSlot()  
    def on_actionProductsWithPriceVariation_triggered(self):
        from xulpymoney.ui.wdgProducts import wdgProducts
        self.w.close()        
        d=MyModalQDialog()       
        d.setWindowTitle(self.tr("Price variation"))
        d.setSettings(self.mem.settings,"frmMain", "mqdProductsWithPriceVariation")
        lblDays=QLabel("Days")
        txtDays=myQLineEdit(d)
        txtDays.setText(90)
        lblVariation=QLabel("Variation")
        txtVariation=myQLineEdit(d)
        txtVariation.setText(-10)
        d.setWidgets(lblDays, txtDays, lblVariation, txtVariation)
        d.exec_()

        sql= "select * from products where is_price_variation_in_time(id, {}, now()::timestamptz-interval '{} day')=true and obsolete=False order by name".format(txtVariation.text(), txtDays.text())
        print(sql)
        self.w=wdgProducts(self.mem, sql)
        self.layout.addWidget(self.w)
        self.w.show()       

    @pyqtSlot()  
    def on_actionProductsWithOldPrice_triggered(self):
        from xulpymoney.ui.wdgProducts import wdgProducts
        self.w.close()
        prod=ProductManager(self.mem)
        prod.load_from_db("select p.* from products p, quote(p.id, now()) q where p.id=q.id and q.datetime<now() -interval '30 day' and obsolete=False order by name")
        arrInt=[]
        for p in prod.arr:
            arrInt.append(p.id)
        self.w=wdgProducts(self.mem,  arrInt)
        self.layout.addWidget(self.w)
        self.w.show()    
        
    @pyqtSlot()  
    def on_actionProductsInvestmentInactive_triggered(self):
        from xulpymoney.ui.wdgProducts import wdgProducts
        self.w.close()
        prod=ProductManager(self.mem)
        prod.load_from_db("select * from products where id in (select products_id from inversiones where active=false) order by name")
        arrInt=[]
        for p in prod.arr:
            arrInt.append(p.id)
        self.w=wdgProducts(self.mem,  arrInt)
        self.layout.addWidget(self.w)
        self.w.show()

    @pyqtSlot()  
    def on_actionProductsObsolete_triggered(self):
        from xulpymoney.ui.wdgProducts import wdgProducts
        self.w.close()
        arrInt=[]
        for p in self.mem.data.products.arr:
            if p.obsolete==True:
                arrInt.append(p.id)
        self.w=wdgProducts(self.mem,  arrInt)
        self.layout.addWidget(self.w)
        self.w.show()
                
    @pyqtSlot()  
    def on_actionProductsAutoUpdate_triggered(self):
        from xulpymoney.ui.wdgProducts import wdgProducts
        self.w.close()
        prod=ProductManager(self.mem)
        prod.load_from_db("""select * from products 
                where id in ({})
                order by name
                """.format(list2string(list(self.mem.autoupdate))))
        arrInt=[]
        for p in prod.arr:
            arrInt.append(p.id)
        self.w=wdgProducts(self.mem,  arrInt)
        self.layout.addWidget(self.w)
        self.w.show()       
    
    @pyqtSlot()  
    def on_actionProductsNotAutoUpdate_triggered(self):
        from xulpymoney.ui.wdgProducts import wdgProducts
        self.w.close()
        prod=ProductManager(self.mem)
        prod.load_from_db("""select * from products 
                where obsolete=false and id not in ({})
                order by name
                """.format(list2string(list(self.mem.autoupdate))))
        arrInt=[]
        for p in prod.arr:
            arrInt.append(p.id)
        self.w=wdgProducts(self.mem,  arrInt)
        self.layout.addWidget(self.w)
        self.w.show()            
        
    @pyqtSlot()  
    def on_actionProductsUser_triggered(self):
        from xulpymoney.ui.wdgProducts import wdgProducts
        self.w.close()
        arrInt=[]
        for p in self.mem.data.products.arr:
            if p.id<0:
                arrInt.append(p.id)
        self.w=wdgProducts(self.mem,  arrInt)
        self.layout.addWidget(self.w)
        self.w.show()

    @pyqtSlot()  
    def on_actionProductsWithoutISIN_triggered(self):
        from xulpymoney.ui.wdgProducts import wdgProducts
        self.w.close()
        prod=ProductManager(self.mem)
        prod.load_from_db("select * from products  where obsolete=false and (isin is null or isin ='') order by name,id")
        arrInt=[]
        for p in prod.arr:
            arrInt.append(p.id)
        self.w=wdgProducts(self.mem,  arrInt)
        self.layout.addWidget(self.w)
        self.w.show()

    @pyqtSlot()  
    def on_actionXetra_triggered(self):
        from xulpymoney.ui.wdgProducts import wdgProducts
        self.w.close()
        arrInt=[]
        for p in self.mem.data.products.arr:
            if p.agrupations.dbstring().find("|DAX|")!=-1 and p.obsolete==False:
                arrInt.append(p.id)
        self.w=wdgProducts(self.mem,  arrInt)
        self.layout.addWidget(self.w)
        self.w.show()        
        
    @pyqtSlot()  
    def on_actionSearch_triggered(self):
        from xulpymoney.ui.wdgProducts import wdgProducts
        self.w.close()
        self.w=wdgProducts(self.mem)
        self.layout.addWidget(self.w)
        
    @pyqtSlot()  
    def on_actionOrders_triggered(self):  
        from xulpymoney.ui.wdgOrders import wdgOrders
        self.w.close()
        self.w=wdgOrders(self.mem, self)
        self.layout.addWidget(self.w)
        self.w.show()

    @pyqtSlot()  
    def on_actionPriceUpdates_triggered(self):
        from xulpymoney.ui.wdgQuotesUpdate import wdgQuotesUpdate
        self.w.close()
        self.w=wdgQuotesUpdate(self.mem, self)
        self.layout.addWidget(self.w)
        self.w.show()


class frmMainProductsMaintenance(frmMain):
    def __init__(self, mem, parent = 0,  flags = False):
        frmMain.__init__(self, mem, parent, flags)
        self.mem.insertProducts=ProductManager(self.mem)
        self.mem.updateProducts=ProductManager(self.mem)
        self.mem.deleteProducts=ProductManager(self.mem)
        self.setWindowTitle(self.tr("Xulpymoney 2010-{0} \xa9 (Products maintenance mode)").format(__versiondate__.year))#print ("Xulpymoney 2010-{0} © €".encode('unicode-escape'))
        self.setWindowIcon(self.mem.qicon_admin())
        
        for action in [
            self.actionAccounts, 
            self.actionBanks, 
            self.actionCalculator, 
            self.actionConcepts, 
            self.actionDerivativesReport, 
            self.actionDividendsReport, 
            self.actionEvolutionReport,
            self.actionGlobalReport,
            self.actionLastOperation, 
            self.actionOrders, 
            self.actionIndexRange, 
            self.actionInvestmentRanking, 
            self.actionInvestmentsClasses, 
            self.actionInvestmentsOperations, 
            self.actionInvestmentsZeroRisk, 
            self.actionInvestments, 
            self.actionSimulations, 
            self.actionAuxiliarTables, 
            self.actionTotalReport, 
            self.actionTransfer, 
            self.actionProductRange, 
            self.actionProductsComparation, 
            self.actionPurchaseOpportunities, 
            
        ]:
            action.setEnabled(False)
        
    @pyqtSlot()  
    def on_actionExit_triggered(self): 
        reply = QMessageBox.question(
                    None, 
                    self.tr('Developer mode'), 
                    self.tr("""You are in products maintenance mode.
Changes will not be saved in database, but they will added to a SQL format file, for futures updates.
Do you want to generate it?"""), 
                    QMessageBox.Yes, 
                    QMessageBox.No
                )
        if reply==QMessageBox.Yes:
            filename="{}.sql".format(dtnaive2string(datetime.now(), "%Y%m%d%H%M"))
            f=open(filename, "w")
            f.write("\n-- Products inserts\n")
            for o in self.mem.insertProducts.arr:
                f.write(o.sql_insert(returning_id=False) + "\n")
            f.write("\n-- Products updates\n")
            for o in self.mem.updateProducts.arr:
                f.write(o.sql_update() + "\n")
            f.close()
        info("App correctly closed")
        exit(0)
        
