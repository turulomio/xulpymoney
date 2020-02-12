## @namespace xulpymoney.libxulpymoney
## @brief Package with all xulpymoney core classes .

from PyQt5.QtCore import QObject, Qt,  QCoreApplication
from PyQt5.QtGui import QIcon,  QColor,  QPixmap
from PyQt5.QtWidgets import QTableWidgetItem,   QMessageBox, QApplication, QProgressDialog
from datetime import datetime, timedelta, date, time
from decimal import Decimal, getcontext
from logging import debug, info, critical, error
from pytz import timezone
from xulpymoney.datetime_functions import dtaware, dtaware_day_end_from_date,  days2string, dtaware_month_end, dtaware_month_start, dtaware_year_end, dtaware_year_start
from xulpymoney.decorators import deprecated
from xulpymoney.libxulpymoneyfunctions import  function_name, have_same_sign, set_sign_of_other_number
from xulpymoney.ui.myqtablewidget import qdatetime, qright, qleft, qdate, qnumber
from xulpymoney.libxulpymoneytypes import eConcept, eComment,  eProductType,  eOperationType,  eLeverageType,  eQColor, eMoneyCurrency
from xulpymoney.libmanagers import Object_With_IdName, ObjectManager_With_Id_Selectable, ObjectManager_With_IdName_Selectable, ObjectManager_With_IdDatetime_Selectable,  DictObjectManager_With_IdName_Selectable
from xulpymoney.objects.account import Account, AccountManager
from xulpymoney.objects.accountoperation import AccountOperation, AccountOperationOfInvestmentOperation
from xulpymoney.objects.comment import Comment
from xulpymoney.objects.estimation import EstimationDPSManager, EstimationEPSManager
from xulpymoney.objects.dps import  DPSManager
from xulpymoney.objects.money import Money
from xulpymoney.objects.ohcl import OHCLDaily, OHCLDailyManager
from xulpymoney.objects.order import OrderManager
from xulpymoney.objects.percentage import Percentage
from xulpymoney.objects.product import ProductManager
from xulpymoney.objects.quote import Quote, QuoteAllIntradayManager


getcontext().prec=20



class SimulationTypeManager(ObjectManager_With_IdName_Selectable):
    def __init__(self, mem):
        ObjectManager_With_IdName_Selectable.__init__(self)
        self.mem=mem

    def load_all(self):
        self.append(SimulationType().init__create(1,QApplication.translate("Mem","Xulpymoney between dates")))
        self.append(SimulationType().init__create(2,QApplication.translate("Mem","Xulpymvoney only investments between dates")))
        self.append(SimulationType().init__create(3,QApplication.translate("Mem","Simulating current benchmark between dates")))
        
    def qcombobox(self, combo,  selected=None):
        """selected is a SimulationType object""" 
        ###########################
        combo.clear()
        for a in self.arr:
            combo.addItem(a.qicon(), a.name, a.id)

        if selected!=None:
                combo.setCurrentIndex(combo.findData(selected.id))

class InvestmentManager(QObject, ObjectManager_With_IdName_Selectable):
    def __init__(self, mem, cuentas, products, benchmark):
        QObject.__init__(self)
        ObjectManager_With_IdName_Selectable.__init__(self)
        self.mem=mem
        self.accounts=cuentas
        self.products=products
        self.benchmark=benchmark  ##Objeto product

    def load_from_db(self, sql,  progress=False):
        cur=self.mem.con.cursor()
        cur.execute(sql)#"Select * from inversiones"
        for row in cur:
            inv=Investment(self.mem).init__db_row(row,  self.accounts.find_by_id(row['id_cuentas']), self.products.find_by_id(row['products_id']))
            self.append(inv)
        cur.close()  

    def myqtablewidget(self, wdg):
        type=eMoneyCurrency.User
        data=[]
        for i, inv in enumerate(self.arr):
            tpc_invertido=inv.op_actual.tpc_total(inv.product.result.basic.last, type)
            tpc_venta=inv.percentage_to_selling_point()
            data.append([
                "{0} ({1})".format(inv.name, inv.account.name), 
                inv.product.result.basic.last.datetime, 
                inv.product.result.basic.last.quote, 
                inv.op_actual.gains_last_day(type),
                inv.op_actual.tpc_diario(), 
                inv.balance(None,  type), 
                inv.op_actual.pendiente(inv.product.result.basic.last, type), 
                tpc_invertido, 
                tpc_venta, 
            ])
        wdg.setData(
            [self.tr("Investment"), self.tr("Last datetime"), self.tr("Last value"), 
            self.tr("Daily difference"), self.tr("% Intraday"), self.tr("Balance"), 
            self.tr("Pending"), self.tr("% Invested"), self.tr("% Selling point")
            ], 
            None, 
            data,  
            decimals=[0, 0, 6, 2, 2, 2, 2, 2, 2], 
            zonename=self.mem.localzone_name, 
        )   
        
        """Esta tabla muestra los money con la moneda local"""
        for i, inv in enumerate(self.arr):
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

    ## Displays last current operation and shows in red background when operation has lost more than a percentage
    ## @param table MyQTableWidget
    ## @param percentage Percentage object
    def myqtablewidget_lastCurrent(self, wdg,  percentage):
        type=eMoneyCurrency.User
        data=[]
        for i, inv in enumerate(self.arr):
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
            ])
        wdg.setData(
            [self.tr("Investment"), self.tr("Last operation"), self.tr("Last shares"), 
            self.tr("Total shares"), self.tr("Balance"), self.tr("Pending"), 
            self.tr("% Last"),  self.tr("% Invested"), self.tr("% Selling point")
            ], 
            None, 
            data,  
            decimals=[0, 0, 6, 6, 2, 2, 2, 2, 2], 
            zonename=self.mem.localzone_name, 
        )   
        for i, inv in enumerate(self.arr):
            lasttpc=inv.op_actual.last().tpc_total(inv.product.result.basic.last, type=3)
            if lasttpc<percentage:
                wdg.table.item(i, 6).setBackground(eQColor.Red)

    def myqtablewidget_sellingpoints(self, wdg):
        """Crea un set y luego construye la tabla"""
        
        set=InvestmentManager(self.mem,  self.accounts, self.products, self.benchmark)
        for inv in self.arr:
            if inv.selling_expiration!=None and inv.shares()>0:
                set.append(inv)
        set.order_by_percentage_sellingpoint()
        
        wdg.table.setColumnCount(7)
        wdg.table.setHorizontalHeaderItem(0, QTableWidgetItem(QApplication.translate("Mem","Date")))
        wdg.table.setHorizontalHeaderItem(1, QTableWidgetItem(QApplication.translate("Mem","Expiration")))
        wdg.table.setHorizontalHeaderItem(2, QTableWidgetItem(QApplication.translate("Mem","Investment")))
        wdg.table.setHorizontalHeaderItem(3, QTableWidgetItem(QApplication.translate("Mem","Account")))
        wdg.table.setHorizontalHeaderItem(4, QTableWidgetItem(QApplication.translate("Mem","Shares")))
        wdg.table.setHorizontalHeaderItem(5, QTableWidgetItem(QApplication.translate("Mem","Price")))
        wdg.table.setHorizontalHeaderItem(6, QTableWidgetItem(QApplication.translate("Mem","% selling point")))
   
        wdg.applySettings()
        wdg.table.clearContents()
        wdg.table.setRowCount(set.length())
        for i, inv in enumerate(set.arr):
            if inv.selling_expiration!=None:
                wdg.table.setItem(i, 0, qdate(inv.op_actual.last().datetime.date()))
                wdg.table.setItem(i, 1, qdate(inv.selling_expiration))    
                if inv.selling_expiration<date.today():
                    wdg.table.item(i, 1).setBackground(eQColor.Red)       
                wdg.table.setItem(i, 2, qleft(inv.name))
                wdg.table.setItem(i, 3, qleft(inv.account.name))   
                wdg.table.setItem(i, 4, qright(inv.shares()))
                wdg.table.setItem(i, 5, inv.product.currency.qtablewidgetitem(inv.venta))
                wdg.table.setItem(i, 6, inv.percentage_to_selling_point().qtablewidgetitem())


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
        result=InvestmentManager(self.mem, self.accounts, self.products, self.benchmark)
        for inv in self.arr:
            result.append(inv.Investment_At_Datetime(dt))
        debug("InvestmentManager_At_Datetime took {}".format(datetime.now()-start))
        return result


    ## Returns an InvestmentManager object with all investmentes with zero risk
    ## @param product Product to search in this InvestmentManager
    ## @return InvestmentManager
    def InvestmentManager_with_investments_with_zero_risk(self):
        result=InvestmentManager(self.mem, self.accounts, self.products, self.benchmark)
        for inv in self.arr:
            if inv.product.percentage==0:
                result.append(inv)
        return result

    ## Returns an InvestmentManager object with all investmentes with the same product passed as parameter
    ## @param product Product to search in this InvestmentManager
    ## @return InvestmentManager
    def InvestmentManager_with_investments_with_the_same_product(self, product):
        result=InvestmentManager(self.mem, self.accounts, self.products, self.benchmark)
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
        result=InvestmentManager(self.mem, self.accounts, self.products, self.benchmark)
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
            pd= QProgressDialog(QApplication.translate("Mem","Loading additional data to {0} investments from database").format(self.length()),None, 0,self.length())
            pd.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
            pd.setModal(True)
            pd.setWindowTitle(QApplication.translate("Mem","Loading investments..."))
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

    def ProductManager_with_investments_distinct_products(self):
        """Returns a SetProduct with all distinct products of the Set investments items"""
        s=set([])
        for i in self.arr:
            s.add(i.product)
            
        r=ProductManager(self.mem)
        for p in s:
            r.append(p)        
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
        name=QApplication.translate("Mem", "Virtual investment merging all operations of {}".format(product.name))
        bank=Bank(self.mem).init__create("Merging bank", True, -1)
        account=Account(self.mem, "Merging account",  bank, True, "", self.mem.localcurrency, -1)
        r=Investment(self.mem).init__create(name, None, account, product, None, True, -1)
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
        name=QApplication.translate("Mem", "Virtual investment merging current operations of {}".format(product.name))
        bank=Bank(self.mem).init__create("Merging bank", True, -1)
        account=Account(self.mem, "Merging account",  bank, True, "", self.mem.localcurrency, -1)
        r=Investment(self.mem).init__create(name, None, account, product, None, True, -1)    
        r.op=InvestmentOperationHomogeneusManager(self.mem, r)
        r.dividends=DividendHomogeneusManager(self.mem, r)
        for inv in self.arr: #Recorre las inversion del array
            if inv.product.id==product.id:
                inv.needStatus(3)
                for o in inv.op_actual.arr:
                    r.op.append(InvestmentOperation(self.mem).init__create(o.tipooperacion, o.datetime, r, o.shares, o.impuestos, o.comision,  o.valor_accion,  o.comision,  o.show_in_ranges,  o.currency_conversion,  o.id))
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
        r=InvestmentManager(self.mem, self.mem.data.accounts, self.mem.data.products, self.mem.data.benchmark )
        for inv in self.arr:
            if inv.product.type.id==type_id:
                r.append(inv)
        return r

    def setInvestments_merging_investments_with_same_product_merging_operations(self):
        """
            Genera un set Investment nuevo , creando invesments aglutinadoras de todas las inversiones con el mismo producto
            
            Account no es necesaria pero para mostrar algunas tablas con los calculos (currency) se necesita por lo que se puede pasar como parametro. Por ejemplo
            en frmReportInvestment, se pasar´ia la< cuenta asociada ala inversi´on del informe.
            
        """
        invs=InvestmentManager(self.mem, None, self.mem.data.products, self.mem.data.benchmark)
        for product in self.ProductManager_with_investments_distinct_products().arr:
            i=self.Investment_merging_operations_with_same_product(product)
            invs.append(i) 
        return invs

                
    def setInvestments_merging_investments_with_same_product_merging_current_operations(self):
        """
            Genera un set Investment nuevo , creando invesments aglutinadoras de todas las inversiones con el mismo producto
            
            Account no es necesaria pero para mostrar algunas tablas con los calculos (currency) se necesita por lo que se puede pasar como parametro. Por ejemplo
            en frmReportInvestment, se pasar´ia la< cuenta asociada ala inversi´on del informe.
            
        """
        invs=InvestmentManager(self.mem, None, self.mem.data.products, self.mem.data.benchmark)
        for product in self.ProductManager_with_investments_distinct_products().arr:
            i=self.Investment_merging_current_operations_with_same_product(product)
            invs.append(i) 
        return invs






    def qcombobox_same_investmentmq(self, combo,  investmentmq):
        """Muestra las inversiones activas que tienen el mq pasado como parametro"""
        arr=[]
        for i in self.arr:
            if i.active==True and i.product==investmentmq:
                arr.append(("{0} - {1}".format(i.account.eb.name, i.name), i.id))
                        
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
                arr.append(("{} - {}".format(i.account.eb.name, i.name), i.id))
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
        """Orders the Set using self.arr"""
        try:
            self.arr=sorted(self.arr, key=lambda inv: inv.percentage_to_selling_point(),  reverse=False)##, -inv.op_actual.tpc_total(inv.product.result.basic.last, type=3)),  reverse=False) #Ordenado por dos criterios
            return True
        except:
            return False
            
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
        


class ProductModesManager(ObjectManager_With_IdName_Selectable):
    """Agrupa los mode"""
    def __init__(self, mem):
        ObjectManager_With_IdName_Selectable.__init__(self)
        self.mem=mem     
    
    def load_all(self):
        self.append(ProductMode(self.mem).init__create("p",QApplication.translate("Mem","Put")))
        self.append(ProductMode(self.mem).init__create("c",QApplication.translate("Mem","Call")))
        self.append(ProductMode(self.mem).init__create("i",QApplication.translate("Mem","Inline")))

