# Links

Doxygen documentation:
    http://turulomio.users.sourceforge.net/doxygen/xulpymoney/

Pypi web page:
    https://pypi.org/project/xulpymoney/

# Install in Linux

If you use Gentoo, you can find the ebuild in https://github.com/turulomio/myportage/tree/master/app-office/xulpymoney

If you use another distribution, you nee to install PyQtChart and PyQtWebEngine manually. They aren't in Linux setup.py dependencies due to PyQt5 doesn't use standard setup tools. So for compatibility reasons with distributions like Gentoo, we use this additional step.

`pip install PyQtChart`

`pip install PyQtWebEngine`

`pip install xulpymoney`

# Install in Windows

You just must download xulpymoney-X.X.X.exe and xulpymoney_init-X.X.X.exe and execute them. They are portable apps so they took a little more time to start.

# Install in Windows with Python

Install python from https://www.python.org/downloads/ and don't forget to add python to the path during installation.

Open a CMD console

`pip install xulpymoney`

If you want to create a Desktop shortcut you can write in console

`xulpymoney_shortcuts`

# How to launch Xulpymoney

Xulpymoney uses PostgreSQL database as its backend. So you need to create a database and load its schema. Just type:

`xulpymoney_init`

Once database has been created, just log into Xulpymoney after typing:

`xulpymoney`

Warning: Remember Xulpymoney it's still in beta status

# Dependencies

* https://www.python.org/, as the main programming language.
* https://pypi.org/project/colorama/, to give console colors.
* http://initd.org/psycopg/, to access PostgreSQL database.
* https://pypi.org/project/PyQt5/, as the main library.
* https://pypi.org/project/pytz/, to work with timezones.
* https://pypi.org/project/officegenerator/, to work with LibreOffice and Microsoft Office documents.
* https://pypi.org/project/PyQtChart/, to work with charts.
* https://www.scipy.org/, to work with statistics.

# Changelog

0.14.0
  * Added stop loss warning for orders
  * Improved assets report
  * Added more product comparation charts
  * Added strategies
  * Added more products
  * Improved CFD support
  * Updated reusing project files

0.13.0
  * Added plus_minus external script
  * Start time was reduced a 50%
  * Improved wdgTotal

0.12.0
  * wdgAPR is working again.
  * Addapted code to new myqtablewidget and myqcharts objects
  * Code is now compatible with officegenerator 1.23.0
  * Added several products
  * In wdgOrderAdd you can now modify amount and calculate the number of shares of an order.

0.11.0
  * Added modules from reusingcode repository, myqcharts and myqtablewidget has big changes
  * Added translation of hardcoded strings
  * Added a new system to update database
  * Added futures trading hours to stock market objects
  * Added number of registers in about dialog
  * Created strategies submenu. Action has been reordered
  * Assets report has been improved
  * Added paydate to DPS
  * Added product range strategy

0.10.0
  * In orders you can now select products and investments
  * Improved spanish translation
  * Added investing.com support
  * Added more products
  * Reinvest dialogs are improved
  * Added investment chart
  * Investment dividends are now loaded when necessary
  * Improved dialog after saving quotes

0.9.0
  * Improved "About" menu action.
  * Importing from Investing.com CSV is working.
  * Added pie graph to banks.
  * Bank accounts and credit cards numbers are now validated.
  * Added investment chart.
  * Added an gains percentage selector in charts when necessary.

0.8.0
  * Pies showing different investments classifications now show Not Leveraged amounts
  * Fixed problem showing help with root.
  * Menu option to update products from internet is working fine now.
  * Pyinstaller works again to package windows executables.
  * xulpymoney_init now works on Windows. It's packaged in a different file.

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
