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
            m.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
            m.setIcon(QMessageBox.Information)
            m.setText(self.tr("You can't set a selling price to a unsaved investment"))
            m.exec_()     
            return
        if len(self.inversion.op_actual.arr)==0:
            m=QMessageBox()
            m.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
            m.setIcon(QMessageBox.Information)
            m.setText(self.tr("You don't have shares to sale in this investment"))
            m.exec_()     
            return
        
        inicio=datetime.datetime.now()
        self.mem.data.benchmark.result.get_basic_and_ohcls()
        print("Load",  datetime.datetime.now()-inicio)
        setdv=self.mem.data.benchmark.result.ohclDaily.close_to_setdv()
        print  (setdv.average())
        self.tpcsma200=setdv.tpc_to_last_sma200(self.mem.data.benchmark.result.basic.last.quote)
        print("Setdv y sma",  datetime.datetime.now()-inicio)
        self.txtSMA200.setText(tpc(self.tpcsma200))
        if self.tpcsma200<Decimal(2.5):
            self.radSMA200.setEnabled(False)
        
        
        self.puntoventa=Decimal(0)#Guarda el resultado de los cálculos
        self.operinversiones=None 

        if self.mem.gainsyear==True:
            self.chkGainsTime.setCheckState(Qt.Checked)
        else:
            self.chkGainsTime.setEnabled(False)



        self.table.settings(self.mem, "frmSellingPoint")
        self.tableSP.settings(self.mem, "frmSellingPoint")
        
        self.cmbTPC.setCurrentText("{} %".format(self.mem.settingsdb.value("frmSellingPoint/lastgainpercentage",  5)))
        
    def __calcular(self):    
        def load_array():
            if self.chkPonderanAll.checkState()==Qt.Checked:#Ponderan misma inversion
                for  inv in self.mem.data.investments_active().arr:
                    if inv.product.id==self.inversion.product.id:
                        for op in inv.op_actual.arr:
                            self.operinversiones.append(op)                
            else:# No ponderan misma inversion
                self.operinversiones=self.inversion.op_actual.clone()
                
            #Quita operaciones menos de un año si a lugar
            if self.chkGainsTime.checkState()==Qt.Checked:
                for o in self.operinversiones.arr:
                    if o.less_than_a_year()==True:
                        self.operinversiones.remove(o)
        ###########################
        self.operinversiones=SetInvestmentOperationsCurrentHomogeneus(self.mem, self.inversion)
        load_array()
        self.operinversiones.order_by_datetime()
        (sumacciones, suminvertido, sumpendiente)=self.operinversiones.myqtablewidget(self.table, True, self.inversion.product.result.basic.last)
        
        if sumacciones==0:
            self.puntoventa=0
        else:
            if self.radTPC.isChecked()==True:
                tpc=Decimal(self.cmbTPC.currentText().replace(" %", ""))
                self.puntoventa=round(suminvertido.amount*(1+tpc/100)/sumacciones, 2)
            elif self.radPrice.isChecked()==True:
                if self.txtPrice.isValid():#Si hay un numero bien
                    self.puntoventa=self.txtPrice.decimal()
                    self.cmd.setEnabled(True)
                else:
                    self.puntoventa=Decimal(0)
                    self.cmd.setEnabled(False)
            elif self.radGain.isChecked()==True:
                if self.txtGanancia.isValid():#Si hay un numero bien
                    self.puntoventa=round((self.txtGanancia.decimal()+suminvertido.amount)/sumacciones, 2)
                    self.cmd.setEnabled(True)
                else:
                    self.puntoventa=Decimal(0)
                    self.cmd.setEnabled(False)
            elif self.radSMA200.isChecked()==True:
                self.puntoventa=round(suminvertido.amount*(1+self.tpcsma200/100)/sumacciones, 2)

        self.tab.setTabText(1, self.tr("Selling point: {0}".format(self.inversion.product.currency.string(self.puntoventa))) )
        self.tab.setTabText(0, self.tr("Current state: {0}".format(self.inversion.product.currency.string(self.inversion.product.result.basic.last.quote))) )
        (sumacciones, suminvertido, sumpendiente)=self.operinversiones.myqtablewidget(self.tableSP, True, Quote(self.mem).init__create(self.inversion.product, self.mem.localzone.now(), self.puntoventa)) 
        
        if self.chkPonderanAll.checkState()==Qt.Checked:
            self.cmd.setText(self.tr("Set selling price to all investments  of {0} to gain {1}").format(self.inversion.product.currency.string(self.puntoventa), sumpendiente))
        else:
            self.cmd.setText(self.tr("Set {0} shares selling price to {1} to gain {2}").format(sumacciones, self.inversion.product.currency.string(self.puntoventa), sumpendiente))

    def on_radTPC_clicked(self):
        self.__calcular()
        
    def on_radPrice_clicked(self):
        self.__calcular()
        
    def on_radGain_clicked(self):
        self.__calcular()
        
    def on_radSMA200_clicked(self):
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
        
        #Save in settings the last selling percentage, if that's the case
        if self.radTPC.isChecked():
            percentage=Decimal(self.cmbTPC.currentText().replace(" %", ""))
            self.mem.settingsdb.setValue("frmSellingPoint/lastgainpercentage", percentage)
        
        self.done(0)
