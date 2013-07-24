from PyQt4.QtCore import *
from PyQt4.QtGui import *
from decimal import Decimal

class myQLineEdit(QLineEdit):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.selected=None
        self.connect(self,SIGNAL('textChanged(QString)'), self.on_textChanged)
        
    @pyqtSignature("")
    def on_textChanged(self, text):
        text=text.replace(",", ".")
        text=text.strip()
        self.setText(text)
        css=""
        try:
            Decimal(text)
        except:
            css = """QLineEdit { background-color: rgb(255, 182, 182); }"""
        self.setStyleSheet(css)

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
