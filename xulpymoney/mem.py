from PyQt5.QtCore import   QSettings, QCoreApplication, QTranslator, QObject
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QProgressDialog
from argparse import ArgumentParser, RawTextHelpFormatter
from colorama import Fore, Style
from datetime import datetime
from decimal import  getcontext
from logging import info, basicConfig, DEBUG, INFO, CRITICAL, ERROR, WARNING, debug
from os import path, makedirs
from pytz import timezone
from signal import signal, SIGINT
from sys import exit, argv
from xulpymoney.connection_pg import argparse_connection_arguments_group
from xulpymoney.database_update import database_update, SettingsDB
from xulpymoney.objects.account import AccountManager, AccountManager_from_sql
from xulpymoney.objects.bank import BankManager
from xulpymoney.objects.agrupation import AgrupationManager
from xulpymoney.objects.concept import ConceptManager_from_sql
from xulpymoney.objects.country import CountryManager
from xulpymoney.objects.investment import InvestmentManager
from xulpymoney.objects.leverage import LeverageManager
from xulpymoney.objects.money import Money
from xulpymoney.objects.operationtype import OperationTypeManager_hardcoded
from xulpymoney.objects.product import ProductUpdate, ProductManager
from xulpymoney.objects.productmode import ProductModesManager
from xulpymoney.objects.producttype import ProductTypeManager
from xulpymoney.objects.simulationtype import SimulationTypeManager
from xulpymoney.objects.stockmarket import StockMarketManager
from xulpymoney.objects.zone import ZoneManager
from xulpymoney.package_resources import package_filename
from xulpymoney.version import __version__, __versiondate__, __versiondatetime__
from xulpymoney.translationlanguages import TranslationLanguageManager

        
getcontext().prec=20

class DBData(QObject):
    def __init__(self, mem):
        QObject.__init__(self)
        self.mem=mem

    ## Create a QProgressDialog to load Data
    def __qpdStart(self):
        qpdStart= QProgressDialog(self.tr("Loading Xulpymoney data"),None, 0, 6)
        qpdStart.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
        qpdStart.setModal(True)
        qpdStart.setWindowTitle(QApplication.translate("Mem","Loading Xulpymoney..."))
        qpdStart.forceShow()
        return qpdStart
                
    ## Increases qpdStart value
    ## @param qpdStart QProgressDialog
    def __qpdStart_increaseValue(self, qpdStart):
        qpdStart.setValue(qpdStart.value()+1)
        if qpdStart.value()==1:
            qpdStart.setLabelText(self.tr("Loading products definitions"))
        elif qpdStart.value()==2:
            qpdStart.setLabelText(self.tr("Loading benchmark"))
        elif qpdStart.value()==3:
            qpdStart.setLabelText(self.tr("Loading currencies"))
        elif qpdStart.value()==4:
            qpdStart.setLabelText(self.tr("Loading banks and accounts"))
        elif qpdStart.value()==5:
            qpdStart.setLabelText(self.tr("Loading investments"))
        elif qpdStart.value()==6:
            qpdStart.setLabelText(self.tr("Loading products information"))
        qpdStart.update()
        QApplication.processEvents()

    def load(self, progress=True):
        """
            This method will subsitute load_actives and load_inactives
        """
        inicio=datetime.now()
        qpdStart=self.__qpdStart()    

        self.__qpdStart_increaseValue(qpdStart)
        start=datetime.now()
        self.products=ProductManager(self.mem)
        self.products.load_from_db("select * from products", progress=False)
        debug("DBData > Products took {}".format(datetime.now()-start))
        
        self.__qpdStart_increaseValue(qpdStart)
        self.benchmark=self.products.find_by_id(self.mem.settingsdb.value_integer("mem/benchmarkid", 79329 ))
        self.benchmark.needStatus(2)
        
        self.__qpdStart_increaseValue(qpdStart)
        #Loading currencies
        start=datetime.now()
        self.currencies=ProductManager(self.mem)
        for p in self.products.arr:
            if p.type.id==6:
                p.needStatus(3)
                self.currencies.append(p)
        debug("DBData > Currencies took {}".format(datetime.now()-start))
        
        self.__qpdStart_increaseValue(qpdStart)
        self.banks=BankManager(self.mem)
        self.banks.load_from_db("select * from entidadesbancarias order by entidadbancaria")

        self.accounts=AccountManager_from_sql(self.mem, "select * from cuentas order by cuenta")

        self.__qpdStart_increaseValue(qpdStart)
        start=datetime.now()
        self.investments=InvestmentManager(self.mem)
        self.investments.load_from_db("select * from inversiones", progress=False)
        self.investments.needStatus(2, progress=False)
        debug("DBData > Investments took {}".format(datetime.now()-start))

        self.__qpdStart_increaseValue(qpdStart)
        #change status to 1 to self.investments products
        start=datetime.now()
        pros=self.investments.ProductManager_with_investments_distinct_products()
        pros.needStatus(1, progress=False)
        debug("DBData > Products status 1 took {}".format(datetime.now()-start))
        
        self.__qpdStart_increaseValue(qpdStart)
        info("DBData loaded: {}".format(datetime.now()-inicio))

    def accounts_active(self):        
        r=AccountManager(self.mem)
        for b in self.accounts.arr:
            if b.active==True:
                r.append(b)
        return r 

    def accounts_inactive(self):        
        r=AccountManager(self.mem)
        for b in self.accounts.arr:
            if b.active==False:
                r.append(b)
        return r
        
    def banks_active(self):        
        r=BankManager(self.mem)
        for b in self.banks.arr:
            if b.active==True:
                r.append(b)
        return r        
        
    def banks_inactive(self):        
        r=BankManager(self.mem)
        for b in self.banks.arr:
            if b.active==False:
                r.append(b)
        return r        

            
    def investments_active(self):        
        r=InvestmentManager(self.mem)
        for b in self.investments.arr:
            if b.active==True:
                r.append(b)
        return r        
        
    def investments_inactive(self):        
        r=InvestmentManager(self.mem)
        for b in self.investments.arr:
            if b.active==False:
                r.append(b)
        return r        

    def banks_set(self, active):
        """Function to point to list if is active or not"""
        if active==True:
            return self.banks_active()
        else:
            return self.banks_inactive()
            
    def accounts_set(self, active):
        """Function to point to list if is active or not"""
        if active==True:
            return self.accounts_active()
        else:
            return self.accounts_inactive()
    
    def investments_set(self, active):
        """Function to point to list if is active or not"""
        if active==True:
            return self.investments_active()
        else:
            return self.investments_inactive()
        
