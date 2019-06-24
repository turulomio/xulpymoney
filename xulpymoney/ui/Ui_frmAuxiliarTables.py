# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'xulpymoney/ui/frmAuxiliarTables.ui'
#
# Created by: PyQt5 UI code generator 5.12.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_frmAuxiliarTables(object):
    def setupUi(self, frmAuxiliarTables):
        frmAuxiliarTables.setObjectName("frmAuxiliarTables")
        frmAuxiliarTables.resize(612, 541)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/xulpymoney/configure.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        frmAuxiliarTables.setWindowIcon(icon)
        self.horizontalLayout = QtWidgets.QHBoxLayout(frmAuxiliarTables)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(frmAuxiliarTables)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.tabWidget = QtWidgets.QTabWidget(frmAuxiliarTables)
        self.tabWidget.setObjectName("tabWidget")
        self.tabConceptos = QtWidgets.QWidget()
        self.tabConceptos.setObjectName("tabConceptos")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.tabConceptos)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.tblConcepts = myQTableWidget(self.tabConceptos)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tblConcepts.sizePolicy().hasHeightForWidth())
        self.tblConcepts.setSizePolicy(sizePolicy)
        self.tblConcepts.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tblConcepts.setAlternatingRowColors(True)
        self.tblConcepts.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tblConcepts.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tblConcepts.setObjectName("tblConcepts")
        self.tblConcepts.setColumnCount(2)
        self.tblConcepts.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tblConcepts.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblConcepts.setHorizontalHeaderItem(1, item)
        self.tblConcepts.verticalHeader().setVisible(False)
        self.verticalLayout_2.addWidget(self.tblConcepts)
        self.horizontalLayout_2.addLayout(self.verticalLayout_2)
        self.tabWidget.addTab(self.tabConceptos, "")
        self.verticalLayout.addWidget(self.tabWidget)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.actionExpensesAdd = QtWidgets.QAction(frmAuxiliarTables)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/xulpymoney/add.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionExpensesAdd.setIcon(icon1)
        self.actionExpensesAdd.setObjectName("actionExpensesAdd")
        self.actionConceptDelete = QtWidgets.QAction(frmAuxiliarTables)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/xulpymoney/eventdelete.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionConceptDelete.setIcon(icon2)
        self.actionConceptDelete.setObjectName("actionConceptDelete")
        self.actionIncomesAdd = QtWidgets.QAction(frmAuxiliarTables)
        self.actionIncomesAdd.setIcon(icon1)
        self.actionIncomesAdd.setObjectName("actionIncomesAdd")
        self.actionChangeName = QtWidgets.QAction(frmAuxiliarTables)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/xulpymoney/editar.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionChangeName.setIcon(icon3)
        self.actionChangeName.setObjectName("actionChangeName")

        self.retranslateUi(frmAuxiliarTables)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(frmAuxiliarTables)

    def retranslateUi(self, frmAuxiliarTables):
        _translate = QtCore.QCoreApplication.translate
        frmAuxiliarTables.setWindowTitle(_translate("frmAuxiliarTables", "Xulpymoney > Auxiliar tables"))
        self.label.setText(_translate("frmAuxiliarTables", "Auxiliar tables"))
        item = self.tblConcepts.horizontalHeaderItem(0)
        item.setText(_translate("frmAuxiliarTables", "Concepts"))
        item = self.tblConcepts.horizontalHeaderItem(1)
        item.setText(_translate("frmAuxiliarTables", "Operation type"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabConceptos), _translate("frmAuxiliarTables", "Xulpymoney concepts"))
        self.actionExpensesAdd.setText(_translate("frmAuxiliarTables", "Add a expense concept"))
        self.actionExpensesAdd.setToolTip(_translate("frmAuxiliarTables", "Add a expense concept"))
        self.actionConceptDelete.setText(_translate("frmAuxiliarTables", "Delete concept"))
        self.actionConceptDelete.setToolTip(_translate("frmAuxiliarTables", "Delete concept"))
        self.actionIncomesAdd.setText(_translate("frmAuxiliarTables", "Add an income concept"))
        self.actionIncomesAdd.setToolTip(_translate("frmAuxiliarTables", "Add an income concept"))
        self.actionChangeName.setText(_translate("frmAuxiliarTables", "Change name"))
        self.actionChangeName.setToolTip(_translate("frmAuxiliarTables", "Change name"))


from xulpymoney.ui.myqtablewidget import myQTableWidget
import xulpymoney.images.xulpymoney_rc
