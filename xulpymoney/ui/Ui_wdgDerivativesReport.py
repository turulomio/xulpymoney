# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'xulpymoney/ui/wdgDerivativesReport.ui'
#
# Created by: PyQt5 UI code generator 5.14.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_wdgDerivativesReport(object):
    def setupUi(self, wdgDerivativesReport):
        wdgDerivativesReport.setObjectName("wdgDerivativesReport")
        wdgDerivativesReport.setProperty("modal", False)
        wdgDerivativesReport.resize(981, 781)
        self.horizontalLayout = QtWidgets.QHBoxLayout(wdgDerivativesReport)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.lbl = QtWidgets.QLabel(wdgDerivativesReport)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.lbl.setFont(font)
        self.lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl.setObjectName("lbl")
        self.verticalLayout.addWidget(self.lbl)
        self.wdgIOHSLong = wdgInvestmentOperationHistoricalSelector(wdgDerivativesReport)
        self.wdgIOHSLong.setObjectName("wdgIOHSLong")
        self.verticalLayout.addWidget(self.wdgIOHSLong)
        self.wdgIOHSShort = wdgInvestmentOperationHistoricalSelector(wdgDerivativesReport)
        self.wdgIOHSShort.setObjectName("wdgIOHSShort")
        self.verticalLayout.addWidget(self.wdgIOHSShort)
        self.textBrowser = QtWidgets.QTextBrowser(wdgDerivativesReport)
        self.textBrowser.setOpenExternalLinks(True)
        self.textBrowser.setObjectName("textBrowser")
        self.verticalLayout.addWidget(self.textBrowser)
        self.horizontalLayout.addLayout(self.verticalLayout)

        self.retranslateUi(wdgDerivativesReport)
        QtCore.QMetaObject.connectSlotsByName(wdgDerivativesReport)

    def retranslateUi(self, wdgDerivativesReport):
        _translate = QtCore.QCoreApplication.translate
        self.lbl.setText(_translate("wdgDerivativesReport", "Derivatives report"))
from xulpymoney.ui.wdgInvestmentOperationsSelector import wdgInvestmentOperationHistoricalSelector
import xulpymoney.images.xulpymoney_rc
