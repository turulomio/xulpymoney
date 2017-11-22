# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/wdgOrders.ui'
#
# Created by: PyQt5 UI code generator 5.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_wdgOrders(object):
    def setupUi(self, wdgOrders):
        wdgOrders.setObjectName("wdgOrders")
        wdgOrders.resize(656, 497)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/xulpymoney/bank.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        wdgOrders.setWindowIcon(icon)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(wdgOrders)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.lbl = QtWidgets.QLabel(wdgOrders)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.lbl.setFont(font)
        self.lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl.setObjectName("lbl")
        self.verticalLayout_2.addWidget(self.lbl)
        self.tabWidget = QtWidgets.QTabWidget(wdgOrders)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.tab)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.wdgYear = wdgYear(self.tab)
        self.wdgYear.setObjectName("wdgYear")
        self.horizontalLayout.addWidget(self.wdgYear)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem2)
        self.cmbMode = QtWidgets.QComboBox(self.tab)
        self.cmbMode.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        self.cmbMode.setObjectName("cmbMode")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/xulpymoney/new.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.cmbMode.addItem(icon1, "")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/xulpymoney/expired.jpg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.cmbMode.addItem(icon2, "")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/xulpymoney/tools-wizard.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.cmbMode.addItem(icon3, "")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/xulpymoney/eye.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.cmbMode.addItem(icon4, "")
        self.horizontalLayout_2.addWidget(self.cmbMode)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem3)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.tblOrders = myQTableWidget(self.tab)
        self.tblOrders.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tblOrders.setAlternatingRowColors(True)
        self.tblOrders.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tblOrders.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tblOrders.setObjectName("tblOrders")
        self.tblOrders.setColumnCount(0)
        self.tblOrders.setRowCount(0)
        self.tblOrders.verticalHeader().setVisible(False)
        self.verticalLayout.addWidget(self.tblOrders)
        self.horizontalLayout_3.addLayout(self.verticalLayout)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/xulpymoney/editar.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.tabWidget.addTab(self.tab, icon5, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.tab_2)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.tblSellingPoints = myQTableWidget(self.tab_2)
        self.tblSellingPoints.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tblSellingPoints.setAlternatingRowColors(True)
        self.tblSellingPoints.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tblSellingPoints.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tblSellingPoints.setObjectName("tblSellingPoints")
        self.tblSellingPoints.setColumnCount(0)
        self.tblSellingPoints.setRowCount(0)
        self.tblSellingPoints.verticalHeader().setVisible(False)
        self.horizontalLayout_5.addWidget(self.tblSellingPoints)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(":/xulpymoney/today.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.tabWidget.addTab(self.tab_2, icon6, "")
        self.verticalLayout_2.addWidget(self.tabWidget)
        self.horizontalLayout_4.addLayout(self.verticalLayout_2)
        self.actionOrderNew = QtWidgets.QAction(wdgOrders)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(":/xulpymoney/add.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionOrderNew.setIcon(icon7)
        self.actionOrderNew.setObjectName("actionOrderNew")
        self.actionOrderDelete = QtWidgets.QAction(wdgOrders)
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap(":/xulpymoney/button_cancel.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionOrderDelete.setIcon(icon8)
        self.actionOrderDelete.setObjectName("actionOrderDelete")
        self.actionOrderEdit = QtWidgets.QAction(wdgOrders)
        self.actionOrderEdit.setIcon(icon5)
        self.actionOrderEdit.setObjectName("actionOrderEdit")
        self.actionExecute = QtWidgets.QAction(wdgOrders)
        self.actionExecute.setIcon(icon3)
        self.actionExecute.setObjectName("actionExecute")
        self.actionShowReinvest = QtWidgets.QAction(wdgOrders)
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap(":/xulpymoney/gafas.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionShowReinvest.setIcon(icon9)
        self.actionShowReinvest.setObjectName("actionShowReinvest")
        self.actionShowReinvestSameProduct = QtWidgets.QAction(wdgOrders)
        self.actionShowReinvestSameProduct.setIcon(icon9)
        self.actionShowReinvestSameProduct.setObjectName("actionShowReinvestSameProduct")

        self.retranslateUi(wdgOrders)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(wdgOrders)

    def retranslateUi(self, wdgOrders):
        _translate = QtCore.QCoreApplication.translate
        self.lbl.setText(_translate("wdgOrders", "Orders list"))
        self.cmbMode.setItemText(0, _translate("wdgOrders", "Show current orders"))
        self.cmbMode.setItemText(1, _translate("wdgOrders", "Show expired orders"))
        self.cmbMode.setItemText(2, _translate("wdgOrders", "Show executed orders"))
        self.cmbMode.setItemText(3, _translate("wdgOrders", "Show all"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("wdgOrders", "Order annotations list"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("wdgOrders", "Selling point orders"))
        self.actionOrderNew.setText(_translate("wdgOrders", "New purchase order"))
        self.actionOrderNew.setToolTip(_translate("wdgOrders", "New purchase order"))
        self.actionOrderDelete.setText(_translate("wdgOrders", "Delete purchase order"))
        self.actionOrderDelete.setToolTip(_translate("wdgOrders", "Delete purchase order"))
        self.actionOrderEdit.setText(_translate("wdgOrders", "Edit purchase order"))
        self.actionOrderEdit.setToolTip(_translate("wdgOrders", "Edit purchase order"))
        self.actionExecute.setText(_translate("wdgOrders", "Execute order"))
        self.actionExecute.setToolTip(_translate("wdgOrders", "Execute order"))
        self.actionShowReinvest.setText(_translate("wdgOrders", "Show reinvest simulation"))
        self.actionShowReinvest.setToolTip(_translate("wdgOrders", "Show reinvest simulation"))
        self.actionShowReinvestSameProduct.setText(_translate("wdgOrders", "Show reinvest simulation all investments with same product"))
        self.actionShowReinvestSameProduct.setToolTip(_translate("wdgOrders", "Show reinvest simulation all investments with same product"))

from myqtablewidget import myQTableWidget
from wdgYear import wdgYear
import xulpymoney_rc
