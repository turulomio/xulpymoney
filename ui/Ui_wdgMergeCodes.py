# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/wdgMergeCodes.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_wdgMergeCodes(object):
    def setupUi(self, wdgMergeCodes):
        wdgMergeCodes.setObjectName("wdgMergeCodes")
        wdgMergeCodes.resize(1034, 181)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(wdgMergeCodes)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.lbl = QtWidgets.QLabel(wdgMergeCodes)
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
        self.table = myQTableWidget(wdgMergeCodes)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setObjectName("table")
        self.table.setColumnCount(5)
        self.table.setRowCount(2)
        item = QtWidgets.QTableWidgetItem()
        self.table.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.table.setVerticalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        brush = QtGui.QBrush(QtGui.QColor(255, 192, 192))
        brush.setStyle(QtCore.Qt.NoBrush)
        item.setBackground(brush)
        self.table.setItem(1, 0, item)
        self.horizontalLayout.addWidget(self.table)
        self.cmdInterchange = QtWidgets.QToolButton(wdgMergeCodes)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/xulpymoney/transfer.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.cmdInterchange.setIcon(icon)
        self.cmdInterchange.setObjectName("cmdInterchange")
        self.horizontalLayout.addWidget(self.cmdInterchange)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.cmd = QtWidgets.QPushButton(wdgMergeCodes)
        self.cmd.setObjectName("cmd")
        self.verticalLayout.addWidget(self.cmd)
        self.horizontalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(wdgMergeCodes)
        QtCore.QMetaObject.connectSlotsByName(wdgMergeCodes)

    def retranslateUi(self, wdgMergeCodes):
        _translate = QtCore.QCoreApplication.translate
        self.lbl.setText(_translate("wdgMergeCodes", "Merge investments"))
        item = self.table.verticalHeaderItem(0)
        item.setText(_translate("wdgMergeCodes", "Merge data"))
        item = self.table.verticalHeaderItem(1)
        item.setText(_translate("wdgMergeCodes", "Delete data"))
        item = self.table.horizontalHeaderItem(0)
        item.setText(_translate("wdgMergeCodes", "Id"))
        item = self.table.horizontalHeaderItem(1)
        item.setText(_translate("wdgMergeCodes", "Name"))
        item = self.table.horizontalHeaderItem(2)
        item.setText(_translate("wdgMergeCodes", "ISIN"))
        item = self.table.horizontalHeaderItem(3)
        item.setText(_translate("wdgMergeCodes", "Quotes"))
        item = self.table.horizontalHeaderItem(4)
        item.setText(_translate("wdgMergeCodes", "DPS"))
        __sortingEnabled = self.table.isSortingEnabled()
        self.table.setSortingEnabled(False)
        self.table.setSortingEnabled(__sortingEnabled)
        self.cmdInterchange.setText(_translate("wdgMergeCodes", "..."))
        self.cmd.setText(_translate("wdgMergeCodes", "Merge data"))

from myqtablewidget import myQTableWidget
import xulpymoney_rc
