from datetime import datetime
from xulpymoney.libmanagers import ObjectManager_With_IdName_Selectable
from pytz import timezone

## Class to manage datetime timezone and its methods
class Zone:
    ## @param mem MemXulpymoney object
    ## @param id Integer that represents the Zone Id
    ## @param name Zone Name
    ## @param country Country object asociated to the timezone
    def __init__(self, mem, id=None, name=None, country=None):
        self.mem=mem
        self.id=id
        self.name=name
        self.country=country

    ## Returns a timezone
    def timezone(self):
        return timezone(self.name)
        
    ## Datetime aware with the pyttz.timezone
    def now(self):
        return datetime.now(timezone(self.name))
        
    ## Internal __repr__ function
    def __repr__(self):
        return "Zone ({}): {}".format(str(self.id), str(self.name))            

    ## Not all zones names are in pytz zone names. Sometimes we need a conversión
    ##
    ## It's a static method you can invoke with Zone.zone_name_conversion(name)
    ## @param name String with zone not in pytz
    ## @return String with zone name already converted if needed
    @staticmethod
    def zone_name_conversion(name):
        if name=="CEST":
            return "Europe/Berlin"
        if name.find("GMT")!=-1:
            return "Etc/{}".format(name)
        return name

class ZoneManager(ObjectManager_With_IdName_Selectable):
    def __init__(self, mem):
        ObjectManager_With_IdName_Selectable.__init__(self)
        self.setConstructorParameters(mem)
        self.mem=mem
        
    def load_all(self):
        self.append(Zone(self.mem,1,'Europe/Madrid', self.mem.countries.find_by_id("es")))
        self.append(Zone(self.mem,2,'Europe/Lisbon', self.mem.countries.find_by_id("pt")))
        self.append(Zone(self.mem,3,'Europe/Rome', self.mem.countries.find_by_id("it")))
        self.append(Zone(self.mem,4,'Europe/London', self.mem.countries.find_by_id("en")))
        self.append(Zone(self.mem,5,'Asia/Tokyo', self.mem.countries.find_by_id("jp")))
        self.append(Zone(self.mem,6,'Europe/Berlin', self.mem.countries.find_by_id("de")))
        self.append(Zone(self.mem,7,'America/New_York', self.mem.countries.find_by_id("us")))
        self.append(Zone(self.mem,8,'Europe/Paris', self.mem.countries.find_by_id("fr")))
        self.append(Zone(self.mem,9,'Asia/Hong_Kong', self.mem.countries.find_by_id("cn")))
        self.append(Zone(self.mem,10,'Europe/Brussels', self.mem.countries.find_by_id("be")))
        self.append(Zone(self.mem,11,'Europe/Amsterdam', self.mem.countries.find_by_id("nl")))
        self.append(Zone(self.mem,12,'Europe/Dublin', self.mem.countries.find_by_id("ie")))
        self.append(Zone(self.mem,13,'Europe/Helsinki', self.mem.countries.find_by_id("fi")))
        self.append(Zone(self.mem,14,'Europe/Lisbon', self.mem.countries.find_by_id("pt")))
        self.append(Zone(self.mem,15,'Europe/Luxembourg', self.mem.countries.find_by_id("lu")))
        
    def qcombobox(self, combo, zone=None):
        """Carga entidades bancarias en combo"""
        combo.clear()
        for a in self.arr:
            combo.addItem(a.country.qicon(), a.name, a.id)

        if zone!=None:
            combo.setCurrentIndex(combo.findText(zone.name))
