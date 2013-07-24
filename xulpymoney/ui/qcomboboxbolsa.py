## -*- coding: utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from libxulpymoney import *

class QComboBoxBolsa(QComboBox):
    def __init__(self,   parent=None):
        QComboBox.__init__(self, parent)
        self.cfg=None
        
    def cargar_datos(self, cfg):
        """Se crea esta función porque desde designer no se puede pasar self.cfg"""
        self.cfg=cfg
        arr=[]
        arr=sorted(self.cfg.bolsas.list(), key=lambda b: b.name,  reverse=False)          
        for b in arr:
            self.addItem(b.country.qicon(),  b.name,  b.id)

