DESTDIR ?= /

PREFIXBIN=$(DESTDIR)/usr/bin
PREFIXLIB=$(DESTDIR)/usr/lib/xulpymoney
PREFIXSHARE=$(DESTDIR)/usr/share/xulpymoney
PREFIXPIXMAPS=$(DESTDIR)/usr/share/pixmaps
PREFIXAPPLICATIONS=$(DESTDIR)/usr/share/applications

all: compile install
compile:
	pyrcc5  images/xulpymoney.qrc > images/xulpymoney_rc.py  &
	pyuic5 ui/frmAbout.ui > ui/Ui_frmAbout.py &
	pyuic5 ui/frmAccess.ui > ui/Ui_frmAccess.py &
	pyuic5 ui/frmDPSAdd.ui > ui/Ui_frmDPSAdd.py &
	pyuic5 ui/frmHelp.ui > ui/Ui_frmHelp.py &
	pyuic5 ui/frmInit.ui > ui/Ui_frmInit.py &
	pyuic5 ui/frmMain.ui > ui/Ui_frmMain.py &
	pyuic5 ui/frmSplit.ui > ui/Ui_frmSplit.py &
	pyuic5 ui/frmAccountOperationsAdd.ui > ui/Ui_frmAccountOperationsAdd.py &
	pyuic5 ui/frmAuxiliarTables.ui > ui/Ui_frmAuxiliarTables.py &
	pyuic5 ui/wdgBanks.ui > ui/Ui_wdgBanks.py &
	pyuic5 ui/wdgCalculator.ui > ui/Ui_wdgCalculator.py &
	pyuic5 ui/wdgConcepts.ui > ui/Ui_wdgConcepts.py &
	pyuic5 ui/wdgConceptsHistorical.ui > ui/Ui_wdgConceptsHistorical.py &
	pyuic5 ui/wdgAccounts.ui > ui/Ui_wdgAccounts.py &
	pyuic5 ui/wdgDisReinvest.ui > ui/Ui_wdgDisReinvest.py &
	pyuic5 ui/frmAccountsReport.ui > ui/Ui_frmAccountsReport.py &
	pyuic5 ui/wdgInvestmentClasses.ui > ui/Ui_wdgInvestmentClasses.py &
	pyuic5 ui/wdgDividendsReport.ui > ui/Ui_wdgDividendsReport.py &
	pyuic5 ui/wdgAPR.ui > ui/Ui_wdgAPR.py &
	pyuic5 ui/wdgIndexRange.ui > ui/Ui_wdgIndexRange.py &
	pyuic5 ui/wdgInvestments.ui > ui/Ui_wdgInvestments.py &
	pyuic5 ui/wdgInvestmentsRanking.ui > ui/Ui_wdgInvestmentsRanking.py &
	pyuic5 ui/wdgLastCurrent.ui > ui/Ui_wdgLastCurrent.py &
	pyuic5 ui/wdgOrders.ui > ui/Ui_wdgOrders.py &
	pyuic5 ui/wdgOrdersAdd.ui > ui/Ui_wdgOrdersAdd.py &
	pyuic5 ui/frmDividendsAdd.ui > ui/Ui_frmDividendsAdd.py &
	pyuic5 ui/frmInvestmentReport.ui > ui/Ui_frmInvestmentReport.py &
	pyuic5 ui/frmInvestmentOperationsAdd.ui > ui/Ui_frmInvestmentOperationsAdd.py &
	pyuic5 ui/frmSellingPoint.ui > ui/Ui_frmSellingPoint.py &
	pyuic5 ui/frmSettings.ui > ui/Ui_frmSettings.py &
	pyuic5 ui/frmCreditCardsAdd.ui > ui/Ui_frmCreditCardsAdd.py &
	pyuic5 ui/frmTransfer.ui > ui/Ui_frmTransfer.py &
	pyuic5 ui/frmSharesTransfer.ui > ui/Ui_frmSharesTransfer.py &
	pyuic5 ui/wdgTotal.ui > ui/Ui_wdgTotal.py &
	pyuic5 ui/frmProductReport.ui > ui/Ui_frmProductReport.py &
	pyuic5 ui/frmQuotesIBM.ui > ui/Ui_frmQuotesIBM.py &
	pyuic5 ui/frmSelector.ui > ui/Ui_frmSelector.py &
	pyuic5 ui/frmEstimationsAdd.ui > ui/Ui_frmEstimationsAdd.py &
	pyuic5 ui/wdgCuriosity.ui > ui/Ui_wdgCuriosity.py &
	pyuic5 ui/wdgCuriosities.ui > ui/Ui_wdgCuriosities.py &
	pyuic5 ui/wdgDatetime.ui > ui/Ui_wdgDatetime.py &
	pyuic5 ui/wdgProducts.ui > ui/Ui_wdgProducts.py &
	pyuic5 ui/wdgQuotesUpdate.ui > ui/Ui_wdgQuotesUpdate.py &
	pyuic5 ui/wdgSimulations.ui > ui/Ui_wdgSimulations.py &
	pyuic5 ui/wdgSimulationsAdd.ui > ui/Ui_wdgSimulationsAdd.py &
	pyuic5 ui/wdgSource.ui > ui/Ui_wdgSource.py &
	pyuic5 ui/wdgInvestmentsOperations.ui > ui/Ui_wdgInvestmentsOperations.py &
	pyuic5 ui/wdgMergeCodes.ui > ui/Ui_wdgMergeCodes.py &
	pyuic5 ui/wdgYearMonth.ui > ui/Ui_wdgYearMonth.py &
	pyuic5 ui/wdgYear.ui > ui/Ui_wdgYear.py &
	sleep 2
	wait
