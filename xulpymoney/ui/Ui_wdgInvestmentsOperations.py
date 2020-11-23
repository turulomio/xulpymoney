# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'xulpymoney/ui/wdgInvestmentsOperations.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_wdgInvestmentsOperations(object):
    def setupUi(self, wdgInvestmentsOperations):
        wdgInvestmentsOperations.setObjectName("wdgInvestmentsOperations")
        wdgInvestmentsOperations.resize(1048, 635)
        self.horizontalLayout = QtWidgets.QHBoxLayout(wdgInvestmentsOperations)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.lbl = QtWidgets.QLabel(wdgInvestmentsOperations)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.lbl.setFont(font)
        self.lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl.setObjectName("lbl")
        self.verticalLayout.addWidget(self.lbl)
        self.tab = QtWidgets.QTabWidget(wdgInvestmentsOperations)
        self.tab.setObjectName("tab")
        self.tab_1 = QtWidgets.QWidget()
        self.tab_1.setObjectName("tab_1")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout(self.tab_1)
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.groupBox = QtWidgets.QGroupBox(self.tab_1)
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.groupBox)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.radYear = QtWidgets.QRadioButton(self.groupBox)
        self.radYear.setObjectName("radYear")
        self.horizontalLayout_3.addWidget(self.radYear)
        self.wy = wdgYear(self.groupBox)
        self.wy.setObjectName("wy")
        self.horizontalLayout_3.addWidget(self.wy)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.verticalLayout_3.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.radYearMonth = QtWidgets.QRadioButton(self.groupBox)
        self.radYearMonth.setChecked(True)
        self.radYearMonth.setObjectName("radYearMonth")
        self.horizontalLayout_2.addWidget(self.radYearMonth)
        self.wym = wdgYearMonth(self.groupBox)
        self.wym.setObjectName("wym")
        self.horizontalLayout_2.addWidget(self.wym)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)
        self.verticalLayout_2.addLayout(self.verticalLayout_3)
        self.line = QtWidgets.QFrame(self.groupBox)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout_2.addWidget(self.line)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem2)
        self.cmbFilters = QtWidgets.QComboBox(self.groupBox)
        self.cmbFilters.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        self.cmbFilters.setObjectName("cmbFilters")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/xulpymoney/star.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.cmbFilters.addItem(icon, "")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/xulpymoney/add.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.cmbFilters.addItem(icon1, "")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/xulpymoney/list-remove.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.cmbFilters.addItem(icon2, "")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/xulpymoney/eye_red.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.cmbFilters.addItem(icon3, "")
        self.horizontalLayout_4.addWidget(self.cmbFilters)
        self.verticalLayout_2.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_6.addLayout(self.verticalLayout_2)
        self.verticalLayout_4.addWidget(self.groupBox)
        self.mqtw = mqtwObjects(self.tab_1)
        self.mqtw.setObjectName("mqtw")
        self.verticalLayout_4.addWidget(self.mqtw)
        self.horizontalLayout_7.addLayout(self.verticalLayout_4)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/xulpymoney/document-edit.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.tab.addTab(self.tab_1, icon4, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.tab_2)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.mqtwCurrent = mqtwObjects(self.tab_2)
        self.mqtwCurrent.setObjectName("mqtwCurrent")
        self.horizontalLayout_5.addWidget(self.mqtwCurrent)
        self.tab.addTab(self.tab_2, icon4, "")
        self.verticalLayout.addWidget(self.tab)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.actionShowInvestment = QtWidgets.QAction(wdgInvestmentsOperations)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/xulpymoney/bundle.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionShowInvestment.setIcon(icon5)
        self.actionShowInvestment.setObjectName("actionShowInvestment")
        self.actionShowInvestmentOperation = QtWidgets.QAction(wdgInvestmentsOperations)
        self.actionShowInvestmentOperation.setIcon(icon4)
        self.actionShowInvestmentOperation.setObjectName("actionShowInvestmentOperation")
        self.actionShowAccount = QtWidgets.QAction(wdgInvestmentsOperations)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(":/xulpymoney/coins.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionShowAccount.setIcon(icon6)
        self.actionShowAccount.setObjectName("actionShowAccount")
        self.actionShowProduct = QtWidgets.QAction(wdgInvestmentsOperations)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(":/xulpymoney/books.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionShowProduct.setIcon(icon7)
        self.actionShowProduct.setObjectName("actionShowProduct")
        self.actionRangeReport = QtWidgets.QAction(wdgInvestmentsOperations)
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap(":/xulpymoney/eye.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionRangeReport.setIcon(icon8)
        self.actionRangeReport.setObjectName("actionRangeReport")

        self.retranslateUi(wdgInvestmentsOperations)
        self.tab.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(wdgInvestmentsOperations)

    def retranslateUi(self, wdgInvestmentsOperations):
        _translate = QtCore.QCoreApplication.translate
        self.lbl.setText(_translate("wdgInvestmentsOperations", "Investment operations list"))
        self.groupBox.setTitle(_translate("wdgInvestmentsOperations", "List options"))
        self.radYear.setText(_translate("wdgInvestmentsOperations", "Show all investment operations from selected year"))
        self.radYearMonth.setText(_translate("wdgInvestmentsOperations", "Show investment operations from selected year and month"))
        self.cmbFilters.setItemText(0, _translate("wdgInvestmentsOperations", "Show all investment operations"))
        self.cmbFilters.setItemText(1, _translate("wdgInvestmentsOperations", "Show purchasing investment operations"))
        self.cmbFilters.setItemText(2, _translate("wdgInvestmentsOperations", "Show selling investment operations"))
        self.cmbFilters.setItemText(3, _translate("wdgInvestmentsOperations", "Exclude selling and purchasing investment operations"))
        self.tab.setTabText(self.tab.indexOf(self.tab_1), _translate("wdgInvestmentsOperations", "Operations list"))
        self.tab.setTabText(self.tab.indexOf(self.tab_2), _translate("wdgInvestmentsOperations", "Current investment status"))
        self.actionShowInvestment.setText(_translate("wdgInvestmentsOperations", "Show investment"))
        self.actionShowInvestment.setToolTip(_translate("wdgInvestmentsOperations", "Show investment"))
        self.actionShowInvestmentOperation.setText(_translate("wdgInvestmentsOperations", "Show investment operation"))
        self.actionShowInvestmentOperation.setToolTip(_translate("wdgInvestmentsOperations", "Show investment operation"))
        self.actionShowAccount.setText(_translate("wdgInvestmentsOperations", "Show account"))
        self.actionShowAccount.setToolTip(_translate("wdgInvestmentsOperations", "Show account"))
        self.actionShowProduct.setText(_translate("wdgInvestmentsOperations", "Show product"))
        self.actionShowProduct.setToolTip(_translate("wdgInvestmentsOperations", "Show product"))
        self.actionRangeReport.setText(_translate("wdgInvestmentsOperations", "Hide in range report"))
        self.actionRangeReport.setToolTip(_translate("wdgInvestmentsOperations", "Hide in range report"))
from xulpymoney.ui.myqtablewidget import mqtwObjects
from xulpymoney.ui.wdgYear import wdgYear
from xulpymoney.ui.wdgYearMonth import wdgYearMonth
import xulpymoney.images.xulpymoney_rc
