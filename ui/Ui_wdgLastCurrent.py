# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/wdgLastCurrent.ui'
#
# Created by: PyQt5 UI code generator 5.8.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_wdgLastCurrent(object):
    def setupUi(self, wdgLastCurrent):
        wdgLastCurrent.setObjectName("wdgLastCurrent")
        wdgLastCurrent.resize(750, 524)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(wdgLastCurrent)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.lbl = QtWidgets.QLabel(wdgLastCurrent)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.lbl.setFont(font)
        self.lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl.setObjectName("lbl")
        self.verticalLayout.addWidget(self.lbl)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.label = QtWidgets.QLabel(wdgLastCurrent)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.spin = QtWidgets.QSpinBox(wdgLastCurrent)
        self.spin.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.spin.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.spin.setKeyboardTracking(False)
        self.spin.setMinimum(-100)
        self.spin.setMaximum(100)
        self.spin.setSingleStep(5)
        self.spin.setProperty("value", -25)
        self.spin.setObjectName("spin")
        self.horizontalLayout.addWidget(self.spin)
        self.cmd = QtWidgets.QToolButton(wdgLastCurrent)
        self.cmd.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/xulpymoney/button_ok.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.cmd.setIcon(icon)
        self.cmd.setObjectName("cmd")
        self.horizontalLayout.addWidget(self.cmd)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.tblInvestments = myQTableWidget(wdgLastCurrent)
        self.tblInvestments.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tblInvestments.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tblInvestments.setAlternatingRowColors(True)
        self.tblInvestments.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tblInvestments.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tblInvestments.setObjectName("tblInvestments")
        self.tblInvestments.setColumnCount(9)
        self.tblInvestments.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tblInvestments.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblInvestments.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblInvestments.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblInvestments.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblInvestments.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblInvestments.setHorizontalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblInvestments.setHorizontalHeaderItem(6, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblInvestments.setHorizontalHeaderItem(7, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblInvestments.setHorizontalHeaderItem(8, item)
        self.tblInvestments.verticalHeader().setVisible(False)
        self.verticalLayout.addWidget(self.tblInvestments)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem2)
        self.label_2 = QtWidgets.QLabel(wdgLastCurrent)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.cmbSameProduct = QtWidgets.QComboBox(wdgLastCurrent)
        self.cmbSameProduct.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        self.cmbSameProduct.setObjectName("cmbSameProduct")
        self.cmbSameProduct.addItem("")
        self.cmbSameProduct.addItem("")
        self.cmbSameProduct.addItem("")
        self.horizontalLayout_2.addWidget(self.cmbSameProduct)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.wdgIBM = QtWidgets.QWidget(wdgLastCurrent)
        self.wdgIBM.setObjectName("wdgIBM")
        self.verticalLayout.addWidget(self.wdgIBM)
        self.horizontalLayout_3.addLayout(self.verticalLayout)
        self.actionInvestmentReport = QtWidgets.QAction(wdgLastCurrent)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/xulpymoney/bundle.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionInvestmentReport.setIcon(icon1)
        self.actionInvestmentReport.setObjectName("actionInvestmentReport")
        self.actionSortTPCVenta = QtWidgets.QAction(wdgLastCurrent)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/xulpmoney/document-preview.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSortTPCVenta.setIcon(icon2)
        self.actionSortTPCVenta.setObjectName("actionSortTPCVenta")
        self.actionSortTPC = QtWidgets.QAction(wdgLastCurrent)
        self.actionSortTPC.setIcon(icon2)
        self.actionSortTPC.setObjectName("actionSortTPC")
        self.actionSortName = QtWidgets.QAction(wdgLastCurrent)
        self.actionSortName.setIcon(icon2)
        self.actionSortName.setObjectName("actionSortName")
        self.actionSortHour = QtWidgets.QAction(wdgLastCurrent)
        self.actionSortHour.setIcon(icon2)
        self.actionSortHour.setObjectName("actionSortHour")
        self.actionProduct = QtWidgets.QAction(wdgLastCurrent)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/xulpymoney/books.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionProduct.setIcon(icon3)
        self.actionProduct.setObjectName("actionProduct")
        self.actionSortTPCLast = QtWidgets.QAction(wdgLastCurrent)
        self.actionSortTPCLast.setObjectName("actionSortTPCLast")
        self.actionCalculate = QtWidgets.QAction(wdgLastCurrent)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/xulpymoney/tools-wizard.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionCalculate.setIcon(icon4)
        self.actionCalculate.setObjectName("actionCalculate")
        self.actionReinvest = QtWidgets.QAction(wdgLastCurrent)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/xulpymoney/coins.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionReinvest.setIcon(icon5)
        self.actionReinvest.setObjectName("actionReinvest")
        self.actionReinvestCurrent = QtWidgets.QAction(wdgLastCurrent)
        self.actionReinvestCurrent.setIcon(icon5)
        self.actionReinvestCurrent.setObjectName("actionReinvestCurrent")

        self.retranslateUi(wdgLastCurrent)
        QtCore.QMetaObject.connectSlotsByName(wdgLastCurrent)

    def retranslateUi(self, wdgLastCurrent):
        _translate = QtCore.QCoreApplication.translate
        self.lbl.setText(_translate("wdgLastCurrent", "Last operation investments report"))
        self.label.setText(_translate("wdgLastCurrent", "Percentage gains got in last operation investment"))
        self.spin.setSuffix(_translate("wdgLastCurrent", " %"))
        item = self.tblInvestments.horizontalHeaderItem(0)
        item.setText(_translate("wdgLastCurrent", "Investment"))
        item = self.tblInvestments.horizontalHeaderItem(1)
        item.setText(_translate("wdgLastCurrent", "Last operation"))
        item = self.tblInvestments.horizontalHeaderItem(2)
        item.setText(_translate("wdgLastCurrent", "Last shares"))
        item = self.tblInvestments.horizontalHeaderItem(3)
        item.setText(_translate("wdgLastCurrent", "Total shares"))
        item = self.tblInvestments.horizontalHeaderItem(4)
        item.setText(_translate("wdgLastCurrent", "Balance"))
        item = self.tblInvestments.horizontalHeaderItem(5)
        item.setText(_translate("wdgLastCurrent", "Pending"))
        item = self.tblInvestments.horizontalHeaderItem(6)
        item.setText(_translate("wdgLastCurrent", "% Last"))
        item = self.tblInvestments.horizontalHeaderItem(7)
        item.setText(_translate("wdgLastCurrent", "% Invested"))
        item = self.tblInvestments.horizontalHeaderItem(8)
        item.setText(_translate("wdgLastCurrent", "% Selling point"))
        self.label_2.setText(_translate("wdgLastCurrent", "Select the way you want to see results"))
        self.cmbSameProduct.setItemText(0, _translate("wdgLastCurrent", "Show separated investments"))
        self.cmbSameProduct.setItemText(1, _translate("wdgLastCurrent", "Show merging current investment operations"))
        self.cmbSameProduct.setItemText(2, _translate("wdgLastCurrent", "Show merging all investment operations"))
        self.actionInvestmentReport.setText(_translate("wdgLastCurrent", "Investment report"))
        self.actionInvestmentReport.setToolTip(_translate("wdgLastCurrent", "Investment report"))
        self.actionSortTPCVenta.setText(_translate("wdgLastCurrent", "% Selling point"))
        self.actionSortTPCVenta.setToolTip(_translate("wdgLastCurrent", "% Selling point"))
        self.actionSortTPC.setText(_translate("wdgLastCurrent", "% Invested"))
        self.actionSortTPC.setToolTip(_translate("wdgLastCurrent", "% Invested"))
        self.actionSortName.setText(_translate("wdgLastCurrent", "Name"))
        self.actionSortName.setToolTip(_translate("wdgLastCurrent", "Name"))
        self.actionSortHour.setText(_translate("wdgLastCurrent", "Time"))
        self.actionSortHour.setToolTip(_translate("wdgLastCurrent", "Time"))
        self.actionProduct.setText(_translate("wdgLastCurrent", "Product report"))
        self.actionProduct.setToolTip(_translate("wdgLastCurrent", "Product report"))
        self.actionSortTPCLast.setText(_translate("wdgLastCurrent", "% Last operation"))
        self.actionSortTPCLast.setToolTip(_translate("wdgLastCurrent", "% Last operation"))
        self.actionCalculate.setText(_translate("wdgLastCurrent", "Calculate reinvest price"))
        self.actionCalculate.setToolTip(_translate("wdgLastCurrent", "Calculate reinvest price"))
        self.actionReinvest.setText(_translate("wdgLastCurrent", "Reinvest"))
        self.actionReinvest.setToolTip(_translate("wdgLastCurrent", "Reinvest"))
        self.actionReinvestCurrent.setText(_translate("wdgLastCurrent", "Simulate reinvestment at product current price"))
        self.actionReinvestCurrent.setToolTip(_translate("wdgLastCurrent", "Simulate reinvestment at product current price"))

from myqtablewidget import myQTableWidget
import xulpymoney_rc