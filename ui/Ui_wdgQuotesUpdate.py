# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/wdgQuotesUpdate.ui'
#
# Created by: PyQt5 UI code generator 5.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_wdgQuotesUpdate(object):
    def setupUi(self, wdgQuotesUpdate):
        wdgQuotesUpdate.setObjectName("wdgQuotesUpdate")
        wdgQuotesUpdate.resize(1109, 795)
        self.horizontalLayout = QtWidgets.QHBoxLayout(wdgQuotesUpdate)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.cmdIntraday = QtWidgets.QPushButton(wdgQuotesUpdate)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/xulpymoney/transfer.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.cmdIntraday.setIcon(icon)
        self.cmdIntraday.setObjectName("cmdIntraday")
        self.horizontalLayout_3.addWidget(self.cmdIntraday)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.cmdAll = QtWidgets.QPushButton(wdgQuotesUpdate)
        self.cmdAll.setIcon(icon)
        self.cmdAll.setObjectName("cmdAll")
        self.horizontalLayout_3.addWidget(self.cmdAll)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem2)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.tab_3 = QtWidgets.QTabWidget(wdgQuotesUpdate)
        self.tab_3.setObjectName("tab_3")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.tab)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.tableCommands = QtWidgets.QTableWidget(self.tab)
        self.tableCommands.setObjectName("tableCommands")
        self.tableCommands.setColumnCount(0)
        self.tableCommands.setRowCount(0)
        self.horizontalLayout_4.addWidget(self.tableCommands)
        self.tab_3.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.tab_3.addTab(self.tab_2, "")
        self.verticalLayout.addWidget(self.tab_3)
        self.horizontalLayout.addLayout(self.verticalLayout)

        self.retranslateUi(wdgQuotesUpdate)
        QtCore.QMetaObject.connectSlotsByName(wdgQuotesUpdate)

    def retranslateUi(self, wdgQuotesUpdate):
        _translate = QtCore.QCoreApplication.translate
        self.cmdIntraday.setText(_translate("wdgQuotesUpdate", "Intraday only update"))
        self.cmdAll.setText(_translate("wdgQuotesUpdate", "Daily and intraday updates"))
        self.tab_3.setTabText(self.tab_3.indexOf(self.tab), _translate("wdgQuotesUpdate", "Commands"))
        self.tab_3.setTabText(self.tab_3.indexOf(self.tab_2), _translate("wdgQuotesUpdate", "Tab 2"))

import xulpymoney_rc
