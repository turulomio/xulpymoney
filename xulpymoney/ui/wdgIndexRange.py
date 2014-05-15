from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Ui_wdgIndexRange import *
from libxulpymoney import *
from frmAnalisis import *

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
                    

        
    def load_data(self):
        def inversiones(arr,min,max):
            resultado=""
            for i in arr:
                if i[0]>=min and i[0]<max:
                    o=i[1]
                    resultado=resultado+ self.trUtf8("{0} {1}: {2} {3} ( {4} acciones a {5} {6} )\n".format(str(o.datetime)[:19], o.inversion.name, o.importe, o.inversion.product.currency.symbol, int (o.acciones),  o.valor_accion,  o.inversion.product.currency.symbol))
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
        riesgocero=Patrimonio(self.mem).patrimonio_riesgo_cero(self.mem.data.inversiones_active, datetime.date.today())
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
            self.table.setItem(rangos-1, 1,qcenter(str(int((formax+formin)/2))))            
            self.table.setItem(rangos-1, 2,QTableWidgetItem((inversiones(arr, formin, formax))))
            if self.mem.data.benchmark.result.basic.last.quote>formin and self.mem.data.benchmark.result.basic.last.quote<formax:
                self.table.item(rangos-1, 0).setBackgroundColor(QColor(255, 148, 148))
                rangoindexactual=rangos-1
            last=formin
            
        for i in range(rangos-rangoindexactual):
            if (self.table.item(rangoindexactual+i, 2).text())=="" and pasos>0:
                self.table.item(rangoindexactual+i, 2).setBackgroundColor(QColor(148, 255, 148))
                indexcover=int(self.table.item(rangoindexactual+i, 1).text())
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
        w=frmAnalisis(self.mem, self.mem.data.benchmark, None,  self)
        w.exec_()
        
    def on_cmdIRInsertar_pressed(self):
        w=frmQuotesIBM(self.mem, self.mem.data.benchmark, None,  self)
        w.exec_() 
        self.mem.data.benchmark.result.basic.load_from_db()
        self.load_data()
        
    def on_table_cellDoubleClicked(self, row, column):
        if column==1:
            puntoinversion=Decimal(self.table.item(row, column).text())
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.trUtf8("Para llegar al punto de inversión seleccionado, el indice debe variar un {0}".format(tpc((puntoinversion-self.mem.data.benchmark.result.basic.last.quote)*100/self.mem.data.benchmark.result.basic.last.quote))))
            m.exec_()           
        elif column==2:
            inversiones=self.table.item(row, column).text().split(", ")
            m=QMessageBox()
            points="············································································································"
            message=points+"\n"
            inversiones.sort()
            for i in inversiones:
                message=message + i + "\n"
            message=message+ points
            m.setText(message)
            m.exec_()             
