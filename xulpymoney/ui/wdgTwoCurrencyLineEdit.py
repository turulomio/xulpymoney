from PyQt5.QtWidgets import QWidget,  QLabel, QHBoxLayout, QToolButton, QSizePolicy, QSpacerItem
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QIcon, QPixmap
from xulpymoney.objects.currency import currency_symbol
from xulpymoney.ui.myqlineedit import myQLineEdit
from decimal import Decimal

class wdgTwoCurrencyLineEdit(QWidget):
    factorChanged=pyqtSignal(Decimal)#Se usa para cargar datos de ordenes en los datos de este formulario
    textChanged=pyqtSignal()
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.horizontalLayout = QHBoxLayout(self)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel(self)
        self.label.setText(self.tr("Select a product"))
        self.horizontalLayout.addWidget(self.label)

        spacerItem=QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)

        self.txtA=myQLineEdit(self)
        self.txtA.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.txtA.setToolTip(self.tr("Press the search button"))
        self.txtA.setText(0)
        self.horizontalLayout.addWidget(self.txtA)
    
        self.lblCurrencyA=QLabel(self)
        self.horizontalLayout.addWidget(self.lblCurrencyA)          
        
        self.cmd= QToolButton(self)               
        icon = QIcon()
        icon.addPixmap(QPixmap(":/xulpymoney/transfer.png"), QIcon.Normal, QIcon.Off)
        self.cmd.setIcon(icon)                      
        self.cmd.released.connect(self.on_cmd_released)        
        self.horizontalLayout.addWidget(self.cmd)          
        self.cmd.hide() 
        
        self.txtB=myQLineEdit(self)
        self.txtB.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)               
        self.txtB.setToolTip(self.tr("Press the search button"))
        self.txtB.setText(0)
        self.horizontalLayout.addWidget(self.txtB)             

        self.lblCurrencyB=QLabel(self)
        self.horizontalLayout.addWidget(self.lblCurrencyB)
        
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.txtA.sizePolicy().hasHeightForWidth())
        self.txtA.setSizePolicy(sizePolicy)
        sizePolicyb = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicyb.setHorizontalStretch(2)
        sizePolicyb.setVerticalStretch(0)
        sizePolicyb.setHeightForWidth(self.txtB.sizePolicy().hasHeightForWidth())
        self.txtB.setSizePolicy(sizePolicy)
        self.setLabelSize(200)
        self.factormode=False
        
    def setLabelSize(self, size):
        """
            Sets the label size
        """
        self.label.setFixedWidth(size)

    def setLabel(self, text):
        self.label.setText(text)
        
    def setFactorMode(self, boolean):
        """
            Este widget esta en factor mode y puede editar ambos textos, el resultado es un factor, que podrá ser 
            usado en otros widgets con setNewFactor
        """
        self.factormode=boolean
        if boolean==True:
            self.cmd.show()
            self.setTextA(1)
            self.setTextB(self.factor)
        else:
            self.cmd.hide()
    
    def on_cmd_released(self):
        self.txtA.textChanged.disconnect()
        self.txtB.textChanged.disconnect()
        tmp=self.txtA.decimal()
        self.txtA.setText(Decimal(1)/self.txtB.decimal())
        self.txtB.setText(Decimal(1)/tmp)
        self.txtA.textChanged.connect(self.on_txtA_textChanged)
        self.txtB.textChanged.connect(self.on_txtB_textChanged)
    
    
    def set(self, mem, currencya,  currencyb,  factor):
        """Investement is used to set investment pointer. It's usefull to see investment data in product report
        factor is to mul A to get b"""
        self.mem=mem       
        self.factor=factor
        self.currencya=currencya
        self.currencyb=currencyb

        if self.currencya==self.currencyb:
            self.lblCurrencyB.hide()
            self.txtB.hide()

        self.lblCurrencyA.setText(currency_symbol(self.currencya)+" ")   
        self.lblCurrencyB.setText(currency_symbol(self.currencyb))

        self.txtA.textChanged.disconnect()
        self.txtB.textChanged.disconnect()
        self.txtB.setText(self.txtA.decimal()*factor)
        self.textChanged.emit()
        self.txtA.textChanged.connect(self.on_txtA_textChanged)
        self.txtB.textChanged.connect(self.on_txtB_textChanged)

    def isValid(self):
        if self.txtA.isValid() and self.txtB.isValid():
            return True
        return False

    def setTextA(self, text):
        self.txtA.setText(text)

    def setTextB(self, text):
        self.txtB.setText(text)

    def decimalA(self):
        return self.txtA.decimal()

    def decimalB(self):
        return self.txtB.decimal()

    def on_txtA_textChanged(self, text):
        myQLineEdit.on_textChanged(self.txtA, text)
        if self.txtA.isValid():
            if self.factormode==True:
                if self.txtB.decimal()==Decimal(0):
                    return
                self.factor=self.txtA.decimal()/self.txtB.decimal()
                self.factorChanged.emit(self.factor)
            else:
                self.txtB.textChanged.disconnect()
                self.txtB.setText(self.txtA.decimal()*self.factor)
                self.txtB.textChanged.connect(self.on_txtB_textChanged)
        self.textChanged.emit()

    def on_txtB_textChanged(self, text):
        myQLineEdit.on_textChanged(self.txtB, text)
        if self.txtB.isValid():
            if self.factormode==True:
                if self.txtA.decimal()==Decimal(0):
                    return
                self.factor=self.txtB.decimal()/self.txtA.decimal()
                self.factorChanged.emit(self.factor)
            else:
                self.txtA.textChanged.disconnect()
                self.txtA.setText(self.txtB.decimal()/self.factor)
                self.txtA.textChanged.connect(self.on_txtA_textChanged)
        self.textChanged.emit()

    def setReadOnly(self, boolean):
        self.txtA.setReadOnly(boolean)
        self.txtB.setReadOnly(boolean)
