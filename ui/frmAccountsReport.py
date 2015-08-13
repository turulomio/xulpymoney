from PyQt5.QtCore import *
from PyQt5.QtGui import *
from libxulpymoney import *
from Ui_frmAccountsReport import *
from frmAccountOperationsAdd import *
from frmCreditCardsAdd import *
from frmInvestmentOperationsAdd import *

class frmAccountsReport(QDialog, Ui_frmAccountsReport):
    def __init__(self, mem, account,  parent=None):
        """
            selIdAccount=None Inserción de cuentas
            selIdAccount=X. Modificación de cuentas cuando click en cmd y resto de trabajos"""
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.showMaximized()
        self.cmdDatos.setEnabled(False)     
        
        self.mem=mem
        self.mem.data.load_inactives()
                
        self.account=account#Registro de account
        
        self.accountoperations=None#SetAccountOperations. Selected will be an AccountOperation
        self.creditcards=None#SetCreditCard. Selected will be a CreditCard
        self.creditcardoperations=SetCreditCardOperations(self.mem)#SetCreditCardOperations. Selected will be another SetCreditCardOperations
          
        self.tblOperaciones.settings("frmAccountsReport",  self.mem)
        self.tblCreditCards.settings("frmAccountsReport",  self.mem)
        self.tblCreditCardOpers.settings("frmAccountsReport",  self.mem)
        self.tblOpertarjetasHistoricas.settings("frmAccountsReport",  self.mem)
    
        self.calPago.setDate(QDate.currentDate())
        
        self.mem.currencies.qcombobox(self.cmbCurrency)
        self.mem.data.banks_active.qcombobox(self.cmbEB)
                    
        if self.account==None:
            self.lblTitulo.setText(self.tr("New account data"))
            self.tab.setCurrentIndex(0)
            self.tab.setTabEnabled(1, False)
            self.tab.setTabEnabled(2, False)
            self.chkActiva.setChecked(Qt.Checked)
            self.chkActiva.setEnabled(False)
            self.cmdDatos.setText(self.tr("Add a new account"))
        else:               
            self.tab.setCurrentIndex(0)
            self.lblTitulo.setText(self.account.name)
            self.txtAccount.setText(self.account.name)
            self.txtNumero.setText(str(self.account.numero))            
            self.cmbEB.setCurrentIndex(self.cmbEB.findData(self.account.eb.id))
            self.cmbEB.setEnabled(False)    
            self.cmbCurrency.setCurrentIndex(self.cmbCurrency.findData(self.account.currency.id))
            self.cmbCurrency.setEnabled(False)
            self.chkActiva.setChecked(b2c(self.account.active))
            self.cmdDatos.setText(self.tr("Update account data"))

            anoinicio=Assets(self.mem).primera_datetime_con_datos_usuario().year       
            self.wdgYM.initiate(anoinicio,  datetime.date.today().year, datetime.date.today().year, datetime.date.today().month)
            self.accountoperations_reload()
            self.wdgYM.changed.connect(self.on_wdgYM_changed)
            self.creditcards_reload()        
            

    def creditcards_reload(self): 
        if self.chkCreditCards.checkState()==Qt.Unchecked:
            self.creditcards=self.mem.data.creditcards_active.clone_of_account(self.account)
        else:
            self.mem.data.load_inactives()
            self.creditcards=self.mem.data.creditcards_inactive.clone_of_account(self.account)  
        self.creditcards.myqtablewidget(self.tblCreditCards, "frmAccountsReport")
        self.creditcards.selected=None
        self.tblCreditCards.clearSelection()

    def creditcardoperations_reload(self):     
        self.creditcardoperations.load_from_db(mogrify(self.mem.con,"select * from opertarjetas where id_tarjetas=%s and pagado=false", [self.creditcards.selected.id, ]))
        self.creditcardoperations.myqtablewidget(self.tblCreditCardOpers, "frmAccountsReport")
        self.creditcardoperations.selected=SetCreditCardOperations(self.mem)
        
        

    @QtCore.pyqtSlot() 
    def on_actionCreditCardAdd_triggered(self):
        w=frmCreditCardsAdd(self.mem,  self.account,  None, self)
        w.exec_()
        self.on_chkCreditCards_stateChanged(Qt.Unchecked)
        
    @QtCore.pyqtSlot() 
    def on_actionCreditCardEdit_triggered(self):
        w=frmCreditCardsAdd(self.mem, self.account,  self.creditcards.selected, self)
        w.exec_()
        self.tblCreditCards.clearSelection()
        self.creditcards_reload()
        
    @QtCore.pyqtSlot() 
    def on_actionCreditCardActivate_triggered(self):
        if self.account.qmessagebox_inactive() or self.account.eb.qmessagebox_inactive():
            return
            
        if self.creditcards.selected.active==False:#Ha pasado de inactiva a activa
            self.creditcards.selected.active=True
            self.mem.data.creditcards_inactive.remove(self.creditcards.selected)
            self.mem.data.creditcards_active.append(self.creditcards.selected)
        else:
            self.creditcards.selected.active=False
            self.mem.data.creditcards_inactive.append(self.creditcards.selected)
            self.mem.data.creditcards_active.remove(self.creditcards.selected)
        self.creditcards.selected.save()
        self.mem.con.commit()
        
        self.creditcards_reload()
                
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
        self.creditcards_reload()

    def on_chkCreditCards_stateChanged(self, state):      
       self.creditcards_reload() 

    def on_cmdDatos_released(self):
        id_entidadesbancarias=int(self.cmbEB.itemData(self.cmbEB.currentIndex()))
        cuenta=self.txtAccount.text()
        numerocuenta=self.txtNumero.text()
        active=c2b(self.chkActiva.checkState())
        currency=self.cmbCurrency.itemData(self.cmbCurrency.currentIndex())

        if self.account==None:
            cu=Account(self.mem).init__create(cuenta, self.mem.data.banks_active.find(id_entidadesbancarias), active, numerocuenta, self.mem.currencies.find(currency))
            cu.save()
            self.mem.data.accounts_active.append(cu) #Always to active
        else:
            self.account.eb=self.mem.data.banks_active.find(id_entidadesbancarias)
            self.account.name=cuenta
            self.account.numero=numerocuenta
            self.account.active=active
            self.account.currency=self.mem.currencies.find(currency)
            self.account.save()
            self.lblTitulo.setText(self.account.name)
        self.mem.con.commit()
        
        if self.account==None:
            self.done(0)
        self.cmdDatos.setEnabled(False)   

    @pyqtSlot()
    def on_wdgYM_changed(self):
        self.accountoperations_reload()
            
    def accountoperations_reload(self):    
        lastMonthBalance=self.account.balance(datetime.date(self.wdgYM.year, self.wdgYM.month, 1)-datetime.timedelta(days=1))     
          
        self.accountoperations=SetAccountOperations(self.mem)           
        self.accountoperations.load_from_db(mogrify(self.mem.con,"select * from opercuentas where id_cuentas=%s and date_part('year',datetime)=%s and date_part('month',datetime)=%s order by datetime, id_opercuentas", [self.account.id, self.wdgYM.year, self.wdgYM.month]))
        self.accountoperations.myqtablewidget_lastmonthbalance(self.tblOperaciones, "frmAccountsReport", self.account,  lastMonthBalance)   
        self.tblOperaciones.clearSelection()
        self.accountoperations.selected=None

    @QtCore.pyqtSlot() 
    def on_actionOperationAdd_triggered(self):
        w=frmAccountOperationsAdd(self.mem, self.mem.data.accounts_active,  self.account, None, None)
        w.OperAccountIBMed.connect(self.accountoperations_reload)
        w.exec_()
        self.accountoperations_reload()

    @QtCore.pyqtSlot() 
    def on_actionTransferDelete_triggered(self):

        oc_other=AccountOperation(self.mem).init__db_query(int(self.accountoperations.selected.comentario.split("|")[1]))
        
        if self.accountoperations.selected.concepto.id==4:#Tranfer origin
            account_origin=self.account
            account_destiny=self.mem.data.accounts_all().find(int(self.accountoperations.selected.comentario.split("|")[0]))
            oc_comision_id=int(self.accountoperations.selected.comentario.split("|")[2])
    
        if self.accountoperations.selected.concepto.id==5:#Tranfer destiny
            account_origin=self.mem.data.accounts_all().find(int(self.accountoperations.selected.comentario.split("|")[0]))
            account_destiny=self.account
            oc_comision_id=int(oc_other.comentario.split("|")[2])
            
        message=self.tr("Do you really want to delete transfer from {0} to {1}, with amount {2} and it's commision?").format(account_origin.name, account_destiny.name, self.accountoperations.selected.importe)
        reply = QMessageBox.question(self, 'Message', message, QMessageBox.Yes, QMessageBox.No)
            
        if reply == QMessageBox.Yes:
            if oc_comision_id!=0:
                oc_comision=AccountOperation(self.mem).init__db_query(oc_comision_id)
                oc_comision.borrar()
            self.accountoperations.selected.borrar()
            oc_other.borrar()
            self.mem.con.commit()
            self.accountoperations_reload()
        
    @QtCore.pyqtSlot() 
    def on_actionOperationEdit_triggered(self):
        w=frmAccountOperationsAdd(self.mem, self.mem.data.accounts_active,  self.account, self.accountoperations.selected, None)
        w.OperAccountIBMed.connect(self.accountoperations_reload)
        w.exec_()

    @QtCore.pyqtSlot() 
    def on_actionOperationDelete_triggered(self):
        self.accountoperations.selected.borrar() 
        self.mem.con.commit()         
        self.accountoperations_reload()

    @QtCore.pyqtSlot() 
    def on_actionCreditCardOperAdd_triggered(self):
        if self.creditcards.selected.pagodiferido==False:
            w=frmAccountOperationsAdd(self.mem, self.mem.data.accounts_active, self.account, None)
            w.OperAccountIBMed.connect(self.accountoperations_reload)
            w.lblTitulo.setText(self.creditcards.selected.name)
            w.txtComentario.setText(self.tr("CreditCard {0}. ").format(self.creditcards.selected.name))
            w.exec_()
        else:            
            w=frmAccountOperationsAdd(self.mem, self.mem.data.accounts_active,  self.account, None, self.creditcards.selected)
            w.OperCreditCardIBMed.connect(self.creditcardoperations_reload)
            w.lblTitulo.setText(self.tr("CreditCard {0}").format(self.creditcards.selected.name))
            w.exec_()
            
    @QtCore.pyqtSlot() 
    def on_actionCreditCardOperEdit_triggered(self):
        #Como es unico
        selOperCreditCard=self.creditcardoperations.selected.arr[0]
        w=frmAccountOperationsAdd(self.mem, self.mem.data.accounts_active,  self.account, None, self.creditcards.selected, selOperCreditCard)
        w.OperCreditCardIBMed.connect(self.creditcardoperations_reload)
        w.lblTitulo.setText(self.tr("CreditCard {0}").format(self.creditcards.selected.name))
        w.exec_()

    @QtCore.pyqtSlot() 
    def on_actionCreditCardOperDelete_triggered(self):
        for o in self.creditcardoperations.selected.arr:
            o.borrar()
            self.creditcardoperations.arr.remove(o)
        self.mem.con.commit()
        self.creditcardoperations_reload()

    @QtCore.pyqtSlot() 
    def on_actionInvestmentOperationDelete_triggered(self):
        investmentoperation=InvestmentOperation(self.mem).init__from_accountoperation(self.accountoperations.selected)
        investmentoperation.inversion.op.remove(investmentoperation)
        self.mem.con.commit()     
        self.accountoperations_reload()


    @QtCore.pyqtSlot() 
    def on_actionInvestmentOperationEdit_triggered(self):
        investmentoperation=InvestmentOperation(self.mem).init__from_accountoperation(self.accountoperations.selected)
        w=frmInvestmentOperationsAdd(self.mem, investmentoperation.inversion, investmentoperation, self)
        w.exec_()
        self.accountoperations_reload()

    def on_tblOperaciones_customContextMenuRequested(self,  pos):      
        if self.account.qmessagebox_inactive() or self.account.eb.qmessagebox_inactive():
            return

        if self.accountoperations.selected==None:
            self.actionOperationDelete.setEnabled(False)
            self.actionOperationEdit.setEnabled(False)   
            self.actionTransferDelete.setEnabled(False)
        else:
            if self.accountoperations.selected.es_editable()==False:
                self.actionOperationDelete.setEnabled(False)
                self.actionOperationEdit.setEnabled(False)   
                #Una transferencia bien formada no es editable solo con transfer delete.
                if (self.accountoperations.selected.concepto.id==4 and len(self.accountoperations.selected.comentario.split("|"))==3) or (self.accountoperations.selected.concepto.id==5 and len(self.accountoperations.selected.comentario.split("|"))==2):#Tranfer origin or Tranfer destine
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
        if self.accountoperations.selected!=None:
            if self.accountoperations.selected.concepto.id in [29, 35]:#Shares sale or purchase, allow edit or delete investment operation
                menu.addSeparator()
                menu.addAction(self.actionInvestmentOperationEdit)
                menu.addAction(self.actionInvestmentOperationDelete)
        menu.exec_(self.tblOperaciones.mapToGlobal(pos))

    def on_tblOperaciones_itemSelectionChanged(self):
        try:
            for i in self.tblOperaciones.selectedItems():#itera por cada item no row.
                if i.column()==1:#Better than 0, because initial balance is in 1
                    if i.row()==0:#Pressed balance
                        self.accountoperations.selected=None
                    else:
                        self.accountoperations.selected=self.accountoperations.arr[i.row()-1]
        except:
            self.accountoperations.selected=None
            
        print ("Seleccionado: " +  str(self.accountoperations.selected))
        

    def on_tblCreditCards_customContextMenuRequested(self,  pos):
        if self.account.qmessagebox_inactive():
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
            self.tblCreditCardOpers.setRowCount(0)
            return

        self.tabOpertarjetasDiferidas.setCurrentIndex(0)
        self.tabOpertarjetasDiferidas.setEnabled(self.creditcards.selected.pagodiferido)
        
        if self.creditcards.selected.pagodiferido==True:
            self.creditcardoperations_reload()
            self.grpPago.setEnabled(False)
        else:
            self.tblCreditCardOpers.setRowCount(0)
        print ("Seleccionado: " +  str(self.creditcards.selected.name))

    def on_tblCreditCardOpers_customContextMenuRequested(self,  pos):
        if self.account.qmessagebox_inactive() or self.account.eb.qmessagebox_inactive() or self.creditcards.selected.qmessagebox_inactive():
            return
        
        if self.creditcardoperations.selected.length()!=1: # 0 o más de 1
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
        self.creditcardoperations.selected=SetCreditCardOperations(self.mem)
        for i in self.tblCreditCardOpers.selectedItems():#itera por cada item no row.
            if i.column()==0:
                self.creditcardoperations.selected.append(self.creditcardoperations.arr[i.row()])  
        
        #Activa el grp Pago
        if self.creditcardoperations.selected.length()>0:
            self.grpPago.setEnabled(True)
        else:
            self.grpPago.setEnabled(False)

        #Calcula el balance
        self.lblPago.setText(self.mem.localcurrency.string(self.creditcardoperations.selected.balance()))
 
    def on_cmdPago_released(self):
        comentario="{0}|{1}".format(self.creditcards.selected.name, self.creditcardoperations.selected.length())
        fechapago=self.calPago.date().toPyDate()
        c=AccountOperation(self.mem).init__create(fechapago, self.mem.conceptos.find(40), self.mem.tiposoperaciones.find(7), self.creditcardoperations.selected.balance(), comentario, self.account)
        c.save()
        
        #Modifica el registro y lo pone como pagado y la datetime de pago y añade la opercuenta
        for o in self.creditcardoperations.selected.arr:
            o.fechapago=fechapago
            o.pagado=True
            o.opercuenta=c
            o.save()
        self.mem.con.commit()
        self.creditcardoperations_reload()         
        self.accountoperations_reload()  

    
    def on_cmdDevolverPago_released(self):
        id_opercuentas=self.cmbFechasPago.itemData(int(self.cmbFechasPago.currentIndex()))
        cur = self.mem.con.cursor()      
        cur.execute("delete from opercuentas where id_opercuentas=%s", (id_opercuentas, ))#No merece crear objeto
        cur.execute("update opertarjetas set fechapago=null, pagado=false, id_opercuentas=null where id_opercuentas=%s", (id_opercuentas, ) )
        self.mem.con.commit()
        cur.close()     
        self.creditcardoperations_reload()
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
