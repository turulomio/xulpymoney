# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/wdgInvestmentClasses.ui'
#
# Created by: PyQt5 UI code generator 5.8.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_wdgInvestmentClasses(object):
    def setupUi(self, wdgInvestmentClasses):
        wdgInvestmentClasses.setObjectName("wdgInvestmentClasses")
        wdgInvestmentClasses.resize(1026, 487)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(wdgInvestmentClasses.sizePolicy().hasHeightForWidth())
        wdgInvestmentClasses.setSizePolicy(sizePolicy)
        self._2 = QtWidgets.QHBoxLayout(wdgInvestmentClasses)
        self._2.setObjectName("_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.lbl = QtWidgets.QLabel(wdgInvestmentClasses)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.lbl.setFont(font)
        self.lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl.setObjectName("lbl")
        self.verticalLayout.addWidget(self.lbl)
        self.groupBox = QtWidgets.QGroupBox(wdgInvestmentClasses)
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout(self.groupBox)
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.radCurrent = QtWidgets.QRadioButton(self.groupBox)
        self.radCurrent.setChecked(True)
        self.radCurrent.setObjectName("radCurrent")
        self.horizontalLayout_5.addWidget(self.radCurrent)
        self.radInvested = QtWidgets.QRadioButton(self.groupBox)
        self.radInvested.setObjectName("radInvested")
        self.horizontalLayout_5.addWidget(self.radInvested)
        self.horizontalLayout_8.addLayout(self.horizontalLayout_5)
        self.verticalLayout.addWidget(self.groupBox)
        self.tab = QtWidgets.QTabWidget(wdgInvestmentClasses)
        self.tab.setObjectName("tab")
        self.tabTPCVariable = QtWidgets.QWidget()
        self.tabTPCVariable.setObjectName("tabTPCVariable")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.tabTPCVariable)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.layTPC = QtWidgets.QHBoxLayout()
        self.layTPC.setObjectName("layTPC")
        self.horizontalLayout_2.addLayout(self.layTPC)
        self.tab.addTab(self.tabTPCVariable, "")
        self.tabPCI = QtWidgets.QWidget()
        self.tabPCI.setObjectName("tabPCI")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.tabPCI)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.layPCI = QtWidgets.QVBoxLayout()
        self.layPCI.setObjectName("layPCI")
        self.horizontalLayout.addLayout(self.layPCI)
        self.tab.addTab(self.tabPCI, "")
        self.tabTipo = QtWidgets.QWidget()
        self.tabTipo.setObjectName("tabTipo")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.tabTipo)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.layTipo = QtWidgets.QVBoxLayout()
        self.layTipo.setObjectName("layTipo")
        self.horizontalLayout_3.addLayout(self.layTipo)
        self.tab.addTab(self.tabTipo, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.tab_2)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.layApalancado = QtWidgets.QVBoxLayout()
        self.layApalancado.setObjectName("layApalancado")
        self.horizontalLayout_4.addLayout(self.layApalancado)
        self.tab.addTab(self.tab_2, "")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.tab_3)
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.layCountry = QtWidgets.QHBoxLayout()
        self.layCountry.setObjectName("layCountry")
        self.horizontalLayout_6.addLayout(self.layCountry)
        self.tab.addTab(self.tab_3, "")
        self.tab_4 = QtWidgets.QWidget()
        self.tab_4.setObjectName("tab_4")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout(self.tab_4)
        self.horizontalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.layProduct = QtWidgets.QHBoxLayout()
        self.layProduct.setObjectName("layProduct")
        self.horizontalLayout_7.addLayout(self.layProduct)
        self.tab.addTab(self.tab_4, "")
        self.verticalLayout.addWidget(self.tab)
        self._2.addLayout(self.verticalLayout)

        self.retranslateUi(wdgInvestmentClasses)
        self.tab.setCurrentIndex(5)
        QtCore.QMetaObject.connectSlotsByName(wdgInvestmentClasses)

    def retranslateUi(self, wdgInvestmentClasses):
        _translate = QtCore.QCoreApplication.translate
        self.lbl.setText(_translate("wdgInvestmentClasses", "Investments report"))
        self.groupBox.setTitle(_translate("wdgInvestmentClasses", "Calculated charts with"))
        self.radCurrent.setText(_translate("wdgInvestmentClasses", "Current value"))
        self.radInvested.setText(_translate("wdgInvestmentClasses", "Invested balance"))
        self.tab.setTabText(self.tab.indexOf(self.tabTPCVariable), _translate("wdgInvestmentClasses", "By variable percentaje"))
        self.tab.setTabText(self.tab.indexOf(self.tabPCI), _translate("wdgInvestmentClasses", "By Put / Call / Inline"))
        self.tab.setTabText(self.tab.indexOf(self.tabTipo), _translate("wdgInvestmentClasses", "By investment class"))
        self.tab.setTabText(self.tab.indexOf(self.tab_2), _translate("wdgInvestmentClasses", "By leverage"))
        self.tab.setTabText(self.tab.indexOf(self.tab_3), _translate("wdgInvestmentClasses", "By country"))
        self.tab.setTabText(self.tab.indexOf(self.tab_4), _translate("wdgInvestmentClasses", "By investment product"))

import xulpymoney_rc
