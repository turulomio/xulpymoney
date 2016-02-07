
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from Ui_frmAccountOperationsAdd import *
from libxulpymoney import *

class frmAccountOperationsAdd(QDialog, Ui_frmAccountOperationsAdd):
    OperAccountIBMed=pyqtSignal()
    OperCreditCardIBMed=pyqtSignal()
    def __init__(self, mem, cuentas, cuenta, opercuenta=None, tarjeta=None ,  opertarjeta=None ,  parent=None):
        """TIPOS DE ENTRADAS:        
         1   selAccount=x: Inserción de Opercuentas y edición de cuentas
         2   selAccount=x, selMovimiento=x Modificación de opercuentas
         3   selAccount=x, selMovimiento=x , tarjeta=x, Inserción de opertarjetas
         4   selAccount=x, selMovimiento=x , tarjeta=x, opertarjeta Modificación de opertarjetas"""
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        
        self.account=cuenta
        self.opercuenta=opercuenta
        self.tarjeta=tarjeta
        self.opertarjeta=opertarjeta

        self.mem.conceptos.load_opercuentas_qcombobox(self.cmbConcepts)
        self.mem.data.accounts_active().qcombobox(self.cmbAccounts)
        self.wdgDT.show_microseconds(False)

        if opertarjeta!=None:
            self.setWindowTitle(self.tr("Credit card operation update"))
            self.lblTitulo.setText(self.tr("Credit card operation update"))
            self.cmbAccounts.hide()
            self.tipo=4            
            self.wdgDT.set(self.mem, self.opertarjeta.datetime, self.mem.localzone)
            self.cmbConcepts.setCurrentIndex(self.cmbConcepts.findData(self.opertarjeta.concepto.id))
            self.cmbAccounts.setCurrentIndex(self.cmbAccounts.findData(self.opertarjeta.tarjeta.account.id))
            self.txtImporte.setText(str(self.opertarjeta.importe))
            self.txtComentario.setText(self.opertarjeta.comentario)
        elif tarjeta!=None:
            self.setWindowTitle(self.tr("New credit card operation"))
            self.lblTitulo.setText(self.tr("New credit card operation"))
            self.wdgDT.set(self.mem)
            self.cmbAccounts.hide()
            self.tipo=3
        elif self.opercuenta!=None:
            self.tipo=2
            self.setWindowTitle(self.tr("Account operation update"))
            self.lblTitulo.setText(self.tr("Account operation update"))
            self.wdgDT.set(self.mem, self.opercuenta.datetime, self.mem.localzone)
            self.cmbConcepts.setCurrentIndex(self.cmbConcepts.findData(self.opercuenta.concepto.id))
            self.cmbAccounts.setCurrentIndex(self.cmbAccounts.findData(self.opercuenta.account.id))
            self.txtImporte.setText(str(self.opercuenta.importe))
            self.txtComentario.setText((self.opercuenta.comentario))    
        else:
            self.tipo=1
            self.setWindowTitle(self.tr("New account operation"))
            self.lblTitulo.setText(self.tr("New account operation"))
            self.wdgDT.set(self.mem)
            self.cmbAccounts.setCurrentIndex(self.cmbAccounts.findData(self.account.id))

        
    def on_cmd_released(self):
        concepto=self.mem.conceptos.find_by_id(self.cmbConcepts.itemData(self.cmbConcepts.currentIndex()))
        importe=self.txtImporte.decimal()
        comentario=self.txtComentario.text()
        id_cuentas=self.cmbAccounts.itemData(self.cmbAccounts.currentIndex()) #Sólo se usará en 1 y 2.
        
        if not importe:
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.tr("You must set the operation amount"))
            m.exec_()    
            return        
        
        if concepto.tipooperacion.id==1 and importe>0:
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.tr("Expenses can not have a positive amount"))
            m.exec_()    
            return
            
        if concepto.tipooperacion.id==2 and importe<0:
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.tr("Incomes can not have a negative amount"))
            m.exec_()
            return
                    
        if self.tipo==1:
            self.opercuenta=AccountOperation(self.mem)
            self.opercuenta.account=self.account
            self.opercuenta.datetime=self.wdgDT.datetime()
            self.opercuenta.concepto=concepto
            self.opercuenta.tipooperacion=concepto.tipooperacion
            self.opercuenta.importe=importe
            self.opercuenta.comentario=comentario
            self.opercuenta.account=self.mem.data.accounts_active().find_by_id(id_cuentas)#Se puede cambiar
            self.opercuenta.save()
            self.mem.con.commit()        #Se debe hacer el commit antes para que al actualizar con el signal salga todos los datos
            self.OperAccountIBMed.emit()
            self.wdgDT.set(self.mem, self.wdgDT.datetime()+datetime.timedelta(seconds=1), self.wdgDT.zone)
        elif self.tipo==2:            
            self.opercuenta.datetime=self.wdgDT.datetime()
            self.opercuenta.concepto=concepto
            self.opercuenta.tipooperacion=concepto.tipooperacion
            self.opercuenta.importe=importe
            self.opercuenta.comentario=comentario
            self.opercuenta.account=self.mem.data.accounts_active().find_by_id(id_cuentas)#Se puede cambiar
            self.opercuenta.save()
            self.mem.con.commit()        #Se debe hacer el commit antes para que al actualizar con el signal salga todos los datos
            self.OperAccountIBMed.emit()
            self.done(0)
        elif self.tipo==3:
            self.opertarjeta=CreditCardOperation(self.mem).init__create(self.wdgDT.datetime(), concepto, concepto.tipooperacion, importe, comentario, self.tarjeta, False, None, None )
            self.opertarjeta.save()
            self.mem.con.commit()        
#            self.tarjeta.op_diferido.append(self.opertarjeta)
            self.OperCreditCardIBMed.emit()
            self.wdgDT.set(self.mem, self.wdgDT.datetime()+datetime.timedelta(seconds=1), self.wdgDT.zone)
        elif self.tipo==4:            
            self.opertarjeta.datetime=self.wdgDT.datetime()
            self.opertarjeta.concepto=concepto
            self.opertarjeta.tipooperacion=concepto.tipooperacion
            self.opertarjeta.importe=importe
            self.opertarjeta.comentario=comentario
            self.opertarjeta.save()
            self.mem.con.commit()        #Se debe hacer el commit antes para que al actualizar con el signal salga todos los datos
            self.OperCreditCardIBMed.emit()
            self.done(0)            
    
