# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'xulpymoney/ui/wdgQuotesUpdate.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_wdgQuotesUpdate(object):
    def setupUi(self, wdgQuotesUpdate):
        wdgQuotesUpdate.setObjectName("wdgQuotesUpdate")
        wdgQuotesUpdate.resize(1109, 795)
        self.horizontalLayout = QtWidgets.QHBoxLayout(wdgQuotesUpdate)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.cmdUsed = QtWidgets.QPushButton(wdgQuotesUpdate)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/xulpymoney/transfer.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.cmdUsed.setIcon(icon)
        self.cmdUsed.setObjectName("cmdUsed")
        self.horizontalLayout_3.addWidget(self.cmdUsed)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.cmdAll = QtWidgets.QPushButton(wdgQuotesUpdate)
        self.cmdAll.setIcon(icon)
        self.cmdAll.setObjectName("cmdAll")
        self.horizontalLayout_3.addWidget(self.cmdAll)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem2)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.tab = QtWidgets.QTabWidget(wdgQuotesUpdate)
        self.tab.setObjectName("tab")
        self.tab_4 = QtWidgets.QWidget()
        self.tab_4.setObjectName("tab_4")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.tab_4)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.txtCR2Q = QtWidgets.QTextBrowser(self.tab_4)
        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setBold(True)
        font.setWeight(75)
        self.txtCR2Q.setFont(font)
        self.txtCR2Q.setUndoRedoEnabled(True)
        self.txtCR2Q.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.txtCR2Q.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByKeyboard|QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextBrowserInteraction|QtCore.Qt.TextEditable|QtCore.Qt.TextEditorInteraction|QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.txtCR2Q.setObjectName("txtCR2Q")
        self.verticalLayout_2.addWidget(self.txtCR2Q)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem3)
        self.cmdError = QtWidgets.QPushButton(self.tab_4)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/xulpymoney/eye_red.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.cmdError.setIcon(icon1)
        self.cmdError.setObjectName("cmdError")
        self.horizontalLayout_2.addWidget(self.cmdError)
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem4)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_4.addLayout(self.verticalLayout_2)
        self.tab.addTab(self.tab_4, "")
        self.verticalLayout.addWidget(self.tab)
        self.horizontalLayout.addLayout(self.verticalLayout)

        self.retranslateUi(wdgQuotesUpdate)
        self.tab.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(wdgQuotesUpdate)

    def retranslateUi(self, wdgQuotesUpdate):
        _translate = QtCore.QCoreApplication.translate
        self.cmdUsed.setText(_translate("wdgQuotesUpdate", "Update used products"))
        self.cmdAll.setText(_translate("wdgQuotesUpdate", "Update all products"))
        self.cmdError.setText(_translate("wdgQuotesUpdate", "Next error"))
        self.tab.setTabText(self.tab.indexOf(self.tab_4), _translate("wdgQuotesUpdate", "Update results"))

import xulpymoney.images.xulpymoney_rc
