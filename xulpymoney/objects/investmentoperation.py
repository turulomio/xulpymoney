from PyQt5.QtCore import QObject
from PyQt5.QtGui import QIcon
from datetime import date, timedelta
from decimal import Decimal
from logging import debug, error
from xulpymoney.datetime_functions import dtaware_day_end_from_date, dtaware_month_end, dtaware_year_start, dtaware_month_start, dtaware_year_end
from xulpymoney.libmanagers import ObjectManager_With_IdDatetime_Selectable, ObjectManager_With_Id_Selectable
from xulpymoney.libxulpymoneyfunctions import set_sign_of_other_number, have_same_sign, function_name
from xulpymoney.libxulpymoneytypes import eMoneyCurrency, eComment, eOperationType, eProductType
from xulpymoney.objects.accountoperation import AccountOperationOfInvestmentOperation
from xulpymoney.objects.comment import Comment
from xulpymoney.objects.money import Money
from xulpymoney.objects.product import ProductManager
from xulpymoney.objects.percentage import Percentage
from xulpymoney.objects.quote import Quote
from xulpymoney.ui.myqtablewidget import qcenter, qleft, qdatetime, qright, qdate, qnone, qnumber

class InvestmentOperation:
    def __init__(self, mem):
        self.mem=mem
        self.id=None
        self.tipooperacion=None
        self.investment=None
        self.shares=None
        self.impuestos=None
        self.comision=None
        self.valor_accion=None
        self.datetime=None
        self.comentario=None
        self.archivada=None
        self.currency_conversion=None
        self.show_in_ranges=True
        
    def __repr__(self):
        return ("IO {0} ({1}). {2} {3}. Acciones: {4}. Valor:{5}. IdObject: {6}. Currency conversion {7}".format(self.investment.name, self.investment.id,  self.datetime, self.tipooperacion.name,  self.shares,  self.valor_accion, id(self), self.currency_conversion))
        
        
    def init__db_row(self,  row, inversion,  tipooperacion):
        self.id=row['id_operinversiones']
        self.tipooperacion=tipooperacion
        self.investment=inversion
        self.shares=row['acciones']
        self.impuestos=row['impuestos']
        self.comision=row['comision']
        self.valor_accion=row['valor_accion']
        self.datetime=row['datetime']
        self.comentario=row['comentario']
        self.show_in_ranges=row['show_in_ranges']
        self.currency_conversion=row['currency_conversion']
        return self
        
    def init__create(self, tipooperacion, datetime, inversion, acciones,  impuestos, comision, valor_accion, comentario, show_in_ranges, currency_conversion,    id=None):
        self.id=id
        self.tipooperacion=tipooperacion
        self.datetime=datetime
        self.investment=inversion
        self.shares=acciones
        self.impuestos=impuestos
        self.comision=comision
        self.valor_accion=valor_accion
        self.comentario=comentario
        self.show_in_ranges=show_in_ranges
        self.currency_conversion=currency_conversion
        return self
        
    def init__from_accountoperation(self, accountoperation):
        """AccountOperation is a object, and must have id_conceptos share of sale or purchase. 
        IO returned is an object already created in investments_all()"""
        cur=self.mem.con.cursor()
        cur.execute("select id_inversiones,id_operinversiones from opercuentasdeoperinversiones where id_opercuentas=%s", (accountoperation.id, ))
        if cur.rowcount==0:
            cur.close()
            return None
        row=cur.fetchone()
        cur.close()
        investment=self.mem.data.investments.find_by_id(row['id_inversiones'])
        return investment.op.find(row['id_operinversiones'])
        
    def price(self, type=eMoneyCurrency.Product):
        if type==1:
            return Money(self.mem, self.valor_accion, self.investment.product.currency)
        else:
            return Money(self.mem, self.valor_accion, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion)
            
    def gross(self, type=eMoneyCurrency.Product):
        if type==1:
            return Money(self.mem, abs(self.shares*self.valor_accion), self.investment.product.currency)
        else:
            return Money(self.mem, abs(self.shares*self.valor_accion), self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion)
            
    def net(self, type=eMoneyCurrency.Product):
        if self.shares>=Decimal(0):
            return self.gross(type)+self.commission(type)+self.taxes(type)
        else:
            return self.gross(type)-self.commission(type)-self.taxes(type)
            
    def taxes(self, type=eMoneyCurrency.Product):
        if type==1:
            return Money(self.mem, self.impuestos, self.investment.product.currency)
        else:
            return Money(self.mem, self.impuestos, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion)
            
    def commission(self, type=eMoneyCurrency.Product):
        if type==1:
            return Money(self.mem, self.comision, self.investment.product.currency)
        else:
            return Money(self.mem, self.comision, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion)

    def find_by_mem(self, investment, id):
        """
            Searchs in mem (needed investments_all())
            invesment is an Investment object
            id is the invesmentoperation to find
        """
        for i in self.mem.data.investments:
            if investment.id==i.id:
                found=i.op.find(id)
                if found!=None:
                    return found
        debug ("Investment operation {} hasn't been found in mem".format(id))
        return None

    ## Esta función actualiza la tabla opercuentasdeoperinversiones que es una tabla donde 
    ## se almacenan las opercuentas automaticas por las operaciones con inversiones. Es una tabla 
    ## que se puede actualizar en cualquier momento con esta función
    def actualizar_cuentaoperacion_asociada(self):
        #/Borra de la tabla opercuentasdeoperinversiones los de la operinversión pasada como parámetro
        cur=self.mem.con.cursor()
        cur.execute("delete from opercuentasdeoperinversiones where id_operinversiones=%s",(self.id, )) 
        cur.close()
        
        if self.investment.product.high_low==True: #Because it uses adjustment information
            return
        
        self.comentario=Comment(self.mem).encode(eComment.InvestmentOperation, self)
        if self.tipooperacion.id==4:#Compra Acciones
            #Se pone un registro de compra de acciones que resta el balance de la opercuenta
            importe=-self.gross(type=2)-self.commission(type=2)
            c=AccountOperationOfInvestmentOperation(self.mem, self.datetime, self.mem.conceptos.find_by_id(29), self.tipooperacion, importe.amount, self.comentario, self.investment.account, self,self.investment, None)
            c.save()
        elif self.tipooperacion.id==5:#// Venta Acciones
            #//Se pone un registro de compra de acciones que resta el balance de la opercuenta
            importe=self.gross(type=2)-self.commission(type=2)-self.taxes(type=2)
            c=AccountOperationOfInvestmentOperation(self.mem, self.datetime, self.mem.conceptos.find_by_id(35), self.tipooperacion, importe.amount, self.comentario, self.investment.account, self,self.investment, None)
            c.save()
        elif self.tipooperacion.id==6:
            #//Si hubiera comisión se añade la comisión.
            if(self.comision!=0):
                importe=-self.commission(type=2)-self.taxes(type=2)
                c=AccountOperationOfInvestmentOperation(self.mem, self.datetime, self.mem.conceptos.find_by_id(38), self.mem.tiposoperaciones.find_by_id(1), importe.amount, self.comentario, self.investment.account, self,self.investment, None)
                c.save()
    
    def copy(self, investment=None):
        """
            Crea una inversion operacion desde otra inversionoepracion. NO es un enlace es un objeto clone
            Si el parametro investment es pasado usa el objeto investment  en vez de una referencia a self.investmen
        """
        inv=self.investment if investment==None else investment
        return InvestmentOperation(self.mem).init__create(self.tipooperacion, self.datetime, inv , self.shares, self.impuestos, self.comision, self.valor_accion, self.comentario,  self.show_in_ranges, self.currency_conversion, self.id)

    def less_than_a_year(self):
        if date.today()-self.datetime.date()<=timedelta(days=365):
                return True
        return False
        
    def save(self, recalculate=True,  autocommit=True):
        cur=self.mem.con.cursor()
        if self.id==None:#insertar
            cur.execute("insert into operinversiones(datetime, id_tiposoperaciones,  acciones,  impuestos,  comision,  valor_accion, comentario, show_in_ranges, id_inversiones, currency_conversion) values (%s, %s, %s, %s, %s, %s, %s, %s,%s,%s) returning id_operinversiones", (self.datetime, self.tipooperacion.id, self.shares, self.impuestos, self.comision, self.valor_accion, self.comentario, self.show_in_ranges,  self.investment.id,  self.currency_conversion))
            self.id=cur.fetchone()[0]
            self.investment.op.append(self)
        else:
            cur.execute("update operinversiones set datetime=%s, id_tiposoperaciones=%s, acciones=%s, impuestos=%s, comision=%s, valor_accion=%s, comentario=%s, id_inversiones=%s, show_in_ranges=%s, currency_conversion=%s where id_operinversiones=%s", (self.datetime, self.tipooperacion.id, self.shares, self.impuestos, self.comision, self.valor_accion, self.comentario, self.investment.id, self.show_in_ranges,  self.currency_conversion,  self.id))
        if recalculate==True:
            (self.investment.op_actual,  self.investment.op_historica)=self.investment.op.get_current_and_historical_operations()   
            self.actualizar_cuentaoperacion_asociada()
        if autocommit==True:
            self.mem.con.commit()
        cur.close()
   

