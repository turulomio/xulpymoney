import datetime
from libxulpymoney import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Ui_frmEstimationsAdd import *

class frmEstimationsAdd(QDialog, Ui_frmEstimationsAdd):
    def __init__(self, cfg,  product,  type, parent=None):
        """type="dps or "eps" """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cfg=cfg
        self.type=type
        self.product=product
        self.lbl.setText(self.product.name)
        self.txtYear.setText(str(datetime.date.today().year))
        self.txtDPA.selectAll()

    def on_cmd_released(self):
        if self.type=="dps":
            d=EstimationDPS(self.cfg).init__from_db(self.product, int(self.txtYear.text()) )##Lo carga si existe de la base de datos
        else:
            d=EstimationEPS(self.cfg).init__from_db(self.product, int(self.txtYear.text()) )##Lo carga si existe de la base de datos

        d.estimation=self.txtDPA.decimal()
        d.manual=True
        d.source="Internet"
        d.date_estimation=datetime.date.today()
        d.save()
        self.cfg.conms.commit()      
        if self.type=="dps":
            self.product.estimations_dps.load_from_db()
        else:
            self.product.estimations_eps.load_from_db()
            
        self.accept()
