# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'xulpymoney/ui/wdgInvestmentOperationsSelector.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_wdgInvestmentOperationsSelector(object):
    def setupUi(self, wdgInvestmentOperationsSelector):
        wdgInvestmentOperationsSelector.setObjectName("wdgInvestmentOperationsSelector")
        wdgInvestmentOperationsSelector.resize(400, 300)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(wdgInvestmentOperationsSelector)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.grp = QtWidgets.QGroupBox(wdgInvestmentOperationsSelector)
        self.grp.setObjectName("grp")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.grp)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.chkShowSelected = QtWidgets.QCheckBox(self.grp)
        self.chkShowSelected.setChecked(True)
        self.chkShowSelected.setObjectName("chkShowSelected")
        self.verticalLayout.addWidget(self.chkShowSelected)
        self.wdgProductSelector = wdgProductSelector(self.grp)
        self.wdgProductSelector.setObjectName("wdgProductSelector")
        self.verticalLayout.addWidget(self.wdgProductSelector)
        self.mqtwOperations = mqtwObjects(self.grp)
        self.mqtwOperations.setObjectName("mqtwOperations")
        self.verticalLayout.addWidget(self.mqtwOperations)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.horizontalLayout_2.addWidget(self.grp)

        self.retranslateUi(wdgInvestmentOperationsSelector)
        QtCore.QMetaObject.connectSlotsByName(wdgInvestmentOperationsSelector)

    def retranslateUi(self, wdgInvestmentOperationsSelector):
        _translate = QtCore.QCoreApplication.translate
        wdgInvestmentOperationsSelector.setWindowTitle(_translate("wdgInvestmentOperationsSelector", "Form"))
        self.grp.setTitle(_translate("wdgInvestmentOperationsSelector", "Strategy"))
        self.chkShowSelected.setText(_translate("wdgInvestmentOperationsSelector", "Show selected"))
from xulpymoney.ui.myqtablewidget import mqtwObjects
from xulpymoney.ui.wdgProductSelector import wdgProductSelector
