import datetime
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMenu, QWidget, QTableWidgetItem, QDialog, QVBoxLayout
from xulpymoney.ui.Ui_wdgIndexRange import Ui_wdgIndexRange
from xulpymoney.libxulpymoney import Assets, Percentage
from xulpymoney.libxulpymoneyfunctions import qcenter
from xulpymoney.libxulpymoneytypes import eProductType,  eQColor
from xulpymoney.ui.frmProductReport import frmProductReport
from xulpymoney.ui.frmQuotesIBM import frmQuotesIBM
from xulpymoney.ui.wdgCalculator import wdgCalculator
from decimal import Decimal

class Range:
    def __init__(self, product,  bottom , top, price):
        """Calcula los rangos
        price, es el precio puede ser pasado el ´ultimo o el pen´ultimo"""
        self.product=product
        self.bottom=bottom
        self.top=top
        self.middle=Decimal((self.bottom+self.top)/2)
        self.current=price
        
    def currentPriceBottomVariation(self):
        """Calcs variation percentage from current price to bottom price"""
        return  Percentage(self.bottom-self.current,  self.current)
        
    def currentPriceTopVariation(self):
        return  Percentage(self.top-self.current, self.current)
    
    def currentPriceMiddleVariation(self):
        return  Percentage(self.middle-self.current, self.current)
        
    def textBottom(self):
        """Used to action text"""
        return ("Bottom: {0}. Variation: {1}".format(self.product.currency.string(self.bottom), self.currentPriceBottomVariation()))

    def textMiddle(self):
        """Used to action text"""
        return ("Middle: {0}. Variation: {1}".format(self.product.currency.string(self.middle), self.currentPriceMiddleVariation()))

    def textTop(self):
        """Used to action text"""
        return ("Top: {0}. Variation: {1}".format(self.product.currency.string(self.top), self.currentPriceTopVariation()))

