from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from myqlineedit import myQLineEdit
from libxulpymoney import Money

class wdgCurrencyConversion(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        lay = QHBoxLayout(self)
        self.txt=myQLineEdit(self)
        self.cmd= QToolButton(self)               
        icon = QIcon()
        icon.addPixmap(QPixmap(":/xulpymoney/add.png"), QIcon.Normal, QIcon.Off)
        self.cmd.setIcon(icon)     
        lay.addWidget(self.txt)
        lay.addWidget(self.cmd)

    def setConversion(self, mem, from_currency, to_currency, dt, example):
        """Llena el texto con los datos de la conversi´on"""
        self.mem=mem
        self.mfrom=Money(self.mem, example, from_currency)
        self.txt.setText(self.mfrom.conversionFactor(to_currency, dt))
        self.txt.setToolTip(self.tr("Factor conversion from {} to {} at {}. So {} are {}.".format(from_currency.id, to_currency.id, dt, self.mfrom, self.mfrom.convert_from_datetime(to_currency, dt))))

    def setBackgroundRed(self, red):
        if red==True:
            css = """QLineEdit { background-color: rgb(255, 182, 182); }"""
        else:
            css=""
        self.setStyleSheet(css)
 
        
    def decimal(self):
        """Devuelve el decimal o un None si hay error"""
        try:
            return Decimal(self.text())
        except:
            return None

    def setText(self, num):
        """This funcion  overrides QLineEdit settext and lets enter numbers, int, float, decimals"""
        super(myQLineEdit, self).setText(str(num))
        