class SimulationManager(ObjectManager_With_IdName_Selectable):
    def __init__(self, mem):
        ObjectManager_With_IdName_Selectable.__init__(self)
        self.mem=mem
            
    def delete(self, simulation):
        """Deletes from db and removes object from array.
        simulation is an object"""
        simulation.delete()
        self.remove(simulation)

    def load_from_db(self, sql,  original_db):
        cur=self.mem.con.cursor()
        cur.execute(sql)
        for row in cur:
            s=Simulation(self.mem, original_db).init__db_row(row)
            self.append(s)
        cur.close()  
        
    def myqtablewidget(self, wdg):
        wdg.table.setColumnCount(5)
        wdg.table.setHorizontalHeaderItem(0, QTableWidgetItem(QApplication.translate("Mem", "Creation" )))
        wdg.table.setHorizontalHeaderItem(1, QTableWidgetItem(QApplication.translate("Mem", "Type" )))
        wdg.table.setHorizontalHeaderItem(2, QTableWidgetItem(QApplication.translate("Mem", "Database" )))
        wdg.table.setHorizontalHeaderItem(3, QTableWidgetItem(QApplication.translate("Mem", "Starting" )))
        wdg.table.setHorizontalHeaderItem(4, QTableWidgetItem(QApplication.translate("Mem", "Ending" )))
        wdg.table.clearContents()
        wdg.applySettings()
        wdg.table.setRowCount(self.length())
        for i, a in enumerate(self.arr):
            wdg.table.setItem(i, 0, qdatetime(a.creation, self.mem.localzone_name))
            wdg.table.setItem(i, 1, qleft(a.type.name))
            wdg.table.item(i, 1).setIcon(a.type.qicon())
            wdg.table.setItem(i, 2, qleft(a.simulated_db()))
            wdg.table.setItem(i, 3, qdatetime(a.starting, self.mem.localzone_name))
            wdg.table.setItem(i, 4, qdatetime(a.ending, self.mem.localzone_name))



class ConceptManager(ObjectManager_With_IdName_Selectable):
    def __init__(self, mem):
        ObjectManager_With_IdName_Selectable.__init__(self)
        self.mem=mem 
                 
        
    def load_from_db(self):
        cur=self.mem.con.cursor()
        cur.execute("Select * from conceptos")
        for row in cur:
            self.append(Concept(self.mem, row, self.mem.tiposoperaciones.find_by_id(row['id_tiposoperaciones'])))
        cur.close()
        self.order_by_name()
                        
    def load_opercuentas_qcombobox(self, combo):
        """Carga conceptos operaciones 1,2,3, menos dividends y renta fija, no pueden ser editados, luego no se necesitan"""
        for c in self.arr:
            if c.tipooperacion.id in (1, 2, 3, 11):
                if c.id not in (39, 50, 62, 63, 65, 66):
                    combo.addItem("{0} -- {1}".format(  c.name,  c.tipooperacion.name),  c.id  )

    def load_dividend_qcombobox(self, combo,  select=None):
        """Select es un class Concept"""
        for n in (39, 50,  62):
            c=self.find_by_id(n)
            combo.addItem("{0} -- {1}".format(  c.name,  c.tipooperacion.name),  c.id   )
        if select!=None:
            combo.setCurrentIndex(combo.findData(select.id))

    def load_bonds_qcombobox(self, combo,  select=None):
        """Carga conceptos operaciones 1,2,3"""
        for n in (50, 63, 65, 66):
            c=self.find_by_id(n)
            combo.addItem("{0} -- {1}".format(  c.name,  c.tipooperacion.name),  c.id )
        if select!=None:
            combo.setCurrentIndex(combo.findData(select.id))

    def load_futures_qcombobox(self, combo,  select=None):
        for n in (eConcept.RolloverPaid, eConcept.RolloverReceived):
            c=self.find_by_id(n)
            combo.addItem("{0} -- {1}".format(  c.name,  c.tipooperacion.name),  c.id )
        if select!=None:
            combo.setCurrentIndex(combo.findData(select.id))

    def considered_dividends_in_totals(self):
        """El 63 es pago de cupon corrido y no es considerado dividend  a efectos de totales, sino gasto."""
        return[39, 50, 62, 65, 66]


    def clone_x_tipooperacion(self, id_tiposoperaciones):
        """SSe usa clone y no init ya que ya están cargados en MEM"""
        resultado=ConceptManager(self.mem)
        for c in self.arr:
            if c.tipooperacion.id==id_tiposoperaciones:
                resultado.append(c)
        return resultado
        
    def clone_editables(self):
        """SSe usa clone y no init ya que ya están cargados en MEM"""
        resultado=ConceptManager(self.mem)
        for c in self.arr:
            if c.editable==True:
                resultado.append(c)
        return resultado
        
    def percentage_monthly(self, year, month):
        """ Generates an arr with:
        1) Concept:
        2) Monthly expense
        3) Percentage expenses of all conceptos this month
        4) Monthly average from first operation
        
        Returns three fields:
        1) dictionary arr, whith above values, sort by concepto.name
        2) total expenses of all concepts
        3) total average expenses of all conceptos
        """
        ##Fills column 0 and 1, 3 and gets totalexpenses
        arr=[]
        totalexpenses=Decimal(0)
        totalmedia_mensual=Decimal(0)
        for v in self.arr:
            thismonth=v.mensual(year, month)
            if thismonth==Decimal(0):
                continue
            totalexpenses=totalexpenses+thismonth
            media_mensual=v.media_mensual()
            totalmedia_mensual=totalmedia_mensual+media_mensual
            arr.append([v, thismonth, None,  media_mensual])
        
        ##Fills column 2 and calculates percentage
        for  v in arr:
            if totalexpenses==Decimal(0):
                v[2]=Decimal(0)
            else:
                v[2]=Decimal(100)*v[1]/totalexpenses
        
        arr=sorted(arr, key=lambda o:o[1])
        return (arr, totalexpenses,  totalmedia_mensual)



class CountryManager(ObjectManager_With_IdName_Selectable):
    def __init__(self, mem):
        ObjectManager_With_IdName_Selectable.__init__(self)
        self.mem=mem   
        
    def load_all(self):
        self.append(Country("es",QApplication.translate("Mem","Spain")))
        self.append(Country("be",QApplication.translate("Mem","Belgium")))
        self.append(Country("cn",QApplication.translate("Mem","China")))
        self.append(Country("de",QApplication.translate("Mem","Germany")))
        self.append(Country("earth",QApplication.translate("Mem","Earth")))
        self.append(Country("en",QApplication.translate("Mem","United Kingdom")))
        self.append(Country("eu",QApplication.translate("Mem","Europe")))
        self.append(Country("fi",QApplication.translate("Mem","Finland")))
        self.append(Country("fr",QApplication.translate("Mem","France")))
        self.append(Country("ie",QApplication.translate("Mem","Ireland")))
        self.append(Country("it",QApplication.translate("Mem","Italy")))
        self.append(Country("jp",QApplication.translate("Mem","Japan")))
        self.append(Country("nl",QApplication.translate("Mem","Netherlands")))
        self.append(Country("pt",QApplication.translate("Mem","Portugal")))
        self.append(Country("us",QApplication.translate("Mem","United States of America")))
        self.append(Country("ro",QApplication.translate("Mem","Romanian")))
        self.append(Country("ru",QApplication.translate("Mem","Rusia")))
        self.append(Country("lu",QApplication.translate("Mem","Luxembourg")))
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



class CurrencyManager(ObjectManager_With_IdName_Selectable):
    def __init__(self, mem):
        ObjectManager_With_IdName_Selectable.__init__(self)
        self.mem=mem   
    
    def load_all(self):
        self.append(Currency().init__create(QApplication.translate("Mem","Chinese Yoan"), "¥", 'CNY'))
        self.append(Currency().init__create(QApplication.translate("Mem","Euro"), "€", "EUR"))
        self.append(Currency().init__create(QApplication.translate("Mem","Pound"),"£", 'GBP'))
        self.append(Currency().init__create(QApplication.translate("Mem","Japones Yen"), '¥', "JPY"))
        self.append(Currency().init__create(QApplication.translate("Mem","American Dolar"), '$', 'USD'))
        self.append(Currency().init__create(QApplication.translate("Mem","Units"), 'u', 'u'))

    def find_by_symbol(self, symbol,  log=False):
        """Finds by id"""
        for c in self.arr:
            if c.symbol==symbol:
                return c
        error("CurrencyManager fails finding {}".format(symbol))
        return None

    def qcombobox(self, combo, selectedcurrency=None):
        """Función que carga en un combo pasado como parámetro las currencies"""
        for c in self.arr:
            combo.addItem("{0} - {1} ({2})".format(c.id, c.name, c.symbol), c.id)
        if selectedcurrency!=None:
                combo.setCurrentIndex(combo.findData(selectedcurrency.id))

class DividendHeterogeneusManager(ObjectManager_With_IdDatetime_Selectable, QObject):
    """Class that  groups dividends from a Xulpymoney Product"""
    def __init__(self, mem):
        ObjectManager_With_IdDatetime_Selectable.__init__(self)
        QObject.__init__(self)
        self.mem=mem
            
    ## Net amount in self.mem.localcurrency
    def net(self):
        r=Money(self.mem, 0, self.mem.localcurrency)
        for d in self.arr:
            r=r+d.net(eMoneyCurrency.User)
        return r

    ## Gross amount in self.mem.localcurrency
    def gross(self):
        r=Money(self.mem, 0, self.mem.localcurrency)
        for d in self.arr:
            r=r+d.gross(eMoneyCurrency.User)
        return r

    def load_from_db(self, sql):    
        del self.arr
        self.arr=[]
        cur=self.mem.con.cursor()
        cur.execute( sql)#"select * from dividends where id_inversiones=%s order by fecha", (self.investment.id, )
        for row in cur:
            inversion=self.mem.data.investments.find_by_id(row['id_inversiones'])
            oc=AccountOperation(self.mem, row['id_opercuentas'])
            self.arr.append(Dividend(self.mem).init__db_row(row, inversion, oc, self.mem.conceptos.find_by_id(row['id_conceptos']) ))
        cur.close()      
                
    def myqtablewidget(self, wdg,   show_investment=False):
        """Section es donde guardar en el config file, coincide con el nombre del formulario en el que está la table
        Devuelve sumatorios"""
        diff=0
        if show_investment==True:
            diff=1
        wdg.table.setColumnCount(7+diff)
        wdg.table.setHorizontalHeaderItem(0, QTableWidgetItem(QApplication.translate("Mem", "Date" )))
        wdg.table.setHorizontalHeaderItem(diff, QTableWidgetItem(QApplication.translate("Mem", "Product" )))
        wdg.table.setHorizontalHeaderItem(diff+1, QTableWidgetItem(QApplication.translate("Mem", "Concept" )))
        wdg.table.setHorizontalHeaderItem(diff+2, QTableWidgetItem(QApplication.translate("Mem", "Gross" )))
        wdg.table.setHorizontalHeaderItem(diff+3, QTableWidgetItem(QApplication.translate("Mem", "Withholding" )))
        wdg.table.setHorizontalHeaderItem(diff+4, QTableWidgetItem(QApplication.translate("Mem", "Comission" )))
        wdg.table.setHorizontalHeaderItem(diff+5, QTableWidgetItem(QApplication.translate("Mem", "Net" )))
        wdg.table.setHorizontalHeaderItem(diff+6, QTableWidgetItem(QApplication.translate("Mem", "DPS" )))
        #DATA  
        wdg.applySettings()
        wdg.table.clearContents()


        wdg.table.setRowCount(len(self.arr)+1)
        sumneto=0
        sumbruto=0
        sumretencion=0
        sumcomision=0
        for i, d in enumerate(self.arr):
            sumneto=sumneto+d.neto
            sumbruto=sumbruto+d.bruto
            sumretencion=sumretencion+d.retencion
            sumcomision=sumcomision+d.comision
            wdg.table.setItem(i, 0, qdatetime(d.datetime, self.mem.localzone_name))
            if show_investment==True:
                wdg.table.setItem(i, diff, qleft(d.investment.name))
            wdg.table.setItem(i, diff+1, qleft(d.opercuenta.concepto.name))
            wdg.table.setItem(i, diff+2, self.mem.localcurrency.qtablewidgetitem(d.bruto))
            wdg.table.setItem(i, diff+3, self.mem.localcurrency.qtablewidgetitem(d.retencion))
            wdg.table.setItem(i, diff+4, self.mem.localcurrency.qtablewidgetitem(d.comision))
            wdg.table.setItem(i, diff+5, self.mem.localcurrency.qtablewidgetitem(d.neto))
            wdg.table.setItem(i, diff+6, self.mem.localcurrency.qtablewidgetitem(d.dpa))
        wdg.table.setItem(len(self.arr), diff+1, qleft(QApplication.translate("Mem","TOTAL")))
        wdg.table.setItem(len(self.arr), diff+2, self.mem.localcurrency.qtablewidgetitem(sumbruto))
        wdg.table.setItem(len(self.arr), diff+3, self.mem.localcurrency.qtablewidgetitem(sumretencion))
        wdg.table.setItem(len(self.arr), diff+4, self.mem.localcurrency.qtablewidgetitem(sumcomision))
        wdg.table.setItem(len(self.arr), diff+5, self.mem.localcurrency.qtablewidgetitem(sumneto))
        return (sumneto, sumbruto, sumretencion, sumcomision)

