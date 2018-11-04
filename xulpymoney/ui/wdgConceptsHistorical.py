import datetime
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMenu, QWidget, QHBoxLayout,  QTableWidgetItem
from xulpymoney.ui.myqtablewidget import myQTableWidget
from xulpymoney.libxulpymoney import AccountOperationManager
from xulpymoney.libxulpymoneyfunctions import qcenter, qmessagebox
from xulpymoney.ui.Ui_wdgConceptsHistorical import Ui_wdgConceptsHistorical

class wdgConceptsHistorical(QWidget, Ui_wdgConceptsHistorical):
    def __init__(self, mem, concepto,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        self.concepto=concepto

        self.month=None#Used to show popup with month or year report if is 0->Year, else->Month
        self.year=None
        self.firstyear=None
        self.table.settings(self.mem, "wdgConceptsHistorical")
        self.reload()

    def reload(self):
        cur=self.mem.con.cursor()
        #Junta opercuentas y opertarjetas y sobre esa subquery uni hace un group by
        sql="""
        select date_part('year',datetime) as year,  date_part('month',datetime) as month, sum(importe) as suma 
        from ( 
                    SELECT opercuentas.datetime, opercuentas.id_conceptos,  opercuentas.importe  FROM opercuentas where id_conceptos={0} 
                        UNION ALL 
                    SELECT opertarjetas.datetime, opertarjetas.id_conceptos, opertarjetas.importe FROM opertarjetas where id_conceptos={0}
                ) as uni 
        group by date_part('year',datetime), date_part('month',datetime) order by 1,2 ;
        """.format(self.concepto.id)
        cur.execute(sql)
        if cur.rowcount!=0:
            arr=cur.fetchall()            
        cur.close()
        self.table.applySettings()
        #Coloca filas y años
        self.firstyear=int(arr[0][0])
        rows=int(datetime.date.today().year-self.firstyear+1)
        self.table.setRowCount(rows+1)
        suma=[]#sumaa en array suma, en el que el año first es 0...
        for i in range(rows):
            suma.append(0)#Inicializa a 0 los sumadores
            self.table.setItem(i, 0, QTableWidgetItem("{0}".format(self.firstyear+i)))
        #Coloca en tabla 
        for a in arr:
            self.table.setItem(a[0]-self.firstyear, a[1],self.mem.localcurrency.qtablewidgetitem(a[2])  )
            suma[int(a[0])-self.firstyear]=suma[int(a[0])-self.firstyear]+a[2]
        #Coloca en tabla los sumaatorios
        for i,  s in enumerate(suma):
            self.table.setItem(i, 13,self.mem.localcurrency.qtablewidgetitem(s) )

        #Add years total
        self.table.setItem(rows, 0, qcenter(self.tr("Total")))
        self.table.setItem(rows, 13, self.mem.localcurrency.qtablewidgetitem(sum(suma)))

    @pyqtSlot() 
    def on_actionShowMonth_triggered(self):
        newtab = QWidget()
        horizontalLayout = QHBoxLayout(newtab)
        table = myQTableWidget(newtab)
        table.settings(self.mem, "wdgConceptsHistorical",  "tblShowMonth")
        set=AccountOperationManager(self.mem)
        set.load_from_db_with_creditcard("""
             select datetime, id_conceptos, id_tiposoperaciones, importe, comentario, id_cuentas , -1 as id_tarjetas 
             from opercuentas 
             where
                 id_conceptos={0} and 
                 date_part('year',datetime)={1} and 
                 date_part('month',datetime)={2} 
             union all 
             select datetime, id_conceptos, id_tiposoperaciones, importe, comentario, id_cuentas ,tarjetas.id_tarjetas as id_tarjetas 
             from opertarjetas, tarjetas 
             where 
                 opertarjetas.id_tarjetas=tarjetas.id_tarjetas and 
                 id_conceptos={0} and 
                 date_part('year',datetime)={1} and 
                 date_part('month',datetime)={2}""".format (self.concepto.id, self.year, self.month))
        set.myqtablewidget(table, True)
        horizontalLayout.addWidget(table)
        self.tab.addTab(newtab, self.tr("Report of {0} of {1}".format(self.table.horizontalHeaderItem(self.month).text(), self.year)))
        self.tab.setCurrentWidget(newtab)

    @pyqtSlot() 
    def on_actionShowYear_triggered(self):
        newtab = QWidget()
        horizontalLayout = QHBoxLayout(newtab)
        table = myQTableWidget(newtab)
        table.settings(self.mem, "wdgConceptsHistorical",  "tblShowYear")
        set=AccountOperationManager(self.mem)
        set.load_from_db_with_creditcard("select datetime, id_conceptos, id_tiposoperaciones, importe, comentario, id_cuentas , -1 as id_tarjetas from opercuentas where id_conceptos={0} and date_part('year',datetime)={1} union all select datetime, id_conceptos, id_tiposoperaciones, importe, comentario, id_cuentas ,tarjetas.id_tarjetas as id_tarjetas from opertarjetas,tarjetas where opertarjetas.id_tarjetas=tarjetas.id_tarjetas and id_conceptos={0} and date_part('year',datetime)={1}".format (self.concepto.id, self.year))
        set.sort()
        set.myqtablewidget(table, True)
        horizontalLayout.addWidget(table)
        self.tab.addTab(newtab, self.tr("Report of {0}".format(self.year)))
        self.tab.setCurrentWidget(newtab)

    def on_table_customContextMenuRequested(self,  pos):
        self.actionShowYear.setEnabled(False)
        self.actionShowMonth.setEnabled(False)
        if self.month!=None:
            if self.month==0 and self.year<=datetime.date.today().year:#Avoid total:
                self.actionShowYear.setEnabled(True)
            elif self.month>0:
                self.actionShowMonth.setEnabled(True)

        menu=QMenu()
        menu.addAction(self.actionShowYear)
        menu.addSeparator()
        menu.addAction(self.actionShowMonth)      
        menu.exec_(self.table.mapToGlobal(pos))

    def on_table_itemSelectionChanged(self):
        self.month=None
        self.year=None
        for i in self.table.selectedItems():#itera por cada item no row.
            if i.column()==0 or i.column()==13:
                self.month=0
            else:
                self.month=i.column()
            self.year=self.firstyear+i.row()
        print ("Selected year: {0}. Selected month: {1}.".format(self.year, self.month))

    def on_tab_tabCloseRequested(self, index):
        """Only removes dinamic tabs"""
        if index==0:
            qmessagebox(self.tr("You can't close this tab"))
        else:
            self.tab.removeTab(index)
