## -*- coding: utf-8 -*-
from libxulpymoney import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
#import PyQt4.Qwt5 as Qwt
from myqtablewidget import *
from Ui_wdgInformeClases import *
#import matplotlib
#from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
#from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
#from matplotlib.figure import Figure

##
##class PieMarker(Qwt.QwtPlotMarker):
##    def __init__(self, data, colors,  *args):
##        Qwt.QwtPlotMarker.__init__(self, *args)
##        self.setRenderHint(Qwt.QwtPlotItem.RenderAntialiased, True)
##        self.data=data
##        self.colors=colors
##
##    def rtti(self):
##        return Qwt.QwtPlotItem.Rtti_PlotUserItem
##
##    def draw(self, painter, xMap, yMap, rect):
##        margin = 15
##        pieRect = QRect()
##        pieRect.setX(rect.x() + margin)
##        pieRect.setY(rect.y() + margin)
##        pieRect.setHeight(yMap.transform(70.0))
###	pieRect.setHeight(pieRect.height())
##        pieRect.setWidth(pieRect.height())
##        suma=0
##        for reg in self.data:
##            suma=suma+reg[2]
##        sumangle=0
##        for i in range(len(self.data)):
##            angle= self.data[i][2]*5760/suma #Resolucion=16*360
##            painter.save()
##            painter.setBrush(QBrush(self.colors[i], Qt.SolidPattern))
##            painter.drawPie(pieRect, sumangle, angle)
##            painter.restore()
##            sumangle=sumangle+angle
##
##class Pie(Qwt.QwtPlot):
##    def __init__(self, data, colors,  *args):
##        Qwt.QwtPlot.__init__(self, *args)
##        self.setAutoReplot(True)
##        self.setCanvasBackground(Qt.white)
##        self.enableAxis(Qwt.QwtPlot.xBottom,  False)
##        self.enableAxis(Qwt.QwtPlot.yLeft,  False)
##        self.plotLayout().setAlignCanvasToScales(True)
##        pie = PieMarker(data, colors)
##        pie.attach(self)
##
##        legend = Qwt.QwtLegend()
##        legend.setItemMode(Qwt.QwtLegend.CheckableItem)
##        self.insertLegend(legend, Qwt.QwtPlot.BottomLegend)
    