class InvestmentOperationCurrent:
    def __init__(self, mem):
        self.mem=mem 
        self.id=None
        self.operinversion=None
        self.tipooperacion=None
        self.datetime=None# con tz
        self.investment=None
        self.shares=None
        self.impuestos=None
        self.comision=None
        self.valor_accion=None
        self.referenciaindice=None##Debera cargarse desde fuera. No se carga con row.. Almacena un Quote, para comprobar si es el indice correcto ver self.referenciaindice.id
        self.show_in_ranges=True
        self.currency_conversion=None
        
    def __repr__(self):
        return ("IOA {0}. {1} {2}. Acciones: {3}. Valor:{4}. Currency conversion: {5}".format(self.investment.name,  self.datetime, self.tipooperacion.name,  self.shares,  self.valor_accion, self.currency_conversion))
        
    def init__create(self, operinversion, tipooperacion, datetime, inversion, acciones,  impuestos, comision, valor_accion, show_in_ranges,  currency_conversion, id=None):
        """Investment es un objeto Investment"""
        self.id=id
        self.operinversion=operinversion
        self.tipooperacion=tipooperacion
        self.datetime=datetime
        self.investment=inversion
        self.shares=acciones
        self.impuestos=impuestos
        self.comision=comision
        self.valor_accion=valor_accion
        self.show_in_ranges=show_in_ranges
        self.currency_conversion=currency_conversion
        return self
        
    def copy(self):
        return self.init__create(self.operinversion, self.tipooperacion, self.datetime, self.investment, self.shares, self.impuestos, self.comision, self.valor_accion, self.show_in_ranges, self.currency_conversion,   self.id)
                
    def age(self):
        """Average age of the current investment operations in days"""
        return (date.today()-self.datetime.date()).days
                
    def get_referencia_indice(self, indice):
        """Función que devuelve un Quote con la referencia del indice.
        Si no existe devuelve un Quote con quote 0"""
        quote=Quote(self.mem).init__from_query( indice, self.datetime)
        if quote==None:
            self.referenciaindice= Quote(self.mem).init__create(indice, self.datetime, 0)
        else:
            self.referenciaindice=quote
        return self.referenciaindice
    ## Función que devuelve el importe invertido teniendo en cuenta las acciones actuales de la operinversión y el valor de compra
    ## Si se usa  el importe no fuNCIONA PASO CON EL PUNTOI DE VENTA.
    def invertido(self, type=eMoneyCurrency.Product):
        if self.investment.product.high_low==True:
            value=abs(self.shares*self.valor_accion*self.investment.product.leveraged.multiplier)
        else:
            value=self.shares*self.valor_accion
        money=Money(self.mem, value, self.investment.product.currency)
        if type==eMoneyCurrency.Product:
            return money
        elif type==eMoneyCurrency.Account:
            return money.convert_from_factor(self.investment.account.currency, self.currency_conversion)#Usa el factor del dia de la operacicón
        elif type==eMoneyCurrency.User:
            return money.convert_from_factor(self.investment.account.currency, self.currency_conversion).local(self.datetime)#Usa el factor del dia de la operacicón
    
    def price(self, type=eMoneyCurrency.Product):
        if type==1:
            return Money(self.mem, self.valor_accion, self.investment.product.currency)
        elif type==2:
            return Money(self.mem, self.valor_accion, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion)
        elif type==3:
            return Money(self.mem, self.valor_accion, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion).local(self.datetime)
            
            
    def revaluation_monthly(self, year, month, type=eMoneyCurrency.Product):
        """
            Returns a money object with monthly reevaluation
        """
        dt_last= dtaware_month_end(year, month, self.mem.localzone_name)
        dt_first=dtaware_month_start(year, month, self.mem.localzone_name)
        if self.datetime>dt_first and self.datetime<dt_last:
            dt_first=self.datetime
        elif self.datetime>dt_last:
            return Money(self.mem, 0, self.investment.product.currency)
        first=Quote(self.mem).init__from_query( self.investment.product, dt_first).quote
        last=Quote(self.mem).init__from_query( self.investment.product, dt_last).quote
        money=Money(self.mem, (last-first)*self.shares, self.investment.product.currency)
        debug("{} {} {} accciones. {}-{}. {}-{}={} ({})".format(self.investment.name, self.datetime, self.shares, dt_last, dt_first, last, first, last-first,  money))
        if type==1:
            return money
        elif type==2:
            return money.convert(self.investment.account.currency, dt_last)
        elif type==3:
            return money.convert(self.investment.account.currency, dt_last).local(dt_last)
            
            
    def revaluation_annual(self, year, type=eMoneyCurrency.Product):
        """
            Returns a money object with monthly reevaluation
        """
        dt_last= dtaware_year_end(year, self.mem.localzone_name)
        dt_first=dtaware_year_start(year, self.mem.localzone_name)
        if self.datetime>dt_first:
            dt_first=self.datetime
        first=Quote(self.mem).init__from_query( self.investment.product, dt_first).quote
        last=Quote(self.mem).init__from_query( self.investment.product, dt_last).quote
        money=Money(self.mem, (last-first)*self.shares, self.investment.product.currency)
        debug("ANNUAL:{} {} {} accciones. {}-{}. {}-{}={} ({})".format(self.investment.name, self.datetime, self.shares, dt_last, dt_first, last, first, last-first,  money))
        if type==1:
            return money
        elif type==2:
            return money.convert(self.investment.account.currency, dt_last)
        elif type==3:
            return money.convert(self.investment.account.currency, dt_last).local(dt_last)
            
            
    def gross(self, type=eMoneyCurrency.Product):
        if type==1:
            return Money(self.mem, self.shares*self.valor_accion, self.investment.product.currency)
        elif type==2:
            return Money(self.mem, self.shares*self.valor_accion, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion)
            
    def net(self, type=eMoneyCurrency.Product):
        if self.shares>=Decimal(0):
            return self.gross(type)+self.commission(type)+self.taxes(type)
        elif type==2:
            return self.gross(type)-self.commission(type)-self.taxes(type)
            
    def taxes(self, type=eMoneyCurrency.Product):
        if type==1:
            return Money(self.mem, self.impuestos, self.investment.product.currency)
        elif type==2:
            return Money(self.mem, self.impuestos, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion)
            
    def commission(self, type=eMoneyCurrency.Product):
        if type==1:
            return Money(self.mem, self.comision, self.investment.product.currency)
        elif type==2:
            return Money(self.mem, self.comision, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion)
        elif type==3:
            return Money(self.mem, self.comision, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion).local()
            
    def balance(self,  lastquote, type=eMoneyCurrency.Product):
        """Función que calcula el balance actual de la operinversion actual
                - lastquote: objeto Quote
                type si da el resultado en la currency del account o en el de la inversion"""
        if lastquote.quote==None:#Empty xulpy
            value=0
        elif self.investment.product.high_low==True:
            if self.shares>0:# Bought
                value=self.shares*lastquote.quote*self.investment.product.leveraged.multiplier
            else:
                diff=(lastquote.quote-self.valor_accion)*abs(self.shares)*self.investment.product.leveraged.multiplier
                init_balance=self.valor_accion*abs(self.shares)*self.investment.product.leveraged.multiplier
                value=init_balance-diff
        else: #HL False
            value=self.shares*lastquote.quote
            
        money=Money(self.mem, value, self.investment.product.currency)

        if type==eMoneyCurrency.Product:
            return money
        elif type==eMoneyCurrency.Account:
            return money.convert(self.investment.account.currency, lastquote.datetime)
        elif type==eMoneyCurrency.User:
            return money.convert(self.investment.account.currency, lastquote.datetime).local(lastquote.datetime)

    def less_than_a_year(self):
        """Returns True, when datetime of the operation is <= a year"""
        if date.today()-self.datetime.date()<=timedelta(days=365):
            return True
        return False

    ## Función que calcula el balance  pendiente de la operacion de inversion actual
    ## Necesita haber cargado mq getbasic y operinversionesactual 
    ## lasquote es un objeto Quote
    def pendiente(self, lastquote,  type=eMoneyCurrency.Product):
        return self.balance(lastquote, type)-self.invertido(type)

    ## Función que calcula elbalance en el penultimate ida
    def penultimate(self, type=eMoneyCurrency.Product):        
        penultimate=self.investment.product.result.basic.penultimate
        if penultimate.quote==None:#Empty xulpy
            error("{} no tenia suficientes quotes en {}".format(function_name(self), self.investment.name))
            value=0
        elif self.investment.product.high_low==True:
            if self.shares>0:# Bought
                value=self.shares*penultimate.quote*self.investment.product.leveraged.multiplier
            else:
                diff=(penultimate.quote-self.valor_accion)*abs(self.shares)*self.investment.product.leveraged.multiplier
                init_balance=self.valor_accion*abs(self.shares)*self.investment.product.leveraged.multiplier
                value=init_balance-diff
        else:
            value=self.shares*penultimate.quote

        money=Money(self.mem, value, self.investment.product.currency)
        if type==eMoneyCurrency.Product:
            return money
        elif type==eMoneyCurrency.Account:
            return money.convert(self.investment.account.currency, penultimate.datetime)#Al ser balance actual usa el datetime actual
        elif type==eMoneyCurrency.User:
            return money.convert(self.investment.account.currency, penultimate.datetime).local(penultimate.datetime)
            
    def tpc_anual(self):        
        last=self.investment.product.result.basic.last.quote
        if self.datetime.year==date.today().year:
            lastyear=self.valor_accion #Product value, self.price(type) not needed.
        else:
            lastyear=self.investment.product.result.basic.lastyear.quote
        if last==None or lastyear==None:
            return Percentage()

        if self.shares>0:
            return Percentage(last-lastyear, lastyear)
        else:
            return Percentage(-(last-lastyear), lastyear)

    def tpc_total(self,  last,  type=eMoneyCurrency.Product):
        """
            last is a Quote object 
            type puede ser:
                1 Da el tanto por  ciento en la currency de la inversi´on
                2 Da el tanto por  ciento en la currency de la cuenta, por lo que se debe convertir teniendo en cuenta la temporalidad
                3 Da el tanto por ciento en la currency local, partiendo  de la conversi´on a la currency de la cuenta
        """
        if last==None:#initiating xulpymoney
            return Percentage()
        return Percentage(self.pendiente(last, type), self.invertido(type))
            
        
    def tpc_tae(self, last, type=eMoneyCurrency.Product):
        dias=self.age()
        if dias==0:
            dias=1
        return Percentage(self.tpc_total(last, type)*365,  dias)
        
        
