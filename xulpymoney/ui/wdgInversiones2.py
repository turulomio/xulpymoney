from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Ui_wdgInversiones2 import *
from frmAnalisis import *
from libxulpymoney import *
from frmQuotesIBM import *
from wdgMergeCodes import *
from frmDividendoEstimacionIBM import *

class wdgInversiones2(QWidget, Ui_wdgInversiones2):
    def __init__(self, cfg,  sql,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.cfg=cfg
        self.inversionesmq=[]#Es una lista de inversionesmq
        self.selInvestment=None##Objeto de inversion seleccionado
        self.tblInversiones.setColumnHidden(0, True)
        self.tblInversiones.settings("wdgInversiones",  self.cfg.inifile)    
        self.setFavoritos=set(list_loadprops(self.cfg.inifile, "wdgInversiones", "favoritos"))
        self.progress = QProgressDialog(self.tr("Recibiendo datos solicitados"), self.tr("Cancelar"), 0,0)
        self.progress.setModal(True)
        self.progress.setWindowTitle(self.trUtf8("Recibiendo datos..."))
        self.progress.setMinimumDuration(0)                

        self.build_array(sql)
        self.build_table()
        self.selectedRows=0
#        self.selInvestment.id=""
    
    def build_array(self, sql):
        inicio=datetime.datetime.now()
        self.sql=sql
        self.inversionesmq=[]
        con=self.cfg.connect_myquotes()
        cur = con.cursor()
        cur.execute(sql)
        cur2=con.cursor()
        self.lblFound.setText(self.tr("Encontrados {0} registros".format(cur.rowcount)))
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
                
            inv=Investment(self.cfg)
            inv.init__db_row(i)
            inv.quotes.get_basic(cur2)
            self.inversionesmq.append(inv)
        cur.close()     
        cur2.close()
        self.cfg.disconnect_myquotesd(con)   
        if len(self.inversionesmq)!=0:      
            diff=datetime.datetime.now()-inicio
            print("wdgInversiones > build_array: {0} ({1} cada uno)".format(str(diff), diff/len(self.inversionesmq)))
        

    def build_table(self):
        self.tblInversiones.setRowCount(len(self.inversionesmq))
        #mete a datos
        i=0
        gris = QtGui.QBrush(QtGui.QColor(160, 160, 160))
        gris.setStyle(QtCore.Qt.NoBrush)
                    
        tachado = QtGui.QFont()
        tachado.setStrikeOut(True)        #Fuente tachada
        for inv in self.inversionesmq:
#            bolsa=self.cfg.bolsas[str(inv.id_bolsas)]
            self.tblInversiones.setItem(i, 0, QTableWidgetItem((str(inv.id))))
            self.tblInversiones.setItem(i, 1, QTableWidgetItem(str(inv.name).upper()))
            self.tblInversiones.item(i, 1).setIcon(inv.bolsa.country.qicon())
            self.tblInversiones.setItem(i, 2, QTableWidgetItem(inv.isin))
            self.tblInversiones.setItem(i, 3, qdatetime(inv.quotes.last.datetime))#, config.localzone)))
            self.tblInversiones.setItem(i, 4, inv.currency.qtablewidgetitem(inv.quotes.last.quote, 6 ))
            self.tblInversiones.setItem(i, 5, qtpc(inv.quotes.tpc_diario()))
            self.tblInversiones.setItem(i, 6, qtpc(inv.quotes.tpc_anual()))
            self.tblInversiones.setItem(i, 7, qtpc(inv.quotes.lastdpa))
            if inv.quotes.lastdpa==None:#dividendo
                self.tblInversiones.item(i, 7).setBackgroundColor( QColor(255, 182, 182))          
            if inv.active==False:#Active
                for j in range(8):
                    self.tblInversiones.item(i, j).setForeground(gris)
            if inv.obsolete==True:#Obsolete
                self.tblInversiones.item(i, 1).setFont(tachado)
            i=i+1        
        self.tblInversiones.clearSelection()    
        self.tblInversiones.setFocus()
        
    @QtCore.pyqtSlot()  
    def on_actionFavoritos_activated(self):
        def wdgInversiones_esta_mostrando_favoritos(favoritos):
            """Función que comprueba el sql para ver si está mostrando wdgInversiones a Favoritos"""
            if self.sql=="select * from investments where id in ("+str(favoritos)[1:-1]+") order by name, id":
                return True
            return False
            
        favoritos=list_loadprops(self.cfg.inifile,"wdgInversiones",  "favoritos")
        print (favoritos)
        if str(self.selInvestment.id) in favoritos:
            if wdgInversiones_esta_mostrando_favoritos(favoritos)==True:
                favoritos.remove(self.selInvestment.id)
                self.sql="select * from investments where id in ("+str(favoritos)[1:-1]+") order by name, id"
                self.build_array(self.sql)
                self.build_table()
        else:
            favoritos.append(self.selInvestment.id)
        list_saveprops(self.cfg.inifile,"wdgInversiones",  "favoritos",  favoritos)
        self.setFavoritos=set(favoritos)



    @QtCore.pyqtSlot()  
    def on_actionIbex35_activated(self):
        self.build_array("select * from investments where agrupations like '%|IBEX35|%' and code not in ('EURONEXT#LU0323134006', 'EURONEXT#ES0113790531', 'EURONEXT#ES0113900J37', 'EURONEXT#ES0182870214') order by name,code")
        self.inversionesmq=sorted(self.inversionesmq, key=lambda row: row[2],  reverse=False) 
        self.build_table()       

    @QtCore.pyqtSlot() 
    def on_actionInversionBorrar_activated(self):
        if self.selInvestment.deletable==False:
            m=QMessageBox()
            m.setText(QApplication.translate("myquotes","Esta inversión no puede borrarse porque está marcada como NO BORRABLE"))
            m.exec_()    
            return

        respuesta = QMessageBox.warning(self, self.tr("MyQuotes"), self.trUtf8("Se borrarán los datos de la inversión seleccionada ({0}). Tenga en cuenta que si es el tipo de actualización es manual, no recuperará los datos. ¿Quiere continuar?".format(self.selInvestment.id)), QMessageBox.Ok | QMessageBox.Cancel)
        if respuesta==QMessageBox.Ok:
            con=self.cfg.connect_myquotes()
            cur = con.cursor()
            cur.execute("delete from investments where id=%s", (self.selInvestment.id, ))
            cur.execute("delete from quotes where id=%s", (self.selInvestment.id, ))
            cur.execute("delete from estimaciones where id=%s", (self.selInvestment.id, ))
            con.commit()
            cur.close()     
            self.cfg.disconnect_myquotes(con)    
            self.build_array(self.sql)
            self.build_table()  
            
            
    @QtCore.pyqtSlot() 
    def on_actionInversionModificar_activated(self):
        self.on_actionInversionEstudio_activated()


    @QtCore.pyqtSlot() 
    def on_actionInversionNueva_activated(self):
        w=frmAnalisis(self.cfg, None, self)
        w.exec_()        
        self.build_array(self.sql)
        self.build_table()
        
    @QtCore.pyqtSlot() 
    def on_actionInversionEstudio_activated(self):
        w=frmAnalisis(self.cfg, self.selInvestment, self)
        w.load_data_from_db()
        w.exec_()        
        self.build_array(self.sql)
        self.build_table()
        w.mytimer.stop()
        
    @QtCore.pyqtSlot() 
    def on_actionOrdenarTPCDiario_activated(self):
        self.inversionesmq=sorted(self.inversionesmq, key=lambda inv: inv.quotes.tpc_diario(),  reverse=True) 
        self.build_table()        
        
    @QtCore.pyqtSlot() 
    def on_actionOrdenarTPCAnual_activated(self):
        self.inversionesmq=sorted(self.inversionesmq, key=lambda inv: inv.quotes.tpc_anual(),  reverse=True) 
        self.build_table()    
        
    @QtCore.pyqtSlot() 
    def on_actionOrdenarHora_activated(self):
        self.inversionesmq=sorted(self.inversionesmq, key=lambda inv: inv.quotes.last.datetime,  reverse=False) 
        self.build_table()        
        
    @QtCore.pyqtSlot() 
    def on_actionOrdenarName_activated(self):
        self.inversionesmq=sorted(self.inversionesmq, key=lambda inv: inv.name,  reverse=False) 
        self.build_table()        
        
    @QtCore.pyqtSlot() 
    def on_actionOrdenarDividendo_activated(self):
        self.inversionesmq=sorted(self.inversionesmq, key=lambda inv: inv.quotes.tpc_dpa(),  reverse=True) 
        self.build_table()        
        
    def on_txt_returnPressed(self):
        self.on_cmd_pressed()
        
    def on_cmd_pressed(self):
        if len(self.txt.text().upper())<=3:            
            m=QMessageBox()
            m.setText(self.trUtf8("Búsqueda demasiado extensa. Necesita más de 3 caracteres"))
            m.exec_()  
            return
            
        self.build_array("select * from investments where id::text like '%"+(self.txt.text().upper())+"%' or upper(name) like '%"+(self.txt.text().upper())+"%' or upper(isin) like '%"+(self.txt.text().upper())+"%' or upper(comentario) like '%"+(self.txt.text().upper())+"%' ")
        self.inversionesmq=sorted(self.inversionesmq, key=lambda inv: inv.name,  reverse=False) 
        self.build_table()          


    def on_tblInversiones_customContextMenuRequested(self,  pos):

        menu=QMenu()
        ordenar=QMenu(self.tr("Ordenar por"))
        menu.addAction(self.actionInversionNueva)
        menu.addAction(self.actionInversionModificar)
        menu.addAction(self.actionInversionBorrar)
        menu.addSeparator()
        menu.addAction(self.actionQuoteNew)
        menu.addAction(self.actionDividendoEstimacionNueva)
        menu.addSeparator()
        menu.addAction(self.actionMergeCodes)
        menu.addAction(self.actionFavoritos)
        if self.selInvestment!=None:
            if self.selInvestment.id in self.setFavoritos:
                self.actionFavoritos.setText("Quitar de favoritos")
            else:
                self.actionFavoritos.setText(self.trUtf8("Añadir a favoritos"))
        menu.addSeparator()
        menu.addAction(self.actionInversionEstudio)
        if self.selInvestment!=None:
            if self.selInvestment.id=='^IBEX':
                menu.addSeparator()
                menu.addAction(self.actionIbex35)
        menu.addSeparator()
        menu.addMenu(ordenar)
        ordenar.addAction(self.actionOrdenarName)
        ordenar.addAction(self.actionOrdenarHora)
        ordenar.addAction(self.actionOrdenarTPCDiario)
        ordenar.addAction(self.actionOrdenarTPCAnual)
        ordenar.addAction(self.actionOrdenarDividendo)
        
        #Enabled disabled  
        
        if self.selectedRows==1:
            self.actionMergeCodes.setEnabled(False)
            self.actionInversionModificar.setEnabled(True)
            self.actionInversionBorrar.setEnabled(True)
            self.actionFavoritos.setEnabled(True)
            self.actionInversionEstudio.setEnabled(True)
            self.actionIbex35.setEnabled(True)
            self.actionQuoteNew.setEnabled(True)
            self.actionDividendoEstimacionNueva.setEnabled(True)
        else:
            self.actionMergeCodes.setEnabled(False)
            self.actionInversionModificar.setEnabled(False)
            self.actionInversionBorrar.setEnabled(False)
            self.actionFavoritos.setEnabled(False)
            self.actionInversionEstudio.setEnabled(False)
            self.actionIbex35.setEnabled(False)
            self.actionQuoteNew.setEnabled(False)
            self.actionDividendoEstimacionNueva.setEnabled(False)
        
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
#                self.selInvestment.id=(self.tblInversiones.item(i.row(), 0).text())
                self.selInvestment=self.inversionesmq[i.row()]

    @pyqtSignature("")
    def on_actionQuoteNew_activated(self):
        w=frmQuotesIBM(self.cfg,  self.selInvestment)
        w.exec_()               
        self.build_array(self.sql)
        self.build_table()  

    @pyqtSignature("")
    def on_actionDividendoEstimacionNueva_activated(self):
        d=frmDividendoEstimacionIBM(self.cfg, self.selInvestment)
        d.exec_()
        if d.result()==QDialog.Accepted:
            self.build_array(self.sql)
            self.build_table()  
            