install:
	install -o root -d $(PREFIXBIN)
	install -o root -d $(PREFIXLIB)
	install -o root -d $(PREFIXSHARE)
	install -o root -d $(PREFIXSHARE)/sql
	install -o root -d $(PREFIXPIXMAPS)
	install -o root -d $(PREFIXAPPLICATIONS)

	install -m 755 -o root xulpymoney.py $(PREFIXBIN)/xulpymoney
	install -m 755 -o root xulpymoney_init.py $(PREFIXBIN)/xulpymoney_init
	install -m 755 -o root xulpymoney_sync_quotes.py $(PREFIXBIN)/xulpymoney_sync_quotes
	install -m 755 -o root xulpymoney_simulation_indexrange.py $(PREFIXBIN)/xulpymoney_simulation_indexrange
	install -m 755 -o root sources/source_morningstar.py $(PREFIXBIN)/xulpymoney_source_morningstar
	install -m 755 -o root sources/source_yahoohistorical.py $(PREFIXBIN)/xulpymoney_source_yahoo_historical
	install -m 755 -o root test/xulpymoney_test.py $(PREFIXBIN)/xulpymoney_test
	install -m 644 -o root ui/*.py libxulpymoney.py libdbupdates.py libsources.py libodfgenerator.py images/*.py  $(PREFIXLIB)
	install -m 644 -o root i18n/*.qm $(PREFIXLIB)
	install -m 644 -o root sources/*.py $(PREFIXLIB)
	install -m 644 -o root xulpymoney.desktop $(PREFIXAPPLICATIONS)
	install -m 644 -o root images/coins.png $(PREFIXPIXMAPS)/xulpymoney.png
	install -m 644 -o root GPL-3.txt CHANGELOG.txt AUTHORS.txt RELEASES.txt $(PREFIXSHARE)
	install -m 644 -o root sql/xulpymoney.sql $(PREFIXSHARE)/sql
	install -m 644 -o root odf/report.odt $(PREFIXSHARE)

uninstall:
	rm $(PREFIXBIN)/xulpymoney*
	rm -Rf $(PREFIXLIB)
	rm -Rf $(PREFIXSHARE)
	rm -fr $(PREFIXPIXMAPS)/xulpymoney.png
	rm -fr $(PREFIXAPPLICATIONS)/xulpymoney.desktop

help:
	install -o root -d $(PREFIXLIB)
	pylupdate5 -noobsolete -verbose  xulpymoney.pro
	lrelease xulpymoney.pro
	install -m 644 -o root i18n/*.qm $(PREFIXLIB)
