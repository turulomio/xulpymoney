DESTDIR ?= /

PREFIXETC=$(DESTDIR)/etc/xulpymoney
PREFIXBIN=$(DESTDIR)/usr/bin
PREFIXLIB=$(DESTDIR)/usr/lib/xulpymoney
PREFIXSHARE=$(DESTDIR)/usr/share/xulpymoney
PREFIXPIXMAPS=$(DESTDIR)/usr/share/pixmaps
PREFIXAPPLICATIONS=$(DESTDIR)/usr/share/applications


all: compile install
compile:
	pyrcc4 -py3 images/xulpymoney.qrc > images/xulpymoney_rc.py
	pyuic4 ui/frmAbout.ui > ui/Ui_frmAbout.py 
	pyuic4 ui/frmMain.ui > ui/Ui_frmMain.py
	pyuic4 ui/frmOperCuentas.ui > ui/Ui_frmOperCuentas.py
	pyuic4 ui/frmTablasAuxiliares.ui > ui/Ui_frmTablasAuxiliares.py
	pyuic4 ui/wdgBancos.ui > ui/Ui_wdgBancos.py
	pyuic4 ui/wdgConceptos.ui > ui/Ui_wdgConceptos.py
	pyuic4 ui/wdgCuentas.ui > ui/Ui_wdgCuentas.py
	pyuic4 ui/wdgDesReinversion.ui > ui/Ui_wdgDesReinversion.py
	pyuic4 ui/frmCuentasIBM.ui > ui/Ui_frmCuentasIBM.py
	pyuic4 ui/wdgInformeClases.ui > ui/Ui_wdgInformeClases.py
	pyuic4 ui/wdgInformeHistorico.ui > ui/Ui_wdgInformeHistorico.py
	pyuic4 ui/wdgInformeDividendos.ui > ui/Ui_wdgInformeDividendos.py
	pyuic4 ui/wdgAPR.ui > ui/Ui_wdgAPR.py
	pyuic4 ui/wdgIndexRange.ui > ui/Ui_wdgIndexRange.py
	pyuic4 ui/wdgInversiones.ui > ui/Ui_wdgInversiones.py
	pyuic4 ui/frmDividendosIBM.ui > ui/Ui_frmDividendosIBM.py
	pyuic4 ui/frmInversionesEstudio.ui > ui/Ui_frmInversionesEstudio.py
	pyuic4 ui/frmInversionesIBM.ui > ui/Ui_frmInversionesIBM.py
	pyuic4 ui/frmPuntoVenta.ui > ui/Ui_frmPuntoVenta.py
	pyuic4 ui/frmSettings.ui > ui/Ui_frmSettings.py
	pyuic4 ui/frmTarjetasIBM.ui > ui/Ui_frmTarjetasIBM.py
	pyuic4 ui/frmTransferencia.ui > ui/Ui_frmTransferencia.py
	pyuic4 ui/frmTraspasoValores.ui > ui/Ui_frmTraspasoValores.py
	pyuic4 ui/wdgTotal.ui > ui/Ui_wdgTotal.py
	pylupdate4 -noobsolete xulpymoney.pro
	lrelease xulpymoney.pro

install:
	install -o root -d $(PREFIXETC)
	install -o root -d $(PREFIXBIN)
	install -o root -d $(PREFIXLIB)
	install -o root -d $(PREFIXSHARE)
	install -o root -d $(PREFIXPIXMAPS)
	install -o root -d $(PREFIXAPPLICATIONS)

	install -m 755 -o root xulpymoney.py $(PREFIXBIN)/xulpymoney
	install -m 644 -o root ui/*.py $(PREFIXLIB)
	install -m 644 -o root images/*.py $(PREFIXLIB)
	install -m 644 -o root i18n/*.qm $(PREFIXLIB)
	install -m 644 -o root config.py $(PREFIXETC)/config.py.dist
	install -m 644 -o root xulpymoney.desktop $(PREFIXAPPLICATIONS)
	install -m 644 -o root images/dinero.png $(PREFIXPIXMAPS)/xulpymoney.png

uninstall:
	rm $(PREFIXBIN)/xulpymoney
	rm -Rf $(PREFIXLIB)
	rm -Rf $(PREFIXSHARE)
	rm $(PREFIXETC)/config.py.dist
	rm -fr $(PREFIXPIXMAPS)/xulpymoney.png
	rm -fr $(PREFIXAPPLICATIONS)/xulpymoney.desktop

