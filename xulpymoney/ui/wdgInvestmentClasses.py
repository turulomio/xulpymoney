from PyQt5.QtWidgets import QWidget
from datetime import date
from math import ceil
from xulpymoney.ui.Ui_wdgInvestmentClasses import Ui_wdgInvestmentClasses
from xulpymoney.ui.myqcharts import VCPie
from xulpymoney.libxulpymoneytypes import eLeverageType, eMoneyCurrency
from xulpymoney.objects.assets import Assets
from xulpymoney.objects.money import Money

class wdgInvestmentClasses(QWidget, Ui_wdgInvestmentClasses):
    def __init__(self, mem,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        self.hoy=date.today()

        self.viewTPC=VCPie()
        self.viewTPC.setSettings(self.mem.settings, "wdgInvestmentClasses", "viewTPC")
        self.layTPC.addWidget(self.viewTPC)     
        self.viewPCI=VCPie()
        self.viewPCI.setSettings(self.mem.settings, "wdgInvestmentClasses", "viewPCI")
        self.layPCI.addWidget(self.viewPCI)      
        self.viewTipo=VCPie()
        self.viewTipo.setSettings(self.mem.settings, "wdgInvestmentClasses", "viewTipo")
        self.layTipo.addWidget(self.viewTipo)      
        self.viewApalancado=VCPie()
        self.viewApalancado.setSettings(self.mem.settings, "wdgInvestmentClasses", "viewApalancado")
        self.layApalancado.addWidget(self.viewApalancado)    
        self.viewCountry=VCPie()
        self.viewCountry.setSettings(self.mem.settings, "wdgInvestmentClasses", "viewCountry")
        self.layCountry.addWidget(self.viewCountry)      
        self.viewProduct=VCPie()
        self.viewProduct.setSettings(self.mem.settings, "wdgInvestmentClasses", "viewProduct")
        self.layProduct.addWidget(self.viewProduct)
        
        self.accounts=Assets(self.mem).saldo_todas_cuentas(self.hoy).local()
        self.tab.setCurrentIndex(2)

    ## @param animations boolean True to show animations
    def update(self, animations):
        self.viewApalancado.pie.setAnimations(animations)
        self.viewCountry.pie.setAnimations(animations)
        self.viewPCI.pie.setAnimations(animations)
        self.viewProduct.pie.setAnimations(animations)
        self.viewTPC.pie.setAnimations(animations)
        self.viewTipo.pie.setAnimations(animations)
        self.scriptTPC()
        self.scriptPCI()
        self.scriptTipos()
        self.scriptApalancado()
        self.scriptCountry()
        self.scriptProduct()
        QWidget.update(self)

    def on_radCurrent_toggled(self, checked):
        self.update(animations=True)

    def scriptTPC(self):
        self.viewTPC.clear()
        for r in range(0, 11):
            total=Money(self.mem, 0,  self.mem.localcurrency)
            for i in self.mem.data.investments_active().arr:
                if ceil(i.product.percentage/10.0)==r:
                    if self.radCurrent.isChecked():
                        total=total+i.balance().local()
                    else:
                        total=total+i.invertido().local()
            if r==0:
                total=total+self.accounts
            if total.isGTZero():
                self.viewTPC.pie.appendData("{0}% variable".format(r*10), total)
        if self.radCurrent.isChecked():
            self.viewTPC.pie.setTitle(self.tr("Investment current balance by variable percentage"))
        else:
            self.viewTPC.pie.setTitle(self.tr("Invested balance by variable percentage"))
        self.viewTPC.display()

    def scriptPCI(self):
        self.viewPCI.clear()
        for mode in self.mem.investmentsmodes.arr:
            total=Money(self.mem, 0,  self.mem.localcurrency)
            for i in self.mem.data.investments_active().arr:
                for o in i.op_actual:
                    if o.pci_position()==mode.id:
                        if self.radCurrent.isChecked():
                            total=total+o.balance(i.product.result.basic.last, eMoneyCurrency.User)
                        else:
                            total=total+o.invertido(eMoneyCurrency.User)
            if mode.id=='c':
                total=total+self.accounts
            self.viewPCI.pie.appendData(mode.name.upper(), total)
        if self.radCurrent.isChecked():    
            self.viewPCI.pie.setTitle(self.tr("Investment current balance by Put / Call / Inline"))   
        else:
            self.viewPCI.pie.setTitle(self.tr("Invested balance by Put / Call / Inline"))   
        self.viewPCI.display()

    def scriptTipos(self):
        self.viewTipo.clear()
        
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
                    self.viewTipo.pie.appendData(t.name.upper(), total, True)
                else:
                    self.viewTipo.pie.appendData(t.name.upper(), total)
        if self.radCurrent.isChecked():    
            self.viewTipo.pie.setTitle(self.tr("Investment current balance by product type"))   
        else:
            self.viewTipo.pie.setTitle(self.tr("Invested balance by product type"))   
        self.viewTipo.display()

    def scriptApalancado(self):
        self.viewApalancado.clear()
        
        for a in self.mem.leverages.arr:
            total=Money(self.mem, 0,  self.mem.localcurrency)
            for i in self.mem.data.investments_active().arr:
                if i.product.leveraged==a:
                    if self.radCurrent.isChecked():
                        total=total+i.balance().local()
                    else:
                        total=total+i.invertido().local()
            if a.id==eLeverageType.NotLeveraged:#Accounts
                total=total+self.accounts
            if total.isGTZero():
                self.viewApalancado.pie.appendData(a.name.upper(), total)
        if self.radCurrent.isChecked():    
            self.viewApalancado.pie.setTitle(self.tr("Investment current balance by leverage"))
        else:
            self.viewApalancado.pie.setTitle(self.tr("Invested balance by leverage"))
        self.viewApalancado.display()
        
    def scriptCountry(self):
        self.viewCountry.clear()
        
        for c in self.mem.countries.arr:
            total=Money(self.mem, 0,  self.mem.localcurrency)
            for i in self.mem.data.investments_active().arr:
                if i.product.stockmarket.country==c:
                    if self.radCurrent.isChecked():
                        total=total+i.balance().local()
                    else:
                        total=total+i.invertido().local()
            if total.isGTZero():
                self.viewCountry.pie.appendData(c.name.upper(), total)
        if self.radCurrent.isChecked():    
            self.viewCountry.pie.setTitle(self.tr("Investment current balance by country"))   
        else:
            self.viewCountry.pie.setTitle(self.tr("Invested balance by country"))   
        self.viewCountry.display()

    def scriptProduct(self):
        self.viewProduct.clear()
        
        invs=self.mem.data.investments_active().InvestmentManager_merging_investments_with_same_product_merging_current_operations()
        invs.order_by_balance()
        for i in invs.arr:
            if self.radCurrent.isChecked():
                saldo=i.balance(type=3)
            else:
                saldo=i.invertido(type=3)
            self.viewProduct.pie.appendData(i.name.replace("Virtual investment merging current operations of ", ""), saldo)

        self.viewProduct.pie.appendData(self.tr("Accounts"), self.accounts, True)
        
        if self.radCurrent.isChecked():    
            self.viewProduct.pie.setTitle(self.tr("Investment current balance by product"))
        else:
            self.viewProduct.pie.setTitle(self.tr("Invested balance by product"))        
        self.viewProduct.display()

    ## Used to generate report to avoid bad resolution due to animations
    def open_all_tabs(self):
        for i in range (self.tab.count()):
            self.tab.setCurrentIndex(i)
            QWidget.update(self)
