from PyQt5.QtWidgets import QWidget, QMessageBox
from xulpymoney.ui.Ui_wdgProductsDataMove import Ui_wdgProductsDataMove

class wdgProductsDataMove(QWidget, Ui_wdgProductsDataMove):
    def __init__(self, mem,  origin, destiny, parent = None, name = None, modal = False):
        QWidget.__init__(self,  parent)
        self.mem=mem
        self.origin=origin
        self.destiny=destiny
        self.setupUi(self)
        self.mqtwComparation.setSettings(self.mem.settings, "wdgProductsDataMove", "mqtwComparation") 
        self.origin.needStatus(3)
        self.destiny.needStatus(3)
        self.reload()
        
    def on_cmdInterchange_released(self):
        tmp=self.origin
        self.origin=self.destiny
        self.destiny=tmp
        self.reload()
    
    ## Sets tabble data
    def reload(self):
        hh=[self.tr("Id"), self.tr("Name"), self.tr("ISIN"), self.tr("Quotes"), self.tr("DPS"), self.tr("Investments"), self.tr("Opportunities"), self.tr("Splits"), self.tr("DPS estimations"), self.tr("EPS estimations")]
        hv=[self.tr("Origin"), self.tr("Destiny")]
        data=[]
        for i,  p in enumerate([self.origin, self.destiny]):
            data.append([
                p.id, 
                p.name, 
                p.isin, 
                p.result.all.length(), 
                p.dps.length(), 
                self.mem.data.investments.InvestmentManager_with_investments_with_the_same_product(p).length(), 
                self.mem.con.cursor_one_field("select count(*) from opportunities where products_id=%s and executed is null and removed is null", (p.id, )), 
                p.splits.length(), 
                p.estimations_dps.length(), 
                p.estimations_eps.length(), 
            ])
        self.mqtwComparation.setData(hh, hv, data)
        for i,  p in enumerate([self.origin, self.destiny]):
            self.mqtwComparation.table.item(i, 0).setIcon(p.stockmarket.country.qicon())

    def on_cmd_released(self):
        reply = QMessageBox.question(None, self.tr('Moving data between products'), self.tr("This action can't be undone.\nDo you want to continue?"), QMessageBox.Yes, QMessageBox.No)                  
        if reply==QMessageBox.Yes:
            self.mem.data.products.move_data_between_products(self.origin, self.destiny)
            self.origin.needStatus(3, downgrade_to=0)
            self.destiny.needStatus(3, downgrade_to=0)
            if self.chkInvestments.isChecked()==True:
                self.mem.data.investments.change_product_id(self.origin, self.destiny)
            self.mem.con.commit()
            self.reload()
            

