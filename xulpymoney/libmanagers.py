## @package libmanagers
## @brief Module with objects managers as list or as dictionary.
##
## This file is from pysgae project. Do not edit, It will be overriden.
##
## You have to use list objects if you are going to make selections and secuential access.
##
## You have to use dictionary objects i f you are going to make unordered access to the dictionary. It consumes more memory. To access a selected item in a table you have to hide a column with the id and getit when selecting a row


import logging

class MyMem:
    def __init__(self):
        self.mem=None
        
    def setMem(self, mem):
        self.mem=mem

class ObjectManager(object):
    def __init__(self):
        self.arr=[]       
        self.selected=None#Used to select a item in the set. Usefull in tables. Its a item

    def append(self,  obj):
        self.arr.append(obj)

    def remove(self, obj):
        self.arr.remove(obj)

    def length(self):
        return len(self.arr)
        
    #To use the same name as DictObjectManager
    def values(self):
        return self.arr

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
   
    def first(self):
        if self.length()>0:
            return self.arr[0]
        else:
            print ("There is no first item")
            return None
        
    def last(self):
        return self.arr[self.length()-1]
        
        
    def print(self):
        print ("Objects in {}".format(self.__class__))
        for q in self.arr:
            print(" * {}".format(q))

## Objects in DictListObjectManager has and id. The Id can be a integer or a string or ...
class ObjectManager_With_Id(ObjectManager):
    def __init__(self):
        ObjectManager.__init__(self)
        
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

## Objects in DictListObjectManager has and id and a date attribute
class ObjectManager_With_IdDate(ObjectManager_With_Id):
    def __init__(self):
        ObjectManager_With_Id.__init__(self)

    def order_by_date(self):       
        self.arr=sorted(self.arr, key=lambda e: e.date,  reverse=False) 
        
## Objects in DictListObjectManager has and id and a datetime
class ObjectManager_With_IdDatetime(ObjectManager_With_Id):
    def __init__(self):
        ObjectManager_With_Id.__init__(self)

    def order_by_datetime(self):       
        self.arr=sorted(self.arr, key=lambda e: e.datetime,  reverse=False) 
                
        
    def subSet_from_datetime(self, dt, *initparams):
        """Función que devuelve otro SetInvestmentOperations con las oper que tienen datetime mayor o igual a la pasada como parametro. Las operaciones del array son vinculos a objetos no copiadas como se hace con copy_from"""
        result=self.__class__(*initparams)#Para que coja la clase del objeto que lo invoca
        if dt==None:
            dt=self.mem.localzone.now()
        for a in self.arr:
            if a.datetime>=dt:
                result.append(a)
        return result
        
    def copy_from_datetime(self, dt, *initparams):
        """Función que devuelve otro SetInvestmentOperations con las oper que tienen datetime mayor o igual a la pasada como parametro tambien copiadas."""
        result=self.__class__(*initparams)#Para que coja la clase del objeto que lo invoca
        if dt==None:
            dt=self.mem.localzone.now()
        for a in self.arr:
            if a.datetime>=dt:
                result.append(a.copy())
        return result
        
    ## Function that returns the same object manager, but with a copy of the objects that contains until the datetime given in the parameter.
    ## For exemple the constuctor of InvemestOperationHomogeneous is InvemestOperationHomogeneous(mem,investment). so to use this function you need copy_until_datetime(dt,mem,investment)
    ## @param datetime. This function copies all object with datetime until this parameter
    ## @param initparams. Parameters of the constructor of the ManagerObject class
    def copy_until_datetime(self, dt, *initparams):
        result=self.__class__(*initparams)#Para que coja la clase del objeto que lo invoca
        if dt==None:
            dt=self.mem.localzone.now()
        for a in self.arr:
            if a.datetime<=dt:
                result.append(a.copy())
        return result

## Objects in DictListObjectManager has and id and a name
class ObjectManager_With_IdName(ObjectManager_With_Id):
    def __init__(self):
        ObjectManager_With_Id.__init__(self)
        
    ## Find an object searching in its name to match the parameter
    def find_by_name(self, name,  log=False):
        """self.find_by_id() search by id (number).
        This function replaces  it and searches by name (Europe/Madrid)"""
        for a in self.arr:
            if a.name==name:
                return a
        logging.debug("{} didn't find the name".format(self.__class__))
        return None
        
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

