from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog, QMenu, QInputDialog
from xulpymoney.objects.concept import Concept, ConceptManager_editables
from xulpymoney.ui.myqwidgets import qmessagebox
from xulpymoney.ui.Ui_frmAuxiliarTables import Ui_frmAuxiliarTables

class frmAuxiliarTables(QDialog, Ui_frmAuxiliarTables):
    def __init__(self, mem,  parent = None, name = None, modal = False):
        QDialog.__init__(self,  parent)
        if name:
            self.setObjectName(name)
        self.setModal(True)
        self.setupUi(self)
        self.mem=mem

        self.mqtwConcepts.setSettings(self.mem.settings, "frmAuxiliarTables", "mqtwConcepts")
        self.mqtwConcepts.table.customContextMenuRequested.connect(self.on_mqtwConcepts_table_customContextMenuRequested)
        self.regenerate_list()
        self.mqtwConcepts_reload()
    
    def regenerate_list(self):
        self.concepts=ConceptManager_editables(self.mem)

    @pyqtSlot()  
    def on_actionChangeName_triggered(self):
        t=QInputDialog().getText(self,  "Xulpymoney",  self.tr("Change name"))
        if t[1]==True:
            self.mqtwConcepts.selected.name=t[0]
            self.mqtwConcepts.selected.save()
            self.mem.con.commit()
            self.mem.conceptos.order_by_name()
            self.regenerate_list()
            self.mqtwConcepts_reload()

    @pyqtSlot()  
    def on_actionExpensesAdd_triggered(self):
        t=QInputDialog().getText(self,  "Xulpymoney",  self.tr("Add a new expense concept"))
        if t[1]==True:
            concepto=Concept(self.mem, t[0], self.mem.tiposoperaciones.find_by_id(1), True, None)
            concepto.save()
            self.mem.con.commit()
            self.mem.conceptos.append(concepto)
            self.mem.conceptos.order_by_name()
            self.regenerate_list()
            self.mqtwConcepts_reload()

    @pyqtSlot()  
    def on_actionIncomesAdd_triggered(self):
        t=QInputDialog().getText(self,  "Xulpymoney",  self.tr("Add a new income concept"))
        if t[1]==True:
            concepto=Concept(self.mem, t[0], self.mem.tiposoperaciones.find_by_id(2), True, None)
            concepto.save()
            self.mem.con.commit()
            self.mem.conceptos.append(concepto)
            self.mem.conceptos.order_by_name()
            self.regenerate_list()
            self.mqtwConcepts_reload()

    @pyqtSlot()  
    def on_actionConceptDelete_triggered(self):
        if self.mqtwConcepts.selected.borrar():
            self.mem.con.commit()
            self.mem.conceptos.remove(self.mqtwConcepts.selected)
            self.regenerate_list()
            self.mqtwConcepts.table.clearSelection()
            self.mqtwConcepts.selected=None
            self.mqtwConcepts_reload()
        else:
            qmessagebox(self.tr("This concept can't be deleted"))

    def on_mqtwConcepts_table_customContextMenuRequested(self,  pos):
        if self.mqtwConcepts.selected==None:
            self.actionChangeName.setEnabled(False)
            self.actionConceptDelete.setEnabled(False)
        else:
            self.actionChangeName.setEnabled(True)
            self.actionConceptDelete.setEnabled(True)
        
        menu=QMenu()
        menu.addAction(self.actionExpensesAdd)
        menu.addAction(self.actionIncomesAdd)
        menu.addAction(self.actionChangeName)
        menu.addAction(self.actionConceptDelete)
        menu.addSeparator()
        menu.addMenu(self.mqtwConcepts.qmenu())
        menu.exec_(self.mqtwConcepts.table.mapToGlobal(pos))

    def mqtwConcepts_reload(self):
        self.concepts.mqtw(self.mqtwConcepts)
