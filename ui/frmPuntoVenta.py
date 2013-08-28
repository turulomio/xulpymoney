from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Ui_frmPuntoVenta import *
from libxulpymoney import *
from decimal import Decimal

class frmPuntoVenta(QDialog, Ui_frmPuntoVenta):
    def __init__(self, cfg, setinversiones,  inversion ,   parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.showMaximized()
        self.cfg=cfg
        self.inversion=inversion
        self.cfg.data.inversiones_active=setinversiones
        self.ponderan_all_inversiones=[]
        
        if self.inversion.id==None:
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.trUtf8("No se puede asignar el punto de venta a una inversión no guardada"))
            m.exec_()     
            return
        if len(self.inversion.op_actual.arr)==0:
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.trUtf8("Actualmente no hay acciones disponibles en esta Inversión"))
            m.exec_()     
            return
        
        self.puntoventa=Decimal(0)#Guarda el resultado de los cálculos
        self.operinversiones=list(self.inversion.op_actual.arr)            #0-fecha, 1-banco, 2-acciones, 3-valor-compra, 4-invertido, 5 pendiente, 6-tipooper

        self.table.settings("frmPuntoVenta",  self.cfg)
        self.tableSP.settings("frmPuntoVenta",  self.cfg)
        self.on_radTPC_toggled(True)
        
    def __calcular(self):
        def load_table(table, current_value):
            sumacciones=Decimal(0)
            suminvertido=Decimal(0)
            sumpendiente=Decimal(0)
            table.setRowCount(len(self.operinversiones)+1)
            for i, rec in enumerate(self.operinversiones):
                sumacciones=sumacciones+rec.acciones
                suminvertido=suminvertido+rec.invertido()
                pendiente=rec.pendiente(current_value)
                sumpendiente=sumpendiente+pendiente
                table.setItem(i, 0, qdatetime(rec.datetime, rec.inversion.investment.bolsa.zone))
                table.setItem(i, 1, QTableWidgetItem("{0} ({1})".format(rec.inversion.name, rec.inversion.cuenta.eb.name)))
                table.setItem(i, 2,  QTableWidgetItem(rec.tipooperacion.name))
                table.setItem(i, 3, qright(str(rec.acciones)))
                table.setItem(i, 4, self.inversion.investment.currency.qtablewidgetitem(rec.valor_accion))
                table.setItem(i, 5, self.inversion.investment.currency.qtablewidgetitem(rec.importe))
                table.setItem(i, 6, self.inversion.investment.currency.qtablewidgetitem(pendiente))
            table.setItem(len(self.operinversiones), 1, qright("Total"))        
            table.setItem(len(self.operinversiones), 3, qright(str(sumacciones)))
            table.setItem(len(self.operinversiones), 4, self.inversion.investment.currency.qtablewidgetitem(suminvertido/sumacciones))
            table.setItem(len(self.operinversiones), 5, self.inversion.investment.currency.qtablewidgetitem(suminvertido))
            table.setItem(len(self.operinversiones), 6, self.inversion.investment.currency.qtablewidgetitem(sumpendiente))
            return (sumacciones, suminvertido, sumpendiente)
            
        (sumacciones, suminvertido, sumpendiente)=load_table(self.table, self.inversion.investment.result.basic.last)
        
        if sumacciones==0:
            self.puntoventa=0
        else:
            if self.radTPC.isChecked()==True:
                tpc=Decimal(self.cmbTPC.currentText().replace(" %", ""))
                self.puntoventa=round(suminvertido*(1+tpc/100)/sumacciones, 2)
            else:
                if self.txtGanancia.isValid():#Si hay un numero bien
                    self.puntoventa=round((self.txtGanancia.decimal()+suminvertido)/sumacciones, 2)
                    self.cmd.setEnabled(True)
                else:
                    self.puntoventa=0
                    self.cmd.setEnabled(False)

        (sumacciones, suminvertido, sumpendiente)=load_table(self.tableSP, Quote(self.cfg).init__create(self.inversion.investment, self.cfg.localzone.now(), self.puntoventa))                    
        
        if self.chkPonderanAll.checkState()==Qt.Checked:
            self.cmd.setText("Grabar el punto de venta a todas las inversiones de {0} € para ganar {1}".format(self.puntoventa, self.inversion.investment.currency.string(sumpendiente)))
        else:
            self.cmd.setText("Asignar el punto de venta de {0} € para ganar {1} €".format(self.puntoventa, self.inversion.investment.currency.string(sumpendiente)))
        
    def load_operinversionesactualmismoactivo(self):
        """Recibe un sql y calcula las operinversiones, pueden ser de diferentes inversiones"""
        arr=[]
        self.ponderan_all_inversiones=[]
        for  inv in self.cfg.data.inversiones_active.arr:
            if inv.investment.id==self.inversion.investment.id:
                self.ponderan_all_inversiones.append(inv)
                for op in inv.op_actual.arr:
                    arr.append(op)
        return arr

    def on_radTPC_toggled(self, toggle):
        self.cmbTPC.setEnabled(toggle)
        self.__calcular()
        
    @QtCore.pyqtSlot(str) 
    def on_cmbTPC_currentIndexChanged(self, cur):
        self.__calcular()
        
    def on_txtGanancia_textChanged(self):
        self.__calcular()
        
    def on_chkPonderanAll_stateChanged(self, state):
        if state==Qt.Checked:
            self.operinversiones=self.load_operinversionesactualmismoactivo()
        else:
            self.operinversiones=list(self.inversion.op_actual.arr) 
        self.__calcular()

                
    @QtCore.pyqtSlot() 
    def on_cmd_released(self):
        if self.chkPonderanAll.checkState()==Qt.Checked:
            for inv in self.ponderan_all_inversiones:
                inv.venta=self.puntoventa
                inv.save()
            self.cfg.con.commit()
        self.done(0)
