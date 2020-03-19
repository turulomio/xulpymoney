from PyQt5.QtCore import Qt,  pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QDialog,  QMenu, QMessageBox,  QFileDialog
from datetime import datetime, date, timedelta, time
from logging import info
from officegenerator import ODS_Read, ODS_Write, Currency as ODSCurrency, Coord, ColumnWidthODS
from pytz import timezone
from xulpymoney.datetime_functions import dtnaive, dtaware, dt_day_end, dtaware2string
from xulpymoney.investing_com import InvestingCom
from xulpymoney.objects.leverage import LeverageManager
from xulpymoney.objects.productmode import ProductModesManager
from xulpymoney.objects.agrupation import AgrupationManager
from xulpymoney.objects.currency import currency_name, currency_symbol, currencies_qcombobox
from xulpymoney.objects.producttype import ProductTypeManager
from xulpymoney.objects.dps import DPS
from xulpymoney.objects.percentage import Percentage
from xulpymoney.objects.quote import QuoteManager, Quote, QuoteAllIntradayManager
from xulpymoney.objects.product import  Product
from xulpymoney.libxulpymoneyfunctions import qmessagebox, setReadOnly
from xulpymoney.casts import  c2b
from xulpymoney.objects.stockmarket import StockMarketManager
from xulpymoney.ui.myqtablewidget import qdatetime, qcurrency
from xulpymoney.libxulpymoneytypes import eConcept
from xulpymoney.ui.Ui_frmProductReport import Ui_frmProductReport
from xulpymoney.ui.frmSelector import frmManagerSelector
from xulpymoney.ui.frmDividendsAdd import frmDividendsAdd
from xulpymoney.ui.frmQuotesIBM import frmQuotesIBM
from xulpymoney.ui.frmSplit import frmSplit
from xulpymoney.ui.frmSplitManual import frmSplitManual
from xulpymoney.ui.frmEstimationsAdd import frmEstimationsAdd
from xulpymoney.ui.frmDPSAdd import frmDPSAdd
from xulpymoney.ui.wdgProductHistoricalChart import wdgProductHistoricalChart
from xulpymoney.ui.myqcharts import  VCTemporalSeries
from xulpymoney.version import __version__, __versiondate__

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
        
        self.mqtwTickers.settings(self.mem.settings, "frmProductReport", "mqtwTickers")
        self.mqtwDaily.settings(self.mem.settings, "frmProductReport", "mqtwDaily")    
        self.mqtwDaily.table.customContextMenuRequested.connect(self.on_mqtwDaily_customContextMenuRequested)
        self.mqtwDaily.table.itemSelectionChanged.connect(self.on_mqtwDaily_itemSelectionChanged)
        self.mqtwWeekly.settings(self.mem.settings, "frmProductReport", "mqtwWeekly")
        self.mqtwMonthly.settings(self.mem.settings, "frmProductReport", "mqtwMonthly")    
        self.mqtwMonthly.table.customContextMenuRequested.connect(self.on_mqtwMonthly_customContextMenuRequested)
        self.mqtwMonthly.table.itemSelectionChanged.connect(self.on_mqtwMonthly_itemSelectionChanged)
        self.mqtwYearly.settings(self.mem.settings, "frmProductReport", "mqtwYearly")    
        self.mqtwYearly.table.customContextMenuRequested.connect(self.on_mqtwYearly_customContextMenuRequested)
        self.mqtwYearly.table.itemSelectionChanged.connect(self.on_mqtwYearly_itemSelectionChanged)
        self.mqtwIntradia.settings(self.mem.settings, "frmProductReport", "mqtwIntradia")    
        self.mqtwIntradia.table.customContextMenuRequested.connect(self.on_mqtwIntradia_customContextMenuRequested)
        self.mqtwIntradia.table.itemSelectionChanged.connect(self.on_mqtwIntradia_itemSelectionChanged)
        self.mqtwMensuales.settings(self.mem.settings, "frmProductReport", "mqtwMensuales")    
        self.mqtwSplits.settings(self.mem.settings, "frmProductReport", "mqtwMensuales")
        self.mqtwSplits.table.customContextMenuRequested.connect(self.on_mqtwSplits_customContextMenuRequested)
        self.mqtwSplits.table.itemSelectionChanged.connect(self.on_mqtwSplits_itemSelectionChanged)
        self.mqtwDividendsEstimations.settings(self.mem.settings, "frmProductReport", "mqtwDividendsEstimations")    
        self.mqtwDividendsEstimations.table.customContextMenuRequested.connect(self.on_mqtwDividendsEstimations_customContextMenuRequested)
        self.mqtwDividendsEstimations.table.itemSelectionChanged.connect(self.on_mqtwDividendsEstimations_itemSelectionChanged)
        self.mqtwDPSPaid.settings(self.mem.settings, "frmProductReport", "mqtwDPSPaid")
        self.mqtwDPSPaid.table.customContextMenuRequested.connect(self.on_mqtwDPSPaid_customContextMenuRequested)
        self.mqtwDPSPaid.table.itemSelectionChanged.connect(self.on_mqtwDPSPaid_itemSelectionChanged)
        self.mqtwEPS.settings(self.mem.settings, "frmProductReport", "mqtwEPS")
        self.mqtwEPS.table.customContextMenuRequested.connect(self.on_mqtwEPS_customContextMenuRequested)
        self.mqtwEPS.table.itemSelectionChanged.connect(self.on_mqtwEPS_itemSelectionChanged)


        if self.product==None: #Insertar
            self.adding_new_product=True
            self.product=Product(self.mem)
            self.cmdSave.setText(self.tr("Add a new product"))
            
            self.tab.setTabEnabled(1, False)
            self.tab.setTabEnabled(2, False)
            self.tab.setTabEnabled(3, False)
            self.mem.stockmarkets.qcombobox(self.cmbBolsa)
            self.mem.investmentsmodes.qcombobox(self.cmbPCI)
            currencies_qcombobox(self.cmbCurrency, self.mem.localcurrency)
            self.mem.leverages.qcombobox(self.cmbApalancado)
            self.mem.types.qcombobox(self.cmbTipo)
        elif self.product.id<0: #Editar
            self.mem.stockmarkets.qcombobox(self.cmbBolsa)
            self.mem.investmentsmodes.qcombobox(self.cmbPCI)
            currencies_qcombobox(self.cmbCurrency, self.product.currency)
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
            self.mqtwTickers.blockSignals(True)
            self.txtComentario.setReadOnly(True)
            self.cmdAgrupations.setEnabled(False)
            setReadOnly(self.chkObsolete, True)
            setReadOnly(self.chkHL, True)
            self.cmdSave.setEnabled(False)
            self.spnDecimals.setReadOnly(True)
            
            bolsa=StockMarketManager(mem)
            bolsa.append(self.product.stockmarket)
            bolsa.qcombobox(self.cmbBolsa)
            
            productmodes=ProductModesManager(mem)
            productmodes.append(self.product.mode)
            productmodes.qcombobox(self.cmbPCI)

            self.cmbCurrency.addItem("{0} - {1} ({2})".format(self.product.currency, currency_name(self.product.currency), currency_symbol(self.product.currency)), self.product.currency)
            
            leverages=LeverageManager(mem)
            leverages.append(self.product.leveraged)
            leverages.qcombobox(self.cmbApalancado)
            
            types=ProductTypeManager(mem)
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
        def setTable(mqtw, manager):               
            data=[]
            for i, o in enumerate(manager.arr):
                data.append([
                    o.print_time(), 
                    o.close,
                    o.open, 
                    o.high, 
                    o.low, 
                    o.datetime(),  
                ])
            mqtw.setData(
                [self.tr("Date"), self.tr("Price"), self.tr("Open"), self.tr("Higher"), self.tr("Lower"), self.tr("Agrupation start")], 
                None, 
                data, 
                decimals=2, 
                zonename=self.mem.localzone_name
            )

            mqtw.table.setCurrentCell(manager.length()-1, 0)
            mqtw.table.setFocus()
        ################## load_historicas
        if index==0:
            setTable(self.mqtwDaily, self.product.result.ohclDailyBeforeSplits)
        elif index==1:
            setTable(self.mqtwWeekly, self.product.result.ohclWeekly)
        elif index==2:
            setTable(self.mqtwMonthly, self.product.result.ohclMonthly)
        elif index==3:
            setTable(self.mqtwYearly, self.product.result.ohclYearly)

    def load_information(self):
        def row_mqtwTPV(quote,  row):
            if quote==None:
                return
            self.tblTPC.setItem(row, 0, qdatetime(quote.datetime, self.mem.localzone_name))
            self.tblTPC.setItem(row, 1, self.product.money(quote.quote).qtablewidgetitem(self.product.decimals))

            try:
                tpc=Percentage(self.product.result.basic.last.quote-quote.quote, quote.quote)
                days=(datetime.now(timezone(self.mem.localzone_name))-quote.datetime).days+1
                self.tblTPC.setItem(row, 2, tpc.qtablewidgetitem())
                self.tblTPC.setItem(row, 3,  (tpc*365/days).qtablewidgetitem())
                if self.investment:
                    self.grpHistoricos.setTitle(self.tr('Report of historic prices. You have {} shares valued at {}.').format(self.investment.shares(), self.investment.balance()))
                    self.tblTPC.setItem(row, 4,  self.product.money(self.investment.shares()*(self.product.result.basic.last.quote-quote.quote)).qtablewidgetitem())
            except:
                self.tblTPC.setItem(row, 2, Percentage().qtablewidgetitem())    
                self.tblTPC.setItem(row, 3,  Percentage().qtablewidgetitem())
                self.tblTPC.setItem(row, 3,  qcurrency(None))     

        self.product.agrupations.qcombobox(self.cmbAgrupations)

        self.lblInvestment.setText("{} ( {} )".format(self.product.name, self.product.id))
        self.txtTPC.setText(str(self.product.percentage))
        self.txtName.setText(self.product.name)
        self.txtISIN.setText(self.product.isin)
        self.product.mqtw_tickers(self.mqtwTickers)
        self.txtComentario.setText(self.product.comment)
        self.txtAddress.setText(self.product.address)
        self.txtWeb.setText(self.product.web)
        self.txtMail.setText(self.product.mail)
        self.txtPhone.setText(self.product.phone)
        self.spnDecimals.setValue(self.product.decimals)

        if self.product.has_autoupdate()==True:
            self.lblAutoupdate.setText('<img src=":/xulpymoney/transfer.png" width="16" height="16"/>  {}'.format(self.tr("Product prices are updated automatically")))
        else:
            self.lblAutoupdate.setText(self.tr("Product prices are not updated automatically"))
            
        if self.product.obsolete==True:
            self.chkObsolete.setCheckState(Qt.Checked)
        
        if self.product.high_low==True:
            self.chkHL.setCheckState(Qt.Checked)

        self.cmbBolsa.setCurrentIndex(self.cmbBolsa.findData(self.product.stockmarket.id))
        self.cmbCurrency.setCurrentIndex(self.cmbCurrency.findData(self.product.currency))
        self.cmbPCI.setCurrentIndex(self.cmbPCI.findData(self.product.mode.id))
        self.cmbTipo.setCurrentIndex(self.cmbTipo.findData(self.product.type.id))
        self.cmbApalancado.setCurrentIndex(self.cmbApalancado.findData(self.product.leveraged.id))
        
        if len(self.product.result.ohclDaily.arr)!=0:
            now=self.mem.localzone.now()
            penultimate=self.product.result.basic.penultimate
            iniciosemana=Quote(self.mem).init__from_query(self.product, dt_day_end(now-timedelta(days=date.today().weekday()+1)))
            iniciomes=Quote(self.mem).init__from_query(self.product, dtaware(date(now.year, now.month, 1), time(0, 0), self.product.stockmarket.zone.name))
            inicioano=Quote(self.mem).init__from_query(self.product, dtaware(date(now.year, 1, 1), time(0, 0), self.product.stockmarket.zone.name))             
            docemeses=Quote(self.mem).init__from_query(self.product, dt_day_end(now-timedelta(days=365)))          
            unmes=Quote(self.mem).init__from_query(self.product, dt_day_end(now-timedelta(days=30)))          
            unasemana=Quote(self.mem).init__from_query(self.product, dt_day_end(now-timedelta(days=7)))             
            
            self.tblTPC.setItem(0, 0, qdatetime(self.product.result.basic.last.datetime, self.mem.localzone_name))   
            self.tblTPC.setItem(0, 1, self.product.money(self.product.result.basic.last.quote).qtablewidgetitem(6))
            
            row_mqtwTPV(penultimate, 2)
            row_mqtwTPV(iniciosemana, 3)## Para que sea el domingo
            row_mqtwTPV(iniciomes, 4)
            row_mqtwTPV(inicioano, 5)
            row_mqtwTPV(unasemana, 7)
            row_mqtwTPV(unmes, 8)
            row_mqtwTPV(docemeses, 9)

        
    def update_due_to_quotes_change(self):
        if self.product.id is not None:
            self.product.needStatus(2)
            if self.product.result.ohclDaily.length()>0:
                self.product.result.ohclDaily.selected=[]
                self.product.result.ohclMonthly.selected=[]
                self.product.result.ohclWeekly.selected=[]
                self.product.result.ohclYearly.selected=[]
                self.product.estimations_dps.load_from_db()#No cargada por defecto en product
                self.product.estimations_eps.load_from_db()#No cargada por defecto en product

                self.product.estimations_dps.myqtablewidget(self.mqtwDividendsEstimations)   
                self.product.estimations_eps.myqtablewidget(self.mqtwEPS)            
                self.product.dps.myqtablewidget(self.mqtwDPSPaid)         
                self.product.splits.myqtablewidget(self.mqtwSplits)
                inicio=datetime.now()
                self.load_information()
                info("Datos informacion cargados: {}".format(datetime.now()-inicio))
                self.load_graphics()
                info("Datos gráficos cargados: {}".format(datetime.now()-inicio))
                self.load_mensuales()
                info("Datos mensuales cargados: {}".format(datetime.now()-inicio))
                self.on_tabHistorical_currentChanged(self.tabHistorical.currentIndex())
            else:
                qmessagebox(self.tr("Not enough quotes for this product"))

    def load_graphics(self):
        self.product.result.get_intraday(self.calendar.selectedDate().toPyDate())
        
        #Canvas Historical
        if self.product.result.ohclDaily.length()>2:#Needs 2 to show just a line
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
            self.viewIntraday.chart().setTitle(self.tr("Intraday graph"))
            ls=self.viewIntraday.appendTemporalSeries(self.product.name.upper())
            for quote in self.product.result.intradia.arr:
                self.viewIntraday.appendTemporalSeriesData(ls, quote.datetime, quote.quote)
            self.viewIntraday.display()

        #mqtwIntradia
        self.product.result.intradia.myqtablewidget(self.mqtwIntradia)
        if self.product.result.intradia.length()>0:
            self.lblIntradayVariance.setText(self.tr("Daily maximum variance: {} ({})").format(self.product.money(self.product.result.intradia.variance()), self.product.result.intradia.variance_percentage()))

    def load_mensuales(self):
        data=[]
        minyear=self.product.result.ohclMonthly.arr[0].year
        for i, year in enumerate(range(minyear,  date.today().year+1)):
            row=[]
            row.append(year)
            for month in range(1, 13):
                row.append(self.product.result.ohclMonthly.percentage_by_year_month(year, month))
            row.append(self.product.result.ohclYearly.percentage_by_year(year))
            data.append(row)
            
        self.mqtwMensuales.setData(
            [self.tr("Year"), self.tr("January"),  self.tr("February"), self.tr("March"), self.tr("April"), self.tr("May"), self.tr("June"), self.tr("July"), self.tr("August"), self.tr("September"), self.tr("October"), self.tr("November"), self.tr("December"), self.tr("Total")], 
            None, 
            data, 
            decimals=2, 
            zonename=self.mem.localzone_name
        )

    @pyqtSlot() 
    def on_actionDividendXuNew_triggered(self):
        w=frmDividendsAdd(self.mem, self.investment,  None)
        w.wdgDT.set(dtnaive(self.selDPS.paydate, self.product.stockmarket.closes),  self.product.stockmarket.zone.name)
        gross=self.selDPS.gross*self.investment.shares(self.selDPS.date)
        w.txtBruto.setText(gross)
        w.txtDPA.setText(self.selDPS.gross)
        w.txtRetencion.setText(gross*self.mem.taxcapitalappreciation)
        w.cmb.setCurrentIndex(w.cmb.findData(eConcept.Dividends))
        w.exec_()

    @pyqtSlot()
    def on_actionDPSDelete_triggered(self):
        if self.selDPS!=None:
            for i in self.mqtwDPSPaid.table.selectedItems():#itera por cada item no row.        
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
        self.product.dps.myqtablewidget(self.mqtwDPSPaid)
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
            self.product.estimations_dps.myqtablewidget(self.mqtwDividendsEstimations)
            self.product.needStatus(2, downgrade_to=0)
        
    @pyqtSlot()
    def on_actionEstimationDPSNew_triggered(self):
        d=frmEstimationsAdd(self.mem, self.product, "dps")
        d.exec_()
        self.product.estimations_dps.myqtablewidget(self.mqtwDividendsEstimations)

    @pyqtSlot()
    def on_actionEstimationEPSDelete_triggered(self):
        if self.selEstimationEPS!=None:
            self.selEstimationEPS.borrar()
            self.product.estimations_eps.arr.remove(self.selEstimationEPS)
            self.mem.con.commit()
            self.product.estimations_eps.myqtablewidget(self.mqtwEPS)
            self.product.needStatus(2, downgrade_to=0)
        
    @pyqtSlot()
    def on_actionEstimationEPSNew_triggered(self):
        d=frmEstimationsAdd(self.mem, self.product, "eps")
        d.exec_()
        self.product.estimations_eps.myqtablewidget(self.mqtwEPS)

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
    def on_actionQuoteExport_triggered(self):
        start=datetime.now()
        filename_ods="{} Quotes of {}.ods".format(dtaware2string(self.mem.localzone.now(), "%Y%m%d %H%M"),  self.product.name)    
        filename = QFileDialog.getSaveFileName(self, self.tr("Save File"), filename_ods, self.tr("Libreoffice calc (*.ods)"))[0]
        if filename:
            ods=ODS_Write(filename)
            ods.setMetadata(self.tr("Historical quotes of {}").format(self.product.name),  self.tr("Quotes export"), "Xulpymoney-{} ({})".format(__version__, __versiondate__))
            s1=ods.createSheet(self.tr("Intraday"))
            s1.add("A1", [["Date and time", "Close", "Open","High","Low"]], "OrangeCenter")
            s1.setColumnsWidth([ColumnWidthODS.L])
            for i, o in enumerate(self.product.result.ohclDaily.arr):
                s1.add(Coord("A2").addRow(i), o.date, "WhiteDate")
                s1.add(Coord("B2").addRow(i), ODSCurrency(o.close, self.product.currency.id), "WhiteEUR")
                s1.add(Coord("C2").addRow(i), ODSCurrency(o.open, self.product.currency.id), "WhiteEUR")
                s1.add(Coord("D2").addRow(i), ODSCurrency(o.high, self.product.currency.id), "WhiteEUR")
                s1.add(Coord("E2").addRow(i), ODSCurrency(o.low, self.product.currency.id), "WhiteEUR")
            s1.freezeAndSelect("A2", Coord("A1").addRow(self.product.result.ohclDaily.length()), "A2")
            ods.save()
            qmessagebox(self.tr("Date export to {} took {}").format(filename, datetime.now()-start))

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
    def on_actionQuoteImportInvestingCom_triggered(self):
        filename=QFileDialog.getOpenFileName(self, "", "", "Texto CSV (*.csv)")[0]
        if filename!="":
            set=InvestingCom(self.mem, filename, self.product)
            result=set.save()
            #Display result
            from xulpymoney.ui.wdgQuotesSaveResult import frmQuotesSaveResult
            d=frmQuotesSaveResult()
            d.setFileToDelete(filename)
            d.settings_and_exec_(self.mem, *result)
            #Reloads changed data
            set.change_products_status_after_save(result[0], result[2], 1, downgrade_to=0, progress=True)
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
            self.product.high_low=c2b(self.chkHL.checkState())
            self.product.web=self.txtWeb.text()
            self.product.address=self.txtAddress.text()
            self.product.phone=self.txtPhone.text()
            self.product.mail=self.txtMail.text()
            self.product.percentage=int(self.txtTPC.text())
            self.product.mode=self.mem.investmentsmodes.find_by_id(self.cmbPCI.itemData(self.cmbPCI.currentIndex()))
            self.product.leveraged=self.mem.leverages.find_by_id(self.cmbApalancado.itemData(self.cmbApalancado.currentIndex()))
            self.product.stockmarket=self.mem.stockmarkets.find_by_id(self.cmbBolsa.itemData(self.cmbBolsa.currentIndex()))
            for i in range(self.mqtwTickers.table.rowCount()):
                value=self.mqtwTickers.table.item(i, 0).text()
                if value =="":
                    value=None
                self.product.tickers[i]=value
            self.product.comment=self.txtComentario.text()                
            self.product.decimals=self.spnDecimals.value()
            self.product.save()
            self.mem.con.commit()  
            self.mem.data.products.append(self.product)
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
            agr=self.mem.agrupations.clone()
        if self.product.agrupations==None:
            selected=AgrupationManager(self.mem)#Vacio
        else:
            selected=self.product.agrupations
        f=frmManagerSelector(self)
        f.setManagers(self.mem.settings, "frmProductReport", "frmSelectorAgrupations", agr, selected)
        f.setLabel(self.tr("Agrupation selection"))
        f.exec_()
        f.manager.selected.qcombobox(self.cmbAgrupations)

    def on_mqtwDaily_itemSelectionChanged(self):
        if self.product.result.ohclDaily.selected!=None:
            del self.product.result.ohclDaily.selected
            self.product.result.ohclDaily.selected=[]
            
        for i in self.mqtwDaily.table.selectedItems():#itera por cada item no row.
            if i.column()==0:
                self.product.result.ohclDaily.selected.append(self.product.result.ohclDaily.arr[i.row()])

    def on_mqtwDaily_customContextMenuRequested(self,  pos):
        if len(self.product.result.ohclDaily.selected)>0:
            self.actionQuoteDeleteDays.setEnabled(True)
        else:
            self.actionQuoteDeleteDays.setEnabled(False)
            
        menu=QMenu()
        menu.addAction(self.actionQuoteDeleteDays)        
        menu.addSeparator()
        menu.addAction(self.actionQuoteImport)
        menu.addAction(self.actionQuoteImportInvestingCom)
        menu.addAction(self.actionQuoteExport)
        menu.exec_(self.mqtwDaily.table.mapToGlobal(pos))
        
    def on_mqtwMonthly_itemSelectionChanged(self):
        if self.product.result.ohclMonthly.selected!=None:
            del self.product.result.ohclMonthly.selected
            self.product.result.ohclMonthly.selected=[]
            
        for i in self.mqtwMonthly.table.selectedItems():#itera por cada item no row.
            if i.column()==0:
                self.product.result.ohclMonthly.selected.append(self.product.result.ohclMonthly.arr[i.row()])

    def on_mqtwMonthly_customContextMenuRequested(self,  pos):
        if len(self.product.result.ohclMonthly.selected)>0:
            self.actionQuoteDeleteMonths.setEnabled(True)
        else:
            self.actionQuoteDeleteMonths.setEnabled(False)
            
        menu=QMenu()
        menu.addAction(self.actionQuoteDeleteMonths)        
        menu.exec_(self.mqtwMonthly.table.mapToGlobal(pos))  
        
    def on_mqtwYearly_itemSelectionChanged(self):
        if self.product.result.ohclYearly.selected!=None:
            del self.product.result.ohclYearly.selected
            self.product.result.ohclYearly.selected=[]
            
        for i in self.mqtwYearly.table.selectedItems():#itera por cada item no row.
            if i.column()==0:
                self.product.result.ohclYearly.selected.append(self.product.result.ohclYearly.arr[i.row()])

    def on_mqtwYearly_customContextMenuRequested(self,  pos):
        if len(self.product.result.ohclYearly.selected)>0:
            self.actionQuoteDeleteYears.setEnabled(True)
        else:
            self.actionQuoteDeleteYears.setEnabled(False)
            
        menu=QMenu()
        menu.addAction(self.actionQuoteDeleteYears)        
        menu.exec_(self.mqtwYearly.table.mapToGlobal(pos))
    def on_mqtwIntradia_customContextMenuRequested(self,  pos):
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
        menu.exec_(self.mqtwIntradia.table.mapToGlobal(pos))

    def on_mqtwIntradia_itemSelectionChanged(self):
        sel=[]
        try:
            for i in self.mqtwIntradia.table.selectedItems():#itera por cada item no row.
                if i.column()==0:
                    sel.append(self.product.result.intradia.arr[i.row()])
            self.setSelIntraday=set(sel)
        except:
            self.setSelIntraday=set([])
            
            
    def on_mqtwDividendsEstimations_itemSelectionChanged(self):
        try:
            for i in self.mqtwDividendsEstimations.table.selectedItems():#itera por cada item no row.        
                if i.column()==0:
                    self.selEstimationDPS=self.product.estimations_dps.arr[i.row()]
        except:
            self.selEstimationDPS=None
            
    def on_mqtwDividendsEstimations_customContextMenuRequested(self,  pos):
        if self.selEstimationDPS==None:
            self.actionEstimationDPSDelete.setEnabled(False)
        else:
            self.actionEstimationDPSDelete.setEnabled(True)
        menu=QMenu()
        menu.addAction(self.actionEstimationDPSNew)
        menu.addAction(self.actionEstimationDPSDelete)    
        menu.exec_(self.mqtwDividendsEstimations.table.mapToGlobal(pos))
            
            
    def on_mqtwEPS_itemSelectionChanged(self):
        try:
            for i in self.mqtwEPS.table.selectedItems():#itera por cada item no row.        
                if i.column()==0:
                    self.selEstimationEPS=self.product.estimations_eps.arr[i.row()]
        except:
            self.selEstimationEPS=None
            
    def on_mqtwSplits_customContextMenuRequested(self,  pos):
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
        menu.exec_(self.mqtwSplits.table.mapToGlobal(pos))
            
    def on_mqtwSplits_itemSelectionChanged(self):
        try:
            for i in self.mqtwSplits.table.selectedItems():#itera por cada item no row.        
                if i.column()==0:
                    self.product.splits.selected=self.product.splits.arr[i.row()]
        except:
            self.product.splits.selected=None
            
    def on_mqtwEPS_customContextMenuRequested(self,  pos):
        if self.selEstimationEPS==None:
            self.actionEstimationEPSDelete.setEnabled(False)
        else:
            self.actionEstimationEPSDelete.setEnabled(True)
        menu=QMenu()
        menu.addAction(self.actionEstimationEPSNew)
        menu.addAction(self.actionEstimationEPSDelete)    
        menu.exec_(self.mqtwEPS.table.mapToGlobal(pos))
            
    def on_mqtwDPSPaid_itemSelectionChanged(self):
        self.selDPS=None
        try:
            for i in self.mqtwDPSPaid.table.selectedItems():#itera por cada item no row.        
                if i.column()==0:
                    self.selDPS=self.product.dps.arr[i.row()]
        except:
            self.selDPS=None
        
            
    def on_mqtwDPSPaid_customContextMenuRequested(self,  pos):
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
        menu.exec_(self.mqtwDPSPaid.table.mapToGlobal(pos))
