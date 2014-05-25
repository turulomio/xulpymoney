from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Ui_wdgAPR import *
from libxulpymoney import *

class wdgAPR(QWidget, Ui_wdgAPR):
    def __init__(self, mem,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        self.progress = QProgressDialog(self.tr("Rellenando los datos del informe"), self.tr("Cancelar"), 0,0)
        self.progress.setModal(True)
        self.progress.setWindowTitle(self.trUtf8("Calculando datos..."))
        self.progress.setMinimumDuration(0)        
        self.table.settings("wdgAPR",  self.mem)
        
        self.mem.data.load_inactives()
        self.load_data()


    def load_data(self):        
        inicio=datetime.datetime.now()
#        con=self.mem.connect_xulpymoney()
#        cur = con.cursor()
#        mq=self.mem.connect_mystocks()
#        curms=mq.cursor()                
        anoinicio=Assets(self.mem).primera_fecha_con_datos_usuario().year       
        anofinal=datetime.date.today().year+1        
        
        self.progress.reset()
        self.progress.setMinimum(1)
        self.progress.setMaximum(anofinal-anoinicio+1)
        self.progress.forceShow()
        self.progress.setValue(1)
        self.table.setRowCount(anofinal-anoinicio+1)
        lastsaldo=0
        sumdividends=0
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
            sf=Assets(self.mem).saldo_total(self.mem.data.inversiones_all(),  datetime.date(i, 12, 31))
            gastos=Assets(self.mem).saldo_anual_por_tipo_operacion( i,1)#+Assets(self.mem).saldo_anual_por_tipo_operacion (cur,i, 7)#Gastos + Facturación de tarjeta
            dividends=Investment(self.mem).dividends_bruto( i)
            ingresos=Assets(self.mem).saldo_anual_por_tipo_operacion(  i,2)-dividends #Se quitan los dividends que luego se suman
            consolidado=Assets(self.mem).consolidado_neto(self.mem.data.inversiones_all(),  i)

            gi=ingresos+dividends+consolidado+gastos     
            self.table.setItem(i-anoinicio, 0, qcenter(str(i)))
            self.table.setItem(i-anoinicio, 1, self.mem.localcurrency.qtablewidgetitem(si))
            self.table.setItem(i-anoinicio, 2, self.mem.localcurrency.qtablewidgetitem(sf))
            self.table.setItem(i-anoinicio, 3, self.mem.localcurrency.qtablewidgetitem(sf-si))
            self.table.setItem(i-anoinicio, 4, self.mem.localcurrency.qtablewidgetitem(ingresos))
            self.table.setItem(i-anoinicio, 5, self.mem.localcurrency.qtablewidgetitem(consolidado))
            self.table.setItem(i-anoinicio, 6, self.mem.localcurrency.qtablewidgetitem(dividends))
            self.table.setItem(i-anoinicio, 7, self.mem.localcurrency.qtablewidgetitem(gastos))
            self.table.setItem(i-anoinicio, 8, self.mem.localcurrency.qtablewidgetitem(gi))
            sumdividends=sumdividends+dividends
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
#        self.mem.disconnect_xulpymoney(con)     
#        curms.close()
#        self.mem.disconnect_mystocks(mq)     
        self.table.setItem(anofinal-anoinicio, 0, qcenter((self.tr("TOTAL"))))
        self.table.setItem(anofinal-anoinicio, 4, self.mem.localcurrency.qtablewidgetitem(sumingresos))
        self.table.setItem(anofinal-anoinicio, 5, self.mem.localcurrency.qtablewidgetitem(sumconsolidado))
        self.table.setItem(anofinal-anoinicio, 6, self.mem.localcurrency.qtablewidgetitem(sumdividends))
        self.table.setItem(anofinal-anoinicio, 7, self.mem.localcurrency.qtablewidgetitem(sumgastos))
        self.table.setItem(anofinal-anoinicio, 8, self.mem.localcurrency.qtablewidgetitem(sumicdg))
        final=datetime.datetime.now()          
        print ("wdgAPR > load_data: {0}".format(final-inicio))
