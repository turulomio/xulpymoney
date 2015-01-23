from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Ui_frmCreditCardsAdd import *
from libxulpymoney import *

class frmCreditCardsAdd(QDialog, Ui_frmCreditCardsAdd):
    def __init__(self, mem,  cuenta,  tarjeta,  parent=None):
        """
            Account es registro
            Si tarjeta=None # Insertar
            Si tarjeta=reg(CreditCard) #Modificar
        """
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        self.cuenta=cuenta

        if tarjeta==None:
            self.tipo=1#Insertar
            self.tarjeta=CreditCard(self.mem)
            self.lblTitle.setText(self.tr("New credit card of {0}").format(self.cuenta.name))
        else:
            self.tipo=2#Modificar
            self.tarjeta=tarjeta
            self.lblTitle.setText(self.tr("Updating {} credit card").format(self.tarjeta.name))
            self.txtCreditCard.setText(self.tarjeta.name)
            self.chkDelayed.setChecked(b2c(self.tarjeta.active))
            self.txtMaximum.setText(str(self.tarjeta.saldomaximo))
            self.txtNumber.setText(self.tarjeta.numero)
            
    def on_cmd_pressed(self):
        self.tarjeta.name=self.txtCreditCard.text()
        self.tarjeta.cuenta=self.cuenta
        self.tarjeta.pagodiferido=c2b(self.chkDelayed.checkState())
        self.tarjeta.saldomaximo=self.txtMaximum.decimal()
        self.tarjeta.numero=self.txtNumber.text()
        self.tarjeta.active=True
        self.tarjeta.save()
        self.mem.con.commit()        
        
        if self.tipo==1:#insertar
            self.mem.data.tarjetas_active.append(self.tarjeta)
        
        self.done(0)
    
