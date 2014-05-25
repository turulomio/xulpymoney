from PyQt4.QtCore import *
from PyQt4.QtGui import *
from libxulpymoney import *
from frmAccountsReport import *
from frmInvestmentReport import *
from Ui_wdgBanks import *

class wdgBanks(QWidget, Ui_wdgBanks):
    def __init__(self, mem,  parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        self.selEB=None#id_ebs
        self.selAccount=None #id_cuentas
        self.selInvestment=None #Registro
        
        
        
        self.ebs=None
        self.inversiones=None
        self.cuentas=None

        self.tblEB.settings("wdgBanks",  self.mem)
        self.tblAccounts.settings("wdgBanks",  self.mem)
        self.tblInvestments.settings("wdgBanks",  self.mem)
        
        self.on_chkInactivas_stateChanged(Qt.Unchecked)#Carga eb

        
    def load_eb(self):
        self.tblEB.clearContents()
        self.tblEB.setRowCount(len(self.ebs)+1);
        sumsaldos=Decimal(0)
        for i,  e in enumerate(self.ebs):
            self.tblEB.setItem(i, 0, QTableWidgetItem(e.name))
            self.tblEB.setItem(i, 1, qbool(e.activa))
            balance=e.balance(self.mem.data.cuentas_active, self.mem.data.inversiones_active)
            self.tblEB.setItem(i, 2, self.mem.localcurrency.qtablewidgetitem(balance))
            sumsaldos=sumsaldos+balance     
        self.tblEB.setItem(len(self.ebs), 0, QTableWidgetItem(self.tr('TOTAL')))
        self.tblEB.setItem(len(self.ebs), 2, self.mem.localcurrency.qtablewidgetitem(sumsaldos))        
        
    def load_cuentas(self):
        self.tblAccounts.clearContents()
        self.tblAccounts.setRowCount(len(self.cuentas)+1);
        sumsaldos=0
        for i,  c in enumerate(self.cuentas):
            self.tblAccounts.setItem(i, 0, QTableWidgetItem(c.name))
            self.tblAccounts.setItem(i, 1, qbool(c.activa))
            self.tblAccounts.setItem(i, 2, self.mem.localcurrency.qtablewidgetitem(c.balance))
            sumsaldos=sumsaldos+c.balance
        self.tblAccounts.setItem(len(self.cuentas), 0, QTableWidgetItem(self.tr('TOTAL')))
        self.tblAccounts.setItem(len(self.cuentas), 2, self.mem.localcurrency.qtablewidgetitem(sumsaldos))                
        
                
    def load_inversiones(self):
        self.tblInvestments.clearContents()
        self.tblInvestments.setRowCount(len(self.inversiones)+1);
        sumsaldos=0
        for i, inv in enumerate(self.inversiones):
            self.tblInvestments.setItem(i, 0, QTableWidgetItem(inv.name))
            self.tblInvestments.setItem(i, 1, qbool(inv.activa))
            balance=inv.balance()
            self.tblInvestments.setItem(i, 2, self.mem.localcurrency.qtablewidgetitem(balance))
            sumsaldos=sumsaldos+balance
        self.tblInvestments.setItem(len(self.inversiones), 0, QTableWidgetItem(self.tr('TOTAL')))
        self.tblInvestments.setItem(len(self.inversiones), 2, self.mem.localcurrency.qtablewidgetitem(sumsaldos))                
        
        
    def on_chkInactivas_stateChanged(self, state):
        if state==Qt.Unchecked:
            self.ebs=self.mem.data.ebs_active.arr
        else:
            self.mem.data.load_inactives()
            self.ebs=self.mem.data.ebs_inactive.arr
        self.load_eb()
        self.tblEB.clearSelection()   
        self.tblAccounts.setRowCount(0)
        self.tblAccounts.clearContents()
        self.tblInvestments.setRowCount(0);
        self.tblInvestments.clearContents()

    def on_tblEB_itemSelectionChanged(self):
        self.selEB=None
        self.inversiones=[]
        self.cuentas=[]
        
        for i in self.tblEB.selectedItems():#itera por cada item no row.
            if i.row()<len(self.ebs):#Necesario porque tiene fila de total
                self.selEB=self.ebs[i.row()]
        print ("Seleccionado: " +  str(self.selEB))
        
        if self.selEB==None:
            self.tblEB.clearSelection()   
            self.tblAccounts.setRowCount(0)
            self.tblAccounts.clearContents()
            self.tblInvestments.setRowCount(0);
            self.tblInvestments.clearContents()
            return
            
        activas=False
        if self.chkInactivas.checkState()==Qt.Unchecked:
            activas=True
            
        for i in self.mem.data.inversiones_active.arr:
            if i.activa==activas and i.cuenta.eb.id==self.selEB.id:
                self.inversiones.append(i)
        self.inversiones=sorted(self.inversiones, key=lambda inve: inve.name,  reverse=False) 
        
        for v in self.mem.data.cuentas_active.arr:
            if v.activa==activas and v.eb.id==self.selEB.id:
                self.cuentas.append(v)
        self.cuentas=sorted(self.cuentas, key=lambda c: c.name,  reverse=False) 
        
        self.load_cuentas()
        self.load_inversiones()

    def on_tblEB_customContextMenuRequested(self,  pos):
        if self.selEB==None:
            self.actionBankDelete.setEnabled(False)
            self.actionBankEdit.setEnabled(False)
            self.actionActive.setEnabled(False)
        else:
            self.actionBankDelete.setEnabled(True)
            self.actionBankEdit.setEnabled(True)
            self.actionActive.setEnabled(True)
            
        if self.chkInactivas.checkState()==Qt.Unchecked:
            self.actionActive.setChecked(True)
        else:
            self.actionActive.setChecked(False)
            
        menu=QMenu()
        menu.addAction(self.actionBankAdd)
        menu.addAction(self.actionBankEdit)
        menu.addAction(self.actionBankDelete)
        menu.addSeparator()
        menu.addAction(self.actionActive)
        menu.exec_(self.tblEB.mapToGlobal(pos))
        
    @QtCore.pyqtSlot() 
    def on_actionAccountReport_activated(self):
        w=frmAccountsReport(self.mem, self.selAccount)
        w.exec_()        
        self.load_cuentas()

    @QtCore.pyqtSlot() 
    def on_actionInvestmentReport_activated(self):
        w=frmInvestmentReport(self.mem,   self.selInvestment)
        w.exec_()
        self.load_inversiones()

    def on_tblAccounts_itemSelectionChanged(self):
        self.selAccount=None
        for i in self.tblAccounts.selectedItems():#itera por cada item no row.
            if i.row()<len(self.cuentas):#Necesario porque tiene fila de total
                self.selAccount=self.cuentas[i.row()]
        print ("Seleccionado: " +  str(self.selAccount))

    def on_tblAccounts_customContextMenuRequested(self,  pos):
        if self.selAccount==None:
            self.actionAccountReport.setEnabled(False)
        else:
            self.actionAccountReport.setEnabled(True)
        menu=QMenu()
        menu.addAction(self.actionAccountReport)
        menu.exec_(self.tblAccounts.mapToGlobal(pos))


    def on_tblInvestments_itemSelectionChanged(self):
        self.selInvestment=None
        for i in self.tblInvestments.selectedItems():#itera por cada item no row.
            if i.row()<len(self.inversiones):#Necesario porque tiene fila de total
                self.selInvestment=self.inversiones[i.row()]
        print ("Seleccionado: " +  str(self.selInvestment))

        
    def on_tblInvestments_customContextMenuRequested(self,  pos):
        if self.selInvestment==None:
            self.actionInvestmentReport.setEnabled(False)
        else:
            self.actionInvestmentReport.setEnabled(True)
        menu=QMenu()
        menu.addAction(self.actionInvestmentReport)        
        menu.exec_(self.tblInvestments.mapToGlobal(pos))
        
    @QtCore.pyqtSlot()  
    def on_actionBankDelete_activated(self):
        if self.selEB.es_borrable(self.mem.dic_cuentas)==False:
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.trUtf8("Este banco tiene cuentas dependientes y no puede ser borrado"))
            m.exec_()
        else:
            con=self.mem.connect_xulpymoney()
            cur = con.cursor()
            self.selEB.borrar(cur, self.mem.dic_cuentas)
            #Se borra de la lista de wdgBanks ebs y del diccionario raiz 
            self.ebs.remove(self.selEB)
            del self.mem.dic_ebs[str(self.selEB.id)]
            con.commit()  
            cur.close()     
            self.mem.disconnect_xulpymoney(con)    
            self.load_eb()    
        
    @QtCore.pyqtSlot()  
    def on_actionBankAdd_activated(self):
        tipo=QInputDialog().getText(self,  "Xulpymoney > Bancos > Nuevo ",  "Introduce un nuevo banco")
        if tipo[1]==True:
            eb=Bank(self.mem).init__create(tipo[0])
            eb.save()
            self.mem.con.commit()  
            self.mem.data.ebs_active.arr.append(eb)
            self.mem.data.ebs_active.sort()
            
            self.load_eb()


    @QtCore.pyqtSlot()  
    def on_actionBankEdit_activated(self):
        tipo=QInputDialog().getText(self,  "Xulpymoney > Bancos > Modificar",  "Modifica el banco seleccionado", QLineEdit.Normal,   (self.selEB.name))       
        if tipo[1]==True:
            self.selEB.name=tipo[0]
            self.selEB.save()
            self.mem.con.commit()
            self.mem.data.ebs_active.sort()
            
            self.load_eb()   
        
    @QtCore.pyqtSlot() 
    def on_actionActive_activated(self):
        self.selEB.activa=self.actionActive.isChecked()
        self.selEB.save()
        self.mem.con.commit()   
        
        #Recoloca en los SetInvestments
        if self.selEB.activa==True:#Está todavía en inactivas
            self.mem.data.ebs_active.arr.append(self.selEB)
            self.mem.data.ebs_inactive.arr.remove(self.selEB)
        else:#Está todavía en activas
            self.mem.data.ebs_active.arr.remove(self.selEB)
            self.mem.data.ebs_inactive.arr.append(self.selEB)
        
        self.load_eb()
