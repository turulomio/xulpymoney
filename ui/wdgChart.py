#from PyQt4.QtCore import *
#from PyQt4.QtGui import *
#from Ui_wdgChart import *
#from libxulpymoney import *
#
#class wdgChart(QWidget, Ui_wdgChart):
#    def __init__(self, cfg,    parent=None):
#        QWidget.__init__(self, parent)
#        self.setupUi(self)
#        self.cfg=cfg
#            
#    def setTitle(self, title):
#        if title==None or title=="":
#            self.title.hide()
#        self.canvas.title.setText(title)
#        
#    def carga_combos(self, length,  variosdias): #Puede ser 2 o 6
#        self.cmbType.clear()
#        self.cmbPeriodo.clear()
#        type={}
#        type["0"]="Líneas"
#        type["1"]="OHCL"
#        type["2"]="Velas"
#            
#        periodo={}                
#        periodo["3"]="Diario" 
#        periodo["0"]="Tic by Tic"
#        
#        if length==6:
#            del periodo["0"]
#        
#        if length==2:
#            if variosdias==False:
#                del periodo['3']   
#        
#        for k,  v in periodo.items():
#            self.cmbPeriodo.addItem(v, k)
#        for k, v in type.items():
#            self.cmbType.addItem(v, k)
#    def setPeriodo(self, periodo):
#        self.cmbPeriodo.setCurrentIndex(self.cmbPeriodo.findData(str(periodo)))
#        self.canvas.periodo=periodo
#        
#    def setType(self, type):
#        self.cmbType.setCurrentIndex(self.cmbType.findData(str(type)))
#        self.canvas.type=type
#    
#    def on_cmd_released(self):
#        self.setType(int(self.cmbType.itemData(self.cmbType.currentIndex())))
#        self.setPeriodo(int(self.cmbPeriodo.itemData(self.cmbPeriodo.currentIndex())))
#        self.canvas.mydraw()
#    
#    def load_data(self,  data):
#        """Función que actua dependiendo de la longitud de datos que recibe"""
#        def varios_dias(data):
#            if len(data)==0:
#                return False
#            if len(data[0])==6:
#                return True
#            elif len(data[0])==2:
#                (datetimes, quotes)=zip(*data)
#                first=datetimes[0].date()
#                for dt in datetimes:
#                    if dt.date()!=first:
#                        return True
#                return False
#                
#                
#        variosdias=varios_dias(data)
#        if len(data[0])==6:
#            #Carga posibles graficos
#            print ("datos tipo ochl")
#            self.carga_combos(6, variosdias)
#            self.setPeriodo(3)
#            self.setType(0)
#        elif len(data[0])==2:
#            print ("datos tipo dt,  value")
#            self.carga_combos(2, variosdias)
#            if variosdias==True:
#                self.setPeriodo(0)
#            else:
#                self.setPeriodo(0)
#            self.setType(0)
#        self.canvas.load_data(self.cfg, data)
#            
