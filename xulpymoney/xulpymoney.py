#!/usr/bin/python3
import sys,  os

sys.path.append("/usr/lib/xulpymoney")

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from frmMain import *
    
try:
    os.makedirs( os.environ['HOME']+"/.xulpymoney/")
except:
    pass
    
#Creamos la aplicacion principal y conectamos la señal lastWindowClosed()
#(ultima ventana cerrada) con la funcion quit() (salir de la aplicacion)
app = QApplication(sys.argv)
QTextCodec.setCodecForTr(QTextCodec.codecForName("UTF-8"));
#for k, v in globals().items():             
#    print ("GOLABAS", k, "=", v)

translator = QTranslator(app)
locale=QLocale()
a=locale.system().name()
if len(a)!=2:
    a=a[:-len(a)+2]
s= QApplication.translate("xulpymoney.py",  "Lenguage local detectado: {0}".format(a))
print (s)
translator.load("/usr/lib/xulpymoney/xulpymoney_" + a + ".qm")
app.installTranslator(translator);

frmMain = frmMain() 
frmMain.show()

sys.exit(app.exec_())
