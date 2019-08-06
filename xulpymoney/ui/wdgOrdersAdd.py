from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QWidget, QDialogButtonBox
from datetime import date
from xulpymoney.libxulpymoney import Order
from xulpymoney.libxulpymoneyfunctions import qmessagebox
from xulpymoney.ui.Ui_wdgOrdersAdd import Ui_wdgOrdersAdd

class wdgOrdersAdd(QWidget, Ui_wdgOrdersAdd):
    def __init__(self, mem, order=None, investment=None,   parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        self.order=order
        self.parent=parent

        if order==None:
            self.deDate.setDate(date.today())
            self.lbl.setText("Add new order")
            self.deExpiration.setDate(date.today())
        else:
            self.lbl.setText("Edit order")
            self.deDate.setDate(self.order.date)
            self.deExpiration.setDate(self.order.expiration)
            self.txtShares.setText(self.order.shares)
            self.txtAmount.setText(self.order.amount)
            self.txtPrice.setText(self.order.price)
        
        product=self.mem.data.products.find_by_id(int(self.mem.settings.value("wdgCalculator/product", -9999)))
        self.mem.data.investments.ProductManager_with_investments_distinct_products().qcombobox_not_obsolete(self.cmbProducts, product)
#        if self.investment==None:
#            self.mem.data.investments.qcombobox(self.cmbInvestments, 2, selected=None, obsolete_product=False, investments_active=None,  accounts_active=True)
#        else:
#            self.mem.data.investments.qcombobox(self.cmbInvestments, 2, selected=investment, obsolete_product=False, investments_active=None,  accounts_active=True)

    @pyqtSlot()
    def on_buttonbox_accepted(self):
        self.date=self.deDate.date()
        if not (self.txtAmount.isValid() and self.txtPrice.isValid() and self.txtShares.isValid()):
            qmessagebox(self.tr("Incorrect data. Try again."))
            return
        investment=self.mem.data.investments.find_by_id(self.cmbInvestments.itemData(self.cmbInvestments.currentIndex()))
        if investment==None:
            qmessagebox(self.tr("You must select an investment"))
            return
        if self.deExpiration.date()<self.deDate.date():
            qmessagebox(self.tr("Expiration date can't be less than order date."))
            return
            
        if self.order==None:
            self.order=Order(self.mem)
        self.order.date=self.deDate.date().toPyDate()
        self.order.expiration=self.deExpiration.date().toPyDate()
        self.order.shares=self.txtShares.decimal()
        self.order.amount=self.txtAmount.decimal()
        self.order.price=self.txtPrice.decimal()
        self.order.investment=investment
        
        self.order.save()
        self.mem.con.commit()
        self.order.qmessagebox_reminder()
        self.parent.accept()

    @pyqtSlot()
    def on_buttonbox_rejected(self):
        self.parent.reject()
            
    @pyqtSlot(int)  
    def on_cmbProducts_currentIndexChanged(self, index):
        """To invoke this function you must call self.cmbProducts.setCurrentIndex()"""
        product=self.mem.data.products.find_by_id(self.cmbProducts.itemData(index))
        if product!=None:
            #Fills self.cmbInvestments with all product investments or with zero shares product investments
            if self.chkWithoutShares.checkState()==Qt.Checked:
                self.investments=self.mem.data.investments.InvestmentManager_with_investments_with_the_same_product_with_zero_shares(product)
            else:
                self.investments=self.mem.data.investments.InvestmentManager_with_investments_with_the_same_product(product)
            self.investments.qcombobox(self.cmbInvestments, tipo=3, selected=None, obsolete_product=False, investments_active=None, accounts_active=None)
 
            self.mem.settings.setValue("wdgCalculator/product", product.id)
    
    @pyqtSlot(int)  
    def on_cmbInvestments_currentIndexChanged(self, index):
        """To invoke this function you must call self.cmbInvestments.setCurrentIndex()"""
        if index>=0:#Only enabled if some investment is selected
            self.buttonbox.button(QDialogButtonBox.Ok).setEnabled(True)
        else:
            self.buttonbox.button(QDialogButtonBox.Cancel).setEnabled(True)
        self.investments.selected=self.mem.data.investments.find_by_id(self.cmbInvestments.itemData(index))


    ## This check filters investments showing ones with 0 currrent shares
    def on_chkWithoutShares_stateChanged(self, state):
        self.on_cmbProducts_currentIndexChanged(self.cmbProducts.currentIndex())
        
