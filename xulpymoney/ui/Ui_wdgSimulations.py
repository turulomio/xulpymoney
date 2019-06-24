# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'xulpymoney/ui/wdgSimulations.ui'
#
# Created by: PyQt5 UI code generator 5.12.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_wdgSimulations(object):
    def setupUi(self, wdgSimulations):
        wdgSimulations.setObjectName("wdgSimulations")
        wdgSimulations.resize(1048, 499)
        self.horizontalLayout = QtWidgets.QHBoxLayout(wdgSimulations)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.lblTitulo = QtWidgets.QLabel(wdgSimulations)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.lblTitulo.setFont(font)
        self.lblTitulo.setAlignment(QtCore.Qt.AlignCenter)
        self.lblTitulo.setObjectName("lblTitulo")
        self.verticalLayout.addWidget(self.lblTitulo)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem)
        self.lblPixmap = QtWidgets.QLabel(wdgSimulations)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblPixmap.sizePolicy().hasHeightForWidth())
        self.lblPixmap.setSizePolicy(sizePolicy)
        self.lblPixmap.setMinimumSize(QtCore.QSize(48, 48))
        self.lblPixmap.setMaximumSize(QtCore.QSize(48, 48))
        self.lblPixmap.setPixmap(QtGui.QPixmap(":/xulpymoney/replication.png"))
        self.lblPixmap.setScaledContents(True)
        self.lblPixmap.setAlignment(QtCore.Qt.AlignCenter)
        self.lblPixmap.setObjectName("lblPixmap")
        self.horizontalLayout_4.addWidget(self.lblPixmap)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.groupBox = QtWidgets.QGroupBox(wdgSimulations)
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.groupBox)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.tblSimulations = myQTableWidget(self.groupBox)
        self.tblSimulations.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tblSimulations.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tblSimulations.setObjectName("tblSimulations")
        self.tblSimulations.setColumnCount(0)
        self.tblSimulations.setRowCount(0)
        self.horizontalLayout_2.addWidget(self.tblSimulations)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.cmdCreate = QtWidgets.QPushButton(self.groupBox)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/xulpymoney/add.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.cmdCreate.setIcon(icon)
        self.cmdCreate.setObjectName("cmdCreate")
        self.verticalLayout_2.addWidget(self.cmdCreate)
        self.cmdDelete = QtWidgets.QPushButton(self.groupBox)
        self.cmdDelete.setEnabled(False)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/xulpymoney/list-remove.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.cmdDelete.setIcon(icon1)
        self.cmdDelete.setObjectName("cmdDelete")
        self.verticalLayout_2.addWidget(self.cmdDelete)
        self.cmdConnect = QtWidgets.QPushButton(self.groupBox)
        self.cmdConnect.setEnabled(False)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/xulpymoney/transfer.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.cmdConnect.setIcon(icon2)
        self.cmdConnect.setObjectName("cmdConnect")
        self.verticalLayout_2.addWidget(self.cmdConnect)
        self.horizontalLayout_2.addLayout(self.verticalLayout_2)
        self.horizontalLayout_3.addLayout(self.horizontalLayout_2)
        self.verticalLayout.addWidget(self.groupBox)
        self.horizontalLayout.addLayout(self.verticalLayout)

        self.retranslateUi(wdgSimulations)
        QtCore.QMetaObject.connectSlotsByName(wdgSimulations)

    def retranslateUi(self, wdgSimulations):
        _translate = QtCore.QCoreApplication.translate
        wdgSimulations.setWindowTitle(_translate("wdgSimulations", "Form"))
        self.lblTitulo.setText(_translate("wdgSimulations", "Xulpymoney simulations"))
        self.groupBox.setTitle(_translate("wdgSimulations", "Simulations"))
        self.cmdCreate.setText(_translate("wdgSimulations", "Create"))
        self.cmdDelete.setText(_translate("wdgSimulations", "Delete"))
        self.cmdConnect.setText(_translate("wdgSimulations", "Connect"))


from xulpymoney.ui.myqtablewidget import myQTableWidget
import xulpymoney.images.xulpymoney_rc
