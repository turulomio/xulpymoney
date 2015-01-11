from PyQt4.QtCore import *
from PyQt4.QtGui import *
from myqtablewidget import *

class wdgProductSelector(QWidget):
    """Para usarlo promocionar un qwidget en designer y darle los comportamientos de tamaña que neceseite
    incluso añadirlo a un layout."""
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.selected=None
    
    def setupUi(self, mem):
        self.mem=mem
        self.horizontalLayout_2 = QHBoxLayout(self)
        self.horizontalLayout = QHBoxLayout()
        self.label = QLabel(self)
        self.label.setText(self.tr("Select a product"))
        self.horizontalLayout.addWidget(self.label)                                                                                                                                 
        self.txt = QLineEdit(self)                                                                                                                                       
        self.txt.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)                                                                             
        self.txt.setReadOnly(True)      
        self.txt.setToolTip(self.tr("Press the search button"))                                                                                                                                                           
        self.horizontalLayout.addWidget(self.txt)                                                                                                                                 
        self.cmd= QToolButton(self)               
        icon = QIcon()
        icon.addPixmap(QPixmap(":/xulpymoney/document-preview-archive.png"), QIcon.Normal, QIcon.Off)
        self.cmd.setIcon(icon)                                                                                                                                   
        self.horizontalLayout.addWidget(self.cmd)                                                                                                                            
        self.horizontalLayout_2.addLayout(self.horizontalLayout)                                                                                                                                                                                                                                                                 
        self.connect(self.cmd,SIGNAL('released()'),  self.on_cmd_released)

    def on_cmd_released(self):
        d=frmProductSelector(self, self.mem)
        d.exec_()
        self.setSelected(d.selected)
            
    def setSelected(self, product):
        """Recibe un objeto Product. No se usará posteriormente, por lo que puede no estar completo con get_basic.:."""
        self.selected=product
        if self.selected==None:
            self.txt.setText(self.tr("Not selected"))
        else:
            self.txt.setText("{0} ({1})".format(self.selected.name, self.selected.id))
        

class frmProductSelector(QDialog):
    def __init__(self, parent, mem):
        QDialog.__init__(self, parent)
        self.mem=mem
        self.products=[]
        self.selected=None
        self.resize(1024, 500)
        self.horizontalLayout_2 = QHBoxLayout(self)
        self.verticalLayout = QVBoxLayout()
        self.lbl = QLabel(self)
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.lbl.setFont(font)
        self.lbl.setAlignment(Qt.AlignCenter)
        self.verticalLayout.addWidget(self.lbl)
        self.horizontalLayout = QHBoxLayout()
        spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.widget = wdgProductSelector(self)
        self.horizontalLayout.addWidget(self.widget)
        self.label = QLabel(self)
        self.horizontalLayout.addWidget(self.label)
        self.txt = QLineEdit(self)
        self.horizontalLayout.addWidget(self.txt)
        self.cmd = QToolButton(self)
        icon = QIcon()
        icon.addPixmap(QPixmap(":/xulpymoney/document-preview-archive.png"), QIcon.Normal, QIcon.Off)
        self.cmd.setIcon(icon)
        self.horizontalLayout.addWidget(self.cmd)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.tblInvestments = myQTableWidget(self)
        self.tblInvestments.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tblInvestments.setAlternatingRowColors(True)
        self.tblInvestments.setColumnCount(4)
        self.tblInvestments.setRowCount(0)
        self.tblInvestments.settings("wdgProductSelector",  self.mem)    
        self.tblInvestments.setHorizontalHeaderItem(0, QTableWidgetItem(self.tr("Product")))
        self.tblInvestments.setHorizontalHeaderItem(1, QTableWidgetItem(self.tr("Id")))
        self.tblInvestments.setHorizontalHeaderItem(2, QTableWidgetItem(self.tr("ISIN")))
        self.tblInvestments.setHorizontalHeaderItem(3, QTableWidgetItem(self.tr("Ticker")))
        self.tblInvestments.horizontalHeader().setStretchLastSection(False)
        self.tblInvestments.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tblInvestments.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tblInvestments.setSelectionMode(QAbstractItemView.SingleSelection)

        self.tblInvestments.verticalHeader().setVisible(False)
        self.verticalLayout.addWidget(self.tblInvestments)
        self.lblFound = QLabel(self)
        self.verticalLayout.addWidget(self.lblFound)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        self.setWindowTitle(self.tr("Select a product"))
        self.lbl.setText(self.tr("Product list"))
        self.label.setText(self.tr("Search by code, ISIN, ticker or product name"))
        self.lblFound.setText(self.tr("Found registers"))

        self.setTabOrder(self.txt, self.cmd)
        self.setTabOrder(self.cmd, self.tblInvestments)                                                                                                                                                                                                                                        
        self.connect(self.cmd,SIGNAL('released()'),  self.on_cmd_released)                                                                                                                                                                                                         
        self.connect(self.txt,SIGNAL('returnPressed()'),  self.on_cmd_released)                                                                                                                                                                                              
        self.connect(self.tblInvestments,SIGNAL('itemSelectionChanged()'),  self.on_tblInvestments_itemSelectionChanged)                                                                                                             
        self.connect(self.tblInvestments,SIGNAL('cellDoubleClicked(int,int)'),  self.on_tblInvestments_cellDoubleClicked)
        
    def on_cmd_released(self):
        if len(self.txt.text().upper())<=3:            
            m=QMessageBox()
            m.setText(self.tr("Search too wide. You need more than 3 characters"))
            m.exec_()  
            return

        self.products=[]
        cur = self.mem.con.cursor()
        cur.execute("select * from products where id::text like '%"+(self.txt.text().upper())+
                    "%' or upper(name) like '%"+(self.txt.text().upper())+
                    "%' or upper(isin) like '%"+(self.txt.text().upper())+
                    "%' or upper(ticker) like '%"+(self.txt.text().upper())+
                    "%' or upper(comentario) like '%"+(self.txt.text().upper())+
                    "%' order by name")
        self.lblFound.setText(self.tr("Found {0} registers").format(cur.rowcount))
                
        self.tblInvestments.setRowCount(cur.rowcount)
        for i in cur:
            inv=Product(self.mem)
            inv.init__db_row(i)
            self.products.append(inv)
            self.tblInvestments.setItem(cur.rownumber-1, 0, QTableWidgetItem(inv.name.upper()))
            self.tblInvestments.setItem(cur.rownumber-1, 1, QTableWidgetItem(str(inv.id)))
            self.tblInvestments.item(cur.rownumber-1, 0).setIcon(inv.stockexchange.country.qicon())
            self.tblInvestments.setItem(cur.rownumber-1, 2, QTableWidgetItem(inv.isin))
            self.tblInvestments.setItem(cur.rownumber-1, 3, QTableWidgetItem(inv.ticker))
        cur.close()     
        
    def on_tblInvestments_cellDoubleClicked(self, row, column):
        self.done(0)
    
    def on_tblInvestments_itemSelectionChanged(self):
        try:
            for i in self.tblInvestments.selectedItems():
                if i.column()==0:
                    self.selected=self.products[i.row()]
            print (self.selected)
        except:
            self.selected=None
