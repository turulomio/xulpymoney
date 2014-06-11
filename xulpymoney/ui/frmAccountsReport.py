from PyQt4.QtCore import *
from PyQt4.QtGui import *
from libxulpymoney import *
from Ui_frmAccountsReport import *
from frmAccountOperationsAdd import *
from frmCreditCardsAdd import *

class frmAccountsReport(QDialog, Ui_frmAccountsReport):
    def __init__(self, mem, cuenta,  parent=None):
        """
            selIdAccount=None Inserción de cuentas
            selIdAccount=X. Modificación de cuentas cuando click en cmd y resto de trabajos"""
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.showMaximized()
        self.cmdDatos.setEnabled(False)     
        
        self.mem=mem
        self.mem.data.load_inactives()
                
        self.selOperAccount=None #Registro de oper cuentas
        self.selCreditCard=None#Registro de CreditCard seleccionada
        self.setSelOperCreditCards=set([])#Conjunto de oper tarjetas diferidas seleccionadas
        self.selAccount=cuenta#Registro de selAccount
        
        self.opercuentas=[]#Array de objetos CUentaOperacion
        self.tarjetas=[]
        
        self.totalOperCreditCards=0
        
        self.saldoiniciomensual=0#Almacena el inicio según on_cmdMovimientos_released
          
        self.tblOperaciones.settings("frmAccountsReport",  self.mem)
        self.tblCreditCards.settings("frmAccountsReport",  self.mem)
        self.tblCreditCardOpers.settings("frmAccountsReport",  self.mem)
        self.tblOpertarjetasHistoricas.settings("frmAccountsReport",  self.mem)
    
        self.calPago.setDate(QDate.currentDate())
        
        self.mem.currencies.qcombobox(self.cmbCurrency)
        self.mem.data.ebs_active.qcombobox(self.cmbEB)
                    
        if self.selAccount==None:
            self.lblTitulo.setText(self.trUtf8("Datos de la nueva cuenta bancaria"))
            self.tab.setCurrentIndex(0)
            self.tab.setTabEnabled(1, False)
            self.tab.setTabEnabled(2, False)
            self.chkActiva.setChecked(Qt.Checked)
            self.chkActiva.setEnabled(False)
            self.cmdDatos.setText(self.trUtf8("Insertar nueva cuenta bancaria"))
        else:               
            self.tab.setCurrentIndex(0)
            self.lblTitulo.setText(self.selAccount.name)
            self.txtAccount.setText(self.selAccount.name)
            self.txtNumero.setText(str(self.selAccount.numero))            
            self.cmbEB.setCurrentIndex(self.cmbEB.findData(self.selAccount.eb.id))
            self.cmbEB.setEnabled(False)    
            self.cmbCurrency.setCurrentIndex(self.cmbCurrency.findData(self.selAccount.currency.id))
            self.cmbCurrency.setEnabled(False)
            self.chkActiva.setChecked(b2c(self.selAccount.activa))
            self.cmdDatos.setText(self.trUtf8("Modificar los datos de la cuenta bancaria"))

            anoinicio=Assets(self.mem).primera_fecha_con_datos_usuario().year       
            self.wdgYM.initiate(anoinicio,  datetime.date.today().year, datetime.date.today().year, datetime.date.today().month)
            QObject.connect(self.wdgYM, SIGNAL("changed"), self.on_wdgYM_changed)

#            self.load_data_from_db()

            self.on_wdgYM_changed()
            self.on_chkCreditCards_stateChanged(self.chkCreditCards.checkState())        
            
