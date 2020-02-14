from PyQt5.QtCore import QObject
from  xulpymoney.libmanagers import Object_With_IdName, ObjectManager_With_IdName_Selectable
from xulpymoney.libxulpymoneytypes import eProductType
## Product type class
class ProductType(Object_With_IdName):
    def __init__(self, *args):
        Object_With_IdName.__init__(self, *args)

## Set of product types
class ProductTypeManager(ObjectManager_With_IdName_Selectable, QObject):
    def __init__(self, mem):
        ObjectManager_With_IdName_Selectable.__init__(self)
        QObject.__init__(self)
        self.mem=mem

    def load_all(self):
        self.append(ProductType(eProductType.Share.value,self.tr("Shares")))
        self.append(ProductType(eProductType.Fund.value,self.tr("Funds")))
        self.append(ProductType(eProductType.Index.value,self.tr("Indexes")))
        self.append(ProductType(eProductType.ETF.value,self.tr("ETF")))
        self.append(ProductType(eProductType.Warrant.value,self.tr("Warrants")))
        self.append(ProductType(eProductType.Currency.value,self.tr("Currencies")))
        self.append(ProductType(eProductType.PublicBond.value,self.tr("Public Bond")))
        self.append(ProductType(eProductType.PensionPlan.value,self.tr("Pension plans")))
        self.append(ProductType(eProductType.PrivateBond.value,self.tr("Private Bond")))
        self.append(ProductType(eProductType.Deposit.value,self.tr("Deposit")))
        self.append(ProductType(eProductType.Account.value,self.tr("Accounts")))
        self.append(ProductType(eProductType.CFD.value,self.tr("CFD")))
        self.append(ProductType(eProductType.Future.value,self.tr("Futures")))

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
