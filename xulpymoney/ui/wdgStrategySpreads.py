
from PyQt5.QtWidgets import QWidget
from xulpymoney.ui.Ui_wdgStrategySpreads import Ui_wdgStrategySpreads

class wdgStrategySpreads(QWidget, Ui_wdgStrategySpreads):
    def __init__(self, mem,  parent = None, name = None):
        QWidget.__init__(self,  parent)
        self.setupUi(self)
        self.mem=mem
        self.parent=parent      
        self.wdgA.setupUi(self.mem)
        self.wdgIndexA.setupUi(self.mem)
        self.wdgB.setupUi(self.mem)
        self.wdgIndexB.setupUi(self.mem)
        
        self.productA=self.mem.data.products.find_by_id(int(self.mem.settings.value("wdgProductsComparation/productA", "81112")))
        self.wdgA.setSelected(self.productA)
        self.wdgA.setLabel(self.tr("Select a product for long position"))
        self.productIndexA=self.mem.data.products.find_by_id(int(self.mem.settings.value("wdgProductsComparation/productA", "79329")))
        self.wdgIndexA.setSelected(self.productIndexA)
        self.wdgIndexA.setLabel(self.tr("Select product index"))
        self.productB=self.mem.data.products.find_by_id(int(self.mem.settings.value("wdgProductsComparation/productB", "81105")))
        self.wdgB.setSelected(self.productB)
        self.wdgB.setLabel(self.tr("Select a product for short position"))
        self.productIndexB=self.mem.data.products.find_by_id(int(self.mem.settings.value("wdgProductsComparation/productB", "79329")))
        self.wdgIndexB.setSelected(self.productIndexB)
        self.wdgIndexB.setLabel(self.tr("Select product index"))

