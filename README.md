What is Xulpymoney
==================
Desktop app to manage personal and financial contability

License
=======
GPL-3

Links
=====

Source code & Development:
    https://github.com/Turulomio/xulpymoney

Doxygen documentation:
    http://turulomio.users.sourceforge.net/doxygen/xulpymoney/

Main developer web page:
    https://github.com/Turulomio 
    http://turulomio.users.sourceforge.net/en/proyectos.html

Pypi web page:
    https://pypi.org/project/xulpymoney/

Install in Linux
================
If you use Gentoo you can find a ebuild in https://sourceforge.net/p/xulpymoney/code/HEAD/tree/myportage/app-office/xulpymoney/

If you use other distribution, you need to install PyQtChart manually. PyQtChart is not in Linux setup.py dependencies due to PyQt5 doesn't use standard setup tools. So for compatibility reasons with distributions like Gentoo, we use this additional step.

`pip install PyQtChart`
`pip install xulpymoney`

Intall in Windows
=================
You need to install Python from https://www.python.org and add it to the PATH

You must open a console with Administrator privileges and type:

`pip install xulpymoney`

If you want to create a Desktop shortcut to launch Xulpymoney you must write:

`xulpymoney.exe --shortcuts-create`

If you want to delete that Desktop shortcut you can write:

`xulpymoney.exe --shortcuts-remove`

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
0.3.0
  * Added platform dependent dependencies

0.2.0
  * Fixed a lot of bugs
  * Now products update is made from products.xlsx on internet
  * Create product.needStatus to load necessary quotes automatically
  * Added python-stdnum dependency to validate ISIN code
  * Updated and added several products

0.1.1
  * Added missing files to MANIFEST.in

0.1.0
*  * Migration from Sourceforge
  * Changed code to python package
