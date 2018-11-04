from PyQt5.QtWidgets import QDialog, QTableWidgetItem
from xulpymoney.ui.Ui_frmSelector import Ui_frmSelector
from xulpymoney.libxulpymoneyfunctions import qmessagebox

class frmSelector(QDialog, Ui_frmSelector):
    def __init__(self, mem, set,  selectedset, name = None, modal = False  ):
        """Lista es un objeto tipo set cuyos objetos agrupados tienen id y name
        Selected es otro objeto set"""
        QDialog.__init__(self)
        self.setupUi(self)   
        self.mem=mem
        self.selected=selectedset
        self.set=set
        
        tmpset=self.set.clone(self.mem)##Lo uso para no borrar mientras itero sale error
        for a in tmpset.arr:
            if self.selected.find_by_id(a.id)!=None:
                self.set.remove(a)
        
        self.load_tbl()
        self.load_tblSelected()

    def load_tblSelected(self):        
        self.tblSelected.setRowCount(self.selected.length())
        for i, l in enumerate(self.selected.arr):
            try:
                self.tblSelected.setItem(i, 0, QTableWidgetItem(str(l.id)))
                self.tblSelected.setItem(i, 1, QTableWidgetItem(l.name))
            except:
                qmessagebox(self.tr("This dialog got unknown selected data ({0}), select it again").format(str(self.selected)))
    
                self.selected=[]
                self.load_tbl()
                self.load_tblSelected()
                break
        
    def load_tbl(self):
        self.tbl.setRowCount(self.set.length())
        for i, l in enumerate(self.set.arr):
                self.tbl.setItem(i, 0, QTableWidgetItem(str(l.id)))
                self.tbl.setItem(i, 1, QTableWidgetItem(l.name))

    def on_cmdLeft_released(self):
        try:
            for i in self.tbl.selectedItems():
                self.set.selected=self.set.arr[i.row()]
            self.selected.append(self.set.selected)
            self.set.remove(self.set.selected)
        except:
            return
        self.load_tbl()
        self.load_tblSelected()
        
    def on_cmdRight_released(self):        
        try:
            for i in self.tblSelected.selectedItems():
                self.selected.selected=self.selected.arr[i.row()]
            self.set.append(self.selected.selected)       
            self.selected.remove(self.selected.selected) 
        except:
            return
        self.load_tbl()
        self.load_tblSelected()
        
        
    def on_cmd_released(self):
        self.done(0)
        
    def on_cmdUp_released(self):
        pos=None
        for i in self.tblSelected.selectedItems():
            pos=i.row()
        tmp=self.selected.arr[pos]
        self.selected.arr[pos]=self.selected.arr[pos-1]
        self.selected.arr[pos-1]=tmp
        self.load_tbl()
        self.load_tblSelected()             
        
    def on_cmdDown_released(self):
        pos=None
        for i in self.tblSelected.selectedItems():
            pos=i.row()
        tmp=self.selected.arr[pos+1]
        self.selected.arr[pos+1]=self.selected.arr[pos]
        self.selected.arr[pos]=tmp
        self.load_tbl()
        self.load_tblSelected()        
        
    def on_tbl_cellDoubleClicked(self, row, column):
        self.on_cmdLeft_released()
        
    def on_tblSelected_cellDoubleClicked(self, row, column):
        self.on_cmdRight_released()
        
