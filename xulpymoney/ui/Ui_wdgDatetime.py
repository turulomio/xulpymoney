# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'xulpymoney/ui/wdgDatetime.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_wdgDatetime(object):
    def setupUi(self, wdgDatetime):
        wdgDatetime.setObjectName("wdgDatetime")
        wdgDatetime.resize(439, 254)
        self.horizontalLayout = QtWidgets.QHBoxLayout(wdgDatetime)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.grp = QtWidgets.QGroupBox(wdgDatetime)
        self.grp.setObjectName("grp")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.grp)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.teDate = QtWidgets.QCalendarWidget(self.grp)
        self.teDate.setFirstDayOfWeek(QtCore.Qt.Monday)
        self.teDate.setVerticalHeaderFormat(QtWidgets.QCalendarWidget.NoVerticalHeader)
        self.teDate.setObjectName("teDate")
        self.horizontalLayout_2.addWidget(self.teDate)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.teTime = QtWidgets.QTimeEdit(self.grp)
        self.teTime.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.teTime.setObjectName("teTime")
        self.verticalLayout.addWidget(self.teTime)
        self.teMicroseconds = QtWidgets.QSpinBox(self.grp)
        self.teMicroseconds.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.teMicroseconds.setMaximum(999999)
        self.teMicroseconds.setObjectName("teMicroseconds")
        self.verticalLayout.addWidget(self.teMicroseconds)
        self.cmbZone = QtWidgets.QComboBox(self.grp)
        self.cmbZone.setObjectName("cmbZone")
        self.verticalLayout.addWidget(self.cmbZone)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.line = QtWidgets.QFrame(self.grp)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout_2.addWidget(self.line)
        self.cmdNow = QtWidgets.QPushButton(self.grp)
        self.cmdNow.setObjectName("cmdNow")
        self.verticalLayout_2.addWidget(self.cmdNow)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem1)
        self.horizontalLayout_2.addLayout(self.verticalLayout_2)
        self.verticalLayout_4.addLayout(self.horizontalLayout_2)
        self.horizontalLayout.addWidget(self.grp)

        self.retranslateUi(wdgDatetime)
        QtCore.QMetaObject.connectSlotsByName(wdgDatetime)

    def retranslateUi(self, wdgDatetime):
        _translate = QtCore.QCoreApplication.translate
        self.grp.setTitle(_translate("wdgDatetime", "Select a datetime"))
        self.teTime.setToolTip(_translate("wdgDatetime", "Select a time"))
        self.teTime.setDisplayFormat(_translate("wdgDatetime", "HH:mm:ss"))
        self.teMicroseconds.setToolTip(_translate("wdgDatetime", "Select microseconds"))
        self.cmdNow.setToolTip(_translate("wdgDatetime", "Set current time"))
        self.cmdNow.setText(_translate("wdgDatetime", "Now"))

