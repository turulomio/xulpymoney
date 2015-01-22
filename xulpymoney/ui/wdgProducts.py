from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Ui_wdgProducts import *
from frmProductReport import *
from libxulpymoney import *
from frmQuotesIBM import *
from wdgMergeCodes import *
from frmEstimationsAdd import *

class wdgProducts(QWidget, Ui_wdgProducts):
    def __init__(self, mem,  sql,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        self.products=SetProducts(self.mem)
        self.products.selected=[]#Can be selected several products
        self.tblInvestments.settings("wdgProducts",  self.mem)    
        self.mem.stockexchanges.qcombobox(self.cmbStockExchange)
        self.favoritos=self.mem.config.get_list( "wdgProducts", "favoritos")
        self.showingfavorites=False#Switch to know if widget is showing favorites            

        self.build_array(sql)
        self.products.myqtablewidget(self.tblInvestments,"wdgProducts")
    
    def build_array(self, sql):
        self.sql=sql
        self.products.load_from_db(self.sql, True)
        self.products.order_by_name()
        self.lblFound.setText(self.tr("Found {0} records".format(self.products.length())))

        
    @QtCore.pyqtSlot()  
    def on_actionFavorites_activated(self):      
        if str(self.products.selected[0].id) in self.favoritos:
            self.favoritos.remove(str(self.products.selected[0].id))
            if self.showingfavorites==True:
                if len(self.favoritos)>0:
                    self.sql="select * from products where id in ("+str(self.favoritos)[1:-1]+") order by name, id"
                else:
                    self.sql="select * from products where id=-99999999"
            self.build_array(self.sql)
            self.products.myqtablewidget(self.tblInvestments,"wdgProducts")
        else:
            self.favoritos.append(str(self.products.selected[0].id))
        print ("Favoritos", self.favoritos)
        self.mem.config.set_list("wdgProducts",  "favoritos",  self.favoritos)
        self.mem.config.save()

    @QtCore.pyqtSlot()  
    def on_actionIbex35_activated(self):
        self.build_array("select * from products where agrupations like '%|IBEX|%' order by name,id")
        self.products.myqtablewidget(self.tblInvestments,"wdgProducts")       

    @QtCore.pyqtSlot() 
    def on_actionProductDelete_activated(self):
        if self.products.selected[0].is_deletable()==False:
            m=QMessageBox()
            m.setText(self.tr("This product can't be removed, because is marked as not romavable"))
            m.exec_()    
            return
            
        if self.products.selected[0].is_system()==True:
            m=QMessageBox()
            m.setText(self.tr("This product can't be removed, because is a system product"))
            m.exec_()    
            return
            
        respuesta = QMessageBox.warning(self, self.tr("Xulpymoney"), self.tr("Deleting data from selected product ({0}). If you use manual update mode, data won't be recovered. Do you want to continue?".format(self.products.selected[0].id)), QMessageBox.Ok | QMessageBox.Cancel)
        if respuesta==QMessageBox.Ok:
            con=self.mem.connect_from_config()
            cur = con.cursor()
            cur.execute("delete from products where id=%s", (self.products.selected[0].id, ))
            cur.execute("delete from quotes where id=%s", (self.products.selected[0].id, ))
            cur.execute("delete from estimations_dps where id=%s", (self.products.selected[0].id, ))
            con.commit()
            cur.close()     
            self.mem.disconnect(con)    
            self.build_array(self.sql)
            self.products.myqtablewidget(self.tblInvestments,"wdgProducts")  
            

    @QtCore.pyqtSlot() 
    def on_actionProductNew_activated(self):
        w=frmProductReport(self.mem, None, self)
        w.exec_()        
        self.build_array(self.sql)
        self.products.myqtablewidget(self.tblInvestments,"wdgProducts")

    @QtCore.pyqtSlot() 
    def on_actionProductReport_activated(self):
        w=frmProductReport(self.mem, self.products.selected[0], None,  self)
        w.exec_()        
        self.build_array(self.sql)
        self.products.myqtablewidget(self.tblInvestments,"wdgProducts")
        
    @QtCore.pyqtSlot() 
    def on_actionSortTPCDiario_activated(self):
        if self.products.order_by_daily_tpc():
            self.products.myqtablewidget(self.tblInvestments,"wdgProducts")        
        else:
            qmessagebox_error_ordering()
        
    @QtCore.pyqtSlot() 
    def on_actionSortTPCAnual_activated(self):
        if self.products.order_by_annual_tpc():
            self.products.myqtablewidget(self.tblInvestments,"wdgProducts")        
        else:
            qmessagebox_error_ordering()
        
    @QtCore.pyqtSlot() 
    def on_actionSortHour_activated(self):
        self.products.order_by_datetime()
        self.products.myqtablewidget(self.tblInvestments,"wdgProducts")        
        
    @QtCore.pyqtSlot() 
    def on_actionSortName_activated(self):
        self.products.order_by_name()
        self.products.myqtablewidget(self.tblInvestments,"wdgProducts")        
        
    @QtCore.pyqtSlot() 
    def on_actionSortDividend_activated(self):
        if self.products.order_by_dividend():
            self.products.myqtablewidget(self.tblInvestments,"wdgProducts")        
        else:
            qmessagebox_error_ordering()     
        
    def on_txt_returnPressed(self):
        self.on_cmd_pressed()
        
    def on_cmd_pressed(self):
        if len(self.txt.text().upper())<=3:            
            m=QMessageBox()
            m.setText(self.tr("Search too wide. You need more than 3 characters"))
            m.exec_()  
            return
            
        #Stock exchange Filter
        stockexchangefilter=""
        if self.chkStockExchange.checkState()==Qt.Checked:
            bolsa=self.mem.stockexchanges.find(self.cmbStockExchange.itemData(self.cmbStockExchange.currentIndex()))            
            stockexchangefilter=" and id_bolsas={0} ".format(bolsa.id)

        self.build_array("select * from products where (id::text like '%"+(self.txt.text().upper())+
                "%' or upper(name) like '%"+(self.txt.text().upper())+
                "%' or upper(isin) like '%"+(self.txt.text().upper())+
                "%' or upper(ticker) like '%"+(self.txt.text().upper())+
                "%' or upper(comentario) like '%"+(self.txt.text().upper())+
                "%') "+ stockexchangefilter)
        self.products.myqtablewidget(self.tblInvestments,"wdgProducts")          


    def on_tblInvestments_customContextMenuRequested(self,  pos):

        menu=QMenu()
        menu.addAction(self.actionProductReport)
        menu.addSeparator()
        menu.addAction(self.actionProductNew)
        menu.addAction(self.actionProductDelete)
        menu.addSeparator()
        menu.addAction(self.actionQuoteNew)
        menu.addAction(self.actionEstimationDPSNew)
        menu.addSeparator()
        menu.addAction(self.actionMergeCodes)
        menu.addAction(self.actionFavorites)
        if len(self.products.selected)==1:
            if str(self.products.selected[0].id) in self.favoritos:
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
            self.actionIbex35.setEnabled(True)
            self.actionQuoteNew.setEnabled(True)
            self.actionEstimationDPSNew.setEnabled(True)
            self.actionPurge.setEnabled(True)
        else:
            self.actionMergeCodes.setEnabled(False)
            self.actionProductDelete.setEnabled(False)
            self.actionFavorites.setEnabled(False)
            self.actionProductReport.setEnabled(False)
            self.actionIbex35.setEnabled(False)
            self.actionQuoteNew.setEnabled(False)
            self.actionEstimationDPSNew.setEnabled(False)
            self.actionPurge.setEnabled(False)
        
        if len(self.products.selected)==2:
            self.actionMergeCodes.setEnabled(True)
            
        menu.exec_(self.tblInvestments.mapToGlobal(pos))

        
        
    @QtCore.pyqtSlot() 
    def on_actionMergeCodes_activated(self):
        #Only two checked in custom contest       
        d=QDialog(self)        
        d.setFixedSize(800, 210)
        d.setWindowTitle(self.tr("Merging codes"))
        w=wdgMergeCodes(self.mem, self.products.selected[0], self.products.selected[1])
        lay = QVBoxLayout(d)
        lay.addWidget(w)
        d.exec_()
        self.build_array(self.sql)
        self.products.myqtablewidget(self.tblInvestments,"wdgProducts")

    
    def on_tblInvestments_itemSelectionChanged(self):
        del self.products.selected
        self.products.selected=[]
        for i in self.tblInvestments.selectedItems():
            if i.column()==0:#only once per row
                self.products.selected.append(self.products.arr[i.row()])
        print (self.products.selected)

    @QtCore.pyqtSlot()  
    def on_actionPurge_activated(self):
        all=SetQuotesAll(self.mem)
        all.load_from_db(self.products.selected[0])
        numpurged=all.purge(progress=True)
        if numpurged!=None:#Canceled
            self.mem.con.commit()
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.tr("{0} quotes have been purged from {1}".format(numpurged, self.products.selected[0].name)))
            m.exec_()    
        else:
            self.mem.con.rollback()

    @QtCore.pyqtSlot()  
    def on_actionQuoteNew_activated(self):
        w=frmQuotesIBM(self.mem,  self.products.selected[0])
        w.exec_()               
        self.build_array(self.sql)
        self.products.myqtablewidget(self.tblInvestments,"wdgProducts")  

    @QtCore.pyqtSlot()  
    def on_actionEstimationDPSNew_activated(self):
        d=frmEstimationsAdd(self.mem, self.products.selected[0], "dps")
        d.exec_()
        if d.result()==QDialog.Accepted:
            self.build_array(self.sql)
            self.products.myqtablewidget(self.tblInvestments,"wdgProducts")  
            