class Mem(QObject):
    def __init__(self):
        QObject.__init__(self)
        self.dir_tmp=self.dirs_create()
        self.inittime=datetime.now()
        self.load_data_in_code()
        signal(SIGINT, self.signal_handler)
        
    ## @param con
    ## @param mode Qt or Console
    def setConnection(self, con, mode):
        self.con=con
        self.settingsdb=SettingsDB(self.con)
        database_update(self.con, "xulpymoney", __versiondatetime__, mode)

    ## If you want to translate hardcoded string you can use mem.tr due to strings are into Mem Class
    def trHS(self, s):
        return QCoreApplication.translate("Mem", s)

    def epilog(self):
        return self.tr("If you like this app, please give me a star in GitHub (https://github.com/turulomio/xulpymoney).")+"\n" + self.tr("Developed by Mariano Mu\xf1oz 2015-{} \xa9".format(__versiondate__.year))

    def dirs_create(self):
        """
            Returns xulpymoney_tmp_dir, ...
        """
        dir_tmp=path.expanduser("~/.xulpymoney/tmp/")
        try:
            makedirs(dir_tmp)
        except:
            pass
        return dir_tmp
        
    def load_data_in_code(self):
        self.countries=CountryManager(self)
        self.countries.load_all()
        self.zones=ZoneManager(self)
        self.zones.load_all()        
        self.stockmarkets=StockMarketManager(self)
        self.stockmarkets.load_all()
        
    def load_db_data(self, progress=True):
        """Esto debe ejecutarse una vez establecida la conexión"""
        inicio=datetime.now()
        self.data=DBData(self)
        self.data.load(progress)
        info("Loading db data took {}".format(datetime.now()-inicio))

    def __del__(self):
        try:
            self.con.disconnect()
        except:
            pass

    ## Sets debug sustem, needs
    ## @param level
    def addDebugSystem(self, level):
        logFormat = "%(asctime)s.%(msecs)03d %(levelname)s %(message)s [%(module)s:%(lineno)d]"
        dateFormat='%F %H:%M:%S'

        if level=="DEBUG":#Show detailed information that can help with program diagnosis and troubleshooting. CODE MARKS
            basicConfig(level=DEBUG, format=logFormat, datefmt=dateFormat)
        elif level=="INFO":#Everything is running as expected without any problem. TIME BENCHMARCKS
            basicConfig(level=INFO, format=logFormat, datefmt=dateFormat)
        elif level=="WARNING":#The program continues running, but something unexpected happened, which may lead to some problem down the road. THINGS TO DO
            basicConfig(level=WARNING, format=logFormat, datefmt=dateFormat)
        elif level=="ERROR":#The program fails to perform a certain function due to a bug.  SOMETHING BAD LOGIC
            basicConfig(level=ERROR, format=logFormat, datefmt=dateFormat)
        elif level=="CRITICAL":#The program encounters a serious error and may stop running. ERRORS
            basicConfig(level=CRITICAL, format=logFormat, datefmt=dateFormat)
        info("Debug level set to {}".format(level))
        self.debuglevel=level
        
    ## Adds the commons parameter of the program to argparse
    ## @param parser It's a argparse.ArgumentParser
    def addCommonToArgParse(self, parser):
        parser.add_argument('--version', action='version', version="{} ({})".format(__version__, __versiondate__))
        parser.add_argument('--debug', help="Debug program information", choices=["DEBUG","INFO","WARNING","ERROR","CRITICAL"], default="ERROR")

    def signal_handler(self, signal, frame):
            print(Style.BRIGHT+Fore.RED+"You pressed 'Ctrl+C', exiting...")
            exit(1)

    def localzone_now(self):
        return datetime.now(timezone(self.localzone_name))

