from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Ui_frmSelector import *
from libxulpymoney import *

class frmSelector(QDialog, Ui_frmSelector):
    def __init__(self, cfg, set,  selectedset, name = None, modal = False  ):
        """Lista es un objeto tipo set cuyos objetos agrupados tienen id y name
        Selected es otro objeto set"""
        QDialog.__init__(self)
        self.setupUi(self)   
        self.cfg=cfg
        self.selected=selectedset
        self.set=set
        for k, a in self.set.dic_arr.items():
            if k in self.selected.dic_arr:
                del self.set.dic_arr[k]
        self.load_tbl()
        self.load_tblSelected()
        
    def load_tblSelected(self):        
        self.tblSelected.setRowCount(len(self.selected.dic_arr))
        for i, l in enumerate(self.selected.list()):
            try:
                self.tblSelected.setItem(i, 0, QTableWidgetItem(str(l.id)))
                self.tblSelected.setItem(i, 1, QTableWidgetItem(l.name))
            except:
                m=QMessageBox()
                m.setText(self.trUtf8("Se han pasado datos seleccionados no reconocidos({0}), vuelva a seleccionarlos".format(str(self.selected))))
                m.exec_()        
                self.selected=[]
                self.load_tbl()
                self.load_tblSelected()
                break
        
    def load_tbl(self):
        print (len(self.set.dic_arr))
        self.tbl.setRowCount(len(self.set.dic_arr))
        for i, l in enumerate(self.set.list()):
                self.tbl.setItem(i, 0, QTableWidgetItem(str(l.id)))
                self.tbl.setItem(i, 1, QTableWidgetItem(l.name))

    def on_cmdLeft_released(self):
        try:
            for i in self.tbl.selectedItems():
                sel=self.set.dic_arr[i.row()]
        except:
            return
        self.selected.append(sel)
        self.lista.remove(sel)
        self.load_tbl()
        self.load_tblSelected()
        
    def on_cmdRight_released(self):
        try:
            for i in self.tblSelected.selectedItems():
                sel=self.selected[i.row()]
        except:
            return
        self.selected.remove(sel)
        self.lista.append(sel)        
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
        
