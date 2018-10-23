import datetime
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget
from Ui_wdgProductsComparation import Ui_wdgProductsComparation
from PyQt5.QtChart import QValueAxis
from libxulpymoney import ProductComparation
from libxulpymoneyfunctions import qmessagebox,  day_end_from_date
from canvaschart import  VCTemporalSeries
class wdgProductsComparation(QWidget, Ui_wdgProductsComparation):
    def __init__(self, mem,  product1=None,  product2=None, parent = None, name = None):
        QWidget.__init__(self,  parent)
        self.setupUi(self)
        self.mem=mem
        self.parent=parent
        self.product1=product1
        self.product2=product2
        
#        self.pseCompare.setupUi(self.mem, self.investment)
#        self.pseCompare.label.setText(self.tr("Select a product to compare"))
#        self.pseCompare.setSelected(self.mem.data.benchmark)
#        self.pseCompare.selectionChanged.connect(self.load_comparation)
#        self.pseCompare.showProductButton(False)
        self.cmbCompareTypes.setCurrentIndex(0)
        self.cmbCompareTypes.currentIndexChanged.connect(self.on_my_cmbCompareTypes_currentIndexChanged)
        self.viewCompare=None
        self.deCompare.dateChanged.connect(self.load_comparation)
#        self.load_comparation()
        
        
    def load_comparation(self):
        """Loads comparation canvas"""
        if self.product.id==None: #Adding a product doesn't need to comparate products.
            return
            
        inicio=datetime.datetime.now()
        if self.pseCompare.selected==None:
            qmessagebox(self.tr("You must select a product to compare with."))
            return
        self.comparation=ProductComparation(self.mem, self.product, self.pseCompare.selected)
        if self.viewCompare!=None:
            self.viewCompare.hide()
            self.layCompareProduct.removeWidget(self.viewCompare)
        if self.comparation.canBeMade()==False:
            qmessagebox(self.tr("Comparation can't be made."))
            return
        
        self.deCompare.setMinimumDate(self.comparation.dates()[0])
        self.deCompare.setMaximumDate(self.comparation.dates()[len(self.comparation.dates())-1-1])#Es menos 2, ya que hay alguna funcion de comparation que lo necesita
        self.comparation.setFromDate(self.deCompare.date())
            
        self.viewCompare=VCTemporalSeries()
        if self.cmbCompareTypes.currentIndex()==0:#Not changed data

            ls1=self.viewCompare.appendTemporalSeries(self.comparation.product1.name.upper(), self.comparation.product1.currency)#Line seies
            ls2=self.viewCompare.appendTemporalSeries(self.comparation.product2.name.upper(), self.comparation.product1.currency)#Line seies
            dates=self.comparation.dates()
            closes1=self.comparation.product1Closes()
            closes2=self.comparation.product2Closes()
            for i,  date in enumerate(dates):
                self.viewCompare.appendTemporalSeriesData(ls1, day_end_from_date(date, self.mem.localzone) , closes1[i])
                self.viewCompare.appendTemporalSeriesData(ls2, day_end_from_date(date, self.mem.localzone) , closes2[i])
                    #        BEGIN DISPLAY)
            self.viewCompare.setChart(self.viewCompare.chart)
            self.viewCompare.setAxisFormat(self.viewCompare.axisX, self.viewCompare.minx, self.viewCompare.maxx, 1)
            self.viewCompare.setAxisFormat(self.viewCompare.axisY, min(self.comparation.product1Closes()), max(self.comparation.product1Closes()),  0)
            axis3=QValueAxis()
            self.viewCompare.chart.addAxis(self.viewCompare.axisY, Qt.AlignLeft);
            self.viewCompare.chart.addAxis(self.viewCompare.axisX, Qt.AlignBottom);
            self.viewCompare.chart.addAxis(axis3, Qt.AlignRight)

            self.viewCompare.chart.addSeries(ls1)
            ls1.attachAxis(self.viewCompare.axisX)
            ls1.attachAxis(self.viewCompare.axisY)
            self.viewCompare.axisY.setRange(min(self.comparation.product1Closes()), max(self.comparation.product1Closes()))
            
            
            self.viewCompare.chart.addSeries(ls2)
            ls2.attachAxis(self.viewCompare.axisX)
            ls2.attachAxis(axis3)
            axis3.setRange (min(self.comparation.product2Closes()), max(self.comparation.product2Closes()))
            
            
            if self.viewCompare._allowHideSeries==True:
                for marker in self.viewCompare.chart.legend().markers():
                    try:
                        marker.clicked.disconnect()
                    except:
                        pass
                    marker.clicked.connect(self.viewCompare.on_marker_clicked)
            
            
            self.viewCompare.repaint()
            ###END DISPLAY

        elif self.cmbCompareTypes.currentIndex()==1:#Scatter
            pass

        elif self.cmbCompareTypes.currentIndex()==2:#Controlling percentage evolution.

            ls1=self.viewCompare.appendTemporalSeries(self.comparation.product1.name.upper(), self.comparation.product1.currency)#Line seies
            ls2=self.viewCompare.appendTemporalSeries(self.comparation.product2.name.upper(), self.comparation.product1.currency)#Line seies
            dates=self.comparation.dates()
            closes1=self.comparation.product1PercentageFromFirstProduct2Price()
            closes2=self.comparation.product2Closes()
            for i,  date in enumerate(dates):
                self.viewCompare.appendTemporalSeriesData(ls1, day_end_from_date(date, self.mem.localzone) , closes1[i])
                self.viewCompare.appendTemporalSeriesData(ls2, day_end_from_date(date, self.mem.localzone) , closes2[i])
            self.viewCompare.display()
        elif self.cmbCompareTypes.currentIndex()==3:#Controlling percentage evolution reducing leverage.
            ls1=self.viewCompare.appendTemporalSeries(self.comparation.product1.name.upper(), self.comparation.product1.currency)#Line seies
            ls2=self.viewCompare.appendTemporalSeries(self.comparation.product2.name.upper(), self.comparation.product1.currency)#Line seies
            dates=self.comparation.dates()
            closes1=self.comparation.product1PercentageFromFirstProduct2PriceLeveragedReduced()
            closes2=self.comparation.product2Closes()
            for i,  date in enumerate(dates):
                self.viewCompare.appendTemporalSeriesData(ls1, day_end_from_date(date, self.mem.localzone) , closes1[i])
                self.viewCompare.appendTemporalSeriesData(ls2, day_end_from_date(date, self.mem.localzone) , closes2[i])
            self.viewCompare.display()
        elif self.cmbCompareTypes.currentIndex()==4:#Controlling inverse percentage evolution.
            ls1=self.viewCompare.appendTemporalSeries(self.comparation.product1.name.upper(), self.comparation.product1.currency)#Line seies
            ls2=self.viewCompare.appendTemporalSeries(self.comparation.product2.name.upper(), self.comparation.product1.currency)#Line seies
            dates=self.comparation.dates()
            closes1=self.comparation.product1PercentageFromFirstProduct2InversePrice()
            closes2=self.comparation.product2Closes()
            for i,  date in enumerate(dates):
                self.viewCompare.appendTemporalSeriesData(ls1, day_end_from_date(date, self.mem.localzone) , closes1[i])
                self.viewCompare.appendTemporalSeriesData(ls2, day_end_from_date(date, self.mem.localzone) , closes2[i])
            self.viewCompare.display()
        elif self.cmbCompareTypes.currentIndex()==5:#Controlling inverse percentage evolution reducing leverage.
            ls1=self.viewCompare.appendTemporalSeries(self.comparation.product1.name.upper(), self.comparation.product1.currency)#Line seies
            ls2=self.viewCompare.appendTemporalSeries(self.comparation.product2.name.upper(), self.comparation.product1.currency)#Line seies
            dates=self.comparation.dates()
            closes1=self.comparation.product1PercentageFromFirstProduct2InversePriceLeveragedReduced()
            closes2=self.comparation.product2Closes()
            for i,  date in enumerate(dates):
                self.viewCompare.appendTemporalSeriesData(ls1, day_end_from_date(date, self.mem.localzone) , closes1[i])
                self.viewCompare.appendTemporalSeriesData(ls2, day_end_from_date(date, self.mem.localzone) , closes2[i])
            self.viewCompare.display()

        
        self.layCompareProduct.addWidget(self.viewCompare)
        print ("Comparation took {}".format(datetime.datetime.now()-inicio))

    def on_my_cmbCompareTypes_currentIndexChanged(self, int):
        self.load_comparation()