#        
#    def load_data_from_db(self):
#        inicio=datetime.datetime.now()
#        print("\n","Cargando data en wdgInvestments",  datetime.datetime.now()-inicio)
#            
#    def load_inactive_data_from_db(self):
#        if self.loadedinactive==False:
#            inicio=datetime.datetime.now()        
#            self.mem.data.load_inactives()
#            print("\n","Cargando data en wdgInvestments",  datetime.datetime.now()-inicio)
#            self.loadedinactive=True
#            
#        print (self.trUtf8("Ya se habían cargado las inactivas"))
    def load_tabOperCreditCards(self):     
        self.selCreditCard.op_diferido=sorted(self.selCreditCard.op_diferido, key=lambda o:o.fecha)
        self.tblCreditCardOpers.setRowCount(len(self.selCreditCard.op_diferido));        
        for i,  o in enumerate(self.selCreditCard.op_diferido):
            self.tblCreditCardOpers.setItem(i, 0, QTableWidgetItem(str(o.fecha)))
            self.tblCreditCardOpers.setItem(i, 1, QTableWidgetItem((o.concepto.name)))
            self.tblCreditCardOpers.setItem(i, 2, self.selAccount.currency.qtablewidgetitem(o.importe))
            self.tblCreditCardOpers.setItem(i, 3, QTableWidgetItem(o.comentario))
         #actualiza balance en tblCreditCards   
        self.tblCreditCards.setItem(self.tblCreditCards.currentRow(), 5, self.selAccount.currency.qtablewidgetitem(self.selCreditCard.saldo_pendiente()))
        self.tblCreditCardOpers.clearSelection()
        self.setSelOperCreditCards=set([])
         
        
    def load_tabCreditCards(self):     
        self.tblCreditCards.setRowCount(len(self.tarjetas.arr))        
        for i, t in enumerate(self.tarjetas.arr):
            self.tblCreditCards.setItem(i, 0, QTableWidgetItem(t.name))
            self.tblCreditCards.setItem(i, 1, QTableWidgetItem(str(t.numero)))
            self.tblCreditCards.setItem(i, 2, qbool(t.activa))
            self.tblCreditCards.setItem(i, 3, qbool(t.pagodiferido))
            self.tblCreditCards.setItem(i, 4, self.selAccount.currency.qtablewidgetitem(t.saldomaximo, ))
            self.tblCreditCards.setItem(i, 5, self.selAccount.currency.qtablewidgetitem(t.saldo_pendiente()))


    @QtCore.pyqtSlot() 
    def on_actionCreditCardAdd_activated(self):
        w=frmCreditCardsAdd(self.mem,  self.selAccount,  None, self)
        w.exec_()
        self.on_chkCreditCards_stateChanged(Qt.Unchecked)
        
    @QtCore.pyqtSlot() 
    def on_actionCreditCardEdit_activated(self):
        w=frmCreditCardsAdd(self.mem, self.selAccount,  self.selCreditCard, self)
        w.exec_()
        self.tblCreditCards.clearSelection()
        self.on_chkCreditCards_stateChanged(self.chkCreditCards.checkState())
        
    @QtCore.pyqtSlot() 
    def on_actionCreditCardActivate_activated(self):
        if self.selAccount.qmessagebox_inactive() or self.selAccount.eb.qmessagebox_inactive():
            return
            
        if self.actionCreditCardActivate.isChecked():#Ha pasado de inactiva a activa
            self.selCreditCard.activa=True
            self.mem.data.tarjetas_inactive.arr.remove(self.selCreditCard)
            self.mem.data.tarjetas_active.arr.append(self.selCreditCard)
        else:
            self.selCreditCard.activa=False
            self.mem.data.tarjetas_inactive.arr.append(self.selCreditCard)
            self.mem.data.tarjetas_active.arr.remove(self.selCreditCard)
        self.selCreditCard.save()
        self.mem.con.commit()
        
        self.on_chkCreditCards_stateChanged(self.chkCreditCards.checkState())
                
    @QtCore.pyqtSlot() 
    def on_actionCreditCardDelete_activated(self):
        if self.selCreditCard.borrar()==False:
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.trUtf8("No se ha borrado la tarjeta por tener registros dependientes"))
            m.exec_()                 
        self.mem.con.commit()
        self.mem.data.tarjetas_active.arr.remove(self.selCreditCard)
        self.tblCreditCards.clearSelection()
        self.on_chkCreditCards_stateChanged(self.chkCreditCards.checkState())

    def on_chkCreditCards_stateChanged(self, state):        
        if state==Qt.Unchecked:
            self.tarjetas=self.mem.data.tarjetas_active.clone_of_account(self.selAccount)
        else:
            self.mem.data.load_inactives()
            self.tarjetas=self.mem.data.tarjetas_inactive.clone_of_account(self.selAccount)
        self.load_tabCreditCards() 
        self.selCreditCard=None
        self.tblCreditCards.clearSelection()

    def on_cmdDatos_released(self):
        id_entidadesbancarias=int(self.cmbEB.itemData(self.cmbEB.currentIndex()))
        cuenta=self.txtAccount.text()
        numerocuenta=self.txtNumero.text()
        cu_activa=c2b(self.chkActiva.checkState())
        currency=self.cmbCurrency.itemData(self.cmbCurrency.currentIndex())

        if self.selAccount==None:
            cu=Account(self.mem).init__create(cuenta, self.mem.data.ebs_active.find(id_entidadesbancarias), cu_activa, numerocuenta, self.mem.currencies.find(currency))
            cu.save()
            self.mem.data.cuentas_active.arr.append(cu)
        else:
            self.selAccount.eb=self.mem.data.ebs_active.find(id_entidadesbancarias)
            self.selAccount.name=cuenta
            self.selAccount.numero=numerocuenta
            self.selAccount.activa=cu_activa
            self.selAccount.currency=self.mem.currencies.find(currency)
            self.selAccount.save()
            self.lblTitulo.setText(self.selAccount.name)
        self.mem.con.commit()
        
        if self.selAccount==None:
            self.done(0)
        self.cmdDatos.setEnabled(False)   

    @pyqtSlot()
    def on_wdgYM_changed(self):
        cur = self.mem.con.cursor()      
        self.opercuentas=[]
        self.saldoiniciomensual=self.selAccount.saldo_from_db( str(datetime.date(self.wdgYM.year, self.wdgYM.month, 1)-datetime.timedelta(days=1)))         
        if self.saldoiniciomensual==None:
            self.saldoiniciomensual=0
        cur.execute("select * from opercuentas where id_cuentas="+str(self.selAccount.id)+" and date_part('year',fecha)="+str(self.wdgYM.year)+" and date_part('month',fecha)="+str(self.wdgYM.month)+" order by fecha, id_opercuentas")
        for o in cur:
            self.opercuentas.append(AccountOperation(self.mem).init__db_row(o, self.mem.conceptos.find(o['id_conceptos']), self.mem.tiposoperaciones.find(o['id_tiposoperaciones']), self.selAccount))
        cur.close()     
        self.load_tblOperaciones()  
            
    def load_tblOperaciones(self):
        self.tblOperaciones.setRowCount(len(self.opercuentas)+1)        
        self.tblOperaciones.setItem(0, 1, QTableWidgetItem(("balance al iniciar el mes")))
        self.tblOperaciones.setItem(0, 3, self.selAccount.currency.qtablewidgetitem(self.saldoiniciomensual))
        saldoinicio=self.saldoiniciomensual
        for i, o in enumerate(self.opercuentas):
            saldoinicio=saldoinicio+o.importe
            self.tblOperaciones.setItem(i+1, 0, QTableWidgetItem(str(o.fecha)))
            self.tblOperaciones.setItem(i+1, 1, QTableWidgetItem(o.concepto.name))
            self.tblOperaciones.setItem(i+1, 2, self.selAccount.currency.qtablewidgetitem(o.importe))
            self.tblOperaciones.setItem(i+1, 3, self.selAccount.currency.qtablewidgetitem(saldoinicio))
            self.tblOperaciones.setItem(i+1, 4, QTableWidgetItem(o.comment()))        

    @QtCore.pyqtSlot() 
    def on_actionOperationAdd_activated(self):
        w=frmAccountOperationsAdd(self.mem, self.mem.data.cuentas_active,  self.selAccount, None, None)
        self.connect(w, SIGNAL("OperAccountIBMed"), self.on_wdgYM_changed)
        w.exec_()
        self.load_tblOperaciones()
        self.tblOperaciones.clearSelection()
        self.selOperAccount=None



    @QtCore.pyqtSlot() 
    def on_actionTransferDelete_activated(self):
        
        oc_other=AccountOperation(self.mem).init__db_query(int(self.selOperAccount.comentario.split("|")[1]))
        
        if self.selOperAccount.concepto.id==4:#Tranfer origin
            account_origin=self.selAccount
            account_destiny=self.mem.data.cuentas_all().find(int(self.selOperAccount.comentario.split("|")[0]))
            oc_comision_id=int(self.selOperAccount.comentario.split("|")[2])
    
        if self.selOperAccount.concepto.id==5:#Tranfer destiny
            account_origin=self.mem.data.cuentas_all().find(int(self.selOperAccount.comentario.split("|")[0]))
            account_destiny=self.selAccount
            oc_comision_id=int(oc_other.comentario.split("|")[2])
            
        message=self.trUtf8("Do you really want to delete transfer from {0} to {1}, with amount {2} and it's commision?".format(account_origin.name, account_destiny.name, self.selOperAccount.importe))
        reply = QMessageBox.question(self, 'Message', message, QMessageBox.Yes, QMessageBox.No)
            
        if reply == QMessageBox.Yes:
            if oc_comision_id!=0:
                oc_comision=AccountOperation(self.mem).init__db_query(oc_comision_id)
                oc_comision.borrar()
            self.selOperAccount.borrar()
            oc_other.borrar()
            self.mem.con.commit()
            self.on_wdgYM_changed()
            self.tblOperaciones.clearSelection()
            self.selOperAccount=None
        
    @QtCore.pyqtSlot() 
    def on_actionOperationEdit_activated(self):
        w=frmAccountOperationsAdd(self.mem, self.mem.data.cuentas_active,  self.selAccount, self.selOperAccount, None)
        self.connect(w, SIGNAL("OperAccountIBMed"), self.on_wdgYM_changed)#Actualiza movimientos como si cmd
        w.exec_()
        self.load_tblOperaciones()
        self.tblOperaciones.clearSelection()
        self.selOperAccount=None

    @QtCore.pyqtSlot() 
    def on_actionOperationDelete_activated(self):
        self.selOperAccount.borrar() 
        self.mem.con.commit()  
        self.opercuentas.remove(self.selOperAccount)         
        self.load_tblOperaciones()
        self.tblOperaciones.clearSelection()
        self.selOperAccount=None

    @QtCore.pyqtSlot() 
    def on_actionCreditCardOperAdd_activated(self):
        if self.selCreditCard.pagodiferido==False:
            w=frmAccountOperationsAdd(self.mem, self.mem.data.cuentas_active, self.selAccount, None)
            self.connect(w, SIGNAL("OperAccountIBMed"), self.on_wdgYM_changed)
            w.lblTitulo.setText(((self.selCreditCard.name)))
            w.txtComentario.setText(self.tr("CreditCard {0}. ".format((self.selCreditCard.name))))
            w.exec_()
        else:            
            w=frmAccountOperationsAdd(self.mem, self.mem.data.cuentas_active,  self.selAccount, None, self.selCreditCard)
            self.connect(w, SIGNAL("OperCreditCardIBMed"), self.load_tabOperCreditCards)
            w.lblTitulo.setText(self.tr("CreditCard {0}".format((self.selCreditCard.name))))
            w.exec_()
            
    @QtCore.pyqtSlot() 
    def on_actionCreditCardOperEdit_activated(self):
        #Como es unico
        for s in self.setSelOperCreditCards:
            selOperCreditCard=s
        w=frmAccountOperationsAdd(self.mem, self.mem.data.cuentas_active,  self.selAccount, None, self.selCreditCard, selOperCreditCard)
        self.connect(w, SIGNAL("OperCreditCardIBMed"), self.load_tabOperCreditCards)
        w.lblTitulo.setText(self.tr("CreditCard {0}".format((self.selCreditCard.name))))
        w.exec_()

    @QtCore.pyqtSlot() 
    def on_actionCreditCardOperDelete_activated(self):
        for o in self.setSelOperCreditCards:
            o.borrar()
            self.selCreditCard.op_diferido.remove(o)
        self.mem.con.commit()
        self.load_tabOperCreditCards()

    def on_tblOperaciones_customContextMenuRequested(self,  pos):      
        if self.selAccount.qmessagebox_inactive() or self.selAccount.eb.qmessagebox_inactive():
            return

        if self.selOperAccount==None:
            self.actionOperationDelete.setEnabled(False)
            self.actionOperationEdit.setEnabled(False)   
            self.actionTransferDelete.setEnabled(False)
        else:
            if self.selOperAccount.es_editable()==False:
                self.actionOperationDelete.setEnabled(False)
                self.actionOperationEdit.setEnabled(False)   
                #Una transferencia bien formada no es editable solo con transfer delete.
                if (self.selOperAccount.concepto.id==4 and len(self.selOperAccount.comentario.split("|"))==3) or (self.selOperAccount.concepto.id==5 and len(self.selOperAccount.comentario.split("|"))==2):#Tranfer origin or Tranfer destine
                    self.actionTransferDelete.setEnabled(True)
                else:
                    self.actionTransferDelete.setEnabled(False)
            else: #es editable
                self.actionOperationDelete.setEnabled(True)    
                self.actionOperationEdit.setEnabled(True)      
                self.actionTransferDelete.setEnabled(False)  
            
        menu=QMenu()
        menu.addAction(self.actionOperationAdd)
        menu.addAction(self.actionOperationEdit)
        menu.addAction(self.actionOperationDelete)
        menu.addSeparator()
        menu.addAction(self.actionTransferDelete)
        menu.exec_(self.tblOperaciones.mapToGlobal(pos))

    def on_tblOperaciones_itemSelectionChanged(self):
        try:
            for i in self.tblOperaciones.selectedItems():#itera por cada item no row.
                self.selOperAccount=self.opercuentas[i.row()-1]
        except:
            self.selOperAccount=None
        print ("Seleccionado: " +  str(self.selOperAccount))
        

    def on_tblCreditCards_customContextMenuRequested(self,  pos):
        if self.selAccount.qmessagebox_inactive():
            return 
        menu=QMenu()
        menu.addAction(self.actionCreditCardOperAdd)
        menu.addSeparator()
        menu.addAction(self.actionCreditCardAdd)
        menu.addAction(self.actionCreditCardEdit)
        menu.addAction(self.actionCreditCardDelete)
        menu.addSeparator()
        menu.addAction(self.actionCreditCardActivate)
        
        if self.selCreditCard==None:
            self.actionCreditCardDelete.setEnabled(False)
            self.actionCreditCardEdit.setEnabled(False)
            self.actionCreditCardActivate.setEnabled(False)
        else:
            self.actionCreditCardDelete.setEnabled(True)
            self.actionCreditCardEdit.setEnabled(True)
            self.actionCreditCardActivate.setEnabled(True)
            if self.selCreditCard.activa==True:
                self.actionCreditCardActivate.setChecked(True)
            else:
                self.actionCreditCardActivate.setChecked(False)
        menu.exec_(self.tblCreditCards.mapToGlobal(pos))



    def on_tblCreditCards_itemSelectionChanged(self):
        try:
            for i in self.tblCreditCards.selectedItems():#itera por cada item no row.
                self.selCreditCard=self.tarjetas.arr[i.row()]
        except:
            self.selCreditCard=None
            self.tblCreditCardOpers.setRowCount(0)
            
        if self.selCreditCard==None:
            return
        if self.selCreditCard.pagodiferido==True:
            self.load_tabOperCreditCards()         
        else:
            self.tblCreditCardOpers.setRowCount(0)
        self.tabOpertarjetasDiferidas.setCurrentIndex(0)
        self.tabOpertarjetasDiferidas.setEnabled(self.selCreditCard.pagodiferido)
        print ("Seleccionado: " +  str(self.selCreditCard.name))

    def on_tblCreditCardOpers_customContextMenuRequested(self,  pos):
        if self.selAccount.qmessagebox_inactive() or self.selAccount.eb.qmessagebox_inactive() or self.selCreditCard.qmessagebox_inactive():
            return
        
        if len(self.setSelOperCreditCards)!=1: # 0 o más de 1
            self.actionCreditCardOperDelete.setEnabled(False)
            self.actionCreditCardOperEdit.setEnabled(False)
        else:
            self.actionCreditCardOperDelete.setEnabled(True)
            self.actionCreditCardOperEdit.setEnabled(True)
            
        menu=QMenu()
        menu.addAction(self.actionCreditCardOperAdd)
        menu.addAction(self.actionCreditCardOperEdit)
        menu.addAction(self.actionCreditCardOperDelete)
        
        
            
        
        menu.exec_(self.tblCreditCardOpers.mapToGlobal(pos))


    def on_tblCreditCardOpers_itemSelectionChanged(self):
        sel=[]
        self.totalOperCreditCards=Decimal(0)
        for i in self.tblCreditCardOpers.selectedItems():#itera por cada item no row.
            if i.column()==0:
                sel.append(self.selCreditCard.op_diferido[i.row()])  
        self.setSelOperCreditCards=set(sel)
        
        #Activa el grp Pago
        if len(self.setSelOperCreditCards)>0:
            self.grpPago.setEnabled(True)
        else:
            self.grpPago.setEnabled(False)
        
        #Calcula el balance
        for o in self.setSelOperCreditCards:
            self.totalOperCreditCards=self.totalOperCreditCards+Decimal(o.importe)
        self.lblPago.setText(self.mem.localcurrency.string(self.totalOperCreditCards, 2))
 
    def on_cmdPago_released(self):
        comentario="{0}|{1}".format(self.selCreditCard.name, len(self.setSelOperCreditCards))
        fechapago=self.calPago.date().toPyDate()
        c=AccountOperation(self.mem).init__create(fechapago, self.mem.conceptos.find(40), self.mem.tiposoperaciones.find(7), self.totalOperCreditCards, comentario, self.selAccount)
        c.save()
        
        #Modifica el registro y lo pone como pagado y la fecha de pago y añade la opercuenta
        for o in self.setSelOperCreditCards:
            o.fechapago=fechapago
            o.pagado=True
            o.opercuenta=c
            o.save()
            self.selCreditCard.op_diferido.remove(o)
        self.mem.con.commit()
        self.load_tabOperCreditCards()         
        self.on_wdgYM_changed()  

    
    def on_cmdDevolverPago_released(self):
        print ("solo uno")
        id_opercuentas=self.cmbFechasPago.itemData(int(self.cmbFechasPago.currentIndex()))
        cur = self.mem.con.cursor()      
        cur.execute("delete from opercuentas where id_opercuentas=%s", (id_opercuentas, ))#No merece crear objeto
        cur.execute("update opertarjetas set fechapago=null, pagado=false, id_opercuentas=null where id_opercuentas=%s", (id_opercuentas, ) )
        self.mem.con.commit()
        self.selCreditCard.get_opertarjetas_diferidas_pendientes()
        self.on_cmdMovimientos_released()
        self.load_tabOperCreditCards()
        cur.close()     
        self.tabOpertarjetasDiferidas.setCurrentIndex(0)     
        
    @QtCore.pyqtSlot(int) 
    def on_cmbFechasPago_currentIndexChanged(self, index):
        id_opercuentas=self.cmbFechasPago.itemData(int(self.cmbFechasPago.currentIndex()))
        print (id_opercuentas)            
        con=self.mem.connect_xulpymoney()
        cur = con.cursor()      
        cur.execute("select id_opertarjetas,fecha,conceptos.concepto,importe,comentario from opertarjetas,conceptos where opertarjetas.id_conceptos=conceptos.id_conceptos and id_opercuentas=%s;", (id_opercuentas, ))
        self.tblOpertarjetasHistoricas.clearContents()
        self.tblOpertarjetasHistoricas.setRowCount(cur.rowcount);       
        balance=0
        for rec in cur:
            balance=balance+rec['importe']
            self.tblOpertarjetasHistoricas.setItem(cur.rownumber-1, 0, QTableWidgetItem(str(rec['id_opertarjetas'])))
            self.tblOpertarjetasHistoricas.setItem(cur.rownumber-1, 1, QTableWidgetItem(str(rec['fecha'])))
            self.tblOpertarjetasHistoricas.setItem(cur.rownumber-1, 2, QTableWidgetItem((rec['concepto'])))
            self.tblOpertarjetasHistoricas.setItem(cur.rownumber-1, 3, self.selAccount.currency.qtablewidgetitem(rec['importe']))
            self.tblOpertarjetasHistoricas.setItem(cur.rownumber-1, 4, self.selAccount.currency.qtablewidgetitem(balance))
            self.tblOpertarjetasHistoricas.setItem(cur.rownumber-1, 5, QTableWidgetItem((rec['comentario'])))
        cur.close()     
        self.mem.disconnect_xulpymoney(con)      

    def on_tabOpertarjetasDiferidas_currentChanged(self, index): 
        if  index==1: #PAGOS
            #Carga combo
            self.cmbFechasPago.clear()
            con=self.mem.connect_xulpymoney()
            cur = con.cursor()       
            cur2=con.cursor()
            cur.execute("select distinct(fechapago), id_opercuentas from opertarjetas where id_tarjetas=%s and fechapago is not null  order by fechapago;", (self.selCreditCard.id, ))
            for row in cur:  
                cur2.execute("select importe from opercuentas where id_opercuentas=%s", (row['id_opercuentas'], ))
                importe=cur2.fetchone()["importe"]
                self.cmbFechasPago.addItem(self.tr("Pago efectuado el {0} de {1}".format(row['fechapago'],  self.mem.localcurrency.string(-importe))),row['id_opercuentas'])
            self.cmbFechasPago.setCurrentIndex(cur.rowcount-1)
            cur.close()     
            cur2.close()
            self.mem.disconnect_xulpymoney(con)      
            

    def on_txtAccount_textChanged(self):
        self.cmdDatos.setEnabled(True)
    def on_txtNumero_textChanged(self):
        self.cmdDatos.setEnabled(True)
    def on_cmbEB_currentIndexChanged(self, index):
        self.cmdDatos.setEnabled(True)
    def on_chkActiva_stateChanged(self,  state):
        self.cmdDatos.setEnabled(True)
