from libxulpymoney import *
import math
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import pylab
from Ui_wdgInvestmentClasses import *
from libxulpymoney import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
class canvasPie(FigureCanvasQTAgg):
    def __init__(self, parent=None):
        """
        mem. Fichero configuración
        fracs. Datos a dibujar
        explode. Valor para esplotar datos"""
        self.fig = Figure()
        FigureCanvasQTAgg.__init__(self, self.fig)        
        FigureCanvasQTAgg.setSizePolicy(self,QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvasQTAgg.updateGeometry(self)
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
        self.fig.legend(self.patches,self.labels,"upper right")
        self.draw()

    def savePixmap(self, filename, dpi=250):
        """Saves a pixmap of the pie"""
        current=self.showlegend
        if self.showlegend==True:
            self.showLegend(False)
        self.fig.savefig(filename, dpi=dpi)        
        self.showLegend(current)

    def savePixmapLegend(self, filename, dpi=250):
        """Saves a pixmap of the legend"""
        wi=8
        he=0.45*len(self.labels)
        # create a second figure for the legend
        figLegend = pylab.figure(figsize = (wi,he))

        # produce a legend for the objects in the other figure
        pylab.figlegend(self.patches, self.labels, loc = 'upper left')

        # save the two figures to files
        figLegend.savefig(filename, dpi=dpi)        
        return (wi, he)

    def showLegend(self, bool):
        if bool==False:
            self.fig.legends=[]
            self.showlegend=False
        else:
            self.fig.legend(self.patches,self.labels,"upper right")
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
        


class wdgInvestmentClasses(QWidget, Ui_wdgInvestmentClasses):
    def __init__(self, mem,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        self.balances={}#Variable que cachea todos los balances
        self.hoy=datetime.date.today()

        self.canvasTPC=canvasPie(self)
        self.canvasTPC.ax.set_title(self.tr("Investment current balance by variable percentage"), fontsize=30, fontweight="bold", y=1.02)   
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
        
        self.accounts=Assets(self.mem).saldo_todas_cuentas(self.hoy).local()
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
        sumtotal=Money(self.mem, 0, self.mem.localcurrency)
        for r in range(0, 11):
            total=Money(self.mem, 0,  self.mem.localcurrency)
            for i in self.mem.data.investments_active().arr:
                if math.ceil(i.product.percentage/10.0)==r:
                    if self.radCurrent.isChecked():
                        total=total+i.balance().local()
                    else:
                        total=total+i.invertido().local()
            if r==0:
                total=total+self.accounts
            if total.isGTZero():
                labels.append("{0}% variable".format(r*10))
                data.append(total.amount)
                explode.append(0)
            sumtotal=sumtotal+total
        if self.radCurrent.isChecked():    
            self.canvasTPC.ax.set_title(self.tr("Investment current balance by variable percentage"), fontsize=30, fontweight="bold", y=1.02)   
        else:
            self.canvasTPC.ax.set_title(self.tr("Invested balance by variable percentage"), fontsize=30, fontweight="bold", y=1.02)   
        self.canvasTPC.ax.annotate(xy=(5, 5), xycoords="figure pixels",  s=self.tr("Total: {0}".format(sumtotal)))
        self.canvasTPC.mydraw(data, labels,  explode)       



    def scriptPCI(self):
        self.canvasPCI.clearContents()
        labels=[]
        data=[]
        explode=[]
        sumtotal=Money(self.mem, 0, self.mem.localcurrency)

        for m in self.mem.investmentsmodes.arr:
            total=Money(self.mem, 0,  self.mem.localcurrency)
            for i in self.mem.data.investments_active().arr:
                if i.product.mode==m:
                    if self.radCurrent.isChecked():
                        total=total+i.balance().local()
                    else:
                        total=total+i.invertido().local()
            labels.append(m.name)
            if m.id=='c':
                total=total+self.accounts
                data.append(total.amount)
            else:
                data.append(total.amount)
            explode.append(0)
            sumtotal=sumtotal+total
        if self.radCurrent.isChecked():    
            self.canvasPCI.ax.set_title(self.tr("Investment current balance by Put / Call / Inline"), fontsize=30, fontweight="bold", y=1.02)   
        else:
            self.canvasPCI.ax.set_title(self.tr("Invested balance by Put / Call / Inline"), fontsize=30, fontweight="bold", y=1.02)   
        self.canvasPCI.ax.annotate(xy=(5, 5), xycoords="figure pixels",  s=self.tr("Total: {0}".format(sumtotal)))
        self.canvasPCI.mydraw(data, labels,  explode)  

        
    def scriptTipos(self):
        self.canvasTipo.clearContents()
        labels=[]
        data=[]
        explode=[]
        sumtotal=Money(self.mem, 0, self.mem.localcurrency)
        for t in self.mem.types.arr:
            total=Money(self.mem, 0,  self.mem.localcurrency)
            for i in self.mem.data.investments_active().arr:
                if i.product.type==t:
                    if self.radCurrent.isChecked():
                        total=total+i.balance().local()
                    else:
                        total=total+i.invertido().local()
            if t.id==11:#Accounts
                total=total+self.accounts
            if total.isGTZero():
                labels.append(t.name)
                data.append(total.amount)
                if t.id==11:#Accounts
                    explode.append(0.15)        
                else:
                    explode.append(0)
            sumtotal=sumtotal+total
        if self.radCurrent.isChecked():    
            self.canvasTipo.ax.set_title(self.tr("Investment current balance by product type"), fontsize=30, fontweight="bold", y=1.02)   
        else:
            self.canvasTipo.ax.set_title(self.tr("Invested balance by product type"), fontsize=30, fontweight="bold", y=1.02)   
        self.canvasTipo.ax.annotate(xy=(5, 5), xycoords="figure pixels",  s=self.tr("Total: {0}".format(sumtotal)))
        self.canvasTipo.mydraw(data, labels,  explode)  

        
    def scriptApalancado(self):
        self.canvasApalancado.clearContents()
        labels=[]
        data=[]
        explode=[]
        sumtotal=Money(self.mem, 0, self.mem.localcurrency)
                
        for a in self.mem.leverages.arr:
            total=Money(self.mem, 0,  self.mem.localcurrency)
            for i in self.mem.data.investments_active().arr:
                if i.product.leveraged==a:
                    if self.radCurrent.isChecked():
                        total=total+i.balance().local()
                    else:
                        total=total+i.invertido().local()
            if a.id==0:#Accounts
                total=total+self.accounts
            if total.isGTZero():
                labels.append(a.name)
                data.append(total.amount)
                explode.append(0)
            sumtotal=sumtotal+total
        if self.radCurrent.isChecked():    
            self.canvasApalancado.ax.set_title(self.tr("Investment current balance by leverage"), fontsize=30, fontweight="bold", y=1.02)   
        else:
            self.canvasApalancado.ax.set_title(self.tr("Invested balance by leverage"), fontsize=30, fontweight="bold", y=1.02)   
        self.canvasApalancado.ax.annotate(xy=(5, 5), xycoords="figure pixels",  s=self.tr("Total: {0}".format(sumtotal)))
        self.canvasApalancado.mydraw(data, labels,  explode)  
        
    def scriptCountry(self):
        self.canvasCountry.clearContents()
        labels=[]
        data=[]
        explode=[]
        sumtotal=Money(self.mem, 0, self.mem.localcurrency)
                
        for c in self.mem.countries.arr:
            total=Money(self.mem, 0,  self.mem.localcurrency)
            for i in self.mem.data.investments_active().arr:
                if i.product.stockmarket.country==c:
                    if self.radCurrent.isChecked():
                        total=total+i.balance().local()
                    else:
                        total=total+i.invertido().local()
            if total.isGTZero():
                labels.append(c.name)
                data.append(total.amount)
                explode.append(0)
            sumtotal=sumtotal+total
        if self.radCurrent.isChecked():    
            self.canvasCountry.ax.set_title(self.tr("Investment current balance by country"), fontsize=30, fontweight="bold", y=1.02)   
        else:
            self.canvasCountry.ax.set_title(self.tr("Invested balance by country"), fontsize=30, fontweight="bold", y=1.02)   
        self.canvasCountry.ax.annotate(xy=(5, 5), xycoords="figure pixels",  s=self.tr("Total: {0}".format(sumtotal)))
        self.canvasCountry.mydraw(data, labels,  explode)  

    def scriptProduct(self):
        self.canvasProduct.clearContents()
        labels=[]
        data=[]
        explode=[]
        sumtotal=Money(self.mem, 0, self.mem.localcurrency)
            
        #Genera SetInvestments con distinct products
        invs=self.mem.data.investments_active().setInvestments_merging_investments_with_same_product_merging_operations()
        invs.order_by_balance()
        for i in invs.arr:
            labels.append(i.name.replace("Investment merging operations of ", "").replace(" (FIFO)", ""))
            if self.radCurrent.isChecked():
                saldo=i.balance().local()
            else:
                saldo=i.invertido().local()
            data.append(saldo.amount)
            explode.append(0)
            sumtotal=sumtotal+saldo 
        sumtotal=sumtotal+self.accounts
        labels.append(self.tr("Accounts"))
        data.append(self.accounts.amount)
        explode.append(0.15)            
        
        if self.radCurrent.isChecked():    
            self.canvasProduct.ax.set_title(self.tr("Investment current balance by product"), fontsize=30, fontweight="bold", y=1.02)   
        else:
            self.canvasProduct.ax.set_title(self.tr("Invested balance by product"), fontsize=30, fontweight="bold", y=1.02)   
        self.canvasProduct.ax.annotate(xy=(5, 5), xycoords="figure pixels",  s=self.tr("Total: {0}".format(sumtotal)))
        self.canvasProduct.mydraw(data, labels,  explode)  