class MemRunClient(Mem):
    def __init__(self):
        Mem.__init__(self)
    

class MemInit(Mem):
    def __init__(self):
        Mem.__init__(self)
        self.settings=QSettings()

    def run(self):
        self.args=self.parse_arguments()
        self.addDebugSystem(self.args.debug) #Must be before QCoreApplication
        self.app=QApplication(argv)
        self.app.setOrganizationName("xulpymoney")
        self.app.setOrganizationDomain("xulpymoney")
        self.app.setApplicationName("xulpymoney")
        self.load_translation()
                
    def load_translation(self):
        self.qtranslator=QTranslator(self.app)
        self.languages=TranslationLanguageManager()
        self.languages.load_all()
        self.languages.selected=self.languages.find_by_id(self.settings.value("frmAccess/language", "en"))
        filename=package_filename("xulpymoney", "i18n/xulpymoney_{}.qm".format(self.languages.selected.id))
        self.qtranslator.load(filename)
        info("TranslationLanguage changed to {}".format(self.languages.selected.id))
        self.app.installTranslator(self.qtranslator)

    def parse_arguments(self):
        self.parser=ArgumentParser(prog='xulpymoney_init', description=self.tr('Create a new xulpymoney database'), epilog=self.epilog(), formatter_class=RawTextHelpFormatter)
        self. addCommonToArgParse(self.parser)
        argparse_connection_arguments_group(self.parser, default_db="xulpymoney")
        args=self.parser.parse_args()
        return args

class MemSources(Mem):
    def __init__(self, coreapplication=True):
        Mem.__init__(self)      
        if coreapplication==True:
            self.app=QCoreApplication(argv)
        else:
            self.app=QApplication(argv)
            
        self.app.setOrganizationName("xulpymoney")
        self.app.setOrganizationDomain("xulpymoney")
        self.app.setApplicationName("xulpymoney")
        
        self.settings=QSettings()
        self.localzone_name=self.settings.value("mem/localzone", "Europe/Madrid")
        self.load_translation()
        self.settings=QSettings()
        

    def __del__(self):
        self.settings.sync()

    def load_translation(self):
        self.languages=TranslationLanguageManager()
        self.languages.load_all()
        self.languages.selected=self.languages.find_by_id(self.settings.value("frmAccess/language", "en"))
        self.languages.cambiar(self.languages.selected.id, "xulpymoney")

