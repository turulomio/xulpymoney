from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Ui_wdgProducts import *
from frmAnalisis import *
from libxulpymoney import *
from frmQuotesIBM import *
from wdgMergeCodes import *
from frmEstimationsAdd import *

class wdgProducts(QWidget, Ui_wdgProducts):
    def __init__(self, cfg,  sql,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.cfg=cfg
        self.products=[]#Es una lista de products
        self.selProduct=None##Objeto de inversion seleccionado
        self.tblInversiones.settings("wdgProducts",  self.cfg)    
        self.cfg.bolsas.load_qcombobox(self.cmbStockExchange)
        self.setFavoritos=set(self.cfg.config.get_list( "wdgProducts", "favoritos"))
        self.progress = QProgressDialog(self.tr("Recibiendo datos solicitados"), self.tr("Cancelar"), 0,0)
        self.progress.setModal(True)
        self.progress.setWindowTitle(self.trUtf8("Recibiendo datos..."))
        self.progress.setMinimumDuration(0)                

        self.build_array(sql)
        self.build_table()
        self.selectedRows=0
    
    def build_array(self, sql):
        inicio=datetime.datetime.now()
        self.sql=sql
        self.products=[]
        cur = self.cfg.conms.cursor()
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
                
            inv=Product(self.cfg)
            inv.init__db_row(i)
            inv.result.basic.load_from_db()
            inv.estimations_dps.load_from_db()
            self.products.append(inv)
        cur.close()     
        if len(self.products)!=0:      
            diff=datetime.datetime.now()-inicio
            print("wdgProducts > build_array: {0} ({1} cada uno)".format(str(diff), diff/len(self.products)))
        

    def build_table(self):
        self.tblInversiones.setRowCount(len(self.products))
        tachado = QtGui.QFont()
        tachado.setStrikeOut(True)        #Fuente tachada
        for i,  inv in enumerate(self.products):
            self.tblInversiones.setItem(i, 0, QTableWidgetItem((str(inv.id))))
            self.tblInversiones.setItem(i, 1, QTableWidgetItem(str(inv.name).upper()))
            self.tblInversiones.item(i, 1).setIcon(inv.bolsa.country.qicon())
            self.tblInversiones.setItem(i, 2, QTableWidgetItem(inv.isin))
            self.tblInversiones.setItem(i, 3, qdatetime(inv.result.basic.last.datetime, inv.bolsa.zone))#, self.cfg.localzone.name)))
            self.tblInversiones.setItem(i, 4, inv.currency.qtablewidgetitem(inv.result.basic.last.quote, 6 ))
            self.tblInversiones.setItem(i, 5, qtpc(inv.result.basic.tpc_diario()))
            self.tblInversiones.setItem(i, 6, qtpc(inv.result.basic.tpc_anual()))
            
            
            if inv.estimations_dps.currentYear()==None:
                self.tblInversiones.setItem(i, 7, qtpc(None))
                self.tblInversiones.item(i, 7).setBackgroundColor( QColor(255, 182, 182))          
            else:
                self.tblInversiones.setItem(i, 7, qtpc(inv.estimations_dps.currentYear().percentage()))  
                
            if inv.active==True:#Active
                self.tblInversiones.item(i, 4).setIcon(QIcon(":/xulpymoney/transfer.png"))
            if inv.obsolete==True:#Obsolete
                self.tblInversiones.item(i, 1).setFont(tachado)
   
        self.tblInversiones.clearSelection()    
        self.tblInversiones.setFocus()
        
    @QtCore.pyqtSlot()  
    def on_actionFavoritos_activated(self):
        def wdgInversiones_esta_mostrando_favoritos(favoritos):
            """Función que comprueba el sql para ver si está mostrando wdgInversiones a Favoritos"""
            if self.sql=="select * from products where id in ("+str(favoritos)[1:-1]+") order by name, id":
                return True
            return False
            
        favoritos=self.cfg.config.get_list("wdgProducts",  "favoritos")
        if str(self.selProduct.id) in favoritos:
            if wdgInversiones_esta_mostrando_favoritos(favoritos)==True:
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
        self.cfg.config.set_list("wdgProducts",  "favoritos",  favoritos)
        self.cfg.config.save()
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
            m.setText(QApplication.translate("mystocks","Esta inversión no puede borrarse porque está marcada como NO BORRABLE"))
            m.exec_()    
            return

        respuesta = QMessageBox.warning(self, self.tr("MyStocks"), self.trUtf8("Deleting data from selected product ({0}). If you use manual update mode, data won't be recovered. Do you want to continue?".format(self.selProduct.id)), QMessageBox.Ok | QMessageBox.Cancel)
        if respuesta==QMessageBox.Ok:
            con=self.cfg.connect_mystocks()
            cur = con.cursor()
            cur.execute("delete from products where id=%s", (self.selProduct.id, ))
            cur.execute("delete from quotes where id=%s", (self.selProduct.id, ))
            cur.execute("delete from estimaciones where id=%s", (self.selProduct.id, ))
            con.commit()
            cur.close()     
            self.cfg.disconnect_mystocks(con)    
            self.build_array(self.sql)
            self.build_table()  
            
            
    @QtCore.pyqtSlot() 
    def on_actionProductEdit_activated(self):
        self.on_actionProductReport_activated()


    @QtCore.pyqtSlot() 
    def on_actionProductNew_activated(self):
        w=frmAnalisis(self.cfg, None, self)
        w.exec_()        
        self.build_array(self.sql)
        self.build_table()
    @QtCore.pyqtSlot() 
    def on_actionProductReport_activated(self):

        w=frmAnalisis(self.cfg, self.selProduct, None,  self)
        w.exec_()        
        self.build_array(self.sql)
        self.build_table()
#        w.mytimer.stop()
        
    @QtCore.pyqtSlot() 
    def on_actionOrdenarTPCDiario_activated(self):
        self.products=sorted(self.products, key=lambda inv: inv.result.basic.tpc_diario(),  reverse=True) 
        self.build_table()        
        
    @QtCore.pyqtSlot() 
    def on_actionOrdenarTPCAnual_activated(self):
        self.products=sorted(self.products, key=lambda inv: inv.result.basic.tpc_anual(),  reverse=True) 
        self.build_table()    
        
    @QtCore.pyqtSlot() 
    def on_actionOrdenarHora_activated(self):
        self.products=sorted(self.products, key=lambda inv: inv.result.basic.last.datetime,  reverse=False) 
        self.build_table()        
        
    @QtCore.pyqtSlot() 
    def on_actionOrdenarName_activated(self):
        self.products=sorted(self.products, key=lambda inv: inv.name,  reverse=False) 
        self.build_table()        
        
    @QtCore.pyqtSlot() 
    def on_actionOrdenarDividend_activated(self):
        self.products=sorted(self.products, key=lambda inv: inv.estimations_dps.currentYear().percentage(),  reverse=True) 
        self.build_table()        
        
    def on_txt_returnPressed(self):
        self.on_cmd_pressed()
        
    def on_cmd_pressed(self):
        if len(self.txt.text().upper())<=3:            
            m=QMessageBox()
            m.setText(self.trUtf8("Búsqueda demasiado extensa. Necesita más de 3 caracteres"))
            m.exec_()  
            return
            
        #Stock exchange Filter
        stockexchangefilter=""
        if self.chkStockExchange.checkState()==Qt.Checked:
            bolsa=self.cfg.bolsas.find(self.cmbStockExchange.itemData(self.cmbStockExchange.currentIndex()))            
            stockexchangefilter=" and id_bolsas={0} ".format(bolsa.id)

        self.build_array("select * from products where (id::text like '%"+(self.txt.text().upper())+"%' or upper(name) like '%"+(self.txt.text().upper())+"%' or upper(isin) like '%"+(self.txt.text().upper())+"%' or upper(comentario) like '%"+(self.txt.text().upper())+"%') "+ stockexchangefilter)
        self.products=sorted(self.products, key=lambda inv: inv.name,  reverse=False) 
        self.build_table()          


    def on_tblInversiones_customContextMenuRequested(self,  pos):

        menu=QMenu()
        ordenar=QMenu(self.tr("Ordenar por"))
        menu.addAction(self.actionProductNew)
        menu.addAction(self.actionProductEdit)
        menu.addAction(self.actionProductDelete)
        menu.addSeparator()
        menu.addAction(self.actionQuoteNew)
        menu.addAction(self.actionEstimationDPSNew)
        menu.addSeparator()
        menu.addAction(self.actionMergeCodes)
        menu.addAction(self.actionFavoritos)
        if self.selProduct!=None:
            if self.selProduct.id in self.setFavoritos:
                self.actionFavoritos.setText("Quitar de favoritos")
            else:
                self.actionFavoritos.setText(self.trUtf8("Añadir a favoritos"))
        menu.addSeparator()
        menu.addAction(self.actionProductReport)
        menu.addAction(self.actionPurge)
        
        if self.selProduct!=None:
            if self.selProduct.id=='^IBEX':
                menu.addSeparator()
                menu.addAction(self.actionIbex35)
        menu.addSeparator()
        menu.addMenu(ordenar)
        ordenar.addAction(self.actionOrdenarName)
        ordenar.addAction(self.actionOrdenarHora)
        ordenar.addAction(self.actionOrdenarTPCDiario)
        ordenar.addAction(self.actionOrdenarTPCAnual)
        ordenar.addAction(self.actionOrdenarDividend)
        
        #Enabled disabled  
        
        if self.selectedRows==1:
            self.actionMergeCodes.setEnabled(False)
            self.actionProductEdit.setEnabled(True)
            self.actionProductDelete.setEnabled(True)
            self.actionFavoritos.setEnabled(True)
            self.actionProductReport.setEnabled(True)
            self.actionIbex35.setEnabled(True)
            self.actionQuoteNew.setEnabled(True)
            self.actionEstimationDPSNew.setEnabled(True)
        else:
            self.actionMergeCodes.setEnabled(False)
            self.actionProductEdit.setEnabled(False)
            self.actionProductDelete.setEnabled(False)
            self.actionFavoritos.setEnabled(False)
            self.actionProductReport.setEnabled(False)
            self.actionIbex35.setEnabled(False)
            self.actionQuoteNew.setEnabled(False)
            self.actionEstimationDPSNew.setEnabled(False)
        
        if self.selectedRows==2:
            self.actionMergeCodes.setEnabled(True)
            
        menu.exec_(self.tblInversiones.mapToGlobal(pos))

    @QtCore.pyqtSlot() 
    def on_actionMergeCodes_activated(self):
        #Saca codeorigen y codedestino        
        setrows=set([])
        for i in self.tblInversiones.selectedItems():
            setrows.add((self.tblInversiones.item(i.row(), 0).text()))
        setrows=list(setrows)
        codeorigen=setrows[0]
        codedestino=setrows[1]
        

        #Llama a form
        d=QDialog(self)        
        d.setFixedSize(800, 210)
        d.setWindowTitle(self.trUtf8("Combinando códigos"))
        w=wdgMergeCodes(self.cfg, codeorigen, codedestino)
        lay = QVBoxLayout(d)
        lay.addWidget(w)
        d.exec_()
        self.build_array(self.sql)
        self.build_table()

    
    def on_tblInversiones_itemSelectionChanged(self):
        #Saca número de filas seleccionadas
        setrows=set([])
        for i in self.tblInversiones.selectedItems():
            setrows.add( i.row())
        self.selectedRows=len(setrows)
        
        if self.selectedRows==1:
            for i in self.tblInversiones.selectedItems():#itera por cada item no row.
                self.selProduct=self.products[i.row()]

    @pyqtSignature("")
    def on_actionPurge_activated(self):
        all=SetQuotesAll(self.cfg)
        all.load_from_db(self.selProduct)
        numpurged=all.purge(progress=True)
        if numpurged!=None:#Canceled
            self.cfg.conms.commit()
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.trUtf8("{0} quotes have been purged from {1}".format(numpurged, self.selProduct.name)))
            m.exec_()    
        else:
            self.cfg.conms.rollback()
        

    @pyqtSignature("")
    def on_actionQuoteNew_activated(self):
        w=frmQuotesIBM(self.cfg,  self.selProduct)
        w.exec_()               
        self.build_array(self.sql)
        self.build_table()  

    @pyqtSignature("")
    def on_actionEstimationDPSNew_activated(self):
        d=frmEstimationsAdd(self.cfg, self.selProduct)
        d.exec_()
        if d.result()==QDialog.Accepted:
            self.build_array(self.sql)
            self.build_table()  
            
