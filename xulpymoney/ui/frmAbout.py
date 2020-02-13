from colorama import __version__ as colorama__version__
from officegenerator import __version__ as officegenerator__version__
from platform import python_version
from stdnum import __version__ as stdnum__version__
from psycopg2 import __version__ as psycopg2__version__
from pytz import __version__ as pytz__version__
from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import QUrl, PYQT_VERSION_STR
from PyQt5.QtChart import PYQT_CHART_VERSION_STR
from xulpymoney.ui.myqtablewidget import qcenter, qempty
from xulpymoney.datetime_functions import string2dtnaive
from xulpymoney.libxulpymoneytypes import eProductType
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
        productsversion=string2dtnaive(self.mem.settingsdb.value("Version", "197001010000"), "%Y%m%d%H%M")
        self.lblProductsVersion.setText(self.tr("Database version: {}").format(productsversion))
        self.mqtwSoftware.settings(self.mem.settings, "frmAbout", "mqtwSoftware")
        self.mqtwStatistics.settings(self.mem.settings, "frmAbout", "mqtwStatistics")
        self.mqtwRegisters.settings(self.mem.settings, "frmAbout", "mqtwRegisters")
        self.load_mqtwStatistics() 
        self.load_mqtwSoftware()
        self.load_mqtwRegisters()
        self.mqtwSoftware.table.itemClicked.connect(self.OpenLink)
    
    def load_mqtwStatistics(self):
        def pais(cur, columna, bolsa):
            """Si pais es Null es para todos"""
            total=0
            cur.execute("select count(*) from products where type=1 and obsolete=false and stockmarkets_id=%s", (bolsa.id,))
            tmp=cur.fetchone()[0]
            total=total+tmp
            self.mqtwStatistics.table.setItem(0, columna , qcenter(tmp))
            cur.execute("select count(*) from products where type=2 and obsolete=false and stockmarkets_id=%s", (bolsa.id,))
            tmp=cur.fetchone()[0]
            total=total+tmp
            self.mqtwStatistics.table.setItem(1, columna , qcenter(tmp))
            cur.execute("select count(*) from products where type=3 and obsolete=false and stockmarkets_id=%s", (bolsa.id,))
            tmp=cur.fetchone()[0]
            total=total+tmp
            self.mqtwStatistics.table.setItem(2, columna , qcenter(tmp))
            cur.execute("select count(*) from products where type=4 and obsolete=false and stockmarkets_id=%s", (bolsa.id,))
            tmp=cur.fetchone()[0]
            total=total+tmp
            self.mqtwStatistics.table.setItem(3, columna , qcenter(tmp))
            cur.execute("select count(*) from products where type=5 and obsolete=false and stockmarkets_id=%s", (bolsa.id,))
            tmp=cur.fetchone()[0]
            total=total+tmp
            self.mqtwStatistics.table.setItem(4, columna , qcenter(tmp))
            cur.execute("select count(*) from products where type=7 and obsolete=false and stockmarkets_id=%s", (bolsa.id,))
            tmp=cur.fetchone()[0]
            total=total+tmp
            self.mqtwStatistics.table.setItem(5, columna , qcenter(tmp))
            cur.execute("select count(*) from products where type=9 and obsolete=false and stockmarkets_id=%s", (bolsa.id,))
            tmp=cur.fetchone()[0]
            total=total+tmp
            self.mqtwStatistics.table.setItem(6, columna , qcenter(tmp))
            cur.execute("select count(*) from products where type=%s and obsolete=false and stockmarkets_id=%s", (eProductType.CFD.value, bolsa.id,))
            tmp=cur.fetchone()[0]
            total=total+tmp
            self.mqtwStatistics.table.setItem(7, columna , qcenter(tmp))
            cur.execute("select count(*) from products where type=%s and obsolete=false and stockmarkets_id=%s", (eProductType.Future.value, bolsa.id,))
            tmp=cur.fetchone()[0]
            total=total+tmp
            self.mqtwStatistics.table.setItem(8, columna , qcenter(tmp))
            self.mqtwStatistics.table.setItem(9, columna , qempty())
            cur.execute("select count(*) from products where obsolete=true and stockmarkets_id=%s", (bolsa.id,))
            tmp=cur.fetchone()[0]
            self.mqtwStatistics.table.setItem(10, columna , qcenter(tmp))
            self.mqtwStatistics.table.setItem(11, columna , qempty())
            self.mqtwStatistics.table.setItem(12, columna , qcenter(total))
