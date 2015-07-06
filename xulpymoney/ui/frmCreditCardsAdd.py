from PyQt5.QtCore import *
from PyQt5.QtGui import *
from Ui_frmCreditCardsAdd import *
from libxulpymoney import *

class frmCreditCardsAdd(QDialog, Ui_frmCreditCardsAdd):
    def __init__(self, mem,  account,  creditcard,  parent=None):
        """
            Account es registro
            Si creditcard=None # Insertar
            Si creditcard=reg(CreditCard) #Modificar
        """
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        self.account=account

        if creditcard==None:
            self.tipo=1#Insertar
            self.creditcard=CreditCard(self.mem)
            self.lblTitle.setText(self.tr("New credit card of {0}").format(self.account.name))
            self.creditcard.active=True
        else:
            self.tipo=2#Modificar
            self.creditcard=creditcard
            self.lblTitle.setText(self.tr("Updating {} credit card").format(self.creditcard.name))
            self.txtCreditCard.setText(self.creditcard.name)
            self.chkDelayed.setChecked(b2c(self.creditcard.pagodiferido))
            self.txtMaximum.setText(str(self.creditcard.saldomaximo))
            self.txtNumber.setText(self.creditcard.numero)
            
    def on_cmd_pressed(self):
        self.creditcard.name=self.txtCreditCard.text()
        self.creditcard.account=self.account
        self.creditcard.pagodiferido=c2b(self.chkDelayed.checkState())
        self.creditcard.saldomaximo=self.txtMaximum.decimal()
        self.creditcard.numero=self.txtNumber.text()
        self.creditcard.save()
        self.mem.con.commit()        
        
        if self.tipo==1:#insertar
            self.mem.data.creditcards_active.append(self.creditcard)
        
        self.done(0)
    
