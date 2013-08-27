from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Ui_wdgCuentas import *
from frmTransferencia import *
from frmCuentasIBM import *

class wdgCuentas(QWidget, Ui_wdgCuentas):
    def __init__(self, cfg,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.cfg=cfg
        self.tblCuentas.settings("wdgCuentas",  self.cfg)
        self.cuentas=self.cfg.data.cuentas_active.arr
        self.selCuenta=None
        self.load_table()
        self.loadedinactive=False
        

    def load_table(self):
        """Función que carga la tabla de cuentas"""
        self.tblCuentas.setRowCount(len(self.cuentas));
        sumsaldos=0
        for i, c in enumerate(self.cuentas):
            self.tblCuentas.setItem(i, 0, QTableWidgetItem((c.name)))
            self.tblCuentas.setItem(i, 1, QTableWidgetItem((c.eb.name)))
            self.tblCuentas.setItem(i, 2, QTableWidgetItem((c.numero)))
            self.tblCuentas.setItem(i, 3, c.currency.qtablewidgetitem(c.saldo))
            sumsaldos=sumsaldos+c.saldo  
        self.lblTotal.setText(("Saldo en las cuentas: %s" % (self.cfg.localcurrency.string(sumsaldos))))
        self.tblCuentas.clearSelection()
        
    @QtCore.pyqtSlot() 
    def on_actionCuentaEstudio_activated(self):
        w=frmCuentasIBM(self.cfg,   self.selCuenta, self)
        w.exec_()
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())
        self.load_table()
        
    @QtCore.pyqtSlot() 
    def on_actionCuentaNueva_activated(self):
        w=frmCuentasIBM(self.cfg, None)
        w.exec_()
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())
        self.load_table()
      
    @QtCore.pyqtSlot() 
    def on_actionCuentaBorrar_activated(self):
        if self.selCuenta.eb.qmessagebox_inactive() or self.selCuenta.qmessagebox_inactive():
            return
        cur = self.cfg.con.cursor()
        if self.selCuenta.es_borrable(cur)==False:
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.trUtf8("Esta cuenta tiene inversiones, tarjetas o movimientos dependientes y no puede ser borrada"))
            m.exec_()
        else:
            self.selCuenta.borrar(cur)
            self.cfg.con.commit()
            self.cfg.data.cuentas_active.arr.remove(self.selCuenta)
            self.cuentas.remove(self.selCuenta)
        cur.close()
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())
        self.load_table()
        
    def on_chkInactivas_stateChanged(self, state):
        if state==Qt.Unchecked:
            self.cuentas=self.cfg.data.cuentas_active.arr
        else:
            self.cfg.data.load_inactives()
            self.cuentas=self.cfg.data.cuentas_inactive.arr
        self.load_table()
        

    def on_tblCuentas_customContextMenuRequested(self,  pos):
        if self.selCuenta==None:
            self.actionCuentaBorrar.setEnabled(False)
            self.actionCuentaEstudio.setEnabled(False)
            self.actionActiva.setEnabled(False)
            self.actionCuentaEstudio.setEnabled(False)
        else:
            self.actionCuentaBorrar.setEnabled(True)
            self.actionCuentaEstudio.setEnabled(True)
            self.actionActiva.setEnabled(True)
            self.actionCuentaEstudio.setEnabled(True)
            self.actionActiva.setChecked(self.selCuenta.activa)
        
        
        
        menu=QMenu()
        menu.addAction(self.actionCuentaNueva)
        menu.addAction(self.actionCuentaBorrar)
        menu.addSeparator()
        menu.addAction(self.actionActiva)
        menu.addSeparator()
        menu.addAction(self.actionTransferencia)
        menu.addSeparator()
        menu.addAction(self.actionCuentaEstudio)
        menu.exec_(self.tblCuentas.mapToGlobal(pos))

        
    @QtCore.pyqtSlot() 
    def on_actionActiva_activated(self):
        if self.selCuenta.eb.qmessagebox_inactive()==True:
            return
        
        self.cfg.data.load_inactives()#Debe tenerlas para borrarla luego
        self.selCuenta.activa=self.chkInactivas.isChecked()
        self.selCuenta.save()
        self.cfg.con.commit()     
        #Recoloca en los Setcuentas
        if self.selCuenta.activa==True:#Está todavía en inactivas
            self.cfg.data.cuentas_active.arr.append(self.selCuenta)
            self.cfg.data.cuentas_inactive.arr.remove(self.selCuenta)
        else:#Está todavía en activas
            self.cfg.data.cuentas_active.arr.remove(self.selCuenta)
            self.cfg.data.cuentas_inactive.arr.append(self.selCuenta)    
        self.load_table()

    @QtCore.pyqtSlot()  
    def on_actionTransferencia_activated(self):
        w=frmTransferencia(self.cfg, self.selCuenta)
        w.exec_()
        self.load_table()

    def on_tblCuentas_itemSelectionChanged(self):
        self.selCuenta=None
        for i in self.tblCuentas.selectedItems():#itera por cada item no row.
            if i.column()==0:
                self.selCuenta=self.cuentas[i.row()]
                break
        print (self.selCuenta)
