from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Ui_wdgIndexRange import *
from core import *
from frmAnalisis import *

class wdgIndexRange(QWidget, Ui_wdgIndexRange):
    def __init__(self,cfg, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.cfg=cfg
        
        self.load_data_from_db()
        self.quote_lastindex=None
        self.table.settings("wdgIndexRange",  self.cfg.inifile)
        self.load_data()
                    
    def load_data_from_db(self):
        inicio=datetime.datetime.now()
        self.data_ebs=SetEBs(self.cfg)
        self.data_ebs.load_from_db("select * from entidadesbancarias where eb_activa=true")
        self.data_cuentas=SetCuentas(self.cfg, self.data_ebs)
        self.data_cuentas.load_from_db("select * from cuentas where cu_activa=true")
        self.data_investments=SetMQInvestments(self.cfg)
        self.data_investments.load_from_db("select distinct(myquotesid) from inversiones where in_activa=true")
        self.data_inversiones=SetInversiones(self.cfg, self.data_cuentas, self.data_investments)
        self.data_inversiones.load_from_db("select * from inversiones where in_activa=true")
        print("\n","Cargando data en wdgInversiones",  datetime.datetime.now()-inicio)
        
        
    def load_data(self):
        def inversiones(arr,min,max):
            resultado=""
            for i in arr:
                if i[0]>=min and i[0]<max:
                    o=i[1]
                    resultado=resultado+ self.trUtf8("{0} {1}: {2} {3} ( {4} acciones a {5} {6} )\n".format(str(o.datetime)[:19], o.inversion.name, o.importe, o.inversion.mq.currency.symbol, int (o.acciones),  o.valor_accion,  o.inversion.mq.currency.symbol))
            return resultado[:-1]
        inicio=datetime.datetime.now()

        arr=[]

        for i in self.data_inversiones.arr:
            if i.mq.tpc!=0:
                for o in i.op_actual.arr:
                    arr.append((o.referenciaindice.quote, o))

        arr=sorted(arr, key=lambda row: row[1].datetime,  reverse=False) 
        
        if len (arr)==0: #Peta en base de datos vacía
            return
        
        con=self.cfg.connect_xulpymoney()
        cur = con.cursor()        
        mq=self.cfg.connect_myquotes()
        curmq=mq.cursor()
        
        maximo= int(max(arr)[0]*(1+ Decimal(self.spin.value()/200.0)))
        riesgocero=Patrimonio(self.cfg).patrimonio_riesgo_cero(self.data_inversiones, datetime.date.today())
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
            if self.cfg.indicereferencia.quotes.last.quote>formin and self.cfg.indicereferencia.quotes.last.quote<formax:
                self.table.item(rangos-1, 0).setBackgroundColor(QColor(255, 148, 148))
                rangoindexactual=rangos-1
            last=formin
            
        for i in range(rangos-rangoindexactual):
            if (self.table.item(rangoindexactual+i, 2).text())=="" and pasos>0:
                self.table.item(rangoindexactual+i, 2).setBackgroundColor(QColor(148, 255, 148))
                indexcover=int(self.table.item(rangoindexactual+i, 1).text())
                pasos=pasos-1
                
        #Variación del índice hoy
        if self.cfg.indicereferencia.quotes.penultimate.quote==0 or self.cfg.indicereferencia.quotes.penultimate.quote==None:
            variacion=0
        else:
            variacion=(self.cfg.indicereferencia.quotes.last.quote-self.cfg.indicereferencia.quotes.penultimate.quote)*100/self.cfg.indicereferencia.quotes.penultimate.quote
        self.lblTotal.setText(("Tengo cubierto hasta el %d del índice de referencia (%s). Su valor a %s es %d (%.2f %%)" %( indexcover, self.cfg.indicereferencia.name, self.cfg.indicereferencia.quotes.last.datetime,   int(self.cfg.indicereferencia.quotes.last.quote),  variacion)))
        cur.close()     
        self.cfg.disconnect_xulpymoney(con) 
        curmq.close()
        self.cfg.disconnect_myquotes(mq)
        print ("wdgIndexRange > load_data: {0}".format(datetime.datetime.now()-inicio))

    def on_cmd_pressed(self):
        self.load_data()

    def on_cmdIRAnalisis_pressed(self):
        w=frmAnalisis(self.cfg, self.cfg.indicereferencia, self)
        w.exec_()
        
    def on_cmdIRInsertar_pressed(self):
        w=frmQuotesIBM(self.cfg, self.cfg.indicereferencia,  self)
        w.exec_()
        mq=self.cfg.connect_myquotes()
        curmq=mq.cursor()       
        self.cfg.indicereferencia.quotes.get_basic(curmq)
        curmq.close()
        self.cfg.disconnect_myquotes(mq)     
        self.load_data()
        
    def on_table_cellDoubleClicked(self, row, column):
        if column==1:
            puntoinversion=Decimal(self.table.item(row, column).text())
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.trUtf8("Para llegar al punto de inversión seleccionado, el indice debe variar un {0}".format(tpc((puntoinversion-self.cfg.indicereferencia.quotes.last.quote)*100/self.cfg.indicereferencia.quotes.last.quote))))
            m.exec_()           
        elif column==2:
            inversiones=self.table.item(row, column).text().split(", ")
            m=QMessageBox()
            points=self.trUtf8("············································································································")
            message=points+"\n"
            inversiones.sort()
            for i in inversiones:
                message=message + i + "\n"
            message=message+ points
            m.setText(message)
            m.exec_()             
