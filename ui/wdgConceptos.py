from PyQt4.QtCore import *
from PyQt4.QtGui import *
from libxulpymoney import *
from Ui_wdgConceptos import *

class wdgConceptos(QWidget, Ui_wdgConceptos):
    def __init__(self, cfg,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.cfg=cfg
        
        self.expenses=self.cfg.conceptos.clone_x_tipooperacion(1)
        self.incomes=self.cfg.conceptos.clone_x_tipooperacion(2)

        self.tblExpenses.settings("wdgConceptos",  self.cfg.file_ui)
        self.tblIncomes.settings("wdgConceptos",  self.cfg.file_ui)
        
        anoinicio=Patrimonio(self.cfg).primera_fecha_con_datos_usuario().year       
        self.wdgYM.initiate(anoinicio,  datetime.date.today().year, datetime.date.today().year, datetime.date.today().month)
        QObject.connect(self.wdgYM, SIGNAL("changed"), self.on_wdgYM_changed)
        
        self.on_wdgYM_changed()
        
    def load_gastos(self,  year,  month):
        self.tblExpenses.clearContents()
        self.tblExpenses.setRowCount(len(self.expenses.dic_arr)+1)
        
        (dic, totalexpenses,  totalaverageexpenses)=self.expenses.percentage_monthly(year, month)
        
        
        for i, c in enumerate(self.expenses.list()):
            self.tblExpenses.setItem(i, 0, QTableWidgetItem(c.name))
            self.tblExpenses.setItem(i, 2, self.cfg.localcurrency.qtablewidgetitem(dic[str(c.id)][1]))
            self.tblExpenses.setItem(i, 3, qtpc(dic[str(c.id)][2]))
            self.tblExpenses.setItem(i, 4, self.cfg.localcurrency.qtablewidgetitem(dic[str(c.id)][3]))
            
            if dic[str(c.id)][1]!=0:
                if dic[str(c.id)][1]>dic[str(c.id)][3]:
                    self.tblExpenses.item(i, 2).setBackgroundColor( QColor(182, 255, 182))          
                else:
                    self.tblExpenses.item(i, 2).setBackgroundColor( QColor(255, 182, 182))      
                
        self.tblExpenses.setItem(len(self.expenses.dic_arr), 0, QTableWidgetItem(self.tr('TOTAL')))
        self.tblExpenses.setItem(len(self.expenses.dic_arr), 2, self.cfg.localcurrency.qtablewidgetitem(totalexpenses))    
        self.tblExpenses.setItem(len(self.expenses.dic_arr), 3, qtpc(100))    
        self.tblExpenses.setItem(len(self.expenses.dic_arr), 4, self.cfg.localcurrency.qtablewidgetitem(totalaverageexpenses))       

    def load_ingresos(self,  year,  month):
        self.tblIncomes.clearContents()
        self.tblIncomes.setRowCount(len(self.incomes.dic_arr)+1)
        
        (dic, totalincomes,  totalaverageincomes)=self.incomes.percentage_monthly(year, month)
        
        
        for i, c in enumerate(self.incomes.list()):
            self.tblIncomes.setItem(i, 0, QTableWidgetItem(c.name))
            self.tblIncomes.setItem(i, 2, self.cfg.localcurrency.qtablewidgetitem(dic[str(c.id)][1]))
            self.tblIncomes.setItem(i, 3, qtpc(dic[str(c.id)][2]))
            self.tblIncomes.setItem(i, 4, self.cfg.localcurrency.qtablewidgetitem(dic[str(c.id)][3]))
            
            if dic[str(c.id)][1]!=0:
                if dic[str(c.id)][1]>dic[str(c.id)][3]:
                    self.tblIncomes.item(i, 2).setBackgroundColor( QColor(182, 255, 182))          
                else:
                    self.tblIncomes.item(i, 2).setBackgroundColor( QColor(255, 182, 182))      
                
        self.tblIncomes.setItem(len(self.incomes.dic_arr), 0, QTableWidgetItem(self.tr('TOTAL')))
        self.tblIncomes.setItem(len(self.incomes.dic_arr), 2, self.cfg.localcurrency.qtablewidgetitem(totalincomes))    
        self.tblIncomes.setItem(len(self.incomes.dic_arr), 3, qtpc(100))    
        self.tblIncomes.setItem(len(self.incomes.dic_arr), 4, self.cfg.localcurrency.qtablewidgetitem(totalaverageincomes))       


        
    @QtCore.pyqtSlot() 
    def on_wdgYM_changed(self):
        self.load_gastos(self.wdgYM.year, self.wdgYM.month)
        self.load_ingresos(self.wdgYM.year,  self.wdgYM.month)
        
        
