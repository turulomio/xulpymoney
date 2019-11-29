from PyQt5.QtWidgets import QWidget
from xulpymoney.libxulpymoney import InvestmentOperationHistoricalHeterogeneusManager, InvestmentOperationCurrentHeterogeneusManager
from xulpymoney.libxulpymoneytypes import eConcept, eProductType
from xulpymoney.objects.accountoperation import AccountOperationManagerHeterogeneus
from xulpymoney.ui.Ui_wdgDerivativesReport import Ui_wdgDerivativesReport

class wdgDerivativesReport(QWidget, Ui_wdgDerivativesReport):
    def __init__(self, mem, investment, hlcontract=None,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        
        adjustments=AccountOperationManagerHeterogeneus(self.mem)
        adjustments.load_from_db(self.mem.con.mogrify("select * from opercuentas where id_conceptos in (%s,%s)", (eConcept.HlAdjustmentIincome, eConcept.HlAdjustmentExpense)))
        guarantees=AccountOperationManagerHeterogeneus(self.mem)
        guarantees.load_from_db(self.mem.con.mogrify("select * from opercuentas where id_conceptos in (%s,%s)", (eConcept.HlGuaranteePaid, eConcept.HlGuaranteeReturned)))
        comissions=AccountOperationManagerHeterogeneus(self.mem)
        comissions.load_from_db(self.mem.con.mogrify("select * from opercuentas where id_conceptos in (%s)", (eConcept.HlCommission, )))
        interest=AccountOperationManagerHeterogeneus(self.mem)
        interest.load_from_db(self.mem.con.mogrify("select * from opercuentas where id_conceptos in (%s,%s)", (eConcept.HlInterestPaid, eConcept.HlInterestReceived)))
        
        iohhm=self.InvestmentOperationHistoricalHeterogeneusManager_derivatives()
        iochm=self.InvestmentOperationCurrentHeterogeneusManager_derivatives()
        print("Total ajustes", adjustments.balance())
        print("Total garantías", guarantees.balance())
        print("Total comisiones", comissions.balance())
        print("Total intereses",  interest.balance())
        print("Total operaciones históricas", iohhm.consolidado_bruto())
        print("Total operaciones actuales", iochm.pendiente())
        
    def InvestmentOperationHistoricalHeterogeneusManager_derivatives(self):
        r=InvestmentOperationHistoricalHeterogeneusManager(self.mem)
        for o in self.mem.data.investments.arr:
            if o.product.type.id in (eProductType.CFD, eProductType.Future):
                o.needStatus(2)
                for op in o.op_historica.arr:
                    r.append(op)
        return r

    def InvestmentOperationCurrentHeterogeneusManager_derivatives(self):
        r=InvestmentOperationCurrentHeterogeneusManager(self.mem)
        for o in self.mem.data.investments.arr:
            if o.product.type.id in (eProductType.CFD, eProductType.Future):
                o.needStatus(2)
                for op in o.op_actual.arr:
                    r.append(op)
        return r
