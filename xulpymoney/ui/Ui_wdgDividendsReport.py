# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/wdgDividendsReport.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_wdgDividendsReport(object):
    def setupUi(self, wdgDividendsReport):
        wdgDividendsReport.setObjectName("wdgDividendsReport")
        wdgDividendsReport.resize(1000, 531)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(wdgDividendsReport.sizePolicy().hasHeightForWidth())
        wdgDividendsReport.setSizePolicy(sizePolicy)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(wdgDividendsReport)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.lbl = QtWidgets.QLabel(wdgDividendsReport)
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
        self.label = QtWidgets.QLabel(wdgDividendsReport)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.spin = QtWidgets.QSpinBox(wdgDividendsReport)
        self.spin.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.spin.setMinimum(1)
        self.spin.setMaximum(3650)
        self.spin.setSingleStep(10)
        self.spin.setProperty("value", 90)
        self.spin.setObjectName("spin")
        self.horizontalLayout.addWidget(self.spin)
        self.cmd = QtWidgets.QPushButton(wdgDividendsReport)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/xulpymoney/alarm_clock.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.cmd.setIcon(icon)
        self.cmd.setObjectName("cmd")
        self.horizontalLayout.addWidget(self.cmd)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.chkInactivas = QtWidgets.QCheckBox(wdgDividendsReport)
        self.chkInactivas.setObjectName("chkInactivas")
        self.verticalLayout.addWidget(self.chkInactivas)
        self.tblInvestments = myQTableWidget(wdgDividendsReport)
        self.tblInvestments.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tblInvestments.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tblInvestments.setAlternatingRowColors(True)
        self.tblInvestments.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tblInvestments.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tblInvestments.setObjectName("tblInvestments")
        self.tblInvestments.setColumnCount(7)
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
        self.tblInvestments.verticalHeader().setVisible(False)
        self.verticalLayout.addWidget(self.tblInvestments)
        self.lblTotal = QtWidgets.QLabel(wdgDividendsReport)
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)
        self.lblTotal.setFont(font)
        self.lblTotal.setAlignment(QtCore.Qt.AlignCenter)
        self.lblTotal.setObjectName("lblTotal")
        self.verticalLayout.addWidget(self.lblTotal)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        self.actionEstimationDPSEdit = QtWidgets.QAction(wdgDividendsReport)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/xulpymoney/coins.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionEstimationDPSEdit.setIcon(icon1)
        self.actionEstimationDPSEdit.setObjectName("actionEstimationDPSEdit")
        self.actionInvestmentReport = QtWidgets.QAction(wdgDividendsReport)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/xulpymoney/report2.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionInvestmentReport.setIcon(icon2)
        self.actionInvestmentReport.setObjectName("actionInvestmentReport")
        self.actionProductReport = QtWidgets.QAction(wdgDividendsReport)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/xulpymoney/kmplot.jpg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionProductReport.setIcon(icon3)
        self.actionProductReport.setObjectName("actionProductReport")

        self.retranslateUi(wdgDividendsReport)
        QtCore.QMetaObject.connectSlotsByName(wdgDividendsReport)

    def retranslateUi(self, wdgDividendsReport):
        _translate = QtCore.QCoreApplication.translate
        self.lbl.setText(_translate("wdgDividendsReport", "Dividends Report"))
        self.label.setText(_translate("wdgDividendsReport", "Dividends per share are with a clock are outdated more than"))
        self.spin.setSuffix(_translate("wdgDividendsReport", " days"))
        self.chkInactivas.setText(_translate("wdgDividendsReport", "Show inactive investments"))
        item = self.tblInvestments.horizontalHeaderItem(0)
        item.setText(_translate("wdgDividendsReport", "Investment"))
        item = self.tblInvestments.horizontalHeaderItem(1)
        item.setText(_translate("wdgDividendsReport", "Bank"))
        item = self.tblInvestments.horizontalHeaderItem(2)
        item.setText(_translate("wdgDividendsReport", "Price"))
        item = self.tblInvestments.horizontalHeaderItem(3)
        item.setText(_translate("wdgDividendsReport", "DPS"))
        item = self.tblInvestments.horizontalHeaderItem(4)
        item.setText(_translate("wdgDividendsReport", "Shares"))
        item = self.tblInvestments.horizontalHeaderItem(5)
        item.setText(_translate("wdgDividendsReport", "Estimated"))
        item = self.tblInvestments.horizontalHeaderItem(6)
        item.setText(_translate("wdgDividendsReport", "% annual dividend"))
        self.actionEstimationDPSEdit.setText(_translate("wdgDividendsReport", "Update dividend per share"))
        self.actionEstimationDPSEdit.setToolTip(_translate("wdgDividendsReport", "Update dividend per share"))
        self.actionInvestmentReport.setText(_translate("wdgDividendsReport", "Investment report"))
        self.actionInvestmentReport.setToolTip(_translate("wdgDividendsReport", "Investment report"))
        self.actionProductReport.setText(_translate("wdgDividendsReport", "Product report"))
        self.actionProductReport.setToolTip(_translate("wdgDividendsReport", "Product report"))

from myqtablewidget import myQTableWidget
import xulpymoney_rc
