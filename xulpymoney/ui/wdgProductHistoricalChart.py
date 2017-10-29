from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget
from Ui_wdgProductHistoricalChart import Ui_wdgProductHistoricalChart

import datetime
from canvaschart import VCCandlestick,   VCTemporalSeries
from libxulpymoney import day_end_from_date,  OHCLDuration

class wdgProductHistoricalChart(QWidget, Ui_wdgProductHistoricalChart):
    def __init__(self,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.view=None
        self.dtFrom.setDate(datetime.datetime.today()-datetime.timedelta(days=365*3))
        self.cmbOHCLDuration.currentIndexChanged.disconnect()
        OHCLDuration.qcombobox(self.cmbOHCLDuration, OHCLDuration.Day)
        self.cmbOHCLDuration.currentIndexChanged.connect(self.on_cmbOHCLDuration_currentIndexChanged)
        
    def setProduct(self, product, investment=None):
        self.product=product
        self.investment=investment
        self.mem=self.product.mem
        self.display()
        
    def on_dtFrom_dateChanged(self, date):
        selected=date.toPyDate()
        if datetime.date.today()-selected<=datetime.timedelta(days=366):
            self.cmdFromRight.setEnabled(False)
        else:
            self.cmdFromRight.setEnabled(True)

    def display(self):
        """Just draw the chart with selected options. It creates and destroys objects"""
        if self.view!=None:
            self.view.close()
        
        selected_datetime= day_end_from_date(self.dtFrom.date().toPyDate(), self.mem.localzone)
        self.setohcl=self.product.result.ohcl(self.cmbOHCLDuration.itemData(self.cmbOHCLDuration.currentIndex()))
        
        if self.cmbChartType.currentIndex()==0:#Lines
            self.view=VCTemporalSeries()
            self.verticalLayout.addWidget(self.view)
            ls=self.view.appendSeries(self.product.name.upper(), self.product.currency)#Line seies
            for ohcl in self.setohcl.arr:
                if ohcl.datetime()>=selected_datetime:
                    self.view.appendData(ls, ohcl.datetime(), ohcl.close)
                    
            if self.chkSMA50.isChecked() and self.setohcl.length()>50:
                sma50=self.view.appendSeries(self.tr("SMA50"),  self.product.currency)#SMA50 line series
                for dt, value in self.setohcl.sma(50):
                    if selected_datetime<=dt:
                        self.view.appendData(sma50, dt, value)
                        
            if self.chkSMA200.isChecked() and self.setohcl.length()>200:#SMA200 line sries
                sma200=self.view.appendSeries(self.tr("SMA200"),  self.product.currency)
                for dt, value in self.setohcl.sma(200):
                    if selected_datetime<=dt:
                        self.view.appendData(sma200, dt, value)
        #################################
        elif self.cmbChartType.currentIndex()==1:#Candles
            self.view=VCCandlestick()
            self.verticalLayout.addWidget(self.view)
            
            candle=self.view.appendCandlestickSeries(self.product.name, self.product.currency)#Candle series
            for ohcl in self.setohcl.arr:
                if ohcl.datetime()>=selected_datetime:
                    self.view.appendCandlestickSeriesData(candle, ohcl)
            self.view.setOHCLDuration(self.cmbOHCLDuration.itemData(self.cmbOHCLDuration.currentIndex()))
            
            if self.chkSMA50.isChecked() and self.setohcl.length()>50:#SMA50 line series
                sma50=self.view.appendTemporalSeries(self.tr("SMA50"),  self.product.currency)
                for dt, value in self.setohcl.sma(50):
                    self.view.appendTemporalSeriesData(sma50, dt, value)
                    
            if self.chkSMA200.isChecked() and self.setohcl.length()>200:#SMA200 line series
                sma200=self.view.appendTemporalSeries(self.tr("SMA200"),  self.product.currency)
                for dt, value in self.setohcl.sma(200):
                    self.view.appendTemporalSeriesData(sma200, dt, value)
                    
        #INVESTMENT
        if self.investment!=None:
            buy=self.view.appendScatterSeries(self.tr("Buy operations"), self.product.currency)
            sell=self.view.appendScatterSeries(self.tr("Sell operations"), self.product.currency)
            for op in self.investment.op.arr:
                if op.tipooperacion.id in (4, ) and op.datetime>selected_datetime:
                    self.view.appendScatterSeriesData(buy, op.datetime, op.valor_accion)
                if op.tipooperacion.id in (5, ) and op.datetime>selected_datetime:
                    self.view.appendScatterSeriesData(sell, op.datetime, op.valor_accion)
        self.view.display()
            
    @pyqtSlot(int)      
    def on_cmbChartType_currentIndexChanged(self, index):
        self.display()
    @pyqtSlot(int)      
    def on_cmbOHCLDuration_currentIndexChanged(self, index):
        self.display()
        
    def on_cmdFromRight_released(self):
        self.dtFrom.setDate(day_end_from_date(self.dtFrom.date().toPyDate(), self.mem.localzone)+datetime.timedelta(days=365))
        self.display()        
    def on_cmdFromLeft_released(self):
        self.dtFrom.setDate(day_end_from_date(self.dtFrom.date().toPyDate(), self.mem.localzone)-datetime.timedelta(days=365))
        self.display()        
    def on_cmdFromRightMax_released(self):
        self.dtFrom.setDate(self.setohcl.last().datetime()-datetime.timedelta(days=365))
        self.display()        
    def on_cmdFromLeftMax_released(self):
        self.dtFrom.setDate(self.setohcl.first().datetime())
        self.display()
    def on_chkSMA50_stateChanged(self, state):
        self.display()
    def on_chkSMA200_stateChanged(self, state):
        self.display()
