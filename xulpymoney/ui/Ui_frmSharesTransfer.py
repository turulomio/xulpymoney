# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'xulpymoney/ui/frmSharesTransfer.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_frmSharesTransfer(object):
    def setupUi(self, frmSharesTransfer):
        frmSharesTransfer.setObjectName("frmSharesTransfer")
        frmSharesTransfer.resize(559, 167)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/xulpymoney/transfer.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        frmSharesTransfer.setWindowIcon(icon)
        frmSharesTransfer.setSizeGripEnabled(True)
        self.horizontalLayout = QtWidgets.QHBoxLayout(frmSharesTransfer)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.lbl = QtWidgets.QLabel(frmSharesTransfer)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.lbl.setFont(font)
        self.lbl.setStyleSheet("color: rgb(0, 128, 0);")
        self.lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl.setObjectName("lbl")
        self.verticalLayout.addWidget(self.lbl)
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.ExpandingFieldsGrow)
        self.formLayout.setObjectName("formLayout")
        self.combo = QtWidgets.QComboBox(frmSharesTransfer)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.combo.sizePolicy().hasHeightForWidth())
        self.combo.setSizePolicy(sizePolicy)
        self.combo.setObjectName("combo")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.combo)
        self.lblCombo = QtWidgets.QLabel(frmSharesTransfer)
        self.lblCombo.setObjectName("lblCombo")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.lblCombo)
        self.lblNumero = QtWidgets.QLabel(frmSharesTransfer)
        self.lblNumero.setObjectName("lblNumero")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.lblNumero)
        self.txtAcciones = myQLineEdit(frmSharesTransfer)
        self.txtAcciones.setEnabled(False)
        self.txtAcciones.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.txtAcciones.setObjectName("txtAcciones")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.txtAcciones)
        self.lblComisionLabel = QtWidgets.QLabel(frmSharesTransfer)
        self.lblComisionLabel.setObjectName("lblComisionLabel")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.lblComisionLabel)
        self.txtComision = myQLineEdit(frmSharesTransfer)
        self.txtComision.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.txtComision.setObjectName("txtComision")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.txtComision)
        self.verticalLayout.addLayout(self.formLayout)
        self.buttons = QtWidgets.QDialogButtonBox(frmSharesTransfer)
        self.buttons.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttons.setObjectName("buttons")
        self.verticalLayout.addWidget(self.buttons, 0, QtCore.Qt.AlignHCenter)
        self.horizontalLayout.addLayout(self.verticalLayout)

        self.retranslateUi(frmSharesTransfer)
        QtCore.QMetaObject.connectSlotsByName(frmSharesTransfer)

    def retranslateUi(self, frmSharesTransfer):
        _translate = QtCore.QCoreApplication.translate
        frmSharesTransfer.setWindowTitle(_translate("frmSharesTransfer", "Shares transfer"))
        self.lblCombo.setText(_translate("frmSharesTransfer", "Select the destiny for the shares"))
        self.lblNumero.setText(_translate("frmSharesTransfer", "Number of shares"))
        self.lblComisionLabel.setText(_translate("frmSharesTransfer", "Shares transfer comission"))
        self.txtComision.setText(_translate("frmSharesTransfer", "0"))
from xulpymoney.ui.myqlineedit import myQLineEdit
import xulpymoney.images.xulpymoney_rc
