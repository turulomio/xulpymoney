from PyQt4.QtCore import *
from PyQt4.QtGui import *
from libxulpymoney import *
from Ui_wdgJointReport import *

class wdgJointReport(QWidget, Ui_wdgJointReport):
    def __init__(self, mem,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        self.tblEstudio.settings("wdgJointReport",  self.mem)
        self.tblDividends.settings("wdgJointReport",  self.mem)
        self.tblInvestments.settings("wdgJointReport",  self.mem)
        self.tblLess.settings("wdgJointReport",  self.mem)
        self.tblMore.settings("wdgJointReport",  self.mem)
        self.tblAdded.settings("wdgJointReport",  self.mem)
        
        
        self.mem.data.load_inactives()
        
        self.totalDividendsNetos=0
        self.totalDividendsBrutos=0
        self.totalDividendsRetenciones=0
                
        anoinicio=Assets(self.mem).primera_datetime_con_datos_usuario().year       

#        ran=datetime.date.today().year-anoinicio+1
        
        self.wy.initiate(anoinicio, datetime.date.today().year, datetime.date.today().year)
        QObject.connect(self.wy, SIGNAL("changed"), self.on_wy_changed)

        if str2bool(self.mem.config.get_value("settings", "gainsyear"))==True:
            self.tab.removeTab(1)
        else:
            self.tab.removeTab(2)
            self.tab.removeTab(2)

        self.load()   
        self.tab.setCurrentIndex(0)


    def load(self):
        inicio=datetime.datetime.now()
        self.load_dividends()
        if str2bool(self.mem.config.get_value("settings", "gainsyear"))==True:
            self.load_less()
            self.load_more()
        else:
            self.load_historicas()
        self.load_added()
        self.load_rendimientos()
        print("wdgJointReport > load: {0}".format(datetime.datetime.now()-inicio))
        
    def load_added(self):
        operaciones=[]
        for i in self.mem.data.investments_all().arr:
            for o in i.op.arr:
                if o.tipooperacion.id==6 and o.datetime.year==self.wy.year:
                    operaciones.append(o)    
        operaciones=sorted(operaciones, key=lambda o: o.datetime,  reverse=False)                         
                    
        self.tblAdded.setRowCount(len(operaciones)+1)
        sumsaldo=0        
        curms=self.mem.con.cursor()
        for i,  o in enumerate(operaciones):
            valor=Quote(self.mem).init__from_query(o.inversion.product, o.datetime).quote
            if valor==None:
                print("wdgJointReport > load_added: {0} en {1} da nulo".format(o.inversion.product.id, o.datetime))
                valor=0
            balance=valor*o.acciones
            sumsaldo=sumsaldo+balance
            self.tblAdded.setItem(i, 0, qdatetime(o.datetime,  o.inversion.product.stockexchange.zone))
            self.tblAdded.setItem(i, 1, QTableWidgetItem(o.inversion.name))
            self.tblAdded.setItem(i, 2, QTableWidgetItem(self.mem.tiposoperaciones.find(6).name))
            self.tblAdded.setItem(i, 3, qright(str(o.acciones)))
            self.tblAdded.setItem(i, 4, self.mem.localcurrency.qtablewidgetitem(balance))
        curms.close()
        self.tblAdded.setItem(len(operaciones), 3, QTableWidgetItem(("TOTAL")))
        self.tblAdded.setItem(len(operaciones), 4, self.mem.localcurrency.qtablewidgetitem(sumsaldo))
   
    def load_dividends(self):
        set=SetDividends(self.mem)
        set.load_from_db("select * from dividends where id_conceptos not in (63) and date_part('year',fecha)={0} order by fecha".format(self.wy.year))
        (self.totalDividendsNetos, self.totalDividendsBrutos, self.totalDividendsRetenciones, sumcomision)=set.myqtablewidget(self.tblDividends, "wdgJointReport", True)

    def load_historicas(self):
        operaciones=SetInvestmentOperationsHistorical(self.mem)
        for i in self.mem.data.investments_all().arr:
            for o in i.op_historica.arr:
                if o.fecha_venta.year==self.wy.year and o.tipooperacion.id in (5, 8):#Venta y traspaso fondos inversion
                    operaciones.arr.append(o)
        operaciones.sort()
        (self.totalBruto, self.totalComisiones, self.totalImpuestos, self.totalNeto)=operaciones.myqtablewidget(self.tblInvestments, "wdgJointReport")
    def load_less(self):
        operaciones=SetInvestmentOperationsHistorical(self.mem)
        for i in self.mem.data.investments_all().arr:
            for o in i.op_historica.arr:
                if o.fecha_venta.year==self.wy.year and o.tipooperacion.id in (5, 8) and o.less_than_a_year()==True:#Venta y traspaso fondos inversion
                    operaciones.arr.append(o)
        operaciones.sort()
        (self.totalBruto, self.totalComisiones, self.totalImpuestos, self.totalNeto)=operaciones.myqtablewidget(self.tblLess, "wdgJointReport")
    def load_more(self):
        operaciones=SetInvestmentOperationsHistorical(self.mem)
        for i in self.mem.data.investments_all().arr:
            for o in i.op_historica.arr:
                if o.fecha_venta.year==self.wy.year and o.tipooperacion.id in (5, 8) and o.less_than_a_year()==False:#Venta y traspaso fondos inversion
                    operaciones.arr.append(o)
        operaciones.sort()
        (self.totalBruto, self.totalComisiones, self.totalImpuestos, self.totalNeto)=operaciones.myqtablewidget(self.tblMore, "wdgJointReport")



    def load_rendimientos(self):
        inicio=datetime.date(self.wy.year-1, 12, 31)
        cur=self.mem.con.cursor()
        cur.execute("select sum(importe) as suma from opercuentas where id_conceptos=59 and date_part('year',datetime)="+str(self.wy.year))
        sumcomisioncustodia=cur.fetchone()[0]        
        if sumcomisioncustodia==None:
            sumcomisioncustodia=0
            
        saldototal=Assets(self.mem).saldo_total(self.mem.data.investments_all() ,  datetime.date.today());
        saldototalinicio=Assets(self.mem).saldo_total( self.mem.data.investments_all(), inicio)
        if self.totalBruto>0:
            impxplus=-self.totalBruto*self.mem.taxcapitalappreciation
        else:            
            impxplus=0
        
        beneficiosin=self.totalBruto+self.totalComisiones+sumcomisioncustodia+self.totalDividendsBrutos
        beneficiopag=self.totalBruto+impxplus+self.totalImpuestos+self.totalComisiones+sumcomisioncustodia+self.totalDividendsNetos
        
        if saldototalinicio==0:
            tpcneto=None
            tpcimpxplus=None
            tpcplus=None
            tpcdividendsbrutos=None
            tpcdividendsnetos=None
            tpcsumcomision=None
            tpcsumcustodia=None
            tpcsumimpuestos=None
            tpcretenciondividends=None
        else:
            tpcneto=self.totalNeto*100/saldototalinicio
            tpcimpxplus=impxplus*100/saldototalinicio
            tpcplus=self.totalBruto*100/saldototalinicio
            tpcdividendsbrutos=self.totalDividendsBrutos*100/saldototalinicio
            tpcdividendsnetos=self.totalDividendsNetos*100/saldototalinicio
            tpcsumcomision=self.totalComisiones*100/saldototalinicio
            tpcsumcustodia=sumcomisioncustodia*100/saldototalinicio
            tpcsumimpuestos=self.totalImpuestos*100/saldototalinicio
            tpcretenciondividends=self.totalDividendsRetenciones*100/saldototalinicio

        self.tblEstudio.horizontalHeaderItem(1).setText(("% TAE desde "+str(inicio)))
        self.lblSaldo.setText(self.tr("balance a {0}, {1}".format(str(inicio), self.mem.localcurrency.string(saldototalinicio))))

        self.tblEstudio.setItem(0, 0,self.mem.localcurrency.qtablewidgetitem(self.totalBruto))       
        self.tblEstudio.setItem(0, 1,qtpc(tpcplus))            

        self.tblEstudio.setItem(1, 0,self.mem.localcurrency.qtablewidgetitem(self.totalComisiones))       
        self.tblEstudio.setItem(1, 1,qtpc(tpcsumcomision))     

        self.tblEstudio.setItem(2, 0,self.mem.localcurrency.qtablewidgetitem(self.totalImpuestos))       
        self.tblEstudio.setItem(2, 1,qtpc(tpcsumimpuestos))    
        
        self.tblEstudio.setItem(3, 0,self.mem.localcurrency.qtablewidgetitem(self.totalNeto))    #Lo que sale en total y patrimonio   
        self.tblEstudio.setItem(3, 1,qtpc(tpcneto))      

        self.tblEstudio.setItem(5, 0,self.mem.localcurrency.qtablewidgetitem(self.totalDividendsBrutos))       
        self.tblEstudio.setItem(5, 1,qtpc(tpcdividendsbrutos))     
        
        self.tblEstudio.setItem(6, 0,self.mem.localcurrency.qtablewidgetitem(self.totalDividendsRetenciones))       
        self.tblEstudio.setItem(6, 1,qtpc(tpcretenciondividends))            

        self.tblEstudio.setItem(7, 0,self.mem.localcurrency.qtablewidgetitem(self.totalDividendsNetos))       
        self.tblEstudio.setItem(7, 1,qtpc(tpcdividendsnetos))                
        
        self.tblEstudio.setItem(9, 0,self.mem.localcurrency.qtablewidgetitem(sumcomisioncustodia))       
        self.tblEstudio.setItem(9, 1,qtpc(tpcsumcustodia))      

        self.tblEstudio.setItem(11, 0,self.mem.localcurrency.qtablewidgetitem(impxplus))     
        self.tblEstudio.setItem(11, 1, qtpc(tpcimpxplus))


        self.tblEstudio.setItem(13, 0,self.mem.localcurrency.qtablewidgetitem(beneficiosin))       
        try:
            self.tblEstudio.setItem(13, 1,qtpc((beneficiosin)*100/saldototalinicio))            
        except:
            self.tblEstudio.setItem(13, 1,qtpc(None))     

        self.tblEstudio.setItem(14, 0,self.mem.localcurrency.qtablewidgetitem(beneficiopag))       
        try:
            self.tblEstudio.setItem(14, 1,qtpc((beneficiopag)*100/saldototalinicio))            
        except:
            self.tblEstudio.setItem(14,  1,qtpc(None))     

        self.tblEstudio.setItem(16, 0,self.mem.localcurrency.qtablewidgetitem(saldototal))       
        try:
            self.tblEstudio.setItem(16, 1,qtpc((saldototal-saldototalinicio)*100/saldototalinicio))            
        except:
            self.tblEstudio.setItem(16, 1,qtpc(None))     
            
        cur.close()


    def on_wy_changed(self):          
        self.load() 

