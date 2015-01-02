from PyQt4.QtCore import *
from PyQt4.QtGui import *
import datetime
from libxulpymoney import *
from Ui_wdgDividendsReport import *
from frmInvestmentReport import *
from frmProductReport import *
from frmEstimationsAdd import *

class wdgDividendsReport(QWidget, Ui_wdgDividendsReport):
    def __init__(self, mem,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        self.inversiones=[]

        self.tblInvestments.settings("wdgDividendsReport",  self.mem)
        
        self.on_chkInactivas_stateChanged(Qt.Unchecked)

    @QtCore.pyqtSlot()  
    def on_actionEstimationDPSEdit_activated(self):
        d=frmEstimationsAdd(self.mem, self.selInvestment.product, "dps")
        d.exec_()
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())
        self.tblInvestments.clearSelection()

    def on_chkInactivas_stateChanged(self,  state):               
        if state==Qt.Checked:
            self.mem.data.load_inactives()
            self.inversiones=self.mem.data.investments_inactive
        else:
            self.inversiones=self.mem.data.investments_active
        self.load_inversiones()
        
    def load_inversiones(self):    
        self.inversiones.order_by_percentage()#Se ordena self.inversiones.arr
        
        self.tblInvestments.clearContents()
        self.tblInvestments.setRowCount(len(self.inversiones.arr));
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
            
            self.tblInvestments.setItem(i, 0,QTableWidgetItem(inv.name))
            self.tblInvestments.setItem(i, 1, QTableWidgetItem(inv.cuenta.eb.name))
            self.tblInvestments.setItem(i, 2, inv.product.currency.qtablewidgetitem(inv.product.result.basic.last.quote))
            self.tblInvestments.setItem(i, 3, inv.product.currency.qtablewidgetitem(dpa))    
            self.tblInvestments.setItem(i, 4, qright(str(inv.acciones())))
            sumdiv=sumdiv+divestimado
            self.tblInvestments.setItem(i, 5, inv.product.currency.qtablewidgetitem(divestimado))
            self.tblInvestments.setItem(i, 6, qtpc(tpc))
                
            #Colorea si está desactualizado
            if inv.product.estimations_dps.dias_sin_actualizar()>self.spin.value():
                self.tblInvestments.item(i, 3).setBackgroundColor(QColor(255, 146, 148))
        self.lblTotal.setText(self.trUtf8("If I keep this investment during a year, I'll get {0}").format( self.mem.localcurrency.string(sumdiv)))
            
        
    @QtCore.pyqtSlot() 
    def on_actionInvestmentReport_activated(self):
        w=frmInvestmentReport(self.mem, self.selInvestment, self)
        w.exec_()
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())

            
    @QtCore.pyqtSlot() 
    def on_actionProductReport_activated(self):
        w=frmProductReport(self.mem, self.selInvestment.product, self.selInvestment, self)
        w.exec_()
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())

                    
    def on_cmd_pressed(self):
        self.on_chkInactivas_stateChanged(self.chkInactivas.checkState())

    def on_tblInvestments_customContextMenuRequested(self,  pos):        
        menu=QMenu()
        menu.addAction(self.actionEstimationDPSEdit)
        menu.addSeparator()
        menu.addAction(self.actionInvestmentReport) 
        menu.addAction(self.actionProductReport)    
        menu.exec_(self.tblInvestments.mapToGlobal(pos))

    def on_tblInvestments_itemSelectionChanged(self):
        self.selInvestment=None
        for i in self.tblInvestments.selectedItems():#itera por cada item no row.
            self.selInvestment=self.inversiones.arr[i.row()]
        print ("Seleccionado: " +  str(self.selInvestment))

