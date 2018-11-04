from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QLineEdit, QWidget
from decimal import Decimal

class myQLineEdit(QLineEdit):
    doubleClicked=pyqtSignal()
    def __init__(self, parent):
        QWidget.__init__(self, parent)       
#        self.setValidator(QDoubleValidator(self)) ##Failed to show point from numerical pad
        self.textChanged.connect(self.on_textChanged)
        self.setMaxLength(30)
        
        
    def isValid(self):
        """Devuelve si el textedit es un float o un decimal valido"""
        if self.decimal()==None:
            return False
        return True
            
    def setBackgroundRed(self, red):
        if red==True:
            css = """QLineEdit { background-color: rgb(255, 182, 182); }"""
        else:
            css=""
        self.setStyleSheet(css)
 
    @pyqtSlot(str)
    def on_textChanged(self, text):
        pos=self.cursorPosition()
        text=text.replace(",", ".")
        text=text.replace("e", "0")#Avoids scientific numbers
        self.setText(text)
        if self.isValid():        
            self.setBackgroundRed(False)
        else:
            self.setBackgroundRed(True)
        self.setCursorPosition(pos)     
        
#    def keyReleaseEvent(self, event):
#        super(myQLineEdit, self).keyReleaseEvent(event)
#        if event.text() in ("0123456789.,"):
#            print("acepted")
#            event.accept()
#            return
#        print ("ignore")
#        print (event.text())
#        event.ignore()
        
    def decimal(self):
        """Devuelve el decimal o un None si hay error"""
        try:
            #Due to database precision (18,6) debe redondear a 10^12
            a=Decimal(self.text())
            if a<Decimal(1000000000000):
                return a
            else:
                return None
        except:
            return None

    def float(self):
        try:
            return float(self.text())
        except:
            return None
            
    def setText(self, num):
        """This funcion  overrides QLineEdit settext and lets enter numbers, int, float, decimals"""
        super(myQLineEdit, self).setText(str(num))
        

    def mouseDoubleClickEvent(self, event):
        print("MOUSEDOUBLECLICKEVENT")
        self.doubleClicked.emit()
        print("EMITEED")
