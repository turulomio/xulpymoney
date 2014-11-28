from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Ui_wdgIndexRangeSimulator import *
from libxulpymoney import *

class wdgIndexRangeSimulator(QWidget, Ui_wdgIndexRangeSimulator):
    def __init__(self,mem, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.con=mem.con
        self.mem=mem
        self.tblRanges.settings("wdgIndexRangeSimulator",  self.mem)
        
#        self.spin.setValue(float(self.mem.config.get_value("wdgIndexRangeSimulator", "spin")))
#        self.txtInvertir.setText(self.mem.config.get_value("wdgIndexRangeSimulator", "txtInvertir"))
#        self.txtMinimo.setText(self.mem.config.get_value("wdgIndexRangeSimulator", "txtMinimo"))
        
        self.benchmark=mem.data.benchmark
        self.banks=SetBanks(self.mem)
        self.accounts=SetAccounts(self.mem, self.banks)
        self.products=SetProducts(self.mem)
        self.investments=SetInvestments(self.mem, self.accounts, self.products,self.benchmark )
        
        self.load_data()
        

    def load_data(self):
        def inversiones(arr,min,max):
            resultado=""
            for i in arr:
                if i[0]>=min and i[0]<max:
                    o=i[1]
                    resultado=resultado+ self.trUtf8("{0} {1} ({2}): {3} shares of {4} = {5}\n".format(str(o.datetime)[:16], o.inversion.name, o.inversion.cuenta.name, round(o.acciones, 0),  o.inversion.product.currency.string(o.valor_accion), o.inversion.product.currency.string(o.importe)))
            return resultado[:-1]
        ######################################################
        
        inicio=datetime.datetime.now()

        #Makes and array arr with investment current operations and sorts it
        arr=[]
        for i in self.investments.arr:
            for o in i.op_actual.arr:
                arr.append((o.referenciaindice.quote, o))
        arr=sorted(arr, key=lambda row: row[1].datetime,  reverse=False) 

        #Makes and array from benchmark maximum + 4% to minimum
        ranges=[]
        cur=self.mem.con.cursor()
        cur.execute("select max(quote) from quotes where id=%s;", (self.benchmark.id, ))
        maximo= int( cur.fetchone()[0]*Decimal(1.04))
        cur.close()
        minimo=int(self.txtLowest.text())
        PuntRange=maximo
        while PuntRange>minimo:
            ranges.append(PuntRange)
            PuntRange=int(PuntRange*(1-(self.spin.value()/100)))
    
        
        #Iterates all ranges and prints tblRanges
        self.tblRanges.clearContents()
        self.tblRanges.setRowCount(len(ranges))
        colorized=0
        benchmarkrange=0#Int will point to the range of the benchmark
        for i, r in enumerate(ranges):
            top=r
            bottom=int(r*(1-(self.spin.value()/100)))
            self.tblRanges.setItem(i, 0,qcenter("{}-{}".format(bottom, top)))
            self.tblRanges.setItem(i, 1,QTableWidgetItem(inversiones(arr, bottom, top)))
            if self.benchmark.result.basic.last.quote>=bottom and self.benchmark.result.basic.last.quote<top: ##Colorize current price
                self.tblRanges.item(i, 0).setBackgroundColor(QColor(255, 160, 160))
                benchmarkrange=r
            if self.benchmark.result.basic.last.quote<benchmarkrange and colorized<=rangescovered:
                self.tblRanges.item(i, 1).setBackgroundColor(QColor(160, 255, 160))
                colorized=colorized+1
        print ("wdgIndexRangeSimulator > load_data: {0}".format(datetime.datetime.now()-inicio))

    def on_cmd_pressed(self):
        if self.spin.value()!=float(self.mem.config.get_value("wdgIndexRangeSimulator", "spin")):
            self.mem.config.set_value("wdgIndexRangeSimulator", "spin", self.spin.value())
            self.mem.config.save()
        if self.txtInvertir.text()!=self.mem.config.get_value("wdgIndexRangeSimulator", "txtInvertir"):
            self.mem.config.set_value("wdgIndexRangeSimulator", "txtInvertir", self.txtInvertir.text())
            self.mem.config.save()
        if self.txtMinimo.text()!=self.mem.config.get_value("wdgIndexRangeSimulator", "txtMinimo"):
            self.mem.config.set_value("wdgIndexRangeSimulator", "txtMinimo", self.txtMinimo.text())
            self.mem.config.save()
        self.load_data()

