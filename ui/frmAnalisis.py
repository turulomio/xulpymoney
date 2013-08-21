from PyQt4.QtCore import *
from PyQt4.QtGui import *
import threading 
from myqtablewidget import *
from libxulpymoney import *
from frmSelector import *
from Ui_frmAnalisis import *
from frmQuotesIBM import *
from frmDividendoEstimacionIBM import *
from canvaschart import *
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar

class frmAnalisis(QDialog, Ui_frmAnalisis):
    def __init__(self, cfg,  investment, parent = None, name = None, modal = False):
        """
            investment=None #insertar
            investment es un objeto newInversioQ#modificar
        """
        QDialog.__init__(self,  parent)
        self.hide()
        QApplication.processEvents()
        self.setupUi(self)
        self.showMaximized()        

        self.cfg=cfg
        self.investment=investment
        self.setSelIntraday=None
        
        self.selDate=None #Fecha seleccionado en datos historicos
        self.selDateTime=None #Datetime seleccionado para borrar quote no es el mismo procedimiento de borrado
        self.tab.setCurrentIndex(0)
        self.tabGraphics.setCurrentIndex(0)
        self.tabHistorical.setCurrentIndex(0)
        
        self.tblTPC.settings("frmAnalisis",  self.cfg.file_ui)    
        self.tblDaily.settings("frmAnalisis",  self.cfg.file_ui)    
        self.tblMonthly.settings("frmAnalisis",  self.cfg.file_ui)    
        self.tblYearly.settings("frmAnalisis",  self.cfg.file_ui)    
        self.tblIntradia.settings("frmAnalisis",  self.cfg.file_ui)    
        self.tblMensuales.settings("frmAnalisis",  self.cfg.file_ui)    
        self.tblDividendosEstimaciones.settings("frmAnalisis",  self.cfg.file_ui)    
                
        if self.investment==None:
            self.investment=Investment(self.cfg)
            self.tab.setTabEnabled(1, False)
            self.tab.setTabEnabled(2, False)
            self.tab.setTabEnabled(3, False)
            self.cmdSave.setText(self.trUtf8("Añadir nueva inversión"))

        self.canvasIntraday=canvasChartIntraday( self.cfg, self)
        self.ntbIntraday = NavigationToolbar(self.canvasIntraday, self)
        self.layIntraday.addWidget(self.canvasIntraday)
        self.layIntraday.addWidget(self.ntbIntraday)
        
        self.canvasHistorical=canvasChartHistorical( self.cfg, self)
        self.ntbHistorical=NavigationToolbar(self.canvasHistorical, self)
        self.layHistorical.addWidget(self.canvasHistorical)
        self.layHistorical.addWidget(self.ntbHistorical)
        
        self.cfg.bolsas.load_qcombobox(self.cmbBolsa)
        self.cfg.investmentsmodes.load_qcombobox(self.cmbPCI)
        self.cfg.currencies.load_qcombobox(self.cmbCurrency)
        self.cfg.apalancamientos.load_qcombobox(self.cmbApalancado)
        self.cfg.types.load_qcombobox(self.cmbTipo)

        self.update_due_to_quotes_change()    
        
    def __load_information(self):
        def row_tblTPV(quote,  row):
            if quote==None:
                return
            self.tblTPC.setItem(row, 0, qdatetime(quote.datetime, self.cfg.localzone))
            self.tblTPC.setItem(row, 1, self.investment.currency.qtablewidgetitem(quote.quote, 6))

            try:
                tpc=(self.investment.result.last.quote-quote.quote)*100/quote.quote
                days=(datetime.datetime.now(pytz.timezone(self.cfg.localzone.name))-quote.datetime).days+1
                self.tblTPC.setItem(row, 2, qtpc(round(tpc, 2)))    
                self.tblTPC.setItem(row, 3,  qtpc(round(tpc*365/days, 2)))
            except:
                self.tblTPC.setItem(row, 2, qtpc(None))    
                self.tblTPC.setItem(row, 3,  qtpc(None))     
                
                
        self.investment.agrupations.load_qcombobox(self.cmbAgrupations)
        self.investment.priority.load_qcombobox(self.cmbPriority)
        self.investment.priorityhistorical.load_qcombobox(self.cmbPriorityHistorical)

        self.lblInversion.setText(("%s ( %s )" %(self.investment.name, self.investment.id)))
        self.txtTPC.setText(str(self.investment.tpc))
        self.txtName.setText((self.investment.name))
        self.txtISIN.setText((self.investment.isin))
        self.txtYahoo.setText(str(self.investment.yahoo))
        self.txtComentario.setText(self.investment.comentario)
        self.txtAddress.setText(self.investment.address)
        self.txtWeb.setText(self.investment.web)
        self.txtMail.setText(self.investment.mail)
        self.txtPhone.setText(self.investment.phone)

        if self.investment.active==True:
            self.chkActive.setCheckState(Qt.Checked)
        if self.investment.obsolete==True:
            self.chkObsolete.setCheckState(Qt.Checked)          

        self.cmbBolsa.setCurrentIndex(self.cmbBolsa.findData(self.investment.bolsa.id))
        self.cmbCurrency.setCurrentIndex(self.cmbCurrency.findData(self.investment.currency.id))
        self.cmbPCI.setCurrentIndex(self.cmbPCI.findData(self.investment.mode.id))
        self.cmbTipo.setCurrentIndex(self.cmbTipo.findData(self.investment.type.id))
        self.cmbApalancado.setCurrentIndex(self.cmbApalancado.findData(self.investment.apalancado.id))
        
        if len(self.investment.result.ohclDaily.arr)!=0:
            now=self.cfg.localzone.now()
            penultimate=self.investment.result.penultimate
            iniciosemana=Quote(self.cfg).init__from_query(self.investment,  day_end(now-datetime.timedelta(days=datetime.date.today().weekday()+1), self.investment.bolsa.zone))
            iniciomes=Quote(self.cfg).init__from_query(self.investment, dt(datetime.date(now.year, now.month, 1), datetime.time(0, 0), self.investment.bolsa.zone))
            inicioano=Quote(self.cfg).init__from_query(self.investment, dt(datetime.date(now.year, 1, 1), datetime.time(0, 0), self.investment.bolsa.zone))             
            docemeses=Quote(self.cfg).init__from_query(self.investment, day_end(now-datetime.timedelta(days=365), self.investment.bolsa.zone))          
            unmes=Quote(self.cfg).init__from_query(self.investment, day_end(now-datetime.timedelta(days=30), self.investment.bolsa.zone))          
            unasemana=Quote(self.cfg).init__from_query(self.investment, day_end(now-datetime.timedelta(days=7), self.investment.bolsa.zone))             
                
            self.tblTPC.setItem(0, 0, qdatetime(self.investment.result.last.datetime, self.investment.bolsa.zone))   
            self.tblTPC.setItem(0, 1, self.investment.currency.qtablewidgetitem(self.investment.result.last.quote,  6))
            
            row_tblTPV(penultimate, 2)
            row_tblTPV(iniciosemana, 3)## Para que sea el domingo
            row_tblTPV(iniciomes, 4)
            row_tblTPV(inicioano, 5)
            row_tblTPV(unasemana, 7)
            row_tblTPV(unmes, 8)
            row_tblTPV(docemeses, 9)

        
    def update_due_to_quotes_change(self):
        if self.investment.id!=None:
            self.investment.result.get_basic_ohcls()
            self.load_dividendos()
        inicio=datetime.datetime.now()
        self.__load_information()
        if len(self.investment.result.ohclDaily.arr)!=0:
            print ("Datos informacion cargados:",  datetime.datetime.now()-inicio)
            self.load_graphics()
            print ("Datos gráficos cargados:",  datetime.datetime.now()-inicio)
            self.load_historicas()
            print ("Datos historicos cargados:",  datetime.datetime.now()-inicio)
            self.load_mensuales()
            print ("Datos mensuales cargados:",  datetime.datetime.now()-inicio)


        
        
    def load_dividendos(self):
        
        ###
        cur=self.cfg.conms.cursor()
        cur.execute("select year,dpa from estimaciones where id=%s order by year", (self.investment.id, ) )
        self.tblDividendosEstimaciones.setRowCount(cur.rowcount)
        for reg in cur:
            self.tblDividendosEstimaciones.setItem(cur.rownumber-1, 0, qcenter(str(reg['year'])))
            self.tblDividendosEstimaciones.setItem(cur.rownumber-1, 1, self.investment.currency.qtablewidgetitem(reg['dpa'], 6))       
            try:
                tpc=reg['dpa']*100/self.investment.result.last.quote
                self.tblDividendosEstimaciones.setItem(cur.rownumber-1, 2, qtpc(round(tpc, 2)))    
            except:      
                self.tblDividendosEstimaciones.setItem(cur.rownumber-1, 2, qtpc(None))    
        self.tblDividendosEstimaciones.setCurrentCell(cur.rowcount-1, 0)
        self.tblDividendosEstimaciones.setFocus()
        cur.close()




    def load_historicas(self): 
        def setTable(table, data):
            table.setRowCount(len(data.arr))
            for punt, d in enumerate(data.arr):
                table.setItem(punt, 0, qcenter(d.print_time())) 
                table.setItem(punt, 1, self.investment.currency.qtablewidgetitem(d.close,6))
                table.setItem(punt, 2, self.investment.currency.qtablewidgetitem(d.open,6))
                table.setItem(punt, 3, self.investment.currency.qtablewidgetitem(d.high,6))
                table.setItem(punt, 4, self.investment.currency.qtablewidgetitem(d.low,6))
                table.setItem(punt, 5, qcenter(str(d.datetime())))
            table.setCurrentCell(len(data.arr)-1, 0)
            table.setFocus()
        ## load_historicas
        setTable(self.tblDaily, self.investment.result.ohclDaily)
        setTable(self.tblWeekly, self.investment.result.ohclWeekly)
        setTable(self.tblMonthly, self.investment.result.ohclMonthly)
        setTable(self.tblYearly, self.investment.result.ohclYearly)
        
        

    def load_graphics(self):
        t2 = threading.Thread(target=self.canvasHistorical.load_data,  args=(self.investment,  self.investment.result))
        t2.start()
        self.investment.result.intradia.load_from_db(self.calendar.selectedDate().toPyDate(), self.investment)
        if len(self.investment.result.intradia.arr)==0:
            self.tblIntradia.setRowCount(0)
            self.canvasIntraday.clear()
            t2.join()
            return
        else:
            self.tblIntradia.setRowCount(len(self.investment.result.intradia.arr))
            self.canvasIntraday.show()
            ma=max(self.investment.result.intradia.arr,key=lambda q: q.quote) #devuelve objeto
            mi=min(self.investment.result.intradia.arr,key=lambda q: q.quote)

    
            #Construlle tabla
            for i , q in enumerate(self.investment.result.intradia.arr):
                self.tblIntradia.setItem(i, 0, qcenter(str(q.datetime)[11:-6]))
                self.tblIntradia.setItem(i, 1, self.investment.currency.qtablewidgetitem(q.quote,6))       
                try:
                    tpc=(q.quote-self.investment.result.penultimate.quote)*100/q.quote
                    self.tblIntradia.setItem(i, 2, qtpc(round(tpc, 2)))    
                except:       
                    self.tblIntradia.setItem(i, 2, qtpc(None))    
                if q==ma:
                    self.tblIntradia.item(i, 1).setBackgroundColor(QColor(148, 255, 148))
                elif q==mi:
                    self.tblIntradia.item(i, 1).setBackgroundColor( QColor(255, 148, 148))                
        
        t1 = threading.Thread(target=self.canvasIntraday.load_data_intraday,   args=(self.investment, ))
        t1.start()

        t1.join()        
        t2.join()  
        self.tblIntradia.setFocus()
        self.tblIntradia.setCurrentCell(len(self.investment.result.intradia.arr)-1, 0)



    def load_mensuales(self):
        minyear=self.investment.result.ohclMonthly.arr[0].year
        rowcount=int(datetime.date.today().year-minyear+1)
        self.tblMensuales.setRowCount(rowcount)    
        
        #Rellena titulos
        for i in range(rowcount):
            self.tblMensuales.setItem(i, 0, QTableWidgetItem(self.trUtf8("Año "+ str(int(minyear+i)))))
        
        #Rellena meses
        for i in range(len(self.investment.result.ohclMonthly.arr)):
            if i==0:
                continue
            if (self.investment.result.ohclMonthly.arr[i].datetime()-self.investment.result.ohclMonthly.arr[i-1].datetime()).days<=31:
                if self.investment.result.ohclMonthly.arr[i-1].close==0:
                    tpc=0
                else:
                    tpc=(self.investment.result.ohclMonthly.arr[i].close-self.investment.result.ohclMonthly.arr[i-1].close)*100/self.investment.result.ohclMonthly.arr[i-1].close
                current=self.investment.result.ohclMonthly.arr[i].datetime()
                self.tblMensuales.setItem(current.year-minyear, current.month, qtpc(tpc)) 
        
        #Rellena años
        for i in range(len(self.investment.result.ohclYearly.arr)):
            if i==0:
                continue
            if (self.investment.result.ohclYearly.arr[i].datetime()-self.investment.result.ohclYearly.arr[i-1].datetime()).days<=366:
                if self.investment.result.ohclYearly.arr[i-1].close==0:
                    tpc=0
                else:
                    tpc=(self.investment.result.ohclYearly.arr[i].close-self.investment.result.ohclYearly.arr[i-1].close)*100/self.investment.result.ohclYearly.arr[i-1].close
                current=self.investment.result.ohclYearly.arr[i].datetime()
                self.tblMensuales.setItem(current.year-minyear, 13, qtpc(tpc)) 


    @pyqtSignature("")
    def on_actionDividendoEstimacionBorrar_activated(self):
        try:
            for i in self.tblDividendosEstimaciones.selectedItems():#itera por cada item no row.        
                year=int(self.tblDividendosEstimaciones.item(i.row(), 0).text())
        except:
            year=None
        if year!=None:
            con=self.cfg.connect_myquotes()
            cur = con.cursor()
            cur.execute("delete from estimaciones where code=%s and year=%s", (self.investment.id, year))
            con.commit()
            self.load_dividendos()
            cur.close() 
            self.cfg.disconnect_myquotes(con)  
        
    @pyqtSignature("")
    def on_actionDividendoEstimacionNueva_activated(self):
        d=frmDividendoEstimacionIBM(self.cfg, self.investment)
        d.exec_()
        if d.result()==QDialog.Accepted:
            con=self.cfg.connect_myquotes()
            cur = con.cursor()
            self.load_dividendos()
            cur.close() 
            self.cfg.disconnect_myquotes(con)  


    @pyqtSignature("")
    def on_actionPurgeDay_activated(self):
        self.investment.result.intradia.purge()
        self.cfg.conms.commit()
        self.load_graphics()#OHLC ya estaba cargado, no var´ia por lo que no uso update_due_to_quotes_change
        
    @pyqtSignature("")
    def on_actionQuoteNew_activated(self):
        w=frmQuotesIBM(self.cfg,  self.investment)
        w.exec_()   
        self.update_due_to_quotes_change()

    @pyqtSignature("")
    def on_actionQuoteDelete_activated(self):
        cur = self.cfg.conms.cursor()
        for q in self.setSelIntraday:
            q.delete()
            self.investment.result.intradia.arr.remove(q)
        self.cfg.conms.commit()
        cur.close() 
        self.update_due_to_quotes_change()



    def on_calendar_selectionChanged(self):
        self.load_graphics()

    def on_cmdSplit_pressed(self):
        qmessagebox_developing()
        
    def on_cmdPurge_pressed(self):
        all=SetQuotesAll(self.cfg)
        all.load_from_db(self.investment)
        numpurged=all.purge(progress=True)
        if numpurged!=None:#Canceled
            self.cfg.conms.commit()
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.trUtf8("{0} quotes have been purged from {1}".format(numpurged, self.investment.name)))
            m.exec_()    
        else:
            self.cfg.conms.rollback()
        
    def on_cmdSave_pressed(self):
        self.investment.name=self.txtName.text()
        self.investment.isin=self.txtISIN.text()
        self.investment.currency=self.cfg.currencies.find(self.cmbCurrency.itemData(self.cmbCurrency.currentIndex()))
        self.investment.type=self.cfg.types.find(self.cmbTipo.itemData(self.cmbTipo.currentIndex()))
        self.investment.agrupations=SetAgrupations(self.cfg).clone_from_combo(self.cmbAgrupations)
        self.investment.active=c2b(self.chkActive.checkState())
        self.investment.obsolete=c2b(self.chkObsolete.checkState())
        self.investment.web=self.txtWeb.text()
        self.investment.address=self.txtAddress.text()
        self.investment.phone=self.txtPhone.text()
        self.investment.mail=self.txtMail.text()
        self.investment.tpc=int(self.txtTPC.text())
        self.investment.mode=self.cfg.investmentsmodes.find(self.cmbPCI.itemData(self.cmbPCI.currentIndex()))
        self.investment.apalancado=self.cfg.apalancamientos.find(self.cmbApalancado.itemData(self.cmbApalancado.currentIndex()))
        self.investment.bolsa=self.cfg.bolsas.find(self.cmbBolsa.itemData(self.cmbBolsa.currentIndex()))
        self.investment.yahoo=self.txtYahoo.text()
        self.investment.system=False
        self.investment.priority=SetPriorities(self.cfg).init__create_from_combo(self.cmbPriority)
        self.investment.priorityhistorical=SetPrioritiesHistorical(self.cfg).init__create_from_combo(self.cmbPriorityHistorical)
        self.investment.comentario=self.txtComentario.text()
        
        insertarquote=False#se hace antes porque id despues de save ya tiene valor
        if self.investment.id==None:
            insertarquote=True
            
        self.investment.save()
        self.cfg.conms.commit()  
        
        if insertarquote==True:
            w=frmQuotesIBM(self.cfg,  self.investment)
            w.exec_()    
            self.done(0)
    

    def on_cmdAgrupations_released(self):
        ##Se debe clonar, porque selector borra
        if self.cmbTipo.itemData(self.cmbTipo.currentIndex())==2:#Fondos de inversión
            agr=self.cfg.agrupations.clone_fondos()
        elif self.cmbTipo.itemData(self.cmbTipo.currentIndex())==1:#Acciones
            agr=self.cfg.agrupations.clone_acciones()
        elif self.cmbTipo.itemData(self.cmbTipo.currentIndex())==4:#ETFs
            agr=self.cfg.agrupations.clone_etfs()
        elif self.cmbTipo.itemData(self.cmbTipo.currentIndex())==5:#ETFs
            agr=self.cfg.agrupations.clone_warrants()
        else:
            agr=self.cfg.agrupations.clone()
        if self.investment.agrupations==None:
            selected=SetAgrupations(self.cfg)#Vacio
        else:
            selected=self.investment.agrupations
        f=frmSelector(self.cfg, agr, selected)
        f.lbl.setText("Selector de Agrupaciones")
        f.exec_()
        f.selected.load_qcombobox(self.cmbAgrupations)

    def on_cmdPriority_released(self):
        if self.investment.id==None:#Insertar nueva inversión
            selected=SetPriorities(self.cfg)#Esta vacio
        else:
            selected=self.investment.priority
        
        f=frmSelector(self.cfg, self.cfg.priorities.clone(), selected)
        f.lbl.setText("Selector de prioridades")
        f.exec_()
        self.cmbPriority.clear()
        for item in f.selected.arr:
            self.cmbPriority.addItem(item.name, item.id)

    def on_cmdPriorityHistorical_released(self):
        if self.investment.id==None:#Insertar nueva inversión
            selected=SetPrioritiesHistorical(self.cfg)#“acio
        else:
            selected=self.investment.priorityhistorical
        
        f=frmSelector(self.cfg, self.cfg.prioritieshistorical.clone(),  selected) 
        f.lbl.setText("Selector de prioridades de datos históricos")
        f.exec_()
        self.cmbPriorityHistorical.clear()
        for item in f.selected.arr:
            self.cmbPriorityHistorical.addItem(item.name, item.id)



    def on_tblIntradia_customContextMenuRequested(self,  pos):
        menu=QMenu()
        menu.addAction(self.actionQuoteNew)

        menu.addAction(self.actionQuoteDelete)        
        if len (self.setSelIntraday)>0:
            self.actionQuoteDelete.setEnabled(True)
        else:
            self.actionQuoteDelete.setEnabled(False)
            
        menu.addSeparator()
        menu.addAction(self.actionPurgeDay)
        menu.exec_(self.tblIntradia.mapToGlobal(pos))

    def on_tblIntradia_itemSelectionChanged(self):
        sel=[]
        try:
            for i in self.tblIntradia.selectedItems():#itera por cada item no row.
                if i.column()==0:
                    sel.append(self.investment.result.intradia.arr[i.row()])
            self.setSelIntraday=set(sel)
        except:
            self.setSelIntraday=set([])
            
    def on_tblDividendosEstimaciones_customContextMenuRequested(self,  pos):
        menu=QMenu()
        menu.addAction(self.actionDividendoEstimacionNueva)
        menu.addAction(self.actionDividendoEstimacionBorrar)    
        menu.exec_(self.tblDividendosEstimaciones.mapToGlobal(pos))