class MemXulpymoney(Mem):
    def __init__(self):        
        Mem.__init__(self)     
        
        
        self.inittime=datetime.now()#Tiempo arranca el config
        self.dbinitdate=None#Fecha de inicio bd.
        self.con=None#Conexión        
        self._products_maintenance_mode=False
        
                
        self.closing=False#Used to close threads
        self.url_wiki="https://github.com/turulomio/xulpymoney/wiki"



    def run(self):
        self.args=self.parse_arguments()
        self.addDebugSystem(self.args.debug)
        self.setProductsMaintenanceMode(self.args.products_maintenance)
        self.app=QApplication(argv)
        self.app.setOrganizationName("xulpymoney")
        self.app.setOrganizationDomain("xulpymoney")
        self.app.setApplicationName("xulpymoney")
        from importlib import import_module
        import_module("xulpymoney.images.xulpymoney_rc")

        self.con=None

        self.frmMain=None #Pointer to mainwidget
        self.closing=False#Used to close threads
        self.url_wiki="https://github.com/turulomio/xulpymoney/wiki"

    
    def parse_arguments(self):
        self.parser=ArgumentParser(prog='xulpymoney', description=self.tr('Personal accounting system'), epilog=self.epilog(), formatter_class=RawTextHelpFormatter)
        self. addCommonToArgParse(self.parser)
        self.parser.add_argument('--products_maintenance', help=self.tr("Products mantainer interface (only developers)"), action="store_true", default=False)
        args=self.parser.parse_args()
        return args
        

    def qicon(self):
        icon = QIcon()
        icon.addPixmap(QPixmap(":/xulpymoney/xulpymoney.svg"), QIcon.Normal, QIcon.Off)
        return icon

    ## Returns an icon for admin 
    def qicon_admin(self):
        icon = QIcon()
        icon.addPixmap(QPixmap(":/xulpymoney/admin.png"), QIcon.Normal, QIcon.Off)
        return icon

    def load_db_data(self, progress=True, load_data=True):
        """Esto debe ejecutarse una vez establecida la conexión"""
        inicio=datetime.now()

        self.autoupdate=ProductUpdate.generateAutoupdateSet(self) #Set with a list of products with autoupdate
        info("There are {} products with autoupdate".format(len(self.autoupdate)))
        debug("Autoupdate took {}".format(datetime.now()-inicio))
        
        self.localcurrency=self.settingsdb.value("mem/localcurrency", "EUR")
        
        self.investmentsmodes=ProductModesManager(self)
        self.investmentsmodes.load_all()
        
        self.simulationtypes=SimulationTypeManager(self)
        self.simulationtypes.load_all()
        
        self.zones=ZoneManager(self)
        self.zones.load_all()
        self.localzone_name=self.settingsdb.value("mem/localzone", "Europe/Madrid")
        self.localzone=self.zones.find_by_name(self.localzone_name).first() #Find by name returns a ZoneManager, so I need first
        
        self.tiposoperaciones=OperationTypeManager_hardcoded(self)
        
        self.conceptos=ConceptManager_from_sql(self, "select * from conceptos order by concepto")

        self.types=ProductTypeManager(self)
        self.types.load_all()
        
        self.stockmarkets=StockMarketManager(self)
        self.stockmarkets.load_all()
        
        self.agrupations=AgrupationManager(self)
        self.agrupations.load_all()

        self.leverages=LeverageManager(self)
        self.leverages.load_all()

        if load_data:
            self.data=DBData(self)
            self.data.load(progress)
        
        #mem Variables con base de datos
        self.dividendwithholding=self.settingsdb.value_decimal("mem/dividendwithholding", "0.19")
        self.taxcapitalappreciation=self.settingsdb.value_decimal("mem/taxcapitalappreciation", "0.19")
        self.taxcapitalappreciationbelow=self.settingsdb.value_decimal("mem/taxcapitalappreciationbelow", "0.5")
        self.gainsyear=self.settingsdb.value_boolean("mem/gainsyear", "False")
        self.fillfromyear=self.settingsdb.value_integer("mem/fillfromyear", "2005")
        
        info("Loading db data took {}".format(datetime.now()-inicio))
        
    def localmoney(self, amount):
        return Money(self, amount, self.localcurrency)
        
    def localmoney_zero(self):
        return self.localmoney(0)
        
    def setProductsMaintenanceMode(self, boolean):
        self._products_maintenance_mode=boolean
        
    def isProductsMaintenanceMode(self):
        return self._products_maintenance_mode