class DividendHomogeneusManager(DividendHeterogeneusManager):
    def __init__(self, mem, investment):
        DividendHeterogeneusManager.__init__(self, mem)
        self.investment=investment
        
    ## @param emoneycurrency eMoneyCurrency type
    ## @param current If true only shows dividends from first current operation. If false show all dividends
    def gross(self, emoneycurrency, current):
        r=Money(self.mem, 0, self.investment.resultsCurrency(emoneycurrency))
        for d in self.arr:
            if current==True and self.investment.op_actual.length()>0  and d.datetime<self.investment.op_actual.first().datetime:
                continue
            else:
                r=r+d.gross(emoneycurrency)
        return r

    ## @param emoneycurrency eMoneyCurrency type
    ## @param current If true only shows dividends from first current operation. If false show all dividends
    def net(self, emoneycurrency, current):
        r=Money(self.mem, 0, self.investment.resultsCurrency(emoneycurrency))
        for d in self.arr:
            if current==True and self.investment.op_actual.length()>0 and d.datetime<self.investment.op_actual.first().datetime:
                continue
            else:
                r=r+d.net(emoneycurrency)
        return r

    ## @param emoneycurrency eMoneyCurrency type
    ## @param current If true only shows dividends from first current operation. If false show all dividends
    def percentage_from_invested(self, emoneycurrency, current):
        return Percentage(self.gross(emoneycurrency, current), self.investment.invertido(None, emoneycurrency))

    ## @param emoneycurrency eMoneyCurrency type
    ## @param current If true only shows dividends from first current operation. If false show all dividends
    def percentage_tae_from_invested(self, emoneycurrency, current):
        try:
            dias=(date.today()-self.investment.op_actual.first().datetime.date()).days+1
            return Percentage(self.percentage_from_invested(emoneycurrency, current)*365, dias )
        except:#No first
            return Percentage()
        
    ## Method that fills a qtablewidget with dividend data
    ## @param table QTableWidget
    ## @param emoneycurrency eMoneyCurrency type
    ## @param current If true only shows dividends from first current operation. If false show all dividends
    def myqtablewidget(self, wdg, emoneycurrency, current=True):
        wdg.table.setColumnCount(7)
        wdg.table.setHorizontalHeaderItem(0, QTableWidgetItem(self.tr("Date" )))
        wdg.table.setHorizontalHeaderItem(1, QTableWidgetItem(self.tr("Concept" )))
        wdg.table.setHorizontalHeaderItem(2, QTableWidgetItem(self.tr("Gross" )))
        wdg.table.setHorizontalHeaderItem(3, QTableWidgetItem(self.tr("Withholding" )))
        wdg.table.setHorizontalHeaderItem(4, QTableWidgetItem(self.tr("Comission" )))
        wdg.table.setHorizontalHeaderItem(5, QTableWidgetItem(self.tr("Net" )))
        wdg.table.setHorizontalHeaderItem(6, QTableWidgetItem(self.tr("DPS" )))
        #DATA  
        wdg.applySettings()
        wdg.table.clearContents()

        currency=self.investment.resultsCurrency(emoneycurrency)

        wdg.table.setRowCount(self.length()+1)
        sumneto=Money(self.mem, 0, currency)
        sumbruto=Money(self.mem, 0, currency)
        sumretencion=Money(self.mem, 0, currency)
        sumcomision=Money(self.mem, 0, currency)
        for i, d in enumerate(self.arr):
            if current==True and self.investment.op_actual.length()>0 and d.datetime<self.investment.op_actual.first().datetime:
                wdg.table.hideRow(i)
                continue
            else:
                wdg.table.showRow(i)
            sumneto=sumneto+d.net(emoneycurrency)
            sumbruto=sumbruto+d.gross(emoneycurrency)
            sumretencion=sumretencion+d.retention(emoneycurrency)
            sumcomision=sumcomision+d.commission(emoneycurrency)
            wdg.table.setItem(i, 0, qdatetime(d.datetime, self.mem.localzone_name))
            wdg.table.setItem(i, 1, qleft(d.opercuenta.concepto.name))
            wdg.table.setItem(i, 2, d.gross(emoneycurrency).qtablewidgetitem())
            wdg.table.setItem(i, 3, d.retention(emoneycurrency).qtablewidgetitem())
            wdg.table.setItem(i, 4, d.commission(emoneycurrency).qtablewidgetitem())
            wdg.table.setItem(i, 5, d.net(emoneycurrency).qtablewidgetitem())
            wdg.table.setItem(i, 6, d.dps(emoneycurrency).qtablewidgetitem())
        wdg.table.setItem(self.length(), 1, qleft(self.tr("TOTAL")))
        wdg.table.setItem(self.length(), 2, sumbruto.qtablewidgetitem())
        wdg.table.setItem(self.length(), 3, sumretencion.qtablewidgetitem())
        wdg.table.setItem(self.length(), 4, sumcomision.qtablewidgetitem())
        wdg.table.setItem(self.length(), 5, sumneto.qtablewidgetitem())
        return (sumneto, sumbruto, sumretencion, sumcomision)
        
        
class BankManager(ObjectManager_With_IdName_Selectable):
    def __init__(self, mem):
        ObjectManager_With_IdName_Selectable.__init__(self)
        self.mem=mem   

    def load_from_db(self, sql):
        cur=self.mem.con.cursor()
        cur.execute(sql)#"select * from entidadesbancarias"
        for row in cur:
            self.append(Bank(self.mem).init__db_row(row))
        cur.close()            
        
    def delete(self, bank):
        """Deletes from db and removes object from array.
        bank is an object"""
        bank.delete()
        self.remove(bank)


class InvestmentOperationHeterogeneusManager(ObjectManager_With_IdDatetime_Selectable):       
    """Clase es un array ordenado de objetos newInvestmentOperation"""
    def __init__(self, mem):
        ObjectManager_With_IdDatetime_Selectable.__init__(self)
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
        wdg.table.setHorizontalHeaderItem(0, QTableWidgetItem(QApplication.translate("Mem", "Date" )))
        wdg.table.setHorizontalHeaderItem(1, QTableWidgetItem(QApplication.translate("Mem", "Product" )))
        wdg.table.setHorizontalHeaderItem(2, QTableWidgetItem(QApplication.translate("Mem", "Account" )))
        wdg.table.setHorizontalHeaderItem(3, QTableWidgetItem(QApplication.translate("Mem", "Operation type" )))
        wdg.table.setHorizontalHeaderItem(4, QTableWidgetItem(QApplication.translate("Mem", "Shares" )))
        wdg.table.setHorizontalHeaderItem(5, QTableWidgetItem(QApplication.translate("Mem", "Price" )))
        wdg.table.setHorizontalHeaderItem(6, QTableWidgetItem(QApplication.translate("Mem", "Amount" )))
        wdg.table.setHorizontalHeaderItem(7, QTableWidgetItem(QApplication.translate("Mem", "Comission" )))
        wdg.table.setHorizontalHeaderItem(8, QTableWidgetItem(QApplication.translate("Mem", "Taxes" )))
        wdg.table.setHorizontalHeaderItem(9, QTableWidgetItem(QApplication.translate("Mem", "Total" )))
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

    def myqtablewidget(self, wdg, type=1):
        """Section es donde guardar en el config file, coincide con el nombre del formulario en el que está la tabla
        show_accounts, muestra el producto y la cuenta
        type muestra los money en la currency de la cuenta
        """
        
        self.order_by_datetime()
        if self.investment.hasSameAccountCurrency()==True:
            wdg.table.setColumnCount(8)
        else:
            wdg.table.setColumnCount(9)
        wdg.table.setHorizontalHeaderItem(0, QTableWidgetItem(QApplication.translate("Mem", "Date" )))
        wdg.table.setHorizontalHeaderItem(1, QTableWidgetItem(QApplication.translate("Mem", "Operation type" )))
        wdg.table.setHorizontalHeaderItem(2, QTableWidgetItem(QApplication.translate("Mem", "Shares" )))
        wdg.table.setHorizontalHeaderItem(3, QTableWidgetItem(QApplication.translate("Mem", "Price" )))
        wdg.table.setHorizontalHeaderItem(4, QTableWidgetItem(QApplication.translate("Mem", "Gross" )))
        wdg.table.setHorizontalHeaderItem(5, QTableWidgetItem(QApplication.translate("Mem", "Comission" )))
        wdg.table.setHorizontalHeaderItem(6, QTableWidgetItem(QApplication.translate("Mem", "Taxes" )))
        wdg.table.setHorizontalHeaderItem(7, QTableWidgetItem(QApplication.translate("Mem", "Total" )))
        if self.investment.hasSameAccountCurrency()==False:
            wdg.table.setHorizontalHeaderItem(8, QTableWidgetItem(QApplication.translate("Mem", "Currency conversion" )))
        
        #DATA 
        wdg.applySettings()
        wdg.table.clearContents()  
        wdg.table.setRowCount(len(self.arr))
        
        for rownumber, a in enumerate(self.arr):
            wdg.table.setItem(rownumber, 0, qdatetime(a.datetime, self.mem.localzone_name))
            if self.mem.gainsyear==True and a.less_than_a_year()==True:
                wdg.table.item(rownumber, 0).setIcon(QIcon(":/xulpymoney/new.png"))
                
            wdg.table.setItem(rownumber, 1, QTableWidgetItem(a.tipooperacion.name))
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

class InvestmentOperationCurrentHeterogeneusManager(ObjectManager_With_IdDatetime_Selectable):    
    """Clase es un array ordenado de objetos newInvestmentOperation"""
    def __init__(self, mem):
        ObjectManager_With_IdDatetime_Selectable.__init__(self)
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
        wdg.table.setColumnCount(12)
        wdg.table.setHorizontalHeaderItem(0, QTableWidgetItem(QApplication.translate("Mem", "Date" )))
        wdg.table.setHorizontalHeaderItem(1, QTableWidgetItem(QApplication.translate("Mem", "Product" )))
        wdg.table.setHorizontalHeaderItem(2, QTableWidgetItem(QApplication.translate("Mem", "Account" )))
        wdg.table.setHorizontalHeaderItem(3, QTableWidgetItem(QApplication.translate("Mem", "Shares" )))
        wdg.table.setHorizontalHeaderItem(4, QTableWidgetItem(QApplication.translate("Mem", "Price" )))
        wdg.table.setHorizontalHeaderItem(5, QTableWidgetItem(QApplication.translate("Mem", "Invested" )))
        wdg.table.setHorizontalHeaderItem(6, QTableWidgetItem(QApplication.translate("Mem", "Current balance" )))
        wdg.table.setHorizontalHeaderItem(7, QTableWidgetItem(QApplication.translate("Mem", "Pending" )))
        wdg.table.setHorizontalHeaderItem(8, QTableWidgetItem(QApplication.translate("Mem", "% annual" )))
        wdg.table.setHorizontalHeaderItem(9, QTableWidgetItem(QApplication.translate("Mem", "% APR" )))
        wdg.table.setHorizontalHeaderItem(10, QTableWidgetItem(QApplication.translate("Mem", "% Total" )))
        wdg.table.setHorizontalHeaderItem(11, QTableWidgetItem(QApplication.translate("Mem", "Benchmark" )))
        #DATA
        if self.length()==0:
            wdg.table.setRowCount(0)
            return
        type=3
            
        wdg.applySettings()
        wdg.table.clearContents()
        wdg.table.setRowCount(self.length()+1)
        for rownumber, a in enumerate(self.arr):        
            wdg.table.setItem(rownumber, 0, qdatetime(a.datetime, self.mem.localzone_name))
            if self.mem.gainsyear==True and a.less_than_a_year()==True:
                wdg.table.item(rownumber, 0).setIcon(QIcon(":/xulpymoney/new.png"))
            wdg.table.setItem(rownumber, 1, qleft(a.investment.name))
            wdg.table.setItem(rownumber, 2, qleft(a.investment.account.name))
            wdg.table.setItem(rownumber, 3, qright("{0:.6f}".format(a.shares)))
            wdg.table.setItem(rownumber, 4, a.price().local().qtablewidgetitem())
            wdg.table.setItem(rownumber, 5, a.invertido(type).qtablewidgetitem())
            wdg.table.setItem(rownumber, 6, a.balance(a.investment.product.result.basic.last, type).qtablewidgetitem())
            wdg.table.setItem(rownumber, 7, a.pendiente(a.investment.product.result.basic.last, type).qtablewidgetitem())
            wdg.table.setItem(rownumber, 8, a.tpc_anual().qtablewidgetitem())
            wdg.table.setItem(rownumber, 9, a.tpc_tae(a.investment.product.result.basic.last, type=2).qtablewidgetitem())
            wdg.table.setItem(rownumber, 10, a.tpc_total(a.investment.product.result.basic.last, type=2).qtablewidgetitem())
            if a.referenciaindice==None:
                wdg.table.setItem(rownumber, 11, self.mem.data.benchmark.currency.qtablewidgetitem(None))
            else:
                wdg.table.setItem(rownumber, 11, self.mem.data.benchmark.currency.qtablewidgetitem(a.referenciaindice.quote))

        wdg.table.setItem(self.length(), 0, qleft(days2string(self.average_age())))
        wdg.table.setItem(self.length(), 0, QTableWidgetItem(("TOTAL")))
        wdg.table.setItem(self.length(), 5, self.invertido().qtablewidgetitem())
        wdg.table.setItem(self.length(), 6, self.balance().qtablewidgetitem())
        wdg.table.setItem(self.length(), 7, self.pendiente().qtablewidgetitem())
        wdg.table.setItem(self.length(), 8, self.tpc_tae().qtablewidgetitem())
        wdg.table.setItem(self.length(), 9, self.tpc_total().qtablewidgetitem())


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
        self.investment=investment
    
    def average_age(self, type=1):
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

    def average_price(self, type=1):
        """Calcula el precio medio de compra"""
        
        shares=self.shares()
        currency=self.investment.resultsCurrency(type)
        sharesxprice=Decimal(0)
        for o in self.arr:
            sharesxprice=sharesxprice+o.shares*o.price(type).amount
        return Money(self.mem, 0, currency) if shares==Decimal(0) else Money(self.mem, sharesxprice/shares,  currency)
        
        
    def average_price_after_a_gains_percentage(self, percentage,  type=1):
        """
            percentage is a Percentage object
            Returns a Money object after add a percentage to the average_price
        """
        return self.average_price(type)*(1+percentage.value)
        
    def invertido(self, type=1):
        """Al ser homegeneo da el resultado en Money del producto"""
        currency=self.investment.resultsCurrency(type)
        resultado=Money(self.mem, 0, currency)
        for o in self.arr:
            resultado=resultado+o.invertido(type)
        return resultado
        
    def balance(self, quote, type=1):
        """Al ser homegeneo da el resultado en Money del producto"""
        currency=self.investment.resultsCurrency(type)
        resultado=Money(self.mem, 0, currency)
        for o in self.arr:
            resultado=resultado+o.balance(quote, type)
        return resultado        

    def penultimate(self, type=1):
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
    def gains_last_day(self, type=1):
        return self.balance(self.investment.product.result.basic.last, type)-self.penultimate(type)

    def gains_in_selling_point(self, type=1):
        """Gains in investment defined selling point"""
        if self.investment.venta!=None:
            return self.investment.selling_price(type)*self.investment.shares()-self.investment.invertido(None, type)
        return Money(self.mem,  0, self.investment.resultsCurrency(type) )
        

    def gains_from_percentage(self, percentage,  type=1):
        """
            Gains a percentage from average_price
            percentage is a Percentage object
        """        
        return self.average_price(type)*percentage.value*self.shares()

    def pendiente(self, lastquote, type=1):
        currency=self.investment.resultsCurrency(type)
        resultado=Money(self.mem, 0, currency)
        for o in self.arr:
            resultado=resultado+o.pendiente(lastquote, type)
        return resultado
        
    def pendiente_positivo(self, lastquote, type=1):
        currency=self.investment.resultsCurrency(type)
        resultado=Money(self.mem, 0, currency)
        for o in self.arr:
            pendiente=o.pendiente(lastquote, type)
            if pendiente.isGETZero():
                resultado=resultado+pendiente
        return resultado
        
    def pendiente_negativo(self, lastquote, type=1):
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

    def tpc_tae(self, last,  type=1):
        dias=self.average_age()
        if dias==0:
            dias=1
        return Percentage(self.tpc_total(last, type)*365, dias)

    def tpc_total(self, last, type=1):
        """
            last is a Money object with investment.product currency
            type puede ser:
                1 Da el tanto por  ciento en la currency de la inversi´on
                2 Da el tanto por  ciento en la currency de la cuenta, por lo que se debe convertir teniendo en cuenta la temporalidad
                3 Da el tanto por ciento en la currency local, partiendo  de la conversi´on a la currency de la cuenta
        """
        return Percentage(self.pendiente(last, type), self.invertido(type))
    
    def myqtablewidget(self,  wdg,  quote=None, type=1):
        """Función que rellena una tabla pasada como parámetro con datos procedentes de un array de objetos
        InvestmentOperationCurrent y dos valores de mystocks para rellenar los tpc correspodientes
        
        Se dibujan las columnas pero las propiedad alternate color... deben ser en designer
        
        Parámetros
            - tabla myQTableWidget en la que rellenar los datos
            - quote, si queremos cargar las operinversiones con un valor determinado se pasará la quote correspondiente. Es un Objeto quote
            - type. Si es Falsa muestra la moneda de la inversión si es verdadera con la currency de la cuentaº
        """
            
        wdg.table.setColumnCount(10)
        wdg.table.setHorizontalHeaderItem(0, QTableWidgetItem(QApplication.translate("Mem", "Date" )))
        wdg.table.setHorizontalHeaderItem(1, QTableWidgetItem(QApplication.translate("Mem", "Shares" )))
        wdg.table.setHorizontalHeaderItem(2, QTableWidgetItem(QApplication.translate("Mem", "Price" )))
        wdg.table.setHorizontalHeaderItem(3, QTableWidgetItem(QApplication.translate("Mem", "Invested" )))
        wdg.table.setHorizontalHeaderItem(4, QTableWidgetItem(QApplication.translate("Mem", "Current balance" )))
        wdg.table.setHorizontalHeaderItem(5, QTableWidgetItem(QApplication.translate("Mem", "Pending" )))
        wdg.table.setHorizontalHeaderItem(6, QTableWidgetItem(QApplication.translate("Mem", "% annual" )))
        wdg.table.setHorizontalHeaderItem(7, QTableWidgetItem(QApplication.translate("Mem", "% APR" )))
        wdg.table.setHorizontalHeaderItem(8, QTableWidgetItem(QApplication.translate("Mem", "% Total" )))
        wdg.table.setHorizontalHeaderItem(9, QTableWidgetItem(QApplication.translate("Mem", "Benchmark" )))
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
                wdg.table.setItem(rownumber, 9, self.mem.data.benchmark.currency.qtablewidgetitem(None))
            else:
                wdg.table.setItem(rownumber, 9, self.mem.data.benchmark.currency.qtablewidgetitem(a.referenciaindice.quote))
                
        wdg.table.setItem(self.length(), 0, QTableWidgetItem(("TOTAL")))
        wdg.table.setItem(self.length(), 1, qright(self.shares()))
        wdg.table.setItem(self.length(), 2, self.average_price(type).qtablewidgetitem())
        wdg.table.setItem(self.length(), 3, self.invertido(type).qtablewidgetitem())
        wdg.table.setItem(self.length(), 4, self.balance(quote, type).qtablewidgetitem())
        wdg.table.setItem(self.length(), 5, self.pendiente(quote, type).qtablewidgetitem())
        wdg.table.setItem(self.length(), 7, self.tpc_tae(quote, type).qtablewidgetitem())
        wdg.table.setItem(self.length(), 8, self.tpc_total(quote, type).qtablewidgetitem())

