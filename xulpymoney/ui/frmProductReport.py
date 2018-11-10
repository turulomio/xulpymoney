import datetime
import logging
import pytz
from PyQt5.QtCore import Qt,  pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QDialog,  QMenu, QMessageBox,  QFileDialog
from xulpymoney.ui.Ui_frmProductReport import Ui_frmProductReport
from xulpymoney.libxulpymoney import DPS, Percentage, Product, Quote, AgrupationManager, QuoteManager, QuoteAllIntradayManager, StockMarketManager,  CurrencyManager, LeverageManager, ProductModesManager, ProductTypesManager
from xulpymoney.libxulpymoneyfunctions import c2b, day_end, dtaware, qcenter, qdatetime, qleft
from xulpymoney.ui.frmSelector import frmSelector
from xulpymoney.ui.frmDividendsAdd import frmDividendsAdd
from xulpymoney.ui.frmQuotesIBM import frmQuotesIBM
from xulpymoney.ui.frmSplit import frmSplit
from xulpymoney.ui.frmSplitManual import frmSplitManual
from xulpymoney.ui.frmEstimationsAdd import frmEstimationsAdd
from xulpymoney.ui.frmDPSAdd import frmDPSAdd
from xulpymoney.ui.wdgProductHistoricalChart import wdgProductHistoricalChart
from xulpymoney.ui.canvaschart import  VCTemporalSeries
from officegenerator import ODS_Read

