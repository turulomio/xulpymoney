# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/frmInvestmentOperationsAdd.ui'
#
# Created by: PyQt5 UI code generator 5.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_frmInvestmentOperationsAdd(object):
    def setupUi(self, frmInvestmentOperationsAdd):
        frmInvestmentOperationsAdd.setObjectName("frmInvestmentOperationsAdd")
        frmInvestmentOperationsAdd.setWindowModality(QtCore.Qt.WindowModal)
        frmInvestmentOperationsAdd.resize(719, 557)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/xulpymoney/document-edit.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        frmInvestmentOperationsAdd.setWindowIcon(icon)
        frmInvestmentOperationsAdd.setModal(True)
        self.horizontalLayout = QtWidgets.QHBoxLayout(frmInvestmentOperationsAdd)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.lblTitulo = QtWidgets.QLabel(frmInvestmentOperationsAdd)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.lblTitulo.setFont(font)
        self.lblTitulo.setStyleSheet("color: rgb(0, 128, 0);")
        self.lblTitulo.setAlignment(QtCore.Qt.AlignCenter)
        self.lblTitulo.setObjectName("lblTitulo")
        self.verticalLayout.addWidget(self.lblTitulo)
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem)
        self.wdgDT = wdgDatetime(frmInvestmentOperationsAdd)
        self.wdgDT.setObjectName("wdgDT")
        self.horizontalLayout_8.addWidget(self.wdgDT)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout_8)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.lblType = QtWidgets.QLabel(frmInvestmentOperationsAdd)
        self.lblType.setObjectName("lblType")
        self.horizontalLayout_3.addWidget(self.lblType)
        self.cmbTiposOperaciones = QtWidgets.QComboBox(frmInvestmentOperationsAdd)
        self.cmbTiposOperaciones.setObjectName("cmbTiposOperaciones")
        self.horizontalLayout_3.addWidget(self.cmbTiposOperaciones)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.lblShares = QtWidgets.QLabel(frmInvestmentOperationsAdd)
        self.lblShares.setObjectName("lblShares")
        self.horizontalLayout_5.addWidget(self.lblShares)
        self.txtAcciones = myQLineEdit(frmInvestmentOperationsAdd)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.txtAcciones.sizePolicy().hasHeightForWidth())
        self.txtAcciones.setSizePolicy(sizePolicy)
        self.txtAcciones.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.txtAcciones.setObjectName("txtAcciones")
        self.horizontalLayout_5.addWidget(self.txtAcciones)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.wdg2CCurrencyConversion = wdgTwoCurrencyLineEdit(frmInvestmentOperationsAdd)
        self.wdg2CCurrencyConversion.setObjectName("wdg2CCurrencyConversion")
        self.verticalLayout.addWidget(self.wdg2CCurrencyConversion)
        self.wdg2CPrice = wdgTwoCurrencyLineEdit(frmInvestmentOperationsAdd)
        self.wdg2CPrice.setObjectName("wdg2CPrice")
        self.verticalLayout.addWidget(self.wdg2CPrice)
        self.wdg2CTaxes = wdgTwoCurrencyLineEdit(frmInvestmentOperationsAdd)
        self.wdg2CTaxes.setObjectName("wdg2CTaxes")
        self.verticalLayout.addWidget(self.wdg2CTaxes)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.wdg2CComission = wdgTwoCurrencyLineEdit(frmInvestmentOperationsAdd)
        self.wdg2CComission.setObjectName("wdg2CComission")
        self.horizontalLayout_2.addWidget(self.wdg2CComission)
        self.cmdComissionCalculator = QtWidgets.QToolButton(frmInvestmentOperationsAdd)
        self.cmdComissionCalculator.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/xulpymoney/tools-wizard.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.cmdComissionCalculator.setIcon(icon1)
        self.cmdComissionCalculator.setObjectName("cmdComissionCalculator")
        self.horizontalLayout_2.addWidget(self.cmdComissionCalculator)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.wdg2CGross = wdgTwoCurrencyLineEdit(frmInvestmentOperationsAdd)
        self.wdg2CGross.setObjectName("wdg2CGross")
        self.verticalLayout.addWidget(self.wdg2CGross)
        self.wdg2CNet = wdgTwoCurrencyLineEdit(frmInvestmentOperationsAdd)
        self.wdg2CNet.setObjectName("wdg2CNet")
        self.verticalLayout.addWidget(self.wdg2CNet)
        self.cmd = QtWidgets.QPushButton(frmInvestmentOperationsAdd)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/xulpymoney/save.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.cmd.setIcon(icon2)
        self.cmd.setObjectName("cmd")
        self.verticalLayout.addWidget(self.cmd)
        self.horizontalLayout.addLayout(self.verticalLayout)

        self.retranslateUi(frmInvestmentOperationsAdd)
        QtCore.QMetaObject.connectSlotsByName(frmInvestmentOperationsAdd)

    def retranslateUi(self, frmInvestmentOperationsAdd):
        _translate = QtCore.QCoreApplication.translate
        frmInvestmentOperationsAdd.setWindowTitle(_translate("frmInvestmentOperationsAdd", "New investment operation"))
        self.lblType.setText(_translate("frmInvestmentOperationsAdd", "Operation type"))
        self.lblShares.setText(_translate("frmInvestmentOperationsAdd", "Number of shares"))
        self.txtAcciones.setText(_translate("frmInvestmentOperationsAdd", "0"))
        self.cmdComissionCalculator.setToolTip(_translate("frmInvestmentOperationsAdd", "Comission calculator"))
        self.cmd.setText(_translate("frmInvestmentOperationsAdd", "Save"))

from myqlineedit import myQLineEdit
from wdgDatetime import wdgDatetime
from wdgTwoCurrencyLineEdit import wdgTwoCurrencyLineEdit
import xulpymoney_rc
