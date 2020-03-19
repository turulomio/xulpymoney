from PyQt5.QtWidgets import QWidget, QHBoxLayout, QToolButton, QInputDialog, QLineEdit, QSizePolicy
from PyQt5.QtGui import QIcon, QPixmap
from xulpymoney.ui.myqlineedit import myQLineEdit
from decimal import Decimal

class wdgCurrencyConversion(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        lay = QHBoxLayout(self)
        self.txt=myQLineEdit(self)       
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.txt.sizePolicy().hasHeightForWidth())
        self.txt.setSizePolicy(sizePolicy)
        self.txt.setReadOnly(True)
        self.cmd= QToolButton(self)             
        self.cmd.released.connect(self.on_cmd_released)
        icon = QIcon()
        icon.addPixmap(QPixmap(":/xulpymoney/add.png"), QIcon.Normal, QIcon.Off)
        self.cmd.setIcon(icon)     
        lay.addWidget(self.txt)
        lay.addWidget(self.cmd)

    def setConversion(self, mfrom, tcurrency, dt, factor=None):
        """Llena el texto con los datos de la conversión. Can be invoked several times
        Si se pasa el parametro factor, ya se calculan los datos, Se usa para modificaciones"""
        self.mem=mfrom.mem
        self.mfrom=mfrom
        self.tcurrency=tcurrency
        self.dt=dt
        if factor==None:
            self.factor=self.mfrom.conversionFactor(tcurrency, dt)
        else:
            self.factor=factor
        self.txt.setText(self.mfrom.convert_from_factor(tcurrency, self.factor).amount)
        self.txt.setToolTip(self.tr("Factor conversion from {} to {} at {} is {}. So {} are {}.".format(self.mfrom.currency, tcurrency, dt, self.factor,  self.mfrom, self.mfrom.convert_from_factor(tcurrency, self.factor))))

    def decimal(self):
        return self.txt.decimal()
 
    def on_cmd_released(self):
        if self.factor==None:
            input=QInputDialog.getText(self,  "Xulpymoney",  self.tr("Please introduce the relation between {} and {}. To help you I set value at {}.".format(self.mfrom.currency, self.tcurrency, self.dt)), QLineEdit.Normal, str(self.mfrom.conversionFactor(self.tcurrency, self.dt)))
        else:
            input=QInputDialog.getText(self,  "Xulpymoney",  self.tr("Please change relation between {} and {} if necessary".format(self.mfrom.currency, self.tcurrency)), QLineEdit.Normal, str(self.factor))
        if input[1]==True:
            try:
                self.setConversion(self.mfrom, self.tcurrency, self.dt, Decimal(input[0]))
            except:
                pass
