from PyQt4.QtCore import *
from PyQt4.QtGui import *
class QComboBoxTipoInversion(QComboBox):
    def __init__(self, parent=None):
        QComboBox.__init__(self, parent)
        self.cfg=None #Se carga al invocar load
    
    def load_all(self, cfg):
        self.cfg=cfg
        for id,  type in self.cfg.Types.items():
            self.addItem(type, int(id))

    def load_investments(self, cfg):
        self.cfg=cfg
        for id,  type in Type(self.cfg).investments():
            self.addItem(type, int(id))
        
