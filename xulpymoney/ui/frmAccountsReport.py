from PyQt5.QtCore import Qt, pyqtSlot,  QSize
from PyQt5.QtWidgets import QDialog, QMenu,  QMessageBox, QVBoxLayout
from datetime import date,  timedelta
from logging import debug
from xulpymoney.casts import b2c,  c2b
from xulpymoney.libmanagers import ManagerSelectionMode
from xulpymoney.objects.account import Account
from xulpymoney.libxulpymoney import Assets, InvestmentOperation, CreditCardOperationManager
from xulpymoney.libxulpymoneytypes import eComment
from xulpymoney.objects.accountoperation import AccountOperation, AccountOperationManager
from xulpymoney.objects.comment import Comment
from xulpymoney.ui.Ui_frmAccountsReport import Ui_frmAccountsReport
from xulpymoney.ui.frmAccountOperationsAdd import frmAccountOperationsAdd
from xulpymoney.ui.frmCreditCardsAdd import frmCreditCardsAdd
from xulpymoney.ui.frmInvestmentOperationsAdd import frmInvestmentOperationsAdd
from xulpymoney.ui.myqwidgets import qmessagebox
from xulpymoney.ui.wdgConceptsHistorical import wdgConceptsHistorical

## I have a lot of problems updating tables with selected objects in credict cards
## To solve I use only Ui events to select options
## myqtablewidget will not select  inside it's code. If needed I'll put it inside actions
##
##  account=None Inserción de cuentas
##  account=X. Modificación de cuentas cuando click en cmd y resto de trabajos

