from PyQt5.QtGui import QIcon
from  xulpymoney.libmanagers import ObjectManager_With_IdName_Selectable

## Una inversión pertenece a una lista de agrupaciones ibex, indices europeos
## fondo europeo, fondo barclays. Hat tantas agrupaciones como clasificaciones . grupos en kaddressbook similar
class Agrupation:
    ## Constructor with the following attributes combination
    ## 1. Agrupation(mem). Create an aggrupation with all attributes to None
    ## 2. Agrupation(mem, id,  name, type, bolsa). Create an agrupation settings all attributes.
    ## @param mem MemXulpymoney object
    ## @param name String with the name of the agrupation
    ## @param type
    ## @param stockmarket StockMarket object
    ## @param id Integer that sets the id of the agrupation
    def __init__(self,  *args):        
        def init__create( id,  name, type, bolsa):
            self.id=id
            self.name=name
            self.type=type
            self.stockmarket=bolsa
            
        self.mem=args[0]
        if len(args)==1:
            init__create(None, None, None, None)
        if len(args)==5:
            init__create(args[1], args[2], args[3], args[4])

    def __str__(self):
        return self.name
        
    def qicon(self):
        return QIcon(":/xulpymoney/books.png")

    
class AgrupationManager(ObjectManager_With_IdName_Selectable):
    """Se usa para meter en mem las agrupaciones, pero también para crear agrupaciones en las inversiones"""
    def __init__(self, mem):
        """Usa la variable mem.Agrupations"""
        ObjectManager_With_IdName_Selectable.__init__(self)
        self.mem=mem
        self.setConstructorParameters(self.mem)

    def load_all(self):
        self.append(Agrupation(self.mem,  "IBEX","Ibex 35", self.mem.types.find_by_id(3), self.mem.stockmarkets.find_by_id(1) ))
        self.append(Agrupation(self.mem,  "MERCADOCONTINUO","Mercado continuo español", self.mem.types.find_by_id(3), self.mem.stockmarkets.find_by_id(1) ))
        self.append(Agrupation(self.mem, "CAC",  "CAC 40 de París", self.mem.types.find_by_id(3),self.mem.stockmarkets.find_by_id(3) ))
        self.append(Agrupation(self.mem,  "EUROSTOXX","Eurostoxx 50", self.mem.types.find_by_id(3),self.mem.stockmarkets.find_by_id(10)  ))
        self.append(Agrupation(self.mem,  "DAX","DAX", self.mem.types.find_by_id(3), self.mem.stockmarkets.find_by_id(5)  ))
        self.append(Agrupation(self.mem, "SP500",  "Standard & Poors 500", self.mem.types.find_by_id(3), self.mem.stockmarkets.find_by_id(2)  ))
        self.append(Agrupation(self.mem,  "NASDAQ100","Nasdaq 100", self.mem.types.find_by_id(3), self.mem.stockmarkets.find_by_id(2)  ))
        self.append(Agrupation(self.mem,  "EURONEXT",  "EURONEXT", self.mem.types.find_by_id(3), self.mem.stockmarkets.find_by_id(10)  ))
        self.append(Agrupation(self.mem,  "DEUTSCHEBOERSE",  "DEUTSCHEBOERSE", self.mem.types.find_by_id(3), self.mem.stockmarkets.find_by_id(5)  ))
        self.append(Agrupation(self.mem,  "LATIBEX",  "LATIBEX", self.mem.types.find_by_id(3), self.mem.stockmarkets.find_by_id(1)  ))

        self.append(Agrupation(self.mem,  "e_fr_LYXOR","LYXOR", self.mem.types.find_by_id(4),self.mem.stockmarkets.find_by_id(3)  ))
        self.append(Agrupation(self.mem,  "e_de_DBXTRACKERS","Deutsche Bank X-Trackers", self.mem.types.find_by_id(4),self.mem.stockmarkets.find_by_id(5)  ))
        
        self.append(Agrupation(self.mem,  "f_es_BMF","Fondos de la bolsa de Madrid", self.mem.types.find_by_id(2), self.mem.stockmarkets.find_by_id(1) ))
        self.append(Agrupation(self.mem,  "f_fr_CARMIGNAC","Gestora CARMIGNAC", self.mem.types.find_by_id(2), self.mem.stockmarkets.find_by_id(3) ))
        self.append(Agrupation(self.mem, "f_cat_money","Funds category: Money", self.mem.types.find_by_id(2),self.mem.stockmarkets.find_by_id(10)))

        self.append(Agrupation(self.mem,  "w_fr_SG","Warrants Societe Generale", self.mem.types.find_by_id(5),self.mem.stockmarkets.find_by_id(3) ))
        self.append(Agrupation(self.mem, "w_es_BNP","Warrants BNP Paribas", self.mem.types.find_by_id(5),self.mem.stockmarkets.find_by_id(1)))
        
        
  
    def clone_by_type(self,  type):
        """Muestra las agrupaciónes de un tipo pasado como parámetro. El parámetro type es un objeto Type"""
        resultado=AgrupationManager(self.mem)
        for a in self.arr:
            if a.type==type:
                resultado.append(a)
        return resultado

    def clone_etfs(self):
        """Función que filtra el diccionario a según el país y el fondo """
        return self.clone_by_type(self.mem.types.find_by_id(4))
        
    def clone_warrants(self):
        """Función que filtra el diccionario a según el país y el fondo """
        return self.clone_by_type(self.mem.types.find_by_id(5))
        
    def clone_fondos(self):
        """Función que filtra el diccionario a según el país y el fondo """
        return self.clone_by_type(self.mem.types.find_by_id(2))
        
    def clone_acciones(self):
        """Función que filtra el diccionario a según el país y el fondo """
        return self.clone_by_type(self.mem.types.find_by_id(3))
        
        
    def clone_from_dbstring(self, dbstr):
        """Convierte la cadena de la base datos en un array de objetos agrupation"""
        resultado=AgrupationManager(self.mem)
        if dbstr==None or dbstr=="":
            pass
        else:
            for item in dbstr[1:-1].split("|"):
                resultado.append(self.mem.agrupations.find_by_id(item))
        return resultado
            
    def dbstring(self):
        resultado="|"
        for a in self.arr:
            resultado=resultado+a.id+"|"
        if resultado=="|":
            return ""
        return resultado
        
        
    def clone_from_combo(self, cmb):
        """Función que convierte un combo de agrupations a un array de agrupations"""
        resultado=AgrupationManager(self.mem)
        for i in range (cmb.count()):
            resultado.append(self.mem.agrupations.find_by_id(cmb.itemData(i)))
        return resultado