class InvestmentOperationCurrentHeterogeneusManager(ObjectManager_With_IdDatetime_Selectable, QObject):
    """Clase es un array ordenado de objetos newInvestmentOperation"""
    def __init__(self, mem):
        ObjectManager_With_IdDatetime_Selectable.__init__(self)
        QObject.__init__(self)
        self.setConstructorParameters(mem)
        self.mem=mem

    def __repr__(self):
        try:
            inversion=self.arr[0].investment.id
        except:
            inversion= "Desconocido"
        return ("SetIOA Inv: {0}. N.Registros: {1}. N.shares: {2}. Invertido: {3}. Valor medio:{4}".format(inversion,  len(self.arr), self.shares(),  self.invertido(),  self.average_price()))
                        
    def average_age(self):
        """Average age of the current investment operations in days"""
        (sumbalance, sumbalanceage)=(Decimal(0), Decimal(0))
        for o in self.arr:
            balance=o.balance(o.investment.product.result.basic.last).convert_from_factor(o.investment.account.currency, o.currency_conversion).local()
            sumbalance=sumbalance+balance.amount
            sumbalanceage=sumbalanceage+balance.amount*o.age()
        if sumbalance!=Decimal(0):
            return round(sumbalanceage/sumbalance, 2)
        else:
            return Decimal(0)
            
    def average_price(self):
        """Calcula el precio medio de compra"""
        
        shares=Money(self.mem)
        sharesxprice=Money(self.mem)
        for o in self.arr:
            shares=shares+Money(self.mem, o.shares)
            sharesxprice=sharesxprice+Money(self.mem, o.shares*o.valor_accion)

        if shares.isZero():
            return Money(self.mem)
        return sharesxprice/shares

    def balance(self):
        """Al ser homegeneo da el resultado en Money del producto"""
        resultado=Money(self.mem, 0, self.mem.localcurrency)
        for o in self.arr:
            resultado=resultado+o.balance(o.investment.product.result.basic.last, type=3)
        return resultado        

    def shares(self):
        """Devuelve el número de acciones de la inversión actual"""
        resultado=Decimal(0)
        for o in self.arr:
            resultado=resultado+o.shares
        return resultado

    ## Returns a list with operation shares. Usefull to debug io calculations
    def list_of_shares(self):
        r=[]
        for o in self.arr:
            r.append(o.shares)
        return r

    def invertido(self):
        """Al ser heterogeneo da el resultado en Money local"""
        resultado=Money(self.mem, 0, self.mem.localcurrency)
        for o in self.arr:
            resultado=resultado+o.invertido(type=3)
        return resultado
        
    def last(self):
        """Returns last current operation with valor_accion greater than 0"""
        for o in reversed(self.arr):
            if o.valor_accion==Decimal(0):#Añadidos
                continue
            return o
        return None 
    
    def less_than_a_year(self):
        for o in self.arr:
            if o.less_than_a_year()==True:
                return True
        return False
        
    def myqtablewidget(self,  wdg):
        """Parámetros
            - tabla myQTableWidget en la que rellenar los datos
            
            Al ser heterogeneo se calcula con self.mem.localcurrency
        """
        hh=[self.tr("Date" ), self.tr("Product" ), self.tr("Account" ), self.tr("Shares" ), self.tr("Price" ), self.tr("Invested" ), 
            self.tr("Current balance" ), self.tr("Pending" ), self.tr("% annual" ), self.tr("% APR" ), self.tr("% Total" ), self.tr("Benchmark" )]
            
        #DATA
        if self.length()==0:
            wdg.table.setRowCount(0)
            return
        type=eMoneyCurrency.User
            
        data=[]
        for rownumber, a in enumerate(self.arr):     
            if a.referenciaindice==None:
                benchmark=None
            else:
                benchmark=a.referenciaindice.quote
            data.append([
                a.datetime, 
                a.investment.name, 
                a.investment.account.name, 
                a.shares,
                a.price().local(), 
                a.invertido(type), 
                a.balance(a.investment.product.result.basic.last, type), 
                a.pendiente(a.investment.product.result.basic.last, type),
                a.tpc_anual(), 
                a.tpc_tae(a.investment.product.result.basic.last, type), 
                a.tpc_total(a.investment.product.result.basic.last, type), 
                benchmark, 
            ])
        data.append([self.tr("Total"), "", "", "", "", self.invertido(), self.balance(), self.pendiente(), "", self.tpc_tae(), self.tpc_total(), ""])
        wdg.setData(hh, None, data, zonename=self.mem.localzone_name)
        for rownumber, a in enumerate(self.arr):    
            if self.mem.gainsyear==True and a.less_than_a_year()==True:
                wdg.table.item(rownumber, 0).setIcon(QIcon(":/xulpymoney/new.png"))



    def pendiente(self):
        """Calcula el resultado de pendientes utilizando lastquote como el ultimo de cada operaci´on"""
        resultado=Money(self.mem, 0, self.mem.localcurrency)
        for o in self.arr:
            resultado=resultado+o.pendiente(o.investment.product.result.basic.last, type=3)
        return resultado
    

    def tpc_tae(self):
        dias=self.average_age()
        if dias==0:
            dias=1
        return Percentage(self.tpc_total()*365, dias)

    def tpc_total(self):
        """Como es heterogenous el resultado sera en local"""
        return Percentage(self.pendiente(), self.invertido())
        
    
    def get_valor_benchmark(self, indice):
        cur=self.mem.con.cursor()
        for o in self.arr:
            o.get_referencia_indice(indice)
        cur.close()
        
    ## eMoneyCurrency.User because is heterogeneous
    def commissions(self):
        r=Money(self.mem, 0, self.mem.localcurrency)
        for a in self.arr:
            r=r+a.commission(eMoneyCurrency.User)
        return r

