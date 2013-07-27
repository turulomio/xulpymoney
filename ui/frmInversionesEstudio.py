from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Ui_frmInversionesEstudio import *
from frmInversionesIBM import *
from frmDividendosIBM import *
from frmPuntoVenta import *
from wdgDesReinversion import *
from frmTraspasoValores import *
from libxulpymoney import *

class frmInversionesEstudio(QDialog, Ui_frmInversionesEstudio):
    def __init__(self, cfg, cuentas, inversiones,  investments,  selInversion=None,  parent=None):
        """Cuentas es un set cuentas"""
        """TIPOS DE ENTRADAS:        
         1   : Inserción de Opercuentas
         2   selInversion=x"""
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.showMaximized()
        self.cfg=cfg
        self.data_cuentas=cuentas
        self.data_inversiones=inversiones
        self.data_investments=investments##Para modificar investments
        self.selInversion=selInversion
        
        self.indicereferencia=Investment(self.cfg).init__db(self.cfg.config.get("settings", "indicereferencia" ))
        self.indicereferencia.quotes.get_basic()
#        self.currentIndex=79329
        self.selDividendo=None#Dividendo seleccionado
        
        #arrays asociados a tablas
        self.op=[]#Necesario porque puede acortarse el original
        self.dividendos=[]#Necesario porque pueden visualizarse o no historicos
        
        self.ise.setupUi(self.cfg)
        
        if selInversion==None:
            self.tipo=1
            self.cmdInversion.setText(self.trUtf8("Añadir una nueva inversión"))
            self.lblTitulo.setText(self.trUtf8("Nueva inversión"))
            self.selInversion=None
            self.tab.setCurrentIndex(0)
            self.tabDividendos.setEnabled(False)
            self.tabOperacionesHistoricas.setEnabled(False)
            self.tabInversionActual.setEnabled(False)
            self.ise.setSelected(None)
            self.cmdPuntoVenta.setEnabled(False)
        else:
            self.tipo=2    
            self.cmbCuenta.setEnabled(False)
            self.tab.setCurrentIndex(1)
            self.lblTitulo.setText((self.selInversion.name))
            self.txtInversion.setText((self.selInversion.name))
            self.txtVenta.setText(str((self.selInversion.venta)))
            self.ise.setSelected(self.selInversion.mq)
            self.cmdPuntoVenta.setEnabled(True)

