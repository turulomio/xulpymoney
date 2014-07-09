from PyQt4.QtCore import *
from PyQt4.QtGui import *
from libxulpymoney import *
from Ui_wdgConceptsHistorical import *

class wdgConceptsHistorical(QWidget, Ui_wdgConceptsHistorical):
    def __init__(self, mem, concepto,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        self.concepto=concepto
        self.mem.data.load_inactives()

        self.month=None#Used to show popup with month or year report if is 0->Year, else->Month
        self.year=None
        self.firstyear=None
        self.table.settings("wdgConceptsHistorical",  self.mem)
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
        
#        sql="select date_part('year',datetime) as year,  date_part('month',datetime) as month, sum(importe) as suma from opercuentastarjetas where id_conceptos={0} group by date_part('year',datetime), date_part('month',datetime) order by 1,2 ;".format(self.concepto.id)
        cur.execute(sql)
        if cur.rowcount!=0:
            arr=cur.fetchall()            
        cur.close()
        
        #Coloca filas y años
        self.firstyear=int(arr[0][0])
        rows=int(datetime.date.today().year-self.firstyear+1)
        self.table.setRowCount(rows)
        sum=[]#suma en array suma, en el que el año first es 0...
        for i in range(rows):
            sum.append(0)#Inicializa a 0 los sumadores
            self.table.setItem(i, 0, QTableWidgetItem("{0}".format(self.firstyear+i)))
        #Coloca en tabla 
        for a in arr:
            self.table.setItem(a[0]-self.firstyear, a[1],self.mem.localcurrency.qtablewidgetitem(a[2])  )
            sum[int(a[0])-self.firstyear]=sum[int(a[0])-self.firstyear]+a[2]
        #Coloca en tabla los sumatorios
        for i,  s in enumerate(sum):
            self.table.setItem(i, 13,self.mem.localcurrency.qtablewidgetitem(s) )

    
    @QtCore.pyqtSlot() 
    def on_actionShowMonth_activated(self):
        newtab = QWidget()
        horizontalLayout = QHBoxLayout(newtab)
        table = myQTableWidget(newtab)
        set=SetAccountOperations(self.mem)
        set.load_from_db_with_creditcard("select datetime, id_conceptos, id_tiposoperaciones, importe, comentario, id_cuentas , -1 as id_tarjetas from opercuentas where id_conceptos={0} and date_part('year',datetime)={1} and date_part('month',datetime)={2} union all select datetime, id_conceptos, id_tiposoperaciones, importe, comentario, id_cuentas ,tarjetas.id_tarjetas as id_tarjetas from opertarjetas,tarjetas where opertarjetas.id_tarjetas=tarjetas.id_tarjetas and id_conceptos={0} and date_part('year',datetime)={1} and date_part('month',datetime)={2}".format (self.concepto.id, self.year, self.month))
        set.sort()
        set.myqtablewidget(table, None, True)
        horizontalLayout.addWidget(table)
        self.tab.addTab(newtab, self.trUtf8("Report of {0} of {1}".format(self.table.horizontalHeaderItem(self.month).text(), self.year)))
        self.tab.setCurrentWidget(newtab)

    
    @QtCore.pyqtSlot() 
    def on_actionShowYear_activated(self):
        newtab = QWidget()
        horizontalLayout = QHBoxLayout(newtab)
        table = myQTableWidget(newtab)
        set=SetAccountOperations(self.mem)
        set.load_from_db_with_creditcard("select datetime, id_conceptos, id_tiposoperaciones, importe, comentario, id_cuentas , -1 as id_tarjetas from opercuentas where id_conceptos={0} and date_part('year',datetime)={1} union all select datetime, id_conceptos, id_tiposoperaciones, importe, comentario, id_cuentas ,tarjetas.id_tarjetas as id_tarjetas from opertarjetas,tarjetas where opertarjetas.id_tarjetas=tarjetas.id_tarjetas and id_conceptos={0} and date_part('year',datetime)={1}".format (self.concepto.id, self.year))
        set.sort()
        set.myqtablewidget(table, None, True)
        horizontalLayout.addWidget(table)
        self.tab.addTab(newtab, self.trUtf8("Report of {0}".format(self.year)))
        self.tab.setCurrentWidget(newtab)

    def on_table_customContextMenuRequested(self,  pos):
        self.actionShowYear.setEnabled(False)
        self.actionShowMonth.setEnabled(False)
        if self.month!=None:
            if self.month==0:
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
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.trUtf8("You can't close this tab"))
            m.exec_()  
        else:
            self.tab.removeTab(index)