class frmAccountsReport(QDialog, Ui_frmAccountsReport):
    def __init__(self, mem, account,  parent=None):
        QDialog.__init__(self, parent)
        self.mem=mem
        self.account=account#Registro de account
        self.setupUi(self)
        self.showMaximized()
        self.cmdDatos.setEnabled(False)     
        self.wdgDtPago.show_microseconds(False)
        self.wdgDtPago.show_timezone(False)
        self.wdgDtPago.setTitle(self.tr("Select payment time"))
        
        
        self.accountoperations=None#AccountOperationManager. Selected will be an AccountOperation
        self.creditcardoperations=CreditCardOperationManager(self.mem)#CreditCardOperationManager. Selected will be another CreditCardOperationManager
          
        self.mqtwOperations.settings(self.mem.settings, "frmAccountsReport", "mqtwOperations")
        self.mqtwOperations.table.customContextMenuRequested.connect(self.on_mqtwOperations_customContextMenuRequested)
        self.mqtwOperations.table.itemSelectionChanged.connect(self.on_mqtwOperations_itemSelectionChanged)
        self.mqtwCreditCards.settings(self.mem.settings, "frmAccountsReport", "mqtwCreditCards")
        self.mqtwCreditCards.table.customContextMenuRequested.connect(self.on_mqtwCreditCards_customContextMenuRequested)
        self.mqtwCreditCards.table.itemSelectionChanged.connect(self.on_mqtwCreditCards_itemSelectionChanged)
        self.mqtwCreditCardOperations.settings(self.mem.settings, "frmAccountsReport", "mqtwCreditCardOperations")
        self.mqtwCreditCardOperations.table.customContextMenuRequested.connect(self.on_mqtwCreditCardOperations_customContextMenuRequested)
        self.mqtwCreditCardOperations.table.itemSelectionChanged.connect(self.on_mqtwCreditCardOperations_itemSelectionChanged)
        self.mqtwCreditCardOperationsHistorical.settings(self.mem.settings, "frmAccountsReport", "mqtwCreditCardOperationsHistorical")
    
        self.wdgDtPago.set(None, self.mem.localzone_name)
        
        self.mem.currencies.qcombobox(self.cmbCurrency)
        self.mem.data.banks_active().qcombobox(self.cmbEB)
                    
        if self.account==None:
            self.lblTitulo.setText(self.tr("New account data"))
            self.tab.setCurrentIndex(0)
            self.tab.setTabEnabled(1, False)
            self.tab.setTabEnabled(2, False)
            self.chkActiva.setChecked(Qt.Checked)
            self.chkActiva.setEnabled(False)
            self.mqtwOperations.setEnabled(False)
            self.cmdDatos.setText(self.tr("Add a new account"))
        else:
            self.account.needStatus(1)
            print(self.account, self.account.status, id(self.account))
            print(self.account.creditcards.length())
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
            self.wdgYM.initiate(anoinicio,  date.today().year, date.today().year, date.today().month)
            self.wdgYM.changed.connect(self.on_wdgYM_changed)
            self.on_wdgYM_changed()
            self.mqtwCreditCards_update()

    @pyqtSlot() 
    def on_actionCreditCardAdd_triggered(self):
        w=frmCreditCardsAdd(self.mem,  self.account,  None, self)
        w.exec_()

        self.mqtwCreditCards.clear()
        self.on_mqtwCreditCards_itemSelectionChanged()

    @pyqtSlot() 
    def on_actionCreditCardEdit_triggered(self):
        w=frmCreditCardsAdd(self.mem, self.account,  self.account.creditcards.selected, self)
        w.exec_()
        self.on_mqtwCreditCards_itemSelectionChanged()# It's already selected

    @pyqtSlot() 
    def on_actionCreditCardActivate_triggered(self):
        if self.account.qmessagebox_inactive() or self.account.eb.qmessagebox_inactive():
            return
        if self.account.creditcards.selected==None:
            print("Selected must be not null")
            return
        self.account.creditcards.selected.active=not self.account.creditcards.selected.active
        self.account.creditcards.selected.save()
        self.mem.con.commit()
        self.on_mqtwCreditCards_itemSelectionChanged()
                
    @pyqtSlot() 
    def on_actionCreditCardDelete_triggered(self):
        if self.account.creditcards.selected.is_deletable()==False:
            qmessagebox(self.tr("I can't delete the credit card, because it has dependent registers"), ":/xulpymoney/coins.png")
        else:
            self.account.creditcards.selected.delete()
            self.mem.con.commit()
            self.mqtwCreditCards.clear()#Must be before needStatus (Crashed)
            self.account.needStatus(1, downgrade_to=0)
            self.on_mqtwCreditCards_itemSelectionChanged()

    def on_chkCreditCards_stateChanged(self, state):
        self.mqtwCreditCards.clear()
        self.on_mqtwCreditCards_itemSelectionChanged()

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
        lastMonthBalance=self.account.balance(date(self.wdgYM.year, self.wdgYM.month, 1)-timedelta(days=1), type=2)     
        self.accountoperations=AccountOperationManager(self.mem)           
        self.accountoperations.load_from_db(self.mem.con.mogrify("select * from opercuentas where id_cuentas=%s and date_part('year',datetime)=%s and date_part('month',datetime)=%s order by datetime, id_opercuentas", [self.account.id, self.wdgYM.year, self.wdgYM.month]))
        self.accountoperations.myqtablewidget_lastmonthbalance(self.mqtwOperations,  self.account,  lastMonthBalance)   

    @pyqtSlot() 
    def on_actionOperationAdd_triggered(self):
        w=frmAccountOperationsAdd(self.mem, self.account)
        w.AccountOperationChanged.connect(self.on_wdgYM_changed)
        w.exec_()

    @pyqtSlot() 
    def on_actionTransferDelete_triggered(self):
        """
            Ya está validado si es Comment coded 10001,10002,10003
        """
        args=Comment(self.mem).getArgs(self.accountoperations.selected.first().comentario)#origin,destiny,commission
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
            self.on_wdgYM_changed()
        
    @pyqtSlot() 
    def on_actionOperationEdit_triggered(self):
        w=frmAccountOperationsAdd(self.mem, self.account, self.accountoperations.selected.first())
        w.AccountOperationChanged.connect(self.on_wdgYM_changed)
        w.exec_()

    @pyqtSlot() 
    def on_actionOperationDelete_triggered(self):
        self.accountoperations.selected.first().borrar() 
        self.mem.con.commit()         
        self.on_wdgYM_changed()

    @pyqtSlot() 
    def on_actionCreditCardOperAdd_triggered(self):
        w=frmAccountOperationsAdd(self.mem, self.account, None, self.account.creditcards.selected)
        w.CreditCardOperationChanged.connect(self.mqtwCreditCardsOperations_update)
        w.AccountOperationChanged.connect(self.on_wdgYM_changed)#Tarjetas en debito
        w.exec_()
            
    @pyqtSlot() 
    def on_actionCreditCardOperEdit_triggered(self):
        #Como es unico
        selOperCreditCard=self.creditcardoperations.selected.arr[0]
        w=frmAccountOperationsAdd(self.mem,  self.account, None, self.account.creditcards.selected, selOperCreditCard)
        w.CreditCardOperationChanged.connect(self.mqtwCreditCardsOperations_update)
        w.exec_()

    @pyqtSlot() 
    def on_actionCreditCardOperDelete_triggered(self):
        for o in self.creditcardoperations.selected.arr:
            o.borrar()
            self.creditcardoperations.arr.remove(o)
        self.mem.con.commit()
        self.mqtwCreditCardsOperations_update()
        
    @pyqtSlot() 
    def on_actionCreditCardOperRefund_triggered(self):
        w=frmAccountOperationsAdd(self.mem, opertarjeta=self.creditcardoperations.selected.arr[0], refund=True)
        w.CreditCardOperationChanged.connect(self.mqtwCreditCardsOperations_update)
        w.exec_()
            
    @pyqtSlot() 
    def on_actionInvestmentOperationDelete_triggered(self):
        investmentoperation=InvestmentOperation(self.mem).init__from_accountoperation(self.accountoperations.selected)
        investmentoperation.investment.op.remove(investmentoperation)
        self.mem.con.commit()     
        print("Borrando investment ooperation",  investmentoperation)
        self.on_wdgYM_changed()


    @pyqtSlot() 
    def on_actionInvestmentOperationEdit_triggered(self):
        investmentoperation=InvestmentOperation(self.mem).init__from_accountoperation(self.accountoperations.selected.first())
        w=frmInvestmentOperationsAdd(self.mem, investmentoperation.investment, investmentoperation, self)
        w.exec_()
        debug("Edit investmentoperation {}".format(self.accountoperations.selected.first()))
        self.on_wdgYM_changed()

    @pyqtSlot()
    def on_actionConceptReport_triggered(self):
        if self.tab.currentIndex()==0:
            concepto=self.accountoperations.selected.first().concepto
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
    def on_mqtwOperations_customContextMenuRequested(self,  pos):      
        if self.account.qmessagebox_inactive() or self.account.eb.qmessagebox_inactive():
            return

        if self.accountoperations.selected.length()==0:
            self.actionOperationDelete.setEnabled(False)
            self.actionOperationEdit.setEnabled(False)   
            self.actionTransferDelete.setEnabled(False)
            self.actionConceptReport.setEnabled(False)
        else:
            if self.accountoperations.selected.first().es_editable()==False:
                self.actionOperationDelete.setEnabled(False)
                self.actionOperationEdit.setEnabled(False)   
                #Una transferencia bien formada no es editable solo con transfer delete.
                if Comment(self.mem).getCode(self.accountoperations.selected.first().comentario) in (eComment.AccountTransferOrigin, eComment.AccountTransferDestiny, eComment.AccountTransferOriginCommission):
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
            if self.accountoperations.selected.first().concepto.id in [29, 35]:#Shares sale or purchase, allow edit or delete investment operation
                menu.addSeparator()
                menu.addAction(self.actionInvestmentOperationEdit)
                menu.addAction(self.actionInvestmentOperationDelete)
        menu.exec_(self.mqtwOperations.table.mapToGlobal(pos))

    def on_mqtwOperations_itemSelectionChanged(self):
        self.accountoperations.selected.clean()
        for i in self.mqtwOperations.table.selectedItems():#itera por cada item no row.
            if i.column()==1 and i.row()!=0:#Initial month
                id=int(self.mqtwOperations.table.item(i.row(), 5).text())#Id it's hidden in the fifth column
                self.accountoperations.selected.append(self.accountoperations.find_by_id(id)) #AccountOperationManager is a DictManager
        print ("Seleccionado: " +  str(self.accountoperations.selected.arr))

    def on_mqtwCreditCards_customContextMenuRequested(self,  pos):
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
        
        if self.account.creditcards.selected==None:
            self.actionCreditCardOperAdd.setEnabled(False)
            self.actionCreditCardDelete.setEnabled(False)
            self.actionCreditCardEdit.setEnabled(False)
            self.actionCreditCardActivate.setEnabled(False)
        else:
            self.actionCreditCardOperAdd.setEnabled(True)
            self.actionCreditCardDelete.setEnabled(True)
            self.actionCreditCardEdit.setEnabled(True)
            self.actionCreditCardActivate.setEnabled(True)
            if self.account.creditcards.selected.active==True:
                self.actionCreditCardActivate.setChecked(True)
            else:
                self.actionCreditCardActivate.setChecked(False)
        menu.exec_(self.mqtwCreditCards.table.mapToGlobal(pos))


    def mqtwCreditCards_update(self):
        if self.account.creditcards.selected==None:#No selected
