import datetime
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMenu, QWidget, QTableWidgetItem, QDialog, QVBoxLayout
from xulpymoney.ui.Ui_wdgProductRange import Ui_wdgProductRange
from xulpymoney.objects.assets import Assets
from xulpymoney.objects.productrange import ProductRangeManager
from xulpymoney.objects.percentage import Percentage
from xulpymoney.ui.myqtablewidget import qcenter
from xulpymoney.libxulpymoneytypes import eProductType,  eQColor
from xulpymoney.ui.frmProductReport import frmProductReport
from xulpymoney.ui.frmQuotesIBM import frmQuotesIBM
from xulpymoney.ui.wdgCalculator import wdgCalculator
from decimal import Decimal

class wdgProductRange(QWidget, Ui_wdgProductRange):
    def __init__(self,mem, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
         
        
        self.product=self.mem.data.products.find_by_id(79228)
        
        self.prm=ProductRangeManager(self.mem, self.product, Percentage(5, 100), Percentage(15, 100))

        
        
        self.mqtw.settings(self.mem.settings, "wdgProductRange", "mqtw")
        self.mqtw.table.customContextMenuRequested.connect(self.on_mqtw_customContextMenuRequested)
        self.mqtw.table.itemSelectionChanged.connect(self.on_mqtw_itemSelectionChanged)
        self.mqtw.setVerticalHeaderHeight(None)#Must be after settings
                
        self.spin.setValue(float(self.mem.settingsdb.value("wdgProductRange/spin", "2")))
        self.txtInvertir.setText(Decimal(self.mem.settingsdb.value("wdgProductRange/invertir", "10000")))
        self.txtMinimo.setText(Decimal(self.mem.settingsdb.value("wdgProductRange/minimo", "1000")))        
        
        self.cmbBenchmarkCurrent_load()
        self.load_data()
        
        self.selRange=None#Range() in right click
        
    def cmbBenchmarkCurrent_load(self):       
        if self.product:
            self.cmbBenchmarkCurrent.clear() 
            self.cmbBenchmarkCurrent.addItem(self.tr("Benchmark penultimate price ({}) is {}".format(str(self.product.result.basic.penultimate.datetime)[:16], self.product.money(self.product.result.basic.penultimate.quote))))
            self.cmbBenchmarkCurrent.addItem(self.tr("Benchmark last price ({}) is {}. Last daily variation: {}.".format(str(self.product.result.basic.last.datetime)[:16], self.product.money(self.product.result.basic.last.quote), self.product.result.basic.tpc_diario()) ))
            self.cmbBenchmarkCurrent.setCurrentIndex(1)#Last price
            
    def cmbBenchmarkCurrent_price(self):
        """Returns price of Benchmark selected in combo"""
        if self.cmbBenchmarkCurrent.currentIndex()==1:
            return self.product.result.basic.last.quote
        else:
            return self.product.result.basic.penultimate.quote

    def load_data(self):
        
        self.prm.mqtw(self.mqtw)
        #Prints label
#        self.lblTotal.setText(self.tr("{} green colorized ranges of {} benchmark are covered by zero risk and bonds balance ({}).").format(colorized, self.product.name, self.mem.localmoney(zeroriskplusbonds)))
#        print ("wdgProductRange > load_data: {0}".format(datetime.datetime.now()-inicio))

    def on_cmd_pressed(self):
        self.mem.settingsdb.setValue("wdgProductRange/spin", self.spin.value())
        self.mem.settingsdb.setValue("wdgProductRange/invertir", self.txtInvertir.text())
        self.mem.settingsdb.setValue("wdgProductRange/minimo", self.txtMinimo.text())
        self.load_data()

    @pyqtSlot(int)  
    def on_cmbBenchmarkCurrent_currentIndexChanged(self, index):
        self.load_data()
        
    def on_cmbShowOptions_currentIndexChanged(self, index):
        self.load_data()

    def on_cmdIRAnalisis_pressed(self):
        w=frmProductReport(self.mem, self.product, None,  self)
        w.exec_()
        
    def on_cmdIRInsertar_pressed(self):
        w=frmQuotesIBM(self.mem, self.product, None,  self)
        w.exec_() 
        self.product.needStatus(2, downgrade_to=0)
        self.cmbBenchmarkCurrent_load()
        self.load_data()

    def on_mqtw_customContextMenuRequested(self,  pos):
        if self.range!=None:
            self.actionBottom.setText(self.range.textBottom())
            self.actionTop.setText(self.range.textTop())
            self.actionMiddle.setText(self.range.textMiddle())
            menu=QMenu()
            menu.addAction(self.actionTop)
            menu.addAction(self.actionMiddle)   
            menu.addAction(self.actionBottom)
            menu.exec_(self.mqtw.table.mapToGlobal(pos))

    def on_mqtw_itemSelectionChanged(self):
        try:
            for i in self.mqtw.table.selectedItems():#itera por cada item no row.
                if i.column()==0:
                    self.range=Range(self.product, int(i.text().split("-")[0]), int(i.text().split("-")[1]), self.cmbBenchmarkCurrent_price())
        except:
            self.range=None

    @pyqtSlot() 
    def on_actionBottom_triggered(self):        
        d=QDialog(self)        
        d.setFixedSize(850, 850)
        d.setWindowTitle(self.tr("Investment calculator"))
        w=wdgCalculator(self.mem)
        w.setProduct(self.mem.data.products.find_by_id(int(self.mem.settings.value("wdgCalculator/product", "0"))))
        w.spnProductPriceVariation.setValue(self.range.currentPriceBottomVariation().value_100())
        lay = QVBoxLayout(d)
        lay.addWidget(w)
        if w.hasProducts==True:
            d.show()
        else:
            d.close()

    @pyqtSlot() 
    def on_actionTop_triggered(self):        
        d=QDialog(self)
        d.setFixedSize(850, 850)
        d.setWindowTitle(self.tr("Investment calculator"))
        w=wdgCalculator(self.mem)
        w.setProduct(self.mem.data.products.find_by_id(int(self.mem.settings.value("wdgCalculator/product", "0"))))
        w.spnProductPriceVariation.setValue(self.range.currentPriceTopVariation().value_100())
        lay = QVBoxLayout(d)
        lay.addWidget(w)
        if w.hasProducts==True:
            d.show()
        else:
            d.close()

    @pyqtSlot() 
    def on_actionMiddle_triggered(self):        
        d=QDialog(self)        
        d.setFixedSize(850, 850)
        d.setWindowTitle(self.tr("Investment calculator"))
        w=wdgCalculator(self.mem)
        w.setProduct(self.mem.data.products.find_by_id(int(self.mem.settings.value("wdgCalculator/product", "0"))))
        w.spnProductPriceVariation.setValue(self.range.currentPriceMiddleVariation().value_100())
        lay = QVBoxLayout(d)
        lay.addWidget(w)
        if w.hasProducts==True:
            d.show()
        else:
            d.close()
        
