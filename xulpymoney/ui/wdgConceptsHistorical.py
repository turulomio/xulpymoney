from PyQt4.QtCore import *
from PyQt4.QtGui import *
from libxulpymoney import *
from Ui_wdgConceptsHistorical import *

class wdgConceptsHistorical(QWidget, Ui_wdgConceptsHistorical):
    def __init__(self, cfg, concepto,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.cfg=cfg
        self.concepto=concepto

        self.table.settings(None,  self.cfg)
        self.reload()

    def reload(self):
        cur=self.cfg.con.cursor()
        sql="select date_part('year',fecha) as year,  date_part('month',fecha) as month, sum(importe) as suma from opercuentastarjetas where id_conceptos={0} group by date_part('year',fecha), date_part('month',fecha) order by 1,2 ;".format(self.concepto.id)
        cur.execute(sql)
        if cur.rowcount!=0:
            arr=cur.fetchall()            
        cur.close()
        
        #Coloca filas y años
        firstyear=int(arr[0][0])
        rows=int(datetime.date.today().year-firstyear+1)
        self.table.setRowCount(rows)
        sum=[]#suma en array suma, en el que el año first es 0...
        for i in range(rows):
            sum.append(0)#Inicializa a 0 los sumadores
            self.table.setItem(i, 0, QTableWidgetItem("{0}".format(firstyear+i)))
        #Coloca en tabla 
        for a in arr:
            self.table.setItem(a[0]-firstyear, a[1],self.cfg.localcurrency.qtablewidgetitem(a[2])  )
            sum[int(a[0])-firstyear]=sum[int(a[0])-firstyear]+a[2]
        #Coloca en tabla los sumatorios
        for i,  s in enumerate(sum):
            self.table.setItem(i, 13,self.cfg.localcurrency.qtablewidgetitem(s) )
