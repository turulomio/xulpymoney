# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'xulpymoney/ui/frmSplit.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_frmSplit(object):
    def setupUi(self, frmSplit):
        frmSplit.setObjectName("frmSplit")
        frmSplit.resize(494, 432)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/xulpymoney/study.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        frmSplit.setWindowIcon(icon)
        frmSplit.setSizeGripEnabled(True)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(frmSplit)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label = QtWidgets.QLabel(frmSplit)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout_3.addWidget(self.label)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.wdgDt = wdgDatetime(frmSplit)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.wdgDt.sizePolicy().hasHeightForWidth())
        self.wdgDt.setSizePolicy(sizePolicy)
        self.wdgDt.setObjectName("wdgDt")
        self.horizontalLayout_3.addWidget(self.wdgDt)
        self.line = QtWidgets.QFrame(frmSplit)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.horizontalLayout_3.addWidget(self.line)
        self.verticalLayout_3.addLayout(self.horizontalLayout_3)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_2 = QtWidgets.QLabel(frmSplit)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setItalic(True)
        self.label_2.setFont(font)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.txtInitial = myQLineEdit(frmSplit)
        self.txtInitial.setAlignment(QtCore.Qt.AlignCenter)
        self.txtInitial.setObjectName("txtInitial")
        self.verticalLayout.addWidget(self.txtInitial)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_3 = QtWidgets.QLabel(frmSplit)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setItalic(True)
        self.label_3.setFont(font)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_2.addWidget(self.label_3)
        self.txtFinal = myQLineEdit(frmSplit)
        self.txtFinal.setAlignment(QtCore.Qt.AlignCenter)
        self.txtFinal.setObjectName("txtFinal")
        self.verticalLayout_2.addWidget(self.txtFinal)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_4 = QtWidgets.QLabel(frmSplit)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_4.addWidget(self.label_4)
        self.txtComment = QtWidgets.QLineEdit(frmSplit)
        self.txtComment.setObjectName("txtComment")
        self.horizontalLayout_4.addWidget(self.txtComment)
        self.verticalLayout_3.addLayout(self.horizontalLayout_4)
        self.lblExample = QtWidgets.QLabel(frmSplit)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.lblExample.setFont(font)
        self.lblExample.setAlignment(QtCore.Qt.AlignCenter)
        self.lblExample.setWordWrap(True)
        self.lblExample.setObjectName("lblExample")
        self.verticalLayout_3.addWidget(self.lblExample)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem2)
        self.buttonbox = QtWidgets.QDialogButtonBox(frmSplit)
        self.buttonbox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonbox.setCenterButtons(True)
        self.buttonbox.setObjectName("buttonbox")
        self.horizontalLayout_2.addWidget(self.buttonbox)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem3)
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_5.addLayout(self.verticalLayout_3)

        self.retranslateUi(frmSplit)
        QtCore.QMetaObject.connectSlotsByName(frmSplit)

    def retranslateUi(self, frmSplit):
        _translate = QtCore.QCoreApplication.translate
        frmSplit.setWindowTitle(_translate("frmSplit", "Split / Contrasplit relation"))
        self.label.setText(_translate("frmSplit", "Split / Contrasplit"))
        self.label_2.setText(_translate("frmSplit", "Current Shares"))
        self.txtInitial.setText(_translate("frmSplit", "1"))
        self.label_3.setText(_translate("frmSplit", "Final Shares"))
        self.txtFinal.setText(_translate("frmSplit", "10"))
        self.label_4.setText(_translate("frmSplit", "Comment"))
from xulpymoney.ui.myqlineedit import myQLineEdit
from xulpymoney.ui.wdgDatetime import wdgDatetime
import xulpymoney.images.xulpymoney_rc
