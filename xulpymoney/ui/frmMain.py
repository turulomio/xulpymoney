## @package frmMain
## @brief User interface main window.

from PyQt5.QtCore import pyqtSlot, QProcess, QUrl,  QSize
from PyQt5.QtGui import QIcon, QDesktopServices
from PyQt5.QtWidgets import QMainWindow,  QWidget, QLabel, QMessageBox, QProgressDialog, QDialog,  QApplication, QVBoxLayout
import os
from xulpymoney.ui.Ui_frmMain import Ui_frmMain
from xulpymoney.ui.frmAbout import frmAbout
from xulpymoney.libxulpymoney import AssetsReport, Product, ProductManager
from xulpymoney.libxulpymoneyfunctions import list2string, qmessagebox, sync_data
from xulpymoney.libxulpymoneytypes import eProductType
from xulpymoney.version import __versiondate__
from xulpymoney.ui.frmAccess import frmAccess
from xulpymoney.ui.myqlineedit import myQLineEdit
from xulpymoney.ui.wdgTotal import wdgTotal
from xulpymoney.ui.wdgDividendsReport import wdgDividendsReport
from xulpymoney.ui.wdgInvestmentClasses import wdgInvestmentClasses
from xulpymoney.ui.wdgAPR import wdgAPR
from xulpymoney.ui.wdgAccounts import wdgAccounts
from xulpymoney.ui.wdgBanks import wdgBanks
from xulpymoney.ui.wdgConcepts import wdgConcepts
from xulpymoney.ui.wdgCalculator import wdgCalculator
from xulpymoney.ui.wdgCuriosities import wdgCuriosities
from xulpymoney.ui.wdgIndexRange import wdgIndexRange
from xulpymoney.ui.wdgInvestments import wdgInvestments
from xulpymoney.ui.wdgInvestmentsOperations import wdgInvestmentsOperations
from xulpymoney.ui.wdgInvestmentsRanking import wdgInvestmentsRanking
from xulpymoney.ui.frmAuxiliarTables import frmAuxiliarTables
from xulpymoney.ui.frmTransfer import frmTransfer
from xulpymoney.ui.frmSettings import frmSettings
from xulpymoney.ui.frmHelp import frmHelp
from xulpymoney.ui.wdgOrders import wdgOrders
from xulpymoney.ui.wdgOpportunities import wdgOpportunities
from xulpymoney.ui.wdgProducts import wdgProducts
from xulpymoney.ui.wdgProductsComparation import wdgProductsComparation
from xulpymoney.ui.wdgSimulations import wdgSimulations
from xulpymoney.ui.wdgQuotesUpdate import wdgQuotesUpdate
from stdnum.isin import is_valid

from xulpymoney.ui.wdgLastCurrent import wdgLastCurrent

