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
        self.products=[]#Es una lista de products
        self.selProduct=None##Objeto de inversion seleccionado
        self.tblInvestments.settings("wdgProducts",  self.mem)    
        self.mem.stockexchanges.qcombobox(self.cmbStockExchange)
        self.setFavoritos=set(self.mem.config.get_list( "wdgProducts", "favoritos"))
        self.progress = QProgressDialog(self.tr("Receiving data"), self.tr("Cancel"), 0,0)
        self.progress.setModal(True)
        self.progress.setWindowTitle(self.tr("Receiving data..."))
        self.progress.setMinimumDuration(0)                

        self.build_array(sql)
        self.build_table()
        self.selectedRows=0
    
    def build_array(self, sql):
        inicio=datetime.datetime.now()
        self.sql=sql
        self.products=[]
        cur = self.mem.con.cursor()
        cur.execute(sql)
        self.lblFound.setText(self.tr("Found {0} records".format(cur.rowcount)))
        #mete a datos        
        if cur.rowcount>0:
            self.progress.reset()
            self.progress.setMinimum(0)
            self.progress.setMaximum(cur.rowcount)
            self.progress.forceShow()
            self.progress.setValue(0)
        for i in cur:
            if self.progress.wasCanceled():
                break
            else:
                self.progress.setValue(self.progress.value()+1)       
                
            inv=Product(self.mem)
            inv.init__db_row(i)
            inv.result.basic.load_from_db()
            inv.estimations_dps.load_from_db()
            self.products.append(inv)
        cur.close()     
        if len(self.products)!=0:      
            diff=datetime.datetime.now()-inicio
            print("wdgProducts > build_array: {0} ({1} cada uno)".format(str(diff), diff/len(self.products)))
        

    def build_table(self):
        inicio=datetime.datetime.now()
        self.tblInvestments.clearContents()
        self.tblInvestments.setRowCount(len(self.products))
        tachado = QtGui.QFont()
        tachado.setStrikeOut(True)        #Fuente tachada
        transfer=QIcon(":/xulpymoney/transfer.png")
        for i,  inv in enumerate(self.products):
            self.tblInvestments.setItem(i, 0, QTableWidgetItem((str(inv.id))))
            self.tblInvestments.setItem(i, 1, QTableWidgetItem(str(inv.name).upper()))
            self.tblInvestments.item(i, 1).setIcon(inv.stockexchange.country.qicon())
            self.tblInvestments.setItem(i, 2, QTableWidgetItem(inv.isin))
            self.tblInvestments.setItem(i, 3, qdatetime(inv.result.basic.last.datetime, inv.stockexchange.zone))#, self.mem.localzone.name)))
            self.tblInvestments.setItem(i, 4, inv.currency.qtablewidgetitem(inv.result.basic.last.quote, 6 ))
            self.tblInvestments.setItem(i, 5, qtpc(inv.result.basic.tpc_diario()))
            self.tblInvestments.setItem(i, 6, qtpc(inv.result.basic.tpc_anual()))
            
            if inv.estimations_dps.currentYear()==None:
                self.tblInvestments.setItem(i, 7, qtpc(None))
                self.tblInvestments.item(i, 7).setBackgroundColor( QColor(255, 182, 182))          
            else:
                self.tblInvestments.setItem(i, 7, qtpc(inv.estimations_dps.currentYear().percentage()))  
                
            if inv.active==True:#Active
                self.tblInvestments.item(i, 4).setIcon(transfer)
            if inv.obsolete==True:#Obsolete
                self.tblInvestments.item(i, 1).setFont(tachado)
   
        self.tblInvestments.clearSelection()    
        self.tblInvestments.setFocus()
        if len(self.products)!=0:      
            diff=datetime.datetime.now()-inicio
            print("wdgProducts > build_table: {0} ({1} cada uno)".format(str(diff), diff/len(self.products)))
        
    @QtCore.pyqtSlot()  
    def on_actionFavorites_activated(self):
        def wdgInvestments_esta_mostrando_favoritos(favoritos):
            """Función que comprueba el sql para ver si está mostrando wdgInvestments a Favoritos"""
            if self.sql=="select * from products where id in ("+str(favoritos)[1:-1]+") order by name, id":
                return True
            return False
            
        favoritos=self.mem.config.get_list("wdgProducts",  "favoritos")
        if str(self.selProduct.id) in favoritos:
            if wdgInvestments_esta_mostrando_favoritos(favoritos)==True:
                favoritos.remove(str(self.selProduct.id))
                if len(favoritos)==0:
                    self.sql="select * from products where id=-999999999"
                else:
                    self.sql="select * from products where id in ("+str(favoritos)[1:-1]+") order by name, id"
                self.build_array(self.sql)
                self.build_table()
        else:
            favoritos.append(self.selProduct.id)
        print ("Favoritos", favoritos)
        self.mem.config.set_list("wdgProducts",  "favoritos",  favoritos)
        self.mem.config.save()
        self.setFavoritos=set(favoritos)



    @QtCore.pyqtSlot()  
    def on_actionIbex35_activated(self):
        self.build_array("select * from products where agrupations like '%|IBEX35|%' and code not in ('EURONEXT#LU0323134006', 'EURONEXT#ES0113790531', 'EURONEXT#ES0113900J37', 'EURONEXT#ES0182870214') order by name,code")
        self.products=sorted(self.products, key=lambda row: row[2],  reverse=False) 
        self.build_table()       

    @QtCore.pyqtSlot() 
    def on_actionProductDelete_activated(self):
        if self.selProduct.deletable==False:
            m=QMessageBox()
            m.setText(self.tr("This product can't be removed, because is marked as not romavable"))
            m.exec_()    
            return

        respuesta = QMessageBox.warning(self, self.tr("Xulpymoney"), self.tr("Deleting data from selected product ({0}). If you use manual update mode, data won't be recovered. Do you want to continue?".format(self.selProduct.id)), QMessageBox.Ok | QMessageBox.Cancel)
        if respuesta==QMessageBox.Ok:
            con=self.mem.connect_xulpymoney()
            cur = con.cursor()
            cur.execute("delete from products where id=%s", (self.selProduct.id, ))
            cur.execute("delete from quotes where id=%s", (self.selProduct.id, ))
            cur.execute("delete from estimations_dps where id=%s", (self.selProduct.id, ))
            con.commit()
            cur.close()     
            self.mem.disconnect_xulpymoney(con)    
            self.build_array(self.sql)
            self.build_table()  
            
            
    @QtCore.pyqtSlot() 
    def on_actionProductEdit_activated(self):
        w=frmProductReport(self.mem, self.selProduct, None,  self)
        w.exec_()        
        self.build_array(self.sql)
        self.build_table()

    @QtCore.pyqtSlot() 
    def on_actionProductNew_activated(self):
        w=frmProductReport(self.mem, None, self)
        w.exec_()        
        self.build_array(self.sql)
        self.build_table()

    @QtCore.pyqtSlot() 
    def on_actionProductReport_activated(self):
        w=frmProductReport(self.mem, self.selProduct, None,  self)
        w.exec_()        
        self.build_array(self.sql)
        self.build_table()
        
    @QtCore.pyqtSlot() 
    def on_actionSortTPCDiario_activated(self):
        self.products=sorted(self.products, key=lambda inv: inv.result.basic.tpc_diario(),  reverse=True) 
        self.build_table()        
        
    @QtCore.pyqtSlot() 
    def on_actionSortTPCAnual_activated(self):
        self.products=sorted(self.products, key=lambda inv: inv.result.basic.tpc_anual(),  reverse=True) 
        self.build_table()    
        
    @QtCore.pyqtSlot() 
    def on_actionSortHour_activated(self):
        self.products=sorted(self.products, key=lambda inv: inv.result.basic.last.datetime,  reverse=False) 
        self.build_table()        
        
    @QtCore.pyqtSlot() 
    def on_actionSortName_activated(self):
        self.products=sorted(self.products, key=lambda inv: inv.name,  reverse=False) 
        self.build_table()        
        
    @QtCore.pyqtSlot() 
    def on_actionSortDividend_activated(self):
        self.products=sorted(self.products, key=lambda inv: inv.estimations_dps.currentYear().percentage(),  reverse=True) 
        self.build_table()        
        
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

        self.build_array("select * from products where (id::text like '%"+(self.txt.text().upper())+"%' or upper(name) like '%"+(self.txt.text().upper())+"%' or upper(isin) like '%"+(self.txt.text().upper())+"%' or upper(comentario) like '%"+(self.txt.text().upper())+"%') "+ stockexchangefilter)
        self.products=sorted(self.products, key=lambda inv: inv.name,  reverse=False) 
        self.build_table()          


    def on_tblInvestments_customContextMenuRequested(self,  pos):

        menu=QMenu()
        ordenar=QMenu(self.tr("Order by"))
        menu.addAction(self.actionProductNew)
        menu.addAction(self.actionProductEdit)
        menu.addAction(self.actionProductDelete)
        menu.addSeparator()
        menu.addAction(self.actionQuoteNew)
        menu.addAction(self.actionEstimationDPSNew)
        menu.addSeparator()
        menu.addAction(self.actionMergeCodes)
        menu.addAction(self.actionFavorites)
        if self.selProduct!=None:
            if self.selProduct.id in self.setFavoritos:
                self.actionFavorites.setText(self.tr("Remove from favorites"))
            else:
                self.actionFavorites.setText(self.tr("Add to favorites"))
        menu.addSeparator()
        menu.addAction(self.actionProductReport)
        menu.addAction(self.actionPurge)
        
        if self.mem.adminmode and self.selProduct.id<0:
            menu.addSeparator()
            menu.addAction(self.actionConvertProductToSystem)
        if self.mem.adminmode and self.selProduct.id>=0:
            menu.addSeparator()
            menu.addAction(self.actionConvertProductToUser)
        
        if self.selProduct!=None:
            if self.selProduct.id=='^IBEX':
                menu.addSeparator()
                menu.addAction(self.actionIbex35)
        menu.addSeparator()
        menu.addMenu(ordenar)
        ordenar.addAction(self.actionSortName)
        ordenar.addAction(self.actionSortHour)
        ordenar.addAction(self.actionSortTPCDiario)
        ordenar.addAction(self.actionSortTPCAnual)
        ordenar.addAction(self.actionSortDividend)
        
        #Enabled disabled  
        
        if self.selectedRows==1:
            self.actionMergeCodes.setEnabled(False)
            self.actionProductEdit.setEnabled(True)
            self.actionProductDelete.setEnabled(True)
            self.actionFavorites.setEnabled(True)
            self.actionProductReport.setEnabled(True)
            self.actionIbex35.setEnabled(True)
            self.actionQuoteNew.setEnabled(True)
            self.actionEstimationDPSNew.setEnabled(True)
            self.actionPurge.setEnabled(True)
            self.actionConvertProductToSystem.setEnabled(True)
        else:
            self.actionMergeCodes.setEnabled(False)
            self.actionProductEdit.setEnabled(False)
            self.actionProductDelete.setEnabled(False)
            self.actionFavorites.setEnabled(False)
            self.actionProductReport.setEnabled(False)
            self.actionIbex35.setEnabled(False)
            self.actionQuoteNew.setEnabled(False)
            self.actionEstimationDPSNew.setEnabled(False)
            self.actionPurge.setEnabled(False)
            self.actionConvertProductToSystem.setEnabled(False)
        
        if self.selectedRows==2:
            self.actionMergeCodes.setEnabled(True)
            
        menu.exec_(self.tblInvestments.mapToGlobal(pos))

    @QtCore.pyqtSlot() 
    def on_actionConvertProductToSystem_activated(self):
        self.selProduct.convert_to_system_product()
        self.mem.con.commit()
        self.mem.data.reload()
        self.build_table()
        
    @QtCore.pyqtSlot() 
    def on_actionConvertProductToUser_activated(self):
        self.selProduct.convert_to_user_product()
        self.mem.con.commit()
        self.mem.data.reload()
        self.build_table()
        
        
    @QtCore.pyqtSlot() 
    def on_actionMergeCodes_activated(self):
        #Saca codeorigen y codedestino        
        selected=[]
        for i in self.tblInvestments.selectedItems():
            if i.column()==0:
                selected.append(self.products[i.row()])
        print (selected)
        

        #Llama a form
        d=QDialog(self)        
        d.setFixedSize(800, 210)
        d.setWindowTitle(self.tr("Merging codes"))
        w=wdgMergeCodes(self.mem, selected[0], selected[1])
        lay = QVBoxLayout(d)
        lay.addWidget(w)
        d.exec_()
        self.build_array(self.sql)
        self.build_table()

    
    def on_tblInvestments_itemSelectionChanged(self):
        #Saca número de filas seleccionadas
        setrows=set([])
        for i in self.tblInvestments.selectedItems():
            setrows.add( i.row())
        self.selectedRows=len(setrows)
        
        if self.selectedRows==1:
            for i in self.tblInvestments.selectedItems():#itera por cada item no row.
                self.selProduct=self.products[i.row()]

    @QtCore.pyqtSlot()  
    def on_actionPurge_activated(self):
        all=SetQuotesAll(self.mem)
        all.load_from_db(self.selProduct)
        numpurged=all.purge(progress=True)
        if numpurged!=None:#Canceled
            self.mem.con.commit()
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.tr("{0} quotes have been purged from {1}".format(numpurged, self.selProduct.name)))
            m.exec_()    
        else:
            self.mem.con.rollback()
        

    @QtCore.pyqtSlot()  
    def on_actionQuoteNew_activated(self):
        w=frmQuotesIBM(self.mem,  self.selProduct)
        w.exec_()               
        self.build_array(self.sql)
        self.build_table()  

    @QtCore.pyqtSlot()  
    def on_actionEstimationDPSNew_activated(self):
        d=frmEstimationsAdd(self.mem, self.selProduct, "dps")
        d.exec_()
        if d.result()==QDialog.Accepted:
            self.build_array(self.sql)
            self.build_table()  
            
