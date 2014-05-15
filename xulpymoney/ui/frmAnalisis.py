from PyQt4.QtCore import *
from PyQt4.QtGui import *
import threading 
from myqtablewidget import *
from libxulpymoney import *
from frmSelector import *
from Ui_frmAnalisis import *
from frmDividendsAdd import *
from frmQuotesIBM import *
from frmSplit import *
from frmEstimationsAdd import *
from frmDPSAdd import *
from canvaschart import *
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar

class frmAnalisis(QDialog, Ui_frmAnalisis):
    def __init__(self, mem,  product, inversion=None, parent = None, name = None, modal = False):
        """
            product=None #insertar
            product es un objeto newInversioQ#modificar
        """
        QDialog.__init__(self,  parent)
        self.hide()
        QApplication.processEvents()
        self.setupUi(self)
        self.showMaximized()        

        self.mem=mem
        self.product=product
        self.inversion=inversion#Used to generate puntos de venta, punto de compra....
        self.setSelIntraday=set([])
        
        self.selDPS=None
        self.selEstimationDPS=None
        self.selEstimationEPS=None
        
        self.selDate=None #Fecha seleccionado en datos historicos
        self.selDateTime=None #Datetime seleccionado para borrar quote no es el mismo procedimiento de borrado
        self.tab.setCurrentIndex(1)
        self.tabGraphics.setCurrentIndex(1)
        self.tabHistorical.setCurrentIndex(4)
        
        self.tblTPC.settings("frmAnalisis",  self.mem)    
        self.tblDaily.settings("frmAnalisis",  self.mem)    
        self.tblMonthly.settings("frmAnalisis",  self.mem)    
        self.tblYearly.settings("frmAnalisis",  self.mem)    
        self.tblIntradia.settings("frmAnalisis",  self.mem)    
        self.tblMensuales.settings("frmAnalisis",  self.mem)    
        self.tblDividendsEstimations.settings("frmAnalisis",  self.mem)    
        self.tblDPSPaid.settings("frmAnalisis", self.mem)
        self.tblEPS.settings("frmAnalisis", self.mem)
                
        if self.product==None:
            self.product=Product(self.mem)
            self.tab.setTabEnabled(1, False)
            self.tab.setTabEnabled(2, False)
            self.tab.setTabEnabled(3, False)
            self.cmdSave.setText(self.trUtf8("Añadir nueva inversión"))

        self.canvasIntraday=canvasChartIntraday( self.mem, self)
        self.ntbIntraday = NavigationToolbar(self.canvasIntraday, self)
        self.layIntraday.addWidget(self.canvasIntraday)
        self.layIntraday.addWidget(self.ntbIntraday)
        
        self.canvasHistorical=canvasChartHistorical( self.mem, self)
        self.ntbHistorical=NavigationToolbar(self.canvasHistorical, self)
        self.layHistorical.addWidget(self.canvasHistorical)
        self.layHistorical.addWidget(self.ntbHistorical)
        
        self.canvasHistoricalSD=canvasChartHistorical( self.mem, self)
        self.ntbHistoricalSD=NavigationToolbar(self.canvasHistoricalSD, self)
        self.layHistoricalSD.addWidget(self.canvasHistoricalSD)
        self.layHistoricalSD.addWidget(self.ntbHistoricalSD)
        
        self.mem.bolsas.load_qcombobox(self.cmbBolsa)
        self.mem.investmentsmodes.load_qcombobox(self.cmbPCI)
        self.mem.currencies.load_qcombobox(self.cmbCurrency)
        self.mem.apalancamientos.load_qcombobox(self.cmbApalancado)
        self.mem.types.load_qcombobox(self.cmbTipo)

        self.update_due_to_quotes_change()    
        
    def __load_information(self):
        def row_tblTPV(quote,  row):
            if quote==None:
                return
            self.tblTPC.setItem(row, 0, qdatetime(quote.datetime, self.mem.localzone))
            self.tblTPC.setItem(row, 1, self.product.currency.qtablewidgetitem(quote.quote, 6))

            try:
                tpc=(self.product.result.basic.last.quote-quote.quote)*100/quote.quote
                days=(datetime.datetime.now(pytz.timezone(self.mem.localzone.name))-quote.datetime).days+1
                self.tblTPC.setItem(row, 2, qtpc(round(tpc, 2)))    
                self.tblTPC.setItem(row, 3,  qtpc(round(tpc*365/days, 2)))
            except:
                self.tblTPC.setItem(row, 2, qtpc(None))    
                self.tblTPC.setItem(row, 3,  qtpc(None))     
                
                
        self.product.agrupations.load_qcombobox(self.cmbAgrupations)
        self.product.priority.load_qcombobox(self.cmbPriority)
        self.product.priorityhistorical.load_qcombobox(self.cmbPriorityHistorical)

        self.lblInversion.setText(("%s ( %s )" %(self.product.name, self.product.id)))
        self.txtTPC.setText(str(self.product.tpc))
        self.txtName.setText((self.product.name))
        self.txtISIN.setText((self.product.isin))
        self.txtYahoo.setText(str(self.product.ticker))
        self.txtComentario.setText(self.product.comentario)
        self.txtAddress.setText(self.product.address)
        self.txtWeb.setText(self.product.web)
        self.txtMail.setText(self.product.mail)
        self.txtPhone.setText(self.product.phone)

        if self.product.active==True:
            self.chkActive.setCheckState(Qt.Checked)
        if self.product.obsolete==True:
            self.chkObsolete.setCheckState(Qt.Checked)          

        self.cmbBolsa.setCurrentIndex(self.cmbBolsa.findData(self.product.bolsa.id))
        self.cmbCurrency.setCurrentIndex(self.cmbCurrency.findData(self.product.currency.id))
        self.cmbPCI.setCurrentIndex(self.cmbPCI.findData(self.product.mode.id))
        self.cmbTipo.setCurrentIndex(self.cmbTipo.findData(self.product.type.id))
        self.cmbApalancado.setCurrentIndex(self.cmbApalancado.findData(self.product.apalancado.id))
        
        if len(self.product.result.ohclDaily.arr)!=0:
            now=self.mem.localzone.now()
            penultimate=self.product.result.basic.penultimate
            iniciosemana=Quote(self.mem).init__from_query(self.product,  day_end(now-datetime.timedelta(days=datetime.date.today().weekday()+1), self.product.bolsa.zone))
            iniciomes=Quote(self.mem).init__from_query(self.product, dt(datetime.date(now.year, now.month, 1), datetime.time(0, 0), self.product.bolsa.zone))
            inicioano=Quote(self.mem).init__from_query(self.product, dt(datetime.date(now.year, 1, 1), datetime.time(0, 0), self.product.bolsa.zone))             
            docemeses=Quote(self.mem).init__from_query(self.product, day_end(now-datetime.timedelta(days=365), self.product.bolsa.zone))          
            unmes=Quote(self.mem).init__from_query(self.product, day_end(now-datetime.timedelta(days=30), self.product.bolsa.zone))          
            unasemana=Quote(self.mem).init__from_query(self.product, day_end(now-datetime.timedelta(days=7), self.product.bolsa.zone))             
                
            self.tblTPC.setItem(0, 0, qdatetime(self.product.result.basic.last.datetime, self.product.bolsa.zone))   
            self.tblTPC.setItem(0, 1, self.product.currency.qtablewidgetitem(self.product.result.basic.last.quote,  6))
            
            row_tblTPV(penultimate, 2)
            row_tblTPV(iniciosemana, 3)## Para que sea el domingo
            row_tblTPV(iniciomes, 4)
            row_tblTPV(inicioano, 5)
            row_tblTPV(unasemana, 7)
            row_tblTPV(unmes, 8)
            row_tblTPV(docemeses, 9)

        
    def update_due_to_quotes_change(self):
        if self.product.id!=None:
            self.product.result.get_basic_ohcls()
            self.product.estimations_eps.load_from_db()#No cargada por defecto en product
            self.product.dps.load_from_db()

            self.product.estimations_dps.myqtablewidget(self.tblDividendsEstimations)   
            self.product.estimations_eps.myqtablewidget(self.tblEPS)            
            self.product.dps.myqtablewidget(self.tblDPSPaid)            
        inicio=datetime.datetime.now()
        self.__load_information()
        if len(self.product.result.ohclDaily.arr)!=0:
            print ("Datos informacion cargados:",  datetime.datetime.now()-inicio)
            self.load_graphics()
            print ("Datos gráficos cargados:",  datetime.datetime.now()-inicio)
            self.load_historicas()
            print ("Datos historicos cargados:",  datetime.datetime.now()-inicio)
            self.load_mensuales()
            print ("Datos mensuales cargados:",  datetime.datetime.now()-inicio)


