Links
=====

Doxygen documentation:
    http://turulomio.users.sourceforge.net/doxygen/xulpymoney/

Pypi web page:
    https://pypi.org/project/xulpymoney/

Install in Linux
================
If you use Gentoo, you can find the ebuild in https://github.com/turulomio/myportage/tree/master/app-office/xulpymoney

If you use another distribution, you nee to install PyQtChart and PyQtWebEngine manually. They aren't in Linux setup.py dependencies due to PyQt5 doesn't use standard setup tools. So for compatibility reasons with distributions like Gentoo, we use this additional step.

`pip install PyQtChart`

`pip install PyQtWebEngine`

`pip install xulpymoney`

Install in Windows
==================
Install python from https://www.python.org/downloads/ and don't forget to add python to the path during installation.

Open a CMD console

`pip install xulpymoney`

If you want to create a Desktop shortcut you can write in console

`xulpymoney_shortcuts`

How to launch Xulpymoney
========================
Xulpymoney uses PostgreSQL database as its backend. So you need to create a database and load its schema. Just type:

`xulpymoney_init`

Once database has been created, just log into Xulpymoney after typing:

`xulpymoney`

Warning: Remember Xulpymoney it's still in beta status

Dependencies
============
* https://www.python.org/, as the main programming language.
* https://pypi.org/project/colorama/, to give console colors.
* http://initd.org/psycopg/, to access PostgreSQL database.
* https://pypi.org/project/PyQt5/, as the main library.
* https://pypi.org/project/pytz/, to work with timezones.
* https://pypi.org/project/officegenerator/, to work with LibreOffice and Microsoft Office documents.
* https://pypi.org/project/PyQtChart/, to work with charts.
* https://pypi.org/project/colorama/, to work with colors in console.

Changelog
=========
0.7.0
  * Added several products to products.xlsx
  * Fixed comments bugs
  * Improved long/short investments
  * Added short funcionality to opportunities.
  * Selling point now work for long and short operations.
  * Added more leveraged types
  * Now you can add Rollovers in dividend dialog
  * Added hardcoded translations

0.6.0
  * Added products.xlsx auto update
  * Added long/short strategy investments (ALPHA)
  * Added opportunities
  * UI icons updated
  * Improved merge products

0.2.0
  * Fixed a lot of bugs
  * Now products update is made from products.xlsx on internet
  * Create product.needStatus to load necessary quotes automatically
  * Added python-stdnum dependency to validate ISIN code
  * Updated and added several products

0.1.1
  * Added missing files to MANIFEST.in

0.1.0
  * Migration from Sourceforge
  * Changed code to python package
