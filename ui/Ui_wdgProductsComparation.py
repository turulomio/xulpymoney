# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/wdgProductsComparation.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_wdgProductsComparation(object):
    def setupUi(self, wdgProductsComparation):
        wdgProductsComparation.setObjectName("wdgProductsComparation")
        wdgProductsComparation.resize(1030, 46)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(wdgProductsComparation)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.selector1 = wdgProductSelector(wdgProductsComparation)
        self.selector1.setObjectName("selector1")
        self.verticalLayout.addWidget(self.selector1)
        self.selector2 = wdgProductSelector(wdgProductsComparation)
        self.selector2.setObjectName("selector2")
        self.verticalLayout.addWidget(self.selector2)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.line_3 = QtWidgets.QFrame(wdgProductsComparation)
        self.line_3.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.horizontalLayout.addWidget(self.line_3)
        self.label_2 = QtWidgets.QLabel(wdgProductsComparation)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.cmbCompareTypes = QtWidgets.QComboBox(wdgProductsComparation)
        self.cmbCompareTypes.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        self.cmbCompareTypes.setObjectName("cmbCompareTypes")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/xulpymoney/eye.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.cmbCompareTypes.addItem(icon, "")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/xulpymoney/eye_red.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.cmbCompareTypes.addItem(icon1, "")
        self.cmbCompareTypes.addItem(icon, "")
        self.cmbCompareTypes.addItem(icon1, "")
        self.cmbCompareTypes.addItem(icon, "")
        self.cmbCompareTypes.addItem(icon1, "")
        self.horizontalLayout.addWidget(self.cmbCompareTypes)
        self.line = QtWidgets.QFrame(wdgProductsComparation)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.horizontalLayout.addWidget(self.line)
        self.label_7 = QtWidgets.QLabel(wdgProductsComparation)
        self.label_7.setObjectName("label_7")
        self.horizontalLayout.addWidget(self.label_7)
        self.deCompare = QtWidgets.QDateEdit(wdgProductsComparation)
        self.deCompare.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.deCompare.setObjectName("deCompare")
        self.horizontalLayout.addWidget(self.deCompare)
        self.line_2 = QtWidgets.QFrame(wdgProductsComparation)
        self.line_2.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.horizontalLayout.addWidget(self.line_2)
        self.cmdComparationData = QtWidgets.QToolButton(wdgProductsComparation)
        self.cmdComparationData.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/xulpymoney/compare.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.cmdComparationData.setIcon(icon2)
        self.cmdComparationData.setObjectName("cmdComparationData")
        self.horizontalLayout.addWidget(self.cmdComparationData)
        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.retranslateUi(wdgProductsComparation)
        QtCore.QMetaObject.connectSlotsByName(wdgProductsComparation)

    def retranslateUi(self, wdgProductsComparation):
        _translate = QtCore.QCoreApplication.translate
        wdgProductsComparation.setWindowTitle(_translate("wdgProductsComparation", "Form"))
        self.label_2.setText(_translate("wdgProductsComparation", "Select a method to compare"))
        self.cmbCompareTypes.setItemText(0, _translate("wdgProductsComparation", "Not changed data"))
        self.cmbCompareTypes.setItemText(1, _translate("wdgProductsComparation", "Scattering product prices"))
        self.cmbCompareTypes.setItemText(2, _translate("wdgProductsComparation", "Controling percentage evolution"))
        self.cmbCompareTypes.setItemText(3, _translate("wdgProductsComparation", "Controlling percentage evolution. Leveraged reduced"))
        self.cmbCompareTypes.setItemText(4, _translate("wdgProductsComparation", "Controling inverse percentage evolution"))
        self.cmbCompareTypes.setItemText(5, _translate("wdgProductsComparation", "Controling inverse percentage evolultion. Leveraged reduced"))
        self.label_7.setText(_translate("wdgProductsComparation", "From date"))
        self.deCompare.setDisplayFormat(_translate("wdgProductsComparation", "yyyy-MM-dd"))
        self.cmdComparationData.setToolTip(_translate("wdgProductsComparation", "Shows comparation data"))

from wdgProductSelector import wdgProductSelector
import xulpymoney_rc
