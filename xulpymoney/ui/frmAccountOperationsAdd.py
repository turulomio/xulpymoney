from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QDialog
from Ui_frmAccountOperationsAdd import Ui_frmAccountOperationsAdd
from libxulpymoney import  AccountOperation,  Comment, CreditCardOperation,  qmessagebox
from datetime import timedelta

class frmAccountOperationsAdd(QDialog, Ui_frmAccountOperationsAdd):
    OperationChanged=pyqtSignal(int, int, int, int)#(tipoproducto original (0 Account, 1 CreditCard), id_original, tipoproducto final, id_final)
    def __init__(self, mem, account=None, opercuenta=None, tarjeta=None ,  opertarjeta=None,  refund=False,  parent=None, ):
        """TIPOS DE ENTRADAS:        
         1   selAccount=x: Inserción de Opercuentas y edición de cuentas
         2   selAccount=x, opercuenta=x Modificación de opercuentas e insecioon de opertarjetas a débito
         3   selAccount=x, opercuenta=None , tarjeta=x, Inserción de opertarjetas en diferido
         4   selAccount=x, opercuenta=None , tarjeta=x, opertarjeta=x Modificación de opertarjetas
         5   selAccount=None, opercuenta=None, tarjeta=None, opertarjeta=x, refund=True Refund of opertarjetas. 
         
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

        self.mem.conceptos.load_opercuentas_qcombobox(self.cmbConcepts)
        self.mem.data.accounts_active().qcombobox(self.cmbAccounts)
        self.mem.data.creditcards_active().qcombobox(self.cmbCreditCards)
        self.wdgDT.show_microseconds(False)

        if account==None and opercuenta==None and tarjeta==None and opertarjeta!=None and  refund==True:
            self.original=opertarjeta
            self.radCreditCards.setChecked(True)
            self.radAccounts.setEnabled(False)
            self.radCreditCards.setEnabled(False)
            self.cmbCreditCards.setEnabled(False)
            self.setWindowTitle(self.tr("Credit card operation refund"))
            self.lblTitulo.setText(self.tr("Credit card operation refund"))
            self.wdgDT.set(self.mem)
            self.cmbConcepts.setCurrentIndex(self.cmbConcepts.findData(67))
            self.cmbConcepts.setEnabled(False)
            self.cmbAccounts.setCurrentIndex(self.cmbAccounts.findData(opertarjeta.tarjeta.account.id))
            self.cmbCreditCards.setCurrentIndex(self.cmbCreditCards.findData(opertarjeta.tarjeta.id))
            self.txtImporte.setText(-opertarjeta.importe)
            self.txtComentario.setEnabled(False)
        elif opertarjeta!=None:
            self.original=opertarjeta
            self.setWindowTitle(self.tr("Credit card operation update"))
            self.lblTitulo.setText(self.tr("Credit card operation update"))
            self.radCreditCards.setChecked(True)
            self.wdgDT.set(self.mem, opertarjeta.datetime, self.mem.localzone)
            self.cmbConcepts.setCurrentIndex(self.cmbConcepts.findData(opertarjeta.concepto.id))
            self.cmbAccounts.setCurrentIndex(self.cmbAccounts.findData(opertarjeta.tarjeta.account.id))
            self.cmbCreditCards.setCurrentIndex(self.cmbCreditCards.findData(opertarjeta.tarjeta.id))
            self.txtImporte.setText(opertarjeta.importe)
            self.txtComentario.setText(opertarjeta.comentario)
        elif tarjeta!=None:
            self.original=None
            self.radCreditCards.setChecked(True)
            self.cmbCreditCards.setCurrentIndex(self.cmbCreditCards.findData(tarjeta.id))
            self.setWindowTitle(self.tr("New credit card operation"))
            self.lblTitulo.setText(self.tr("New credit card operation"))
            self.wdgDT.set(self.mem)
        elif opercuenta!=None:
            self.original=opercuenta
            self.radAccounts.setChecked(True)
            self.setWindowTitle(self.tr("Account operation update"))
            self.lblTitulo.setText(self.tr("Account operation update"))
            self.wdgDT.set(self.mem, opercuenta.datetime, self.mem.localzone)
            self.cmbConcepts.setCurrentIndex(self.cmbConcepts.findData(opercuenta.concepto.id))
            self.cmbAccounts.setCurrentIndex(self.cmbAccounts.findData(opercuenta.account.id))
            self.txtImporte.setText(opercuenta.importe)
            self.txtComentario.setText(opercuenta.comentario)
        else:
            self.original=None
            self.radAccounts.setChecked(True)
            self.setWindowTitle(self.tr("New account operation"))
            self.lblTitulo.setText(self.tr("New account operation"))
            self.wdgDT.set(self.mem)
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
            
    def emit_OperationChanged(self, type_and_id_initial,  type_and_id_final):
        self.OperationChanged.emit(type_and_id_initial[0], type_and_id_initial[1], type_and_id_final[0], type_and_id_final[1])


    def on_cmd_released(self):
        concepto=self.mem.conceptos.find_by_id(self.cmbConcepts.itemData(self.cmbConcepts.currentIndex()))
        importe=self.txtImporte.decimal()
        comentario=self.txtComentario.text()
        id_cuentas=self.cmbAccounts.itemData(self.cmbAccounts.currentIndex()) #Sólo se usará en 1 y 2.
        id_tarjetas=self.cmbCreditCards.itemData(self.cmbCreditCards.currentIndex())
        cuenta=self.mem.data.accounts_active().find_by_id(id_cuentas)
        tarjeta=self.mem.data.creditcards_active().find_by_id(id_tarjetas)
        
        if not importe:
            qmessagebox(self.tr("You must set the operation amount"))
            return        
        
        if concepto.tipooperacion.id==1 and importe>0:
            qmessagebox(self.tr("Expenses can not have a positive amount"))
            return
            
        if concepto.tipooperacion.id==2 and importe<0:
            qmessagebox(self.tr("Incomes can not have a negative amount"))
            return
            
        if self.radAccounts.isChecked():#Producto final es un operaccount
            if self.original==None:#Producto nuevo
                final=AccountOperation(self.mem)
                final.datetime=self.wdgDT.datetime()
                final.concepto=concepto
                final.tipooperacion=concepto.tipooperacion
                final.importe=importe
                final.comentario=comentario
                final.account=cuenta
                final.save()
                self.mem.con.commit()        #Se debe hacer el commit antes para que al actualizar con el signal salga todos los datos
                self.emit_OperationChanged(self.type_and_id(self.original), self.type_and_id(final))
                self.wdgDT.set(self.mem, self.wdgDT.datetime()+timedelta(seconds=1), self.wdgDT.zone)
                return
            elif self.original.__class__==CreditCardOperation:#Modificación  de opercreditcard por operaccount hay que borrar opercreditcard
                final=AccountOperation(self.mem)
                final.datetime=self.wdgDT.datetime()
                final.concepto=concepto
                final.tipooperacion=concepto.tipooperacion
                final.importe=importe
                final.comentario=comentario
                final.account=cuenta
                final.save()
                self.original.borrar()
                self.mem.con.commit()        #Se debe hacer el commit antes para que al actualizar con el signal salga todos los datos
                self.emit_OperationChanged(self.type_and_id(self.original), self.type_and_id(final))
                self.done(0)
                return
            elif self.original.__class__==AccountOperation:
                origi=self.type_and_id(self.original)#Ya que se cambia en el save
                self.original.datetime=self.wdgDT.datetime()
                self.original.concepto=concepto
                self.original.tipooperacion=concepto.tipooperacion
                self.original.importe=importe
                self.original.comentario=comentario
                self.original.account=cuenta
                self.original.save()
                self.mem.con.commit()        #Se debe hacer el commit antes para que al actualizar con el signal salga todos los datos
                self.emit_OperationChanged(origi, self.type_and_id(self.original))
                self.done(0)
                return

        elif self.radCreditCards.isChecked():#Producto final es un opercreditcard
            if tarjeta.pagodiferido==False:#Pago débito
                final=AccountOperation(self.mem)
                final.datetime=self.wdgDT.datetime()
                final.concepto=concepto
                final.tipooperacion=concepto.tipooperacion
                final.importe=importe
                final.comentario=self.tr("CreditCard {0}. {1}".format(tarjeta.name, comentario))
                final.account=tarjeta.account
                final.save()
                if self.original!=None:
                    self.original.borrar()
                self.mem.con.commit()
                self.emit_OperationChanged(self.type_and_id(self.original), self.type_and_id(final))
                self.done(0)
                return
            elif self.original==None:#CreditCardOperation nueva
                final=CreditCardOperation(self.mem).init__create(self.wdgDT.datetime(), concepto, concepto.tipooperacion, importe, comentario, tarjeta, False, None, None )
                final.save()
                self.mem.con.commit()
                self.emit_OperationChanged(self.type_and_id(self.original), self.type_and_id(final))
                self.wdgDT.set(self.mem, self.wdgDT.datetime()+timedelta(seconds=1), self.wdgDT.zone)
                return
            elif self.refund==True:#Refun d         
                refund=CreditCardOperation(self.mem)
                refund.datetime=self.wdgDT.datetime()
                refund.concepto=concepto
                refund.tarjeta=tarjeta
                refund.tipooperacion=concepto.tipooperacion
                refund.pagado=False
                refund.importe=importe
                refund.comentario=Comment(self.mem).setEncoded10006(self.original)
                refund.save()
                self.mem.con.commit()        #Se debe hacer el commit antes para que al actualizar con el signal salga todos los datos
                self.emit_OperationChanged(self.type_and_id(self.original), self.type_and_id(refund))
                self.done(0) 
                return
            elif self.original.__class__==AccountOperation:#Modificación  de opercreditcard por operaccount hay que borrar opercreditcard
                final=CreditCardOperation(self.mem).init__create(self.wdgDT.datetime(), concepto, concepto.tipooperacion, importe, comentario, tarjeta, False, None, None )
                final.save()
                self.original.borrar()
                self.mem.con.commit()        #Se debe hacer el commit antes para que al actualizar con el signal salga todos los datos
                self.emit_OperationChanged(self.type_and_id(self.original), self.type_and_id(final))
                self.done(0)
                return
            elif self.original.__class__==CreditCardOperation:
                origi=self.type_and_id(self.original)#Ya que se cambia en el save
                self.original.datetime=self.wdgDT.datetime()
                self.original.concepto=concepto
                self.original.tipooperacion=concepto.tipooperacion
                self.original.importe=importe
                self.original.comentario=comentario
                self.original.tarjeta=tarjeta
                self.original.save()
                self.mem.con.commit()        #Se debe hacer el commit antes para que al actualizar con el signal salga todos los datos
                self.emit_OperationChanged(origi, self.type_and_id(self.original))
                self.done(0)
                return

    
