from libxulpymoney import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Ui_wdgInversiones import *
from frmInversionesEstudio import *
from frmQuotesIBM import *
from frmAnalisis import *

class wdgInversiones(QWidget, Ui_wdgInversiones):
    def __init__(self, mem,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        self.inversiones=None
        self.selInversion=None##Apunta a un objeto inversión
        self.loadedinactive=False

        self.progress = QProgressDialog(self.tr("Recibiendo datos solicitados"), self.tr("Cancelar"), 0,0)
        self.progress.setModal(True)
        self.progress.setWindowTitle(self.trUtf8("Recibiendo datos..."))
        self.progress.setMinimumDuration(0)                 
        self.tblInversiones.settings("wdgInversiones",  self.mem)
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())#Carga la tabla
                
    def tblInversiones_load(self):
        """Función que carga la tabla de inversiones con el orden que tenga el arr serl.inversiones"""
        self.tblInversiones.setRowCount(len(self.inversiones.arr))
        self.tblInversiones.clearContents()
        sumpendiente=0
        sumdiario=0
        suminvertido=0
        i=0
        sumpositivos=0
        sumnegativos=0
        gainsyear=str2bool(self.mem.config.get_value("settings", "gainsyear"))
        for inv in self.inversiones.arr:            
            self.tblInversiones.setItem(i, 0, QTableWidgetItem("{0} ({1})".format(inv.name, inv.cuenta.name)))            
            self.tblInversiones.setItem(i, 1, qdatetime(inv.product.result.basic.last.datetime, inv.product.bolsa.zone))
            self.tblInversiones.setItem(i, 2, inv.product.currency.qtablewidgetitem(inv.product.result.basic.last.quote,  6))#Se debería recibir el parametro currency
            
            diario=inv.diferencia_saldo_diario()
            try:
                sumdiario=sumdiario+diario
            except:
                pass
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
            if gainsyear==True and inv.op_actual.less_than_a_year()==True:
                self.tblInversiones.item(i, 8).setIcon(QIcon(":/xulpymoney/new.png"))
            if tpc_invertido!=None and tpc_venta!=None:
                if tpc_invertido<=-50:   
                    self.tblInversiones.item(i, 7).setBackgroundColor(QColor(255, 148, 148))
                if (tpc_venta<=5 and tpc_venta>0) or tpc_venta<0:
                    self.tblInversiones.item(i, 8).setBackgroundColor(QColor(148, 255, 148))
            i=i+1
        if suminvertido!=0:
            self.lblTotal.setText("Patrimonio invertido: %s. Pendiente: %s - %s = %s (%s patrimonio). Dif. Diaria: %s" % (self.mem.localcurrency.string(suminvertido), self.mem.localcurrency.string(sumpositivos),  self.mem.localcurrency.string(-sumnegativos),  self.mem.localcurrency.string(sumpendiente), tpc(100*sumpendiente/suminvertido) , self.mem.localcurrency.string( sumdiario)))
        else:
            self.lblTotal.setText(self.trUtf8("No hay patrimonio invertido"))
            
    def tblInversiones_load_inactivas(self):
        """Función que carga la tabla de inversiones con el orden que tenga el arr serl.inversiones"""
        self.tblInversiones.setRowCount(len(self.inversiones.arr))
        self.tblInversiones.clearContents()
        for i, inv in enumerate(self.inversiones.arr):
            self.tblInversiones.setItem(i, 0, QTableWidgetItem("{0} ({1})".format(inv.name, inv.cuenta.name)))
            self.tblInversiones.setItem(i, 5, inv.product.currency.qtablewidgetitem(inv.saldo()))

    @QtCore.pyqtSlot() 
    def on_actionActiva_activated(self):
        if self.selInversion.cuenta.eb.qmessagebox_inactive()  or self.selInversion.cuenta.qmessagebox_inactive():
            return  
        
        self.mem.data.load_inactives()
        if self.actionActiva.isChecked()==True:
            self.selInversion.activa=True
        else:
            self.selInversion.activa=False
        self.selInversion.save()
        self.mem.con.commit()     
        #Recoloca en los SetInversiones
        if self.selInversion.activa==True:#Está todavía en inactivas
            self.mem.data.inversiones_active.arr.append(self.selInversion)
            if self.mem.data.inversiones_inactive!=None:#Puede que no se haya cargado
                self.mem.data.inversiones_inactive.arr.remove(self.selInversion)
        else:#Está todavía en activas
            self.mem.data.inversiones_active.arr.remove(self.selInversion)
            if self.mem.data.inversiones_inactive!=None:#Puede que no se haya cargado
                self.mem.data.inversiones_inactive.arr.append(self.selInversion)
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())#Carga la tabla

            
    @QtCore.pyqtSlot() 
    def on_actionInversionBorrar_activated(self):
        cur = self.mem.con.cursor()
        self.selInversion.borrar(cur)
        self.mem.con.commit()
        self.mem.data.inversiones_active.arr.remove(self.selInversion)
        self.inversiones.arr.remove(self.selInversion)
        cur.close()
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())#Carga la tabla

          
    @QtCore.pyqtSlot() 
    def on_actionInversionNueva_activated(self):
        w=frmInversionesEstudio(self.mem,   None, self)
        w.exec_()
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())#Carga la tabla
        
    @QtCore.pyqtSlot() 
    def on_actionInversionEstudio_activated(self):
        w=frmInversionesEstudio(self.mem, self.selInversion, self)
        w.exec_()
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())#Carga la tabla

                
    @QtCore.pyqtSlot() 
    def on_actionProduct_activated(self):
        w=frmAnalisis(self.mem, self.selInversion.product, self.selInversion, self)
        w.exec_()
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())#Carga la tabla
            
            
    @QtCore.pyqtSlot() 
    def on_actionProductPrice_activated(self):
        w=frmQuotesIBM(self.mem, self.selInversion.product,None,  self)
        w.exec_()
        self.selInversion.product.result.basic.load_from_db()
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())#Carga la tabla

    @QtCore.pyqtSlot() 
    def on_actionOrdenarTPCDiario_activated(self):
        self.inversiones.arr=sorted(self.inversiones.arr, key=lambda inv: inv.product.result.basic.tpc_diario(),  reverse=True) 
        self.tblInversiones_reload_after_order()
        
    @QtCore.pyqtSlot() 
    def on_actionOrdenarTPCVenta_activated(self):
        try:
            self.inversiones.arr=sorted(self.inversiones.arr, key=lambda inv: ( inv.tpc_venta(), -inv.tpc_invertido()),  reverse=False) #Ordenado por dos criterios
            self.tblInversiones_reload_after_order()
        except:
            print(function_name(self),"Error ordering")
            pass
        
    @QtCore.pyqtSlot() 
    def on_actionOrdenarTPC_activated(self):
        self.inversiones.arr=sorted(self.inversiones.arr, key=lambda inv: inv.tpc_invertido(),  reverse=True) 
        self.tblInversiones_reload_after_order()
        
    @QtCore.pyqtSlot() 
    def on_actionOrdenarHora_activated(self):
        self.inversiones.arr=sorted(self.inversiones.arr, key=lambda inv: inv.product.result.basic.last.datetime,  reverse=False) 
        self.tblInversiones_reload_after_order()
        
    @QtCore.pyqtSlot() 
    def on_actionOrdenarName_activated(self):
        self.inversiones.arr=sorted(self.inversiones.arr, key=lambda inv: inv.name,  reverse=False) 
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
            self.inversiones=self.mem.data.inversiones_active
            self.on_actionOrdenarTPCVenta_activated()
            self.tblInversiones_load()
        else:
            self.mem.data.load_inactives()
            self.inversiones=self.mem.data.inversiones_inactive
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
            self.selInversion=self.inversiones.arr[i.row()]
        
    def on_tblInversiones_cellDoubleClicked(self, row, column):
        if column==7:#TPC inversion
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.trUtf8("Shares number: {0}".format(self.selInversion.acciones()))+"\n"+self.trUtf8("Purchase price average: {0}".format(self.selInversion.product.currency.string(self.selInversion.op_actual.valor_medio_compra()))))
            m.exec_()     
        if column==8:#TPC venta
            f=frmPuntoVenta(self.mem, self.selInversion)
            f.exec_()
