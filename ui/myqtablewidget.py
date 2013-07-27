import configparser
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from libxulpymoney import *

class myQTableWidget(QTableWidget):
    def __init__(self, parent):
        QTableWidget.__init__(self, parent)
        self.mytimer = QTimer()
        self.file=None
        self.section=None
        self.inisettings=[]    
        self.verticalHeader().setResizeMode(QHeaderView.ResizeToContents)

        QObject.connect(self.mytimer, SIGNAL("timeout()"), self.checksettings)        
        
    def __del__(self):
#        print ("Parando el timer por destrucción de myqtablewidget")
        self.mytimer.stop()
        
    def settings(self, section,  file):		
        """Esta funcion debe ejecutarse despues de haber creado las columnas
        If section=NOne and file=None, se usa resizemode por defecto
        """
        if section==None and file==None:
            self.horizontalHeader().setResizeMode(QHeaderView.ResizeToContents)
            
        else:
            self.file=file
            self.section=section
            self.inisettings=self.qtablewidget_loadprops(  self,  self.section,  self.file)
            self.mytimer.start(5000)
        
    def checksettings(self):
        if self.inisettings==[]:#si no hay settings
            self.savesettings()           
        for i in range(self.columnCount()):
            if self.columnWidth(i)!=self.inisettings[i]:
                self.savesettings()
                print (self.file,self.section, "settings saved")
                return
                
 
    def savesettings(self):
        self.qtablewidget_saveprops(  self,  self.section, self.file)    
        self.inisettings=self.qtablewidget_loadprops(  self,  self.section,  self.file)

    
    def qtablewidget_loadprops( self,  table,  section,  file):
        config = configparser.ConfigParser()
        config.read(file)
        resultado=[]
        try:
            for i in range (table.columnCount()):
                table.setColumnWidth(i, config.getint(section, (table.objectName())+'_column'+str(i)) )
                resultado.append(config.getint(section, (table.objectName())+'_column'+str(i)))
            return resultado
        except:
            print (QApplication.translate("Core",("No hay fichero de configuración")    ))
            return []
    
    
    def qtablewidget_saveprops(self,  table,  section, file):
        config = configparser.ConfigParser()
        config.read(file)
    #    print config.has_section(section)
        if config.has_section(section)==False:
            config.add_section(section)
        
        for i in range (table.columnCount()):
    #        config.remove_option(section, (table.objectName())+'_column'+str(i))
            config.set(section,  (table.objectName())+'_column'+str(i), str(table.columnWidth(i)))
        # Writing our configuration file to 'example.cfg'
        with open(file, 'w') as configfile:
            config.write(configfile)