class InvestmentOperationHistoricalHeterogeneusManager(ObjectManager_With_Id_Selectable):
    def __init__(self, mem):
        ObjectManager_With_Id_Selectable.__init__(self)
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
        wdg.table.setHorizontalHeaderItem(0, QTableWidgetItem(QApplication.translate("Mem", "Date" )))
        wdg.table.setHorizontalHeaderItem(1, QTableWidgetItem(QApplication.translate("Mem", "Years" )))
        wdg.table.setHorizontalHeaderItem(2, QTableWidgetItem(QApplication.translate("Mem", "Product" )))
        wdg.table.setHorizontalHeaderItem(3, QTableWidgetItem(QApplication.translate("Mem", "Account" )))
        wdg.table.setHorizontalHeaderItem(4, QTableWidgetItem(QApplication.translate("Mem", "Operation type" )))
        wdg.table.setHorizontalHeaderItem(5, QTableWidgetItem(QApplication.translate("Mem", "Shares" )))
        wdg.table.setHorizontalHeaderItem(6, QTableWidgetItem(QApplication.translate("Mem", "Initial balance" )))
        wdg.table.setHorizontalHeaderItem(7, QTableWidgetItem(QApplication.translate("Mem", "Final balance" )))
        wdg.table.setHorizontalHeaderItem(8, QTableWidgetItem(QApplication.translate("Mem", "Gross gains" )))
        wdg.table.setHorizontalHeaderItem(9, QTableWidgetItem(QApplication.translate("Mem", "Commissions" )))
        wdg.table.setHorizontalHeaderItem(10, QTableWidgetItem(QApplication.translate("Mem", "Taxes" )))
        wdg.table.setHorizontalHeaderItem(11, QTableWidgetItem(QApplication.translate("Mem", "Net gains" )))
        wdg.table.setHorizontalHeaderItem(12, QTableWidgetItem(QApplication.translate("Mem", "% Net APR" )))
        wdg.table.setHorizontalHeaderItem(13, QTableWidgetItem(QApplication.translate("Mem", "% Net Total" )))

        wdg.applySettings()
        wdg.table.clearContents()
        wdg.table.setRowCount(self.length()+1)
        for rownumber, a in enumerate(self.arr):    
            wdg.table.setItem(rownumber, 0,QTableWidgetItem(str(a.fecha_venta)))    
            wdg.table.setItem(rownumber, 1,QTableWidgetItem(str(round(a.years(), 2))))    
            wdg.table.setItem(rownumber, 2,QTableWidgetItem(a.investment.name))
            wdg.table.setItem(rownumber, 3,QTableWidgetItem(a.investment.account.name))
            wdg.table.setItem(rownumber, 4,QTableWidgetItem(a.tipooperacion.name))
            wdg.table.setItem(rownumber, 5,qright(a.shares))
            wdg.table.setItem(rownumber, 6,a.bruto_compra(eMoneyCurrency.User).qtablewidgetitem())
            wdg.table.setItem(rownumber, 7,a.bruto_venta(eMoneyCurrency.User).qtablewidgetitem())
            wdg.table.setItem(rownumber, 8,a.consolidado_bruto(eMoneyCurrency.User).qtablewidgetitem())
            wdg.table.setItem(rownumber, 9,a.commission(eMoneyCurrency.User).qtablewidgetitem())
            wdg.table.setItem(rownumber, 10,a.taxes(eMoneyCurrency.User).qtablewidgetitem())
            wdg.table.setItem(rownumber, 11,a.consolidado_neto(eMoneyCurrency.User).qtablewidgetitem())
            wdg.table.setItem(rownumber, 12,a.tpc_tae_neto().qtablewidgetitem())
            wdg.table.setItem(rownumber, 13,a.tpc_total_neto().qtablewidgetitem())

        wdg.table.setItem(self.length(), 2,QTableWidgetItem("TOTAL"))
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
        wdg.table.setHorizontalHeaderItem(0, QTableWidgetItem(QApplication.translate("Mem", "Date" )))
        wdg.table.setHorizontalHeaderItem(1, QTableWidgetItem(QApplication.translate("Mem", "Years" )))
        if show_accounts==True:
            wdg.table.setHorizontalHeaderItem(2, QTableWidgetItem(QApplication.translate("Mem", "Product" )))
            wdg.table.setHorizontalHeaderItem(3, QTableWidgetItem(QApplication.translate("Mem", "Account" )))
        wdg.table.setHorizontalHeaderItem(2+diff, QTableWidgetItem(QApplication.translate("Mem", "Operation type" )))
        wdg.table.setHorizontalHeaderItem(3+diff, QTableWidgetItem(QApplication.translate("Mem", "Shares" )))
        wdg.table.setHorizontalHeaderItem(4+diff, QTableWidgetItem(QApplication.translate("Mem", "Initial gross" )))
        wdg.table.setHorizontalHeaderItem(5+diff, QTableWidgetItem(QApplication.translate("Mem", "Final gross" )))
        wdg.table.setHorizontalHeaderItem(6+diff, QTableWidgetItem(QApplication.translate("Mem", "Gross gains" )))
        wdg.table.setHorizontalHeaderItem(7+diff, QTableWidgetItem(QApplication.translate("Mem", "Commissions" )))
        wdg.table.setHorizontalHeaderItem(8+diff, QTableWidgetItem(QApplication.translate("Mem", "Taxes" )))
        wdg.table.setHorizontalHeaderItem(9+diff, QTableWidgetItem(QApplication.translate("Mem", "Net gains" )))
        wdg.table.setHorizontalHeaderItem(10+diff, QTableWidgetItem(QApplication.translate("Mem", "% Net APR" )))
        wdg.table.setHorizontalHeaderItem(11+diff, QTableWidgetItem(QApplication.translate("Mem", "% Net Total" )))

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
    
    def price(self, type=1):
        if type==1:
            return Money(self.mem, self.valor_accion, self.investment.product.currency)
        elif type==2:
            return Money(self.mem, self.valor_accion, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion)
        elif type==3:
            return Money(self.mem, self.valor_accion, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion).local(self.datetime)
            
            
    def revaluation_monthly(self, year, month, type=1):
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
            
            
    def revaluation_annual(self, year, type=1):
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
            
            
    def gross(self, type=1):
        if type==1:
            return Money(self.mem, self.shares*self.valor_accion, self.investment.product.currency)
        elif type==2:
            return Money(self.mem, self.shares*self.valor_accion, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion)
            
    def net(self, type=1):
        if self.shares>=Decimal(0):
            return self.gross(type)+self.commission(type)+self.taxes(type)
        elif type==2:
            return self.gross(type)-self.commission(type)-self.taxes(type)
            
    def taxes(self, type=1):
        if type==1:
            return Money(self.mem, self.impuestos, self.investment.product.currency)
        elif type==2:
            return Money(self.mem, self.impuestos, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion)
            
    def commission(self, type=1):
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
    def pendiente(self, lastquote,  type=1):
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

    def tpc_total(self,  last,  type=1):
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
            
        
    def tpc_tae(self, last, type=1):
        dias=self.age()
        if self.age()==0:
            dias=1
        return Percentage(self.tpc_total(last, type)*365,  dias)
        
        

## Class to manage operation concepts for expenses, incomes... For example: Restuarant, Supermarket
class Concept:
    ## Constructor with the following attributes combination
    ## 1. Concept(mem). Create a Concept with all attributes to None
    ## 2. Concept(mem, row, tipooperacion). Create a Concept from a db row, generated in a database query
    ## 3. Concept(mem, name, tipooperacion,editable, id). Create a Concept passing all attributes
    ## @param mem MemXulpymoney object
    ## @param row Dictionary of a database query cursor
    ## @param tipooperacion OperationType Bank object
    ## @param name Concept name
    ## @param editable Boolean that sets if a Concept is editable by the user
    ## @param id Integer that sets the id of an Concept. You must set id=None if the Concept is not in the database. id is set in the save method
    def __init__(self, *args):
        def init__create(name, tipooperacion, editable,  id):
            self.id=id
            self.name=self.mem.trMem(name)
            self.tipooperacion=tipooperacion
            self.editable=editable

        def init__db_row(row, tipooperacion):
            return init__create(row['concepto'], tipooperacion, row['editable'], row['id_conceptos'])

        self.mem=args[0]
        if len(args)==1:
            init__create(None, None, None, None)
        elif len(args)==3:
            init__db_row(*args[1:])
        elif len(args)==5:
            init__create(*args[1:])

    def __repr__(self):
        return ("Instancia de Concept: {0} -- {1} ({2})".format( self.name, self.tipooperacion.name,  self.id))

        
    def save(self):
        cur=self.mem.con.cursor()
        if self.id==None:
            cur.execute("insert into conceptos (concepto, id_tiposoperaciones, editable) values (%s, %s, %s) returning id_conceptos", (self.name, self.tipooperacion.id, self.editable))
            self.id=cur.fetchone()[0]
        else:
            cur.execute("update conceptos set concepto=%s, id_tiposoperaciones=%s, editable=%s where id_conceptos=%s", (self.name, self.tipooperacion.id, self.editable, self.id))
        cur.close()
                            
    def is_deletable(self):
        """Función que devuelve un booleano si una cuenta es borrable, es decir, que no tenga registros dependientes."""
        if self.uses()>0 and self.editable==True:
            return False
        return True
        
    def uses(self):
        """Returns the number of uses in opercuenta and opertarjetas"""
        cur=self.mem.con.cursor()
        cur.execute("select count(*) from opercuentas where id_conceptos=%s", (self.id, ))
        opercuentas=cur.fetchone()[0]
        cur.execute("select count(*) from opertarjetas where id_conceptos=%s", (self.id, ))
        opertarjetas=cur.fetchone()[0]
        cur.close()
        return opercuentas+opertarjetas

    def borrar(self):
        if self.is_deletable():
            cur=self.mem.con.cursor()        
            cur.execute("delete from conceptos where id_conceptos=%s", (self.id, ))
            cur.close()
            return True
        return False

    def media_mensual(self):
        cur=self.mem.con.cursor()
        cur.execute("select datetime from opercuentas where id_conceptos=%s union all select datetime from opertarjetas where id_conceptos=%s order by datetime limit 1", (self.id, self.id))
        res=cur.fetchone()
        if res==None:
            primerafecha=date.today()-timedelta(days=1)
        else:
            primerafecha=res['datetime'].date()
        cur.execute("select sum(importe) as suma from opercuentas where id_conceptos=%s union all select sum(importe) as suma from opertarjetas where id_conceptos=%s", (self.id, self.id))
        suma=Decimal(0)
        for i in cur:
            if i['suma']==None:
                continue
            suma=suma+i['suma']
        cur.close()
        return Decimal(30)*suma/((date.today()-primerafecha).days+1)
        
    def mensual(self,   year,  month):  
        """Saca el gasto mensual de este concepto"""
        cur=self.mem.con.cursor()
        cur.execute("select sum(importe) as suma from opercuentas where id_conceptos=%s and date_part('month',datetime)=%s and date_part('year', datetime)=%s union all select sum(importe) as suma from opertarjetas where id_conceptos=%s  and date_part('month',datetime)=%s and date_part('year', datetime)=%s", (self.id,  month, year,  self.id,  month, year  ))
        suma=0
        for i in cur:
            if i['suma']==None:
                continue
            suma=suma+i['suma']
        cur.close()
        return suma

        
