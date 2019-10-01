from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget, QDialog, QVBoxLayout
from datetime import datetime
from decimal import Decimal
from logging import error
from pytz import timezone
from xulpymoney.ui.wdgOrdersAdd import wdgOrdersAdd
from xulpymoney.libxulpymoney import InvestmentOperation, Money, Percentage,  Quote
from xulpymoney.libxulpymoneyfunctions import qmessagebox
from xulpymoney.ui.Ui_wdgDisReinvest import Ui_wdgDisReinvest
from xulpymoney.ui.wdgProductHistoricalChart import wdgProductHistoricalReinvestChart

class wdgDisReinvest(QWidget, Ui_wdgDisReinvest):
    ## @param allProduct true, make study with all active investments  of the product
    def __init__(self, mem, inversion,  allProduct=False,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem            

        if allProduct==False:
            self.investment=inversion
        else:
            self.investment=self.mem.data.investments_active().Investment_merging_current_operations_with_same_product(inversion.product)

        self.txtValorAccion.setText(self.investment.product.result.basic.last.quote)
        self.txtSimulacion.setText(Decimal(self.mem.settingsdb.value("wdgIndexRange/invertir", "10000")))
        self.tabOps.setCurrentIndex(1)

        self.tblOps.settings(self.mem, "wdgDisReinvest")
        self.tblCurrentOps.settings(self.mem, "wdgDisReinvest")
        
        if self.investment.op_actual.length()==0:
            qmessagebox(self.tr("There aren't shares for this investment"))
            return
        
        self.on_radRe_clicked()

    def shares(self):
        resultado=Decimal(0)
        
        if self.radDes.isChecked():#DESINVERSION
            perdida=Money(self.mem, self.txtSimulacion.decimal(),self.investment.product.currency)#Va disminuyendo con las distintas operaciones
            q=Quote(self.mem).init__create(self.investment.product, datetime.now(timezone(self.mem.localzone_name)), self.txtValorAccion.decimal())
            for rec in self.investment.op_actual.arr:
                pendiente=rec.pendiente(q)
                if (perdida+pendiente).isZero():
                    resultado=resultado+rec.shares
                    break
                elif (perdida+pendiente).isGTZero():
                    resultado=resultado+rec.shares
                    perdida=perdida+pendiente
                elif (perdida+pendiente).isLTZero():
                    # Si de tantas acciones queda pendiente "pendiente"
                    # X                                queda la perdida
                    acciones=abs(int(perdida.amount*rec.shares/pendiente.amount))
                    resultado=resultado+Decimal(acciones)#Se resta porque se debe calcular antes de quitarse el pendiente
                    break
        else:#REINVERSION
            resultado=Decimal(int(self.txtSimulacion.decimal()/self.txtValorAccion.decimal()))
        return resultado
            
    @pyqtSlot() 
    def on_radDes_clicked(self):
        self.lblTitulo.setText(self.tr("Divest simulation of {0}").format(self.investment.name))
        self.lblSimulacion.setText(self.tr("Divest loss to asume"))
        self.lblValor.setText(self.tr("Selling price (Current: {})").format(self.investment.product.currency.string(self.investment.product.result.basic.last.quote)))
        self.cmdOrder.setEnabled(False)
        
    @pyqtSlot() 
    def on_radRe_clicked(self):
        self.lblTitulo.setText(self.tr("Reinvest simulation of {0}").format(self.investment.name))
        self.lblSimulacion.setText(self.tr("Amount to reinvest"))
        self.lblValor.setText(self.tr("Purchase price (Current: {})").format(self.investment.product.currency.string(self.investment.product.result.basic.last.quote)))
        self.cmdOrder.setEnabled(False)
   
    def on_cmd_released(self):
        self.investment_simulated=self.investment.Investment_At_Datetime(self.mem.localzone.now())       

        if self.txtSimulacion.decimal()<=Decimal('0'):
            qmessagebox(self.tr("Simulation value must be positive"))
            return
            
        valor_accion=self.txtValorAccion.decimal()
        impuestos=0
        comision=self.txtComision.decimal()
        
        if valor_accion==0:
            qmessagebox(self.tr("Share price can't be 0"))
            return
        
        acciones=self.shares()
        importe=valor_accion*acciones
        self.txtAcciones.setText(acciones)
        self.txtImporte.setText(importe)

        error("Factor de conversion no siempre es 1")
        currency_conversion=1

        #Creamos un nuevo operinversiones 
        id_operinversiones=self.investment_simulated.op.get_highest_io_id ()+1##Para simular un id_operinversiones real, le asignamos uno
        if self.radDes.isChecked():#DESINVERSION
            d=InvestmentOperation(self.mem).init__create(self.mem.tiposoperaciones.find_by_id(5), datetime.now(timezone(self.mem.localzone_name)), self.investment, -acciones, impuestos, comision, valor_accion, "",  True, currency_conversion,  id_operinversiones)
        else:#REINVERSION
            d=InvestmentOperation(self.mem).init__create(self.mem.tiposoperaciones.find_by_id(4), datetime.now(timezone(self.mem.localzone_name)), self.investment, acciones, impuestos, comision, valor_accion, "",  True, currency_conversion,  id_operinversiones)
        self.investment_simulated.op.append(d)
        (self.investment_simulated.op_actual, self.investment_simulated.op_historica)=self.investment_simulated.op.get_current_and_historical_operations()
        
        self.cmbPrices_reload()
        
        self.cmdOrder.setEnabled(True)
        self.cmdGraph.setEnabled(True)

    @pyqtSlot()
    def on_cmdGraph_released(self):
        self.investment.product.needStatus(2)
        d=QDialog(self)     
        d.setWindowTitle(self.tr("Reinvest graph"))
        d.showMaximized()
        lay = QVBoxLayout(d)
        
        wc=wdgProductHistoricalReinvestChart()
        wc.setProduct(self.investment.product, self.investment)
        wc.setReinvest( self.investment_simulated.op, self.investment_simulated.op_actual)
        
        lay.addWidget(wc)
        wc.generate()
        wc.display()
        
        d.exec_()

    @pyqtSlot()
    def on_cmdOrder_released(self):
        d=QDialog(self)     
        d.setModal(True)
        d.setWindowTitle(self.tr("Add new order"))
        w=wdgOrdersAdd(self.mem, None, self.investment, d)
        w.txtShares.setText(self.txtAcciones.decimal())
        if self.radDes.isChecked():#DESINVERSION
            w.txtPrice.setText(-self.txtValorAccion.decimal())
        else:#REINVERSION
            w.txtPrice.setText(self.txtValorAccion.decimal())
        lay = QVBoxLayout(d)
        lay.addWidget(w)
        d.exec_()

    ## This function is created because self.cmbPrices.setCurrentIndex(1) wouldn't create prices
    ## @param is the selected index after reload
    def cmbPrices_reload(self):
        if self.cmbPrices.currentIndex()>=0:
            index=self.cmbPrices.currentIndex()
        else:
            index=9
        
        #quotes
        quote_current=self.investment.product.result.basic.last
        quote_simulation=Quote(self.mem).init__create(self.investment.product, datetime.now(), self.txtValorAccion.decimal())
        moneybefore_0=self.investment.op_actual.average_price()
        quotebefore_0=Quote(self.mem).init__create(self.investment.product, datetime.now(), moneybefore_0.amount)
        moneybefore_2_5=self.investment.op_actual.average_price_after_a_gains_percentage(Percentage(2.5, 100))
        quotebefore_2_5=Quote(self.mem).init__create(self.investment.product, datetime.now(), moneybefore_2_5.amount)
        moneybefore_5=self.investment.op_actual.average_price_after_a_gains_percentage(Percentage(5, 100))
        quotebefore_5=Quote(self.mem).init__create(self.investment.product, datetime.now(), moneybefore_5.amount)
        moneybefore_7_5=self.investment.op_actual.average_price_after_a_gains_percentage(Percentage(7.5, 100))
        quotebefore_7_5=Quote(self.mem).init__create(self.investment.product, datetime.now(), moneybefore_7_5.amount)
        moneybefore_10=self.investment.op_actual.average_price_after_a_gains_percentage(Percentage(10, 100))
        quotebefore_10=Quote(self.mem).init__create(self.investment.product, datetime.now(), moneybefore_10.amount)
        moneyafter_0=self.investment_simulated.op_actual.average_price()
        quoteafter_0=Quote(self.mem).init__create(self.investment.product, datetime.now(), moneyafter_0.amount)
        moneyafter_2_5=self.investment_simulated.op_actual.average_price_after_a_gains_percentage(Percentage(2.5, 100))
        quoteafter_2_5=Quote(self.mem).init__create(self.investment.product, datetime.now(), moneyafter_2_5.amount)
        moneyafter_5=self.investment_simulated.op_actual.average_price_after_a_gains_percentage(Percentage(5, 100))
        quoteafter_5=Quote(self.mem).init__create(self.investment.product, datetime.now(), moneyafter_5.amount)
        moneyafter_7_5=self.investment_simulated.op_actual.average_price_after_a_gains_percentage(Percentage(7.5, 100))
        quoteafter_7_5=Quote(self.mem).init__create(self.investment.product, datetime.now(), moneyafter_7_5.amount)
        moneyafter_10=self.investment_simulated.op_actual.average_price_after_a_gains_percentage(Percentage(10, 100))
        quoteafter_10=Quote(self.mem).init__create(self.investment.product, datetime.now(), moneyafter_10.amount)
        
        #Combobox update
        self.cmbPrices.blockSignals(True)
        self.cmbPrices.clear()
        self.cmbPrices.addItem(self.tr("Before simulation: current price ({})").format(quote_current.money()))
        self.cmbPrices.addItem(self.tr("Before simulation: simulation price ({})").format(quote_simulation.money()))
        self.cmbPrices.addItem(self.tr("Before simulation: selling price to gain 0 % ({})").format(moneybefore_0))
        self.cmbPrices.addItem(self.tr("Before simulation: selling price to gain 2.5 % ({})").format(moneybefore_2_5))
        self.cmbPrices.addItem(self.tr("Before simulation: selling price to gain 5.0 % ({})").format(moneybefore_5))
        self.cmbPrices.addItem(self.tr("Before simulation: selling price to gain 7.5 % ({})").format(moneybefore_7_5))
        self.cmbPrices.addItem(self.tr("Before simulation: selling price to gain 10.0 % ({})").format(moneybefore_10))
        self.cmbPrices.insertSeparator(7);
        self.cmbPrices.addItem(self.tr("After simulation: current price ({})").format(quote_current.money()))
        self.cmbPrices.addItem(self.tr("After simulation: simulation price ({})").format(quote_simulation.money()))
        self.cmbPrices.addItem(self.tr("After simulation: selling price to gain 0 % ({})").format(moneyafter_0))
        self.cmbPrices.addItem(self.tr("After simulation: selling price to gain 2.5 % ({})").format(moneyafter_2_5))
        self.cmbPrices.addItem(self.tr("After simulation: selling price to gain 5.0 % ({})").format(moneyafter_5))
        self.cmbPrices.addItem(self.tr("After simulation: selling price to gain 7.5 % ({})").format(moneyafter_7_5))
        self.cmbPrices.addItem(self.tr("After simulation: selling price to gain 10.0 % ({})").format(moneyafter_10))
        self.cmbPrices.setCurrentIndex(index)
        self.cmbPrices.blockSignals(False)

        #Show tables
        if index==0:#Before current price
            self.investment.op.myqtablewidget(self.tblOps, quote_current)
            self.investment.op_actual.myqtablewidget(self.tblCurrentOps, quote_current)
        elif index==1:# Before simulation simulation price
            self.investment.op.myqtablewidget(self.tblOps, quote_simulation)
            self.investment.op_actual.myqtablewidget(self.tblCurrentOps, quote_simulation)
        elif index==2:# Before current price to gain 0
            self.investment.op.myqtablewidget(self.tblOps, quotebefore_0)
            self.investment.op_actual.myqtablewidget(self.tblCurrentOps, quotebefore_0)
        elif index==3:# Before current price to gain 2.5%
            self.investment.op.myqtablewidget(self.tblOps, quotebefore_2_5)
            self.investment.op_actual.myqtablewidget(self.tblCurrentOps, quotebefore_2_5)
        elif index==4:# Before current price to gain 5%
            self.investment.op.myqtablewidget(self.tblOps, quotebefore_5)
            self.investment.op_actual.myqtablewidget(self.tblCurrentOps, quotebefore_5)
        elif index==5:# Before current price to gain 7.5%
            self.investment.op.myqtablewidget(self.tblOps, quotebefore_7_5)
            self.investment.op_actual.myqtablewidget(self.tblCurrentOps, quotebefore_7_5)
        elif index==6:# Before current price to gain 10%
            self.investment.op.myqtablewidget(self.tblOps, quotebefore_10)
            self.investment.op_actual.myqtablewidget(self.tblCurrentOps, quotebefore_10)
        elif index==8:# After current price
            self.investment_simulated.op.myqtablewidget(self.tblOps, quote_current)
            self.investment_simulated.op_actual.myqtablewidget(self.tblCurrentOps, quote_current)
        elif index==9:# After simulation price
            self.investment_simulated.op.myqtablewidget(self.tblOps, quote_simulation)
            self.investment_simulated.op_actual.myqtablewidget(self.tblCurrentOps, quote_simulation)
        elif index==10:# After current price to gain 0
            self.investment_simulated.op.myqtablewidget(self.tblOps, quoteafter_0)
            self.investment_simulated.op_actual.myqtablewidget(self.tblCurrentOps, quoteafter_0)
        elif index==11:# After current price to gain 2.5%
            self.investment_simulated.op.myqtablewidget(self.tblOps, quoteafter_2_5)
            self.investment_simulated.op_actual.myqtablewidget(self.tblCurrentOps, quoteafter_2_5)
        elif index==12:# After current price to gain 5%
            self.investment_simulated.op.myqtablewidget(self.tblOps, quoteafter_5)
            self.investment_simulated.op_actual.myqtablewidget(self.tblCurrentOps, quoteafter_5)
        elif index==13:# After current price to gain 7.5%
            self.investment_simulated.op.myqtablewidget(self.tblOps, quoteafter_7_5)
            self.investment_simulated.op_actual.myqtablewidget(self.tblCurrentOps, quoteafter_7_5)
        elif index==14:# After current price to gain 10%
            self.investment_simulated.op.myqtablewidget(self.tblOps, quoteafter_10)
            self.investment_simulated.op_actual.myqtablewidget(self.tblCurrentOps, quoteafter_10)

    @pyqtSlot(int) 
    def on_cmbPrices_currentIndexChanged(self, index):
        self.cmbPrices_reload()

