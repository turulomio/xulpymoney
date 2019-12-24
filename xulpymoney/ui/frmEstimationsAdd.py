import datetime
from xulpymoney.objects.estimation import EstimationDPS, EstimationEPS
from PyQt5.QtWidgets import QDialog
from xulpymoney.ui.Ui_frmEstimationsAdd import Ui_frmEstimationsAdd

class frmEstimationsAdd(QDialog, Ui_frmEstimationsAdd):
    def __init__(self, mem,  product,  type, parent=None):
        """type="dps or "eps" """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        self.type=type
        self.product=product
        self.lbl.setText(self.product.name)
        self.txtYear.setText(str(datetime.date.today().year))
        self.txtDPA.selectAll()
        if self.type=="dps":
            self.setWindowTitle(self.tr("New dividend per share estimation"))
            self.lblEstimation.setText(self.tr("Add a dividend per share estimation"))
            self.cmd.setText(self.tr("Save a dividend per share estimation"))
        else:
            self.setWindowTitle(self.tr("New earnings per share estimation"))
            self.lblEstimation.setText(self.tr("Add a earning per share estimation"))
            self.cmd.setText(self.tr("Save a earning per share estimation"))

    def on_cmd_released(self):
        if self.type=="dps":
            d=EstimationDPS(self.mem).init__from_db(self.product, int(self.txtYear.text()) )##Lo carga si existe de la base de datos
        else:
            d=EstimationEPS(self.mem).init__from_db(self.product, int(self.txtYear.text()) )##Lo carga si existe de la base de datos

        d.estimation=self.txtDPA.decimal()
        d.manual=True
        d.source="Internet"
        d.date_estimation=datetime.date.today()
        d.save()
        self.mem.con.commit()      
        if self.type=="dps":
            self.product.estimations_dps.load_from_db()
        else:
            self.product.estimations_eps.load_from_db()
            
        self.accept()