class DBData:
    def __init__(self, mem):
        self.mem=mem

    def load(self, progress=True):
        """
            This method will subsitute load_actives and load_inactives
        """
        inicio=datetime.now()
        
        start=datetime.now()
        self.products=ProductManager(self.mem)
        self.products.load_from_db("select * from products", progress)
        debug("DBData > Products took {}".format(datetime.now()-start))
        
        self.benchmark=self.products.find_by_id(int(self.mem.settingsdb.value("mem/benchmark", "79329" )))
        self.benchmark.needStatus(2)
        
        #Loading currencies
        start=datetime.now()
        self.currencies=ProductManager(self.mem)
        for p in self.products.arr:
            if p.type.id==6:
                p.needStatus(3)
                self.currencies.append(p)
        debug("DBData > Currencies took {}".format(datetime.now()-start))
        
        self.banks=BankManager(self.mem)
        self.banks.load_from_db("select * from entidadesbancarias")

        self.accounts=AccountManager(self.mem, self.banks)
        self.accounts.load_from_db("select * from cuentas")

        self.investments=InvestmentManager(self.mem, self.accounts, self.products, self.benchmark)
        self.investments.load_from_db("select * from inversiones", progress)
        self.investments.needStatus(2, progress=True)
        
        
        #change status to 1 to self.investments products
        pros=self.investments.ProductManager_with_investments_distinct_products()
        pros.needStatus(1, progress=True)
        
        info("DBData loaded: {}".format(datetime.now()-inicio))

    def accounts_active(self):        
        r=AccountManager(self.mem, self.banks)
        for b in self.accounts.arr:
            if b.active==True:
                r.append(b)
        return r 

    def accounts_inactive(self):        
        r=AccountManager(self.mem, self.banks)
        for b in self.accounts.arr:
            if b.active==False:
                r.append(b)
        return r
        
    def banks_active(self):        
        r=BankManager(self.mem)
        for b in self.banks.arr:
            if b.active==True:
                r.append(b)
        return r        
        
    def banks_inactive(self):        
        r=BankManager(self.mem)
        for b in self.banks.arr:
            if b.active==False:
                r.append(b)
        return r        

            
    def investments_active(self):        
        r=InvestmentManager(self.mem, self.accounts, self.products, self.benchmark)
        for b in self.investments.arr:
            if b.active==True:
                r.append(b)
        return r        
        
    def investments_inactive(self):        
        r=InvestmentManager(self.mem, self.accounts, self.products, self.benchmark)
        for b in self.investments.arr:
            if b.active==False:
                r.append(b)
        return r        

    def banks_set(self, active):
        """Function to point to list if is active or not"""
        if active==True:
            return self.banks_active()
        else:
            return self.banks_inactive()
            
    def accounts_set(self, active):
        """Function to point to list if is active or not"""
        if active==True:
            return self.accounts_active()
        else:
            return self.accounts_inactive()
    
    def investments_set(self, active):
        """Function to point to list if is active or not"""
        if active==True:
            return self.investments_active()
        else:
            return self.investments_inactive()
        
class Dividend:
    def __init__(self, mem):
        self.mem=mem
        self.id=None
        self.investment=None
        self.bruto=None
        self.retencion=None
        self.neto=None
        self.dpa=None
        self.datetime=None
        self.opercuenta=None
        self.comision=None
        self.concepto=None#Puedeser 39 o 62 para derechos venta
        self.currency_conversion=None

    def __repr__(self):
        return ("Instancia de Dividend: {0} ({1})".format( self.neto, self.id))
        
    def init__create(self,  inversion,  bruto,  retencion, neto,  dpa,  fecha,  comision,  concepto, currency_conversion,  opercuenta=None,  id=None):
        """Opercuenta puede no aparecer porque se asigna al hacer un save que es cuando se crea. Si id=None,opercuenta debe ser None"""
        self.id=id
        self.investment=inversion
        self.bruto=bruto
        self.retencion=retencion
        self.neto=neto
        self.dpa=dpa
        self.datetime=fecha
        self.opercuenta=opercuenta
        self.comision=comision
        self.concepto=concepto
        self.currency_conversion=currency_conversion
        return self
        
    def init__db_row(self, row, inversion,  opercuenta,  concepto):
        return self.init__create(inversion,  row['bruto'],  row['retencion'], row['neto'],  row['valorxaccion'],  row['fecha'],   row['comision'],  concepto, row['currency_conversion'], opercuenta, row['id_dividends'])
        
    def init__db_query(self, id):
        """
            Searches in db dividend, investment from memory, operaccount from db
        """
        row=self.mem.con.cursor_one_row("select * from dividends where id_dividends=%s", (id, ))
        accountoperation=AccountOperation(self.mem,  row['id_opercuentas'])
        return self.init__db_row(row, self.mem.data.investments.find_by_id(row['id_inversiones']), accountoperation, self.mem.conceptos.find_by_id(row['id_conceptos']))
        
    def borrar(self):
        """Borra un dividend, para ello borra el registro de la tabla dividends 
            y el asociado en la tabla opercuentas
            
            También actualiza el balance de la cuenta."""
        cur=self.mem.con.cursor()
        self.opercuenta.borrar()
        cur.execute("delete from dividends where id_dividends=%s", (self.id, ))
        cur.close()
        
    def gross(self, type=1):
        if type==1:
            return Money(self.mem, self.bruto, self.investment.product.currency)
        elif type==2:
            return Money(self.mem, self.bruto, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion)
        elif type==3:
            return Money(self.mem, self.bruto, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion).local(self.datetime)

    def net(self, type=1):
        if type==1:
            return Money(self.mem, self.neto, self.investment.product.currency)
        elif type==2:
            return Money(self.mem, self.neto, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion)
        elif type==3:
            return Money(self.mem, self.neto, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion).local(self.datetime)
    def retention(self, type=1):
        if type==1:
            return Money(self.mem, self.retencion, self.investment.product.currency)
        elif type==2:
            return Money(self.mem, self.retencion, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion)
        elif type==3:
            return Money(self.mem, self.retencion, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion).local(self.datetime)
    def dps(self, type=1):
        "Dividend per share"
        if type==1:
            return Money(self.mem, self.dpa, self.investment.product.currency)
        elif type==2:
            return Money(self.mem, self.dpa, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion)
        elif type==3:
            return Money(self.mem, self.dpa, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion).local(self.datetime)
    def commission(self, type=1):
        if type==1:
            return Money(self.mem, self.comision, self.investment.product.currency)
        elif type==2:
            return Money(self.mem, self.comision, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion)
        elif type==3:
            return Money(self.mem, self.comision, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion).local(self.datetime)
            
    def copy(self ):
        return Dividend(self.mem).init__create(self.investment, self.bruto, self.retencion, self.neto, self.dpa, self.datetime, self.comision, self.concepto, self.currency_conversion, self.opercuenta, self.id)
        
    def neto_antes_impuestos(self):
        return self.bruto-self.comision
    
    def save(self):
        """Insertar un dividend y una opercuenta vinculada a la tabla dividends en el campo id_opercuentas
        
        En caso de que sea actualizar un dividend hay que actualizar los datos de opercuenta y se graba desde aquí. No desde el objeto opercuenta
        
        Actualiza la cuenta 
        """
        cur=self.mem.con.cursor()
        if self.id==None:#Insertar
            self.opercuenta=AccountOperation(self.mem,  self.datetime,self.concepto, self.concepto.tipooperacion, self.neto, "Transaction not finished", self.investment.account, None)
            self.opercuenta.save()
            cur.execute("insert into dividends (fecha, valorxaccion, bruto, retencion, neto, id_inversiones,id_opercuentas, comision, id_conceptos,currency_conversion) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) returning id_dividends", (self.datetime, self.dpa, self.bruto, self.retencion, self.neto, self.investment.id, self.opercuenta.id, self.comision, self.concepto.id, self.currency_conversion))
            self.id=cur.fetchone()[0]
            self.opercuenta.comentario=Comment(self.mem).encode(eComment.Dividend, self)
            self.opercuenta.save()
        else:
            self.opercuenta.datetime=self.datetime
            self.opercuenta.importe=self.neto
            self.opercuenta.comentario=Comment(self.mem).encode(eComment.Dividend, self)
            self.opercuenta.concepto=self.concepto
            self.opercuenta.tipooperacion=self.concepto.tipooperacion
            self.opercuenta.save()
            cur.execute("update dividends set fecha=%s, valorxaccion=%s, bruto=%s, retencion=%s, neto=%s, id_inversiones=%s, id_opercuentas=%s, comision=%s, id_conceptos=%s, currency_conversion=%s where id_dividends=%s", (self.datetime, self.dpa, self.bruto, self.retencion, self.neto, self.investment.id, self.opercuenta.id, self.comision, self.concepto.id, self.currency_conversion, self.id))
        cur.close()

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
        
    def price(self, type=1):
        if type==1:
            return Money(self.mem, self.valor_accion, self.investment.product.currency)
        else:
            return Money(self.mem, self.valor_accion, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion)
            
    def gross(self, type=1):
        if type==1:
            return Money(self.mem, abs(self.shares*self.valor_accion), self.investment.product.currency)
        else:
            return Money(self.mem, abs(self.shares*self.valor_accion), self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion)
            
    def net(self, type=1):
        if self.shares>=Decimal(0):
            return self.gross(type)+self.commission(type)+self.taxes(type)
        else:
            return self.gross(type)-self.commission(type)-self.taxes(type)
            
    def taxes(self, type=1):
        if type==1:
            return Money(self.mem, self.impuestos, self.investment.product.currency)
        else:
            return Money(self.mem, self.impuestos, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion)
            
    def commission(self, type=1):
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
   
class Bank:
    """Clase que encapsula todas las funciones que se pueden realizar con una Entidad bancaria o banco"""
    def __init__(self, mem):
        """Constructor que inicializa los atributos a None"""
        self.mem=mem
        self.id=None
        self.name=None
        self.active=None
        
    def init__create(self, name,  activa=True, id=None):
        self.id=id
        self.active=activa
        self.name=name
        return self
        
    def __repr__(self):
        return ("Instancia de Bank: {0} ({1})".format( self.name, self.id))

    def init__db_row(self, row):
        self.id=row['id_entidadesbancarias']
        self.name=QCoreApplication.translate("Mem", row['entidadbancaria'])
        self.active=row['active']
        return self
        
    def qmessagebox_inactive(self):
        if self.active==False:
            m=QMessageBox()
            m.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
            m.setIcon(QMessageBox.Information)
            m.setText(QApplication.translate("Mem", "The associated bank is not active. You must activate it first"))
            m.exec_()    
            return True
        return False
    def save(self):
        """Función que inserta si self.id es nulo y actualiza si no es nulo"""
        cur=self.mem.con.cursor()
        if self.id==None:
            cur.execute("insert into entidadesbancarias (entidadbancaria, active) values (%s,%s) returning id_entidadesbancarias", (self.name, self.active))
            self.id=cur.fetchone()[0]
        else:
            cur.execute("update entidadesbancarias set entidadbancaria=%s, active=%s where id_entidadesbancarias=%s", (self.name, self.active, self.id))
        cur.close()
        
    def balance(self, setcuentas,  setinversiones):
        resultado=Money(self, 0, self.mem.localcurrency)
        #Recorre balance cuentas
        for c in setcuentas.arr:
            if c.eb.id==self.id:
                resultado=resultado+c.balance().local()
        
        #Recorre balance inversiones
        for i in setinversiones.arr:
            if i.account.eb.id==self.id:
                resultado=resultado+i.balance().local()
        return resultado
        
    def is_deletable(self):
        """Función que devuelve un booleano si una cuenta es borrable, es decir, que no tenga registros dependientes."""
        #Recorre balance cuentas
        for c  in self.mem.data.accounts.arr:
            if c.eb.id==self.id:
                if c.is_deletable()==self.id:
                    return False
        return True
        
    def delete(self):
        """Función que borra. You must use is_deletable before"""
        cur=self.mem.con.cursor()
        cur.execute("delete from entidadesbancarias where id_entidadesbancarias=%s", (self.id, ))  
        cur.close()

