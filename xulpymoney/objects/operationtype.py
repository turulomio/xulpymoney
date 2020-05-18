from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QApplication
from xulpymoney.libmanagers import ObjectManager_With_IdName_Selectable, Object_With_IdName
from xulpymoney.libxulpymoneytypes import eOperationType

class OperationType(Object_With_IdName, QObject):
    def __init__(self, mem=None,  id=None, name=None):
        Object_With_IdName.__init__(self, id, name)
        QObject.__init__(self)
        self.mem=mem

    def fullName(self):
        return self.mem.trHS(self.name)

class OperationTypeManager(ObjectManager_With_IdName_Selectable, QObject):
    def __init__(self, mem):
        ObjectManager_With_IdName_Selectable.__init__(self)
        QObject.__init__(self)
        self.mem=mem     

def OperationTypeManager_hardcoded(mem):
    r=OperationTypeManager(mem)
    r.append(OperationType(mem, eOperationType.Expense,QApplication.translate("Mem", "Expense")))
    r.append(OperationType(mem, eOperationType.Income,QApplication.translate("Mem", "Income")))
    r.append(OperationType(mem, eOperationType.Transfer,QApplication.translate("Mem", "Transfer")))
    r.append(OperationType(mem, eOperationType.SharesPurchase,QApplication.translate("Mem", "Purchase of shares")))
    r.append(OperationType(mem, eOperationType.SharesSale,QApplication.translate("Mem", "Sale of shares")))
    r.append(OperationType(mem, eOperationType.SharesAdd,QApplication.translate("Mem", "Added of shares")))
    r.append(OperationType(mem, eOperationType.CreditCardBilling,QApplication.translate("Mem", "Credit card billing")))
    r.append(OperationType(mem, eOperationType.TransferFunds,QApplication.translate("Mem", "Transfer of funds"))) #Se contabilizan como ganancia
    r.append(OperationType(mem, eOperationType.TransferSharesOrigin,QApplication.translate("Mem", "Transfer of shares. Origin"))) #No se contabiliza
    r.append(OperationType(mem, eOperationType.TransferSharesDestiny,QApplication.translate("Mem", "Transfer of shares. Destiny"))) #No se contabiliza     
    r.append(OperationType(mem, eOperationType.DerivativeManagement,QApplication.translate("Mem", "HL investment guarantee"))) #No se contabiliza     
    return r

def OperationTypeManager_from_list_ids(mem, list_ids):
    r=OperationTypeManager(mem)
    for id in list_ids:
        r.append(mem.tiposoperaciones.find_by_id(id))
    return r
    
def OperationTypeManager_for_InvestmentOperations(mem):
    return OperationTypeManager_from_list_ids( mem,  (eOperationType.SharesPurchase, eOperationType.SharesSale, eOperationType.SharesAdd, eOperationType.TransferFunds))
