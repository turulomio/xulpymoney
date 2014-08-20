from PyQt4.QtCore import *
from PyQt4.QtGui import *
from libxulpymoney import *
from Ui_frmSettings import *

class frmSettings(QDialog, Ui_frmSettings):
    def __init__(self, mem, parent = None, name = None, modal = False):
        """
        Constructor
        
        @param parent The parent widget of this dialog. (QWidget)
        @param name The name of this dialog. (QString)
        @param modal Flag indicating a modal dialog. (boolean)
        """
        QDialog.__init__(self, parent)
        if name:
            self.setObjectName(name)
        self.setModal(True)
        self.setupUi(self)
        self.mem=mem
        self.mem.data.load_inactives()
        self.mem.currencies.qcombobox(self.cmbCurrencies,self.mem.currencies.find(self.mem.config.get_value("settings", "localcurrency")))
        self.mem.languages.qcombobox(self.cmbLanguages,self.mem.config.get_value("settings", "language"))
        self.mem.zones.qcombobox(self.cmbZones, self.mem.zones.find(self.mem.config.get_value("settings", "localzone")))
        self.indexes=SetProducts(self.mem)
        self.indexes.load_from_db("select * from products where type=3 order by name")
        self.indexes.order_by_name()
        self.indexes.qcombobox(self.cmbIndex, self.mem.data.benchmark)
        self.spnDividendPercentage.setValue(float(self.mem.config.get_value("settings", "dividendwithholding"))*100)
        self.spnGainsPercentaje.setValue(float(self.mem.config.get_value("settings", "taxcapitalappreciation"))*100)
        self.chkGainsYear.setChecked(b2c(str2bool(self.mem.config.get_value("settings", "gainsyear"))))

    @pyqtSlot(str)      
    def on_cmbLanguages_currentIndexChanged(self, stri):
        self.mem.languages.cambiar(self.cmbLanguages.itemData(self.cmbLanguages.currentIndex()))
        self.retranslateUi(self)

    @pyqtSignature("")
    def on_buttonbox_accepted(self):
        self.mem.config.set_value("settings", "localcurrency", self.cmbCurrencies.itemData(self.cmbCurrencies.currentIndex()))
        self.mem.config.set_value("settings", "language", self.cmbLanguages.itemData(self.cmbLanguages.currentIndex()))
        self.mem.config.set_value("settings", "localzone", self.cmbZones.itemData(self.cmbZones.currentIndex()))
        self.mem.config.set_value("settings", "benchmark", self.cmbIndex.itemData(self.cmbIndex.currentIndex()))
        self.mem.config.set_value("settings", "dividendwithholding", self.spnDividendPercentage.value()/100)
        self.mem.config.set_value("settings", "taxcapitalappreciation", self.spnGainsPercentaje.value()/100)
        self.mem.config.set_value("settings", "gainsyear", str(c2b(self.chkGainsYear.checkState())))
        self.mem.config.save()
        
        self.mem.languages.cambiar(self.cmbLanguages.itemData(self.cmbLanguages.currentIndex()))       
        self.retranslateUi(self)
        
        self.accept()    
        
        
    @pyqtSignature("")
    def on_buttonbox_rejected(self):
        self.reject()
        
