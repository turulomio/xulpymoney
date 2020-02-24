from PyQt5.QtCore import QObject
from xulpymoney.libmanagers import ObjectManager_With_IdName_Selectable
from xulpymoney.libxulpymoneytypes import eOperationType


class OperationType:
    def __init__(self):
        self.id=None
        self.name=None
        
    def init__create(self, name,  id=None):
        self.id=id
        self.name=name
        return self


class OperationTypeManager(ObjectManager_With_IdName_Selectable, QObject):
    def __init__(self, mem):
        ObjectManager_With_IdName_Selectable.__init__(self)
        QObject.__init__(self)
        self.mem=mem     

    def load(self):
        self.append(OperationType().init__create( self.tr("Expense"),  eOperationType.Expense))
        self.append(OperationType().init__create( self.tr("Income"), eOperationType.Income))
        self.append(OperationType().init__create( self.tr("Transfer"), eOperationType.Transfer))
        self.append(OperationType().init__create( self.tr("Purchase of shares"), eOperationType.SharesPurchase))
        self.append(OperationType().init__create( self.tr("Sale of shares"), eOperationType.SharesSale))
        self.append(OperationType().init__create( self.tr("Added of shares"), eOperationType.SharesAdd))
        self.append(OperationType().init__create( self.tr("Credit card billing"), eOperationType.CreditCardBilling))
        self.append(OperationType().init__create( self.tr("Transfer of funds"), eOperationType.TransferFunds)) #Se contabilizan como ganancia
        self.append(OperationType().init__create( self.tr("Transfer of shares. Origin"), eOperationType.TransferSharesOrigin)) #No se contabiliza
        self.append(OperationType().init__create( self.tr("Transfer of shares. Destiny"), eOperationType.TransferSharesDestiny)) #No se contabiliza     
        self.append(OperationType().init__create( self.tr("HL investment guarantee"), eOperationType.DerivativeManagement)) #No se contabiliza     


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
