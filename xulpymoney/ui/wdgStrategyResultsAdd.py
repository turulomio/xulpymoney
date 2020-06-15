from PyQt5.QtWidgets import QWidget, QFileDialog
from xulpymoney.ui.Ui_wdgStrategyResultsAdd import Ui_wdgStrategyResultsAdd
from xulpymoney.objects.investment import InvestmentManager
from xulpymoney.objects.strategy import Strategy

class wdgStrategyResultsAdd(QWidget, Ui_wdgStrategyResultsAdd):
    def __init__(self, mem, strategy=None,  parent = None):
        QWidget.__init__(self,  parent)
        self.setupUi(self)
        self.mem=mem
        self.parent=parent  
        self.strategy=strategy
        
        self.wdgDtFrom.setTitle(self.tr("Select strategy start date and time"))
        self.wdgDtFrom.setLocalzone(self.mem.localzone_name)
        self.wdgDtFrom.show_microseconds(False)
        self.wdgDtTo.setTitle(self.tr("Select strategy end date and time"))
        self.wdgDtTo.setLocalzone(self.mem.localzone_name)
        self.wdgDtTo.show_microseconds(False)
        self.wdgDtTo.show_none(True)
        
        self.cmsInvestments.frm.widget.setShowObjectCallingByName(["fullName", ()])
        self.mqtwCurrent.setSettings(self.mem.settings, "wdgStrategyResultsAdd", "mqtwCurrent")
        self.mqtwHistorical.setSettings(self.mem.settings, "wdgStrategyResultsAdd", "mqtwHistorical")
        self.mqtwDividends.setSettings(self.mem.settings, "wdgStrategyResultsAdd", "mqtwDividends")
        
        
        
        if self.strategy is None:# New one
            self.strategy=Strategy(self.mem)
            self.strategy.investments=InvestmentManager(self.mem)
            self.wdgDtFrom.set()
            self.wdgDtTo.set()
            self.cmsInvestments.setManagers(self.mem.settings,"wdgStrategyResultsAdd", "cmsInvestments", self.mem.data.investments, None)
        else:
            self.txtName.setText(self.strategy.name)
            self.wdgDtFrom.set(self.strategy.dt_from, self.mem.localzone_name)
            self.wdgDtTo.set(self.strategy.dt_to, self.mem.localzone_name)
            self.cmsInvestments.setManagers(self.mem.settings,"wdgStrategyResultsAdd", "cmsInvestments", self.mem.data.investments, self.strategy.investments)

        self.cmdSave.setEnabled(False)
        self.update()

    def on_cmsInvestments_comboSelectionChanged(self):
        self.cmdSave.setEnabled(True)
        self.update()

    def on_wdgDtFrom_changed(self):
        self.cmdSave.setEnabled(True)
        self.update()

    def on_wdgDtTo_changed(self):
        self.cmdSave.setEnabled(True)
        self.update()
        
    def on_cmdProductsUpdate_released(self):
        from xulpymoney.investing_com import InvestingCom
        filename=QFileDialog.getOpenFileName(self, "", "", "Texto CSV (*.csv)")[0]
        if filename!="":
            set=InvestingCom(self.mem, filename)
            result=set.save()
            self.mem.con.commit()
            #Display result
            from xulpymoney.ui.wdgQuotesSaveResult import frmQuotesSaveResult
            d=frmQuotesSaveResult()
            d.setFileToDelete(filename)
            d.setQuotesManagers(*result)
            d.exec_()
            #Reloads changed data
            set.change_products_status_after_save(result[0], result[2], 1, downgrade_to=0, progress=True)
            self.update()
        
    def on_cmdSave_released(self):
        self.strategy.name=self.txtName.text()
        self.strategy.dt_to=self.wdgDtTo.datetime()
        self.strategy.dt_from=self.wdgDtFrom.datetime()
        self.strategy.save()
        self.mem.con.commit()
        self.cmdSave.setEnabled(False)
        self.mem.settingsdb.setValue("wdgStrategyResultsAdd/cmbStrategies", self.strategy.id )
        self.update()
        
    def on_txtName_textChanged(self):
        self.cmdSave.setEnabled(True)
        self.update()
        
    def update(self):
        current=self.strategy.currentOperations()
        current.myqtablewidget(self.mqtwCurrent)
        historical=self.strategy.historicalOperations()
        historical.myqtablewidget(self.mqtwHistorical)
        dividends=self.strategy.dividends()
        dividends.myqtablewidget(self.mqtwDividends)
        
        s=self.tr("Total = Current net gains + Historical net gains + Net dividends = {} + {} + {} = {}").format(current.pendiente(), historical.consolidado_neto(), dividends.net(),  current.pendiente()+ historical.consolidado_neto()+ dividends.net()) 
        s= s + "\n"
        s= s + self.tr("Call operations balance: {}. Put operations balance: {}").format(current.balance_long_operations(), current.balance_short_operations())
        self.lblResults.setText(s)

