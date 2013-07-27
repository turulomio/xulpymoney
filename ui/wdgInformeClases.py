from libxulpymoney import *
import   math
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Ui_wdgInformeClases import *
from libxulpymoney import *

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
class canvasPie(FigureCanvas):
    def __init__(self, parent=None):
        """
        cfg. Fichero configuración
        fracs. Datos a dibujar
        explode. Valor para esplotar datos"""
        self.fig = Figure()
        FigureCanvas.__init__(self, self.fig)        
        FigureCanvas.setSizePolicy(self,QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.data=None
        self.fracs=None
        self.explode=None
        self.labels=None
        self.ax = self.fig.add_subplot(111)
        (self.patches, self.texts, self.autotexts)=(None, None, None) #Valores que devuelve el dibujo
        self.showlegend=True

    def mydraw(self, fracs, labels, explode):
        self.fracs=fracs
        self.explode=explode
        self.labels=labels
        (self.patches, self.texts, self.autotexts)=self.ax.pie(fracs, explode=explode, labels=labels, labeldistance=100, pctdistance=1.1, autopct='%1.1f%%',  shadow=True)
        
        for i in range(len(self.labels)):
            self.labels[i]=self.labels[i]+". {0} € ({1})".format(round(self.fracs[i], 2),self.autotexts[i].get_text())
        self.fig.legend(self.patches,self.labels,"lower center")
        self.fig.text(0, 0, "Total: {0} €".format(round(sum(self.fracs), 2)))

        self.draw()

    def showLegend(self, bool):
        if bool==False:
            self.fig.legends=[]
            self.showlegend=False
        else:
            self.fig.legend(self.patches,self.labels,"lower center")
            self.showlegend=True
        self.draw()      
            

    def mouseReleaseEvent(self,  event):
        self.showLegend(not self.showlegend)


class wdgInformeClases(QWidget, Ui_wdgInformeClases):
    def __init__(self, cfg,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.cfg=cfg
        self.saldos={}#Variable que cachea todos los saldos
        self.hoy=datetime.date.today()

        self.canvasTPC=canvasPie(self)
        self.layTPC.addWidget(self.canvasTPC)     
        self.canvasPCI=canvasPie(self)
        self.layPCI.addWidget(self.canvasPCI)      
        self.canvasTipo=canvasPie(self)
        self.layTipo.addWidget(self.canvasTipo)      
        self.canvasApalancado=canvasPie(self)
        self.layApalancado.addWidget(self.canvasApalancado)    
        self.canvasCountry=canvasPie(self)
        self.layCountry.addWidget(self.canvasCountry)      
        
        self.load_data_from_db()
        self.cuentas=Patrimonio(self.cfg).saldo_todas_cuentas(self.hoy)
               
        self.scriptTPC()
        self.scriptPCI()
        self.scriptTipos()
        self.scriptApalancado()
        self.scriptCountry()
        self.tab.setCurrentIndex(2)
        
    def load_data_from_db(self):
        inicio=datetime.datetime.now()
        self.indicereferencia=Investment(self.cfg).init__db(self.cfg.config.get("settings", "indicereferencia" ))
        self.indicereferencia.quotes.get_basic()
        self.data_ebs=SetEntidadesBancarias(self.cfg)
        self.data_ebs.load_from_db("select * from entidadesbancarias where eb_activa=true")
        self.data_cuentas=SetCuentas(self.cfg, self.data_ebs)
        self.data_cuentas.load_from_db("select * from cuentas where cu_activa=true")
        self.data_investments=SetInvestments(self.cfg)
        self.data_investments.load_from_db("select distinct(myquotesid) from inversiones where in_activa=true")
        self.data_inversiones=SetInversiones(self.cfg, self.data_cuentas, self.data_investments, self.indicereferencia)
        self.data_inversiones.load_from_db("select * from inversiones where in_activa=true")
        print("\n","Cargando data en wdgInversiones",  datetime.datetime.now()-inicio)

    def scriptTPC(self):
        labels=[]
        data=[]
        explode=[]
        for r in range(0, 11):
            total=0
            for i in self.data_inversiones.arr:
                if math.ceil(i.mq.tpc/10.0)==r:
                    total=total+i.saldo()
            if r==0:
                total=total+self.cuentas
            if total>0:
                labels.append("{0}% variable".format(r*10))
                data.append(total)
                explode.append(0)
        self.canvasTPC.mydraw(data, labels,  explode)              



    def scriptPCI(self):
        labels=[]
        data=[]
        explode=[]

        for m in self.cfg.investmentsmodes.list():
            total=0
            for i in self.data_inversiones.arr:
                if i.mq.mode==m:
                    total=total+i.saldo()
            labels.append(m.name)
            if m.id=='c':
                data.append(total+self.cuentas)
            else:
                data.append(total)
            explode.append(0)
        self.canvasPCI.mydraw(data, labels,  explode)  

        
    def scriptTipos(self):
        labels=[]
        data=[]
        explode=[]
        for t in self.cfg.types.list():
#            id_type=int(id_type)
            total=0
            for i in self.data_inversiones.arr:
                if i.mq.type==t:
                    total=total+i.saldo()
            if t.id==11:#Cuentas
                total=total+self.cuentas
            if total>0:
                labels.append(t.name)
                data.append(total)
                explode.append(0)
        self.canvasTipo.mydraw(data, labels,  explode)  

        
    def scriptApalancado(self):
        labels=[]
        data=[]
        explode=[]
                
        for a in self.cfg.apalancamientos.list():
            total=0
            for i in self.data_inversiones.arr:
                if i.mq.apalancado==a:
                    total=total+i.saldo()
            if a.id==0:#Cuentas
                total=total+self.cuentas
            if total>0:
                labels.append(a.name)
                data.append(total)
                explode.append(0)
        self.canvasApalancado.mydraw(data, labels,  explode)  
        
    def scriptCountry(self):
        labels=[]
        data=[]
        explode=[]
                
        for c in self.cfg.countries.list():
            total=0
            for i in self.data_inversiones.arr:
                if i.mq.bolsa.country==c:
                    total=total+i.saldo()
            if total>0:
                labels.append(c.name)
                data.append(total)
                explode.append(0)
        self.canvasCountry.mydraw(data, labels,  explode)  
