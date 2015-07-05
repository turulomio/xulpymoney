from PyQt5.QtCore import *
from PyQt5.QtGui import *
from libxulpymoney import *
from Ui_frmAccountsReport import *
from frmAccountOperationsAdd import *
from frmCreditCardsAdd import *
from frmInvestmentOperationsAdd import *

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
        self.selAccount=cuenta#Registro de selAccount
        
        self.opercuentas=[]#Array de objetos CUentaOperacion
        self.creditcards=None#SetCreditCard,
        self.creditcardsoperations=SetCreditCardOperations(self.mem)#SetCreditCardOperations
        
        
        self.saldoiniciomensual=0#Almacena el inicio según on_cmdMovimientos_released
          
        self.tblOperaciones.settings("frmAccountsReport",  self.mem)
        self.tblCreditCards.settings("frmAccountsReport",  self.mem)
        self.tblCreditCardOpers.settings("frmAccountsReport",  self.mem)
        self.tblOpertarjetasHistoricas.settings("frmAccountsReport",  self.mem)
    
        self.calPago.setDate(QDate.currentDate())
        
        self.mem.currencies.qcombobox(self.cmbCurrency)
        self.mem.data.banks_active.qcombobox(self.cmbEB)
                    
        if self.selAccount==None:
            self.lblTitulo.setText(self.tr("New account data"))
            self.tab.setCurrentIndex(0)
            self.tab.setTabEnabled(1, False)
            self.tab.setTabEnabled(2, False)
            self.chkActiva.setChecked(Qt.Checked)
            self.chkActiva.setEnabled(False)
            self.cmdDatos.setText(self.tr("Add a new account"))
        else:               
            self.tab.setCurrentIndex(0)
            self.lblTitulo.setText(self.selAccount.name)
            self.txtAccount.setText(self.selAccount.name)
            self.txtNumero.setText(str(self.selAccount.numero))            
            self.cmbEB.setCurrentIndex(self.cmbEB.findData(self.selAccount.eb.id))
            self.cmbEB.setEnabled(False)    
            self.cmbCurrency.setCurrentIndex(self.cmbCurrency.findData(self.selAccount.currency.id))
            self.cmbCurrency.setEnabled(False)
            self.chkActiva.setChecked(b2c(self.selAccount.active))
            self.cmdDatos.setText(self.tr("Update account data"))

            anoinicio=Assets(self.mem).primera_datetime_con_datos_usuario().year       
            self.wdgYM.initiate(anoinicio,  datetime.date.today().year, datetime.date.today().year, datetime.date.today().month)
            self.on_wdgYM_changed()
            self.wdgYM.changed.connect(self.on_wdgYM_changed)
            self.on_chkCreditCards_stateChanged(self.chkCreditCards.checkState())        
            

    def load_tabOperCreditCards(self):     
        self.creditcardsoperations.myqtablewidget(self.tblCreditCardOpers, "frmAccountsReport")
        self.creditcardsoperations.selected=SetCreditCardOperations(self.mem)
         
        
    def load_tabCreditCards(self):     
        self.creditcards.myqtablewidget(self.tblCreditCards, "frmAccountsReport")

    @QtCore.pyqtSlot() 
    def on_actionCreditCardAdd_triggered(self):
        w=frmCreditCardsAdd(self.mem,  self.selAccount,  None, self)
        w.exec_()
        self.on_chkCreditCards_stateChanged(Qt.Unchecked)
        
    @QtCore.pyqtSlot() 
    def on_actionCreditCardEdit_triggered(self):
        w=frmCreditCardsAdd(self.mem, self.selAccount,  self.creditcards.selected, self)
        w.exec_()
        self.tblCreditCards.clearSelection()
        self.on_chkCreditCards_stateChanged(self.chkCreditCards.checkState())
        
    @QtCore.pyqtSlot() 
    def on_actionCreditCardActivate_triggered(self):
        if self.selAccount.qmessagebox_inactive() or self.selAccount.eb.qmessagebox_inactive():
            return
            
        if self.actionCreditCardActivate.isChecked():#Ha pasado de inactiva a activa
            self.creditcards.selected.active=True
            self.mem.data.creditcards_inactive.remove(self.creditcards.selected)
            self.mem.data.creditcards_active.append(self.creditcards.selected)
        else:
            self.creditcards.selected.active=False
            self.mem.data.creditcards_inactive.append(self.creditcards.selected)
            self.mem.data.creditcards_active.remove(self.creditcards.selected)
        self.creditcards.selected.save()
        self.mem.con.commit()
        
        self.on_chkCreditCards_stateChanged(self.chkCreditCards.checkState())
                
    @QtCore.pyqtSlot() 
    def on_actionCreditCardDelete_triggered(self):
        if self.creditcards.selected.borrar()==False:
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.tr("I can't delete the credit card, because it has dependent registers"))
            m.exec_()                 
        self.mem.con.commit()
        self.mem.data.creditcards_active.arr.remove(self.creditcards.selected)
        self.tblCreditCards.clearSelection()
        self.on_chkCreditCards_stateChanged(self.chkCreditCards.checkState())

    def on_chkCreditCards_stateChanged(self, state):        
        if state==Qt.Unchecked:
            self.creditcards=self.mem.data.creditcards_active.clone_of_account(self.selAccount)
        else:
            self.mem.data.load_inactives()
            self.creditcards=self.mem.data.creditcards_inactive.clone_of_account(self.selAccount)
        self.load_tabCreditCards() 
        self.creditcards.selected=None
        self.tblCreditCards.clearSelection()

    def on_cmdDatos_released(self):
        id_entidadesbancarias=int(self.cmbEB.itemData(self.cmbEB.currentIndex()))
        cuenta=self.txtAccount.text()
        numerocuenta=self.txtNumero.text()
        active=c2b(self.chkActiva.checkState())
        currency=self.cmbCurrency.itemData(self.cmbCurrency.currentIndex())

        if self.selAccount==None:
            cu=Account(self.mem).init__create(cuenta, self.mem.data.banks_active.find(id_entidadesbancarias), active, numerocuenta, self.mem.currencies.find(currency))
            cu.save()
            self.mem.data.accounts_active.append(cu) #Always to active
        else:
            self.selAccount.eb=self.mem.data.banks_active.find(id_entidadesbancarias)
            self.selAccount.name=cuenta
            self.selAccount.numero=numerocuenta
            self.selAccount.active=active
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
        self.saldoiniciomensual=self.selAccount.balance(datetime.date(self.wdgYM.year, self.wdgYM.month, 1)-datetime.timedelta(days=1))         
        if self.saldoiniciomensual==None:
            self.saldoiniciomensual=0
        
        cur.execute("select * from opercuentas where id_cuentas=%s and date_part('year',datetime)=%s and date_part('month',datetime)=%s order by datetime, id_opercuentas", (self.selAccount.id, self.wdgYM.year, self.wdgYM.month))
        for o in cur:
            self.opercuentas.append(AccountOperation(self.mem).init__db_row(o, self.mem.conceptos.find(o['id_conceptos']), self.mem.tiposoperaciones.find(o['id_tiposoperaciones']), self.selAccount))
        cur.close()     
        self.load_tblOperaciones()  
            
    def load_tblOperaciones(self):
        self.tblOperaciones.setRowCount(len(self.opercuentas)+1)        
        self.tblOperaciones.setItem(0, 1, QTableWidgetItem(self.tr("Starting month balance")))
        self.tblOperaciones.setItem(0, 3, self.selAccount.currency.qtablewidgetitem(self.saldoiniciomensual))
        saldoinicio=self.saldoiniciomensual
        for i, o in enumerate(self.opercuentas):
            saldoinicio=saldoinicio+o.importe
            self.tblOperaciones.setItem(i+1, 0, qdatetime(o.datetime, self.mem.localzone))
            self.tblOperaciones.setItem(i+1, 1, QTableWidgetItem(o.concepto.name))
            self.tblOperaciones.setItem(i+1, 2, self.selAccount.currency.qtablewidgetitem(o.importe))
            self.tblOperaciones.setItem(i+1, 3, self.selAccount.currency.qtablewidgetitem(saldoinicio))
            self.tblOperaciones.setItem(i+1, 4, QTableWidgetItem(o.comment()))        

    @QtCore.pyqtSlot() 
    def on_actionOperationAdd_triggered(self):
        w=frmAccountOperationsAdd(self.mem, self.mem.data.accounts_active,  self.selAccount, None, None)
        w.OperAccountIBMed.connect(self.on_wdgYM_changed)
        w.exec_()
        self.load_tblOperaciones()
        self.tblOperaciones.clearSelection()
        self.selOperAccount=None



    @QtCore.pyqtSlot() 
    def on_actionTransferDelete_triggered(self):
        
        oc_other=AccountOperation(self.mem).init__db_query(int(self.selOperAccount.comentario.split("|")[1]))
        
        if self.selOperAccount.concepto.id==4:#Tranfer origin
            account_origin=self.selAccount
            account_destiny=self.mem.data.accounts_all().find(int(self.selOperAccount.comentario.split("|")[0]))
            oc_comision_id=int(self.selOperAccount.comentario.split("|")[2])
    
        if self.selOperAccount.concepto.id==5:#Tranfer destiny
            account_origin=self.mem.data.accounts_all().find(int(self.selOperAccount.comentario.split("|")[0]))
            account_destiny=self.selAccount
            oc_comision_id=int(oc_other.comentario.split("|")[2])
            
        message=self.tr("Do you really want to delete transfer from {0} to {1}, with amount {2} and it's commision?").format(account_origin.name, account_destiny.name, self.selOperAccount.importe)
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
    def on_actionOperationEdit_triggered(self):
        w=frmAccountOperationsAdd(self.mem, self.mem.data.accounts_active,  self.selAccount, self.selOperAccount, None)
        w.OperAccountIBMed.connect(self.on_wdgYM_changed)
        w.exec_()
        self.load_tblOperaciones()
        self.tblOperaciones.clearSelection()
        self.selOperAccount=None

    @QtCore.pyqtSlot() 
    def on_actionOperationDelete_triggered(self):
        self.selOperAccount.borrar() 
        self.mem.con.commit()  
        self.opercuentas.remove(self.selOperAccount)         
        self.load_tblOperaciones()
        self.tblOperaciones.clearSelection()
        self.selOperAccount=None

    @QtCore.pyqtSlot() 
    def on_actionCreditCardOperAdd_triggered(self):
        if self.creditcards.selected.pagodiferido==False:
            w=frmAccountOperationsAdd(self.mem, self.mem.data.accounts_active, self.selAccount, None)
            w.OperAccountIBMed.connect(self.on_wdgYM_changed)
            w.lblTitulo.setText(self.creditcards.selected.name)
            w.txtComentario.setText(self.tr("CreditCard {0}. ").format(self.creditcards.selected.name))
            w.exec_()
        else:            
            w=frmAccountOperationsAdd(self.mem, self.mem.data.accounts_active,  self.selAccount, None, self.creditcards.selected)
            w.OperCreditCardIBMed.connect(self.load_tabOperCreditCards)
            w.lblTitulo.setText(self.tr("CreditCard {0}").format(self.creditcards.selected.name))
            w.exec_()
            
    @QtCore.pyqtSlot() 
    def on_actionCreditCardOperEdit_triggered(self):
        #Como es unico
        selOperCreditCard=self.creditcardsoperations.selected.arr[0]
        w=frmAccountOperationsAdd(self.mem, self.mem.data.accounts_active,  self.selAccount, None, self.creditcards.selected, selOperCreditCard)
        w.OperCreditCardIBMed.connect(self.load_tabOperCreditCards)
        w.lblTitulo.setText(self.tr("CreditCard {0}").format(self.creditcards.selected.name))
        w.exec_()

    @QtCore.pyqtSlot() 
    def on_actionCreditCardOperDelete_triggered(self):
        for o in self.creditcardsoperations.selected.arr:
            o.borrar()
            self.creditcardsoperations.arr.remove(o)
        self.mem.con.commit()
        self.load_tabOperCreditCards()

    @QtCore.pyqtSlot() 
    def on_actionInvestmentOperationDelete_triggered(self):
        investmentoperation=InvestmentOperation(self.mem).init__from_accountoperation(self.selOperAccount)
        investmentoperation.inversion.op.remove(investmentoperation)
        self.mem.con.commit()     
        self.on_wdgYM_changed()
        self.tblOperaciones.clearSelection()
        self.selOperAccount=None


    @QtCore.pyqtSlot() 
    def on_actionInvestmentOperationEdit_triggered(self):
        investmentoperation=InvestmentOperation(self.mem).init__from_accountoperation(self.selOperAccount)
        w=frmInvestmentOperationsAdd(self.mem, investmentoperation.inversion, investmentoperation, self)
        w.exec_()
        self.on_wdgYM_changed()
        self.tblOperaciones.clearSelection()
        self.selOperAccount=None

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
        if self.selOperAccount!=None:
            if self.selOperAccount.concepto.id in [29, 35]:#Shares sale or purchase, allow edit or delete investment operation
                menu.addSeparator()
                menu.addAction(self.actionInvestmentOperationEdit)
                menu.addAction(self.actionInvestmentOperationDelete)
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
        
        if self.creditcards.selected==None:
            self.actionCreditCardDelete.setEnabled(False)
            self.actionCreditCardEdit.setEnabled(False)
            self.actionCreditCardActivate.setEnabled(False)
        else:
            self.actionCreditCardDelete.setEnabled(True)
            self.actionCreditCardEdit.setEnabled(True)
            self.actionCreditCardActivate.setEnabled(True)
            if self.creditcards.selected.active==True:
                self.actionCreditCardActivate.setChecked(True)
            else:
                self.actionCreditCardActivate.setChecked(False)
        menu.exec_(self.tblCreditCards.mapToGlobal(pos))



    def on_tblCreditCards_itemSelectionChanged(self):
        try:
            for i in self.tblCreditCards.selectedItems():#itera por cada item no row.
                self.creditcards.selected=self.creditcards.arr[i.row()]
        except:
            self.creditcards.selected=None
            self.tblCreditCardOpers.setRowCount(0)
            
        if self.creditcards.selected==None:
            return

        if self.creditcards.selected.pagodiferido==True:
            self.creditcardsoperations.load_from_db(mogrify(self.mem.con,"select * from opertarjetas where id_tarjetas=%s and pagado=false", [self.creditcards.selected.id, ]))
            self.creditcardsoperations.myqtablewidget(self.tblCreditCardOpers, "frmAccountsReport")
            self.creditcardsoperations.selected=SetCreditCardOperations(self.mem)
        else:
            self.tblCreditCardOpers.setRowCount(0)
        self.tabOpertarjetasDiferidas.setCurrentIndex(0)
        self.tabOpertarjetasDiferidas.setEnabled(self.creditcards.selected.pagodiferido)
        print ("Seleccionado: " +  str(self.creditcards.selected.name))

    def on_tblCreditCardOpers_customContextMenuRequested(self,  pos):
        if self.selAccount.qmessagebox_inactive() or self.selAccount.eb.qmessagebox_inactive() or self.creditcards.selected.qmessagebox_inactive():
            return
        
        if self.creditcardsoperations.selected.length()!=1: # 0 o más de 1
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
        self.creditcardsoperations.selected=SetCreditCardOperations(self.mem)
        for i in self.tblCreditCardOpers.selectedItems():#itera por cada item no row.
            if i.column()==0:
                self.creditcardsoperations.selected.append(self.creditcardsoperations.arr[i.row()])  
        
        #Activa el grp Pago
        if self.creditcardsoperations.selected.length()>0:
            self.grpPago.setEnabled(True)
        else:
            self.grpPago.setEnabled(False)

        #Calcula el balance
        self.lblPago.setText(self.mem.localcurrency.string(self.creditcardsoperations.selected.balance()))
 
    def on_cmdPago_released(self):
        comentario="{0}|{1}".format(self.creditcards.selected.name, self.creditcardsoperations.selected.length())
        fechapago=self.calPago.date().toPyDate()
        c=AccountOperation(self.mem).init__create(fechapago, self.mem.conceptos.find(40), self.mem.tiposoperaciones.find(7), self.creditcardsoperations.selected.balance(), comentario, self.selAccount)
        c.save()
        
        #Modifica el registro y lo pone como pagado y la datetime de pago y añade la opercuenta
        for o in self.creditcardsoperations.selected.arr:
            o.fechapago=fechapago
            o.pagado=True
            o.opercuenta=c
            o.save()
            self.creditcardsoperations.arr.remove(o)
        self.mem.con.commit()
        self.load_tabOperCreditCards()         
        self.on_wdgYM_changed()  

    
    def on_cmdDevolverPago_released(self):
        id_opercuentas=self.cmbFechasPago.itemData(int(self.cmbFechasPago.currentIndex()))
        cur = self.mem.con.cursor()      
        cur.execute("delete from opercuentas where id_opercuentas=%s", (id_opercuentas, ))#No merece crear objeto
        cur.execute("update opertarjetas set fechapago=null, pagado=false, id_opercuentas=null where id_opercuentas=%s", (id_opercuentas, ) )
        self.mem.con.commit()
        self.creditcardsoperations.load_from_db(mogrify(self.mem.con,"select * from opertarjetas where id_tarjetas=%s and pagado=false", [self.creditcards.selected.id, ]))
        self.load_tabOperCreditCards()
        cur.close()     
        self.tabOpertarjetasDiferidas.setCurrentIndex(0)     
        
    @QtCore.pyqtSlot(int) 
    def on_cmbFechasPago_currentIndexChanged(self, index):
        if index==-1:#Empty
            self.tblOpertarjetasHistoricas.setRowCount(0)
            return
        id_opercuentas=self.cmbFechasPago.itemData(index)
        setPaidCreditCardOperations=SetCreditCardOperations(self.mem)
        setPaidCreditCardOperations.load_from_db("select * from opertarjetas where id_opercuentas={};".format(id_opercuentas, ))
        setPaidCreditCardOperations.myqtablewidget(self.tblOpertarjetasHistoricas, "frmAccountsReport")

    def on_tabOpertarjetasDiferidas_currentChanged(self, index): 
        if  index==1: #PAGOS
            #Carga combo
            self.cmbFechasPago.clear()
            cur = self.mem.con.cursor()       
            cur.execute("select distinct(fechapago), id_opercuentas from opertarjetas where id_tarjetas=%s and fechapago is not null  order by fechapago;", (self.creditcards.selected.id, ))
            for row in cur:   
                ao=AccountOperation(self.mem).init__db_query(row['id_opercuentas'])
                self.cmbFechasPago.addItem(self.tr("{0} was made a paid of {1}").format(row['fechapago'],  self.mem.localcurrency.string(-ao.importe))    , ao.id)
            self.cmbFechasPago.setCurrentIndex(cur.rowcount-1)
            cur.close()     

    def on_txtAccount_textChanged(self):
        self.cmdDatos.setEnabled(True)
    def on_txtNumero_textChanged(self):
        self.cmdDatos.setEnabled(True)
    def on_cmbEB_currentIndexChanged(self, index):
        self.cmdDatos.setEnabled(True)
    def on_chkActiva_stateChanged(self,  state):
        self.cmdDatos.setEnabled(True)
