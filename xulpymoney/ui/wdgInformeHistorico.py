from PyQt4.QtCore import *
from PyQt4.QtGui import *
from libxulpymoney import *
from Ui_wdgInformeHistorico import *

class wdgInformeHistorico(QWidget, Ui_wdgInformeHistorico):
    def __init__(self, cfg,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.cfg=cfg
        self.tblEstudio.settings(None,  self.cfg)
        self.tblDividendos.settings(None,  self.cfg)
        self.tblInversiones.settings("wdgInformeHistorico",  self.cfg)
        self.tblAdded.settings(None,  self.cfg)
        
        
        self.cfg.data.load_inactives()
        
        self.totalDividendosNetos=0
        self.totalDividendosBrutos=0
        self.totalDividendosRetenciones=0
                
        anoinicio=Patrimonio(self.cfg).primera_fecha_con_datos_usuario().year       

#        ran=datetime.date.today().year-anoinicio+1
        
        self.wy.initiate(anoinicio, datetime.date.today().year, datetime.date.today().year)
        QObject.connect(self.wy, SIGNAL("changed"), self.on_wy_changed)

        self.load()   
        self.tab.setCurrentIndex(0)


    def load(self):
        inicio=datetime.datetime.now()
        self.load_dividendos()
        self.load_historicas()
        self.load_added()
        self.load_rendimientos()
        print("wdgInformeHistorico > load: {0}".format(datetime.datetime.now()-inicio))
        
    def load_added(self):
        operaciones=[]
        for i in self.cfg.data.inversiones_all().arr:
            for o in i.op.arr:
                if o.tipooperacion.id==6 and o.datetime.year==self.wy.year:
                    operaciones.append(o)    
        operaciones=sorted(operaciones, key=lambda o: o.datetime,  reverse=False)                         
                    
        self.tblAdded.setRowCount(len(operaciones)+1)
        sumsaldo=0        
        curms=self.cfg.conms.cursor()
        for i,  o in enumerate(operaciones):
            valor=Quote(self.cfg).init__from_query(o.inversion.investment, o.datetime).quote
            if valor==None:
                print("wdgInformeHistorico > load_added: {0} en {1} da nulo".format(o.inversion.investment.id, o.datetime))
                valor=0
            saldo=valor*o.acciones
            sumsaldo=sumsaldo+saldo
            self.tblAdded.setItem(i, 0, qdatetime(o.datetime,  o.inversion.investment.bolsa.zone))
            self.tblAdded.setItem(i, 1, QTableWidgetItem(o.inversion.name))
            self.tblAdded.setItem(i, 2, QTableWidgetItem(self.cfg.tiposoperaciones.find(6).name))
            self.tblAdded.setItem(i, 3, qright(str(o.acciones)))
            self.tblAdded.setItem(i, 4, self.cfg.localcurrency.qtablewidgetitem(saldo))
        curms.close()
        self.tblAdded.setItem(len(operaciones), 3, QTableWidgetItem(("TOTAL")))
        self.tblAdded.setItem(len(operaciones), 4, self.cfg.localcurrency.qtablewidgetitem(sumsaldo))
   
    def load_dividendos(self):
        cur=self.cfg.con.cursor()
        self.totalDividendosNetos=0
        self.totalDividendosBrutos=0
        self.totalDividendosRetenciones=0
        sql="select * from dividendos where date_part('year',fecha)="+str(self.wy.year) + " order by fecha"
        cur.execute(sql); 
        dividendos=[]
        for row in  cur:
            dividendos.append(Dividendo(self.cfg).init__db_row(row, self.cfg.data.inversiones_all().find(row['id_inversiones']), None,  self.cfg.conceptos.find(row['id_conceptos'])))#Creación incompleta por no ser necesario con None
        self.tblDividendos.clearContents()
        self.tblDividendos.setRowCount(len(dividendos)+1)
        for i, d in enumerate(dividendos):
            self.totalDividendosNetos=self.totalDividendosNetos+d.neto_antes_impuestos()
            self.totalDividendosBrutos=self.totalDividendosBrutos+d.bruto
            self.totalDividendosRetenciones=self.totalDividendosRetenciones+d.retencion
            self.tblDividendos.setItem(i, 0,QTableWidgetItem(str(d.fecha)))
            self.tblDividendos.setItem(i, 1,QTableWidgetItem(d.concepto.name))
            self.tblDividendos.setItem(i, 2,QTableWidgetItem(d.inversion.name))
            self.tblDividendos.setItem(i, 3,QTableWidgetItem(d.inversion.cuenta.name))
            self.tblDividendos.setItem(i, 4,self.cfg.localcurrency.qtablewidgetitem(d.neto_antes_impuestos()))
        self.tblDividendos.setItem(len(dividendos), 3,QTableWidgetItem(("TOTAL")))
        self.tblDividendos.setItem(len(dividendos), 4,self.cfg.localcurrency.qtablewidgetitem(self.totalDividendosNetos))
        self.tblDividendos.setCurrentCell(len(dividendos), 4)
        cur.close()

    def load_historicas(self):
        operaciones=SetInversionOperacionHistorica(self.cfg)
        for i in self.cfg.data.inversiones_all().arr:
            for o in i.op_historica.arr:
                if o.fecha_venta.year==self.wy.year and o.tipooperacion.id in (5, 8):#Venta y traspaso fondos inversion
                    operaciones.arr.append(o)
        operaciones.arr=sorted(operaciones.arr, key=lambda o: o.fecha_venta,  reverse=False)      
        (self.totalBruto, self.totalComisiones, self.totalImpuestos, self.totalNeto)=operaciones.load_myqtablewidget(self.tblInversiones, "wdgInformeHistorico")



    def load_rendimientos(self):
        inicio=datetime.date(self.wy.year-1, 12, 31)
        cur=self.cfg.con.cursor()
        cur.execute("select sum(importe) as suma from opercuentas where id_conceptos=59 and date_part('year',fecha)="+str(self.wy.year))
        sumcomisioncustodia=cur.fetchone()[0]        
        if sumcomisioncustodia==None:
            sumcomisioncustodia=0
            
        saldototal=Patrimonio(self.cfg).saldo_total(self.cfg.data.inversiones_all() ,  datetime.date.today());
        saldototalinicio=Patrimonio(self.cfg).saldo_total( self.cfg.data.inversiones_all(), inicio)
        if self.totalBruto>0:
            impxplus=-self.totalBruto*self.cfg.taxcapitalappreciation
        else:            
            impxplus=0
        
        beneficiosin=self.totalBruto+self.totalComisiones+sumcomisioncustodia+self.totalDividendosBrutos
        beneficiopag=self.totalBruto+impxplus+self.totalImpuestos+self.totalComisiones+sumcomisioncustodia+self.totalDividendosNetos
        
        if saldototalinicio==0:
            tpcneto=None
            tpcimpxplus=None
            tpcplus=None
            tpcdividendosbrutos=None
            tpcdividendosnetos=None
            tpcsumcomision=None
            tpcsumcustodia=None
            tpcsumimpuestos=None
            tpcretenciondividendos=None
        else:
            tpcneto=self.totalNeto*100/saldototalinicio
            tpcimpxplus=impxplus*100/saldototalinicio
            tpcplus=self.totalBruto*100/saldototalinicio
            tpcdividendosbrutos=self.totalDividendosBrutos*100/saldototalinicio
            tpcdividendosnetos=self.totalDividendosNetos*100/saldototalinicio
            tpcsumcomision=self.totalComisiones*100/saldototalinicio
            tpcsumcustodia=sumcomisioncustodia*100/saldototalinicio
            tpcsumimpuestos=self.totalImpuestos*100/saldototalinicio
            tpcretenciondividendos=self.totalDividendosRetenciones*100/saldototalinicio

        self.tblEstudio.horizontalHeaderItem(1).setText(("% TAE desde "+str(inicio)))
        self.lblSaldo.setText(self.tr("Saldo a {0}, {1}".format(str(inicio), self.cfg.localcurrency.string(saldototalinicio))))

        self.tblEstudio.setItem(0, 0,self.cfg.localcurrency.qtablewidgetitem(self.totalBruto))       
        self.tblEstudio.setItem(0, 1,qtpc(tpcplus))            

        self.tblEstudio.setItem(1, 0,self.cfg.localcurrency.qtablewidgetitem(self.totalComisiones))       
        self.tblEstudio.setItem(1, 1,qtpc(tpcsumcomision))     

        self.tblEstudio.setItem(2, 0,self.cfg.localcurrency.qtablewidgetitem(self.totalImpuestos))       
        self.tblEstudio.setItem(2, 1,qtpc(tpcsumimpuestos))    
        
        self.tblEstudio.setItem(3, 0,self.cfg.localcurrency.qtablewidgetitem(self.totalNeto))    #Lo que sale en total y patrimonio   
        self.tblEstudio.setItem(3, 1,qtpc(tpcneto))      

        self.tblEstudio.setItem(5, 0,self.cfg.localcurrency.qtablewidgetitem(self.totalDividendosBrutos))       
        self.tblEstudio.setItem(5, 1,qtpc(tpcdividendosbrutos))     
        
        self.tblEstudio.setItem(6, 0,self.cfg.localcurrency.qtablewidgetitem(self.totalDividendosRetenciones))       
        self.tblEstudio.setItem(6, 1,qtpc(tpcretenciondividendos))            

        self.tblEstudio.setItem(7, 0,self.cfg.localcurrency.qtablewidgetitem(self.totalDividendosNetos))       
        self.tblEstudio.setItem(7, 1,qtpc(tpcdividendosnetos))                
        
        self.tblEstudio.setItem(9, 0,self.cfg.localcurrency.qtablewidgetitem(sumcomisioncustodia))       
        self.tblEstudio.setItem(9, 1,qtpc(tpcsumcustodia))      

        self.tblEstudio.setItem(11, 0,self.cfg.localcurrency.qtablewidgetitem(impxplus))     
        self.tblEstudio.setItem(11, 1, qtpc(tpcimpxplus))


        self.tblEstudio.setItem(13, 0,self.cfg.localcurrency.qtablewidgetitem(beneficiosin))       
        try:
            self.tblEstudio.setItem(13, 1,qtpc((beneficiosin)*100/saldototalinicio))            
        except:
            self.tblEstudio.setItem(13, 1,qtpc(None))     

        self.tblEstudio.setItem(14, 0,self.cfg.localcurrency.qtablewidgetitem(beneficiopag))       
        try:
            self.tblEstudio.setItem(14, 1,qtpc((beneficiopag)*100/saldototalinicio))            
        except:
            self.tblEstudio.setItem(14,  1,qtpc(None))     

        self.tblEstudio.setItem(16, 0,self.cfg.localcurrency.qtablewidgetitem(saldototal))       
        try:
            self.tblEstudio.setItem(16, 1,qtpc((saldototal-saldototalinicio)*100/saldototalinicio))            
        except:
            self.tblEstudio.setItem(16, 1,qtpc(None))     
            
        cur.close()


    def on_wy_changed(self):          
        self.load() 

