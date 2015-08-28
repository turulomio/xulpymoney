from PyQt5.QtCore import *
from PyQt5.QtGui import *
from Ui_wdgIndexRange import *
from libxulpymoney import *
from frmProductReport import *
from wdgCalculator import *

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
        return  (self.bottom-self.current)*100/self.current
        
    def currentPriceTopVariation(self):
        return  (self.top-self.current)*100/self.current
    
    def currentPriceMiddleVariation(self):
        return  (self.middle-self.current)*100/self.current
        
    def textBottom(self):
        """Used to action text"""
        return ("Bottom: {0}. Variation: {1}".format(self.product.currency.string(self.bottom), tpc(self.currentPriceBottomVariation())))

    def textMiddle(self):
        """Used to action text"""
        return ("Middle: {0}. Variation: {1}".format(self.product.currency.string(self.middle), tpc(self.currentPriceMiddleVariation())))

    def textTop(self):
        """Used to action text"""
        return ("Top: {0}. Variation: {1}".format(self.product.currency.string(self.top), tpc(self.currentPriceTopVariation())))

class wdgIndexRange(QWidget, Ui_wdgIndexRange):
    def __init__(self,mem, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        self.mem.data.load_inactives()
        
        self.benchmark=self.mem.data.benchmark
        self.table.settings(self.mem)
        
        self.gl_wdgIndexRange_spin=Global(self.mem, "wdgIndexRange", "spin")
        self.gl_wdgIndexRange_txtInvertir=Global(self.mem, "wdgIndexRange", "txtInvertir")
        self.gl_wdgIndexRange_txtMinimo=Global(self.mem, "wdgIndexRange", "txtMinimo")
        
        self.spin.setValue(float(self.gl_wdgIndexRange_spin.get()))
        self.txtInvertir.setText(self.gl_wdgIndexRange_txtInvertir.get())
        self.txtMinimo.setText(self.gl_wdgIndexRange_txtMinimo.get())        
        self.cmbBenchmarkCurrent_load()
        self.load_data()
        
        self.selRange=None#Range() in right click
        
    def cmbBenchmarkCurrent_load(self):       
        if self.benchmark:
            self.cmbBenchmarkCurrent.clear() 
            self.cmbBenchmarkCurrent.addItem(self.tr("Benchmark penultimate price ({}) is {}".format(str(self.benchmark.result.basic.penultimate.datetime)[:16], self.benchmark.currency.string(self.benchmark.result.basic.penultimate.quote))))
            self.cmbBenchmarkCurrent.addItem(self.tr("Benchmark last price ({}) is {}. Last dayly variation: {}.".format(str(self.benchmark.result.basic.last.datetime)[:16], self.benchmark.currency.string(self.benchmark.result.basic.last.quote),tpc(self.benchmark.result.basic.tpc_diario()) )))
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
                    resultado=resultado+ self.tr("{0} {1} ({2}): {3} shares of {4} = {5}\n".format(str(o.datetime)[:16], o.inversion.name, o.inversion.account.name, round(o.acciones, 0),  o.inversion.product.currency.string(o.valor_accion), o.inversion.product.currency.string(o.importe)))
            return resultado[:-1]
        ######################################################
        inicio=datetime.datetime.now()

        #Makes and array arr with investment current operations and sorts it
        arr=[]
        maxoper=0
        for i in self.mem.data.investments_active.arr:
                for o in i.op_actual.arr:
                    if self.cmbShowOptions.currentIndex()==0 and o.show_in_ranges==True:#Show qualified        
                        if maxoper<o.referenciaindice.quote:
                            maxoper=o.referenciaindice.quote
                        arr.append((o.referenciaindice.quote, o))                    
                    elif self.cmbShowOptions.currentIndex()==1 and i.product.type.id in (1, 4, 5):            #Shares, Warrants, ETF
                        if maxoper<o.referenciaindice.quote:
                            maxoper=o.referenciaindice.quote
                        arr.append((o.referenciaindice.quote, o))             
                    elif self.cmbShowOptions.currentIndex()==2 and i.product.type.id in (7, 8):            #Bonds
                        if maxoper<o.referenciaindice.quote:
                            maxoper=o.referenciaindice.quote
                        arr.append((o.referenciaindice.quote, o))             
                    elif self.cmbShowOptions.currentIndex()==3 and i.product.type.id in (2, ):            #Funds
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
        minimo=int(self.txtMinimo.text())
        PuntRange=minimo
        while PuntRange<maximo:
            ranges.insert(0, PuntRange)
            PuntRange=int(PuntRange*(1+(self.spin.value()/100)))
    
        #Calculate zero risk assests and range number covered
        zeroriskplusbonds=Assets(self.mem).patrimonio_riesgo_cero(self.mem.data.investments_active, datetime.date.today()) +Assets(self.mem).saldo_todas_inversiones_bonds(datetime.date.today())
        rangescovered=int(zeroriskplusbonds/self.txtInvertir.decimal())##zero risk assests
        
        #Iterates all ranges and prints table
        self.table.clearContents()
        self.table.setRowCount(len(ranges))
        colorized=0
        for i, r in enumerate(ranges):###De mayor a menor
            top=int(r*(1+(self.spin.value()/100)))
            bottom=r
            self.table.setItem(i, 0,qcenter("{}-{}".format(bottom, top)))
            self.table.setItem(i, 1,QTableWidgetItem(inversiones(arr, bottom, top)))
            if bottom<self.cmbBenchmarkCurrent_price():
                if self.cmbBenchmarkCurrent_price()<=top: ##Colorize current price
                    self.table.item(i, 0).setBackground(QColor(255, 160, 160))
                if colorized<=rangescovered:
                    self.table.item(i, 1).setBackground(QColor(160, 255, 160))
                    colorized=colorized+1

        #Prints label
        self.lblTotal.setText(self.tr("Green colorized ranges of {} benchmark are covered by zero risk and bonds balance ({}).").format(self.benchmark.name, self.mem.localcurrency.string(zeroriskplusbonds)))
        print ("wdgIndexRange > load_data: {0}".format(datetime.datetime.now()-inicio))

    def on_cmd_pressed(self):
        self.gl_wdgIndexRange_spin.set(Decimal(self.spin.value()))
        self.gl_wdgIndexRange_txtInvertir.set(self.txtInvertir.text())
        self.gl_wdgIndexRange_txtMinimo.set(self.txtMinimo.text())
        self.mem.con.commit()
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
        self.benchmark.result.basic.load_from_db()
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

    @QtCore.pyqtSlot() 
    def on_actionBottom_triggered(self):        
        d=QDialog(self)        
        d.setFixedSize(850, 850)
        d.setWindowTitle(self.tr("Investment calculator"))
        w=wdgCalculator(self.mem)
        w.init__percentagevariation_amount(self.range.currentPriceBottomVariation(), self.txtInvertir.decimal())
        lay = QVBoxLayout(d)
        lay.addWidget(w)
        if w.hasProducts==True:
            d.show()
        else:
            d.close()

    @QtCore.pyqtSlot() 
    def on_actionTop_triggered(self):        
        d=QDialog(self)
        d.setFixedSize(850, 850)
        d.setWindowTitle(self.tr("Investment calculator"))
        w=wdgCalculator(self.mem)
        w.init__percentagevariation_amount(self.range.currentPriceTopVariation(), self.txtInvertir.decimal())
        lay = QVBoxLayout(d)
        lay.addWidget(w)
        if w.hasProducts==True:
            d.show()
        else:
            d.close()

    @QtCore.pyqtSlot() 
    def on_actionMiddle_triggered(self):        
        d=QDialog(self)        
        d.setFixedSize(850, 850)
        d.setWindowTitle(self.tr("Investment calculator"))
        w=wdgCalculator(self.mem)
        w.init__percentagevariation_amount(self.range.currentPriceMiddleVariation(), self.txtInvertir.decimal())
        lay = QVBoxLayout(d)
        lay.addWidget(w)
        if w.hasProducts==True:
            d.show()
        else:
            d.close()
        
