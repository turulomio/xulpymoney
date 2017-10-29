from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget
from Ui_wdgProductHistoricalChart import Ui_wdgProductHistoricalChart

import datetime
from canvaschart import VCCandlestick,  OHCLDuration,  VCTemporalSeries
from libxulpymoney import day_end_from_date
class wdgProductHistoricalChart(QWidget, Ui_wdgProductHistoricalChart):
    def __init__(self,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.view=None
        self.dtFrom.setDate(datetime.datetime.today()-datetime.timedelta(days=365*3))
        OHCLDuration.qcombobox(self.cmbOHCLDuration, OHCLDuration.Day)
        
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
        
        selected_date=self.dtFrom.date().toPyDate()
        selected_datetime= day_end_from_date(selected_date, self.mem.localzone)
        
        if self.cmbChartType.currentIndex()==0:#Lines
            self.view=VCTemporalSeries()
            self.verticalLayout.addWidget(self.view)
            ls=self.view.appendSeries(self.product.name.upper(), self.product.currency)
            for ohcl in self.product.result.ohclDaily.arr:
                if ohcl.date>=selected_date:
                    self.view.appendData(ls, ohcl.datetime(), ohcl.close)
                    
            if self.chkSMA50.isChecked():
                sma50=self.view.appendSeries(self.tr("SMA50"),  self.product.currency)
                for dt, value in self.product.result.ohclDaily.sma(50):
                    if selected_datetime<=dt:
                        self.view.appendData(sma50, dt, value)
            if self.chkSMA200.isChecked():
                sma200=self.view.appendSeries(self.tr("SMA200"),  self.product.currency)
                for dt, value in self.product.result.ohclDaily.sma(200):
                    if selected_datetime<=dt:
                        self.view.appendData(sma200, dt, value)
                    
                    
        elif self.cmbChartType.currentIndex()==1:#Candles
            self.view=VCCandlestick()
            self.verticalLayout.addWidget(self.view)
            self.view.appendSeries(self.product)
            self.view.setFrom(selected_date,  OHCLDuration.Day)
            
            if self.chkSMA50.isChecked():
                sma50=self.view.appendTemporalSeries(self.tr("SMA50"),  self.product.currency)
                for dt, value in self.product.result.ohclDaily.sma(50):
                    self.view.appendTemporalSeriesData(sma50, dt, value)
            if self.chkSMA200.isChecked():
                sma200=self.view.appendTemporalSeries(self.tr("SMA200"),  self.product.currency)
                for dt, value in self.product.result.ohclDaily.sma(200):
                    self.view.appendTemporalSeriesData(sma200, dt, value)
                
        self.view.display()
            
    @pyqtSlot(int)      
    def on_cmbChartType_currentIndexChanged(self, index):
        self.display()
        
    def on_cmdFromRight_released(self):
        self.dtFrom.setDate(self.dtFrom.date().toPyDate()+datetime.timedelta(days=365))
        self.display()        
    def on_cmdFromLeft_released(self):
        self.dtFrom.setDate(self.dtFrom.date().toPyDate()-datetime.timedelta(days=365))
        self.display()        
    def on_cmdFromRightMax_released(self):
        self.dtFrom.setDate(self.product.result.ohclDaily.last().date-datetime.timedelta(days=90))
        self.display()        
    def on_cmdFromLeftMax_released(self):
        self.dtFrom.setDate(self.product.result.ohclDaily.first().date)
        self.display()


    def on_chkSMA50_stateChanged(self, state):
        self.display()
    def on_chkSMA200_stateChanged(self, state):
        self.display()