class wdgPie(QWidget):    
    """Data recibe los datos
    id tabla
    concepto
    valor
    otros
    La tabla tendra
    id tabla oculot
    concepto
    valor
    tpc
    otros
    self.data y selfcolors debedn ser del mismo tamaño.
    """
    def __init__(self, parent):
        QWidget.__init__(self,parent)

    def set_data(self, cfg,  data, headers , colors,  name=""):
        self.cfg=cfg
        self.data=data
        self.headers=headers
        self.colors=colors
        self.canvas=None
        self.create_main_frame()
        self.setObjectName(name)
        self.resize(754, 525)
        self.verticalLayout_3 = QVBoxLayout(self)
        self.verticalLayout = QVBoxLayout()
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.addWidget(self.pie)
        self.table = myQTableWidget(self)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setCascadingSectionResizes(False)
        self.table.setObjectName("table")
        self.table.setColumnCount(len(self.headers))
        self.table.setRowCount(len(self.data))
        for i in range( len(self.headers)):
            self.table.setHorizontalHeaderItem(i, qcenter(self.headers[i]))
        total=0
        for reg in self.data:
            total=total+reg[2]
        for i in range(len(self.data)):
            self.table.setItem(i, 0, QTableWidgetItem(self.data[i][0]))
            self.table.setItem(i, 1, QTableWidgetItem(self.data[i][1]))
            self.table.setItem(i, 2, self.cfg.currencies.find('EUR').qtablewidgetitem(self.data[i][2]))            
            self.table.setItem(i, 3, qtpc(self.data[i][2]*100/total))        
            self.table.item(i, 1).setBackgroundColor(self.colors[i])           
        self.horizontalLayout.addWidget(self.table)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout_3.addLayout(self.verticalLayout)

        self.table.settings(name+"wdgPie_table",  self.cfg)
        QtCore.QMetaObject.connectSlotsByName(self)

    def save_plot(self):
        file_choices = "PNG (*.png)|*.png"
        
        path = unicode(QFileDialog.getSaveFileName(self, 
                        'Save file', '', 
                        file_choices))
        if path:
            self.canvas.print_figure(path, dpi=self.dpi)
            self.statusBar().showMessage('Saved to %s' % path, 2000)

    def on_pick(self, event):
        # The event received here is of the type
        # matplotlib.backend_bases.PickEvent
        #
        # It carries lots of information, of which we're using
        # only a small amount here.
        # 
        box_points = event.artist.get_bbox().get_points()
        msg = "You've clicked on a bar with coords:\n %s" % box_points
        
        QMessageBox.information(self, "Click!", msg)
    
    def on_draw(self):
        """ Redraws the figure
        """
        str = unicode(self.textbox.text())
        self.data = map(int, str.split())
        
        x = range(len(self.data))

        # clear the axes and redraw the plot anew
        #
        self.axes.clear()        
        self.axes.grid(self.grid_cb.isChecked())
        
        self.axes.bar(
            left=x, 
            height=self.data, 
            width=self.slider.value() / 100.0, 
            align='center', 
            alpha=0.44,
            picker=5)
        
        self.canvas.draw()
    
    def create_main_frame(self):
        self.main_frame = QWidget()
        
        # Create the mpl Figure and FigCanvas objects. 
        # 5x4 inches, 100 dots-per-inch
        #
        self.dpi = 100
        self.fig = Figure((5.0, 4.0), dpi=self.dpi)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)
        
        # Since we have only one plot, we can use add_axes 
        # instead of add_subplot, but then the subplot
        # configuration tool in the navigation toolbar wouldn't
        # work.
        #
        self.axes = self.fig.add_subplot(111)
        
        # Bind the 'pick' event for clicking on one of the bars
        #
        self.canvas.mpl_connect('pick_event', self.on_pick)
        
        # Create the navigation toolbar, tied to the canvas
        #
        self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)
        
        # Other GUI controls
        # 
        self.textbox = QLineEdit()
        self.textbox.setMinimumWidth(200)
        self.connect(self.textbox, SIGNAL('editingFinished ()'), self.on_draw)
        
        self.draw_button = QPushButton("&Draw")
        self.connect(self.draw_button, SIGNAL('clicked()'), self.on_draw)
        
        self.grid_cb = QCheckBox("Show &Grid")
        self.grid_cb.setChecked(False)
        self.connect(self.grid_cb, SIGNAL('stateChanged(int)'), self.on_draw)
        
        slider_label = QLabel('Bar width (%):')
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(1, 100)
        self.slider.setValue(20)
        self.slider.setTracking(True)
        self.slider.setTickPosition(QSlider.TicksBothSides)
        self.connect(self.slider, SIGNAL('valueChanged(int)'), self.on_draw)
        
        #
        # Layout with box sizers
        # 
        hbox = QHBoxLayout()
        
        for w in [  self.textbox, self.draw_button, self.grid_cb,
                    slider_label, self.slider]:
            hbox.addWidget(w)
            hbox.setAlignment(w, Qt.AlignVCenter)
        
        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)
        vbox.addWidget(self.mpl_toolbar)
        vbox.addLayout(hbox)
        
        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)
    
    def create_status_bar(self):
        self.status_text = QLabel("This is a demo")
        self.statusBar().addWidget(self.status_text, 1)
        
    def create_menu(self):        
        self.file_menu = self.menuBar().addMenu("&File")
        
        load_file_action = self.create_action("&Save plot",
            shortcut="Ctrl+S", slot=self.save_plot, 
            tip="Save the plot")
        quit_action = self.create_action("&Quit", slot=self.close, 
            shortcut="Ctrl+Q", tip="Close the application")
        
        self.add_actions(self.file_menu, 
            (load_file_action, None, quit_action))
        
        self.help_menu = self.menuBar().addMenu("&Help")
        about_action = self.create_action("&About", 
            shortcut='F1', slot=self.on_about, 
            tip='About the demo')
        
        self.add_actions(self.help_menu, (about_action,))

    def add_actions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def create_action(  self, text, slot=None, shortcut=None, 
                        icon=None, tip=None, checkable=False, 
                        signal="triggered()"):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action
