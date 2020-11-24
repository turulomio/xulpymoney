from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QDialog
from xulpymoney.ui.Ui_frmAccountOperationsAdd import Ui_frmAccountOperationsAdd
from xulpymoney.objects.creditcardoperation import  CreditCardOperation
from xulpymoney.ui.myqwidgets import qmessagebox
from xulpymoney.libxulpymoneytypes import eComment
from xulpymoney.objects.accountoperation import AccountOperation
from xulpymoney.objects.comment import Comment
from xulpymoney.objects.concept import ConceptManager_for_accountsoperations
from datetime import timedelta

class frmAccountOperationsAdd(QDialog, Ui_frmAccountOperationsAdd):
    AccountOperationChanged=pyqtSignal(AccountOperation)
    CreditCardOperationChanged=pyqtSignal(CreditCardOperation)
    def __init__(self, mem, account=None, opercuenta=None, tarjeta=None ,  opertarjeta=None,  refund=False,  parent=None, ):
        """TIPOS DE ENTRADAS:        
         1   selAccount=x: Inserción de accountsoperations y edición de accounts
         2   selAccount=x, opercuenta=x Modificación de accountsoperations e insecioon de creditcardsoperations a débito
         3   selAccount=x, opercuenta=None , tarjeta=x, Inserción de creditcardsoperations en diferido
         4   selAccount=x, opercuenta=None , tarjeta=x, opertarjeta=x Modificación de creditcardsoperations
         5   selAccount=None, opercuenta=None, tarjeta=None, opertarjeta=x, refund=True Refund of creditcardsoperations. 
         
         Debido a que se puede cambiar de opercuenta a opercreditcard grabo el producto original, en el caso de modificación
         Original puede ser un 
            operaccount, para poder editarla
            opercreditcard, para poder editarlo y refund (aunque existe el booleano self.refund para diferenciarlo)
            -999, para productos nuevos, ya que no puedo sacar null por la señal.
            
        Luego usaré el objeto original para la modificación ya que después se sale de este dialogo y si es uno nuevo dejaré origianl a None y usarre uno nuevo que llamaré final
         """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        
        self.refund=refund
        ConceptManager_for_accountsoperations(self.mem).qcombobox(self.cmbConcepts)
        self.mem.data.accounts_active().qcombobox(self.cmbAccounts)
        self.mem.data.accounts_active().CreditCardManager_active().qcombobox(self.cmbCreditCards)
        self.wdgDT.setLocalzone(self.mem.localzone_name)
        self.wdgDT.show_microseconds(False)

        if account==None and opercuenta==None and tarjeta==None and opertarjeta!=None and  refund==True:
            self.original=opertarjeta
            self.radCreditCards.setChecked(True)
            self.radAccounts.setEnabled(False)
            self.radCreditCards.setEnabled(False)
            self.cmbCreditCards.setEnabled(False)
            self.setWindowTitle(self.tr("Credit card operation refund"))
            self.lblTitulo.setText(self.tr("Credit card operation refund"))
            self.wdgDT.set()
            self.cmbConcepts.setCurrentIndex(self.cmbConcepts.findData(67))
            self.cmbConcepts.setEnabled(False)
            self.cmbAccounts.setCurrentIndex(self.cmbAccounts.findData(opertarjeta.tarjeta.account.id))
            self.cmbCreditCards.setCurrentIndex(self.cmbCreditCards.findData(opertarjeta.tarjeta.id))
            self.txtImporte.setText(-opertarjeta.amount)
            self.txtComentario.setEnabled(False)
        elif opertarjeta!=None:
            self.original=opertarjeta
            self.setWindowTitle(self.tr("Credit card operation update"))
            self.lblTitulo.setText(self.tr("Credit card operation update"))
            self.radCreditCards.setChecked(True)
            self.wdgDT.set(opertarjeta.datetime, self.mem.localzone_name)
            self.cmbConcepts.setCurrentIndex(self.cmbConcepts.findData(opertarjeta.concept.id))
            self.cmbAccounts.setCurrentIndex(self.cmbAccounts.findData(opertarjeta.tarjeta.account.id))
            self.cmbCreditCards.setCurrentIndex(self.cmbCreditCards.findData(opertarjeta.tarjeta.id))
            self.txtImporte.setText(opertarjeta.amount)
            self.txtComentario.setText(opertarjeta.comment)
        elif tarjeta!=None:
            self.original=None
            self.radCreditCards.setChecked(True)
            self.cmbCreditCards.setCurrentIndex(self.cmbCreditCards.findData(tarjeta.id))
            self.setWindowTitle(self.tr("New credit card operation"))
            self.lblTitulo.setText(self.tr("New credit card operation"))
            self.wdgDT.set()
        elif opercuenta!=None:
            self.original=opercuenta
            self.radAccounts.setChecked(True)
            self.setWindowTitle(self.tr("Account operation update"))
            self.lblTitulo.setText(self.tr("Account operation update"))
            self.wdgDT.set(opercuenta.datetime, self.mem.localzone_name)
            self.cmbConcepts.setCurrentIndex(self.cmbConcepts.findData(opercuenta.concept.id))
            self.cmbAccounts.setCurrentIndex(self.cmbAccounts.findData(opercuenta.account.id))
            self.txtImporte.setText(opercuenta.amount)
            self.txtComentario.setText(opercuenta.comment)
        else:
            self.original=None
            self.radAccounts.setChecked(True)
            self.setWindowTitle(self.tr("New account operation"))
            self.lblTitulo.setText(self.tr("New account operation"))
            self.wdgDT.set()
            self.cmbAccounts.setCurrentIndex(self.cmbAccounts.findData(account.id))


    def type_and_id(self, product):
        """0 if account,  1 if credit card. Como no puedo pasar Null por la señal, saco con -999, es decir cuando sea producto nuevo"""
        if product==None:
            return [-999, -999]
        if product.__class__==AccountOperation:
            return (0, product.account.id)
        if product.__class__==CreditCardOperation:
            return (1, product.tarjeta.id)
        print (product.__class__, "ERROR",  product)
            


    def on_cmd_released(self):
        concept=self.mem.concepts.find_by_id(self.cmbConcepts.itemData(self.cmbConcepts.currentIndex()))
        if concept is None:
            qmessagebox(self.tr("You must select a concept"))
            return
        amount=self.txtImporte.decimal()
        comment=self.txtComentario.text()
        accounts_id=self.cmbAccounts.itemData(self.cmbAccounts.currentIndex()) #Sólo se usará en 1 y 2.
        creditcards_id=self.cmbCreditCards.itemData(self.cmbCreditCards.currentIndex())
        cuenta=self.mem.data.accounts_active().find_by_id(accounts_id)
        tarjeta=self.mem.data.accounts.find_creditcard_by_id(creditcards_id)
        
        if not amount:
            qmessagebox(self.tr("You must set the operation amount"))
            return        
        
        if concept.tipooperacion.id==1 and amount>0:
            qmessagebox(self.tr("Expenses can not have a positive amount"))
            return
            
        if concept.tipooperacion.id==2 and amount<0:
            qmessagebox(self.tr("Incomes can not have a negative amount"))
            return
            
        if self.radAccounts.isChecked():#Producto final es un operaccount
            if cuenta==None:
                qmessagebox(self.tr("You need to select an account"))
                return
            if self.original==None:#Producto nuevo
                final=AccountOperation(self.mem)
                final.datetime=self.wdgDT.datetime()
                final.concept=concept
                final.tipooperacion=concept.tipooperacion
                final.amount=amount
                final.comment=comment
                final.account=cuenta
                final.save()
                self.mem.con.commit()        #Se debe hacer el commit antes para que al actualizar con el signal salga todos los datos
                self.AccountOperationChanged.emit(final)
                self.wdgDT.set(self.wdgDT.datetime()+timedelta(seconds=1), self.mem.localzone_name)
                return
            elif self.original.__class__==CreditCardOperation:#Modificación  de opercreditcard por operaccount hay que borrar opercreditcard
                final=AccountOperation(self.mem)
                final.datetime=self.wdgDT.datetime()
                final.concept=concept
                final.tipooperacion=concept.tipooperacion
                final.amount=amount
                final.comment=comment
                final.account=cuenta
                final.save()
                self.original.borrar()
                self.mem.con.commit()        #Se debe hacer el commit antes para que al actualizar con el signal salga todos los datos
                self.AccountOperationChanged.emit(final)
                self.done(0)
                return
            elif self.original.__class__==AccountOperation:
