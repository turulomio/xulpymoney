# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'xulpymoney/ui/wdgAPR.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_wdgAPR(object):
    def setupUi(self, wdgAPR):
        wdgAPR.setObjectName("wdgAPR")
        wdgAPR.resize(1199, 447)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(wdgAPR.sizePolicy().hasHeightForWidth())
        wdgAPR.setSizePolicy(sizePolicy)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/xulpymoney/history.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        wdgAPR.setWindowIcon(icon)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(wdgAPR)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.lbl = QtWidgets.QLabel(wdgAPR)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.lbl.setFont(font)
        self.lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl.setObjectName("lbl")
        self.verticalLayout.addWidget(self.lbl)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem)
        self.wdgYear = wdgYear(wdgAPR)
        self.wdgYear.setObjectName("wdgYear")
        self.horizontalLayout_4.addWidget(self.wdgYear)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.tab = QtWidgets.QTabWidget(wdgAPR)
        self.tab.setObjectName("tab")
        self.tab_5 = QtWidgets.QWidget()
        self.tab_5.setObjectName("tab_5")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.tab_5)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.mqtw = mqtw(self.tab_5)
        self.mqtw.setObjectName("mqtw")
        self.horizontalLayout.addWidget(self.mqtw)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/xulpymoney/document-edit.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.tab.addTab(self.tab_5, icon1, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.tab_2)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.mqtwReport = mqtw(self.tab_2)
        self.mqtwReport.setObjectName("mqtwReport")
        self.verticalLayout_2.addWidget(self.mqtwReport)
        self.lblReport = QtWidgets.QLabel(self.tab_2)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.lblReport.setFont(font)
        self.lblReport.setText("")
        self.lblReport.setAlignment(QtCore.Qt.AlignCenter)
        self.lblReport.setObjectName("lblReport")
        self.verticalLayout_2.addWidget(self.lblReport)
        self.horizontalLayout_5.addLayout(self.verticalLayout_2)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/xulpymoney/coins.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.tab.addTab(self.tab_2, icon2, "")
        self.verticalLayout.addWidget(self.tab)
        self.horizontalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(wdgAPR)
        self.tab.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(wdgAPR)

    def retranslateUi(self, wdgAPR):
        _translate = QtCore.QCoreApplication.translate
        self.lbl.setText(_translate("wdgAPR", "Assets report"))
        self.tab.setTabText(self.tab.indexOf(self.tab_5), _translate("wdgAPR", "Assets report"))
        self.tab.setTabText(self.tab.indexOf(self.tab_2), _translate("wdgAPR", "Invested report"))
from xulpymoney.ui.myqtablewidget import mqtw
from xulpymoney.ui.wdgYear import wdgYear
import xulpymoney.images.xulpymoney_rc