class wdgIndexRange(QWidget, Ui_wdgIndexRange):
    def __init__(self,mem, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
         
        
        self.benchmark=self.mem.data.benchmark
        self.table.settings(self.mem, "wdgIndexRange")
        self.table.setVerticalHeaderHeight(None)#Must be after settings
                
        self.spin.setValue(float(self.mem.settingsdb.value("wdgIndexRange/spin", "2")))
        self.txtInvertir.setText(Decimal(self.mem.settingsdb.value("wdgIndexRange/invertir", "10000")))
        self.txtMinimo.setText(Decimal(self.mem.settingsdb.value("wdgIndexRange/minimo", "1000")))        
        
        self.cmbBenchmarkCurrent_load()
        self.load_data()
        
        self.selRange=None#Range() in right click
        
    def cmbBenchmarkCurrent_load(self):       
        if self.benchmark:
            self.cmbBenchmarkCurrent.clear() 
            self.cmbBenchmarkCurrent.addItem(self.tr("Benchmark penultimate price ({}) is {}".format(str(self.benchmark.result.basic.penultimate.datetime)[:16], self.benchmark.currency.string(self.benchmark.result.basic.penultimate.quote))))
            self.cmbBenchmarkCurrent.addItem(self.tr("Benchmark last price ({}) is {}. Last daily variation: {}.".format(str(self.benchmark.result.basic.last.datetime)[:16], self.benchmark.currency.string(self.benchmark.result.basic.last.quote), self.benchmark.result.basic.tpc_diario()) ))
            self.cmbBenchmarkCurrent.setCurrentIndex(1)#Last price
            
    def cmbBenchmarkCurrent_price(self):
        """Returns price of Benchmark selected in combo"""
        if self.cmbBenchmarkCurrent.currentIndex()==1:
            return self.benchmark.result.basic.last.quote
        else:
            return self.benchmark.result.basic.penultimate.quote

    def load_data(self):
        def inversiones(arr,min,max):
            resultado=""
            for i in arr:
                if i[0]>=min and i[0]<max:
                    o=i[1]
                    resultado=resultado+ self.tr("{0} {1} ({2}): {3} shares of {4} = {5}\n".format(str(o.datetime)[:16], o.investment.name, o.investment.account.name, round(o.shares, 0),  o.price(type=1), o.gross(type=1)))
            return resultado[:-1]
        ######################################################
        inicio=datetime.datetime.now()

        #Makes and array arr with investment current operations and sorts it
        arr=[]
        maxoper=0
        for i in self.mem.data.investments_active().arr:
                for o in i.op_actual.arr:
                    if self.cmbShowOptions.currentIndex()==0 and o.show_in_ranges==True:#Show qualified        
                        if maxoper<o.referenciaindice.quote:
                            maxoper=o.referenciaindice.quote
                        arr.append((o.referenciaindice.quote, o))                    
                    elif self.cmbShowOptions.currentIndex()==1 and i.product.type.id in (eProductType.Share, eProductType.Warrant, eProductType.ETF):            #Shares, Warrants, ETF
                        if maxoper<o.referenciaindice.quote:
                            maxoper=o.referenciaindice.quote
                        arr.append((o.referenciaindice.quote, o))             
                    elif self.cmbShowOptions.currentIndex()==2 and i.product.type.id in (eProductType.PrivateBond, eProductType.PublicBond):            #Bonds
                        if maxoper<o.referenciaindice.quote:
                            maxoper=o.referenciaindice.quote
                        arr.append((o.referenciaindice.quote, o))             
                    elif self.cmbShowOptions.currentIndex()==3 and i.product.type.id in (eProductType.Fund, ):            #Funds
                        if maxoper<o.referenciaindice.quote:
                            maxoper=o.referenciaindice.quote
                        arr.append((o.referenciaindice.quote, o))       
                    elif self.cmbShowOptions.currentIndex()==4:            
                        if maxoper<o.referenciaindice.quote:
                            maxoper=o.referenciaindice.quote
                        arr.append((o.referenciaindice.quote, o))             
        arr=sorted(arr, key=lambda row: row[1].datetime,  reverse=False) 
        
        #Makes and array from  minimum to benchmark maximum + 2% to minimum
        ranges=[]       
        if maxoper==0:##NO hay operinvestments
            maximo=self.cmbBenchmarkCurrent_price()*(1+2*Decimal(self.spin.value()/100))
        else:
            maximo=maxoper*(1+2*Decimal(self.spin.value()/100))##1.04 en caso de 2
        minimo=self.txtMinimo.decimal()
        PuntRange=minimo
        while PuntRange<maximo:
            ranges.insert(0, PuntRange)
            PuntRange=PuntRange*(1+Decimal(self.spin.value()/100))
    
        #Calculate zero risk assests and range number covered
        zeroriskplusbonds=Assets(self.mem).patrimonio_riesgo_cero(self.mem.data.investments_active(), datetime.date.today()).amount# +Assets(self.mem).saldo_todas_inversiones_bonds(datetime.date.today()).amount
        rangescovered=int(zeroriskplusbonds/self.txtInvertir.decimal())
        
        #Iterates all ranges and prints table
        self.table.applySettings()
        self.table.clearContents()
        self.table.setRowCount(len(ranges))
        colorized=0
        for i, r in enumerate(ranges):###De mayor a menor
            top=r*(1+Decimal(self.spin.value()/100))
            bottom=r
            self.table.setItem(i, 0,qcenter("{}-{}".format(int(bottom), int(top))))
            self.table.setItem(i, 1,QTableWidgetItem(inversiones(arr, bottom, top)))
            if bottom<self.cmbBenchmarkCurrent_price():
                if self.cmbBenchmarkCurrent_price()<=top: ##Colorize current price
                    self.table.item(i, 0).setBackground(eQColor.Red)
                if colorized<=rangescovered:
                    self.table.item(i, 1).setBackground(eQColor.Green)
                    colorized=colorized+1

        #Prints label
        self.lblTotal.setText(self.tr("{} green colorized ranges of {} benchmark are covered by zero risk and bonds balance ({}).").format(colorized, self.benchmark.name, self.mem.localcurrency.string(zeroriskplusbonds)))
        print ("wdgIndexRange > load_data: {0}".format(datetime.datetime.now()-inicio))

    def on_cmd_pressed(self):
        self.mem.settingsdb.setValue("wdgIndexRange/spin", self.spin.value())
        self.mem.settingsdb.setValue("wdgIndexRange/invertir", self.txtInvertir.text())
        self.mem.settingsdb.setValue("wdgIndexRange/minimo", self.txtMinimo.text())
        self.load_data()

    @pyqtSlot(int)  
    def on_cmbBenchmarkCurrent_currentIndexChanged(self, index):
        self.load_data()
        
    def on_cmbShowOptions_currentIndexChanged(self, index):
        self.load_data()

    def on_cmdIRAnalisis_pressed(self):
        w=frmProductReport(self.mem, self.benchmark, None,  self)
        w.exec_()
        
    def on_cmdIRInsertar_pressed(self):
        w=frmQuotesIBM(self.mem, self.benchmark, None,  self)
        w.exec_() 
        self.benchmark.needStatus(2, downgrade_to=0)
        self.cmbBenchmarkCurrent_load()
        self.load_data()

    def on_table_customContextMenuRequested(self,  pos):
        if self.range!=None:
            self.actionBottom.setText(self.range.textBottom())
            self.actionTop.setText(self.range.textTop())
            self.actionMiddle.setText(self.range.textMiddle())
            menu=QMenu()
            menu.addAction(self.actionTop)
            menu.addAction(self.actionMiddle)   
            menu.addAction(self.actionBottom)
            menu.exec_(self.table.mapToGlobal(pos))

    def on_table_itemSelectionChanged(self):
        try:
            for i in self.table.selectedItems():#itera por cada item no row.
                if i.column()==0:
                    self.range=Range(self.benchmark, int(i.text().split("-")[0]), int(i.text().split("-")[1]), self.cmbBenchmarkCurrent_price())
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
        
