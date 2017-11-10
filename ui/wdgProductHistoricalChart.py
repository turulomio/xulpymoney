from PyQt5.QtCore import pyqtSlot, Qt,  QDate
from PyQt5.QtGui import QColor,  QPen,  QIcon, QPixmap
from PyQt5.QtWidgets import QWidget,  QHBoxLayout, QLabel,  QToolButton,  QSpacerItem,  QSizePolicy
from Ui_wdgProductHistoricalChart import Ui_wdgProductHistoricalChart

import datetime
from decimal import Decimal
from myqlineedit import myQLineEdit
from canvaschart import   VCTemporalSeries
from libxulpymoney import day_end_from_date,  OHCLDuration,  InvestmentOperation,  Investment,  Money, SetInvestmentOperationsHomogeneus

class wdgProductHistoricalChart(QWidget, Ui_wdgProductHistoricalChart):
    def __init__(self,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.view=None
        self.dtFrom.blockSignals(True)
        
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
        self.dtFrom.blockSignals(False)
        self.cmbOHCLDuration.currentIndexChanged.disconnect()
        OHCLDuration.qcombobox(self.cmbOHCLDuration, OHCLDuration.Day)
        self.cmbOHCLDuration.currentIndexChanged.connect(self.on_cmbOHCLDuration_currentIndexChanged)
        
    @pyqtSlot(QDate) 
    def on_dtFrom_dateChanged(self, date):
        selected=date.toPyDate()
        print(selected)
        if datetime.date.today()-selected<=datetime.timedelta(days=366):
            self.cmdFromRight.setEnabled(False)
        else:
            self.cmdFromRight.setEnabled(True)
        self.generate()
        self.display()

    def generate(self):
        """Just draw the chart with selected options. It creates and destroys objects"""
        if self.view!=None:
            self.view.hide()
            self.view.close()
            self.verticalLayout.removeWidget(self.view)

        selected_datetime= day_end_from_date(self.dtFrom.date().toPyDate(), self.mem.localzone)
        self.setohcl=self.product.result.ohcl(self.cmbOHCLDuration.itemData(self.cmbOHCLDuration.currentIndex()))
        
        self.view=VCTemporalSeries()
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
            #Buy sell operations
            buy=self.view.appendScatterSeries(self.tr("Buy operations"), self.product.currency)
            buy.setColor(QColor(85, 170, 127))
            sell=self.view.appendScatterSeries(self.tr("Sell operations"), self.product.currency)
            sell.setColor(QColor(170, 85, 85))
            for op in self.investment.op.arr:
                print (op.datetime, selected_datetime-datetime.timedelta(days=10))
                if op.tipooperacion.id in (4, ) and op.datetime.date()>=selected_datetime.date():
                    self.view.appendScatterSeriesData(buy, op.datetime, op.valor_accion)
                if op.tipooperacion.id in (5, ) and op.datetime.date()>=selected_datetime.date():
                    self.view.appendScatterSeriesData(sell, op.datetime, op.valor_accion)
            
            #Average price
            if self.investment.op_actual.length()>0:
                m_average_price=self.investment.op_actual.average_price(type=1)
                average_price=self.view.appendTemporalSeries(self.tr("Average price: {}".format(m_average_price.string())),  self.product.currency)
                average_price.setColor(QColor(85, 170, 127))
                self.view.appendTemporalSeriesData(average_price, self.investment.op_actual.first().datetime, m_average_price.amount)
                self.view.appendTemporalSeriesData(average_price, self.mem.localzone.now(), m_average_price.amount)
                if self.investment.selling_expiration!=None:#If no selling point, it makes ugly the chart
                    selling_price=self.view.appendTemporalSeries(self.tr("Selling price {} to gain {}".format(self.investment.product.currency.string(self.investment.venta),  self.investment.op_actual.gains_in_selling_point())),  self.product.currency)
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
        self.labelBuyPrice=QLabel(self.tr("Add wanted price"))
        self.txtBuyPrice=myQLineEdit(self)                                                                                                    
        self.cmdBuyPrice= QToolButton(self)               
        icon = QIcon()
        icon.addPixmap(QPixmap(":/xulpymoney/tools-wizard.png"), QIcon.Normal, QIcon.Off)
        self.cmdBuyPrice.setIcon(icon)                                      
        self.horizontalLayout_3.addWidget(self.labelBuyPrice)
        self.spacerBuyPrice = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_3.addWidget(self.txtBuyPrice)
        self.horizontalLayout_3.addWidget(self.cmdBuyPrice)
        self.horizontalLayout_3.addItem(self.spacerBuyPrice)
        
        self.cmdBuyPrice.released.connect(self.on_cmdBuyPrice_released)
        
        self.layAmounts = QHBoxLayout()
        self.label1=QLabel(self)
        self.label1.setText(self.tr("First purchase"))
        self.txt1=myQLineEdit(self)
        self.txt1.setText(2500)
        self.label2=QLabel(self)
        self.label2.setText(self.tr("First reinvestment"))
        self.txt2=myQLineEdit(self)
        self.txt2.setText(3500)
        self.label3=QLabel(self)
        self.label3.setText(self.tr("Second reinvestment"))
        self.txt3=myQLineEdit(self)
        self.txt3.setText(12000)
        
        self.labelGains=QLabel(self)
        self.labelGains.setText(self.tr("Gains percentage"))
        self.txtGains=myQLineEdit(self)
        self.txtGains.setText(10)
        
        
        self.labelLastOperationPercentage=QLabel(self)
        self.labelLastOperationPercentage.setText(self.tr("Last Operation next buy percentage"))
        self.txtLastOperationPercentage=myQLineEdit(self)
        self.txtLastOperationPercentage.setText(33)
        
        self.spacer1 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.spacer2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.spacer3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.spacer4 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.spacer5 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.spacer6 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.layAmounts.addItem(self.spacer1)
        self.layAmounts.addWidget(self.label1)
        self.layAmounts.addWidget(self.txt1)
        self.layAmounts.addItem(self.spacer2)
        self.layAmounts.addWidget(self.label2)
        self.layAmounts.addWidget(self.txt2)
        self.layAmounts.addItem(self.spacer3)
        self.layAmounts.addWidget(self.label3)
        self.layAmounts.addWidget(self.txt3)
        self.layAmounts.addItem(self.spacer4)
        self.layAmounts.addWidget(self.labelGains)
        self.layAmounts.addWidget(self.txtGains)
        self.layAmounts.addItem(self.spacer5)
        self.layAmounts.addWidget(self.labelLastOperationPercentage)
        self.layAmounts.addWidget(self.txtLastOperationPercentage)
        self.layAmounts.addItem(self.spacer6)
        self.verticalLayout.addLayout(self.layAmounts)
        

    def setPrice(self, price):
        """
            Must be added after setProduct
        """
        self.txtBuyPrice.setText(price)
        
    def on_cmdBuyPrice_released(self):
        if self.txtBuyPrice.isValid():
            self.generate()
            self.display()
        
    
        
    def generate(self):
        """Just draw the chart with selected options. It creates and destroys objects"""
        wdgProductHistoricalChart.generate(self)
        
        percentage=self.txtGains.decimal()
        selected_datetime= day_end_from_date(self.dtFrom.date().toPyDate(), self.mem.localzone)

        inv=Investment(self.mem).init__create("Buy Chart", None, None, self.product, None, True, -1)
        inv.op=SetInvestmentOperationsHomogeneus(self.mem, inv)
        #PURCHASE
        d1=InvestmentOperation(self.mem).init__create  (   self.mem.tiposoperaciones.find_by_id(4), 
                                                                                        self.mem.localzone.now(), 
                                                                                        inv, 
                                                                                        int(self.txt1.decimal()/self.txtBuyPrice.decimal()), 
                                                                                        0, 
                                                                                        0, 
                                                                                        self.txtBuyPrice.decimal(), 
                                                                                        "",  
                                                                                        True, 
                                                                                        1,  
                                                                                        -10000
                                                                                    )
        inv.op.append(d1)
        (inv.op_actual, inv.op_historica)=inv.op.calcular()
        m_new_average_price=inv.op_actual.average_price()
        new_average_price=self.view.appendTemporalSeries(self.tr("Buy: {}".format(m_new_average_price.string())).format(str(0)),  self.product.currency)
        new_average_price.setColor(QColor(85, 170, 127))
        new_average_price.setPen(self.pen(Qt.SolidLine, QColor(85, 170, 127)))
        self.view.appendTemporalSeriesData(new_average_price, selected_datetime, m_new_average_price.amount)
        self.view.appendTemporalSeriesData(new_average_price, self.mem.localzone.now(), m_new_average_price.amount)

        m_new_selling_price=  inv.op_actual.average_price()*(1+percentage/Decimal(100))
        new_selling_price=self.view.appendTemporalSeries(self.tr("Sell at {} to gain {}".format(m_new_selling_price.string(), inv.op_actual.gains_from_percentage(self.txtGains.decimal()))),  self.product.currency)
        new_selling_price.setColor(QColor(170, 85, 85))
        new_selling_price.setPen(self.pen(Qt.SolidLine, QColor(170, 85, 85)))
        self.view.appendTemporalSeriesData(new_selling_price, selected_datetime, m_new_selling_price.amount)
        self.view.appendTemporalSeriesData(new_selling_price, self.mem.localzone.now(),m_new_selling_price.amount)

        #FIRST REINVESTMENT
        purchase2=Money(self.mem, d1.valor_accion*(1-self.txtLastOperationPercentage.decimal()/100),  self.product.currency)
        d2=InvestmentOperation(self.mem).init__create  (   self.mem.tiposoperaciones.find_by_id(4), 
                                                                                        self.mem.localzone.now(), 
                                                                                        inv, 
                                                                                        int(self.txt2.decimal()/purchase2.amount), 
                                                                                        0, 
                                                                                        0, 
                                                                                        purchase2.amount, 
                                                                                        "",  
                                                                                        True, 
                                                                                        1,  
                                                                                        -9999
                                                                                    )
        inv.op.append(d2)
        (inv.op_actual, inv.op_historica)=inv.op.calcular()
        new_purchase_price=self.view.appendTemporalSeries(self.tr("First reinvestment (FR) purchase: {}").format(purchase2.string()),  self.product.currency)
        new_purchase_price.setColor(QColor(85, 170, 127))
        new_purchase_price.setPen(self.pen(Qt.DashLine, QColor(85, 170, 127)))
        self.view.appendTemporalSeriesData(new_purchase_price, selected_datetime, purchase2.amount)
        self.view.appendTemporalSeriesData(new_purchase_price, self.mem.localzone.now(), purchase2.amount)
        
        new_average_price=self.view.appendTemporalSeries(self.tr("FR average price: {}").format(inv.op_actual.average_price().string()),  self.product.currency)
        new_average_price.setColor(QColor(85, 170, 127))
        new_average_price.setPen(self.pen(Qt.DashLine, QColor(85, 85, 170)))
        self.view.appendTemporalSeriesData(new_average_price, selected_datetime, inv.op_actual.average_price().amount)
        self.view.appendTemporalSeriesData(new_average_price, self.mem.localzone.now(), inv.op_actual.average_price().amount)

        new_selling_price=self.view.appendTemporalSeries(self.tr("FR sale price at {} to gain {}".format(self.product.currency.string(inv.op_actual.average_price().amount*(1+percentage/Decimal(100))), inv.op_actual.gains_from_percentage(self.txtGains.decimal()))),   self.product.currency)
        new_selling_price.setColor(QColor(170, 85, 85))
        new_selling_price.setPen(self.pen(Qt.DashLine, QColor(170, 85, 85)))
        self.view.appendTemporalSeriesData(new_selling_price, selected_datetime, inv.op_actual.average_price().amount*(1+percentage/Decimal(100)))
        self.view.appendTemporalSeriesData(new_selling_price, self.mem.localzone.now(),  inv.op_actual.average_price().amount*(1+percentage/Decimal(100)))
        
        

        #SECOND REINVESTMENT
        purchase3=Money(self.mem, d2.valor_accion*(1-self.txtLastOperationPercentage.decimal()/100),  self.product.currency)
        d3=InvestmentOperation(self.mem).init__create  (   self.mem.tiposoperaciones.find_by_id(4), 
                                                                                        self.mem.localzone.now(), 
                                                                                        inv, 
                                                                                        int(self.txt3.decimal()/purchase3.amount), 
                                                                                        0, 
                                                                                        0, 
                                                                                        purchase3.amount, 
                                                                                        "",  
                                                                                        True, 
                                                                                        1,  
                                                                                        -9999
                                                                                    )
        inv.op.append(d3)
        (inv.op_actual, inv.op_historica)=inv.op.calcular()
        new_purchase_price=self.view.appendTemporalSeries(self.tr("Second reinvestment (SR) purchase: {}").format(purchase3.string()),  self.product.currency)
        new_purchase_price.setColor(QColor(85, 170, 127))
        new_purchase_price.setPen(self.pen(Qt.DotLine, QColor(85, 170, 127)))
        self.view.appendTemporalSeriesData(new_purchase_price, selected_datetime, purchase3.amount)
        self.view.appendTemporalSeriesData(new_purchase_price, self.mem.localzone.now(), purchase3.amount)
        
        new_average_price=self.view.appendTemporalSeries(self.tr("SR average price: {}").format(inv.op_actual.average_price().string()),  self.product.currency)
        new_average_price.setColor(QColor(85, 170, 127))
        new_average_price.setPen(self.pen(Qt.DotLine, QColor(85, 85, 170)))
        self.view.appendTemporalSeriesData(new_average_price, selected_datetime, inv.op_actual.average_price().amount)
        self.view.appendTemporalSeriesData(new_average_price, self.mem.localzone.now(), inv.op_actual.average_price().amount)

        new_selling_price=self.view.appendTemporalSeries(self.tr("SR sale price at {} to gain {}".format(self.product.currency.string(inv.op_actual.average_price().amount*(1+percentage/Decimal(100))), inv.op_actual.gains_from_percentage(self.txtGains.decimal()))),   self.product.currency)
        new_selling_price.setColor(QColor(170, 85, 85))
        new_selling_price.setPen(self.pen(Qt.DotLine, QColor(170, 85, 85)))
        self.view.appendTemporalSeriesData(new_selling_price, selected_datetime, inv.op_actual.average_price().amount*(1+percentage/Decimal(100)))
        self.view.appendTemporalSeriesData(new_selling_price, self.mem.localzone.now(),  inv.op_actual.average_price().amount*(1+percentage/Decimal(100)))
        
        
