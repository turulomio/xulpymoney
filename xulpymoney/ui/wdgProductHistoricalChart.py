## @namespace xulpymoney.ui.wdgProductHistoricalChart
## @brief Several product historical chart widgets

from PyQt5.QtCore import pyqtSlot, Qt,  QDate
from PyQt5.QtGui import QColor,  QPen,  QIcon, QPixmap,  QWheelEvent
from PyQt5.QtWidgets import QWidget,  QHBoxLayout, QLabel,  QToolButton,  QSpacerItem,  QSizePolicy,  QPushButton, QVBoxLayout, QDialog, QLineEdit
from xulpymoney.ui.Ui_wdgProductHistoricalChart import Ui_wdgProductHistoricalChart

import datetime
import logging
from xulpymoney.datetime_functions import dtaware_day_start_from_date, dt_day_start
from xulpymoney.ui.myqlineedit import myQLineEdit
from xulpymoney.objects.investment import Investment
from xulpymoney.objects.investmentoperation import InvestmentOperation, InvestmentOperationHomogeneusManager
from xulpymoney.objects.money import Money
from xulpymoney.objects.percentage import Percentage
from xulpymoney.casts import string2list_of_integers
from xulpymoney.libxulpymoneytypes import eHistoricalChartAdjusts, eOperationType, eOHCLDuration
from xulpymoney.ui.wdgOpportunitiesAdd import wdgOpportunitiesAdd

