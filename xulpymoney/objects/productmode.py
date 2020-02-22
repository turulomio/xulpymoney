from PyQt5.QtCore import QObject
from xulpymoney.libmanagers import ObjectManager_With_IdName_Selectable


class ProductMode:
    def __init__(self, mem):
        self.mem=mem
        self.id=None
        self.name=None
        
    def init__create(self, id, name):
        self.id=id
        self.name=name
        return self
        

class ProductModesManager(ObjectManager_With_IdName_Selectable, QObject):
    """Agrupa los mode"""
    def __init__(self, mem):
        ObjectManager_With_IdName_Selectable.__init__(self)
        QObject.__init__(self)
        self.mem=mem     
    
    def load_all(self):
        self.append(ProductMode(self.mem).init__create("p",self.tr("Put")))
        self.append(ProductMode(self.mem).init__create("c",self.tr("Call")))
        self.append(ProductMode(self.mem).init__create("i",self.tr("Inline")))