class InvestmentOperationCurrentHomogeneusManager(InvestmentOperationCurrentHeterogeneusManager):
    def __init__(self, mem, investment):
        InvestmentOperationCurrentHeterogeneusManager.__init__(self, mem)
        self.setConstructorParameters(mem, investment)
        self.investment=investment
    
    def average_age(self, type=eMoneyCurrency.Product):
        """Average age of the current investment operations in days"""
        (sumbalance, sumbalanceage)=(Decimal(0), Decimal(0))
        for o in self.arr:
            balance=o.balance(o.investment.product.result.basic.last, type)
            sumbalance=sumbalance+balance.amount
            sumbalanceage=sumbalanceage+balance.amount*o.age()
        if sumbalance!=Decimal(0):
            return sumbalanceage/sumbalance
        else:
            return Decimal(0)

    def average_price(self, type=eMoneyCurrency.Product):
        """Calcula el precio medio de compra"""
        
        shares=self.shares()
        currency=self.investment.resultsCurrency(type)
        sharesxprice=Decimal(0)
        for o in self.arr:
            sharesxprice=sharesxprice+o.shares*o.price(type).amount
        return Money(self.mem, 0, currency) if shares==Decimal(0) else Money(self.mem, sharesxprice/shares,  currency)
        
        
    def average_price_after_a_gains_percentage(self, percentage,  type=eMoneyCurrency.Product):
        """
            percentage is a Percentage object
            Returns a Money object after add a percentage to the average_price
        """
        return self.average_price(type)*(1+percentage.value)
        
    def invertido(self, type=eMoneyCurrency.Product):
        """Al ser homegeneo da el resultado en Money del producto"""
        currency=self.investment.resultsCurrency(type)
        resultado=Money(self.mem, 0, currency)
        for o in self.arr:
            resultado=resultado+o.invertido(type)
        return resultado
        
    def balance(self, quote, type=eMoneyCurrency.Product):
        """Al ser homegeneo da el resultado en Money del producto"""
        currency=self.investment.resultsCurrency(type)
        resultado=Money(self.mem, 0, currency)
        for o in self.arr:
            resultado=resultado+o.balance(quote, type)
        return resultado        

    def penultimate(self, type=eMoneyCurrency.Product):
        """Al ser homegeneo da el resultado en Money del producto"""
        currency=self.investment.resultsCurrency(type)
        resultado=Money(self.mem, 0, currency)
        for o in self.arr:
            resultado=resultado+o.penultimate( type)
        return resultado
        
    ## Calculates an investment selling price from a gains percentage using current operations
    ## If emoneycurrency== Account, calcula el percentage del dinero invertido. Si tienen divisas distinntas el producto y la cuenta. Calcula el porcentage dela cuenta
    ## @param percentage Percentage object to gain
    ## @return Money object with the currency of the product. It's the product price to sell.
    def selling_price_to_gain_percentage_of_invested(self, percentage, emoneycurrency):
        invested=self.invertido(emoneycurrency)
        invested_plus_gains=invested*(1+percentage.value)
        return self.selling_price_to_gain_money(invested_plus_gains-invested)

    ## Calculates an investment selling price to gain a money in the current investment
    ## @param money Money object with a currency
    ## @return Money object with the currency of the product. It's the product price to sell.
    def selling_price_to_gain_money(self, money):
        # Calculates leverage. Must be futures and CFD products to be used in calculations
        if self.investment.product.type in [eProductType.CFD,  eProductType.Future]:
            leverage=self.investment.product.leveraged.multiplier
        else:
            leverage=1
        
        #Calcultate gains in product currency
        if money.currency==self.investment.account.currency:#money in account currency
            balance_after_gains=money+self.invertido(eMoneyCurrency.Account)
            balance_after_gains_product_currency=balance_after_gains.convert(self.investment.product.currency)#Current conversion
        else:#money in product currency
            balance_after_gains_product_currency=money+self.invertido(eMoneyCurrency.Product)
            
        #Calculate price from gains in product concurrency
        if self.investment.op_actual.shares()>0:#Long position
            return Money(self.mem, balance_after_gains_product_currency.amount/self.shares()/leverage, self.investment.product.currency)
        else:#Short position
            #(Average price - PF) · Shares·Leverage=Gains. Despejando
            #Creo que esta mal por que el average price no cuenta lo que ha costado en divisa. En multidivisa
            #print(self.average_price(eMoneyCurrency.Product).amount, abs(self.shares()),  leverage,  money.amount)
            price=(self.average_price(eMoneyCurrency.Product).amount*abs(self.shares())*leverage-money.amount)/(abs(self.shares())*leverage)
            return Money(self.mem, price, self.investment.product.currency)

    ## Función que calcula la diferencia de balance entre last y penultimate
    ## Necesita haber cargado mq getbasic y operinversionesactual
    def gains_last_day(self, type=eMoneyCurrency.Product):
        return self.balance(self.investment.product.result.basic.last, type)-self.penultimate(type)

    def gains_in_selling_point(self, type=eMoneyCurrency.Product):
        """Gains in investment defined selling point"""
        if self.investment.venta!=None:
            return self.investment.selling_price(type)*self.investment.shares()-self.investment.invertido(None, type)
        return Money(self.mem,  0, self.investment.resultsCurrency(type) )
        

    def gains_from_percentage(self, percentage,  type=eMoneyCurrency.Product):
        """
            Gains a percentage from average_price
            percentage is a Percentage object
        """        
        return self.average_price(type)*percentage.value*self.shares()

    def pendiente(self, lastquote, type=eMoneyCurrency.Product):
        currency=self.investment.resultsCurrency(type)
        resultado=Money(self.mem, 0, currency)
        for o in self.arr:
            resultado=resultado+o.pendiente(lastquote, type)
        return resultado
        
    def pendiente_positivo(self, lastquote, type=eMoneyCurrency.Product):
        currency=self.investment.resultsCurrency(type)
        resultado=Money(self.mem, 0, currency)
        for o in self.arr:
            pendiente=o.pendiente(lastquote, type)
            if pendiente.isGETZero():
                resultado=resultado+pendiente
        return resultado
        
    def pendiente_negativo(self, lastquote, type=eMoneyCurrency.Product):
        currency=self.investment.resultsCurrency(type)
        resultado=Money(self.mem, 0, currency)
        for o in self.arr:
            pendiente=o.pendiente(lastquote, type)
            if pendiente.isLETZero():
                resultado=resultado+pendiente
        return resultado

    ## We dont'use result basic tpc_diario due to HL can be sold or bought
    def tpc_diario(self):
        last=self.investment.product.result.basic.last.quote
        penultimate=self.investment.product.result.basic.penultimate.quote
        if last==None or penultimate==None:
            return Percentage()
            
        if self.shares()>0:
            return Percentage(last-penultimate, penultimate)
        else:
            return Percentage(-(last-penultimate), penultimate)

    def tpc_tae(self, last,  type=eMoneyCurrency.Product):
        dias=self.average_age()
        if dias==0:
            dias=1
        return Percentage(self.tpc_total(last, type)*365, dias)

    def tpc_total(self, last, type=eMoneyCurrency.Product):
        """
            last is a Money object with investment.product currency
            type puede ser:
                1 Da el tanto por  ciento en la currency de la inversi´on
                2 Da el tanto por  ciento en la currency de la cuenta, por lo que se debe convertir teniendo en cuenta la temporalidad
                3 Da el tanto por ciento en la currency local, partiendo  de la conversi´on a la currency de la cuenta
        """
        return Percentage(self.pendiente(last, type), self.invertido(type))
    
    def myqtablewidget(self,  wdg,  quote=None, type=eMoneyCurrency.Product):
        """Función que rellena una tabla pasada como parámetro con datos procedentes de un array de objetos
        InvestmentOperationCurrent y dos valores de mystocks para rellenar los tpc correspodientes
        
        Se dibujan las columnas pero las propiedad alternate color... deben ser en designer
        
        Parámetros
            - tabla myQTableWidget en la que rellenar los datos
            - quote, si queremos cargar las operinversiones con un valor determinado se pasará la quote correspondiente. Es un Objeto quote
            - type. Si es Falsa muestra la moneda de la inversión si es verdadera con la currency de la cuentaº
        """
            
        wdg.table.setColumnCount(10)
        wdg.table.setHorizontalHeaderItem(0, qcenter(self.tr("Date" )))
        wdg.table.setHorizontalHeaderItem(1, qcenter(self.tr("Shares" )))
        wdg.table.setHorizontalHeaderItem(2, qcenter(self.tr("Price" )))
        wdg.table.setHorizontalHeaderItem(3, qcenter(self.tr("Invested" )))
        wdg.table.setHorizontalHeaderItem(4, qcenter(self.tr("Current balance" )))
        wdg.table.setHorizontalHeaderItem(5, qcenter(self.tr("Pending" )))
        wdg.table.setHorizontalHeaderItem(6, qcenter(self.tr("% annual" )))
        wdg.table.setHorizontalHeaderItem(7, qcenter(self.tr("% APR" )))
        wdg.table.setHorizontalHeaderItem(8, qcenter(self.tr("% Total" )))
        wdg.table.setHorizontalHeaderItem(9, qcenter(self.tr("Benchmark" )))
        #DATA
        if self.length()==0:
            wdg.table.setRowCount(0)
            return

        if quote==None:
            quote=self.investment.product.result.basic.last

        wdg.applySettings()
        wdg.table.clearContents()
        wdg.table.setRowCount(self.length()+1)
        for rownumber, a in enumerate(self.arr):
            wdg.table.setItem(rownumber, 0, qdatetime(a.datetime, self.mem.localzone_name))
            if self.mem.gainsyear==True and a.less_than_a_year()==True:
                wdg.table.item(rownumber, 0).setIcon(QIcon(":/xulpymoney/new.png"))
            
            wdg.table.setItem(rownumber, 1, qright(a.shares))
            wdg.table.setItem(rownumber, 2, a.price(type).qtablewidgetitem())            
            wdg.table.setItem(rownumber, 3, a.invertido(type).qtablewidgetitem())
            wdg.table.setItem(rownumber, 4, a.balance(quote, type).qtablewidgetitem())
            wdg.table.setItem(rownumber, 5, a.pendiente(quote, type).qtablewidgetitem())
            wdg.table.setItem(rownumber, 6, a.tpc_anual().qtablewidgetitem())
            wdg.table.setItem(rownumber, 7, a.tpc_tae(quote, type).qtablewidgetitem())
            wdg.table.setItem(rownumber, 8, a.tpc_total(quote, type).qtablewidgetitem())
            if a.referenciaindice==None:
                wdg.table.setItem(rownumber, 9, qnone(None))
            else:
                wdg.table.setItem(rownumber, 9, self.mem.data.benchmark.money(a.referenciaindice.quote).qtablewidgetitem())
                
        wdg.table.setItem(self.length(), 0, qcenter(("TOTAL")))
        wdg.table.setItem(self.length(), 1, qright(self.shares()))
        wdg.table.setItem(self.length(), 2, self.average_price(type).qtablewidgetitem())
        wdg.table.setItem(self.length(), 3, self.invertido(type).qtablewidgetitem())
        wdg.table.setItem(self.length(), 4, self.balance(quote, type).qtablewidgetitem())
        wdg.table.setItem(self.length(), 5, self.pendiente(quote, type).qtablewidgetitem())
        wdg.table.setItem(self.length(), 7, self.tpc_tae(quote, type).qtablewidgetitem())
        wdg.table.setItem(self.length(), 8, self.tpc_total(quote, type).qtablewidgetitem())

