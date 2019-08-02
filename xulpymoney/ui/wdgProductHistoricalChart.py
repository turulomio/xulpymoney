## @namespace xulpymoney.ui.wdgProductHistoricalChart
## @brief Several product historical chart widgets

from PyQt5.QtCore import pyqtSlot, Qt,  QDate
from PyQt5.QtGui import QColor,  QPen,  QIcon, QPixmap,  QWheelEvent
from PyQt5.QtWidgets import QWidget,  QHBoxLayout, QLabel,  QToolButton,  QSpacerItem,  QSizePolicy,  QPushButton, QVBoxLayout, QDialog, QLineEdit, QDoubleSpinBox
from xulpymoney.ui.Ui_wdgProductHistoricalChart import Ui_wdgProductHistoricalChart

import datetime
import logging
from decimal import Decimal
from xulpymoney.ui.myqlineedit import myQLineEdit
from xulpymoney.ui.canvaschart import   VCTemporalSeries
from xulpymoney.libxulpymoney import InvestmentOperation,  Investment,  Money, Percentage, InvestmentOperationHomogeneusManager
from xulpymoney.libxulpymoneyfunctions import day_start_from_date, day_start, string2list_of_integers
from xulpymoney.libxulpymoneytypes import eHistoricalChartAdjusts, eOHCLDuration,  eOperationType
from xulpymoney.ui.wdgOpportunitiesAdd import wdgOpportunitiesAdd

