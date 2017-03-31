# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/frmDividendsAdd.ui'
#
# Created by: PyQt5 UI code generator 5.8.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_frmDividendsAdd(object):
    def setupUi(self, frmDividendsAdd):
        frmDividendsAdd.setObjectName("frmDividendsAdd")
        frmDividendsAdd.setWindowModality(QtCore.Qt.WindowModal)
        frmDividendsAdd.resize(488, 493)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/xulpymoney/Money.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        frmDividendsAdd.setWindowIcon(icon)
        frmDividendsAdd.setModal(True)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(frmDividendsAdd)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.lblTitulo = QtWidgets.QLabel(frmDividendsAdd)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.lblTitulo.setFont(font)
        self.lblTitulo.setStyleSheet("color: rgb(0, 128, 0);")
        self.lblTitulo.setAlignment(QtCore.Qt.AlignCenter)
        self.lblTitulo.setObjectName("lblTitulo")
        self.verticalLayout.addWidget(self.lblTitulo)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.wdgDT = wdgDatetime(frmDividendsAdd)
        self.wdgDT.setObjectName("wdgDT")
        self.horizontalLayout.addWidget(self.wdgDT)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(frmDividendsAdd)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.cmb = QtWidgets.QComboBox(frmDividendsAdd)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmb.sizePolicy().hasHeightForWidth())
        self.cmb.setSizePolicy(sizePolicy)
        self.cmb.setObjectName("cmb")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.cmb)
        self.lblGross = QtWidgets.QLabel(frmDividendsAdd)
        self.lblGross.setObjectName("lblGross")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.lblGross)
        self.txtBruto = myQLineEdit(frmDividendsAdd)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.txtBruto.sizePolicy().hasHeightForWidth())
        self.txtBruto.setSizePolicy(sizePolicy)
        self.txtBruto.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.txtBruto.setObjectName("txtBruto")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.txtBruto)
        self.lblGrossAccount = QtWidgets.QLabel(frmDividendsAdd)
        self.lblGrossAccount.setObjectName("lblGrossAccount")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.lblGrossAccount)
        self.wdgCurrencyConversion = wdgCurrencyConversion(frmDividendsAdd)
        self.wdgCurrencyConversion.setObjectName("wdgCurrencyConversion")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.wdgCurrencyConversion)
        self.lblLiquido_4 = QtWidgets.QLabel(frmDividendsAdd)
        self.lblLiquido_4.setObjectName("lblLiquido_4")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.lblLiquido_4)
        self.txtRetencion = myQLineEdit(frmDividendsAdd)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.txtRetencion.sizePolicy().hasHeightForWidth())
        self.txtRetencion.setSizePolicy(sizePolicy)
        self.txtRetencion.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.txtRetencion.setObjectName("txtRetencion")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.txtRetencion)
        self.lblLiquido_5 = QtWidgets.QLabel(frmDividendsAdd)
        self.lblLiquido_5.setObjectName("lblLiquido_5")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.lblLiquido_5)
        self.txtDPA = myQLineEdit(frmDividendsAdd)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.txtDPA.sizePolicy().hasHeightForWidth())
        self.txtDPA.setSizePolicy(sizePolicy)
        self.txtDPA.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.txtDPA.setObjectName("txtDPA")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.txtDPA)
        self.lblLiquido = QtWidgets.QLabel(frmDividendsAdd)
        self.lblLiquido.setObjectName("lblLiquido")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.lblLiquido)
        self.txtComision = myQLineEdit(frmDividendsAdd)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.txtComision.sizePolicy().hasHeightForWidth())
        self.txtComision.setSizePolicy(sizePolicy)
        self.txtComision.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.txtComision.setObjectName("txtComision")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.txtComision)
        self.lblLiquido_7 = QtWidgets.QLabel(frmDividendsAdd)
        self.lblLiquido_7.setObjectName("lblLiquido_7")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.LabelRole, self.lblLiquido_7)
        self.txtNeto = myQLineEdit(frmDividendsAdd)
        self.txtNeto.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.txtNeto.sizePolicy().hasHeightForWidth())
        self.txtNeto.setSizePolicy(sizePolicy)
        self.txtNeto.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.txtNeto.setReadOnly(True)
        self.txtNeto.setObjectName("txtNeto")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.FieldRole, self.txtNeto)
        self.verticalLayout.addLayout(self.formLayout)
        self.lblTPC = QtWidgets.QLabel(frmDividendsAdd)
        self.lblTPC.setText("")
        self.lblTPC.setAlignment(QtCore.Qt.AlignCenter)
        self.lblTPC.setObjectName("lblTPC")
        self.verticalLayout.addWidget(self.lblTPC)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem2)
        self.cmd = QtWidgets.QPushButton(frmDividendsAdd)
        self.cmd.setObjectName("cmd")
        self.horizontalLayout_2.addWidget(self.cmd)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem3)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3.addLayout(self.verticalLayout)

        self.retranslateUi(frmDividendsAdd)
        QtCore.QMetaObject.connectSlotsByName(frmDividendsAdd)
        frmDividendsAdd.setTabOrder(self.cmb, self.txtBruto)
        frmDividendsAdd.setTabOrder(self.txtBruto, self.txtRetencion)
        frmDividendsAdd.setTabOrder(self.txtRetencion, self.txtDPA)
        frmDividendsAdd.setTabOrder(self.txtDPA, self.txtComision)
        frmDividendsAdd.setTabOrder(self.txtComision, self.cmd)
        frmDividendsAdd.setTabOrder(self.cmd, self.txtNeto)

    def retranslateUi(self, frmDividendsAdd):
        _translate = QtCore.QCoreApplication.translate
        frmDividendsAdd.setWindowTitle(_translate("frmDividendsAdd", "Dividends"))
        self.lblTitulo.setText(_translate("frmDividendsAdd", "New dividend"))
        self.label.setText(_translate("frmDividendsAdd", "Select dividend type"))
        self.lblGross.setText(_translate("frmDividendsAdd", "Gross amount"))
        self.txtBruto.setText(_translate("frmDividendsAdd", "0"))
        self.lblGrossAccount.setText(_translate("frmDividendsAdd", "Gross amount in account currency"))
        self.lblLiquido_4.setText(_translate("frmDividendsAdd", "Withholding tax amount"))
        self.txtRetencion.setText(_translate("frmDividendsAdd", "0"))
        self.lblLiquido_5.setText(_translate("frmDividendsAdd", "Dividend per share"))
        self.txtDPA.setText(_translate("frmDividendsAdd", "0"))
        self.lblLiquido.setText(_translate("frmDividendsAdd", "Comission"))
        self.txtComision.setText(_translate("frmDividendsAdd", "0"))
        self.lblLiquido_7.setText(_translate("frmDividendsAdd", "Net amount"))
        self.txtNeto.setText(_translate("frmDividendsAdd", "0"))

from myqlineedit import myQLineEdit
from wdgCurrencyConversion import wdgCurrencyConversion
from wdgDatetime import wdgDatetime
import xulpymoney_rc