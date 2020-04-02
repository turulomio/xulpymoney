from PyQt5.QtWidgets import QWidget
from logging import debug
from xulpymoney.objects.investmentoperation import InvestmentOperationHistoricalHeterogeneusManager, InvestmentOperationCurrentHeterogeneusManager
from xulpymoney.libxulpymoneytypes import eConcept, eProductType
from xulpymoney.objects.accountoperation import AccountOperationManagerHeterogeneus
from xulpymoney.ui.Ui_wdgDerivativesReport import Ui_wdgDerivativesReport

class wdgDerivativesReport(QWidget, Ui_wdgDerivativesReport):
    def __init__(self, mem,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        
        adjustments=AccountOperationManagerHeterogeneus(self.mem)
        adjustments.load_from_db(self.mem.con.mogrify("select * from opercuentas where id_conceptos in (%s)", (eConcept.DerivativesAdjustment, )))
        guarantees=AccountOperationManagerHeterogeneus(self.mem)
        guarantees.load_from_db(self.mem.con.mogrify("select * from opercuentas where id_conceptos in (%s)", (eConcept.DerivativesGuarantee, )))
        commissions=AccountOperationManagerHeterogeneus(self.mem)
        commissions.load_from_db(self.mem.con.mogrify("select * from opercuentas where id_conceptos in (%s)", (eConcept.DerivativesCommission, )))
        rollover=AccountOperationManagerHeterogeneus(self.mem)
        rollover.load_from_db(self.mem.con.mogrify("select * from opercuentas where id_conceptos in (%s)", (eConcept.RolloverPaid, )))
        iohhm=self.InvestmentOperationHistoricalHeterogeneusManager_derivatives()
        iochm=self.InvestmentOperationCurrentHeterogeneusManager_derivatives()
        s=""
        s=s+"Total ajustes {}\n".format(adjustments.balance())
        s=s+"Total garantías: {}\n".format(guarantees.balance())
        s=s+"Total comisiones: {}\n".format(commissions.balance())
        s=s+"Total operaciones históricas: {}\n".format(iohhm.consolidado_bruto())
        s=s+"Total operaciones actuales: {}\n".format(iochm.pendiente())
        s=s+"Total rollover pagado: {}\n".format(rollover.balance())
        s=s+"Comisiones actuales e históricas: {} + {} = {}\n".format(iochm.commissions(), iohhm.commissions(), iohhm.commissions()+iochm.commissions())
        s=s+"Resultado=OpHist+OpActu-Comisiones-Rollover= {} + {} + {} + {} = {}".format(iohhm.consolidado_bruto(), iochm.pendiente(), commissions.balance(), rollover.balance(), iohhm.consolidado_bruto()+iochm.pendiente()+commissions.balance()+rollover.balance())
        self.textBrowser.setText(s)
        self.wdgIOHSLong.blockSignals(True)
        self.wdgIOHSLong.setManager(self.mem, iohhm, "wdgDerivativesReport", "wdgIOHSLong")
        self.wdgIOHSLong.setSelectedString(self.mem.settingsdb.value("strategyLongShort/historicalLong", ""))
        self.wdgIOHSLong.blockSignals(False)
        
    def on_wdgIOHSLong_itemChanged(self):
        self.mem.settingsdb.setValue("strategyLongShort/historicalLong", self.wdgIOHSLong.getSelectedString())
        debug("itemCheckStatusChanged {}".format(self.wdgIOHSLong.getSelectedString()))

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
