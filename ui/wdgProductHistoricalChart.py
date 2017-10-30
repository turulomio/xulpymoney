from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QColor,  QPen
from PyQt5.QtWidgets import QWidget,  QLabel
from Ui_wdgProductHistoricalChart import Ui_wdgProductHistoricalChart

import datetime
from decimal import Decimal
from canvaschart import   VCTemporalSeries
from libxulpymoney import day_end_from_date,  OHCLDuration,  InvestmentOperation,  Investment,  SetInvestmentOperationsHomogeneus

class wdgProductHistoricalChart(QWidget, Ui_wdgProductHistoricalChart):
    def __init__(self,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.view=None
        
    def pen(self, style, color):
        pen=QPen()
        pen.setStyle(style)
        pen.setColor(color)
        return pen
    def setProduct(self, product, investment=None):
        self.product=product
        self.investment=investment
        self.mem=self.product.mem
        from_=datetime.datetime.today()-datetime.timedelta(days=365*3)
        if self.investment!=None:
            if self.investment.op_actual.length()>0:
                from_=self.investment.op_actual.first().datetime
            elif self.investment.op.length()>0:
                from_=self.investment.op.first().datetime
        self.dtFrom.setDate(from_)
        self.cmbOHCLDuration.currentIndexChanged.disconnect()
        OHCLDuration.qcombobox(self.cmbOHCLDuration, OHCLDuration.Day)
        self.cmbOHCLDuration.currentIndexChanged.connect(self.on_cmbOHCLDuration_currentIndexChanged)
        
    def on_dtFrom_dateChanged(self, date):
        selected=date.toPyDate()
        if datetime.date.today()-selected<=datetime.timedelta(days=366):
            self.cmdFromRight.setEnabled(False)
        else:
            self.cmdFromRight.setEnabled(True)

    def generate(self):
        """Just draw the chart with selected options. It creates and destroys objects"""
        if self.view!=None:
            self.view.close()
        selected_datetime= day_end_from_date(self.dtFrom.date().toPyDate(), self.mem.localzone)
        self.setohcl=self.product.result.ohcl(self.cmbOHCLDuration.itemData(self.cmbOHCLDuration.currentIndex()))
        
        self.view=VCTemporalSeries()
        
        print("GENERATIUNG", self.view)
        self.verticalLayout.addWidget(self.view)
        if self.cmbChartType.currentIndex()==0:#Lines
            ls=self.view.appendTemporalSeries(self.product.name.upper(), self.product.currency)#Line seies
            for ohcl in self.setohcl.arr:
                if ohcl.datetime()>=selected_datetime:
                    self.view.appendTemporalSeriesData(ls, ohcl.datetime(), ohcl.close)
        elif self.cmbChartType.currentIndex()==1:#Candles            
            candle=self.view.appendCandlestickSeries(self.product.name, self.product.currency)#Candle series
            for ohcl in self.setohcl.arr:
                if ohcl.datetime()>=selected_datetime:
                    self.view.appendCandlestickSeriesData(candle, ohcl)
            self.view.setOHCLDuration(self.cmbOHCLDuration.itemData(self.cmbOHCLDuration.currentIndex()))
            
        if self.chkSMA50.isChecked() and self.setohcl.length()>50:#SMA50 line series
            sma50=self.view.appendTemporalSeries(self.tr("SMA50"),  self.product.currency)
            sma50.setColor(QColor(255, 170, 255))
            for dt, value in self.setohcl.sma(50):
                if dt>selected_datetime:
                    self.view.appendTemporalSeriesData(sma50, dt, value)
                
        if self.chkSMA200.isChecked() and self.setohcl.length()>200:#SMA200 line series
            sma200=self.view.appendTemporalSeries(self.tr("SMA200"),  self.product.currency)
            sma200.setColor(QColor(165, 165, 165))
            for dt, value in self.setohcl.sma(200):
                if dt>selected_datetime:
                    self.view.appendTemporalSeriesData(sma200, dt, value)
                    
        #INVESTMENT
        if self.investment!=None:
            buy=self.view.appendScatterSeries(self.tr("Buy operations"), self.product.currency)
            buy.setColor(QColor(85, 170, 127))
            sell=self.view.appendScatterSeries(self.tr("Sell operations"), self.product.currency)
            sell.setColor(QColor(170, 85, 85))
            for op in self.investment.op.arr:
                if op.tipooperacion.id in (4, ) and op.datetime>selected_datetime:
                    self.view.appendScatterSeriesData(buy, op.datetime, op.valor_accion)
                if op.tipooperacion.id in (5, ) and op.datetime>selected_datetime:
                    self.view.appendScatterSeriesData(sell, op.datetime, op.valor_accion)
            if self.investment.op_actual.length()>0:
                average_price=self.view.appendTemporalSeries(self.tr("Average price"),  self.product.currency)
                average_price.setColor(QColor(85, 170, 127))
                self.view.appendTemporalSeriesData(average_price, self.investment.op_actual.first().datetime, self.investment.op_actual.average_price(type=1).amount)
                self.view.appendTemporalSeriesData(average_price, self.mem.localzone.now(), self.investment.op_actual.average_price(type=1).amount)
                if self.investment.selling_expiration!=None:#If no selling point, it makes ugly the chart
                    selling_price=self.view.appendTemporalSeries(self.tr("Selling price"),  self.product.currency)
                    selling_price.setColor(QColor(170, 85, 85))
                    self.view.appendTemporalSeriesData(selling_price, self.investment.op_actual.first().datetime, self.investment.venta)
                    self.view.appendTemporalSeriesData(selling_price, self.mem.localzone.now(), self.investment.venta)
                    
    def display(self):
        self.view.display()
            
    @pyqtSlot(int)      
    def on_cmbChartType_currentIndexChanged(self, index):
        self.generate()
        self.display()
    @pyqtSlot(int)      
    def on_cmbOHCLDuration_currentIndexChanged(self, index):
        self.generate()
        self.display()
        
    def on_cmdFromRight_released(self):
        self.dtFrom.setDate(day_end_from_date(self.dtFrom.date().toPyDate(), self.mem.localzone)+datetime.timedelta(days=365))
        self.generate()
        self.display()        
    def on_cmdFromLeft_released(self):
        self.dtFrom.setDate(day_end_from_date(self.dtFrom.date().toPyDate(), self.mem.localzone)-datetime.timedelta(days=365))
        self.generate()
        self.display()        
    def on_cmdFromRightMax_released(self):
        self.dtFrom.setDate(self.setohcl.last().datetime()-datetime.timedelta(days=365))
        self.generate()
        self.display()        
    def on_cmdFromLeftMax_released(self):
        self.dtFrom.setDate(self.setohcl.first().datetime())
        self.generate()
        self.display()
    def on_chkSMA50_stateChanged(self, state):
        self.generate()
        self.display()
    def on_chkSMA200_stateChanged(self, state):
        self.generate()
        self.display()


class wdgProductHistoricalReinvestChart(wdgProductHistoricalChart):
    def __init__(self,  parent=None):
        wdgProductHistoricalChart.__init__(self, parent)
        self.sim_op=None
        self.sim_opactual=None
        self.lblComment=QLabel()
        
    def setReinvest(self,  sim_op,  sim_opactual):
        self.sim_op=sim_op
        self.sim_opactual=sim_opactual
        

    def generate(self):
        """Just draw the chart with selected options. It creates and destroys objects"""
            
        wdgProductHistoricalChart.generate(self)
        if self.investment!=None:
            if self.investment.op_actual.length()>0:
                
                percentage=Decimal(self.mem.settingsdb.value("frmSellingPoint/lastgainpercentage",  5))
                self.new_avg_1=self.sim_opactual.average_price().amount
                self.new_sell_price_1=self.new_avg_1*(1+percentage/Decimal(100))
                
                new_average_price=self.view.appendTemporalSeries(self.tr("New average price: {}").format(str(self.new_avg_1)),  self.product.currency)
                new_average_price.setColor(QColor(85, 170, 127))
                new_average_price.setPen(self.pen(Qt.DashLine, QColor(85, 170, 127)))
                self.view.appendTemporalSeriesData(new_average_price, self.investment.op_actual.first().datetime, self.new_avg_1)
                self.view.appendTemporalSeriesData(new_average_price, self.mem.localzone.now(), self.new_avg_1)
                
                if self.investment.selling_expiration!=None:#If no selling point, it makes ugly the chart
                    
                    new_selling_price=self.view.appendTemporalSeries(self.tr("New selling price"),  self.product.currency)
                    new_selling_price.setColor(QColor(170, 85, 85))
                    new_selling_price.setPen(self.pen(Qt.DashLine, QColor(170, 85, 85)))
                    self.view.appendTemporalSeriesData(new_selling_price, self.investment.op_actual.first().datetime, self.new_sell_price_1)
                    self.view.appendTemporalSeriesData(new_selling_price, self.mem.localzone.now(), self.new_sell_price_1)
                    
                gains=(self.new_sell_price_1-self.new_avg_1)*self.sim_opactual.acciones()
                self.lblComment.setText(self.tr("Gains percentage: {} %. Gains in the new selling reference: {}".format(percentage, self.investment.product.currency.string(gains))))
                self.verticalLayout.addWidget(self.lblComment)

class wdgProductHistoricalBuyChart(wdgProductHistoricalChart):
    def __init__(self,  parent=None):
        wdgProductHistoricalChart.__init__(self, parent)
        self.lblComment=QLabel()
        
    def generate(self):
        """Just draw the chart with selected options. It creates and destroys objects"""
        wdgProductHistoricalChart.generate(self)
        
        percentage=Decimal(self.mem.settingsdb.value("frmSellingPoint/lastgainpercentage",  5))

        inv=Investment(self.mem).init__create("Buy Chart", None, None, self.product, None, True, -1)
        inv.op=SetInvestmentOperationsHomogeneus(self.mem, inv)
        #FIRST REINVESTMETN
        d1=InvestmentOperation(self.mem).init__create  (   self.mem.tiposoperaciones.find_by_id(4), 
                                                                                        self.mem.localzone.now(), 
                                                                                        inv, 
                                                                                        int(2500/self.product.result.basic.last.quote), 
                                                                                        0, 
                                                                                        0, 
                                                                                        self.product.result.basic.last.quote, 
                                                                                        "",  
                                                                                        True, 
                                                                                        1,  
                                                                                        -10000
                                                                                    )
        inv.op.append(d1)
        (inv.op_actual, inv.op_historica)=inv.op.calcular()
        new_average_price=self.view.appendTemporalSeries(self.tr("New average price: {}").format(str(0)),  self.product.currency)
        new_average_price.setColor(QColor(85, 170, 127))
        new_average_price.setPen(self.pen(Qt.SolidLine, QColor(85, 170, 127)))
        self.view.appendTemporalSeriesData(new_average_price, inv.op_actual.first().datetime-datetime.timedelta(days=365), inv.op_actual.average_price().amount)
        self.view.appendTemporalSeriesData(new_average_price, self.mem.localzone.now(), inv.op_actual.average_price().amount)

        new_selling_price=self.view.appendTemporalSeries(self.tr("New selling price"),  self.product.currency)
        new_selling_price.setColor(QColor(170, 85, 85))
        new_selling_price.setPen(self.pen(Qt.SolidLine, QColor(170, 85, 85)))
        self.view.appendTemporalSeriesData(new_selling_price, inv.op_actual.first().datetime-datetime.timedelta(days=365), inv.op_actual.average_price().amount*(1+percentage/Decimal(100)))
        self.view.appendTemporalSeriesData(new_selling_price, self.mem.localzone.now(),  inv.op_actual.average_price().amount*(1+percentage/Decimal(100)))
        #SECOND REINVESTMENT
        purchase2=d1.valor_accion*Decimal(0.67)
        d2=InvestmentOperation(self.mem).init__create  (   self.mem.tiposoperaciones.find_by_id(4), 
                                                                                        self.mem.localzone.now(), 
                                                                                        inv, 
                                                                                        int(3500/purchase2), 
                                                                                        0, 
                                                                                        0, 
                                                                                        purchase2, 
                                                                                        "",  
                                                                                        True, 
                                                                                        1,  
                                                                                        -9999
                                                                                    )
        inv.op.append(d2)
        (inv.op_actual, inv.op_historica)=inv.op.calcular()
        new_average_price=self.view.appendTemporalSeries(self.tr("New average price: {}").format(str(0)),  self.product.currency)
        new_average_price.setColor(QColor(85, 170, 127))
        new_average_price.setPen(self.pen(Qt.DashLine, QColor(85, 170, 127)))
        self.view.appendTemporalSeriesData(new_average_price, inv.op_actual.first().datetime-datetime.timedelta(days=365), inv.op_actual.average_price().amount)
        self.view.appendTemporalSeriesData(new_average_price, self.mem.localzone.now(), inv.op_actual.average_price().amount)

        new_selling_price=self.view.appendTemporalSeries(self.tr("New selling price"),  self.product.currency)
        new_selling_price.setColor(QColor(170, 85, 85))
        new_selling_price.setPen(self.pen(Qt.DashLine, QColor(170, 85, 85)))
        self.view.appendTemporalSeriesData(new_selling_price, inv.op_actual.first().datetime-datetime.timedelta(days=365), inv.op_actual.average_price().amount*(1+percentage/Decimal(100)))
        self.view.appendTemporalSeriesData(new_selling_price, self.mem.localzone.now(),  inv.op_actual.average_price().amount*(1+percentage/Decimal(100)))
        
        self.lblComment.setText(self.tr("Lines calculated investing: 2500 €, 3500 €, 12000 €, 12000 €." + " " + self.tr("Selling percentage: {} %.".format(percentage))))
        
#        
#        if self.investment!=None:
#            if self.investment.op_actual.length()>0:
#                percentagespersonal=[0.777, 0.5225, 0.4035, 0.269]
#                percentagesmy=percentagespersonal
        #
        #
        #        if self.purchase_type==2:
        #            
        #            dat=[]
        #            dat.append(self.from_dt)
        #            dat.append(datetime.datetime.now())
        #            self.price_sell=self.price_buy*(1+percentage/Decimal(100))
        #            
#                self.price_a1=self.price_buy*Decimal(percentagesmy[0])
#                self.price_s1=self.price_a1*(1+percentage/Decimal(100))
#                self.price_b1=self.price_buy*Decimal(1-0.33)
#                
#                self.price_a2=self.price_buy*Decimal(percentagesmy[1])
#                self.price_s2=self.price_a2*(1+percentage/Decimal(100))
#                self.price_b2=self.price_b1*Decimal(1-0.33)
#                
#                self.price_a3=self.price_buy*Decimal(percentagesmy[2])
#                self.price_s3=self.price_a3*(1+percentage/Decimal(100))
#                self.price_b3=self.price_b2*Decimal(1-0.33)



#        
##                self.new_avg_1=self.sim_opactual.average_price().amount
##                self.new_sell_price_1=self.new_avg_1*(1+percentage/Decimal(100))
#                
#                new_average_price=self.view.appendTemporalSeries(self.tr("New average price: {}").format(str(self.new_avg_1)),  self.product.currency)
#                new_average_price.setColor(QColor(85, 170, 127))
#                new_average_price.setPen(self.pen(Qt.DashLine, QColor(85, 170, 127)))
#                self.view.appendTemporalSeriesData(new_average_price, self.investment.op_actual.first().datetime, self.new_avg_1)
#                self.view.appendTemporalSeriesData(new_average_price, self.mem.localzone.now(), self.new_avg_1)
#                
#                if self.investment.selling_expiration!=None:#If no selling point, it makes ugly the chart
#                    
#                    new_selling_price=self.view.appendTemporalSeries(self.tr("New selling price"),  self.product.currency)
#                    new_selling_price.setColor(QColor(170, 85, 85))
#                    new_selling_price.setPen(self.pen(Qt.DashLine, QColor(170, 85, 85)))
#                    self.view.appendTemporalSeriesData(new_selling_price, self.investment.op_actual.first().datetime, self.new_sell_price_1)
#                    self.view.appendTemporalSeriesData(new_selling_price, self.mem.localzone.now(), self.new_sell_price_1)
#                    
#                gains=(self.new_sell_price_1-self.new_avg_1)*self.sim_opactual.acciones()
#                label=QLabel(self.tr("Gains percentage: {} %. Gains in the new selling reference: {}".format(percentage, self.investment.product.currency.string(gains))))
#                self.verticalLayout.addWidget(label)
