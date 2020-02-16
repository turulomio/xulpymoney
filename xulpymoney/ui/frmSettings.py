from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog
from xulpymoney.casts import b2c, c2b
from xulpymoney.libxulpymoneytypes import eProductType
from decimal import Decimal
from xulpymoney.objects.currency import currencies_qcombobox
from xulpymoney.ui.Ui_frmSettings import Ui_frmSettings

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
 
        currencies_qcombobox(self.cmbCurrencies,self.mem.localcurrency)
        self.mem.frmAccess.languages.qcombobox(self.cmbLanguages,self.mem.frmAccess.languages.selected)
        self.mem.zones.qcombobox(self.cmbZones, self.mem.localzone)
        self.indexes=self.mem.data.products.ProductManager_with_same_type(self.mem.types.find_by_id(eProductType.Index.value))
        self.indexes.order_by_name()
        self.indexes.qcombobox(self.cmbIndex, self.mem.data.benchmark)
        self.spnDividendPercentage.setValue(float(self.mem.dividendwithholding)*100)
        self.spnGainsPercentaje.setValue(float(self.mem.taxcapitalappreciation)*100)
        self.spnGainsPercentajeBelow.setValue(float(self.mem.taxcapitalappreciationbelow)*100)
        self.chkGainsYear.setChecked(b2c(self.mem.gainsyear))
        if self.mem.gainsyear==False:
            self.spnGainsPercentajeBelow.setEnabled(False)

    @pyqtSlot(str)      
    def on_cmbLanguages_currentIndexChanged(self, stri):
        self.mem.frmAccess.languages.selected=self.mem.frmAccess.languages.find_by_id(self.cmbLanguages.itemData(self.cmbLanguages.currentIndex()))
        self.mem.frmAccess.languages.cambiar(self.mem.frmAccess.languages.selected.id, "xulpymoney")
        self.retranslateUi(self)

    @pyqtSlot()
    def on_buttonbox_accepted(self):
        self.mem.localcurrency=self.cmbCurrencies.itemData(self.cmbCurrencies.currentIndex())
        self.mem.localzone=self.mem.zones.find_by_id(self.cmbZones.itemData(self.cmbZones.currentIndex()))
        self.mem.data.benchmark=self.mem.data.products.find_by_id(self.cmbIndex.itemData(self.cmbIndex.currentIndex()))
        self.mem.data.benchmark.needStatus(2)
        self.mem.dividendwithholding=Decimal(self.spnDividendPercentage.value())/100
        self.mem.taxcapitalappreciation=Decimal(self.spnGainsPercentaje.value())/100
        self.mem.taxcapitalappreciationbelow=Decimal(self.spnGainsPercentajeBelow.value())/100
        self.mem.gainsyear=c2b(self.chkGainsYear.checkState())

        self.mem.settingsdb.setValue("mem/localcurrency", self.mem.localcurrency)
        self.mem.settingsdb.setValue("mem/localzone", self.mem.localzone.name)
        self.mem.settingsdb.setValue("mem/dividendwithholding", Decimal(self.mem.dividendwithholding))
        self.mem.settingsdb.setValue("mem/taxcapitalappreciation", Decimal(self.mem.taxcapitalappreciation))
        self.mem.settingsdb.setValue("mem/taxcapitalappreciationbelow", Decimal(self.mem.taxcapitalappreciationbelow))
        self.mem.settingsdb.setValue("mem/gainsyear", self.mem.gainsyear)
        self.mem.settingsdb.setValue("mem/benchmarkid", self.mem.data.benchmark.id)
        self.mem.settingsdb.setValue("mem/fillfromyear", self.mem.fillfromyear)
        
        self.mem.settings.setValue("access/language", self.mem.frmAccess.languages.selected.id)
        self.mem.frmAccess.languages.cambiar(self.cmbLanguages.itemData(self.cmbLanguages.currentIndex()), "xulpymoney")  
        self.retranslateUi(self)
        self.mem.settings.sync()
        self.mem.load_db_data()#To load hardcoded strings in the new language
        self.accept()    
        
    def on_chkGainsYear_stateChanged(self, state):
        self.spnGainsPercentajeBelow.setEnabled(c2b(state))
        
    @pyqtSlot()
    def on_buttonbox_rejected(self):
        self.reject()
        
