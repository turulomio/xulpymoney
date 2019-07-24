# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'xulpymoney/ui/frmQuotesIBM.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_frmQuotesIBM(object):
    def setupUi(self, frmQuotesIBM):
        frmQuotesIBM.setObjectName("frmQuotesIBM")
        frmQuotesIBM.resize(529, 407)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/xulpymoney/add.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        frmQuotesIBM.setWindowIcon(icon)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(frmQuotesIBM)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.lblInvestment = QtWidgets.QLabel(frmQuotesIBM)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.lblInvestment.setFont(font)
        self.lblInvestment.setStyleSheet("color: rgb(0, 192, 0);")
        self.lblInvestment.setAlignment(QtCore.Qt.AlignCenter)
        self.lblInvestment.setObjectName("lblInvestment")
        self.verticalLayout.addWidget(self.lblInvestment)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.wdgDT = wdgDatetime(frmQuotesIBM)
        self.wdgDT.setFocusPolicy(QtCore.Qt.TabFocus)
        self.wdgDT.setObjectName("wdgDT")
        self.horizontalLayout_2.addWidget(self.wdgDT)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.chkNone = QtWidgets.QCheckBox(frmQuotesIBM)
        self.chkNone.setObjectName("chkNone")
        self.verticalLayout.addWidget(self.chkNone)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(frmQuotesIBM)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.txtQuote = myQLineEdit(frmQuotesIBM)
        self.txtQuote.setObjectName("txtQuote")
        self.horizontalLayout.addWidget(self.txtQuote)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.chkCanBePurged = QtWidgets.QCheckBox(frmQuotesIBM)
        self.chkCanBePurged.setEnabled(False)
        self.chkCanBePurged.setChecked(True)
        self.chkCanBePurged.setObjectName("chkCanBePurged")
        self.verticalLayout.addWidget(self.chkCanBePurged)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem2)
        self.buttonbox = QtWidgets.QDialogButtonBox(frmQuotesIBM)
        self.buttonbox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonbox.setObjectName("buttonbox")
        self.horizontalLayout_4.addWidget(self.buttonbox)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem3)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_3.addLayout(self.verticalLayout)

        self.retranslateUi(frmQuotesIBM)
        QtCore.QMetaObject.connectSlotsByName(frmQuotesIBM)
        frmQuotesIBM.setTabOrder(self.txtQuote, self.buttonbox)
        frmQuotesIBM.setTabOrder(self.buttonbox, self.chkNone)
        frmQuotesIBM.setTabOrder(self.chkNone, self.chkCanBePurged)
        frmQuotesIBM.setTabOrder(self.chkCanBePurged, self.wdgDT)

    def retranslateUi(self, frmQuotesIBM):
        _translate = QtCore.QCoreApplication.translate
        frmQuotesIBM.setWindowTitle(_translate("frmQuotesIBM", "Add a product price manually"))
        self.chkNone.setText(_translate("frmQuotesIBM", "Add a close session price"))
        self.label.setText(_translate("frmQuotesIBM", "Add a price"))
        self.chkCanBePurged.setText(_translate("frmQuotesIBM", "Can be purged?"))
from xulpymoney.ui.myqlineedit import myQLineEdit
from xulpymoney.ui.wdgDatetime import wdgDatetime
import xulpymoney.images.xulpymoney_rc
