# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/wdgSource.ui'
#
# Created by: PyQt5 UI code generator 5.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_wdgSource(object):
    def setupUi(self, wdgSource):
        wdgSource.setObjectName("wdgSource")
        wdgSource.resize(712, 100)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(wdgSource.sizePolicy().hasHeightForWidth())
        wdgSource.setSizePolicy(sizePolicy)
        wdgSource.setMinimumSize(QtCore.QSize(0, 100))
        wdgSource.setMaximumSize(QtCore.QSize(16777215, 100))
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(wdgSource)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.grp = QtWidgets.QGroupBox(wdgSource)
        self.grp.setObjectName("grp")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.grp)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.lbl = QtWidgets.QLabel(self.grp)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lbl.sizePolicy().hasHeightForWidth())
        self.lbl.setSizePolicy(sizePolicy)
        self.lbl.setMinimumSize(QtCore.QSize(200, 0))
        self.lbl.setMaximumSize(QtCore.QSize(200, 16777215))
        self.lbl.setObjectName("lbl")
        self.horizontalLayout_2.addWidget(self.lbl)
        self.progress = QtWidgets.QProgressBar(self.grp)
        self.progress.setProperty("value", 0)
        self.progress.setObjectName("progress")
        self.horizontalLayout_2.addWidget(self.progress)
        self.cmdRun = QtWidgets.QToolButton(self.grp)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmdRun.sizePolicy().hasHeightForWidth())
        self.cmdRun.setSizePolicy(sizePolicy)
        self.cmdRun.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/xulpymoney/transfer.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.cmdRun.setIcon(icon)
        self.cmdRun.setObjectName("cmdRun")
        self.horizontalLayout_2.addWidget(self.cmdRun)
        self.cmdCancel = QtWidgets.QToolButton(self.grp)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/xulpymoney/button_cancel.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.cmdCancel.setIcon(icon1)
        self.cmdCancel.setObjectName("cmdCancel")
        self.horizontalLayout_2.addWidget(self.cmdCancel)
        self.line = QtWidgets.QFrame(self.grp)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.horizontalLayout_2.addWidget(self.line)
        self.chkUserOnly = QtWidgets.QCheckBox(self.grp)
        self.chkUserOnly.setChecked(True)
        self.chkUserOnly.setObjectName("chkUserOnly")
        self.horizontalLayout_2.addWidget(self.chkUserOnly)
        self.line_2 = QtWidgets.QFrame(self.grp)
        self.line_2.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.horizontalLayout_2.addWidget(self.line_2)
        self.cmdDropDown = QtWidgets.QToolButton(self.grp)
        self.cmdDropDown.setEnabled(False)
        self.cmdDropDown.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/xulpymoney/star.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.cmdDropDown.setIcon(icon2)
        self.cmdDropDown.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.cmdDropDown.setObjectName("cmdDropDown")
        self.horizontalLayout_2.addWidget(self.cmdDropDown)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.verticalLayout.addWidget(self.grp)
        self.horizontalLayout_4.addLayout(self.verticalLayout)
        self.actionProducts = QtWidgets.QAction(wdgSource)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/xulpymoney/document-preview-archive.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionProducts.setIcon(icon3)
        self.actionProducts.setObjectName("actionProducts")
        self.actionErrors = QtWidgets.QAction(wdgSource)
        self.actionErrors.setIcon(icon1)
        self.actionErrors.setObjectName("actionErrors")
        self.actionInserted = QtWidgets.QAction(wdgSource)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/xulpymoney/add.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionInserted.setIcon(icon4)
        self.actionInserted.setObjectName("actionInserted")
        self.actionEdited = QtWidgets.QAction(wdgSource)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/xulpymoney/editar.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionEdited.setIcon(icon5)
        self.actionEdited.setObjectName("actionEdited")
        self.actionIgnored = QtWidgets.QAction(wdgSource)
        self.actionIgnored.setObjectName("actionIgnored")
        self.actionWrong = QtWidgets.QAction(wdgSource)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(":/xulpymoney/checkbox0.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionWrong.setIcon(icon6)
        self.actionWrong.setObjectName("actionWrong")
        self.actionHTML = QtWidgets.QAction(wdgSource)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(":/xulpymoney/history2.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionHTML.setIcon(icon7)
        self.actionHTML.setObjectName("actionHTML")

        self.retranslateUi(wdgSource)
        QtCore.QMetaObject.connectSlotsByName(wdgSource)

    def retranslateUi(self, wdgSource):
        _translate = QtCore.QCoreApplication.translate
        self.lbl.setText(_translate("wdgSource", "Update progress"))
        self.chkUserOnly.setText(_translate("wdgSource", "User only"))
        self.actionProducts.setText(_translate("wdgSource", "Products searched"))
        self.actionProducts.setToolTip(_translate("wdgSource", "Products searched"))
        self.actionErrors.setText(_translate("wdgSource", "Parsing errors"))
        self.actionErrors.setToolTip(_translate("wdgSource", "Parsing errors"))
        self.actionInserted.setText(_translate("wdgSource", "Inserted quotes"))
        self.actionInserted.setToolTip(_translate("wdgSource", "Inserted quotes"))
        self.actionEdited.setText(_translate("wdgSource", "Edited quotes"))
        self.actionEdited.setToolTip(_translate("wdgSource", "Edited quotes"))
        self.actionIgnored.setText(_translate("wdgSource", "Ignored quotes"))
        self.actionIgnored.setToolTip(_translate("wdgSource", "Ignored quotes"))
        self.actionWrong.setText(_translate("wdgSource", "Wrong quotes"))
        self.actionWrong.setToolTip(_translate("wdgSource", "Wrong quotes"))
        self.actionHTML.setText(_translate("wdgSource", "Show HTML"))
        self.actionHTML.setToolTip(_translate("wdgSource", "Show HTML"))

import xulpymoney_rc
