from libxulpymoney import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Ui_wdgInversiones import *
from frmInversionesEstudio import *
from frmQuotesIBM import *
from frmAnalisis import *

class wdgInversiones(QWidget, Ui_wdgInversiones):
    def __init__(self, cfg,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.cfg=cfg
        self.inversiones=[]
        self.selInversion=None##Apunta a un objeto inversión
        self.loadedinactive=False

        self.progress = QProgressDialog(self.tr("Recibiendo datos solicitados"), self.tr("Cancelar"), 0,0)
        self.progress.setModal(True)
        self.progress.setWindowTitle(self.trUtf8("Recibiendo datos..."))
        self.progress.setMinimumDuration(0)                 
        self.tblInversiones.settings("wdgInversiones",  self.cfg)
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())#Carga la tabla
                
    def tblInversiones_load(self):
        """Función que carga la tabla de inversiones con el orden que tenga el arr serl.inversiones"""
        self.tblInversiones.setRowCount(len(self.inversiones))
        self.tblInversiones.clearContents()
        sumpendiente=0
        sumdiario=0
        suminvertido=0
        i=0
        sumpositivos=0
        sumnegativos=0
        for inv in self.inversiones:
            self.tblInversiones.setItem(i, 0, QTableWidgetItem("{0} ({1})".format(inv.name, inv.cuenta.name)))
            self.tblInversiones.setItem(i, 1, qdatetime(inv.product.result.basic.last.datetime, inv.product.bolsa.zone))
            self.tblInversiones.setItem(i, 2, inv.product.currency.qtablewidgetitem(inv.product.result.basic.last.quote,  6))#Se debería recibir el parametro currency
            
            diario=inv.diferencia_saldo_diario()
            try:
                sumdiario=sumdiario+diario
            except:
                pass
            print (inv)
            self.tblInversiones.setItem(i, 3, inv.product.currency.qtablewidgetitem(diario))
            self.tblInversiones.setItem(i, 4, qtpc(inv.product.result.basic.tpc_diario()))
            self.tblInversiones.setItem(i, 5, inv.product.currency.qtablewidgetitem(inv.saldo()))
            suminvertido=suminvertido+inv.invertido()
            pendiente=inv.pendiente()
            if pendiente>0:
                sumpositivos=sumpositivos+pendiente
            else:
                sumnegativos=sumnegativos+pendiente
            sumpendiente=sumpendiente+pendiente
            self.tblInversiones.setItem(i, 6, inv.product.currency.qtablewidgetitem(pendiente))
            tpc_invertido=inv.tpc_invertido()
            self.tblInversiones.setItem(i, 7, qtpc(tpc_invertido))
            tpc_venta=inv.tpc_venta()
            self.tblInversiones.setItem(i, 8, qtpc(tpc_venta))
            if tpc_invertido!=None and tpc_venta!=None:
                if tpc_invertido<=-50:   
                    self.tblInversiones.item(i, 7).setBackgroundColor(QColor(255, 148, 148))
                if (tpc_venta<=5 and tpc_venta>0) or tpc_venta<0:
                    self.tblInversiones.item(i, 8).setBackgroundColor(QColor(148, 255, 148))
            i=i+1
        if suminvertido!=0:
            self.lblTotal.setText("Patrimonio invertido: %s. Pendiente: %s - %s = %s (%s patrimonio). Dif. Diaria: %s" % (self.cfg.localcurrency.string(suminvertido), self.cfg.localcurrency.string(sumpositivos),  self.cfg.localcurrency.string(-sumnegativos),  self.cfg.localcurrency.string(sumpendiente), tpc(100*sumpendiente/suminvertido) , self.cfg.localcurrency.string( sumdiario)))
        else:
            self.lblTotal.setText(self.trUtf8("No hay patrimonio invertido"))
            
    def tblInversiones_load_inactivas(self):
        """Función que carga la tabla de inversiones con el orden que tenga el arr serl.inversiones"""
        self.tblInversiones.setRowCount(len(self.inversiones))
        self.tblInversiones.clearContents()
        for i, inv in enumerate(self.inversiones):
            self.tblInversiones.setItem(i, 0, QTableWidgetItem("{0} ({1})".format(inv.name, inv.cuenta.name)))
            self.tblInversiones.setItem(i, 5, inv.product.currency.qtablewidgetitem(inv.saldo()))

    @QtCore.pyqtSlot() 
    def on_actionActiva_activated(self):
        if self.selInversion.cuenta.eb.qmessagebox_inactive()  or self.selInversion.cuenta.qmessagebox_inactive():
            return  
        
        self.cfg.data.load_inactives()
        if self.actionActiva.isChecked()==True:
            self.selInversion.activa=True
        else:
            self.selInversion.activa=False
        self.selInversion.save()
        self.cfg.con.commit()     
        #Recoloca en los SetInversiones
        if self.selInversion.activa==True:#Está todavía en inactivas
            self.cfg.data.inversiones_active.arr.append(self.selInversion)
            if self.cfg.data.inversiones_inactive!=None:#Puede que no se haya cargado
                self.cfg.data.inversiones_inactive.arr.remove(self.selInversion)
        else:#Está todavía en activas
            self.cfg.data.inversiones_active.arr.remove(self.selInversion)
            if self.cfg.data.inversiones_inactive!=None:#Puede que no se haya cargado
                self.cfg.data.inversiones_inactive.arr.append(self.selInversion)
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())#Carga la tabla

            
    @QtCore.pyqtSlot() 
    def on_actionInversionBorrar_activated(self):
        cur = self.cfg.con.cursor()
        self.selInversion.borrar(cur)
        self.cfg.con.commit()
        self.cfg.data.inversiones_active.arr.remove(self.selInversion)
        self.inversiones.remove(self.selInversion)
        cur.close()
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())#Carga la tabla

          
    @QtCore.pyqtSlot() 
    def on_actionInversionNueva_activated(self):
        w=frmInversionesEstudio(self.cfg,   None, self)
        w.exec_()
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())#Carga la tabla
        
    @QtCore.pyqtSlot() 
    def on_actionInversionEstudio_activated(self):
        w=frmInversionesEstudio(self.cfg, self.selInversion, self)
        w.exec_()
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())#Carga la tabla
            
    @QtCore.pyqtSlot() 
    def on_actionProduct_activated(self):
        w=frmAnalisis(self.cfg, self.selInversion.product, self.selInversion, self)
        w.exec_()
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())#Carga la tabla
            
            
    @QtCore.pyqtSlot() 
    def on_actionProductPrice_activated(self):
        w=frmQuotesIBM(self.cfg, self.selInversion.product,None,  self)
        w.exec_()
        self.selInversion.product.result.basic.load_from_db()
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())#Carga la tabla

    @QtCore.pyqtSlot() 
    def on_actionOrdenarTPCDiario_activated(self):
        self.inversiones=sorted(self.inversiones, key=lambda inv: inv.product.result.basic.tpc_diario(),  reverse=True) 
        self.tblInversiones_reload_after_order()
        
    @QtCore.pyqtSlot() 
    def on_actionOrdenarTPCVenta_activated(self):
        try:
            self.inversiones=sorted(self.inversiones, key=lambda inv: ( inv.tpc_venta(), -inv.tpc_invertido()),  reverse=False) #Ordenado por dos criterios
            self.tblInversiones_reload_after_order()
        except:
            print(function_name(self),"Error ordering")
            pass
        
    @QtCore.pyqtSlot() 
    def on_actionOrdenarTPC_activated(self):
        self.inversiones=sorted(self.inversiones, key=lambda inv: inv.tpc_invertido(),  reverse=True) 
        self.tblInversiones_reload_after_order()
        
    @QtCore.pyqtSlot() 
    def on_actionOrdenarHora_activated(self):
        self.inversiones=sorted(self.inversiones, key=lambda inv: inv.product.result.basic.last.datetime,  reverse=False) 
        self.tblInversiones_reload_after_order()
        
    @QtCore.pyqtSlot() 
    def on_actionOrdenarName_activated(self):
        self.inversiones=sorted(self.inversiones, key=lambda inv: inv.name,  reverse=False) 
        self.tblInversiones_reload_after_order()
        
    def tblInversiones_reload_after_order(self):
        if self.chkInactivas.checkState()==Qt.Unchecked:
            self.tblInversiones_load()
        else:
            self.tblInversiones_load_inactivas()
        self.tblInversiones.clearSelection()
        self.selInversion=None   
        
    def on_chkInactivas_stateChanged(self, state):
        if state==Qt.Unchecked:
            self.inversiones=self.cfg.data.inversiones_active.arr
            self.on_actionOrdenarTPCVenta_activated()
            self.tblInversiones_load()
        else:
            self.cfg.data.load_inactives()
            self.inversiones=self.cfg.data.inversiones_inactive.arr
            self.on_actionOrdenarName_activated()
            self.tblInversiones_load_inactivas()
        self.tblInversiones.clearSelection()
        self.selInversion=None   

    def on_tblInversiones_customContextMenuRequested(self,  pos):
        if self.selInversion==None:
            self.actionInversionEstudio.setEnabled(False)
            self.actionInversionBorrar.setEnabled(False)
            self.actionActiva.setEnabled(False)
            self.actionProduct.setEnabled(False)
        else:
            self.actionInversionEstudio.setEnabled(True)
            self.actionActiva.setEnabled(True)       
            self.actionProduct.setEnabled(True)
            if self.selInversion.es_borrable()==True:
                self.actionInversionBorrar.setEnabled(True)
            else:
                self.actionInversionBorrar.setEnabled(False)
            if self.selInversion.activa==True:
                self.actionActiva.setChecked(True)
            else:
                self.actionActiva.setChecked(False)

        menu=QMenu()
        menu.addAction(self.actionInversionNueva)
        menu.addAction(self.actionInversionBorrar)   
        menu.addSeparator()   
        menu.addAction(self.actionInversionEstudio)        
        menu.addAction(self.actionProduct)
        menu.addSeparator()
        menu.addAction(self.actionProductPrice)
        menu.addSeparator()
        menu.addAction(self.actionActiva)
        menu.addSeparator()        
        ordenar=QMenu(self.trUtf8("Order by"))
        ordenar.addAction(self.actionOrdenarName)
        ordenar.addAction(self.actionOrdenarHora)
        ordenar.addAction(self.actionOrdenarTPCDiario)
        ordenar.addAction(self.actionOrdenarTPC)
        ordenar.addAction(self.actionOrdenarTPCVenta)
        menu.addMenu(ordenar)        
        menu.exec_(self.tblInversiones.mapToGlobal(pos))

    def on_tblInversiones_itemSelectionChanged(self):
        self.selInversion=None
        for i in self.tblInversiones.selectedItems():#itera por cada item no row.
            self.selInversion=self.inversiones[i.row()]
        
    def on_tblInversiones_cellDoubleClicked(self, row, column):
        if column==7:#TPC inversion
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.trUtf8("Shares number: {0}".format(self.selInversion.acciones()))+"\n"+self.trUtf8("Purchase price average: {0}".format(self.selInversion.product.currency.string(self.selInversion.op_actual.valor_medio_compra()))))
            m.exec_()           
            return
        if column==8:#TPC venta
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            if self.selInversion.venta==0 or self.selInversion.venta==None:
                m.setText(self.trUtf8("There's not selling prince."))
            else:
                m.setText(self.trUtf8("Selling price: {0}".format(self.selInversion.product.currency.string(self.selInversion.venta)))+"\n"+self.trUtf8("Gain obtained: {0}").format(self.selInversion.product.currency.string(self.selInversion.acciones()*(self.selInversion.venta-self.selInversion.op_actual.valor_medio_compra())))) 
            m.exec_()           
            return     