class Investment:
    """Clase que encapsula todas las funciones que se pueden realizar con una Inversión
    
    Las entradas al objeto pueden ser por:
        - init__db_row
        - init__db_extended_row
        - create. Solo contenedor hasta realizar un save y guardar en id, el id apropiado. mientras id=None
        
    """
    def __init__(self, mem):
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

        ## Variable with the current product status
        ## 0 No data
        ## 1 Loaded ops
        ## 2 Calculate ops_actual, ops_historical
        ## 3 Dividends
        self.status=0
        self.dividends=None#Must be created due to in mergeing investments needs to add it manually
    
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
            cur=self.mem.con.cursor()
            self.op=InvestmentOperationHomogeneusManager(self.mem, self)
            cur.execute("select * from operinversiones where id_inversiones=%s order by datetime", (self.id, ))
            for row in cur:
                self.op.append(InvestmentOperation(self.mem).init__db_row(row, self, self.mem.tiposoperaciones.find_by_id(row['id_tiposoperaciones'])))
            cur.close()
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

    def init__create(self, name, venta, cuenta, product, selling_expiration, active, id=None):
        self.name=name
        self.venta=venta
        self.account=cuenta
        self.product=product
        self.active=active
        self.selling_expiration=selling_expiration
        self.id=id
        return self

    ## Replicates an investment with data at datetime
    ## Loads self.op, self.op_actual, self.op_historica and self.hlcontractmanager
    ## Return and Investment with status 3 (dividends inside)
    ## @param dt Datetime 
    ## @return Investment
    def Investment_At_Datetime(self, dt):
        self.needStatus(3)
        r=self.copy()
        r.op=self.op.ObjectManager_copy_until_datetime(dt, self.mem, r)
        (r.op_actual,  r.op_historica)=r.op.get_current_and_historical_operations()
        r.dividends=self.dividends.ObjectManager_copy_until_datetime(dt, self.mem, r)
        return r

    def copy(self ):
        return Investment(self.mem).init__create(self.name, self.venta, self.account, self.product, self.selling_expiration, self.active, self.id)
    
    def save(self):
        """Inserta o actualiza la inversión dependiendo de si id=None o no"""
        cur=self.mem.con.cursor()
        if self.id==None:
            cur.execute("insert into inversiones (inversion, venta, id_cuentas, active, selling_expiration,products_id) values (%s, %s,%s,%s,%s,%s) returning id_inversiones", (self.name, self.venta, self.account.id, self.active, self.selling_expiration,  self.product.id))    
            self.id=cur.fetchone()[0]      
        else:
            cur.execute("update inversiones set inversion=%s, venta=%s, id_cuentas=%s, active=%s, selling_expiration=%s, products_id=%s where id_inversiones=%s", (self.name, self.venta, self.account.id, self.active, self.selling_expiration,  self.product.id, self.id))
        cur.close()

    def selling_price(self, type=1):
        if type==1:
            return Money(self.mem, self.venta, self.product.currency)

    ## This function is in Investment because uses investment information
    def DividendManager_of_current_operations(self):
        self.needStatus(3)
        if self.op_actual.length()==0:
            return DividendHomogeneusManager(self.mem, self)
        else:
            return self.dividends.ObjectManager_from_datetime(self.op_actual.first().datetime, self.mem, self)
        
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

    def resultsCurrency(self, type=1 ):
        if type==1:
            return self.product.currency
        elif type==2:
            return self.account.currency
        elif type==3:
            return self.mem.localcurrency
        critical("Rare investment result currency: {}".format(type))

    def quote2money(self, quote,  type=1):
        """
            Converts a quote object to a money. Then shows money with the currency type
        """        
        if quote==None:
            return None
            
        if quote.product.currency.id!=self.product.currency.id:
            error("I can't convert a quote to money, if quote product is diferent to investment product")
            return None
            
        if type==1:
            return Money(self.mem, quote.quote, self.product.currency)
        elif type==2:
            return Money(self.mem, quote.quote, self.product.currency).convert(self.account.currency, quote.datetime)
        elif type==3:
            return  Money(self.mem, quote.quote, self.product.currency).convert(self.account.currency, quote.datetime).local(quote.datetime)
    
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
        if self.product.currency.id==self.account.currency.id:
            return True
        return False
        
    def qmessagebox_inactive(self):
        if self.active==False:
            m=QMessageBox()
            m.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
            m.setIcon(QMessageBox.Information)
            m.setText(QApplication.translate("Mem", "The associated product is not active. You must activate it first"))
            m.exec_()    
            return True
        return False

    def questionbox_inactive(self):
        """It makes a database commit"""
        if self.active==False:
            reply = QMessageBox.question(None, QApplication.translate("Mem", 'Investment activation question'), QApplication.translate("Mem", "Investment {} ({}) is inactive.\nDo you want to activate it?").format(self.name, self.account.name), QMessageBox.Yes, QMessageBox.No)          
            if reply==QMessageBox.Yes:
                self.active=True
                self.save()
                self.mem.con.commit()
                return QMessageBox.Yes
            return QMessageBox.No
        return QMessageBox.Yes
        
    ## Función que calcula el balance de la inversión
    def balance(self, fecha=None, type=eMoneyCurrency.Product):
#        acciones=self.shares(fecha)
#        currency=self.resultsCurrency(type)
#        if acciones==0 or self.product.result.basic.last.quote==None:#Empty xulpy
#            return Money(self.mem, 0, currency)
                
        if fecha==None:
            return self.op_actual.balance(self.product.result.basic.last, type)
        else:
            quote=Quote(self.mem).init__from_query(self.product, dtaware_day_end_from_date(fecha, self.mem.localzone_name))
            if quote.datetime==None:
                debug ("Investment balance: {0} ({1}) en {2} no tiene valor".format(self.name, self.product.id, fecha))
                return Money(self.mem, 0, self.resultsCurrency(type) )
            return self.Investment_At_Datetime(dtaware_day_end_from_date(fecha, self.mem.localzone_name)).op_actual.balance(quote, type)
        
    ## Función que calcula el balance invertido partiendo de las acciones y el precio de compra
    ## Necesita haber cargado mq getbasic y operinversionesactual
    def invertido(self, date=None, type=1):
        if date==None or date==date.today():#Current
            return self.op_actual.invertido(type)
        else:
            # Creo una vinversion fake para reutilizar codigo, cargando operinversiones hasta date
            invfake=self.copy()
            invfake.op=self.op.ObjectManager_copy_until_datetime(dtaware_day_end_from_date(date, self.mem.localzone_name), self.mem, invfake)
            (invfake.op_actual,  invfake.op_historica)=invfake.op.get_current_and_historical_operations()
            return invfake.op_actual.invertido(type)
                
    def percentage_to_selling_point(self):       
        """Función que calcula el tpc venta partiendo de las el last y el valor_venta
        Necesita haber cargado mq getbasic y operinversionesactual"""
        if self.venta==0 or self.venta==None:
            return Percentage()
        if self.op_actual.shares()>0:
            return Percentage(self.venta-self.product.result.basic.last.quote, self.product.result.basic.last.quote)
        else:#Long short products
            return Percentage(-(self.venta-self.product.result.basic.last.quote), self.product.result.basic.last.quote)
        

class CreditCardOperation:
    def __init__(self, mem):
        """CreditCard es un objeto CreditCardOperation. pagado, fechapago y opercuenta solo se rellena cuando se paga"""
        self.mem=mem
        self.id=None
        self.datetime=None
        self.concepto=None
        self.tipooperacion=None
        self.importe=None
        self.comentario=None
        self.tarjeta=None
        self.pagado=None
        self.fechapago=None
        self.opercuenta=None
        
    def __repr__(self):
        return "CreditCardOperation: {}".format(self.id)

    def init__create(self, dt,  concepto, tipooperacion, importe, comentario, tarjeta, pagado=None, fechapago=None, opercuenta=None, id_opertarjetas=None):
        """pagado, fechapago y opercuenta solo se rellena cuando se paga"""
        self.id=id_opertarjetas
        self.datetime=dt
        self.concepto=concepto
        self.tipooperacion=tipooperacion
        self.importe=importe
        self.comentario=comentario
        self.tarjeta=tarjeta
        self.pagado=pagado
        self.fechapago=fechapago
        self.opercuenta=opercuenta
        return self
            
            
    def init__db_query(self, id):
        """Creates a CreditCardOperation querying database for an id_opertarjetas"""
        if id==None:
            return None
        cur=self.mem.con.cursor()
        cur.execute("select * from opertarjetas where id_opertarjetas=%s", (id, ))
        for row in cur:
            concepto=self.mem.conceptos.find_by_id(row['id_conceptos'])
            self.init__db_row(row, concepto, concepto.tipooperacion, self.mem.data.accounts.find_creditcard_by_id(row['id_tarjetas']))
        cur.close()
        return self

    def init__db_row(self, row, concepto, tipooperacion, tarjeta, opercuenta=None):
        return self.init__create(row['datetime'],  concepto, tipooperacion, row['importe'], row['comentario'], tarjeta, row['pagado'], row['fechapago'], opercuenta, row['id_opertarjetas'])
        
    def borrar(self):
        cur=self.mem.con.cursor()
        sql="delete from opertarjetas where id_opertarjetas="+ str(self.id)
        cur.execute(sql)
        cur.close()
        
    def save(self):
        cur=self.mem.con.cursor()
        if self.id==None:#insertar
            sql="insert into opertarjetas (datetime, id_conceptos, id_tiposoperaciones, importe, comentario, id_tarjetas, pagado) values ('" + str(self.datetime) + "'," + str(self.concepto.id)+","+ str(self.tipooperacion.id) +","+str(self.importe)+", '"+self.comentario+"', "+str(self.tarjeta.id)+", "+str(self.pagado)+") returning id_opertarjetas"
            cur.execute(sql);
            self.id=cur.fetchone()[0]
        else:
            if self.tarjeta.pagodiferido==True and self.pagado==False:#No hay opercuenta porque es en diferido y no se ha pagado
                cur.execute("update opertarjetas set datetime=%s, id_conceptos=%s, id_tiposoperaciones=%s, importe=%s, comentario=%s, id_tarjetas=%s, pagado=%s, fechapago=%s, id_opercuentas=%s where id_opertarjetas=%s", (self.datetime, self.concepto.id, self.tipooperacion.id,  self.importe,  self.comentario, self.tarjeta.id, self.pagado, self.fechapago, None, self.id))
            else:
                cur.execute("update opertarjetas set datetime=%s, id_conceptos=%s, id_tiposoperaciones=%s, importe=%s, comentario=%s, id_tarjetas=%s, pagado=%s, fechapago=%s, id_opercuentas=%s where id_opertarjetas=%s", (self.datetime, self.concepto.id, self.tipooperacion.id,  self.importe,  self.comentario, self.tarjeta.id, self.pagado, self.fechapago, self.opercuenta.id, self.id))
        cur.close()

class OperationType:
    def __init__(self):
        self.id=None
        self.name=None
        
    def init__create(self, name,  id=None):
        self.id=id
        self.name=name
        return self

class AnnualTarget:
    def __init__(self, mem):
        self.mem=mem
        self.year=None
        self.percentage=None
        self.lastyear_assests=None
        self.saved_in_db=False #Controls if AnnualTarget is saved in the table annualtargets
    
    ## Fills the object with data from db.
    ## If lastyear_assests=None it gets the assests from db
    def init__from_db(self, year, lastyear_assests=None):
        cur=self.mem.con.cursor()
        
        if lastyear_assests==None:
            self.lastyear_assests=Assets(self.mem).saldo_total(self.mem.data.investments,  date(year-1, 12, 31))
        else:
            self.lastyear_assests=lastyear_assests
        
        cur.execute("select * from annualtargets where year=%s", (year, ))
        if cur.rowcount==0:
            self.year=year
            self.percentage=0
        else:
            row=cur.fetchone()
            self.year=year
            self.percentage=row['percentage']
            self.saved_in_db=True
        cur.close()
        return self
        
    def save(self):
        cur=self.mem.con.cursor()
        if self.saved_in_db==False:
            cur.execute("insert into annualtargets (year, percentage) values (%s,%s)", (self.year, self.percentage))
            self.saved_in_db=True
        else:
            cur.execute("update annualtargets set percentage=%s where year=%s", (self.percentage, self.year))
        cur.close()
        
    ## Returns the amount of tthe annual target
    def annual_balance(self):
        return self.lastyear_assests.amount*self.percentage/100
        
    ## Returns the amount of the monthly target (annual/12)
    def monthly_balance(self):
        return self.annual_balance()/12