#                origi=self.type_and_id(self.original)#Ya que se cambia en el save
                self.original.datetime=self.wdgDT.datetime()
                self.original.concept=concept
                self.original.tipooperacion=concept.tipooperacion
                self.original.amount=amount
                self.original.comment=comment
                self.original.account=cuenta
                self.original.save()
                self.mem.con.commit()        #Se debe hacer el commit antes para que al actualizar con el signal salga todos los datos
                self.AccountOperationChanged.emit(self.original)
                self.done(0)
                return

        elif self.radCreditCards.isChecked():#Producto final es un opercreditcard
            if tarjeta==None:
                qmessagebox(self.tr("You need to select a credit card"))
                return
            if tarjeta.deferred==False:#Pago débito
                final=AccountOperation(self.mem)
                final.datetime=self.wdgDT.datetime()
                final.concept=concept
                final.tipooperacion=concept.tipooperacion
                final.amount=amount
                final.comment=self.tr("CreditCard {0}. {1}".format(tarjeta.name, comment))
                final.account=tarjeta.account
                final.save()
                if self.original!=None:
                    self.original.borrar()
                self.mem.con.commit()
                self.AccountOperationChanged.emit(final)
                self.done(0)
                return
            elif self.original==None:#CreditCardOperation nueva
                final=CreditCardOperation(self.mem).init__create(self.wdgDT.datetime(), concept, concept.tipooperacion, amount, comment, tarjeta, False, None, None )
                final.save()
                self.mem.con.commit()
                self.CreditCardOperationChanged.emit(final)
                self.wdgDT.set(self.wdgDT.datetime()+timedelta(seconds=1), self.mem.localzone_name)
                return
            elif self.refund==True:#Refun d         
                refund=CreditCardOperation(self.mem)
                refund.datetime=self.wdgDT.datetime()
                refund.concept=concept
                refund.tarjeta=tarjeta
                refund.tipooperacion=concept.tipooperacion
                refund.paid=False
                refund.amount=amount
                refund.comment=Comment(self.mem).encode(eComment.CreditCardRefund, self.original)
                refund.save()
                self.mem.con.commit()        #Se debe hacer el commit antes para que al actualizar con el signal salga todos los datos
                self.CreditCardOperationChanged.emit(refund)
                self.done(0) 
                return
            elif self.original.__class__==AccountOperation:#Modificación  de opercreditcard por operaccount hay que borrar opercreditcard
                final=CreditCardOperation(self.mem).init__create(self.wdgDT.datetime(), concept, concept.tipooperacion, amount, comment, tarjeta, False, None, None )
                final.save()
                self.original.borrar()
                self.mem.con.commit()        #Se debe hacer el commit antes para que al actualizar con el signal salga todos los datos
                self.CreditCardOperationChanged.emit(final)
                self.done(0)
                return
            elif self.original.__class__==CreditCardOperation:
#                origi=self.type_and_id(self.original)#Ya que se cambia en el save
                self.original.datetime=self.wdgDT.datetime()
                self.original.concept=concept
                self.original.tipooperacion=concept.tipooperacion
                self.original.amount=amount
                self.original.comment=comment
                self.original.tarjeta=tarjeta
                self.original.save()
                self.mem.con.commit()        #Se debe hacer el commit antes para que al actualizar con el signal salga todos los datos
                self.CreditCardOperationChanged.emit(self.original)
                self.done(0)
                return

    
