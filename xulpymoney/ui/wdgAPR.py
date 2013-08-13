from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Ui_wdgAPR import *
from libxulpymoney import *

class wdgAPR(QWidget, Ui_wdgAPR):
    def __init__(self, cfg,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.cfg=cfg
        self.progress = QProgressDialog(self.tr("Rellenando los datos del informe"), self.tr("Cancelar"), 0,0)
        self.progress.setModal(True)
        self.progress.setWindowTitle(self.trUtf8("Calculando datos..."))
        self.progress.setMinimumDuration(0)        
        self.table.settings("wdgAPR",  self.cfg.file_ui)
        
        self.cfg.data.load_inactives()
        self.load_data()


    def load_data(self):        
        inicio=datetime.datetime.now()
#        con=self.cfg.connect_xulpymoney()
#        cur = con.cursor()
#        mq=self.cfg.connect_myquotes()
#        curms=mq.cursor()                
        anoinicio=Patrimonio(self.cfg).primera_fecha_con_datos_usuario().year       
        anofinal=datetime.date.today().year+1        
        
        self.progress.reset()
        self.progress.setMinimum(1)
        self.progress.setMaximum(anofinal-anoinicio+1)
        self.progress.forceShow()
        self.progress.setValue(1)
        self.table.setRowCount(anofinal-anoinicio+1)
        lastsaldo=0
        sumdividendos=0
        sumconsolidado=0
        sumgastos=0
        sumingresos=0
        (sumicdg, sumsaldoaccionescostecero)=(0, 0)
        for i in range(anoinicio, anofinal):
            if self.progress.wasCanceled():
                break;
            else:
                self.progress.setValue(self.progress.value()+1)                     
            si=lastsaldo
            sf=Patrimonio(self.cfg).saldo_total(self.cfg.data.inversiones_all(),  datetime.date(i, 12, 31))
            gastos=Patrimonio(self.cfg).saldo_anual_por_tipo_operacion( i,1)#+Patrimonio(self.cfg).saldo_anual_por_tipo_operacion (cur,i, 7)#Gastos + Facturación de tarjeta
            dividendos=Inversion(self.cfg).dividendos_bruto( i)
            ingresos=Patrimonio(self.cfg).saldo_anual_por_tipo_operacion(  i,2)-dividendos #Se quitan los dividendos que luego se suman
            consolidado=Patrimonio(self.cfg).consolidado_neto(self.cfg.data.inversiones_all(),  i)

            gi=ingresos+dividendos+consolidado+gastos     
            self.table.setItem(i-anoinicio, 0, qcenter(str(i)))
            self.table.setItem(i-anoinicio, 1, self.cfg.localcurrency.qtablewidgetitem(si))
            self.table.setItem(i-anoinicio, 2, self.cfg.localcurrency.qtablewidgetitem(sf))
            self.table.setItem(i-anoinicio, 3, self.cfg.localcurrency.qtablewidgetitem(sf-si))
            self.table.setItem(i-anoinicio, 4, self.cfg.localcurrency.qtablewidgetitem(ingresos))
            self.table.setItem(i-anoinicio, 5, self.cfg.localcurrency.qtablewidgetitem(consolidado))
            self.table.setItem(i-anoinicio, 6, self.cfg.localcurrency.qtablewidgetitem(dividendos))
            self.table.setItem(i-anoinicio, 7, self.cfg.localcurrency.qtablewidgetitem(gastos))
            self.table.setItem(i-anoinicio, 8, self.cfg.localcurrency.qtablewidgetitem(gi))
            sumdividendos=sumdividendos+dividendos
            sumconsolidado=sumconsolidado+consolidado
            sumgastos=sumgastos+gastos
            sumingresos=sumingresos+ingresos
            sumicdg=sumicdg+gi
            if si==0:
                tae=0
            else:
                tae=(sf -si)*100/si
            self.table.setItem(i-anoinicio, 9, qtpc(tae))
            lastsaldo=sf
#        cur.close()     
#        self.cfg.disconnect_xulpymoney(con)     
#        curms.close()
#        self.cfg.disconnect_myquotes(mq)     
        self.table.setItem(anofinal-anoinicio, 0, qcenter((self.tr("TOTAL"))))
        self.table.setItem(anofinal-anoinicio, 4, self.cfg.localcurrency.qtablewidgetitem(sumingresos))
        self.table.setItem(anofinal-anoinicio, 5, self.cfg.localcurrency.qtablewidgetitem(sumconsolidado))
        self.table.setItem(anofinal-anoinicio, 6, self.cfg.localcurrency.qtablewidgetitem(sumdividendos))
        self.table.setItem(anofinal-anoinicio, 7, self.cfg.localcurrency.qtablewidgetitem(sumgastos))
        self.table.setItem(anofinal-anoinicio, 8, self.cfg.localcurrency.qtablewidgetitem(sumicdg))
        final=datetime.datetime.now()          
        print ("wdgAPR > load_data: {0}".format(final-inicio))
