## -*- coding: utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from libxulpymoney import *
from Ui_wdgConceptos import *

class wdgConceptos(QWidget, Ui_wdgConceptos):
    def __init__(self, cfg,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.cfg=cfg

        self.tblGastos.setColumnHidden(0, True)
        self.tblGastos.settings("wdgConceptos",  self.cfg.file)
        self.tblIngresos.setColumnHidden(0, True)
        self.tblIngresos.settings("wdgConceptos",  self.cfg.file)
        
        fechainicio=Patrimonio(self.cfg).primera_fecha_con_datos_usuario()         
        if fechainicio==None: #No hay datos y petaba por db vacía
            self.cmd.setEnabled(False)
            return

        for i in range(datetime.date.today().year-fechainicio.year+1):
            self.cmbYear.addItem(str(fechainicio.year+i))    
        self.cmbYear.setCurrentIndex(self.cmbYear.findText(str(datetime.date.today().year)))
        self.cmbMonth.setCurrentIndex(datetime.date.today().month-1)
        
        self.on_cmd_clicked()
        
    def load_gastos(self,  year,  month):
        cur = self.cfg.con.cursor()
        gastos=Patrimonio(self.cfg).saldo_por_tipo_operacion(year,  month, 1)
        conceptos=self.cfg.conceptos.list_x_tipooperacion(1)
        self.tblGastos.clearContents()
        self.tblGastos.setRowCount(len(conceptos)+1)
        for i, c in enumerate(conceptos):
            self.tblGastos.setItem(i, 1, QTableWidgetItem(c.name))
            mes=c.mensual( year, month)
            self.tblGastos.setItem(i, 2, self.cfg.localcurrency.qtablewidgetitem(mes))
            if gastos==0:
                tpc=0
            else:
                tpc=100*mes/gastos
            self.tblGastos.setItem(i, 3, qtpc(tpc))
            self.tblGastos.setItem(i, 4, self.cfg.localcurrency.qtablewidgetitem(c.media_mensual()))
        cur.close()         
        self.tblGastos.setItem(len(conceptos), 1, QTableWidgetItem(self.tr('TOTAL')))
        self.tblGastos.setItem(len(conceptos), 2, self.cfg.localcurrency.qtablewidgetitem(gastos))       

    def load_ingresos(self,  year,  month):
        con=self.cfg.connect_xulpymoney()
        cur = con.cursor()
        ingresos=Patrimonio(self.cfg).saldo_por_tipo_operacion(year,  month, 2)
        conceptos=self.cfg.conceptos.list_x_tipooperacion(2)
        self.tblIngresos.clearContents()
        self.tblIngresos.setRowCount(len(conceptos)+1)
        for i, c in enumerate(conceptos):
            self.tblIngresos.setItem(i, 1, QTableWidgetItem(c.name))
            mes=c.mensual( year, month)
            self.tblIngresos.setItem(i, 2, self.cfg.localcurrency.qtablewidgetitem(mes))
            if ingresos==0:
                tpc=0
            else:
                tpc=100*mes/ingresos
            self.tblIngresos.setItem(i, 3, qtpc(tpc))
            self.tblIngresos.setItem(i, 4, self.cfg.localcurrency.qtablewidgetitem(c.media_mensual()))
        cur.close()     
        self.cfg.disconnect_xulpymoney(con)         
        self.tblIngresos.setItem(len(conceptos), 1, QTableWidgetItem(self.tr('TOTAL')))
        self.tblIngresos.setItem(len(conceptos), 2, self.cfg.localcurrency.qtablewidgetitem(ingresos))          

        
    @QtCore.pyqtSlot() 
    def on_cmd_clicked(self):
        year=int(self.cmbYear.currentText())
        month=self.cmbMonth.currentIndex()+1
        self.load_gastos(year,  month)
        self.load_ingresos(year,  month)
        
        
