DESTDIR ?= /

PREFIXBIN=$(DESTDIR)/usr/bin
PREFIXLIB=$(DESTDIR)/usr/lib/xulpymoney
PREFIXSHARE=$(DESTDIR)/usr/share/xulpymoney
PREFIXPIXMAPS=$(DESTDIR)/usr/share/pixmaps
PREFIXAPPLICATIONS=$(DESTDIR)/usr/share/applications

all: compile install
compile:
	pyrcc4 -py3 images/xulpymoney.qrc > images/xulpymoney_rc.py 
	pyuic4 ui/frmAbout.ui > ui/Ui_frmAbout.py &
	pyuic4 ui/frmAccess.ui > ui/Ui_frmAccess.py &
	pyuic4 ui/frmDPSAdd.ui > ui/Ui_frmDPSAdd.py &
	pyuic4 ui/frmHelp.ui > ui/Ui_frmHelp.py &
	pyuic4 ui/frmInit.ui > ui/Ui_frmInit.py &
	pyuic4 ui/frmMain.ui > ui/Ui_frmMain.py &
	pyuic4 ui/frmSplit.ui > ui/Ui_frmSplit.py &
	pyuic4 ui/frmAccountOperationsAdd.ui > ui/Ui_frmAccountOperationsAdd.py &
	pyuic4 ui/frmAuxiliarTables.ui > ui/Ui_frmAuxiliarTables.py &
	pyuic4 ui/wdgBanks.ui > ui/Ui_wdgBanks.py &
	pyuic4 ui/wdgCalculator.ui > ui/Ui_wdgCalculator.py &
	pyuic4 ui/wdgConcepts.ui > ui/Ui_wdgConcepts.py &
	pyuic4 ui/wdgConceptsHistorical.ui > ui/Ui_wdgConceptsHistorical.py &
	pyuic4 ui/wdgAccounts.ui > ui/Ui_wdgAccounts.py &
	pyuic4 ui/wdgDisReinvest.ui > ui/Ui_wdgDisReinvest.py &
	pyuic4 ui/frmAccountsReport.ui > ui/Ui_frmAccountsReport.py &
	pyuic4 ui/wdgInvestmentClasses.ui > ui/Ui_wdgInvestmentClasses.py &
	pyuic4 ui/wdgJointReport.ui > ui/Ui_wdgJointReport.py &
	pyuic4 ui/wdgDividendsReport.ui > ui/Ui_wdgDividendsReport.py &
	pyuic4 ui/wdgAPR.ui > ui/Ui_wdgAPR.py &
	pyuic4 ui/wdgIndexRange.ui > ui/Ui_wdgIndexRange.py &
	pyuic4 ui/wdgInvestments.ui > ui/Ui_wdgInvestments.py &
	pyuic4 ui/frmDividendsAdd.ui > ui/Ui_frmDividendsAdd.py &
	pyuic4 ui/frmInvestmentReport.ui > ui/Ui_frmInvestmentReport.py &
	pyuic4 ui/frmInvestmentOperationsAdd.ui > ui/Ui_frmInvestmentOperationsAdd.py &
	pyuic4 ui/frmSellingPoint.ui > ui/Ui_frmSellingPoint.py &
	pyuic4 ui/frmSettings.ui > ui/Ui_frmSettings.py &
	pyuic4 ui/frmCreditCardsAdd.ui > ui/Ui_frmCreditCardsAdd.py &
	pyuic4 ui/frmTransfer.ui > ui/Ui_frmTransfer.py &
	pyuic4 ui/frmSharesTransfer.ui > ui/Ui_frmSharesTransfer.py &
	pyuic4 ui/wdgTotal.ui > ui/Ui_wdgTotal.py &
	pyuic4 ui/frmProductReport.ui > ui/Ui_frmProductReport.py &
	pyuic4 ui/frmQuotesIBM.ui > ui/Ui_frmQuotesIBM.py &
	pyuic4 ui/frmSelector.ui > ui/Ui_frmSelector.py &
	pyuic4 ui/frmEstimationsAdd.ui > ui/Ui_frmEstimationsAdd.py
	pyuic4 ui/wdgDatetime.ui > ui/Ui_wdgDatetime.py
	pyuic4 ui/wdgProducts.ui > ui/Ui_wdgProducts.py
	pyuic4 ui/wdgInvestmentsOperations.ui > ui/Ui_wdgInvestmentsOperations.py
	pyuic4 ui/wdgMergeCodes.ui > ui/Ui_wdgMergeCodes.py
	pyuic4 ui/wdgYearMonth.ui > ui/Ui_wdgYearMonth.py
	pyuic4 ui/wdgYear.ui > ui/Ui_wdgYear.py
	pylupdate4 -noobsolete -verbose  xulpymoney.pro
	lrelease xulpymoney.pro

install:
	install -o root -d $(PREFIXBIN)
	install -o root -d $(PREFIXLIB)
	install -o root -d $(PREFIXSHARE)
	install -o root -d $(PREFIXSHARE)/sql
	install -o root -d $(PREFIXPIXMAPS)
	install -o root -d $(PREFIXAPPLICATIONS)

	install -m 755 -o root xulpymoney.py $(PREFIXBIN)/xulpymoney
	install -m 755 -o root xulpymoney_init.py $(PREFIXBIN)/xulpymoney_init
	install -m 644 -o root ui/*.py libxulpymoney.py libsources.py images/*.py  $(PREFIXLIB)
	install -m 644 -o root i18n/*.qm $(PREFIXLIB)
	install -m 644 -o root sources/*.py $(PREFIXLIB)


	install -m 644 -o root xulpymoney.desktop $(PREFIXAPPLICATIONS)
	install -m 644 -o root images/dinero.png $(PREFIXPIXMAPS)/xulpymoney.png

	install -m 644 -o root GPL-3.txt CHANGELOG.txt AUTHORS.txt RELEASES.txt $(PREFIXSHARE)
	install -m 644 -o root sql/xulpymoney.sql $(PREFIXSHARE)/sql
	install -m 644 -o root images/kmplot.jpg $(PREFIXPIXMAPS)/mystocks.jpg

uninstall:
	rm $(PREFIXBIN)/xulpymoney
	rm -Rf $(PREFIXLIB)
	rm -Rf $(PREFIXSHARE)
	rm -fr $(PREFIXPIXMAPS)/xulpymoney.png
	rm -fr $(PREFIXAPPLICATIONS)/xulpymoney.desktop
