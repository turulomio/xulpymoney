# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'xulpymoney/ui/frmAccess.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_frmAccess(object):
    def setupUi(self, frmAccess):
        frmAccess.setObjectName("frmAccess")
        frmAccess.setWindowModality(QtCore.Qt.WindowModal)
        frmAccess.resize(437, 458)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(frmAccess.sizePolicy().hasHeightForWidth())
        frmAccess.setSizePolicy(sizePolicy)
        frmAccess.setModal(True)
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout(frmAccess)
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.lblPixmap = QtWidgets.QLabel(frmAccess)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblPixmap.sizePolicy().hasHeightForWidth())
        self.lblPixmap.setSizePolicy(sizePolicy)
        self.lblPixmap.setMinimumSize(QtCore.QSize(80, 80))
        self.lblPixmap.setMaximumSize(QtCore.QSize(80, 80))
        self.lblPixmap.setText("")
        self.lblPixmap.setScaledContents(True)
        self.lblPixmap.setAlignment(QtCore.Qt.AlignCenter)
        self.lblPixmap.setObjectName("lblPixmap")
        self.horizontalLayout_2.addWidget(self.lblPixmap)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.lbl = QtWidgets.QLabel(frmAccess)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.lbl.setFont(font)
        self.lbl.setText("")
        self.lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl.setObjectName("lbl")
        self.verticalLayout.addWidget(self.lbl)
        self.line = QtWidgets.QFrame(frmAccess)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.lblLanguage_2 = QtWidgets.QLabel(frmAccess)
        self.lblLanguage_2.setObjectName("lblLanguage_2")
        self.horizontalLayout_9.addWidget(self.lblLanguage_2)
        self.cmbProfiles = QtWidgets.QComboBox(frmAccess)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbProfiles.sizePolicy().hasHeightForWidth())
        self.cmbProfiles.setSizePolicy(sizePolicy)
        self.cmbProfiles.setMaximumSize(QtCore.QSize(200, 16777215))
        self.cmbProfiles.setFocusPolicy(QtCore.Qt.NoFocus)
        self.cmbProfiles.setObjectName("cmbProfiles")
        self.horizontalLayout_9.addWidget(self.cmbProfiles)
        self.cmdProfileNew = QtWidgets.QToolButton(frmAccess)
        self.cmdProfileNew.setFocusPolicy(QtCore.Qt.NoFocus)
        self.cmdProfileNew.setText("")
        self.cmdProfileNew.setObjectName("cmdProfileNew")
        self.horizontalLayout_9.addWidget(self.cmdProfileNew)
        self.cmdProfileUpdate = QtWidgets.QToolButton(frmAccess)
        self.cmdProfileUpdate.setFocusPolicy(QtCore.Qt.NoFocus)
        self.cmdProfileUpdate.setText("")
        self.cmdProfileUpdate.setObjectName("cmdProfileUpdate")
        self.horizontalLayout_9.addWidget(self.cmdProfileUpdate)
        self.cmdProfileDelete = QtWidgets.QToolButton(frmAccess)
        self.cmdProfileDelete.setFocusPolicy(QtCore.Qt.NoFocus)
        self.cmdProfileDelete.setText("")
        self.cmdProfileDelete.setObjectName("cmdProfileDelete")
        self.horizontalLayout_9.addWidget(self.cmdProfileDelete)
        self.verticalLayout.addLayout(self.horizontalLayout_9)
        self.line_2 = QtWidgets.QFrame(frmAccess)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.verticalLayout.addWidget(self.line_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.lblLanguage = QtWidgets.QLabel(frmAccess)
        self.lblLanguage.setObjectName("lblLanguage")
        self.horizontalLayout.addWidget(self.lblLanguage)
        self.cmbLanguages = QtWidgets.QComboBox(frmAccess)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbLanguages.sizePolicy().hasHeightForWidth())
        self.cmbLanguages.setSizePolicy(sizePolicy)
        self.cmbLanguages.setMaximumSize(QtCore.QSize(200, 16777215))
        self.cmbLanguages.setFocusPolicy(QtCore.Qt.NoFocus)
        self.cmbLanguages.setObjectName("cmbLanguages")
        self.horizontalLayout.addWidget(self.cmbLanguages)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.lblServer = QtWidgets.QLabel(frmAccess)
        self.lblServer.setObjectName("lblServer")
        self.horizontalLayout_3.addWidget(self.lblServer)
        self.txtServer = QtWidgets.QLineEdit(frmAccess)
        self.txtServer.setMaximumSize(QtCore.QSize(200, 16777215))
        self.txtServer.setInputMethodHints(QtCore.Qt.ImhNone)
        self.txtServer.setText("")
        self.txtServer.setEchoMode(QtWidgets.QLineEdit.Normal)
        self.txtServer.setObjectName("txtServer")
        self.horizontalLayout_3.addWidget(self.txtServer)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.lblPort = QtWidgets.QLabel(frmAccess)
        self.lblPort.setObjectName("lblPort")
        self.horizontalLayout_4.addWidget(self.lblPort)
        self.txtPort = QtWidgets.QLineEdit(frmAccess)
        self.txtPort.setMaximumSize(QtCore.QSize(200, 16777215))
        self.txtPort.setText("")
        self.txtPort.setObjectName("txtPort")
        self.horizontalLayout_4.addWidget(self.txtPort)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.lblDatabase = QtWidgets.QLabel(frmAccess)
        self.lblDatabase.setObjectName("lblDatabase")
        self.horizontalLayout_5.addWidget(self.lblDatabase)
        self.txtDB = QtWidgets.QLineEdit(frmAccess)
        self.txtDB.setMaximumSize(QtCore.QSize(200, 16777215))
        self.txtDB.setObjectName("txtDB")
        self.horizontalLayout_5.addWidget(self.txtDB)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.lblUser = QtWidgets.QLabel(frmAccess)
        self.lblUser.setObjectName("lblUser")
        self.horizontalLayout_6.addWidget(self.lblUser)
        self.txtUser = QtWidgets.QLineEdit(frmAccess)
        self.txtUser.setMaximumSize(QtCore.QSize(200, 16777215))
        self.txtUser.setObjectName("txtUser")
        self.horizontalLayout_6.addWidget(self.txtUser)
        self.verticalLayout.addLayout(self.horizontalLayout_6)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.lblPass = QtWidgets.QLabel(frmAccess)
        self.lblPass.setObjectName("lblPass")
        self.horizontalLayout_7.addWidget(self.lblPass)
        self.txtPass = QtWidgets.QLineEdit(frmAccess)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.txtPass.sizePolicy().hasHeightForWidth())
        self.txtPass.setSizePolicy(sizePolicy)
        self.txtPass.setMaximumSize(QtCore.QSize(200, 16777215))
        self.txtPass.setInputMethodHints(QtCore.Qt.ImhHiddenText|QtCore.Qt.ImhNoAutoUppercase|QtCore.Qt.ImhNoPredictiveText|QtCore.Qt.ImhSensitiveData)
        self.txtPass.setEchoMode(QtWidgets.QLineEdit.Password)
        self.txtPass.setObjectName("txtPass")
        self.horizontalLayout_7.addWidget(self.txtPass)
        self.verticalLayout.addLayout(self.horizontalLayout_7)
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.cmdDatabaseNew = QtWidgets.QPushButton(frmAccess)
        self.cmdDatabaseNew.setFocusPolicy(QtCore.Qt.NoFocus)
        self.cmdDatabaseNew.setAutoDefault(False)
        self.cmdDatabaseNew.setObjectName("cmdDatabaseNew")
        self.horizontalLayout_8.addWidget(self.cmdDatabaseNew)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem2)
        self.cmdYN = QtWidgets.QDialogButtonBox(frmAccess)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmdYN.sizePolicy().hasHeightForWidth())
        self.cmdYN.setSizePolicy(sizePolicy)
        self.cmdYN.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedKingdom))
        self.cmdYN.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.cmdYN.setCenterButtons(True)
        self.cmdYN.setObjectName("cmdYN")
        self.horizontalLayout_8.addWidget(self.cmdYN)
        self.verticalLayout.addLayout(self.horizontalLayout_8)
        self.horizontalLayout_10.addLayout(self.verticalLayout)

        self.retranslateUi(frmAccess)
        QtCore.QMetaObject.connectSlotsByName(frmAccess)
        frmAccess.setTabOrder(self.txtPass, self.cmdYN)
        frmAccess.setTabOrder(self.cmdYN, self.txtServer)
        frmAccess.setTabOrder(self.txtServer, self.txtPort)
        frmAccess.setTabOrder(self.txtPort, self.txtDB)
        frmAccess.setTabOrder(self.txtDB, self.txtUser)

    def retranslateUi(self, frmAccess):
        _translate = QtCore.QCoreApplication.translate
        self.lblLanguage_2.setText(_translate("frmAccess", "Select a profile"))
        self.cmdProfileNew.setToolTip(_translate("frmAccess", "Create a new profile"))
        self.cmdProfileUpdate.setToolTip(_translate("frmAccess", "Update current profile name"))
        self.cmdProfileDelete.setToolTip(_translate("frmAccess", "Delete current profile"))
        self.lblLanguage.setText(_translate("frmAccess", "Language"))
        self.lblServer.setText(_translate("frmAccess", "Server"))
        self.lblPort.setText(_translate("frmAccess", "Port"))
        self.lblDatabase.setText(_translate("frmAccess", "Database"))
        self.lblUser.setText(_translate("frmAccess", "User"))
        self.lblPass.setText(_translate("frmAccess", "Password"))
        self.cmdDatabaseNew.setText(_translate("frmAccess", "New Database"))
