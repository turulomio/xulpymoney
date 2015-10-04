from PyQt5.QtCore import *
from PyQt5.QtGui import *
from Ui_wdgDisReinvest import *
from libxulpymoney import *
from decimal import *

class wdgDisReinvest(QWidget, Ui_wdgDisReinvest):
    def __init__(self, mem, inversion,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        self.inversion=inversion
                
        if self.inversion.op_actual.length()==0:
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.tr("There aren't shares for this investment"))
            m.exec_()     
            return

        self.txtValorAccion.setText(self.inversion.product.result.basic.last.quote)
        self.txtSimulacion.setText(Global(self.mem, "wdgIndexRange", "txtInvertir").get())
        self.tabOpAcHi.setCurrentIndex(1)
        self.tabAB.setCurrentIndex(1)
        
        self.inversion.op_actual.myqtablewidget(self.tblInvestmentsActualAntes)
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
        self.lblValor.setText(self.tr("Selling price"))
        self.tabAB.setCurrentIndex(1)
        
    @QtCore.pyqtSlot() 
    def on_radRe_clicked(self):
        self.lblTitulo.setText(self.tr("Reinvest simulation of {0}").format(self.inversion.name))
        self.lblSimulacion.setText(self.tr("Amount to reinvest"))
        self.lblValor.setText(self.tr("Purchase price"))
        self.tabAB.setCurrentIndex(1)
   
    def on_cmd_released(self): 
        self.sim_op=None
        self.sim_opactual=None
        self.sim_ophistorica=None

        if self.txtSimulacion.decimal()<=Decimal('0'):
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.tr("Simulation value must be positive"))
            m.exec_()    
            return
            
        valor_accion=self.txtValorAccion.decimal()
        impuestos=0
        comision=self.txtComision.decimal()
        
        if valor_accion==0:
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.tr("Share price can't be 0"))
            m.exec_()    
            return
        
        acciones=self.acciones()
        importe=valor_accion*acciones
        self.txtAcciones.setText(acciones)
        self.txtImporte.setText(importe)

        #Creamos un nuevo operinversiones 
        self.sim_op=self.inversion.op.clone()
        id_operinversiones=self.sim_op.get_highest_io_id ()+1##Para simular un id_operinversiones real, le asignamos uno
        if self.radDes.isChecked():#DESINVERSION
            d=InvestmentOperation(self.mem).init__create(self.mem.tiposoperaciones.find(5), datetime.datetime.now(pytz.timezone(self.mem.localzone.name)), self.inversion, -acciones, importe, impuestos, comision, valor_accion, "",  True, id_operinversiones)
        else:#REINVERSION
            d=InvestmentOperation(self.mem).init__create(self.mem.tiposoperaciones.find(4), datetime.datetime.now(pytz.timezone(self.mem.localzone.name)), self.inversion, acciones, importe, impuestos, comision, valor_accion, "",  True, id_operinversiones)
        self.sim_op.arr.append(d)

        (self.sim_opactual, self.sim_ophistorica)=self.sim_op.calcular()
        self.sim_op.myqtablewidget(self.tblOperaciones)
        self.sim_opactual.myqtablewidget(self.tblInvestmentsActualDespues)
        self.sim_ophistorica.myqtablewidget(self.tblInvestmentsHistoricas)
        self.tabAB.setCurrentIndex(0)
        self.tabOpAcHi.setCurrentIndex(1)
