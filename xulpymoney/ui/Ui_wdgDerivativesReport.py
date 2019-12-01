# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'xulpymoney/ui/wdgDerivativesReport.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_wdgDerivativesReport(object):
    def setupUi(self, wdgDerivativesReport):
        wdgDerivativesReport.setObjectName("wdgDerivativesReport")
        wdgDerivativesReport.setProperty("modal", False)
        wdgDerivativesReport.resize(450, 290)
        self._2 = QtWidgets.QHBoxLayout(wdgDerivativesReport)
        self._2.setObjectName("_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.lblTitulo = QtWidgets.QLabel(wdgDerivativesReport)
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.lblTitulo.setFont(font)
        self.lblTitulo.setStyleSheet("color: rgb(0, 128, 0);")
        self.lblTitulo.setAlignment(QtCore.Qt.AlignCenter)
        self.lblTitulo.setObjectName("lblTitulo")
        self.verticalLayout.addWidget(self.lblTitulo)
        self.textBrowser = QtWidgets.QTextBrowser(wdgDerivativesReport)
        self.textBrowser.setOpenExternalLinks(True)
        self.textBrowser.setObjectName("textBrowser")
        self.verticalLayout.addWidget(self.textBrowser)
        self._2.addLayout(self.verticalLayout)

        self.retranslateUi(wdgDerivativesReport)
        QtCore.QMetaObject.connectSlotsByName(wdgDerivativesReport)

    def retranslateUi(self, wdgDerivativesReport):
        _translate = QtCore.QCoreApplication.translate
        self.lblTitulo.setText(_translate("wdgDerivativesReport", "Derivatives report"))
import xulpymoney.images.xulpymoney_rc
