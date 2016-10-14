from PyQt5.QtCore import *
from PyQt5.QtGui import *
from Ui_wdgDisReinvest import *
from libxulpymoney import *
from wdgOrdersAdd import *
from decimal import *
from canvaschart import canvasChartHistoricalReinvest
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT 

class wdgDisReinvest(QWidget, Ui_wdgDisReinvest):
    def __init__(self, mem, inversion,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        self.inversion=inversion
                
        if self.inversion.op_actual.length()==0:
            m=QMessageBox()
            m.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
            m.setIcon(QMessageBox.Information)
            m.setText(self.tr("There aren't shares for this investment"))
            m.exec_()     
            return

        self.txtValorAccion.setText(self.inversion.product.result.basic.last.quote)
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
        
        self.inversion.op_actual.myqtablewidget_homogeneus(self.tblInvestmentsActualAntes)
        self.on_radRe_clicked()

    def acciones(self):
        resultado=0
        
        if self.radDes.isChecked():#DESINVERSION
            perdida=self.txtSimulacion.decimal()#Va disminuyendo con las distintas operaciones
            q=Quote(self.mem).init__create(self.inversion.product, datetime.datetime.now(pytz.timezone(self.mem.localzone.name)), self.txtValorAccion.decimal())
            for rec in self.inversion.op_actual.arr:
                pendiente=rec.pendiente(q)
                if perdida+pendiente==0:
                    resultado=resultado+Decimal(str(rec.acciones))
                    break
                elif perdida+pendiente>0:
                    resultado=resultado+Decimal(str(rec.acciones))
                    perdida=perdida+pendiente
                elif perdida+pendiente<0:
                    # Si de tantas acciones queda pendiente "pendiente"
                    # X                                queda la perdida
                    acciones=abs(int(perdida*rec.acciones/pendiente))
                    resultado=resultado+Decimal(acciones)#Se resta porque se debe calcular antes de quitarse el pendiente
                    break
        else:#REINVERSION
            resultado=Decimal(int(self.txtSimulacion.decimal()/self.txtValorAccion.decimal()))
        return resultado
            
    @QtCore.pyqtSlot() 
    def on_radDes_clicked(self):
        self.lblTitulo.setText(self.tr("Divest simulation of {0}").format(self.inversion.name))
        self.lblSimulacion.setText(self.tr("Divest loss to asume"))
        self.lblValor.setText(self.tr("Selling price (Current: {})").format(self.inversion.product.currency.string(self.inversion.product.result.basic.last.quote)))
        self.tabAB.setCurrentIndex(3)
        self.cmdOrder.setEnabled(False)
        
    @QtCore.pyqtSlot() 
    def on_radRe_clicked(self):
        self.lblTitulo.setText(self.tr("Reinvest simulation of {0}").format(self.inversion.name))
        self.lblSimulacion.setText(self.tr("Amount to reinvest"))
        self.lblValor.setText(self.tr("Purchase price (Current: {})").format(self.inversion.product.currency.string(self.inversion.product.result.basic.last.quote)))
        self.tabAB.setCurrentIndex(3)
        self.cmdOrder.setEnabled(False)
   
    def on_cmd_released(self): 
        self.sim_op=None
        self.sim_opactual=None
        self.sim_ophistorica=None
        
        
        at=Quote(self.mem).init__create(self.inversion.product, datetime.datetime.now(), self.txtValorAccion.decimal())
        
        self.tabAB.setTabText(0, self.tr("After at {}").format(self.inversion.product.currency.string(self.inversion.product.result.basic.last.quote)))
        self.tabAB.setTabText(1, self.tr("After at {}").format(self.inversion.product.currency.string(at.quote)))
        self.tabAB.setTabText(2, self.tr("Before at {}").format(self.inversion.product.currency.string(at.quote)))
        self.tabAB.setTabText(3, self.tr("Before at {}").format(self.inversion.product.currency.string(self.inversion.product.result.basic.last.quote)))

        if self.txtSimulacion.decimal()<=Decimal('0'):
            m=QMessageBox()
            m.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
            m.setIcon(QMessageBox.Information)
            m.setText(self.tr("Simulation value must be positive"))
            m.exec_()    
            return
            
        valor_accion=self.txtValorAccion.decimal()
        impuestos=0
        comision=self.txtComision.decimal()
        
        if valor_accion==0:
            m=QMessageBox()
            m.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
            m.setIcon(QMessageBox.Information)
            m.setText(self.tr("Share price can't be 0"))
            m.exec_()    
            return
        
        acciones=self.acciones()
        importe=valor_accion*acciones
        self.txtAcciones.setText(acciones)
        self.txtImporte.setText(importe)

        logging.error("Factor de conversion no siempre es 1")
        currency_conversion=1

        #Creamos un nuevo operinversiones 
        self.sim_op=self.inversion.op.clone()
        id_operinversiones=self.sim_op.get_highest_io_id ()+1##Para simular un id_operinversiones real, le asignamos uno
        if self.radDes.isChecked():#DESINVERSION
            d=InvestmentOperation(self.mem).init__create(self.mem.tiposoperaciones.find_by_id(5), datetime.datetime.now(pytz.timezone(self.mem.localzone.name)), self.inversion, -acciones, importe, impuestos, comision, valor_accion, "",  True, currency_conversion,  id_operinversiones)
        else:#REINVERSION
            d=InvestmentOperation(self.mem).init__create(self.mem.tiposoperaciones.find_by_id(4), datetime.datetime.now(pytz.timezone(self.mem.localzone.name)), self.inversion, acciones, importe, impuestos, comision, valor_accion, "",  True, currency_conversion,  id_operinversiones)
        self.sim_op.arr.append(d)

        (self.sim_opactual, self.sim_ophistorica)=self.sim_op.calcular()
        #After
        self.sim_op.myqtablewidget(self.tblOperaciones)
        self.sim_opactual.myqtablewidget_homogeneus(self.tblInvestmentsActualDespues, quote=self.inversion.product.result.basic.last)
        self.sim_ophistorica.myqtablewidget(self.tblInvestmentsHistoricas)
        self.gains(self.tblGainsAfter,  self.inversion.acciones()+self.acciones(), self.sim_opactual.average_price())
        
        #After at
        self.sim_opactual.myqtablewidget_homogeneus(self.tblInvestmentsActualDespuesAt, quote=at)
        
        #Before at
        self.inversion.op_actual.myqtablewidget_homogeneus(self.tblInvestmentsActualAntesAt, quote=at)
        
        
        #Before
        self.tabAB.setCurrentIndex(1)
        self.tabOpAcHi.setCurrentIndex(1)
        self.gains(self.tblGainsBefore, self.inversion.acciones(), self.inversion.op_actual.average_price())
        
        self.cmdOrder.setEnabled(True)
        self.cmdGraph.setEnabled(True)
                
    @pyqtSlot()
    def on_cmdGraph_released(self):
        self.inversion.product.result.get_basic_and_ohcls()
        d=QDialog(self)     
        d.setWindowTitle(self.tr("Reinvest graph"))
        d.showMaximized()
        w=canvasChartHistoricalReinvest(self.mem, d)
        ntb= NavigationToolbar2QT(w, d)
        w.load_data_reinvest(self.inversion, self.sim_op,  self.sim_opactual)
        lay = QVBoxLayout(d)
        lay.addWidget(w)
        lay.addWidget(ntb)
        d.exec_()

    @pyqtSlot()
    def on_cmdOrder_released(self):
        d=QDialog(self)     
        d.setModal(True)
        d.setWindowTitle(self.tr("Add new order"))
        w=wdgOrdersAdd(self.mem, None, self.inversion, d)
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
            table.setItem(i, 0, qtpc(tpc))
            tpcprice= averageprice*Decimal(1+tpc/100)
            table.setItem(i, 1, self.mem.localcurrency.qtablewidgetitem(tpcprice))       
            table.setItem(i, 2, self.mem.localcurrency.qtablewidgetitem(shares*(tpcprice-averageprice)))
