from PyQt5.QtCore import QObject
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox, QApplication, QProgressDialog
from datetime import datetime, date
from decimal import Decimal
from logging import debug, critical, error
from math import ceil
from xulpymoney.datetime_functions import dtaware_day_end_from_date
from xulpymoney.decorators import deprecated
from xulpymoney.libmanagers import ObjectManager_With_IdName_Selectable
from xulpymoney.libxulpymoneytypes import eMoneyCurrency, eQColor, eOperationType
from xulpymoney.ui.myqwidgets import qmessagebox
from xulpymoney.objects.account import Account
from xulpymoney.objects.accountoperation import AccountOperation
from xulpymoney.objects.assets import Assets
from xulpymoney.objects.bank import Bank
from xulpymoney.objects.dividend import DividendHomogeneusManager
from xulpymoney.objects.investmentoperation import InvestmentOperationHomogeneusManager, InvestmentOperation, InvestmentOperationCurrentHeterogeneusManager, InvestmentOperation_from_row
from xulpymoney.objects.money import Money
from xulpymoney.objects.order import OrderManager
from xulpymoney.objects.percentage import Percentage
from xulpymoney.objects.product import ProductManager
from xulpymoney.objects.quote import Quote


class Investment(QObject):
    """Clase que encapsula todas las funciones que se pueden realizar con una Inversión
    
    Las entradas al objeto pueden ser por:
        - init__db_row
        - init__db_extended_row
        - create. Solo contenedor hasta realizar un save y guardar en id, el id apropiado. mientras id=None
        
    """
    def __init__(self, mem):
        QObject.__init__(self)
        """Constructor que inicializa los atributos a None"""
        self.mem=mem
        self.id=None
        self.name=None
        self.venta=None
        self.product=None#Puntero a objeto MQInvestment
        self.account=None#Vincula a un objeto  Account
        self.active=None
        self.op=None#Es un objeto SetInvestmentOperations
        self.op_actual=None#Es un objeto Setoperinversionesactual
        self.op_historica=None#setoperinversioneshistorica
        self.selling_expiration=None
        self.merged=False#If this investment is the result of merge several Investments
        self.daily_adjustment=None

        ## Variable with the current product status
        ## 0 No data
        ## 1 Loaded ops
        ## 2 Calculate ops_actual, ops_historical
        ## 3 Dividends
        self.status=0
        self.dividends=None#Must be created due to in mergeing investments needs to add it manually

    def qicon(self):
        return QIcon(":/xulpymoney/investment.png")

    ## REturn a money object with the amount and investment currency
    def money(self, amount):
        return Money(self.mem, amount, self.product.currency)

    ## ESTA FUNCION VA AUMENTANDO STATUS SIN MOLESTAR LOS ANTERIORES, SOLO CARGA CUANDO stsatus_to es mayor que self.status
    ## @param statusneeded  Integer with the status needed 
    ## @param downgrade_to Integer with the status to downgrade before checking needed status. If None it does nothing
    def needStatus(self, statusneeded, downgrade_to=None):
        if downgrade_to!=None:
            self.status=downgrade_to
        
        if self.status==statusneeded:
            return
        #0
        if self.status==0 and statusneeded==1: #MAIN
            start=datetime.now()
            self.op=InvestmentOperationHomogeneusManager(self.mem, self)
            rows=self.mem.con.cursor_rows("select * from operinversiones where id_inversiones=%s order by datetime", (self.id, ))
            for row in rows:
                self.op.append(InvestmentOperation_from_row(self.mem, row))
            self.status=1
        elif self.status==0 and statusneeded==2:
            self.needStatus(1)
            self.needStatus(2)
        elif self.status==0 and statusneeded==3:
            self.needStatus(1)
            self.needStatus(2)
            self.needStatus(3)
        elif self.status==1 and statusneeded==2: #MAIN
            start=datetime.now()
            (self.op_actual,  self.op_historica)=self.op.get_current_and_historical_operations()
            self.status=2
        elif self.status==1 and statusneeded==3:
            self.needStatus(2)
            self.needStatus(3)
        elif self.status==2 and statusneeded==3:#MAIN
            start=datetime.now()
            self.dividends=DividendHomogeneusManager(self.mem, self)
            self.dividends.load_from_db("select * from dividends where id_inversiones={0} order by fecha".format(self.id ))  
            debug("Investment {} took {} to pass from status {} to {}".format(self.name, datetime.now()-start, self.status, statusneeded))
            self.status=3

    def init__create(self, name, venta, cuenta, product, selling_expiration, active, daily_adjustment, id=None):
        self.name=name
        self.venta=venta
        self.account=cuenta
        self.product=product
        self.active=active
        self.selling_expiration=selling_expiration
        self.id=id
        self.daily_adjustment=daily_adjustment
        return self

    ## Replicates an investment with data at datetime
    ## Loads self.op, self.op_actual, self.op_historica and self.hlcontractmanager
    ## Return and Investment with status 3 (dividends inside)
    ## @param dt Datetime 
    ## @return Investment
    def Investment_At_Datetime(self, dt):
        self.needStatus(3)
        r=self.copy()
        r.op=self.op.ObjectManager_copy_until_datetime(dt)
        (r.op_actual,  r.op_historica)=r.op.get_current_and_historical_operations()
        r.dividends=self.dividends.ObjectManager_copy_until_datetime(dt)
        return r

    def copy(self ):
        return Investment(self.mem).init__create(self.name, self.venta, self.account, self.product, self.selling_expiration, self.active, self.daily_adjustment,  self.id)
    
    def save(self):
        """Inserta o actualiza la inversión dependiendo de si id=None o no"""
        cur=self.mem.con.cursor()
        if self.id==None:
            cur.execute("insert into inversiones (inversion, venta, id_cuentas, active, selling_expiration,products_id,daily_adjustment) values (%s, %s,%s,%s,%s,%s,%s) returning id_inversiones", (self.name, self.venta, self.account.id, self.active, self.selling_expiration,  self.product.id, self.daily_adjustment))    
            self.id=cur.fetchone()[0]      
        else:
            cur.execute("update inversiones set inversion=%s, venta=%s, id_cuentas=%s, active=%s, selling_expiration=%s, products_id=%s,daily_adjustment=%s where id_inversiones=%s", (self.name, self.venta, self.account.id, self.active, self.selling_expiration,  self.product.id, self.daily_adjustment, self.id))
        cur.close()

    def selling_price(self, type=eMoneyCurrency.Product):
        if type==1:
            return Money(self.mem, self.venta, self.product.currency)

    ## This function is in Investment because uses investment information
    def DividendManager_of_current_operations(self):
        self.needStatus(3)
        if self.op_actual.length()==0:
            return DividendHomogeneusManager(self.mem, self)
        else:
            return self.dividends.ObjectManager_from_datetime(self.op_actual.first().datetime)
        
    def __repr__(self):
        return ("Instancia de Investment: {0} ({1})".format( self.name, self.id))
        
    def init__db_row(self, row, cuenta, mqinvestment):
        self.id=row['id_inversiones']
        self.name=row['inversion']
        self.venta=row['venta']
        self.account=cuenta
        self.product=mqinvestment
        self.active=row['active']
        self.selling_expiration=row['selling_expiration']
        self.daily_adjustment=row['daily_adjustment']
        return self

    ## Función que devuelve un booleano si una cuenta es borrable, es decir, que no tenga registros dependientes.
    def is_deletable(self):
        self.needStatus(3)
        if self.op.length()>0:
            return False
        if self.dividends.length()>0:
            return False
        if OrderManager(self.mem).number_of_investment_orders(self)>0:# Check if has orders
            return False
        return True
        

    def actualizar_cuentasoperaciones_asociadas(self):
        #Borra las opercuentasdeoperinversiones de la inversión actual
        cur=self.mem.con.cursor()
        cur.execute("delete from opercuentasdeoperinversiones where id_inversiones=%s", (self.id, ));
        cur.close()
        for o in self.op.arr:
            o.actualizar_cuentaoperacion_asociada()
            
    def borrar(self):
        cur=self.mem.con.cursor()
        cur.execute("delete from inversiones where id_inversiones=%s", (self.id, ))
        cur.close()

    ## @returns Decimal. Amount to invest considering Zero risk assets and the number of the reinvestment
    def recommended_amount_to_invest(self):
        zr=Assets(self.mem).patrimonio_riesgo_cero(date.today()).amount
        i=ceil(zr/250000)
        if self.op_actual.length()==0:
            amount=2500
        elif self.op_actual.length()==1:
            amount=3500
        elif self.op_actual.length()>=2:
            amount=8400
        return i*amount

    def resultsCurrency(self, type=eMoneyCurrency.Product ):
        if type==1:
            return self.product.currency
        elif type==2:
            return self.account.currency
        elif type==3:
            return self.mem.localcurrency
        critical("Rare investment result currency: {}".format(type))
    
    def fullName(self):
        return "{} ({})".format(self.name, self.account.name)

    @deprecated
    def get_operinversiones(self, date=None):
        """Funci`on que carga un array con objetos inversion operacion y con ellos calcula el set de actual e historicas
        date is used to get invested balance in a particular date"""
        cur=self.mem.con.cursor()
        self.op=InvestmentOperationHomogeneusManager(self.mem, self)
        if date==None:
            cur.execute("select * from operinversiones where id_inversiones=%s order by datetime", (self.id, ))
        else:
            cur.execute("select * from operinversiones where id_inversiones=%s and datetime::date<=%s order by datetime", (self.id, date))
        for row in cur:
            self.op.append(InvestmentOperation(self.mem).init__db_row(row, self, self.mem.tiposoperaciones.find_by_id(row['id_tiposoperaciones'])))
        (self.op_actual,  self.op_historica)=self.op.get_current_and_historical_operations()
        
        cur.close()

    def dividend_bruto_estimado(self, year=None):
        """
            Si el year es None es el año actual
            Calcula el dividend estimado de la inversion se ha tenido que cargar:
                - El inversiones mq
                - La estimacion de dividends mq"""
        if year==None:
            year=date.today().year
        try:
            return Money(self.mem, self.shares()*self.product.estimations_dps.find(year).estimation, self.product.currency)
        except:
            return Money(self.mem, 0, self.product.currency)


    def shares(self, fecha=None):
        """Función que saca el número de acciones de las self.op_actual"""
        if fecha==None:
            dat=self.mem.localzone.now()
        else:
            dat=dtaware_day_end_from_date(fecha, self.mem.localzone_name)
        resultado=Decimal('0')

        for o in self.op.arr:
            if o.datetime<=dat:
                resultado=resultado+o.shares
        return resultado
        
    def hasSameAccountCurrency(self):
        """
            Returns a boolean
            Check if investment currency is the same that account currency
        """
        if self.product.currency==self.account.currency:
            return True
        return False
        
    def qmessagebox_inactive(self):
        if self.active==False:
            qmessagebox(self.tr( "The associated product is not active. You must activate it first"))
            return True
        return False

    def questionbox_inactive(self):
        """It makes a database commit"""
        if self.active==False:
            reply = QMessageBox.question(None, self.tr( 'Investment activation question'), self.tr( "Investment {} ({}) is inactive.\nDo you want to activate it?").format(self.name, self.account.name), QMessageBox.Yes, QMessageBox.No)          
            if reply==QMessageBox.Yes:
                self.active=True
                self.save()
                self.mem.con.commit()
                return QMessageBox.Yes
            return QMessageBox.No
        return QMessageBox.Yes
        
    ## Función que calcula el balance de la inversión
    def balance(self, fecha=None, type=eMoneyCurrency.Product):
        if fecha==None:
            return self.op_actual.balance(self.product.result.basic.last, type)
        else:
            quote=Quote(self.mem).init__from_query(self.product, dtaware_day_end_from_date(fecha, self.mem.localzone_name))
            if quote.datetime==None:
                debug ("Investment balance: {0} ({1}) en {2} no tiene valor".format(self.name, self.product.id, fecha))
                return Money(self.mem, 0, self.resultsCurrency(type) )
            return self.Investment_At_Datetime(dtaware_day_end_from_date(fecha, self.mem.localzone_name)).op_actual.balance(quote, type)
            
    ## Cuando tengo inversiones apalancadas, se aumenta ficticiamente el saldo y la cantidad invertida, para calculos de totales de patrimonio_riesgo_cero
    ## Necesito usar solo la cantidad sin apalancar.
    def balance_real(self, fecha, type=eMoneyCurrency.Product):
        return self.balance(fecha, type)/self.product.real_leveraged_multiplier()
        
    ## Función que calcula el balance invertido partiendo de las acciones y el precio de compra
    ## Necesita haber cargado mq getbasic y operinversionesactual
    def invertido(self, date=None, type=eMoneyCurrency.Product):
        if date==None or date==date.today():#Current
            return self.op_actual.invertido(type)
        else:
            invfake=self.Investment_At_Datetime(dtaware_day_end_from_date(date, self.mem.localzone_name))
            return invfake.op_actual.invertido(type)
                            
    ## Cuando tengo inversiones apalancadas, se aumenta ficticiamente el saldo y la cantidad invertida, para calculos de totales de patrimonio_riesgo_cero
    ## Necesito usar solo la cantidad sin apalancar.
    def invested_real(self, date, type=eMoneyCurrency.Product):
        return self.invertido(date, type)/self.product.real_leveraged_multiplier()

    def percentage_to_selling_point(self):       
        """Función que calcula el tpc venta partiendo de las el last y el valor_venta
        Necesita haber cargado mq getbasic y operinversionesactual"""
        if self.venta==0 or self.venta==None:
            return Percentage()
        if self.op_actual.shares()>0:
            return Percentage(self.venta-self.product.result.basic.last.quote, self.product.result.basic.last.quote)
        else:#Long short products
            return Percentage(-(self.venta-self.product.result.basic.last.quote), self.product.result.basic.last.quote)

