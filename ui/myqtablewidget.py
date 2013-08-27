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
 
        
    def __del__(self):
        self.mytimer.stop()
        
    def settings(self, section,  cfg):		
        """Esta funcion debe ejecutarse despues de haber creado las columnas
        If section=NOne and file=None, se usa resizemode por defecto
        """
        self.cfg=cfg
        if section==None and file==None:
            self.horizontalHeader().setResizeMode(QHeaderView.ResizeToContents)
        else:
            self.section=section
            self.columnswidth_in_config=self.cfg.config_ui.get_list( self.section,   self.objectName()+"_columns_width")
            if len(self.columnswidth_in_config)==self.columnCount():
                for i in range(self.columnCount()):
                    self.setColumnWidth(i, int(self.columnswidth_in_config[i]))
            self.mytimer.start(5000)
        QObject.connect(self.mytimer, SIGNAL("timeout()"), self.checksettings)       
        
    def checksettings(self):
        ##Si est´a vacio columnswidth_in_config lo carga y guarda en settings
        
        if len(self.columnswidth_in_config)==0:#si no hay settings primera vez
            self.save_columns()
            return 
            
        if len(self.columnswidth_in_config)!=self.columnCount():
            self.save_columns
            return
            
        ##Comprueba que no se hayan movido las columnas y si se han movido lo guarda
        for i in range(self.columnCount()):
            if self.columnWidth(i)!=int(self.columnswidth_in_config[i]):
                self.save_columns()
                return


    def save_columns(self):
        del self.columnswidth_in_config
        self.columnswidth_in_config=[]
        for i in range(self.columnCount()):#Genera array
            self.columnswidth_in_config.append(str(self.columnWidth(i)))
        if len(self.columnswidth_in_config)>0:#No grabe si no hay columnas
            self.cfg.config_ui.set_list(self.section, self.objectName()+"_columns_width", self.columnswidth_in_config)
            self.cfg.config_ui.save()
            print (self.section, self.objectName(), "columns width saved")

