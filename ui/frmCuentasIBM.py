from PyQt4.QtCore import *
from PyQt4.QtGui import *
from libxulpymoney import *
from Ui_frmCuentasIBM import *
from frmOperCuentas import *
from frmTarjetasIBM import *

class frmCuentasIBM(QDialog, Ui_frmCuentasIBM):
    def __init__(self, cfg, cuenta,  parent=None):
        """
            selIdCuenta=None Inserción de cuentas
            selIdCuenta=X. Modificación de cuentas cuando click en cmd y resto de trabajos"""
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.showMaximized()
        self.cmdDatos.setEnabled(False)     
        
        self.cfg=cfg
        self.loadedinactive=False
                
        self.selOperCuenta=None #Registro de oper cuentas
        self.selTarjeta=None#Registro de Tarjeta seleccionada
        self.setSelOperTarjetas=set([])#Conjunto de oper tarjetas diferidas seleccionadas
        self.selCuenta=cuenta#Registro de selCuenta
        
        self.opercuentas=[]#Array de objetos CUentaOperacion
        self.tarjetas=[]
        
        self.totalOperTarjetas=0
        
        self.saldoiniciomensual=0#Almacena el inicio según on_cmdMovimientos_released
          
        self.tblOperaciones.settings("frmCuentasIBM",  self.cfg)
        self.tblTarjetas.settings("frmCuentasIBM",  self.cfg)
        self.tblOperTarjetas.settings("frmCuentasIBM",  self.cfg)
        self.tblOpertarjetasHistoricas.settings("frmCuentasIBM",  self.cfg)
    
        self.calPago.setDate(QDate.currentDate())
        
        self.cfg.currencies.load_qcombobox(self.cmbCurrency)
        self.cfg.data.ebs_active.load_qcombobox(self.cmbEB)
                    
        if self.selCuenta==None:
            self.lblTitulo.setText(self.trUtf8("Datos de la nueva cuenta bancaria"))
            self.tab.setCurrentIndex(0)
            self.tab.setTabEnabled(1, False)
            self.tab.setTabEnabled(2, False)
            self.chkActiva.setChecked(Qt.Checked)
            self.chkActiva.setEnabled(False)
            self.cmdDatos.setText(self.trUtf8("Insertar nueva cuenta bancaria"))
        else:               
            self.tab.setCurrentIndex(0)
            self.lblTitulo.setText(self.selCuenta.name)
            self.txtCuenta.setText(self.selCuenta.name)
            self.txtNumero.setText(str(self.selCuenta.numero))            
            self.cmbEB.setCurrentIndex(self.cmbEB.findData(self.selCuenta.eb.id))
            self.cmbEB.setEnabled(False)    
            self.cmbCurrency.setCurrentIndex(self.cmbCurrency.findData(self.selCuenta.currency.id))
            self.cmbCurrency.setEnabled(False)
            self.chkActiva.setChecked(b2c(self.selCuenta.activa))
            self.cmdDatos.setText(self.trUtf8("Modificar los datos de la cuenta bancaria"))

            anoinicio=Patrimonio(self.cfg).primera_fecha_con_datos_usuario().year       
            self.wdgYM.initiate(anoinicio,  datetime.date.today().year, datetime.date.today().year, datetime.date.today().month)
            QObject.connect(self.wdgYM, SIGNAL("changed"), self.on_wdgYM_changed)

#            self.load_data_from_db()

            self.on_wdgYM_changed()
            self.on_chkTarjetas_stateChanged(self.chkTarjetas.checkState())        
            
