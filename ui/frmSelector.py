from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Ui_frmSelector import *
from libxulpymoney import *

class frmSelector(QDialog, Ui_frmSelector):
    def __init__(self, mem, set,  selectedset, name = None, modal = False  ):
        """Lista es un objeto tipo set cuyos objetos agrupados tienen id y name
        Selected es otro objeto set"""
        QDialog.__init__(self)
        self.setupUi(self)   
        self.mem=mem
        self.selected=selectedset
        self.set=set
        
        tmpset=self.set.clone()##Lo uso para no borrar mientras itero sale error
        #¢arga datos y desactiva botones
        if self.typeofset()==1:#dic
            self.cmdDown.setEnabled(False)
            self.cmdUp.setEnabled(False)
            for k,  v in tmpset.dic_arr.items():
                if  k in self.selected.dic_arr:
                    del self.set.dic_arr[k]            
        else:#list
            self.cmdDown.setEnabled(True)
            self.cmdUp.setEnabled(True)
        
        self.load_tbl()
        self.load_tblSelected()
        
        
    def typeofset(self):
        """Returns 1 si es diccionario y 2 si es un list set"""
        try:
            len(self.set.dic_arr)
            return 1
        except:
            return 2
        
        
    def load_tblSelected(self):        
        if self.typeofset()==1:#dic
            lista=self.selected.list()
        else:
            lista=self.selected.arr
        self.tblSelected.setRowCount(len(lista))
        for i, l in enumerate(lista):
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
        if self.typeofset()==1:#dic
            lista=self.set.list()
        else:
            lista=self.set.arr
        self.tbl.setRowCount(len(lista))
        for i, l in enumerate(lista):
                self.tbl.setItem(i, 0, QTableWidgetItem(str(l.id)))
                self.tbl.setItem(i, 1, QTableWidgetItem(l.name))

    def on_cmdLeft_released(self):
        if self.typeofset()==1:# dict
            try:
                for i in self.tbl.selectedItems():
                    key=self.tbl.item(i.row(),0).text()
                sel=self.set.dic_arr[key]
                self.selected.dic_arr[key]=sel
                del self.set.dic_arr[key]
            except:
                return
        else:#lista
            try:
                for i in self.tbl.selectedItems():
                    sel=self.set.arr[i.row()]
                self.selected.arr.append(sel)
                self.set.arr.remove(sel)
            except:
                return
        self.load_tbl()
        self.load_tblSelected()
        
    def on_cmdRight_released(self):        
        if self.typeofset()==1:# dict
            try:
                for i in self.tblSelected.selectedItems():
                    key=self.tblSelected.item(i.row(), 0).text()
                sel=self.selected.dic_arr[key]
                self.set.dic_arr[key]=sel
                del self.selected.dic_arr[key]
            except:
                return
        else:#lista
            try:
                for i in self.tblSelected.selectedItems():
                    sel=self.selected.arr[i.row()]
                self.set.arr.append(sel)       
                self.selected.arr.remove(sel) 
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
        