class InvestmentOperationHistoricalHeterogeneusManager(ObjectManager_With_Id_Selectable, QObject):
    def __init__(self, mem):
        ObjectManager_With_Id_Selectable.__init__(self)
        QObject.__init__(self)
        self.setConstructorParameters(mem)
        self.mem=mem

    def consolidado_bruto(self,  year=None,  month=None):
        resultado=Money(self.mem, 0, self.mem.localcurrency)
        for o in self.arr:        
            if year==None:#calculo historico
                resultado=resultado+o.consolidado_bruto(eMoneyCurrency.User)
            else:                
                if month==None:#Calculo anual
                    if o.fecha_venta.year==year:
                        resultado=resultado+o.consolidado_bruto(eMoneyCurrency.User)
                else:#Calculo mensual
                    if o.fecha_venta.year==year and o.fecha_venta.month==month:
                        resultado=resultado+o.consolidado_bruto(eMoneyCurrency.User)
        return resultado        
        
    def consolidado_neto(self,  year=None,  month=None):
        resultado=Money(self.mem, 0, self.mem.localcurrency)
        for o in self.arr:        
            if year==None:#calculo historico
                resultado=resultado+o.consolidado_neto(eMoneyCurrency.User)
            else:                
                if month==None:#Calculo anual
                    if o.fecha_venta.year==year:
                        resultado=resultado+o.consolidado_neto(eMoneyCurrency.User)
                else:#Calculo mensual
                    if o.fecha_venta.year==year and o.fecha_venta.month==month:
                        resultado=resultado+o.consolidado_neto(eMoneyCurrency.User)
        return resultado
        
    def consolidado_neto_antes_impuestos(self,  year=None,  month=None):
        resultado=Money(self.mem, 0, self.mem.localcurrency)
        for o in self.arr:        
            if year==None:#calculo historico
                resultado=resultado+o.consolidado_neto_antes_impuestos(eMoneyCurrency.User)
            else:                
                if month==None:#Calculo anual
                    if o.fecha_venta.year==year:
                        resultado=resultado+o.consolidado_neto_antes_impuestos(eMoneyCurrency.User)
                else:#Calculo mensual
                    if o.fecha_venta.year==year and o.fecha_venta.month==month:
                        resultado=resultado+o.consolidado_neto_antes_impuestos(eMoneyCurrency.User)
        return resultado

    def gross_purchases(self):
        """Bruto de todas las compras de la historicas"""
        r=Money(self.mem, 0, self.mem.localcurrency)
        for a in self.arr:
            r=r+a.bruto_compra(eMoneyCurrency.User)
        return r

    ## Returns a list with operation shares. Usefull to debug io calculations
    def list_of_shares(self):
        r=[]
        for o in self.arr:
            r.append(o.shares)
        return r

    def gross_sales(self):
        """Bruto de todas las compras de la historicas"""
        r=Money(self.mem, 0, self.mem.localcurrency)
        for a in self.arr:
            r=r+a.bruto_venta(eMoneyCurrency.User)
        return r
        
    def taxes(self):
        r=Money(self.mem, 0, self.mem.localcurrency)
        for a in self.arr:
            r=r+a.taxes(eMoneyCurrency.User)
        return r
        
    def tpc_total_neto(self):
        return Percentage(self.consolidado_neto(), self.gross_purchases())

    ## eMoneyCurrency.User because is heterogeneous
    def commissions(self):
        r=Money(self.mem, 0, self.mem.localcurrency)
        for a in self.arr:
            r=r+a.commission(eMoneyCurrency.User)
        return r

    def gross_positive_operations(self):
        r=Money(self.mem, 0, self.mem.localcurrency)
        for a in self.arr:
            if a.bruto(eMoneyCurrency.User).isGETZero():
                r=r+a.bruto(eMoneyCurrency.User)
        return r
    
    def gross_negative_operations(self):
        r=Money(self.mem, 0, self.mem.localcurrency)
        for a in self.arr:
            if a.bruto(eMoneyCurrency.User).isLTZero():
                r=r+a.bruto(eMoneyCurrency.User)
        return r

    def myqtablewidget(self, wdg):
        wdg.table.setColumnCount(14)
        wdg.table.setHorizontalHeaderItem(0, qcenter(self.tr( "Date" )))
        wdg.table.setHorizontalHeaderItem(1, qcenter(self.tr( "Years" )))
        wdg.table.setHorizontalHeaderItem(2, qcenter(self.tr( "Product" )))
        wdg.table.setHorizontalHeaderItem(3, qcenter(self.tr( "Account" )))
        wdg.table.setHorizontalHeaderItem(4, qcenter(self.tr( "Operation type" )))
        wdg.table.setHorizontalHeaderItem(5, qcenter(self.tr( "Shares" )))
        wdg.table.setHorizontalHeaderItem(6, qcenter(self.tr( "Initial balance" )))
        wdg.table.setHorizontalHeaderItem(7, qcenter(self.tr( "Final balance" )))
        wdg.table.setHorizontalHeaderItem(8, qcenter(self.tr( "Gross gains" )))
        wdg.table.setHorizontalHeaderItem(9, qcenter(self.tr( "Commissions" )))
        wdg.table.setHorizontalHeaderItem(10, qcenter(self.tr( "Taxes" )))
        wdg.table.setHorizontalHeaderItem(11, qcenter(self.tr( "Net gains" )))
        wdg.table.setHorizontalHeaderItem(12, qcenter(self.tr( "% Net APR" )))
        wdg.table.setHorizontalHeaderItem(13, qcenter(self.tr( "% Net Total" )))

        wdg.applySettings()
        wdg.table.clearContents()
        wdg.table.setRowCount(self.length()+1)
        for rownumber, a in enumerate(self.arr):    
            wdg.table.setItem(rownumber, 0, qdate(a.fecha_venta))
            wdg.table.setItem(rownumber, 1, qnumber(a.years(), 2))
            wdg.table.setItem(rownumber, 2, qleft(a.investment.name))
            wdg.table.setItem(rownumber, 3, qleft(a.investment.account.name))
            wdg.table.setItem(rownumber, 4, qleft(a.tipooperacion.name))
            wdg.table.setItem(rownumber, 5,qright(a.shares))
            wdg.table.setItem(rownumber, 6,a.bruto_compra(eMoneyCurrency.User).qtablewidgetitem())
            wdg.table.setItem(rownumber, 7,a.bruto_venta(eMoneyCurrency.User).qtablewidgetitem())
            wdg.table.setItem(rownumber, 8,a.consolidado_bruto(eMoneyCurrency.User).qtablewidgetitem())
            wdg.table.setItem(rownumber, 9,a.commission(eMoneyCurrency.User).qtablewidgetitem())
            wdg.table.setItem(rownumber, 10,a.taxes(eMoneyCurrency.User).qtablewidgetitem())
            wdg.table.setItem(rownumber, 11,a.consolidado_neto(eMoneyCurrency.User).qtablewidgetitem())
            wdg.table.setItem(rownumber, 12,a.tpc_tae_neto().qtablewidgetitem())
            wdg.table.setItem(rownumber, 13,a.tpc_total_neto().qtablewidgetitem())

        wdg.table.setItem(self.length(), 2,qcenter("TOTAL"))
        wdg.table.setItem(self.length(), 6,self.gross_purchases().qtablewidgetitem())    
        wdg.table.setItem(self.length(), 7,self.gross_sales().qtablewidgetitem())    
        wdg.table.setItem(self.length(), 8,self.consolidado_bruto().qtablewidgetitem())    
        wdg.table.setItem(self.length(), 9,self.commissions().qtablewidgetitem())    
        wdg.table.setItem(self.length(), 10,self.taxes().qtablewidgetitem())    
        wdg.table.setItem(self.length(), 11,self.consolidado_neto().qtablewidgetitem())
        wdg.table.setItem(self.length(), 13,self.tpc_total_neto().qtablewidgetitem())
        wdg.table.setCurrentCell(self.length(), 5)       
    
    def order_by_fechaventa(self):
        """Sort by selling date"""
        self.arr=sorted(self.arr, key=lambda o: o.fecha_venta,  reverse=False)      