class frmProductReport(QDialog, Ui_frmProductReport):
    def __init__(self, mem,  product, inversion=None, parent = None, name = None, modal = False):
        """
            self.product.id==None Insertar
            self.product.id <0 Editar
            self.product.id >0 Red ONly
        """
        QDialog.__init__(self,  parent)
        self.hide()
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.setupUi(self)

        self.mem=mem
        self.product=product
        self.investment=inversion#Used to generate puntos de venta, punto de compra....
        self.setSelIntraday=set([])
        
        self.adding_new_product=False#Tag to know is I access this dialog adding a product
        self.selDPS=None
        self.selEstimationDPS=None
        self.selEstimationEPS=None
        
        self.selDate=None #Fecha seleccionado en datos historicos
        self.selDateTime=None #Datetime seleccionado para borrar quote no es el mismo procedimiento de borrado
        self.tab.setCurrentIndex(1)
        self.tabGraphics.setCurrentIndex(1)
        self.tabHistorical.setCurrentIndex(4)
        
        self.tblTPC.settings(self.mem, "frmProductReport")
        self.tblDaily.settings(self.mem, "frmProductReport")    
        self.tblWeekly.settings(self.mem, "frmProductReport")
        self.tblMonthly.settings(self.mem, "frmProductReport")    
        self.tblYearly.settings(self.mem, "frmProductReport")    
        self.tblIntradia.settings(self.mem, "frmProductReport")    
        self.tblMensuales.settings(self.mem, "frmProductReport")    
        self.tblSplits.settings(self.mem, "frmProductReport")
        self.tblDividendsEstimations.settings(self.mem, "frmProductReport")    
        self.tblDPSPaid.settings(self.mem, "frmProductReport")
        self.tblEPS.settings(self.mem, "frmProductReport")


        if self.product==None: #Insertar
            self.adding_new_product=True
            self.product=Product(self.mem)
            self.cmdSave.setText(self.tr("Add a new product"))
            
            self.tab.setTabEnabled(1, False)
            self.tab.setTabEnabled(2, False)
            self.tab.setTabEnabled(3, False)
            self.mem.stockmarkets.qcombobox(self.cmbBolsa)
            self.mem.investmentsmodes.qcombobox(self.cmbPCI)
            self.mem.currencies.qcombobox(self.cmbCurrency)
            self.mem.leverages.qcombobox(self.cmbApalancado)
            self.mem.types.qcombobox(self.cmbTipo)
        elif self.product.id<0: #Editar
            self.mem.stockmarkets.qcombobox(self.cmbBolsa)
            self.mem.investmentsmodes.qcombobox(self.cmbPCI)
            self.mem.currencies.qcombobox(self.cmbCurrency)
            self.mem.leverages.qcombobox(self.cmbApalancado)
            self.mem.types.qcombobox(self.cmbTipo)
        elif self.product.id>=0:#Readonly
            self.txtISIN.setReadOnly(True)
            self.txtName.setReadOnly(True)
            self.txtWeb.setReadOnly(True)
            self.txtAddress.setReadOnly(True)
            self.txtMail.setReadOnly(True)
            self.txtTPC.setReadOnly(True)
            self.txtPhone.setReadOnly(True)
            self.tblTickers.setEnabled(False)
            self.txtComentario.setReadOnly(True)
            self.cmdAgrupations.setEnabled(False)
            self.chkObsolete.setEnabled(False)
            self.cmdSave.setEnabled(False)
            
            bolsa=StockMarketManager(mem)
            bolsa.append(self.product.stockmarket)
            bolsa.qcombobox(self.cmbBolsa)
            
            productmodes=ProductModesManager(mem)
            productmodes.append(self.product.mode)
            productmodes.qcombobox(self.cmbPCI)
            
            currencies=CurrencyManager(mem)
            currencies.append(self.product.currency)
            currencies.qcombobox(self.cmbCurrency)
            
            leverages=LeverageManager(mem)
            leverages.append(self.product.leveraged)
            leverages.qcombobox(self.cmbApalancado)
            
            types=ProductTypesManager(mem)
            types.append(self.product.type)
            types.qcombobox(self.cmbTipo)
        
        self.viewIntraday=VCTemporalSeries()
        self.layIntraday.addWidget(self.viewIntraday)
       
        self.wdgHistorical=wdgProductHistoricalChart(self)
        self.layHistorical.addWidget(self.wdgHistorical)


        
        self.update_due_to_quotes_change()    
        self.showMaximized()        
        QApplication.restoreOverrideCursor()
        
        
    def on_tabHistorical_currentChanged(self, index):
        def setTable(table, data):
            table.setRowCount(len(data.arr))
            table.applySettings()
            table.clearContents()
            if len(data.arr)==0:
                return
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
        if index==0:
            setTable(self.tblDaily, self.product.result.ohclDailyBeforeSplits)
        elif index==1:
            setTable(self.tblWeekly, self.product.result.ohclWeekly)
        elif index==2:
            setTable(self.tblMonthly, self.product.result.ohclMonthly)
        elif index==3:
            setTable(self.tblYearly, self.product.result.ohclYearly)

        
    def load_information(self):
        def row_tblTPV(quote,  row):
            if quote==None:
                return
            self.tblTPC.setItem(row, 0, qdatetime(quote.datetime, self.mem.localzone))
            self.tblTPC.setItem(row, 1, self.product.currency.qtablewidgetitem(quote.quote, 6))

            try:
                tpc=Percentage(self.product.result.basic.last.quote-quote.quote, quote.quote)
                days=(datetime.datetime.now(pytz.timezone(self.mem.localzone.name))-quote.datetime).days+1
                self.tblTPC.setItem(row, 2, tpc.qtablewidgetitem())
                self.tblTPC.setItem(row, 3,  (tpc*365/days).qtablewidgetitem())
                if self.investment:
                    self.grpHistoricos.setTitle(self.tr('Report of historic prices. You have {} shares valued at {}.').format(self.investment.shares(), self.investment.balance()))
                    self.tblTPC.setItem(row, 4,  self.product.currency.qtablewidgetitem(self.investment.shares()*(self.product.result.basic.last.quote-quote.quote)))
            except:
                self.tblTPC.setItem(row, 2, Percentage().qtablewidgetitem())    
                self.tblTPC.setItem(row, 3,  Percentage().qtablewidgetitem())
                self.tblTPC.setItem(row, 3,  self.product.currency.qtablewidgetitem(None))     

        self.product.agrupations.qcombobox(self.cmbAgrupations)

        self.lblInvestment.setText("{} ( {} )".format(self.product.name, self.product.id))
        self.txtTPC.setText(str(self.product.percentage))
        self.txtName.setText(self.product.name)
        self.txtISIN.setText(self.product.isin)
        for i, ticker in enumerate(self.product.tickers):
            if ticker==None:
                self.tblTickers.setItem(i, 0, qleft(""))
            else:
                self.tblTickers.setItem(i, 0, qleft(self.product.tickers[i]))
        self.txtComentario.setText(self.product.comment)
        self.txtAddress.setText(self.product.address)
        self.txtWeb.setText(self.product.web)
        self.txtMail.setText(self.product.mail)
        self.txtPhone.setText(self.product.phone)

        if self.product.has_autoupdate()==True:
            self.lblAutoupdate.setText('<img src=":/xulpymoney/transfer.png" width="16" height="16"/>  {}'.format(self.tr("Product prices are updated automatically")))
        else:
            self.lblAutoupdate.setText(self.tr("Product prices are not updated automatically"))
            
        if self.product.obsolete==True:
            self.chkObsolete.setCheckState(Qt.Checked)          

        self.cmbBolsa.setCurrentIndex(self.cmbBolsa.findData(self.product.stockmarket.id))
        self.cmbCurrency.setCurrentIndex(self.cmbCurrency.findData(self.product.currency.id))
        self.cmbPCI.setCurrentIndex(self.cmbPCI.findData(self.product.mode.id))
        self.cmbTipo.setCurrentIndex(self.cmbTipo.findData(self.product.type.id))
        self.cmbApalancado.setCurrentIndex(self.cmbApalancado.findData(self.product.leveraged.id))
        
        if len(self.product.result.ohclDaily.arr)!=0:
            now=self.mem.localzone.now()
            penultimate=self.product.result.basic.penultimate
            iniciosemana=Quote(self.mem).init__from_query(self.product,  day_end(now-datetime.timedelta(days=datetime.date.today().weekday()+1), self.product.stockmarket.zone))
            iniciomes=Quote(self.mem).init__from_query(self.product, dtaware(datetime.date(now.year, now.month, 1), datetime.time(0, 0), self.product.stockmarket.zone.name))
            inicioano=Quote(self.mem).init__from_query(self.product, dtaware(datetime.date(now.year, 1, 1), datetime.time(0, 0), self.product.stockmarket.zone.name))             
            docemeses=Quote(self.mem).init__from_query(self.product, day_end(now-datetime.timedelta(days=365), self.product.stockmarket.zone))          
            unmes=Quote(self.mem).init__from_query(self.product, day_end(now-datetime.timedelta(days=30), self.product.stockmarket.zone))          
            unasemana=Quote(self.mem).init__from_query(self.product, day_end(now-datetime.timedelta(days=7), self.product.stockmarket.zone))             
            
            self.tblTPC.applySettings()
            self.tblTPC.setItem(0, 0, qdatetime(self.product.result.basic.last.datetime, self.mem.localzone))   
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
            self.product.needStatus(2)
            self.product.result.ohclDaily.selected=[]
            self.product.result.ohclMonthly.selected=[]
            self.product.result.ohclWeekly.selected=[]
            self.product.result.ohclYearly.selected=[]
            self.product.estimations_dps.load_from_db()#No cargada por defecto en product
            self.product.estimations_eps.load_from_db()#No cargada por defecto en product

            self.product.estimations_dps.myqtablewidget(self.tblDividendsEstimations)   
            self.product.estimations_eps.myqtablewidget(self.tblEPS)            
            self.product.dps.myqtablewidget(self.tblDPSPaid)         
            self.product.splits.myqtablewidget(self.tblSplits)
            inicio=datetime.datetime.now()
            self.load_information()
            logging.info("Datos informacion cargados: {}".format(datetime.datetime.now()-inicio))
            self.load_graphics()
            logging.info("Datos gráficos cargados: {}".format(datetime.datetime.now()-inicio))
            self.load_mensuales()
            logging.info("Datos mensuales cargados: {}".format(datetime.datetime.now()-inicio))
            self.on_tabHistorical_currentChanged(self.tabHistorical.currentIndex())


        

    def load_graphics(self):
        self.product.result.get_intraday(self.calendar.selectedDate().toPyDate())
        
        #Canvas Historical
        if len(self.product.result.ohclDaily.arr)<2:#Needs 2 to show just a line
            pass
        else:
            self.wdgHistorical.setProduct(self.product, self.investment)
            self.wdgHistorical.generate()
            self.wdgHistorical.display()

        #Canvas Intradia
        if self.product.result.intradia.length()<2:
            self.viewIntraday.hide()
        else:
            self.viewIntraday.show()
            self.layIntraday.removeWidget(self.viewIntraday)
            self.viewIntraday.close()
            
            self.viewIntraday=VCTemporalSeries()
            self.layIntraday.addWidget(self.viewIntraday)
            self.viewIntraday.chart.setTitle(self.tr("Intraday graph"))
            ls=self.viewIntraday.appendTemporalSeries(self.product.name.upper(), self.product.currency)
            for quote in self.product.result.intradia.arr:
                self.viewIntraday.appendTemporalSeriesData(ls, quote.datetime, quote.quote)
            self.viewIntraday.display()

        #tblIntradia
        try:
            self.product.result.intradia.myqtablewidget(self.tblIntradia)
            if self.product.result.intradia.length()>0:
                self.lblIntradayVariance.setText(self.tr("Daily maximum variance: {} ({})").format(self.product.currency.string(self.product.result.intradia.variance()), self.product.result.intradia.variance_percentage()))
        except:
            logging.error("Error creating intraday table. Perhaps due to currency exchange missing quotes")

    def load_mensuales(self):
        if len(self.product.result.ohclMonthly.arr)==0:
            self.tblMensuales.clear()
            return

        minyear=self.product.result.ohclMonthly.arr[0].year
        rowcount=int(datetime.date.today().year-minyear+1)
        self.tblMensuales.applySettings()
        self.tblMensuales.setRowCount(rowcount)    

        for i, year in enumerate(range(minyear,  datetime.date.today().year+1)):
            self.tblMensuales.setItem(i, 0, qleft(year))
            for month in range(1, 13):
                self.tblMensuales.setItem(i, month, self.product.result.ohclMonthly.percentage_by_year_month(year, month).qtablewidgetitem())
            self.tblMensuales.setItem(i, 13, self.product.result.ohclYearly.percentage_by_year(year).qtablewidgetitem())

    @pyqtSlot() 
    def on_actionDividendXuNew_triggered(self):
        w=frmDividendsAdd(self.mem, self.investment,  None)
        w.wdgDT.setCombine(self.mem, self.selDPS.date, self.product.stockmarket.closes, self.product.stockmarket.zone)
        gross=self.selDPS.gross*self.investment.shares(self.selDPS.date)
        w.txtBruto.setText(gross)
        w.txtDPA.setText(self.selDPS.gross)
        w.txtRetencion.setText(gross*self.mem.taxcapitalappreciation)
        w.cmb.setCurrentIndex(w.cmb.findData(39))
        w.exec_()

    @pyqtSlot()
    def on_actionDPSDelete_triggered(self):
        if self.selDPS!=None:
            for i in self.tblDPSPaid.selectedItems():#itera por cada item no row.        
                if i.column()==0:
                    dps=self.product.dps.arr[i.row()]
                    dps.borrar()
            self.mem.con.commit()
            self.product.result.load_dps_and_splits(force=True)#Reload becouse, deleting one in one loose index reference
            self.product.needStatus(2, downgrade_to=1)
            self.update_due_to_quotes_change()

        
    @pyqtSlot()
    def on_actionDPSNew_triggered(self):
        d=frmDPSAdd(self.mem, self.product)
        d.exec_()
        self.product.dps.myqtablewidget(self.tblDPSPaid)
        self.product.needStatus(2, downgrade_to=1)
        self.update_due_to_quotes_change()
        
    @pyqtSlot()
    def on_actionDPSImport_triggered(self):
        filename=QFileDialog.getOpenFileName(self, "", "", "LibreOffice Calc (*.ods)")[0]
        got=0
        if filename!="":
            ods=ODS_Read(filename)
            sheet=ods.getSheetElementByIndex(0)
            for number in range(2, ods.rowNumber(sheet)):
                date=ods.getCellValue(sheet, "A", str(number))
                value=ods.getCellValue(sheet, "B", str(number))
                print (date, value)
                dps=DPS(self.mem, self.product).init__create(date,  value)
                dps.save()
                self.product.dps.append(dps)
                got=got+1
            print("Added {} DPS from {} ODS rows".format(got, ods.rowNumber(sheet)-1))
            self.mem.con.commit()
            self.product.needStatus(2, downgrade_to=1)
            self.update_due_to_quotes_change()

    @pyqtSlot()
    def on_actionEstimationDPSDelete_triggered(self):
        if self.selEstimationDPS!=None:
            self.selEstimationDPS.borrar()
            self.product.estimations_dps.arr.remove(self.selEstimationDPS)
            self.mem.con.commit()
            self.product.estimations_dps.myqtablewidget(self.tblDividendsEstimations)
            self.product.needStatus(2, downgrade_to=0)
        
    @pyqtSlot()
    def on_actionEstimationDPSNew_triggered(self):
        d=frmEstimationsAdd(self.mem, self.product, "dps")
        d.exec_()
        self.product.estimations_dps.myqtablewidget(self.tblDividendsEstimations)

    @pyqtSlot()
    def on_actionEstimationEPSDelete_triggered(self):
        if self.selEstimationEPS!=None:
            self.selEstimationEPS.borrar()
            self.product.estimations_eps.arr.remove(self.selEstimationEPS)
            self.mem.con.commit()
            self.product.estimations_eps.myqtablewidget(self.tblEPS)
            self.product.needStatus(2, downgrade_to=0)
        
    @pyqtSlot()
    def on_actionEstimationEPSNew_triggered(self):
        d=frmEstimationsAdd(self.mem, self.product, "eps")
        d.exec_()
        self.product.estimations_eps.myqtablewidget(self.tblEPS)

    @pyqtSlot()
    def on_actionPurgeDay_triggered(self):
        self.product.result.intradia.purge()
        self.mem.con.commit()
        self.load_graphics()#OHLC ya estaba cargado, no varía por lo que no uso update_due_to_quotes_change
        
    @pyqtSlot()
    def on_actionQuoteEdit_triggered(self):
        for quote in self.setSelIntraday:##Only is one, but i don't know how to refer to quote
            w=frmQuotesIBM(self.mem,  self.product, quote)
            w.exec_()   
            if w.result()==QDialog.Accepted:
                self.product.needStatus(2, downgrade_to=0)
                self.update_due_to_quotes_change()
        
        
    @pyqtSlot()
    def on_actionQuoteImport_triggered(self):
        filename=QFileDialog.getOpenFileName(self, "", "", "LibreOffice Calc (*.ods)")[0]
        
        
        
        got=0
        if filename!="":
            set=QuoteManager(self.mem)
            ods=ODS_Read(filename)
            sheet=ods.getSheetElementByIndex(0)
            for number in range(2, ods.rowNumber(sheet)):
                date=ods.getCellValue(sheet, "A"+ str(number))
                value=ods.getCellValue(sheet, "B"+ str(number))
                print (date, value)
                set.append(Quote(self.mem).init__create(self.product, dtaware(date, self.product.stockmarket.closes, self.product.stockmarket.zone.name),  value))
                got=got+1
            print("Added {} DPS from {} ODS rows".format(got, ods.rowNumber(sheet)-1))
            set.save()
            self.mem.con.commit()
            self.product.needStatus(2, downgrade_to=0)
            self.update_due_to_quotes_change()

    @pyqtSlot()
    def on_actionQuoteNew_triggered(self):
        w=frmQuotesIBM(self.mem,  self.product)
        w.wdgDT.teDate.setSelectedDate(self.calendar.selectedDate())
        w.exec_()   
        if w.result()==QDialog.Accepted:
            self.product.needStatus(2, downgrade_to=0)
            self.update_due_to_quotes_change()

    @pyqtSlot()
    def on_actionQuoteDelete_triggered(self):
        for q in self.setSelIntraday:
            q.delete()
            self.product.result.intradia.arr.remove(q)
        self.mem.con.commit()
        self.product.needStatus(2, downgrade_to=0)
        self.update_due_to_quotes_change()
        
    @pyqtSlot()
    def on_actionQuoteDeleteDays_triggered(self):
        for ohcl in self.product.result.ohclDaily.selected:
            ohcl.delete()
        self.mem.con.commit()
        self.product.needStatus(2, downgrade_to=0)
        self.update_due_to_quotes_change()
    
    @pyqtSlot()
    def on_actionQuoteDeleteMonths_triggered(self):
        for ohcl in self.product.result.ohclMonthly.selected:
            ohcl.delete()
        self.mem.con.commit()
        self.product.needStatus(2, downgrade_to=0)
        self.update_due_to_quotes_change()
    
    @pyqtSlot()
    def on_actionQuoteDeleteYears_triggered(self):
        for ohcl in self.product.result.ohclYearly.selected:
            ohcl.delete()
        self.mem.con.commit()
        self.product.needStatus(2, downgrade_to=0)
        self.update_due_to_quotes_change()

    def on_calendar_selectionChanged(self):
        self.load_graphics()

    def on_cmdSplitManual_pressed(self):
        w=frmSplitManual(self.mem, self.product)
        w.exec_()   
        if w.result()==QDialog.Accepted:
            self.product.needStatus(2, downgrade_to=0)
            self.update_due_to_quotes_change()
            
    @pyqtSlot()
    def on_actionSplitNew_triggered(self):
        w=frmSplit(self.mem, self.product)
        w.exec_()   
        if w.result()==QDialog.Accepted:
            self.mem.con.commit()
            self.product.splits.append(w.split)
            self.product.splits.order_by_datetime()
            self.product.needStatus(2, downgrade_to=0)
            self.update_due_to_quotes_change()
    
    
    @pyqtSlot()
    def on_actionSplitEdit_triggered(self):
        w=frmSplit(self.mem, self.product, self.product.splits.selected)
        w.exec_()   
        if w.result()==QDialog.Accepted:
            self.product.needStatus(2, downgrade_to=0)
            self.update_due_to_quotes_change()

    @pyqtSlot()
    def on_actionSplitRemove_triggered(self):
        self.product.splits.delete(self.product.splits.selected)
        self.mem.con.commit()
        self.product.needStatus(2, downgrade_to=0)
        self.update_due_to_quotes_change()
        
    def on_cmdPurge_pressed(self):
        all=QuoteAllIntradayManager(self.mem)
        all.load_from_db(self.product)
        numpurged=all.purge(progress=True)
        if numpurged!=None:#Canceled
            self.mem.con.commit()
            m=QMessageBox()
            m.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
            m.setIcon(QMessageBox.Information)
            m.setText(self.tr("{0} quotes have been purged from {1}".format(numpurged, self.product.name)))
            m.exec_()    
        else:
            self.mem.con.rollback()
        
    def on_cmdSave_pressed(self):
        if self.product.id==None or self.product.id<0:
            self.product.name=self.txtName.text()
            if self.txtISIN.text()=="":
                self.product.isin=None
            else:
                self.product.isin=self.txtISIN.text()
            self.product.currency=self.mem.currencies.find_by_id(self.cmbCurrency.itemData(self.cmbCurrency.currentIndex()))
            self.product.type=self.mem.types.find_by_id(self.cmbTipo.itemData(self.cmbTipo.currentIndex()))
            self.product.agrupations=AgrupationManager(self.mem).clone_from_combo(self.cmbAgrupations)
            self.product.obsolete=c2b(self.chkObsolete.checkState())
            self.product.web=self.txtWeb.text()
            self.product.address=self.txtAddress.text()
            self.product.phone=self.txtPhone.text()
            self.product.mail=self.txtMail.text()
            self.product.percentage=int(self.txtTPC.text())
            self.product.mode=self.mem.investmentsmodes.find_by_id(self.cmbPCI.itemData(self.cmbPCI.currentIndex()))
            self.product.leveraged=self.mem.leverages.find_by_id(self.cmbApalancado.itemData(self.cmbApalancado.currentIndex()))
            self.product.stockmarket=self.mem.stockmarkets.find_by_id(self.cmbBolsa.itemData(self.cmbBolsa.currentIndex()))
            for i in range(self.tblTickers.rowCount()):
                value=self.tblTickers.item(i, 0).text()
                if value =="":
                    value=None
                self.product.tickers[i]=value
            self.product.comment=self.txtComentario.text()                
            self.product.save()
            self.mem.con.commit()  



            (last, penultimate, lastyear, estimations_dps)=self.product.has_basic_data()
            while (last, penultimate, lastyear, estimations_dps)!=(True, True, True, True):
                m=QMessageBox()
                m.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
                m.setIcon(QMessageBox.Information)
                m.setText(self.tr("You have to add three quotes (last, penultimate and end last year quotes) and current year dividend per share estimation to the new product"))
                m.exec_()   
                now=datetime.datetime.now()
                if last==False:
                    w=frmQuotesIBM(self.mem,  self.product)
                    w.wdgDT.set(self.mem, now, self.mem.localzone)
                    w.lblInvestment.setText(self.tr("Please add the product last quote"))
                    w.setWindowTitle(self.tr("Product: {0} ({1})").format(self.product.name,  self.product.id))
                    w.exec_()          
                        
                if penultimate==False:
                    penultimate=now-datetime.timedelta(days=1)
                    w=frmQuotesIBM(self.mem,  self.product)
                    w.wdgDT.set(self.mem, datetime.datetime(penultimate.year, penultimate.month, penultimate.day, self.product.stockmarket.closes.hour, self.product.stockmarket.closes.minute), self.mem.localzone)
                    w.lblInvestment.setText(self.tr("Please add the product penultimate quote"))
                    w.setWindowTitle(self.tr("Product: {0} ({1})").format(self.product.name,  self.product.id))
                    w.exec_()    
                    
                if lastyear==False:
                    w=frmQuotesIBM(self.mem,  self.product)
                    w.wdgDT.set(self.mem, datetime.datetime(now.year-1, 12, 31, self.product.stockmarket.closes.hour, self.product.stockmarket.closes.minute), self.mem.localzone)
                    w.lblInvestment.setText(self.tr("Please add the product lastyear quote"))
                    w.setWindowTitle(self.tr("Product: {0} ({1})").format(self.product.name,  self.product.id))
                    w.exec_()    
                
                if estimations_dps==False:
                    d=frmEstimationsAdd(self.mem, self.product, "dps")
                    d.lbl.setText(self.tr("Please add current year dividend per share estimation"))
                    w.setWindowTitle(self.tr("Product: {0} ({1})").format(self.product.name,  self.product.id))
                    d.exec_()   
                
                (last, penultimate, lastyear, estimations_dps)=self.product.has_basic_data()
                print(last, penultimate, lastyear, estimations_dps)
            self.done(0)
        elif self.product.id>0:
            m=QMessageBox()
            m.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
            m.setText("Only developers can change system products. You can create a new personal product or fill a ticket in the sourceforge page. It will be updated soon")
            m.setIcon(QMessageBox.Information)
            m.exec_()        
            return

    def on_cmdAgrupations_released(self):
        ##Se debe clonar, porque selector borra
        if self.cmbTipo.itemData(self.cmbTipo.currentIndex())==2:#Fondos de inversión
            agr=self.mem.agrupations.clone_fondos()
        elif self.cmbTipo.itemData(self.cmbTipo.currentIndex())==1:#Acciones
            agr=self.mem.agrupations.clone_acciones()
        elif self.cmbTipo.itemData(self.cmbTipo.currentIndex())==4:#ETFs
            agr=self.mem.agrupations.clone_etfs()
        elif self.cmbTipo.itemData(self.cmbTipo.currentIndex())==5:#Warrants
            agr=self.mem.agrupations.clone_warrants()
        else:
            agr=self.mem.agrupations.clone(self.mem)
        if self.product.agrupations==None:
            selected=AgrupationManager(self.mem)#Vacio
        else:
            selected=self.product.agrupations
        f=frmSelector(self.mem, agr, selected)
        f.lbl.setText(self.tr("Agrupation selection"))
        f.exec_()
        f.selected.qcombobox(self.cmbAgrupations)

    def on_tblDaily_itemSelectionChanged(self):
        if self.product.result.ohclDaily.selected!=None:
            del self.product.result.ohclDaily.selected
            self.product.result.ohclDaily.selected=[]
            
        for i in self.tblDaily.selectedItems():#itera por cada item no row.
            if i.column()==0:
                self.product.result.ohclDaily.selected.append(self.product.result.ohclDaily.arr[i.row()])

    def on_tblDaily_customContextMenuRequested(self,  pos):
        if len(self.product.result.ohclDaily.selected)>0:
            self.actionQuoteDeleteDays.setEnabled(True)
        else:
            self.actionQuoteDeleteDays.setEnabled(False)
            
        menu=QMenu()
        menu.addAction(self.actionQuoteDeleteDays)        
        menu.addSeparator()
        menu.addAction(self.actionQuoteImport)
        menu.exec_(self.tblDaily.mapToGlobal(pos))
        
    def on_tblMonthly_itemSelectionChanged(self):
        if self.product.result.ohclMonthly.selected!=None:
            del self.product.result.ohclMonthly.selected
            self.product.result.ohclMonthly.selected=[]
            
        for i in self.tblMonthly.selectedItems():#itera por cada item no row.
            if i.column()==0:
                self.product.result.ohclMonthly.selected.append(self.product.result.ohclMonthly.arr[i.row()])

    def on_tblMonthly_customContextMenuRequested(self,  pos):
        if len(self.product.result.ohclMonthly.selected)>0:
            self.actionQuoteDeleteMonths.setEnabled(True)
        else:
            self.actionQuoteDeleteMonths.setEnabled(False)
            
        menu=QMenu()
        menu.addAction(self.actionQuoteDeleteMonths)        
        menu.exec_(self.tblMonthly.mapToGlobal(pos))  
        
    def on_tblYearly_itemSelectionChanged(self):
        if self.product.result.ohclYearly.selected!=None:
            del self.product.result.ohclYearly.selected
            self.product.result.ohclYearly.selected=[]
            
        for i in self.tblYearly.selectedItems():#itera por cada item no row.
            if i.column()==0:
                self.product.result.ohclYearly.selected.append(self.product.result.ohclYearly.arr[i.row()])

    def on_tblYearly_customContextMenuRequested(self,  pos):
        if len(self.product.result.ohclYearly.selected)>0:
            self.actionQuoteDeleteYears.setEnabled(True)
        else:
            self.actionQuoteDeleteYears.setEnabled(False)
            
        menu=QMenu()
        menu.addAction(self.actionQuoteDeleteYears)        
        menu.exec_(self.tblYearly.mapToGlobal(pos))
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
            
    def on_tblSplits_customContextMenuRequested(self,  pos):
        if self.product.splits.selected==None:
            self.actionSplitEdit.setEnabled(False)
            self.actionSplitRemove.setEnabled(False)
        else:
            self.actionSplitEdit.setEnabled(True)
            self.actionSplitRemove.setEnabled(True)
        menu=QMenu()
        menu.addAction(self.actionSplitNew)
        menu.addAction(self.actionSplitEdit)
        menu.addAction(self.actionSplitRemove)
        menu.exec_(self.tblSplits.mapToGlobal(pos))
            
    def on_tblSplits_itemSelectionChanged(self):
        try:
            for i in self.tblSplits.selectedItems():#itera por cada item no row.        
                if i.column()==0:
                    self.product.splits.selected=self.product.splits.arr[i.row()]
        except:
            self.product.splits.selected=None
            
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
        menu.addSeparator()
        menu.addAction(self.actionDPSImport)
        if self.investment!=None:
            menu.addSeparator()
            menu.addAction(self.actionDividendXuNew)
        menu.exec_(self.tblDPSPaid.mapToGlobal(pos))
