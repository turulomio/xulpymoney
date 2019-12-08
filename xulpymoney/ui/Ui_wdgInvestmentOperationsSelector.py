# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'xulpymoney/ui/wdgInvestmentOperationsSelector.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_wdgInvestmentOperationsSelector(object):
    def setupUi(self, wdgInvestmentOperationsSelector):
        wdgInvestmentOperationsSelector.setObjectName("wdgInvestmentOperationsSelector")
        wdgInvestmentOperationsSelector.resize(400, 300)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(wdgInvestmentOperationsSelector)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.groupBox = QtWidgets.QGroupBox(wdgInvestmentOperationsSelector)
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.groupBox)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.chkShowSelected = QtWidgets.QCheckBox(self.groupBox)
        self.chkShowSelected.setChecked(True)
        self.chkShowSelected.setObjectName("chkShowSelected")
        self.verticalLayout.addWidget(self.chkShowSelected)
        self.wdgProductSelector = wdgProductSelector(self.groupBox)
        self.wdgProductSelector.setObjectName("wdgProductSelector")
        self.verticalLayout.addWidget(self.wdgProductSelector)
        self.tbl = myQTableWidget(self.groupBox)
        self.tbl.setObjectName("tbl")
        self.tbl.setColumnCount(0)
        self.tbl.setRowCount(0)
        self.verticalLayout.addWidget(self.tbl)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.horizontalLayout_2.addWidget(self.groupBox)

        self.retranslateUi(wdgInvestmentOperationsSelector)
        QtCore.QMetaObject.connectSlotsByName(wdgInvestmentOperationsSelector)

    def retranslateUi(self, wdgInvestmentOperationsSelector):
        _translate = QtCore.QCoreApplication.translate
        wdgInvestmentOperationsSelector.setWindowTitle(_translate("wdgInvestmentOperationsSelector", "Form"))
        self.groupBox.setTitle(_translate("wdgInvestmentOperationsSelector", "Strategy"))
        self.chkShowSelected.setText(_translate("wdgInvestmentOperationsSelector", "Show selected"))
from xulpymoney.ui.myqtablewidget import myQTableWidget
from xulpymoney.ui.wdgProductSelector import wdgProductSelector
