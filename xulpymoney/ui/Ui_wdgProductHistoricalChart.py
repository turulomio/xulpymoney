# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/wdgProductHistoricalChart.ui'
#
# Created by: PyQt5 UI code generator 5.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_wdgProductHistoricalChart(object):
    def setupUi(self, wdgProductHistoricalChart):
        wdgProductHistoricalChart.setObjectName("wdgProductHistoricalChart")
        wdgProductHistoricalChart.resize(1014, 615)
        self.verticalLayout = QtWidgets.QVBoxLayout(wdgProductHistoricalChart)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtWidgets.QLabel(wdgProductHistoricalChart)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.cmbChartType = QtWidgets.QComboBox(wdgProductHistoricalChart)
        self.cmbChartType.setObjectName("cmbChartType")
        self.cmbChartType.addItem("")
        self.cmbChartType.addItem("")
        self.horizontalLayout_2.addWidget(self.cmbChartType)
        self.horizontalLayout_3.addLayout(self.horizontalLayout_2)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_3 = QtWidgets.QLabel(wdgProductHistoricalChart)
        self.label_3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_4.addWidget(self.label_3)
        self.cmbOHCLDuration = QtWidgets.QComboBox(wdgProductHistoricalChart)
        self.cmbOHCLDuration.setObjectName("cmbOHCLDuration")
        self.horizontalLayout_4.addWidget(self.cmbOHCLDuration)
        self.horizontalLayout_3.addLayout(self.horizontalLayout_4)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(wdgProductHistoricalChart)
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.cmdFromLeftMax = QtWidgets.QToolButton(wdgProductHistoricalChart)
        self.cmdFromLeftMax.setObjectName("cmdFromLeftMax")
        self.horizontalLayout.addWidget(self.cmdFromLeftMax)
        self.cmdFromLeft = QtWidgets.QToolButton(wdgProductHistoricalChart)
        self.cmdFromLeft.setObjectName("cmdFromLeft")
        self.horizontalLayout.addWidget(self.cmdFromLeft)
        self.dtFrom = QtWidgets.QDateEdit(wdgProductHistoricalChart)
        self.dtFrom.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.dtFrom.setCalendarPopup(True)
        self.dtFrom.setObjectName("dtFrom")
        self.horizontalLayout.addWidget(self.dtFrom)
        self.cmdFromRight = QtWidgets.QToolButton(wdgProductHistoricalChart)
        self.cmdFromRight.setObjectName("cmdFromRight")
        self.horizontalLayout.addWidget(self.cmdFromRight)
        self.cmdFromRightMax = QtWidgets.QToolButton(wdgProductHistoricalChart)
        self.cmdFromRightMax.setObjectName("cmdFromRightMax")
        self.horizontalLayout.addWidget(self.cmdFromRightMax)
        self.horizontalLayout_3.addLayout(self.horizontalLayout)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem3)
        self.chkSMA50 = QtWidgets.QCheckBox(wdgProductHistoricalChart)
        self.chkSMA50.setChecked(True)
        self.chkSMA50.setObjectName("chkSMA50")
        self.horizontalLayout_3.addWidget(self.chkSMA50)
        self.chkSMA200 = QtWidgets.QCheckBox(wdgProductHistoricalChart)
        self.chkSMA200.setChecked(True)
        self.chkSMA200.setObjectName("chkSMA200")
        self.horizontalLayout_3.addWidget(self.chkSMA200)
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem4)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.actionProductReport = QtWidgets.QAction(wdgProductHistoricalChart)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/xulpymoney/books.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionProductReport.setIcon(icon)
        self.actionProductReport.setObjectName("actionProductReport")
        self.actionSortTPCDiario = QtWidgets.QAction(wdgProductHistoricalChart)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/images/document-preview.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSortTPCDiario.setIcon(icon1)
        self.actionSortTPCDiario.setObjectName("actionSortTPCDiario")
        self.actionSortTPCAnual = QtWidgets.QAction(wdgProductHistoricalChart)
        self.actionSortTPCAnual.setIcon(icon1)
        self.actionSortTPCAnual.setObjectName("actionSortTPCAnual")
        self.actionSortName = QtWidgets.QAction(wdgProductHistoricalChart)
        self.actionSortName.setIcon(icon1)
        self.actionSortName.setObjectName("actionSortName")
        self.actionSortDividend = QtWidgets.QAction(wdgProductHistoricalChart)
        self.actionSortDividend.setIcon(icon1)
        self.actionSortDividend.setObjectName("actionSortDividend")
        self.actionSortHour = QtWidgets.QAction(wdgProductHistoricalChart)
        self.actionSortHour.setIcon(icon1)
        self.actionSortHour.setObjectName("actionSortHour")
        self.actionIbex35 = QtWidgets.QAction(wdgProductHistoricalChart)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/countries/spain.gif"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionIbex35.setIcon(icon2)
        self.actionIbex35.setObjectName("actionIbex35")
        self.actionProductNew = QtWidgets.QAction(wdgProductHistoricalChart)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/xulpymoney/add.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionProductNew.setIcon(icon3)
        self.actionProductNew.setObjectName("actionProductNew")
        self.actionProductDelete = QtWidgets.QAction(wdgProductHistoricalChart)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/xulpymoney/list-remove.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionProductDelete.setIcon(icon4)
        self.actionProductDelete.setObjectName("actionProductDelete")
        self.actionFavorites = QtWidgets.QAction(wdgProductHistoricalChart)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/xulpymoney/star.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionFavorites.setIcon(icon5)
        self.actionFavorites.setObjectName("actionFavorites")
        self.actionMergeCodes = QtWidgets.QAction(wdgProductHistoricalChart)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(":/images/cakes.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionMergeCodes.setIcon(icon6)
        self.actionMergeCodes.setObjectName("actionMergeCodes")
        self.actionQuoteNew = QtWidgets.QAction(wdgProductHistoricalChart)
        self.actionQuoteNew.setIcon(icon3)
        self.actionQuoteNew.setObjectName("actionQuoteNew")
        self.actionEstimationDPSNew = QtWidgets.QAction(wdgProductHistoricalChart)
        self.actionEstimationDPSNew.setIcon(icon3)
        self.actionEstimationDPSNew.setObjectName("actionEstimationDPSNew")
        self.actionPurge = QtWidgets.QAction(wdgProductHistoricalChart)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(":/xulpymoney/tools-wizard.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionPurge.setIcon(icon7)
        self.actionPurge.setObjectName("actionPurge")
        self.actionPurchaseGraphic = QtWidgets.QAction(wdgProductHistoricalChart)
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap(":/xulpymoney/report.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionPurchaseGraphic.setIcon(icon8)
        self.actionPurchaseGraphic.setObjectName("actionPurchaseGraphic")
        self.actionProductPriceLastRemove = QtWidgets.QAction(wdgProductHistoricalChart)
        self.actionProductPriceLastRemove.setIcon(icon4)
        self.actionProductPriceLastRemove.setObjectName("actionProductPriceLastRemove")

        self.retranslateUi(wdgProductHistoricalChart)
        self.cmbChartType.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(wdgProductHistoricalChart)

    def retranslateUi(self, wdgProductHistoricalChart):
        _translate = QtCore.QCoreApplication.translate
        self.label_2.setText(_translate("wdgProductHistoricalChart", "Chart type"))
        self.cmbChartType.setItemText(0, _translate("wdgProductHistoricalChart", "Lines"))
        self.cmbChartType.setItemText(1, _translate("wdgProductHistoricalChart", "Candles"))
        self.label_3.setText(_translate("wdgProductHistoricalChart", "Select time range"))
        self.label.setText(_translate("wdgProductHistoricalChart", "Show from selected date"))
        self.cmdFromLeftMax.setText(_translate("wdgProductHistoricalChart", "<<"))
        self.cmdFromLeft.setText(_translate("wdgProductHistoricalChart", "<"))
        self.dtFrom.setDisplayFormat(_translate("wdgProductHistoricalChart", "yyyy-MM-dd"))
        self.cmdFromRight.setText(_translate("wdgProductHistoricalChart", ">"))
        self.cmdFromRightMax.setText(_translate("wdgProductHistoricalChart", ">>"))
        self.chkSMA50.setText(_translate("wdgProductHistoricalChart", "SMA50"))
        self.chkSMA200.setText(_translate("wdgProductHistoricalChart", "SMA200"))
        self.actionProductReport.setText(_translate("wdgProductHistoricalChart", "Product report"))
        self.actionProductReport.setToolTip(_translate("wdgProductHistoricalChart", "Product report"))
        self.actionSortTPCDiario.setText(_translate("wdgProductHistoricalChart", "% Daily"))
        self.actionSortTPCDiario.setToolTip(_translate("wdgProductHistoricalChart", "% Daily"))
        self.actionSortTPCAnual.setText(_translate("wdgProductHistoricalChart", "% Annual"))
        self.actionSortTPCAnual.setToolTip(_translate("wdgProductHistoricalChart", "% Annual"))
        self.actionSortName.setText(_translate("wdgProductHistoricalChart", "Name"))
        self.actionSortName.setToolTip(_translate("wdgProductHistoricalChart", "Name"))
        self.actionSortDividend.setText(_translate("wdgProductHistoricalChart", "Dividend"))
        self.actionSortDividend.setToolTip(_translate("wdgProductHistoricalChart", "Dividend"))
        self.actionSortHour.setText(_translate("wdgProductHistoricalChart", "Hour"))
        self.actionSortHour.setToolTip(_translate("wdgProductHistoricalChart", "Hour"))
        self.actionIbex35.setText(_translate("wdgProductHistoricalChart", "Ibex 35"))
        self.actionProductNew.setText(_translate("wdgProductHistoricalChart", "New product"))
        self.actionProductNew.setToolTip(_translate("wdgProductHistoricalChart", "New user product"))
        self.actionProductDelete.setText(_translate("wdgProductHistoricalChart", "Delete product"))
        self.actionProductDelete.setToolTip(_translate("wdgProductHistoricalChart", "Delete user product"))
        self.actionFavorites.setText(_translate("wdgProductHistoricalChart", "Add to favorites"))
        self.actionFavorites.setToolTip(_translate("wdgProductHistoricalChart", "Add to favorites"))
        self.actionMergeCodes.setText(_translate("wdgProductHistoricalChart", "Merge selected codes"))
        self.actionMergeCodes.setToolTip(_translate("wdgProductHistoricalChart", "Merge selected codes"))
        self.actionQuoteNew.setText(_translate("wdgProductHistoricalChart", "New price"))
        self.actionQuoteNew.setToolTip(_translate("wdgProductHistoricalChart", "New price"))
        self.actionEstimationDPSNew.setText(_translate("wdgProductHistoricalChart", "New DPS estimation"))
        self.actionEstimationDPSNew.setToolTip(_translate("wdgProductHistoricalChart", "New Dividend per share estimation"))
        self.actionPurge.setText(_translate("wdgProductHistoricalChart", "Purge investment"))
        self.actionPurge.setToolTip(_translate("wdgProductHistoricalChart", "Deletes quotes innecesary. Leaves open, high, low and close quotes."))
        self.actionPurchaseGraphic.setText(_translate("wdgProductHistoricalChart", "Show purchase graphic"))
        self.actionPurchaseGraphic.setToolTip(_translate("wdgProductHistoricalChart", "Show purchase graphic"))
        self.actionProductPriceLastRemove.setText(_translate("wdgProductHistoricalChart", "Remove last product price"))
        self.actionProductPriceLastRemove.setToolTip(_translate("wdgProductHistoricalChart", "Remove last product price"))

import xulpymoney_rc