#        
#        
#    def load_dividends(self):
#        
#        ###
#        cur=self.mem.conms.cursor()
#        cur.execute("select year,dpa from estimaciones where id=%s order by year", (self.product.id, ) )
#        self.tblDividendsEstimations.setRowCount(cur.rowcount)
#        for reg in cur:
#            self.tblDividendsEstimations.setItem(cur.rownumber-1, 0, qcenter(str(reg['year'])))
#            self.tblDividendsEstimations.setItem(cur.rownumber-1, 1, self.product.currency.qtablewidgetitem(reg['estimation'], 6))       
#            try:
#                tpc=reg['estimation']*100/self.product.result.basic.last.quote
#                self.tblDividendsEstimations.setItem(cur.rownumber-1, 2, qtpc(round(tpc, 2)))    
#            except:      
#                self.tblDividendsEstimations.setItem(cur.rownumber-1, 2, qtpc(None))    
#        self.tblDividendsEstimations.setCurrentCell(cur.rowcount-1, 0)
#        self.tblDividendsEstimations.setFocus()
#        cur.close()




    def load_historicas(self): 
        def setTable(table, data):
            table.setRowCount(len(data.arr))
            for punt, d in enumerate(data.arr):
                table.setItem(punt, 0, qcenter(d.print_time())) 
                table.setItem(punt, 1, self.product.currency.qtablewidgetitem(d.close,6))
                table.setItem(punt, 2, self.product.currency.qtablewidgetitem(d.open,6))
                table.setItem(punt, 3, self.product.currency.qtablewidgetitem(d.high,6))
                table.setItem(punt, 4, self.product.currency.qtablewidgetitem(d.low,6))
                table.setItem(punt, 5, qcenter(str(d.datetime())))
            table.setCurrentCell(len(data.arr)-1, 0)
            table.setFocus()
        ## load_historicas
        setTable(self.tblDaily, self.product.result.ohclDaily)
        setTable(self.tblWeekly, self.product.result.ohclWeekly)
        setTable(self.tblMonthly, self.product.result.ohclMonthly)
        setTable(self.tblYearly, self.product.result.ohclYearly)
        
        

    def load_graphics(self):
        t2 = threading.Thread(target=self.canvasHistorical.load_data,  args=(self.product, self.inversion))
        t2.start()
        t3 = threading.Thread(target=self.canvasHistoricalSD.load_data,  args=(self.product, self.inversion, True))
        t3.start()
        self.product.result.intradia.load_from_db(self.calendar.selectedDate().toPyDate(), self.product)
        if len(self.product.result.intradia.arr)==0:
            self.tblIntradia.setRowCount(0)
            self.canvasIntraday.ax.clear()
            t2.join()
            t3.join()
            return
        else:
            self.tblIntradia.setRowCount(len(self.product.result.intradia.arr))
            self.canvasIntraday.show()
            ma=max(self.product.result.intradia.arr,key=lambda q: q.quote) #devuelve objeto
            mi=min(self.product.result.intradia.arr,key=lambda q: q.quote)

    
            #Construlle tabla
            for i , q in enumerate(self.product.result.intradia.arr):
                if q.datetime.microsecond==5:
                    self.tblIntradia.setItem(i, 0, qcenter(str(q.datetime)[11:-13]))
                    self.tblIntradia.item(i, 0).setBackgroundColor(QColor(255, 255, 148))
                elif q.datetime.microsecond==4:
                    self.tblIntradia.setItem(i, 0, qcenter(str(q.datetime)[11:-13]))
                    self.tblIntradia.item(i, 0).setBackgroundColor(QColor(148, 148, 148))
                else:
                    self.tblIntradia.setItem(i, 0, qcenter(str(q.datetime)[11:-6]))
                self.tblIntradia.setItem(i, 1, self.product.currency.qtablewidgetitem(q.quote,6))       
                try:
                    tpc=(q.quote-self.product.result.basic.penultimate.quote)*100/q.quote
                    self.tblIntradia.setItem(i, 2, qtpc(round(tpc, 2)))    
                except:       
                    self.tblIntradia.setItem(i, 2, qtpc(None))    
                if q==ma:
                    self.tblIntradia.item(i, 1).setBackgroundColor(QColor(148, 255, 148))
                elif q==mi:
                    self.tblIntradia.item(i, 1).setBackgroundColor( QColor(255, 148, 148))  
      
                    
        
        t1 = threading.Thread(target=self.canvasIntraday.load_data_intraday,   args=(self.product, ))
        t1.start()

        t1.join()        
        t2.join()  
        t3.join()
        self.tblIntradia.setFocus()
        self.tblIntradia.setCurrentCell(len(self.product.result.intradia.arr)-1, 0)
        self.tblIntradia.clearSelection()



    def load_mensuales(self):
        minyear=self.product.result.ohclMonthly.arr[0].year
        rowcount=int(datetime.date.today().year-minyear+1)
        self.tblMensuales.setRowCount(rowcount)    
        
        #Rellena titulos
        for i in range(rowcount):
            self.tblMensuales.setItem(i, 0, QTableWidgetItem(self.trUtf8("Año "+ str(int(minyear+i)))))
        
        #Rellena meses
        for i in range(len(self.product.result.ohclMonthly.arr)):
            if i==0:
                continue
            if (self.product.result.ohclMonthly.arr[i].datetime()-self.product.result.ohclMonthly.arr[i-1].datetime()).days<=31:
                if self.product.result.ohclMonthly.arr[i-1].close==0:
                    tpc=0
                else:
                    tpc=(self.product.result.ohclMonthly.arr[i].close-self.product.result.ohclMonthly.arr[i-1].close)*100/self.product.result.ohclMonthly.arr[i-1].close
                current=self.product.result.ohclMonthly.arr[i].datetime()
                self.tblMensuales.setItem(current.year-minyear, current.month, qtpc(tpc)) 
        
        #Rellena años
        for i in range(len(self.product.result.ohclYearly.arr)):
            if i==0:
                continue
            if (self.product.result.ohclYearly.arr[i].datetime()-self.product.result.ohclYearly.arr[i-1].datetime()).days<=366:
                if self.product.result.ohclYearly.arr[i-1].close==0:
                    tpc=0
                else:
                    tpc=(self.product.result.ohclYearly.arr[i].close-self.product.result.ohclYearly.arr[i-1].close)*100/self.product.result.ohclYearly.arr[i-1].close
                current=self.product.result.ohclYearly.arr[i].datetime()
                self.tblMensuales.setItem(current.year-minyear, 13, qtpc(tpc)) 

    @QtCore.pyqtSlot() 
    def on_actionDividendXuNew_activated(self):
        w=frmDividendsAdd(self.mem, self.inversion,  None)
        w.cal.setSelectedDate(self.selDPS.date)
        gross=self.selDPS.gross*self.inversion.acciones(self.selDPS.date)
        w.txtBruto.setText(gross)
        w.txtDPA.setText(self.selDPS.gross)
        w.txtRetencion.setText(gross*self.mem.taxcapitalappreciation)
        w.cmb.setCurrentIndex(w.cmb.findData(39))
        w.exec_()

    @pyqtSignature("")
    def on_actionDPSDelete_activated(self):
        if self.selDPS!=None:
            self.selDPS.borrar()
            self.mem.conms.commit()
            self.product.dps.arr.remove(self.selDPS)
            self.product.dps.myqtablewidget(self.tblDPSPaid)
        
    @pyqtSignature("")
    def on_actionDPSNew_activated(self):
        d=frmDPSAdd(self.mem, self.product)
        d.exec_()
        self.product.dps.myqtablewidget(self.tblDPSPaid)

    @pyqtSignature("")
    def on_actionEstimationDPSDelete_activated(self):
        if self.selEstimationDPS!=None:
            self.selEstimationDPS.borrar()
            self.product.estimations_dps.arr.remove(self.selEstimationDPS)
            self.mem.conms.commit()
            self.product.estimations_dps.myqtablewidget(self.tblDividendsEstimations)
        
    @pyqtSignature("")
    def on_actionEstimationDPSNew_activated(self):
        d=frmEstimationsAdd(self.mem, self.product, "dps")
        d.exec_()
        self.product.estimations_dps.myqtablewidget(self.tblDividendsEstimations)

    @pyqtSignature("")
    def on_actionEstimationEPSDelete_activated(self):
        if self.selEstimationEPS!=None:
            self.selEstimationEPS.borrar()
            self.product.estimations_eps.arr.remove(self.selEstimationEPS)
            self.mem.conms.commit()
            self.product.estimations_eps.myqtablewidget(self.tblEPS)
        
    @pyqtSignature("")
    def on_actionEstimationEPSNew_activated(self):
        d=frmEstimationsAdd(self.mem, self.product, "eps")
        d.exec_()
        self.product.estimations_eps.myqtablewidget(self.tblEPS)

    @pyqtSignature("")
    def on_actionPurgeDay_activated(self):
        self.product.result.intradia.purge()
        self.mem.conms.commit()
        self.load_graphics()#OHLC ya estaba cargado, no varía por lo que no uso update_due_to_quotes_change
        
    @pyqtSignature("")
    def on_actionQuoteEdit_activated(self):
        for quote in self.setSelIntraday:##Only is one, but i don't know how to refer to quote
            w=frmQuotesIBM(self.mem,  self.product, quote)
            w.exec_()   
            if w.result()==QDialog.Accepted:
                self.update_due_to_quotes_change()
        
        
    @pyqtSignature("")
    def on_actionQuoteNew_activated(self):
        w=frmQuotesIBM(self.mem,  self.product)
        w.exec_()   
        if w.result()==QDialog.Accepted:
            self.update_due_to_quotes_change()

    @pyqtSignature("")
    def on_actionQuoteDelete_activated(self):
        for q in self.setSelIntraday:
            q.delete()
            self.product.result.intradia.arr.remove(q)
        self.mem.conms.commit()
        self.update_due_to_quotes_change()



    def on_calendar_selectionChanged(self):
        self.load_graphics()

    def on_cmdSplit_pressed(self):
        w=frmSplit(self.mem)
        w.exec_()   
        if w.result()==QDialog.Accepted:
            all=SetQuotesAll(self.mem)
            all.load_from_db(self.product)
            for setquoteintraday in all.arr:
                w.split.updateQuotes(setquoteintraday.arr)         
            self.mem.conms.commit()
            self.update_due_to_quotes_change()
        
    def on_cmdPurge_pressed(self):
        all=SetQuotesAll(self.mem)
        all.load_from_db(self.product)
        numpurged=all.purge(progress=True)
        if numpurged!=None:#Canceled
            self.mem.conms.commit()
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.trUtf8("{0} quotes have been purged from {1}".format(numpurged, self.product.name)))
            m.exec_()    
        else:
            self.mem.conms.rollback()
        
    def on_cmdSave_pressed(self):
        self.product.name=self.txtName.text()
        self.product.isin=self.txtISIN.text()
        self.product.currency=self.mem.currencies.find(self.cmbCurrency.itemData(self.cmbCurrency.currentIndex()))
        self.product.type=self.mem.types.find(self.cmbTipo.itemData(self.cmbTipo.currentIndex()))
        self.product.agrupations=SetAgrupations(self.mem).clone_from_combo(self.cmbAgrupations)
        self.product.active=c2b(self.chkActive.checkState())
        self.product.obsolete=c2b(self.chkObsolete.checkState())
        self.product.web=self.txtWeb.text()
        self.product.address=self.txtAddress.text()
        self.product.phone=self.txtPhone.text()
        self.product.mail=self.txtMail.text()
        self.product.tpc=int(self.txtTPC.text())
        self.product.mode=self.mem.investmentsmodes.find(self.cmbPCI.itemData(self.cmbPCI.currentIndex()))
        self.product.apalancado=self.mem.apalancamientos.find(self.cmbApalancado.itemData(self.cmbApalancado.currentIndex()))
        self.product.bolsa=self.mem.bolsas.find(self.cmbBolsa.itemData(self.cmbBolsa.currentIndex()))
        self.product.ticker=self.txtYahoo.text()
        self.product.system=False
        self.product.priority=SetPriorities(self.mem).init__create_from_combo(self.cmbPriority)
        self.product.priorityhistorical=SetPrioritiesHistorical(self.mem).init__create_from_combo(self.cmbPriorityHistorical)
        self.product.comentario=self.txtComentario.text()
        
        insertarquote=False#se hace antes porque id despues de save ya tiene valor
        if self.product.id==None:
            insertarquote=True
            
        self.product.save()
        self.mem.conms.commit()  
        
        if insertarquote==True:
            w=frmQuotesIBM(self.mem,  self.product)
            w.exec_()    
            self.done(0)
    

    def on_cmdAgrupations_released(self):
        ##Se debe clonar, porque selector borra
        if self.cmbTipo.itemData(self.cmbTipo.currentIndex())==2:#Fondos de inversión
            agr=self.mem.agrupations.clone_fondos()
        elif self.cmbTipo.itemData(self.cmbTipo.currentIndex())==1:#Acciones
            agr=self.mem.agrupations.clone_acciones()
        elif self.cmbTipo.itemData(self.cmbTipo.currentIndex())==4:#ETFs
            agr=self.mem.agrupations.clone_etfs()
        elif self.cmbTipo.itemData(self.cmbTipo.currentIndex())==5:#ETFs
            agr=self.mem.agrupations.clone_warrants()
        else:
            agr=self.mem.agrupations.clone()
        if self.product.agrupations==None:
            selected=SetAgrupations(self.mem)#Vacio
        else:
            selected=self.product.agrupations
        f=frmSelector(self.mem, agr, selected)
        f.lbl.setText("Selector de Agrupaciones")
        f.exec_()
        f.selected.load_qcombobox(self.cmbAgrupations)

    def on_cmdPriority_released(self):
        if self.product.id==None:#Insertar nueva inversión
            selected=SetPriorities(self.mem)#Esta vacio
        else:
            selected=self.product.priority
        
        f=frmSelector(self.mem, self.mem.priorities.clone(), selected)
        f.lbl.setText("Selector de prioridades")
        f.exec_()
        self.cmbPriority.clear()
        for item in f.selected.arr:
            self.cmbPriority.addItem(item.name, item.id)

    def on_cmdPriorityHistorical_released(self):
        if self.product.id==None:#Insertar nueva inversión
            selected=SetPrioritiesHistorical(self.mem)#“acio
        else:
            selected=self.product.priorityhistorical
        
        f=frmSelector(self.mem, self.mem.prioritieshistorical.clone(),  selected) 
        f.lbl.setText("Selector de prioridades de datos históricos")
        f.exec_()
        self.cmbPriorityHistorical.clear()
        for item in f.selected.arr:
            self.cmbPriorityHistorical.addItem(item.name, item.id)



    def on_tblIntradia_customContextMenuRequested(self,  pos):
        if len (self.setSelIntraday)>0:
            self.actionQuoteDelete.setEnabled(True)
        else:
            self.actionQuoteDelete.setEnabled(False)

        if len(self.setSelIntraday)==1:
            self.actionQuoteEdit.setEnabled(True)
        else:
            self.actionQuoteEdit.setEnabled(False)
            
        menu=QMenu()
        menu.addAction(self.actionQuoteNew)
        menu.addAction(self.actionQuoteEdit)
        menu.addAction(self.actionQuoteDelete)        
        menu.addSeparator()
        menu.addAction(self.actionPurgeDay)
        menu.exec_(self.tblIntradia.mapToGlobal(pos))

    def on_tblIntradia_itemSelectionChanged(self):
        sel=[]
        try:
            for i in self.tblIntradia.selectedItems():#itera por cada item no row.
                if i.column()==0:
                    sel.append(self.product.result.intradia.arr[i.row()])
            self.setSelIntraday=set(sel)
        except:
            self.setSelIntraday=set([])
            
            
    def on_tblDividendsEstimations_itemSelectionChanged(self):
        try:
            for i in self.tblDividendsEstimations.selectedItems():#itera por cada item no row.        
                if i.column()==0:
                    self.selEstimationDPS=self.product.estimations_dps.arr[i.row()]
        except:
            self.selEstimationDPS=None
            
    def on_tblDividendsEstimations_customContextMenuRequested(self,  pos):
        if self.selEstimationDPS==None:
            self.actionEstimationDPSDelete.setEnabled(False)
        else:
            self.actionEstimationDPSDelete.setEnabled(True)
        menu=QMenu()
        menu.addAction(self.actionEstimationDPSNew)
        menu.addAction(self.actionEstimationDPSDelete)    
        menu.exec_(self.tblDividendsEstimations.mapToGlobal(pos))
            
            
    def on_tblEPS_itemSelectionChanged(self):
        try:
            for i in self.tblEPS.selectedItems():#itera por cada item no row.        
                if i.column()==0:
                    self.selEstimationEPS=self.product.estimations_eps.arr[i.row()]
        except:
            self.selEstimationEPS=None
            
    def on_tblEPS_customContextMenuRequested(self,  pos):
        if self.selEstimationEPS==None:
            self.actionEstimationEPSDelete.setEnabled(False)
        else:
            self.actionEstimationEPSDelete.setEnabled(True)
        menu=QMenu()
        menu.addAction(self.actionEstimationEPSNew)
        menu.addAction(self.actionEstimationEPSDelete)    
        menu.exec_(self.tblEPS.mapToGlobal(pos))
            
    def on_tblDPSPaid_itemSelectionChanged(self):
        self.selDPS=None
        try:
            for i in self.tblDPSPaid.selectedItems():#itera por cada item no row.        
                if i.column()==0:
                    self.selDPS=self.product.dps.arr[i.row()]
        except:
            self.selDPS=None
        print (self.selDPS)
        
            
    def on_tblDPSPaid_customContextMenuRequested(self,  pos):
        if self.selDPS==None:
            self.actionDPSDelete.setEnabled(False)
            self.actionDividendXuNew.setEnabled(False)
        else:
            self.actionDPSDelete.setEnabled(True)
            self.actionDividendXuNew.setEnabled(True)
            
        menu=QMenu()
        menu.addAction(self.actionDPSNew)
        menu.addAction(self.actionDPSDelete)    
        if self.inversion!=None:
            menu.addSeparator()
            menu.addAction(self.actionDividendXuNew)
        menu.exec_(self.tblDPSPaid.mapToGlobal(pos))