class Assets:
    def __init__(self, mem):
        self.mem=mem        
    
    ## Devuelve la datetime actual si no hay datos. Base de datos vacía
    def first_datetime_with_user_data(self):        
        cur=self.mem.con.cursor()
        sql='select datetime from opercuentas UNION all select datetime from operinversiones UNION all select datetime from opertarjetas order by datetime limit 1;'
        cur.execute(sql)
        if cur.rowcount==0:
            return datetime.now()
        resultado=cur.fetchone()[0]
        cur.close()
        return resultado

    def saldo_todas_cuentas(self,  datetime=None):
        """Si cur es none y datetime calcula el balance actual."""
        cur=self.mem.con.cursor()
        cur.execute("select cuentas_saldo('"+str(datetime)+"') as balance")
        resultado=cur.fetchone()[0] 
        cur.close()
        return Money(self.mem, resultado, self.mem.localcurrency)

        
    def saldo_total(self, setinversiones,  datetime):
        """Versión que se calcula en cliente muy optimizada"""
        return self.saldo_todas_cuentas(datetime)+self.saldo_todas_inversiones(setinversiones, datetime)

    ## This method gets all investments balance. High-Low investments are not sumarized, due to they have daily account adjustments
    ##
    ## Esta función se calcula en cliente
    def saldo_todas_inversiones(self, setinversiones, fecha):
        resultado=Money(self.mem, 0, self.mem.localcurrency)
        for i in setinversiones.arr:
            if i.product.high_low==False:#Due to there is a daily adjustments in accouts 
                resultado=resultado+i.balance(fecha, type=3)
        return resultado

    ## This method gets all High-Low investments balance
    ##
    ## Esta función se calcula en cliente
    def saldo_todas_inversiones_high_low(self, setinversiones, fecha):
        resultado=Money(self.mem, 0, self.mem.localcurrency)
        for i in setinversiones.arr:
            if i.product.high_low==True:
                resultado=resultado+i.balance(fecha, type=3)
        return resultado

    def saldo_todas_inversiones_riesgo_cero(self, setinversiones, fecha=None):
        """Versión que se calcula en cliente muy optimizada
        Fecha None calcula  el balance actual
        """
        resultado=Money(self.mem, 0, self.mem.localcurrency)
        for inv in setinversiones.arr:
            if inv.product.percentage==0:        
                resultado=resultado+inv.balance( fecha, type=3)
        return resultado
            
    def dividends_neto(self, ano,  mes=None):
        """Dividend cobrado en un año y mes pasado como parámetro, independientemente de si la inversión esta activa o no.
        El 63 es un gasto aunque también este registrado en dividends."""
        r=Money(self.mem, 0, self.mem.localcurrency)
        for inv in self.mem.data.investments.arr:
            inv.needStatus(3)
            for dividend in inv.dividends.arr:
                if mes==None:
                    if dividend.datetime.year==ano:
                        r=r+dividend.net(type=3)
                else:# WIth mounth
                    if dividend.datetime.year==ano and dividend.datetime.month==mes:
                        r=r+dividend.net(type=3)
        return r

    def dividends_bruto(self,  ano,  mes=None):
        """Dividend cobrado en un año y mes pasado como parámetro, independientemente de si la inversión esta activa o no"""
        r=Money(self.mem, 0, self.mem.localcurrency)
        for inv in self.mem.data.investments.arr:
            inv.needStatus(3)
            for dividend in inv.dividends.arr:
                if mes==None:
                    if dividend.datetime.year==ano:
                        r=r+dividend.gross(type=3)
                else:# WIth mounth
                    if dividend.datetime.year==ano and dividend.datetime.month==mes:
                        r=r+dividend.net(type=3)
        return r
        
        
        
        

        
    def invested(self, date=None):
        """Devuelve el patrimonio invertido en una determinada fecha"""
        if date==None or date==date.today():
            array=self.mem.data.investments_active().arr #Current and active
        else:
            array=self.mem.data.investments.arr#All, because i don't know witch one was active.
        
        r=Money(self.mem, 0, self.mem.localcurrency)
        for inv in array:
            r=r+inv.invertido(date, type=3)
        return r
        
    def saldo_todas_inversiones_bonds(self, fecha=None):        
        """Versión que se calcula en cliente muy optimizada
        Fecha None calcula  el balance actual
        """
        resultado=Money(self.mem, 0, self.mem.localcurrency)
        for inv in self.mem.data.investments.arr:
            if inv.product.type.id in (eProductType.PublicBond, eProductType.PrivateBond):#public and private bonds        
                if fecha==None:
                    resultado=resultado+inv.balance().local()
                else:
                    resultado=resultado+inv.balance( fecha).local()
        return resultado

    def patrimonio_riesgo_cero(self, setinversiones, fecha):
        """CAlcula el patrimonio de riego cero"""
        return self.saldo_todas_cuentas(fecha)+self.saldo_todas_inversiones_riesgo_cero(setinversiones, fecha)

    def saldo_anual_por_tipo_operacion(self,  year,  id_tiposoperaciones):   
        """Opercuentas y opertarjetas"""
        resultado=Money(self.mem, 0, self.mem.localcurrency)
        for currency in self.mem.currencies.arr:
            cur=self.mem.con.cursor()
            sql="""
                select sum(Importe) as importe 
                from 
                    opercuentas,
                    cuentas
                where 
                    id_tiposoperaciones={0} and 
                    date_part('year',datetime)={1} and
                    cuentas.currency='{2}' and
                    cuentas.id_cuentas=opercuentas.id_cuentas   
            union all 
                select sum(Importe) as importe 
                from 
                    opertarjetas ,
                    tarjetas,
                    cuentas
                where 
                    id_tiposoperaciones={0} and 
                    date_part('year',datetime)={1} and
                    cuentas.currency='{2}' and
                    cuentas.id_cuentas=tarjetas.id_cuentas and
                    tarjetas.id_tarjetas=opertarjetas.id_tarjetas""".format(id_tiposoperaciones, year,  currency.id)
            cur.execute(sql)        
            for i in cur:
                if i['importe']==None:
                    continue
                resultado=resultado+Money(self.mem, i['importe'], currency).local()
            cur.close()
        return resultado

    def saldo_por_tipo_operacion(self,  year,  month,  id_tiposoperaciones):   
        """Opercuentas y opertarjetas"""
        resultado=Money(self.mem, 0, self.mem.localcurrency)
        for currency in self.mem.currencies.arr:
            cur=self.mem.con.cursor()
            sql="""
                select sum(Importe) as importe 
                from 
                    opercuentas,
                    cuentas
                where 
                    id_tiposoperaciones={0} and 
                    date_part('year',datetime)={1} and
                    date_part('month',datetime)={2} and
                    cuentas.currency='{3}' and
                    cuentas.id_cuentas=opercuentas.id_cuentas   
            union all 
                select sum(Importe) as importe 
                from 
                    opertarjetas ,
                    tarjetas,
                    cuentas
                where 
                    id_tiposoperaciones={0} and 
                    date_part('year',datetime)={1} and
                    date_part('month',datetime)={2} and
                    cuentas.currency='{3}' and
                    cuentas.id_cuentas=tarjetas.id_cuentas and
                    tarjetas.id_tarjetas=opertarjetas.id_tarjetas""".format(id_tiposoperaciones, year, month,  currency.id)
            cur.execute(sql)        
            for i in cur:
                if i['importe']==None:
                    continue
                resultado=resultado+Money(self.mem, i['importe'], currency).local()
            cur.close()
        return resultado
        
    def consolidado_bruto(self, setinversiones,  year=None, month=None):
        """Si year es none calcula el historicca  si month es nonve calcula el anual sino el mensual"""
        resultado=Money(self.mem, 0, self.mem.localcurrency)
        for i in setinversiones.arr:        
            resultado=resultado+i.op_historica.consolidado_bruto(year, month)
        return resultado
    def consolidado_neto_antes_impuestos(self, setinversiones, year=None, month=None):
        """Si year es none calcula el historicca  si month es nonve calcula el anual sino el mensual"""
        resultado=Money(self.mem, 0, self.mem.localcurrency)
        for i in setinversiones.arr:        
            resultado=resultado+i.op_historica.consolidado_neto_antes_impuestos(year, month)
        return resultado
        
                
    def consolidado_neto(self, setinversiones, year=None, month=None):
        """Si year es none calcula el historicca  si month es nonve calcula el anual sino el mensual"""
        resultado=Money(self.mem, 0, self.mem.localcurrency)
        for i in setinversiones.arr:        
            resultado=resultado+i.op_historica.consolidado_neto(year, month).local()
        return resultado        



class CreditCardOperationManager(ObjectManager_With_IdDatetime_Selectable):
    def __init__(self, mem):
        ObjectManager_With_IdDatetime_Selectable.__init__(self)
        self.mem=mem

    def balance(self):
        """Returns the balance of all credit card operations"""
        result=Decimal(0)
        for o in self.arr:
            result=result+o.importe
        return result
        
    def load_from_db(self, sql):
        del self.arr
        self.arr=[]
        cur=self.mem.con.cursor()
        cur.execute(sql)#"Select * from opercuentas"
        for row in cur:        
            co=CreditCardOperation(self.mem).init__db_row(row, self.mem.conceptos.find_by_id(row['id_conceptos']), self.mem.tiposoperaciones.find_by_id(row['id_tiposoperaciones']), self.mem.data.accounts.find_creditcard_by_id(row['id_tarjetas']), AccountOperation(self.mem,  row['id_opercuentas']))
            self.append(co)
        cur.close()
        
    def myqtablewidget(self, wdg):
        """Section es donde guardar en el config file, coincide con el nombre del formulario en el que está la tabla
        show_accounts muestra la cuenta cuando las opercuentas son de diversos cuentas (Estudios totales)"""
        ##HEADERS
        wdg.table.setColumnCount(5)
        wdg.table.setHorizontalHeaderItem(0, QTableWidgetItem(QApplication.translate("Mem","Date" )))
        wdg.table.setHorizontalHeaderItem(1, QTableWidgetItem(QApplication.translate("Mem","Concept" )))
        wdg.table.setHorizontalHeaderItem(2,  QTableWidgetItem(QApplication.translate("Mem","Amount" )))
        wdg.table.setHorizontalHeaderItem(3, QTableWidgetItem(QApplication.translate("Mem","Balance" )))
        wdg.table.setHorizontalHeaderItem(4, QTableWidgetItem(QApplication.translate("Mem","Comment" )))
        ##DATA 
        wdg.applySettings()
        wdg.table.clearContents()   
        wdg.table.setRowCount(self.length())
        balance=Decimal(0)
        self.order_by_datetime()
        for rownumber, a in enumerate(self.arr):
            balance=balance+a.importe
            wdg.table.setItem(rownumber, 0, qdatetime(a.datetime, self.mem.localzone_name))
            wdg.table.setItem(rownumber, 1, qleft(a.concepto.name))
            wdg.table.setItem(rownumber, 2, self.mem.localcurrency.qtablewidgetitem(a.importe))
            wdg.table.setItem(rownumber, 3, self.mem.localcurrency.qtablewidgetitem(balance))
            wdg.table.setItem(rownumber, 4, qleft(Comment(self.mem).decode(a.comentario)))
            if self.selected: #If selected is not necesary is None by default
                if self.selected.length()>0:
                    for sel in self.selected.arr:
                        if a.id==sel.id:
                            wdg.table.selectRow(rownumber)

class OperationTypeManager(DictObjectManager_With_IdName_Selectable):
    def __init__(self, mem):
        DictObjectManager_With_IdName_Selectable.__init__(self)
        self.mem=mem     

    def load(self):
        self.append(OperationType().init__create( QApplication.translate("Mem","Expense"),  eOperationType.Expense))
        self.append(OperationType().init__create( QApplication.translate("Mem","Income"), eOperationType.Income))
        self.append(OperationType().init__create( QApplication.translate("Mem","Transfer"), eOperationType.Transfer))
        self.append(OperationType().init__create( QApplication.translate("Mem","Purchase of shares"), eOperationType.SharesPurchase))
        self.append(OperationType().init__create( QApplication.translate("Mem","Sale of shares"), eOperationType.SharesSale))
        self.append(OperationType().init__create( QApplication.translate("Mem","Added of shares"), eOperationType.SharesAdd))
        self.append(OperationType().init__create( QApplication.translate("Mem","Credit card billing"), eOperationType.CreditCardBilling))
        self.append(OperationType().init__create( QApplication.translate("Mem","Transfer of funds"), eOperationType.TransferFunds)) #Se contabilizan como ganancia
        self.append(OperationType().init__create( QApplication.translate("Mem","Transfer of shares. Origin"), eOperationType.TransferSharesOrigin)) #No se contabiliza
        self.append(OperationType().init__create( QApplication.translate("Mem","Transfer of shares. Destiny"), eOperationType.TransferSharesDestiny)) #No se contabiliza     
        self.append(OperationType().init__create( QApplication.translate("Mem","HL investment guarantee"), eOperationType.DerivativeManagement)) #No se contabiliza     


    def qcombobox_basic(self, combo,  selected=None):
        """Load lust some items
        Selected is and object
        It sorts by name the arr""" 
        combo.clear()
        for n in (eOperationType.Expense, eOperationType.Income):
            a=self.find_by_id(str(n))
            combo.addItem(a.name, a.id)

        if selected!=None:
            combo.setCurrentIndex(combo.findData(selected.id))
            
            
    def qcombobox_investments_operations(self, combo,  selected=None):
        """Load lust some items
        Selected is and object
        It sorts by name the arr""" 
        combo.clear()
        for n in (eOperationType.SharesPurchase, eOperationType.SharesSale, eOperationType.SharesAdd, eOperationType.TransferFunds):
            a=self.find_by_id(str(n))
            combo.addItem(a.name, a.id)

        if selected!=None:
            combo.setCurrentIndex(combo.findData(selected.id))

class AgrupationManager(ObjectManager_With_IdName_Selectable):
    """Se usa para meter en mem las agrupaciones, pero también para crear agrupaciones en las inversiones"""
    def __init__(self, mem):
        """Usa la variable mem.Agrupations"""
        ObjectManager_With_IdName_Selectable.__init__(self)
        self.mem=mem

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

class LeverageManager(ObjectManager_With_IdName_Selectable):
    def __init__(self, mem):
        ObjectManager_With_IdName_Selectable.__init__(self)
        self.mem=mem

    def load_all(self):
        self.append(Leverage(self.mem).init__create(eLeverageType.Variable,QApplication.translate("Mem","Variable leverage (Warrants)"), eLeverageType.Variable))
        self.append(Leverage(self.mem).init__create(eLeverageType.NotLeveraged ,QApplication.translate("Mem","Not leveraged"), eLeverageType.NotLeveraged))
        self.append(Leverage(self.mem).init__create(eLeverageType.X2,QApplication.translate("Mem","Leverage x2"), eLeverageType.X2))
        self.append(Leverage(self.mem).init__create(eLeverageType.X3,QApplication.translate("Mem","Leverage x3"), eLeverageType.X3))
        self.append(Leverage(self.mem).init__create(eLeverageType.X4,QApplication.translate("Mem","Leverage x4"), eLeverageType.X4))
        self.append(Leverage(self.mem).init__create(eLeverageType.X5,QApplication.translate("Mem","Leverage x5"), eLeverageType.X5))
        self.append(Leverage(self.mem).init__create(eLeverageType.X10,QApplication.translate("Mem","Leverage x10"), eLeverageType.X10))
        self.append(Leverage(self.mem).init__create(eLeverageType.X50, QApplication.translate("Mem", "Leverage x50"), eLeverageType.X50))
        self.append(Leverage(self.mem).init__create(eLeverageType.X100, QApplication.translate("Mem", "Leverage x100"), eLeverageType.X100))


class Currency:
    """Clase que almacena el concepto divisa"""
    def __init__(self ):
        self.name=None
        self.symbol=None
        self.id=None

    def __repr__(self):
        return ("Currency: {} ({})".format( self.id, self.symbol))
        
    def init__create(self, name, symbol,  id=None):
        self.name=name
        self.symbol=symbol
        self.id=id
        return self

    def string(self, number,  digits=2):
        if number==None:
            return "None " + self.symbol
        else:
            return "{} {}".format(round(number, digits), self.symbol)

    def qtablewidgetitem(self, n, digits=2):
        """Devuelve un QTableWidgetItem mostrando un currency
        curren es un objeto Curryency"""
        text= self.string(n,  digits)
        a=QTableWidgetItem(text)
        a.setTextAlignment(Qt.AlignVCenter|Qt.AlignRight)
        if n==None:
            a.setForeground(QColor(0, 0, 255))
        elif n<0:
            a.setForeground(QColor(255, 0, 0))
        return a

    ## returns a qtablewidgetitem colored in red is amount is smaller than target or green if greater
    def qtablewidgetitem_with_target(self, amount, target, digits=2):
        item=self.qtablewidgetitem(amount, digits)
        if amount<target:   
            item.setBackground(eQColor.Red)
        else:
            item.setBackground(eQColor.Green)
        return item
        

            

class ProductMode:
    def __init__(self, mem):
        self.mem=mem
        self.id=None
        self.name=None
        
    def init__create(self, id, name):
        self.id=id
        self.name=name
        return self
        


class Leverage:
    def __init__(self, mem):
        self.id=None
        self.name=None
        self.multiplier=None#Valor por el que multiplicar
    def init__create(self, id, name, multiplier):
        self.id=id
        self.name=name
        self.multiplier=multiplier
        return self
        
    
