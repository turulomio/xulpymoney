from PyQt4.QtCore import *
from PyQt4.QtGui import *
from libxulpymoney import *

class myQTableWidget(QTableWidget):
    def __init__(self, parent):
        QTableWidget.__init__(self, parent)
        self.mytimer = QTimer()
        self.section=None
        self.columnswidth_in_config=[]     #Es un array de strings no de int
        self.verticalHeader().setResizeMode(QHeaderView.ResizeToContents)
        QObject.connect(self.mytimer, SIGNAL("timeout()"), self.checksettings)      
 
        
    def __del__(self):
        self.mytimer.stop()
        
    def settings(self, section,  mem):		
        """Esta funcion debe ejecutarse despues de haber creado las columnas
        If section=NOne and file=None, se usa resizemode por defecto
        """
        self.mem=mem
        self.section=section
        if self.mytimer.isActive():
            self.mytimer.stop()
        print ("settings", section, self.objectName())
#            
#        if section==None:
#            self.horizontalHeader().setResizeMode(QHeaderView.ResizeToContents)
#            self.resizeColumnsToContents()
#            self.mytimer.stop()
#        else:
        self.horizontalHeader().setResizeMode(QHeaderView.Interactive)
        self.columnswidth_in_config=self.mem.config_ui.get_list( self.section,   self.objectName()+"_columns_width")
        
        #Checks if config has same columns as qtable and resizes the table
        if len(self.columnswidth_in_config)==self.columnCount():
            for i in range(self.columnCount()):
                self.setColumnWidth(i, int(self.columnswidth_in_config[i]))
        self.mytimer.start(5000) 
        
    def checksettings(self):
        ##Si está vacio columnswidth_in_config lo carga y guarda en settings
        if self.section==None:# No graba
            return
            
        if len(self.columnswidth_in_config)==0:#si no hay settings primera vez
            print (self.section, self.objectName(), "myQTableWidget. No columns in config. Saving table width")            
            self.save_columns()
            return 
            
        if len(self.columnswidth_in_config)!=self.columnCount():
            print (self.section, self.objectName(), "myQTableWidget. Diferent config columns and table columns. Saving table columns")
            self.save_columns()
            return
            
        ##Comprueba que no se hayan movido las columnas y si se han movido lo guarda
        for i in range(self.columnCount()):
            if self.columnWidth(i)!=int(self.columnswidth_in_config[i]):
                print (self.section, self.objectName(), "myQTableWidget. Saving moved columns")
                self.save_columns()
                break


    def save_columns(self):
        del self.columnswidth_in_config
        self.columnswidth_in_config=[]
        for i in range(self.columnCount()):#Genera array
            self.columnswidth_in_config.append(str(self.columnWidth(i)))
        self.mem.config_ui.set_list(self.section, self.objectName()+"_columns_width", self.columnswidth_in_config)
        self.mem.config_ui.save()
            
            
    def verticalScrollbarAction(self,  action):
        for i in range(self.columnCount()):
            if self.sizeHintForColumn(i)>self.columnWidth(i):
                self.setColumnWidth(i, self.sizeHintForColumn(i))
#        self.resizeColumnsToContents()
        
    def mouseDoubleClickEvent(self, event):
        self.resizeColumnsToContents()