class InvestmentOperationHistoricalHomogeneusManager(InvestmentOperationHistoricalHeterogeneusManager):
    def __init__(self, mem, investment):
        InvestmentOperationHistoricalHeterogeneusManager.__init__(self, mem)
        self.setConstructorParameters(mem, investment)
        self.investment=investment
        
    def taxes(self, type=eMoneyCurrency.Product):
        r=Money(self.mem,  0,  self.investment.resultsCurrency(type))
        for a in self.arr:
            r=r+a.taxes(type)
        return r

    def commissions(self, type=eMoneyCurrency.Product):
        r=Money(self.mem, 0,  self.investment.resultsCurrency(type))
        for a in self.arr:
            r=r+a.commission(type)
        return r

    def consolidado_bruto(self,  year=None,  month=None, type=eMoneyCurrency.Product):
        resultado=Money(self.mem, 0, self.investment.resultsCurrency(type))
        for o in self.arr:        
            if year==None:#calculo historico
                resultado=resultado+o.consolidado_bruto(type)
            else:                
                if month==None:#Calculo anual
                    if o.fecha_venta.year==year:
                        resultado=resultado+o.consolidado_bruto(type)
                else:#Calculo mensual
                    if o.fecha_venta.year==year and o.fecha_venta.month==month:
                        resultado=resultado+o.consolidado_bruto(type)
        return resultado
        
    def consolidado_neto(self,  year=None,  month=None, type=eMoneyCurrency.Product):
        resultado=Money(self.mem, 0, self.investment.resultsCurrency(type))
        for o in self.arr:        
            if year==None:#calculo historico
                resultado=resultado+o.consolidado_neto(type)
            else:                
                if month==None:#Calculo anual
                    if o.fecha_venta.year==year:
                        resultado=resultado+o.consolidado_neto(type)
                else:#Calculo mensual
                    if o.fecha_venta.year==year and o.fecha_venta.month==month:
                        resultado=resultado+o.consolidado_neto(type)
        return resultado
        
    def consolidado_neto_antes_impuestos(self,  year=None,  month=None):
        resultado=Money(self.mem, 0, self.investment.product.currency)
        for o in self.arr:        
            if year==None:#calculo historico
                resultado=resultado+o.consolidado_neto_antes_impuestos()
            else:                
                if month==None:#Calculo anual
                    if o.fecha_venta.year==year:
                        resultado=resultado+o.consolidado_neto_antes_impuestos()
                else:#Calculo mensual
                    if o.fecha_venta.year==year and o.fecha_venta.month==month:
                        resultado=resultado+o.consolidado_neto_antes_impuestos()
        return resultado
        
    def bruto_compra(self, type=eMoneyCurrency.Product):
        resultado=Money(self.mem,  0,  self.investment.resultsCurrency(type))
        for o in self.arr:
            resultado=resultado+o.bruto_compra(type)
        return resultado

    def bruto_venta(self, type=eMoneyCurrency.Product):
        resultado=Money(self.mem,  0,  self.investment.resultsCurrency(type))
        for o in self.arr:
            resultado=resultado+o.bruto_venta(type)
        return resultado

    def tpc_total_neto(self):
        return Percentage(self.consolidado_neto(), self.bruto_compra())

    def gross_purchases(self, type=eMoneyCurrency.Product):
        r=Money(self.mem,  0,  self.investment.resultsCurrency(type))
        for a in self.arr:
            r=r+a.bruto_compra(type)
        return r

    def gross_sales(self, type=eMoneyCurrency.Product):
        r=Money(self.mem,  0,  self.investment.resultsCurrency(type))
        for a in self.arr:
            r=r+a.bruto_venta(type)
        return r

    def myqtablewidget(self, wdg, show_accounts=False, type=eMoneyCurrency.Product):
        """Rellena datos de un array de objetos de InvestmentOperationHistorical, devuelve totales ver código"""
        diff=0
        if show_accounts==True:
            diff=2
            
        wdg.table.setColumnCount(12+diff)
        wdg.table.setHorizontalHeaderItem(0, qcenter(self.tr( "Date" )))
        wdg.table.setHorizontalHeaderItem(1, qcenter(self.tr( "Years" )))
        if show_accounts==True:
            wdg.table.setHorizontalHeaderItem(2, qcenter(self.tr( "Product" )))
            wdg.table.setHorizontalHeaderItem(3, qcenter(self.tr( "Account" )))
        wdg.table.setHorizontalHeaderItem(2+diff, qcenter(self.tr( "Operation type" )))
        wdg.table.setHorizontalHeaderItem(3+diff, qcenter(self.tr( "Shares" )))
        wdg.table.setHorizontalHeaderItem(4+diff, qcenter(self.tr( "Initial gross" )))
        wdg.table.setHorizontalHeaderItem(5+diff, qcenter(self.tr( "Final gross" )))
        wdg.table.setHorizontalHeaderItem(6+diff, qcenter(self.tr( "Gross gains" )))
        wdg.table.setHorizontalHeaderItem(7+diff, qcenter(self.tr( "Commissions" )))
        wdg.table.setHorizontalHeaderItem(8+diff, qcenter(self.tr( "Taxes" )))
        wdg.table.setHorizontalHeaderItem(9+diff, qcenter(self.tr( "Net gains" )))
        wdg.table.setHorizontalHeaderItem(10+diff, qcenter(self.tr( "% Net APR" )))
        wdg.table.setHorizontalHeaderItem(11+diff, qcenter(self.tr( "% Net Total" )))

        wdg.applySettings()
        wdg.table.clearContents()
        wdg.table.setRowCount(self.length()+1)
        for rownumber, a in enumerate(self.arr):    
            wdg.table.setItem(rownumber, 0,qdate(a.fecha_venta))
            wdg.table.setItem(rownumber, 1, qnumber(round(a.years(), 2)))
            if show_accounts==True:
                wdg.table.setItem(rownumber, 2, qleft(a.investment.name))
                wdg.table.setItem(rownumber, 3, qleft(a.investment.account.name))
            wdg.table.setItem(rownumber, 2+diff, qleft(a.tipooperacion.name))
            wdg.table.setItem(rownumber, 3+diff, qright(a.shares))
            wdg.table.setItem(rownumber, 4+diff, a.bruto_compra(type).qtablewidgetitem())
            wdg.table.setItem(rownumber, 5+diff, a.bruto_venta(type).qtablewidgetitem())
            wdg.table.setItem(rownumber, 6+diff, a.consolidado_bruto(type).qtablewidgetitem())
            wdg.table.setItem(rownumber, 7+diff,a.commission(type).qtablewidgetitem())
            wdg.table.setItem(rownumber, 8+diff,a.taxes(type).qtablewidgetitem())
            wdg.table.setItem(rownumber, 9+diff, a.consolidado_neto(type).qtablewidgetitem())
            wdg.table.setItem(rownumber, 10+diff, a.tpc_tae_neto().qtablewidgetitem())
            wdg.table.setItem(rownumber, 11+diff, a.tpc_total_neto().qtablewidgetitem())

        if self.length()>0:
            wdg.table.setItem(self.length(), 2, qleft("TOTAL"))
            wdg.table.setItem(self.length(), 4+diff, self.gross_purchases(type).qtablewidgetitem())
            wdg.table.setItem(self.length(), 5+diff, self.gross_sales(type).qtablewidgetitem())
            wdg.table.setItem(self.length(), 6+diff, self.consolidado_bruto(type=type).qtablewidgetitem())  
            wdg.table.setItem(self.length(), 7+diff, self.commissions(type).qtablewidgetitem())    
            wdg.table.setItem(self.length(), 8+diff, self.taxes(type).qtablewidgetitem())    
            wdg.table.setItem(self.length(), 9+diff, self.consolidado_neto(type=type).qtablewidgetitem())
            wdg.table.setItem(self.length(), 11+diff, self.tpc_total_neto().qtablewidgetitem())
            wdg.table.setCurrentCell(self.length(), 4+diff)
    
