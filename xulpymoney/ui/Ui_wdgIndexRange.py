# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/wdgIndexRange.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_wdgIndexRange(object):
    def setupUi(self, wdgIndexRange):
        wdgIndexRange.setObjectName("wdgIndexRange")
        wdgIndexRange.resize(747, 519)
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout(wdgIndexRange)
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.lbl = QtWidgets.QLabel(wdgIndexRange)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lbl.sizePolicy().hasHeightForWidth())
        self.lbl.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.lbl.setFont(font)
        self.lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl.setObjectName("lbl")
        self.verticalLayout_3.addWidget(self.lbl)
        self.groupBox = QtWidgets.QGroupBox(wdgIndexRange)
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout(self.groupBox)
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.spin = QtWidgets.QDoubleSpinBox(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.spin.sizePolicy().hasHeightForWidth())
        self.spin.setSizePolicy(sizePolicy)
        self.spin.setMinimumSize(QtCore.QSize(200, 0))
        self.spin.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.spin.setDecimals(1)
        self.spin.setSingleStep(0.1)
        self.spin.setProperty("value", 2.0)
        self.spin.setObjectName("spin")
        self.horizontalLayout.addWidget(self.spin)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.txtInvertir = myQLineEdit(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.txtInvertir.sizePolicy().hasHeightForWidth())
        self.txtInvertir.setSizePolicy(sizePolicy)
        self.txtInvertir.setMinimumSize(QtCore.QSize(200, 0))
        self.txtInvertir.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.txtInvertir.setObjectName("txtInvertir")
        self.horizontalLayout_2.addWidget(self.txtInvertir)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_4 = QtWidgets.QLabel(self.groupBox)
        self.label_4.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_3.addWidget(self.label_4)
        self.txtMinimo = myQLineEdit(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.txtMinimo.sizePolicy().hasHeightForWidth())
        self.txtMinimo.setSizePolicy(sizePolicy)
        self.txtMinimo.setMinimumSize(QtCore.QSize(200, 0))
        self.txtMinimo.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.txtMinimo.setObjectName("txtMinimo")
        self.horizontalLayout_3.addWidget(self.txtMinimo)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_5.addLayout(self.verticalLayout)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.cmd = QtWidgets.QPushButton(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmd.sizePolicy().hasHeightForWidth())
        self.cmd.setSizePolicy(sizePolicy)
        self.cmd.setObjectName("cmd")
        self.verticalLayout_2.addWidget(self.cmd)
        self.horizontalLayout_5.addLayout(self.verticalLayout_2)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem1)
        self.horizontalLayout_7.addLayout(self.horizontalLayout_5)
        self.verticalLayout_3.addWidget(self.groupBox)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem2)
        self.cmbBenchmarkCurrent = QtWidgets.QComboBox(wdgIndexRange)
        self.cmbBenchmarkCurrent.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContentsOnFirstShow)
        self.cmbBenchmarkCurrent.setObjectName("cmbBenchmarkCurrent")
        self.horizontalLayout_4.addWidget(self.cmbBenchmarkCurrent)
        self.cmdIRAnalisis = QtWidgets.QToolButton(wdgIndexRange)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/xulpymoney/books.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.cmdIRAnalisis.setIcon(icon)
        self.cmdIRAnalisis.setObjectName("cmdIRAnalisis")
        self.horizontalLayout_4.addWidget(self.cmdIRAnalisis)
        self.cmdIRInsertar = QtWidgets.QToolButton(wdgIndexRange)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/xulpymoney/add.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.cmdIRInsertar.setIcon(icon1)
        self.cmdIRInsertar.setObjectName("cmdIRInsertar")
        self.horizontalLayout_4.addWidget(self.cmdIRInsertar)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem3)
        self.verticalLayout_3.addLayout(self.horizontalLayout_4)
        self.table = myQTableWidget(wdgIndexRange)
        self.table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setObjectName("table")
        self.table.setColumnCount(2)
        self.table.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(1, item)
        self.table.verticalHeader().setVisible(False)
        self.verticalLayout_3.addWidget(self.table)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.lblTotal = QtWidgets.QLabel(wdgIndexRange)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblTotal.sizePolicy().hasHeightForWidth())
        self.lblTotal.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)
        self.lblTotal.setFont(font)
        self.lblTotal.setAlignment(QtCore.Qt.AlignCenter)
        self.lblTotal.setObjectName("lblTotal")
        self.horizontalLayout_6.addWidget(self.lblTotal)
        self.cmbShowOptions = QtWidgets.QComboBox(wdgIndexRange)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbShowOptions.sizePolicy().hasHeightForWidth())
        self.cmbShowOptions.setSizePolicy(sizePolicy)
        self.cmbShowOptions.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        self.cmbShowOptions.setObjectName("cmbShowOptions")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/xulpymoney/eye.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.cmbShowOptions.addItem(icon2, "")
        self.cmbShowOptions.addItem("")
        self.cmbShowOptions.addItem("")
        self.cmbShowOptions.addItem("")
        self.cmbShowOptions.addItem("")
        self.horizontalLayout_6.addWidget(self.cmbShowOptions)
        self.verticalLayout_3.addLayout(self.horizontalLayout_6)
        self.horizontalLayout_8.addLayout(self.verticalLayout_3)
        self.actionTop = QtWidgets.QAction(wdgIndexRange)
        self.actionTop.setObjectName("actionTop")
        self.actionMiddle = QtWidgets.QAction(wdgIndexRange)
        self.actionMiddle.setObjectName("actionMiddle")
        self.actionBottom = QtWidgets.QAction(wdgIndexRange)
        self.actionBottom.setObjectName("actionBottom")

        self.retranslateUi(wdgIndexRange)
        QtCore.QMetaObject.connectSlotsByName(wdgIndexRange)

    def retranslateUi(self, wdgIndexRange):
        _translate = QtCore.QCoreApplication.translate
        self.lbl.setText(_translate("wdgIndexRange", "Investments by index range"))
        self.groupBox.setTitle(_translate("wdgIndexRange", "Report data"))
        self.label_2.setText(_translate("wdgIndexRange", "Percentage between ranges"))
        self.spin.setSuffix(_translate("wdgIndexRange", " %"))
        self.label.setText(_translate("wdgIndexRange", "Money to invest"))
        self.txtInvertir.setText(_translate("wdgIndexRange", "4000"))
        self.label_4.setText(_translate("wdgIndexRange", "Index lowest limit"))
        self.txtMinimo.setText(_translate("wdgIndexRange", "1000"))
        self.cmd.setText(_translate("wdgIndexRange", "Update ranges"))
        self.cmdIRAnalisis.setToolTip(_translate("wdgIndexRange", "Show benchmark report"))
        self.cmdIRAnalisis.setText(_translate("wdgIndexRange", "..."))
        self.cmdIRInsertar.setToolTip(_translate("wdgIndexRange", "Add a price to the benchmark"))
        self.cmdIRInsertar.setText(_translate("wdgIndexRange", "..."))
        item = self.table.horizontalHeaderItem(0)
        item.setText(_translate("wdgIndexRange", "Range"))
        item = self.table.horizontalHeaderItem(1)
        item.setText(_translate("wdgIndexRange", "Investments"))
        self.cmbShowOptions.setItemText(0, _translate("wdgIndexRange", "Marked to show investment operations"))
        self.cmbShowOptions.setItemText(1, _translate("wdgIndexRange", "Show ETF, Shares and Warrants Investment operations"))
        self.cmbShowOptions.setItemText(2, _translate("wdgIndexRange", "Show bonds"))
        self.cmbShowOptions.setItemText(3, _translate("wdgIndexRange", "Show funds"))
        self.cmbShowOptions.setItemText(4, _translate("wdgIndexRange", "Show all investment operations"))
        self.actionTop.setText(_translate("wdgIndexRange", "Top"))
        self.actionMiddle.setText(_translate("wdgIndexRange", "Middle"))
        self.actionBottom.setText(_translate("wdgIndexRange", "Bottom"))

from myqlineedit import myQLineEdit
from myqtablewidget import myQTableWidget
import xulpymoney_rc