## Main class that sets a product (can add an investment too) with setProduct function
##
## OHCL set is updated each time generate function is called
class wdgProductHistoricalChart(QWidget, Ui_wdgProductHistoricalChart):
    def __init__(self,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.view=None
        self.dtFrom.blockSignals(True)
        self.HistoricalChartAdjusts=eHistoricalChartAdjusts.Splits
        
    def _pen(self, style, color):
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
                from_=self.investment.op_actual.first().datetime-datetime.timedelta(days=30)
            elif self.investment.op.length()>0:
                from_=self.investment.op.first().datetime-datetime.timedelta(days=30)
        self.dtFrom.setDate(from_)
        self.dtFrom.blockSignals(False)
        self.cmbOHCLDuration.currentIndexChanged.disconnect()
        eOHCLDuration.qcombobox(self.cmbOHCLDuration, eOHCLDuration.Day)
        self.cmbOHCLDuration.currentIndexChanged.connect(self.on_cmbOHCLDuration_currentIndexChanged)
        
    @pyqtSlot(QDate) 
    def on_dtFrom_dateChanged(self, date):
        selected=date.toPyDate()
        if datetime.date.today()-selected<=datetime.timedelta(days=366):
            self.cmdFromRight.setEnabled(False)
        else:
            self.cmdFromRight.setEnabled(True)
        self.generate()
        self.display()

    ## Just draw the chart with selected options. It creates and destroys objects
    ##
    ## self.setohcl is set calling this function
    def generate(self):
        if self.view!=None:
            self.view.hide()
            self.view.close()
            self.verticalLayout.removeWidget(self.view)

        selected_datetime= day_start_from_date(self.dtFrom.date().toPyDate(), self.mem.localzone)
        self.setohcl=self.product.result.ohcl(self.cmbOHCLDuration.itemData(self.cmbOHCLDuration.currentIndex()), eHistoricalChartAdjusts.Splits)
        
        self.view=VCTemporalSeries()
        self.verticalLayout.addWidget(self.view)
        if self.cmbChartType.currentIndex()==0:#Lines
            ls=self.view.appendTemporalSeries(self.product.name.upper(), self.product.currency)#Line seies
            for ohcl in self.setohcl.arr:
                if ohcl.datetime()>=selected_datetime:
                    self.view.appendTemporalSeriesData(ls, day_start(ohcl.datetime(), self.mem.localzone), ohcl.close) #Added day_start to show the purchase circle the first day
        elif self.cmbChartType.currentIndex()==1:#Candles            
            candle=self.view.appendCandlestickSeries(self.product.name, self.product.currency)#Candle series
            for ohcl in self.setohcl.arr:
                if ohcl.datetime()>=selected_datetime-datetime.timedelta(days=10):#Added one day to show the purchase circle the first day
                    self.view.appendCandlestickSeriesData(candle, ohcl)
            self.view.setOHCLDuration(self.cmbOHCLDuration.itemData(self.cmbOHCLDuration.currentIndex()))
            
        if self.chkSMA50.isChecked() and self.setohcl.length()>50:#SMA50 line series
            sma50=self.view.appendTemporalSeries(self.tr("SMA50"),  self.product.currency)
            sma50.setColor(QColor(255, 170, 255))
            for dt, value in self.setohcl.sma(50):
                if dt>=selected_datetime:
                    self.view.appendTemporalSeriesData(sma50, dt, value)
                
        if self.chkSMA200.isChecked() and self.setohcl.length()>200:#SMA200 line series
            sma200=self.view.appendTemporalSeries(self.tr("SMA200"),  self.product.currency)
            sma200.setColor(QColor(165, 165, 165))
            for dt, value in self.setohcl.sma(200):
                if dt>=selected_datetime:
                    self.view.appendTemporalSeriesData(sma200, dt, value)

        if self.chkMedian.isChecked():#Median value
            median=self.setohcl.closes_median_value()
            med=self.view.appendTemporalSeries(self.tr("Median at {}".format(self.product.currency.string(median))),  self.product.currency)
            med.setColor(QColor(165, 165, 0))
            self.view.appendTemporalSeriesData(med, selected_datetime, median)
            self.view.appendTemporalSeriesData(med, self.mem.localzone.now(), median)

        if not self.chkAdjustSplits.isChecked():#
            ls=self.view.appendTemporalSeries(self.product.name.upper() + " (No adjust)", self.product.currency)#Line seies
            for ohcl in self.product.result.ohcl(self.cmbOHCLDuration.itemData(self.cmbOHCLDuration.currentIndex()), eHistoricalChartAdjusts.NoAdjusts).arr:
                if ohcl.datetime()>=selected_datetime:
                    self.view.appendTemporalSeriesData(ls, day_start(ohcl.datetime(), self.mem.localzone), ohcl.close) 

        if self.chkAdjustDividends.isChecked():#
            ls=self.view.appendTemporalSeries(self.product.name.upper() + (" (Dividend adjust)"), self.product.currency)#Line seies
            for ohcl in self.product.result.ohcl(self.cmbOHCLDuration.itemData(self.cmbOHCLDuration.currentIndex()), eHistoricalChartAdjusts.SplitsAndDividends).arr:
                if ohcl.datetime()>=selected_datetime:
                    self.view.appendTemporalSeriesData(ls, day_start(ohcl.datetime(), self.mem.localzone), ohcl.close) 

        #INVESTMENT
        if self.investment!=None:
            #Buy sell operations
            buy=self.view.appendScatterSeries(self.tr("Buy operations"), self.product.currency)
            buy.setColor(QColor(85, 170, 127))
            sell=self.view.appendScatterSeries(self.tr("Sell operations"), self.product.currency)
            sell.setColor(QColor(170, 85, 85))
            for op in self.investment.op.arr:
                if (    op.tipooperacion.id in (eOperationType.SharesAdd, eOperationType.SharesPurchase, eOperationType.TransferSharesDestiny ) or 
                        (op.tipooperacion.id==eOperationType.TransferFunds and op.shares>0)
                    ) and op.datetime>=selected_datetime:
                    self.view.appendScatterSeriesData(buy, op.datetime, op.valor_accion)
                if (    op.tipooperacion.id in (eOperationType.TransferSharesOrigin, eOperationType.SharesSale) or 
                        (op.tipooperacion.id==eOperationType.TransferFunds and op.shares<0)
                    ) and op.datetime>=selected_datetime:
                    self.view.appendScatterSeriesData(sell, op.datetime, op.valor_accion)
            
            #Average price
            if self.investment.op_actual.length()>0:
                m_selling_price=self.investment.selling_price()
                m_average_price=self.investment.op_actual.average_price(type=1)
                if self.investment.selling_expiration!=None:#If no selling point, it makes ugly the chart
                    selling_price=self.view.appendTemporalSeries(self.tr("Selling price at {} to gain {}".format(m_selling_price,  self.investment.op_actual.gains_in_selling_point())),  self.product.currency)
                    selling_price.setColor(QColor(170, 85, 85))
                    self.view.appendTemporalSeriesData(selling_price, self.investment.op_actual.first().datetime, m_selling_price.amount)
                    self.view.appendTemporalSeriesData(selling_price, self.mem.localzone.now(), m_selling_price.amount)
                average_price=self.view.appendTemporalSeries(self.tr("Average price at {}".format(m_average_price)),  self.product.currency)
                average_price.setColor(QColor(85, 170, 127))
                self.view.appendTemporalSeriesData(average_price, self.investment.op_actual.first().datetime, m_average_price.amount)
                self.view.appendTemporalSeriesData(average_price, self.mem.localzone.now(), m_average_price.amount)


    ## This code generates an Horizontal Layout with an spin Gains, it's not shown by default, but it will be usefull in several subclases
    ##  You can access objects normally because they are in self
    def laySpinGainsPercentage(self, parent, spacer_at_right=False):
        self.layGainsPercentage = QHBoxLayout(parent)
        self.layGainsPercentage.setObjectName("layGainsPercentage")
        self.lblGainsPercentage = QLabel(parent)
        self.lblGainsPercentage.setObjectName("lblGainsPercentage")
        self.lblGainsPercentage.setText(self.tr("Gains percentage"))
        self.layGainsPercentage.addWidget(self.lblGainsPercentage)
        self.spnGainsPercentage = QDoubleSpinBox(parent)
        self.spnGainsPercentage.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.spnGainsPercentage.setMaximum(300.0)
        self.spnGainsPercentage.setSingleStep(0.5)
        self.spnGainsPercentage.setProperty("value", 10.0)
        self.spnGainsPercentage.setObjectName("spnGainsPercentage")
        self.layGainsPercentage.addWidget(self.spnGainsPercentage)
        if spacer_at_right==True:
            spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
            self.layGainsPercentage.addItem(spacerItem)
        return self.layGainsPercentage

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
        self.dtFrom.setDate(day_start_from_date(self.dtFrom.date().toPyDate(), self.mem.localzone)+datetime.timedelta(days=365))
        self.generate()
        self.display()        
        
    def on_cmdFromLeft_released(self):
        self.dtFrom.setDate(day_start_from_date(self.dtFrom.date().toPyDate(), self.mem.localzone)-datetime.timedelta(days=365))
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
    def on_chkAdjustSplits_stateChanged(self, state):
        self.generate()
        self.display()
    def on_chkAdjustDividends_stateChanged(self, state):
        self.generate()
        self.display()
    
    ## Function executed when changing state in QCheckbox chkmedian
    def on_chkMedian_stateChanged(self, state):
        self.generate()
        self.display()
        
    @pyqtSlot(QWheelEvent)
    def wheelEvent(self, event: QWheelEvent):
        def checkDate(newdate):
            """
                Check newdate doesn't go over bounds
            """
            date=self.dtFrom.date()
            firstdate=self.product.result.ohcl(self.cmbOHCLDuration.itemData(self.cmbOHCLDuration.currentIndex())).first().datetime().date()
            if newdate>date:
                if newdate>datetime.date.today():
                    return date
                else:
                    return newdate
            else:#newdate<=date
                if newdate<firstdate:
                    return date
                else:
                    return newdate
        ##############################  
        event.accept()#If I dont use this makes two events
        if event.modifiers() == Qt.ControlModifier:
            step=30
        elif event.modifiers() == Qt.ShiftModifier:
            step=7
        else:
            step=365

        if event.angleDelta().y()<0:
            self.dtFrom.setDate(checkDate(self.dtFrom.date().toPyDate()-datetime.timedelta(days=step)))
        else:
            self.dtFrom.setDate(checkDate(self.dtFrom.date().toPyDate()+datetime.timedelta(days=step)))


class wdgProductHistoricalReinvestChart(wdgProductHistoricalChart):
    def __init__(self,  parent=None):
        wdgProductHistoricalChart.__init__(self, parent)
        self.sim_op=None
        self.sim_opactual=None
        
    def setReinvest(self,  sim_op,  sim_opactual):
        self.sim_op=sim_op
        self.sim_opactual=sim_opactual
        self.mem=sim_op.mem
        self.verticalLayout.addLayout(self.laySpinGainsPercentage(self, spacer_at_right=True))
        self.spnGainsPercentage.setValue(float(self.mem.settingsdb.value("frmSellingPoint/lastgainpercentage",  5)))
        self.spnGainsPercentage.valueChanged.connect(self.on_spnGainsPercentage_valueChanged)
        

    def generate(self):
        """Just draw the chart with selected options. It creates and destroys objects"""
            
        wdgProductHistoricalChart.generate(self)
        if self.investment!=None:
            if self.investment.op_actual.length()>0:
                #Calcs
                percentage=Percentage(self.spnGainsPercentage.value(), 100)
                new_avg_1=self.sim_opactual.average_price()
                new_sell_price_1=self.sim_opactual.average_price_after_a_gains_percentage(percentage)                
                new_purchase_price_1=self.sim_opactual.last().price()
                gains_1=self.sim_opactual.gains_from_percentage(percentage)
                
                #First reinvestment
                if self.investment.selling_expiration!=None:#If no selling point, it makes ugly the chart
                    new_selling_price=self.view.appendTemporalSeries(self.tr("Reinvestment selling price at {} to gain {}".format(new_sell_price_1, gains_1)),  self.product.currency)
                    new_selling_price.setColor(QColor(170, 85, 85))
                    new_selling_price.setPen(self._pen(Qt.DashLine, QColor(170, 85, 85)))
                    self.view.appendTemporalSeriesData(new_selling_price, self.investment.op_actual.first().datetime, new_sell_price_1.amount)
                    self.view.appendTemporalSeriesData(new_selling_price, self.mem.localzone.now(), new_sell_price_1.amount)
                
                new_average_price=self.view.appendTemporalSeries(self.tr("Reinvestment average price at {}").format(new_avg_1),  self.product.currency)
                new_average_price.setColor(QColor(85, 85, 170))
                new_average_price.setPen(self._pen(Qt.DashLine, QColor(85, 85, 170)))
                self.view.appendTemporalSeriesData(new_average_price, self.investment.op_actual.first().datetime, new_avg_1.amount)
                self.view.appendTemporalSeriesData(new_average_price, self.mem.localzone.now(), new_avg_1.amount)
                
                new_purchase_price=self.view.appendTemporalSeries(self.tr("Reinvestment purchase at {}").format(new_purchase_price_1),  self.product.currency)
                new_purchase_price.setColor(QColor(85, 170, 127))
                new_purchase_price.setPen(self._pen(Qt.DashLine, QColor(85, 170, 127)))
                self.view.appendTemporalSeriesData(new_purchase_price, self.sim_opactual.first().datetime, new_purchase_price_1.amount)
                self.view.appendTemporalSeriesData(new_purchase_price, self.mem.localzone.now(), new_purchase_price_1.amount) 

    @pyqtSlot(float) 
    def on_spnGainsPercentage_valueChanged(self, value):
        self.generate()
        self.display()

class ReinvestmentLines:
    Buy=0
    Average=1
    Sell=2


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
        self.label1.setText(self.tr("Amounts to invest separated by ;"))
        self.txtAmounts=QLineEdit(self)
        self.txtAmounts.setText("2500;3500;8400;8400")
        
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
        self.layAmounts.addWidget(self.txtAmounts)
        self.layAmounts.addItem(self.spacer2)
        self.layAmounts.addLayout(self.laySpinGainsPercentage(self))
        self.layAmounts.addItem(self.spacer5)
        self.layAmounts.addWidget(self.labelLastOperationPercentage)
        self.layAmounts.addWidget(self.txtLastOperationPercentage)
        self.layAmounts.addItem(self.spacer6)
        self.verticalLayout.addLayout(self.layAmounts)
        
        #Add Calculator widget
        self.layOpportunity=QHBoxLayout()
        self.spacerOpportunity=QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.cmdOpportunity=QPushButton(self.tr("Add Opportunity"))
        self.cmdOpportunity.released.connect(self.on_cmdOpportunity_released)
        icon1 = QIcon()
        icon1.addPixmap(QPixmap(":/xulpymoney/kcalc.png"), QIcon.Normal, QIcon.Off)
        self.cmdOpportunity.setIcon(icon1)
        self.layOpportunity.addItem(self.spacerOpportunity)
        self.layOpportunity.addWidget(self.cmdOpportunity)
        
        
        
    ## Must be added after setProduct
    def setPrice(self, price):
        self.txtBuyPrice.setText(price)
        
    def on_cmdBuyPrice_released(self):
        if self.txtBuyPrice.isValid():
            self.generate()
            self.display()
    
    ## This button allows to open order Opportunity with the first purchase price
    def on_cmdOpportunity_released(self):
        d=QDialog(self)     
        d.setModal(True)
        d.setWindowTitle(self.tr("Add new opportunity"))
        w=wdgOpportunitiesAdd(self.mem, None, d)
        w.productSelector.setSelected(self.product)
        w.txtPrice.setText(self.txtBuyPrice.decimal())
        lay = QVBoxLayout(d)
        lay.addWidget(w)
        d.exec_()    

    def __qcolor_by_reinvestment_line(self, reinvestment_line):
        if reinvestment_line==ReinvestmentLines.Buy:
            return QColor(85, 170, 127)
        elif reinvestment_line==ReinvestmentLines.Average:
            return QColor(85, 85, 170)
        elif reinvestment_line==ReinvestmentLines.Sell:
            return QColor(170, 85, 85)
            
    def __qpen_by_amounts_index(self, index, reinvestment_line):
        if index==0:
            return self._pen(Qt.SolidLine, self.__qcolor_by_reinvestment_line(reinvestment_line))
        elif index==1:
            return self._pen(Qt.DashLine, self.__qcolor_by_reinvestment_line(reinvestment_line))
        elif index==2:
            return self._pen(Qt.DotLine, self.__qcolor_by_reinvestment_line(reinvestment_line))
        else:
            return self._pen(Qt.DotLine, self.__qcolor_by_reinvestment_line(reinvestment_line))

    ## Just draw the chart with selected options. It creates and destroys objects
    def generate(self):
        self.amounts=string2list_of_integers(self.txtAmounts.text(), ";")
        logging.debug(self.amounts)
        wdgProductHistoricalChart.generate(self)
        
        percentage=Percentage(self.spnGainsPercentage.value(), 100)
        selected_datetime= day_start_from_date(self.dtFrom.date().toPyDate(), self.mem.localzone)

        inv=Investment(self.mem).init__create("Buy Chart", None, None, self.product, None, True, -1)
        inv.op=InvestmentOperationHomogeneusManager(self.mem, inv)
        p_last_operation=Percentage(self.txtLastOperationPercentage.decimal(), 100)

        m_purchase=Money(self.mem, self.txtBuyPrice.decimal(), self.product.currency)
        #index=0 purchase, 1 = first reinvestment
        lastIO=None
        for index, amount in enumerate(self.amounts):
            lastIO=InvestmentOperation(self.mem).init__create  (   self.mem.tiposoperaciones.find_by_id(4), 
                                                                                            self.mem.localzone.now(), 
                                                                                            inv, 
                                                                                            int(self.amounts[index]/m_purchase.amount), 
                                                                                            0, 
                                                                                            0, 
                                                                                            m_purchase.amount, 
                                                                                            "",  
                                                                                            True, 
                                                                                            1,  
                                                                                            -10000
                                                                                        )
            inv.op.append(lastIO)
            (inv.op_actual, inv.op_historica)=inv.op.get_current_and_historical_operations()
            new_purchase_price=self.view.appendTemporalSeries(self.tr("Purchase price {}: {}").format(index, m_purchase.string()),  self.product.currency)
            new_purchase_price.setColor(self.__qcolor_by_reinvestment_line(ReinvestmentLines.Buy))
            new_purchase_price.setPen(self.__qpen_by_amounts_index(index, ReinvestmentLines.Buy))
            self.view.appendTemporalSeriesData(new_purchase_price, selected_datetime, m_purchase.amount)
            self.view.appendTemporalSeriesData(new_purchase_price, self.mem.localzone.now(), m_purchase.amount)
        
            m_new_average_price=inv.op_actual.average_price()
            m_new_selling_price=inv.op_actual.average_price_after_a_gains_percentage(percentage)
            new_average_price=self.view.appendTemporalSeries(self.tr("Average price {}: {}".format(index, m_new_average_price)),  self.product.currency)
            new_average_price.setColor(self.__qcolor_by_reinvestment_line(ReinvestmentLines.Average))
            new_average_price.setPen(self.__qpen_by_amounts_index(index, ReinvestmentLines.Average))
            self.view.appendTemporalSeriesData(new_average_price, selected_datetime, m_new_average_price.amount)
            self.view.appendTemporalSeriesData(new_average_price, self.mem.localzone.now(), m_new_average_price.amount)

            new_selling_price=self.view.appendTemporalSeries(self.tr("Sell price {} at {} to gain {}".format(index, m_new_selling_price, inv.op_actual.gains_from_percentage(percentage))),  self.product.currency)
            new_selling_price.setColor(self.__qcolor_by_reinvestment_line(ReinvestmentLines.Sell))
            new_selling_price.setPen(self.__qpen_by_amounts_index(index, ReinvestmentLines.Sell))
            self.view.appendTemporalSeriesData(new_selling_price, selected_datetime, m_new_selling_price.amount)
            self.view.appendTemporalSeriesData(new_selling_price, self.mem.localzone.now(),m_new_selling_price.amount)

            m_purchase=Money(self.mem, lastIO.valor_accion*(1-p_last_operation.value),  self.product.currency)


class wdgProductHistoricalOpportunity(wdgProductHistoricalChart):
    def __init__(self,  parent=None):
        wdgProductHistoricalChart.__init__(self, parent)
    
    def setOpportunity(self,  opportunity):
        self.opportunity=opportunity
        
    def generate(self):
        wdgProductHistoricalChart.generate(self)
        if not hasattr(self, 'opportunity'):
            logging.debug(self.tr("You need to use wdgProductHistoricalOpportunity.setOpportunity before wdgProductHistoricalOpportunity.generate"))
            return
            
        if self.opportunity.entry!=None:
            entry=self.view.appendTemporalSeries(self.tr("Entry"),  self.product.currency)
            entry.setColor(QColor(85, 85, 170))
            entry.setPen(self._pen(Qt.DashLine, QColor(85, 85, 170)))
            self.view.appendTemporalSeriesData(entry, day_start_from_date(self.dtFrom.date().toPyDate(), self.mem.localzone)-datetime.timedelta(days=10), self.opportunity.entry)
            self.view.appendTemporalSeriesData(entry, self.mem.localzone.now()+datetime.timedelta(days=10), self.opportunity.entry)

        if self.opportunity.target!=None:
            target=self.view.appendTemporalSeries(self.tr("Target"),  self.product.currency)
            target.setColor(QColor(85, 170, 85))
            target.setPen(self._pen(Qt.DashLine, QColor(85, 170, 85)))
            self.view.appendTemporalSeriesData(target, day_start_from_date(self.dtFrom.date().toPyDate(), self.mem.localzone)-datetime.timedelta(days=10), self.opportunity.target)
            self.view.appendTemporalSeriesData(target, self.mem.localzone.now()+datetime.timedelta(days=10), self.opportunity.target)

        if self.opportunity.stoploss!=None:
            stoploss=self.view.appendTemporalSeries(self.tr("Stop loss"),  self.product.currency)
            stoploss.setColor(QColor(170, 85, 85))
            stoploss.setPen(self._pen(Qt.DashLine, QColor(170, 85, 85)))
            self.view.appendTemporalSeriesData(stoploss, day_start_from_date(self.dtFrom.date().toPyDate(), self.mem.localzone)-datetime.timedelta(days=10), self.opportunity.stoploss)
            self.view.appendTemporalSeriesData(stoploss, self.mem.localzone.now()+datetime.timedelta(days=10), self.opportunity.stoploss)

                
