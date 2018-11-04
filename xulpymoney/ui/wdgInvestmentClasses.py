from xulpymoney.libxulpymoney import Assets, Money
import math
import datetime
from PyQt5.QtWidgets import QWidget
from xulpymoney.ui.Ui_wdgInvestmentClasses import Ui_wdgInvestmentClasses
from xulpymoney.ui.canvaschart import VCPie
from PyQt5.QtChart import QChart

class wdgInvestmentClasses(QWidget, Ui_wdgInvestmentClasses):
    def __init__(self, mem,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        self.balances={}#Variable que cachea todos los balances
        self.hoy=datetime.date.today()
        self.animations=True#Mostrar animaciones

        self.viewTPC=VCPie()
        self.layTPC.addWidget(self.viewTPC)     
        self.viewPCI=VCPie()
        self.layPCI.addWidget(self.viewPCI)      
        self.viewTipo=VCPie()
        self.layTipo.addWidget(self.viewTipo)      
        self.viewApalancado=VCPie()
        self.layApalancado.addWidget(self.viewApalancado)    
        self.viewCountry=VCPie()
        self.layCountry.addWidget(self.viewCountry)      
        self.viewProduct=VCPie()
        self.layProduct.addWidget(self.viewProduct)
        
        self.accounts=Assets(self.mem).saldo_todas_cuentas(self.hoy).local()
        self.tab.setCurrentIndex(2)

    def update(self, animations=None):
        """Update calcs and charts"""
        if self.animations==None:
            self.animations=QChart.AllAnimations
        self.animations=animations
        self.scriptTPC()
        self.scriptPCI()
        self.scriptTipos()
        self.scriptApalancado()
        self.scriptCountry()
        self.scriptProduct()

    def on_radCurrent_toggled(self, checked):
        self.update()

    def scriptTPC(self):
        self.viewTPC.clear(self.animations)
        self.viewTPC.setCurrency(self.mem.localcurrency)
        for r in range(0, 11):
            total=Money(self.mem, 0,  self.mem.localcurrency)
            for i in self.mem.data.investments_active().arr:
                if math.ceil(i.product.percentage/10.0)==r:
                    if self.radCurrent.isChecked():
                        total=total+i.balance().local()
                    else:
                        total=total+i.invertido().local()
            if r==0:
                total=total+self.accounts
            if total.isGTZero():
                self.viewTPC.appendData("{0}% variable".format(r*10), total.amount)
        if self.radCurrent.isChecked():
            self.viewTPC.chart.setTitle(self.tr("Investment current balance by variable percentage"))
        else:
            self.viewTPC.chart.setTitle(self.tr("Invested balance by variable percentage"))
        self.viewTPC.display()

    def scriptPCI(self):
        self.viewPCI.clear(self.animations)
        self.viewPCI.setCurrency(self.mem.localcurrency)
        for m in self.mem.investmentsmodes.arr:
            total=Money(self.mem, 0,  self.mem.localcurrency)
            for i in self.mem.data.investments_active().arr:
                if i.product.mode==m:
                    if self.radCurrent.isChecked():
                        total=total+i.balance().local()
                    else:
                        total=total+i.invertido().local()
            if m.id=='c':
                total=total+self.accounts
            self.viewPCI.appendData(m.name.upper(), total.amount)
        if self.radCurrent.isChecked():    
            self.viewPCI.chart.setTitle(self.tr("Investment current balance by Put / Call / Inline"))   
        else:
            self.viewPCI.chart.setTitle(self.tr("Invested balance by Put / Call / Inline"))   
        self.viewPCI.display()

    def scriptTipos(self):
        self.viewTipo.clear(self.animations)
        self.viewTipo.setCurrency(self.mem.localcurrency)
        
        for t in self.mem.types.arr:
            total=Money(self.mem, 0,  self.mem.localcurrency)
            for i in self.mem.data.investments_active().arr:
                if i.product.type==t:
                    if self.radCurrent.isChecked():
                        total=total+i.balance().local()
                    else:
                        total=total+i.invertido().local()
            if t.id==11:#Accounts
                total=total+self.accounts
            if total.isGTZero():
                if t.id==11:#Accounts
                    self.viewTipo.appendData(t.name.upper(), total.amount, True)
                else:
                    self.viewTipo.appendData(t.name.upper(), total.amount)
        if self.radCurrent.isChecked():    
            self.viewTipo.chart.setTitle(self.tr("Investment current balance by product type"))   
        else:
            self.viewTipo.chart.setTitle(self.tr("Invested balance by product type"))   
        self.viewTipo.display()

    def scriptApalancado(self):
        self.viewApalancado.clear(self.animations)
        self.viewApalancado.setCurrency(self.mem.localcurrency)
        
        for a in self.mem.leverages.arr:
            total=Money(self.mem, 0,  self.mem.localcurrency)
            for i in self.mem.data.investments_active().arr:
                if i.product.leveraged==a:
                    if self.radCurrent.isChecked():
                        total=total+i.balance().local()
                    else:
                        total=total+i.invertido().local()
            if a.id==0:#Accounts
                total=total+self.accounts
            if total.isGTZero():
                self.viewApalancado.appendData(a.name.upper(), total.amount)
        if self.radCurrent.isChecked():    
            self.viewApalancado.chart.setTitle(self.tr("Investment current balance by leverage"))
        else:
            self.viewApalancado.chart.setTitle(self.tr("Invested balance by leverage"))
        self.viewApalancado.display()
        
    def scriptCountry(self):
        self.viewCountry.clear(self.animations)
        self.viewCountry.setCurrency(self.mem.localcurrency)
        
        for c in self.mem.countries.arr:
            total=Money(self.mem, 0,  self.mem.localcurrency)
            for i in self.mem.data.investments_active().arr:
                if i.product.stockmarket.country==c:
                    if self.radCurrent.isChecked():
                        total=total+i.balance().local()
                    else:
                        total=total+i.invertido().local()
            if total.isGTZero():
                self.viewCountry.appendData(c.name.upper(), total.amount)
        if self.radCurrent.isChecked():    
            self.viewCountry.chart.setTitle(self.tr("Investment current balance by country"))   
        else:
            self.viewCountry.chart.setTitle(self.tr("Invested balance by country"))   
        self.viewCountry.display()

    def scriptProduct(self):
        self.viewProduct.clear(self.animations)
        self.viewProduct.setCurrency(self.mem.localcurrency)
        
        invs=self.mem.data.investments_active().setInvestments_merging_investments_with_same_product_merging_current_operations()
        invs.order_by_balance()
        for i in invs.arr:
            if self.radCurrent.isChecked():
                saldo=i.balance(type=3)
            else:
                saldo=i.invertido(type=3)
            self.viewProduct.appendData(i.name.replace("Virtual investment merging current operations of ", ""), saldo.amount)

        self.viewProduct.appendData(self.tr("Accounts"), self.accounts.amount, True)
        
        if self.radCurrent.isChecked():    
            self.viewProduct.chart.setTitle(self.tr("Investment current balance by product"))
        else:
            self.viewProduct.chart.setTitle(self.tr("Invested balance by product"))        
        self.viewProduct.display()
