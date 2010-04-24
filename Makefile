DESTDIR ?= /

PREFIXBIN=$(DESTDIR)/usr/bin
PREFIXPYTHON=$(DESTDIR)/usr/lib
PREFIXWEB=$(DESTDIR)/var/www/localhost/htdocs
PREFIXCONFIG=$(DESTDIR)/etc/xulpymoney

install: 
	echo "Instalando en ${DESTDIR}"
	install -o apache -d $(PREFIXPYTHON)/xulpymoney
	install -o apache -d $(PREFIXWEB)
	install -o apache -d $(PREFIXWEB)/xulpymoney
	install -o apache -d $(PREFIXWEB)/xulpymoney/ajax
	install -o apache -d $(PREFIXWEB)/xulpymoney/images
	install -o apache -d $(PREFIXWEB)/xulpymoney/languages
	install -o apache -d $(PREFIXCONFIG)
	install -o apache -d $(PREFIXWEB)/tmp
	install -d $(PREFIXBIN)
	install -m 400 -o apache *.psp $(PREFIXWEB)/xulpymoney
	install -m 400 -o apache xulpymoney.pdf $(PREFIXWEB)/xulpymoney
	install -m 400 -o apache ajax/*.psp $(PREFIXWEB)/xulpymoney/ajax
	install -m 400 -o apache images/*.png $(PREFIXWEB)/xulpymoney/images
	install -m 400 -o apache images/*.jpg $(PREFIXWEB)/xulpymoney/images
	install -m 400 -o apache clases/*.py  $(PREFIXPYTHON)/xulpymoney
	install -m 400 -o apache *.css  $(PREFIXWEB)/xulpymoney
	install -m 400 -o apache GPL-3.txt  $(PREFIXWEB)/xulpymoney
	install -m 755 -o apache scripts/xulpymoney* $(PREFIXBIN)/

uninstall:
	rm -fr $(PREFIXWEB)/xulpymoney
	rm -fr $(PREFIXPYTHON)/xulpymoney
	rm -fr $(DESTDIR)/usr/bin/xulpymoney*
