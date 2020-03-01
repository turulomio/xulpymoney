from PyQt5.QtCore import   QSettings, QCoreApplication, QTranslator, QObject
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QApplication
from argparse import ArgumentParser, RawTextHelpFormatter
from colorama import Fore, Style
from datetime import datetime
from decimal import Decimal, getcontext
from logging import info, basicConfig, DEBUG, INFO, CRITICAL, ERROR, WARNING, debug
from os import path, makedirs
from pytz import timezone
from signal import signal, SIGINT
from sys import exit, argv
from xulpymoney.connection_pg import argparse_connection_arguments_group
from xulpymoney.casts import str2bool, string2list_of_integers
from xulpymoney.objects.account import AccountManager
from xulpymoney.objects.bank import BankManager
from xulpymoney.objects.agrupation import AgrupationManager
from xulpymoney.objects.concept import ConceptManager
from xulpymoney.objects.country import CountryManager
from xulpymoney.objects.investment import InvestmentManager
from xulpymoney.objects.leverage import LeverageManager
from xulpymoney.objects.money import Money
from xulpymoney.objects.operationtype import OperationTypeManager_hardcoded
from xulpymoney.objects.product import ProductUpdate, ProductManager
from xulpymoney.objects.productmode import ProductModesManager
from xulpymoney.objects.producttype import ProductTypeManager
from xulpymoney.objects.settingsdb import SettingsDB
from xulpymoney.objects.simulationtype import SimulationTypeManager
from xulpymoney.objects.stockmarket import StockMarketManager
from xulpymoney.objects.zone import ZoneManager
from xulpymoney.package_resources import package_filename
from xulpymoney.version import __version__, __versiondate__
from xulpymoney.translationlanguages import TranslationLanguageManager

        
getcontext().prec=20

class DBData:
    def __init__(self, mem):
        self.mem=mem

    def load(self, progress=True):
        """
            This method will subsitute load_actives and load_inactives
        """
        inicio=datetime.now()
        
        start=datetime.now()
        self.products=ProductManager(self.mem)
        self.products.load_from_db("select * from products", progress)
        debug("DBData > Products took {}".format(datetime.now()-start))
        
        self.benchmark=self.products.find_by_id(int(self.mem.settingsdb.value("mem/benchmark", "79329" )))
        self.benchmark.needStatus(2)
        
        #Loading currencies
        start=datetime.now()
        self.currencies=ProductManager(self.mem)
        for p in self.products.arr:
            if p.type.id==6:
                p.needStatus(3)
                self.currencies.append(p)
        debug("DBData > Currencies took {}".format(datetime.now()-start))
        
        self.banks=BankManager(self.mem)
        self.banks.load_from_db("select * from entidadesbancarias")

        self.accounts=AccountManager(self.mem, self.banks)
        self.accounts.load_from_db("select * from cuentas")

        self.investments=InvestmentManager(self.mem, self.accounts, self.products, self.benchmark)
        self.investments.load_from_db("select * from inversiones", progress)
        self.investments.needStatus(2, progress=True)
        
        
        #change status to 1 to self.investments products
        pros=self.investments.ProductManager_with_investments_distinct_products()
        pros.needStatus(1, progress=True)
        
        info("DBData loaded: {}".format(datetime.now()-inicio))

    def accounts_active(self):        
        r=AccountManager(self.mem, self.banks)
        for b in self.accounts.arr:
            if b.active==True:
                r.append(b)
        return r 

    def accounts_inactive(self):        
        r=AccountManager(self.mem, self.banks)
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
        r=InvestmentManager(self.mem, self.accounts, self.products, self.benchmark)
        for b in self.investments.arr:
            if b.active==True:
                r.append(b)
        return r        
        
    def investments_inactive(self):        
        r=InvestmentManager(self.mem, self.accounts, self.products, self.benchmark)
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
        self.con=None
        self.inittime=datetime.now()
        self.load_data_in_code()
        signal(SIGINT, self.signal_handler)

    ## If you want to translate hardcoded string you can use mem.tr due to strings are into Mem Class
    def trMem(self, s):
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
    ## @param args It's the result of a argparse     args=parser.parse_args()        
    def addDebugSystem(self, level):
        logFormat = "%(asctime)s.%(msecs)03d %(levelname)s %(message)s [%(module)s:%(lineno)d]"
        dateFormat='%F %I:%M:%S'

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
        return datetime.now(timezone(self.name))

class MemRunClient(Mem):
    def __init__(self):
        Mem.__init__(self)
    

class MemInit(Mem):
    def __init__(self):
        Mem.__init__(self)
        
        self.settings=QSettings()
        
    def __del__(self):
        self.settings.sync()

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
        
        self.settingsdb=SettingsDB(self)
        
        self.inittime=datetime.now()#Tiempo arranca el config
        self.dbinitdate=None#Fecha de inicio bd.
        self.con=None#Conexión        
        self._products_maintainer_mode=False
        
                
        self.closing=False#Used to close threads
        self.url_wiki="https://github.com/turulomio/xulpymoney/wiki"
    
    def run(self):
        self.args=self.parse_arguments()
        self.addDebugSystem(self.args.debug)
        self.app=QApplication(argv)
        self.app.setOrganizationName("xulpymoney")
        self.app.setOrganizationDomain("xulpymoney")
        self.app.setApplicationName("xulpymoney")
        self.con=None

        self.frmMain=None #Pointer to mainwidget
        self.closing=False#Used to close threads
        self.url_wiki="https://github.com/turulomio/xulpymoney/wiki"
    
    def parse_arguments(self):
        self.parser=ArgumentParser(prog='xulpymoney', description=self.tr('Personal accounting system'), epilog=self.epilog(), formatter_class=RawTextHelpFormatter)
        self. addCommonToArgParse(self.parser)
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
        
        self.conceptos=ConceptManager(self)
        self.conceptos.load_from_db()

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
        self.dividendwithholding=Decimal(self.settingsdb.value("mem/dividendwithholding", "0.19"))
        self.taxcapitalappreciation=Decimal(self.settingsdb.value("mem/taxcapitalappreciation", "0.19"))
        self.taxcapitalappreciationbelow=Decimal(self.settingsdb.value("mem/taxcapitalappreciationbelow", "0.5"))
        self.gainsyear=str2bool(self.settingsdb.value("mem/gainsyear", "False"))
        self.favorites=string2list_of_integers(self.settingsdb.value("mem/favorites", ""))
        self.fillfromyear=int(self.settingsdb.value("mem/fillfromyear", "2005"))
        
        info("Loading db data took {}".format(datetime.now()-inicio))
        
    def localmoney(self, amount):
        return Money(self, amount, self.localcurrency)
        
    def setProductsMaintainerMode(self, boolean):
        self._products_maintainer_mode=boolean
        
    def isProductsMaintainerMode(self):
        return self._products_maintainer_mode
