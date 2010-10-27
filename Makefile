DESTDIR ?= /

PREFIXBIN=$(DESTDIR)/usr/bin
PREFIXPYTHON=$(DESTDIR)/usr/lib
PREFIXWEB=$(DESTDIR)/var/www/localhost/htdocs
PREFIXCONFIG=$(DESTDIR)/etc/xulpymoney
PREFIXPO=$(DESTDIR)/usr/share/locale

install: 
	echo "Instalando en ${DESTDIR}"
	cd po; ./translate; cd ..
	install -o apache -d $(PREFIXPYTHON)/xulpymoney
	install -o apache -d $(PREFIXWEB)
	install -o apache -d $(PREFIXWEB)/xulpymoney
	install -o apache -d $(PREFIXWEB)/xulpymoney/ajax
	install -o apache -d $(PREFIXWEB)/xulpymoney/images
	install -o apache -d $(PREFIXWEB)/xulpymoney/js
	install -o apache -d $(PREFIXWEB)/xulpymoney/languages
	install -o root -d $(PREFIXPO)/en/LC_MESSAGES/
	install -o apache -d $(PREFIXCONFIG)
	install -o apache -d $(PREFIXWEB)/tmp
	install -d $(PREFIXBIN)
	install -m 644 -o root xulpymoney.crontab /etc/cron.d
	install -m 644 -o root po/en.mo $(PREFIXPO)/en/LC_MESSAGES/xulpymoney.mo
	install -m 400 -o apache *.py $(PREFIXWEB)/xulpymoney
	install -m 400 -o apache xulpymoney*.odt $(PREFIXWEB)/xulpymoney
	install -m 400 -o apache js/*.js $(PREFIXWEB)/xulpymoney/js
	install -m 400 -o apache ajax/*.py $(PREFIXWEB)/xulpymoney/ajax
	install -m 400 -o apache images/*.png $(PREFIXWEB)/xulpymoney/images
	install -m 400 -o apache images/*.jpg $(PREFIXWEB)/xulpymoney/images
	install -m 400 -o apache clases/*.py  $(PREFIXPYTHON)/xulpymoney
	install -m 400 -o apache clases/config.py  $(PREFIXCONFIG)/config.py.distrib
	install -m 400 -o apache *.css  $(PREFIXWEB)/xulpymoney
	install -m 400 -o apache GPL-3.txt  $(PREFIXWEB)/xulpymoney
	install -m 755 -o apache scripts/xulpymoney* $(PREFIXBIN)/
	rm -fr $(PREFIXPYTHON)/xulpymoney/config.py

uninstall:
	rm /etc/cron.d/xulpymoney.crontab
	rm -fr $(PREFIXWEB)/xulpymoney
	rm -fr $(PREFIXPYTHON)/xulpymoney
	rm -fr $(DESTDIR)/usr/bin/xulpymoney*
	rm $(PREFIXPO)/en/LC_MESSAGES/xulpymoney.mo