## Objects has a field called id, whose string is the key of the item of dict
## It Can be a DictObjectManager without id
## It doesn't need to cfreate DictListObjectManager_With_IdName, because all funcions are used with ObjectManager_With_IdName
class DictObjectManager_With_Id(object):
    ## @param selectable Create an attribute to self.selected if it's true than it's a DictObjectManager_With_Id but with selectable=False to avoid recursivity
    def __init__(self, selectable=True):
        self.dic={}
        ## It's a DictObjectManager_With_Id so we can work with one or several at the same time
        ## We can access using keys, values or items
        if selectable==True:
            self.selected=DictObjectManager_With_Id(selectable=False)

    def append(self,  obj):
        self.dic[str(obj.id)]=obj
        
    def values(self):
        return self.dic.values()
        
    def keys(self):
        return self.dic.keys()
        
    def items(self):
        return self.dic.items()
        
    def remove(self, obj):
        del self.dic[str(obj.id)]
        
    def clear(self):
        self.dic={}

    def length(self):
        return len(self.dic)
        
    ## Sometimes there is a dictionary with a unique valor. This function returns the value, not the key.
    ## I dón't use first because dict has no orders.
    def only(self):
        return self.dic[next(iter(self.dic))]
        
    ## Find by object passing o that is an object        
    def find(self, o,  log=False):
        """o is and object with id parameter"""
        print("find is deprecated")
        try:
            return self.dic[str(o.id)]    
        except:
            if log:
                print ("DictListObjectManager_With_IdName ({}) fails finding {}".format(self.__class__.__name__, o.id))
            return None        

    def find_by_id(self, id,  log=False):
        """Finds by id"""
        try:
            return self.dic[str(id)]    
        except:
            if log:
                print ("DictListObjectManager_With_IdName ({}) fails finding {}".format(self.__class__.__name__, id))
            return None
            
    def values_order_by_id(self):
        return sorted(self.dic.values(), key=lambda o: o.id)
        
    ## Useful to setselection without interactivvite ui
    ## @param list List of objects. These objects have o.id so I can append them
    def setSelected(self, list):
        self.selected.clear()
        for o in list:
            self.selected.append(o)

class DictObjectManager_With_IdName(DictObjectManager_With_Id):
    """Base clase to create Sets, it needs id and name attributes, as index. It has a list arr and a dics dict to access objects of the set"""
    def __init__(self):
        DictObjectManager_With_Id.__init__(self)

    ## Uses dict because is faster
    def values_order_by_name(self):
        return sorted(self.dic.values(), key=lambda o: o.name)
        
class DictObjectManager_With_IdDate(DictObjectManager_With_Id):
    """Base clase to create Sets, it needs id and name attributes, as index. It has a list arr and a dics dict to access objects of the set"""
    def __init__(self):
        DictObjectManager_With_Id.__init__(self)

    ## Uses dict because is faster
    def values_order_by_date(self):
        return sorted(self.dic.values(), key=lambda o: o.date)

class DictObjectManager_With_IdDatetime(DictObjectManager_With_Id):
    """Base clase to create Sets, it needs id and name attributes, as index. It has a list arr and a dics dict to access objects of the set"""
    
    def __init__(self):
        DictObjectManager_With_Id.__init__(self)

    ## Uses dict because is faster
    def values_order_by_datetime(self):
        return sorted(self.dic.values(), key=lambda o: o.datetime)
        
## Usefull when creating a class with two attributes self.id and self.name only
class Object_With_IdName:
    ## Constructor with the following attributes combination
    ## 1. Object_With_IdName(). Create an Object_With_IdName with all attributes to None
    ## 2. Object_With_IdName( id,  name). Create an Object_With_IdName settings all attributes.
    ## @param name String with the name of the Object_With_IdName
    ## @param id Integer that sets the id of the Object_With_IdName
    def __init__(self, *args):
        def init__create( id,  name):
            self.id=id
            self.name=name
        if len(args)==0:
            init__create(None, None)
        if len(args)==2:
            init__create(*args)

if __name__ == "__main__":
     import datetime
     sizes=(1,10,100,1000,10000,100000,1000000,3000000)
     for size in sizes:
         l=ObjectManager_With_Id()
         d=DictObjectManager_With_Id()
         for number in range(size):
             o=Object_With_IdName(number,"Name {}".format(number))
             l.append(o)
             d.append(o)
         middle=size*2//3
         start=datetime.datetime.now()
         l.find_by_id(middle)
         ltime=datetime.datetime.now()-start
         start=datetime.datetime.now()
         d.find_by_id(middle)
         dtime=datetime.datetime.now()-start
         print("Benchmarking search_by_id in to element {} with {} objects".format(middle,size))
         if ltime>=dtime:
             print("  * ObjectManager took {} more time than DictObjectManager".format(ltime-dtime))
         else:
             print("  * DictObjectManager took {} more time than ObjectManager".format(dtime-ltime))
