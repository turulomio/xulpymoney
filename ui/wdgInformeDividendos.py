from PyQt4.QtCore import *
from PyQt4.QtGui import *
import datetime
from libxulpymoney import *
from Ui_wdgInformeDividendos import *
from frmInversionesEstudio import *
from frmAnalisis import *
from frmDividendoEstimacionIBM import *

class wdgInformeDividendos(QWidget, Ui_wdgInformeDividendos):
    def __init__(self, cfg,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.cfg=cfg
        self.inversiones=[]

        self.load_data_from_db()
        self.tblInversiones.settings("wdgInformeDividendos",  self.cfg.file_ui)
        
        self.on_chkInactivas_stateChanged(Qt.Unchecked)
        
        
            
    def load_data_from_db(self):
        inicio=datetime.datetime.now()
        self.indicereferencia=Investment(self.cfg).init__db(self.cfg.config.get("settings", "indicereferencia" ))
        self.indicereferencia.quotes.get_basic()
        self.data_ebs=SetEntidadesBancarias(self.cfg)
        self.data_ebs.load_from_db("select * from entidadesbancarias where eb_activa=true")
        self.data_cuentas=SetCuentas(self.cfg, self.data_ebs)
        self.data_cuentas.load_from_db("select * from cuentas where cu_activa=true")
        self.data_investments=SetInvestments(self.cfg)
        self.data_investments.load_from_db("select distinct(myquotesid) from inversiones where in_activa=true")
        self.data_inversiones=SetInversiones(self.cfg, self.data_cuentas, self.data_investments, self.indicereferencia)
        self.data_inversiones.load_from_db("select * from inversiones where in_activa=true")
        print("\n","Cargando data en wdgInversiones",  datetime.datetime.now()-inicio)

    @QtCore.pyqtSlot()  
    def on_actionModificarDPA_activated(self):
        d=frmDividendoEstimacionIBM(self.cfg, self.selInversion.investment)
        d.exec_()
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())
        self.tblInversiones.clearSelection()

    def on_chkInactivas_stateChanged(self,  state):               
        if state==Qt.Checked:
            self.inversiones=self.data_inversiones
        else:
            self.inversiones=self.data_inversiones
        self.load_inversiones()
        
    def load_inversiones(self):    
        self.inversiones.sort_by_tpc_dpa()#Se ordena self.inversiones.arr
        
        self.tblInversiones.clearContents()
        self.tblInversiones.setRowCount(len(self.inversiones.arr));
        sumdiv=Decimal(0)
        for i, inv in enumerate(self.inversiones.arr):
            if inv.investment.estimacionesdividendo.find(datetime.date.today().year)==None:
                dpa=0
                tpc=0
                divestimado=0
            else:
                dpa=inv.investment.estimacionesdividendo.currentYear().dpa
                tpc=inv.investment.estimacionesdividendo.currentYear().tpc_dpa()
                divestimado=inv.dividendo_bruto_estimado()
            
            self.tblInversiones.setItem(i, 0,QTableWidgetItem(inv.name))
            self.tblInversiones.setItem(i, 1, QTableWidgetItem(inv.cuenta.eb.name))
            self.tblInversiones.setItem(i, 2, inv.investment.currency.qtablewidgetitem(inv.investment.quotes.last.quote))
            self.tblInversiones.setItem(i, 3, inv.investment.currency.qtablewidgetitem(dpa))    
            self.tblInversiones.setItem(i, 4, qright(str(inv.acciones())))
            sumdiv=sumdiv+divestimado
            self.tblInversiones.setItem(i, 5, inv.investment.currency.qtablewidgetitem(divestimado))
            self.tblInversiones.setItem(i, 6, qtpc(tpc))
                
            #Colorea si está desactualizado
            if inv.investment.estimacionesdividendo.dias_sin_actualizar()>self.spin.value():
                self.tblInversiones.item(i, 3).setBackgroundColor(QColor(255, 146, 148))
        self.lblTotal.setText(self.trUtf8("Si mantuviera la inversión un año obtendría {0}".format( self.cfg.localcurrency.string(sumdiv)) ))
            
        
    @QtCore.pyqtSlot() 
    def on_actionInversionEstudio_activated(self):
        w=frmInversionesEstudio(self.cfg, self.data_cuentas, self.data_inversiones, self.data_investments, self.selInversion, self)
        w.exec_()
        
            
    @QtCore.pyqtSlot() 
    def on_actionMyStocks_activated(self):
        w=frmAnalisis(self.cfg, self.selInversion.investment, self)
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

