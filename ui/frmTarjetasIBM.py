from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Ui_frmTarjetasIBM import *
from libxulpymoney import *

class frmTarjetasIBM(QDialog, Ui_frmTarjetasIBM):
    def __init__(self, mem,  cuenta,  tarjeta,  parent=None):
        """
            Cuenta es registro
            Si tarjeta=None # Insertar
            Si tarjeta=reg(Tarjeta) #Modificar
        """
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        self.cuenta=cuenta
        
            

        if tarjeta==None:
            self.tipo=1#Insertar
            self.tarjeta=Tarjeta(self.mem)
            self.lblTitulo.setText(self.tr("Nueva tarjeta de {0}".format(self.cuenta.name)))
        else:
            self.tipo=2#Modificar
            self.tarjeta=tarjeta
            self.lblTitulo.setText(self.tr("Modificando la tarjeta {0}".format(self.tarjeta.name)))
            self.txtTarjeta.setText(self.tarjeta.name)
            self.chkPagoDiferido.setChecked(b2c(self.tarjeta.activa))
            self.txtSaldoMaximo.setText(str(self.tarjeta.saldomaximo))
            self.txtNumero.setText(self.tarjeta.numero)
            
    def on_cmd_pressed(self):
        self.tarjeta.name=self.txtTarjeta.text()
        self.tarjeta.cuenta=self.cuenta
        self.tarjeta.pagodiferido=c2b(self.chkPagoDiferido.checkState())
        self.tarjeta.saldomaximo=self.txtSaldoMaximo.decimal()
        self.tarjeta.numero=self.txtNumero.text()
        self.tarjeta.activa=True
        self.tarjeta.save()
        self.mem.con.commit()        
        
        if self.tipo==1:#insertar
            self.mem.data.tarjetas_active.arr.append(self.tarjeta)
        
        self.done(0)
    
