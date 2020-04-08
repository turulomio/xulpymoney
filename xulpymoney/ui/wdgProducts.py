from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QWidget, QDialog, QVBoxLayout, QMenu, QMessageBox, QAbstractItemView
from logging import debug
from xulpymoney.ui.Ui_wdgProducts import Ui_wdgProducts
from xulpymoney.objects.quote import QuoteAllIntradayManager
from xulpymoney.ui.myqdialog import MyModalQDialog
from xulpymoney.ui.myqwidgets import qmessagebox
from xulpymoney.ui.frmQuotesIBM import frmQuotesIBM
from xulpymoney.ui.wdgProductsDataMove import wdgProductsDataMove
from xulpymoney.ui.frmEstimationsAdd import frmEstimationsAdd

class wdgProducts(QWidget, Ui_wdgProducts):
    def __init__(self, mem,  arrInt=[],  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        self.mqtwInvestments.setSelectionMode(QAbstractItemView.SelectRows, QAbstractItemView.MultiSelection)
        self.mqtwInvestments.setSettings(self.mem.settings, "wdgProducts", "mqtwInvestments")
        self.mqtwInvestments.table.cellDoubleClicked.connect(self.on_mqtwInvestments_cellDoubleClicked)
        self.mqtwInvestments.table.customContextMenuRequested.connect(self.on_mqtwInvestments_customContextMenuRequested)
        self.mem.stockmarkets.qcombobox(self.cmbStockExchange)
        self.arrInt=arrInt#Lista de ids of products showed and used to show
        self.build_array_from_arrInt()
        self.favorites=self.mem.settingsdb.value_list_of_integers("mem/favorites",  "")
        
    def build_array_from_arrInt(self):        
        self.products=self.mem.data.products.ProductManager_with_id_in_list(self.arrInt)
        self.products.needStatus(needstatus=1, progress=True)
        self.lblFound.setText(self.tr("Found {0} records".format(self.products.length())))
        self.products.myqtablewidget(self.mqtwInvestments)
        self.mqtwInvestments.setOrderBy(1, False)

    @pyqtSlot()
    def on_actionFavorites_triggered(self):      
        if len(self.mqtwInvestments.selected)>0:
            if self.mqtwInvestments.selected[0].id in self.favorites:
                self.favorites.remove(self.mqtwInvestments.selected[0].id)
            else:
                self.favorites.append(self.mqtwInvestments.selected[0].id)
            debug("Favorites: {}".format(self.favorites))
            self.mem.settingsdb.setValue("mem/favorites", self.favorites)
        
            del self.arrInt
            self.arrInt=[]
            for f in self.favorites:
                self.arrInt.append(f)
            self.build_array_from_arrInt()

    @pyqtSlot()  
    def on_actionIbex35_triggered(self):
        del self.arrInt
        self.arrInt=[]
        for p in self.mem.data.products.arr:
            if p.agrupations.dbstring.find("|IBEX|")!=-1 and p.obsolete==False:
                self.arrInt.append(p.id)
        self.build_array_from_arrInt()

    @pyqtSlot() 
    def on_actionProductDelete_triggered(self):
        if len(self.mqtwInvestments.selected)>0:
            if self.mqtwInvestments.selected[0].is_deletable()==False:
                qmessagebox(self.tr("This product can't be removed, because is marked as not remavable"))
                return
                
            if self.mqtwInvestments.selected[0].is_system()==True:
                qmessagebox(self.tr("This product can't be removed, because is a system product"))
                return
                
            respuesta = QMessageBox.warning(self, self.tr("Xulpymoney"), self.tr("Deleting data from selected product ({0}). If you use manual update mode, data won't be recovered. Do you want to continue?".format(self.mqtwInvestments.selected[0].id)), QMessageBox.Ok | QMessageBox.Cancel)
            if respuesta==QMessageBox.Ok:
                self.arrInt.remove(self.mqtwInvestments.selected[0].id)
                self.mem.data.products.remove(self.mqtwInvestments.selected[0])
                self.mem.con.commit()
                self.build_array_from_arrInt()            

    @pyqtSlot() 
    def on_actionProductNew_triggered(self):
        from xulpymoney.ui.frmProductReport import frmProductReport
        w=frmProductReport(self.mem, None, self)
        w.exec_()        
        del self.arrInt
        self.arrInt=[w.product.id, ]
        self.build_array_from_arrInt()

    @pyqtSlot() 
    def on_actionPurchaseGraphic_triggered(self):
        if len(self.mqtwInvestments.selected)>0:
            from xulpymoney.ui.wdgProductHistoricalChart import wdgProductHistoricalBuyChart
            self.mqtwInvestments.selected[0].needStatus(2)
            d=QDialog(self)     
            d.showMaximized()
            d.setWindowTitle(self.tr("Purchase graph"))
            lay = QVBoxLayout(d)
            
            wc=wdgProductHistoricalBuyChart()
            wc.setProduct(self.mqtwInvestments.selected[0], None)
            wc.setPrice(self.mqtwInvestments.selected[0].result.basic.last.quote)
            wc.generate()
            wc.display()
            lay.addWidget(wc)
            d.exec_()
        
    @pyqtSlot() 
    def on_actionProductReport_triggered(self):
        if len(self.mqtwInvestments.selected)>0:
            from xulpymoney.ui.frmProductReport import frmProductReport
            w=frmProductReport(self.mem, self.mqtwInvestments.selected[0], None,  self)
            w.exec_()        
            self.build_array_from_arrInt()
    
    def on_txt_returnPressed(self):
        self.on_cmd_pressed()

    def on_mqtwInvestments_cellDoubleClicked(self, row, column):
        self.on_actionProductReport_triggered()

    def on_cmd_pressed(self):
        if len(self.txt.text().upper())<=2:            
            qmessagebox(self.tr("Search too wide. You need more than 2 characters"))
            return

        # To filter by stockmarket
        sm=None
        if self.chkStockExchange.checkState()==Qt.Checked:
            sm=self.mem.stockmarkets.find_by_id(self.cmbStockExchange.itemData(self.cmbStockExchange.currentIndex()))     

        del self.arrInt
        self.arrInt=[]
        #Temporal ProductManager
        pros=self.mem.data.products.ProductManager_contains_string(self.txt.text())
        for p in pros.arr:
            #Filter sm
            if sm!=None and sm.id!=p.stockmarket.id:
                continue
            else:
                self.arrInt.append(p.id)

        self.build_array_from_arrInt()

    def on_mqtwInvestments_customContextMenuRequested(self,  pos):
        menu=QMenu()
        menu.addAction(self.actionProductReport)
        menu.addAction(self.actionPurchaseGraphic)
        menu.addSeparator()
        menu.addAction(self.actionProductNew)
        menu.addAction(self.actionProductDelete)
        menu.addSeparator()
        menu.addAction(self.actionQuoteNew)
        menu.addAction(self.actionProductPriceLastRemove)
        menu.addAction(self.actionEstimationDPSNew)
        menu.addSeparator()
        menu.addAction(self.actionMergeCodes)
        menu.addAction(self.actionFavorites)
        menu.addSeparator()
        menu.addAction(self.actionPurge)
        #Enabled disabled  
        if self.mqtwInvestments.selected is None or len(self.mqtwInvestments.selected)>2:
            self.actionMergeCodes.setEnabled(False)
            self.actionProductDelete.setEnabled(False)
            self.actionFavorites.setEnabled(False)
            self.actionProductReport.setEnabled(False)
            self.actionPurchaseGraphic.setEnabled(False)
            self.actionIbex35.setEnabled(False)
            self.actionQuoteNew.setEnabled(False)
            self.actionEstimationDPSNew.setEnabled(False)
            self.actionPurge.setEnabled(False)
            self.actionProductPriceLastRemove.setEnabled(False)
        elif len(self.mqtwInvestments.selected)==1:
            if self.mqtwInvestments.selected[0].id in self.favorites:
                self.actionFavorites.setText(self.tr("Remove from favorites"))
            else:
                self.actionFavorites.setText(self.tr("Add to favorites"))

            if self.mqtwInvestments.selected[0].id==79329:
                menu.addSeparator()
                menu.addAction(self.actionIbex35)
            self.actionMergeCodes.setEnabled(False)
            self.actionProductDelete.setEnabled(True)
            self.actionFavorites.setEnabled(True)
            self.actionProductReport.setEnabled(True)
            self.actionPurchaseGraphic.setEnabled(True)
            self.actionIbex35.setEnabled(True)
            self.actionQuoteNew.setEnabled(True)
            self.actionEstimationDPSNew.setEnabled(True)
            self.actionPurge.setEnabled(True)
            self.actionProductPriceLastRemove.setEnabled(True)
        elif len(self.mqtwInvestments.selected)==2:
            self.actionMergeCodes.setEnabled(True)
            self.actionFavorites.setEnabled(False)
        menu.addSeparator()
        menu.addMenu(self.mqtwInvestments.qmenu())
        menu.exec_(self.mqtwInvestments.table.mapToGlobal(pos))

    @pyqtSlot() 
    def on_actionMergeCodes_triggered(self):
        if len(self.mqtwInvestments.selected)==2:
            #Only two checked in custom contest
            d=MyModalQDialog(self)
            d.setWindowTitle(self.tr("Merging codes"))
            d.setSettings(self.mem.settings, "wdgProducts", "frmMergeProducts")
            w=wdgProductsDataMove(self.mem, self.mqtwInvestments.selected[0], self.mqtwInvestments.selected[1])
            d.setWidgets(w)
            d.exec_()
            self.build_array_from_arrInt()

    @pyqtSlot()  
    def on_actionPurge_triggered(self):
        if len(self.mqtwInvestments.selected)>0:
            all=QuoteAllIntradayManager(self.mem)
            all.load_from_db(self.mqtwInvestments.selected[0])
            numpurged=all.purge(progress=True)
            if numpurged!=None:#Canceled
                self.mem.con.commit()
                qmessagebox(self.tr("{0} quotes have been purged from {1}".format(numpurged, self.mqtwInvestments.selected[0].name)))
            else:
                self.mem.con.rollback()

    @pyqtSlot()  
    def on_actionQuoteNew_triggered(self):
        if len(self.mqtwInvestments.selected)>0:
            w=frmQuotesIBM(self.mem,  self.mqtwInvestments.selected[0])
            w.exec_()
            self.build_array_from_arrInt()

    @pyqtSlot() 
    def on_actionProductPriceLastRemove_triggered(self):
        if len(self.mqtwInvestments.selected)>0:
            self.mqtwInvestments.selected[0].result.basic.last.delete()
            self.mem.con.commit()
            self.mqtwInvestments.selected[0].needStatus(1, downgrade_to=0)
            self.build_array_from_arrInt()

    @pyqtSlot()  
    def on_actionEstimationDPSNew_triggered(self):
        if len(self.mqtwInvestments.selected)>0:
            d=frmEstimationsAdd(self.mem, self.mqtwInvestments.selected[0], "dps")
            d.exec_()
            if d.result()==QDialog.Accepted:
                self.mqtwInvestments.selected[0].needStatus(1, downgrade_to=0)
                self.build_array_from_arrInt()