#        self.tblOperaciones.settings("frmInversionesEstudio",  self.cfg.file_ui)
#        self.tblOperaciones.setColumnHidden(0, True)    
        self.tblInversionHistorica.settings("frmInversionesEstudio",  self.cfg.file_ui)
        self.tblDividendos.settings("frmInversionesEstudio",  self.cfg.file_ui)
        
        self.data_cuentas.load_qcombobox(self.cmbCuenta)

        if self.tipo==2:
            self.cmbCuenta.setCurrentIndex(self.cmbCuenta.findData(self.selInversion.cuenta.id))
            self.selMovimiento=0
            self.on_chkOperaciones_stateChanged(Qt.Unchecked)
            self.update_tables()
 

        self.cmdInversion.setEnabled(False)                                                                                                                                                                                            
        self.connect(self.ise.cmd,SIGNAL('released()'),  self.on_cmdISE_released)            

    def load_tblDividendos(self):        

        self.tblDividendos.setRowCount(len(self.dividendos)+1)
        sumneto=0
        sumbruto=0
        sumretencion=0
        sumcomision=0
        for i, d in enumerate(self.dividendos):
            sumneto=sumneto+d.neto
            sumbruto=sumbruto+d.bruto
            sumretencion=sumretencion+d.retencion
            sumcomision=sumcomision+d.comision
            self.tblDividendos.setItem(i, 0, QTableWidgetItem(str(d.fecha)))
            self.tblDividendos.setItem(i, 1, QTableWidgetItem(str(d.opercuenta.concepto.name)))
            self.tblDividendos.setItem(i, 2, self.selInversion.mq.currency.qtablewidgetitem(d.bruto))
            self.tblDividendos.setItem(i, 3, self.selInversion.mq.currency.qtablewidgetitem(d.retencion))
            self.tblDividendos.setItem(i, 4, self.selInversion.mq.currency.qtablewidgetitem(d.comision))
            self.tblDividendos.setItem(i, 5, self.selInversion.mq.currency.qtablewidgetitem(d.neto))
            self.tblDividendos.setItem(i, 6, self.selInversion.mq.currency.qtablewidgetitem(d.dpa))
        self.tblDividendos.setItem(len(self.dividendos), 1, QTableWidgetItem("TOTAL"))
        self.tblDividendos.setItem(len(self.dividendos), 2, self.selInversion.mq.currency.qtablewidgetitem(sumbruto))
        self.tblDividendos.setItem(len(self.dividendos), 3, self.selInversion.mq.currency.qtablewidgetitem(sumretencion))
        self.tblDividendos.setItem(len(self.dividendos), 4, self.selInversion.mq.currency.qtablewidgetitem(sumcomision))
        self.tblDividendos.setItem(len(self.dividendos), 5, self.selInversion.mq.currency.qtablewidgetitem(sumneto))
        
        if self.chkDividendosHistoricos.checkState()==Qt.Unchecked:
            if len(self.dividendos)>0:
                importeinvertido=self.selInversion.invertido()
                dias=(datetime.date.today()-self.selInversion.op_actual.datetime_primera_operacion().date()).days+1
                dtpc=100*sumbruto/importeinvertido
                dtae=365*dtpc/abs(dias)
            else:
                dtpc=0
                dtae=0

            estimacion=self.selInversion.mq.estimaciones[str(datetime.date.today().year)]
            acciones=self.selInversion.acciones()
            tpccalculado=100*estimacion.dpa/self.selInversion.mq.quotes.last.quote
            self.lblDivAnualEstimado.setText(("El dividendo anual estimado, según el valor actual de la acción es del {0} % ({1}€ por acción)".format(str(round(tpccalculado, 2)),  str(estimacion.dpa))))
            self.lblDivFechaRevision.setText(('Fecha de la última revisión del dividendo: '+ str(estimacion.fechaestimacion)))
            self.lblDivSaldoEstimado.setText(("Saldo estimado: {0}€ ({1}€ después de impuestos)".format( str(round(acciones*estimacion.dpa, 2)),  str(round(acciones*estimacion.dpa*(1-self.cfg.dividendwithholding))), 2)))
            self.lblDivTPC.setText(("% de lo invertido: "+tpc(dtpc)))
            self.lblDivTAE.setText(("% TAE de lo invertido: "+tpc(dtae)))        
            self.grpDividendosEstimacion.show()
            self.grpDividendosEfectivos.show()
        else:
            self.grpDividendosEstimacion.hide()
            self.grpDividendosEfectivos.hide()
       
    def on_chkOperaciones_stateChanged(self, state):
        if state==Qt.Unchecked:
            self.op=self.selInversion.op.clone_from_datetime(self.selInversion.op_actual.datetime_primera_operacion())
        else:
            self.op=self.selInversion.op
        self.op.load_myqtablewidget(self.tblOperaciones, "frmInversionesEstudio")
            
        
    def update_tables(self):             
        #Actualiza el indice de referencia porque ha cambiado
        self.selInversion.op_actual.get_valor_indicereferencia(self.indicereferencia)
        self.on_chkOperaciones_stateChanged(self.chkOperaciones.checkState())
        self.selInversion.op_actual.load_myqtablewidget(self.tblInversionActual,  "frmInversionesEstudio")
        self.selInversion.op_historica.load_myqtablewidget(self.tblInversionHistorica,  "frmInversionesEstudio"  )
        self.on_chkDividendosHistoricos_stateChanged(self.chkDividendosHistoricos.checkState())
    

    @QtCore.pyqtSlot() 
    def on_actionDividendoNuevo_activated(self):
        w=frmDividendosIBM(self.cfg, self.selInversion,  None)
        w.exec_()
        self.on_chkDividendosHistoricos_stateChanged(self.chkDividendosHistoricos.checkState())
        self.load_tblDividendos() 
        
    @QtCore.pyqtSlot() 
    def on_actionDividendoModificar_activated(self):
        w=frmDividendosIBM(self.cfg, self.selInversion, self.selDividendo)
        w.exec_()
        self.on_chkDividendosHistoricos_stateChanged(self.chkDividendosHistoricos.checkState())
        self.load_tblDividendos() 
        
    @QtCore.pyqtSlot() 
    def on_actionDividendoBorrar_activated(self):
        con=self.cfg.connect_xulpymoney()
        cur = con.cursor()
        self.selDividendo.borrar(cur)
        con.commit()
        cur.close()      
        self.cfg.disconnect_xulpymoney(con)     
        self.on_chkDividendosHistoricos_stateChanged(self.chkDividendosHistoricos.checkState())
        self.load_tblDividendos() 
                
    @QtCore.pyqtSlot() 
    def on_actionDesReinversion_activated(self):
        #Llama a form
        d=QDialog(self)       
        d.showMaximized() 
        d.setWindowTitle(self.trUtf8("Simulación de Desinversión / Reinversión"))
        w=wdgDesReinversion(self.cfg, self.selInversion)
        lay = QVBoxLayout(d)
        lay.addWidget(w)
        d.exec_()
        
    @QtCore.pyqtSlot() 
    def on_actionMovimientoNuevo_activated(self):
        w=frmInversionesIBM(self.cfg, self.selInversion, None, self)
        w.exec_()
        self.update_tables()    
        
    @QtCore.pyqtSlot() 
    def on_actionMovimientoModificar_activated(self):
        w=frmInversionesIBM(self.cfg, self.selInversion, self.selMovimiento, self)
        w.exec_()
        self.update_tables() 

                        
    @QtCore.pyqtSlot() 
    def on_actionTraspasoValores_activated(self):

        w=frmTraspasoValores(self.cfg, self.selInversion, self)
        w.exec_()
        self.update_tables()                               
    @QtCore.pyqtSlot() 
    def on_actionDeshacerTraspasoValores_activated(self):
        if self.cfg.inversiones.traspaso_valores_deshacer(self.selMovimiento)==False:
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.trUtf8("No se ha podiddo deshacer el traspaso de valores"))
            m.exec_()          
            return
        self.update_tables()       

    @QtCore.pyqtSlot() 
    def on_cmdPuntoVenta_released(self):
        f=frmPuntoVenta(self.cfg, self.selInversion)
        f.exec_()
        self.txtVenta.setText(str(f.puntoventa))

    @QtCore.pyqtSlot() 
    def on_actionMovimientoBorrar_activated(self):
        con=self.cfg.connect_xulpymoney()
        cur = con.cursor()      
        cur2 = con.cursor()  
        self.selMovimiento.borrar(cur, cur2)
        con.commit()
        cur.close()     
        cur2.close()     
        self.cfg.disconnect_xulpymoney(con)             
        self.update_tables()

    def on_chkDividendosHistoricos_stateChanged(self, state):
        self.dividendos=[]
        fechapo=self.selInversion.op_actual.datetime_primera_operacion()
        if fechapo==None and self.chkDividendosHistoricos.checkState()==Qt.Unchecked:
            self.load_tblDividendos()
            return
            
        con=self.cfg.connect_xulpymoney()
        cur = con.cursor()        
        cur2=con.cursor()
        self.tblDividendos.clearSelection()
        self.selDividendo=None        

        if state==Qt.Unchecked:   
            strfechapo=" and fecha >='{0}' ".format(fechapo.date())
        else:
            strfechapo=""  
        sql="select * from dividendos where dividendos.id_inversiones="+str(self.selInversion.id) + strfechapo+" order by fecha;"
        cur.execute(sql) 
        for d in cur:
            cur2.execute("select * from opercuentas where id_opercuentas=%s", (d['id_opercuentas'], ))
            oc=cur2.fetchone()
            opercuenta=CuentaOperacion(self.cfg).init__db_row( oc, self.cfg.conceptos.find(oc['id_conceptos']),self.cfg.tiposoperaciones.find(oc['id_tiposoperaciones']), self.selInversion.cuenta  )
            self.dividendos.append(Dividendo(self.cfg).init__db_row(d, self.selInversion, opercuenta, self.cfg.conceptos.find(d['id_conceptos'])))        
        cur.close()       
        cur2.close()
        self.cfg.disconnect_xulpymoney(con)         
        self.load_tblDividendos()

    def on_cmdISE_released(self):
        self.cmdInversion.setEnabled(True)
    def on_txtVenta_textChanged(self):
        self.cmdInversion.setEnabled(True)
    def on_txtInversion_textChanged(self):
        self.cmdInversion.setEnabled(True)
    def on_cmbTipoInversion_currentIndexChanged(self, index):
        self.cmdInversion.setEnabled(True)
        

            
    def on_cmdInversion_pressed(self):
        if self.ise.selected==None:
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.trUtf8("Debe seleccionar una inversión de MyQuotes para continuar"))
            m.exec_()     
            return
        inversion=self.txtInversion.text()
        venta=self.txtVenta.decimal()
        id_cuentas=int(self.cmbCuenta.itemData(self.cmbCuenta.currentIndex()))
        myquotesid=int(self.ise.selected.id)
        
        
        if self.data_investments.find(myquotesid)==None:
            print ("Cargando otro mqinversiones")
            inv=Investment(self.cfg).init__db(myquotesid)
            inv.load_estimacion()
            inv.quotes.get_basic()
            self.data_investments.arr.append(inv)
            
        

        if self.tipo==1:        #insertar
            i=Inversion(self.cfg).create(inversion,   venta,  self.data_cuentas.find(id_cuentas),  self.data_investments.find(myquotesid))      
            i.save()
            self.cfg.con.commit()
            ##Se añade a cfg y vincula. No carga datos porque myquotesid debe existir            
            #Lo añade con las operaciones vacias pero calculadas.
            i.op=SetInversionOperacion(self.cfg)
            (i.op_actual, i.op_historica)=i.op.calcular()
            self.data_inversiones.arr.append(i)
            self.done(0)
        elif self.tipo==2:
            self.selInversion.name=inversion
            self.selInversion.venta=venta
            self.selInversion.mq=self.data_investments.find(myquotesid)
            self.selInversion.save()##El id y el id_cuentas no se pueden modificar
            self.cfg.con.commit()
            self.cmdInversion.setEnabled(False)
        
    def on_tblOperaciones_customContextMenuRequested(self,  pos):
        menu=QMenu()
        menu.addAction(self.actionMovimientoNuevo)
        menu.addAction(self.actionMovimientoModificar)
        menu.addAction(self.actionMovimientoBorrar)
        if self.selMovimiento.tipooperacion.id==9:#Traspaso valores origen
            menu.addSeparator()
            menu.addAction(self.actionDeshacerTraspasoValores)
        menu.exec_(self.tblOperaciones.mapToGlobal(pos))

    def on_tblInversionActual_customContextMenuRequested(self,  pos):
        menu=QMenu()
        menu.addAction(self.actionDesReinversion)
        menu.addSeparator()
        menu.addAction(self.actionMovimientoNuevo)
        menu.addSeparator()
        menu.addAction(self.actionTraspasoValores)
        menu.exec_(self.tblInversionActual.mapToGlobal(pos))


    def on_tblOperaciones_itemSelectionChanged(self):
#        self.selMovimiento=self.op.find[i.row()]
        try:
            for i in self.tblOperaciones.selectedItems():#itera por cada item no row.
                self.selMovimiento=self.op.arr[i.row()]
        except:
            self.selMovimiento=None
        print ("Seleccionado: " +  str(self.selMovimiento))
        
        
    def on_tblDividendos_customContextMenuRequested(self,  pos):
        if self.selDividendo==None:
            self.actionDividendoBorrar.setEnabled(False)
            self.actionDividendoModificar.setEnabled(False)
        else:
            self.actionDividendoBorrar.setEnabled(True)
            self.actionDividendoModificar.setEnabled(True)
            
        menu=QMenu()
        menu.addAction(self.actionDividendoNuevo)
        menu.addAction(self.actionDividendoBorrar)
        menu.addAction(self.actionDividendoModificar)
        menu.exec_(self.tblDividendos.mapToGlobal(pos))

    def on_tblDividendos_itemSelectionChanged(self):
        try:
            for i in self.tblDividendos.selectedItems():#itera por cada item no rowse.
                self.selDividendo=self.dividendos[i.row()]
        except:
            self.selDividendo=None
        print ("Dividendo seleccionado: " +  str(self.selDividendo))        

