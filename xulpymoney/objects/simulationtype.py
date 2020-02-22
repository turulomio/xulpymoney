from PyQt5.QtCore import QObject
from PyQt5.QtGui import QIcon
from xulpymoney.libmanagers import ObjectManager_With_IdName_Selectable

class SimulationTypeManager(ObjectManager_With_IdName_Selectable, QObject):
    def __init__(self, mem):
        ObjectManager_With_IdName_Selectable.__init__(self)
        QObject.__init__(self)
        self.mem=mem

    def load_all(self):
        self.append(SimulationType().init__create(1,self.tr("Xulpymoney between dates")))
        self.append(SimulationType().init__create(2,self.tr("Xulpymvoney only investments between dates")))
        self.append(SimulationType().init__create(3,self.tr("Simulating current benchmark between dates")))
        
    def qcombobox(self, combo,  selected=None):
        """selected is a SimulationType object""" 
        ###########################
        combo.clear()
        for a in self.arr:
            combo.addItem(a.qicon(), a.name, a.id)

        if selected!=None:
                combo.setCurrentIndex(combo.findData(selected.id))


class SimulationType:
    def __init__(self):
        self.id=None
        self.name=None
    def init__create(self, id, name):
        self.id=id
        self.name=name
        return self
        

    def qicon(self):
        if self.id in (1, 2):
            return QIcon(":/xulpymoney/database.png")
        else:
            return QIcon(":/xulpymoney/replication.png")    
