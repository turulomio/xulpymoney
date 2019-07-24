# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'xulpymoney/ui/frmEstimationsAdd.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_frmEstimationsAdd(object):
    def setupUi(self, frmEstimationsAdd):
        frmEstimationsAdd.setObjectName("frmEstimationsAdd")
        frmEstimationsAdd.setWindowModality(QtCore.Qt.ApplicationModal)
        frmEstimationsAdd.resize(634, 177)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/dinero.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        frmEstimationsAdd.setWindowIcon(icon)
        frmEstimationsAdd.setModal(True)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(frmEstimationsAdd)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.lbl = QtWidgets.QLabel(frmEstimationsAdd)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.lbl.setFont(font)
        self.lbl.setStyleSheet("color: rgb(0, 192, 0);")
        self.lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl.setObjectName("lbl")
        self.verticalLayout.addWidget(self.lbl)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(frmEstimationsAdd)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.txtYear = QtWidgets.QLineEdit(frmEstimationsAdd)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.txtYear.sizePolicy().hasHeightForWidth())
        self.txtYear.setSizePolicy(sizePolicy)
        self.txtYear.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.txtYear.setObjectName("txtYear")
        self.horizontalLayout.addWidget(self.txtYear)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.lblEstimation = QtWidgets.QLabel(frmEstimationsAdd)
        self.lblEstimation.setObjectName("lblEstimation")
        self.horizontalLayout_2.addWidget(self.lblEstimation)
        self.txtDPA = myQLineEdit(frmEstimationsAdd)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.txtDPA.sizePolicy().hasHeightForWidth())
        self.txtDPA.setSizePolicy(sizePolicy)
        self.txtDPA.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.txtDPA.setObjectName("txtDPA")
        self.horizontalLayout_2.addWidget(self.txtDPA)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_3 = QtWidgets.QLabel(frmEstimationsAdd)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_3.addWidget(self.label_3)
        self.cmbSource = QtWidgets.QComboBox(frmEstimationsAdd)
        self.cmbSource.setObjectName("cmbSource")
        self.horizontalLayout_3.addWidget(self.cmbSource)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.cmd = QtWidgets.QPushButton(frmEstimationsAdd)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/xulpymoney/save.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.cmd.setIcon(icon1)
        self.cmd.setObjectName("cmd")
        self.verticalLayout.addWidget(self.cmd)
        self.horizontalLayout_4.addLayout(self.verticalLayout)

        self.retranslateUi(frmEstimationsAdd)
        QtCore.QMetaObject.connectSlotsByName(frmEstimationsAdd)
        frmEstimationsAdd.setTabOrder(self.txtDPA, self.txtYear)
        frmEstimationsAdd.setTabOrder(self.txtYear, self.cmbSource)
        frmEstimationsAdd.setTabOrder(self.cmbSource, self.cmd)

    def retranslateUi(self, frmEstimationsAdd):
        _translate = QtCore.QCoreApplication.translate
        frmEstimationsAdd.setWindowTitle(_translate("frmEstimationsAdd", "New estimation"))
        self.label.setText(_translate("frmEstimationsAdd", "Add a year"))
        self.lblEstimation.setText(_translate("frmEstimationsAdd", "Add a estimation"))
        self.txtDPA.setText(_translate("frmEstimationsAdd", "0"))
        self.label_3.setText(_translate("frmEstimationsAdd", "Add a source"))
        self.cmd.setText(_translate("frmEstimationsAdd", "Save estimation"))
from xulpymoney.ui.myqlineedit import myQLineEdit
import xulpymoney.images.xulpymoney_rc
