PREFIXPYTHON=/usr/local/lib
PREFIXWEB=/var/www/localhost/htdocs/

install: 
	install -o apache -d $(PREFIXPYTHON)/xulpymoney
	install -o apache -d $(PREFIXWEB)
	install -o apache -d $(PREFIXWEB)/xulpymoney
	install -o apache -d $(PREFIXWEB)/xulpymoney/ajax
	install -o apache -d $(PREFIXWEB)/xulpymoney/images
	install -o apache -d $(PREFIXWEB)/xulpymoney/languages
	install -o apache -d $(PREFIXWEB)
	install -o apache -d $(PREFIXWEB)/tmp
	install -m 400 -o apache *.psp $(PREFIXWEB)/xulpymoney
	install -m 400 -o apache ajax/*.psp $(PREFIXWEB)/xulpymoney/ajax
	install -m 400 -o apache images/*.png $(PREFIXWEB)/xulpymoney/images
	install -m 400 -o apache images/*.jpg $(PREFIXWEB)/xulpymoney/images
	install -m 400 -o apache clases/*.py  $(PREFIXPYTHON)/xulpymoney
	install -m 400 -o apache *.css  $(PREFIXWEB)/xulpymoney

uninstall:
	rm -fr $(PREFIXWEB)/xulpymoney
	rm -fr $(PREFIXPYTHON)/xulpymoney
