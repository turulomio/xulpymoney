import datetime
from decimal import Decimal
from libxulpymoney import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Ui_frmDividendoEstimacionIBM import *

class frmDividendoEstimacionIBM(QDialog, Ui_frmDividendoEstimacionIBM):
    def __init__(self, cfg,  investment,  parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cfg=cfg
        self.investment=investment
        self.lbl.setText(self.investment.name)
        self.txtYear.setText(str(datetime.date.today().year))
        self.txtDPA.selectAll()
        

    def on_cmd_released(self):
        year=int(self.txtYear.text())
        dpa=Decimal(self.txtDPA.text())
        DividendoEstimacion(self.cfg).insertar(self.investment.id,  year, dpa)
        self.cfg.conmq.commit()      
        self.accept()
