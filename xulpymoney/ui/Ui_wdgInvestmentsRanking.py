# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'xulpymoney/ui/wdgInvestmentsRanking.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_wdgInvestmentsRanking(object):
    def setupUi(self, wdgInvestmentsRanking):
        wdgInvestmentsRanking.setObjectName("wdgInvestmentsRanking")
        wdgInvestmentsRanking.resize(750, 524)
        self.horizontalLayout = QtWidgets.QHBoxLayout(wdgInvestmentsRanking)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.lbl = QtWidgets.QLabel(wdgInvestmentsRanking)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.lbl.setFont(font)
        self.lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl.setObjectName("lbl")
        self.verticalLayout.addWidget(self.lbl)
        self.tab = QtWidgets.QTabWidget(wdgInvestmentsRanking)
        self.tab.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tab.setObjectName("tab")
        self.tab_ = QtWidgets.QWidget()
        self.tab_.setObjectName("tab_")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.tab_)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.tblCurrentOperations = myQTableWidget(self.tab_)
        self.tblCurrentOperations.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tblCurrentOperations.setAlternatingRowColors(True)
        self.tblCurrentOperations.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tblCurrentOperations.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tblCurrentOperations.setObjectName("tblCurrentOperations")
        self.tblCurrentOperations.setColumnCount(0)
        self.tblCurrentOperations.setRowCount(0)
        self.horizontalLayout_3.addWidget(self.tblCurrentOperations)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/xulpymoney/crown.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.tab.addTab(self.tab_, icon, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.tab_2)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.tblOperations = myQTableWidget(self.tab_2)
        self.tblOperations.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tblOperations.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tblOperations.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tblOperations.setObjectName("tblOperations")
        self.tblOperations.setColumnCount(0)
        self.tblOperations.setRowCount(0)
        self.horizontalLayout_2.addWidget(self.tblOperations)
        self.tab.addTab(self.tab_2, icon, "")
        self.verticalLayout.addWidget(self.tab)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.actionSameProduct = QtWidgets.QAction(wdgInvestmentsRanking)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/xulpymoney/bundle.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSameProduct.setIcon(icon1)
        self.actionSameProduct.setObjectName("actionSameProduct")
        self.actionSameProductFIFO = QtWidgets.QAction(wdgInvestmentsRanking)
        self.actionSameProductFIFO.setIcon(icon1)
        self.actionSameProductFIFO.setObjectName("actionSameProductFIFO")
        self.actionProduct = QtWidgets.QAction(wdgInvestmentsRanking)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/xulpymoney/books.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionProduct.setIcon(icon2)
        self.actionProduct.setObjectName("actionProduct")

        self.retranslateUi(wdgInvestmentsRanking)
        self.tab.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(wdgInvestmentsRanking)

    def retranslateUi(self, wdgInvestmentsRanking):
        _translate = QtCore.QCoreApplication.translate
        self.lbl.setText(_translate("wdgInvestmentsRanking", "Investments ranking"))
        self.tab.setTabText(self.tab.indexOf(self.tab_), _translate("wdgInvestmentsRanking", "With same product merging current operations"))
        self.tab.setTabText(self.tab.indexOf(self.tab_2), _translate("wdgInvestmentsRanking", "With same product merging operations"))
        self.actionSameProduct.setText(_translate("wdgInvestmentsRanking", "Same product Investments merging current operations"))
        self.actionSameProduct.setToolTip(_translate("wdgInvestmentsRanking", "Same product Investments merging current operations"))
        self.actionSameProductFIFO.setText(_translate("wdgInvestmentsRanking", "Same product Investments merging operations"))
        self.actionSameProductFIFO.setToolTip(_translate("wdgInvestmentsRanking", "Same product Investments merging operations"))
        self.actionProduct.setText(_translate("wdgInvestmentsRanking", "Product report"))
        self.actionProduct.setToolTip(_translate("wdgInvestmentsRanking", "Product report"))
from xulpymoney.ui.myqtablewidget import myQTableWidget
import xulpymoney.images.xulpymoney_rc
