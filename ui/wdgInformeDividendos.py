from PyQt4.QtCore import *
from PyQt4.QtGui import *
import datetime
from libxulpymoney import *
from Ui_wdgInformeDividendos import *
from frmInversionesEstudio import *
from frmAnalisis import *
from frmEstimationsAdd import *

class wdgInformeDividendos(QWidget, Ui_wdgInformeDividendos):
    def __init__(self, cfg,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.cfg=cfg
        self.inversiones=[]

        self.tblInversiones.settings("wdgInformeDividendos",  self.cfg)
        
        self.on_chkInactivas_stateChanged(Qt.Unchecked)
        
        
            


    @QtCore.pyqtSlot()  
    def on_actionModificarDPA_activated(self):
        d=frmEstimationsAdd(self.cfg, self.selInversion.investment)
        d.exec_()
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())
        self.tblInversiones.clearSelection()

    def on_chkInactivas_stateChanged(self,  state):               
        if state==Qt.Checked:
            self.cfg.data.load_inactives()
            self.inversiones=self.cfg.data.inversiones_inactive
        else:
            self.inversiones=self.cfg.data.inversiones_active
        self.load_inversiones()
        
    def load_inversiones(self):    
        self.inversiones.sort_by_tpc_dpa()#Se ordena self.inversiones.arr
        
        self.tblInversiones.clearContents()
        self.tblInversiones.setRowCount(len(self.inversiones.arr));
        sumdiv=Decimal(0)
        for i, inv in enumerate(self.inversiones.arr):
            if inv.investment.estimations_dps.find(datetime.date.today().year)==None:
                dpa=0
                tpc=0
                divestimado=0
            else:
                dpa=inv.investment.estimations_dps.currentYear().estimation
                tpc=inv.investment.estimations_dps.currentYear().tpc_dpa()
                divestimado=inv.dividendo_bruto_estimado()
            
            self.tblInversiones.setItem(i, 0,QTableWidgetItem(inv.name))
            self.tblInversiones.setItem(i, 1, QTableWidgetItem(inv.cuenta.eb.name))
            self.tblInversiones.setItem(i, 2, inv.investment.currency.qtablewidgetitem(inv.investment.result.basic.last.quote))
            self.tblInversiones.setItem(i, 3, inv.investment.currency.qtablewidgetitem(dpa))    
            self.tblInversiones.setItem(i, 4, qright(str(inv.acciones())))
            sumdiv=sumdiv+divestimado
            self.tblInversiones.setItem(i, 5, inv.investment.currency.qtablewidgetitem(divestimado))
            self.tblInversiones.setItem(i, 6, qtpc(tpc))
                
            #Colorea si está desactualizado
            if inv.investment.estimations_dps.dias_sin_actualizar()>self.spin.value():
                self.tblInversiones.item(i, 3).setBackgroundColor(QColor(255, 146, 148))
        self.lblTotal.setText(self.trUtf8("Si mantuviera la inversión un año obtendría {0}".format( self.cfg.localcurrency.string(sumdiv)) ))
            
        
    @QtCore.pyqtSlot() 
    def on_actionInversionEstudio_activated(self):
        w=frmInversionesEstudio(self.cfg, self.selInversion, self)
        w.exec_()
        
            
    @QtCore.pyqtSlot() 
    def on_actionMyStocks_activated(self):
        w=frmAnalisis(self.cfg, self.selInversion.investment, self.selInversion, self)
        w.load_data_from_db()
        w.exec_()
                    
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