#        
#    def load_data_from_db(self):
#        inicio=datetime.datetime.now()
#        print("\n","Cargando data en wdgInversiones",  datetime.datetime.now()-inicio)
#            
#    def load_inactive_data_from_db(self):
#        if self.loadedinactive==False:
#            inicio=datetime.datetime.now()        
#            self.cfg.data.load_inactives()
#            print("\n","Cargando data en wdgInversiones",  datetime.datetime.now()-inicio)
#            self.loadedinactive=True
#            
#        print (self.trUtf8("Ya se habían cargado las inactivas"))
    def load_tabOperTarjetas(self):     
        self.selTarjeta.op_diferido=sorted(self.selTarjeta.op_diferido, key=lambda o:o.fecha)
        self.tblOperTarjetas.setRowCount(len(self.selTarjeta.op_diferido));        
        for i,  o in enumerate(self.selTarjeta.op_diferido):
            self.tblOperTarjetas.setItem(i, 0, QTableWidgetItem(str(o.fecha)))
            self.tblOperTarjetas.setItem(i, 1, QTableWidgetItem((o.concepto.name)))
            self.tblOperTarjetas.setItem(i, 2, self.selCuenta.currency.qtablewidgetitem(o.importe))
            self.tblOperTarjetas.setItem(i, 3, QTableWidgetItem(o.comentario))
         #actualiza saldo en tblTarjetas   
        self.tblTarjetas.setItem(self.tblTarjetas.currentRow(), 5, self.selCuenta.currency.qtablewidgetitem(self.selTarjeta.saldo_pendiente()))
        self.tblOperTarjetas.clearSelection()
        self.setSelOperTarjetas=set([])
         
        
    def load_tabTarjetas(self):     
        self.tblTarjetas.setRowCount(len(self.tarjetas.arr))        
        for i, t in enumerate(self.tarjetas.arr):
            self.tblTarjetas.setItem(i, 0, QTableWidgetItem(t.name))
            self.tblTarjetas.setItem(i, 1, QTableWidgetItem(str(t.numero)))
            self.tblTarjetas.setItem(i, 2, qbool(t.activa))
            self.tblTarjetas.setItem(i, 3, qbool(t.pagodiferido))
            self.tblTarjetas.setItem(i, 4, self.selCuenta.currency.qtablewidgetitem(t.saldomaximo, ))
            self.tblTarjetas.setItem(i, 5, self.selCuenta.currency.qtablewidgetitem(t.saldo_pendiente()))


    @QtCore.pyqtSlot() 
    def on_actionTarjetaNueva_activated(self):
        w=frmTarjetasIBM(self.cfg,  self.selCuenta,  None, self)
        w.exec_()
        self.on_chkTarjetas_stateChanged(Qt.Unchecked)
        
    @QtCore.pyqtSlot() 
    def on_actionTarjetaModificar_activated(self):
        w=frmTarjetasIBM(self.cfg, self.selCuenta,  self.selTarjeta, self)
        w.exec_()
        self.tblTarjetas.clearSelection()
        self.on_chkTarjetas_stateChanged(self.chkTarjetas.checkState())
        
    @QtCore.pyqtSlot() 
    def on_actionTarjetaActivar_activated(self):
        if self.selCuenta.qmessagebox_inactive() or self.selCuenta.eb.qmessagebox_inactive():
            return
            
        if self.actionTarjetaActivar.isChecked():#Ha pasado de inactiva a activa
            self.selTarjeta.activa=True
            self.cfg.data.tarjetas_inactive.arr.remove(self.selTarjeta)
            self.cfg.data.tarjetas_active.arr.append(self.selTarjeta)
        else:
            self.selTarjeta.activa=False
            self.cfg.data.tarjetas_inactive.arr.append(self.selTarjeta)
            self.cfg.data.tarjetas_active.arr.remove(self.selTarjeta)
        self.selTarjeta.save()
        self.cfg.con.commit()
        
        self.on_chkTarjetas_stateChanged(self.chkTarjetas.checkState())
                
    @QtCore.pyqtSlot() 
    def on_actionTarjetaBorrar_activated(self):
        if self.selTarjeta.borrar()==False:
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.trUtf8("No se ha borrado la tarjeta por tener registros dependientes"))
            m.exec_()                 
        self.cfg.con.commit()
        self.cfg.data.tarjetas_active.arr.remove(self.selTarjeta)
        self.tblTarjetas.clearSelection()
        self.on_chkTarjetas_stateChanged(self.chkTarjetas.checkState())

    def on_chkTarjetas_stateChanged(self, state):        
        if state==Qt.Unchecked:
            self.tarjetas=self.cfg.data.tarjetas_active.clone_of_account(self.selCuenta)
        else:
            self.cfg.data.load_inactives()
            self.tarjetas=self.cfg.data.tarjetas_inactive.clone_of_account(self.selCuenta)
        self.load_tabTarjetas() 
        self.selTarjeta=None
        self.tblTarjetas.clearSelection()

    def on_cmdDatos_released(self):
        id_entidadesbancarias=int(self.cmbEB.itemData(self.cmbEB.currentIndex()))
        cuenta=self.txtCuenta.text()
        numerocuenta=self.txtNumero.text()
        cu_activa=c2b(self.chkActiva.checkState())
        currency=self.cmbCurrency.itemData(self.cmbCurrency.currentIndex())

        if self.selCuenta==None:
            cu=Cuenta(self.cfg).init__create(cuenta, self.cfg.data.ebs_active.find(id_entidadesbancarias), cu_activa, numerocuenta, self.cfg.currencies.find(currency))
            cu.save()
            self.cfg.data.cuentas_active.arr.append(cu)
        else:
            self.selCuenta.eb=self.cfg.data.ebs_active.find(id_entidadesbancarias)
            self.selCuenta.name=cuenta
            self.selCuenta.numero=numerocuenta
            self.selCuenta.activa=cu_activa
            self.selCuenta.currency=self.cfg.currencies.find(currency)
            self.selCuenta.save()
            self.lblTitulo.setText(self.selCuenta.name)
        self.cfg.con.commit()
        
        if self.selCuenta==None:
            self.done(0)
        self.cmdDatos.setEnabled(False)   

    @pyqtSlot()
    def on_wdgYM_changed(self):
        cur = self.cfg.con.cursor()      
        self.opercuentas=[]
        self.saldoiniciomensual=self.selCuenta.saldo_from_db( str(datetime.date(self.wdgYM.year, self.wdgYM.month, 1)-datetime.timedelta(days=1)))         
        if self.saldoiniciomensual==None:
            self.saldoiniciomensual=0
        cur.execute("select * from opercuentas where id_cuentas="+str(self.selCuenta.id)+" and date_part('year',fecha)="+str(self.wdgYM.year)+" and date_part('month',fecha)="+str(self.wdgYM.month)+" order by fecha, id_opercuentas")
        for o in cur:
            self.opercuentas.append(CuentaOperacion(self.cfg).init__db_row(o, self.cfg.conceptos.find(o['id_conceptos']), self.cfg.tiposoperaciones.find(o['id_tiposoperaciones']), self.selCuenta))
        cur.close()     
        self.load_tblOperaciones()  
            
    def load_tblOperaciones(self):
        self.tblOperaciones.setRowCount(len(self.opercuentas)+1)        
        self.tblOperaciones.setItem(0, 1, QTableWidgetItem(("Saldo al iniciar el mes")))
        self.tblOperaciones.setItem(0, 3, self.selCuenta.currency.qtablewidgetitem(self.saldoiniciomensual))
        saldoinicio=self.saldoiniciomensual
        for i, o in enumerate(self.opercuentas):
            saldoinicio=saldoinicio+o.importe
            self.tblOperaciones.setItem(i+1, 0, QTableWidgetItem(str(o.fecha)))
            self.tblOperaciones.setItem(i+1, 1, QTableWidgetItem(o.concepto.name))
            self.tblOperaciones.setItem(i+1, 2, self.selCuenta.currency.qtablewidgetitem(o.importe))
            self.tblOperaciones.setItem(i+1, 3, self.selCuenta.currency.qtablewidgetitem(saldoinicio))
            self.tblOperaciones.setItem(i+1, 4, QTableWidgetItem(o.comentariobonito()))        

    @QtCore.pyqtSlot() 
    def on_actionMovimientoNuevo_activated(self):
        w=frmOperCuentas(self.cfg, self.cfg.data.cuentas_active,  self.selCuenta, None, None)
        self.connect(w, SIGNAL("OperCuentaIBMed"), self.on_wdgYM_changed)
        w.exec_()
        self.load_tblOperaciones()
        self.tblOperaciones.clearSelection()
        self.selOperCuenta=None

    @QtCore.pyqtSlot() 
    def on_actionMovimientoModificar_activated(self):
        w=frmOperCuentas(self.cfg, self.cfg.data.cuentas_active,  self.selCuenta, self.selOperCuenta, None)
        self.connect(w, SIGNAL("OperCuentaIBMed"), self.on_wdgYM_changed)#Actualiza movimientos como si cmd
        w.exec_()
        self.load_tblOperaciones()
        self.tblOperaciones.clearSelection()
        self.selOperCuenta=None

    @QtCore.pyqtSlot() 
    def on_actionMovimientoBorrar_activated(self):
        self.selOperCuenta.borrar() 
        self.cfg.con.commit()  
        self.opercuentas.remove(self.selOperCuenta)         
        self.load_tblOperaciones()
        self.tblOperaciones.clearSelection()
        self.selOperCuenta=None

    @QtCore.pyqtSlot() 
    def on_actionOperTarjetaNueva_activated(self):
        if self.selTarjeta.pagodiferido==False:
            w=frmOperCuentas(self.cfg, self.cfg.data.cuentas_active, self.selCuenta, None)
            self.connect(w, SIGNAL("OperCuentaIBMed"), self.on_wdgYM_changed)
            w.lblTitulo.setText(((self.selTarjeta.name)))
            w.txtComentario.setText(self.tr("Tarjeta {0}. ".format((self.selTarjeta.name))))
            w.exec_()
        else:            
            w=frmOperCuentas(self.cfg, self.cfg.data.cuentas_active,  self.selCuenta, None, self.selTarjeta)
            self.connect(w, SIGNAL("OperTarjetaIBMed"), self.load_tabOperTarjetas)
            w.lblTitulo.setText(self.tr("Tarjeta {0}".format((self.selTarjeta.name))))
            w.exec_()
            
    @QtCore.pyqtSlot() 
    def on_actionOperTarjetaModificar_activated(self):
        #Como es unico
        for s in self.setSelOperTarjetas:
            selOperTarjeta=s
        w=frmOperCuentas(self.cfg, self.cfg.data.cuentas_active,  self.selCuenta, None, self.selTarjeta, selOperTarjeta)
        self.connect(w, SIGNAL("OperTarjetaIBMed"), self.load_tabOperTarjetas)
        w.lblTitulo.setText(self.tr("Tarjeta {0}".format((self.selTarjeta.name))))
        w.exec_()

    @QtCore.pyqtSlot() 
    def on_actionOperTarjetaBorrar_activated(self):
        for o in self.setSelOperTarjetas:
            o.borrar()
            self.selTarjeta.op_diferido.remove(o)
        self.cfg.con.commit()
        self.load_tabOperTarjetas()

    def on_tblOperaciones_customContextMenuRequested(self,  pos):      
        if self.selCuenta.qmessagebox_inactive() or self.selCuenta.eb.qmessagebox_inactive():
            return

        if self.selOperCuenta==None:
            self.actionMovimientoBorrar.setEnabled(False)
            self.actionMovimientoModificar.setEnabled(False)   
        else:
            if self.selOperCuenta.es_editable()==False:
                self.actionMovimientoBorrar.setEnabled(False)
                self.actionMovimientoModificar.setEnabled(False)   
            else:
                self.actionMovimientoBorrar.setEnabled(True)    
                self.actionMovimientoModificar.setEnabled(True)        
            
        menu=QMenu()
        menu.addAction(self.actionMovimientoNuevo)
        menu.addAction(self.actionMovimientoModificar)
        menu.addAction(self.actionMovimientoBorrar)
        menu.exec_(self.tblOperaciones.mapToGlobal(pos))

    def on_tblOperaciones_itemSelectionChanged(self):
        try:
            for i in self.tblOperaciones.selectedItems():#itera por cada item no row.
                self.selOperCuenta=self.opercuentas[i.row()-1]
        except:
            self.selOperCuenta=None
        print ("Seleccionado: " +  str(self.selOperCuenta))
        

    def on_tblTarjetas_customContextMenuRequested(self,  pos):
        if self.selCuenta.qmessagebox_inactive():
            return 
        menu=QMenu()
        menu.addAction(self.actionOperTarjetaNueva)
        menu.addSeparator()
        menu.addAction(self.actionTarjetaNueva)
        menu.addAction(self.actionTarjetaModificar)
        menu.addAction(self.actionTarjetaBorrar)
        menu.addSeparator()
        menu.addAction(self.actionTarjetaActivar)
        
        if self.selTarjeta==None:
            self.actionTarjetaBorrar.setEnabled(False)
            self.actionTarjetaModificar.setEnabled(False)
            self.actionTarjetaActivar.setEnabled(False)
        else:
            self.actionTarjetaBorrar.setEnabled(True)
            self.actionTarjetaModificar.setEnabled(True)
            self.actionTarjetaActivar.setEnabled(True)
            if self.selTarjeta.activa==True:
                self.actionTarjetaActivar.setChecked(True)
            else:
                self.actionTarjetaActivar.setChecked(False)
        menu.exec_(self.tblTarjetas.mapToGlobal(pos))



    def on_tblTarjetas_itemSelectionChanged(self):
        try:
            for i in self.tblTarjetas.selectedItems():#itera por cada item no row.
                self.selTarjeta=self.tarjetas.arr[i.row()]
        except:
            self.selTarjeta=None
            self.tblOperTarjetas.setRowCount(0)
            
        if self.selTarjeta==None:
            return
        if self.selTarjeta.pagodiferido==True:
            self.load_tabOperTarjetas()         
        else:
            self.tblOperTarjetas.setRowCount(0)
        self.tabOpertarjetasDiferidas.setCurrentIndex(0)
        self.tabOpertarjetasDiferidas.setEnabled(self.selTarjeta.pagodiferido)
        print ("Seleccionado: " +  str(self.selTarjeta.name))

    def on_tblOperTarjetas_customContextMenuRequested(self,  pos):
        if self.selCuenta.qmessagebox_inactive() or self.selCuenta.eb.qmessagebox_inactive() or self.selTarjeta.qmessagebox_inactive():
            return
        
        if len(self.setSelOperTarjetas)!=1: # 0 o más de 1
            self.actionOperTarjetaBorrar.setEnabled(False)
            self.actionOperTarjetaModificar.setEnabled(False)
        else:
            self.actionOperTarjetaBorrar.setEnabled(True)
            self.actionOperTarjetaModificar.setEnabled(True)
            
        menu=QMenu()
        menu.addAction(self.actionOperTarjetaNueva)
        menu.addAction(self.actionOperTarjetaModificar)
        menu.addAction(self.actionOperTarjetaBorrar)
        
        
            
        
        menu.exec_(self.tblOperTarjetas.mapToGlobal(pos))


    def on_tblOperTarjetas_itemSelectionChanged(self):
        sel=[]
        self.totalOperTarjetas=Decimal(0)
        for i in self.tblOperTarjetas.selectedItems():#itera por cada item no row.
            if i.column()==0:
                sel.append(self.selTarjeta.op_diferido[i.row()])  
        self.setSelOperTarjetas=set(sel)
        
        #Activa el grp Pago
        if len(self.setSelOperTarjetas)>0:
            self.grpPago.setEnabled(True)
        else:
            self.grpPago.setEnabled(False)
        
        #Calcula el saldo
        for o in self.setSelOperTarjetas:
            self.totalOperTarjetas=self.totalOperTarjetas+Decimal(o.importe)
        self.lblPago.setText(self.cfg.localcurrency.string(self.totalOperTarjetas, 2))
 
    def on_cmdPago_released(self):
        comentario="{0}|{1}".format(self.selTarjeta.name, len(self.setSelOperTarjetas))
        fechapago=self.calPago.date().toPyDate()
        c=CuentaOperacion(self.cfg).init__create(fechapago, self.cfg.conceptos.find(40), self.cfg.tiposoperaciones.find(7), self.totalOperTarjetas, comentario, self.selCuenta)
        c.save()
        
        #Modifica el registro y lo pone como pagado y la fecha de pago y añade la opercuenta
        for o in self.setSelOperTarjetas:
            o.fechapago=fechapago
            o.pagado=True
            o.opercuenta=c
            o.save()
            self.selTarjeta.op_diferido.remove(o)
        self.cfg.con.commit()
        self.load_tabOperTarjetas()         
        self.on_wdgYM_changed()  

    
    def on_cmdDevolverPago_released(self):
        print ("solo uno")
        id_opercuentas=self.cmbFechasPago.itemData(int(self.cmbFechasPago.currentIndex()))
        cur = self.cfg.con.cursor()      
        cur.execute("delete from opercuentas where id_opercuentas=%s", (id_opercuentas, ))#No merece crear objeto
        cur.execute("update opertarjetas set fechapago=null, pagado=false, id_opercuentas=null where id_opercuentas=%s", (id_opercuentas, ) )
        self.cfg.con.commit()
        self.selTarjeta.get_opertarjetas_diferidas_pendientes()
        self.on_cmdMovimientos_released()
        self.load_tabOperTarjetas()
        cur.close()     
        self.tabOpertarjetasDiferidas.setCurrentIndex(0)     
        
    @QtCore.pyqtSlot(int) 
    def on_cmbFechasPago_currentIndexChanged(self, index):
        id_opercuentas=self.cmbFechasPago.itemData(int(self.cmbFechasPago.currentIndex()))
        print (id_opercuentas)            
        con=self.cfg.connect_xulpymoney()
        cur = con.cursor()      
        cur.execute("select id_opertarjetas,fecha,conceptos.concepto,importe,comentario from opertarjetas,conceptos where opertarjetas.id_conceptos=conceptos.id_conceptos and id_opercuentas=%s;", (id_opercuentas, ))
        self.tblOpertarjetasHistoricas.clearContents()
        self.tblOpertarjetasHistoricas.setRowCount(cur.rowcount);       
        saldo=0
        for rec in cur:
            saldo=saldo+rec['importe']
            self.tblOpertarjetasHistoricas.setItem(cur.rownumber-1, 0, QTableWidgetItem(str(rec['id_opertarjetas'])))
            self.tblOpertarjetasHistoricas.setItem(cur.rownumber-1, 1, QTableWidgetItem(str(rec['fecha'])))
            self.tblOpertarjetasHistoricas.setItem(cur.rownumber-1, 2, QTableWidgetItem((rec['concepto'])))
            self.tblOpertarjetasHistoricas.setItem(cur.rownumber-1, 3, self.selCuenta.currency.qtablewidgetitem(rec['importe']))
            self.tblOpertarjetasHistoricas.setItem(cur.rownumber-1, 4, self.selCuenta.currency.qtablewidgetitem(saldo))
            self.tblOpertarjetasHistoricas.setItem(cur.rownumber-1, 5, QTableWidgetItem((rec['comentario'])))
        cur.close()     
        self.cfg.disconnect_xulpymoney(con)      

    def on_tabOpertarjetasDiferidas_currentChanged(self, index): 
        if  index==1: #PAGOS
            #Carga combo
            self.cmbFechasPago.clear()
            con=self.cfg.connect_xulpymoney()
            cur = con.cursor()       
            cur2=con.cursor()
            cur.execute("select distinct(fechapago), id_opercuentas from opertarjetas where id_tarjetas=%s and fechapago is not null  order by fechapago;", (self.selTarjeta.id, ))
            for row in cur:  
                cur2.execute("select importe from opercuentas where id_opercuentas=%s", (row['id_opercuentas'], ))
                importe=cur2.fetchone()["importe"]
                self.cmbFechasPago.addItem(self.tr("Pago efectuado el {0} de {1}".format(row['fechapago'],  self.cfg.localcurrency.string(-importe))),row['id_opercuentas'])
            self.cmbFechasPago.setCurrentIndex(cur.rowcount-1)
            cur.close()     
            cur2.close()
            self.cfg.disconnect_xulpymoney(con)      
            

    def on_txtCuenta_textChanged(self):
        self.cmdDatos.setEnabled(True)
    def on_txtNumero_textChanged(self):
        self.cmdDatos.setEnabled(True)
    def on_cmbEB_currentIndexChanged(self, index):
        self.cmdDatos.setEnabled(True)
    def on_chkActiva_stateChanged(self,  state):
        self.cmdDatos.setEnabled(True)
