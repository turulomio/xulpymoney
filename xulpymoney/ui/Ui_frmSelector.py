# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'xulpymoney/ui/frmSelector.ui'
#
# Created by: PyQt5 UI code generator 5.12.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_frmSelector(object):
    def setupUi(self, frmSelector):
        frmSelector.setObjectName("frmSelector")
        frmSelector.resize(687, 352)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/xulpymoney/books.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        frmSelector.setWindowIcon(icon)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(frmSelector)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.lbl = QtWidgets.QLabel(frmSelector)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.lbl.setFont(font)
        self.lbl.setStyleSheet("color: rgb(0, 192, 0);")
        self.lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.lbl.setObjectName("lbl")
        self.verticalLayout_2.addWidget(self.lbl)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tblSelected = QtWidgets.QTableWidget(frmSelector)
        self.tblSelected.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tblSelected.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tblSelected.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tblSelected.setObjectName("tblSelected")
        self.tblSelected.setColumnCount(2)
        self.tblSelected.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tblSelected.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblSelected.setHorizontalHeaderItem(1, item)
        self.tblSelected.horizontalHeader().setStretchLastSection(True)
        self.tblSelected.verticalHeader().setVisible(False)
        self.horizontalLayout.addWidget(self.tblSelected)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.cmdUp = QtWidgets.QToolButton(frmSelector)
        self.cmdUp.setObjectName("cmdUp")
        self.verticalLayout.addWidget(self.cmdUp)
        self.cmdRight = QtWidgets.QToolButton(frmSelector)
        self.cmdRight.setObjectName("cmdRight")
        self.verticalLayout.addWidget(self.cmdRight)
        self.cmdLeft = QtWidgets.QToolButton(frmSelector)
        self.cmdLeft.setObjectName("cmdLeft")
        self.verticalLayout.addWidget(self.cmdLeft)
        self.cmdDown = QtWidgets.QToolButton(frmSelector)
        self.cmdDown.setObjectName("cmdDown")
        self.verticalLayout.addWidget(self.cmdDown)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.tbl = QtWidgets.QTableWidget(frmSelector)
        self.tbl.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tbl.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tbl.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tbl.setObjectName("tbl")
        self.tbl.setColumnCount(2)
        self.tbl.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tbl.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tbl.setHorizontalHeaderItem(1, item)
        self.tbl.horizontalHeader().setStretchLastSection(True)
        self.tbl.verticalHeader().setVisible(False)
        self.horizontalLayout.addWidget(self.tbl)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.cmd = QtWidgets.QPushButton(frmSelector)
        self.cmd.setObjectName("cmd")
        self.verticalLayout_2.addWidget(self.cmd)
        self.horizontalLayout_2.addLayout(self.verticalLayout_2)

        self.retranslateUi(frmSelector)
        QtCore.QMetaObject.connectSlotsByName(frmSelector)

    def retranslateUi(self, frmSelector):
        _translate = QtCore.QCoreApplication.translate
        self.lbl.setText(_translate("frmSelector", "Investment"))
        item = self.tblSelected.horizontalHeaderItem(0)
        item.setText(_translate("frmSelector", "Id"))
        item = self.tblSelected.horizontalHeaderItem(1)
        item.setText(_translate("frmSelector", "Selected elements"))
        self.cmdUp.setText(_translate("frmSelector", "^"))
        self.cmdRight.setText(_translate("frmSelector", ">"))
        self.cmdLeft.setText(_translate("frmSelector", "<"))
        self.cmdDown.setText(_translate("frmSelector", "V"))
        item = self.tbl.horizontalHeaderItem(0)
        item.setText(_translate("frmSelector", "Id"))
        item = self.tbl.horizontalHeaderItem(1)
        item.setText(_translate("frmSelector", "Elements"))
        self.cmd.setText(_translate("frmSelector", "Accept selection"))


import xulpymoney.images.xulpymoney_rc
