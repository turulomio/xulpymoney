from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from Ui_frmSellingPoint import *
from libxulpymoney import *
from decimal import Decimal

class frmSellingPoint(QDialog, Ui_frmSellingPoint):
    def __init__(self, mem,  inversion ,   parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.showMaximized()
        self.mem=mem
        self.inversion=inversion
        
        if self.inversion.id==None:
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.tr("You can't set a selling price to a unsaved investment"))
            m.exec_()     
            return
        if len(self.inversion.op_actual.arr)==0:
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.tr("You don't have shares to sale in this investment"))
            m.exec_()     
            return
        
        self.puntoventa=Decimal(0)#Guarda el resultado de los cálculos
        self.operinversiones=[]            #0-fecha, 1-banco, 2-acciones, 3-valor-compra, 4-invertido, 5 pendiente, 6-tipooper


        if str2bool(self.mem.config.get_value("settings", "gainsyear"))==True:
            self.chkGainsTime.setCheckState(Qt.Checked)
        else:
            self.chkGainsTime.setEnabled(False)


        self.table.settings("frmSellingPoint",  self.mem)
        self.tableSP.settings("frmSellingPoint",  self.mem)
        self.__calcular()
        
    def __calcular(self):    
        def load_array():
            tmp=[]
            if self.chkPonderanAll.checkState()==Qt.Checked:#Ponderan misma inversion
                for  inv in self.mem.data.investments_active.arr:
                    if inv.product.id==self.inversion.product.id:
                        for op in inv.op_actual.arr:
                            tmp.append(op)                
            else:# No ponderan misma inversion
                tmp=list(self.inversion.op_actual.arr) 
                
            #Quita operaciones menos de un año si ha lugar
            if self.chkGainsTime.checkState()==Qt.Checked:
                for o in tmp:
                    if o.less_than_a_year()==False:
                        self.operinversiones.append(o)
            else:
                self.operinversiones=tmp
                
        def load_table(table, current_value):
            sumacciones=Decimal(0)
            suminvertido=Decimal(0)
            sumpendiente=Decimal(0)
            table.clearContents()
            table.setRowCount(len(self.operinversiones)+1)
            for i, rec in enumerate(self.operinversiones):
                sumacciones=sumacciones+rec.acciones
                suminvertido=suminvertido+rec.invertido()
                pendiente=rec.pendiente(current_value)
                sumpendiente=sumpendiente+pendiente
                table.setItem(i, 0, qdatetime(rec.datetime, rec.inversion.product.stockexchange.zone))
                table.setItem(i, 1, QTableWidgetItem("{0} ({1})".format(rec.inversion.name, rec.inversion.cuenta.eb.name)))
                table.setItem(i, 2,  QTableWidgetItem(rec.tipooperacion.name))
                table.setItem(i, 3, qright(str(rec.acciones)))
                table.setItem(i, 4, self.inversion.product.currency.qtablewidgetitem(rec.valor_accion))
                table.setItem(i, 5, self.inversion.product.currency.qtablewidgetitem(rec.importe))
                table.setItem(i, 6, self.inversion.product.currency.qtablewidgetitem(pendiente))
            table.setItem(len(self.operinversiones), 1, qright("Total"))        
            table.setItem(len(self.operinversiones), 3, qright(str(sumacciones)))
            if sumacciones!=0:
                table.setItem(len(self.operinversiones), 4, self.inversion.product.currency.qtablewidgetitem(suminvertido/sumacciones))
            table.setItem(len(self.operinversiones), 5, self.inversion.product.currency.qtablewidgetitem(suminvertido))
            table.setItem(len(self.operinversiones), 6, self.inversion.product.currency.qtablewidgetitem(sumpendiente))
            return (sumacciones, suminvertido, sumpendiente)
        ###########################
        del self.operinversiones
        self.operinversiones=[]
        load_array()
        (sumacciones, suminvertido, sumpendiente)=load_table(self.table, self.inversion.product.result.basic.last)
        
        if sumacciones==0:
            self.puntoventa=0
        else:
            if self.radTPC.isChecked()==True:
                tpc=Decimal(self.cmbTPC.currentText().replace(" %", ""))
                self.puntoventa=round(suminvertido*(1+tpc/100)/sumacciones, 2)
            elif self.radPrice.isChecked()==True:
                if self.txtPrice.isValid():#Si hay un numero bien
                    self.puntoventa=Decimal(self.txtPrice.text())
                    self.cmd.setEnabled(True)
                else:
                    self.puntoventa=0
                    self.cmd.setEnabled(False)
            elif self.radGain.isChecked()==True:
                if self.txtGanancia.isValid():#Si hay un numero bien
                    self.puntoventa=round((self.txtGanancia.decimal()+suminvertido)/sumacciones, 2)
                    self.cmd.setEnabled(True)
                else:
                    self.puntoventa=0
                    self.cmd.setEnabled(False)

        self.tab.setTabText(1, self.tr("Selling point: {0}".format(self.inversion.product.currency.string(self.puntoventa))) )
        self.tab.setTabText(0, self.tr("Current state: {0}".format(self.inversion.product.currency.string(self.inversion.product.result.basic.last.quote))) )
        (sumacciones, suminvertido, sumpendiente)=load_table(self.tableSP, Quote(self.mem).init__create(self.inversion.product, self.mem.localzone.now(), self.puntoventa))                    
        
        if self.chkPonderanAll.checkState()==Qt.Checked:
            self.cmd.setText(self.tr("Set selling price to all investments  of {0} to gain {1}").format(self.inversion.product.currency.string(self.puntoventa), self.inversion.product.currency.string(sumpendiente)))
        else:
            self.cmd.setText(self.tr("Set {0} shares selling price to {1} to gain {2}").format(sumacciones, self.inversion.product.currency.string(self.puntoventa), self.inversion.product.currency.string(sumpendiente)))

    def on_radTPC_clicked(self):
        self.__calcular()
        
    def on_radPrice_clicked(self):
        self.__calcular()
        
    def on_radGain_clicked(self):
        self.__calcular()
        
    @QtCore.pyqtSlot(str) 
    def on_cmbTPC_currentIndexChanged(self, cur):
        self.__calcular()
        
    def on_txtGanancia_textChanged(self):
        self.__calcular()
        
    def on_txtPrice_textChanged(self):
        self.__calcular()
        
    def on_chkPonderanAll_stateChanged(self, state):
        self.__calcular()
        
    def on_chkGainsTime_stateChanged(self, state):
        self.__calcular()

    @QtCore.pyqtSlot() 
    def on_cmd_released(self):
        if self.chkPonderanAll.checkState()==Qt.Checked:
            invs=set()#Solo un save por inversion
            for o in self.operinversiones:
                if o.inversion not in invs:
                    invs.add(o.inversion)
            print (list(invs))
            for inv in list(invs):
                inv.venta=self.puntoventa
                inv.save()
            self.mem.con.commit()
        self.done(0)