## Main class that sets a product (can add an investment too) with setProduct function
##
## OHCL set is updated each time generate function is called
class wdgProductHistoricalChart(QWidget, Ui_wdgProductHistoricalChart):
    def __init__(self,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.dtFrom.blockSignals(True)
        self.HistoricalChartAdjusts=eHistoricalChartAdjusts.Splits
        
    def _pen(self, style, color):
        pen=QPen()
        pen.setStyle(style)
        pen.setColor(color)
        return pen


    def setOHCLDuration(self, ohclduration):
        self.__ohclduration=ohclduration
        
        
    ## @param list_decimals List of Decimlas with the range value where a line must be drawn
    def setDrawRangeLines(self, list_decimals):
        self._drawRangeLines=list_decimals

    def setProduct(self, product, investment=None):
        self.product=product
        self.investment=investment
        self.mem=self.product.mem
        self.wdgTS.setSettings(self.mem.settings, "wdgProductHistoricalChart", "wdgTS")
        from_=datetime.datetime.today()-datetime.timedelta(days=365*3)
        if self.investment!=None:
            if self.investment.op_actual.length()>0:
                from_=self.investment.op_actual.first().datetime-datetime.timedelta(days=30)
            elif self.investment.op.length()>0:
                from_=self.investment.op.first().datetime-datetime.timedelta(days=30)
        self.dtFrom.setDate(from_)
        self.dtFrom.blockSignals(False)

        if self.__class__.__name__=="wdgProductHistoricalChart" and self.investment is not None and self.investment.venta is not None and self.investment.venta!=0:
            m_average_price=self.investment.op_actual.average_price(type=1)       
            gains_percentage=Percentage(self.investment.selling_price().amount-m_average_price.amount, m_average_price.amount)
            self.spnGainsPercentage.blockSignals(True)
            self.spnGainsPercentage.setValue(gains_percentage.value_100())
            self.spnGainsPercentage.blockSignals(False)
        else:
            self.spnGainsPercentage.blockSignals(True)
            self.spnGainsPercentage.setValue(self.mem.settingsdb.value_float("frmSellingPoint/lastgainpercentage",  "5"))
            self.spnGainsPercentage.blockSignals(False)
        
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

    @pyqtSlot(float) 
    def on_spnGainsPercentage_valueChanged(self, value):
        self.generate()
        self.display()

    ## Just draw the chart with selected options. It creates and destroys objects
    ##
    ## self.setohcl is set calling this function
    def generate(self):
        selected_datetime= dtaware_day_start_from_date(self.dtFrom.date().toPyDate(), self.mem.localzone_name)
        self.setohcl=self.product.result.ohcl(self.cmbOHCLDuration.itemData(self.cmbOHCLDuration.currentIndex()), eHistoricalChartAdjusts.Splits)
        
        self.wdgTS.ts.clear()
        if self.cmbChartType.currentIndex()==0:#Lines
            ls=self.wdgTS.ts.appendTemporalSeries(self.product.name.upper())#Line seies
            for ohcl in self.setohcl.arr:
                if ohcl.datetime()>=selected_datetime:
                    self.wdgTS.ts.appendTemporalSeriesData(ls, ohcl.datetime(), ohcl.close) #Added day_start to show the purchase circle the first day
        elif self.cmbChartType.currentIndex()==1:#Candles            
            candle=self.wdgTS.ts.appendCandlestickSeries(self.product.name)#Candle series
            for ohcl in self.setohcl.arr:
                if ohcl.datetime()>=selected_datetime:
                    self.wdgTS.ts.appendCandlestickSeriesData(candle, ohcl.datetime(), ohcl.open, ohcl.high, ohcl.close, ohcl.low)
            
            
        dvm=self.setohcl.DatetimeValueManager("close")
            
        if self.chkSMA10.isChecked() and self.setohcl.length()>10:#SMA10 line series
            sma10=self.wdgTS.ts.appendTemporalSeries(self.tr("SMA10"))
            sma10.setColor(QColor(255, 165, 165))
            for dv in dvm.sma(10).arr:
                if dv.datetime>=selected_datetime:
                    self.wdgTS.ts.appendTemporalSeriesData(sma10, dv.datetime, dv.value)

        if self.chkSMA50.isChecked() and self.setohcl.length()>50:#SMA50 line series
            sma50=self.wdgTS.ts.appendTemporalSeries(self.tr("SMA50"))
            sma50.setColor(QColor(255, 170, 255))
            for dv in dvm.sma(50).arr:
                if dv.datetime>=selected_datetime:
                    self.wdgTS.ts.appendTemporalSeriesData(sma50, dv.datetime, dv.value)
                
        if self.chkSMA200.isChecked() and self.setohcl.length()>200:#SMA200 line series
            sma200=self.wdgTS.ts.appendTemporalSeries(self.tr("SMA200"))
            sma200.setColor(QColor(165, 165, 165))
            for dv in dvm.sma(200).arr:
                if dv.datetime>=selected_datetime:
                    self.wdgTS.ts.appendTemporalSeriesData(sma200, dv.datetime, dv.value)

        if self.chkMedian.isChecked():#Median value
            median=self.setohcl.closes_median_value()
            med=self.wdgTS.ts.appendTemporalSeries(self.tr("Median at {}".format(self.product.money(median))))
            med.setColor(QColor(165, 165, 0))
            self.wdgTS.ts.appendTemporalSeriesData(med, selected_datetime, median)
            self.wdgTS.ts.appendTemporalSeriesData(med, self.mem.localzone.now(), median)

        if not self.chkAdjustSplits.isChecked():#
            ls=self.wdgTS.ts.appendTemporalSeries(self.product.name.upper() + " (No adjust)")#Line seies
            for ohcl in self.product.result.ohcl(self.cmbOHCLDuration.itemData(self.cmbOHCLDuration.currentIndex()), eHistoricalChartAdjusts.NoAdjusts).arr:
                if ohcl.datetime()>=selected_datetime:
                    self.wdgTS.ts.appendTemporalSeriesData(ls, dt_day_start(ohcl.datetime()), ohcl.close) 

        if self.chkAdjustDividends.isChecked():#
            ls=self.wdgTS.ts.appendTemporalSeries(self.product.name.upper() + (" (Dividend adjust)"))#Line seies
            for ohcl in self.product.result.ohcl(self.cmbOHCLDuration.itemData(self.cmbOHCLDuration.currentIndex()), eHistoricalChartAdjusts.SplitsAndDividends).arr:
                if ohcl.datetime()>=selected_datetime:
                    self.wdgTS.ts.appendTemporalSeriesData(ls, dt_day_start(ohcl.datetime()), ohcl.close) 

        #INVESTMENT
        if self.investment is not None:
            #Buy sell operations
            buy=self.wdgTS.ts.appendScatterSeries(self.tr("Buy operations"))
            buy.setColor(QColor(85, 170, 127))
            sell=self.wdgTS.ts.appendScatterSeries(self.tr("Sell operations"))
            sell.setColor(QColor(170, 85, 85))
            for op in self.investment.op.arr:
                if (    op.tipooperacion.id in (eOperationType.SharesAdd, eOperationType.SharesPurchase, eOperationType.TransferSharesDestiny ) or 
                        (op.tipooperacion.id==eOperationType.TransferFunds and op.shares>0)
                    ) and op.datetime>=selected_datetime:
                    self.wdgTS.ts.appendScatterSeriesData(buy, op.datetime, op.valor_accion)
                if (    op.tipooperacion.id in (eOperationType.TransferSharesOrigin, eOperationType.SharesSale) or 
                        (op.tipooperacion.id==eOperationType.TransferFunds and op.shares<0)
                    ) and op.datetime>=selected_datetime:
                    self.wdgTS.ts.appendScatterSeriesData(sell, op.datetime, op.valor_accion)

            #Average price
            if self.investment.op_actual.length()>0:
                gains_percentage=Percentage(self.spnGainsPercentage.value(), 100)
                m_average_price=self.investment.op_actual.average_price(type=1)                
                m_selling_price=self.investment.op_actual.average_price_after_a_gains_percentage(gains_percentage)

                selling_price=self.wdgTS.ts.appendTemporalSeries(self.tr("Selling price at {} to gain {}".format(m_selling_price,  self.investment.op_actual.gains_from_percentage(gains_percentage))))
                selling_price.setColor(QColor(170, 85, 85))
                self.wdgTS.ts.appendTemporalSeriesData(selling_price, self.investment.op_actual.first().datetime, m_selling_price.amount)
                self.wdgTS.ts.appendTemporalSeriesData(selling_price, self.mem.localzone.now()+datetime.timedelta(days=1), m_selling_price.amount)

                average_price=self.wdgTS.ts.appendTemporalSeries(self.tr("Average price at {}".format(m_average_price)))
                average_price.setColor(QColor(85, 85, 170))
                self.wdgTS.ts.appendTemporalSeriesData(average_price, self.investment.op_actual.first().datetime, m_average_price.amount)
                self.wdgTS.ts.appendTemporalSeriesData(average_price, self.mem.localzone.now() + datetime.timedelta(days=1), m_average_price.amount)

        if hasattr(self,  "_drawRangeLines") is True: #Draws range linbes
            for range in self._drawRangeLines:
                range=round(range, self.product.decimals)
                m_range=self.product.money(range)
                tsrange=self.wdgTS.ts.appendTemporalSeries(self.tr("Range at {}".format(m_range)))
                tsrange.setColor(QColor(95, 154, 12))
                self.wdgTS.ts.appendTemporalSeriesData(tsrange, selected_datetime, range)
                self.wdgTS.ts.appendTemporalSeriesData(tsrange, self.mem.localzone.now(), range)

    def display(self):
        self.wdgTS.display()

    @pyqtSlot(int)      
    def on_cmbChartType_currentIndexChanged(self, index):
        self.generate()
        self.display()

    @pyqtSlot(int)      
    def on_cmbOHCLDuration_currentIndexChanged(self, index):
        self.generate()
        self.display()
        
    def on_cmdFromRight_released(self):
        self.dtFrom.setDate(dtaware_day_start_from_date(self.dtFrom.date().toPyDate(), self.mem.localzone_name)+datetime.timedelta(days=365))
        self.generate()
        self.display()        
        
    def on_cmdFromLeft_released(self):
        self.dtFrom.setDate(dtaware_day_start_from_date(self.dtFrom.date().toPyDate(), self.mem.localzone_name)-datetime.timedelta(days=365))
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
        
    def on_chkSMA10_stateChanged(self, state):
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
        self.spnGainsPercentage.valueChanged.connect(self.on_spnGainsPercentage_valueChanged)
        

    def generate(self):            
        wdgProductHistoricalChart.generate(self)
        
        if self.investment.op_actual.length()>0:
            #Calcs
            percentage=Percentage(self.spnGainsPercentage.value(), 100)
            new_avg_1=self.sim_opactual.average_price()
            new_sell_price_1=self.sim_opactual.average_price_after_a_gains_percentage(percentage)                
            new_purchase_price_1=self.sim_opactual.last().price()
            gains_1=self.sim_opactual.gains_from_percentage(percentage)
            
            #First reinvestment
            new_selling_price=self.wdgTS.ts.appendTemporalSeries(self.tr("Reinvestment selling price at {} to gain {}".format(new_sell_price_1, gains_1)))
            new_selling_price.setColor(QColor(170, 85, 85))
            new_selling_price.setPen(self._pen(Qt.DashLine, QColor(170, 85, 85)))
            self.wdgTS.ts.appendTemporalSeriesData(new_selling_price, self.investment.op_actual.first().datetime, new_sell_price_1.amount)
            self.wdgTS.ts.appendTemporalSeriesData(new_selling_price, self.mem.localzone.now(), new_sell_price_1.amount)
            
            new_average_price=self.wdgTS.ts.appendTemporalSeries(self.tr("Reinvestment average price at {}").format(new_avg_1))
            new_average_price.setColor(QColor(85, 85, 170))
            new_average_price.setPen(self._pen(Qt.DashLine, QColor(85, 85, 170)))
            self.wdgTS.ts.appendTemporalSeriesData(new_average_price, self.investment.op_actual.first().datetime, new_avg_1.amount)
            self.wdgTS.ts.appendTemporalSeriesData(new_average_price, self.mem.localzone.now(), new_avg_1.amount)
            
            new_purchase_price=self.wdgTS.ts.appendTemporalSeries(self.tr("Reinvestment purchase at {}").format(new_purchase_price_1))
            new_purchase_price.setColor(QColor(85, 170, 127))
            new_purchase_price.setPen(self._pen(Qt.DashLine, QColor(85, 170, 127)))
            self.wdgTS.ts.appendTemporalSeriesData(new_purchase_price, self.sim_opactual.first().datetime, new_purchase_price_1.amount)
            self.wdgTS.ts.appendTemporalSeriesData(new_purchase_price, self.mem.localzone.now(), new_purchase_price_1.amount) 


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
        selected_datetime= dtaware_day_start_from_date(self.dtFrom.date().toPyDate(), self.mem.localzone_name)

        inv=Investment(self.mem).init__create("Buy Chart", None, None, self.product, None, True, False -1)
        inv.op=InvestmentOperationHomogeneusManager(self.mem, inv)
        p_last_operation=Percentage(self.txtLastOperationPercentage.decimal(), 100)

        m_purchase=Money(self.mem, self.txtBuyPrice.decimal(), self.product.currency)
        #index=0 purchase, 1 = first reinvestment
        lastIO=None
        for index, amount in enumerate(self.amounts):
            lastIO=InvestmentOperation(self.mem, 
                                                            self.mem.tiposoperaciones.find_by_id(4), 
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
            new_purchase_price=self.wdgTS.ts.appendTemporalSeries(self.tr("Purchase price {}: {}").format(index, m_purchase.string()))
            new_purchase_price.setColor(self.__qcolor_by_reinvestment_line(ReinvestmentLines.Buy))
            new_purchase_price.setPen(self.__qpen_by_amounts_index(index, ReinvestmentLines.Buy))
            self.wdgTS.ts.appendTemporalSeriesData(new_purchase_price, selected_datetime, m_purchase.amount)
            self.wdgTS.ts.appendTemporalSeriesData(new_purchase_price, self.mem.localzone.now(), m_purchase.amount)
        
            m_new_average_price=inv.op_actual.average_price()
            m_new_selling_price=inv.op_actual.average_price_after_a_gains_percentage(percentage)
            new_average_price=self.wdgTS.ts.appendTemporalSeries(self.tr("Average price {}: {}".format(index, m_new_average_price)))
            new_average_price.setColor(self.__qcolor_by_reinvestment_line(ReinvestmentLines.Average))
            new_average_price.setPen(self.__qpen_by_amounts_index(index, ReinvestmentLines.Average))
            self.wdgTS.ts.appendTemporalSeriesData(new_average_price, selected_datetime, m_new_average_price.amount)
            self.wdgTS.ts.appendTemporalSeriesData(new_average_price, self.mem.localzone.now(), m_new_average_price.amount)

            new_selling_price=self.wdgTS.ts.appendTemporalSeries(self.tr("Sell price {} at {} to gain {}".format(index, m_new_selling_price, inv.op_actual.gains_from_percentage(percentage))))
            new_selling_price.setColor(self.__qcolor_by_reinvestment_line(ReinvestmentLines.Sell))
            new_selling_price.setPen(self.__qpen_by_amounts_index(index, ReinvestmentLines.Sell))
            self.wdgTS.ts.appendTemporalSeriesData(new_selling_price, selected_datetime, m_new_selling_price.amount)
            self.wdgTS.ts.appendTemporalSeriesData(new_selling_price, self.mem.localzone.now(),m_new_selling_price.amount)

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
            entry=self.wdgTS.ts.appendTemporalSeries(self.tr("Entry"))
            entry.setColor(QColor(85, 85, 170))
            entry.setPen(self._pen(Qt.DashLine, QColor(85, 85, 170)))
            self.wdgTS.ts.appendTemporalSeriesData(entry, dtaware_day_start_from_date(self.dtFrom.date().toPyDate(), self.mem.localzone_name)-datetime.timedelta(days=10), self.opportunity.entry)
            self.wdgTS.ts.appendTemporalSeriesData(entry, self.mem.localzone.now()+datetime.timedelta(days=10), self.opportunity.entry)

        if self.opportunity.target!=None:
            target=self.wdgTS.ts.appendTemporalSeries(self.tr("Target"))
            target.setColor(QColor(85, 170, 85))
            target.setPen(self._pen(Qt.DashLine, QColor(85, 170, 85)))
            self.wdgTS.ts.appendTemporalSeriesData(target, dtaware_day_start_from_date(self.dtFrom.date().toPyDate(), self.mem.localzone_name)-datetime.timedelta(days=10), self.opportunity.target)
            self.wdgTS.ts.appendTemporalSeriesData(target, self.mem.localzone.now()+datetime.timedelta(days=10), self.opportunity.target)

        if self.opportunity.stoploss!=None:
            stoploss=self.wdgTS.ts.appendTemporalSeries(self.tr("Stop loss"))
            stoploss.setColor(QColor(170, 85, 85))
            stoploss.setPen(self._pen(Qt.DashLine, QColor(170, 85, 85)))
            self.wdgTS.ts.appendTemporalSeriesData(stoploss, dtaware_day_start_from_date(self.dtFrom.date().toPyDate(), self.mem.localzone_name)-datetime.timedelta(days=10), self.opportunity.stoploss)
            self.wdgTS.ts.appendTemporalSeriesData(stoploss, self.mem.localzone.now()+datetime.timedelta(days=10), self.opportunity.stoploss)

                
