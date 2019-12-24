from xulpymoney.objects.dps import DPS
from PyQt5.QtWidgets import QDialog
from xulpymoney.ui.Ui_frmDPSAdd import Ui_frmDPSAdd

class frmDPSAdd(QDialog, Ui_frmDPSAdd):
    def __init__(self, mem,  product,   parent=None):
        """type="dps or "eps" """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        self.product=product
        self.dps=None
        self.lbl.setText(self.tr("New DPS"))

    def on_cmd_released(self):
        self.dps=DPS(self.mem, self.product).init__create(self.calendar.selectedDate().toPyDate(), self.txtGross.decimal(), self.calendarPay.selectedDate().toPyDate())
        self.dps.save()
        self.mem.con.commit()      
        self.product.dps.arr.append(self.dps)
        self.accept()
