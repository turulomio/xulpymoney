# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/wdgConceptsHistorical.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_wdgConceptsHistorical(object):
    def setupUi(self, wdgConceptsHistorical):
        wdgConceptsHistorical.setObjectName("wdgConceptsHistorical")
        wdgConceptsHistorical.resize(1280, 612)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/xulpymoney/history.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        wdgConceptsHistorical.setWindowIcon(icon)
        self.horizontalLayout = QtWidgets.QHBoxLayout(wdgConceptsHistorical)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.tab = QtWidgets.QTabWidget(wdgConceptsHistorical)
        self.tab.setTabsClosable(True)
        self.tab.setObjectName("tab")
        self.widget = QtWidgets.QWidget()
        self.widget.setObjectName("widget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.table = myQTableWidget(self.widget)
        self.table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.table.setObjectName("table")
        self.table.setColumnCount(14)
        self.table.setRowCount(0)
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
        self.table.setHorizontalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(6, item)
        item = QtWidgets.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(7, item)
        item = QtWidgets.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(8, item)
        item = QtWidgets.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(9, item)
        item = QtWidgets.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(10, item)
        item = QtWidgets.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(11, item)
        item = QtWidgets.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(12, item)
        item = QtWidgets.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(13, item)
        self.table.verticalHeader().setVisible(False)
        self.horizontalLayout_2.addWidget(self.table)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/xulpymoney/hucha.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.tab.addTab(self.widget, icon1, "")
        self.verticalLayout.addWidget(self.tab)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.actionShowMonth = QtWidgets.QAction(wdgConceptsHistorical)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/xulpymoney/search.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionShowMonth.setIcon(icon2)
        self.actionShowMonth.setObjectName("actionShowMonth")
        self.actionShowYear = QtWidgets.QAction(wdgConceptsHistorical)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/xulpymoney/document-preview-archive.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionShowYear.setIcon(icon3)
        self.actionShowYear.setObjectName("actionShowYear")

        self.retranslateUi(wdgConceptsHistorical)
        self.tab.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(wdgConceptsHistorical)

    def retranslateUi(self, wdgConceptsHistorical):
        _translate = QtCore.QCoreApplication.translate
        wdgConceptsHistorical.setWindowTitle(_translate("wdgConceptsHistorical", "Historical concepts report"))
        item = self.table.horizontalHeaderItem(0)
        item.setText(_translate("wdgConceptsHistorical", "Year"))
        item = self.table.horizontalHeaderItem(1)
        item.setText(_translate("wdgConceptsHistorical", "January"))
        item = self.table.horizontalHeaderItem(2)
        item.setText(_translate("wdgConceptsHistorical", "February"))
        item = self.table.horizontalHeaderItem(3)
        item.setText(_translate("wdgConceptsHistorical", "March"))
        item = self.table.horizontalHeaderItem(4)
        item.setText(_translate("wdgConceptsHistorical", "April"))
        item = self.table.horizontalHeaderItem(5)
        item.setText(_translate("wdgConceptsHistorical", "May"))
        item = self.table.horizontalHeaderItem(6)
        item.setText(_translate("wdgConceptsHistorical", "June"))
        item = self.table.horizontalHeaderItem(7)
        item.setText(_translate("wdgConceptsHistorical", "July"))
        item = self.table.horizontalHeaderItem(8)
        item.setText(_translate("wdgConceptsHistorical", "August"))
        item = self.table.horizontalHeaderItem(9)
        item.setText(_translate("wdgConceptsHistorical", "September"))
        item = self.table.horizontalHeaderItem(10)
        item.setText(_translate("wdgConceptsHistorical", "October"))
        item = self.table.horizontalHeaderItem(11)
        item.setText(_translate("wdgConceptsHistorical", "November"))
        item = self.table.horizontalHeaderItem(12)
        item.setText(_translate("wdgConceptsHistorical", "December"))
        item = self.table.horizontalHeaderItem(13)
        item.setText(_translate("wdgConceptsHistorical", "Total"))
        self.tab.setTabText(self.tab.indexOf(self.widget), _translate("wdgConceptsHistorical", "Historical report"))
        self.actionShowMonth.setText(_translate("wdgConceptsHistorical", "Show month operations"))
        self.actionShowMonth.setToolTip(_translate("wdgConceptsHistorical", "Show month operations"))
        self.actionShowYear.setText(_translate("wdgConceptsHistorical", "Show year operations"))
        self.actionShowYear.setToolTip(_translate("wdgConceptsHistorical", "Show year operations"))

from myqtablewidget import myQTableWidget
import xulpymoney_rc