#            self.mqtwCreditCards.table.clearSelection()
            self.tabOpertarjetasDiferidas.setEnabled(False)
            self.account.creditcards.myqtablewidget(self.mqtwCreditCards, not self.chkCreditCards.isChecked())
            self.mqtwCreditCardOperations.table.setRowCount(0)
        else:
            print(self.account.creditcards.selected, "AQUI")
            self.tabOpertarjetasDiferidas.setEnabled(self.account.creditcards.selected.pagodiferido)
            self.account.creditcards.myqtablewidget(self.mqtwCreditCards, not self.chkCreditCards.isChecked())
            self.mqtwCreditCardsOperations_update()

    def on_mqtwCreditCards_itemSelectionChanged(self):
        print("on_mqtwCreditCards_itemSelectionChanged")
        self.account.creditcards.setSelectionMode(ManagerSelectionMode.Object)
        self.account.creditcards.cleanSelection()
        for i in self.mqtwCreditCards.table.selectedItems():#itera por cada item no row.
            if i.column()==0:
                self.account.creditcards.setSelected(self.account.creditcards.arr[i.row()])
        debug("CreditCard selection: {}".format(self.account.creditcards.selected))
        self.mqtwCreditCardsOperations_update()

            
    def on_mqtwCreditCardOperations_customContextMenuRequested(self,  pos):
        if self.account.qmessagebox_inactive() or self.account.eb.qmessagebox_inactive() or self.account.creditcards.selected.qmessagebox_inactive():
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
                if self.account.creditcards.selected.pagodiferido==True and self.creditcardoperations.selected.arr[0].importe<0:#Only difered purchases
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
        menu.exec_(self.mqtwCreditCardOperations.table.mapToGlobal(pos))


    def on_mqtwCreditCardOperations_itemSelectionChanged(self):
        self.creditcardoperations.setSelectionMode(ManagerSelectionMode.Manager)
        self.creditcardoperations.selected=CreditCardOperationManager(self.mem)
        for i in self.mqtwCreditCardOperations.table.selectedItems():#itera por cada item no row.
            if i.column()==0:
                self.creditcardoperations.selected.append(self.creditcardoperations.arr[i.row()])  
        
        #Activa el grp Pago
        if self.creditcardoperations.selected.length()>0:
            self.grpPago.setEnabled(True)
        else:
            self.grpPago.setEnabled(False)

        #Calcula el balance
        self.lblPago.setText(self.mem.localcurrency.string(self.creditcardoperations.selected.balance()))

    def mqtwCreditCardsOperations_update(self):
        self.tabOpertarjetasDiferidas.setCurrentIndex(0)
        self.mqtwCreditCardOperations.table.setRowCount(0)

        self.tabOpertarjetasDiferidas.setEnabled(self.account.creditcards.selected.pagodiferido)
        if self.account.creditcards.selected.pagodiferido==True:#Solo se muestran operaciones si es diferido
            self.grpPago.setEnabled(True)
            self.creditcardoperations.load_from_db(self.mem.con.mogrify("select * from opertarjetas where id_tarjetas=%s and pagado=false", [self.account.creditcards.selected.id, ]))
            self.creditcardoperations.myqtablewidget(self.mqtwCreditCardOperations)
        else:
            self.grpPago.setEnabled(False)

    def on_cmdPago_released(self):
        c=AccountOperation(self.mem, self.wdgDtPago.datetime(), self.mem.conceptos.find_by_id(40), self.mem.tiposoperaciones.find_by_id(7), self.creditcardoperations.selected.balance(), "Transaction in progress", self.account, None)
        c.save()
        
        c.comentario=Comment(self.mem).encode(eComment.CreditCardBilling, self.account.creditcards.selected, c)
        c.save()
        
        #Modifica el registro y lo pone como pagado y la datetime de pago y añade la opercuenta
        for o in self.creditcardoperations.selected.arr:
            o.fechapago=self.wdgDtPago.datetime()
            o.pagado=True
            o.opercuenta=c
            o.save()
        self.mem.con.commit()
        self.on_wdgYM_changed()
        self.on_mqtwCreditCards_itemSelectionChanged()
    
    def on_cmdDevolverPago_released(self):
        id_opercuentas=self.cmbFechasPago.itemData(int(self.cmbFechasPago.currentIndex()))
        cur = self.mem.con.cursor()      
        cur.execute("delete from opercuentas where id_opercuentas=%s", (id_opercuentas, ))#No merece crear objeto
        cur.execute("update opertarjetas set fechapago=null, pagado=false, id_opercuentas=null where id_opercuentas=%s", (id_opercuentas, ) )
        self.mem.con.commit()
        cur.close()     
        self.on_wdgYM_changed()
        self.on_mqtwCreditCards_itemSelectionChanged()
        self.tabOpertarjetasDiferidas.setCurrentIndex(0)     
        
    @pyqtSlot(int) 
    def on_cmbFechasPago_currentIndexChanged(self, index):
        if index==-1:#Empty
            self.mqtwCreditCardOperationsHistorical.table.setRowCount(0)
            return
        id_opercuentas=self.cmbFechasPago.itemData(index)
        setPaidCreditCardOperations=CreditCardOperationManager(self.mem)
        setPaidCreditCardOperations.load_from_db("select * from opertarjetas where id_opercuentas={};".format(id_opercuentas, ))
        setPaidCreditCardOperations.myqtablewidget(self.mqtwCreditCardOperationsHistorical)

    def on_tabOpertarjetasDiferidas_currentChanged(self, index): 
        if  index==1: #PAGOS
            #Carga combo
            self.cmbFechasPago.clear()
            cur = self.mem.con.cursor()       
            cur.execute("select distinct(fechapago), id_opercuentas from opertarjetas where id_tarjetas=%s and fechapago is not null  order by fechapago;", (self.account.creditcards.selected.id, ))
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
