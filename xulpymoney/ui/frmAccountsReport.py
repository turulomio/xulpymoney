import datetime
import logging
from PyQt5.QtCore import Qt, pyqtSlot,  QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QMenu,  QMessageBox, QVBoxLayout
from xulpymoney.libxulpymoney import Account, AccountOperation, Assets, Comment, InvestmentOperation, AccountOperationManager,  CreditCardOperationManager,  CreditCardOperation
from xulpymoney.libxulpymoneyfunctions import b2c,  c2b
from xulpymoney.ui.Ui_frmAccountsReport import Ui_frmAccountsReport
from xulpymoney.ui.frmAccountOperationsAdd import frmAccountOperationsAdd
from xulpymoney.ui.frmCreditCardsAdd import frmCreditCardsAdd
from xulpymoney.ui.frmInvestmentOperationsAdd import frmInvestmentOperationsAdd
from xulpymoney.ui.wdgConceptsHistorical import wdgConceptsHistorical

class frmAccountsReport(QDialog, Ui_frmAccountsReport):
    def __init__(self, mem, account,  parent=None):
        """
            selIdAccount=None Inserción de cuentas
            selIdAccount=X. Modificación de cuentas cuando click en cmd y resto de trabajos"""
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.showMaximized()
        self.cmdDatos.setEnabled(False)     
        self.wdgDtPago.show_microseconds(False)
        self.wdgDtPago.show_timezone(False)
        self.wdgDtPago.setTitle(self.tr("Select payment time"))
        
        self.mem=mem
         
                
        self.account=account#Registro de account
        
        self.accountoperations=None#AccountOperationManager. Selected will be an AccountOperation
        self.creditcards=None#SetCreditCard. Selected will be a CreditCard
        self.creditcardoperations=CreditCardOperationManager(self.mem)#CreditCardOperationManager. Selected will be another CreditCardOperationManager
          
        self.tblOperaciones.settings(self.mem, "frmAccountsReport")
        self.tblCreditCards.settings(self.mem, "frmAccountsReport")
        self.tblCreditCardOpers.settings(self.mem, "frmAccountsReport")
        self.tblOpertarjetasHistoricas.settings(self.mem, "frmAccountsReport")
    
        self.wdgDtPago.set(self.mem, None, self.mem.localzone)
        
        self.mem.currencies.qcombobox(self.cmbCurrency)
        self.mem.data.banks_active().qcombobox(self.cmbEB)
                    
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

            anoinicio=Assets(self.mem).first_datetime_with_user_data().year       
            self.wdgYM.initiate(anoinicio,  datetime.date.today().year, datetime.date.today().year, datetime.date.today().month)
            self.on_AccountOperationChanged(None)
            self.on_CreditCardChanged(None)
            self.wdgYM.changed.connect(self.on_wdgYM_changed)

    @pyqtSlot() 
    def on_actionCreditCardAdd_triggered(self):
        w=frmCreditCardsAdd(self.mem,  self.account,  None, self)
        w.exec_()
        self.on_CreditCardChanged(w.creditcard)

    @pyqtSlot() 
    def on_actionCreditCardEdit_triggered(self):
        w=frmCreditCardsAdd(self.mem, self.account,  self.creditcards.selected, self)
        w.exec_()
        self.on_CreditCardChanged(self.creditcards.selected)

    @pyqtSlot() 
    def on_actionCreditCardActivate_triggered(self):
        if self.account.qmessagebox_inactive() or self.account.eb.qmessagebox_inactive():
            return

        self.creditcards.selected.active=not self.creditcards.selected.active
        self.creditcards.selected.save()
        self.mem.con.commit()
        self.on_CreditCardChanged(None)
                
    @pyqtSlot() 
    def on_actionCreditCardDelete_triggered(self):
        if self.creditcards.selected.is_deletable()==False:
            m=QMessageBox()
            m.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
            m.setIcon(QMessageBox.Information)
            m.setText(self.tr("I can't delete the credit card, because it has dependent registers"))
            m.exec_()
        else:
            print("BORRANDO", self.creditcards.selected)
            self.mem.data.creditcards.delete(self.creditcards.selected)#self.creditcards is only a clone and is reloaded later
            self.mem.con.commit()
            self.on_CreditCardOperationChanged(None)

    def on_chkCreditCards_stateChanged(self, state):      
       self.on_CreditCardChanged(None) 

    def on_cmdDatos_released(self):
        id_entidadesbancarias=int(self.cmbEB.itemData(self.cmbEB.currentIndex()))
        cuenta=self.txtAccount.text()
        numerocuenta=self.txtNumero.text()
        active=c2b(self.chkActiva.checkState())
        currency=self.cmbCurrency.itemData(self.cmbCurrency.currentIndex())

        if self.account==None:
            cu=Account(self.mem, cuenta, self.mem.data.banks_active().find_by_id(id_entidadesbancarias), active, numerocuenta, self.mem.currencies.find_by_id(currency), None)
            cu.save()
            self.mem.data.accounts.append(cu) #Always to active
        else:
            self.account.eb=self.mem.data.banks_active().find_by_id(id_entidadesbancarias)
            self.account.name=cuenta
            self.account.numero=numerocuenta
            self.account.active=active
            self.account.currency=self.mem.currencies.find_by_id(currency)
            self.account.save()
            self.lblTitulo.setText(self.account.name)
        self.mem.con.commit()
        
        if self.account==None:
            self.done(0)
        self.cmdDatos.setEnabled(False)   

    @pyqtSlot()
    def on_wdgYM_changed(self):
        self.on_AccountOperationChanged(None)
        
    def on_AccountOperationChanged(self, o):
        """
            o=None, significa que hay que actualizarlo las opercuentas sin seleccionar
            o=AccountOperation, significa que hay que actualizar opercuentas y seleccionarla
        """
        lastMonthBalance=self.account.balance(datetime.date(self.wdgYM.year, self.wdgYM.month, 1)-datetime.timedelta(days=1), type=2)     
        self.accountoperations=AccountOperationManager(self.mem)           
        self.accountoperations.load_from_db(self.mem.con.mogrify("select * from opercuentas where id_cuentas=%s and date_part('year',datetime)=%s and date_part('month',datetime)=%s order by datetime, id_opercuentas", [self.account.id, self.wdgYM.year, self.wdgYM.month]))
        if o!=None:
            self.accountoperations.setSelected([o, ])
        self.accountoperations.myqtablewidget_lastmonthbalance(self.tblOperaciones,  self.account,  lastMonthBalance)   

    def on_CreditCardChanged(self, o):
        """
            o=None, significa que hay que actualizar las tarjetas sin seleccionar
            o=CreditCard, significa que hay que actualizar las tarjetas seleccionandola 
        """           
        if self.chkCreditCards.checkState()==Qt.Unchecked:
            self.creditcards=self.mem.data.creditcards_active().clone_of_account(self.account)
        else:
            self.creditcards=self.mem.data.creditcards_inactive().clone_of_account(self.account)  

        self.tabOpertarjetasDiferidas.setCurrentIndex(0)

        if o==None:#No selected
            self.creditcards.myqtablewidget(self.tblCreditCards)
            self.tblCreditCardOpers.setRowCount(0)
        else:
            self.creditcards.setSelected(o)
            self.tabOpertarjetasDiferidas.setEnabled(self.creditcards.selected.pagodiferido)
            self.creditcards.myqtablewidget(self.tblCreditCards)
            if self.creditcards.selected.pagodiferido==True:#Solo se muestran operaciones si es diferido
                self.creditcardoperations.load_from_db(self.mem.con.mogrify("select * from opertarjetas where id_tarjetas=%s and pagado=false", [self.creditcards.selected.id, ]))
                self.creditcardoperations.myqtablewidget(self.tblCreditCardOpers)
                self.grpPago.setEnabled(False)
            else:
                self.tblCreditCardOpers.setRowCount(0)

    def on_CreditCardOperationChanged(self, o):
        """ ES DISTINTA A CREDIRCARDCHANGED NO JUNTAR
            o=None, significa que hay que actualizar las tarjetas sin seleccionar
            o=CreditCardOperation, significa que hay que actualizar creditcardoperation, usando el id de la tarjeta seleccionada
        """          
        if self.chkCreditCards.checkState()==Qt.Unchecked:
            self.creditcards=self.mem.data.creditcards_active().clone_of_account(self.account)
        else:
            self.creditcards=self.mem.data.creditcards_inactive().clone_of_account(self.account)  
        self.creditcards.selected=o.tarjeta
        self.tabOpertarjetasDiferidas.setCurrentIndex(0)

        if o==None:#No selected
            self.creditcards.myqtablewidget(self.tblCreditCards)
            self.tblCreditCardOpers.setRowCount(0)
            self.grpPago.setEnabled(False)
        else:
            self.tabOpertarjetasDiferidas.setEnabled(self.creditcards.selected.pagodiferido)
            self.creditcards.myqtablewidget(self.tblCreditCards)
            if self.creditcards.selected.pagodiferido==True:#Solo se muestran operaciones si es diferido
                self.grpPago.setEnabled(True)
                self.creditcardoperations.load_from_db(self.mem.con.mogrify("select * from opertarjetas where id_tarjetas=%s and pagado=false", [self.creditcards.selected.id, ]))
                if o.__class__==CreditCardOperation:#It's an array
                    sel=CreditCardOperationManager(self.mem)
                    sel.append(o)
                    self.creditcardoperations.selected=sel
                self.creditcardoperations.myqtablewidget(self.tblCreditCardOpers)
            else:
                self.grpPago.setEnabled(False)
                self.tblCreditCardOpers.setRowCount(0)

    @pyqtSlot() 
    def on_actionOperationAdd_triggered(self):
        w=frmAccountOperationsAdd(self.mem, self.account)
        w.AccountOperationChanged.connect(self.on_AccountOperationChanged)
        w.exec_()

    @pyqtSlot() 
    def on_actionTransferDelete_triggered(self):
        """
            Ya está validado si es Comment coded 10001,10002,10003
        """
        args=Comment(self.mem).getArgs(self.accountoperations.selected.only().comentario)#origin,destiny,comission
        aoo=AccountOperation(self.mem, args[0])
        aod=AccountOperation(self.mem, args[1])

        message=self.tr("Do you really want to delete transfer from {0} to {1}, with amount {2} and it's commision?").format(aoo.account.name, aod.account.name, aoo.importe)
        reply = QMessageBox.question(self, 'Message', message, QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            if args[2]!=-1:
                aoc=AccountOperation(self.mem, args[2])
                aoc.borrar()
            aoo.borrar()
            aod.borrar()
            self.mem.con.commit()
            self.on_AccountOperationChanged(None)
        
    @pyqtSlot() 
    def on_actionOperationEdit_triggered(self):
        w=frmAccountOperationsAdd(self.mem, self.account, self.accountoperations.selected.only())
        w.AccountOperationChanged.connect(self.on_AccountOperationChanged)
        w.exec_()

    @pyqtSlot() 
    def on_actionOperationDelete_triggered(self):
        self.accountoperations.selected.only().borrar() 
        self.mem.con.commit()         
        self.on_AccountOperationChanged(None)

    @pyqtSlot() 
    def on_actionCreditCardOperAdd_triggered(self):
        w=frmAccountOperationsAdd(self.mem, self.account, None, self.creditcards.selected)
        w.CreditCardOperationChanged.connect(self.on_CreditCardOperationChanged)
        w.AccountOperationChanged.connect(self.on_AccountOperationChanged)#Tarjetas en debito
        w.exec_()
            
    @pyqtSlot() 
    def on_actionCreditCardOperEdit_triggered(self):
        #Como es unico
        selOperCreditCard=self.creditcardoperations.selected.arr[0]
        w=frmAccountOperationsAdd(self.mem,  self.account, None, self.creditcards.selected, selOperCreditCard)
        w.CreditCardOperationChanged.connect(self.on_CreditCardOperationChanged)
        w.exec_()

    @pyqtSlot() 
    def on_actionCreditCardOperDelete_triggered(self):
        for o in self.creditcardoperations.selected.arr:
            o.borrar()
            self.creditcardoperations.arr.remove(o)
        self.mem.con.commit()
        self.on_CreditCardChanged(self.creditcards.selected)
        
    @pyqtSlot() 
    def on_actionCreditCardOperRefund_triggered(self):
        w=frmAccountOperationsAdd(self.mem, opertarjeta=self.creditcardoperations.selected.arr[0], refund=True)
        w.CreditCardOperationChanged.connect(self.on_CreditCardOperationChanged)
        w.exec_()
            
    @pyqtSlot() 
    def on_actionInvestmentOperationDelete_triggered(self):
        investmentoperation=InvestmentOperation(self.mem).init__from_accountoperation(self.accountoperations.selected)
        investmentoperation.investment.op.remove(investmentoperation)
        self.mem.con.commit()     
        print("Borrando investment ooperation",  investmentoperation)
        self.on_AccountOperationChanged(None)


    @pyqtSlot() 
    def on_actionInvestmentOperationEdit_triggered(self):
        investmentoperation=InvestmentOperation(self.mem).init__from_accountoperation(self.accountoperations.selected.only())
        w=frmInvestmentOperationsAdd(self.mem, investmentoperation.investment, investmentoperation, self)
        w.exec_()
        logging.debug("Edit investmentoperation {}".format(self.accountoperations.selected.only()))
        self.on_AccountOperationChanged(self.accountoperations.selected.only())

    @pyqtSlot()
    def on_actionConceptReport_triggered(self):
        if self.tab.currentIndex()==0:
            concepto=self.accountoperations.selected.only().concepto
        else:
            concepto=self.creditcardoperations.selected.first().concepto

        d=QDialog(self)     
        d.resize(self.mem.settings.value("frmAccountsReport/qdialog_conceptreport", QSize(800, 600)))
        d.setWindowTitle(self.tr("Historical report of {}").format(concepto.name))
        w = wdgConceptsHistorical(self.mem, concepto, d)
        lay = QVBoxLayout(d)
        lay.addWidget(w)
        d.exec_()
        self.mem.settings.setValue("frmAccountsReport/qdialog_conceptreport", d.size())


    ## Selection can be only one row, due to table definitions
    def on_tblOperaciones_customContextMenuRequested(self,  pos):      
        if self.account.qmessagebox_inactive() or self.account.eb.qmessagebox_inactive():
            return

        if self.accountoperations.selected.length()==0:
            self.actionOperationDelete.setEnabled(False)
            self.actionOperationEdit.setEnabled(False)   
            self.actionTransferDelete.setEnabled(False)
            self.actionConceptReport.setEnabled(False)
        else:
            if self.accountoperations.selected.only().es_editable()==False:
                self.actionOperationDelete.setEnabled(False)
                self.actionOperationEdit.setEnabled(False)   
                #Una transferencia bien formada no es editable solo con transfer delete.
                if Comment(self.mem).getCode(self.accountoperations.selected.only().comentario) in (10001, 10002, 10003):#Account transfers
                    self.actionTransferDelete.setEnabled(True)
                else:
                    self.actionTransferDelete.setEnabled(False)
            else: #es editable
                self.actionOperationDelete.setEnabled(True)    
                self.actionOperationEdit.setEnabled(True)      
                self.actionTransferDelete.setEnabled(False)
            self.actionConceptReport.setEnabled(True)
            
        menu=QMenu()
        menu.addAction(self.actionOperationAdd)
        menu.addAction(self.actionOperationEdit)
        menu.addAction(self.actionOperationDelete)
        menu.addSeparator()
        menu.addAction(self.actionConceptReport)
        menu.addSeparator()
        menu.addAction(self.actionTransferDelete)

        if self.accountoperations.selected.length()!=0:
            if self.accountoperations.selected.only().concepto.id in [29, 35]:#Shares sale or purchase, allow edit or delete investment operation
                menu.addSeparator()
                menu.addAction(self.actionInvestmentOperationEdit)
                menu.addAction(self.actionInvestmentOperationDelete)
        menu.exec_(self.tblOperaciones.mapToGlobal(pos))

    def on_tblOperaciones_itemSelectionChanged(self):
        self.accountoperations.selected.clean()
        for i in self.tblOperaciones.selectedItems():#itera por cada item no row.
            if i.column()==1 and i.row()!=0:#Initial month
                id=int(self.tblOperaciones.item(i.row(), 5).text())#Id it's hidden in the fifth column
                self.accountoperations.selected.append(self.accountoperations.find_by_id(id)) #AccountOperationManager is a DictManager
        print ("Seleccionado: " +  str(self.accountoperations.selected.dic))
        

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
        self.creditcards.selected=None
        for i in self.tblCreditCards.selectedItems():#itera por cada item no row.
            if i.column()==0:
                self.creditcards.setSelected(self.creditcards.arr[i.row()])
        
        self.on_CreditCardChanged(self.creditcards.selected)

    def on_tblCreditCardOpers_customContextMenuRequested(self,  pos):
        if self.account.qmessagebox_inactive() or self.account.eb.qmessagebox_inactive() or self.creditcards.selected.qmessagebox_inactive():
            return
        if self.creditcardoperations.selected!=None:
            if self.creditcardoperations.selected.length()!=1: # 0 o más de 1
                self.actionCreditCardOperDelete.setEnabled(False)
                self.actionCreditCardOperEdit.setEnabled(False)
                self.actionCreditCardOperRefund.setEnabled(False)
                self.actionConceptReport.setEnabled(False)
            else:
                self.actionCreditCardOperDelete.setEnabled(True)
                self.actionCreditCardOperEdit.setEnabled(True)
                if self.creditcards.selected.pagodiferido==True and self.creditcardoperations.selected.arr[0].importe<0:#Only difered purchases
                    self.actionCreditCardOperRefund.setEnabled(True)
                else:
                    self.actionCreditCardOperRefund.setEnabled(False)
                self.actionConceptReport.setEnabled(True)
            
        menu=QMenu()
        menu.addAction(self.actionCreditCardOperAdd)
        menu.addAction(self.actionCreditCardOperEdit)
        menu.addAction(self.actionCreditCardOperDelete)
        menu.addSeparator()
        menu.addAction(self.actionConceptReport)
        menu.addSeparator()
        menu.addAction(self.actionCreditCardOperRefund)
        menu.exec_(self.tblCreditCardOpers.mapToGlobal(pos))


    def on_tblCreditCardOpers_itemSelectionChanged(self):
        self.creditcardoperations.selected=CreditCardOperationManager(self.mem)
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
#        comentario="{0}|{1}".format(self.creditcards.selected.name, self.creditcardoperations.selected.length())v
        c=AccountOperation(self.mem, self.wdgDtPago.datetime(), self.mem.conceptos.find_by_id(40), self.mem.tiposoperaciones.find_by_id(7), self.creditcardoperations.selected.balance(), "Transaction in progress", self.account, None)
        c.save()
        
        c.comentario=Comment(self.mem).setEncoded10005(self.creditcards.selected, c)
        c.save()
        
        #Modifica el registro y lo pone como pagado y la datetime de pago y añade la opercuenta
        for o in self.creditcardoperations.selected.arr:
            o.fechapago=self.wdgDtPago.datetime()
            o.pagado=True
            o.opercuenta=c
            o.save()
        self.mem.con.commit()
        self.on_AccountOperationChanged(None)
        self.on_CreditCardChanged(self.creditcards.selected)

    
    def on_cmdDevolverPago_released(self):
        id_opercuentas=self.cmbFechasPago.itemData(int(self.cmbFechasPago.currentIndex()))
        cur = self.mem.con.cursor()      
        cur.execute("delete from opercuentas where id_opercuentas=%s", (id_opercuentas, ))#No merece crear objeto
        cur.execute("update opertarjetas set fechapago=null, pagado=false, id_opercuentas=null where id_opercuentas=%s", (id_opercuentas, ) )
        self.mem.con.commit()
        cur.close()     
        self.on_AccountOperationChanged(None)
        self.on_CreditCardChanged(self.creditcards.selected)
        self.tabOpertarjetasDiferidas.setCurrentIndex(0)     
        
    @pyqtSlot(int) 
    def on_cmbFechasPago_currentIndexChanged(self, index):
        if index==-1:#Empty
            self.tblOpertarjetasHistoricas.setRowCount(0)
            return
        id_opercuentas=self.cmbFechasPago.itemData(index)
        setPaidCreditCardOperations=CreditCardOperationManager(self.mem)
        setPaidCreditCardOperations.load_from_db("select * from opertarjetas where id_opercuentas={};".format(id_opercuentas, ))
        setPaidCreditCardOperations.myqtablewidget(self.tblOpertarjetasHistoricas)

    def on_tabOpertarjetasDiferidas_currentChanged(self, index): 
        if  index==1: #PAGOS
            #Carga combo
            self.cmbFechasPago.clear()
            cur = self.mem.con.cursor()       
            cur.execute("select distinct(fechapago), id_opercuentas from opertarjetas where id_tarjetas=%s and fechapago is not null  order by fechapago;", (self.creditcards.selected.id, ))
            for row in cur:   
                ao=AccountOperation(self.mem, row['id_opercuentas'])
                self.cmbFechasPago.addItem(self.tr("{0} was made a paid of {1}").format(str(row['fechapago'])[0:19],  self.mem.localcurrency.string(-ao.importe))    , ao.id)
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
