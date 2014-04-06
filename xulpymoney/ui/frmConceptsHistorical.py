from PyQt4.QtCore import *
from PyQt4.QtGui import *
from libxulpymoney import *
from Ui_frmConceptsHistorical import *

class frmConceptsHistorical(QDialog, Ui_frmConceptsHistorical):
    def __init__(self, cfg, concepto,  parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cfg=cfg
        self.concepto=concepto

        self.table.settings("wdgConceptsHistorical",  self.cfg)
        self.reload()
    def reload(self):
        cur=self.cfg.con.cursor()
        sql="select date_part('year',fecha) as year,  date_part('month',fecha) as month, sum(importe) as suma from opercuentas where id_conceptos={0} group by date_part('year',fecha), date_part('month',fecha) order by 1,2 ;".format(self.concepto.id)
        cur.execute(sql)
        if cur.rowcount!=0:
            arr=cur.fetchall()            
        cur.close()
        
        #Coloca filas y años
        firstyear=int(arr[0][0])
        rows=int(datetime.date.today().year-firstyear+1)
        self.table.setRowCount(rows)
        for i in range(rows):
            self.table.setItem(i, 0, QTableWidgetItem("{0}".format(firstyear+i)))
            
        for a in arr:
            self.table.setItem(a[0]-firstyear, a[1], self.cfg.localcurrency.qtablewidgetitem(a[2]) )
