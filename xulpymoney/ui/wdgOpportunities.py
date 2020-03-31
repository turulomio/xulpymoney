import datetime
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget, QDialog, QVBoxLayout, QMenu, QMessageBox
from xulpymoney.ui.Ui_wdgOpportunities import Ui_wdgOpportunities
from xulpymoney.objects.opportunity import OpportunityManager
from xulpymoney.ui.wdgOpportunitiesAdd import wdgOpportunitiesAdd
from xulpymoney.ui.wdgProductHistoricalChart import wdgProductHistoricalOpportunity
from xulpymoney.ui.wdgCalculator import wdgCalculator

class wdgOpportunities(QWidget, Ui_wdgOpportunities):
    def __init__(self, mem,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        self.opportunities=None 
         
        self.txtInvest.setText(self.mem.settingsdb.value_decimal("wdgIndexRange/invertir", "10000"))
        self.mqtwOpportunities.setSettings(self.mem.settings, "wdgOpportunities", "mqtwOpportunities")
        self.mqtwOpportunities.table.customContextMenuRequested.connect(self.on_mqtwOpportunities_customContextMenuRequested)
        self.on_cmbMode_currentIndexChanged(self.cmbMode.currentIndex())
        self.wdgYear.initiate(self.opportunities.date_of_the_first_database_oppportunity().year,  datetime.date.today().year, datetime.date.today().year)

    @pyqtSlot()  
    def on_actionOpportunityNew_triggered(self):
        d=QDialog(self)     
        d.setModal(True)
        d.setWindowTitle(self.tr("Add new opportunity"))
        w=wdgOpportunitiesAdd(self.mem, None, d)
        lay = QVBoxLayout(d)
        lay.addWidget(w)
        d.exec_()    
        self.on_cmbMode_currentIndexChanged(self.cmbMode.currentIndex())
    
    @pyqtSlot()  
    def on_actionOpportunityEdit_triggered(self):
        d=QDialog(self)     
        d.setModal(True)
        d.setWindowTitle(self.tr("Edit opportunity"))
        w=wdgOpportunitiesAdd(self.mem, self.mqtwOpportunities.selected, d)
        lay = QVBoxLayout(d)
        lay.addWidget(w)
        d.exec_()
        self.on_cmbMode_currentIndexChanged(self.cmbMode.currentIndex())
        
    @pyqtSlot() 
    def on_actionOpportunityDelete_triggered(self):
        self.opportunities.remove(self.mqtwOpportunities.selected)
        self.mem.con.commit()
        self.on_cmbMode_currentIndexChanged(self.cmbMode.currentIndex())
        
        
    @pyqtSlot() 
    def on_actionExecute_triggered(self):        
        if self.mqtwOpportunities.selected.executed==None:#Only adds an order if it's not executed
            d=QDialog(self)        
            d.setModal(True)
            d.setFixedSize(850, 850)
            d.setWindowTitle(self.tr("Investment calculator"))
            w=wdgCalculator(self.mem, self)
            w.setProduct(self.mqtwOpportunities.selected.product)
            w.txtFinalPrice.setText(self.mqtwOpportunities.selected.entry)
            lay = QVBoxLayout(d)
            lay.addWidget(w)
            d.exec_()
            reply = QMessageBox.question(None, self.tr('Opportunity execution'), self.tr("If you have make and order, you must execute\nDo you want to execute this oportunity?"),  QMessageBox.Yes, QMessageBox.No)          
            if reply==QMessageBox.Yes:
                self.mqtwOpportunities.selected.executed=self.mem.localzone.now()#Set execution
                self.mqtwOpportunities.selected.save()
                self.mem.con.commit()
        else:
            self.mqtwOpportunities.selected.executed=None#Remove execution
            self.mqtwOpportunities.selected.save()
            self.mem.con.commit()
        self.on_cmbMode_currentIndexChanged(self.cmbMode.currentIndex())

    @pyqtSlot() 
    def on_actionRemove_triggered(self):        
        self.mqtwOpportunities.selected.removed=datetime.date.today()
        self.mqtwOpportunities.selected.save()
        self.mem.con.commit()
        self.on_cmbMode_currentIndexChanged(self.cmbMode.currentIndex())

    @pyqtSlot() 
    def on_actionShowGraphic_triggered(self):
        self.mqtwOpportunities.selected.product.needStatus(2)
        d=QDialog(self)     
        d.showMaximized()
        d.setWindowTitle(self.tr("Opportunity graph"))
        lay = QVBoxLayout(d)
        wc=wdgProductHistoricalOpportunity()
        wc.setProduct(self.mqtwOpportunities.selected.product, None)
        wc.setOpportunity(self.mqtwOpportunities.selected)
#        wc.setPrice(self.mqtwOpportunities.selected.entry)
        wc.generate()
        wc.display()
        lay.addWidget(wc)
        d.exec_()

    def load_OpportunityData(self, frm):
        """Carga los datos de la orden en el frmInvestmentOperationsAdd"""
        if self.mqtwOpportunities.selected.shares<0:
            frm.cmbTiposOperaciones.setCurrentIndex(frm.cmbTiposOperaciones.findData(5))#Sale
        else:
            frm.cmbTiposOperaciones.setCurrentIndex(frm.cmbTiposOperaciones.findData(4))#Purchase
        frm.txtAcciones.setText(self.mqtwOpportunities.selected.shares)
        frm.wdg2CPrice.setTextA(self.mqtwOpportunities.selected.entry)

    @pyqtSlot(int)     
    def on_cmbMode_currentIndexChanged(self, index):
        if index==0:#Current
            self.wdgYear.hide()            
            self.opportunities=OpportunityManager(self.mem).init__from_db("""
                SELECT * 
                FROM 
                    OPPORTUNITIES
                WHERE
                    REMOVED IS NULL AND
                    EXECUTED IS NULL
                ORDER BY DATE
           """)
            self.opportunities.order_by_percentage_from_current_price()
        elif index==1: #show expired
            self.wdgYear.show()
            self.opportunities=OpportunityManager(self.mem).init__from_db(self.mem.con.mogrify("""
                SELECT * 
                FROM 
                    OPPORTUNITIES
                WHERE
                    DATE BETWEEN '%s-1-1' AND '%s-12-31' AND
                    REMOVED<NOW()::DATE AND
                    EXECUTED IS NULL
                ORDER BY DATE
           """, (self.wdgYear.year, self.wdgYear.year)))
            self.opportunities.order_by_removed()
        elif index==2: #show executed
            self.wdgYear.show()
            self.opportunities=OpportunityManager(self.mem).init__from_db(self.mem.con.mogrify("""
                SELECT * 
                FROM 
                    OPPORTUNITIES
                WHERE
                    DATE BETWEEN '%s-1-1' AND '%s-12-31' AND
                    EXECUTED IS NOT NULL
                ORDER BY DATE
           """, (self.wdgYear.year, self.wdgYear.year)))
            self.opportunities.order_by_executed()
        else:
            self.wdgYear.show()
            self.opportunities=OpportunityManager(self.mem).init__from_db(self.mem.con.mogrify("""
                SELECT * 
                FROM 
                    OPPORTUNITIES
                WHERE
                    DATE BETWEEN '%s-1-1' AND '%s-12-31'
                ORDER BY DATE
           """, (self.wdgYear.year, self.wdgYear.year)))
            self.opportunities.order_by_date()
        self.opportunities.mqtw(self.mqtwOpportunities, self.txtInvest.decimal())
        print(self.opportunities)
        print(self.mqtwOpportunities.data)
        self.mqtwOpportunities.setOrderBy(8, True)
       
    def on_mqtwOpportunities_customContextMenuRequested(self,  pos):
        if self.mqtwOpportunities.selected==None:
            self.actionOpportunityDelete.setEnabled(False)
            self.actionOpportunityEdit.setEnabled(False)
            self.actionExecute.setEnabled(False)
            self.actionRemove.setEnabled(False)
            self.actionShowGraphic.setEnabled(False)
        else:
            self.actionOpportunityDelete.setEnabled(True)
            self.actionOpportunityEdit.setEnabled(True)
            self.actionExecute.setEnabled(True)
            self.actionRemove.setEnabled(True)
            if self.mqtwOpportunities.selected.executed==None:
                self.actionExecute.setText("Execute opportunity")
            else:
                self.actionExecute.setText("Remove execution time")
            self.actionShowGraphic.setEnabled(True)
                
                
            
        menu=QMenu()
        menu.addAction(self.actionOpportunityNew)
        menu.addSeparator()
        menu.addAction(self.actionOpportunityEdit)
        menu.addAction(self.actionOpportunityDelete)
        menu.addSeparator()
        menu.addAction(self.actionExecute)      
        menu.addAction(self.actionRemove)        
        menu.addSeparator()
        menu.addAction(self.actionShowGraphic)
        menu.addSeparator()
        menu.addMenu(self.mqtwOpportunities.qmenu())
        menu.exec_(self.mqtwOpportunities.table.mapToGlobal(pos))
                
    def on_wdgYear_changed(self):
        self.on_cmbMode_currentIndexChanged(self.cmbMode.currentIndex())
        
