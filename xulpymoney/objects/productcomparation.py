from PyQt5.QtCore import QObject
from xulpymoney.libmanagers import ObjectManager
from xulpymoney.objects.ohcl import OHCLDailyManager
from xulpymoney.objects.percentage import percentage_between, Percentage


## Class that compares two products, removes ohclDaily that aren't in both products
class ProductComparation(QObject):
    def __init__(self, mem, product1, product2):
        QObject.__init__(self)
        self.mem=mem
        
        self.__fromDate=None#None all array.
        self.product1=product1
        self.product2=product2     
        self.set1=OHCLDailyManager(self.mem, self.product1)#Set with common data. Needed in order to not broke self.product1 data
        self.set2=OHCLDailyManager(self.mem, self.product2)
        self.product1.needStatus(2)
        self.product2.needStatus(2)
        self.__commonDates=None 
        self.__removeNotCommon()
        
        self.name="{}-{}".format(self.product1.name, self.product2.name)
        
    def __eq__(self, o):
        if self.product1==o.product1 and self.product2==o.product2:
            return True
        return False
        
    def __str__(self):
        return self.name
        
    def setName(self, name):
        self.name=name
    
    ## Changes product1 by product2
    def swap(self):
        tmp_product=self.product2
        tmp_set=self.set2
        self.product2=self.product1
        self.product1=tmp_product
        self.set2=self.set1
        self.set1=tmp_set
        
    def setFromDate(self, date):
        """Only affect to functions returning data, not to constructor"""
        self.__fromDate=date            
            
    def canBeMade(self):
        """Returns a boolean if comparation can be made"""        
        if len(self.__commonDates)==0:
            return False
        return True
            
    def __removeNotCommon(self):
        self.__commonDates=list(set(self.product1.result.ohclDaily.dates()) & set(self.product2.result.ohclDaily.dates()))
        self.__commonDates=sorted(self.__commonDates, key=lambda c: c,  reverse=False)     
        for ohcl in self.product1.result.ohclDaily.arr:
            if ohcl.date in self.__commonDates:
                self.set1.append(ohcl)
        for ohcl in self.product2.result.ohclDaily.arr:
            if ohcl.date in self.__commonDates:
                self.set2.append(ohcl)

    def myqtablewidget(self, wdg):
        arr=[]#date, product1, product2
        productcloses1=self.product1PercentageEvolution()
        productcloses2=self.product2PercentageEvolution()
        for i, dat in enumerate(self.__commonDates):
            if i==0:
                arr.append((dat, self.set1.arr[i].close, self.set2.arr[i].close, Percentage(None), Percentage(None)))
            else:
                arr.append((dat, self.set1.arr[i].close, self.set2.arr[i].close, Percentage(productcloses1[i-1], 100), Percentage(productcloses2[i-1], 100)))

            
        hh=[self.tr("Date"), self.product1.name, self.product2.name, self.tr("Gains 1"), self.tr("Gains 2")]
        
        wdg.setData(hh, None, arr)
        
    def index(self, date):
        """Returns date index in array"""
        if date==None:
            return 0
        for i, d in enumerate(self.__commonDates):
            if date<=d:
                return i
        return 0

    def dates(self):
        """Returns a list with common dates"""
        return self.__commonDates[self.index(self.__fromDate):len(self.__commonDates)]
        
    def product1Closes(self):
        r=[]
        for ohcl in self.set1.arr:
            r.append(ohcl.close)
        return r[self.index(self.__fromDate):len(self.__commonDates)]

    def product1PercentageEvolution(self):
        r=[]
        productcloses=self.product1Closes()
        for i in range(1, len(productcloses)):
            r.append(percentage_between(productcloses[i-1], productcloses[i]).float_100())
        return r

    def product2Closes(self):
        r=[]
        for ohcl in self.set2.arr:
            r.append(ohcl.close)
        return r[self.index(self.__fromDate):len(self.__commonDates)]
    def product2PercentageEvolution(self):
        r=[]
        productcloses=self.product2Closes()
        for i in range(1, len(productcloses)):
            r.append(percentage_between(productcloses[i-1], productcloses[i]).float_100())
        return r
    
    def product1ClosesDividingFirst(self):
        """Divides set1 by a factor to get the same price in the first ohcl"""
        idx=self.index(self.__fromDate)
        factor=self.set1.arr[idx].close/self.set2.arr[idx].close
        r=[]
        for ohcl in self.set1.arr:
            r.append(ohcl.close/factor)
        return r[idx:len(self.__commonDates)]

    def product1ClosesDividingFirstLeveragedReduced(self):
        """Divides set1 by a factor to get the same price in the first ohcl
        It controls leverage too"""
        idx=self.index(self.__fromDate)
        factor=self.set1.arr[idx].close/self.set2.arr[idx].close*self.product1.leveraged.multiplier
        r=[]
        for ohcl in self.set1.arr:
            r.append(ohcl.close/factor)
        return r[idx:len(self.__commonDates)]
        
    def product1PercentageFromFirstProduct2Price(self):
        """Usa el primer valor de set 2 y la va sumando los porcentajes de set1. """
        idx=self.index(self.__fromDate)
        r=[]
        last=self.set2.arr[idx].close
        r.append(last)
        for index in range(idx+1, self.set1.length()):
            last=last*(1+ self.set1.arr[index-1].percentage(self.set1.arr[index]).value)
            r.append(last)
        return r 
        
    def product1PercentageFromFirstProduct2PriceLeveragedReduced(self):
        """Usa el primer valor de set 2 y la va sumando los porcentajes de set1. Contrala leverages"""
        idx=self.index(self.__fromDate)
        r=[]
        last=self.set2.arr[idx].close
        r.append(last)
        for index in range(idx+1, self.set1.length()):
            last=last*(1+ self.set1.arr[index-1].percentage(self.set1.arr[index]).value/self.product1.leveraged.multiplier)
            r.append(last)
        return r
        
    def product1PercentageFromFirstProduct2InversePrice(self):
        """Usa el primer valor de set 2 y la va sumando los porcentajes de set1. """
        idx=self.index(self.__fromDate)
        r=[]
        last=self.set2.arr[idx].close
        r.append(last)
        for index in range(idx+1, self.set1.length()):
            last=last*(1- self.set1.arr[index-1].percentage(self.set1.arr[index]).value)
            r.append(last)
        return r 
        
    def product1PercentageFromFirstProduct2InversePriceLeveragedReduced(self):
        """Usa el primer valor de set 2 y la va sumando los porcentajes de set1. Contrala leverages"""
        idx=self.index(self.__fromDate)
        r=[]
        last=self.set2.arr[idx].close
        r.append(last)
        for index in range(idx+1, self.set1.length()):
            last=last*(1- self.set1.arr[index-1].percentage(self.set1.arr[index]).value/self.product1.leveraged.multiplier)
            r.append(last)
        return r

    def correlacion_lineal(self):
        from scipy.stats import linregress
        slope, intercept, r_value, p_value, std_err =  linregress(self.product1PercentageEvolution(), self.product2PercentageEvolution())
        r_squared=r_value**2
        return  "{4} = {0} {3} + {1}. R²={2}".format(slope, intercept, r_squared, self.product1.name, self.product2.name)

class ProductComparationManager(ObjectManager):
    def __init__(self, mem):
        ObjectManager.__init__(self)
        self.mem=mem

    def __contains__(self, o):
        for p in self.arr: 
            if o==p:
                return True
        return False

    def save_to_settingsdb(self):
        self.mem.settingsdb.setValue("wdgProductsComparation/pairs", self.data_string())
        
    ## Convert arr to a data_string (name, product1.id, product2.id)
    def data_string(self):
        r=[]
        for o in self:
            r.append((o.name,  o.product1.id, o.product2.id))
        return str(r)

def ProductComparationManager_from_settingsdb(mem):
    r=ProductComparationManager(mem)
    s=mem.settingsdb.value("wdgProductsComparation/pairs", "[]")
    l=eval(s)
    for name,  id1, id2 in l:
        p=ProductComparation(mem, mem.data.products.find_by_id(id1), mem.data.products.find_by_id(id2))
        p.setName(name)
        r.append(p)
    return r
