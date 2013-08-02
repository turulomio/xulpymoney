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
        self.tblCuentas.settings("wdgCuentas",  self.cfg.file_ui)
        self.tblCuentas.setColumnHidden(0, True)
        self.load_data_from_db()
        self.cuentas=self.data_cuentas.arr
        self.selCuenta=None
        self.load_table()
        self.loadedinactive=False
        
        
    def load_data_from_db(self):
        inicio=datetime.datetime.now()
        self.data_ebs=SetEntidadesBancarias(self.cfg)
        self.data_ebs.load_from_db("select * from entidadesbancarias where eb_activa=true")
        self.data_cuentas=SetCuentas(self.cfg, self.data_ebs)
        self.data_cuentas.load_from_db("select * from cuentas where cu_activa=true order by cuenta")
        print("Cargando data en wdgCuentas",  datetime.datetime.now()-inicio)
        
    def load_inactive_data_from_db(self):
        if self.loadedinactive==False:
            inicio=datetime.datetime.now()
            
            self.data_ebs_inactive=SetEntidadesBancarias(self.cfg)
            self.data_ebs_inactive.load_from_db("select * from entidadesbancarias where eb_activa=false")
            self.data_ebs_all=self.data_ebs.union(self.data_ebs_inactive)
            
            self.data_cuentas_inactive=SetCuentas(self.cfg, self.data_ebs_all)
            self.data_cuentas_inactive.load_from_db("select * from cuentas where cu_activa=false order by cuenta")
            self.data_cuentas_all=self.data_cuentas.union(self.data_cuentas_inactive)
            
            print("Cargando inactive data en wdgCuentas",  datetime.datetime.now()-inicio)
            self.loadedinactive=True
        print (self.trUtf8("Ya se habían cargado las inactivas"))
    def load_table(self):
        """Función que carga la tabla de cuentas"""
        self.tblCuentas.setRowCount(len(self.cuentas));
        sumsaldos=0
        for i, c in enumerate(self.cuentas):
            self.tblCuentas.setItem(i, 0, QTableWidgetItem(str(c.id)))
            self.tblCuentas.setItem(i, 1, QTableWidgetItem((c.name)))
            self.tblCuentas.setItem(i, 2, QTableWidgetItem((c.eb.name)))
            self.tblCuentas.setItem(i, 3, QTableWidgetItem((c.numero)))
            self.tblCuentas.setItem(i, 4, c.currency.qtablewidgetitem(c.saldo))
            sumsaldos=sumsaldos+c.saldo  
        self.lblTotal.setText(("Saldo en las cuentas: %s" % (self.cfg.localcurrency.string(sumsaldos))))
        self.tblCuentas.clearSelection()
        
    @QtCore.pyqtSlot() 
    def on_actionCuentaEstudio_activated(self):
        w=frmCuentasIBM(self.cfg, self.data_ebs,  self.data_cuentas,  self.selCuenta, self)
        w.exec_()
        self.on_chkInactivas_stateChanged(Qt.Unchecked)
        self.load_table()
        
    @QtCore.pyqtSlot() 
    def on_actionCuentaNueva_activated(self):
        w=frmCuentasIBM(self.cfg, None)
        w.exec_()
        self.on_chkInactivas_stateChanged(Qt.Unchecked)
        self.load_table()
      
    @QtCore.pyqtSlot() 
    def on_actionCuentaBorrar_activated(self):
        con=self.cfg.connect_xulpymoney()
        cur = con.cursor()
        if self.selCuenta.es_borrable(cur)==False:
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.trUtf8("Esta cuenta tiene inversiones, tarjetas o movimientos dependientes y no puede ser borrada"))
            m.exec_()
        else:
            self.selCuenta.borrar(cur)
            con.commit()
            del self.cfg.dic_cuentas[str(self.selCuenta.id)]
            self.cuentas.remove(self.selCuenta)
        cur.close()
        self.cfg.disconnect_xulpymoney(con)
        self.on_chkInactivas_stateChanged(Qt.Unchecked)
        self.load_table()
        
    def on_chkInactivas_stateChanged(self, state):
        self.load_inactive_data_from_db()
        if state==Qt.Unchecked:
            self.cuentas=self.data_cuentas.arr
        else:
            self.cuentas=self.data_cuentas_inactive.arr
        self.load_table()
        

    def on_tblCuentas_customContextMenuRequested(self,  pos):
        menu=QMenu()
        menu.addAction(self.actionCuentaNueva)
        menu.addAction(self.actionCuentaBorrar)
        menu.addSeparator()
        menu.addAction(self.actionActiva)
        self.actionActiva.setChecked(self.selCuenta.activa)
        menu.addSeparator()
        menu.addAction(self.actionTransferencia)
        menu.addSeparator()
        menu.addAction(self.actionCuentaEstudio)
        menu.exec_(self.tblCuentas.mapToGlobal(pos))

        
    @QtCore.pyqtSlot() 
    def on_actionActiva_activated(self):
        self.load_inactive_data_from_db()#Debe tenerlas para borrarla luego
        self.selCuenta.activa=self.chkInactivas.isChecked()
        self.selCuenta.save()
        self.cfg.con.commit()     
        #Recoloca en los Setcuentas
        if self.selCuenta.activa==True:#Está todavía en inactivas
            self.data_cuentas.arr.append(self.selCuenta)
            self.data_cuentas_inactive.arr.remove(self.selCuenta)
        else:#Está todavía en activas
            self.data_cuentas.arr.remove(self.selCuenta)
            self.data_cuentas_inactive.arr.append(self.selCuenta)
        self.data_cuentas_all=self.data_cuentas.union(self.data_cuentas_inactive)        
        self.load_table()

    @QtCore.pyqtSlot()  
    def on_actionTransferencia_activated(self):
        w=frmTransferencia(self.cfg, self.selCuenta)
        w.exec_()
        self.load_table()

    def on_tblCuentas_itemSelectionChanged(self):
        for i in self.tblCuentas.selectedItems():#itera por cada item no row.
            self.selCuenta=self.cuentas[i.row()]
        print (self.selCuenta)
