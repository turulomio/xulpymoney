from PyQt4.QtCore import *
from PyQt4.QtGui import *
from myqtablewidget import *

class investmentSelector(QWidget):
    """Para usarlo promocionar un qwidget en designer y darle los comportamientos de tamaña que neceseite
    incluso añadirlo a un layout."""
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.selected=None
    
    def setupUi(self, cfg):
        self.cfg=cfg
        self.horizontalLayout_2 = QHBoxLayout(self)
        self.horizontalLayout = QHBoxLayout()
        self.label = QLabel(self)
        self.label.setText(self.trUtf8("Selecciona una inversión de MyQuotes"))
        self.horizontalLayout.addWidget(self.label)                                                                                                                                 
        self.txt = QLineEdit(self)                                                                                                                                       
        self.txt.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)                                                                             
        self.txt.setReadOnly(True)      
        self.txt.setToolTip(self.trUtf8("Pulsa en el botón de búsqueda"))                                                                                                                                                           
        self.horizontalLayout.addWidget(self.txt)                                                                                                                                 
        self.cmd= QToolButton(self)               
        icon = QIcon()
        icon.addPixmap(QPixmap(":/images/document-preview.png"), QIcon.Normal, QIcon.Off)
        self.cmd.setIcon(icon)                                                                                                                                   
        self.horizontalLayout.addWidget(self.cmd)                                                                                                                            
        self.horizontalLayout_2.addLayout(self.horizontalLayout)                                                                                                                                                                                                                                                                 
        self.connect(self.cmd,SIGNAL('released()'),  self.on_cmd_released)

    def on_cmd_released(self):
        d=investmentDialog(self, self.cfg)
        d.exec_()
        self.setSelected(d.selected)
            
    def setSelected(self, investment):
        """Recibe un objeto Investment. No se usará posteriormente, por lo que puede no estar completo con get_basic.:."""
        self.selected=investment
        if self.selected==None:
            self.txt.setText(self.trUtf8("No seleccionado"))
        else:
            self.txt.setText("{0} ({1})".format(self.selected.name, self.selected.id))
        

class investmentDialog(QDialog):
    def __init__(self, parent, cfg):
        QDialog.__init__(self, parent)
        self.cfg=cfg
        self.inversiones=[]
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
        self.widget = investmentSelector(self)
        self.horizontalLayout.addWidget(self.widget)
        self.label = QLabel(self)
        self.horizontalLayout.addWidget(self.label)
        self.txt = QLineEdit(self)
        self.horizontalLayout.addWidget(self.txt)
        self.cmd = QPushButton(self)
        icon = QIcon()
        icon.addPixmap(QPixmap(":/images/document-preview.png"), QIcon.Normal, QIcon.Off)
        self.cmd.setIcon(icon)
        self.horizontalLayout.addWidget(self.cmd)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.tblInversiones = myQTableWidget(self)
        self.tblInversiones.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tblInversiones.setAlternatingRowColors(True)
        self.tblInversiones.setColumnCount(4)
        self.tblInversiones.setRowCount(0)
        self.tblInversiones.settings("investmentSelector",  self.cfg.file)    
        self.tblInversiones.setHorizontalHeaderItem(0, QTableWidgetItem(self.trUtf8("Inversión")))
        self.tblInversiones.setHorizontalHeaderItem(1, QTableWidgetItem(self.trUtf8("Id")))
        self.tblInversiones.setHorizontalHeaderItem(2, QTableWidgetItem(self.trUtf8("ISIN")))
        self.tblInversiones.setHorizontalHeaderItem(3, QTableWidgetItem(self.trUtf8("Ticker")))
        self.tblInversiones.horizontalHeader().setStretchLastSection(False)
        self.tblInversiones.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tblInversiones.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tblInversiones.setSelectionMode(QAbstractItemView.SingleSelection)

        self.tblInversiones.verticalHeader().setVisible(False)
        self.verticalLayout.addWidget(self.tblInversiones)
        self.lblFound = QLabel(self)
        self.verticalLayout.addWidget(self.lblFound)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        self.setWindowTitle(self.trUtf8("Selecciona una inversión"))
        self.lbl.setText(self.trUtf8("Listado de inversiones"))
        self.label.setText(self.trUtf8("Búsqueda por código, ISIN o nombre de la inversión"))
        self.lblFound.setText(self.trUtf8("Registros encontrados"))

        self.setTabOrder(self.txt, self.cmd)
        self.setTabOrder(self.cmd, self.tblInversiones)                                                                                                                                                                                                                                        
        self.connect(self.cmd,SIGNAL('released()'),  self.on_cmd_released)                                                                                                                                                                                              
        self.connect(self.tblInversiones,SIGNAL('itemSelectionChanged()'),  self.on_tblInversiones_itemSelectionChanged)                                                                                                             
        self.connect(self.tblInversiones,SIGNAL('cellDoubleClicked(int,int)'),  self.on_tblInversiones_cellDoubleClicked)


    def on_cmd_released(self):
        if len(self.txt.text().upper())<=3:            
            m=QMessageBox()
            m.setText(self.trUtf8("Búsqueda demasiado extensa. Necesita más de 3 caracteres"))
            m.exec_()  
            return

        self.inversiones=[]
        con=self.cfg.connect_myquotes()
        cur = con.cursor()
        cur.execute("select * from investments where id::text like '%"+(self.txt.text().upper())+"%' or upper(name) like '%"+(self.txt.text().upper())+"%' or upper(isin) like '%"+(self.txt.text().upper())+"%' or upper(comentario) like '%"+(self.txt.text().upper())+"%' order by name")
        self.lblFound.setText(self.tr("Encontrados {0} registros".format(cur.rowcount)))
                
        self.tblInversiones.setRowCount(cur.rowcount)
        for i in cur:
            inv=Investment(self.cfg)
            inv.init__db_row(self.cfg, i)
            self.inversiones.append(inv)
            self.tblInversiones.setItem(cur.rownumber-1, 0, QTableWidgetItem(inv.name.upper()))
            self.tblInversiones.setItem(cur.rownumber-1, 1, QTableWidgetItem(str(inv.id)))
            self.tblInversiones.item(cur.rownumber-1, 0).setIcon(inv.bolsa.country.qicon())
            self.tblInversiones.setItem(cur.rownumber-1, 2, QTableWidgetItem(inv.isin))
            self.tblInversiones.setItem(cur.rownumber-1, 3, QTableWidgetItem(inv.yahoo))
        cur.close()     
        self.cfg.disconnect_myquotesd(con)   
        
    def on_tblInversiones_cellDoubleClicked(self, row, column):
        self.done(0)
    
    def on_tblInversiones_itemSelectionChanged(self):
        try:
            for i in self.tblInversiones.selectedItems():
                if i.column()==0:
                    self.selected=self.inversiones[i.row()]
            print (self.selected)
        except:
            self.selected=None
