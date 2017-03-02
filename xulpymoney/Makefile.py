#!/usr/bin/python3
import argparse
import datetime
from subprocess import call
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import cpu_count

def shell(*args):
	print(" ".join(args))
	call(args,shell=True)

if __name__ == '__main__':
	start=datetime.datetime.now()
	parser=argparse.ArgumentParser(prog='Makefile.py', description='Makefile in python', epilog="Developed by Mariano Muñoz", formatter_class=argparse.RawTextHelpFormatter)
	parser.add_argument('--man', help="Generate docs and i18n",action="store_true",default=False)
	parser.add_argument('--destdir', help="Dir to installn",action="store",default="/")
	parser.add_argument('--uninstall', help="Uninstall",action="store_true",default=False)
	parser.add_argument('--dist_sources', help="Make a sources tar", action="store_true",default=False)
	args=parser.parse_args()

	prefixbin=args.destdir+"/usr/bin"
	prefixlib=args.destdir+"/usr/lib/xulpymoney"
	prefixshare=args.destdir+"/usr/share/xulpymoney"
	prefixpixmaps=args.destdir+"/usr/share/pixmaps"
	prefixapplications=args.destdir+"/usr/share/applications"

	if args.man==True:
		shell("pylupdate5 -noobsolete -verbose xulpymoney.pro")
		shell("lrelease xulpymoney.pro")
	elif args.uninstall==True:
		shell("rm " + prefixbin + "/xulpymoney*")
		shell("rm -Rf " + prefixlib)
		shell("rm -Rf " + prefixshare)
		shell("rm -fr " + prefixpixmaps + "/xulpymoney.png")
		shell("rm -fr " + prefixapplications +"/xulpymoney.desktop")
	elif args.dist_sources==True:
		shell("python3 setup2.py sdist")
	else:
		futures=[]
		with ProcessPoolExecutor(max_workers=cpu_count()+1) as executor:
			futures.append(executor.submit(shell, "pyrcc5 images/xulpymoney.qrc -o images/xulpymoney_rc.py"))
			futures.append(executor.submit(shell, "pyuic5 ui/frmAbout.ui -o ui/Ui_frmAbout.py"))
			futures.append(executor.submit(shell, "pyuic5 ui/frmAccess.ui -o ui/Ui_frmAccess.py"))
			futures.append(executor.submit(shell, "pyuic5 ui/frmDPSAdd.ui -o ui/Ui_frmDPSAdd.py"))
			futures.append(executor.submit(shell, "pyuic5 ui/frmHelp.ui -o ui/Ui_frmHelp.py"))
			futures.append(executor.submit(shell, "pyuic5 ui/frmInit.ui -o ui/Ui_frmInit.py"))
			futures.append(executor.submit(shell, "pyuic5 ui/frmMain.ui -o ui/Ui_frmMain.py"))
			futures.append(executor.submit(shell, "pyuic5 ui/frmSplit.ui -o ui/Ui_frmSplit.py"))
			futures.append(executor.submit(shell, "pyuic5 ui/frmAccountOperationsAdd.ui -o ui/Ui_frmAccountOperationsAdd.py"))
			futures.append(executor.submit(shell, "pyuic5 ui/frmAuxiliarTables.ui -o ui/Ui_frmAuxiliarTables.py"))
			futures.append(executor.submit(shell, "pyuic5 ui/wdgBanks.ui -o ui/Ui_wdgBanks.py"))
			futures.append(executor.submit(shell, "pyuic5 ui/wdgCalculator.ui -o ui/Ui_wdgCalculator.py"))
			futures.append(executor.submit(shell, "pyuic5 ui/wdgConcepts.ui -o ui/Ui_wdgConcepts.py"))
			futures.append(executor.submit(shell, "pyuic5 ui/wdgConceptsHistorical.ui -o ui/Ui_wdgConceptsHistorical.py"))
			futures.append(executor.submit(shell, "pyuic5 ui/wdgAccounts.ui -o ui/Ui_wdgAccounts.py"))
			futures.append(executor.submit(shell, "pyuic5 ui/wdgDisReinvest.ui -o ui/Ui_wdgDisReinvest.py"))
			futures.append(executor.submit(shell, "pyuic5 ui/frmAccountsReport.ui -o ui/Ui_frmAccountsReport.py"))
			futures.append(executor.submit(shell, "pyuic5 ui/wdgInvestmentClasses.ui -o ui/Ui_wdgInvestmentClasses.py"))
			futures.append(executor.submit(shell, "pyuic5 ui/wdgDividendsReport.ui -o ui/Ui_wdgDividendsReport.py"))
			futures.append(executor.submit(shell, "pyuic5 ui/wdgAPR.ui -o ui/Ui_wdgAPR.py"))
			futures.append(executor.submit(shell, "pyuic5 ui/wdgIndexRange.ui -o ui/Ui_wdgIndexRange.py"))
			futures.append(executor.submit(shell, "pyuic5 ui/wdgInvestments.ui -o ui/Ui_wdgInvestments.py"))
			futures.append(executor.submit(shell, "pyuic5 ui/wdgInvestmentsRanking.ui -o ui/Ui_wdgInvestmentsRanking.py"))
			futures.append(executor.submit(shell, "pyuic5 ui/wdgLastCurrent.ui -o ui/Ui_wdgLastCurrent.py"))
			futures.append(executor.submit(shell, "pyuic5 ui/wdgOrders.ui -o ui/Ui_wdgOrders.py"))
			futures.append(executor.submit(shell, "pyuic5 ui/wdgOrdersAdd.ui -o ui/Ui_wdgOrdersAdd.py"))
			futures.append(executor.submit(shell, "pyuic5 ui/frmDividendsAdd.ui -o ui/Ui_frmDividendsAdd.py"))
			futures.append(executor.submit(shell, "pyuic5 ui/frmInvestmentReport.ui -o ui/Ui_frmInvestmentReport.py"))
			futures.append(executor.submit(shell, "pyuic5 ui/frmInvestmentOperationsAdd.ui -o ui/Ui_frmInvestmentOperationsAdd.py"))
			futures.append(executor.submit(shell, "pyuic5 ui/frmSellingPoint.ui -o ui/Ui_frmSellingPoint.py"))
			futures.append(executor.submit(shell, "pyuic5 ui/frmSettings.ui -o ui/Ui_frmSettings.py"))
			futures.append(executor.submit(shell, "pyuic5 ui/frmCreditCardsAdd.ui -o ui/Ui_frmCreditCardsAdd.py"))
			futures.append(executor.submit(shell, "pyuic5 ui/frmTransfer.ui -o ui/Ui_frmTransfer.py"))
			futures.append(executor.submit(shell, "pyuic5 ui/frmSharesTransfer.ui -o ui/Ui_frmSharesTransfer.py"))
			futures.append(executor.submit(shell, "pyuic5 ui/wdgTotal.ui -o ui/Ui_wdgTotal.py"))
			futures.append(executor.submit(shell, "pyuic5 ui/frmProductReport.ui -o ui/Ui_frmProductReport.py"))
			futures.append(executor.submit(shell, "pyuic5 ui/frmQuotesIBM.ui -o ui/Ui_frmQuotesIBM.py"))
			futures.append(executor.submit(shell, "pyuic5 ui/frmSelector.ui -o ui/Ui_frmSelector.py"))
			futures.append(executor.submit(shell, "pyuic5 ui/frmEstimationsAdd.ui -o ui/Ui_frmEstimationsAdd.py"))
			futures.append(executor.submit(shell, "pyuic5 ui/wdgCuriosity.ui -o ui/Ui_wdgCuriosity.py"))
			futures.append(executor.submit(shell, "pyuic5 ui/wdgCuriosities.ui -o ui/Ui_wdgCuriosities.py"))
			futures.append(executor.submit(shell, "pyuic5 ui/wdgDatetime.ui -o ui/Ui_wdgDatetime.py"))
			futures.append(executor.submit(shell, "pyuic5 ui/wdgProducts.ui -o ui/Ui_wdgProducts.py"))
			futures.append(executor.submit(shell, "pyuic5 ui/wdgQuotesUpdate.ui -o ui/Ui_wdgQuotesUpdate.py"))
			futures.append(executor.submit(shell, "pyuic5 ui/wdgSimulations.ui -o ui/Ui_wdgSimulations.py"))
			futures.append(executor.submit(shell, "pyuic5 ui/wdgSimulationsAdd.ui -o ui/Ui_wdgSimulationsAdd.py"))
			futures.append(executor.submit(shell, "pyuic5 ui/wdgSource.ui -o ui/Ui_wdgSource.py"))
			futures.append(executor.submit(shell, "pyuic5 ui/wdgInvestmentsOperations.ui -o ui/Ui_wdgInvestmentsOperations.py"))
			futures.append(executor.submit(shell, "pyuic5 ui/wdgMergeCodes.ui -o ui/Ui_wdgMergeCodes.py"))
			futures.append(executor.submit(shell, "pyuic5 ui/wdgYearMonth.ui -o ui/Ui_wdgYearMonth.py"))
			futures.append(executor.submit(shell, "pyuic5 ui/wdgYear.ui -o ui/Ui_wdgYear.py"))

		shell("install -o root -d "+ prefixbin)
		shell("install -o root -d "+ prefixlib)
		shell("install -o root -d "+ prefixshare)
		shell("install -o root -d "+ prefixshare+"/sql")
		shell("install -o root -d "+ prefixpixmaps)
		shell("install -o root -d "+ prefixapplications)

		shell("install -m 755 -o root xulpymoney.py "+ prefixbin+"/xulpymoney")
		shell("install -m 755 -o root xulpymoney_init.py "+ prefixbin+"/xulpymoney_init")
		shell("install -m 755 -o root xulpymoney_sync_quotes.py "+ prefixbin+"/xulpymoney_sync_quotes")
		shell("install -m 755 -o root xulpymoney_simulation_indexrange.py "+ prefixbin+"/xulpymoney_simulation_indexrange")
		shell("install -m 755 -o root sources/source_morningstar.py "+ prefixbin+"/xulpymoney_source_morningstar")
		shell("install -m 755 -o root sources/source_yahoohistorical.py "+ prefixbin+"/xulpymoney_source_yahoo_historical")
		shell("install -m 755 -o root test/xulpymoney_test.py "+ prefixbin+"/xulpymoney_test")
		shell("install -m 644 -o root ui/*.py libxulpymoney.py libdbupdates.py libsources.py libodfgenerator.py images/*.py "+ prefixlib)
		shell("install -m 644 -o root i18n/*.qm " + prefixlib)
		shell("install -m 644 -o root sources/*.py "+ prefixlib)
		shell("install -m 644 -o root xulpymoney.desktop "+ prefixapplications)
		shell("install -m 644 -o root images/coins.png "+ prefixpixmaps+"/xulpymoney.png")
		shell("install -m 644 -o root GPL-3.txt CHANGELOG.txt AUTHORS.txt RELEASES.txt "+ prefixshare)
		shell("install -m 644 -o root sql/xulpymoney.sql "+ prefixshare+"/sql")
		shell("install -m 644 -o root odf/report.odt "+ prefixshare)
	print ("*** Process took {} using {} processors ***".format(datetime.datetime.now()-start , cpu_count()))