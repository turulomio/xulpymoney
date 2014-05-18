from PyQt4.QtCore import *
from PyQt4.QtGui import *
from libxulpymoney import *
from Ui_frmTablasAuxiliares import *

class frmTablasAuxiliares(QDialog, Ui_frmTablasAuxiliares):
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

        self.tblConceptos.settings(None,  self.mem)
        
        self.mem.tiposoperaciones.qcombobox_basic(self.cmbOperationType)
        self.selConcepto=None
        self.conceptos=[]
        for c in self.mem.conceptos.list():
            if c.editable==True:
                self.conceptos.append(c)
 
        self.tblConceptos_reload()
        

    @QtCore.pyqtSlot()  
    def on_actionConceptAdd_activated(self):
        self.tblConceptos.clearSelection()
        self.grpConcept.setEnabled(True)
        self.cmbOperationType.setEnabled(True)
        self.selConcepto=Concepto(self.mem).init__create(self.tr("Add a concept"), self.mem.tiposoperaciones.find(1), True)
        self.txtConcept.setText(self.selConcepto.name)
        self.cmbOperationType.setCurrentIndex(0)

    @QtCore.pyqtSlot()  
    def on_actionConceptDelete_activated(self):
        borrado=self.selConcepto.borrar()
        if borrado:
            self.mem.con.commit()
            self.conceptos.remove(self.selConcepto)
            self.tblConceptos.clearSelection()
            self.selConcepto=None
            self.grpConcept.setEnabled(False)
            self.tblConceptos_reload()
            
        
    def on_cmdSaveConcept_released(self):
        isnew=False
        if self.selConcepto.id==None:
            isnew=True
        self.selConcepto.name=self.txtConcept.text()
        self.selConcepto.tipooperacion=self.mem.tiposoperaciones.find(self.cmbOperationType.itemData(self.cmbOperationType.currentIndex()))
        self.selConcepto.editable=True
        self.selConcepto.save()
        self.mem.con.commit()
        if isnew:
            self.conceptos.append(self.selConcepto)
            self.cmbOperationType.setEnabled(False)
        self.tblConceptos_reload()
        

       
    def on_tblConceptos_customContextMenuRequested(self,  pos):
        if self.selConcepto==None:
            self.actionConceptDelete.setEnabled(False)
        else:
            self.actionConceptDelete.setEnabled(True)
        
        menu=QMenu()
        menu.addAction(self.actionConceptAdd)
        menu.addAction(self.actionConceptDelete)
        menu.exec_(self.tblConceptos.mapToGlobal(pos))

    def on_tblConceptos_itemSelectionChanged(self):
        try:
            for i in self.tblConceptos.selectedItems():#itera por cada item no row.
                self.selConcepto=self.conceptos[i.row()]
        except:
            self.selConcepto=None
        if self.selConcepto==None:      
            self.grpConcept.setEnabled(False)
        else:
            self.grpConcept.setEnabled(True)
            self.cmbOperationType.setEnabled(False)
            self.txtConcept.setText(self.selConcepto.name)
            self.cmbOperationType.setCurrentIndex(self.cmbOperationType.findData(self.selConcepto.tipooperacion.id))
        
        
    def tblConceptos_reload(self):
        self.tblConceptos.setRowCount(len(self.conceptos));
        for i, c in enumerate(self.conceptos):
            self.tblConceptos.setItem(i, 0, QTableWidgetItem(c.name))
            self.tblConceptos.setItem(i, 1, QTableWidgetItem(c.tipooperacion.name))

        
        
        