class Simulation:
    def __init__(self,mem, original_db):
        """Types are defined in combo ui wdgSimulationsADd
        database is the database which data is going to be simulated"""
        self.mem=mem
        self.database=original_db
        self.id=None
        self.name=None#self.simulated_db, used to reuse ObjectManager_With_IdName_Selectable
        self.creation=None
        self.type=None
        self.starting=None
        self.ending=None
        
    def init__create(self, type_id, starting, ending):
        """Used only to create a new one"""
        self.type=self.mem.simulationtypes.find_by_id(type_id)
        self.starting=starting
        self.ending=ending
        self.creation=self.mem.localzone.now()
        return self
        
    def simulated_db(self):
        """Returns"""
        return "{}_{}".format(self.database, self.id)    

    def init__db_row(self, row):
        self.id=row['id']
        self.database=row['database']
        self.creation=row['creation']
        self.type=self.mem.simulationtypes.find_by_id(row['type'])
        self.starting=row['starting']
        self.ending=row['ending']
        return self
        
    def save(self):
        cur=self.mem.con.cursor()
        if self.id==None:
            cur.execute("insert into simulations (database, type, starting, ending, creation) values (%s,%s,%s,%s,%s) returning id", (self.database, self.type.id, self.starting, self.ending, self.creation))
            self.id=cur.fetchone()[0]
            self.name=self.simulated_db()
        else:
            cur.execute("update simulations set database=%s, type=%s, starting=%s, ending=%s, creation=%s where id=%s", (self.database, self.type.id, self.starting, self.ending, self.creation, self.id))
        cur.close()

    def delete(self):
        cur=self.mem.con.cursor()
        cur.execute("delete from simulations where id=%s", (self.id, ))
        cur.close()

class SimulationType:
    def __init__(self):
        self.id=None
        self.name=None
    def init__create(self, id, name):
        self.id=id
        self.name=name
        return self
        

    def qicon(self):
        if self.id in (1, 2):
            return QIcon(":/xulpymoney/database.png")
        else:
            return QIcon(":/xulpymoney/replication.png")    


## Split associated to a product quotes. It's a record in splits table. It doesn't modifie quotes in database. RECOMENDED
class Split:
    def __init__(self, mem):
        self.mem=mem
        self.id=None
        self.product=None
        self.datetime=None
        self.after=None
        self.before=None
        self.comment=None
                
    def __repr__(self):
        return ("Instancia de Split: {0} ({1})".format( self.id, self.id))
        
    def init__create(self, product, datetime, before, after, comment, id=None):
        self.id=id
        self.product=product
        self.datetime=datetime
        self.after=after
        self.before=before
        self.comment=comment
        return self
        
    def init__db_row(self, row, product):
        return self.init__create(product,  row['datetime'],  row['before'], row['after'],   row['comment'],  row['id'])

    def save(self):
        cur=self.mem.con.cursor()
        if self.id==None:#Insertar
            cur.execute("insert into splits(products_id,datetime,after,before,comment) values (%s,%s,%s,%s,%s) returning id", (self.product.id, self.datetime, self.after, self.before, self.comment))
            self.id=cur.fetchone()[0]
        else:
            cur.execute("update splits set products_id=%s, datetime=%s, after=%s, before=%s, comment=%s where id=%s", (self.product.id, self.datetime, self.after, self.before, self.comment, self.id))
        cur.close()


    def convertShares(self, shares):
        """Function to calculate new shares just pass the number you need to convert"""
        return shares*self.after/self.before
        
    def convertPrices(self, price):
        return price*self.before/self.after
                
    def delete(self):
        cur=self.mem.con.cursor()
        cur.execute("delete from splits where id=%s", (self.id,))
        cur.close()
            
        
    def type(self):
        """Función que devuelve si es un Split o contrasplit"""
        if self.before>self.after:
            return "Contrasplit"
        else:
            return "Split"

class SplitManager(ObjectManager_With_IdName_Selectable):
    def __init__(self, mem, product):
        ObjectManager_With_IdName_Selectable.__init__(self)
        self.product=product
        self.mem=mem
        
    def init__from_db(self, sql):
        cur=self.mem.con.cursor()
        cur.execute(sql)
        for row in cur:
            self.append(Split(self.mem).init__db_row(row, self.product))
        cur.close()
        return self
            
    def order_by_datetime(self):
        """Orders the Set using self.arr"""
        try:
            self.arr=sorted(self.arr, key=lambda c: c.product.result.basic.last.datetime,  reverse=False)  
            return True
        except:
            return False
    def myqtablewidget(self, wdg):
        """Section es donde guardar en el config file, coincide con el nombre del formulario en el que está la table
        Devuelve sumatorios"""

        wdg.table.setColumnCount(4)
        wdg.table.setHorizontalHeaderItem(0, QTableWidgetItem(QApplication.translate("Mem", "Date" )))
        wdg.table.setHorizontalHeaderItem(1, QTableWidgetItem(QApplication.translate("Mem", "Before" )))
        wdg.table.setHorizontalHeaderItem(2, QTableWidgetItem(QApplication.translate("Mem", "After" )))
        wdg.table.setHorizontalHeaderItem(3, QTableWidgetItem(QApplication.translate("Mem", "Comment" )))
        #DATA  
        wdg.applySettings()
        wdg.table.clearContents()

        wdg.table.setRowCount(len(self.arr))
        for i, o in enumerate(self.arr):
            wdg.table.setItem(i, 0, qdatetime(o.datetime, self.mem.localzone_name))
            wdg.table.setItem(i, 1, qright(o.before))
            wdg.table.setItem(i, 2, qright(o.after))
            wdg.table.setItem(i, 3, qleft(o.comment))
                
    def delete(self, o):
        o.delete()    #Delete from database
        self.remove(o)    #Removes from array
        
    def adjustPrice(self, datetime, price):
        """
            Returns a new price adjusting
        """
        r=price
        for split in reversed(self.arr):
            if datetime<split.datetime:
                r=split.convertPrices(r)
        return r
        
    def adjustOHCLDaily(self, ohcl ):
        r=OHCLDaily(self.mem)
        r.product=ohcl.product
        r.date=ohcl.date
        r.close=self.adjustPrice(ohcl.datetime(), ohcl.close)
        r.open=self.adjustPrice(ohcl.datetime(), ohcl.open)
        r.high=self.adjustPrice(ohcl.datetime(), ohcl.high)
        r.low=self.adjustPrice(ohcl.datetime(), ohcl.low)
        return r

    def adjustOHCLDailyManager(self, set):
        r=OHCLDailyManager(self.mem, self.product)
        for ohcl in set.arr:
            r.append(self.adjustOHCLDaily(ohcl))
        return r

## Class to make calculations with splits or contrasplits, between two datetimes
## This class updates quotes, and investment operations
## It's not recommended. Only useful to update quotes already in database with jumps in splits.
class SplitManual:
    def __init__(self, mem, product, sharesinitial,  sharesfinal,  dtinitial, dtfinal):
        self.mem=mem
        self.initial=sharesinitial
        self.final=sharesfinal
        self.dtinitial=dtinitial
        self.dtfinal=dtfinal
        self.product=product

    def convertShares(self, actions):
        """Function to calculate new shares just pass the number you need to convert"""
        return actions*self.final/self.initial
        
    def convertPrices(self, price):
        return price*self.initial/self.final
    
    def updateQuotes(self):
        """Transforms de price of the quotes of the array"""
        self.quotes=QuoteAllIntradayManager(self.mem)
        self.quotes.load_from_db(self.product)
        for setquoteintraday in self.quotes.arr:
            for q in setquoteintraday.arr:
                if self.dtinitial<=q.datetime and self.dtfinal>=q.datetime:
                    q.quote=self.convertPrices(q.quote)
                    q.save()
                    
    def updateDPS(self):
        set=DPSManager(self.mem, self.product)
        set.load_from_db()
        for d in set.arr:
            if self.dtinitial.date()<=d.date and self.dtfinal.date()>=d.date:
                d.gross=self.convertPrices(d.gross)
                d.save()
        
    def updateEPS(self):
        pass
        
    def updateEstimationsDPS(self):
        set=EstimationDPSManager(self.mem, self.product)
        set.load_from_db()
        for d in set.arr:
            if self.dtinitial.year<=d.year and self.dtfinal.year>=d.year:
                d.estimation=self.convertPrices(d.estimation)
                d.save()
        
    def updateEstimationsEPS(self):
        set=EstimationEPSManager(self.mem, self.product)
        set.load_from_db()
        for d in set.arr:
            if self.dtinitial.year<=d.year and self.dtfinal.year>=d.year:
                d.estimation=self.convertPrices(d.estimation)
                d.save()
        
        
    def updateOperInvestments(self):
        """Transforms de number of shares and its price of the array of InvestmentOperation"""
        for inv in self.mem.data.investments.arr:
            if inv.product.id==self.product.id:
                for oi in inv.op.arr:
                    if self.dtinitial<=oi.datetime and self.dtfinal>=oi.datetime:
                        oi.shares=self.convertShares(oi.shares)
                        oi.valor_accion=self.convertPrices(oi.valor_accion)
                        oi.save(autocommit=False)

        
    def updateDividends(self):
        """Transforms de dpa of an array of dividends"""
        for inv in self.mem.data.investments.arr:
            if inv.product.id==self.product.id:
                dividends=DividendHomogeneusManager(self.mem, inv)
                dividends.load_from_db("select * from dividends where id_inversiones={0} order by fecha".format(inv.id ))  
                for d in dividends.arr:
                    if self.dtinitial<=d.datetime and self.dtfinal>=d.datetime:
                        d.dpa=self.convertPrices(d.dpa)
                    d.save()
        
    def type(self):
        """Función que devuelve si es un Split o contrasplit"""
        if self.initial>self.final:
            return "Contrasplit"
        else:
            return "Split"
            
    def makeSplit(self):
        """All calculates to make the split"""        
        self.updateDPS()
        self.updateEstimationsDPS()
        self.updateEstimationsEPS()
        self.updateOperInvestments()
        self.updateDividends()
        self.updateQuotes()
        self.mem.con.commit()



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

## Product type class
class ProductType(Object_With_IdName):
    def __init__(self, *args):
        Object_With_IdName.__init__(self, *args)

## Set of product types
class ProductTypeManager(ObjectManager_With_IdName_Selectable):
    def __init__(self, mem):
        ObjectManager_With_IdName_Selectable.__init__(self)
        self.mem=mem

    def load_all(self):
        self.append(ProductType(eProductType.Share.value,QApplication.translate("Mem","Shares")))
        self.append(ProductType(eProductType.Fund.value,QApplication.translate("Mem","Funds")))
        self.append(ProductType(eProductType.Index.value,QApplication.translate("Mem","Indexes")))
        self.append(ProductType(eProductType.ETF.value,QApplication.translate("Mem","ETF")))
        self.append(ProductType(eProductType.Warrant.value,QApplication.translate("Mem","Warrants")))
        self.append(ProductType(eProductType.Currency.value,QApplication.translate("Mem","Currencies")))
        self.append(ProductType(eProductType.PublicBond.value,QApplication.translate("Mem","Public Bond")))
        self.append(ProductType(eProductType.PensionPlan.value,QApplication.translate("Mem","Pension plans")))
        self.append(ProductType(eProductType.PrivateBond.value,QApplication.translate("Mem","Private Bond")))
        self.append(ProductType(eProductType.Deposit.value,QApplication.translate("Mem","Deposit")))
        self.append(ProductType(eProductType.Account.value,QApplication.translate("Mem","Accounts")))
        self.append(ProductType(eProductType.CFD.value,QApplication.translate("Mem","CFD")))
        self.append(ProductType(eProductType.Future.value,QApplication.translate("Mem","Futures")))

    def investment_types(self):
        """Returns a ProductTypeManager without Indexes and Accounts"""
        r=ProductTypeManager(self.mem)
        for t in self.arr:
            if t.id not in (eProductType.Index, eProductType.Account):
                r.append(t)
        return r

    def with_operation_commissions_types(self):
        """Returns a ProductTypeManager with types which product operations  has commissions"""
        r=ProductTypeManager(self.mem)
        for t in self.arr:
            if t.id not in (eProductType.Fund, eProductType.Index, eProductType.PensionPlan, eProductType.Deposit, eProductType.Account):
                r.append(t)
        return r
    
            
class Maintenance:
    """Funciones de mantenimiento y ayuda a la programación y depuración"""
    def __init__(self, mem):
        self.mem=mem
        
    def regenera_todas_opercuentasdeoperinversiones(self):
         
        for inv in self.mem.data.investments.arr:
            inv.actualizar_cuentasoperaciones_asociadas()
        self.mem.con.commit()        
        
        
    def show_investments_status(self, date):
        """Shows investments status in a date"""
        datet=dtaware(date, time(22, 00), self.mem.localzone_name)
        sumbalance=0
        print ("{0:<40s} {1:>15s} {2:>15s} {3:>15s}".format("Investments at {0}".format(date), "Shares", "Price", "Balance"))
        for inv in self.mem.data.investments.arr:
            balance=inv.balance(date)
            sumbalance=sumbalance+balance
            acciones=inv.shares(date)
            price=Quote(self.mem).init__from_query(inv.product, datet)
            if acciones!=0:
                print ("{0:<40s} {1:>15f} {2:>15s} {3:>15s}".format(inv.name, acciones, self.mem.localcurrency.string(price.quote),  self.mem.localcurrency.string(balance)))
        print ("{0:>40s} {1:>15s} {2:>15s} {3:>15s}".format("Total balance at {0}".format(date), "","", self.mem.localcurrency.string(sumbalance)))

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
            
## Class to manage datetime timezone and its methods
class Zone:
    ## Constructor with the following attributes combination
    ## 1. Zone(mem). Create a Zone with all attributes set to None, except mem
    ## 2. Zone(mem, id, name, country). Create account passing all attributes
    ## @param mem MemXulpymoney object
    ## @param id Integer that represents the Zone Id
    ## @param name Zone Name
    ## @param country Country object asociated to the timezone
    def __init__(self, *args):
        def init__create(id, name, country):
            self.id=id
            self.name=name
            self.country=country
            return self
        self.mem=args[0]
        if len(args)==1:
            init__create(None, None, None)
        if len(args)==4:
            init__create(args[1], args[2], args[3])

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
