# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'xulpymoney/ui/wdgDividendsReport.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


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
        self.mqtw = mqtwObjects(wdgDividendsReport)
        self.mqtw.setObjectName("mqtw")
        self.verticalLayout.addWidget(self.mqtw)
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
        self.actionEstimationDPSEdit.setText(_translate("wdgDividendsReport", "Update dividend per share"))
        self.actionEstimationDPSEdit.setToolTip(_translate("wdgDividendsReport", "Update dividend per share"))
        self.actionInvestmentReport.setText(_translate("wdgDividendsReport", "Investment report"))
        self.actionInvestmentReport.setToolTip(_translate("wdgDividendsReport", "Investment report"))
        self.actionProductReport.setText(_translate("wdgDividendsReport", "Product report"))
        self.actionProductReport.setToolTip(_translate("wdgDividendsReport", "Product report"))
from xulpymoney.ui.myqtablewidget import mqtwObjects
import xulpymoney.images.xulpymoney_rc
