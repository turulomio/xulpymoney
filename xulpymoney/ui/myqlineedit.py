from PyQt4.QtCore import *
from PyQt4.QtGui import *
from decimal import Decimal

class myQLineEdit(QLineEdit):
    def __init__(self, parent):
        QWidget.__init__(self, parent)       
        self.setValidator(QDoubleValidator(self))
        self.setMaxLength(12)
        self.connect(self,SIGNAL('textChanged(QString)'), self.on_textChanged)
        
        
    def isValid(self):
        """Devuelve si el textedit es un float o un decimal valido"""
        try:
            Decimal(self.text())
            return True
        except:
            return False
        
    @pyqtSignature("")
    def on_textChanged(self, text):
        pos=self.cursorPosition()
        text=text.replace(",", ".")
        text=text.replace("e", "0")#Avoids scientific numbers
        self.setText(text)
        if self.isValid():        
            css=""
        else:
            css = """QLineEdit { background-color: rgb(255, 182, 182); }"""
        self.setStyleSheet(css)
        self.setCursorPosition(pos)

    def decimal(self):
        """Devuelve el decimal o un None si hay error"""
        try:
            return Decimal(self.text())
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
        
