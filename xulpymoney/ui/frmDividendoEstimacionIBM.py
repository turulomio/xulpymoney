import datetime
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
        d=DividendoEstimacion(self.cfg).init__from_db(self.investment, int(self.txtYear.text()) )##Lo carga si existe de la base de datos
        d.dpa=self.txtDPA.text()
        d.manual=True
        d.fuente="Internet"
        d.fechaestimacion=datetime.date.today()
        d.save()
        self.cfg.conmq.commit()      
#######        self.investment.estimaciones[d.txtYear.text()].dpa=d.txtDPA.decimal()
        self.accept()
