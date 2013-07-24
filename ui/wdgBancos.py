from PyQt4.QtCore import *
from PyQt4.QtGui import *
from libxulpymoney import *
from frmCuentasIBM import *
from frmInversionesEstudio import *
from Ui_wdgBancos import *

class wdgBancos(QWidget, Ui_wdgBancos):
    def __init__(self, cfg,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.cfg=cfg
        self.selEB=None#id_ebs
        self.selCuenta=None #id_cuentas
        self.selInversion=None #Registro
        
        self.load_data_from_db()
        
        self.ebs=None
        self.inversiones=None
        self.cuentas=None

        self.tblEB.settings("wdgBancos",  self.cfg.inifile)
        self.tblCuentas.settings("wdgBancos",  self.cfg.inifile)
        self.tblInversiones.settings("wdgBancos",  self.cfg.inifile)
        
        self.on_chkInactivas_stateChanged(Qt.Unchecked)#Carga eb
                
    def load_data_from_db(self):
        inicio=datetime.datetime.now()
        self.data_ebs=SetEntidadesBancarias(self.cfg)
        self.data_ebs.load_from_db("select * from entidadesbancarias where eb_activa=true")
        self.data_cuentas=SetCuentas(self.cfg, self.data_ebs)
        self.data_cuentas.load_from_db("select * from cuentas where cu_activa=true")
        self.data_investments=SetInvestments(self.cfg)
        self.data_investments.load_from_db("select distinct(myquotesid) from inversiones where in_activa=true")
        self.data_inversiones=SetInversiones(self.cfg, self.data_cuentas, self.data_investments)
        self.data_inversiones.load_from_db("select * from inversiones where in_activa=true")
        print("\n","Cargando data en wdgInversiones",  datetime.datetime.now()-inicio)
        
    def load_eb(self):

        self.tblEB.clearContents()
        self.tblEB.setRowCount(len(self.ebs)+1);
        sumsaldos=Decimal(0)
        for i,  e in enumerate(self.ebs):
            self.tblEB.setItem(i, 0, QTableWidgetItem(e.name))
            self.tblEB.setItem(i, 1, qbool(e.activa))
            saldo=e.saldo(self.data_cuentas, self.data_inversiones)
            self.tblEB.setItem(i, 2, self.cfg.localcurrency.qtablewidgetitem(saldo))
            sumsaldos=sumsaldos+saldo     
        self.tblEB.setItem(len(self.ebs), 0, QTableWidgetItem(self.tr('TOTAL')))
        self.tblEB.setItem(len(self.ebs), 2, self.cfg.localcurrency.qtablewidgetitem(sumsaldos))        
        
    def load_cuentas(self):
        self.tblCuentas.clearContents()
        self.tblCuentas.setRowCount(len(self.cuentas)+1);
        sumsaldos=0
        for i,  c in enumerate(self.cuentas):
            self.tblCuentas.setItem(i, 0, QTableWidgetItem(c.name))
            self.tblCuentas.setItem(i, 1, qbool(c.activa))
            self.tblCuentas.setItem(i, 2, self.cfg.localcurrency.qtablewidgetitem(c.saldo))
            sumsaldos=sumsaldos+c.saldo
        self.tblCuentas.setItem(len(self.cuentas), 0, QTableWidgetItem(self.tr('TOTAL')))
        self.tblCuentas.setItem(len(self.cuentas), 2, self.cfg.localcurrency.qtablewidgetitem(sumsaldos))                
        
                
    def load_inversiones(self):
        self.tblInversiones.clearContents()
        self.tblInversiones.setRowCount(len(self.inversiones)+1);
        sumsaldos=0
        for i, inv in enumerate(self.inversiones):
            self.tblInversiones.setItem(i, 0, QTableWidgetItem(inv.name))
            self.tblInversiones.setItem(i, 1, qbool(inv.activa))
            saldo=inv.saldo()
            self.tblInversiones.setItem(i, 2, self.cfg.localcurrency.qtablewidgetitem(saldo))
            sumsaldos=sumsaldos+saldo
        self.tblInversiones.setItem(len(self.inversiones), 1, QTableWidgetItem(self.tr('TOTAL')))
        self.tblInversiones.setItem(len(self.inversiones), 3, self.cfg.localcurrency.qtablewidgetitem(sumsaldos))                
        
        
    def on_chkInactivas_stateChanged(self, state):
        if state==Qt.Unchecked:
            self.ebs=self.data_ebs.arr
        else:
            self.ebs=self.cfg.ebs_activas(False)
        self.ebs=sorted(self.ebs, key=lambda eb: eb.name,  reverse=False) 
        self.load_eb()
        self.tblEB.clearSelection()   
        self.tblCuentas.setRowCount(0)
        self.tblCuentas.clearContents()
        self.tblInversiones.setRowCount(0);
        self.tblInversiones.clearContents()

    def on_tblEB_itemSelectionChanged(self):
        self.selEB=None
        self.inversiones=[]
        self.cuentas=[]
        
        for i in self.tblEB.selectedItems():#itera por cada item no row.
            if i.row()<len(self.ebs):#Necesario porque tiene fila de total
                self.selEB=self.ebs[i.row()]
        print ("Seleccionado: " +  str(self.selEB))
        
        if self.selEB==None:
            self.tblEB.clearSelection()   
            self.tblCuentas.setRowCount(0)
            self.tblCuentas.clearContents()
            self.tblInversiones.setRowCount(0);
            self.tblInversiones.clearContents()
            return
            
        activas=False
        if self.chkInactivas.checkState()==Qt.Unchecked:
            activas=True
            
        for i in self.data_inversiones.arr:
            if i.activa==activas and i.cuenta.eb.id==self.selEB.id:
                self.inversiones.append(i)
        self.inversiones=sorted(self.inversiones, key=lambda inve: inve.name,  reverse=False) 
        
        for v in self.data_cuentas.arr:
            if v.activa==activas and v.eb.id==self.selEB.id:
                self.cuentas.append(v)
        self.cuentas=sorted(self.cuentas, key=lambda c: c.name,  reverse=False) 
        
        self.load_cuentas()
        self.load_inversiones()

    def on_tblEB_customContextMenuRequested(self,  pos):
        if self.selEB==None:
            self.actionBancoBorrar.setEnabled(False)
            self.actionBancoModificar.setEnabled(False)
            self.actionActiva.setEnabled(False)
        else:
            self.actionBancoBorrar.setEnabled(True)
            self.actionBancoModificar.setEnabled(True)
            self.actionActiva.setEnabled(True)
            
        if self.chkInactivas.checkState()==Qt.Unchecked:
            self.actionActiva.setChecked(True)
        else:
            self.actionActiva.setChecked(False)
            
        menu=QMenu()
        menu.addAction(self.actionBancoNuevo)
        menu.addAction(self.actionBancoModificar)
        menu.addAction(self.actionBancoBorrar)
        menu.addSeparator()
        menu.addAction(self.actionActiva)
        menu.exec_(self.tblEB.mapToGlobal(pos))
        
    @QtCore.pyqtSlot() 
    def on_actionCuentaEstudio_activated(self):
        w=frmCuentasIBM(self.cfg, self.selCuenta)
        w.exec_()        
        self.load_cuentas()

    @QtCore.pyqtSlot() 
    def on_actionInversionEstudio_activated(self):
        w=frmInversionesEstudio(self.cfg, self.selInversion)
        w.exec_()
        self.load_inversiones()

    def on_tblCuentas_itemSelectionChanged(self):
        self.selCuenta=None
        for i in self.tblCuentas.selectedItems():#itera por cada item no row.
            if i.row()<len(self.cuentas):#Necesario porque tiene fila de total
                self.selCuenta=self.cuentas[i.row()]
        print ("Seleccionado: " +  str(self.selCuenta))

    def on_tblCuentas_customContextMenuRequested(self,  pos):
        if self.selCuenta==None:
            self.actionCuentaEstudio.setEnabled(False)
        else:
            self.actionCuentaEstudio.setEnabled(True)
        menu=QMenu()
        menu.addAction(self.actionCuentaEstudio)
        menu.exec_(self.tblCuentas.mapToGlobal(pos))


    def on_tblInversiones_itemSelectionChanged(self):
        self.selInversion=None
        for i in self.tblInversiones.selectedItems():#itera por cada item no row.
            if i.row()<len(self.inversiones):#Necesario porque tiene fila de total
                self.selInversion=self.inversiones[i.row()]
        print ("Seleccionado: " +  str(self.selInversion))

        
    def on_tblInversiones_customContextMenuRequested(self,  pos):
        if self.selInversion==None:
            self.actionInversionEstudio.setEnabled(False)
        else:
            self.actionInversionEstudio.setEnabled(True)
        menu=QMenu()
        menu.addAction(self.actionInversionEstudio)        
        menu.exec_(self.tblInversiones.mapToGlobal(pos))
        
    @QtCore.pyqtSlot()  
    def on_actionBancoBorrar_activated(self):
        if self.selEB.es_borrable(self.cfg.dic_cuentas)==False:
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.trUtf8("Este banco tiene cuentas dependientes y no puede ser borrado"))
            m.exec_()
        else:
            con=self.cfg.connect_xulpymoney()
            cur = con.cursor()
            self.selEB.borrar(cur, self.cfg.dic_cuentas)
            #Se borra de la lista de wdgBancos ebs y del diccionario raiz 
            self.ebs.remove(self.selEB)
            del self.cfg.dic_ebs[str(self.selEB.id)]
            con.commit()  
            cur.close()     
            self.cfg.disconnect_xulpymoney(con)    
            self.load_eb()    
        
    @QtCore.pyqtSlot()  
    def on_actionBancoNuevo_activated(self):
        tipo=QInputDialog().getText(self,  "Xulpymoney > Bancos > Nuevo ",  "Introduce un nuevo banco")
        if tipo[1]==True:
            eb=EntidadBancaria().init__create(tipo[0])
            con=self.cfg.connect_xulpymoney()
            cur = con.cursor()
            eb.save(cur)
            con.commit()
            cur.close()     
            #Se añade a la lista local y al diccionario raiz
            self.cfg.disconnect_xulpymoney(con)    
            self.ebs.append(eb)
            self.cfg.dic_ebs[str(eb.id)]=eb
            self.ebs=sorted(self.ebs, key=lambda eb: eb.name,  reverse=False) 
            self.load_eb()


    @QtCore.pyqtSlot()  
    def on_actionBancoModificar_activated(self):
        tipo=QInputDialog().getText(self,  "Xulpymoney > Bancos > Modificar",  "Modifica el banco seleccionado", QLineEdit.Normal,   (self.selEB.name))       
        if tipo[1]==True:
            self.selEB.name=tipo[0]
            con=self.cfg.connect_xulpymoney()
            cur = con.cursor()
            self.selEB.save(cur)
            con.commit()
            cur.close()     
            self.cfg.disconnect_xulpymoney(con)    
            self.ebs=sorted(self.ebs, key=lambda eb: eb.name,  reverse=False) 
            self.load_eb()   
        
    @QtCore.pyqtSlot() 
    def on_actionActiva_activated(self):
        self.selEB.activa=self.actionActiva.isChecked()
        con=self.cfg.connect_xulpymoney()
        cur = con.cursor()      
        self.selEB.save(cur)
        con.commit()   
        cur.close()     
        self.cfg.disconnect_xulpymoney(con)    
        self.ebs.remove(self.selEB)
        self.load_eb()
