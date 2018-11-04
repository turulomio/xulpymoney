from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QWidget, QDialog, QVBoxLayout, QMenu, QMessageBox
from xulpymoney.ui.Ui_wdgProducts import Ui_wdgProducts
from xulpymoney.ui.frmProductReport import frmProductReport
from xulpymoney.libxulpymoney import ProductManager, QuoteAllIntradayManager
from xulpymoney.libxulpymoneyfunctions import list2string, qmessagebox
from xulpymoney.ui.frmQuotesIBM import frmQuotesIBM
from xulpymoney.ui.wdgMergeCodes import wdgMergeCodes
from xulpymoney.ui.frmEstimationsAdd import frmEstimationsAdd
from xulpymoney.ui.wdgProductHistoricalChart import wdgProductHistoricalBuyChart
import logging

class wdgProducts(QWidget, Ui_wdgProducts):
    def __init__(self, mem,  sql,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        self.products=ProductManager(self.mem)
        self.products.selected=[]#Can be selected several products
        self.tblInvestments.settings(self.mem, "wdgProducts")
        self.mem.stockmarkets.qcombobox(self.cmbStockExchange)
        self.showingfavorites=False#Switch to know if widget is showing favorites            

        self.build_array(sql)
        self.products.myqtablewidget(self.tblInvestments)
    
    def build_array(self, sql):
        self.sql=sql
        logging.debug(sql)
        self.products.load_from_db(self.sql, True)
        self.products.order_by_upper_name()
        self.lblFound.setText(self.tr("Found {0} records".format(self.products.length())))

        
    @pyqtSlot()  
    def on_actionFavorites_triggered(self):      
        if self.products.selected[0].id in self.mem.favorites:
            self.mem.favorites.remove(self.products.selected[0].id)
            if self.showingfavorites==True:
                if len(self.mem.favorites)>0:
                    self.sql="select * from products where id in ("+list2string(self.mem.favorites)+") order by name, id"
                else:
                    self.sql="select * from products where id=-99999999"
            self.build_array(self.sql)
            self.products.myqtablewidget(self.tblInvestments)
        else:
            self.mem.favorites.append(self.products.selected[0].id)
        print ("Favoritos", self.mem.favorites)
        self.mem.save_MemSettingsDB()

    @pyqtSlot()  
    def on_actionIbex35_triggered(self):
        self.build_array("select * from products where agrupations like '%|IBEX|%' and obsolete=False order by name,id")
        self.products.myqtablewidget(self.tblInvestments)       

    @pyqtSlot() 
    def on_actionProductDelete_triggered(self):
         
        if self.products.selected[0].is_deletable()==False:
            qmessagebox(self.tr("This product can't be removed, because is marked as not romavable"))
            return
            
        if self.products.selected[0].is_system()==True:
            qmessagebox(self.tr("This product can't be removed, because is a system product"))
            return
            
        respuesta = QMessageBox.warning(self, self.tr("Xulpymoney"), self.tr("Deleting data from selected product ({0}). If you use manual update mode, data won't be recovered. Do you want to continue?".format(self.products.selected[0].id)), QMessageBox.Ok | QMessageBox.Cancel)
        if respuesta==QMessageBox.Ok:
            cur = self.mem.con.cursor()
            cur.execute("delete from quotes where id=%s", (self.products.selected[0].id, ))
            cur.execute("delete from estimations_dps where id=%s", (self.products.selected[0].id, ))
            cur.execute("delete from estimations_eps where id=%s", (self.products.selected[0].id, ))
            cur.execute("delete from dps where id=%s", (self.products.selected[0].id, ))
            cur.execute("delete from products where id=%s", (self.products.selected[0].id, ))
            self.mem.con.commit()
            cur.close()     
            self.build_array(self.sql)
            self.products.myqtablewidget(self.tblInvestments)  
            

    @pyqtSlot() 
    def on_actionProductNew_triggered(self):
        w=frmProductReport(self.mem, None, self)
        w.exec_()        
        self.build_array(self.sql)
        self.products.myqtablewidget(self.tblInvestments)

    @pyqtSlot() 
    def on_actionPurchaseGraphic_triggered(self):
        self.products.selected[0].result.get_basic_and_ohcls()
        d=QDialog(self)     
        d.showMaximized()
        d.setWindowTitle(self.tr("Purchase graph"))
        lay = QVBoxLayout(d)
        
        wc=wdgProductHistoricalBuyChart()
        wc.setProduct(self.products.selected[0], None)
        wc.setPrice(self.products.selected[0].result.basic.last.quote)
        wc.generate()
        wc.display()
        lay.addWidget(wc)
        d.exec_()
        
    @pyqtSlot() 
    def on_actionProductReport_triggered(self):
        w=frmProductReport(self.mem, self.products.selected[0], None,  self)
        w.exec_()        
        self.build_array(self.sql)
        self.products.myqtablewidget(self.tblInvestments)
        
    @pyqtSlot() 
    def on_actionSortTPCDiario_triggered(self):
        if self.products.order_by_daily_tpc():
            self.products.myqtablewidget(self.tblInvestments)        
        else:
            qmessagebox(self.tr("I couldn't order data due to they have null values"))
        
    @pyqtSlot() 
    def on_actionSortTPCAnual_triggered(self):
        if self.products.order_by_annual_tpc():
            self.products.myqtablewidget(self.tblInvestments)        
        else:
            qmessagebox(self.tr("I couldn't order data due to they have null values"))
        
    @pyqtSlot() 
    def on_actionSortHour_triggered(self):
        self.products.order_by_datetime()
        self.products.myqtablewidget(self.tblInvestments)        
        
    @pyqtSlot() 
    def on_actionSortName_triggered(self):
        self.products.order_by_upper_name()
        self.products.myqtablewidget(self.tblInvestments)        
        
    @pyqtSlot() 
    def on_actionSortDividend_triggered(self):
        if self.products.order_by_dividend():
            self.products.myqtablewidget(self.tblInvestments)        
        else:
            qmessagebox(self.tr("I couldn't order data due to they have null values"))     
        
    def on_txt_returnPressed(self):
        self.on_cmd_pressed()

    def on_tblInvestments_cellDoubleClicked(self, row, column):
        self.on_actionProductReport_triggered()

    def on_cmd_pressed(self):
        if len(self.txt.text().upper())<=3:            
            qmessagebox(self.tr("Search too wide. You need more than 3 characters"))
            return
            
        #Stock exchange Filter
        stockmarketfilter=""
        if self.chkStockExchange.checkState()==Qt.Checked:
            bolsa=self.mem.stockmarkets.find_by_id(self.cmbStockExchange.itemData(self.cmbStockExchange.currentIndex()))            
            stockmarketfilter=" and stockmarkets_id={0} ".format(bolsa.id)
            
        if self.chkObsolete.checkState()==Qt.Checked:
            obsoletefilter=""
        else:
            obsoletefilter=" and obsolete=False "

        self.build_array("select * from products where (id::text like '%"+(self.txt.text().upper())+
                "%' or upper(name) like '%"+(self.txt.text().upper())+
                "%' or upper(isin) like '%"+(self.txt.text().upper())+
                "%' or '{}'=any(tickers) ".format(self.txt.text().upper())+
                " or upper(comment) like '%"+(self.txt.text().upper())+
                "%') "+ stockmarketfilter +obsoletefilter)
        self.products.myqtablewidget(self.tblInvestments)          


    def on_tblInvestments_customContextMenuRequested(self,  pos):

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
        if len(self.products.selected)==1:
            if self.products.selected[0].id in self.mem.favorites:
                self.actionFavorites.setText(self.tr("Remove from favorites"))
            else:
                self.actionFavorites.setText(self.tr("Add to favorites"))
        menu.addSeparator()
        menu.addAction(self.actionPurge)

        if len (self.products.selected)==1:
            if self.products.selected[0].id==79329:
                menu.addSeparator()
                menu.addAction(self.actionIbex35)
        menu.addSeparator()
        ordenar=QMenu(self.tr("Order by"))
        menu.addMenu(ordenar)
        ordenar.addAction(self.actionSortName)
        ordenar.addAction(self.actionSortHour)
        ordenar.addAction(self.actionSortTPCDiario)
        ordenar.addAction(self.actionSortTPCAnual)
        ordenar.addAction(self.actionSortDividend)
        
        #Enabled disabled  
        if len(self.products.selected)==1:
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
        elif len(self.products.selected)==2:
            self.actionMergeCodes.setEnabled(True)
        else:
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
        menu.exec_(self.tblInvestments.mapToGlobal(pos))

    @pyqtSlot() 
    def on_actionMergeCodes_triggered(self):
        #Only two checked in custom contest
        d=QDialog(self)
        d.setFixedSize(800, 210)
        d.setWindowTitle(self.tr("Merging codes"))
        w=wdgMergeCodes(self.mem, self.products.selected[0], self.products.selected[1])
        lay = QVBoxLayout(d)
        lay.addWidget(w)
        d.exec_()
        self.build_array(self.sql)
        self.products.myqtablewidget(self.tblInvestments)

    
    def on_tblInvestments_itemSelectionChanged(self):
        self.products.cleanSelection()
        for i in self.tblInvestments.selectedItems():
            if i.column()==0:#only once per row
                self.products.selected.append(self.products.arr[i.row()])
        logging.debug(self.products.selected)

    @pyqtSlot()  
    def on_actionPurge_triggered(self):
        all=QuoteAllIntradayManager(self.mem)
        all.load_from_db(self.products.selected[0])
        numpurged=all.purge(progress=True)
        if numpurged!=None:#Canceled
            self.mem.con.commit()
            qmessagebox(self.tr("{0} quotes have been purged from {1}".format(numpurged, self.products.selected[0].name)))
        else:
            self.mem.con.rollback()

    @pyqtSlot()  
    def on_actionQuoteNew_triggered(self):
        w=frmQuotesIBM(self.mem,  self.products.selected[0])
        w.exec_()               
        self.build_array(self.sql)
        self.products.myqtablewidget(self.tblInvestments)  
        
    @pyqtSlot() 
    def on_actionProductPriceLastRemove_triggered(self):
        self.products.selected[0].result.basic.last.delete()
        self.mem.con.commit()
        self.products.selected[0].result.basic.load_from_db()
        self.build_array(self.sql)
        self.products.myqtablewidget(self.tblInvestments)
        
    @pyqtSlot()  
    def on_actionEstimationDPSNew_triggered(self):
        d=frmEstimationsAdd(self.mem, self.products.selected[0], "dps")
        d.exec_()
        if d.result()==QDialog.Accepted:
            self.build_array(self.sql)
            self.products.myqtablewidget(self.tblInvestments)  
            
