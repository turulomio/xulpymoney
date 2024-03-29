# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'xulpymoney/ui/wdgOrdersAdd.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_wdgOrdersAdd(object):
    def setupUi(self, wdgOrdersAdd):
        wdgOrdersAdd.setObjectName("wdgOrdersAdd")
        wdgOrdersAdd.resize(826, 455)
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
        self.lblPixmap = QtWidgets.QLabel(wdgOrdersAdd)
        self.lblPixmap.setMaximumSize(QtCore.QSize(64, 64))
        self.lblPixmap.setText("")
        self.lblPixmap.setPixmap(QtGui.QPixmap(":/xulpymoney/order.png"))
        self.lblPixmap.setScaledContents(True)
        self.lblPixmap.setAlignment(QtCore.Qt.AlignCenter)
        self.lblPixmap.setObjectName("lblPixmap")
        self.verticalLayout.addWidget(self.lblPixmap, 0, QtCore.Qt.AlignHCenter)
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label_7 = QtWidgets.QLabel(wdgOrdersAdd)
        self.label_7.setObjectName("label_7")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_7)
        self.cmbProducts = QtWidgets.QComboBox(wdgOrdersAdd)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbProducts.sizePolicy().hasHeightForWidth())
        self.cmbProducts.setSizePolicy(sizePolicy)
        self.cmbProducts.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        self.cmbProducts.setObjectName("cmbProducts")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.cmbProducts)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.cmbInvestments = QtWidgets.QComboBox(wdgOrdersAdd)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbInvestments.sizePolicy().hasHeightForWidth())
        self.cmbInvestments.setSizePolicy(sizePolicy)
        self.cmbInvestments.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        self.cmbInvestments.setObjectName("cmbInvestments")
        self.horizontalLayout_6.addWidget(self.cmbInvestments)
        self.chkWithoutShares = QtWidgets.QCheckBox(wdgOrdersAdd)
        self.chkWithoutShares.setObjectName("chkWithoutShares")
        self.horizontalLayout_6.addWidget(self.chkWithoutShares)
        self.formLayout.setLayout(1, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout_6)
        self.label = QtWidgets.QLabel(wdgOrdersAdd)
        self.label.setObjectName("label")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label)
        self.label_2 = QtWidgets.QLabel(wdgOrdersAdd)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.deDate = QtWidgets.QDateEdit(wdgOrdersAdd)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.deDate.sizePolicy().hasHeightForWidth())
        self.deDate.setSizePolicy(sizePolicy)
        self.deDate.setMinimumSize(QtCore.QSize(200, 0))
        self.deDate.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.deDate.setCalendarPopup(True)
        self.deDate.setObjectName("deDate")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.deDate)
        self.label_3 = QtWidgets.QLabel(wdgOrdersAdd)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.deExpiration = QtWidgets.QDateEdit(wdgOrdersAdd)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.deExpiration.sizePolicy().hasHeightForWidth())
        self.deExpiration.setSizePolicy(sizePolicy)
        self.deExpiration.setMinimumSize(QtCore.QSize(200, 0))
        self.deExpiration.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.deExpiration.setCalendarPopup(True)
        self.deExpiration.setObjectName("deExpiration")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.deExpiration)
        self.label_4 = QtWidgets.QLabel(wdgOrdersAdd)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.txtShares = myQLineEdit(wdgOrdersAdd)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.txtShares.sizePolicy().hasHeightForWidth())
        self.txtShares.setSizePolicy(sizePolicy)
        self.txtShares.setMinimumSize(QtCore.QSize(200, 0))
        self.txtShares.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.txtShares.setObjectName("txtShares")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.txtShares)
        self.label_5 = QtWidgets.QLabel(wdgOrdersAdd)
        self.label_5.setObjectName("label_5")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.label_5)
        self.txtPrice = myQLineEdit(wdgOrdersAdd)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.txtPrice.sizePolicy().hasHeightForWidth())
        self.txtPrice.setSizePolicy(sizePolicy)
        self.txtPrice.setMinimumSize(QtCore.QSize(200, 0))
        self.txtPrice.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.txtPrice.setObjectName("txtPrice")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.txtPrice)
        self.label_6 = QtWidgets.QLabel(wdgOrdersAdd)
        self.label_6.setObjectName("label_6")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.label_6)
        self.txtAmount = myQLineEdit(wdgOrdersAdd)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.txtAmount.sizePolicy().hasHeightForWidth())
        self.txtAmount.setSizePolicy(sizePolicy)
        self.txtAmount.setMinimumSize(QtCore.QSize(200, 0))
        self.txtAmount.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.txtAmount.setObjectName("txtAmount")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.txtAmount)
        self.verticalLayout.addLayout(self.formLayout)
        self.lblWarning = QtWidgets.QLabel(wdgOrdersAdd)
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.lblWarning.setFont(font)
        self.lblWarning.setStyleSheet("color: rgb(200, 0, 0);")
        self.lblWarning.setFrameShape(QtWidgets.QFrame.Box)
        self.lblWarning.setAlignment(QtCore.Qt.AlignCenter)
        self.lblWarning.setObjectName("lblWarning")
        self.verticalLayout.addWidget(self.lblWarning)
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
        self.label_7.setText(_translate("wdgOrdersAdd", "Select a product"))
        self.chkWithoutShares.setText(_translate("wdgOrdersAdd", "Without shares"))
        self.label.setText(_translate("wdgOrdersAdd", "Select your investment"))
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
        self.lblWarning.setText(_translate("wdgOrdersAdd", "WARNING"))
from xulpymoney.ui.myqlineedit import myQLineEdit
import xulpymoney.images.xulpymoney_rc
