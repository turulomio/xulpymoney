from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Ui_frmPuntoVenta import *
from libxulpymoney import *
from decimal import Decimal

class frmPuntoVenta(QDialog, Ui_frmPuntoVenta):
    def __init__(self, cfg, inversion ,   parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.cfg=cfg
        self.inversion=inversion
        
        if len(self.inversion.op_actual.arr)==0:
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.trUtf8("Actualmente no hay acciones disponibles en esta Inversión"))
            m.exec_()     
            return
        
        self.puntoventa=0#Guarda el resultado de los cálculos
        self.operinversiones=list(self.inversion.op_actual.arr)            #0-fecha, 1-banco, 2-acciones, 3-valor-compra, 4-invertido, 5 pendiente, 6-tipooper
        self.txtGanancia.setValidator(QDoubleValidator(self))
        self.table.settings("frmPuntoVenta",  self.cfg.file_ui)
        self.on_radTPC_toggled(True)
        
    def __calcular(self):
        sumacciones=0
        suminvertido=0
        self.table.setRowCount(len(self.operinversiones)+1)
        for i, rec in enumerate(self.operinversiones):
            if self.chkPonderanAdded.checkState()==Qt.Checked:
                sumacciones=sumacciones+rec.acciones
                suminvertido=suminvertido+rec.invertido()
            elif rec.tipooperacion.id!=6:
                    sumacciones=sumacciones+rec.acciones
                    suminvertido=suminvertido+rec.importe
            self.table.setItem(i, 0, qdatetime(rec.datetime, rec.inversion.investment.bolsa.zone))
            self.table.setItem(i, 1, QTableWidgetItem("{0} ({1})".format(rec.inversion.name, rec.inversion.cuenta.eb.name)))
            self.table.setItem(i, 2,  QTableWidgetItem(rec.tipooperacion.name))
            self.table.setItem(i, 3, qright(str(rec.acciones)))
            self.table.setItem(i, 4, self.inversion.investment.currency.qtablewidgetitem(rec.valor_accion))
            self.table.setItem(i, 5, self.inversion.investment.currency.qtablewidgetitem(rec.importe))
            self.table.setItem(i, 6, self.inversion.investment.currency.qtablewidgetitem(rec.pendiente(self.inversion.investment.quotes.last)))
        self.table.setItem(len(self.operinversiones), 1, qright("Total"))        
        self.table.setItem(len(self.operinversiones), 3, qright(str(sumacciones)))
        self.table.setItem(len(self.operinversiones), 4, self.inversion.investment.currency.qtablewidgetitem(suminvertido/sumacciones))
        self.table.setItem(len(self.operinversiones), 5, self.inversion.investment.currency.qtablewidgetitem(suminvertido))
            
        if sumacciones==0:
            self.puntoventa=0
        else:
            
            if self.radTPC.isChecked()==True:
                tpc=Decimal(self.cmbTPC.currentText().replace(" %", ""))
                self.puntoventa=round(suminvertido*(1+tpc/100)/sumacciones, 2)
            else:
                self.puntoventa=round((Decimal(self.txtGanancia.text())+suminvertido)/sumacciones, 2)
        self.cmd.setText("Asignar el punto de venta de {0} € para ganar {1} €".format(self.puntoventa, round(sumacciones*self.puntoventa-suminvertido, 2)))
        
    def load_operinversionesactualmismoactivo(self):
        """Recibe un sql y calcula las operinversiones, pueden ser de diferentes inversiones"""
        arr=[]
        for  inv in self.cfg.inversiones_activas():
            if inv.investment.id==self.inversion.investment.id:
                for op in inv.op_actual.arr:
                    arr.append(op)
        return arr

    def on_radTPC_toggled(self, toggle):
        self.cmbTPC.setEnabled(toggle)
        if toggle==True:
            self.chkPonderanAdded.setCheckState(Qt.Checked)
        print ("toggled")
        self.__calcular()
        
    @QtCore.pyqtSlot(str) 
    def on_cmbTPC_currentIndexChanged(self, cur):
        self.__calcular()
        
    def on_txtGanancia_textChanged(self):
        self.__calcular()
    
    def on_chkPonderanAdded_stateChanged(self, state):
        self.__calcular()
        
    def on_chkPonderanAll_stateChanged(self, state):
        if state==Qt.Checked:
            self.operinversiones=self.load_operinversionesactualmismoactivo()
        else:
            self.operinversiones=list(self.inversion.op_actual.arr) 
        self.__calcular()

                
    @QtCore.pyqtSlot() 
    def on_cmd_released(self):
        self.done(0)