#            self.mqtwStatistics.table.horizontalHeaderItem (columna).setIcon(bolsa.country.qicon())
#            self.mqtwStatistics.table.horizontalHeaderItem (columna).setToolTip((bolsa.country.name))

        def todos(cur):
            """Si pais es Null es para todos"""
            total=0
            cur.execute("select count(*) from products where type=1 and obsolete=false")
            tmp=cur.fetchone()[0]
            total=total+tmp
            self.mqtwStatistics.table.setItem(0, 0 , qcenter(tmp))
            cur.execute("select count(*) from products where type=2  and obsolete=false")
            tmp=cur.fetchone()[0]
            total=total+tmp
            self.mqtwStatistics.table.setItem(1, 0 , qcenter(tmp))
            cur.execute("select count(*) from products where type=3  and obsolete=false")
            tmp=cur.fetchone()[0]
            total=total+tmp
            self.mqtwStatistics.table.setItem(2, 0 , qcenter(tmp))
            cur.execute("select count(*) from products where type=4  and obsolete=false")
            tmp=cur.fetchone()[0]
            total=total+tmp
            self.mqtwStatistics.table.setItem(3, 0 , qcenter(tmp))
            cur.execute("select count(*) from products where type=5  and obsolete=false")
            tmp=cur.fetchone()[0]
            total=total+tmp
            self.mqtwStatistics.table.setItem(4, 0 , qcenter(tmp))
            cur.execute("select count(*) from products where type=7  and obsolete=false")
            tmp=cur.fetchone()[0]
            total=total+tmp
            self.mqtwStatistics.table.setItem(5, 0 , qcenter(tmp))
            cur.execute("select count(*) from products where type=9  and obsolete=false")
            tmp=cur.fetchone()[0]
            total=total+tmp
            self.mqtwStatistics.table.setItem(6, 0 , qcenter(tmp))
            cur.execute("select count(*) from products where type=%s  and obsolete=false", (eProductType.CFD.value, ))
            tmp=cur.fetchone()[0]
            total=total+tmp
            self.mqtwStatistics.table.setItem(7, 0 , qcenter(tmp))
            cur.execute("select count(*) from products where type=%s  and obsolete=false", (eProductType.Future.value, ))
            tmp=cur.fetchone()[0]
            total=total+tmp
            self.mqtwStatistics.table.setItem(8, 0 , qcenter(tmp))
            self.mqtwStatistics.table.setItem(9, 0 , qempty())
            cur.execute("select count(*) from products where obsolete=true ")
            tmp=cur.fetchone()[0]
            self.mqtwStatistics.table.setItem(10, 0 , qcenter(tmp))
            self.mqtwStatistics.table.setItem(11, 0 , qempty())
            self.mqtwStatistics.table.setItem(12, 0 , qcenter(total))

    
        cur = self.mem.con.cursor()
        todos(cur)
        pais(cur, 1, self.mem.stockmarkets.find_by_id(1))
        pais(cur, 2, self.mem.stockmarkets.find_by_id(2))
        pais(cur, 3, self.mem.stockmarkets.find_by_id(3))
        pais(cur, 4, self.mem.stockmarkets.find_by_id(4))
        pais(cur, 5, self.mem.stockmarkets.find_by_id(5))
        pais(cur, 6,self.mem.stockmarkets.find_by_id(6))
        pais(cur, 7, self.mem.stockmarkets.find_by_id(7))
        pais(cur, 8, self.mem.stockmarkets.find_by_id(8))
        pais(cur, 9, self.mem.stockmarkets.find_by_id(9))
        pais(cur, 10, self.mem.stockmarkets.find_by_id(10))
        pais(cur, 11, self.mem.stockmarkets.find_by_id(11))
        pais(cur, 12, self.mem.stockmarkets.find_by_id(12))
        pais(cur, 13, self.mem.stockmarkets.find_by_id(13))
        pais(cur, 14, self.mem.stockmarkets.find_by_id(14))
        pais(cur, 15, self.mem.stockmarkets.find_by_id(15))
        cur.close()
        self.mqtwStatistics.applySettings()

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
        self.mqtwSoftware.setData(hh, None, data)

    def load_mqtwRegisters(self):
        rows=self.mem.con.cursor_one_column("SELECT tablename FROM pg_catalog.pg_tables where schemaname='public' order by tablename") 
        
        hh=[self.tr("Table"),  self.tr("Number of registers")]
        data=[]
        for i, row in enumerate(rows):
            data.append([row, self.mem.con.cursor_one_field("select count(*) from "+ row)])
        self.mqtwRegisters.setData(hh, None, data, decimals=0)
