from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QTableWidgetItem
from datetime import datetime
from decimal import Decimal
from logging import error, debug, critical
        
class Money:
    "Permite operar con dinero y divisas teniendo en cuenta la fecha de la operación mirando la divisa en mystocks"
    def __init__(self, mem,  amount=None,  currency=None) :
        self.mem=mem
        if amount==None:
            self.amount=Decimal(0)
        else:
            self.amount=Decimal(str(amount))
        if currency==None:
            self.currency=self.mem.localcurrency
        else:
            self.currency=currency
            
    ## Returns a generic_currency object from reusingcode
    def generic_currency(self):
        from xulpymoney.objects.currency import Currency ##Generic Currency
        return Currency(self.amount, self.currency.id)


    def __add__(self, money):
        """Si las divisas son distintas, queda el resultado con la divisa del primero"""
        if self.currency==money.currency:
            return Money(self.mem, self.amount+money.amount, self.currency)
        else:
            error("Before adding, please convert to the same currency")
            raise "MoneyOperationException"
            
        
    def __sub__(self, money):
        """Si las divisas son distintas, queda el resultado con la divisa del primero"""
        if self.currency==money.currency:
            return Money(self.mem, self.amount-money.amount, self.currency)
        else:
            error("Before substracting, please convert to the same currency")
            raise "MoneyOperationException"
        
    def __lt__(self, money):
        if self.currency==money.currency:
            if self.amount < money.amount:
                return True
            return False
        else:
            error("Before lt ordering, please convert to the same currency")
            exit(1)
        
    def __mul__(self, money):
        """Si las divisas son distintas, queda el resultado con la divisa del primero
        En caso de querer multiplicar por un numero debe ser despues
        money*4
        """
        if money.__class__ in (int,  float, Decimal):
            return Money(self.mem, self.amount*money, self.currency)
        if self.currency==money.currency:
            return Money(self.mem, self.amount*money.amount, self.currency)
        else:
            error("Before multiplying, please convert to the same currency")
            exit(1)
    
    def __truediv__(self, money):
        """Si las divisas son distintas, queda el resultado con la divisa del primero"""
        if self.currency==money.currency:
            return Money(self.mem, self.amount/money.amount, self.currency)
        else:
            error("Before true dividing, please convert to the same currency")
            exit(1)
        
    def __repr__(self):
        return self.string(2)
        
    def string(self,   digits=2):
        return self.currency.string(self.amount, digits)
        
    def isZero(self):
        if self.amount==Decimal(0):
            return True
        else:
            return False
            
    def isGETZero(self):
        if self.amount>=Decimal(0):
            return True
        else:
            return False            
    def isGTZero(self):
        if self.amount>Decimal(0):
            return True
        else:
            return False

    def isLTZero(self):
        if self.amount<Decimal(0):
            return True
        else:
            return False

    def isLETZero(self):
        if self.amount<=Decimal(0):
            return True
        else:
            return False
            
    def __neg__(self):
        """Devuelve otro money con el amount con signo cambiado"""
        return Money(self.mem, -self.amount, self.currency)
        
    def local(self, dt=None):
        """Converts a Money to local currency
        Date==None means today"""
        return self.convert(self.mem.localcurrency, dt)
        
    def convert(self, currency, dt=None):
        """Converts self money to currency"""
        if self.currency==currency:
            return self
        if self.amount==Decimal(0):
            return Money(self.mem, 0, currency)
            
        init=datetime.now()
        if dt==None:
            dt=self.mem.localzone.now()
        factor=self.conversionFactor(currency, dt)
        result=Money(self.mem, self.amount*factor, currency)
        debug("Money conversion. {} to {} at {} took {}".format(self.string(6), result.string(6), dt, datetime.now()-init))
        return result
        
    def conversionFactor(self, currency, dt):
        """Factor to convert from self currency to parameter currency, using datetime from result. allsetquotesintraday, uses mem"""
        if self.currency==currency:
            return Decimal(1)
        
        if self.currency.id=="EUR":
            if currency.id=="USD":
                return self.mem.data.currencies.find_by_id(74747).result.all.find(dt).quote
        elif self.currency.id=="USD":
            if currency.id=="EUR":
                return 1/self.mem.data.currencies.find_by_id(74747).result.all.find(dt).quote
        critical("No existe factor de conversión")
        return None  

    def conversionFactorString(self, currency, dt):
        """Factor to convert from self currency to parameter currency, using datetime from result. allsetquotesintraday, uses mem"""
        factor=self.conversionFactor(currency, dt)
        
        if self.currency==currency:
            return "No currency conversion factor"
            
        return "1 {} = {} {}".format(self.currency.id, factor, currency.id)
   
    def conversionDatetime(self, currency, dt):
        """
            Returns conversion datetime
        """       
        if self.currency==currency:
            return dt
        
        if self.currency.id=="EUR":
            if currency.id=="USD":
                return self.mem.data.currencies.find_by_id(74747).result.all.find(dt).datetime
        elif self.currency.id=="USD":
            if currency.id=="EUR":
                return 1/self.mem.data.currencies.find_by_id(74747).result.all.find(dt).datetime
        critical("No existe factor de conversión, por lo que tampoco su datetime")
        return None
        
        
    def convert_from_factor(self, currency, factor):
        """Converts self money to currency, multiplicando el amount del self con el factor y obteniendo la nueva currency pasada como parametro"""
        if self.currency==currency:
            return self
        
        return Money(self.mem, self.amount*factor, currency)

    def qtablewidgetitem(self, digits=2):
        """Devuelve un QTableWidgetItem mostrando un currency
        curren es un objeto Curryency"""
        text=self.string(digits)
        a=QTableWidgetItem(text)
        a.setTextAlignment(Qt.AlignVCenter|Qt.AlignRight)
        if self.amount==None:
            a.setForeground(QColor(0, 0, 255))
        elif self.amount<Decimal(0):
            a.setForeground(QColor(255, 0, 0))
        return a

    def round(self, digits=2):
        return round(self.amount, digits)
