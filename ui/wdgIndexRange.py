from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Ui_wdgIndexRange import *
from libxulpymoney import *
from frmProductReport import *
from wdgCalculator import *

class Range:
    def __init__(self, product,  bottom , top):
        """Calcula los rangos"""
        self.product=product
        self.bottom=bottom
        self.top=top
        self.middle=Decimal((self.bottom+self.top)/2)
        self.current=product.result.basic.last.quote
        
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
        
        self.quote_lastindex=None
        self.table.settings("wdgIndexRange",  self.mem)
        
        self.spin.setValue(float(self.mem.config.get_value("wdgIndexRange", "spin")))
        self.txtInvertir.setText(self.mem.config.get_value("wdgIndexRange", "txtInvertir"))
        self.txtMinimo.setText(self.mem.config.get_value("wdgIndexRange", "txtMinimo"))
        
        self.load_data()
        
        self.selRange=None#Range()#Bottom,middle,top
                    

        
    def load_data(self):
        def inversiones(arr,min,max):
            resultado=""
            for i in arr:
                if i[0]>=min and i[0]<max:
                    o=i[1]
                    resultado=resultado+ self.trUtf8("{0} {1} ({2}): {3} shares of {4} = {5}\n".format(str(o.datetime)[:16], o.inversion.name, o.inversion.cuenta.name, round(o.acciones, 0),  o.inversion.product.currency.string(o.valor_accion), o.inversion.product.currency.string(o.importe)))
            return resultado[:-1]
        inicio=datetime.datetime.now()

        arr=[]

        for i in self.mem.data.inversiones_active.arr:
            if i.product.tpc!=0 and i.product.type.id not in (7, 9):
                for o in i.op_actual.arr:
                    arr.append((o.referenciaindice.quote, o))

        arr=sorted(arr, key=lambda row: row[1].datetime,  reverse=False) 
        
        if len (arr)==0: #Peta en base de datos vacía
            return
                
        maximo= int(max(arr)[0]*(1+ Decimal(self.spin.value()/200.0)))
        riesgocero=Assets(self.mem).patrimonio_riesgo_cero(self.mem.data.inversiones_active, datetime.date.today())
        pasos=int(riesgocero/Decimal(self.txtInvertir.text()))
        last=maximo
        rangos=0
        self.table.clearContents()
        rangoindexactual=0
        indexcover=0
        while last>int(self.txtMinimo.text()):
            rangos=rangos+1
            self.table.setRowCount(rangos)
            formin=last*(1.0-(self.spin.value()/100))
            formax=last

            self.table.setItem(rangos-1, 0,qcenter(str(int(formin))+"-"+str(int(formax))))
            self.table.setItem(rangos-1, 1,QTableWidgetItem((inversiones(arr, formin, formax))))
            if self.mem.data.benchmark.result.basic.last.quote>formin and self.mem.data.benchmark.result.basic.last.quote<formax:
                self.table.item(rangos-1, 0).setBackgroundColor(QColor(255, 148, 148))
                rangoindexactual=rangos-1
            last=formin
            
        for i in range(rangos-rangoindexactual):
            if (self.table.item(rangoindexactual+i, 1).text())=="" and pasos>0:
                self.table.item(rangoindexactual+i, 1).setBackgroundColor(QColor(148, 255, 148))
#                indexcover=int(self.table.item(rangoindexactual+i, 1).text())
                pasos=pasos-1
                
        #Variación del índice hoy
        if self.mem.data.benchmark.result.basic.penultimate.quote==0 or self.mem.data.benchmark.result.basic.penultimate.quote==None:
            variacion=0
        else:
            variacion=(self.mem.data.benchmark.result.basic.last.quote-self.mem.data.benchmark.result.basic.penultimate.quote)*100/self.mem.data.benchmark.result.basic.penultimate.quote
        self.lblTotal.setText(("Tengo cubierto hasta el %d del índice de referencia (%s). Su valor a %s es %d (%.2f %%)" %( indexcover, self.mem.data.benchmark.name, self.mem.data.benchmark.result.basic.last.datetime,   int(self.mem.data.benchmark.result.basic.last.quote),  variacion)))

        print ("wdgIndexRange > load_data: {0}".format(datetime.datetime.now()-inicio))

    def on_cmd_pressed(self):
        if self.spin.value()!=float(self.mem.config.get_value("wdgIndexRange", "spin")):
            self.mem.config.set_value("wdgIndexRange", "spin", self.spin.value())
            self.mem.config.save()
        if self.txtInvertir.text()!=self.mem.config.get_value("wdgIndexRange", "txtInvertir"):
            self.mem.config.set_value("wdgIndexRange", "txtInvertir", self.txtInvertir.text())
            self.mem.config.save()
        if self.txtMinimo.text()!=self.mem.config.get_value("wdgIndexRange", "txtMinimo"):
            self.mem.config.set_value("wdgIndexRange", "txtMinimo", self.txtMinimo.text())
            self.mem.config.save()
        self.load_data()

    def on_cmdIRAnalisis_pressed(self):
        w=frmProductReport(self.mem, self.mem.data.benchmark, None,  self)
        w.exec_()
        
    def on_cmdIRInsertar_pressed(self):
        w=frmQuotesIBM(self.mem, self.mem.data.benchmark, None,  self)
        w.exec_() 
        self.mem.data.benchmark.result.basic.load_from_db()
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
                    self.range=Range(self.mem.data.benchmark, int(i.text().split("-")[0]), int(i.text().split("-")[1]))
        except:
            self.range=None

    @QtCore.pyqtSlot() 
    def on_actionBottom_activated(self):        
        d=QDialog(self)        
        d.setFixedSize(670, 670)
        d.setWindowTitle(self.trUtf8("Investment calculator"))
        w=wdgCalculator(self.mem)
        w.init__percentagevariation_amount(self.range.currentPriceBottomVariation(), self.txtInvertir.decimal())
        lay = QVBoxLayout(d)
        lay.addWidget(w)
        d.exec_()

    @QtCore.pyqtSlot() 
    def on_actionTop_activated(self):        
        d=QDialog(self)        
        d.setFixedSize(670, 670)
        d.setWindowTitle(self.trUtf8("Investment calculator"))
        w=wdgCalculator(self.mem)
        w.init__percentagevariation_amount(self.range.currentPriceTopVariation(), self.txtInvertir.decimal())
        lay = QVBoxLayout(d)
        lay.addWidget(w)
        d.exec_()

    @QtCore.pyqtSlot() 
    def on_actionMiddle_activated(self):        
        d=QDialog(self)        
        d.setFixedSize(670, 670)
        d.setWindowTitle(self.trUtf8("Investment calculator"))
        w=wdgCalculator(self.mem)
        w.init__percentagevariation_amount(self.range.currentPriceMiddleVariation(), self.txtInvertir.decimal())
        lay = QVBoxLayout(d)
        lay.addWidget(w)
        d.exec_()
        
