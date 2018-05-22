# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/wdgOrdersAdd.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_wdgOrdersAdd(object):
    def setupUi(self, wdgOrdersAdd):
        wdgOrdersAdd.setObjectName("wdgOrdersAdd")
        wdgOrdersAdd.resize(510, 328)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/xulpymoney/bank.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        wdgOrdersAdd.setWindowIcon(icon)
        self.horizontalLayout = QtWidgets.QHBoxLayout(wdgOrdersAdd)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.lbl = QtWidgets.QLabel(wdgOrdersAdd)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.lbl.setFont(font)
        self.lbl.setText("")
        self.lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl.setObjectName("lbl")
        self.verticalLayout.addWidget(self.lbl)
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.ExpandingFieldsGrow)
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(wdgOrdersAdd)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.cmbInvestments = QtWidgets.QComboBox(wdgOrdersAdd)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbInvestments.sizePolicy().hasHeightForWidth())
        self.cmbInvestments.setSizePolicy(sizePolicy)
        self.cmbInvestments.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        self.cmbInvestments.setObjectName("cmbInvestments")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.cmbInvestments)
        self.label_2 = QtWidgets.QLabel(wdgOrdersAdd)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.deDate = QtWidgets.QDateEdit(wdgOrdersAdd)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.deDate.sizePolicy().hasHeightForWidth())
        self.deDate.setSizePolicy(sizePolicy)
        self.deDate.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.deDate.setCalendarPopup(True)
        self.deDate.setObjectName("deDate")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.deDate)
        self.label_3 = QtWidgets.QLabel(wdgOrdersAdd)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.deExpiration = QtWidgets.QDateEdit(wdgOrdersAdd)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.deExpiration.sizePolicy().hasHeightForWidth())
        self.deExpiration.setSizePolicy(sizePolicy)
        self.deExpiration.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.deExpiration.setCalendarPopup(True)
        self.deExpiration.setObjectName("deExpiration")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.deExpiration)
        self.label_4 = QtWidgets.QLabel(wdgOrdersAdd)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.txtShares = myQLineEdit(wdgOrdersAdd)
        self.txtShares.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.txtShares.setObjectName("txtShares")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.txtShares)
        self.label_5 = QtWidgets.QLabel(wdgOrdersAdd)
        self.label_5.setObjectName("label_5")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.LabelRole, self.label_5)
        self.txtPrice = myQLineEdit(wdgOrdersAdd)
        self.txtPrice.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.txtPrice.setObjectName("txtPrice")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.FieldRole, self.txtPrice)
        self.label_6 = QtWidgets.QLabel(wdgOrdersAdd)
        self.label_6.setObjectName("label_6")
        self.formLayout.setWidget(8, QtWidgets.QFormLayout.LabelRole, self.label_6)
        self.txtAmount = myQLineEdit(wdgOrdersAdd)
        self.txtAmount.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.txtAmount.setObjectName("txtAmount")
        self.formLayout.setWidget(8, QtWidgets.QFormLayout.FieldRole, self.txtAmount)
        self.verticalLayout.addLayout(self.formLayout)
        self.buttonbox = QtWidgets.QDialogButtonBox(wdgOrdersAdd)
        self.buttonbox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonbox.setCenterButtons(True)
        self.buttonbox.setObjectName("buttonbox")
        self.verticalLayout.addWidget(self.buttonbox)
        self.horizontalLayout.addLayout(self.verticalLayout)

        self.retranslateUi(wdgOrdersAdd)
        QtCore.QMetaObject.connectSlotsByName(wdgOrdersAdd)

    def retranslateUi(self, wdgOrdersAdd):
        _translate = QtCore.QCoreApplication.translate
        self.label.setText(_translate("wdgOrdersAdd", "Active investment"))
        self.label_2.setText(_translate("wdgOrdersAdd", "Order date"))
        self.deDate.setDisplayFormat(_translate("wdgOrdersAdd", "yyyy/MM/dd"))
        self.label_3.setText(_translate("wdgOrdersAdd", "Order expiration date"))
        self.deExpiration.setDisplayFormat(_translate("wdgOrdersAdd", "yyyy/MM/dd"))
        self.label_4.setText(_translate("wdgOrdersAdd", "Shares number"))
        self.txtShares.setText(_translate("wdgOrdersAdd", "0"))
        self.label_5.setText(_translate("wdgOrdersAdd", "Price"))
        self.txtPrice.setText(_translate("wdgOrdersAdd", "0"))
        self.label_6.setText(_translate("wdgOrdersAdd", "Amount"))
        self.txtAmount.setText(_translate("wdgOrdersAdd", "0"))

from myqlineedit import myQLineEdit
import xulpymoney_rc
