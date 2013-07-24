from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Ui_frmTarjetasIBM import *
from libxulpymoney import *

class frmTarjetasIBM(QDialog, Ui_frmTarjetasIBM):
    def __init__(self, cfg,  cuenta,  tarjeta,  parent=None):
        """
            Cuenta es registro
            Si tarjeta=None # Insertar
            Si tarjeta=reg(Tarjeta) #Modificar
        """
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.cfg=cfg
        self.cuenta=cuenta
        self.tarjeta=tarjeta

        if tarjeta==None:
            self.tipo=1#Insertar
            self.lblTitulo.setText(self.tr("Nueva tarjeta de {0}".format((self.cuenta['cuenta']))))
        else:
            self.tipo=2#Modificar
            self.lblTitulo.setText(self.tr("Modificando la tarjeta {0}".format((self.tarjeta['tarjeta']))))
            self.txtTarjeta.setText((self.tarjeta['tarjeta']))
            self.chkPagoDiferido.setChecked(b2c(self.tarjeta['tj_activa']))
            self.txtSaldoMaximo.setText(str(self.tarjeta['saldomaximo']))
            self.txtNumero.setText(str(self.tarjeta['numero']))
            
    def on_cmd_pressed(self):
        con=self.cfg.connect_xulpymoney()
        cur = con.cursor()    
        id_cuentas=self.cuenta['id_cuentas']
        tarjeta=(self.txtTarjeta.text())
        pagodiferido=False
        if self.chkPagoDiferido.checkState()==Qt.Checked:
            pagodiferido=True
        saldomaximo=Decimal(self.txtSaldoMaximo.text())
        numero=(self.txtNumero.text())

        if self.tipo==1:#insertar
            Tarjeta(self.cfg).insertar( cur,  id_cuentas,  tarjeta,  numero, pagodiferido, saldomaximo, True)
        else:#Modificar
            Tarjeta(self.cfg).modificar( cur,  self.tarjeta['id_tarjetas'], tarjeta,  numero,  pagodiferido,  saldomaximo)
        con.commit()        
        cur.close()     
        self.cfg.disconnect_xulpymoney(con)        
        self.done(0)
    
