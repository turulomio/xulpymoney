
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
