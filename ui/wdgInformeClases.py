from libxulpymoney import *
import math
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Ui_wdgInformeClases import *
from libxulpymoney import *

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
class canvasPie(FigureCanvas):
    def __init__(self, parent=None):
        """
        mem. Fichero configuración
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
        (self.patches, self.texts, self.autotexts)=self.ax.pie(self.fracs, explode=explode, labels=labels, labeldistance=100, pctdistance=1.1, autopct='%1.1f%%',  shadow=True)
        
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
        
    def clearContents(self):
        self.fig.clf()
        del self.fracs
        del self.explode
        del self.labels
        del self.patches
        del self.texts
        del self.autotexts
        del self.ax
        self.ax = self.fig.add_subplot(111)
        


class wdgInformeClases(QWidget, Ui_wdgInformeClases):
    def __init__(self, mem,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
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
        self.canvasProduct=canvasPie(self)
        self.layProduct.addWidget(self.canvasProduct)      
        
        self.cuentas=Patrimonio(self.mem).saldo_todas_cuentas(self.hoy)
        self.tab.setCurrentIndex(2)
        self.update()
               
    def update(self):
        """Update calcs and charts"""
        self.scriptTPC()
        self.scriptPCI()
        self.scriptTipos()
        self.scriptApalancado()
        self.scriptCountry()
        self.scriptProduct()
        
    def on_radCurrent_toggled(self, checked):
        self.update()
            

    def scriptTPC(self):
        self.canvasTPC.clearContents()
        labels=[]
        data=[]
        explode=[]
        for r in range(0, 11):
            total=0
            for i in self.mem.data.inversiones_active.arr:
                if math.ceil(i.product.tpc/10.0)==r:
                    if self.radCurrent.isChecked():
                        total=total+i.saldo()
                    else:
                        total=total+i.invertido()
            if r==0:
                total=total+self.cuentas
            if total>0:
                labels.append("{0}% variable".format(r*10))
                data.append(total)
                explode.append(0)
        self.canvasTPC.mydraw(data, labels,  explode)              



    def scriptPCI(self):
        self.canvasPCI.clearContents()
        labels=[]
        data=[]
        explode=[]

        for m in self.mem.investmentsmodes.list():
            total=0
            for i in self.mem.data.inversiones_active.arr:
                if i.product.mode==m:
                    if self.radCurrent.isChecked():
                        total=total+i.saldo()
                    else:
                        total=total+i.invertido()
            labels.append(m.name)
            if m.id=='c':
                data.append(total+self.cuentas)
            else:
                data.append(total)
            explode.append(0)
        self.canvasPCI.mydraw(data, labels,  explode)  

        
    def scriptTipos(self):
        self.canvasTipo.clearContents()
        labels=[]
        data=[]
        explode=[]
        for t in self.mem.types.list():
#            id_type=int(id_type)
            total=0
            for i in self.mem.data.inversiones_active.arr:
                if i.product.type==t:
                    if self.radCurrent.isChecked():
                        total=total+i.saldo()
                    else:
                        total=total+i.invertido()
            if t.id==11:#Cuentas
                total=total+self.cuentas
            if total>0:
                labels.append(t.name)
                data.append(total)
                explode.append(0)
        self.canvasTipo.mydraw(data, labels,  explode)  

        
    def scriptApalancado(self):
        self.canvasApalancado.clearContents()
        labels=[]
        data=[]
        explode=[]
                
        for a in self.mem.apalancamientos.list():
            total=0
            for i in self.mem.data.inversiones_active.arr:
                if i.product.apalancado==a:
                    if self.radCurrent.isChecked():
                        total=total+i.saldo()
                    else:
                        total=total+i.invertido()
            if a.id==0:#Cuentas
                total=total+self.cuentas
            if total>0:
                labels.append(a.name)
                data.append(total)
                explode.append(0)
        self.canvasApalancado.mydraw(data, labels,  explode)  
        
    def scriptCountry(self):
        self.canvasCountry.clearContents()
        labels=[]
        data=[]
        explode=[]
                
        for c in self.mem.countries.list():
            total=0
            for i in self.mem.data.inversiones_active.arr:
                if i.product.bolsa.country==c:
                    if self.radCurrent.isChecked():
                        total=total+i.saldo()
                    else:
                        total=total+i.invertido()
            if total>0:
                labels.append(c.name)
                data.append(total)
                explode.append(0)
        self.canvasCountry.mydraw(data, labels,  explode)  

    def scriptProduct(self):
        self.canvasProduct.clearContents()
        labels=[]
        data=[]
        explode=[]
        #Saca products active
        s=set([])
        for i in self.mem.data.inversiones_active.arr:
            s.add(i.product)
        
        arr=list(s)
        if self.radCurrent.isChecked():
            arr=sorted(arr, key=lambda inv: self.mem.data.inversiones_active.saldo_misma_investment(inv),  reverse=True) 
        else:
            arr=sorted(arr, key=lambda inv: self.mem.data.inversiones_active.invertido_misma_investment(inv),  reverse=True) 
   
        for i in arr:
            labels.append(i.name)
            if self.radCurrent.isChecked():
                data.append(self.mem.data.inversiones_active.saldo_misma_investment(i))
            else:
                data.append(self.mem.data.inversiones_active.invertido_misma_investment(i))
            explode.append(0)
        labels.append(self.trUtf8("Accounts"))
        data.append(self.cuentas)
        explode.append(0.15)            
        
        self.canvasProduct.mydraw(data, labels,  explode)  
