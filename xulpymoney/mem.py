from PyQt5.QtCore import   QSettings, QCoreApplication, QTranslator, QObject
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QApplication
from argparse import ArgumentParser, RawTextHelpFormatter
from colorama import Fore, Style
from datetime import datetime
from decimal import Decimal
from logging import info, basicConfig, DEBUG, INFO, CRITICAL, ERROR, WARNING
from os import path, makedirs
from pytz import timezone
from signal import signal, SIGINT
from sys import exit, argv
from xulpymoney.connection_pg import argparse_connection_arguments_group
from xulpymoney.libxulpymoney import DBData, CountryManager, ZoneManager, StockMarketManager, SettingsDB, ProductModesManager, ProductTypeManager, ProductUpdate, CurrencyManager, SimulationTypeManager, OperationTypeManager, ConceptManager, AgrupationManager, LeverageManager
from xulpymoney.casts import  list2string, str2bool, string2list_of_integers
from xulpymoney.package_resources import package_filename
from xulpymoney.version import __version__, __versiondate__
from xulpymoney.translationlanguages import TranslationLanguageManager



class Mem(QObject):
    def __init__(self):
        QObject.__init__(self)
        self.dir_tmp=self.dirs_create()
        self.con=None
        self.inittime=datetime.now()
        self.load_data_in_code()
        signal(SIGINT, self.signal_handler)

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
        if self.con:#Cierre por reject en frmAccess
            self.con.disconnect()
            

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
        self.localzone=self.settings.value("mem/localzone", "Europe/Madrid")
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
        
    def setLocalzone(self):
        self.localzone_name=self.settings.value("mem/localzone", "Europe/Madrid")
        self.localzone=self.zones.find_by_name(self.settingsdb.value("mem/localzone", self.localzone_name))
    
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
        
        self.currencies=CurrencyManager(self)
        self.currencies.load_all()
        self.localcurrency=self.currencies.find_by_id(self.settingsdb.value("mem/localcurrency", "EUR"))
        
        self.investmentsmodes=ProductModesManager(self)
        self.investmentsmodes.load_all()
        
        self.simulationtypes=SimulationTypeManager(self)
        self.simulationtypes.load_all()
        
        self.zones=ZoneManager(self)
        self.zones.load_all()
        self.localzone=self.zones.find_by_name(self.settingsdb.value("mem/localzone", "Europe/Madrid"))
        
        self.tiposoperaciones=OperationTypeManager(self)
        self.tiposoperaciones.load()
        
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
        
    def save_MemSettingsDB(self):
        self.settingsdb.setValue("mem/localcurrency", self.localcurrency.id)
        self.settingsdb.setValue("mem/localzone", self.localzone.name)
        self.settingsdb.setValue("mem/dividendwithholding", Decimal(self.dividendwithholding))
        self.settingsdb.setValue("mem/taxcapitalappreciation", Decimal(self.taxcapitalappreciation))
        self.settingsdb.setValue("mem/taxcapitalappreciationbelow", Decimal(self.taxcapitalappreciationbelow))
        self.settingsdb.setValue("mem/gainsyear", self.gainsyear)
        self.settingsdb.setValue("mem/favorites", list2string(self.favorites))
        self.settingsdb.setValue("mem/benchmarkid", self.data.benchmark.id)
        self.settingsdb.setValue("mem/fillfromyear", self.fillfromyear)
        info ("Saved Database settings")
        


#class MemSources:
#    def __init__(self):
#        self.data=DBData(self)
#        
#        self.countries=CountryManager(self)
#        self.countries.load_all()
#        
#        self.zones=ZoneManager(self)
#        self.zones.load_all()
#        #self.localzone=self.zones.find_by_name(self.settingsdb.value("mem/localzone", "Europe/Madrid"))
#        
#        self.stockmarkets=StockMarketManager(self)
#        self.stockmarkets.load_all()
#        
#        
#        
#class MemXulpymoney:
#    def __init__(self):                

#
#    def init__script(self, title, tickers=False, sql=False):
#        """
#            Script arguments and autoconnect in mem.con, load_db_data
#            
#            type==1 #tickers
#        """
#        app = QCoreApplication(argv)
#        app.setOrganizationName("Mariano Muñoz ©")
#        app.setOrganizationDomain("turulomio.users.sourceforge.net")
#        app.setApplicationName("Xulpymoney")
#
#        self.setQTranslator(QTranslator(app))
#        self.languages.cambiar(self.language.id)
#
#        parser=ArgumentParser(title)
#        parser.add_argument('--user', help='Postgresql user', default='postgres')
#        parser.add_argument('--port', help='Postgresql server port', default=5432)
#        parser.add_argument('--host', help='Postgresql server address', default='127.0.0.1')
#        parser.add_argument('--db', help='Postgresql database', default='xulpymoney')
#        if tickers:
#            parser.add_argument('--tickers', help='Generate tickers', default=False, action='store_true')
#        if sql:
#            parser.add_argument('--sql', help='Generate update sql', default=False, action='store_true')
#
#        args=parser.parse_args()
#        password=getpass.getpass()
#        self.con=ConnectionQt().init__create(args.user,  password,  args.host, args.port, args.db)
#        self.con.connect()
#        if not self.con.is_active():
#            critical(QCoreApplication.translate("Core", "Error connecting to database"))
#            exit(255)        
#        self.load_db_data(progress=False, load_data=False)
#        return args
#
#
#    def __del__(self):
#        if self.con:#Cierre por reject en frmAccess
#            self.con.disconnect()
#            
#    def setQTranslator(self, qtranslator):
#        self.qtranslator=qtranslator
#
#        
#

