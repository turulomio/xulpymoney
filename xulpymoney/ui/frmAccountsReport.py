from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog, QMenu,  QMessageBox, QAbstractItemView
from datetime import date,  timedelta, datetime
from logging import debug
from xulpymoney.objects.account import Account
from xulpymoney.libxulpymoneytypes import eComment, eConcept
from xulpymoney.objects.accountoperation import AccountOperation, AccountOperationManagerHomogeneus
from xulpymoney.objects.assets import Assets
from xulpymoney.objects.comment import Comment
from xulpymoney.objects.creditcardoperation import CreditCardOperationManager
from xulpymoney.objects.currency import currencies_qcombobox
from xulpymoney.objects.investmentoperation import InvestmentOperation_from_accountoperation
from xulpymoney.ui.Ui_frmAccountsReport import Ui_frmAccountsReport
from xulpymoney.ui.frmAccountOperationsAdd import frmAccountOperationsAdd
from xulpymoney.ui.frmCreditCardsAdd import frmCreditCardsAdd
from xulpymoney.ui.frmInvestmentOperationsAdd import frmInvestmentOperationsAdd
from xulpymoney.ui.myqdialog import MyModalQDialog
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
        
        self.creditcardoperations=CreditCardOperationManager(self.mem)#CreditCardOperationManager. Selected will be another CreditCardOperationManager
          
        self.mqtwOperations.setSettings(self.mem.settings, "frmAccountsReport", "mqtwOperations")
        self.mqtwOperations.table.customContextMenuRequested.connect(self.on_mqtwOperations_customContextMenuRequested)

        self.mqtwCreditCards.setSettings(self.mem.settings, "frmAccountsReport", "mqtwCreditCards")
        self.mqtwCreditCards.table.customContextMenuRequested.connect(self.on_mqtwCreditCards_customContextMenuRequested)

        self.mqtwCreditCardOperations.setSettings(self.mem.settings, "frmAccountsReport", "mqtwCreditCardOperations")
        self.mqtwCreditCardOperations.table.customContextMenuRequested.connect(self.on_mqtwCreditCardOperations_customContextMenuRequested)
        self.mqtwCreditCardOperations.setSelectionMode(QAbstractItemView.SelectRows, QAbstractItemView.MultiSelection)

        self.mqtwCreditCardOperationsHistorical.setSettings(self.mem.settings, "frmAccountsReport", "mqtwCreditCardOperationsHistorical")
    
        self.wdgDtPago.set(datetime.now(), self.mem.localzone_name)
        
        currencies_qcombobox(self.cmbCurrency)
        self.mem.data.banks_active().qcombobox(self.cmbEB)
                    
        if self.account is None:
            self.account_insert=True
            self.account=Account(self.mem)
            self.lblTitulo.setText(self.tr("New account data"))
            self.tab.setCurrentIndex(0)
            self.tab.setTabEnabled(1, False)
            self.tab.setTabEnabled(2, False)
            self.chkActiva.setChecked(True)
            self.chkActiva.setEnabled(False)
            self.mqtwOperations.setEnabled(False)
            self.cmdDatos.setText(self.tr("Add a new account"))
        else:
            self.account_insert=False
            self.account.needStatus(1)
            self.tab.setCurrentIndex(0)
            self.lblTitulo.setText(self.account.name)
            self.txtAccount.setText(self.account.name)
            self.txtNumero.setText(str(self.account.number))            
            self.cmbEB.setCurrentIndex(self.cmbEB.findData(self.account.bank.id))
            self.cmbEB.setEnabled(False)    
            self.cmbCurrency.setCurrentIndex(self.cmbCurrency.findData(self.account.currency))
            self.cmbCurrency.setEnabled(False)
            self.chkActiva.setChecked(self.account.active)
            self.cmdDatos.setText(self.tr("Update account data"))

            dtFirst=Assets(self.mem).first_datetime_allowed_estimated()       
            dtLast=Assets(self.mem).last_datetime_allowed_estimated()
            self.wdgYM.initiate(dtFirst.year,  dtLast.year, date.today().year, date.today().month)
            self.on_wdgYM_changed()
            self.mqtwCreditCards_update()

    @pyqtSlot() 
    def on_actionCreditCardAdd_triggered(self):
        w=frmCreditCardsAdd(self.mem,  self.account,  None, self)
        w.exec_()
        self.mqtwCreditCards_update()

    @pyqtSlot() 
    def on_actionCreditCardEdit_triggered(self):
        w=frmCreditCardsAdd(self.mem, self.account,  self.mqtwCreditCards.selected, self)
        w.exec_()
        self.mqtwCreditCards_update()

    @pyqtSlot() 
    def on_actionCreditCardActivate_triggered(self):
        if self.account.qmessagebox_inactive() or self.account.bank.qmessagebox_inactive():
            return
        if self.mqtwCreditCards.selected==None:
            debug("Selected must be not null")
            return
        self.mqtwCreditCards.selected.active=not self.mqtwCreditCards.selected.active
        self.mqtwCreditCards.selected.save()
        self.mem.con.commit()
        self.mqtwCreditCards_update()
                
    @pyqtSlot() 
    def on_actionCreditCardDelete_triggered(self):
        if self.mqtwCreditCards.selected.is_deletable()==False:
            qmessagebox(self.tr("I can't delete the credit card, because it has dependent registers"), ":/xulpymoney/coins.png")
        else:
            self.mqtwCreditCards.selected.delete()
            self.mem.con.commit()
            self.mqtwCreditCards.clear()#Must be before needStatus (Crashed)
            self.account.needStatus(1, downgrade_to=0)
        self.mqtwCreditCards_update()

    def on_chkCreditCards_stateChanged(self, state):
        self.mqtwCreditCards_update()

    def on_cmdDatos_released(self):
        id_entidadesbancarias=self.cmbEB.itemData(self.cmbEB.currentIndex())
        if id_entidadesbancarias is None:
            qmessagebox(self.tr("You must select a bank"))
            return

        self.account.bank=self.mem.data.banks_active().find_by_id(id_entidadesbancarias)
        self.account.name=self.txtAccount.text()
        self.account.number=self.txtNumero.text()
        self.account.active=self.chkActiva.isChecked()
        self.account.currency=self.cmbCurrency.itemData(self.cmbCurrency.currentIndex())
        self.account.save()
        self.mem.con.commit()
        
        self.lblTitulo.setText(self.account.name)
        self.cmdDatos.setEnabled(False)
        
        if self.account_insert is True:
            self.mem.data.accounts.append(self.account)
            self.done(0)

    def on_wdgYM_changed(self):
        lastMonthBalance=self.account.balance(date(self.wdgYM.year, self.wdgYM.month, 1)-timedelta(days=1), type=2)     
        self.accountoperations=AccountOperationManagerHomogeneus(self.mem, self.account)     
        self.accountoperations.load_from_db(self.mem.con.mogrify("select * from opercuentas where id_cuentas=%s and date_part('year',datetime)=%s and date_part('month',datetime)=%s order by datetime, id_opercuentas", [self.account.id, self.wdgYM.year, self.wdgYM.month]))
        self.accountoperations.myqtablewidget_lastmonthbalance(self.mqtwOperations,  lastMonthBalance)   

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
        args=Comment(self.mem).getArgs(self.mqtwOperations.selected.comentario)#origin,destiny,commission
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
        w=frmAccountOperationsAdd(self.mem, self.account, self.mqtwOperations.selected)
        w.AccountOperationChanged.connect(self.on_wdgYM_changed)
        w.exec_()

    @pyqtSlot() 
    def on_actionOperationDelete_triggered(self):
        self.mqtwOperations.selected.borrar() 
        self.mem.con.commit()         
        self.on_wdgYM_changed()

    @pyqtSlot() 
    def on_actionCreditCardOperAdd_triggered(self):
        w=frmAccountOperationsAdd(self.mem, self.account, None, self.mqtwCreditCards.selected)
        w.CreditCardOperationChanged.connect(self.mqtwCreditCardsOperations_update)
        w.AccountOperationChanged.connect(self.on_wdgYM_changed)#Tarjetas en debito
        w.exec_()
            
    @pyqtSlot() 
    def on_actionCreditCardOperEdit_triggered(self):
        #Como es unico
        selOperCreditCard=self.mqtwCreditCardOperations.selected[0]
        w=frmAccountOperationsAdd(self.mem,  self.account, None, self.mqtwCreditCards.selected, selOperCreditCard)
        w.CreditCardOperationChanged.connect(self.mqtwCreditCardsOperations_update)
        w.exec_()

    @pyqtSlot() 
    def on_actionCreditCardOperDelete_triggered(self):
        for o in self.mqtwCreditCardOperations.selected:
            o.borrar()
            self.creditcardoperations.arr.remove(o)
        self.mem.con.commit()
        self.mqtwCreditCardsOperations_update()
        
    @pyqtSlot() 
    def on_actionCreditCardOperRefund_triggered(self):
        w=frmAccountOperationsAdd(self.mem, opertarjeta=self.mqtwCreditCardOperations.selected[0], refund=True)
        w.CreditCardOperationChanged.connect(self.mqtwCreditCardsOperations_update)
        w.exec_()
            
    @pyqtSlot() 
    def on_actionInvestmentOperationDelete_triggered(self):
        investmentoperation=InvestmentOperation_from_accountoperation(self.mem, self.mqtwOperations.selected)
        investmentoperation.investment.op.remove(investmentoperation)
        self.mem.con.commit()     
        debug("Borrando investment operation "+  str(investmentoperation))
        self.on_wdgYM_changed()

    @pyqtSlot() 
    def on_actionInvestmentOperationEdit_triggered(self):
        investmentoperation=InvestmentOperation_from_accountoperation(self.mem, self.mqtwOperations.selected)
        w=frmInvestmentOperationsAdd(self.mem, investmentoperation.investment, investmentoperation, self)
        w.exec_()
        debug("Edit investmentoperation {}".format(investmentoperation))
        self.on_wdgYM_changed()

    @pyqtSlot()
    def on_actionConceptReport_triggered(self):
        if self.tab.currentIndex()==0:
            concepto=self.mqtwOperations.selected.concepto
        else:
            concepto=self.mqtwCreditCardOperations.selected[0].concepto

        d=MyModalQDialog(self)     
        d.setSettings(self.mem.settings, "frmAccountsReport","qdialog_conceptreport")
        d.setWindowTitle(self.tr("Historical report of {}").format(concepto.name))
        d.setWidgets(wdgConceptsHistorical(self.mem, concepto, d))
        d.exec_()

    ## Selection can be only one row, due to table definitions
    def on_mqtwOperations_customContextMenuRequested(self,  pos):      
        if self.account.qmessagebox_inactive() or self.account.bank.qmessagebox_inactive():
            return

        if self.mqtwOperations.selected is None:
            self.actionOperationDelete.setEnabled(False)
            self.actionOperationEdit.setEnabled(False)   
            self.actionTransferDelete.setEnabled(False)
            self.actionConceptReport.setEnabled(False)
        else:
            if self.mqtwOperations.selected.es_editable()==False:
                self.actionOperationDelete.setEnabled(False)
                self.actionOperationEdit.setEnabled(False)   
                #Una transferencia bien formada no es editable solo con transfer delete.
                if Comment(self.mem).getCode(self.mqtwOperations.selected.comentario) in (
                            eComment.AccountTransferOrigin, 
                            eComment.AccountTransferDestiny, 
                            eComment.AccountTransferOriginCommission, 
                ):
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
        menu.addSeparator()
        menu.addMenu(self.mqtwOperations.qmenu())

        if self.mqtwOperations.selected is not None:
            if self.mqtwOperations.selected.concepto.id in [eConcept.BuyShares,  eConcept.SellShares]:#Shares sale or purchase, allow edit or delete investment operation
                menu.addSeparator()
                menu.addAction(self.actionInvestmentOperationEdit)
                menu.addAction(self.actionInvestmentOperationDelete)
        menu.exec_(self.mqtwOperations.table.mapToGlobal(pos))

    def on_mqtwCreditCards_tableSelectionChanged(self):
            self.mqtwCreditCardsOperations_update()

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
        
        if self.mqtwCreditCards.selected==None:
            self.actionCreditCardOperAdd.setEnabled(False)
            self.actionCreditCardDelete.setEnabled(False)
            self.actionCreditCardEdit.setEnabled(False)
            self.actionCreditCardActivate.setEnabled(False)
        else:
            self.actionCreditCardOperAdd.setEnabled(True)
            self.actionCreditCardDelete.setEnabled(True)
            self.actionCreditCardEdit.setEnabled(True)
            self.actionCreditCardActivate.setEnabled(True)
            if self.mqtwCreditCards.selected.active==True:
                self.actionCreditCardActivate.setChecked(True)
            else:
                self.actionCreditCardActivate.setChecked(False)
        menu.exec_(self.mqtwCreditCards.table.mapToGlobal(pos))

    def mqtwCreditCards_update(self):
        if self.mqtwCreditCards.selected is None:#No1 selected
            self.tabOpertarjetasDiferidas.setEnabled(False)
            self.account.creditcards.myqtablewidget(self.mqtwCreditCards, not self.chkCreditCards.isChecked())
            self.mqtwCreditCardOperations.table.setRowCount(0)
        else:
            self.tabOpertarjetasDiferidas.setEnabled(self.mqtwCreditCards.selected.pagodiferido)
            self.account.creditcards.myqtablewidget(self.mqtwCreditCards, not self.chkCreditCards.isChecked())
            self.mqtwCreditCardsOperations_update()

    def on_mqtwCreditCardOperations_customContextMenuRequested(self,  pos):
        if self.account.qmessagebox_inactive() or self.account.bank.qmessagebox_inactive() or self.mqtwCreditCards.selected.qmessagebox_inactive():
            return

        if self.mqtwCreditCardOperations.selected is None:
            return 

        if len(self.mqtwCreditCardOperations.selected)==0:
            self.grpPago.setEnabled(False)
            self.actionCreditCardOperDelete.setEnabled(False)
            self.actionCreditCardOperEdit.setEnabled(False)
            self.actionCreditCardOperRefund.setEnabled(False)
            self.actionConceptReport.setEnabled(False)
        elif len(self.mqtwCreditCardOperations.selected)==1:
            self.grpPago.setEnabled(True)
            self.actionCreditCardOperDelete.setEnabled(True)
            self.actionCreditCardOperEdit.setEnabled(True)
            self.actionConceptReport.setEnabled(True)
            if self.mqtwCreditCards.selected.pagodiferido==True and self.mqtwCreditCardOperations.selected[0].importe<0:#Only difered purchases
                self.actionCreditCardOperRefund.setEnabled(True)
            else:
                self.actionCreditCardOperRefund.setEnabled(False)
        else:# >=2
            self.grpPago.setEnabled(True)
            self.actionCreditCardOperDelete.setEnabled(False)
            self.actionCreditCardOperEdit.setEnabled(False)
            self.actionConceptReport.setEnabled(False)
            self.actionCreditCardOperRefund.setEnabled(False)
            
        menu=QMenu()
        menu.addAction(self.actionCreditCardOperAdd)
        menu.addAction(self.actionCreditCardOperEdit)
        menu.addAction(self.actionCreditCardOperDelete)
        menu.addSeparator()
        menu.addAction(self.actionConceptReport)
        menu.addSeparator()
        menu.addAction(self.actionCreditCardOperRefund)
        menu.exec_(self.mqtwCreditCardOperations.table.mapToGlobal(pos))
    
    def on_mqtwCreditCardOperations_tableSelectionChanged(self):
        #Manager of selection to be reused
        self.mqtwCreditCardOperations_selectedmanager=CreditCardOperationManager(self.mem)
        for o in self.mqtwCreditCardOperations.selected:
            self.mqtwCreditCardOperations_selectedmanager.append(o)
        #Calcula el balance
        self.lblPago.setText(self.mem.localmoney(self.mqtwCreditCardOperations_selectedmanager.balance()).string())

    def mqtwCreditCardsOperations_update(self):
        self.tabOpertarjetasDiferidas.setCurrentIndex(0)
        self.mqtwCreditCardOperations.table.setRowCount(0)
        if self.mqtwCreditCards.selected is not None:
            self.tabOpertarjetasDiferidas.setEnabled(self.mqtwCreditCards.selected.pagodiferido)
            if self.mqtwCreditCards.selected.pagodiferido==True:#Solo se muestran operaciones si es diferido
                self.grpPago.setEnabled(True)
                self.creditcardoperations.load_from_db(self.mem.con.mogrify("select * from opertarjetas where id_tarjetas=%s and pagado=false", [self.mqtwCreditCards.selected.id, ]))
                self.creditcardoperations.myqtablewidget(self.mqtwCreditCardOperations)
                self.mqtwCreditCardOperations.setOrderBy(0, False)
            else:
                self.grpPago.setEnabled(False)

    def on_cmdPago_released(self):
        c=AccountOperation(self.mem, self.wdgDtPago.datetime(), self.mem.conceptos.find_by_id(40), self.mem.tiposoperaciones.find_by_id(7), self.mqtwCreditCardOperations_selectedmanager.balance(), "Transaction in progress", self.account, None)
        c.save()
        
        c.comentario=Comment(self.mem).encode(eComment.CreditCardBilling, self.mqtwCreditCards.selected, c)
        c.save()
        
        #Modifica el registro y lo pone como pagado y la datetime de pago y añade la opercuenta
        for o in self.mqtwCreditCardOperations_selectedmanager.arr:
            o.fechapago=self.wdgDtPago.datetime()
            o.pagado=True
            o.opercuenta=c
            o.save()
        self.mem.con.commit()
        self.on_wdgYM_changed()
        self.mqtwCreditCardsOperations_update()
    
    def on_cmdDevolverPago_released(self):
        id_opercuentas=self.cmbFechasPago.itemData(int(self.cmbFechasPago.currentIndex()))
        cur = self.mem.con.cursor()      
        cur.execute("delete from opercuentas where id_opercuentas=%s", (id_opercuentas, ))#No merece crear objeto
        cur.execute("update opertarjetas set fechapago=null, pagado=false, id_opercuentas=null where id_opercuentas=%s", (id_opercuentas, ) )
        self.mem.con.commit()
        cur.close()     
        self.on_wdgYM_changed()
        self.mqtwCreditCardsOperations_update()
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
            cur.execute("select distinct(fechapago), id_opercuentas from opertarjetas where id_tarjetas=%s and fechapago is not null  order by fechapago;", (self.mqtwCreditCards.selected.id, ))
            for row in cur:   
                ao=AccountOperation(self.mem, row['id_opercuentas'])
                self.cmbFechasPago.addItem(self.tr("{0} was made a paid of {1}").format(str(row['fechapago'])[0:19],  self.mem.localmoney(-ao.importe))    , ao.id)
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