class InvestmentManager(QObject, ObjectManager_With_IdName_Selectable):
    def __init__(self, mem):
        QObject.__init__(self)
        ObjectManager_With_IdName_Selectable.__init__(self)
        self.mem=mem
        self.setConstructorParameters(self.mem)

    def load_from_db(self, sql,  progress=False):
        cur=self.mem.con.cursor()
        cur.execute(sql)#"Select * from inversiones"
        for row in cur:
            inv=Investment(self.mem).init__db_row(row,  self.mem.data.accounts.find_by_id(row['id_cuentas']), self.mem.data.products.find_by_id(row['products_id']))
            self.append(inv)
        cur.close()  

    def myqtablewidget(self, wdg):
        type=eMoneyCurrency.User
        data=[]
        for i, inv in enumerate(self.arr):
            tpc_invertido=inv.op_actual.tpc_total(inv.product.result.basic.last, type)
            tpc_venta=inv.percentage_to_selling_point()
            data.append([
                inv.fullName(), 
                inv.product.result.basic.last.datetime, 
                inv.product.result.basic.last.quote, 
                inv.op_actual.gains_last_day(type),
                inv.op_actual.tpc_diario(), 
                inv.balance(None,  type), 
                inv.op_actual.pendiente(inv.product.result.basic.last, type), 
                tpc_invertido, 
                tpc_venta, 
                inv#Data with objects
            ])
        wdg.setDataWithObjects(
            [self.tr("Investment"), self.tr("Last datetime"), self.tr("Last value"), 
            self.tr("Daily difference"), self.tr("% Intraday"), self.tr("Balance"), 
            self.tr("Pending"), self.tr("% Invested"), self.tr("% Selling point")
            ], 
            None, 
            data,  
            decimals=[0, 0, 6, 2, 2, 2, 2, 2, 2], 
            zonename=self.mem.localzone_name, 
            additional=self.myqtablewidget_additional
        )   
        
    def myqtablewidget_additional(self, wdg):
        type=eMoneyCurrency.User
        for i, inv in enumerate(wdg.objects()):
            tpc_invertido=inv.op_actual.tpc_total(inv.product.result.basic.last, type)
            tpc_venta=inv.percentage_to_selling_point()
            if inv.op_actual.shares()>=0: #Long operation
                wdg.table.item(i, 0).setIcon(QIcon(":/xulpymoney/up.png"))
            else:
                wdg.table.item(i, 0).setIcon(QIcon(":/xulpymoney/down.png"))         
            if self.mem.gainsyear==True and inv.op_actual.less_than_a_year()==True:
                wdg.table.item(i, 7).setIcon(QIcon(":/xulpymoney/new.png"))
            if inv.selling_expiration!=None:
                if inv.selling_expiration<date.today():
                    wdg.table.item(i, 8).setIcon(QIcon(":/xulpymoney/alarm_clock.png"))

            if tpc_invertido.isValid() and tpc_venta.isValid():
                if tpc_invertido.value_100()<=-Decimal(50):   
                    wdg.table.item(i, 7).setBackground(eQColor.Red)
                if (tpc_venta.value_100()<=Decimal(5) and tpc_venta.isGTZero()) or tpc_venta.isLTZero():
                    wdg.table.item(i, 8).setBackground(eQColor.Green)
                

    def myqtablewidget_information(self, wdg):
