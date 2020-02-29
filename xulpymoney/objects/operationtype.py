from PyQt5.QtCore import QObject
from xulpymoney.libmanagers import ObjectManager_With_IdName_Selectable, Object_With_IdName
from xulpymoney.libxulpymoneytypes import eOperationType

class OperationType(Object_With_IdName):
    def __init__(self, id=None, name=None):
        Object_With_IdName.__init__(self, id, name)

class OperationTypeManager(ObjectManager_With_IdName_Selectable, QObject):
    def __init__(self, mem):
        ObjectManager_With_IdName_Selectable.__init__(self)
        QObject.__init__(self)
        self.mem=mem     

def OperationTypeManager_hardcoded(mem):
    r=OperationTypeManager(mem)
    r.append(OperationType(eOperationType.Expense, r.tr("Expense")))
    r.append(OperationType(eOperationType.Income, r.tr("Income")))
    r.append(OperationType(eOperationType.Transfer, r.tr("Transfer")))
    r.append(OperationType(eOperationType.SharesPurchase, r.tr("Purchase of shares")))
    r.append(OperationType(eOperationType.SharesSale, r.tr("Sale of shares")))
    r.append(OperationType(eOperationType.SharesAdd, r.tr("Added of shares")))
    r.append(OperationType(eOperationType.CreditCardBilling, r.tr("Credit card billing")))
    r.append(OperationType(eOperationType.TransferFunds, r.tr("Transfer of funds"))) #Se contabilizan como ganancia
    r.append(OperationType(eOperationType.TransferSharesOrigin, r.tr("Transfer of shares. Origin"))) #No se contabiliza
    r.append(OperationType(eOperationType.TransferSharesDestiny, r.tr("Transfer of shares. Destiny"))) #No se contabiliza     
    r.append(OperationType(eOperationType.DerivativeManagement, r.tr("HL investment guarantee"))) #No se contabiliza     
    return r

def OperationTypeManager_from_list_ids(mem, list_ids):
    r=OperationTypeManager(mem)
    for id in list_ids:
        r.append(mem.tiposoperaciones.find_by_id(id))
    return r
    
def OperationTypeManager_for_InvestmentOperations(mem):
    return OperationTypeManager_from_list_ids( mem,  (eOperationType.SharesPurchase, eOperationType.SharesSale, eOperationType.SharesAdd, eOperationType.TransferFunds))