class frmMain(QMainWindow, Ui_frmMain):
    def __init__(self, mem, parent = 0,  flags = False):
        QMainWindow.__init__(self, None)
        self.setupUi(self)
        self.showMaximized()
        
        self.mem=mem
        self.mem.con.inactivity_timeout.connect(self.inactivity_timeout)        
        self.sqlvacio="select * from products where id=-999999"
        
        self.w=QWidget()       
        self.statusBar.addWidget(QLabel(self.tr("postgres://{}@{}:{}/{}").format(self.mem.con.user, self.mem.con.server,  self.mem.con.port, self.mem.con.db)))

        self.mem.load_db_data() ##CARGA TODOS LOS DATOS Y LOS VINCULA       
  
        if self.mem.con.is_superuser():
            self.setWindowTitle(self.tr("Xulpymoney 2010-{0} \xa9 (Admin mode)").format(__versiondate__.year))#print ("Xulpymoney 2010-{0} © €".encode('unicode-escape'))
            self.setWindowIcon(self.mem.qicon_admin())
        else:
            self.setWindowTitle(self.tr("Xulpymoney 2010-{0} \xa9").format(__versiondate__.year))
            

    def actionsEnabled(self, bool):
        self.menuBar.setEnabled(bool)
        self.toolBar.setEnabled(bool)
        
    @pyqtSlot()
    def on_actionGlobalReport_triggered(self):
        file="AssetsReport.odt"
        doc=AssetsReport(self.mem, file)
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
        arrInt=[]
        for p in self.mem.data.products.arr:
            if p.agrupations.dbstring().find("|CAC|")!=-1 and p.obsolete==False:
                arrInt.append(p.id)
        self.w=wdgProducts(self.mem,  arrInt)
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
        self.w.close()
        prod=ProductManager(self.mem)
        prod.load_from_db("select * from products where id in (select id from estimations_dps where year=date_part('year',now()) and estimation is not null) and id in (select distinct(id) from quotes where date_part('year', datetime)=date_part('year',now()))")
        self.w=wdgProducts(self.mem,  prod.array_of_ids())
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

        arrInt=[]
        for p in self.mem.data.products.arr:
            if p.agrupations.dbstring().find("|NASDAQ100|")!=-1 and p.obsolete==False:
                arrInt.append(p.id)
        self.w=wdgProducts(self.mem,  arrInt)
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
        if len(self.mem.favorites)==0:
            m=QMessageBox()
            m.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
            m.setIcon(QMessageBox.Information)
            m.setText(self.tr("There aren't favorite products"))
            m.exec_()     
            return
        self.w.close()
        self.w=wdgProducts(self.mem, self.mem.favorites)
        self.layout.addWidget(self.w)
        self.w.show()

    @pyqtSlot()  
    def on_actionSharesAll_triggered(self):
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
        arrInt=[]
        for p in self.mem.data.products.arr:
            if p.type.id in (eProductType.PrivateBond,  eProductType.PublicBond) and p.obsolete==False:
                arrInt.append(p.id)
            
        self.w=wdgProducts(self.mem,  arrInt)

        self.layout.addWidget(self.w)
        self.w.show()
        
    @pyqtSlot()  
    def on_actionBondsObsolete_triggered(self):
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
        self.w.close()
        arrInt=[]
        for p in self.mem.data.products.arr:
            if p.type.id==eProductType.Index and p.obsolete==True:
                arrInt.append(p.id)
        self.w=wdgProducts(self.mem,  arrInt)
        self.layout.addWidget(self.w)
        self.w.show()     
                
    @pyqtSlot()  
    def on_actionSP500_triggered(self):
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
        self.w.close()
        self.w=wdgProductsComparation(self.mem)

        self.layout.addWidget(self.w)
        self.w.show()            

    @pyqtSlot()  
    def on_actionProductsInvestmentActive_triggered(self):
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
        self.w.close()        
        d=QDialog()       
        d.setWindowTitle(self.tr("Price variation"))
        lblDays=QLabel("Days")
        txtDays=myQLineEdit(d)
        txtDays.setText(90)
        lblVariation=QLabel("Variation")
        txtVariation=myQLineEdit(d)
        txtVariation.setText(-10)
        lay = QVBoxLayout(d)
        lay.addWidget(lblDays)
        lay.addWidget(txtDays)
        lay.addWidget(lblVariation)
        lay.addWidget(txtVariation)
        d.exec_()
        sql= "select * from products where is_price_variation_in_time(id, {}, now()::timestamptz-interval '{} day')=true and obsolete=False order by name".format(txtVariation.text(), txtDays.text())
        print(sql)
        self.w=wdgProducts(self.mem, sql)
        self.layout.addWidget(self.w)
        self.w.show()       

    @pyqtSlot()  
    def on_actionProductsWithOldPrice_triggered(self):
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
        self.w.close()
        arrInt=[]
        for p in self.mem.data.products.arr:
            if p.id<0:
                arrInt.append(p.id)
        self.w=wdgProducts(self.mem,  arrInt)
        self.layout.addWidget(self.w)
        self.w.show()
        
    @pyqtSlot()  
    def on_actionProductsUpdate_triggered(self):
        p=ProductManager(self.mem)
        p.update_from_internet()

        
    @pyqtSlot()  
    def on_actionProductsWithoutISIN_triggered(self):
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
    def on_actionTablasAuxiliares_triggered(self):
        w=frmAuxiliarTables(self.mem, self)
        w.tblTipos_reload()
        w.exec_()

                
    @pyqtSlot()  
    def on_actionXetra_triggered(self):
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
        self.w.close()
        self.w=wdgProducts(self.mem)
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