#        type=eMoneyCurrency.User
        data=[]
        for i, inv in enumerate(self.arr):
            data.append([
                inv.fullName(), 
                inv.invertido(), 
                inv.balance(), 
                0, 
                inv#Data with objects
            ])
        wdg.setDataWithObjects(
            [self.tr("Investment"), self.tr("Invested"), self.tr("Balance"), self.tr("Gains")
            ], 
            None, 
            data,  
            decimals=[0, 0, 6, 2, 2, 2, 2, 2, 2], 
            zonename=self.mem.localzone_name, 
            additional=self.myqtablewidget_information_additional
        )   
        
    def myqtablewidget_information_additional(self, wdg):
        wdg.table.setRowCount(len(wdg.objects())+1)
#        type=eMoneyCurrency.User
        wdg.addRow(
            len(wdg.objects()), 
            [
                self.tr("Total"), 
                self.invested(), 
                self.balance(), 
                self.pendiente(), 
                None
            ], 
            zonename=self.mem.localzone_name)
            
#            tpc_invertido=inv.op_actual.tpc_total(inv.product.result.basic.last, type)
#            tpc_venta=inv.percentage_to_selling_point()
#            if inv.op_actual.shares()>=0: #Long operation
#                wdg.table.item(i, 0).setIcon(QIcon(":/xulpymoney/up.png"))
#            else:
#                wdg.table.item(i, 0).setIcon(QIcon(":/xulpymoney/down.png"))         
#            if self.mem.gainsyear==True and inv.op_actual.less_than_a_year()==True:
#                wdg.table.item(i, 7).setIcon(QIcon(":/xulpymoney/new.png"))
#            if inv.selling_expiration!=None:
#                if inv.selling_expiration<date.today():
#                    wdg.table.item(i, 8).setIcon(QIcon(":/xulpymoney/alarm_clock.png"))
#
#            if tpc_invertido.isValid() and tpc_venta.isValid():
#                if tpc_invertido.value_100()<=-Decimal(50):   
#                    wdg.table.item(i, 7).setBackground(eQColor.Red)
#                if (tpc_venta.value_100()<=Decimal(5) and tpc_venta.isGTZero()) or tpc_venta.isLTZero():
#                    wdg.table.item(i, 8).setBackground(eQColor.Green)

    def mqtw_active(self, wdg):                
        wdg.setDataFromManager(
            [self.tr("Investment"), self.tr("Active"), self.tr("Balance")], 
            None, 
            self, 
            ["name", "active", ("balance", [])], 
            additional=self.mqtw_active_additional
        )

    def mqtw_active_additional(self, wdg):
        wdg.table.setRowCount(self.length()+1)
        for i, o in enumerate(self.arr):
            wdg.table.item(i, 0).setIcon(o.qicon())
        wdg.addRow(self.length(), [self.tr("Total"), "#crossedout", self.balance()])

    ## Displays last current operation and shows in red background when operation has lost more than a percentage
    ## @param table MyQTableWidget
    ## @param percentage Percentage object
    def myqtablewidget_lastCurrent(self, wdg,  percentage):
        type=eMoneyCurrency.User
        data=[]
        wdg.auxiliar=percentage
        for i, inv in enumerate(self.arr):
            print(inv.op_actual.last())
            if inv.op_actual.last() is None:
                data.append([
                    "{0} ({1})".format(inv.name, inv.account.name), 
                    None, 
                    None, 
                    inv.op_actual.shares(), 
                    inv.balance(None,  type), 
                    inv.op_actual.pendiente(inv.product.result.basic.last, type), 
                    None,
                    None,
                    inv.percentage_to_selling_point(), 
                    inv, 
                ])
            else:
                data.append([
                    "{0} ({1})".format(inv.name, inv.account.name), 
                    inv.op_actual.last().datetime, 
                    inv.op_actual.last().shares, 
                    inv.op_actual.shares(), 
                    inv.balance(None,  type), 
                    inv.op_actual.pendiente(inv.product.result.basic.last, type), 
                    inv.op_actual.last().tpc_total(inv.product.result.basic.last, type=3), 
                    inv.op_actual.tpc_total(inv.product.result.basic.last, type=3),
                    inv.percentage_to_selling_point(), 
                    inv, 
                ])
        wdg.setDataWithObjects(
            [self.tr("Investment"), self.tr("Last operation"), self.tr("Last shares"), 
            self.tr("Total shares"), self.tr("Balance"), self.tr("Pending"), 
            self.tr("% Last"),  self.tr("% Invested"), self.tr("% Selling point")
            ], 
            None, 
            data,  
            decimals=[0, 0, 6, 6, 2, 2, 2, 2, 2, 2], 
            zonename=self.mem.localzone_name, 
            additional=self.myqtablewidget_lastCurrent_additional
        )   
        
    def myqtablewidget_lastCurrent_additional(self, wdg):
        percentage=wdg.auxiliar
        for i, inv in enumerate(wdg.objects()):
            if inv.op_actual.last() is not None:
                lasttpc=inv.op_actual.last().tpc_total(inv.product.result.basic.last, type=3)
                if lasttpc<percentage:
                    wdg.table.item(i, 6).setBackground(eQColor.Red)

    def mqtw_sellingpoints(self, wdg):                
        data=[]
        for o in self.arr:
            data.append([
                o.fullName(), 
                o.selling_expiration, 
                o.shares(), 
                o.money(o.venta), 
                o.percentage_to_selling_point(), 
                o, #mqtwObjects
            ])
        
        wdg.setDataWithObjects(
            [self.tr("Investment"),  self.tr("Expiration"), self.tr("Shares"), self.tr("Price"), self.tr("% selling point")], 
            None, 
            data, 
            additional=self.mqtw_sellingpoints_additional
        )
        
    ## @param wdg mqtwObjects
    def mqtw_sellingpoints_additional(self, wdg):
        for i, inv in enumerate(wdg.objects()):
                if inv.selling_expiration is not None and inv.selling_expiration<date.today():
                    wdg.table.item(i, 1).setIcon(QIcon(":/xulpymoney/alarm_clock.png"))
                wdg.table.item(i, 0).setIcon(inv.qicon())


    ## @param wdg mqtwObjects
    def mqtw_with_dps_estimations(self, wdg):
        hh= [self.tr("Investment" ), self.tr("Price" ), self.tr("DPS" ), self.tr("Shares" ), self.tr("Estimated" ), self.tr("% Annual dividend" )]
        data=[]
        for i, inv in enumerate(self.arr):
            if inv.product.estimations_dps.find(date.today().year)==None:
                dpa=0
                tpc=Percentage()
                divestimado=Money(self.mem, 0, self.mem.localcurrency)
            else:
                dpa=inv.product.estimations_dps.currentYear().estimation
                tpc=inv.product.estimations_dps.currentYear().percentage()
                divestimado=inv.dividend_bruto_estimado().local()
            data.append([
                inv.fullName(), 
                inv.product.result.basic.last.money(), 
                dpa, 
                inv.shares(), 
                divestimado, 
                tpc, 
                inv, 
            ])
        wdg.setDataWithObjects(hh, None, data,  decimals=[0, 6, 6, 6, 2, 2])

    def average_age(self):
        """Average age of the investments in this set in days"""
        #Extracts all currentinvestmentoperations
        set=InvestmentOperationCurrentHeterogeneusManager(self.mem)
        for inv in self.arr:
            for o in inv.op_actual.arr:
                set.arr.append(o)
        average=set.average_age()
        if average==None:
            return None
        return round(average, 2)

    ## Returns an InvestmentManager with operations with datetime before to parameter
    ## @param dt Aware datetime
    ## @return InvestmentManager
    def InvestmentManager_At_Datetime(self, dt):
        start=datetime.now()
        result=InvestmentManager(self.mem)
        for inv in self.arr:
            result.append(inv.Investment_At_Datetime(dt))
        debug("InvestmentManager_At_Datetime took {}".format(datetime.now()-start))
        return result


    ## Returns an InvestmentManager object with all investmentes with zero risk
    ## @param product Product to search in this InvestmentManager
    ## @return InvestmentManager
    def InvestmentManager_with_investments_with_zero_risk(self):
        result=InvestmentManager(self.mem)
        for inv in self.arr:
            if inv.product.percentage==0:
                result.append(inv)
        return result

    ## Returns an InvestmentManager object with all investmentes with the same product passed as parameter
    ## @param product Product to search in this InvestmentManager
    ## @return InvestmentManager
    def InvestmentManager_with_investments_with_the_same_product(self, product):
        result=InvestmentManager(self.mem)
        for inv in self.arr:
            if inv.product.id==product.id:
                result.append(inv)
        return result

    ## Returns an InvestmentManager object with all investmentes with the same product passed as parameter, that has zero current shares
    ## 
    ## This function is used in wdgCalculator to show investments unused
    ## @param product Product to search in this InvestmentManager
    ## @return InvestmentManager
    def InvestmentManager_with_investments_with_the_same_product_with_zero_shares(self, product):
        result=InvestmentManager(self.mem)
        for inv in self.arr:
            if inv.product.id==product.id and inv.op_actual.shares()==0:
                result.append(inv)
        return result


    ## Returns the balance of al investments
    def balance(self, date=None):
        """Da el resultado en self.mem.localcurrency"""
        r=Money(self.mem, 0, self.mem.localcurrency)
        for inv in self.arr:
            r=r+inv.balance(date, eMoneyCurrency.User)
        return r

    ## Change investments with a product_id to another product_id
    ## @param product_from. 
    ## @param product_to
    def change_product_id(self,  product_from,  product_to):
        for inv in self.InvestmentManager_with_investments_with_the_same_product(product_from).arr:
            inv.product=product_to
            inv.save()
            
    ## Gets an ivestment object from it's fullName. Used to get dinamic actions by name in wdgProductRange
    def find_by_fullName(self, s):
        for o in self.arr:
            if o.fullName()==s:
                return o
        return None

    def findInvestmentOperation(self, id):
        """Busca la IO en el set o dveuleve None"""
        for inv in self.arr:
            for o in inv.op.arr:
                if o.id==id:
                    return o
        return None

    def revaluation_monthly(self, type_id,  year, month):
        """
            Used to get investments type_id revauation montyly
            if type==2 I get current investment funds revaluation_annual
            I must use current investment, because inactive has been contabilized in gains
        """
        r=Money(self.mem, 0, self.mem.localcurrency)
        for inv in self.setinvestments_filter_by_type(type_id).arr:
            for o in inv.op_actual.arr:
                r=r+o.revaluation_monthly(year, month, type=3)
        return r
                    
    def revaluation_annual(self, type_id, year):
        """
            Used to get investments type_id revauation annual
            if type==2 I get current investment funds revaluation_annual
            I must use current investment, because inactive has been contabilized in gains
        """
        r=Money(self.mem, 0, self.mem.localcurrency)
        for inv in self.setinvestments_filter_by_type(type_id).arr:
            for o in inv.op_actual.arr:
                r=r+o.revaluation_annual(year, type=3)
        return r
            
    def gains_last_day(self):
        """Da el resultado en self.mem.localcurrency"""
        r=Money(self.mem, 0, self.mem.localcurrency)
        for inv in self.arr:
            r=r+inv.op_actual.gains_last_day(type=3)
        return r 

    def invested(self):
        """Da el resultado en self.mem.localcurrency"""
        r=Money(self.mem, 0, self.mem.localcurrency)
        for inv in self.arr:
            r=r+inv.invertido(type=3)
        return r            
    
    ## Passes product.needStatus method to all products in arr
    ## @param needstatus Status needed
    ## @param progress Boolean. If true shows a progress bar
    def needStatus(self, needstatus,  progress=False):
        if progress==True:
            pd= QProgressDialog(self.tr("Loading additional data to {0} investments from database").format(self.length()),None, 0,self.length())
            pd.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
            pd.setModal(True)
            pd.setWindowTitle(self.tr("Loading investments..."))
            pd.forceShow()
        for i, inv in enumerate(self.arr):
            if progress==True:
                pd.setValue(i)
                pd.update()
                QApplication.processEvents()
            inv.needStatus(needstatus)
            
    def numberWithSameProduct(self, product):
        """
            Returns the number of investments with the same product in the array
        """
        r=0
        for inv in self.arr:
            if inv.product.id==product.id:
                r=r+1
        return r
        
    def pendiente(self):
        """Da el resultado en self.mem.localcurrency"""
        r=Money(self.mem, 0, self.mem.localcurrency)
        for inv in self.arr:
            r=r+inv.op_actual.pendiente(inv.product.result.basic.last, 3)
        return r

    def pendiente_positivo(self):
        """Da el resultado en self.mem.localcurrency"""
        r=Money(self.mem, 0, self.mem.localcurrency)
        for inv in self.arr:
            pendiente=inv.op_actual.pendiente(inv.product.result.basic.last, 3)
            if pendiente.isGETZero():
                r=r+pendiente
        return r
    def pendiente_negativo(self):
        """Da el resultado en self.mem.localcurrency"""
        r=Money(self.mem, 0, self.mem.localcurrency)
        for inv in self.arr:
            pendiente=inv.op_actual.pendiente(inv.product.result.basic.last, 3)
            if pendiente.isLETZero():
                r=r+pendiente
        return r

    ## @param only_with_shares Boolean. If True only investments of products used with shares in current operations. If False all used products with investments
    def ProductManager_with_investments_distinct_products(self, only_with_shares=False):
        """Returns a SetProduct with all distinct products of the Set investments items"""
        r=ProductManager(self.mem)
        for i in self.arr:
            if only_with_shares==True:
                if i.shares()!=0:
                    r.append_distinct(i.product)
            else:
                r.append_distinct(i.product)
        return r
        

    def Investment_merging_operations_with_same_product(self,  product):
        """
            Returns and investment object, with all operations of the invesments with the same product. The merged investments are in the set
            The investment and the operations are copied objects.
            
            Tiene cuenta como None, Active=False y Id=None
            
            Account no es necesaria pero para mostrar algunas tablas con los calculos (currency) se necesita por lo que se puede pasar como parametro. Por ejemplo
            en frmReportInvestment, se pasar´ia la< cuenta asociada ala inversi´on del informe.
            
            Realmente es aplicar el m´etodo FIFO  a todas las inversiones.
            
        """
        name=self.tr( "Virtual investment merging all operations of {}".format(product.name))
        bank=Bank(self.mem).init__create("Merging bank", True, -1)
        account=Account(self.mem, "Merging account",  bank, True, "", self.mem.localcurrency, -1)
        r=Investment(self.mem).init__create(name, None, account, product, None, True, False, -1)
        r.op=InvestmentOperationHomogeneusManager(self.mem, r)
        r.dividends=DividendHomogeneusManager(self.mem, r)
        for inv in self.arr: #Recorre las inversion del array
            if inv.product.id==product.id:
                inv.needStatus(3)
                for o in inv.op.arr:
                    #En operations quito los traspasos, ya que fallaban calculos dobles pasadas y en realidad no hace falta porque son transpasos entre mismos productos
                    #En operations actual no hace falta porque se eliminan los transpasos origen de las operaciones actuales
                    if o.tipooperacion.id not in (eOperationType.TransferSharesOrigin, eOperationType.TransferSharesDestiny):
                        io=o.copy(investment=r)
                        r.op.append(io)  

                for d in inv.dividends.arr:
                    r.dividends.append(d)
                   
        r.dividends.order_by_datetime()
        r.op.order_by_datetime()
        (r.op_actual,  r.op_historica)=r.op.get_current_and_historical_operations()
        r.status=3#With dividends loaded manually            
        r.merged=True
        return r

    def Investment_merging_current_operations_with_same_product(self, product):
        """
            Funci´on que convierte el set actual de inversiones, sacando las del producto pasado como parámetro
            Crea una inversi´on nueva cogiendo las  operaciones actuales, juntándolas , convirtiendolas en operaciones normales 
            
            se usa para hacer reinversiones, en las que no se ha tenido cuenta el metodo fifo, para que use las acciones actuales.
        """
        name=self.tr( "Virtual investment merging current operations of {}".format(product.name))
        bank=Bank(self.mem).init__create("Merging bank", True, -1)
        account=Account(self.mem, "Merging account",  bank, True, "", self.mem.localcurrency, -1)
        r=Investment(self.mem).init__create(name, None, account, product, None, True, False,  -1)    
        r.op=InvestmentOperationHomogeneusManager(self.mem, r)
        r.dividends=DividendHomogeneusManager(self.mem, r)
        for inv in self.arr: #Recorre las inversion del array
            if inv.product.id==product.id:
                inv.needStatus(3)
                for o in inv.op_actual.arr:
                    r.op.append(InvestmentOperation(self.mem, o.tipooperacion, o.datetime, r, o.shares, o.impuestos, o.comision,  o.valor_accion,  o.comision,  o.show_in_ranges,  o.currency_conversion,  o.id))
                for d in inv.DividendManager_of_current_operations().arr:
                    r.dividends.append(d)
        r.dividends.order_by_datetime()
        r.op.order_by_datetime() 
        (r.op_actual,  r.op_historica)=r.op.get_current_and_historical_operations()
        r.status=3#With dividends loaded manually
        r.merged=True
        return r

    def setinvestments_filter_by_type(self,  type_id):
        """
            Returns a new setinvestments filtering original by type_id
            For example to get all funds in the original setinvesmet
        """
        r=InvestmentManager(self.mem )
        for inv in self.arr:
            if inv.product.type.id==type_id:
                r.append(inv)
        return r

        
    def InvestmentManager_merging_investments_with_same_product_merging_operations(self):
        """
            Genera un set Investment nuevo , creando invesments aglutinadoras de todas las inversiones con el mismo producto
            
            Account no es necesaria pero para mostrar algunas tablas con los calculos (currency) se necesita por lo que se puede pasar como parametro. Por ejemplo
            en frmReportInvestment, se pasar´ia la< cuenta asociada ala inversi´on del informe.
            
        """
        invs=InvestmentManager(self.mem)
        for product in self.ProductManager_with_investments_distinct_products().arr:
            i=self.Investment_merging_operations_with_same_product(product)
            invs.append(i) 
        return invs

    def InvestmentManager_merging_investments_with_same_product_merging_current_operations(self):
        """
            Genera un set Investment nuevo , creando invesments aglutinadoras de todas las inversiones con el mismo producto
            
            Account no es necesaria pero para mostrar algunas tablas con los calculos (currency) se necesita por lo que se puede pasar como parametro. Por ejemplo
            en frmReportInvestment, se pasar´ia la< cuenta asociada ala inversi´on del informe.
            
        """
        invs=InvestmentManager(self.mem)
        for product in self.ProductManager_with_investments_distinct_products().arr:
            i=self.Investment_merging_current_operations_with_same_product(product)
            invs.append(i) 
        return invs

    def qcombobox_same_investmentmq(self, combo,  investmentmq):
        """Muestra las inversiones activas que tienen el mq pasado como parametro"""
        arr=[]
        for i in self.arr:
            if i.active==True and i.product==investmentmq:
                arr.append(("{0} - {1}".format(i.account.bank.name, i.name), i.id))
                        
        arr=sorted(arr, key=lambda a: a[0]  ,  reverse=False)  
        for a in arr:
            combo.addItem(a[0], a[1])

    def qcombobox(self, combo, tipo, selected=None, obsolete_product=False, investments_active=True,  accounts_active=True):
        """
        Investments_active puede tomar None. Muestra Todas, True. Muestra activas y False Muestra inactivas
        Accounts_active puede tomar None. Muestra Todas, True. Muestra activas y False Muestra inactivas
        Obsolete_product puede tomar True: Muestra tambien obsoletos y False, no muestra los obsoletos
        tipo es una variable que controla la forma de visualizar
        0: inversion
        1: eb - inversion
        2: inversion (cuenta)
        3: Cuenta - inversion
        
        selected is an Investment object"""
        combo.clear()
        arr=[]
        for i in self.arr:
            if accounts_active==True:
                if i.account.active==False:
                    continue
            elif accounts_active==False:
                if i.account.active==True:
                    continue
                    
            if investments_active==True:
                if i.active==False:
                    continue
            elif investments_active==False:
                if i.active==True:
                    continue
                    
            if obsolete_product==False:
                if i.product.obsolete==True:
                    continue

            if tipo==0:
                arr.append((i.name, i.id))            
            elif tipo==1:
                arr.append(("{} - {}".format(i.account.bank.name, i.name), i.id))
            elif tipo==2:
                arr.append(("{} ({})".format(i.name, i.account.name), i.id))
            elif tipo==3:
                arr.append(("{} - {}".format(i.account.name, i.name), i.id))
                
        
        arr=sorted(arr, key=lambda a: a[0]  ,  reverse=False)  
        for a in arr:
            combo.addItem(a[0], a[1])
        if selected==None:
            combo.setCurrentIndex(-1)
        else:
            combo.setCurrentIndex(combo.findData(selected.id))
            
    def traspaso_valores(self, origen, destino, numacciones, comision):
        """Función que realiza un traspaso de valores desde una inversion origen a destino
        
        En origen:
            - Debe comprobar que origen y destino es el mismo
            - Se añade una operinversion con traspaso de valores origen que tendrá un balance de acciones negativo
            - Se añadirá un comentario con id_inversiondestino
            
        En destino:
            - Se añaden tantas operaciones como operinversionesactual con misma datetime 
            - Tendrán balance positivo y el tipo operacion es traspaso de valores. destino 
            - Se añadirá un comentario con id_operinversion origen
            
        Devuelve False si ha habido algún problema
        
        ACTUALMENTE SOLO HACE UN TRASLADO TOTAL
        """
        #Comprueba que el subyacente de origen y destino sea el mismo
        if origen.product!=destino.product:
            return False
        now=self.mem.localzone.now()
        currency_conversion=1
        if comision!=0:
            op_cuenta=AccountOperation(self.mem, now.date(), self.mem.conceptos.find_by_id(38), self.mem.tiposoperaciones.find_by_id(1), -comision, "Traspaso de valores", origen.account, None)
            op_cuenta.save()           
            comentario="{0}|{1}".format(destino.id, op_cuenta.id)
        else:
            comentario="{0}|{1}".format(destino.id, "None")
        
        op_origen=InvestmentOperation(self.mem).init__create( self.mem.tiposoperaciones.find_by_id(9), now, origen,  -numacciones, 0,0, comision, 0, comentario, True, currency_conversion)
        op_origen.save( False)      

        #NO ES OPTIMO YA QUE POR CADA SAVE SE CALCULA TODO
        comentario="{0}".format(op_origen.id)
        for o in origen.op_actual.arr:
            op_destino=InvestmentOperation(self.mem).init__create( self.mem.tiposoperaciones.find_by_id(10), now, destino,  o.shares, o.importe, o.impuestos, o.comision, o.valor_accion, comentario,  o.show_in_ranges, currency_conversion)
            op_destino.save( False)
            
        #Vuelvo a introducir el comentario de la opercuenta
        self.mem.con.commit()
        (origen.op_actual,  origen.op_historica)=origen.op.get_current_and_historical_operations()   
        (destino.op_actual,  destino.op_historica)=destino.op.get_current_and_historical_operations()   
        return True
        
    def traspaso_valores_deshacer(self, operinversionorigen):
        """Da marcha atrás a un traspaso de valores realizado por equivocación
        Solo se podrá hacer desde el listado de operinversiones
        Elimina todos los operinversion cuyo id_tipooperacion=10 (destino) cuyo comentario tengo "idorigen|"
        Se comprobará antes de eliminar que el id_inversiondestino del comentario coincide con los que quiero eliminar
        Elimina el id_operinversionorigen"""        
