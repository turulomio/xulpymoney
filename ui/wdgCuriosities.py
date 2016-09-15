from PyQt5.QtWidgets import QWidget, QSpacerItem, QSizePolicy
from Ui_wdgCuriosities import *
from wdgCuriosity import *
from libxulpymoney import Assets

class wdgCuriosities(QWidget, Ui_wdgCuriosities):
    def __init__(self, mem,  parent = None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.mem=mem
        
        c=wdgCuriosity(self.mem)
        c.setTitle(self.tr("Since when there is data in the database?"))
        c.setText("The first data is from {}".format(Assets(self.mem).first_datetime_with_user_data()))
        self.layout.addWidget(c)
        c=wdgCuriosity(self.mem)
        c.setTitle(self.tr("Which is the investment I gain more money?"))
        self.layout.addWidget(c)
        c=wdgCuriosity(self.mem)
        c.setTitle(self.tr("Which is the product I gain more money?"))
        self.layout.addWidget(c)
        c=wdgCuriosity(self.mem)
        c.setTitle(self.tr("Which is the benchmark highest and lowest price?"))
        self.layout.addWidget(c)
        c=wdgCuriosity(self.mem)
        c.setTitle(self.tr("How many quotes are there in the database?"))
        self.layout.addWidget(c)
        c=wdgCuriosity(self.mem)
        c.setTitle(self.tr("Which product has the highest quote?"))
        self.layout.addWidget(c)
        c=wdgCuriosity(self.mem)
        c.setTitle(self.tr("Which is the amount of the largest account operation?"))
        self.layout.addWidget(c)
        c=wdgCuriosity(self.mem)
        c.setTitle(self.tr("Which is the amount of the largest credit card operation?"))
        self.layout.addWidget(c)
        c=wdgCuriosity(self.mem)
        c.setTitle(self.tr("Which is the amount of the largest investment operation?"))
        self.layout.addWidget(c)
        self.layout.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Expanding, QSizePolicy.Expanding))

    
