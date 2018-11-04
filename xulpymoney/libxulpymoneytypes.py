## @package libxulpymoneytypes
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