class InvestmentOperationHistorical:
    def __init__(self, mem):
        self.mem=mem 
        self.id=None
        self.operinversion=None
        self.investment=None
        self.fecha_inicio=None
        self.tipooperacion=None
        self.shares=None#Es negativo
        self.comision=None
        self.impuestos=None
        self.fecha_venta=None
        self.valor_accion_compra=None
        self.valor_accion_venta=None     
        self.currency_conversion_compra=None
        self.currency_conversion_venta=None
            
    def __repr__(self):
        return ("IOH {0}. {1} {2}. Acciones: {3}. Valor:{4}. Currency conversion: {5} y {6}".format(self.investment.name,  self.fecha_venta, self.tipooperacion.name,  self.shares,  self.valor_accion_venta, self.currency_conversion_compra,  self.currency_conversion_venta))
        
    def init__create(self, operinversion, inversion, fecha_inicio, tipooperacion, acciones,comision,impuestos,fecha_venta,valor_accion_compra,valor_accion_venta, currency_conversion_compra, currency_conversion_venta,  id=None):
        """Genera un objeto con los parametros. id_operinversioneshistoricas es puesto a new"""
        self.id=id
        self.operinversion=operinversion
        self.investment=inversion
        self.fecha_inicio=fecha_inicio
        self.tipooperacion=tipooperacion
        self.shares=acciones
        self.comision=comision
        self.impuestos=impuestos
        self.fecha_venta=fecha_venta
        self.valor_accion_compra=valor_accion_compra
        self.valor_accion_venta=valor_accion_venta
        self.currency_conversion_compra=currency_conversion_compra
        self.currency_conversion_venta=currency_conversion_venta
        return self
        
    def less_than_a_year(self):
        """Returns True, when datetime of the operation is <= a year"""
        if self.fecha_venta-self.fecha_inicio<=timedelta(days=365):
            return True
        return False
        
    def consolidado_bruto(self, type=eMoneyCurrency.Product):
        return self.bruto_venta(type)-self.bruto_compra(type)
        
    def consolidado_neto(self, type=eMoneyCurrency.Product):
        currency=self.investment.resultsCurrency(type)
        if self.tipooperacion.id in (eOperationType.TransferSharesOrigin, eOperationType.TransferSharesDestiny):
            return Money(self.mem, 0, currency)
        return self.consolidado_bruto(type)-self.commission(type)-self.taxes(type)

    def consolidado_neto_antes_impuestos(self, type=eMoneyCurrency.Product):
        currency=self.investment.resultsCurrency(type)
        if self.tipooperacion.id in (eOperationType.TransferSharesOrigin, eOperationType.TransferSharesDestiny):
            return Money(self.mem, 0, currency)
        return self.consolidado_bruto(type)-self.commission(type)

    def bruto_compra(self, type=eMoneyCurrency.Product):
        if self.tipooperacion.id in (eOperationType.TransferSharesOrigin, eOperationType.TransferSharesDestiny):
            value=0
        if self.investment.product.high_low==True:
            value=abs(self.shares)*self.valor_accion_compra*self.investment.product.leveraged.multiplier
        else:
            value=abs(self.shares)*self.valor_accion_compra
            
        money=Money(self.mem, value, self.investment.product.currency)
        dt=dtaware_day_end_from_date(self.fecha_inicio, self.mem.localzone_name)
        if type==eMoneyCurrency.Product:
            return money
        elif type==eMoneyCurrency.Account:
            return money.convert_from_factor(self.investment.account.currency, self.currency_conversion_compra)
        elif type==eMoneyCurrency.User:
            return money.convert_from_factor(self.investment.account.currency, self.currency_conversion_compra).local(dt)
    
    def bruto_venta(self, type=eMoneyCurrency.Product):
        if self.tipooperacion.id in (eOperationType.TransferSharesOrigin, eOperationType.TransferSharesDestiny):
            value=0
        elif self.investment.product.high_low==True:
            if self.shares<0:# Sell after a primary bought
                value=abs(self.shares)*self.valor_accion_venta*self.investment.product.leveraged.multiplier
            else:# Bought after a primary sell
                diff=(self.valor_accion_venta-self.valor_accion_compra)*abs(self.shares)*self.investment.product.leveraged.multiplier
                init_balance=self.valor_accion_compra*abs(self.shares)*self.investment.product.leveraged.multiplier
                value=init_balance-diff
        else: #HL False
            value=abs(self.shares)*self.valor_accion_venta

        money=Money(self.mem, value, self.investment.product.currency)
        dt=dtaware_day_end_from_date(self.fecha_venta, self.mem.localzone_name)
        if type==eMoneyCurrency.Product:
            return money
        elif type==eMoneyCurrency.Account:
            return money.convert_from_factor(self.investment.account.currency, self.currency_conversion_venta)
        elif type==eMoneyCurrency.User:
            return money.convert_from_factor(self.investment.account.currency, self.currency_conversion_venta).local(dt)

    def taxes(self, type=eMoneyCurrency.Product):
        money=Money(self.mem, self.impuestos, self.investment.product.currency)
        dt=dtaware_day_end_from_date(self.fecha_venta, self.mem.localzone_name)
        if type==eMoneyCurrency.Product:
            return money
        elif type==eMoneyCurrency.Account:
            return money.convert_from_factor(self.investment.account.currency, self.currency_conversion_venta)
        elif type==eMoneyCurrency.User:
            return money.convert_from_factor(self.investment.account.currency, self.currency_conversion_venta).local(dt)
    
    def commission(self, type=eMoneyCurrency.Product):
        money=Money(self.mem, self.comision, self.investment.product.currency)
        dt=dtaware_day_end_from_date(self.fecha_venta, self.mem.localzone_name)
        if type==eMoneyCurrency.Product:
            return money
        elif type==eMoneyCurrency.Account:
            return money.convert_from_factor(self.investment.account.currency, self.currency_conversion_venta)
        elif type==eMoneyCurrency.User:
            return money.convert_from_factor(self.investment.account.currency, self.currency_conversion_venta).local(dt)

    def days(self):
        return (self.fecha_venta-self.fecha_inicio).days
        
    def years(self):
        dias=self.days()
        if dias==0:#Operación intradía
            return Decimal(1/365.0)
        else:
                return dias/Decimal(365)

    def tpc_total_neto(self):
        return Percentage(self.consolidado_neto(), self.bruto_compra())
        
    def tpc_total_bruto(self):
        return Percentage(self.consolidado_bruto(), self.bruto_compra())
        
    def tpc_tae_neto(self):
        dias=(self.fecha_venta-self.fecha_inicio).days +1 #Account el primer día
        if dias==0:
            dias=1
        return Percentage(self.tpc_total_neto()*365, dias)
        


class InvestmentOperationHeterogeneusManager(ObjectManager_With_IdDatetime_Selectable, QObject):       
    """Clase es un array ordenado de objetos newInvestmentOperation"""
    def __init__(self, mem):
        ObjectManager_With_IdDatetime_Selectable.__init__(self)
        QObject.__init__(self)
        self.setConstructorParameters(mem)
        self.mem=mem
        
    def get_highest_io_id(self):
        """Get the highest IO.Id of the arr"""
        max=0
        for i in self.arr:
            if i.id>max:
                max=i.id
        return max
        
    def remove(self,  io):      
        """io is an InvestmentOPeration object
        Deletes from db and removes from array, and recalculate things"""  
        cur=self.mem.con.cursor()
        cur.execute("delete from operinversiones where id_operinversiones=%s",(io.id, ))
        cur.close()
        
        super(InvestmentOperationHeterogeneusManager, self).remove(io)
        
        (io.investment.op_actual,  io.investment.op_historica)=io.investment.op.get_current_and_historical_operations()
        io.investment.actualizar_cuentasoperaciones_asociadas()#Regenera toda la inversión.

        
    def setDistinctProducts(self):
        """Extracts distinct products in IO"""
        s=set([])
        for o in self.arr:
            s.add(o.investment.product)
        result=ProductManager(self.mem)
        result.arr=list(s)
        return result

    def order_by_datetime(self):       
        self.arr=sorted(self.arr, key=lambda e: e.datetime,  reverse=False) 

    def myqtablewidget(self, wdg):
        """Muestra los resultados en self.mem.localcurrency al ser heterogeneo().local()"""
        self.order_by_datetime()
        wdg.table.setColumnCount(10)
        wdg.table.setHorizontalHeaderItem(0, qcenter(self.tr( "Date" )))
        wdg.table.setHorizontalHeaderItem(1, qcenter(self.tr( "Product" )))
        wdg.table.setHorizontalHeaderItem(2, qcenter(self.tr( "Account" )))
        wdg.table.setHorizontalHeaderItem(3, qcenter(self.tr( "Operation type" )))
        wdg.table.setHorizontalHeaderItem(4, qcenter(self.tr( "Shares" )))
        wdg.table.setHorizontalHeaderItem(5, qcenter(self.tr( "Price" )))
        wdg.table.setHorizontalHeaderItem(6, qcenter(self.tr( "Amount" )))
        wdg.table.setHorizontalHeaderItem(7, qcenter(self.tr( "Comission" )))
        wdg.table.setHorizontalHeaderItem(8, qcenter(self.tr( "Taxes" )))
        wdg.table.setHorizontalHeaderItem(9, qcenter(self.tr( "Total" )))
        #DATA 
        wdg.applySettings()
        wdg.table.clearContents()  
        wdg.table.setRowCount(self.length())
        for rownumber, a in enumerate(self.arr):
            wdg.table.setItem(rownumber, 0, qdatetime(a.datetime, self.mem.localzone_name))
            if self.mem.gainsyear==True and a.less_than_a_year()==True:
                wdg.table.item(rownumber, 0).setIcon(QIcon(":/xulpymoney/new.png"))
        
            wdg.table.setItem(rownumber, 1, qleft(a.investment.name))
            wdg.table.setItem(rownumber, 2, qleft(a.investment.account.name))
            
            wdg.table.setItem(rownumber, 3, qleft(a.tipooperacion.name))
            if a.show_in_ranges==True:
                wdg.table.item(rownumber, 3).setIcon(QIcon(":/xulpymoney/eye.png"))
            else:
                wdg.table.item(rownumber, 3).setIcon(QIcon(":/xulpymoney/eye_red.png"))
            
            wdg.table.setItem(rownumber, 4, qright(a.shares))
            wdg.table.setItem(rownumber, 5, a.price().local().qtablewidgetitem())
            wdg.table.setItem(rownumber, 6, a.gross().local().qtablewidgetitem())
            wdg.table.setItem(rownumber, 7, a.commission().local().qtablewidgetitem())
            wdg.table.setItem(rownumber, 8, a.taxes().local().qtablewidgetitem())
            wdg.table.setItem(rownumber, 9, a.net().local().qtablewidgetitem())

    def find(self,  investmentoperation_id):
        """Returns an investmenoperation with the id equals to the parameter"""
        for o in self.arr:
            if o.id==investmentoperation_id:
                return o
        return None

