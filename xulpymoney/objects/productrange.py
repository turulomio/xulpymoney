from PyQt5.QtCore import QObject
from decimal import Decimal
from xulpymoney.libmanagers import ObjectManager
from xulpymoney.libxulpymoneytypes import eQColor
from xulpymoney.objects.investment import InvestmentManager
from xulpymoney.objects.order import OrderManager

class ProductRange(QObject):
    def __init__(self, mem=None, product=None,  value=None, percentage_down=None,  percentage_up=None, decimals=2):
        QObject.__init__(self)
        self.mem=mem
        self.product=product
        self.value=value
        self.percentage_down=percentage_down
        self.percentage_up=percentage_up
        self.decimals=decimals
        self.recomendation_invest=False
        self.recomendation_reinvest=False
        
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
    def getInvestments(self):
        r=InvestmentManager(self.mem)
        for o in self.mem.data.investments.InvestmentManager_with_investments_with_the_same_product(self.product).arr:
            if o.op_actual.length()>0 and self.isInside(o.op_actual.first().valor_accion)==True:
                r.append(o)
        return r
        
    ## Search for orders in self.mem.data and 
    def getInvestmentsFromOrders(self): 
        orders=OrderManager(self.mem).init__from_db("""
            SELECT * 
            FROM 
                ORDERS
            WHERE
                EXPIRATION>=NOW()::DATE AND
                EXECUTED IS NULL
            ORDER BY DATE
       """)
        r=InvestmentManager(self.mem)
        for o in orders.arr:
            if o.investment.product==self.product and self.isInside(o.price)==True:
                r.append(o.investment)
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
        product_highest=self.product.result.ohclYearly.highest().high
        product_lowest=self.product.result.ohclYearly.lowest().low
        range_highest=product_highest*2#100%
        range_lowest=product_lowest*Decimal(0.1)#90%
        current_value=10000000
        while current_value>range_lowest:
            if current_value>=range_lowest and current_value<=range_highest:
                self.append(ProductRange(self.mem, self.product, current_value, percentage_down, percentage_up))
            current_value=current_value*(1-percentage_down.value)
            
            
    def mqtw(self, wdg):
        data=[]
        for i, o in enumerate(self.arr):
            data.append([
                o.value, 
                o.getInvestments().string_with_names(),                 
                o.getInvestmentsFromOrders().string_with_names(), 
                o, 
            ])
        wdg.setDataWithObjects(
            [self.tr("Value"), self.tr("Investments"), self.tr("Orders"),
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
#        type=eMoneyCurrency.User
#        for i, inv in enumerate(wdg.objects()):
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
        
        
        
