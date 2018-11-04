# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'xulpymoney/ui/wdgOpportunitiesAdd.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_wdgOpportunitiesAdd(object):
    def setupUi(self, wdgOpportunitiesAdd):
        wdgOpportunitiesAdd.setObjectName("wdgOpportunitiesAdd")
        wdgOpportunitiesAdd.resize(959, 206)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/xulpymoney/bank.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        wdgOpportunitiesAdd.setWindowIcon(icon)
        self.horizontalLayout = QtWidgets.QHBoxLayout(wdgOpportunitiesAdd)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.lbl = QtWidgets.QLabel(wdgOpportunitiesAdd)
        self.lbl.setMinimumSize(QtCore.QSize(800, 0))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.lbl.setFont(font)
        self.lbl.setText("")
        self.lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl.setObjectName("lbl")
        self.verticalLayout.addWidget(self.lbl)
        self.productSelector = wdgProductSelector(wdgOpportunitiesAdd)
        self.productSelector.setObjectName("productSelector")
        self.verticalLayout.addWidget(self.productSelector)
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.ExpandingFieldsGrow)
        self.formLayout.setObjectName("formLayout")
        self.deDate = QtWidgets.QDateEdit(wdgOpportunitiesAdd)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.deDate.sizePolicy().hasHeightForWidth())
        self.deDate.setSizePolicy(sizePolicy)
        self.deDate.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.deDate.setCalendarPopup(True)
        self.deDate.setObjectName("deDate")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.deDate)
        self.label_2 = QtWidgets.QLabel(wdgOpportunitiesAdd)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.txtPrice = myQLineEdit(wdgOpportunitiesAdd)
        self.txtPrice.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.txtPrice.setObjectName("txtPrice")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.txtPrice)
        self.label_5 = QtWidgets.QLabel(wdgOpportunitiesAdd)
        self.label_5.setObjectName("label_5")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_5)
        self.verticalLayout.addLayout(self.formLayout)
        self.buttonbox = QtWidgets.QDialogButtonBox(wdgOpportunitiesAdd)
        self.buttonbox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonbox.setCenterButtons(True)
        self.buttonbox.setObjectName("buttonbox")
        self.verticalLayout.addWidget(self.buttonbox)
        self.horizontalLayout.addLayout(self.verticalLayout)

        self.retranslateUi(wdgOpportunitiesAdd)
        QtCore.QMetaObject.connectSlotsByName(wdgOpportunitiesAdd)

    def retranslateUi(self, wdgOpportunitiesAdd):
        _translate = QtCore.QCoreApplication.translate
        self.deDate.setDisplayFormat(_translate("wdgOpportunitiesAdd", "yyyy/MM/dd"))
        self.label_2.setText(_translate("wdgOpportunitiesAdd", "Opportunity date"))
        self.txtPrice.setText(_translate("wdgOpportunitiesAdd", "0"))
        self.label_5.setText(_translate("wdgOpportunitiesAdd", "Price"))

from xulpymoney.ui.myqlineedit import myQLineEdit
from xulpymoney.ui.wdgProductSelector import wdgProductSelector
import xulpymoney.images.xulpymoney_rc
