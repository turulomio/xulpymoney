## @namespace xulpymoney.libxulpymoneytypes
## @brief Package with all xulpymoney types.
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication
from enum import IntEnum

## Class with used QColors in app
class eQColor:
    Red=QColor(255, 148, 148)
    Green=QColor(148, 255, 148)
        
class eProductType(IntEnum):
    """
        IntEnum permite comparar 1 to eProductType.Share
    """
    Share=1
    Fund=2
    Index=3
    ETF=4
    Warrant=5
    Currency=6
    PublicBond=7
    PensionPlan=8
    PrivateBond=9
    Deposit=10
    Account=11
    CFD=12
    
## Operation tipes
class eOperationType:
    Expense=1
    Income=2
    Transfer=3
    SharesPurchase=4
    SharesSale=5
    SharesAdd=6
    CreditCardBilling=7
    TransferFunds=8
    TransferSharesOrigin=9
    TransferSharesDestiny=10
    HlContract=11
    
class eTickerPosition(IntEnum):
    """It's the number to access to a python list,  not to postgresql. In postgres it will be +1"""
    Yahoo=0
    Morningstar=1
    Google=2
    QueFondos=3
    
    def postgresql(etickerposition):
        return etickerposition.value+1
        
    ## Returns the number of atributes
    def length():
        return len(eTickerPosition.__dict__)


class eComment:
    InvestmentOperation=10000
    Dividend=10004
    HlContract=10007


## System concepts tipified
class eConcept:
    OpenAccount=1
    TransferOrigin=4
    TransferDestiny=5
    TaxesReturn=6
    BuyShares=29
    SellShares=35
    TaxesPayment=37
    BankCommissions=38
    Dividends=39
    CreditCardBilling=40
    AddShares=43
    AssistancePremium=50
    CommissionCustody=59
    DividendsSaleRights=62
    BondsCouponRunPayment=63
    BondsCouponRunIncome=65
    BondsCoupon=66
    CreditCardRefund=67
    HlAdjustmentIincome=68
    HlAdjustmentExpense=69
    HlGuaranteePaid=70
    HlGuaranteeReturned=71
    HlCommission=72
    HlInterestPaid=73
    HlInterestReceived=74


## Sets if a Historical Chart must adjust splits or dividends with splits or do nothing
class eHistoricalChartAdjusts:
    ## Without splits nor dividens
    NoAdjusts=0
    ## WithSplits
    Splits=1
    ##With splits and dividends
    SplitsAndDividends=2#Dividends with splits.        
    
class eOHCLDuration:
    Day=1
    Week=2
    Month=3
    Year=4

    @classmethod
    def qcombobox(self, combo, selected_eOHCLDuration):
        combo.addItem(QApplication.translate("Core", "Day"), 1)
        combo.addItem(QApplication.translate("Core", "Week"), 2)
        combo.addItem(QApplication.translate("Core", "Month"), 3)
        combo.addItem(QApplication.translate("Core", "Year"), 4)
        combo.setCurrentIndex(combo.findData(selected_eOHCLDuration))

class eLeverageType:
    Variable=-1
    NotLeveraged=1
    X2=2
    X3=3
    X4=4
    X5=5
    X10=10
    
class eMoneyCurrency:
    Product=1
    Account=2
    User=3