#        try:
        (id_inversiondestino, id_opercuentacomision)=operinversionorigen.comentario.split("|")
        origen=operinversionorigen.investment
        destino=self.find_by_id(int(id_inversiondestino))
        cur=self.mem.con.cursor()
#        print (cur.mogrify("delete from operinversiones where id_tiposoperaciones=10 and id_inversiones=%s and comentario=%s", (id_inversiondestino, str(operinversionorigen.id))))

        cur.execute("delete from operinversiones where id_tiposoperaciones=10 and id_inversiones=%s and comentario=%s", (destino.id, str(operinversionorigen.id)))
        cur.execute("delete from operinversiones where id_operinversiones=%s", (operinversionorigen.id, ))
        if id_opercuentacomision!="None":
            cur.execute("delete from opercuentas where id_opercuentas=%s", (int(id_opercuentacomision), ))
            
        self.mem.con.commit()
        origen.get_operinversiones()
        destino.get_operinversiones()
        cur.close()
        return True

    def order_by_percentage_daily(self):
        """Orders the Set using self.arr"""
        try:
            self.arr=sorted(self.arr, key=lambda inv: inv.product.result.basic.tpc_diario(),  reverse=True) 
            return True
        except:
            return False

    def order_by_selling_expiration(self):
        """Orders the Set using self.arr"""
        try:
            self.arr=sorted(self.arr, key=lambda inv: inv.selling_expiration,  reverse=False) 
            return True
        except:
            return False


    def order_by_percentage_last_operation(self):
        """Orders the Set using self.arr"""
        try:
            self.arr=sorted(self.arr, key=lambda inv: inv.op_actual.last().tpc_total(inv.product.result.basic.last, type=3),  reverse=True)
            return True
        except:
            return False
            
    def order_by_datetime_last_operation(self):
        """Orders the Set using self.arr"""
        try:
            self.arr=sorted(self.arr, key=lambda inv: inv.op_actual.last().datetime,  reverse=False) 
            return True
        except:
            return False


    def order_by_percentage_sellingpoint(self):
        self.order_with_none(["percentage_to_selling_point", ()], False, True)

    def order_by_percentage_invested(self):
        """Orders the Set using self.arr"""
            
        try:
            self.arr=sorted(self.arr, key=lambda inv: inv.op_actual.tpc_total(inv.product.result.basic.last, type=3),  reverse=True) 
            return True
        except:
            return False
            
    def order_by_datetime(self):
        """Orders the Set using self.arr"""
        try:
            self.arr=sorted(self.arr, key=lambda c: c.product.result.basic.last.datetime,  reverse=False)  
            return True
        except:
            return False
            
    def order_by_dividend(self):
        """Orders the Set using self.arr"""
        try:
            self.arr=sorted(self.arr, key=lambda inv: inv.product.estimations_dps.currentYear().percentage(),  reverse=True) 
            return True
        except:
            return False
            
    def order_by_balance(self, fecha=None,  type=3):
        """Orders the Set using self.arr"""
        try:
            self.arr=sorted(self.arr, key=lambda inv: inv.balance(fecha, type),  reverse=True) 
            return True
        except:
            error("InvestmentManager can't order by balance")
            return False

def InvestmentManager_from_list_of_ids( mem, l):
    invs=InvestmentManager(mem)
    for inv in mem.data.investments:
        if inv.id in l:
            invs.append(inv)
    return invs
