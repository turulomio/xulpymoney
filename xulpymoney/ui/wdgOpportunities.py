import datetime
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget, QDialog, QVBoxLayout, QMenu, QMessageBox
from xulpymoney.ui.Ui_wdgOpportunities import Ui_wdgOpportunities
from xulpymoney.libxulpymoney import OpportunityManager
from xulpymoney.ui.wdgOpportunitiesAdd import wdgOpportunitiesAdd
from xulpymoney.ui.wdgProductHistoricalChart import wdgProductHistoricalBuyChart
from xulpymoney.ui.wdgCalculator import wdgCalculator

class wdgOpportunities(QWidget, Ui_wdgOpportunities):
    def __init__(self, mem,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        self.opportunities=None 
         
        self.tblOpportunities.settings(self.mem, "wdgOpportunities")
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
        w=wdgOpportunitiesAdd(self.mem, self.opportunities.selected, d)
        lay = QVBoxLayout(d)
        lay.addWidget(w)
        d.exec_()
        self.on_cmbMode_currentIndexChanged(self.cmbMode.currentIndex())
        
    @pyqtSlot() 
    def on_actionOpportunityDelete_triggered(self):
        self.opportunities.remove(self.opportunities.selected)
        self.mem.con.commit()
        self.on_cmbMode_currentIndexChanged(self.cmbMode.currentIndex())
        
        
    @pyqtSlot() 
    def on_actionExecute_triggered(self):        
        if self.opportunities.selected.executed==None:#Only adds an order if it's not executed
            d=QDialog(self)        
            d.setModal(True)
            d.setFixedSize(850, 850)
            d.setWindowTitle(self.tr("Investment calculator"))
            w=wdgCalculator(self.mem, self)
            w.setProduct(self.opportunities.selected.product)
            w.txtFinalPrice.setText(self.opportunities.selected.price)
            lay = QVBoxLayout(d)
            lay.addWidget(w)
            d.exec_()
            reply = QMessageBox.question(None, self.tr('Opportunity execution'), self.tr("If you have make and order, you must execute\nDo you want to execute this oportunity?"),  QMessageBox.Yes, QMessageBox.No)          
            if reply==QMessageBox.Yes:
                self.opportunities.selected.executed=self.mem.localzone.now()#Set execution
                self.opportunities.selected.save()
                self.mem.con.commit()
        else:
            self.opportunities.selected.executed=None#Remove execution
            self.opportunities.selected.save()
            self.mem.con.commit()
        self.on_cmbMode_currentIndexChanged(self.cmbMode.currentIndex())

    @pyqtSlot() 
    def on_actionRemove_triggered(self):        
        self.opportunities.selected.removed=datetime.date.today()
        self.opportunities.selected.save()
        self.mem.con.commit()
        self.on_cmbMode_currentIndexChanged(self.cmbMode.currentIndex())

    @pyqtSlot() 
    def on_actionShowGraphic_triggered(self):
        self.opportunities.selected.product.needStatus(2)
        d=QDialog(self)     
        d.showMaximized()
        d.setWindowTitle(self.tr("Purchase graph"))
        lay = QVBoxLayout(d)
        wc=wdgProductHistoricalBuyChart()
        wc.setProduct(self.opportunities.selected.product, None)
        wc.setPrice(self.opportunities.selected.price)
        wc.generate()
        wc.display()
        lay.addWidget(wc)
        d.exec_()

    def load_OpportunityData(self, frm):
        """Carga los datos de la orden en el frmInvestmentOperationsAdd"""
        if self.opportunities.selected.shares<0:
            frm.cmbTiposOperaciones.setCurrentIndex(frm.cmbTiposOperaciones.findData(5))#Sale
        else:
            frm.cmbTiposOperaciones.setCurrentIndex(frm.cmbTiposOperaciones.findData(4))#Purchase
        frm.txtAcciones.setText(self.opportunities.selected.shares)
        frm.wdg2CPrice.setTextA(self.opportunities.selected.price)

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
        self.opportunities.myqtablewidget(self.tblOpportunities)
       
    def on_tblOpportunities_customContextMenuRequested(self,  pos):
        if self.opportunities.selected==None:
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
            if self.opportunities.selected.executed==None:
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
        menu.exec_(self.tblOpportunities.mapToGlobal(pos))

    def on_tblOpportunities_itemSelectionChanged(self):
        self.opportunities.selected=None
        for i in self.tblOpportunities.selectedItems():
            if i.column()==0:#only once per row
                self.opportunities.selected=self.opportunities.arr[i.row()]
                
    def on_wdgYear_changed(self):
        self.on_cmbMode_currentIndexChanged(self.cmbMode.currentIndex())
        
