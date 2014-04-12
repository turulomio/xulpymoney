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
    def __init__(self, cfg, inversion=None,  parent=None):
        """Cuentas es un set cuentas"""
        """TIPOS DE ENTRADAS:        
         1   : Inserción de Opercuentas
         2   inversion=x"""
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.showMaximized()
        self.cfg=cfg
        self.inversion=inversion
        
        self.selDividendo=None#Dividendo seleccionado
        
        #arrays asociados a tablas
        self.op=[]#Necesario porque puede acortarse el original
        self.dividendos=SetDividends(self.cfg)
        self.cfg.data.load_inactives()
        
        self.ise.setupUi(self.cfg)
#        self.tblInversionHistorica.settings("frmInversionesEstudio",  self.cfg)
        self.tblDividendos.settings("frmInversionesEstudio",  self.cfg)
        self.cmdInversion.setEnabled(False)                                                                                                                                                                                            
        self.connect(self.ise.cmd,SIGNAL('released()'),  self.on_cmdISE_released)         
        
        self.cfg.data.cuentas_active.load_qcombobox(self.cmbCuenta)
        
        if inversion==None:
            self.tipo=1
            self.cmdInversion.setText(self.trUtf8("Añadir una nueva inversión"))
            self.lblTitulo.setText(self.trUtf8("Nueva inversión"))
            self.inversion=None
            self.tab.setCurrentIndex(0)
            self.tabDividendos.setEnabled(False)
            self.tabOperacionesHistoricas.setEnabled(False)
            self.tabInversionActual.setEnabled(False)
            self.ise.setSelected(None)
            self.cmdPuntoVenta.setEnabled(False)
        else:
            self.tipo=2    
            self.tab.setCurrentIndex(1)
            self.lblTitulo.setText((self.inversion.name))
            self.txtInversion.setText((self.inversion.name))
            self.txtVenta.setText(str((self.inversion.venta)))
            self.ise.setSelected(self.inversion.investment)
            self.cmdPuntoVenta.setEnabled(True)
            self.cmbCuenta.setCurrentIndex(self.cmbCuenta.findData(self.inversion.cuenta.id))
            self.selMovimiento=None
            self.on_chkOperaciones_stateChanged(self.chkOperaciones.checkState())
            self.on_chkDividendosHistoricos_stateChanged(self.chkDividendosHistoricos.checkState())
            
            if len(self.op.arr)!=0 or len(self.dividendos.arr)!=0:#CmbCuenta está desabilitado si hay dividendos o operinversiones
                self.cmbCuenta.setEnabled(False)
            
            self.inversion.op_actual.get_valor_indicereferencia(self.cfg.data.indicereferencia)
            self.inversion.op_actual.myqtablewidget(self.tblInversionActual,  "frmInversionesEstudio")
            self.inversion.op_historica.myqtablewidget(self.tblInversionHistorica,  "frmInversionesEstudio"  )
   

    def load_tabDividendos(self):        
        (sumneto, sumbruto, sumretencion, sumcomision)=self.dividendos.myqtablewidget(self.tblDividendos, "frmInversionesEstudio")
        if self.chkDividendosHistoricos.checkState()==Qt.Unchecked:
            if len(self.dividendos.arr)>0:
                importeinvertido=self.inversion.invertido()
                dias=(datetime.date.today()-self.inversion.op_actual.datetime_primera_operacion().date()).days+1
                dtpc=100*sumbruto/importeinvertido
                dtae=365*dtpc/abs(dias)
            else:
                dtpc=0
                dtae=0
            
            estimacion=self.inversion.investment.estimations_dps.currentYear()
            if estimacion.estimation!=None:
                acciones=self.inversion.acciones()
                tpccalculado=100*estimacion.estimation/self.inversion.investment.result.basic.last.quote
                self.lblDivAnualEstimado.setText(("El dividendo anual estimado, según el valor actual de la acción es del {0} % ({1}€ por acción)".format(str(round(tpccalculado, 2)),  str(estimacion.estimation))))
                self.lblDivFechaRevision.setText(('Fecha de la última revisión del dividendo: '+ str(estimacion.date_estimation)))
                self.lblDivSaldoEstimado.setText(("Saldo estimado: {0}€ ({1}€ después de impuestos)".format( str(round(acciones*estimacion.estimation, 2)),  str(round(acciones*estimacion.estimation*(1-self.cfg.dividendwithholding))), 2)))
            self.lblDivTPC.setText(("% de lo invertido: "+tpc(dtpc)))
            self.lblDivTAE.setText(("% TAE de lo invertido: "+tpc(dtae)))        
            self.grpDividendosEstimacion.show()
            self.grpDividendosEfectivos.show()
        else:
            self.grpDividendosEstimacion.hide()
            self.grpDividendosEfectivos.hide()
       
    def on_chkOperaciones_stateChanged(self, state):
        if state==Qt.Unchecked:
            primera=self.inversion.op_actual.datetime_primera_operacion()
            if primera==None:
                primera=self.cfg.localzone.now()
            self.op=self.inversion.op.clone_from_datetime(primera)
        else:
            self.op=self.inversion.op
        self.selMovimiento=None
        self.op.myqtablewidget(self.tblOperaciones, "frmInversionesEstudio")
            
        
    def update_tables(self):             
        #Actualiza el indice de referencia porque ha cambiado
        self.inversion.op_actual.get_valor_indicereferencia(self.cfg.data.indicereferencia)
        self.on_chkOperaciones_stateChanged(self.chkOperaciones.checkState())
        self.inversion.op_actual.myqtablewidget(self.tblInversionActual,  "frmInversionesEstudio")
        self.inversion.op_historica.myqtablewidget(self.tblInversionHistorica,  "frmInversionesEstudio"  )
        self.load_tabDividendos()
    

    @QtCore.pyqtSlot() 
    def on_actionDividendoNuevo_activated(self):
        w=frmDividendosIBM(self.cfg, self.inversion,  None)
        w.exec_()
        self.on_chkDividendosHistoricos_stateChanged(self.chkDividendosHistoricos.checkState())

        
    @QtCore.pyqtSlot() 
    def on_actionDividendoModificar_activated(self):
        w=frmDividendosIBM(self.cfg, self.inversion, self.selDividendo)
        w.exec_()
        self.on_chkDividendosHistoricos_stateChanged(self.chkDividendosHistoricos.checkState())

        
    @QtCore.pyqtSlot() 
    def on_actionDividendoBorrar_activated(self):
        self.selDividendo.borrar()
        self.cfg.con.commit()
        self.on_chkDividendosHistoricos_stateChanged(self.chkDividendosHistoricos.checkState())

                
    @QtCore.pyqtSlot() 
    def on_actionDesReinversion_activated(self):
        #Llama a form
        d=QDialog(self)       
        d.showMaximized() 
        d.setWindowTitle(self.trUtf8("Simulación de Desinversión / Reinversión"))
        w=wdgDesReinversion(self.cfg, self.inversion)
        lay = QVBoxLayout(d)
        lay.addWidget(w)
        d.exec_()
        
    @QtCore.pyqtSlot() 
    def on_actionMovimientoNuevo_activated(self):
        w=frmInversionesIBM(self.cfg, self.inversion, None, self)
        w.exec_()
        self.update_tables()    
        
    @QtCore.pyqtSlot() 
    def on_actionMovimientoModificar_activated(self):
        w=frmInversionesIBM(self.cfg, self.inversion, self.selMovimiento, self)
        w.exec_()
        self.update_tables() 

    @QtCore.pyqtSlot() 
    def on_actionSplit_activated(self):
        w=frmSplit(self.cfg)
        w.exec_()   
        if w.result()==QDialog.Accepted:
            w.split.updateOperInversiones(self.inversion.op.arr)         
            w.split.updateDividendos(self.dividendos)         
            self.cfg.con.commit()
            self.update_tables()
        
    @QtCore.pyqtSlot() 
    def on_actionTraspasoValores_activated(self):
        w=frmTraspasoValores(self.cfg, self.inversion, self)
        w.exec_()
        self.update_tables()                               

    @QtCore.pyqtSlot() 
    def on_actionDeshacerTraspasoValores_activated(self):
        if self.cfg.data.inversiones_active.traspaso_valores_deshacer(self.selMovimiento)==False:
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.trUtf8("No se ha podiddo deshacer el traspaso de valores"))
            m.exec_()          
            return
        self.update_tables()       

    @QtCore.pyqtSlot() 
    def on_cmdPuntoVenta_released(self):
        f=frmPuntoVenta(self.cfg, self.cfg.data.inversiones_active, self.inversion)
        f.exec_()
        self.txtVenta.setText(str(f.puntoventa))

    @QtCore.pyqtSlot() 
    def on_actionMovimientoBorrar_activated(self):
        self.selMovimiento.borrar()
        self.cfg.con.commit()     
        self.update_tables()

    def on_chkDividendosHistoricos_stateChanged(self, state):
        fechapo=self.inversion.op_actual.datetime_primera_operacion()

        self.tblDividendos.clearSelection()
        self.selDividendo=None        

        if state==Qt.Unchecked and fechapo!=None:   
            self.dividendos.load_from_db("select * from dividendos where id_inversiones={0} and fecha >='{1}'  order by fecha".format(self.inversion.id, fechapo.date()))
        else:
            self.dividendos.load_from_db("select * from dividendos where id_inversiones={0} order by fecha".format(self.inversion.id ))  
        self.load_tabDividendos()

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
            m.setText(self.trUtf8("Debe seleccionar una inversión de MyStocks para continuar"))
            m.exec_()     
            return
        inversion=self.txtInversion.text()
        venta=self.txtVenta.decimal()
        id_cuentas=int(self.cmbCuenta.itemData(self.cmbCuenta.currentIndex()))
        mystocksid=int(self.ise.selected.id)
        
        
        if self.cfg.data.investments_active.find(mystocksid)==None:
            print ("Cargando otro mqinversiones")
            inv=Investment(self.cfg).init__db(mystocksid)
            inv.estimations_dps.load_from_db()
            inv.result.basic.load_from_db()
            self.cfg.data.investments_active.arr.append(inv)
            
        

        if self.tipo==1:        #insertar
            i=Inversion(self.cfg).create(inversion,   venta,  self.cfg.data.cuentas_active.find(id_cuentas),  self.cfg.data.investments_active.find(mystocksid))      
            i.save()
            self.cfg.con.commit()
            ##Se añade a cfg y vincula. No carga datos porque mystocksid debe existir            
            #Lo añade con las operaciones vacias pero calculadas.
            i.op=SetInversionOperacion(self.cfg)
            (i.op_actual, i.op_historica)=i.op.calcular()
            self.cfg.data.inversiones_active.arr.append(i)
            self.done(0)
        elif self.tipo==2:
            self.inversion.name=inversion
            self.inversion.venta=venta
            self.inversion.investment=self.cfg.data.investments_active.find(mystocksid)
            self.inversion.save()##El id y el id_cuentas no se pueden modificar
            self.cfg.con.commit()
            self.cmdInversion.setEnabled(False)
        
    def on_tblOperaciones_customContextMenuRequested(self,  pos):
        if self.inversion.qmessagebox_inactive() or self.inversion.cuenta.qmessagebox_inactive()or self.inversion.cuenta.eb.qmessagebox_inactive():
            return
            
            
        
        if self.selMovimiento==None:
            self.actionMovimientoBorrar.setEnabled(False)
            self.actionMovimientoModificar.setEnabled(False)
        else:
            if self.selMovimiento.tipooperacion.id==10:#Traspaso valores destino
                self.actionMovimientoBorrar.setEnabled(False)
                self.actionMovimientoModificar.setEnabled(False)
            else:
                self.actionMovimientoBorrar.setEnabled(True)
                self.actionMovimientoModificar.setEnabled(True)
            
            
        menu=QMenu()
        menu.addAction(self.actionMovimientoNuevo)
        
        menu.addAction(self.actionMovimientoModificar)
        menu.addAction(self.actionMovimientoBorrar)
        
        if self.selMovimiento!=None:
            if self.selMovimiento.tipooperacion.id==9:#Traspaso valores origen
                menu.addSeparator()
                menu.addAction(self.actionDeshacerTraspasoValores)
                
        menu.addSeparator()
        menu.addAction(self.actionSplit)
        menu.exec_(self.tblOperaciones.mapToGlobal(pos))

    def on_tblInversionActual_customContextMenuRequested(self,  pos):
        
        if self.inversion.qmessagebox_inactive() or self.inversion.cuenta.qmessagebox_inactive() or self.inversion.cuenta.eb.qmessagebox_inactive():
            return
        menu=QMenu()
        menu.addAction(self.actionDesReinversion)
        menu.addSeparator()
        menu.addAction(self.actionMovimientoNuevo)
        menu.addSeparator()
        menu.addAction(self.actionTraspasoValores)
        
        
        menu.exec_(self.tblInversionActual.mapToGlobal(pos))


    def on_tblOperaciones_itemSelectionChanged(self):
        try:
            for i in self.tblOperaciones.selectedItems():#itera por cada item no row.
                self.selMovimiento=self.op.arr[i.row()]
        except:
            self.selMovimiento=None
        print ("Seleccionado: " +  str(self.selMovimiento))
        
        
    def on_tblDividendos_customContextMenuRequested(self,  pos):
        if self.inversion.qmessagebox_inactive() or self.inversion.cuenta.qmessagebox_inactive() or self.inversion.cuenta.eb.qmessagebox_inactive():
            return
        
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
                self.selDividendo=self.dividendos.arr[i.row()]
        except:
            self.selDividendo=None
        print ("Dividendo seleccionado: " +  str(self.selDividendo))        

