# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/frmSettings.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_frmSettings(object):
    def setupUi(self, frmSettings):
        frmSettings.setObjectName("frmSettings")
        frmSettings.setWindowModality(QtCore.Qt.WindowModal)
        frmSettings.resize(567, 428)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/xulpymoney/save.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        frmSettings.setWindowIcon(icon)
        frmSettings.setSizeGripEnabled(True)
        frmSettings.setModal(True)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout(frmSettings)
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.lblTitulo = QtWidgets.QLabel(frmSettings)
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
        self.lblPixmap = QtWidgets.QLabel(frmSettings)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblPixmap.sizePolicy().hasHeightForWidth())
        self.lblPixmap.setSizePolicy(sizePolicy)
        self.lblPixmap.setMinimumSize(QtCore.QSize(48, 48))
        self.lblPixmap.setMaximumSize(QtCore.QSize(48, 48))
        self.lblPixmap.setPixmap(QtGui.QPixmap(":/xulpymoney/configure.png"))
        self.lblPixmap.setScaledContents(True)
        self.lblPixmap.setAlignment(QtCore.Qt.AlignCenter)
        self.lblPixmap.setObjectName("lblPixmap")
        self.horizontalLayout_4.addWidget(self.lblPixmap)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.groupBox_2 = QtWidgets.QGroupBox(frmSettings)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy)
        self.groupBox_2.setObjectName("groupBox_2")
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout(self.groupBox_2)
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.label_4 = QtWidgets.QLabel(self.groupBox_2)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_9.addWidget(self.label_4)
        self.cmbLanguages = QtWidgets.QComboBox(self.groupBox_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbLanguages.sizePolicy().hasHeightForWidth())
        self.cmbLanguages.setSizePolicy(sizePolicy)
        self.cmbLanguages.setObjectName("cmbLanguages")
        self.horizontalLayout_9.addWidget(self.cmbLanguages)
        self.verticalLayout_4.addLayout(self.horizontalLayout_9)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.groupBox_2)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.cmbCurrencies = QtWidgets.QComboBox(self.groupBox_2)
        self.cmbCurrencies.setObjectName("cmbCurrencies")
        self.horizontalLayout.addWidget(self.cmbCurrencies)
        self.verticalLayout_4.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtWidgets.QLabel(self.groupBox_2)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.cmbZones = QtWidgets.QComboBox(self.groupBox_2)
        self.cmbZones.setObjectName("cmbZones")
        self.horizontalLayout_2.addWidget(self.cmbZones)
        self.verticalLayout_4.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_3 = QtWidgets.QLabel(self.groupBox_2)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_3.addWidget(self.label_3)
        self.cmbIndex = QtWidgets.QComboBox(self.groupBox_2)
        self.cmbIndex.setObjectName("cmbIndex")
        self.horizontalLayout_3.addWidget(self.cmbIndex)
        self.verticalLayout_4.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_5 = QtWidgets.QLabel(self.groupBox_2)
        self.label_5.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_5.addWidget(self.label_5)
        self.spnDividendPercentage = QtWidgets.QDoubleSpinBox(self.groupBox_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.spnDividendPercentage.sizePolicy().hasHeightForWidth())
        self.spnDividendPercentage.setSizePolicy(sizePolicy)
        self.spnDividendPercentage.setMinimumSize(QtCore.QSize(200, 0))
        self.spnDividendPercentage.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.spnDividendPercentage.setDecimals(2)
        self.spnDividendPercentage.setSingleStep(0.1)
        self.spnDividendPercentage.setProperty("value", 21.0)
        self.spnDividendPercentage.setObjectName("spnDividendPercentage")
        self.horizontalLayout_5.addWidget(self.spnDividendPercentage)
        self.verticalLayout_4.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label_6 = QtWidgets.QLabel(self.groupBox_2)
        self.label_6.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_6.addWidget(self.label_6)
        self.spnGainsPercentaje = QtWidgets.QDoubleSpinBox(self.groupBox_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.spnGainsPercentaje.sizePolicy().hasHeightForWidth())
        self.spnGainsPercentaje.setSizePolicy(sizePolicy)
        self.spnGainsPercentaje.setMinimumSize(QtCore.QSize(200, 0))
        self.spnGainsPercentaje.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.spnGainsPercentaje.setDecimals(2)
        self.spnGainsPercentaje.setSingleStep(0.1)
        self.spnGainsPercentaje.setProperty("value", 21.0)
        self.spnGainsPercentaje.setObjectName("spnGainsPercentaje")
        self.horizontalLayout_6.addWidget(self.spnGainsPercentaje)
        self.verticalLayout_4.addLayout(self.horizontalLayout_6)
        self.chkGainsYear = QtWidgets.QCheckBox(self.groupBox_2)
        self.chkGainsYear.setObjectName("chkGainsYear")
        self.verticalLayout_4.addWidget(self.chkGainsYear)
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.label_7 = QtWidgets.QLabel(self.groupBox_2)
        self.label_7.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_7.setObjectName("label_7")
        self.horizontalLayout_10.addWidget(self.label_7)
        self.spnGainsPercentajeBelow = QtWidgets.QDoubleSpinBox(self.groupBox_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.spnGainsPercentajeBelow.sizePolicy().hasHeightForWidth())
        self.spnGainsPercentajeBelow.setSizePolicy(sizePolicy)
        self.spnGainsPercentajeBelow.setMinimumSize(QtCore.QSize(200, 0))
        self.spnGainsPercentajeBelow.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.spnGainsPercentajeBelow.setDecimals(2)
        self.spnGainsPercentajeBelow.setSingleStep(0.1)
        self.spnGainsPercentajeBelow.setProperty("value", 50.0)
        self.spnGainsPercentajeBelow.setObjectName("spnGainsPercentajeBelow")
        self.horizontalLayout_10.addWidget(self.spnGainsPercentajeBelow)
        self.verticalLayout_4.addLayout(self.horizontalLayout_10)
        self.horizontalLayout_8.addLayout(self.verticalLayout_4)
        self.verticalLayout.addWidget(self.groupBox_2)
        self.buttonbox = QtWidgets.QDialogButtonBox(frmSettings)
        self.buttonbox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonbox.setObjectName("buttonbox")
        self.verticalLayout.addWidget(self.buttonbox)
        self.horizontalLayout_7.addLayout(self.verticalLayout)

        self.retranslateUi(frmSettings)
        QtCore.QMetaObject.connectSlotsByName(frmSettings)

    def retranslateUi(self, frmSettings):
        _translate = QtCore.QCoreApplication.translate
        frmSettings.setWindowTitle(_translate("frmSettings", "Xulpymoney settings"))
        self.lblTitulo.setText(_translate("frmSettings", "Xulpymoney settings"))
        self.groupBox_2.setTitle(_translate("frmSettings", "User settings"))
        self.label_4.setText(_translate("frmSettings", "Select a language"))
        self.label.setText(_translate("frmSettings", "Main currency"))
        self.label_2.setText(_translate("frmSettings", "User datetime zone"))
        self.label_3.setText(_translate("frmSettings", "Benchmark"))
        self.label_5.setText(_translate("frmSettings", "Dividend withholding percentage"))
        self.spnDividendPercentage.setSuffix(_translate("frmSettings", " %"))
        self.label_6.setText(_translate("frmSettings", "Tax gain percentage"))
        self.spnGainsPercentaje.setSuffix(_translate("frmSettings", " %"))
        self.chkGainsYear.setText(_translate("frmSettings", "Capital gains over a year have a different tax"))
        self.label_7.setText(_translate("frmSettings", "Tax gain percentage below a year"))
        self.spnGainsPercentajeBelow.setSuffix(_translate("frmSettings", " %"))

import xulpymoney_rc
