from PyQt5.QtCore import *
from PyQt5.QtGui import *
from libxulpymoney import *
from Ui_wdgOrdersAdd import *

class wdgOrdersAdd(QWidget, Ui_wdgOrdersAdd):
    def __init__(self, mem, order=None, investment=None,   parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        self.order=order
        self.parent=parent
        self.investment=investment

        if order==None:
            self.lbl.setText("Add new order")
            self.deDate.setDate(datetime.date.today())
            self.deExpiration.setDate(datetime.date.today()+datetime.timedelta(days=1))
        else:
            self.lbl.setText("Edit order")
            self.deDate.setDate(self.order.date)
            self.deExpiration.setDate(self.order.expiration)
            self.txtShares.setText(self.order.shares)
            self.txtAmount.setText(self.order.amount)
            self.txtPrice.setText(self.order.price)
            
        self.mem.data.investments_active.qcombobox(self.cmbInvestments, 2, True)
        if self.investment!=None:
            self.cmbInvestments.setCurrentIndex(self.cmbInvestments.findData(self.investment.id))
            
    @pyqtSlot()
    def on_buttonbox_accepted(self):
        self.date=self.deDate.date()
        if not (self.txtAmount.isValid() and self.txtPrice.isValid() and self.txtShares.isValid()):
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.tr("Incorrect data. Try again."))
            m.exec_()    
            return
        if self.order==None:
            self.order=Order(self.mem)
            self.mem.data.orders.append(self.order)#Object can be added here (before commit)
        self.order.date=self.deDate.date().toPyDate()
        self.order.expiration=self.deExpiration.date().toPyDate()
        self.order.shares=self.txtShares.decimal()
        self.order.amount=self.txtAmount.decimal()
        self.order.price=self.txtPrice.decimal()
        self.order.investment=self.mem.data.investments_active.find_by_id(self.cmbInvestments.itemData(self.cmbInvestments.currentIndex()))
        self.order.save()
        self.mem.con.commit()
        self.close()
        self.parent.accept()

    @pyqtSlot()
    def on_buttonbox_rejected(self):
        self.parent.reject()
