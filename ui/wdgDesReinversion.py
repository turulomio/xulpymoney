from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Ui_wdgDesReinversion import *
from libxulpymoney import *
from decimal import *

class wdgDesReinversion(QWidget, Ui_wdgDesReinversion):
    def __init__(self, cfg, inversion,  parent=None):
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
        
        self.tblInversionesActualDespues.settings("wdgDesReinversion",  self.cfg.inifile)
        self.tblInversionesActualAntes.settings("wdgDesReinversion",  self.cfg.inifile)
        self.tblOperaciones.settings("wdgDesReinversion",  self.cfg.inifile)        
        self.tblInversionesHistoricas.settings("wdgDesReinversion",  self.cfg.inifile)         
        
 
        self.operinversiones=SetInversionOperacion(self.cfg)
        for o in self.inversion.op.arr:
            if o.datetime>=self.inversion.op_actual.arr[0].datetime:
                self.operinversiones.append(o.clone())

        self.txtValorAccion.setText(str(self.inversion.mq.quotes.last.quote))
        self.tabResultados.setCurrentIndex(1)
        self.on_radDes_clicked()

    def acciones(self):
        """Debe calcularse las acciones"""
        resultado=0
        perdida=Decimal(self.txtSimulacion.text())       #Va disminuyendo con las distintas operaciones
       
        if self.radDes.isChecked():#DESINVERSION
            (operinversionesactual, operinversioneshistoricas)=self.operinversiones.calcular()
            q=Quote().init__create(self.inversion.mq, datetime.datetime.now(pytz.timezone(config.localzone)), self.txtValorAccion.decimal())
            for rec in operinversionesactual.arr:
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
#                    saldo=abs(perdida*rec.invertido()/pendiente)
                    acciones=abs(int(perdida*rec.acciones/pendiente))
                    print ("acciones a liverar",  acciones)
                    resultado=resultado+Decimal(acciones)#Se resta porque se debe calcular antes de quitarse el pendiente
                    break
        else:#REINVERSION
            resultado=Decimal(int(self.txtSimulacion.decimal()/self.txtValorAccion.decimal()))
        return resultado
            
    @QtCore.pyqtSlot() 
    def on_radDes_clicked(self):
        self.lblTitulo.setText(self.trUtf8("Estudio de desinversión de {0}".format(self.inversion.name)))
        self.lblSimulacion.setText(self.trUtf8("Pérdida aproximada a asumir en la desinversión"))
        self.lblValor.setText(self.trUtf8("Valor de venta"))
        
    @QtCore.pyqtSlot() 
    def on_radRe_clicked(self):
        self.lblTitulo.setText(self.trUtf8("Estudio de reinversión de {0}".format(self.inversion.name)))
        self.lblSimulacion.setText(self.trUtf8("Importe a reinvertir"))
        self.lblValor.setText(self.trUtf8("Valor de compra"))
   
    def on_cmd_released(self):
        if self.txtSimulacion.decimal()<=Decimal('0'):
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.trUtf8("El valor de la simulación debe ser positivo"))
            m.exec_()    
            return
        valor_accion=self.txtValorAccion.decimal()
        impuestos=0
        comision=self.txtComision.decimal()
        if valor_accion==0:
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.trUtf8("El valor de la acción no puede ser 0"))
            m.exec_()    
            return
        acciones=self.acciones()
        importe=valor_accion*acciones
        self.txtAcciones.setText(str(acciones))
        self.txtImporte.setText(str(importe))
        (operinversionesactualantes, operinversioneshistoricasantes)=self.operinversiones.calcular_new()

        #Creamos un nuevo operinversiones 
        operaciones=self.operinversiones.clone()
        d=InversionOperacion(self.cfg)
        id_operinversiones=self.operinversiones.arr[len(self.operinversiones.arr)-1].id+1 ##Para simular un id_operinversiones real, le asignamos uno
        if self.radDes.isChecked():#DESINVERSION
            d.init__create(self.cfg.tiposoperaciones.find(5), datetime.datetime.now(pytz.timezone(config.localzone)), self.inversion, -acciones, importe, impuestos, comision, valor_accion, "", id_operinversiones)
        else:#REINVERSION
            d.init__create(self.cfg.tiposoperaciones.find(4), datetime.datetime.now(pytz.timezone(config.localzone)), self.inversion, acciones, importe, impuestos, comision, valor_accion, "",  id_operinversiones)
            d.init__create(self.cfg.tiposoperaciones.find(4), datetime.datetime.now(pytz.timezone(config.localzone)), self.inversion, acciones, importe, impuestos, comision, valor_accion, "",  id_operinversiones)
        operaciones.arr.append(d)


        (operinversionesactual, operinversioneshistoricas)=operaciones.calcular_new()
        myqtablewidget_loads_SetInversionOperacion(self.tblOperaciones, operaciones.arr)
        myqtablewidget_loads_SetInversionOperacionActual(self.tblInversionesActualAntes, self.inversion.op_actual, "wdgDesReinversion", self.cfg )
        myqtablewidget_loads_SetInversionOperacionActual(self.tblInversionesActualDespues, operinversionesactual,  "wdgDesReinversion", self.cfg)
        myqtablewidget_loads_SetInversionOperacionHistorica(self.tblInversionesHistoricas, operinversioneshistoricas.arr)
