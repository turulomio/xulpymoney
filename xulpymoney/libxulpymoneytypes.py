from PyQt5.QtWidgets import QApplication
from enum import IntEnum
        
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
class HistoricalChartAdjusts:
    NoAdjusts=0
    Splits=1
    Dividends=2#Dividends with splits.        
    
class OHCLDuration:
    Day=1
    Week=2
    Month=3
    Year=4

    @classmethod
    def qcombobox(self, combo, selected_ohclduration):
        combo.addItem(QApplication.translate("Core", "Day"), 1)
        combo.addItem(QApplication.translate("Core", "Week"), 2)
        combo.addItem(QApplication.translate("Core", "Month"), 3)
        combo.addItem(QApplication.translate("Core", "Year"), 4)
        
        combo.setCurrentIndex(combo.findData(selected_ohclduration))
