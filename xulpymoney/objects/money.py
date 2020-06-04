from datetime import datetime
from decimal import Decimal
from logging import error, debug, critical
from xulpymoney.libxulpymoneytypes import eQColor
from xulpymoney.objects.currency import Currency
from xulpymoney.ui.myqtablewidget import qcurrency
        
class Money(Currency):
    "Permite operar con dinero y divisas teniendo en cuenta la fecha de la operación mirando la divisa en mystocks"
    def __init__(self, mem,  amount=None,  currency=None) :
        Currency.__init__(self, amount, currency)
        self.mem=mem

    ## Return the absolute value of obj.
    def __abs__(self):
        if self.amount <0:
            return Money(self.mem, -self.amount, self.currency)
        else:
            return Money(self.mem, self.amount, self.currency)

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
        if money.__class__.__name__ in ("int", "float", "Decimal"):
            return Money(self.mem, self.amount/money, self.currency)
        else: #Money
            if self.currency==money.currency:
                return Money(self.mem, self.amount/money.amount, self.currency)
            else:
                error("Before true dividing, please convert to the same currency")
                exit(1)
            
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
        if factor is None:
            return Money(self.mem, 0, currency)
        result=Money(self.mem, self.amount*factor, currency)
        debug("Money conversion. {} to {} at {} took {}".format(self.string(6), result.string(6), dt, datetime.now()-init))
        return result
        
    def conversionFactor(self, currency, dt):
        """Factor to convert from self currency to parameter currency, using datetime from result. allsetquotesintraday, uses mem"""
        if self.currency==currency:
            return Decimal(1)
        
        if self.currency=="EUR":
            if currency=="USD":
                return self.mem.data.currencies.find_by_id(74747).result.all.find(dt).quote
        elif self.currency=="USD":
            if currency=="EUR":
                return 1/self.mem.data.currencies.find_by_id(74747).result.all.find(dt).quote
        critical("No existe factor de conversión")
        return None  

    def conversionFactorString(self, currency, dt):
        """Factor to convert from self currency to parameter currency, using datetime from result. allsetquotesintraday, uses mem"""
        factor=self.conversionFactor(currency, dt)
        
        if self.currency==currency:
            return "No currency conversion factor"
            
        return "1 {} = {} {}".format(self.currency, factor, currency)
   
    def conversionDatetime(self, currency, dt):
        """
            Returns conversion datetime
        """       
        if self.currency==currency:
            return dt
        
        if self.currency=="EUR":
            if currency=="USD":
                return self.mem.data.currencies.find_by_id(74747).result.all.find(dt).datetime
        elif self.currency=="USD":
            if currency=="EUR":
                return 1/self.mem.data.currencies.find_by_id(74747).result.all.find(dt).datetime
        critical("No existe factor de conversión, por lo que tampoco su datetime")
        return None
        
        
    def convert_from_factor(self, currency, factor):
        """Converts self money to currency, multiplicando el amount del self con el factor y obteniendo la nueva currency pasada como parametro"""
        if self.currency==currency:
            return self
        
        return Money(self.mem, self.amount*factor, currency)

    def currency_object(self):
        return Currency(self.amount, self.currency)
        
    ## Returns a new object with amount zero and same currency
    def zero(self):
        return Money(self.mem, Decimal(0), self.currency)

    ## returns a qtablewidgetitem colored in red is amount is smaller than target or green if greater
    def qtablewidgetitem_with_target(self, target, digits=2):
        item=qcurrency(self.currency_object(), digits)
        if self.amount<target:   
            item.setBackground(eQColor.Red)
        else:
            item.setBackground(eQColor.Green)
        return item
