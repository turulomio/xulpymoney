from PyQt5.QtWidgets import QWidget
from xulpymoney.libxulpymoney import InvestmentOperationHistoricalHeterogeneusManager, InvestmentOperationCurrentHeterogeneusManager
from xulpymoney.libxulpymoneytypes import eConcept, eProductType
from xulpymoney.objects.accountoperation import AccountOperationManagerHeterogeneus
from xulpymoney.ui.Ui_wdgDerivativesReport import Ui_wdgDerivativesReport

class wdgDerivativesReport(QWidget, Ui_wdgDerivativesReport):
    def __init__(self, mem,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        
        adjustments=AccountOperationManagerHeterogeneus(self.mem)
        adjustments.load_from_db(self.mem.con.mogrify("select * from opercuentas where id_conceptos in (%s,%s)", (eConcept.HlAdjustmentIincome, eConcept.HlAdjustmentExpense)))
        guarantees=AccountOperationManagerHeterogeneus(self.mem)
        guarantees.load_from_db(self.mem.con.mogrify("select * from opercuentas where id_conceptos in (%s,%s)", (eConcept.HlGuaranteePaid, eConcept.HlGuaranteeReturned)))
        commissions=AccountOperationManagerHeterogeneus(self.mem)
        commissions.load_from_db(self.mem.con.mogrify("select * from opercuentas where id_conceptos in (%s)", (eConcept.HlCommission, )))
        rollover=AccountOperationManagerHeterogeneus(self.mem)
        rollover.load_from_db(self.mem.con.mogrify("select * from opercuentas where id_conceptos in (%s)", (eConcept.RolloverPaid, )))
        interest=AccountOperationManagerHeterogeneus(self.mem)
        interest.load_from_db(self.mem.con.mogrify("select * from opercuentas where id_conceptos in (%s,%s)", (eConcept.HlInterestPaid, eConcept.HlInterestReceived)))
        iohhm=self.InvestmentOperationHistoricalHeterogeneusManager_derivatives()
        iochm=self.InvestmentOperationCurrentHeterogeneusManager_derivatives()
        s=""
        s=s+"Total ajustes {}\n".format(adjustments.balance())
        s=s+"Total garantías: {}\n".format(guarantees.balance())
        s=s+"Total comisiones: {}\n".format(commissions.balance())
        s=s+"Total intereses: {}\n".format( interest.balance())
        s=s+"Total operaciones históricas: {}\n".format(iohhm.consolidado_bruto())
        s=s+"Total operaciones actuales: {}\n".format(iochm.pendiente())
        s=s+"Total rollover pagado: {}\n".format(rollover.balance())
        s=s+"Comisiones actuales e históricas: {} + {} = {}\n".format(iochm.commissions(), iohhm.commissions(), iohhm.commissions()+iochm.commissions())
        s=s+"Resultado=OpHist+OpActu-Comisiones-Rollover= {} + {} + {} + {} = {}".format(iohhm.consolidado_bruto(), iochm.pendiente(), commissions.balance(), rollover.balance(), iohhm.consolidado_bruto()+iochm.pendiente()+commissions.balance()+rollover.balance())
        self.textBrowser.setText(s)
        
        self.wdgIOHSLong.setManager(self.mem, iohhm, "wdgIOHSLong")
        self.wdgIOHSLong.setCheckedPositions([46, 47])
        print(self.wdgIOHSLong.getCheckedPositions())


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
