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
        type=2
        if self.chkPonderanAll.checkState()==Qt.Checked:#Results are in self.mem.localcurrency
            self.operinversiones=self.mem.data.investments_active().investment_merging_current_operations_with_same_product(self.inversion.product).op_actual
            self.operinversiones.myqtablewidget(self.table)
            suminvertido=self.operinversiones.invertido()
        else:#Results in account currency
            self.operinversiones=SetInvestmentOperationsCurrentHomogeneus(self.mem, self.inversion)
            if self.chkGainsTime.checkState()==Qt.Checked:
                self.operinversiones=self.inversion.op_actual.copy_until_datetime(self.mem.localzone.now()-datetime.timedelta(days=365))
            else:
                self.operinversiones=self.inversion.op_actual.copy_until_datetime(None)
            self.operinversiones.myqtablewidget(self.table, self.inversion.product.result.basic.last,  type)
            suminvertido=self.operinversiones.invertido(type)
        sumacciones=self.operinversiones.acciones()
        
        if sumacciones==Decimal(0):
            self.puntoventa=Money(self.mem, 0, self.inversion.account.currency)
        else:
            if self.radTPC.isChecked()==True:
                tpc=Decimal(self.cmbTPC.currentText().replace(" %", ""))
                self.puntoventa=Money(self.mem, suminvertido.amount*(1+tpc/100)/sumacciones, self.inversion.account.currency)
            elif self.radPrice.isChecked()==True:
                if self.txtPrice.isValid():#Si hay un numero bien
                    self.puntoventa=Money(self.mem,  self.txtPrice.decimal(),  self.inversion.account.currency)
                    self.cmd.setEnabled(True)
                else:
                    self.puntoventa=Money(self.mem, 0, self.inversion.account.currency)
                    self.cmd.setEnabled(False)
            elif self.radGain.isChecked()==True:
                if self.txtGanancia.isValid():#Si hay un numero bien
                    self.puntoventa=Money(self.mem, (self.txtGanancia.decimal()+suminvertido.amount)/sumacciones, self.inversion.account.currency)
                    self.cmd.setEnabled(True)
                else:
                    self.puntoventa=Money(self.mem, 0, self.inversion.account.currency)
                    self.cmd.setEnabled(False)
            elif self.radSMA200.isChecked()==True:
                self.puntoventa=Money(self.mem, suminvertido.amount*(1+self.tpcsma200/100)/sumacciones, self.inversion.account.currency)

        if self.inversion.hasSameAccountCurrency()==False:
            #punto de venta tiene el currency de la acount luego hay que pasarlo al currency de la inversi´on_chkGainsTime_stateChanged
            self.puntoventa=self.puntoventa.convert(self.inversion.product.currency, self.mem.localzone.now())


        quote=Quote(self.mem).init__create(self.inversion.product, self.mem.localzone.now(), self.puntoventa.amount)
        self.tab.setTabText(1, self.tr("Selling point: {0}".format(self.puntoventa)))
        self.tab.setTabText(0, self.tr("Current state: {0}".format(self.inversion.product.currency.string(self.inversion.product.result.basic.last.quote))) )
        self.operinversiones.myqtablewidget(self.tableSP, quote, type) 
        
        if self.chkPonderanAll.checkState()==Qt.Checked:
            self.cmd.setText(self.tr("Set selling price to all investments  of {0} to gain {1}").format(self.puntoventa, self.operinversiones.pendiente(quote, type)))
        else:
            self.cmd.setText(self.tr("Set {0} shares selling price to {1} to gain {2}").format(sumacciones, self.puntoventa, self.operinversiones.pendiente(quote, type)))

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
            for inv in self.mem.data.investments_active().arr:
                if inv.product.id==self.inversion.product.id:
                    inv.venta=self.puntoventa.amount
                    inv.save()
            self.mem.con.commit()
        
        #Save in settings the last selling percentage, if that's the case
        if self.radTPC.isChecked():
            percentage=Decimal(self.cmbTPC.currentText().replace(" %", ""))
            self.mem.settingsdb.setValue("frmSellingPoint/lastgainpercentage", percentage)
        self.done(0)
