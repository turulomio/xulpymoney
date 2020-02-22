from PyQt5.QtCore import QObject
from PyQt5.QtGui import QIcon, QPixmap
from xulpymoney.libmanagers import ObjectManager_With_IdName_Selectable, Object_With_IdName

class Country(Object_With_IdName):
    def __init__(self, *args):
        Object_With_IdName.__init__(self, *args)
            
    def qicon(self):
        icon=QIcon()
        icon.addPixmap(self.qpixmap(), QIcon.Normal, QIcon.Off)    
        return icon 
        
    def qpixmap(self):
        if self.id=="be":
            return QPixmap(":/countries/belgium.gif")
        elif self.id=="cn":
            return QPixmap(":/countries/china.gif")
        elif self.id=="fr":
            return QPixmap(":/countries/france.gif")
        elif self.id=="ie":
            return QPixmap(":/countries/ireland.gif")
        elif self.id=="it":
            return QPixmap(":/countries/italy.gif")
        elif self.id=="earth":
            return QPixmap(":/countries/earth.png")
        elif self.id=="es":
            return QPixmap(":/countries/spain.gif")
        elif self.id=="eu":
            return QPixmap(":/countries/eu.gif")
        elif self.id=="de":
            return QPixmap(":/countries/germany.gif")
        elif self.id=="fi":
            return QPixmap(":/countries/finland.gif")
        elif self.id=="nl":
            return QPixmap(":/countries/nethland.gif")
        elif self.id=="en":
            return QPixmap(":/countries/uk.gif")
        elif self.id=="jp":
            return QPixmap(":/countries/japan.gif")
        elif self.id=="pt":
            return QPixmap(":/countries/portugal.gif")
        elif self.id=="us":
            return QPixmap(":/countries/usa.gif")
        elif self.id=="ro":
            return QPixmap(":/countries/rumania.png")
        elif self.id=="ru":
            return QPixmap(":/countries/rusia.png")
        elif self.id=="lu":
            return QPixmap(":/countries/luxembourg.png")
        else:
            return QPixmap(":/xulpymoney/star.gif")
            

class CountryManager(ObjectManager_With_IdName_Selectable, QObject):
    def __init__(self, mem):
        ObjectManager_With_IdName_Selectable.__init__(self)
        QObject.__init__(self)
        self.mem=mem   
        
    def load_all(self):
        self.append(Country("es",self.tr("Spain")))
        self.append(Country("be",self.tr("Belgium")))
        self.append(Country("cn",self.tr("China")))
        self.append(Country("de",self.tr("Germany")))
        self.append(Country("earth",self.tr("Earth")))
        self.append(Country("en",self.tr("United Kingdom")))
        self.append(Country("eu",self.tr("Europe")))
        self.append(Country("fi",self.tr("Finland")))
        self.append(Country("fr",self.tr("France")))
        self.append(Country("ie",self.tr("Ireland")))
        self.append(Country("it",self.tr("Italy")))
        self.append(Country("jp",self.tr("Japan")))
        self.append(Country("nl",self.tr("Netherlands")))
        self.append(Country("pt",self.tr("Portugal")))
        self.append(Country("us",self.tr("United States of America")))
        self.append(Country("ro",self.tr("Romanian")))
        self.append(Country("ru",self.tr("Rusia")))
        self.append(Country("lu",self.tr("Luxembourg")))
        self.order_by_name()

    def qcombobox(self, combo,  country=None):
        """Función que carga en un combo pasado como parámetro y con un AccountManager pasado como parametro
        Se ordena por nombre y se se pasa el tercer parametro que es un objeto Account lo selecciona""" 
        for cu in self.arr:
            combo.addItem(cu.qicon(), cu.name, cu.id)

        if country!=None:
                combo.setCurrentIndex(combo.findData(country.id))

    def qcombobox_translation(self, combo,  country=None):
        """Función que carga en un combo pasado como parámetro con los pa´ises que tienen traducción""" 
        for cu in [self.find_by_id("es"),self.find_by_id("fr"),self.find_by_id("ro"),self.find_by_id("ru"),self.find_by_id("en") ]:
            combo.addItem(cu.qicon(), cu.name, cu.id)

        if country!=None:
                combo.setCurrentIndex(combo.findData(country.id))


