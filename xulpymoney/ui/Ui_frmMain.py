# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/frmMain.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_frmMain(object):
    def setupUi(self, frmMain):
        frmMain.setObjectName("frmMain")
        frmMain.resize(1186, 625)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(frmMain.sizePolicy().hasHeightForWidth())
        frmMain.setSizePolicy(sizePolicy)
        frmMain.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/xulpymoney/coins.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        frmMain.setWindowIcon(icon)
        self.central = QtWidgets.QWidget(frmMain)
        self.central.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.central.sizePolicy().hasHeightForWidth())
        self.central.setSizePolicy(sizePolicy)
        self.central.setObjectName("central")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.central)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setObjectName("layout")
        self.horizontalLayout.addLayout(self.layout)
        frmMain.setCentralWidget(self.central)
        self.menuBar = QtWidgets.QMenuBar(frmMain)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 1186, 30))
        self.menuBar.setObjectName("menuBar")
        self.menuAyuda = QtWidgets.QMenu(self.menuBar)
        self.menuAyuda.setObjectName("menuAyuda")
        self.menuBancos = QtWidgets.QMenu(self.menuBar)
        self.menuBancos.setObjectName("menuBancos")
        self.menuInformes = QtWidgets.QMenu(self.menuBar)
        self.menuInformes.setObjectName("menuInformes")
        self.menuCuentas = QtWidgets.QMenu(self.menuBar)
        self.menuCuentas.setObjectName("menuCuentas")
        self.menuInversiones = QtWidgets.QMenu(self.menuBar)
        self.menuInversiones.setObjectName("menuInversiones")
        self.menuXulpymoney = QtWidgets.QMenu(self.menuBar)
        self.menuXulpymoney.setObjectName("menuXulpymoney")
        self.menuProducts = QtWidgets.QMenu(self.menuBar)
        self.menuProducts.setObjectName("menuProducts")
        self.menuIndexes = QtWidgets.QMenu(self.menuProducts)
        self.menuIndexes.setObjectName("menuIndexes")
        self.menuMaintenance = QtWidgets.QMenu(self.menuProducts)
        self.menuMaintenance.setObjectName("menuMaintenance")
        self.menuReports = QtWidgets.QMenu(self.menuProducts)
        self.menuReports.setObjectName("menuReports")
        self.menuShares = QtWidgets.QMenu(self.menuProducts)
        self.menuShares.setObjectName("menuShares")
        self.menuCurrencies = QtWidgets.QMenu(self.menuProducts)
        self.menuCurrencies.setObjectName("menuCurrencies")
        self.menuBonds = QtWidgets.QMenu(self.menuProducts)
        self.menuBonds.setObjectName("menuBonds")
        self.menuFunds = QtWidgets.QMenu(self.menuProducts)
        self.menuFunds.setObjectName("menuFunds")
        self.menuETF = QtWidgets.QMenu(self.menuProducts)
        self.menuETF.setObjectName("menuETF")
        self.menuWarrants = QtWidgets.QMenu(self.menuProducts)
        self.menuWarrants.setObjectName("menuWarrants")
        frmMain.setMenuBar(self.menuBar)
        self.toolBar = QtWidgets.QToolBar(frmMain)
        self.toolBar.setIconSize(QtCore.QSize(48, 33))
        self.toolBar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.toolBar.setObjectName("toolBar")
        frmMain.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.statusBar = QtWidgets.QStatusBar(frmMain)
        self.statusBar.setObjectName("statusBar")
        frmMain.setStatusBar(self.statusBar)
        self.actionExit = QtWidgets.QAction(frmMain)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/xulpymoney/exit.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionExit.setIcon(icon1)
        self.actionExit.setObjectName("actionExit")
        self.actionAbout = QtWidgets.QAction(frmMain)
        self.actionAbout.setIcon(icon)
        self.actionAbout.setObjectName("actionAbout")
        self.actionIndexRange = QtWidgets.QAction(frmMain)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/xulpymoney/report.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionIndexRange.setIcon(icon2)
        self.actionIndexRange.setObjectName("actionIndexRange")
        self.actionInvestments = QtWidgets.QAction(frmMain)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/xulpymoney/bundle.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionInvestments.setIcon(icon3)
        self.actionInvestments.setObjectName("actionInvestments")
        self.actionAuxiliarTables = QtWidgets.QAction(frmMain)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/xulpymoney/table.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionAuxiliarTables.setIcon(icon4)
        self.actionAuxiliarTables.setObjectName("actionAuxiliarTables")
        self.actionDividendsReport = QtWidgets.QAction(frmMain)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/xulpymoney/star.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionDividendsReport.setIcon(icon5)
        self.actionDividendsReport.setObjectName("actionDividendsReport")
        self.actionEvolutionReport = QtWidgets.QAction(frmMain)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(":/xulpymoney/dinero.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionEvolutionReport.setIcon(icon6)
        self.actionEvolutionReport.setObjectName("actionEvolutionReport")
        self.actionTotalReport = QtWidgets.QAction(frmMain)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(":/xulpymoney/report2.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionTotalReport.setIcon(icon7)
        self.actionTotalReport.setObjectName("actionTotalReport")
        self.actionAccounts = QtWidgets.QAction(frmMain)
        self.actionAccounts.setIcon(icon)
        self.actionAccounts.setObjectName("actionAccounts")
        self.actionBanks = QtWidgets.QAction(frmMain)
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap(":/xulpymoney/bank.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionBanks.setIcon(icon8)
        self.actionBanks.setObjectName("actionBanks")
        self.actionInvestmentsClasses = QtWidgets.QAction(frmMain)
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap(":/xulpymoney/pie.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionInvestmentsClasses.setIcon(icon9)
        self.actionInvestmentsClasses.setObjectName("actionInvestmentsClasses")
        self.actionTransfer = QtWidgets.QAction(frmMain)
        icon10 = QtGui.QIcon()
        icon10.addPixmap(QtGui.QPixmap(":/xulpymoney/transfer.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionTransfer.setIcon(icon10)
        self.actionTransfer.setObjectName("actionTransfer")
        self.actionConcepts = QtWidgets.QAction(frmMain)
        icon11 = QtGui.QIcon()
        icon11.addPixmap(QtGui.QPixmap(":/xulpymoney/hucha.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionConcepts.setIcon(icon11)
        self.actionConcepts.setObjectName("actionConcepts")
        self.actionMemory = QtWidgets.QAction(frmMain)
        self.actionMemory.setIcon(icon10)
        self.actionMemory.setObjectName("actionMemory")
        self.actionSettings = QtWidgets.QAction(frmMain)
        icon12 = QtGui.QIcon()
        icon12.addPixmap(QtGui.QPixmap(":/xulpymoney/configure.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSettings.setIcon(icon12)
        self.actionSettings.setObjectName("actionSettings")
        self.actionHelp = QtWidgets.QAction(frmMain)
        icon13 = QtGui.QIcon()
        icon13.addPixmap(QtGui.QPixmap(":/xulpymoney/books.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionHelp.setIcon(icon13)
        self.actionHelp.setObjectName("actionHelp")
        self.actionInvestmentsOperations = QtWidgets.QAction(frmMain)
        icon14 = QtGui.QIcon()
        icon14.addPixmap(QtGui.QPixmap(":/xulpymoney/document-edit.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionInvestmentsOperations.setIcon(icon14)
        self.actionInvestmentsOperations.setObjectName("actionInvestmentsOperations")
        self.actionCalculator = QtWidgets.QAction(frmMain)
        icon15 = QtGui.QIcon()
        icon15.addPixmap(QtGui.QPixmap(":/xulpymoney/kcalc.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionCalculator.setIcon(icon15)
        self.actionCalculator.setObjectName("actionCalculator")
        self.actionSearch = QtWidgets.QAction(frmMain)
        icon16 = QtGui.QIcon()
        icon16.addPixmap(QtGui.QPixmap(":/xulpymoney/search.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSearch.setIcon(icon16)
        self.actionSearch.setObjectName("actionSearch")
        self.actionIndexesAll = QtWidgets.QAction(frmMain)
        icon17 = QtGui.QIcon()
        icon17.addPixmap(QtGui.QPixmap(":/xulpymoney/kmplot.jpg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionIndexesAll.setIcon(icon17)
        self.actionIndexesAll.setObjectName("actionIndexesAll")
        self.actionIbex35 = QtWidgets.QAction(frmMain)
        icon18 = QtGui.QIcon()
        icon18.addPixmap(QtGui.QPixmap(":/countries/spain.gif"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionIbex35.setIcon(icon18)
        self.actionIbex35.setObjectName("actionIbex35")
        self.actionEurostoxx50 = QtWidgets.QAction(frmMain)
        icon19 = QtGui.QIcon()
        icon19.addPixmap(QtGui.QPixmap(":/countries/eu.gif"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionEurostoxx50.setIcon(icon19)
        self.actionEurostoxx50.setObjectName("actionEurostoxx50")
        self.actionSP500 = QtWidgets.QAction(frmMain)
        icon20 = QtGui.QIcon()
        icon20.addPixmap(QtGui.QPixmap(":/countries/usa.gif"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSP500.setIcon(icon20)
        self.actionSP500.setObjectName("actionSP500")
        self.actionCAC40 = QtWidgets.QAction(frmMain)
        icon21 = QtGui.QIcon()
        icon21.addPixmap(QtGui.QPixmap(":/countries/france.gif"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionCAC40.setIcon(icon21)
        self.actionCAC40.setObjectName("actionCAC40")
        self.actionNasdaq100 = QtWidgets.QAction(frmMain)
        self.actionNasdaq100.setIcon(icon20)
        self.actionNasdaq100.setObjectName("actionNasdaq100")
        self.actionMC = QtWidgets.QAction(frmMain)
        self.actionMC.setIcon(icon18)
        self.actionMC.setObjectName("actionMC")
        self.actionXetra = QtWidgets.QAction(frmMain)
        icon22 = QtGui.QIcon()
        icon22.addPixmap(QtGui.QPixmap(":/countries/germany.gif"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionXetra.setIcon(icon22)
        self.actionXetra.setObjectName("actionXetra")
        self.actionProductsAutoUpdate = QtWidgets.QAction(frmMain)
        self.actionProductsAutoUpdate.setIcon(icon10)
        self.actionProductsAutoUpdate.setObjectName("actionProductsAutoUpdate")
        self.actionProductsObsolete = QtWidgets.QAction(frmMain)
        icon23 = QtGui.QIcon()
        icon23.addPixmap(QtGui.QPixmap(":/xulpymoney/checkbox0.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionProductsObsolete.setIcon(icon23)
        self.actionProductsObsolete.setObjectName("actionProductsObsolete")
        self.actionProductsUser = QtWidgets.QAction(frmMain)
        icon24 = QtGui.QIcon()
        icon24.addPixmap(QtGui.QPixmap(":/xulpymoney/keko.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionProductsUser.setIcon(icon24)
        self.actionProductsUser.setObjectName("actionProductsUser")
        self.actionCurrenciesAll = QtWidgets.QAction(frmMain)
        icon25 = QtGui.QIcon()
        icon25.addPixmap(QtGui.QPixmap(":/xulpymoney/Money.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionCurrenciesAll.setIcon(icon25)
        self.actionCurrenciesAll.setObjectName("actionCurrenciesAll")
        self.actionFavorites = QtWidgets.QAction(frmMain)
        self.actionFavorites.setIcon(icon5)
        self.actionFavorites.setObjectName("actionFavorites")
        self.actionProductsNotAutoUpdate = QtWidgets.QAction(frmMain)
        icon26 = QtGui.QIcon()
        icon26.addPixmap(QtGui.QPixmap(":/xulpymoney/editar.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionProductsNotAutoUpdate.setIcon(icon26)
        self.actionProductsNotAutoUpdate.setObjectName("actionProductsNotAutoUpdate")
        self.actionDividends = QtWidgets.QAction(frmMain)
        icon27 = QtGui.QIcon()
        icon27.addPixmap(QtGui.QPixmap(":/images/dinero.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionDividends.setIcon(icon27)
        self.actionDividends.setObjectName("actionDividends")
        self.actionWarrantsCall = QtWidgets.QAction(frmMain)
        self.actionWarrantsCall.setIcon(icon)
        self.actionWarrantsCall.setObjectName("actionWarrantsCall")
        self.actionWarrantsPut = QtWidgets.QAction(frmMain)
        self.actionWarrantsPut.setIcon(icon)
        self.actionWarrantsPut.setObjectName("actionWarrantsPut")
        self.actionWarrantsInline = QtWidgets.QAction(frmMain)
        self.actionWarrantsInline.setIcon(icon)
        self.actionWarrantsInline.setObjectName("actionWarrantsInline")
        self.actionBondsAll = QtWidgets.QAction(frmMain)
        icon28 = QtGui.QIcon()
        icon28.addPixmap(QtGui.QPixmap(":/xulpymoney/history2.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionBondsAll.setIcon(icon28)
        self.actionBondsAll.setObjectName("actionBondsAll")
        self.actionSharesAll = QtWidgets.QAction(frmMain)
        self.actionSharesAll.setIcon(icon17)
        self.actionSharesAll.setObjectName("actionSharesAll")
        self.actionBondsPublic = QtWidgets.QAction(frmMain)
        self.actionBondsPublic.setIcon(icon28)
        self.actionBondsPublic.setObjectName("actionBondsPublic")
        self.actionBondsPrivate = QtWidgets.QAction(frmMain)
        self.actionBondsPrivate.setIcon(icon28)
        self.actionBondsPrivate.setObjectName("actionBondsPrivate")
        self.actionWarrantsAll = QtWidgets.QAction(frmMain)
        self.actionWarrantsAll.setIcon(icon)
        self.actionWarrantsAll.setObjectName("actionWarrantsAll")
        self.actionISINDuplicado = QtWidgets.QAction(frmMain)
        icon29 = QtGui.QIcon()
        icon29.addPixmap(QtGui.QPixmap(":/xulpymoney/document-preview-archive.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionISINDuplicado.setIcon(icon29)
        self.actionISINDuplicado.setObjectName("actionISINDuplicado")
        self.actionPurgeAll = QtWidgets.QAction(frmMain)
        icon30 = QtGui.QIcon()
        icon30.addPixmap(QtGui.QPixmap(":/xulpymoney/tools-wizard.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionPurgeAll.setIcon(icon30)
        self.actionPurgeAll.setObjectName("actionPurgeAll")
        self.actionLATIBEX = QtWidgets.QAction(frmMain)
        self.actionLATIBEX.setIcon(icon18)
        self.actionLATIBEX.setObjectName("actionLATIBEX")
        self.actionProductsWithoutISIN = QtWidgets.QAction(frmMain)
        icon31 = QtGui.QIcon()
        icon31.addPixmap(QtGui.QPixmap(":/xulpymoney/gafas.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionProductsWithoutISIN.setIcon(icon31)
        self.actionProductsWithoutISIN.setObjectName("actionProductsWithoutISIN")
        self.actionETFAll = QtWidgets.QAction(frmMain)
        icon32 = QtGui.QIcon()
        icon32.addPixmap(QtGui.QPixmap(":/images/kmplot.jpg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionETFAll.setIcon(icon32)
        self.actionETFAll.setObjectName("actionETFAll")
        self.actionFundsAll = QtWidgets.QAction(frmMain)
        icon33 = QtGui.QIcon()
        icon33.addPixmap(QtGui.QPixmap(":/images/document-preview.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionFundsAll.setIcon(icon33)
        self.actionFundsAll.setObjectName("actionFundsAll")
        self.actionPriceUpdates = QtWidgets.QAction(frmMain)
        self.actionPriceUpdates.setIcon(icon10)
        self.actionPriceUpdates.setObjectName("actionPriceUpdates")
        self.actionProductsInvestmentActive = QtWidgets.QAction(frmMain)
        self.actionProductsInvestmentActive.setIcon(icon13)
        self.actionProductsInvestmentActive.setObjectName("actionProductsInvestmentActive")
        self.actionProductsInvestmentInactive = QtWidgets.QAction(frmMain)
        self.actionProductsInvestmentInactive.setIcon(icon13)
        self.actionProductsInvestmentInactive.setObjectName("actionProductsInvestmentInactive")
        self.actionIndexesObsolete = QtWidgets.QAction(frmMain)
        self.actionIndexesObsolete.setIcon(icon23)
        self.actionIndexesObsolete.setObjectName("actionIndexesObsolete")
        self.actionSharesObsolete = QtWidgets.QAction(frmMain)
        self.actionSharesObsolete.setIcon(icon23)
        self.actionSharesObsolete.setObjectName("actionSharesObsolete")
        self.actionETFObsolete = QtWidgets.QAction(frmMain)
        self.actionETFObsolete.setIcon(icon23)
        self.actionETFObsolete.setObjectName("actionETFObsolete")
        self.actionWarrantsObsolete = QtWidgets.QAction(frmMain)
        self.actionWarrantsObsolete.setIcon(icon23)
        self.actionWarrantsObsolete.setObjectName("actionWarrantsObsolete")
        self.actionFundsObsolete = QtWidgets.QAction(frmMain)
        self.actionFundsObsolete.setIcon(icon23)
        self.actionFundsObsolete.setObjectName("actionFundsObsolete")
        self.actionBondsObsolete = QtWidgets.QAction(frmMain)
        self.actionBondsObsolete.setIcon(icon23)
        self.actionBondsObsolete.setObjectName("actionBondsObsolete")
        self.actionGlobalReport = QtWidgets.QAction(frmMain)
        icon34 = QtGui.QIcon()
        icon34.addPixmap(QtGui.QPixmap(":/xulpymoney/new.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionGlobalReport.setIcon(icon34)
        self.actionGlobalReport.setObjectName("actionGlobalReport")
        self.actionSyncProducts = QtWidgets.QAction(frmMain)
        icon35 = QtGui.QIcon()
        icon35.addPixmap(QtGui.QPixmap(":/xulpymoney/database.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSyncProducts.setIcon(icon35)
        self.actionSyncProducts.setObjectName("actionSyncProducts")
        self.actionSimulations = QtWidgets.QAction(frmMain)
        icon36 = QtGui.QIcon()
        icon36.addPixmap(QtGui.QPixmap(":/xulpymoney/replication.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSimulations.setIcon(icon36)
        self.actionSimulations.setObjectName("actionSimulations")
        self.actionLastOperation = QtWidgets.QAction(frmMain)
        self.actionLastOperation.setIcon(icon29)
        self.actionLastOperation.setObjectName("actionLastOperation")
        self.actionOrders = QtWidgets.QAction(frmMain)
        self.actionOrders.setIcon(icon26)
        self.actionOrders.setObjectName("actionOrders")
        self.actionCuriosities = QtWidgets.QAction(frmMain)
        icon37 = QtGui.QIcon()
        icon37.addPixmap(QtGui.QPixmap(":/xulpymoney/curiosity.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionCuriosities.setIcon(icon37)
        self.actionCuriosities.setObjectName("actionCuriosities")
        self.actionInvestmentRanking = QtWidgets.QAction(frmMain)
        icon38 = QtGui.QIcon()
        icon38.addPixmap(QtGui.QPixmap(":/xulpymoney/crown.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionInvestmentRanking.setIcon(icon38)
        self.actionInvestmentRanking.setObjectName("actionInvestmentRanking")
        self.actionProductsWithoutQuotes = QtWidgets.QAction(frmMain)
        icon39 = QtGui.QIcon()
        icon39.addPixmap(QtGui.QPixmap(":/xulpymoney/alarm_clock.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionProductsWithoutQuotes.setIcon(icon39)
        self.actionProductsWithoutQuotes.setObjectName("actionProductsWithoutQuotes")
        self.actionProductsWithOldPrice = QtWidgets.QAction(frmMain)
        icon40 = QtGui.QIcon()
        icon40.addPixmap(QtGui.QPixmap(":/xulpymoney/expired.jpg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionProductsWithOldPrice.setIcon(icon40)
        self.actionProductsWithOldPrice.setObjectName("actionProductsWithOldPrice")
        self.menuAyuda.addAction(self.actionAbout)
        self.menuAyuda.addSeparator()
        self.menuAyuda.addAction(self.actionCuriosities)
        self.menuAyuda.addSeparator()
        self.menuAyuda.addAction(self.actionHelp)
        self.menuBancos.addAction(self.actionBanks)
        self.menuInformes.addAction(self.actionConcepts)
        self.menuInformes.addAction(self.actionDividendsReport)
        self.menuInformes.addAction(self.actionEvolutionReport)
        self.menuInformes.addAction(self.actionIndexRange)
        self.menuInformes.addAction(self.actionTotalReport)
        self.menuInformes.addSeparator()
        self.menuInformes.addAction(self.actionGlobalReport)
        self.menuCuentas.addAction(self.actionAccounts)
        self.menuCuentas.addSeparator()
        self.menuCuentas.addAction(self.actionTransfer)
        self.menuInversiones.addAction(self.actionInvestments)
        self.menuInversiones.addSeparator()
        self.menuInversiones.addAction(self.actionOrders)
        self.menuInversiones.addSeparator()
        self.menuInversiones.addAction(self.actionInvestmentsClasses)
        self.menuInversiones.addSeparator()
        self.menuInversiones.addAction(self.actionLastOperation)
        self.menuInversiones.addAction(self.actionInvestmentsOperations)
        self.menuInversiones.addSeparator()
        self.menuInversiones.addAction(self.actionCalculator)
        self.menuInversiones.addSeparator()
        self.menuInversiones.addAction(self.actionInvestmentRanking)
        self.menuXulpymoney.addAction(self.actionMemory)
        self.menuXulpymoney.addSeparator()
        self.menuXulpymoney.addAction(self.actionAuxiliarTables)
        self.menuXulpymoney.addSeparator()
        self.menuXulpymoney.addAction(self.actionSettings)
        self.menuXulpymoney.addSeparator()
        self.menuXulpymoney.addAction(self.actionSimulations)
        self.menuXulpymoney.addSeparator()
        self.menuXulpymoney.addAction(self.actionExit)
        self.menuIndexes.addAction(self.actionEurostoxx50)
        self.menuIndexes.addAction(self.actionIbex35)
        self.menuIndexes.addAction(self.actionMC)
        self.menuIndexes.addAction(self.actionLATIBEX)
        self.menuIndexes.addAction(self.actionSP500)
        self.menuIndexes.addAction(self.actionCAC40)
        self.menuIndexes.addAction(self.actionNasdaq100)
        self.menuIndexes.addAction(self.actionXetra)
        self.menuIndexes.addSeparator()
        self.menuIndexes.addAction(self.actionIndexesAll)
        self.menuIndexes.addSeparator()
        self.menuIndexes.addAction(self.actionIndexesObsolete)
        self.menuMaintenance.addSeparator()
        self.menuMaintenance.addAction(self.actionPurgeAll)
        self.menuReports.addAction(self.actionDividends)
        self.menuReports.addSeparator()
        self.menuReports.addAction(self.actionProductsWithoutQuotes)
        self.menuReports.addAction(self.actionProductsWithOldPrice)
        self.menuReports.addSeparator()
        self.menuReports.addAction(self.actionProductsAutoUpdate)
        self.menuReports.addAction(self.actionProductsNotAutoUpdate)
        self.menuReports.addSeparator()
        self.menuReports.addAction(self.actionProductsInvestmentActive)
        self.menuReports.addAction(self.actionProductsInvestmentInactive)
        self.menuReports.addSeparator()
        self.menuReports.addAction(self.actionProductsUser)
        self.menuReports.addAction(self.actionProductsObsolete)
        self.menuReports.addSeparator()
        self.menuReports.addAction(self.actionProductsWithoutISIN)
        self.menuReports.addAction(self.actionISINDuplicado)
        self.menuShares.addAction(self.actionSharesAll)
        self.menuShares.addSeparator()
        self.menuShares.addAction(self.actionSharesObsolete)
        self.menuCurrencies.addAction(self.actionCurrenciesAll)
        self.menuBonds.addAction(self.actionBondsPrivate)
        self.menuBonds.addAction(self.actionBondsPublic)
        self.menuBonds.addAction(self.actionBondsAll)
        self.menuBonds.addSeparator()
        self.menuBonds.addAction(self.actionBondsObsolete)
        self.menuFunds.addAction(self.actionFundsAll)
        self.menuFunds.addSeparator()
        self.menuFunds.addAction(self.actionFundsObsolete)
        self.menuETF.addAction(self.actionETFAll)
        self.menuETF.addSeparator()
        self.menuETF.addAction(self.actionETFObsolete)
        self.menuWarrants.addAction(self.actionWarrantsInline)
        self.menuWarrants.addAction(self.actionWarrantsPut)
        self.menuWarrants.addAction(self.actionWarrantsCall)
        self.menuWarrants.addSeparator()
        self.menuWarrants.addAction(self.actionWarrantsAll)
        self.menuWarrants.addSeparator()
        self.menuWarrants.addAction(self.actionWarrantsObsolete)
        self.menuProducts.addAction(self.menuIndexes.menuAction())
        self.menuProducts.addAction(self.menuShares.menuAction())
        self.menuProducts.addAction(self.menuETF.menuAction())
        self.menuProducts.addAction(self.menuWarrants.menuAction())
        self.menuProducts.addAction(self.menuFunds.menuAction())
        self.menuProducts.addAction(self.menuBonds.menuAction())
        self.menuProducts.addAction(self.menuCurrencies.menuAction())
        self.menuProducts.addSeparator()
        self.menuProducts.addAction(self.menuReports.menuAction())
        self.menuProducts.addSeparator()
        self.menuProducts.addAction(self.menuMaintenance.menuAction())
        self.menuProducts.addSeparator()
        self.menuProducts.addAction(self.actionFavorites)
        self.menuProducts.addAction(self.actionSearch)
        self.menuProducts.addSeparator()
        self.menuProducts.addAction(self.actionPriceUpdates)
        self.menuProducts.addSeparator()
        self.menuProducts.addAction(self.actionSyncProducts)
        self.menuBar.addAction(self.menuXulpymoney.menuAction())
        self.menuBar.addAction(self.menuBancos.menuAction())
        self.menuBar.addAction(self.menuCuentas.menuAction())
        self.menuBar.addAction(self.menuInversiones.menuAction())
        self.menuBar.addAction(self.menuInformes.menuAction())
        self.menuBar.addAction(self.menuProducts.menuAction())
        self.menuBar.addAction(self.menuAyuda.menuAction())
        self.toolBar.addAction(self.actionBanks)
        self.toolBar.addAction(self.actionAccounts)
        self.toolBar.addAction(self.actionInvestments)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionOrders)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionIndexRange)
        self.toolBar.addAction(self.actionConcepts)
        self.toolBar.addAction(self.actionEvolutionReport)
        self.toolBar.addAction(self.actionTotalReport)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionPriceUpdates)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionLastOperation)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionCalculator)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionFavorites)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionExit)

        self.retranslateUi(frmMain)
        QtCore.QMetaObject.connectSlotsByName(frmMain)

    def retranslateUi(self, frmMain):
        _translate = QtCore.QCoreApplication.translate
        self.menuAyuda.setTitle(_translate("frmMain", "He&lp"))
        self.menuBancos.setTitle(_translate("frmMain", "&Banks"))
        self.menuInformes.setTitle(_translate("frmMain", "&Reports"))
        self.menuCuentas.setTitle(_translate("frmMain", "A&ccounts"))
        self.menuInversiones.setTitle(_translate("frmMain", "&Investments"))
        self.menuXulpymoney.setTitle(_translate("frmMain", "&Xulpymoney"))
        self.menuProducts.setTitle(_translate("frmMain", "Prod&ucts"))
        self.menuIndexes.setTitle(_translate("frmMain", "&Indexes"))
        self.menuMaintenance.setTitle(_translate("frmMain", "&Maintenance"))
        self.menuReports.setTitle(_translate("frmMain", "&Reports"))
        self.menuShares.setTitle(_translate("frmMain", "&Shares"))
        self.menuCurrencies.setTitle(_translate("frmMain", "&Currencies"))
        self.menuBonds.setTitle(_translate("frmMain", "&Bonds"))
        self.menuFunds.setTitle(_translate("frmMain", "&Funds"))
        self.menuETF.setTitle(_translate("frmMain", "&ETF"))
        self.menuWarrants.setTitle(_translate("frmMain", "&Warrants"))
        self.toolBar.setWindowTitle(_translate("frmMain", "toolBar"))
        self.actionExit.setText(_translate("frmMain", "E&xit"))
        self.actionExit.setToolTip(_translate("frmMain", "Exit"))
        self.actionExit.setShortcut(_translate("frmMain", "Alt+Esc"))
        self.actionAbout.setText(_translate("frmMain", "&About"))
        self.actionAbout.setToolTip(_translate("frmMain", "About"))
        self.actionAbout.setShortcut(_translate("frmMain", "F2"))
        self.actionIndexRange.setText(_translate("frmMain", "&Index range"))
        self.actionIndexRange.setToolTip(_translate("frmMain", "Index range"))
        self.actionInvestments.setText(_translate("frmMain", "&Investments"))
        self.actionInvestments.setToolTip(_translate("frmMain", "Investments"))
        self.actionAuxiliarTables.setText(_translate("frmMain", "&Auxiliar tables"))
        self.actionAuxiliarTables.setToolTip(_translate("frmMain", "Auxiliar tables"))
        self.actionDividendsReport.setText(_translate("frmMain", "&Dividends report"))
        self.actionEvolutionReport.setText(_translate("frmMain", "&Evolution report"))
        self.actionEvolutionReport.setToolTip(_translate("frmMain", "Evolution report"))
        self.actionTotalReport.setText(_translate("frmMain", "&Total report"))
        self.actionTotalReport.setToolTip(_translate("frmMain", "Total report"))
        self.actionTotalReport.setShortcut(_translate("frmMain", "F10"))
        self.actionAccounts.setText(_translate("frmMain", "&Accounts"))
        self.actionAccounts.setToolTip(_translate("frmMain", "Accounts"))
        self.actionBanks.setText(_translate("frmMain", "&Banks"))
        self.actionBanks.setToolTip(_translate("frmMain", "Banks"))
        self.actionInvestmentsClasses.setText(_translate("frmMain", "Investment types &report"))
        self.actionTransfer.setText(_translate("frmMain", "&Transfer"))
        self.actionTransfer.setToolTip(_translate("frmMain", "Transfer"))
        self.actionConcepts.setText(_translate("frmMain", "&Concepts"))
        self.actionConcepts.setToolTip(_translate("frmMain", "Concepts"))
        self.actionMemory.setText(_translate("frmMain", "&Update memory"))
        self.actionMemory.setToolTip(_translate("frmMain", "Update memory"))
        self.actionSettings.setText(_translate("frmMain", "&Settings"))
        self.actionSettings.setToolTip(_translate("frmMain", "Settings"))
        self.actionHelp.setText(_translate("frmMain", "&Help"))
        self.actionHelp.setToolTip(_translate("frmMain", "Help"))
        self.actionHelp.setShortcut(_translate("frmMain", "F1"))
        self.actionInvestmentsOperations.setText(_translate("frmMain", "I&nvestment operations list"))
        self.actionInvestmentsOperations.setToolTip(_translate("frmMain", "Investment operations list"))
        self.actionCalculator.setText(_translate("frmMain", "&Order calculator"))
        self.actionCalculator.setToolTip(_translate("frmMain", "Order calculator"))
        self.actionSearch.setText(_translate("frmMain", "Search"))
        self.actionSearch.setShortcut(_translate("frmMain", "F2"))
        self.actionIndexesAll.setText(_translate("frmMain", "&All Indexes"))
        self.actionIndexesAll.setShortcut(_translate("frmMain", "Ctrl+I"))
        self.actionIbex35.setText(_translate("frmMain", "&Ibex 35"))
        self.actionEurostoxx50.setText(_translate("frmMain", "&Eurostoxx 50"))
        self.actionSP500.setText(_translate("frmMain", "&S&&P 500"))
        self.actionCAC40.setText(_translate("frmMain", "&CAC 40"))
        self.actionNasdaq100.setText(_translate("frmMain", "&Nasdaq 100"))
        self.actionMC.setText(_translate("frmMain", "&Mercado Continuo"))
        self.actionXetra.setText(_translate("frmMain", "&Xetra"))
        self.actionProductsAutoUpdate.setText(_translate("frmMain", "&Products with auto update"))
        self.actionProductsAutoUpdate.setToolTip(_translate("frmMain", "Products with auto update"))
        self.actionProductsObsolete.setText(_translate("frmMain", "&Obsolete products"))
        self.actionProductsObsolete.setToolTip(_translate("frmMain", "Obsolete products"))
        self.actionProductsUser.setText(_translate("frmMain", "&User products"))
        self.actionProductsUser.setToolTip(_translate("frmMain", "User products"))
        self.actionCurrenciesAll.setText(_translate("frmMain", "&All currencies"))
        self.actionCurrenciesAll.setToolTip(_translate("frmMain", "All currencies"))
        self.actionFavorites.setText(_translate("frmMain", "S&how favorites"))
        self.actionFavorites.setToolTip(_translate("frmMain", "Show favorites"))
        self.actionProductsNotAutoUpdate.setText(_translate("frmMain", "Products &without auto update"))
        self.actionProductsNotAutoUpdate.setToolTip(_translate("frmMain", "Products without auto update"))
        self.actionDividends.setText(_translate("frmMain", "&Biggest dividends"))
        self.actionDividends.setToolTip(_translate("frmMain", "Biggest dividends"))
        self.actionWarrantsCall.setText(_translate("frmMain", "All &call warrants"))
        self.actionWarrantsPut.setText(_translate("frmMain", "All &put warrants"))
        self.actionWarrantsInline.setText(_translate("frmMain", "&All inline warrants"))
        self.actionBondsAll.setText(_translate("frmMain", "All &bonds"))
        self.actionBondsAll.setToolTip(_translate("frmMain", "All bonds"))
        self.actionSharesAll.setText(_translate("frmMain", "&All shares"))
        self.actionSharesAll.setToolTip(_translate("frmMain", "All shares"))
        self.actionBondsPublic.setText(_translate("frmMain", "All &public bonds"))
        self.actionBondsPublic.setToolTip(_translate("frmMain", "All public bonds"))
        self.actionBondsPrivate.setText(_translate("frmMain", "&All private bonds"))
        self.actionBondsPrivate.setToolTip(_translate("frmMain", "All private bonds"))
        self.actionWarrantsAll.setText(_translate("frmMain", "All &warrants"))
        self.actionWarrantsAll.setToolTip(_translate("frmMain", "All warrants"))
        self.actionISINDuplicado.setText(_translate("frmMain", "&Duplicated ISIN products"))
        self.actionISINDuplicado.setToolTip(_translate("frmMain", "Duplicated ISIN products"))
        self.actionPurgeAll.setText(_translate("frmMain", "&Purge all investments"))
        self.actionPurgeAll.setToolTip(_translate("frmMain", "Purge all investments"))
        self.actionLATIBEX.setText(_translate("frmMain", "&LATIBEX"))
        self.actionLATIBEX.setToolTip(_translate("frmMain", "LATIBEX"))
        self.actionProductsWithoutISIN.setText(_translate("frmMain", "Produ&cts without ISIN"))
        self.actionProductsWithoutISIN.setToolTip(_translate("frmMain", "Products without ISIN"))
        self.actionETFAll.setText(_translate("frmMain", "&All ETF"))
        self.actionFundsAll.setText(_translate("frmMain", "&All funds"))
        self.actionPriceUpdates.setText(_translate("frmMain", "&Price updates"))
        self.actionPriceUpdates.setToolTip(_translate("frmMain", "Price updates"))
        self.actionProductsInvestmentActive.setText(_translate("frmMain", "P&roducts of active investment"))
        self.actionProductsInvestmentActive.setToolTip(_translate("frmMain", "Products of active investment"))
        self.actionProductsInvestmentInactive.setText(_translate("frmMain", "Products of &inactive investment"))
        self.actionProductsInvestmentInactive.setToolTip(_translate("frmMain", "Products of inactive investment"))
        self.actionIndexesObsolete.setText(_translate("frmMain", "&Obsolete Indexes"))
        self.actionIndexesObsolete.setToolTip(_translate("frmMain", "Obsolete Indexes"))
        self.actionSharesObsolete.setText(_translate("frmMain", "&Obsolete shares"))
        self.actionSharesObsolete.setToolTip(_translate("frmMain", "Obsolete shares"))
        self.actionETFObsolete.setText(_translate("frmMain", "&Obsolete ETFs"))
        self.actionETFObsolete.setToolTip(_translate("frmMain", "Obsolete ETFs"))
        self.actionWarrantsObsolete.setText(_translate("frmMain", "&Obsolete warrants"))
        self.actionWarrantsObsolete.setToolTip(_translate("frmMain", "Obsolete warrants"))
        self.actionFundsObsolete.setText(_translate("frmMain", "&Obsolete funds"))
        self.actionFundsObsolete.setToolTip(_translate("frmMain", "Obsolete funds"))
        self.actionBondsObsolete.setText(_translate("frmMain", "&Obsolete bonds"))
        self.actionBondsObsolete.setToolTip(_translate("frmMain", "Obsolete bonds"))
        self.actionGlobalReport.setText(_translate("frmMain", "&Generate global report"))
        self.actionGlobalReport.setToolTip(_translate("frmMain", "Generate global report"))
        self.actionSyncProducts.setText(_translate("frmMain", "Sync products from &other Xulpymoney"))
        self.actionSyncProducts.setToolTip(_translate("frmMain", "Move products information to another database"))
        self.actionSyncProducts.setShortcut(_translate("frmMain", "F9"))
        self.actionSimulations.setText(_translate("frmMain", "S&imulations"))
        self.actionSimulations.setToolTip(_translate("frmMain", "Simulations"))
        self.actionSimulations.setShortcut(_translate("frmMain", "Ctrl+S"))
        self.actionLastOperation.setText(_translate("frmMain", "&Last operation"))
        self.actionLastOperation.setToolTip(_translate("frmMain", "Last operation"))
        self.actionOrders.setText(_translate("frmMain", "&Market orders"))
        self.actionOrders.setToolTip(_translate("frmMain", "Market orders"))
        self.actionCuriosities.setText(_translate("frmMain", "&Curiosities"))
        self.actionCuriosities.setToolTip(_translate("frmMain", "Curiosities"))
        self.actionInvestmentRanking.setText(_translate("frmMain", "In&vestment ranking"))
        self.actionInvestmentRanking.setToolTip(_translate("frmMain", "Investment ranking"))
        self.actionProductsWithoutQuotes.setText(_translate("frmMain", "Product&s without price"))
        self.actionProductsWithoutQuotes.setToolTip(_translate("frmMain", "Products without price"))
        self.actionProductsWithOldPrice.setText(_translate("frmMain", "Products wit&h old price"))
        self.actionProductsWithOldPrice.setToolTip(_translate("frmMain", "Products with old price"))

import xulpymoney_rc