class InvestmentOperationHomogeneusManager(InvestmentOperationHeterogeneusManager):
    def __init__(self, mem, investment):
        InvestmentOperationHeterogeneusManager.__init__(self, mem)
        self.setConstructorParameters(mem, investment)
        self.investment=investment

    ## InvestmentOperationHistorical hasn't id. They are generated dinamically with get_current_and_historical_operations from InvestmentOperations. 
    ## Sometimes it's necessary to work with them so I set a ficticius id: investment_id#ioh_position
    def get_current_and_historical_operations(self, test_suite=False):
        def tipo_operacion(shares):
            if shares>=0:
                return self.mem.tiposoperaciones.find_by_id(eOperationType.SharesPurchase)
            return self.mem.tiposoperaciones.find_by_id(eOperationType.SharesSale)
        def next_ioh_id():
            next_ioh_id.number=next_ioh_id.number+1
            return "{}#{}".format(self.investment.id, next_ioh_id.number)
        # ##################################
        next_ioh_id.number=0#To use it in inline functions
        sioc=InvestmentOperationCurrentHomogeneusManager(self.mem, self.investment)
        sioh=InvestmentOperationHistoricalHomogeneusManager(self.mem, self.investment)
        for o in self.arr:
            if sioc.length()==0 or have_same_sign(sioc.first().shares, o.shares)==True:
                sioc.append(InvestmentOperationCurrent(self.mem).init__create(o, o.tipooperacion, o.datetime, o.investment, o.shares, o.impuestos, o.comision, o.valor_accion,  o.show_in_ranges, o.currency_conversion,  o.id))
            elif have_same_sign(sioc.first().shares, o.shares)==False:
                rest=o.shares
                common_ioc=sioc.first() #ESTO NO ESTA EN LA FUNCION CONCEPTO, CUANDO HAY RESTO Y SIOC.LENGTH=0 NECESITA LA IFNORMACION PARA METER
                ciclos=0 #Se pone comisión en IOH en primer ciclo
                while rest!=0:
                    ciclos=ciclos+1
                    comisiones=Decimal('0')
                    impuestos=Decimal('0')
                    if ciclos==1:#Para IOH
                        comisiones=o.comision+common_ioc.comision
                        impuestos=o.impuestos+common_ioc.impuestos
                        
                    if sioc.length()>0:
                        if abs(sioc.first().shares)>abs(rest): 
                            number=set_sign_of_other_number(o.shares, rest)
#CURRENT operinversion, tipooperacion, datetime, inversion, acciones,  impuestos, comision, valor_accion, show_in_ranges,  currency_conversion, id=None):                            
#HISTORICA (operinversion, inversion, fecha_inicio, tipooperacion, acciones,comision,impuestos,fecha_venta,valor_accion_compra,valor_accion_venta, currency_conversion_compra, currency_conversion_venta,  id=None):

                            sioh.append(InvestmentOperationHistorical(self.mem).init__create(o, o.investment, sioc.first().datetime.date(), tipo_operacion(number), number, comisiones, impuestos, o.datetime.date(), sioc.first().valor_accion, o.valor_accion, sioc.first().currency_conversion, o.currency_conversion, next_ioh_id()))
                            if rest+sioc.first().shares!=0:
                                sioc.arr.insert(0, InvestmentOperationCurrent(self.mem).init__create(sioc.first(),sioc.first().tipooperacion, sioc.first().datetime, sioc.first().investment, rest+sioc.first().shares , sioc.first().impuestos, sioc.first().comision, sioc.first().valor_accion,  sioc.first().show_in_ranges, sioc.first().currency_conversion,  sioc.first().id))
                                sioc.arr.pop(1)
                            else:
                                sioc.arr.pop(0)
                            rest=0
                            break
                        else: #Mayor el resto                
                            number=set_sign_of_other_number(o.shares, sioc.first().shares)
                            sioh.append(InvestmentOperationHistorical(self.mem).init__create(o, o.investment, sioc.first().datetime.date(), tipo_operacion(number), number, comisiones, impuestos, o.datetime.date(), sioc.first().valor_accion, o.valor_accion, sioc.first().currency_conversion, o.currency_conversion, next_ioh_id()))
                            rest=rest+sioc.first().shares
                            rest=set_sign_of_other_number(o.shares, rest)
                            sioc.arr.pop(0)
                    else:
                        sioc.arr.insert(0, InvestmentOperationCurrent(self.mem).init__create(common_ioc, common_ioc.tipooperacion, common_ioc.datetime, common_ioc.investment, rest, common_ioc.impuestos, common_ioc.comision, common_ioc.valor_accion,  common_ioc.show_in_ranges, common_ioc.currency_conversion,  common_ioc.id))
                        break
        if test_suite==False:
            sioc.get_valor_benchmark(self.mem.data.benchmark)
        return (sioc, sioh)

    def myqtablewidget(self, wdg, type=eMoneyCurrency.Product):
        """Section es donde guardar en el config file, coincide con el nombre del formulario en el que está la tabla
        show_accounts, muestra el producto y la cuenta
        type muestra los money en la currency de la cuenta
        """
        
        self.order_by_datetime()
        if self.investment.hasSameAccountCurrency()==True:
            wdg.table.setColumnCount(8)
        else:
            wdg.table.setColumnCount(9)
        wdg.table.setHorizontalHeaderItem(0, qcenter(self.tr( "Date" )))
        wdg.table.setHorizontalHeaderItem(1, qcenter(self.tr( "Operation type" )))
        wdg.table.setHorizontalHeaderItem(2, qcenter(self.tr( "Shares" )))
        wdg.table.setHorizontalHeaderItem(3, qcenter(self.tr( "Price" )))
        wdg.table.setHorizontalHeaderItem(4, qcenter(self.tr( "Gross" )))
        wdg.table.setHorizontalHeaderItem(5, qcenter(self.tr( "Comission" )))
        wdg.table.setHorizontalHeaderItem(6, qcenter(self.tr( "Taxes" )))
        wdg.table.setHorizontalHeaderItem(7, qcenter(self.tr( "Total" )))
        if self.investment.hasSameAccountCurrency()==False:
            wdg.table.setHorizontalHeaderItem(8, qcenter(self.tr( "Currency conversion" )))
        
        #DATA 
        wdg.applySettings()
        wdg.table.clearContents()  
        wdg.table.setRowCount(len(self.arr))
        
        for rownumber, a in enumerate(self.arr):
            wdg.table.setItem(rownumber, 0, qdatetime(a.datetime, self.mem.localzone_name))
            if self.mem.gainsyear==True and a.less_than_a_year()==True:
                wdg.table.item(rownumber, 0).setIcon(QIcon(":/xulpymoney/new.png"))
                
            wdg.table.setItem(rownumber, 1,  qleft(a.tipooperacion.name))
            if a.show_in_ranges==True:
                wdg.table.item(rownumber, 1).setIcon(QIcon(":/xulpymoney/eye.png"))
            else:
                wdg.table.item(rownumber, 1).setIcon(QIcon(":/xulpymoney/eye_red.png"))
            
            wdg.table.setItem(rownumber, 2, qright(a.shares))
            wdg.table.setItem(rownumber, 3, a.price(type).qtablewidgetitem())
            wdg.table.setItem(rownumber, 4, a.gross(type).qtablewidgetitem())            
            wdg.table.setItem(rownumber, 5, a.commission(type).qtablewidgetitem())
            wdg.table.setItem(rownumber, 6, a.taxes(type).qtablewidgetitem())
            wdg.table.setItem(rownumber, 7, a.net(type).qtablewidgetitem())
            if self.investment.hasSameAccountCurrency()==False:
                wdg.table.setItem(rownumber, 8, qright(a.currency_conversion))

