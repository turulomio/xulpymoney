# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'xulpymoney/ui/wdgDisReinvest.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_wdgDisReinvest(object):
    def setupUi(self, wdgDisReinvest):
        wdgDisReinvest.setObjectName("wdgDisReinvest")
        wdgDisReinvest.resize(1102, 806)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/xulpymoney/tools-wizard.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        wdgDisReinvest.setWindowIcon(icon)
        self.horizontalLayout_21 = QtWidgets.QHBoxLayout(wdgDisReinvest)
        self.horizontalLayout_21.setObjectName("horizontalLayout_21")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.lblTitulo = QtWidgets.QLabel(wdgDisReinvest)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.lblTitulo.setFont(font)
        self.lblTitulo.setStyleSheet("color: rgb(0, 128, 0);")
        self.lblTitulo.setAlignment(QtCore.Qt.AlignCenter)
        self.lblTitulo.setObjectName("lblTitulo")
        self.verticalLayout_3.addWidget(self.lblTitulo)
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem)
        self.grp = QtWidgets.QGroupBox(wdgDisReinvest)
        self.grp.setTitle("")
        self.grp.setObjectName("grp")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout(self.grp)
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.radRe = QtWidgets.QRadioButton(self.grp)
        self.radRe.setChecked(True)
        self.radRe.setObjectName("radRe")
        self.horizontalLayout.addWidget(self.radRe)
        self.radDes = QtWidgets.QRadioButton(self.grp)
        self.radDes.setChecked(False)
        self.radDes.setObjectName("radDes")
        self.horizontalLayout.addWidget(self.radDes)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.groupBox = QtWidgets.QGroupBox(self.grp)
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.groupBox)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_12 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        self.lblSimulacion = QtWidgets.QLabel(self.groupBox)
        self.lblSimulacion.setObjectName("lblSimulacion")
        self.horizontalLayout_12.addWidget(self.lblSimulacion)
        self.txtSimulacion = myQLineEdit(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.txtSimulacion.sizePolicy().hasHeightForWidth())
        self.txtSimulacion.setSizePolicy(sizePolicy)
        self.txtSimulacion.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.txtSimulacion.setObjectName("txtSimulacion")
        self.horizontalLayout_12.addWidget(self.txtSimulacion)
        self.verticalLayout_2.addLayout(self.horizontalLayout_12)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.lblValor = QtWidgets.QLabel(self.groupBox)
        self.lblValor.setObjectName("lblValor")
        self.horizontalLayout_5.addWidget(self.lblValor)
        self.txtValorAccion = myQLineEdit(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.txtValorAccion.sizePolicy().hasHeightForWidth())
        self.txtValorAccion.setSizePolicy(sizePolicy)
        self.txtValorAccion.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.txtValorAccion.setObjectName("txtValorAccion")
        self.horizontalLayout_5.addWidget(self.txtValorAccion)
        self.verticalLayout_2.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_3 = QtWidgets.QLabel(self.groupBox)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_4.addWidget(self.label_3)
        self.txtComision = myQLineEdit(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.txtComision.sizePolicy().hasHeightForWidth())
        self.txtComision.setSizePolicy(sizePolicy)
        self.txtComision.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.txtComision.setObjectName("txtComision")
        self.horizontalLayout_4.addWidget(self.txtComision)
        self.verticalLayout_2.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.label_5 = QtWidgets.QLabel(self.groupBox)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_11.addWidget(self.label_5)
        self.txtAcciones = myQLineEdit(self.groupBox)
        self.txtAcciones.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.txtAcciones.sizePolicy().hasHeightForWidth())
        self.txtAcciones.setSizePolicy(sizePolicy)
        self.txtAcciones.setText("")
        self.txtAcciones.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.txtAcciones.setObjectName("txtAcciones")
        self.horizontalLayout_11.addWidget(self.txtAcciones)
        self.verticalLayout_2.addLayout(self.horizontalLayout_11)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_3.addWidget(self.label_2)
        self.txtImporte = myQLineEdit(self.groupBox)
        self.txtImporte.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.txtImporte.sizePolicy().hasHeightForWidth())
        self.txtImporte.setSizePolicy(sizePolicy)
        self.txtImporte.setText("")
        self.txtImporte.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.txtImporte.setObjectName("txtImporte")
        self.horizontalLayout_3.addWidget(self.txtImporte)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_6.addLayout(self.verticalLayout_2)
        self.verticalLayout.addWidget(self.groupBox)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.cmdOrder = QtWidgets.QPushButton(self.grp)
        self.cmdOrder.setEnabled(False)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/xulpymoney/add.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.cmdOrder.setIcon(icon1)
        self.cmdOrder.setObjectName("cmdOrder")
        self.horizontalLayout_2.addWidget(self.cmdOrder)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.cmd = QtWidgets.QPushButton(self.grp)
        self.cmd.setIcon(icon)
        self.cmd.setObjectName("cmd")
        self.horizontalLayout_2.addWidget(self.cmd)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_7.addLayout(self.verticalLayout)
        self.horizontalLayout_8.addWidget(self.grp)
        self.cmdGraph = QtWidgets.QToolButton(wdgDisReinvest)
        self.cmdGraph.setEnabled(False)
        self.cmdGraph.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/xulpymoney/report.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.cmdGraph.setIcon(icon2)
        self.cmdGraph.setIconSize(QtCore.QSize(64, 64))
        self.cmdGraph.setObjectName("cmdGraph")
        self.horizontalLayout_8.addWidget(self.cmdGraph)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem2)
        self.verticalLayout_3.addLayout(self.horizontalLayout_8)
        self.horizontalLayout_14 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_14.setObjectName("horizontalLayout_14")
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_14.addItem(spacerItem3)
        self.label = QtWidgets.QLabel(wdgDisReinvest)
        self.label.setObjectName("label")
        self.horizontalLayout_14.addWidget(self.label)
        self.cmbPrices = QtWidgets.QComboBox(wdgDisReinvest)
        self.cmbPrices.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        self.cmbPrices.setObjectName("cmbPrices")
        self.horizontalLayout_14.addWidget(self.cmbPrices)
        self.verticalLayout_3.addLayout(self.horizontalLayout_14)
        self.tabOps = QtWidgets.QTabWidget(wdgDisReinvest)
        self.tabOps.setObjectName("tabOps")
        self.tab_13 = QtWidgets.QWidget()
        self.tab_13.setObjectName("tab_13")
        self.horizontalLayout_24 = QtWidgets.QHBoxLayout(self.tab_13)
        self.horizontalLayout_24.setObjectName("horizontalLayout_24")
        self.mqtwOps = mqtw(self.tab_13)
        self.mqtwOps.setObjectName("mqtwOps")
        self.horizontalLayout_24.addWidget(self.mqtwOps)
        self.tabOps.addTab(self.tab_13, "")
        self.Situac_3 = QtWidgets.QWidget()
        self.Situac_3.setObjectName("Situac_3")
        self.horizontalLayout_26 = QtWidgets.QHBoxLayout(self.Situac_3)
        self.horizontalLayout_26.setObjectName("horizontalLayout_26")
        self.mqtwCurrentOps = mqtw(self.Situac_3)
        self.mqtwCurrentOps.setObjectName("mqtwCurrentOps")
        self.horizontalLayout_26.addWidget(self.mqtwCurrentOps)
        self.tabOps.addTab(self.Situac_3, "")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout(self.tab)
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.mqtwHistoricalOps = mqtwObjects(self.tab)
        self.mqtwHistoricalOps.setObjectName("mqtwHistoricalOps")
        self.horizontalLayout_9.addWidget(self.mqtwHistoricalOps)
        self.tabOps.addTab(self.tab, "")
        self.verticalLayout_3.addWidget(self.tabOps)
        self.horizontalLayout_21.addLayout(self.verticalLayout_3)

        self.retranslateUi(wdgDisReinvest)
        self.tabOps.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(wdgDisReinvest)

    def retranslateUi(self, wdgDisReinvest):
        _translate = QtCore.QCoreApplication.translate
        self.radRe.setText(_translate("wdgDisReinvest", "Reinvest simulation"))
        self.radDes.setText(_translate("wdgDisReinvest", "Disinvest simulation"))
        self.groupBox.setTitle(_translate("wdgDisReinvest", "Operation data"))
        self.txtSimulacion.setText(_translate("wdgDisReinvest", "0"))
        self.txtValorAccion.setText(_translate("wdgDisReinvest", "0"))
        self.label_3.setText(_translate("wdgDisReinvest", "Bank comission"))
        self.txtComision.setText(_translate("wdgDisReinvest", "0"))
        self.label_5.setText(_translate("wdgDisReinvest", "Shares number"))
        self.label_2.setText(_translate("wdgDisReinvest", "Amount"))
        self.cmdOrder.setText(_translate("wdgDisReinvest", "Add order annotations"))
        self.cmd.setText(_translate("wdgDisReinvest", "Make simulation"))
        self.cmdGraph.setToolTip(_translate("wdgDisReinvest", "Show operations in a graph"))
        self.label.setText(_translate("wdgDisReinvest", "Select a price to evaluate the simulation"))
        self.tabOps.setTabText(self.tabOps.indexOf(self.tab_13), _translate("wdgDisReinvest", "Investment operations"))
        self.tabOps.setTabText(self.tabOps.indexOf(self.Situac_3), _translate("wdgDisReinvest", "Investment current state"))
        self.tabOps.setTabText(self.tabOps.indexOf(self.tab), _translate("wdgDisReinvest", "Investment historical operations"))
from xulpymoney.ui.myqlineedit import myQLineEdit
from xulpymoney.ui.myqtablewidget import mqtw, mqtwObjects
import xulpymoney.images.xulpymoney_rc
