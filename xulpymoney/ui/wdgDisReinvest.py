import datetime
import logging
import pytz
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget, QDialog, QVBoxLayout
from xulpymoney.ui.Ui_wdgDisReinvest import Ui_wdgDisReinvest
from xulpymoney.libxulpymoney import InvestmentOperation, Money, Percentage,  Quote
from xulpymoney.libxulpymoneyfunctions import qmessagebox
from xulpymoney.ui.wdgOrdersAdd import wdgOrdersAdd
from decimal import Decimal
from xulpymoney.ui.wdgProductHistoricalChart import wdgProductHistoricalReinvestChart

class wdgDisReinvest(QWidget, Ui_wdgDisReinvest):
    def __init__(self, mem, inversion,  allProduct=False,  parent=None):
        """
            Parameter allProduct true, make study with all active investments  of the product
        """
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem            

        if allProduct==False:
            self.investment=inversion
        else:
            self.investment=self.mem.data.investments_active().investment_merging_current_operations_with_same_product(inversion.product)
            
                
        self.txtValorAccion.setText(self.investment.product.result.basic.last.quote)
        self.txtSimulacion.setText(Decimal(self.mem.settingsdb.value("wdgIndexRange/invertir", "10000")))
        self.tabOpAcHi.setCurrentIndex(1)
        
        self.tblGainsAfter.settings(self.mem, "wdgDisReinvest")
        self.tblGainsBefore.settings(self.mem, "wdgDisReinvest")
        self.tblInvestmentsActualDespues.settings(self.mem, "wdgDisReinvest")
        self.tblInvestmentsActualDespuesAt.settings(self.mem, "wdgDisReinvest")
        self.tblInvestmentsActualAntesAt.settings(self.mem, "wdgDisReinvest")
        self.tblInvestmentsActualAntes.settings(self.mem, "wdgDisReinvest")
        self.tblInvestmentsHistoricas.settings(self.mem, "wdgDisReinvest")
        self.tblOperaciones.settings(self.mem, "wdgDisReinvest")
        
        if self.investment.op_actual.length()==0:
            qmessagebox(self.tr("There aren't shares for this investment"))
            return
            
        self.investment.op_actual.myqtablewidget(self.tblInvestmentsActualAntes)
        self.on_radRe_clicked()

    def shares(self):
        resultado=Decimal(0)
        
        if self.radDes.isChecked():#DESINVERSION
            perdida=Money(self.mem, self.txtSimulacion.decimal(),self.investment.product.currency)#Va disminuyendo con las distintas operaciones
            q=Quote(self.mem).init__create(self.investment.product, datetime.datetime.now(pytz.timezone(self.mem.localzone.name)), self.txtValorAccion.decimal())
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
        self.tabAB.setCurrentIndex(3)
        self.cmdOrder.setEnabled(False)
        
    @pyqtSlot() 
    def on_radRe_clicked(self):
        self.lblTitulo.setText(self.tr("Reinvest simulation of {0}").format(self.investment.name))
        self.lblSimulacion.setText(self.tr("Amount to reinvest"))
        self.lblValor.setText(self.tr("Purchase price (Current: {})").format(self.investment.product.currency.string(self.investment.product.result.basic.last.quote)))
        self.tabAB.setCurrentIndex(3)
        self.cmdOrder.setEnabled(False)
   
    def on_cmd_released(self): 
        self.sim_op=None
        self.sim_opactual=None
        self.sim_ophistorica=None
        
        
        at=Quote(self.mem).init__create(self.investment.product, datetime.datetime.now(), self.txtValorAccion.decimal())
        
        self.tabAB.setTabText(0, self.tr("After at {}").format(self.investment.product.currency.string(self.investment.product.result.basic.last.quote)))
        self.tabAB.setTabText(1, self.tr("After at {}").format(self.investment.product.currency.string(at.quote)))
        self.tabAB.setTabText(2, self.tr("Before at {}").format(self.investment.product.currency.string(at.quote)))
        self.tabAB.setTabText(3, self.tr("Before at {}").format(self.investment.product.currency.string(self.investment.product.result.basic.last.quote)))

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

        logging.error("Factor de conversion no siempre es 1")
        currency_conversion=1

        #Creamos un nuevo operinversiones 
        self.sim_op=self.investment.op.copy_until_datetime(None, self.mem, self.investment)
        id_operinversiones=self.sim_op.get_highest_io_id ()+1##Para simular un id_operinversiones real, le asignamos uno
        if self.radDes.isChecked():#DESINVERSION
            d=InvestmentOperation(self.mem).init__create(self.mem.tiposoperaciones.find_by_id(5), datetime.datetime.now(pytz.timezone(self.mem.localzone.name)), self.investment, -acciones, impuestos, comision, valor_accion, "",  True, currency_conversion,  id_operinversiones)
        else:#REINVERSION
            d=InvestmentOperation(self.mem).init__create(self.mem.tiposoperaciones.find_by_id(4), datetime.datetime.now(pytz.timezone(self.mem.localzone.name)), self.investment, acciones, impuestos, comision, valor_accion, "",  True, currency_conversion,  id_operinversiones)
        self.sim_op.arr.append(d)

        (self.sim_opactual, self.sim_ophistorica)=self.sim_op.calcular()
        #After
        self.sim_op.myqtablewidget(self.tblOperaciones)
        self.sim_opactual.myqtablewidget(self.tblInvestmentsActualDespues, quote=self.investment.product.result.basic.last)
        self.sim_ophistorica.myqtablewidget(self.tblInvestmentsHistoricas)
        self.gains(self.tblGainsAfter,  self.investment.shares()+self.shares(), self.sim_opactual.average_price())
        
        #After at
        self.sim_opactual.myqtablewidget(self.tblInvestmentsActualDespuesAt, quote=at)
        
        #Before at
        self.investment.op_actual.myqtablewidget(self.tblInvestmentsActualAntesAt, quote=at)
        
        
        #Before
        self.tabAB.setCurrentIndex(1)
        self.tabOpAcHi.setCurrentIndex(1)
        self.gains(self.tblGainsBefore, self.investment.shares(), self.investment.op_actual.average_price())
        
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
        wc.setReinvest( self.sim_op, self.sim_opactual)
        
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
        
    def gains(self, table,  shares,  averageprice):
        porcentages=[2.5, 5, 7.5, 10, 15, 30]
        table.applySettings()
        table.clearContents()
        table.setRowCount(len(porcentages))
        for i, tpc in enumerate(porcentages):        
            table.setItem(i, 0, Percentage(tpc, 100).qtablewidgetitem())
            tpcprice= averageprice*Decimal(1+tpc/100)
            table.setItem(i, 1, tpcprice.qtablewidgetitem())
            table.setItem(i, 2, ((tpcprice-averageprice)*shares).qtablewidgetitem())
