from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget, QDialog, QVBoxLayout
from datetime import datetime, date, timedelta
from xulpymoney.ui.myqtablewidget import mqtw
from xulpymoney.ui.Ui_wdgProductsComparation import Ui_wdgProductsComparation
from xulpymoney.datetime_functions import dtaware_day_end_from_date
from xulpymoney.objects.productcomparation import ProductComparation, ProductComparationManager_from_settingsdb
from xulpymoney.ui.myqwidgets import qmessagebox, qmessagebox_developing


class wdgProductsComparation(QWidget, Ui_wdgProductsComparation):
    def __init__(self, mem,  product1=None,  product2=None, parent = None, name = None):
        QWidget.__init__(self,  parent)
        self.setupUi(self)
        self.mem=mem
        self.parent=parent
        
        self.pcmanager=ProductComparationManager_from_settingsdb(self.mem)
        self.cmbPairs_refresh()

        if product1 is None:
            product1=self.mem.data.products.find_by_id(int(self.mem.settings.value("wdgProductsComparation/product1", "79228")))
        
        if product2 is None:
            product2=self.mem.data.products.find_by_id(int(self.mem.settings.value("wdgProductsComparation/product2", "79329")))

        self.selector1.setupUi(self.mem)
        self.selector1.label.setText(self.tr("Select a product to compare"))
        self.selector1.setSelected(product1)
        
        self.selector2.setupUi(self.mem)
        self.selector2.label.setText(self.tr("Select a product to compare"))
        self.selector2.setSelected(product2)

        self.viewCompare.setSettings(self.mem.settings, "wdgProductsComparation", "viewCompare")
        self.viewScatter.setSettings(self.mem.settings, "wdgProductsComparation", "viewScatter")
        self.viewTwoAxis.setSettings(self.mem.settings, "wdgProductsComparation", "viewTwoAxis")

        self.cmbCompareTypes.setCurrentIndex(int(self.mem.settings.value("wdgProductsComparation/cmbCompareTypes", "0")))
        self.comparation=None
        self.__hide_or_show_views()

    def cmbPairs_refresh(self, selected=None):
        self.pcmanager.save_to_settingsdb()
        self.pcmanager=ProductComparationManager_from_settingsdb(self.mem)
        self.pcmanager.qcombobox(self.cmbPairs, selected=selected, id_attr=None,  name_attr=None, needtoselect=True)

    def on_cmdPairsNew_released(self):
        if self.selector1.selected is None or self.selector2.selected is None:
            qmessagebox(self.tr("You need to select both products"))
            return
        p=ProductComparation(self.mem, self.selector1.selected, self.selector2.selected)
        if p in self.pcmanager:
            qmessagebox(self.tr("This pair is already added"))
            return 
        self.pcmanager.append(p)
        self.cmbPairs_refresh(p)

    def on_cmdPairsDelete_released(self):
        self.pcmanager.selected=self.pcmanager.find_by_id_builtin(self.cmbPairs.itemData(self.cmbPairs.currentIndex()))
        if self.pcmanager.selected is not None:
            self.pcmanager.remove(self.pcmanager.selected)
            self.cmbPairs_refresh()
        else:
            qmessagebox(self.tr("You must select a pair"))
        
    @pyqtSlot(int)
    def on_cmbPairs_currentIndexChanged(self, index):
        self.pcmanager.selected=self.pcmanager.find_by_id_builtin(self.cmbPairs.itemData(self.cmbPairs.currentIndex()))
        if self.pcmanager.selected is not None:
            self.selector1.setSelected(self.pcmanager.selected.product1)
            self.selector2.setSelected(self.pcmanager.selected.product2)


    def __hide_or_show_views(self):
        if self.cmbCompareTypes.currentIndex() in (3, 4, 5, 6):
            self.viewCompare.show()
            self.viewScatter.hide()
            self.viewTwoAxis.hide()
        elif self.cmbCompareTypes.currentIndex() in (0, ):
            self.viewCompare.hide()
            self.viewScatter.hide()
            self.viewTwoAxis.show()
        elif self.cmbCompareTypes.currentIndex() in (7, 8):
            self.viewCompare.show()
            self.viewScatter.hide()
            self.viewTwoAxis.show()
        elif self.cmbCompareTypes.currentIndex() in (1, 2):
            self.viewCompare.hide()
            self.viewScatter.show()
            self.viewTwoAxis.hide()
            
    def on_cmdSwap_released(self):
        tmp=self.selector1.selected
        self.selector1.setSelected(self.selector2.selected)
        self.selector2.setSelected(tmp)

    def on_cmdReport_released(self):
        qmessagebox_developing()

    def on_cmdComparation_released(self):
        inicio=datetime.now()
        if self.selector1.selected is None or self.selector2.selected is None:
            qmessagebox(self.tr("You must select a product to compare with"))
            return
        self.comparation=ProductComparation(self.mem, self.selector1.selected, self.selector2.selected)

        if self.comparation.canBeMade()==False:
            qmessagebox(self.tr("Comparation can't be made."))
            return

        self.deCompare.setMinimumDate(self.comparation.dates()[0])
        self.deCompare.setMaximumDate(self.comparation.dates()[len(self.comparation.dates())-1-1])#Es menos 2, ya que hay alguna funcion de comparation que lo necesita
        self.comparation.setFromDate(self.deCompare.date())

        self.__hide_or_show_views()
        
        if self.cmbCompareTypes.currentIndex() in (0, 7, 8):#Not changed data        
            self.viewTwoAxis.clear()
            ls1=self.viewTwoAxis.ts.appendTemporalSeries(self.comparation.product1.name.upper())#Line seies
            ls2=self.viewTwoAxis.ts.appendTemporalSeriesAxis2(self.comparation.product2.name.upper())#Line seies

            dates=self.comparation.dates()
            closes1=self.comparation.product1Closes()
            closes2=self.comparation.product2Closes()
            for i,  date_ in enumerate(dates):
                self.viewTwoAxis.ts.appendTemporalSeriesData(ls1, dtaware_day_end_from_date(date_, self.mem.localzone_name) , closes1[i])
                self.viewTwoAxis.ts.appendTemporalSeriesDataAxis2(ls2, dtaware_day_end_from_date(date_, self.mem.localzone_name) , closes2[i])
            self.viewTwoAxis.display()


        if self.cmbCompareTypes.currentIndex()==1:#Scatter prices
            self.viewScatter.clear()
            self.viewScatter.scatter.setTitle("Scatter chart")
            self.viewScatter.scatter.appendScatterSeries("Correlation", self.comparation.product1Closes(), self.comparation.product2Closes())
            self.viewScatter.scatter.setXFormat("float", self.comparation.product1.name)
            self.viewScatter.scatter.setYFormat("float", self.comparation.product2.name)
            self.viewScatter.display()
            
            
        if self.cmbCompareTypes.currentIndex()==2:#Scatter daily gains percentage
            self.viewScatter.clear()
            self.viewScatter.scatter.setTitle("Scatter chart")
            self.viewScatter.scatter.appendScatterSeries("Correlation", self.comparation.product1PercentageEvolution(), self.comparation.product2PercentageEvolution())
            self.viewScatter.scatter.setXFormat("float", self.comparation.product1.name)
            self.viewScatter.scatter.setYFormat("float", self.comparation.product2.name)
            self.viewScatter.display()


        if self.cmbCompareTypes.currentIndex()==3:#Controlling percentage evolution.
            self.viewCompare.clear()
            ls1=self.viewCompare.ts.appendTemporalSeries(self.comparation.product1.name.upper())#Line seies
            ls2=self.viewCompare.ts.appendTemporalSeries(self.comparation.product2.name.upper())#Line seies
            dates=self.comparation.dates()
            closes1=self.comparation.product1PercentageFromFirstProduct2Price()
            closes2=self.comparation.product2Closes()
            for i,  date_ in enumerate(dates):
                self.viewCompare.ts.appendTemporalSeriesData(ls1, dtaware_day_end_from_date(date_, self.mem.localzone_name) , closes1[i])
                self.viewCompare.ts.appendTemporalSeriesData(ls2, dtaware_day_end_from_date(date_, self.mem.localzone_name) , closes2[i])
            self.viewCompare.display()


        if self.cmbCompareTypes.currentIndex()==4:#Controlling percentage evolution reducing leverage.
            self.viewCompare.clear()
            ls1=self.viewCompare.ts.appendTemporalSeries(self.comparation.product1.name.upper())#Line seies
            ls2=self.viewCompare.ts.appendTemporalSeries(self.comparation.product2.name.upper())#Line seies
            dates=self.comparation.dates()
            closes1=self.comparation.product1PercentageFromFirstProduct2PriceLeveragedReduced()
            closes2=self.comparation.product2Closes()
            for i,  date_ in enumerate(dates):
                self.viewCompare.ts.appendTemporalSeriesData(ls1, dtaware_day_end_from_date(date_, self.mem.localzone_name) , closes1[i])
                self.viewCompare.ts.appendTemporalSeriesData(ls2, dtaware_day_end_from_date(date_, self.mem.localzone_name) , closes2[i])
            self.viewCompare.display()


        if self.cmbCompareTypes.currentIndex()==5:#Controlling inverse percentage evolution.
            self.viewCompare.clear()
            ls1=self.viewCompare.ts.appendTemporalSeries(self.comparation.product1.name.upper())#Line seies
            ls2=self.viewCompare.ts.appendTemporalSeries(self.comparation.product2.name.upper())#Line seies
            dates=self.comparation.dates()
            closes1=self.comparation.product1PercentageFromFirstProduct2InversePrice()
            closes2=self.comparation.product2Closes()
            for i,  date_ in enumerate(dates):
                self.viewCompare.ts.appendTemporalSeriesData(ls1, dtaware_day_end_from_date(date_, self.mem.localzone_name) , closes1[i])
                self.viewCompare.ts.appendTemporalSeriesData(ls2, dtaware_day_end_from_date(date_, self.mem.localzone_name) , closes2[i])
            self.viewCompare.display()
        
        
        if self.cmbCompareTypes.currentIndex()==6:#Controlling inverse percentage evolution reducing leverage.
            self.viewCompare.clear()
            ls1=self.viewCompare.ts.appendTemporalSeries(self.comparation.product1.name.upper())#Line seies
            ls2=self.viewCompare.ts.appendTemporalSeries(self.comparation.product2.name.upper())#Line seies
            dates=self.comparation.dates()
            closes1=self.comparation.product1PercentageFromFirstProduct2InversePriceLeveragedReduced()
            closes2=self.comparation.product2Closes()
            for i,  date_ in enumerate(dates):
                self.viewCompare.ts.appendTemporalSeriesData(ls1, dtaware_day_end_from_date(date_, self.mem.localzone_name) , closes1[i])
                self.viewCompare.ts.appendTemporalSeriesData(ls2, dtaware_day_end_from_date(date_, self.mem.localzone_name) , closes2[i])
            self.viewCompare.display()

        if self.cmbCompareTypes.currentIndex()==7:# Spreading prices joining first scaling.
            self.viewCompare.clear()
            ls=self.viewCompare.ts.appendTemporalSeries(self.tr("Spread of {} - {}").format(self.comparation.product1.name, self.comparation.product2.name))#Line seies
            dates=self.comparation.dates()
            closes1=self.comparation.product1Closes()
            closes2=self.comparation.product2Closes()
            multiplier=closes2[0]/closes1[0]
            for i,  date_ in enumerate(dates):
                diff=closes2[i]-closes1[i]*multiplier
                self.viewCompare.ts.appendTemporalSeriesData(ls, dtaware_day_end_from_date(date_, self.mem.localzone_name) , diff)
            self.viewCompare.display()


        if self.cmbCompareTypes.currentIndex()==8:# Price ratio A/B
            self.viewCompare.clear()
            ls=self.viewCompare.ts.appendTemporalSeries(self.tr("Price Ratio of {} / {}").format(self.comparation.product1.name, self.comparation.product2.name))#Line seies
            dates=self.comparation.dates()
            closes1=self.comparation.product1Closes()
            closes2=self.comparation.product2Closes()
            for i,  date_ in enumerate(dates):
                ratio=closes1[i]/closes2[i]
                self.viewCompare.ts.appendTemporalSeriesData(ls, dtaware_day_end_from_date(date_, self.mem.localzone_name) , ratio)
            self.viewCompare.display()

        self.mem.settings.setValue("wdgProductsComparation/product1", str(self.comparation.product1.id))
        self.mem.settings.setValue("wdgProductsComparation/product2", str(self.comparation.product2.id))
        self.mem.settings.setValue("wdgProductsComparation/cmbCompareTypes", str(self.cmbCompareTypes.currentIndex()))
        self.mem.settings.sync()

        self.lblCorrelation.setText(self.comparation.correlacion_lineal())

        print ("Comparation took {}".format(datetime.now()-inicio))


    @pyqtSlot(int) 
    def on_cmbDateSelector_currentIndexChanged(self, index):
        today=date.today()
        if index==0: #Last 7 days
            self.deCompare.setDate(today-timedelta(days=7))
        elif index==1: #Last 30 days
            self.deCompare.setDate(today-timedelta(days=30))
        elif index==2: #Last 90 days
            self.deCompare.setDate(today-timedelta(days=90))
        elif index==3: #Last 365 days
            self.deCompare.setDate(today-timedelta(days=365))
        elif index==4: #Last 3 years
            self.deCompare.setDate(today-timedelta(days=365*3))
        elif index==5: #Last 10 years
            self.deCompare.setDate(today-timedelta(days=365*10))
        elif index==6: #All
            self.deCompare.setDate(date(1900, 1, 1))

    def on_cmdComparationData_released(self):
        if self.comparation==None:
            qmessagebox(self.tr("You need to compare products first"))
            return
        d=QDialog(self)
        d.resize(800, 600)
        d.setWindowTitle(self.tr("Comparation data table"))
        mqtwQuotes=mqtw(d)
        mqtwQuotes.setSettings(self.mem.settings,"wdgProductsComparation" , "mqtwQuotes")
        mqtwQuotes.showSearchOptions(True)
        self.comparation.myqtablewidget(mqtwQuotes)
        lay = QVBoxLayout(d)
        lay.addWidget(mqtwQuotes)
        d.show()
