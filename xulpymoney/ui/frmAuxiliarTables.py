from PyQt5.QtCore import *
from PyQt5.QtGui import *
from libxulpymoney import *
from Ui_frmAuxiliarTables import *

class frmAuxiliarTables(QDialog, Ui_frmAuxiliarTables):
    def __init__(self, mem,  parent = None, name = None, modal = False):
        """
        Constructor
        
        @param parent The parent widget of this dialog. (QWidget)
        @param name The name of this dialog. (QString)
        @param modal Flag indicating a modal dialog. (boolean)
        """
        QDialog.__init__(self,  parent)
        if name:
            self.setObjectName(name)
        self.setModal(True)
        self.setupUi(self)
        self.mem=mem

        self.tblConcepts.settings(self.mem)
        
        self.mem.tiposoperaciones.qcombobox_basic(self.cmbOperationType)
        self.selConcept=None
        self.conceptos=[]
        self.regenerate_list()
        self.tblConcepts_reload()
    
    def regenerate_list(self):
        del self.conceptos
        self.conceptos=[]
        for c in self.mem.conceptos.arr:
            if c.editable==True:
                self.conceptos.append(c)
 
        

    @QtCore.pyqtSlot()  
    def on_actionConceptAdd_triggered(self):
        self.tblConcepts.clearSelection()
        self.grpConcept.setEnabled(True)
        self.cmbOperationType.setEnabled(True)
        self.selConcept=Concept(self.mem).init__create(self.tr("Add a concept"), self.mem.tiposoperaciones.find_by_id(1), True)
        self.txtConcept.setText(self.selConcept.name)
        self.cmbOperationType.setCurrentIndex(0)

    @QtCore.pyqtSlot()  
    def on_actionConceptDelete_triggered(self):
        borrado=self.selConcept.borrar()
        if borrado:
            self.mem.con.commit()
            self.mem.conceptos.remove(self.selConcept)
            self.regenerate_list()
            self.tblConcepts.clearSelection()
            self.selConcept=None
            self.grpConcept.setEnabled(False)
            self.tblConcepts_reload()
            
        
    def on_cmdSaveConcept_released(self):
        isnew=False
        if self.selConcept.id==None:
            isnew=True
        self.selConcept.name=self.txtConcept.text()
        self.selConcept.tipooperacion=self.mem.tiposoperaciones.find_by_id(self.cmbOperationType.itemData(self.cmbOperationType.currentIndex()))
        self.selConcept.editable=True
        self.selConcept.save()
        self.mem.con.commit()
        if isnew:
            self.mem.conceptos.append(self.selConcept)
            self.cmbOperationType.setEnabled(False)
        self.regenerate_list()
        self.tblConcepts_reload()
        

       
    def on_tblConcepts_customContextMenuRequested(self,  pos):
        if self.selConcept==None:
            self.actionConceptDelete.setEnabled(False)
        else:
            self.actionConceptDelete.setEnabled(True)
        
        menu=QMenu()
        menu.addAction(self.actionConceptAdd)
        menu.addAction(self.actionConceptDelete)
        menu.exec_(self.tblConcepts.mapToGlobal(pos))

    def on_tblConcepts_itemSelectionChanged(self):
        try:
            for i in self.tblConcepts.selectedItems():#itera por cada item no row.
                self.selConcept=self.conceptos[i.row()]
        except:
            self.selConcept=None
        if self.selConcept==None:      
            self.grpConcept.setEnabled(False)
        else:
            self.grpConcept.setEnabled(True)
            self.cmbOperationType.setEnabled(False)
            self.txtConcept.setText(self.selConcept.name)
            self.cmbOperationType.setCurrentIndex(self.cmbOperationType.findData(self.selConcept.tipooperacion.id))
        
        
    def tblConcepts_reload(self):
        self.tblConcepts.setRowCount(len(self.conceptos));
        for i, c in enumerate(self.conceptos):
            self.tblConcepts.setItem(i, 0, QTableWidgetItem(c.name))
            self.tblConcepts.setItem(i, 1, QTableWidgetItem(c.tipooperacion.name))

        
        
        
