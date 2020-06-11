from PyQt5.QtCore import QObject
from xulpymoney.libmanagers import ObjectManager_With_IdName_Selectable
from xulpymoney.libxulpymoneytypes import eLeverageType

class Leverage:
    def __init__(self, mem):
        self.id=None
        self.name=None
        self.multiplier=None#Valor por el que multiplicar
    def init__create(self, id, name, multiplier):
        self.id=id
        self.name=name
        self.multiplier=multiplier
        return self
        

class LeverageManager(ObjectManager_With_IdName_Selectable, QObject):
    def __init__(self, mem):
        ObjectManager_With_IdName_Selectable.__init__(self)
        QObject.__init__(self)
        self.mem=mem

    def load_all(self):
        self.append(Leverage(self.mem).init__create(eLeverageType.Variable,self.tr("Variable leverage (Warrants)"), eLeverageType.Variable))
        self.append(Leverage(self.mem).init__create(eLeverageType.NotLeveraged ,self.tr("Not leveraged"), eLeverageType.NotLeveraged))
        self.append(Leverage(self.mem).init__create(eLeverageType.X2,self.tr("Leverage x2"), eLeverageType.X2))
        self.append(Leverage(self.mem).init__create(eLeverageType.X3,self.tr("Leverage x3"), eLeverageType.X3))
        self.append(Leverage(self.mem).init__create(eLeverageType.X4,self.tr("Leverage x4"), eLeverageType.X4))
        self.append(Leverage(self.mem).init__create(eLeverageType.X5,self.tr("Leverage x5"), eLeverageType.X5))
        self.append(Leverage(self.mem).init__create(eLeverageType.X10,self.tr("Leverage x10"), eLeverageType.X10))
        self.append(Leverage(self.mem).init__create(eLeverageType.X20,self.tr("Leverage x20"), eLeverageType.X20))
        self.append(Leverage(self.mem).init__create(eLeverageType.X25, self.tr( "Leverage x25"), eLeverageType.X25))
        self.append(Leverage(self.mem).init__create(eLeverageType.X50, self.tr( "Leverage x50"), eLeverageType.X50))
        self.append(Leverage(self.mem).init__create(eLeverageType.X100, self.tr( "Leverage x100"), eLeverageType.X100))

      

            
