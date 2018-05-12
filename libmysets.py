class MyObject_With_Id:
    def __init__(self):
        self.id=None

class MyObject_With_IdName:
    def __init__(self):
        self.id=None
        self.name=None
        
class MyObject_With_IdDatetime:
    def __init__(self):
        self.id=None
        self.datetime=None

class MyMem:
    def __init__(self):
        self.mem=None
        
    def setMem(self, mem):
        self.mem=mem

class MyList:
    def __init__(self):
        self.arr=[]       
        self.selected=None#Used to select a item in the set. Usefull in tables. Its a item

    def append(self,  obj):
        self.arr.append(obj)

    def remove(self, obj):
        self.arr.remove(obj)

    def length(self):
        return len(self.arr)

    def clean(self):
        """Deletes all items"""
        self.arr=[]
                
    def clone(self,  *initparams):
        """Returns other Set object, with items referenced, ojo con las formas de las instancias
        initparams son los parametros de iniciación de la clase"""
        result=self.__class__(*initparams)#Para que coja la clase del objeto que lo invoca
        for a in self.arr:
            result.append(a)
        return result

## Objects in MyDictList has and id. The Id can be a integer or a string or ...
class MyList_With_Id(MyList):
    def __init__(self):
        MyList.__init__(self)
        
    def arr_position(self, id):
        """Returns arr position of the id, useful to select items with unittests"""
        for i, a in enumerate(self.arr):
            if a.id==id:
                return i
        return None
    

    ## Search by id iterating array
    def find_by_id(self, id):
        for a in self.arr:
            if a.id==id:
                return a
        return None
                
    def order_by_id(self):
        """Orders the Set using self.arr"""
        try:
            self.arr=sorted(self.arr, key=lambda c: c.id,  reverse=False)     
            return True
        except:
            return False
        
    def union(self,  set,  *initparams):
        """Returns a new set, with the union comparing id
        initparams son los parametros de iniciación de la clse"""        
        resultado=self.__class__(*initparams)#Para que coja la clase del objeto que lo invoca SetProduct(self.mem), luego será self.mem
        for p in self.arr:
            resultado.append(p)
        for p in set.arr:
            if resultado.find_by_id(p.id, False)==None:
                resultado.append(p)
        return resultado

    ## Searches the objects id in the array and mak selected. ReturnsTrue if the o.id exists in the arr and False if don't
    ## It's used when I want to mark an item in a table and I only have an id
    def setSelected(self, sel):
        for i, o in enumerate(self.arr):
            if o.id==sel.id:
                self.selected=o
                return True
        self.selected=None
        return False        
        
    ## Searches the objects id in the array and mak selected. ReturnsTrue if the o.id exists in the arr and False if don't
    ## It's used when I want to mark an item in a table and I only have the list of ids
    def setSelectedList(self, lista):
        assert type(lista) is list, "id is not a list {}".format(lista)
        self.arr=[]
        for i, o in enumerate(self.arr):
            for l in lista:
                if o.id==l.id:
                    self.append(o)
        self.selected=None
        return False

## Objects in MyDictList has and id and a datetime
class MyList_With_IdDatetime(MyList_With_Id):
    def __init__(self):
        MyList_With_Id.__init__(self)

    def order_by_datetime(self):       
        self.arr=sorted(self.arr, key=lambda e: e.datetime,  reverse=False) 

## Objects in MyDictList has and id and a name
class MyList_With_IdName(MyList_With_Id):
    def __init__(self):
        MyList_With_Id.__init__(self)
        
    def order_by_name(self):
        """Orders the Set using self.arr"""
        try:
            self.arr=sorted(self.arr, key=lambda c: c.name,  reverse=False)       
            return True
        except:
            return False        

    def order_by_upper_name(self):
        """Orders the Set using self.arr"""
        try:
            self.arr=sorted(self.arr, key=lambda c: c.name.upper(),  reverse=False)       
            return True
        except:
            return False

    def qcombobox(self, combo,  selected=None):
        """Load set items in a comobo using id and name
        Selected is and object
        It sorts by name the arr""" 
        self.order_by_name()
        combo.clear()
        for a in self.arr:
            combo.addItem(a.name, a.id)

        if selected!=None:
            combo.setCurrentIndex(combo.findData(selected.id))

##Objects has a field called id, whose string is the key of the item of dict
## It Can be a MyDict without id
## It doesn't need to cfreate MyDictList_With_IdName, because all funcions are used with MyList_With_IdName
class MyDict_With_Id:
    def __init__(self):
        self.dic={}
                    
    def append(self,  obj):
        self.dic[str(obj.id)]=obj
        
    def remove(self, obj):
        del self.dic[str(obj.id)]
        
    def clean(self):
        self.dic={}

        
    ## Find by object passing o that is an object        
    def find(self, o,  log=False):
        """o is and object with id parameter"""
        try:
            return self.dic[str(o.id)]    
        except:
            if log:
                print ("MyDictList_With_IdName ({}) fails finding {}".format(self.__class__.__name__, o.id))
            return None        

    def find_by_id(self, id,  log=False):
        """Finds by id"""
        try:
            return self.dic[str(id)]    
        except:
            if log:
                print ("MyDictList_With_IdName ({}) fails finding {}".format(self.__class__.__name__, id))
            return None

## Objects in MyDictList has and id
class MyDictList_With_Id(MyDict_With_Id, MyList_With_Id):
    def __init__(self):
        MyDict_With_Id.__init__(self)
        MyList_With_Id.__init__(self)
        
    def append(self,  obj):
        MyDict_With_Id.append(self, obj)
        MyList_With_Id.append(self, obj)
        
    def remove(self,  obj):
        MyDict_With_Id.remove(self, obj)
        MyList_With_Id.remove(self, obj)

    def clean(self):
        """Deletes all items"""
        MyDict_With_Id.clean(self)
        MyList_With_Id.clean(self)
        
    ## Find by object passing o that is an object        
    def find(self, o,  log=False):
        return MyDict_With_Id.find(self, o, log)
        
    ## Uses dict because is faster
    def find_by_id(self, id,  log=False):
        return MyDict_With_Id.find_by_id(self, id, log)

class MyDictList_With_IdName(MyDictList_With_Id, MyList_With_IdName):
    """Base clase to create Sets, it needs id and name attributes, as index. It has a list arr and a dics dict to access objects of the set"""
    def __init__(self):
        MyDictList_With_Id.__init__(self)
        MyList_With_IdName.__init__(self)

    ## Uses dict because is faster
    def find_by_id(self, id,  log=False):
        return MyDictList_With_Id.find_by_id(self, id, log)

