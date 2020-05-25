from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMenu, QWidget, QHBoxLayout, QAbstractItemView
from datetime import date
from logging import debug
from xulpymoney.casts import lor_sum_column, lor_sum_row
from xulpymoney.ui.myqtablewidget import mqtwObjects
from xulpymoney.objects.accountoperation import AccountOperationManagerHeterogeneus
from xulpymoney.objects.money import Money
from xulpymoney.ui.myqwidgets import qmessagebox
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
        self.mqtwReport.setSettings(self.mem.settings, "wdgConceptsHistorical", "mqtwReport")
        self.mqtwReport.table.customContextMenuRequested.connect(self.on_mqtwReport_table_customContextMenuRequested)
        self.mqtwReport.table.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.reload()

    def reload(self):
        #Junta opercuentas y opertarjetas y sobre esa subquery uni hace un group by
        rows=self.mem.con.cursor_rows("""
        select date_part('year',datetime)::int as year,  date_part('month',datetime)::int as month, sum(importe) as value 
        from ( 
                    SELECT opercuentas.datetime, opercuentas.id_conceptos,  opercuentas.importe  FROM opercuentas where id_conceptos={0} 
                        UNION ALL 
                    SELECT opertarjetas.datetime, opertarjetas.id_conceptos, opertarjetas.importe FROM opertarjetas where id_conceptos={0}
                ) as uni 
        group by date_part('year',datetime), date_part('month',datetime) order by 1,2 ;
        """.format(self.concepto.id))

        if len(rows)==0: #Due it may have no data
            return
            
        self.firstyear=int(rows[0]['year'])
        
        hh=[self.tr("Year"), self.tr("January"),  self.tr("February"), self.tr("March"), self.tr("April"), self.tr("May"), self.tr("June"), self.tr("July"), self.tr("August"), self.tr("September"), self.tr("October"), self.tr("November"), self.tr("December"), self.tr("Total")]
        data=[]
        # Create all data spaces filling year
        for year in range(self.firstyear, date.today().year+1):
            data.append([year, ] + [None]*13)
        # Fills spaces with values
        for row in rows:
            for rowdata in data:
                if rowdata[0]==row['year']:
                    rowdata[row['month']]=Money(self.mem, row['value'], self.mem.localcurrency)
                rowdata[13]=lor_sum_row(rowdata, 1, 12, Money(self.mem, 0, self.mem.localcurrency))
                
        total=lor_sum_column(data, 13, 0, len(data)-1, Money(self.mem, 0, self.mem.localcurrency))
        data.append([self.tr("Total")]+["#crossedout"]*12+[total,])
        self.mqtwReport.setData(hh, None, data)

    @pyqtSlot() 
    def on_actionShowMonth_triggered(self):
        newtab = QWidget()
        horizontalLayout = QHBoxLayout(newtab)
        mqtwMonth = mqtwObjects(newtab)
        mqtwMonth.setSettings(self.mem.settings, "wdgConceptsHistorical",  "mqtwMonth")
        set=AccountOperationManagerHeterogeneus(self.mem)
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
        set.myqtablewidget(mqtwMonth, True)
        horizontalLayout.addWidget(mqtwMonth)
        self.tab.addTab(newtab, self.tr("Report of {0} of {1}".format(self.mqtwReport.table.horizontalHeaderItem(self.month).text(), self.year)))
        self.tab.setCurrentWidget(newtab)

    @pyqtSlot() 
    def on_actionShowYear_triggered(self):
        newtab = QWidget()
        horizontalLayout = QHBoxLayout(newtab)
        mqtwYear = mqtwObjects(newtab)
        mqtwYear.setSettings(self.mem.settings, "wdgConceptsHistorical",  "mqtwYear")
        set=AccountOperationManagerHeterogeneus(self.mem)
        set.load_from_db_with_creditcard("select datetime, id_conceptos, id_tiposoperaciones, importe, comentario, id_cuentas , -1 as id_tarjetas from opercuentas where id_conceptos={0} and date_part('year',datetime)={1} union all select datetime, id_conceptos, id_tiposoperaciones, importe, comentario, id_cuentas ,tarjetas.id_tarjetas as id_tarjetas from opertarjetas,tarjetas where opertarjetas.id_tarjetas=tarjetas.id_tarjetas and id_conceptos={0} and date_part('year',datetime)={1}".format (self.concepto.id, self.year))
        set.myqtablewidget(mqtwYear, True)
        horizontalLayout.addWidget(mqtwYear)
        self.tab.addTab(newtab, self.tr("Report of {0}".format(self.year)))
        self.tab.setCurrentWidget(newtab)

    def on_mqtwReport_table_customContextMenuRequested(self,  pos):
        self.actionShowYear.setEnabled(False)
        self.actionShowMonth.setEnabled(False)
        if self.month is not None and self.year is not None:
            self.actionShowMonth.setEnabled(True)
        if self.year is not None:
            self.actionShowYear.setEnabled(True)

        menu=QMenu()
        menu.addAction(self.actionShowYear)
        menu.addSeparator()
        menu.addAction(self.actionShowMonth)   
        menu.addSeparator()
        menu.addMenu(self.mqtwReport.qmenu())
        menu.exec_(self.mqtwReport.table.mapToGlobal(pos))

    @pyqtSlot()
    def on_mqtwReport_tableSelectionChanged(self):
        self.month=None
        self.year=None
        if self.mqtwReport.selected_items is not None:
            if self.mqtwReport.selected_items.column()>0 and self.mqtwReport.selected_items.column()<=12:
                self.month=self.mqtwReport.selected_items.column()
            year_=self.firstyear+self.mqtwReport.selected_items.row()
            if year_<=date.today().year:
                self.year=year_
            
        debug("Selected year: {0}. Selected month: {1}.".format(self.year, self.month))

    def on_tab_tabCloseRequested(self, index):
        """Only removes dinamic tabs"""
        if index==0:
            qmessagebox(self.tr("You can't close this tab"))
        else:
            self.tab.removeTab(index)
