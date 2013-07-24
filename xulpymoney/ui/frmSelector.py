from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Ui_frmSelector import *
from libxulpymoney import *

class frmSelector(QDialog, Ui_frmSelector):
    def __init__(self, cfg, lista,  selected, name = None, modal = False  ):
        """Lista es un objeto tipo set cuyos objetos agrupados tienen id y name
        Selected es otro objeto set"""
        QDialog.__init__(self)
        self.setupUi(self)   
        self.cfg=cfg
        self.selected=selected
        self.lista=lista
        for a in lista.arr:
            if a  in selected.arr:
                self.lista.arr.remove(a)

        self.load_tbl()
        self.load_tblSelected()
        
    def load_tblSelected(self):        
        self.tblSelected.setRowCount(len(self.selected.arr))
        for i, l in enumerate(self.selected.arr):
            try:
                self.tblSelected.setItem(i, 0, QTableWidgetItem(str(l.id)))
                self.tblSelected.setItem(i, 1, QTableWidgetItem(l.name))
            except:
                m=QMessageBox()
                m.setText(self.trUtf8("Se han pasado datos seleccionados no reconocidos({0}), vuelva a seleccionarlos".format(str(self.selected))))
                m.exec_()        
                self.selected.arr=[]
                self.load_tbl()
                self.load_tblSelected()
                break
        
    def load_tbl(self):
        self.tbl.setRowCount(len(self.lista.arr))
        for i, l in enumerate(self.lista.arr):
                self.tbl.setItem(i, 0, QTableWidgetItem(str(l.id)))
                self.tbl.setItem(i, 1, QTableWidgetItem(l.name))

    def on_cmdLeft_released(self):
        try:
            for i in self.tbl.selectedItems():
                sel=self.lista.arr[i.row()]
        except:
            return
        self.selected.arr.append(sel)
        self.lista.arr.remove(sel)
        self.load_tbl()
        self.load_tblSelected()
        
    def on_cmdRight_released(self):
        try:
            for i in self.tblSelected.selectedItems():
                sel=self.selected.arr[i.row()]
        except:
            return
        self.selected.arr.remove(sel)
        self.lista.arr.append(sel)        
        self.load_tbl()
        self.load_tblSelected()
        
        
    def on_cmd_released(self):
        self.done(0)
        
    def on_cmdUp_released(self):
        pos=None
        for i in self.tblSelected.selectedItems():
            pos=i.row()
        tmp=self.selected[pos]
        self.selected[pos]=self.selected[pos-1]
        self.selected[pos-1]=tmp
        self.load_tbl()
        self.load_tblSelected()             
        
    def on_cmdDown_released(self):
        pos=None
        for i in self.tblSelected.selectedItems():
            pos=i.row()
        tmp=self.selected[pos+1]
        self.selected[pos+1]=self.selected[pos]
        self.selected[pos]=tmp
        self.load_tbl()
        self.load_tblSelected()        
        
    def on_tbl_cellDoubleClicked(self, row, column):
        self.on_cmdLeft_released()
        
    def on_tblSelected_cellDoubleClicked(self, row, column):
        self.on_cmdRight_released()
        
