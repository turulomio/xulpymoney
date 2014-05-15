from PyQt4.QtCore import *
from PyQt4.QtGui import *
import datetime
from libxulpymoney import *
from Ui_wdgDividendsReport import *
from frmInversionesEstudio import *
from frmAnalisis import *
from frmEstimationsAdd import *

class wdgDividendsReport(QWidget, Ui_wdgDividendsReport):
    def __init__(self, mem,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        self.inversiones=[]

        self.tblInversiones.settings("wdgDividendsReport",  self.mem)
        
        self.on_chkInactivas_stateChanged(Qt.Unchecked)

    @QtCore.pyqtSlot()  
    def on_actionModificarDPA_activated(self):
        d=frmEstimationsAdd(self.mem, self.selInversion.product, "dps")
        d.exec_()
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())
        self.tblInversiones.clearSelection()

    def on_chkInactivas_stateChanged(self,  state):               
        if state==Qt.Checked:
            self.mem.data.load_inactives()
            self.inversiones=self.mem.data.inversiones_inactive
        else:
            self.inversiones=self.mem.data.inversiones_active
        self.load_inversiones()
        
    def load_inversiones(self):    
        self.inversiones.sort_by_percentage()#Se ordena self.inversiones.arr
        
        self.tblInversiones.clearContents()
        self.tblInversiones.setRowCount(len(self.inversiones.arr));
        sumdiv=Decimal(0)
        for i, inv in enumerate(self.inversiones.arr):
            if inv.product.estimations_dps.find(datetime.date.today().year)==None:
                dpa=0
                tpc=0
                divestimado=0
            else:
                dpa=inv.product.estimations_dps.currentYear().estimation
                tpc=inv.product.estimations_dps.currentYear().percentage()
                divestimado=inv.dividend_bruto_estimado()
            
            self.tblInversiones.setItem(i, 0,QTableWidgetItem(inv.name))
            self.tblInversiones.setItem(i, 1, QTableWidgetItem(inv.cuenta.eb.name))
            self.tblInversiones.setItem(i, 2, inv.product.currency.qtablewidgetitem(inv.product.result.basic.last.quote))
            self.tblInversiones.setItem(i, 3, inv.product.currency.qtablewidgetitem(dpa))    
            self.tblInversiones.setItem(i, 4, qright(str(inv.acciones())))
            sumdiv=sumdiv+divestimado
            self.tblInversiones.setItem(i, 5, inv.product.currency.qtablewidgetitem(divestimado))
            self.tblInversiones.setItem(i, 6, qtpc(tpc))
                
            #Colorea si está desactualizado
            if inv.product.estimations_dps.dias_sin_actualizar()>self.spin.value():
                self.tblInversiones.item(i, 3).setBackgroundColor(QColor(255, 146, 148))
        self.lblTotal.setText(self.trUtf8("Si mantuviera la inversión un año obtendría {0}".format( self.mem.localcurrency.string(sumdiv)) ))
            
        
    @QtCore.pyqtSlot() 
    def on_actionInversionEstudio_activated(self):
        w=frmInversionesEstudio(self.mem, self.selInversion, self)
        w.exec_()
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())

            
    @QtCore.pyqtSlot() 
    def on_actionMyStocks_activated(self):
        w=frmAnalisis(self.mem, self.selInversion.product, self.selInversion, self)
        w.exec_()
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())

                    
    def on_cmd_pressed(self):
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())

    def on_tblInversiones_customContextMenuRequested(self,  pos):        
        menu=QMenu()
        menu.addAction(self.actionModificarDPA)
        menu.addSeparator()
        menu.addAction(self.actionInversionEstudio) 
        menu.addAction(self.actionMyStocks)    
        menu.exec_(self.tblInversiones.mapToGlobal(pos))

    def on_tblInversiones_itemSelectionChanged(self):
        self.selInversion=None
        for i in self.tblInversiones.selectedItems():#itera por cada item no row.
            self.selInversion=self.inversiones.arr[i.row()]
        print ("Seleccionado: " +  str(self.selInversion))

