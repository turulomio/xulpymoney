from colorama import __version__ as colorama__version__
from officegenerator import __version__ as officegenerator__version__
from platform import python_version
from stdnum import __version__ as stdnum__version__
from psycopg2 import __version__ as psycopg2__version__
from pytz import __version__ as pytz__version__
from scipy import __version__ as scipy__version__
from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import QUrl, PYQT_VERSION_STR
from PyQt5.QtChart import PYQT_CHART_VERSION_STR
from xulpymoney.ui.Ui_frmAbout import Ui_frmAbout
from xulpymoney.version import __version__,  __versiondate__

class frmAbout(QDialog, Ui_frmAbout):
    def __init__(self, mem):
        self.mem=mem
        QDialog.__init__(self)
        self.setModal(True)
        self.setupUi(self)
        
        s="<html><body>"
        s=s + self.tr("""Web page is in <a href="http://github.com/turulomio/xulpymoney/">http://github.com/turulomio/xulpymoney/</a>""")
        s=s + "<p>"
        s=s + self.tr("This program has been developed by Mariano Mu\xf1oz") + "<p>"
        s=s + self.tr("It has been translated to the following languages:")
        s=s + "<ul>"
        s=s + "<li>English</li>"
        s=s + "<li>Espa\xf1ol</li>"
        s=s + "</ul>"
        s=s + "<p>"
        s=s + self.tr("""Avatars are from <a href="http://www.nobleavatar.com/">http://www.nobleavatar.com/</a>""")
        s=s + "</body></html>"
        
        self.textEdit.setHtml(s)
        self.lblVersion.setText("{} ({})".format(__version__, __versiondate__))
        productsversion=self.mem.settingsdb.value_datetime_naive("Version", "197001010000", "%Y%m%d%H%M")
        self.lblProductsVersion.setText(self.tr("Database version: {}").format(productsversion))
        self.mqtwSoftware.setSettings(self.mem.settings, "frmAbout", "mqtwSoftware")
        self.mqtwStatistics.setSettings(self.mem.settings, "frmAbout", "mqtwStatistics")
        self.mqtwStatistics.table.verticalHeader().show()
        self.mqtwRegisters.setSettings(self.mem.settings, "frmAbout", "mqtwRegisters")
        self.load_mqtwStatistics() 
        self.load_mqtwSoftware()
        self.load_mqtwRegisters()
        self.mqtwSoftware.table.itemClicked.connect(self.OpenLink)
    
    def load_mqtwStatistics(self):   
        hh=[""]*self.mem.stockmarkets.length()
        hh.append(self.tr("Total"))
        hv=[]
        for i, tipo in enumerate(self.mem.types.arr):
            hv.append(tipo.name)
        hv.append(self.tr("Total"))
        
        data=[]
        for i, tipo in enumerate(self.mem.types.arr):
            row=[]
            for j, stockmarket in enumerate(self.mem.stockmarkets.arr):
                row.append(self.mem.con.cursor_one_field("select count(*) from products where type=%s and stockmarkets_id=%s and obsolete=False", (tipo.id, stockmarket.id)))
            row.append(self.mem.con.cursor_one_field("select count(*) from products where type=%s and obsolete=False", (tipo.id, )))#Total
            data.append(row)
        
        row=[]#Total last row
        for j, stockmarket in enumerate(self.mem.stockmarkets.arr):
            row.append(self.mem.con.cursor_one_field("select count(*) from products where stockmarkets_id=%s and obsolete=False", (stockmarket.id, )))
        row.append(self.mem.con.cursor_one_field("select count(*) from products where obsolete=False")) #Cross of totals
        data.append(row)

        self.mqtwStatistics.print(hh, hv, data)
        self.mqtwStatistics.setData(hh, hv, data)
        
        for j, stockmarket in enumerate(self.mem.stockmarkets.arr):
            self.mqtwStatistics.table.horizontalHeaderItem (j).setIcon(stockmarket.country.qicon())
            self.mqtwStatistics.table.horizontalHeaderItem (j).setToolTip(stockmarket.name)

    def OpenLink(self,item):
        print(item.text())
        if item.column() == 2:
            QDesktopServices.openUrl(QUrl(item.text()));

    ##Function that fills mqtwSoftware with data 
    def load_mqtwSoftware(self):
        hh=[self.tr("Software"), self.tr("Version"),  self.tr("Project main page")]
        data=[]       
        data.append(["Colorama", colorama__version__,  "https://github.com/tartley/colorama"])
        data.append(["OfficeGenerator", officegenerator__version__,  "https://github.com/turulomio/officegenerator"])
        data.append(["PostgreSQL", self.mem.con.cursor_one_field("show server_version"),  "https://www.postgresql.org/"])
        data.append(["Psycopg2", psycopg2__version__.split(" ")[0],  "http://initd.org/psycopg/"])
        data.append(["Python", python_version(),  "https://www.python.org"])
        data.append(["Python-stdnum", stdnum__version__,  "https://arthurdejong.org/python-stdnum"])
        data.append(["PyQt5", PYQT_VERSION_STR,  "https://riverbankcomputing.com/software/pyqt/intro"])
        data.append(["PyQtChart", PYQT_CHART_VERSION_STR,  "https://riverbankcomputing.com/software/pyqtchart/intro"])        
        data.append(["Pytz", pytz__version__,  "https://pypi.org/project/pytz"])
        data.append(["Scipy", scipy__version__,  "https://www.scipy.org/"])
        self.mqtwSoftware.setData(hh, None, data)

    def load_mqtwRegisters(self):
        rows=self.mem.con.cursor_one_column("SELECT tablename FROM pg_catalog.pg_tables where schemaname='public' order by tablename") 
        
        hh=[self.tr("Table"),  self.tr("Number of registers")]
        data=[]
        for i, row in enumerate(rows):
            data.append([row, self.mem.con.cursor_one_field("select count(*) from "+ row)])
        self.mqtwRegisters.setData(hh, None, data, decimals=0)
