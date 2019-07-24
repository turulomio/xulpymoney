# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'xulpymoney/ui/wdgSimulationsAdd.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_wdgSimulationsAdd(object):
    def setupUi(self, wdgSimulationsAdd):
        wdgSimulationsAdd.setObjectName("wdgSimulationsAdd")
        wdgSimulationsAdd.resize(782, 573)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(wdgSimulationsAdd)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.lblTitulo = QtWidgets.QLabel(wdgSimulationsAdd)
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
        self.lblPixmap = QtWidgets.QLabel(wdgSimulationsAdd)
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
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.cmbSimulationTypes = QtWidgets.QComboBox(wdgSimulationsAdd)
        self.cmbSimulationTypes.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        self.cmbSimulationTypes.setObjectName("cmbSimulationTypes")
        self.verticalLayout_2.addWidget(self.cmbSimulationTypes)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.groupBox = QtWidgets.QGroupBox(wdgSimulationsAdd)
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.groupBox)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.wdgStarting = wdgDatetime(self.groupBox)
        self.wdgStarting.setObjectName("wdgStarting")
        self.horizontalLayout.addWidget(self.wdgStarting)
        self.horizontalLayout_3.addWidget(self.groupBox)
        self.groupBox_2 = QtWidgets.QGroupBox(wdgSimulationsAdd)
        self.groupBox_2.setObjectName("groupBox_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.groupBox_2)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.wdgEnding = wdgDatetime(self.groupBox_2)
        self.wdgEnding.setObjectName("wdgEnding")
        self.horizontalLayout_2.addWidget(self.wdgEnding)
        self.horizontalLayout_3.addWidget(self.groupBox_2)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.buttonbox = QtWidgets.QDialogButtonBox(wdgSimulationsAdd)
        self.buttonbox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonbox.setObjectName("buttonbox")
        self.verticalLayout_2.addWidget(self.buttonbox)
        self.horizontalLayout_5.addLayout(self.verticalLayout_2)

        self.retranslateUi(wdgSimulationsAdd)
        QtCore.QMetaObject.connectSlotsByName(wdgSimulationsAdd)

    def retranslateUi(self, wdgSimulationsAdd):
        _translate = QtCore.QCoreApplication.translate
        wdgSimulationsAdd.setWindowTitle(_translate("wdgSimulationsAdd", "Form"))
        self.lblTitulo.setText(_translate("wdgSimulationsAdd", "Create new simulation"))
        self.groupBox.setTitle(_translate("wdgSimulationsAdd", "Start date and time"))
        self.groupBox_2.setTitle(_translate("wdgSimulationsAdd", "End date and time"))
from xulpymoney.ui.wdgDatetime import wdgDatetime
import xulpymoney.images.xulpymoney_rc
