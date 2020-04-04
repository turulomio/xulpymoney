from PyQt5.QtWidgets import QDialog
from xulpymoney.ui.Ui_frmCreditCardsAdd import Ui_frmCreditCardsAdd
from xulpymoney.objects.creditcard import CreditCard
from xulpymoney.casts import b2c,  c2b
from xulpymoney.ui.myqwidgets import qmessagebox

class frmCreditCardsAdd(QDialog, Ui_frmCreditCardsAdd):
    def __init__(self, mem,  account,  creditcard,  parent=None):
        """
            Account es registro
            Si creditcard=None # Insertar
            Si creditcard=reg(CreditCard) #Modificar
        """
        QDialog.__init__(self, parent)
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
        if self.txtMaximum.isValid():
            self.creditcard.name=self.txtCreditCard.text()
            self.creditcard.account=self.account
            self.creditcard.pagodiferido=c2b(self.chkDelayed.checkState())
            self.creditcard.saldomaximo=self.txtMaximum.decimal()
            self.creditcard.numero=self.txtNumber.text()
            self.creditcard.save()
            self.mem.con.commit()        
            self.account.needStatus(1, downgrade_to=0)
            self.done(0)
        else:
            qmessagebox(self.tr("You have written and invalid number"))
    
