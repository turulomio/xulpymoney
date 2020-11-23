# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'xulpymoney/ui/wdgTotal.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_wdgTotal(object):
    def setupUi(self, wdgTotal):
        wdgTotal.setObjectName("wdgTotal")
        wdgTotal.resize(1512, 815)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(wdgTotal)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.lblTitulo = QtWidgets.QLabel(wdgTotal)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.lblTitulo.setFont(font)
        self.lblTitulo.setAlignment(QtCore.Qt.AlignCenter)
        self.lblTitulo.setObjectName("lblTitulo")
        self.verticalLayout_2.addWidget(self.lblTitulo)
        self.tab = QtWidgets.QTabWidget(wdgTotal)
        self.tab.setTabsClosable(True)
        self.tab.setObjectName("tab")
        self.tabDatos = QtWidgets.QWidget()
        self.tabDatos.setObjectName("tabDatos")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.tabDatos)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout()
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.wyData = wdgYear(self.tabDatos)
        self.wyData.setObjectName("wyData")
        self.horizontalLayout.addWidget(self.wyData)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout_7.addLayout(self.horizontalLayout)
        self.tabData = QtWidgets.QTabWidget(self.tabDatos)
        self.tabData.setTabPosition(QtWidgets.QTabWidget.West)
        self.tabData.setObjectName("tabData")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout(self.tab_3)
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.lblPreviousYear = QtWidgets.QLabel(self.tab_3)
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)
        self.lblPreviousYear.setFont(font)
        self.lblPreviousYear.setAlignment(QtCore.Qt.AlignCenter)
        self.lblPreviousYear.setObjectName("lblPreviousYear")
        self.verticalLayout.addWidget(self.lblPreviousYear)
        self.mqtw = mqtw(self.tab_3)
        self.mqtw.setObjectName("mqtw")
        self.verticalLayout.addWidget(self.mqtw)
        self.lblInvested = QtWidgets.QLabel(self.tab_3)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.lblInvested.setFont(font)
        self.lblInvested.setText("")
        self.lblInvested.setAlignment(QtCore.Qt.AlignCenter)
        self.lblInvested.setObjectName("lblInvested")
        self.verticalLayout.addWidget(self.lblInvested)
        self.horizontalLayout_8.addLayout(self.verticalLayout)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/xulpymoney/coins.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.tabData.addTab(self.tab_3, icon, "")
        self.tab_4 = QtWidgets.QWidget()
        self.tab_4.setObjectName("tab_4")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.tab_4)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout()
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem2)
        self.lblTarget = QtWidgets.QLabel(self.tab_4)
        self.lblTarget.setObjectName("lblTarget")
        self.horizontalLayout_5.addWidget(self.lblTarget)
        self.spinTarget = QtWidgets.QDoubleSpinBox(self.tab_4)
        self.spinTarget.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.spinTarget.setObjectName("spinTarget")
        self.horizontalLayout_5.addWidget(self.spinTarget)
        self.cmdTargets = QtWidgets.QToolButton(self.tab_4)
        self.cmdTargets.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/xulpymoney/save.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.cmdTargets.setIcon(icon1)
        self.cmdTargets.setObjectName("cmdTargets")
        self.horizontalLayout_5.addWidget(self.cmdTargets)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem3)
        self.verticalLayout_8.addLayout(self.horizontalLayout_5)
        self.tabPlus = QtWidgets.QTabWidget(self.tab_4)
        self.tabPlus.setObjectName("tabPlus")
        self.tab_6 = QtWidgets.QWidget()
        self.tab_6.setObjectName("tab_6")
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout(self.tab_6)
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.mqtwTargets = mqtw(self.tab_6)
        self.mqtwTargets.setObjectName("mqtwTargets")
        self.verticalLayout_3.addWidget(self.mqtwTargets)
        self.lblTargets = QtWidgets.QLabel(self.tab_6)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.lblTargets.setFont(font)
        self.lblTargets.setAlignment(QtCore.Qt.AlignCenter)
        self.lblTargets.setObjectName("lblTargets")
        self.verticalLayout_3.addWidget(self.lblTargets)
        self.horizontalLayout_10.addLayout(self.verticalLayout_3)
        self.tabPlus.addTab(self.tab_6, "")
        self.tab_7 = QtWidgets.QWidget()
        self.tab_7.setObjectName("tab_7")
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout(self.tab_7)
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.verticalLayout_9 = QtWidgets.QVBoxLayout()
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.mqtwTargetsPlus = mqtw(self.tab_7)
        self.mqtwTargetsPlus.setObjectName("mqtwTargetsPlus")
        self.verticalLayout_9.addWidget(self.mqtwTargetsPlus)
        self.lblTargetsPlus = QtWidgets.QLabel(self.tab_7)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.lblTargetsPlus.setFont(font)
        self.lblTargetsPlus.setAlignment(QtCore.Qt.AlignCenter)
        self.lblTargetsPlus.setObjectName("lblTargetsPlus")
        self.verticalLayout_9.addWidget(self.lblTargetsPlus)
        self.horizontalLayout_11.addLayout(self.verticalLayout_9)
        self.tabPlus.addTab(self.tab_7, "")
        self.verticalLayout_8.addWidget(self.tabPlus)
        self.horizontalLayout_4.addLayout(self.verticalLayout_8)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/xulpymoney/gafas.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.tabData.addTab(self.tab_4, icon2, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout(self.tab_2)
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.mqtwInvestOrWork = mqtw(self.tab_2)
        self.mqtwInvestOrWork.setObjectName("mqtwInvestOrWork")
        self.verticalLayout_5.addWidget(self.mqtwInvestOrWork)
        self.lblInvestOrWork = QtWidgets.QLabel(self.tab_2)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.lblInvestOrWork.setFont(font)
        self.lblInvestOrWork.setText("")
        self.lblInvestOrWork.setAlignment(QtCore.Qt.AlignCenter)
        self.lblInvestOrWork.setObjectName("lblInvestOrWork")
        self.verticalLayout_5.addWidget(self.lblInvestOrWork)
        self.horizontalLayout_7.addLayout(self.verticalLayout_5)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/xulpymoney/tools-wizard.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.tabData.addTab(self.tab_2, icon3, "")
        self.tab_5 = QtWidgets.QWidget()
        self.tab_5.setObjectName("tab_5")
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout(self.tab_5)
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.mqtwMakeEndsMeet = mqtw(self.tab_5)
        self.mqtwMakeEndsMeet.setObjectName("mqtwMakeEndsMeet")
        self.verticalLayout_6.addWidget(self.mqtwMakeEndsMeet)
        self.lblMakeEndsMeet = QtWidgets.QLabel(self.tab_5)
        self.lblMakeEndsMeet.setText("")
        self.lblMakeEndsMeet.setObjectName("lblMakeEndsMeet")
        self.verticalLayout_6.addWidget(self.lblMakeEndsMeet)
        self.horizontalLayout_9.addLayout(self.verticalLayout_6)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/xulpymoney/books.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.tabData.addTab(self.tab_5, icon4, "")
        self.verticalLayout_7.addWidget(self.tabData)
        self.horizontalLayout_3.addLayout(self.verticalLayout_7)
        self.tab.addTab(self.tabDatos, icon, "")
        self.tabGraphic = QtWidgets.QWidget()
        self.tabGraphic.setObjectName("tabGraphic")
        self.horizontalLayout_12 = QtWidgets.QHBoxLayout(self.tabGraphic)
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        self.verticalLayout_11 = QtWidgets.QVBoxLayout()
        self.verticalLayout_11.setObjectName("verticalLayout_11")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem4)
        self.wyChart = wdgYear(self.tabGraphic)
        self.wyChart.setObjectName("wyChart")
        self.horizontalLayout_6.addWidget(self.wyChart)
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem5)
        self.verticalLayout_11.addLayout(self.horizontalLayout_6)
        self.tabWidget = QtWidgets.QTabWidget(self.tabGraphic)
        self.tabWidget.setTabPosition(QtWidgets.QTabWidget.West)
        self.tabWidget.setObjectName("tabWidget")
        self.tab_8 = QtWidgets.QWidget()
        self.tab_8.setObjectName("tab_8")
        self.horizontalLayout_13 = QtWidgets.QHBoxLayout(self.tab_8)
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.wdgTS = VCTemporalSeries(self.tab_8)
        self.wdgTS.setObjectName("wdgTS")
        self.verticalLayout_4.addWidget(self.wdgTS)
        self.horizontalLayout_13.addLayout(self.verticalLayout_4)
        self.tabWidget.addTab(self.tab_8, "")
        self.tab_9 = QtWidgets.QWidget()
        self.tab_9.setObjectName("tab_9")
        self.horizontalLayout_15 = QtWidgets.QHBoxLayout(self.tab_9)
        self.horizontalLayout_15.setObjectName("horizontalLayout_15")
        self.verticalLayout_10 = QtWidgets.QVBoxLayout()
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.wdgTSInvested = VCTemporalSeries(self.tab_9)
        self.wdgTSInvested.setObjectName("wdgTSInvested")
        self.verticalLayout_10.addWidget(self.wdgTSInvested)
        self.horizontalLayout_15.addLayout(self.verticalLayout_10)
        self.tabWidget.addTab(self.tab_9, "")
        self.verticalLayout_11.addWidget(self.tabWidget)
        self.horizontalLayout_12.addLayout(self.verticalLayout_11)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/xulpymoney/pie.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.tab.addTab(self.tabGraphic, icon5, "")
        self.verticalLayout_2.addWidget(self.tab)
        self.horizontalLayout_2.addLayout(self.verticalLayout_2)
        self.actionShowIncomes = QtWidgets.QAction(wdgTotal)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(":/xulpymoney/bundle.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionShowIncomes.setIcon(icon6)
        self.actionShowIncomes.setObjectName("actionShowIncomes")
        self.actionShowExpenses = QtWidgets.QAction(wdgTotal)
        self.actionShowExpenses.setObjectName("actionShowExpenses")
        self.actionShowDividends = QtWidgets.QAction(wdgTotal)
        self.actionShowDividends.setIcon(icon)
        self.actionShowDividends.setObjectName("actionShowDividends")
        self.actionShowSellingOperations = QtWidgets.QAction(wdgTotal)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(":/xulpymoney/dinero.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionShowSellingOperations.setIcon(icon7)
        self.actionShowSellingOperations.setObjectName("actionShowSellingOperations")
        self.actionShowComissions = QtWidgets.QAction(wdgTotal)
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap(":/xulpymoney/bank.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionShowComissions.setIcon(icon8)
        self.actionShowComissions.setObjectName("actionShowComissions")
        self.actionShowTaxes = QtWidgets.QAction(wdgTotal)
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap(":/xulpymoney/study.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionShowTaxes.setIcon(icon9)
        self.actionShowTaxes.setObjectName("actionShowTaxes")
        self.actionGainsByProductType = QtWidgets.QAction(wdgTotal)
        self.actionGainsByProductType.setIcon(icon)
        self.actionGainsByProductType.setObjectName("actionGainsByProductType")

        self.retranslateUi(wdgTotal)
        self.tab.setCurrentIndex(1)
        self.tabData.setCurrentIndex(0)
        self.tabPlus.setCurrentIndex(1)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(wdgTotal)

    def retranslateUi(self, wdgTotal):
        _translate = QtCore.QCoreApplication.translate
        self.lblTitulo.setText(_translate("wdgTotal", "Total report"))
        self.tabData.setTabText(self.tabData.indexOf(self.tab_3), _translate("wdgTotal", "Data in the year"))
        self.lblTarget.setText(_translate("wdgTotal", "Annual target percentage"))
        self.spinTarget.setSuffix(_translate("wdgTotal", " %"))
        self.tabPlus.setTabText(self.tabPlus.indexOf(self.tab_6), _translate("wdgTotal", "Consolidated Gains"))
        self.tabPlus.setTabText(self.tabPlus.indexOf(self.tab_7), _translate("wdgTotal", "Consolidated Gains + funds revaluation"))
        self.tabData.setTabText(self.tabData.indexOf(self.tab_4), _translate("wdgTotal", "Annual target return"))
        self.tabData.setTabText(self.tabData.indexOf(self.tab_2), _translate("wdgTotal", "Invest or work?"))
        self.tabData.setTabText(self.tabData.indexOf(self.tab_5), _translate("wdgTotal", "Make ends meet?"))
        self.tab.setTabText(self.tab.indexOf(self.tabDatos), _translate("wdgTotal", "Data"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_8), _translate("wdgTotal", "Assets"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_9), _translate("wdgTotal", "Invested assets"))
        self.tab.setTabText(self.tab.indexOf(self.tabGraphic), _translate("wdgTotal", "Chart"))
        self.actionShowIncomes.setText(_translate("wdgTotal", "Show income operations"))
        self.actionShowIncomes.setToolTip(_translate("wdgTotal", "Show income operations"))
        self.actionShowExpenses.setText(_translate("wdgTotal", "Show expense operations"))
        self.actionShowDividends.setText(_translate("wdgTotal", "Show dividends"))
        self.actionShowDividends.setToolTip(_translate("wdgTotal", "Show dividends"))
        self.actionShowSellingOperations.setText(_translate("wdgTotal", "Show selling operations"))
        self.actionShowSellingOperations.setToolTip(_translate("wdgTotal", "Show selling operations"))
        self.actionShowComissions.setText(_translate("wdgTotal", "Show Comissions"))
        self.actionShowComissions.setToolTip(_translate("wdgTotal", "Show Comissions"))
        self.actionShowTaxes.setText(_translate("wdgTotal", "Show taxes"))
        self.actionShowTaxes.setToolTip(_translate("wdgTotal", "Show taxes"))
        self.actionGainsByProductType.setText(_translate("wdgTotal", "Gains by product type"))
        self.actionGainsByProductType.setToolTip(_translate("wdgTotal", "Gains by product type"))
from xulpymoney.ui.myqcharts import VCTemporalSeries
from xulpymoney.ui.myqtablewidget import mqtw
from xulpymoney.ui.wdgYear import wdgYear
import xulpymoney.images.xulpymoney_rc
