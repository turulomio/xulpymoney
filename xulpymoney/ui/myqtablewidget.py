from PyQt4.QtCore import *
from PyQt4.QtGui import *
from libxulpymoney import *

class myQTableWidget(QTableWidget):
    def __init__(self, parent):
        QTableWidget.__init__(self, parent)
        self.mytimer = QTimer()
        self.section=None
        self.array=[]     #Es un array de strings no de int, con los datos para config
        self.verticalHeader().setResizeMode(QHeaderView.ResizeToContents)
        QObject.connect(self.mytimer, SIGNAL("timeout()"), self.checksettings)      
 
        
    def __del__(self):
        self.mytimer.stop()
        
    def settings(self, section,  mem):		
        """Esta funcion debe ejecutarse despues de haber creado las columnas
        If section=NOne and file=None, se usa resizemode por defecto
        """
        self.section=section        
        self.mem=mem
        if self.mytimer.isActive():#Can't be call settings by error in automatic common qtablewidgets
            self.mytimer.stop()
        
        self.horizontalHeader().setResizeMode(QHeaderView.Interactive)
        self.array=self.mem.config_ui.get_list( self.section,   self.objectName()+"_columns_width")
        
        #Checks if config has same columns as qtable and resizes the table
        if len(self.array)==self.columnCount():
            self.array2columns()
        else:#Se coloca en array
            self.columns2array()
        self.mytimer.start(5000) 
        
    def checksettings(self):
        ##Si está vacio array lo carga y guarda en settings
        if self.section==None:# No graba
            return
            
        ##Comprueba que no se hayan movido las columnas y si se han movido lo guarda
        for i in range(self.columnCount()):
            if self.columnWidth(i)!=int(self.array[i]):
                self.save_columns()
                break

    def columns2array(self):
        """Adds in array real columns with in table"""
        del self.array
        self.array=[]
        for i in range(self.columnCount()):#Genera array
            self.array.append(str(self.columnWidth(i)))
            
    def array2columns(self):
        """Gives columns array size"""
        for i in range(self.columnCount()):
            self.setColumnWidth(i, int(self.array[i]))        


    def save_columns(self):
        """Saves column status to array and to config"""
        self.columns2array()
        self.mem.config_ui.set_list(self.section, self.objectName()+"_columns_width", self.array)
        self.mem.config_ui.save()
        print ("- Saved {0} columns size in {1} to {2}".format(self.objectName(), self.section, self.array))
            
            
    def verticalScrollbarAction(self,  action):
        """Resizes columns if column width is less than table hint"""
        for i in range(self.columnCount()):
            if self.sizeHintForColumn(i)>self.columnWidth(i):
                self.setColumnWidth(i, self.sizeHintForColumn(i))
        
    def mouseDoubleClickEvent(self, event):
        """Resizes to minimum contents"""
        self.resizeColumnsToContents()
