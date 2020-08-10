from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QAbstractItemView
from decimal import Decimal
from xulpymoney.libmanagers import ObjectManager
from xulpymoney.libxulpymoneytypes import eQColor
from xulpymoney.objects.investment import InvestmentManager
from xulpymoney.objects.investmentoperation import InvestmentOperationCurrentHeterogeneusManager
from xulpymoney.objects.order import OrderManager

class ProductRangeInvestRecomendation:
    None_=0
    All=1
    ThreeSMA=2
    SMA100=3

class ProductRange(QObject):
    def __init__(self, mem=None, id=None,  product=None,  value=None, percentage_down=None,  percentage_up=None, decimals=2):
        QObject.__init__(self)
        self.mem=mem
        self.id=id
        self.product=product
        self.value=value
        self.percentage_down=percentage_down
        self.percentage_up=percentage_up
        self.decimals=decimals
        self.recomendation_invest=False
        self.recomendation_reinvest=False
        
    def __repr__(self):
        return "({}, {}]".format(
            round(self.range_lowest_value(),  self.decimals), 
            round(self.range_highest_value(), self.decimals), 
        )
    
    ## Returns the value rounded to the number of decimals
    def value_rounded(self):
        return round(self.value, self.decimals)
        
    ## Return th value of the range highest value.. Points + percentage/2
    def range_highest_value(self):
        points_to_next_high= self.value/(1-self.percentage_down.value)-self.value
        return self.value+points_to_next_high/2

    ## Return th value of the range highest value.. Points + percentage/2
    def range_lowest_value(self):
        points_to_next_low=self.value-self.value*(1-self.percentage_down.value)
        return self.value-points_to_next_low/2
        
    ## @return Boolean if it's inside the range
    def isInside(self, value):
        if value<self.range_highest_value() and value>=self.range_lowest_value():
            return True
        else:
            return False
        
    ## Search for investments in self.mem.data and 
    def getInvestmentsInside(self):
        r=InvestmentManager(self.mem)
        for o in self.mem.data.investments.InvestmentManager_with_investments_with_the_same_product(self.product).arr:
            for op in o.op_actual.arr:
                if self.isInside(op.valor_accion)==True:
                    r.append(o)
        return r        

    ## Search for investments in self.mem.data and 
    def getInvestmentsOperationsInside(self):
        r=InvestmentOperationCurrentHeterogeneusManager(self.mem)
        for o in self.mem.data.investments.InvestmentManager_with_investments_with_the_same_product(self.product).arr:
            for op in o.op_actual.arr:
                if self.isInside(op.valor_accion)==True:
                    r.append(op)
        return r
        
    ## Search for orders in self.mem.data and 
    def getOrdersInside(self): 
        orders=OrderManager(self.mem).init__from_db("""
            SELECT * 
            FROM 
                ORDERS
            WHERE
                EXPIRATION>=NOW()::DATE AND
                EXECUTED IS NULL
            ORDER BY DATE
       """)
        r=OrderManager(self.mem)
        for o in orders.arr:
            if o.investment.product==self.product and self.isInside(o.price)==True:
                r.append(o)
        return r
      

class ProductRangeManager(ObjectManager, QObject):
    def __init__(self, mem, product, percentage_down, percentage_up, decimals=2):
        ObjectManager.__init__(self)
        QObject.__init__(self)
        self.mem=mem
        self.product=product
        self.product.needStatus(2)
        self.percentage_down=percentage_down
        self.percentage_up=percentage_up
        self.decimals=decimals
        
        # Create ranges
        inv=self.mem.data.investments.Investment_merging_current_operations_with_same_product(self.product)
        if inv.op_actual.length()>0: #Investment with shares
            range_highest=self.product.highest_investment_operation_price()*Decimal(1+self.percentage_down.value*10)#5 times up value
            range_lowest=self.product.lowest_investment_operation_price()*Decimal(1-self.percentage_down.value*10)#5 times down value
        else: # No investment jet and shows ranges from product current price
            range_highest=self.product.result.basic.last.quote*Decimal(1+self.percentage_down.value*10)#5 times up value
            range_lowest=self.product.result.basic.last.quote*Decimal(1-self.percentage_down.value*10)#5 times down value

        if range_lowest<Decimal(0.001):#To avoid infinity loop
            range_lowest=Decimal(0.001)



        self.highest_range_value=10000000
        current_value=self.highest_range_value
        i=0
        while current_value>range_lowest:
            if current_value>=range_lowest and current_value<=range_highest:
                self.append(ProductRange(self.mem, i, self.product, current_value, percentage_down, percentage_up))
            current_value=current_value*(1-percentage_down.value)
            i=i+1

    ## @return LIst of range values of the manager
    def list_of_range_values(self):
        return self.list_of("value")

    ## Set investment recomendations to all ProductRange objects in array 
    def setInvestRecomendation(self, method, method1_smas=[10, 50, 200]):
        if method==ProductRangeInvestRecomendation. None_:
            for o in self.arr:
                o.recomendation_invest=False
        elif method==ProductRangeInvestRecomendation.All:
            for o in self.arr:
                o.recomendation_invest=True
        elif method==ProductRangeInvestRecomendation.ThreeSMA:      
            dvm=self.product.result.ohclDaily.DatetimeValueManager("close")
            dvm_smas=[]
            for sma in method1_smas:
                dvm_smas.append(dvm.sma(sma))
            
            for o in self.arr:
                number_sma_over_price=len(self.product.result.ohclDaily.list_of_sma_over_price(self.mem.localzone_now(), o.value, method1_smas, dvm_smas,  "close"))
                if number_sma_over_price==3 and o.id % 4==0:
                    o.recomendation_invest=True
                elif number_sma_over_price==2 and o.id %2==0:
                    o.recomendation_invest=True
                elif number_sma_over_price<=1:
                    o.recomendation_invest=True
        elif method==ProductRangeInvestRecomendation.SMA100:           
            dvm=self.product.result.ohclDaily.DatetimeValueManager("close")
            dvm_smas=[]
            for sma in [100, ]:
                dvm_smas.append(dvm.sma(sma))
            
            for o in self.arr:
                number_sma_over_price=len(self.product.result.ohclDaily.list_of_sma_over_price(self.mem.localzone_now(), o.value, [100, ], dvm_smas,  "close"))
                if number_sma_over_price==0:
                    o.recomendation_invest=True
                elif number_sma_over_price==1 and o.id % 4==0:
                    o.recomendation_invest=True
                else: #number_sma_over_price=1 and o.id%4!=0
                    o.recomendation_invest=False

            
            
    def mqtw(self, wdg):
        data=[]
        for i, o in enumerate(self.arr):
            data.append([
                o.value, 
                o.recomendation_invest, 
                o.getInvestmentsOperationsInside().string_with_names(), 
                o.getOrdersInside().string_with_names(), 
                o, 
            ])
        wdg.setDataWithObjects(
            [self.tr("Center"), self.tr("Invest"), self.tr("Product operations"), self.tr("Product orders"),
            ], 
            None, 
            data,  
            decimals=[self.decimals, 0, 6, 6, 0, 0, 0], 
            zonename=self.mem.localzone_name, 
            additional=self.mqtw_additional
        )   
        
    def mqtw_additional(self, wdg):
        for i, o in enumerate(wdg.objects()):
            if o.isInside(o.product.result.basic.last.quote)==True:
                wdg.table.item(i, 0).setBackground(eQColor.Green)
                wdg.table.scrollToItem(wdg.table.item(i, 0), QAbstractItemView.PositionAtCenter)
                wdg.table.selectRow(i)
                wdg.table.clearSelection()
